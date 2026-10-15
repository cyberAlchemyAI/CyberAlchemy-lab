"""Root-only fresh empty persistent technical directories; no runtime call."""
import datetime, json, os, stat, tempfile
from pathlib import Path
OUT=Path(__file__).parent
base=Path('/home/vlad_/.local/share')
roots={}
for key in ['store_parent','output_root']:
    p=Path(tempfile.mkdtemp(prefix='cal-T32-v4-'+key+'-',dir=base))
    os.chmod(p,0o700);s=p.lstat()
    assert stat.S_ISDIR(s.st_mode)and s.st_uid==os.getuid()and stat.S_IMODE(s.st_mode)==0o700 and list(p.iterdir())==[]
    roots[key]={'path':str(p),'identity':[s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]}
value={'schema_version':'lab-T32-root-owned-custody-preparation/v1-candidate','authority_effect':'none',
    'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'roots':roots,
    'persistent_location':True,'filesystem_device_observed':roots['store_parent']['identity'][0],
    'actual_runtime_or_native_executed':False,'technical_deadline_not_yet_selected':True,
    'qualification_runner_independent_peer_pending':True,'host_power_loss_guarantee_proved':False,
    'preserve_all_residue':True,'whole_task_complete':False}
p=OUT/'owned-custody.json'
with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(value,sort_keys=True))

