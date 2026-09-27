import csv
import hashlib
import json
import pathlib
import runpy
import statistics

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
OUTPUT = ROOT / 'results'
OUTPUT.mkdir(exist_ok=True)
snapshot = json.loads((DATA / 'per_step_file_evidence.json').read_text(encoding='utf-8-sig'))
expected = json.loads((DATA / 'reference_exploration_results.json').read_text(encoding='utf-8-sig'))
metric = ROOT / 'scripts/original_exploration_metric.py'
assert hashlib.sha256(metric.read_bytes()).hexdigest() == snapshot['source_script_sha256'], 'Metric source hash mismatch'
ns = runpy.run_path(str(metric), run_name='metric_import')
original = {(r['arm'], r['id']): r for r in expected['rows']}

def write_csv(name, rows):
    with (OUTPUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def excluded_git_step(action):
    return 'git ' in action and any(flag in action for flag in ['--stat', '--name-only', '--name-status', 'ls-files'])

assert excluded_git_step('git diff --stat HEAD main')
assert not excluded_git_step('cat package/file.py')
rows, details, exclusions, file_sets = [], [], [], []
for r in snapshot['rows']:
    gold = set(r['gold_files'])
    seen, clean = set(), set()
    first_seen = {}
    for step in r['steps']:
        action = step['action']
        assert set(step['action_files']) == ns['extract_files'](action), (r['id'], step['step'], 'action extraction mismatch')
        if action.strip() == 'submit':
            continue
        paths = set(step['action_files']) | set(step['observation_files'])
        seen |= paths
        if excluded_git_step(action):
            exclusions.append(dict(arm=r['arm'], id=r['id'], step=step['step'], action=action, files_in_step=len(paths), files=';'.join(sorted(paths))))
            continue
        clean |= paths
        for path in paths:
            first_seen.setdefault(path, step['step'])
    nongold = clean - gold
    prior = original[r['arm'], r['id']]
    assert gold == set(prior['gold_files'])
    assert r['resolved'] == prior['resolved']
    assert len(seen - gold) == prior['nongold_files_seen'], (r['arm'], r['id'], 'unfiltered result changed')
    assert len(nongold) == prior['nongold_excluding_git_lists'], (r['arm'], r['id'], 'filtered result changed')
    rows.append(dict(arm=r['arm'], id=r['id'], resolved=r['resolved'], nongold_files_after_git_filter=len(nongold), nongold_files_before_git_filter=len(seen-gold), gold_files_total=len(gold), gold_files_seen_after_git_filter=len(clean&gold), trajectory_sha256=r['trajectory_sha256']))
    file_sets.append(dict(arm=r['arm'], id=r['id'], gold_files=sorted(gold), files_after_git_filter=sorted(clean), nongold_files_after_git_filter=sorted(nongold)))
    for path in sorted(clean):
        details.append(dict(arm=r['arm'], id=r['id'], file=path, is_gold=path in gold, first_retained_step=first_seen[path]))

index = {(r['arm'], r['id']): r for r in rows}
all_ids = sorted({r['id'] for r in rows})
assert len(all_ids) == 100 and len(rows) == 200
paired = []
for iid in all_ids:
    a, d = index['adi', iid], index['daira', iid]
    paired.append(dict(id=iid, both_resolved=a['resolved'] and d['resolved'], adi=a['nongold_files_after_git_filter'], daira=d['nongold_files_after_git_filter'], daira_minus_adi=d['nongold_files_after_git_filter']-a['nongold_files_after_git_filter']))
summary = []
for group in ['all', 'both_resolved']:
    rr = [r for r in paired if group == 'all' or r['both_resolved']]
    amean, dmean = statistics.mean(r['adi'] for r in rr), statistics.mean(r['daira'] for r in rr)
    row = dict(group=group, tasks=len(rr), adi_mean=amean, daira_mean=dmean, reduction_pct=(amean-dmean)/amean*100, daira_fewer=sum(r['daira']<r['adi'] for r in rr), equal=sum(r['daira']==r['adi'] for r in rr), daira_more=sum(r['daira']>r['adi'] for r in rr))
    prior = expected['summary'][group]['nongold_excluding_git_lists']
    assert abs(amean-prior['adi_mean']) < 1e-10 and abs(dmean-prior['daira_mean']) < 1e-10
    summary.append(row)
assert summary[0]['daira_fewer'] == 70 and summary[1]['tasks'] == 59
write_csv('section_1_2_exploration_comparison.csv', summary)
write_csv('per_task_exploration_statistics_200.csv', rows)
write_csv('paired_task_comparison_100.csv', paired)
write_csv('filtered_file_details.csv', details)
write_csv('excluded_git_listing_steps.csv', exclusions)
(OUTPUT/'filtered_file_sets.json').write_text(json.dumps(file_sets, ensure_ascii=False, indent=2), encoding='utf-8')
(OUTPUT/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
print('PASS: 200 task counts match original results; verified per-step action extraction, unique file sets, and paired groups.')
