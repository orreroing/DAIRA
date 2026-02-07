# DAIRA: Dynamic Analysis-enhanced Issue Resolution Agent

**DAIRA** is an automated repair framework that deeply integrates dynamic analysis into the agent decision loop. By adopting a **Test Tracing-Driven workflow** and equipping agents with **"Perspective Glasses"** (Dynamic Observability), DAIRA mitigates the issue of blind exploration common in existing static analysis-based approaches.

## 📂 Repository Structure

### 🏗️ Project Overview

The directory structure is organized to align strictly with the Research Questions (RQs) and experimental setup described in the manuscript.

```text
DAIRA/
├── Motivating Example/          # 🔎 Case Studies with Gemini 3 Flash Preview ("Perspective Glasses" in action) 
│   ├── sympy_17630_traj/        # Full execution trajectory for SymPy-17630
│   └── matplotlib-22719_traj/   # Full execution trajectory for Matplotlib-22719
├── prompt/                      # 🧠 Prompts
├── swebench result/             # 📊 Evaluation Results
│   ├── DAIRA/                   # Ours Results
│   └── SWE-agent/               # Baseline Results
├── RQ1-Effectiveness/           # 🏆 RQ1: Effectiveness Analysis (vs. SOTA)
├── RQ2-Model_Impact/            # 🤖 RQ2: Model Generalizability Analysis
├── RQ3-Robustness/              # 🛡️ RQ3: Difficulty Robustness Analysis
├── RQ4-Ablation_Study/          # 🧪 RQ4: Ablation Study (Component Contribution)
└── result_image/                # 🖼️ Paper Experimental Results Figures
└──traj/                         #Full Execution Trajectory For All
```
### 1. Qualitative Analysis
* **`Motivating Example/`**: Detailed case studies demonstrating the **"Perspective Glasses"** effect.
    * **`sympy_17630_traj/`** & **`matplotlib-22719_traj/`**: Contains full execution trajectories (`.traj`), and patches (`.patch`).
    * These examples illustrate how DAIRA successfully resolves complex defects (e.g., polymorphic control flows, implicit type degradation) where baselines failed due to a lack of intermediate execution state observation.

### 2. Core Components
* **`prompt/`**: Contains the **System Prompts** and **Analyse Prompts** designed to guide the agent in utilizing dynamic analysis tools and receiving structured analysis report.
* **`swebench result/`**: The raw evaluation logs (JSON format) generated from running DAIRA and baseline methods on the **SWE-bench Verified** dataset. Includes results for:
    * `DAIRA` (Ours)
    * `SWE-agent` (Baseline)
    * Across models: `DeepSeek V3.2`, `Gemini 3 Flash Preview`, `Qwen 3 Coder Flash`.
### 3. Experimental Results (RQ1 - RQ4)
This section corresponds to the quantitative evaluation of the framework:

* **`RQ1-Effectiveness/`**: Data and scripts for **Effectiveness Analysis**.
    * `SOTA_Methods.xlsx` :Instance-level resolution data for DAIRA and SOTA baselines (e.g., SWE-agent, AutoCodeRover).
    * `weien_plot.py` : performance comparison figures.
* **`RQ2-Model_Impact/`**: Data for **Model Generalizability Analysis**.
    * `Different_model.xlsx`:Evaluates the framework's performance across different LLM backbones (`DeepSeek`, `Gemini`, `Qwen`) to verify that DAIRA's improvements are model-agnostic.
    * `different_model_performence.py`:Code for generating performance analysis charts across different models.
* **`RQ3-Robustness/`**: Data for **Robustness Analysis**.
    * `different_method_different_level_reslovedrate.py`: Code for plotting resolution rate maps of DAIRA and other state-of-the-art methods across tasks of varying difficulty.
    * The data for the tables in this section is based on the `Different_model.xlsx` data sheet.
* **`RQ4-Ablation_Study/`**: Detailed Data for **Ablation Study**.
    * Verifies the contribution of individual components by removing them:
        * `without Dynamic Analysis Tool`
        * `without Test Tracing-Driven Workflows`
        * `without Trace Log Semantic Analysis`
        * DAIRA(ours)
        * SWE-agent(baseline)

### 4. 📢 Code Availability
The full source code of the DAIRA framework will be released publicly upon the formal publication of the paper.
