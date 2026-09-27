import json,pathlib,re,collections,statistics
root=pathlib.Path(__file__).resolve().parent.parent
output=root/"results"
output.mkdir(exist_ok=True)
x=json.loads((root/'data/raw_tool_call_evidence.json').read_text(encoding='utf-8-sig'))
rows=[dict(r,scope='standard') for r in x['calls']]
extras={'adi':{'django__django-10097':[26,30,31,32,33,36,38,51]},'daira':{'django__django-10097':[26],'django__django-7530':[31,34,43,48,57]}}
for arm,items in extras.items():
 for iid,steps in items.items():
  for step in steps:
   r=next(r for r in x['other_mentions'] if r['arm']==arm and r['id']==iid and r['step']==step)
   sub=re.search(r'(list-frames|break|call-tree|exec)\b',r['action']).group(1) if arm=='adi' else 'trace'
   rows.append(dict(r,scope='wrapped',subcommand=sub))
manual={('daira','django__django-10097',11):'environment_error',('daira','django__django-7530',18):'environment_error',('daira','django__django-7530',31):'environment_error',('daira','django__django-7530',34):'environment_error',('daira','django__django-13809',49):'no_trace',('daira','django__django-16100',39):'no_trace'}
for r in rows:
 o=r['observation'].strip();key=(r['arm'],r['id'],r['step']);category='evidence_returned'
 if key in manual:category=manual[key]
 elif not o:category='empty_unconfirmed'
 elif r['arm']=='adi':
  if o.startswith('Error: Invalid format'):category='target_format_error'
  elif o.startswith('Error: Line'):category='target_location_error'
  elif o.startswith(('Usage:','Use -')):category='command_argument_error'
  elif o.startswith('[exec output]') and 'Traceback (most recent call last)' in o:category='exec_expression_error'
  elif o.startswith('Traceback (most recent call last)'):category='environment_error'
  elif o.startswith('Error: Target frame') or 'No matching frames found.' in o or o.startswith('Error: exec_result'):category='target_not_reached'
  else:assert not o.startswith('Error:'),key
 else:
  if 'No function calls were tracked' in o:category='no_trace'
  elif '[LLM Analysis Error - Context Window Exceeded]' in o:category='analysis_context_limit'
 r['category']=category
 r['confirmed_failure']=category not in ['evidence_returned','empty_unconfirmed']
 r['interface_error']=category in ['target_format_error','target_location_error','command_argument_error','exec_expression_error']
assert len({(r['arm'],r['id'],r['step']) for r in rows})==len(rows)
summary={}
for scope in ['standard','all']:
 summary[scope]={}
 for arm in ['adi','daira']:
  rr=[r for r in rows if r['arm']==arm and (scope=='all' or r['scope']=='standard')];bytask=collections.defaultdict(list)
  for r in rr:bytask[r['id']].append(r)
  starts=[sorted(v,key=lambda r:r['step'])[0] for v in bytask.values()]
  counts=collections.Counter(r['category'] for r in rr)
  s=dict(calls=len(rr),using_tasks=len(bytask),confirmed_failures=sum(r['confirmed_failure'] for r in rr),empty_unconfirmed=counts['empty_unconfirmed'],categories=dict(counts),failure_tasks=len({r['id'] for r in rr if r['confirmed_failure']}),evidence_tasks=len({r['id'] for r in rr if r['category']=='evidence_returned'}),interface_errors=sum(r['interface_error'] for r in rr),interface_error_tasks=len({r['id'] for r in rr if r['interface_error']}),first_call_failures=sum(r['confirmed_failure'] for r in starts),first_call_interface_errors=sum(r['interface_error'] for r in starts))
  s['failure_rate']=s['confirmed_failures']/s['calls'];summary[scope][arm]=s
print(json.dumps(summary["all"],ensure_ascii=False,indent=2))
(output/'classified_calls_and_summary.json').write_text(json.dumps(dict(summary=summary,calls=rows,definitions={'confirmed_failure':'Explicit tool/interface failure, missing target/trace, or analysis failure. Subject-program exceptions with captured frames are not failures. Empty outputs are separately unconfirmed.','all':'Standard entrypoint calls plus audited absolute-path, python -m ADI, and copied-tool compatibility invocations; excludes reading tool source and raw Hunter API experiments.','manual':'Six report/redirected-output exceptions were individually inspected; daira django-7530 steps31/34 confirmed by subsequent reads steps32/35.'}),ensure_ascii=False,indent=2),encoding='utf-8')
assert summary['standard']['adi']['calls']==394 and summary['standard']['daira']['calls']==328
assert summary['all']['adi']['calls']==402 and summary['all']['daira']['calls']==334

import csv

def save_csv(name, items):
    with (output/name).open('w', encoding='utf-8-sig', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=list(items[0]))
        writer.writeheader(); writer.writerows(items)

expected=json.loads((root/'data/reference_failure_audit.json').read_text(encoding='utf-8-sig'))
assert summary==expected['summary'], 'Summary differs from original audit'
assert {(r['arm'],r['id'],r['step']):r['category'] for r in rows}=={(r['arm'],r['id'],r['step']):r['category'] for r in expected['calls']}, 'Classification differs'
fields=['arm','id','step','scope','subcommand','category','confirmed_failure','interface_error','action','observation']
all_rows=[{k:r.get(k,'') for k in fields} for r in rows]
save_csv('all_tool_calls_736.csv', all_rows)
save_csv('confirmed_failures_189.csv', [r for r in all_rows if r['confirmed_failure']])
reports={a:json.loads((root/'data'/(a+'_report.json')).read_text(encoding='utf-8')) for a in ['adi','daira']}
tasks=[]
for arm in reports:
    for iid in sorted(reports[arm]['submitted_ids']):
        rr=sorted([r for r in rows if r['arm']==arm and r['id']==iid],key=lambda r:r['step'])
        tasks.append(dict(arm=arm,id=iid,calls=len(rr),interface_errors=sum(r['interface_error'] for r in rr),other_failures=sum(r['confirmed_failure'] and not r['interface_error'] for r in rr),all_failures=sum(r['confirmed_failure'] for r in rr),empty_unconfirmed=sum(r['category']=='empty_unconfirmed' for r in rr),first_call_category=rr[0]['category'] if rr else 'not_used'))
save_csv('per_task_call_statistics_200.csv', tasks)
categories=[]
for arm in reports:
    for category in sorted(set(r['category'] for r in rows if r['arm']==arm)):
        rr=[r for r in rows if r['arm']==arm and r['category']==category]
        categories.append(dict(arm=arm,category=category,calls=len(rr),tasks=len(set(r['id'] for r in rr))))
save_csv('failure_categories.csv',categories)
manual_rows=[]
for (arm,iid,step),category in manual.items():
    r=next(r for r in rows if (r['arm'],r['id'],r['step'])==(arm,iid,step))
    manual_rows.append(dict(arm=arm,id=iid,step=step,category=category,action=r['action'],observation=r['observation']))
save_csv('manual_classification_overrides_6.csv',manual_rows)
table=[]
for label,kind in [('Target dynamic information not obtained','other'),('Interface usage errors','interface'),('All confirmed failures','all')]:
    row={'failure_category':label}
    for arm in ['adi','daira']:
        st=summary['all'][arm]
        count=st['confirmed_failures']-st['interface_errors'] if kind=='other' else st['interface_errors'] if kind=='interface' else st['confirmed_failures']
        row[arm.upper()]=f"{count}/{st['calls']} ({count/st['calls']*100:.2f}%)"
    table.append(row)
save_csv('section_1_1_failure_comparison.csv',table)
assert len(rows)==736 and len(tasks)==200 and sum(r['confirmed_failure'] for r in rows)==189
print('PASS: 736 calls, 200 task rows; all classifications and totals match the original audit.')
