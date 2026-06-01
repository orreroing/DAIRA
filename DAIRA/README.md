# DAIRA Code

This directory contains the DAIRA agent implementation built on top of SWE-agent. It keeps the runnable code and core configuration files only; experiment outputs, trajectories, cached files, local environment files, and evaluation artifacts are intentionally excluded.

## Contents

- `sweagent/`: DAIRA runtime, model wrappers, agent logic, trace summarization, and runners.
- `tools/`: tool bundles used by the agent, including dynamic analysis tools for Python, Java, Ruby, C/C++, and JavaScript.
- `config/`: core DAIRA configuration files.
- `tests/`: source tests for the runtime and tool parsing behavior.
- `pyproject.toml`: Python packaging metadata inherited from SWE-agent and adapted for local installation.

## Installation

From this directory, install DAIRA in editable mode. This follows the upstream
SWE-agent source installation flow:

```bash
python -m pip install --upgrade pip
python -m pip install --editable .
```

DAIRA follows SWE-agent's runtime model, so the default environment setup
requires a working Docker installation and permission to access the Docker
daemon, for example `docker ps` should run successfully for your user.

Check that the CLI is available:

```bash
sweagent --help
```

Set model credentials with environment variables or a local `.env` file. Do not
commit local secrets.

```bash
export OPENAI_API_KEY=...
```

## Example Usage

DAIRA keeps SWE-agent's command-line interface. After installation, use the
`sweagent` command and pass DAIRA's default config explicitly.

Run one issue. The example below uses a local problem statement file so it does
not depend on GitHub API rate limits. The first run may take a few minutes while
Docker images and the runtime environment are prepared:

```bash
sweagent run \
  --config config/default_dyana_example4.yaml \
  --agent.model.name deepseek-v4-flash \
  --agent.model.api_base https://api.deepseek.com \
  --env.repo.github_url https://github.com/SWE-agent/test-repo \
  --problem_statement.path examples/test_repo_issue.md
```

To make a quick installation smoke test without calling a model, replace the
model with `instant_empty_submit`:

```bash
sweagent run \
  --config config/default_dyana_example4.yaml \
  --agent.model.name instant_empty_submit \
  --env.repo.github_url https://github.com/SWE-agent/test-repo \
  --problem_statement.path examples/test_repo_issue.md
```

Run a small SWE-bench batch:

```bash
sweagent run-batch \
  --config config/default_dyana_example4.yaml \
  --agent.model.name deepseek-v4-flash \
  --agent.model.api_base https://api.deepseek.com \
  --instances.type swe_bench \
  --instances.subset lite \
  --instances.split dev \
  --instances.slice :3
```

Language-specific validation configs are available at:

- `config/context_retrieval.yaml`
- `config/context_retrieval_c.yaml`
- `config/context_retrieval_java.yaml`
- `config/context_retrieval_javascript.yaml`
- `config/context_retrieval_ruby.yaml`

Small multilingual SWE-bench subsets are under `config/multilingual_subsets/`; larger bookkeeping subsets are under `config/multilingual_subsets_all/`.

## Notes

This code is derived from SWE-agent and keeps the original MIT license. DAIRA-specific changes add dynamic-analysis-driven workflows, trace summarization, multilingual trace tools, and related agent configuration.

The Python package directory is intentionally kept as `sweagent/` to preserve the
upstream import paths, CLI entry point, and configuration compatibility.
