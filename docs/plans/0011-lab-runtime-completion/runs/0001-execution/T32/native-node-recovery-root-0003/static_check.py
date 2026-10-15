"""Root static preflight only; no actual API, guard, lease or native call."""
import ast, hashlib, json, os, stat
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
P=RUN/'T32/native-node-recovery-qualification-preparation-0003'
OLD=RUN/'T32/native-node-recovery-qualification-preparation-0002'
OUT=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p,pin=None):
    b=p.read_bytes()
    if pin is not None:assert sha(b)==pin,(str(p),'SHA')
    return b
def value(p,pin=None):return json.loads(read(p,pin))
mf=value(P/'source-manifest.json','217b74a99d411c030d138bbcf82671c65aa09330e986acae0269abc01dc7547a')
assert len(mf['files'])==361
for row in mf['files']:
    p=Path(row['path']);p=p if p.is_absolute()else ROOT/p
    b=read(p,row['sha256']);assert len(b)==row['size_bytes']
parents=[]
for p,n in [(RUN/'T32/native-store-guard-composition-preparation-0001/source-manifest.json',153),
            (RUN/'T07/ontology-native-execution-preparation-0002/source-manifest.json',176)]:
    rows=value(p)['files'];assert len(rows)==n
    for row in rows:assert row in mf['files']
    parents.append(n)
new=ast.parse(read(P/'qualify.py','292ae8fe80b6d7ac2a99498e6e2aaff6f66524b3e3421ff513459ba57a0db3e3'))
old=ast.parse(read(OLD/'qualify.py','c11f77bc5efd35e74fd84d3dbcb0563f846b1cdd3279c70c778a179e2e4e8b9b'))
dump=lambda n:ast.dump(n,include_attributes=False)
fn=lambda tree:{n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
nf,of=fn(new),fn(old)
unchanged=sorted(set(of)-{'run'})
assert len(unchanged)==13
for name in unchanged:assert dump(nf[name])==dump(of[name]),name
def cases(tree):
    return next(n for n in ast.walk(fn(tree)['run']) if isinstance(n,ast.With) and any(isinstance(v.context_expr,ast.Call)and isinstance(v.context_expr.func,ast.Attribute)and v.context_expr.func.attr=='signed_catalog'for v in n.items))
assert dump(cases(new))==dump(cases(old))
for leaf in ['boundary.py','capture.py']:assert read(P/leaf)==read(OLD/leaf)
packet=value(P/'execution-selection-INACTIVE.json','5763d1e680df47c5d8c3d3bda3d595a0a0a6c8adbfade0b67f9c0c8388b94a3e')
dispatch=value(P/'root-dispatch-INACTIVE.json','b261904d08d5520b0dcb50461c88393943a469df80d66b1ad7935af9f99aca41')
assert packet['technical_deadline_utc'] is None and packet['root_dispatch_binding'] is None
for k in ['store_parent','output_root']:
    assert packet[k]==dispatch[k]=={'path':None,'identity':None}
assert packet['reference_bindings']==dispatch['reference_bindings']
assert packet['ontology_execution_selection_binding']==dispatch['ontology_execution_selection_binding']
assert len(packet['active_code_bindings'])==17
for row in packet['active_code_bindings']+list(packet['reference_bindings'].values())+[packet['ontology_execution_selection_binding']]:
    read(ROOT/row['path'],row['sha256'])
custody=value(OUT/'owned-custody.json','a5de5e8acc282ab1a56b8d562016985a99b270b8ab63e54d1788b7e7d700d5f5')
for k in ['store_parent','output_root']:
    r=custody['roots'][k];p=Path(r['path']);s=p.lstat()
    assert stat.S_ISDIR(s.st_mode) and not p.is_symlink()
    assert [s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]==r['identity']
    assert s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700 and list(p.iterdir())==[]
result={'authority_effect':'none','result':'PASS-static-only','manifest_occurrences':361,'parent_occurrences':parents,
        'unchanged_helpers':unchanged,'original_four_cases_AST_identical':True,
        'boundary_capture_byte_identical':True,'actual_API_Source_executor_native_or_lease':False,
        'owned_roots_still_empty_identity_mode_checked':True}
target=OUT/'static-result.json'
with target.open('x')as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps(result,sort_keys=True))

