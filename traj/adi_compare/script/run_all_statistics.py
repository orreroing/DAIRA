import os
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parent
scripts = [
    root / '01_tool_call_failures/scripts/recompute_failure_statistics.py',
    root / '02_non_gold_file_exploration/scripts/recompute_exploration_statistics.py',
]
env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
for script in scripts:
    subprocess.run([sys.executable, str(script)], check=True, env=env)
print('PASS: both analyses reproduced the archived results.')
