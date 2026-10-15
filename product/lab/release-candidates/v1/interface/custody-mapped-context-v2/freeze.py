"""Freeze mapper, exact original source, old mapping and native executable pins."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
SOURCE=HERE.parent/'custody-participation-v1'
EXE=Path('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader')
EXE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists() and not (HERE/'receipts').exists()
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row,row['path'];p=ROOT/row['path'];assert p.is_file() and not p.is_symlink() and bind(p)==row,row['path'];rows[row['path']]=row
    for n in ['custody-participation-v1','mapped-context-v6','custody-mapped-context-v1']:
        p=HERE.parent/n/'source-manifest.json';m=json.loads(p.read_bytes());add(bind(p))
        for row in m['files']:add(row)
    for p in (SOURCE/'packages/0001').rglob('*'):
        if p.is_file():add(bind(p))
    context=RUN/'context-R03-custody-mapping-0002.json';c=json.loads(context.read_bytes());assert c['strict_coverage']=='PASS'
    for row in c['source_bindings']:add({'path':row['path'],'sha256':row['sha256']})
    for p in [context,RUN/'CONTEXT-R03-custody-mapping-0001.md',RUN/'context-R03-custody-mapping-0001.json',RUN/'custody-mapping-predecessor-terminal-0001.json']:add(bind(p))
    for p in (HERE.parent/'custody-mapped-context-v1').rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:add(bind(p))
    def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
    old=methods(HERE.parent/'mapped-context-v6/run_checks.py');new=methods(HERE/'test_original_mapping.py');assert old==new and len(old)==20
    assert len(methods(HERE/'test_raw_mapping.py'))==9
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            if p.suffix=='.py':ast.parse(p.read_bytes())
            add(bind(p))
    assert EXE.is_file() and not EXE.is_symlink() and hashlib.sha256(EXE.read_bytes()).hexdigest()==EXE_SHA
    m={'schema_version':'lab-original-source-native-mapper-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),
        'original_source_binding':bind(SOURCE/'source-manifest.json'),'original_package_binding':bind(SOURCE/'packages/0001/manifest.json'),
        'original_mapping_binding':bind(HERE.parent/'mapped-context-v6/source-manifest.json'),'context_binding':bind(context),
        'selected_native_executable':{'path':str(EXE),'sha256':EXE_SHA},
        'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},
        'original20assertion_ASTs_retained':True,'additional_raw_source_methods':9,'frozen_before_native_and_cold_source_effects':True,
        'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Candidate native representation for exact original-source context. Actual current host permission/Context delivery/active Session/full public API and original plan remain required.'}
    (HERE/'source-manifest.json').open('x').write(json.dumps(m,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'FROZEN','files':len(rows),'source_binding':bind(HERE/'source-manifest.json'),'methods':29}))
if __name__=='__main__':main()
