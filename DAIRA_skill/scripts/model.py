"""Standalone DAIRA trace-summary model client; no SWE-agent imports."""

import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "references" / "trace_summary_prompt.md"


def settings(env_file=None):
    """Read simple KEY=VALUE settings without executing the .env file."""
    values = {}
    path = Path(env_file) if env_file else ROOT / ".env"
    if path.is_file():
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"Invalid .env entry in {path}")
            key, value = line.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key.strip()] = value
    values.update(os.environ)
    return values


def summarize_trace(raw_trace, language, env_file=None):
    cfg = settings(env_file)
    key = (
        cfg.get("OPENAI_API_KEY")
        or cfg.get("DAIRA_TRACE_API_KEY")
        or cfg.get("DEEPSEEK_API_KEY")
    )
    if not key:
        raise ValueError("Set OPENAI_API_KEY in the skill .env or process environment")
    base = (
        cfg.get("OPENAI_BASE_URL")
        or cfg.get("DAIRA_TRACE_BASE_URL")
        or "https://api.deepseek.com"
    ).rstrip("/")
    model = cfg.get("OPENAI_MODEL_NAME") or cfg.get("DAIRA_TRACE_MODEL") or "deepseek-chat"
    if not base.startswith(("https://", "http://")):
        raise ValueError("DAIRA_TRACE_BASE_URL must be an HTTP(S) URL")
    url = base if base.endswith("/chat/completions") else base + "/chat/completions"
    prompt = PROMPT.read_text(encoding="utf-8")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": (
                    f"Target language: {language}.\n"
                    "Use only facts present in the source and trace. If inputs, return values, "
                    "or calls are not recorded, say they are unknown. Do not infer missing events.\n\n"
                    "Please analyze the full workflow captured below.\n\n---\n"
                    f"{raw_trace}\n---"
                ),
            },
        ],
        "max_tokens": 6000,
    }
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=90) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Summary API returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError("Summary API is unreachable") from exc
    try:
        if result["choices"][0].get("finish_reason") == "length":
            raise RuntimeError("Summary API hit the output token limit; narrow the trace and retry")
        text = result["choices"][0]["message"]["content"]
        if not isinstance(text, str) or not text.strip():
            raise ValueError("empty model response")
        return text
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError("Summary API returned no usable message") from exc
