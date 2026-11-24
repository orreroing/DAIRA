# DAIRA: Dynamic Analysis-enhanced Issue Resolution Agent

DAIRA is a SWE-agent-based issue resolution agent that collects runtime traces and turns them into structured reports for code exploration and repair.

## Experiments

| Research question | Contents | Directory |
| --- | --- | --- |
| RQ1 · Effectiveness | SWE-bench Verified baseline comparisons and plotting script | [RQ1-Effectiveness](RQ1-Effectiveness/) |
| RQ2 · Comparison with Existing Dynamic Analysis Methods | ADI and DAIRA skill comparison and ChatDBG diagnostic sessions | [RQ2-Dynamic_Analysis_Comparison](RQ2-Dynamic_Analysis_Comparison/) |
| RQ3 · Multilingual Generalization | DAIRA and SWE-agent trajectories and predicted patches for C/C++, Ruby, and Java with DeepSeek V3.2 and DeepSeek-V4-Pro | [RQ3-Multilingual_Generalization](RQ3-Multilingual_Generalization/) |
| RQ4 · Model Impact | Per-task resolution and cost data across backbone models, with a plotting script | [RQ4-Model_Impact](RQ4-Model_Impact/) |
| RQ5 · Robustness | Results by task difficulty and the difficulty-comparison plotting script | [RQ5-Robustness](RQ5-Robustness/) |
| RQ6 · Ablation Study | DeepSeek V3.2 results for SWE-agent, full DAIRA, and DAIRA component ablations | [RQ6-Ablation_Study](RQ6-Ablation_Study/) |

## Code and Shared Artifacts

- DAIRA runtime, tracing tools, configurations, and setup instructions. [DAIRA/](DAIRA/README.md)
- Standalone DAIRA skill and installation instructions. [DAIRA_skill/](DAIRA_skill/README.md)
- System and trace-analysis prompts. [prompt](prompt)
- Matplotlib-22719 and SymPy-17630 case studies with trajectories, predicted patches, and trace reports. [Motivating Example/](Motivating%20Example/)
- SWE-bench Verified evaluation reports for DAIRA and SWE-agent across backbone models. [swebench result/](swebench%20result/)
- Agent trajectories and predicted patches, including the RQ2 and RQ3 artifacts. [traj/](traj/)
- Plot PDFs. [result_image/](result_image/)
