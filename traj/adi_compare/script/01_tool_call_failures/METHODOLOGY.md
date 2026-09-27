# 1.1 Tool Call Failures and Interface Usage Costs

## File inventory

| File | Contents |
|---|---|
| `data/raw_tool_call_evidence.json` | 394 standard ADI calls, 328 standard DAIRA calls, and other actions mentioning the tools with their observations. Audited wrapped invocations are selected from the latter. |
| `data/reference_failure_audit.json` | Archived classifications and summaries for all 736 calls, used as a consistency reference. |
| `data/redirected_log_evidence.json` | Logs read at steps 32 and 35 of DAIRA task `django__django-7530`, confirming environment errors at steps 31 and 34, respectively. |
| `data/adi_report.json`, `data/daira_report.json` | Complete task inventories, including tasks that did not invoke a tool. |
| `scripts/recompute_failure_statistics.py` | Classification rules, 14 audited wrapped invocations, six manual classification overrides, CSV exports, and consistency assertions. |
| `scripts/extract_remote_debug_calls.py` | Read-only extraction of commands and observations from remote trajectories; recorded commands are not executed. |
| `results/section_1_1_failure_comparison.csv` | Three-row comparison used in Section 1.1. |
| `results/all_tool_calls_736.csv` | Task ID, step, command, complete observation, category, and failure flags for each call. |
| `results/confirmed_failures_189.csv` | Individual records for 162 ADI failures and 27 DAIRA failures. |
| `results/per_task_call_statistics_200.csv` | 100 tasks per method, with call counts, interface errors, other failures, and first-call category. |
| `results/failure_categories.csv` | Calls and distinct tasks for each category, including non-failure categories. A task may appear in multiple categories; task counts are not additive. |
| `results/manual_classification_overrides_6.csv` | Six individually reviewed classifications overriding the general rules. |
| `results/classified_calls_and_summary.json` | Complete regenerated classifications and summaries. Both standard-entrypoint and wrapped-inclusive scopes are retained; Section 1.1 uses `summary.all`. |

## Counting rules

Each recorded invocation of a dynamic-analysis entry point counts once. This includes ADI `list-frames`, `break`, `exec`, and `call-tree`, DAIRA `run_hunter_trace`, and audited invocations through absolute paths, `python -m ADI`, or compatibility copies of the tools. Reading tool source, requesting help, or reading an existing log does not count as a new analysis call. Diagnostic experiments using the underlying Hunter API directly are excluded.

Beyond the standard entry points, the audit identifies eight ADI calls and six DAIRA calls, giving denominators of 402 and 334. These selections were manually checked for this fixed set of trajectories. They are not a general-purpose invocation detector for new experiments.

Four categories are grouped as **interface usage errors**:

| Internal category | Meaning | ADI calls |
|---|---|---:|
| `target_format_error` | Invalid target format | 91 |
| `target_location_error` | Specified line is outside a traceable function | 8 |
| `command_argument_error` | Invalid subcommand arguments | 9 |
| `exec_expression_error` | Error while executing a frame-level expression | 16 |

The comparison groups `target_not_reached`, `no_trace`, `environment_error`, and `analysis_context_limit` under **target dynamic information not obtained**. ADI has 36 target-not-reached calls and two environment errors, totaling 38. DAIRA has 19 no-trace calls, four environment errors, and four analysis context-limit errors, totaling 27. This grouped label does not imply that all such failures originate in the tracer itself.

`evidence_returned` means that tracing or query information was returned. It does not establish that the information was complete, correct, or sufficient for localization. Exceptions raised by the target program and successfully captured by the tool are not call failures. `empty_unconfirmed` denotes an empty output: three ADI calls and one DAIRA call. These remain in the denominator but count as neither confirmed failures nor returned evidence.

All call failure percentages use the full call denominators: 402 for ADI and 334 for DAIRA. The numbers of tasks invoking the tools are 93 and 100, respectively. Call counts and task counts are different units.

## Manual review decisions

The script's `extras` mapping identifies 14 wrapped or compatibility-copy invocations. Its `manual` mapping records six classifications: two reported startup syntax errors, two environment errors verified through redirected logs, and two reports explicitly stating that no actual trace was available. Each entry retains the task ID and zero-based step index.

These decisions are part of the audit procedure, not counts inferred from the aggregate table. The supporting observations are included. Applying the method to new trajectories requires reviewing these decisions again rather than reusing the archived task IDs and step indices.
