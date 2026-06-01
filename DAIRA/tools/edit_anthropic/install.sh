#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1 && [ -x /root/python3.11/bin/python3 ]; then
  ln -sf /root/python3.11/bin/python3 /root/tools/edit_anthropic/bin/python3
fi
if ! command -v python >/dev/null 2>&1 && [ -x /root/python3.11/bin/python ]; then
  ln -sf /root/python3.11/bin/python /root/tools/edit_anthropic/bin/python
fi

# Ignore failures, see https://github.com/SWE-agent/SWE-agent/issues/1179
pip install 'tree-sitter==0.21.3' || true
pip install 'tree-sitter-languages' || true
