"""Independent static review and expressly authorized pure controls; no API imports."""
import ast, contextlib, hashlib, io, json, os, sys
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
P=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T05/machine-read-development-preparation-0002'
OUT=Path(__file__).absolute().parent
def digest(raw):return hashlib.sha256(raw).hexdigest()
def read(row):
    raw=(ROOT/row['path']).read_bytes()
    assert digest(raw)==row['sha256'],row['path']
    return raw
def funcs(raw,cls=None):
    tree=ast.parse(raw)
    body=tree.body if cls is None else next(n.body for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
    return {n.name:ast.dump(n,include_attributes=False) for n in body if isinstance(n,ast.FunctionDef)}

fd0=len(os.listdir('/proc/self/fd'));modules0=set(sys.modules)
hh=(P/'HANDOFF.json').read_bytes()
assert digest(hh)=='890b9e6173043ed4d61af1a8726ea060565a61e65caf6d1eb7f8ca811c68a99f'
h=json.loads(hh);mf=read(h['source_manifest']);manifest=json.loads(mf)
for row in manifest['files']:
    raw=read(row);assert len(raw)==row['size_bytes']
selection=read(h['selection_template']);p=json.loads(selection)
inputs={role:read(row) for role,row in p['original_bindings'].items()}
own={role:read(row) for role,row in p['owned_code_bindings'].items()}
read(p['api_source_binding']);read(p['api_profile_binding']);read(p['dependency_selection_binding'])
old=funcs(inputs['original_tests'],'MachineTransport');new=funcs(own['tests'],'MachineTransport')
tests={k:v for k,v in old.items() if k.startswith('test_')}
assert len(tests)==14 and tests=={k:v for k,v in new.items() if k.startswith('test_')}
assert funcs(own['runner'])['capture_path']==funcs(own['capture'])['capture_path']
# This comparison includes the entire function source text, not just AST semantics.
def exact_function(raw,name):
    lines=raw.decode().splitlines(keepends=True)
    n=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name==name)
    return ''.join(lines[n.lineno-1:n.end_lineno])
assert exact_function(own['runner'],'capture_path')==exact_function(own['capture'],'capture_path')
assert p['max_session_seconds']==900 and p['original_source_expiry']=='2026-10-15T04:24:34.499247+00:00'
assert json.loads(inputs['legacy_period'])['expires_at']==p['original_source_expiry']
assert p['original_bindings']['machine_helper']['sha256']=='e436f2eeb2076c25bc20d817166eb451d0a8d7c602778a192e116324b8bcba5d'
controls=(P/'controls.py').read_bytes()
assert digest(controls)=='170e921fa88abfe8a1e4bb6d63c5d9e90a4092e2d8df8fe224c989c5ab8c1c7a'
stdout=io.StringIO()
namespace={'__name__':'__main__','__file__':str(P/'controls.py')}
with contextlib.redirect_stdout(stdout):
    exec(compile(controls,str(P/'controls.py'),'exec',dont_inherit=True),namespace)
pure=json.loads(stdout.getvalue())
assert pure['result']=='PASS-pure-T05-component-controls' and pure['FD_delta']==0
new_modules=set(sys.modules)-modules0
for name in new_modules:
    module=sys.modules[name];origin=str(getattr(module,'__file__',''))
    assert '/interface/api-integration-v17/' not in origin
    assert not name.startswith('_cal_T05_selected_actual_API17_0002')
    assert '/lab-context-native-reader' not in origin
for row in manifest['files']:read(row)
for row in p['original_bindings'].values():read(row)
read(p['api_source_binding']);read(p['api_profile_binding']);read(p['dependency_selection_binding'])
assert (P/'HANDOFF.json').read_bytes()==hh and read(h['source_manifest'])==mf
fd1=len(os.listdir('/proc/self/fd'));assert fd1==fd0
result={'schema_version':'lab-T05-independent-pure-review-controls/v1-candidate','authority_effect':'none',
 'result':'PASS-static-byte-and-permitted-pure-controls','handoff_sha256':digest(hh),'manifest_sha256':digest(mf),
 'manifest_rows_entry_exit':len(manifest['files']),'original_inputs_entry_exit':len(inputs),
 'all14_method_ASTs_identical':True,'inline_capture_function_exact_source_identical':True,
 'source_sha256':p['api_source_binding']['sha256'],'profile_sha256':p['api_profile_binding']['sha256'],
 'machine_helper_sha256':p['original_bindings']['machine_helper']['sha256'],
 'original_guard_sha256':p['original_bindings']['api_guard']['sha256'],
 'original_source_expiry':p['original_source_expiry'],'max_session_seconds':p['max_session_seconds'],
 'FD_before':fd0,'FD_after':fd1,'FD_delta':fd1-fd0,'selected_python':sys.executable,
 'new_modules':sorted(new_modules),'pure_controls':pure,'API_Lab_native_imported':False,
 'fourteen_runtime_tests_executed':False,'full_source_body_guard_executed':False,'task_qualified':False}
raw=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode()
fd=os.open(OUT/'selected-controls-result.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'wb') as f:f.write(raw)
print(json.dumps({'result':result['result'],'result_sha256':digest(raw),'FD_delta':0,'controls_checks':len(pure['checks']),'runtime_tests_executed':False},sort_keys=True))
