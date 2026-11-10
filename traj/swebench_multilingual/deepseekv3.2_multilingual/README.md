# DeepSeek V3.2 multilingual trajectories and evaluation

This directory contains 129 DAIRA runs and 129 SWE-agent runs: 42 C/C++, 44 Ruby, and 43 Java tasks per method. The artifact pairs retain the existing directory layout and converted trajectory format.

```text
DAIRA/<instance_id>/
  <instance_id>_traj.json
  <instance_id>.pred
sweagent/<instance_id>/
  <instance_id>_traj.json
  <instance_id>.pred
evaluation/
  summary.csv
  instances.csv
  manifest.json
  reports/<method>/<instance_id>/report.json
  reports/runs/<run_id>/results.json
```

Each trajectory is a JSON list of steps with `step`, `thought`, `action`, and `observation`. Each `.pred` contains `model_name_or_path`, `instance_id`, and `model_patch`. The 258 trajectories and 258 prediction files are byte-for-byte identical to commit `438d402fc89403a5c52d1795c46815ea93a1d68c`; the updated Java results come from reevaluating those patches with cached Gradle distributions.

| Language | DAIRA | SWE-agent | Relative improvement |
|---|---:|---:|---:|
| C/C++ | 27/42 (64.29%) | 25/42 (59.52%) | +8.00% |
| Ruby | 28/44 (63.64%) | 25/44 (56.82%) | +12.00% |
| Java | 31/43 (72.09%) | 25/43 (58.14%) | +24.00% |
| Total | **86/129 (66.67%)** | **75/129 (58.14%)** | **+14.67%** |
| Average (macro) | 66.67% | 58.16% | +14.63% |

Relative improvement is `(DAIRA rate / SWE-agent rate - 1) * 100%`. Total pools all 129 tasks; Average gives each language equal weight. Empty patches and evaluation errors remain in the denominator.

C/C++ and Ruby use the complete November 8, 2026 evaluation runs. Java uses the complete November 9, 2026 runs with the same cached images, dataset, official harness, two workers, and 1,800-second test timeout for both methods. The original generation command timeouts were 600 seconds for DAIRA and 300 seconds for SWE-agent; these are separate from the evaluation timeout.

The official harness commit is `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`; the dataset commit is `846e647b9f33c0b51b739d005d13d85493c9af09`. The manifest records the Java dataset hash and cache image IDs.

`evaluation/instances.csv` maps every artifact pair to its selected run, outcome, and hashes. `evaluation/manifest.json` adds file hashes and links to the official reports. The four run summaries are preserved verbatim. The two November 8 summaries include their original Java results; those Java entries are superseded by the November 9 runs in the current table and index. Instance reports are included for all 251 tasks that produced one; five empty predictions and two evaluation errors retain their statuses without an instance report.

The five empty predictions are preserved. In particular, `sweagent/fastlane__fastlane-21857` has an empty exported prediction despite a submitted diff in its trajectory and remains an empty-patch outcome. Autosubmitted trajectories can lack an explicit `submit` diff. These cases are identified by `submission_binding` in the index.
