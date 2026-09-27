# ADI vs. DAIRA: Supplementary Data and Statistical Scripts

This package supports Section 1.1, "Tool Call Failures and Interface Usage Costs," and Section 1.2, "Non-Gold File Exploration," of the accompanying comparison document. Prepared on September 25, 2026. The records were copied, extracted, and analyzed without rerunning the repair experiments or modifying remote files.

## Contents

| Analysis | Summary table | Detailed results | Local reproduction script |
|---|---|---|---|
| 1.1 Tool call failures | `01_tool_call_failures/results/section_1_1_failure_comparison.csv` | Per-call evidence, confirmed failures, and per-task statistics in the same results directory | `01_tool_call_failures/scripts/recompute_failure_statistics.py` |
| 1.2 Non-gold file exploration | `02_non_gold_file_exploration/results/section_1_2_exploration_comparison.csv` | Paired task comparisons, file-level records, and excluded Git listing steps in the same results directory | `02_non_gold_file_exploration/scripts/recompute_exploration_statistics.py` |

Each analysis has a `METHODOLOGY.md` explaining the denominators, fields, exclusions, and manual review decisions. CSV files use UTF-8 with a BOM for compatibility with Excel. Step indices are zero-based and refer to `trajectory[step]` in the original `.traj` file.

## Reported results

### 1.1 Tool call failures

| Failure category | ADI | DAIRA |
|---|---:|---:|
| Target dynamic information not obtained | 38/402 (9.45%) | 27/334 (8.08%) |
| Interface usage errors | 124/402 (30.85%) | 0/334 (0.00%); no such errors observed |
| All confirmed failures | 162/402 (40.30%) | 27/334 (8.08%) |

"Target dynamic information not obtained" follows the grouped label in the comparison document. It includes missing targets or traces, environment errors, and analysis context-limit errors. It should not be interpreted as a pure tracing failure rate. The detailed records preserve the original categories.

### 1.2 Non-gold file exploration

| Task group | ADI mean | DAIRA mean | DAIRA reduction |
|---|---:|---:|---:|
| All 100 tasks | 37.27 | 28.75 | 22.86% |
| 59 tasks resolved by both methods | 37.98 | 27.24 | 28.29% |

These means exclude designated Git file-listing steps. DAIRA involves fewer non-gold files in 70 of the 100 tasks. The metric counts distinct paths mentioned in retained trajectory steps, rather than operating-system-level file accesses.

## Reproduce locally

Python 3.10 or later is required. The scripts use only the standard library; no network access, SSH connection, or third-party packages are needed. From the package root, run:

```powershell
python ./run_all_statistics.py
```

The command regenerates the files in both `results/` directories without modifying `data/`. Assertions compare call classifications, per-task file counts, and aggregate statistics against the archived results. A successful run ends with `PASS`. Each analysis script can also be run separately.

## Sources and reproduction scope

- Remote host: `orrero@172.16.108.11`.
- Experiment root: `/data/home/orrero/wzh/adi_compare`.
- Original trajectories: `<experiment_root>/<adi_or_daira>/<task_id>/<task_id>.traj`.
- Gold file source: `/data/home/orrero/wzh/baseline/SWE-agent/expr_data/DAIRA/localization_eval/per_instance_localization.csv`.
- Original exploration metric: `/data/home/orrero/wzh/baseline/SWE-agent/scripts/analyze_exploration_efficiency.py`.

The call analysis includes commands, complete call observations, audited wrapped invocations, and supplementary redirected logs. Failure classifications can therefore be recomputed offline.

The exploration analysis includes each step's action, paths extracted from actions and observations, gold file sets, trajectory SHA-256 hashes, and observation SHA-256 hashes. These support offline filtering, deduplication, pairing, and aggregation. The package does not include all 200 full trajectories, which contain repeated conversation context. Local reproduction covers extracted path sets through final metrics. Re-extracting paths from all original observation text requires access to the remote trajectories.

Both `extract_remote_*.py` scripts read fixed remote paths and write JSON to standard output. They do not execute recorded actions or create remote files. From this directory, extract fresh copies as follows:

```powershell
Get-Content -Raw './01_tool_call_failures/scripts/extract_remote_debug_calls.py' | ssh -o BatchMode=yes orrero@172.16.108.11 'python3 -' | Set-Content -Encoding utf8 './new_tool_call_evidence.json'
Get-Content -Raw './02_non_gold_file_exploration/scripts/extract_remote_file_evidence.py' | ssh -o BatchMode=yes orrero@172.16.108.11 'python3 -' | Set-Content -Encoding utf8 './new_file_evidence.json'
```

Compare fresh extractions with the archived evidence before replacing any inputs. Changes to remote trajectories or the original metric script may change the results.

`file_checksums.csv` records file sizes and SHA-256 hashes at packaging time, excluding itself. `validation_log.txt` records reproduction and evidence consistency checks. The original analysis directory was left unchanged. The package contains original paths and experiment logs and has not been anonymized for submission. Raw evidence and the frozen original metric script retain their original text and bytes, including any non-English text.
