"""Exact restored public/historical input hash check; no body copying/export."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).parent
reader=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-node-recovery-qualification-preparation-0004/capture.py'
raw=reader.read_bytes();assert hashlib.sha256(raw).hexdigest()=='b41f1914e0d6a9be125e228525ca92d1b28d853be79c118adffc040bcf01f0fa'
spec=importlib.util.spec_from_file_location('_restored_hash_capture',reader);m=importlib.util.module_from_spec(spec);exec(compile(raw,str(reader),'exec'),m.__dict__)
decl=json.loads((ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/accounting-0001/unavailable-original-inputs.json').read_bytes())
rows=[]
for row in decl['rows']:
    p=Path(row['binding']['path'])
    if not p.exists():rows.append({'binding':row['binding'],'status':'ABSENT','body_exported':False});continue
    body=m.capture_path(p);observed=hashlib.sha256(body).hexdigest()
    rows.append({'binding':row['binding'],'status':'PRESENT-EXACT-ORIGINAL-SHA'if observed==row['binding']['sha256']else'PRESENT-DIFFERENT-SHA','observed_sha256':observed,'size_bytes':len(body),'body_exported':False})
v={'authority_effect':'none','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'counts':{s:sum(r['status']==s for r in rows)for s in ['ABSENT','PRESENT-EXACT-ORIGINAL-SHA','PRESENT-DIFFERENT-SHA']},'current_accounting_or_Source_metadata_changed':False,'old_guard_retroqualified':False}
with(HERE/'hash-result.json').open('x')as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'counts':v['counts'],'mismatches':[r for r in rows if r['status']=='PRESENT-DIFFERENT-SHA'],'missing':[r['binding']for r in rows if r['status']=='ABSENT']},sort_keys=True))

