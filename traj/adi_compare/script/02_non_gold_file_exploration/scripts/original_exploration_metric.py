#!/usr/bin/env python3
"""Compare trajectory exploration efficiency against SWE-bench gold files.

Two file sets are reported:

* ``seen``: Python files mentioned in actions or observations before the final
  submit step. This captures broad search output, grep hits, tracebacks, and
  viewed files.
* ``action``: Python files explicitly named in actions before the final submit
  step. This is a conservative lower bound on files the agent deliberately
  targeted.

Repository test files are intentionally kept. They are counted as non-gold
exploration unless they appear in the gold source patch, because they still
consume context during debugging.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

PY_PATH_RE = re.compile(r"(?:/testbed/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+\.py")
GENERATED_RE = re.compile(r"^(reproduce|debug|trace|test_|check_)[^/]*\.py$")


def normalize(path: str) -> str:
    path = path.strip().strip("`'\",:;()[]{}")
    if path.startswith("/testbed/"):
        path = path[len("/testbed/") :]
    if path.startswith("testbed/"):
        path = path[len("testbed/") :]
    if path.startswith("a/") or path.startswith("b/"):
        path = path[2:]
    while path.startswith("./"):
        path = path[2:]
    return path


def is_source_file(path: str) -> bool:
    if not path.endswith(".py") or "/" not in path:
        return False
    if path.startswith(("opt/", "usr/", "tmp/", "var/", "path/to/")):
        return False
    if "site-packages/" in path or "__pycache__/" in path:
        return False
    if path.startswith("reproduction/"):
        return False
    if GENERATED_RE.match(path):
        return False
    # We evaluate localization to source patches; test files are tracked as
    # exploration noise unless they are in the gold patch.
    return True


def extract_files(text: str) -> set[str]:
    files = set()
    for match in PY_PATH_RE.finditer(text or ""):
        path = normalize(match.group(0))
        if is_source_file(path):
            files.add(path)
    return files


def model_key(run_name: str) -> str:
    return run_name.removeprefix("DAIRA_").removeprefix("SWE-agent_").removeprefix("SWE-agent-").lower()


def run_kind(run_name: str) -> str:
    return "daira" if run_name.startswith("DAIRA") else "baseline"


def load_gold(localization_csv: Path) -> dict[str, set[str]]:
    gold: dict[str, set[str]] = {}
    with localization_csv.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["instance_id"] not in gold:
                gold[row["instance_id"]] = {p for p in row["gold_files"].split(";") if p}
    return gold


def load_traj(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        traj = data.get("trajectory") or data.get("history") or data.get("steps")
        if isinstance(traj, list):
            return traj
    return []


def analyze_instance(traj: list[dict], gold_files: set[str]) -> dict[str, object]:
    seen_files: set[str] = set()
    action_files: set[str] = set()
    observation_files: set[str] = set()
    first_gold_step: int | None = None
    files_before_first_gold: set[str] = set()
    nongold_before_first_gold: set[str] = set()
    first_gold_action_step: int | None = None
    action_files_before_first_gold: set[str] = set()
    nongold_action_before_first_gold: set[str] = set()
    run_hunter_steps = 0

    for idx, step in enumerate(traj, start=1):
        action = str(step.get("action", ""))
        if action.strip() == "submit":
            # The final submit observation is a diff, not part of the search process.
            continue
        observation = str(step.get("observation", ""))
        if action.strip().startswith("run_hunter_trace"):
            run_hunter_steps += 1
        step_action_files = extract_files(action)
        step_observation_files = extract_files(observation)
        step_files = step_action_files | step_observation_files

        if first_gold_step is None and step_files & gold_files:
            first_gold_step = idx
        if first_gold_step is None:
            files_before_first_gold |= step_files
            nongold_before_first_gold |= step_files - gold_files
        if first_gold_action_step is None and step_action_files & gold_files:
            first_gold_action_step = idx
        if first_gold_action_step is None:
            action_files_before_first_gold |= step_action_files
            nongold_action_before_first_gold |= step_action_files - gold_files

        action_files |= step_action_files
        observation_files |= step_observation_files
        seen_files |= step_files

    gold_seen = seen_files & gold_files
    nongold_seen = seen_files - gold_files
    action_gold_seen = action_files & gold_files
    action_nongold_seen = action_files - gold_files
    return {
        "steps": len(traj),
        "run_hunter_steps": run_hunter_steps,
        "unique_files_seen": len(seen_files),
        "unique_action_files": len(action_files),
        "unique_observation_files": len(observation_files),
        "gold_files_seen": len(gold_seen),
        "gold_files_total": len(gold_files),
        "nongold_files_seen": len(nongold_seen),
        "gold_file_recall_seen": len(gold_seen) / len(gold_files) if gold_files else 0.0,
        "gold_file_precision_seen": len(gold_seen) / len(seen_files) if seen_files else 0.0,
        "action_gold_files_seen": len(action_gold_seen),
        "action_nongold_files_seen": len(action_nongold_seen),
        "action_gold_file_recall_seen": len(action_gold_seen) / len(gold_files) if gold_files else 0.0,
        "action_gold_file_precision_seen": len(action_gold_seen) / len(action_files) if action_files else 0.0,
        "first_gold_step": first_gold_step or 0,
        "first_gold_action_step": first_gold_action_step or 0,
        "hit_gold": int(bool(gold_seen)),
        "action_hit_gold": int(bool(action_gold_seen)),
        "files_before_first_gold": len(files_before_first_gold),
        "nongold_before_first_gold": len(nongold_before_first_gold),
        "action_files_before_first_gold": len(action_files_before_first_gold),
        "nongold_action_before_first_gold": len(nongold_action_before_first_gold),
        "files_seen": ";".join(sorted(seen_files)),
        "action_files_seen": ";".join(sorted(action_files)),
        "gold_seen": ";".join(sorted(gold_seen)),
        "action_gold_seen": ";".join(sorted(action_gold_seen)),
    }


def evaluate(traj_root: Path, localization_csv: Path) -> list[dict[str, object]]:
    gold = load_gold(localization_csv)
    rows: list[dict[str, object]] = []
    for run_dir in sorted(p for p in traj_root.iterdir() if p.is_dir() and p.name != "swebench result"):
        for instance_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
            iid = instance_dir.name
            if iid not in gold:
                continue
            traj_file = instance_dir / f"{iid}_traj.json"
            if not traj_file.exists():
                continue
            metrics = analyze_instance(load_traj(traj_file), gold[iid])
            row = {
                "run": run_dir.name,
                "kind": run_kind(run_dir.name),
                "model": model_key(run_dir.name),
                "instance_id": iid,
                "gold_files": ";".join(sorted(gold[iid])),
            }
            row.update(metrics)
            rows.append(row)
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["run"]), str(row["kind"]), str(row["model"]))].append(row)
    out = []
    cols = [
        "steps",
        "unique_files_seen",
        "nongold_files_seen",
        "gold_file_recall_seen",
        "gold_file_precision_seen",
        "first_gold_step",
        "first_gold_action_step",
        "nongold_before_first_gold",
        "unique_action_files",
        "action_nongold_files_seen",
        "action_gold_file_precision_seen",
        "action_gold_file_recall_seen",
        "nongold_action_before_first_gold",
        "run_hunter_steps",
    ]
    for (run, kind, model), items in sorted(groups.items()):
        row: dict[str, object] = {
            "run": run,
            "kind": kind,
            "model": model,
            "n": len(items),
            "hit_gold_rate": mean(float(x["hit_gold"]) for x in items),
        }
        for col in cols:
            vals = [float(x[col]) for x in items if not (col == "first_gold_step" and float(x[col]) == 0)]
            row[f"mean_{col}"] = mean(vals) if vals else 0.0
            row[f"median_{col}"] = median(vals) if vals else 0.0
        out.append(row)
    return out


def pairwise(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by = {(str(r["model"]), str(r["kind"]), str(r["instance_id"])): r for r in rows}
    models = sorted({str(r["model"]) for r in rows})
    out = []
    for model in models:
        common = sorted(
            {iid for (m, k, iid) in by if m == model and k == "daira"}
            & {iid for (m, k, iid) in by if m == model and k == "baseline"}
        )
        if not common:
            continue
        row: dict[str, object] = {"model": model, "paired_n": len(common)}
        for col in [
            "steps",
            "unique_files_seen",
            "unique_action_files",
            "nongold_files_seen",
            "action_nongold_files_seen",
            "gold_file_precision_seen",
            "gold_file_recall_seen",
            "action_gold_file_precision_seen",
            "action_gold_file_recall_seen",
            "first_gold_step",
            "first_gold_action_step",
            "nongold_before_first_gold",
            "nongold_action_before_first_gold",
        ]:
            dvals = [float(by[(model, "daira", iid)][col]) for iid in common]
            bvals = [float(by[(model, "baseline", iid)][col]) for iid in common]
            if col in {"first_gold_step", "first_gold_action_step"}:
                dvals = [v for v in dvals if v > 0]
                bvals = [v for v in bvals if v > 0]
            bavg = mean(bvals) if bvals else 0.0
            davg = mean(dvals) if dvals else 0.0
            row[f"baseline_{col}"] = bavg
            row[f"daira_{col}"] = davg
            row[f"delta_{col}"] = davg - bavg
            row[f"delta_pct_{col}"] = (davg - bavg) / bavg * 100 if bavg else 0.0
        out.append(row)
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        if not rows:
            return
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, paired: list[dict[str, object]]) -> None:
    lines = [
        "# Exploration Efficiency",
        "",
        "Files are extracted from each trajectory's actions and observations, then compared with SWE-bench gold patch files.",
        "The final `submit` diff is excluded. `seen` counts files mentioned in actions or observations; `action` counts only files explicitly named in actions.",
        "Repository test files are retained and counted as non-gold exploration unless they appear in the gold patch.",
        "",
        "| model | n | seen files baseline | seen files DAIRA | change | seen non-gold baseline | seen non-gold DAIRA | change | action files baseline | action files DAIRA | change | action non-gold baseline | action non-gold DAIRA | change | action gold precision baseline | action gold precision DAIRA |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in paired:
        lines.append(
            "| {model} | {n} | {buf:.1f} | {duf:.1f} | {dufp:.1f}% | {bng:.1f} | {dng:.1f} | {dngp:.1f}% | {baf:.1f} | {daf:.1f} | {dafp:.1f}% | {bang:.1f} | {dang:.1f} | {dangp:.1f}% | {bagp:.3f} | {dagp:.3f} |".format(
                model=r["model"],
                n=r["paired_n"],
                buf=r["baseline_unique_files_seen"],
                duf=r["daira_unique_files_seen"],
                dufp=r["delta_pct_unique_files_seen"],
                bng=r["baseline_nongold_files_seen"],
                dng=r["daira_nongold_files_seen"],
                dngp=r["delta_pct_nongold_files_seen"],
                baf=r["baseline_unique_action_files"],
                daf=r["daira_unique_action_files"],
                dafp=r["delta_pct_unique_action_files"],
                bang=r["baseline_action_nongold_files_seen"],
                dang=r["daira_action_nongold_files_seen"],
                dangp=r["delta_pct_action_nongold_files_seen"],
                bagp=r["baseline_action_gold_file_precision_seen"],
                dagp=r["daira_action_gold_file_precision_seen"],
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--traj-root", type=Path, default=Path("/data/home/orrero/wzh/data/DAIRA_traj"))
    parser.add_argument(
        "--localization-csv",
        type=Path,
        default=Path("expr_data/DAIRA/localization_eval/per_instance_localization.csv"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("expr_data/DAIRA/localization_eval"))
    args = parser.parse_args()

    rows = evaluate(args.traj_root, args.localization_csv)
    summary = summarize(rows)
    paired = pairwise(rows)
    write_csv(args.out_dir / "exploration_per_instance.csv", rows)
    write_csv(args.out_dir / "exploration_summary_by_run.csv", summary)
    write_csv(args.out_dir / "exploration_paired.csv", paired)
    write_md(args.out_dir / "exploration_efficiency.md", paired)
    print(f"Wrote {len(rows)} trajectory rows and {len(paired)} paired comparisons to {args.out_dir}")


if __name__ == "__main__":
    main()
