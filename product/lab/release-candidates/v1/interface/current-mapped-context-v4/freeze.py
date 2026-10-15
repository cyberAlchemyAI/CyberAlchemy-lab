"""Require full exact source and reader qualification before native effects."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PARENT=HERE.parent/'current-mapped-context-v3';SOURCE=HERE.parent/'current-participation-v5';ADAPTER=HERE.parent/'current-source-adapter-v4'
EXE=Path('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader');EXE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists()
    required=['current-participation-source-proof-0005.json','current-participation-audit-proof-0005.json','current-source-adapter-checks-proof-0005.json','current-source-adapter-audit-proof-0005.json']
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path']
        rows[row['path']]=row
    for name in required:
        p=RUN/name;value=json.loads(p.read_bytes());assert value['result']=='PASS'
        for row in value['files']:add(row)
        add(bind(p))
    for p in [RUN/'current-mapping-checks-proof-0002.json',RUN/'current-mapping-audit-proof-0002.json',PARENT/'source-manifest.json']:
        for row in json.loads(p.read_bytes())['files']:add(row)
        add(bind(p))
    for name in ['test_original_mapping.py','test_raw_mapping.py']:assert methods(PARENT/name)==methods(HERE/name)
    assert sum(len(methods(HERE/name)) for name in ['test_original_mapping.py','test_raw_mapping.py'])==29
    for p in HERE.iterdir():
        if p.is_file():
            if p.suffix=='.py':ast.parse(p.read_bytes())
            add(bind(p))
    assert EXE.is_file() and not EXE.is_symlink() and hashlib.sha256(EXE.read_bytes()).hexdigest()==EXE_SHA
    value={'schema_version':'lab-current-native-mapper-source/v4-candidate','files':[rows[k] for k in sorted(rows)],'original_source_binding':bind(SOURCE/'source-manifest.json'),'original_package_binding':bind(SOURCE/'packages/0001/manifest.json'),'adapter_source_binding':bind(ADAPTER/'source-manifest.json'),'predecessor_source_binding':bind(PARENT/'source-manifest.json'),'selected_native_executable':{'path':str(EXE),'sha256':EXE_SHA},'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'all29_method_ASTs_retained':True,'expected_tests':29,'frozen_before_native_and_cold_source_effects':True,'authority_effect':'none','actual_owner_outcome':None}
    p=HERE/'source-manifest.json'
    with p.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(p),'files':len(rows),'expected_tests':29}),flush=True)
if __name__=='__main__':main()
