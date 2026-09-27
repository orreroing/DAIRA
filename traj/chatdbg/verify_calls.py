import csv
import pathlib
import statistics

import yaml

root = pathlib.Path(__file__).resolve().parent
with (root / 'completed_summary.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 10
counts = []
complete_diagnoses = 0
for row in rows:
    iid = row['instance_id']
    path = root / 'logs' / f'{iid}.chatdbg.yaml'
    docs = yaml.safe_load(path.read_text(encoding='utf-8'))
    assert len(docs) == 1
    doc = docs[0]
    queries = [step for step in doc['steps'] if step.get('output', {}).get('type') == 'chat']
    assert len(queries) == int(row['llm_queries']) == 1
    calls = sum(out.get('type') == 'call' for query in queries for out in query['output'].get('outputs', []))
    assert calls == int(row['debug_function_calls']), iid
    counts.append(calls)
    complete_diagnoses += doc.get('stats', {}).get('completed') is True
assert len(counts) == 10 and sum(counts) == 852
print('Sessions:', len(counts))
print('Debugger/tool calls:', sum(counts))
print('Mean:', statistics.mean(counts))
print('Median:', statistics.median(counts))
print('Range:', min(counts), max(counts))
print('ChatDBG query completed:', complete_diagnoses, 'of', len(counts))
print('Actual model API request count: not recorded in these logs')
