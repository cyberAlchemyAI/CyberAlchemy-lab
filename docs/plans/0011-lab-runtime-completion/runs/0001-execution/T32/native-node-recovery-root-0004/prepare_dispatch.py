"""Root static review and fresh packet selection for fourth technical attempt."""
import argparse, ast, datetime, hashlib, json, os, stat
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
P=RUN/'T32/native-node-recovery-qualification-preparation-0004'
OLD=RUN/'T32/native-node-recovery-qualification-preparation-0002'
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
a=argparse.ArgumentParser()
for name in ['handoff-sha256','manifest-sha256','peer-sha256','custody-sha256']:a.add_argument('--'+name,required=True)
args=a.parse_args()
peer=RUN/'T32/native-node-recovery-qualification-independent-review-0004/review.json'
review=obj(peer,args.peer_sha256)
assert str(review['result']).startswith('PASS')and review['findings']==[]
handoff=obj(P/'HANDOFF.json',args.handoff_sha256)
manifest=obj(P/'source-manifest.json',args.manifest_sha256)
assert handoff['source_manifest_binding']==bind(P/'source-manifest.json')
for row in manifest['files']:
    p=Path(row['path']);p=p if p.is_absolute()else ROOT/p
    b=read(p,row['sha256']);assert len(b)==row['size_bytes']
parents=[]
for p,n in [(RUN/'T32/native-store-guard-composition-preparation-0001/source-manifest.json',153),
            (RUN/'T07/ontology-native-execution-preparation-0002/source-manifest.json',176)]:
    rows=obj(p)['files'];assert len(rows)==n
    for row in rows:assert row in manifest['files']
    parents.append(n)
new=ast.parse(read(P/'qualify.py',handoff['runner_binding']['sha256']))
old=ast.parse(read(OLD/'qualify.py','c11f77bc5efd35e74fd84d3dbcb0563f846b1cdd3279c70c778a179e2e4e8b9b'))
dump=lambda n:ast.dump(n,include_attributes=False)
fn=lambda tree:{n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
nf,of=fn(new),fn(old)
unchanged=sorted(set(of)-{'run'})
assert len(unchanged)==13 and set(nf)==set(of)
for name in unchanged:assert dump(nf[name])==dump(of[name]),name
def cases(tree):
    return next(n for n in ast.walk(fn(tree)['run'])if isinstance(n,ast.With)and any(isinstance(v.context_expr,ast.Call)and isinstance(v.context_expr.func,ast.Attribute)and v.context_expr.func.attr=='signed_catalog'for v in n.items))
assert dump(cases(new))==dump(cases(old))
for leaf in ['boundary.py','capture.py']:assert read(P/leaf)==read(OLD/leaf)
custody=obj(OUT/'owned-custody.json',args.custody_sha256)
for k in ['store_parent','output_root']:
    r=custody['roots'][k];p=Path(r['path']);s=p.lstat()
    assert stat.S_ISDIR(s.st_mode)and not p.is_symlink()
    assert [s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]==r['identity']
    assert s.st_uid==os.getuid()and stat.S_IMODE(s.st_mode)==0o700 and list(p.iterdir())==[]
packet=obj(P/'execution-selection-INACTIVE.json',handoff['inactive_selection_binding']['sha256'])
dispatch=obj(P/'root-dispatch-INACTIVE.json',handoff['inactive_dispatch_binding']['sha256'])
assert packet['technical_deadline_utc']is None and packet['root_dispatch_binding']is None
assert dispatch['technical_deadline_utc']is None
assert packet['reference_bindings']==dispatch['reference_bindings']
assert packet['ontology_execution_selection_binding']==dispatch['ontology_execution_selection_binding']
for row in packet['active_code_bindings']+list(packet['reference_bindings'].values())+[packet['ontology_execution_selection_binding']]:
    read(ROOT/row['path'],row['sha256'])
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
    'all_manifest_occurrences_rechecked':len(manifest['files']),'all153_guard_and176_execution_rows_retained':True,
    'complete_original_fourcase_and13_helper_AST_checked':True,
    'real_technical_seconds_selected':899,'original_clock_or_period_modified':False,
    'actual_runtime_not_started_at_freeze':True,'new827_selector_explicitly_selected':True,
    'old480_574_equivalence_or_migration_qualified':False,'owned_roots_empty_and_identity_mode_checked':True,
    'existing_Source_sharedAPI_or_installation_changed':False,'genuine_owner_or_whole_runtime_or_task_qualified':False}
write(OUT/'Root-review.json',rootreview)
print(json.dumps({'selection':selected,'deadline':deadline,'Root_review':bind(OUT/'Root-review.json')},sort_keys=True))

