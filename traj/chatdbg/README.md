# ChatDBG diagnostic-call experiment

These ten SWE-bench Verified `matplotlib` instances were run on May 26, 2026. The runner applied the benchmark test patch, reproduced the selected failing test, then started ChatDBG with `deepseek/deepseek-chat` and sent one `why` query. The experiment measures diagnostic interactions; it does not generate or evaluate repair patches.

- `instances_swebench_verified_10_matplotlib_py311_chatdbg_daira.yaml`: the ten instance IDs and execution environments.
- `run_chatdbg_matplotlib_subset.py`: original experiment runner. It requires Docker, ChatDBG, the referenced benchmark evaluation file, PyYAML, the original environment paths and an API key provided through the environment. Its default paths refer to the original server; pass `--instances`, `--evals` and `--out` to adapt them.
- `logs/*.chatdbg.yaml`: original ChatDBG dialog logs, one per instance.
- `completed_summary.csv`: archived per-instance counts and failing test commands.
- `verify_calls.py`: recounts `type: call` entries in the dialog logs and checks the archived counts. Run `python3 verify_calls.py` with PyYAML installed.

Across ten sessions, there were 852 debugger/tool calls: a mean of 85.2, median of 64 and range of 28 to 174. One session (`matplotlib__matplotlib-24149`, 174 calls) ended with an API timeout. The runner still recorded its status as `completed` because it found a log; the ChatDBG log marks the query incomplete. One `why` query per session does not mean one model API request. Per-request model API counts were not recorded. Debugger calls include unsuccessful calls and are not equivalent to DAIRA high-level tool calls.
