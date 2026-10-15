"""Retain predecessor assertions and freeze current mapping before effects."""
import ast
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PARENT=HERE.parent/'custody-mapped-context-v2'
SOURCE=HERE.parent/'current-participation-v2'
ADAPTER=HERE.parent/'current-source-adapter-v1'
EXE=Path('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader')
EXE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists()
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path']
        rows[row['path']]=row
    for p in [RUN/'current-source-adapter-checks-proof-0002.json',RUN/'current-source-adapter-audit-proof-0002.json',PARENT/'source-manifest.json']:
        for row in json.loads(p.read_bytes())['files']:add(row)
        add(bind(p))
    context=RUN/'context-R03-current-mapping-0001.json';c=json.loads(context.read_bytes());assert c['strict_coverage']=='PASS'
    for row in c['source_bindings']:add(row)
    add(bind(context))
    old=methods(PARENT/'test_original_mapping.py');new=methods(HERE/'test_original_mapping.py')
    assert old==new and len(old)==20
    oldraw=methods(PARENT/'test_raw_mapping.py');newraw=methods(HERE/'test_raw_mapping.py')
    retained=[k for k in oldraw if oldraw[k]==newraw.get(k)];assert len(retained)==7 and len(newraw)==9
    for p in HERE.glob('*'):
        if p.is_file():
            if p.suffix=='.py':ast.parse(p.read_bytes())
            add(bind(p))
    assert EXE.is_file() and not EXE.is_symlink() and hashlib.sha256(EXE.read_bytes()).hexdigest()==EXE_SHA
    m={'schema_version':'lab-current-native-mapper-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'context_binding':bind(context),'original_source_binding':bind(SOURCE/'source-manifest.json'),'original_package_binding':bind(SOURCE/'packages/0001/manifest.json'),'adapter_source_binding':bind(ADAPTER/'source-manifest.json'),'predecessor_source_binding':bind(PARENT/'source-manifest.json'),
        'selected_native_executable':{'path':str(EXE),'sha256':EXE_SHA},'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'original20assertion_ASTs_retained':True,'retained_raw_methods':retained,'source_specific_raw_method_successors':2,'expected_tests':29,'frozen_before_native_and_cold_source_effects':True,'authority_effect':'none','actual_owner_outcome':None}
    p=HERE/'source-manifest.json'
    with p.open('x') as f:json.dump(m,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(p),'files':len(rows),'expected_tests':29}),flush=True)
if __name__=='__main__':main()
