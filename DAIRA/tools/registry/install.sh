#!/usr/bin/env bash

# script_dir=$(dirname "$(readlink -f "$0")")
bundle_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if ! command -v python >/dev/null 2>&1 && [ -x /root/python3.11/bin/python ]; then
  ln -sf /root/python3.11/bin/python "$bundle_dir/bin/python"
fi
if ! command -v python3 >/dev/null 2>&1 && [ -x /root/python3.11/bin/python3 ]; then
  ln -sf /root/python3.11/bin/python3 "$bundle_dir/bin/python3"
fi

export PYTHONPATH="$bundle_dir/lib":${PYTHONPATH:-}
