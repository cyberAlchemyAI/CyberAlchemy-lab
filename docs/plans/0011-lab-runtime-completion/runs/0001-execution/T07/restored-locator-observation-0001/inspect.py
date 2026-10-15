"""Observe exact selected unavailable locators, metadata only, no body export."""
import datetime,json,os,stat
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).parent
decl=json.loads((ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/accounting-0001/unavailable-original-inputs.json').read_bytes())
rows=[]
for row in decl['rows']:
    path=Path(row['binding']['path'])
    try:
        s=path.lstat();value={'exists':True,'regular':stat.S_ISREG(s.st_mode),'symlink':stat.S_ISLNK(s.st_mode),'device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid,'mode':stat.S_IMODE(s.st_mode),'size_bytes':s.st_size,'mtime_ns':s.st_mtime_ns}
    except FileNotFoundError:value={'exists':False}
    rows.append({'binding':row['binding'],'classification':row['classification'],'body_read':False,**value})
v={'authority_effect':'none','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'present_count':sum(r['exists']for r in rows),'historical_identity_or_hash_equivalence_proved':False,'original_or_accounting_metadata_changed':False}
with (HERE/'result.json').open('x')as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'present_count':v['present_count'],'present_rows':[r for r in rows if r['exists']]},sort_keys=True))

