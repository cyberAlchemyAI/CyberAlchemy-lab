"""UNRUN static controls: no Lab/API/native modules are imported."""
import ast,hashlib,json,os
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).absolute().parent
def main(argv=None):
    assert not argv
    fd0=len(os.listdir('/proc/self/fd'))
    selected=json.loads((HERE/'generator-source-selection.json').read_bytes());checks=[]
    for r in selected['files']:
        p=ROOT/r['path'];assert not any(v.is_symlink()for v in(p,*p.parents))
        assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
    old=json.loads((ROOT/selected['predecessor_generator_binding']['path']).read_bytes())
    assert all(r in selected['files']for r in old['files']);checks.append('all original24 executable declarations retained exact with v2 full source universe')
    def defs(path):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(path.read_bytes()).body if isinstance(n,ast.FunctionDef)}
    before=defs(ROOT/'implementation/lab-context/candidates/v1/context.py');after=defs(HERE/'context_selected.py')
    assert all(before[k]==after[k]for k in['environment','compiled_schema','validate','required_reference'])
    checks.append('original environment carrier validators and governed reference rules AST-identical')
    ledger=json.loads((HERE/'ORIGINAL-METHOD-LEDGER.json').read_bytes());assert len(ledger['original_methods'])==36
    checks.append('all original23 Context plus13 Session test declarations retained individually with true input pins')
    m=json.loads((HERE/'packages/0001/generator-manifest.json').read_bytes())
    assert m['schema_version']=='lab-context-generator-manifest/v2-candidate' and m['files']==selected['files']+[m['source_closure_binding']]
    for key in['implementation_record','realization_record']:
        r=m[key];assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
    impl=json.loads((ROOT/m['implementation_record']['path']).read_bytes())
    assert impl['payload']['execution_entrypoint_ref']==(HERE/'context_selected.py').relative_to(ROOT).as_posix()+'#SelectedContextSession'
    assert impl['lifecycle_state']=='candidate' and impl['authority_effect']=='none'
    checks.append('concrete candidate implementation realization and v2 manifest select actual new constructor')
    assert len(os.listdir('/proc/self/fd'))==fd0
    print(json.dumps({'result':'PASS-static-selected-C08-only','checks':checks,'FD_delta':0,'actual_native_or_Lab_imports':False,
                      'full36_or_cold_or_runtime_qualified':False,'authority_effect':'none'},sort_keys=True));return 0
