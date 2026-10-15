"""UNRUN static executor/original-contract controls; no native or Lab import."""
import ast,hashlib,json
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).absolute().parent
def main():
    selected=json.loads((HERE/'input-selection.json').read_bytes());checks=[]
    for r in selected['files']:assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
    checks.append('all selected original dependency native adapter and additive executor source pins exact')
    tree=ast.parse((HERE/'native_executor.py').read_bytes())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='SelectedOntologyExecutor')
    methods={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
    assert {'executable_path','executable_sha256','guard','run_native'}<=set(methods)
    checks.append('exact narrow T32 executor interface exists on explicit distinct class')
    base=json.loads((ROOT/selected['base_dependency_selection_binding']['path']).read_bytes())
    assert len(base['inputs'])==720
    native=[r for r in base['inputs']if r['kind']=='native-executable']
    assert len(native)==1 and native[0]['destination']=='bin/lab-context-native-reader'
    assert native[0]['sha256']=='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
    checks.append('old720/0004 declares context native only; ontology role is separate addition')
    draft=json.loads((HERE/'execution-selection-template.json').read_bytes())
    assert draft['new_installation']is None and draft['installation_receipt_binding']is None and draft['added_inputs']==[]
    checks.append('unresolved new source ABI root receipt template cannot activate')
    print(json.dumps({'result':'PASS-static-ontology-port-only','checks':checks,'actual_ELF_native_or_install_executed':False,
                      'new_selected_closure_provisioned':False,'T07_T32_or_runtime_qualified':False,'authority_effect':'none'},sort_keys=True))
if __name__=='__main__':main()
