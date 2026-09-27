# 1.2 Non-Gold File Exploration

## File inventory

| File | Contents |
|---|---|
| `data/per_step_file_evidence.json` | Per-step actions, action and observation path sets, gold sets, trajectory hashes, and observation hashes for 200 trajectories. Includes the original extraction script text and its SHA-256 hash. |
| `data/gold_files_100_tasks.json` | Gold source-patch file sets for 100 tasks. |
| `data/reference_exploration_results.json` | Archived per-task and aggregate statistics, before and after filtering. |
| `scripts/original_exploration_metric.py` | Frozen original extraction and metric implementation; its byte-level SHA-256 matches the source record. Imported for verification, rather than used as the package's direct entry point. |
| `scripts/extract_remote_file_evidence.py` | Reads remote trajectories and gold data, extracts per-step paths, and writes JSON to standard output. |
| `scripts/recompute_exploration_statistics.py` | Reapplies filtering, deduplication, gold subtraction, pairing, and aggregation to the frozen evidence; verifies historical per-task results. |
| `results/section_1_2_exploration_comparison.csv` | Means and reductions for all 100 tasks and the 59 tasks resolved by both methods. |
| `results/paired_task_comparison_100.csv` | Both methods' counts, their difference, and shared-resolution status for each task. |
| `results/per_task_exploration_statistics_200.csv` | Counts before and after filtering, gold counts, and trajectory hashes for each method-task pair. |
| `results/filtered_file_details.csv` | Every retained file, its gold status, and its first retained step for each method-task pair. |
| `results/filtered_file_sets.json` | Gold, retained, and retained non-gold file sets for each method-task pair. |
| `results/excluded_git_listing_steps.csv` | Excluded actions, step indices, and path sets for checking the filter's effect. |
| `results/summary.json` | Full-precision means, reductions, and paired comparison counts. |

## Metric definition

For each task, combine Python file paths extracted from the actions and observations of retained steps, normalize and deduplicate them using the original script, and subtract the task's gold file set. Average the resulting counts with equal weight per task. Gold files come from the `gold_files` column of the original localization evaluation CSV, not the agent's submitted patch.

The archived filtering rules are preserved:

1. Skip a step when `action.strip() == 'submit'`.
2. Exclude the entire step, including its action and observation, if the action contains `git ` and any of `--stat`, `--name-only`, `--name-status`, or `ls-files`. This is string matching, not shell parsing. An action containing several commands is excluded as a whole when it matches.
3. Retain repository test files. The original extraction regex requires a `.py` path containing a path separator and excludes some environment and temporary paths. It is not a filesystem inventory and does not cover all extensions or root-level files.
4. Deduplicate paths from the remaining steps and subtract gold files. A path mentioned in both an excluded step and a retained step still counts once through the retained step.

This metric counts non-gold paths mentioned in a trajectory, not files actually opened at the operating-system level. Non-gold files may provide necessary context, so each one should not automatically be treated as irrelevant exploration.

## Aggregation

- **All tasks:** the same 100 tasks for both methods. ADI mean: 37.27; DAIRA mean: 28.75; reduction: approximately 22.860209%. DAIRA has fewer paths in 70 tasks, the same count in three, and more in 27.
- **Both resolved:** the intersection of resolved task IDs from the two reports, containing 59 tasks. ADI mean: approximately 37.98305085; DAIRA mean: approximately 27.23728814; reduction: approximately 28.29094154%.
- **Reduction:** `(ADI mean - DAIRA mean) / ADI mean * 100%`. Calculate using unrounded means, then round for presentation.

Local reproduction rebuilds file sets and means from the archived per-step paths and verifies path extraction from action text. For observations, the snapshot retains paths and hashes rather than all original text. Re-extracting paths from the original observations requires the remote extraction script. Original trajectory paths and SHA-256 hashes are recorded to identify the experiment version.
