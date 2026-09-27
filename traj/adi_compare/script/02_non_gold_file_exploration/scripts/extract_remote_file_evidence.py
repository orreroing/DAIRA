import pathlib,json,runpy,hashlib,datetime
base=pathlib.Path('/data/home/orrero/wzh');root=base/'adi_compare'
script=base/'baseline/SWE-agent/scripts/analyze_exploration_efficiency.py'
ns=runpy.run_path(str(script),run_name='snapshot_import')
goldpath=base/'baseline/SWE-agent/expr_data/DAIRA/localization_eval/per_instance_localization.csv'
gold=ns['load_gold'](goldpath)
reports={a:json.loads((root/(a+'_report.json')).read_text()) for a in ['adi','daira']}
assert set(reports['adi']['submitted_ids'])==set(reports['daira']['submitted_ids'])
rows=[];supplement=[]
for arm in ['adi','daira']:
 for iid in reports[arm]['submitted_ids']:
  p=(root/arm/iid/(iid+'.traj')).resolve();assert str(p).startswith('/data/home/orrero/')
  raw=p.read_bytes();d=json.loads(raw);steps=[]
  for i,s in enumerate(d['trajectory']):
   a=s.get('action','');o=s.get('observation','');fa=sorted(ns['extract_files'](a));fo=sorted(ns['extract_files'](o))
   steps.append(dict(step=i,action=a,action_files=fa,observation_files=fo,observation_sha256=hashlib.sha256(o.encode()).hexdigest()))
   if arm=='daira' and iid=='django__django-7530' and i in [32,35]:supplement.append(dict(arm=arm,id=iid,step=i,action=a,observation=o))
  rows.append(dict(arm=arm,id=iid,resolved=iid in reports[arm]['resolved_ids'],gold_files=sorted(gold[iid]),trajectory_path=str(p),trajectory_sha256=hashlib.sha256(raw).hexdigest(),steps=steps))
print(json.dumps(dict(extracted_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),reports=reports,source_script=str(script),source_script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),source_script_text=script.read_text(),source_gold=str(goldpath),source_gold_sha256=hashlib.sha256(goldpath.read_bytes()).hexdigest(),rows=rows,redirected_failure_evidence=supplement),ensure_ascii=False))
