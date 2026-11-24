# DAIRA: Dynamic Analysis-enhanced Issue Resolution Agent

**DAIRA** is an automated repair framework that deeply integrates dynamic analysis into the agent decision loop. By adopting a **Test Tracing-Driven workflow** and equipping agents with **"Perspective Glasses"** (Dynamic Observability), DAIRA mitigates the issue of blind exploration common in existing static analysis-based approaches.

**📢 NEW！！！**

**📊 Execution trajectories and predicted patches are available in `traj/`.**

**🌐 Multilingual runs with DeepSeek V3.2 and DeepSeek-V4-Pro are available in [`traj/swebench_multilingual/`](traj/swebench_multilingual/).**

**🧩 DAIRA is now available as a standalone skill in `DAIRA_skill/`.**

## 📂 Repository Structure

### 🏗️ Project Overview

The directory structure is organized to align strictly with the Research Questions (RQs) and experimental setup described in the manuscript.

```text
DAIRA/
├── DAIRA/                           # 🧩 Released source code and core configs
├── DAIRA_skill/                     # 🧩 Standalone DAIRA skill
├── Motivating Example/              # 🔎 Case studies with Gemini 3 Flash Preview
│   ├── Matplotlib-22719/
│   └── Sympy-17630/
├── prompt                           # 🧠 System and trace-analysis prompts
├── swebench result/                 # 📊 SWE-bench Verified evaluation reports
├── RQ1-Effectiveness/               # 🏆 RQ1: Effectiveness Analysis (vs. SOTA)
├── RQ2-Dynamic_Analysis_Comparison/ # 🔍 RQ2: ADI and ChatDBG comparison artifacts
├── RQ3-Multilingual_Generalization/ # 🌐 RQ3: Multilingual trajectories and predictions
├── RQ4-Model_Impact/                # 🤖 RQ4: Model Impact
├── RQ5-Robustness/                  # 🛡️ RQ5: Difficulty Robustness Analysis
├── RQ6-Ablation_Study/              # 🧪 RQ6: Ablation Study (Component Contribution)
├── result_image/                    # 🖼️ Paper experimental figures
└── traj/                            # Execution trajectories and predicted patches
    ├── adi_compare/                 # RQ2: ADI and DAIRA skill runs and analysis
    ├── chatdbg/                     # RQ2: ChatDBG diagnostic sessions
    └── swebench_multilingual/       # RQ3: DeepSeek V3.2 and DeepSeek-V4-Pro
```

### 1. Qualitative Analysis

* **`Motivating Example/`**: Detailed case studies demonstrating the **"Perspective Glasses"** effect.
    * The `Matplotlib-22719/` and `Sympy-17630/` directories contain converted trajectories (`*_traj.json`), predicted patches (`*.pred`), and trace report figures.
    * These examples illustrate how DAIRA successfully resolves complex defects (e.g., polymorphic control flows, implicit type degradation) where baselines failed due to a lack of intermediate execution state observation.

### 2. Core Components

* **`DAIRA/`**: Released implementation of the DAIRA agent. It contains the SWE-agent-based runtime, dynamic analysis tool bundles, trace summarization logic, default configuration (`config/DAIRA_DEFAULT.yaml`), and language-specific validation configs for C/C++, Java, and Ruby. See **`DAIRA/README.md`** for installation and usage.
* The standalone DAIRA skill and its installation instructions are in [`DAIRA_skill/`](DAIRA_skill/README.md).
* The `prompt` file contains the **System Prompts** and **Analyse Prompts** for tool use and trace report generation.
* **`swebench result/`**: The raw evaluation logs (JSON format) generated from running DAIRA and baseline methods on the **SWE-bench Verified** dataset. Includes results for:
    * `DAIRA` (Ours)
    * `SWE-agent` (Baseline)
    * Across models: `DeepSeek V3.2`, `Gemini 3 Flash Preview`, `Qwen 3 Coder Flash`.

### 3. Experimental Results (RQ1 - RQ6)

This section corresponds to the quantitative evaluation of the framework:

* **`RQ1-Effectiveness/`**: Data and scripts for **Effectiveness Analysis**.
    * `SOTA_Methods.xlsx` :Instance-level resolution data for DAIRA and SOTA baselines (e.g., SWE-agent, AutoCodeRover).
    * `weien_plot.py` : performance comparison figures.
* **`RQ2-Dynamic_Analysis_Comparison/`** indexes the ADI and DAIRA skill runs, interface failure and non-gold file exploration analyses, and ChatDBG diagnostic logs. [RQ2 directory](RQ2-Dynamic_Analysis_Comparison/)
* **`RQ3-Multilingual_Generalization/`** indexes C/C++, Ruby, and Java runs with DeepSeek V3.2 and DeepSeek-V4-Pro. Both model directories contain converted trajectories (`*_traj.json`) and predicted patches (`*.pred`) for DAIRA and SWE-agent. [RQ3 directory](RQ3-Multilingual_Generalization/)
* **`RQ4-Model_Impact/`**: Data for **Model Impact Analysis**.
    * `Different_model.xlsx`:Evaluates the framework's performance across different LLM backbones (`DeepSeek`, `Gemini`, `Qwen`) to verify that DAIRA's improvements are model-agnostic.
    * `different_model_performence.py`:Code for generating performance analysis charts across different models.
* **`RQ5-Robustness/`**: Data for **Robustness Analysis**.
    * `different_method_different_level_reslovedrate.py`: Code for plotting resolution rate maps of DAIRA and other state-of-the-art methods across tasks of varying difficulty.
    * The data for the tables in this section is based on the `Different_model.xlsx` data sheet.
* **`RQ6-Ablation_Study/`**: Detailed Data for **Ablation Study**.
    * Verifies the contribution of individual components by removing them:
        * `without Dynamic Analysis Tool`
        * `without Test Tracing-Driven Workflows`
        * `without Trace Log Semantic Analysis`
        * DAIRA(ours)
        * SWE-agent(baseline)

### 4. 📢 Code Availability

The released source code is available under **`DAIRA/`**. The implementation includes the DAIRA runtime, dynamic analysis tools, core configuration files, and a reproducible test-repo example. Please refer to **`DAIRA/README.md`** for setup and running instructions.
