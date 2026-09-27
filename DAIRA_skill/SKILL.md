---
name: daira-dynamic-trace
description: Independently trace a Python, C/C++, Java, or Ruby reproduction with DAIRA's bundled tracers and return an LLM-generated semantic workflow report. Use when the failing runtime call path is unclear; requires an OpenAI-compatible model endpoint.
metadata:
  short-description: DAIRA multilingual trace and semantic report
---

# DAIRA Dynamic Trace

This skill contains its own trace scripts and model client. It does not load SWE-agent, register SWE-agent tool bundles, or rely on the action interception in `sweagent/agent/agents.py`.

The repair workflow follows the original `references/DAIRA_DEFAULT.yaml`: reproduce the bug, trace the relevant function and edge cases, map responsibilities, patch, and verify. The original agent prompt remains a reference, not a second prompt sent to the summary model. For the semantic report, `references/trace_summary_prompt.md` preserves DAIRA's existing trace-analysis prompt with the Python-only role made language-neutral. Append only the selected language's name and evidence constraints.

## Setup

The skill needs Python 3 for `scripts/run.py`, `scripts/model.py`, and the Python/C/C++/Java tracers. Install the runtime for the language you need:

```bash
bash scripts/install.sh python  # Python 3 + hunter, installs hunter if missing
bash scripts/install.sh cpp     # gcc and g++ (checks only)
bash scripts/install.sh java    # JDK with java, jdb, jfr (checks only)
bash scripts/install.sh ruby    # Ruby + Python 3 (checks only)
```

On Debian/Ubuntu, the system dependencies can be installed with `sudo apt-get update && sudo apt-get install -y build-essential openjdk-17-jdk ruby python3 python3-pip`. `hunter` is the only tracer-specific Python package; `TracePoint` is built into Ruby. Project dependencies (Python packages, headers and libraries, Maven/Gradle dependencies, Ruby gems) must be available in the target repository's environment. You do not need SWE-agent, LiteLLM, or the OpenAI Python package; the model client uses Python's standard library.

Copy `.env.example` to `.env` **inside this skill**, set `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL_NAME`, and keep `.env` private. Process environment variables override `.env`; `DAIRA_TRACE_API_KEY` and `DEEPSEEK_API_KEY` are accepted as key fallbacks. The endpoint must implement OpenAI-compatible `POST /chat/completions`. Do not print or commit credentials. The model call costs money; do not run live tests without authorization.

## Trace and summarize

Run the command from the target repository's working directory. The arguments are `language reproduction filter function depth`:

```bash
python3 /path/to/DAIRA_skill/scripts/run.py python /absolute/repro.py sympy/printing _print 10
python3 /path/to/DAIRA_skill/scripts/run.py cpp /absolute/repro.cpp Parser parse 10 --compile-flags="-I include -std=c++20" --link-flags="-lm"
python3 /path/to/DAIRA_skill/scripts/run.py java 'mvn -q -Dtest=ParserTest#testParse test' org.example.Parser parse 10
python3 /path/to/DAIRA_skill/scripts/run.py ruby /absolute/repro.rb lib/parser parse 10
```

For C use `c` instead of `cpp`. The `filter` is a filename substring for Python/Ruby, a symbol substring for C/C++, or a class name for Java. Use an unqualified function or method name for Python/Ruby; C/C++ accepts a symbol substring. Start with a small reproduction, run it without tracing first, and keep filters narrow. If no matching events are captured, the command fails before calling the model; revise the target or filter.

`scripts/run.py` calls one of the bundled tracers, verifies that the trace contains matching events, then passes the full native output to `scripts/model.py`. The model reads `references/trace_summary_prompt.md` and returns only the semantic report to stdout. A terminal invocation of a tracer under `scripts/*_dynamic_analysis_tool/bin/` prints the **raw trace only**; use `run.py` for the complete skill.

Only the native trace acquisition changes by language. The C/C++ tracer compiles a reproduction with function instrumentation and may require project flags; the Java tracer uses a focused run command; Python requires `hunter`, Ruby uses `TracePoint`. Do not invent arguments, returns, or calls absent from the native trace. Verify the patch with the reproduction and existing tests after reviewing the semantic report.

## Files

- `scripts/run.py`: independent language dispatcher and trace-to-summary pipeline.
- `scripts/model.py`: `.env` configuration and OpenAI-compatible model call.
- `scripts/{dynamic_analysis_tool,c_dynamic_analysis_tool,java_dynamic_analysis_tool,ruby_dynamic_analysis_tool}/bin/`: copies of the DAIRA trace implementations, with no SWE-agent imports.
- `references/DAIRA_DEFAULT.yaml`: frozen copy of the original repair workflow.
- `references/trace_summary_prompt.md`: frozen semantic-summary prompt with a language-neutral role.
- `.env.example`: model settings template; `.gitignore` excludes `.env`.
