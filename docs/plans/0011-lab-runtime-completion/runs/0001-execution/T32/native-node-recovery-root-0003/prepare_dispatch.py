"""Root selects one fresh bounded technical dispatch; no native or API call."""
import argparse, datetime, hashlib, json, os, stat
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
P=RUN/'T32/native-node-recovery-qualification-preparation-0003'
OUT=Path(__file__).parent
def read(p,pin=None):
    b=p.read_bytes()
    if pin is not None:assert hashlib.sha256(b).hexdigest()==pin,(str(p),'SHA')
    return b
def obj(p,pin=None):return json.loads(read(p,pin))
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(read(p)).hexdigest()}
def write(p,v):
    b=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC|os.O_NOFOLLOW,0o600)
    try:
        with os.fdopen(fd,'wb',closefd=False)as f:f.write(b);f.flush();os.fsync(fd)
    finally:os.close(fd)
    return bind(p)
a=argparse.ArgumentParser();a.add_argument('--peer-sha256',required=True);args=a.parse_args()
peer=RUN/'T32/native-node-recovery-qualification-independent-review-0003/review.json'
review=obj(peer,args.peer_sha256)
assert review['result']=='PASS-scoped-inactive-qualification-preparation' and review['findings']==[]
handoff=obj(P/'HANDOFF.json','ffcd1062d1116f069c338d6bba10916c02980b7345f23c8fb4bcc6a111d93904')
manifest=obj(P/'source-manifest.json','217b74a99d411c030d138bbcf82671c65aa09330e986acae0269abc01dc7547a')
assert len(manifest['files'])==361
assert obj(OUT/'static-result.json')['result']=='PASS-static-only'
# Freeze byte identities again, without invoking any guard.
for row in manifest['files']:
    p=Path(row['path']);p=p if p.is_absolute()else ROOT/p
    b=read(p,row['sha256']);assert len(b)==row['size_bytes']
custody=obj(OUT/'owned-custody.json','a5de5e8acc282ab1a56b8d562016985a99b270b8ab63e54d1788b7e7d700d5f5')
for k in ['store_parent','output_root']:
    r=custody['roots'][k];p=Path(r['path']);s=p.lstat()
    assert stat.S_ISDIR(s.st_mode)and not p.is_symlink()
    assert [s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]==r['identity']
    assert s.st_uid==os.getuid()and stat.S_IMODE(s.st_mode)==0o700 and list(p.iterdir())==[]
packet=obj(P/'execution-selection-INACTIVE.json','5763d1e680df47c5d8c3d3bda3d595a0a0a6c8adbfade0b67f9c0c8388b94a3e')
dispatch=obj(P/'root-dispatch-INACTIVE.json','b261904d08d5520b0dcb50461c88393943a469df80d66b1ad7935af9f99aca41')
assert packet['technical_deadline_utc']is None and packet['root_dispatch_binding']is None
assert dispatch['technical_deadline_utc']is None
now=datetime.datetime.now(datetime.timezone.utc)
deadline=(now+datetime.timedelta(seconds=899)).isoformat()
for k in ['store_parent','output_root']:
    packet[k]=dispatch[k]=custody['roots'][k]
packet['technical_deadline_utc']=dispatch['technical_deadline_utc']=deadline
dispatch_binding=write(OUT/'root-dispatch.json',dispatch)
packet['root_dispatch_binding']=dispatch_binding
selected=write(OUT/'qualification-selection.json',packet)
rootreview={'schema_version':'lab-T32-Root-four-case-dispatch-selection/v2-candidate',
    'authority_effect':'none','recorded_at':now.isoformat(),'result':'PASS-scoped-Root-selection-for-owned-technical-native-cases',
    'runner_binding':handoff['runner_binding'],'handoff_binding':bind(P/'HANDOFF.json'),
    'source_manifest_binding':bind(P/'source-manifest.json'),'independent_peer_binding':bind(peer),
    'qualification_selection_binding':selected,'root_dispatch_binding':dispatch_binding,
    'full361_rows_rechecked':True,'all153_guard_and176_execution_rows_retained':True,
    'complete_original_fourcase_and13_helper_AST_checked':True,'Root_static_chunk':'0ce86e',
    'real_technical_seconds_selected':899,'original_clock_or_period_modified':False,
    'actual_runtime_not_started_at_freeze':True,'new827_selector_explicitly_selected':True,
    'old480_574_equivalence_or_migration_qualified':False,'owned_roots_empty_and_identity_mode_checked':True,
    'existing_Source_sharedAPI_or_installation_changed':False,'genuine_owner_or_whole_runtime_or_task_qualified':False}
write(OUT/'Root-review.json',rootreview)
print(json.dumps({'selection':selected,'deadline':deadline,'Root_review':bind(OUT/'Root-review.json')},sort_keys=True))

