"""Independent exact component/AST checks and permitted pure T06 controls only."""
import ast,contextlib,hashlib,io,json,os,sys,traceback,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
P=HERE.parent/'maintained-operator-qualification-0001'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(row):
    raw=(ROOT/row['path']).read_bytes();assert sha(raw)==row['sha256'],row['path']
    if 'size_bytes' in row:assert len(raw)==row['size_bytes']
    return raw
fd0=len(os.listdir('/proc/self/fd'));mods0=set(sys.modules)
hh=(P/'HANDOFF.json').read_bytes()
assert sha(hh)=='37486c08a2866b2c1c9442846a48c6773fe395b72ef4e646b51059b1da43cb1b'
h=json.loads(hh);mf=read(h['source_manifest_binding']);assert sha(mf)=='ba2970a3f43781daadefe6f0bcabfe14adfbd04064beab8961ec0cc2a3c740e0'
manifest=json.loads(mf)
captures={r['path']:read(r) for r in manifest['files']}
def definitions(raw):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
orig=definitions(read(h['source_preimage_binding']));new=definitions(read(h['harness_binding']))
for symbol in h['original_unchanged_AST_definitions']:assert orig[symbol]==new[symbol],symbol
selected=json.loads(read(h['Root_selection_template_binding']))
for key in ['source_binding','profile_binding','SDK_binding','provisioning_binding','dependency_selection_binding','members_binding','caller_boundary_binding']:read(selected[key])
for row in selected['bootstrap_bindings']:read(row)
for row in selected['handler_bindings'].values():read(row)
assert selected['status'] is None and selected['probe_seconds'] is None and selected['observation_seconds'] is None
# Bootstrap itself was read, reviewed and pinned before its true-filename compile.
bootstrap=read(h['bootstrap_binding']);stdout=io.StringIO();failure=None;rc=None
namespace={'__name__':'_independent_T06_bootstrap','__file__':str(P/'bootstrap.py')}
try:
    with contextlib.redirect_stdout(stdout):
        exec(compile(bootstrap,str(P/'bootstrap.py'),'exec',dont_inherit=True),namespace)
        rc=namespace['main'](['--manifest-sha256',sha(mf),'--manifest-size',str(len(mf)),'--target','controls'])
except BaseException as exc:failure={'class':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
pure=json.loads(stdout.getvalue()) if failure is None else None
if pure is not None:assert rc==0 and pure['result']=='PASS-pure-fixture-only'
new_modules=set(sys.modules)-mods0
for name in new_modules:
    origin=str(getattr(sys.modules[name],'__file__',''))
    assert '/interface/api-integration-v17/' not in origin,origin
    assert 'lab-context-native-reader' not in origin
    assert not name.startswith('_cal_T06_qualification_API_')
for row in manifest['files']:read(row)
assert (P/'HANDOFF.json').read_bytes()==hh and read(h['source_manifest_binding'])==mf
fd1=len(os.listdir('/proc/self/fd'));assert fd1==fd0
result={'schema_version':'lab-T06-independent-pure-controls/v1-candidate','authority_effect':'none',
 'result':'FAIL-permitted-pure-controls' if failure else 'PASS-permitted-pure-controls',
 'selected_python':sys.executable,'handoff_sha256':sha(hh),'manifest_sha256':sha(mf),
 'component_rows_entry_exit':len(manifest['files']),'original_AST_definitions_preserved':h['original_unchanged_AST_definitions'],
 'inactive_Root_selection':True,'pure_controls_exit_code':rc,'pure_controls':pure,'failure':failure,
 'FD_before':fd0,'FD_after':fd1,'FD_delta':fd1-fd0,'new_modules':sorted(new_modules),
 'API_Lab_native_imported':False,'shared_runtime_lock_acquired':False,'operator_runtime_started':False,
 'full_source_body_or_installed_guard_executed':False,'task_qualified':False}
raw=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
fd=os.open(HERE/'selected-controls-result.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'wb') as f:f.write(raw)
print(json.dumps({'result':result['result'],'result_sha256':sha(raw),'controls':len(pure['controls']) if pure else None,'FD_delta':0,'operator_runtime_started':False},sort_keys=True))
