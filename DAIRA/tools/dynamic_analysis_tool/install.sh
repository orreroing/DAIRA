#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1 && [ -x /root/python3.11/bin/python3 ]; then
  ln -sf /root/python3.11/bin/python3 /root/tools/dynamic_analysis_tool/bin/python3
fi

python3 - <<'PY' >/dev/null 2>&1 || python3 -m pip install hunter
import hunter
PY
