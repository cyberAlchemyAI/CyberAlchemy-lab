"""Freeze corrected carrier realization and new episode before any signer effects."""
import ast
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
ADAPTER=HERE.parent/'current-source-adapter-v2'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists()
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path']
        rows[row['path']]=row
    for p in [RUN/'current-source-adapter-checks-proof-0002.json',RUN/'current-source-adapter-audit-proof-0002.json']:
        for row in json.loads(p.read_bytes())['files']:add(row)
        add(bind(p))
    context=RUN/'context-R03-current-participation-implementation-repair-0003.json'
    c=json.loads(context.read_bytes());assert c['strict_coverage']=='PASS'
    for row in c['source_bindings']:add(row)
    add(bind(context))
    old=methods(HERE.parent/'current-participation-checks-v1/checks.py');new=methods(HERE/'checks.py')
    assert len(old)==16 and len(new)==19 and all(new[k]==v for k,v in old.items())
    for p in [*HERE.glob('*'),*ADAPTER.glob('*.py')]:
        if p.is_file():
            if p.suffix=='.py':ast.parse(p.read_bytes())
            add(bind(p))
    m={'schema_version':'lab-current-participation-source/v3-candidate','files':[rows[k] for k in sorted(rows)],'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'context_binding':bind(context),'implementation_code_binding':bind(ADAPTER/'reader.py'),'implementation_entrypoint_ref':ADAPTER.relative_to(ROOT).as_posix()+'/reader.py#SelectedReader.open_signed','previous_candidate_source_binding':bind(HERE.parent/'current-participation-v2/source-manifest.json'),'previous_candidate_package_binding':bind(HERE.parent/'current-participation-v2/packages/0001/manifest.json'),'original16method_ASTs_retained':True,'new_methods':3,'expected_tests':19,'fixed_new_episode_binding':bind(HERE/'episode-contract.json'),'authority_effect':'none','actual_owner_outcome':None,'current_Agent_qualified':False}
    path=HERE/'source-manifest.json'
    with path.open('x') as f:json.dump(m,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(path),'files':len(rows),'expected_tests':19}),flush=True)
if __name__=='__main__':main()
