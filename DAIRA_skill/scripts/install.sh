#!/usr/bin/env bash
set -euo pipefail
language="${1:-}"
case "$language" in
  python) python3 -c 'import hunter' 2>/dev/null || python3 -m pip install hunter ;;
  c|cpp) command -v gcc >/dev/null; command -v g++ >/dev/null ;;
  java) command -v java >/dev/null; command -v jdb >/dev/null; command -v jfr >/dev/null ;;
  ruby) command -v ruby >/dev/null ;;
  *) echo "Usage: bash scripts/install.sh {python|c|cpp|java|ruby}" >&2; exit 2 ;;
esac
python3 --version
