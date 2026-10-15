"""Freeze exact distinct episode and reader realization before owned effects."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
ADAPTER=HERE.parent/'current-source-adapter-v4'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists()
    prior=HERE.parent/'current-participation-v4';rows={}
    def add(row):
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path']
        rows[row['path']]=row
    for row in json.loads((prior/'source-manifest.json').read_bytes())['files']:add(row)
    for row in json.loads((prior/'packages/0001/manifest.json').read_bytes())['files']:add(row)
    for version in ('v2','v3','v4'):add(bind(HERE.parent/('current-participation-'+version)/'packages/0001/period.json'))
    context=RUN/'context-R03-current-source-construction-0005.json';value=json.loads(context.read_bytes());assert value['strict_coverage']=='PASS'
    for row in value['source_bindings']:add(row)
    add(bind(context))
    original=methods(HERE.parent/'current-participation-checks-v1/checks.py');current=methods(HERE/'checks.py')
    assert len(original)==16 and len(current)==20 and all(current[k]==v for k,v in original.items())
    original_adapter=methods(HERE.parent/'current-source-adapter-v2/checks.py');current_adapter=methods(ADAPTER/'checks.py')
    assert len(original_adapter)==17 and len(current_adapter)==20 and all(current_adapter[k]==v for k,v in original_adapter.items())
    for p in [*HERE.iterdir(),*ADAPTER.iterdir()]:
        if p.is_file():
            if p.suffix=='.py':ast.parse(p.read_bytes())
            add(bind(p))
    value={'schema_version':'lab-current-participation-source/v5-candidate','files':[rows[k] for k in sorted(rows)],'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'context_binding':bind(context),'implementation_code_binding':bind(ADAPTER/'reader.py'),'implementation_entrypoint_ref':str(ADAPTER.relative_to(ROOT))+'/reader.py#SelectedReader.open_signed','previous_candidate_source_binding':bind(prior/'source-manifest.json'),'previous_candidate_package_binding':bind(prior/'packages/0001/manifest.json'),'original16method_ASTs_retained':True,'original17adapter_method_ASTs_retained':True,'expected_tests':20,'three_successor_binding_cases_updated_to_exact_new_sources':True,'additional_original_period_preservation_case':True,'fixed_new_episode_binding':bind(HERE/'episode-contract.json'),'authority_effect':'none','actual_owner_outcome':None,'current_Agent_qualified':False}
    p=HERE/'source-manifest.json'
    with p.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(p),'files':len(rows),'expected_tests':20}),flush=True)
if __name__=='__main__':main()
