#!/usr/bin/env python3
import argparse
import ast
import json
import os
import pathlib
import shlex
import subprocess
import sys
import time

import yaml


ROOT = pathlib.Path("/data/home/orrero/wzh")
DEFAULT_INSTANCES = ROOT / "my_tool/instances_swebench_verified_20_matplotlib_py311_chatdbg.yaml"
DEFAULT_EVALS = ROOT / "baseline/moatless-tree-search/moatless/benchmark/swebench_verified_all_evaluations.json"
DEFAULT_OUT = ROOT / "my_tool/chatdbg_daira_experiment/chatdbg_matplotlib20_py311_deepseek_20260526_v2"
CHATDBG_SRC = ROOT / "baseline/ChatDBG"
CHATDBG_VENV = ROOT / "my_tool/chatdbg_daira_experiment/chatdbg_shared_py311_venv"


def run(cmd, *, timeout=None, env=None, cwd=None, input_text=None):
    return subprocess.run(
        cmd,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        env=env,
        cwd=cwd,
    )


def parse_list(value):
    if isinstance(value, list):
        return value
    return ast.literal_eval(value)


def docker_exec(container, command, *, timeout=None, input_text=None, env=None):
    cmd = ["docker", "exec"]
    if input_text is not None:
        cmd.append("-i")
    for key, value in (env or {}).items():
        cmd += ["-e", f"{key}={value}"]
    cmd += [container, "bash", "-lc", command]
    return run(cmd, timeout=timeout, input_text=input_text)


def summarize_log(path):
    if not path.exists() or path.stat().st_size == 0:
        return {
            "chatdbg_log_found": False,
            "total_tokens": None,
            "total_cost": None,
            "llm_queries": 0,
            "debug_function_calls": 0,
        }
    try:
        docs = yaml.safe_load(path.read_text()) or []
    except Exception as exc:
        return {"chatdbg_log_found": True, "log_parse_error": str(exc)}

    total_tokens = 0
    total_cost = 0
    llm_queries = 0
    debug_calls = 0
    for doc in docs:
        meta = doc.get("meta", {})
        total_tokens += meta.get("total_tokens") or 0
        total_cost += meta.get("total_cost") or 0
        for step in doc.get("steps", []):
            if step.get("output", {}).get("type") == "chat":
                llm_queries += 1
                for out in step.get("output", {}).get("outputs", []):
                    if out.get("type") == "call":
                        debug_calls += 1
    return {
        "chatdbg_log_found": True,
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "llm_queries": llm_queries,
        "debug_function_calls": debug_calls,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instances", type=pathlib.Path, default=DEFAULT_INSTANCES)
    parser.add_argument("--evals", type=pathlib.Path, default=DEFAULT_EVALS)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument("--slice", default=None, help="Python-style slice, e.g. :1 or 3:7")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--model", default=os.environ.get("CHATDBG_MODEL", "deepseek/deepseek-chat"))
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    instances = yaml.safe_load(args.instances.read_text())
    if args.slice:
        start, _, stop = args.slice.partition(":")
        instances = instances[int(start) if start else None : int(stop) if stop else None]

    evals = {item["instance_id"]: item for item in json.loads(args.evals.read_text())}
    summary = []

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    api_base = os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com")
    if not api_key:
        print("DEEPSEEK_API_KEY is required", file=sys.stderr)
        return 2

    for index, inst in enumerate(instances):
        iid = inst["problem_statement"]["id"]
        image = inst["env"]["deployment"]["image"]
        case_dir = args.out / iid
        case_dir.mkdir(parents=True, exist_ok=True)
        eval_item = evals[iid]
        tests = parse_list(eval_item["fail_to_pass"])
        test_cmd = "python -m pytest -q " + " ".join(shlex.quote(t) for t in tests)
        chatdbg_log = f"/results/{iid}.chatdbg.yaml"
        container = f"chatdbg_{iid.replace('__', '_').replace('-', '_')}_{int(time.time())}"

        meta = {
            "instance_id": iid,
            "image": image,
            "tests": tests,
            "test_command": test_cmd,
            "status": "started",
            "start_time": time.time(),
        }
        (case_dir / "metadata.json").write_text(json.dumps(meta, indent=2))
        (case_dir / "test_patch.diff").write_text(eval_item["test_patch"])

        print(f"[{index + 1}/{len(instances)}] {iid}", flush=True)
        try:
            start = run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    container,
                    "-v",
                    f"{CHATDBG_SRC}:/opt/ChatDBG:ro",
                    "-v",
                    f"{CHATDBG_VENV}:/opt/chatdbg_venv:ro",
                    "-v",
                    f"{case_dir}:/results",
                    image,
                    "sleep",
                    "infinity",
                ],
                timeout=120,
            )
            (case_dir / "docker_start.log").write_text(start.stdout)
            if start.returncode != 0:
                meta["status"] = "docker_start_failed"
                continue

            pyver = docker_exec(
                container,
                "python --version; "
                "/opt/chatdbg_venv/bin/python -c "
                "'import sys, chatdbg, numpy; "
                'print(sys.version.split()[0]); print(chatdbg.__file__); print("numpy", numpy.__version__)' + "'",
                timeout=60,
            )
            (case_dir / "environment.log").write_text(pyver.stdout)

            apply_patch = docker_exec(container, "cd /testbed && git apply -v -", timeout=120, input_text=eval_item["test_patch"])
            (case_dir / "apply_test_patch.log").write_text(apply_patch.stdout)
            if apply_patch.returncode != 0:
                meta["status"] = "test_patch_failed"
                continue

            repro = docker_exec(container, f"cd /testbed && timeout 180s {test_cmd}", timeout=240)
            (case_dir / "reproduce_without_chatdbg.log").write_text(repro.stdout)
            meta["plain_test_returncode"] = repro.returncode

            chat_cmd = (
                "cd /testbed && "
                f"printf 'why\\nq\\n' | timeout {args.timeout}s /opt/chatdbg_venv/bin/chatdbg "
                f"--model={shlex.quote(args.model)} --log={shlex.quote(chatdbg_log)} --format=text "
                f"-c continue -m pytest -q {' '.join(shlex.quote(t) for t in tests)}"
            )
            env = {
                "DEEPSEEK_API_KEY": api_key,
                "DEEPSEEK_API_BASE": api_base,
                "CHATDBG_MODEL": args.model,
                "LITELLM_LOG": "ERROR",
                "PYTHONWARNINGS": "ignore:backend2gui is deprecated:DeprecationWarning",
                "MPLBACKEND": "agg",
            }
            chat = docker_exec(container, chat_cmd, timeout=args.timeout + 90, env=env)
            (case_dir / "chatdbg_stdout.log").write_text(chat.stdout)
            meta["chatdbg_returncode"] = chat.returncode

            log_summary = summarize_log(case_dir / f"{iid}.chatdbg.yaml")
            meta.update(log_summary)
            meta["status"] = "completed" if log_summary.get("chatdbg_log_found") else "no_chatdbg_log"
        except subprocess.TimeoutExpired as exc:
            meta["status"] = "timeout"
            meta["timeout_cmd"] = " ".join(exc.cmd) if isinstance(exc.cmd, list) else str(exc.cmd)
            if exc.stdout:
                (case_dir / "timeout_stdout.log").write_text(str(exc.stdout))
        finally:
            stop = run(["docker", "rm", "-f", container], timeout=60)
            (case_dir / "docker_cleanup.log").write_text(stop.stdout)
            meta["end_time"] = time.time()
            meta["elapsed_sec"] = meta["end_time"] - meta["start_time"]
            (case_dir / "metadata.json").write_text(json.dumps(meta, indent=2, sort_keys=True))
            summary.append(meta)
            (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
