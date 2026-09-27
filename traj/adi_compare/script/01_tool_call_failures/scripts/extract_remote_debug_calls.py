import json,pathlib,re
root=pathlib.Path('/data/home/orrero/wzh/adi_compare').resolve()
assert str(root).startswith(str(pathlib.Path('/data/home/orrero').resolve())+'/')
out=[];other=[]
for arm in ['adi','daira']:
 report=json.loads((root/(arm+'_report.json')).read_text())
 for iid in report['submitted_ids']:
  p=(root/arm/iid/(iid+'.traj')).resolve();assert str(p).startswith(str(root)+'/')
  d=json.loads(p.read_text())
  for i,s in enumerate(d['trajectory']):
   a=s['action'];hits=list(re.finditer(r'(?:^|\n|&&|;)\s*(adi_debug|run_hunter_trace)\b([^\n]*)',a))
   if not hits and re.search(r'\b(adi_debug|run_hunter_trace|ADI|run_hunter_trace_py35|run_hunter_py3)\b',a):other.append(dict(arm=arm,id=iid,step=i,action=a,observation=s['observation']))
   for hit in hits:
    tool=hit.group(1);args=hit.group(2).strip();sub=args.split()[0].strip('\'\"') if args else ''
    if tool=='adi_debug' and sub not in ['list-frames','break','exec','call-tree']:continue
    out.append(dict(arm=arm,id=iid,step=i,tool=tool,subcommand=sub if tool=='adi_debug' else 'trace',action=a,observation=s['observation'],execution_time=s.get('execution_time'),matches_in_action=len(hits)))
print(json.dumps(dict(calls=out,other_mentions=other),ensure_ascii=False))

