#!/usr/bin/env bash
set -euo pipefail

java -version >/dev/null
if ! command -v python3 >/dev/null 2>&1 && [ -x /root/python3.11/bin/python3 ]; then
  ln -sf /root/python3.11/bin/python3 /root/tools/java_dynamic_analysis_tool/bin/python3
fi
if ! command -v jfr >/dev/null 2>&1; then
  echo "Warning: JDK 'jfr' command not found. run_java_trace will execute the target command but cannot print JFR samples in this image."
fi
