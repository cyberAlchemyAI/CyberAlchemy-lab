"""Bind original rule obligations and explicit original carrier contracts."""
import ast
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
def bind(path):return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def methods(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'carrier-contracts.json').exists()
    parent=HERE.parent/'classification-rules-v2';proof=parent/'receipts/proof-0001.json'
    actual=json.loads(proof.read_bytes());assert actual['result']=='PASS' and actual['actual_cases']==21 and actual['actual_terminal_exit_code']==0
    prior=methods(parent/'checks.py');current=methods(HERE/'checks.py')
    assert len(prior)==21 and len(current)==35 and all(current[k]==v for k,v in prior.items())
    selected={}
    def add(path):
        row=bind(path);old=selected.get(row['path']);assert old in (None,row);selected[row['path']]=row
    for row in json.loads((parent/'source-manifest.json').read_bytes())['files']:
        assert bind(ROOT/row['path'])==row;add(ROOT/row['path'])
    add(parent/'source-manifest.json');add(proof)
    contracts={};schemas=[];unsupported=[]
    for path in sorted((ROOT/'authority/artifact-types').glob('*/v*/schema.json')):
        add(path);schemas.append(bind(path));artifact=path.parent/'artifact.json'
        if not artifact.exists():unsupported.append({'path':str(path.relative_to(ROOT)),'reason':'No descriptor'});continue
        add(artifact);value=json.loads(artifact.read_bytes());field=value.get('instance_contract',{}).get('identity_field')
        if not field or value.get('schema_digest')!=bind(path)['sha256'] or not value.get('classification',{}).get('semantic_kind'):
            unsupported.append({'path':str(artifact.relative_to(ROOT)),'reason':'No exact declared identity/semantic kind/schema digest'});continue
        carrier=value['artifact_type_ref'];assert carrier not in contracts
        contracts[carrier]={'artifact_binding':bind(artifact),'schema_binding':bind(path),'identity_field':field,'semantic_kind':value['classification']['semantic_kind']}
    for directory in ['docs/proposals/0007-lab-integrated-schema-package/schemas','docs/proposals/0006-lab-artifact-storage/schemas']:
        for path in (ROOT/directory).glob('*.schema.json'):add(path);schemas.append(bind(path))
    assert 'cal.artifact-type.product-identity/v2' in contracts
    table={'schema_version':'lab-explicit-carrier-identity-table/v1-candidate','contracts':contracts,'schemas':schemas,'unsupported_descriptors':unsupported,'authority_effect':'none'}
    with (HERE/'carrier-contracts.json').open('x') as f:json.dump(table,f,indent=2,sort_keys=True);f.write('\n')
    for path in HERE.iterdir():
        if path.is_file():
            if path.suffix=='.py':ast.parse(path.read_bytes())
            add(path)
    for path in [HERE.parent/'current-participation-v4/packages/0001/setup-artifacts/product.json',HERE.parent/'current-mapped-context-v3/packages/0001/mapping.json',RUN/'classification-original-carrier-identity-finding-0001.json']:add(path)
    context={'schema_version':'lab-bounded-context/v1-candidate','task':'R03 original carrier classification','strict_coverage':'PASS','blockers':[],
        'original_test_method_ASTs_preserved':21,'new_typed_carrier_cases':14,
        'constraints':['Original bodies are never rewritten into a uniform node schema.','Exact declared carrier identity fields and schemas; unknown carriers are refused.','Header authority scope and immutable revision remain distinct from domain scope and inline model version.','Actual host authenticates caller and proves complete current/prospective cut and schema/core closure.','Original34API/46tasks/21remaining qualifications and sole finalR08 remain.'],
        'source_bindings':list(selected.values()),'actual_owner_outcome':None,'authority_effect':'none'}
    path=RUN/'context-R03-classification-rules-0003.json'
    with path.open('x') as f:json.dump(context,f,indent=2,sort_keys=True);f.write('\n')
    add(path)
    manifest={'schema_version':'lab-classification-rule-source/v1-candidate','files':list(selected.values()),'context_binding':bind(path),'expected_tests':35,'original_test_method_ASTs_preserved':21,'public_API_qualified':False,'runtime_conformance_proven':False,'task_complete':False,'actual_owner_outcome':None,'authority_effect':'none'}
    with (HERE/'source-manifest.json').open('x') as f:json.dump(manifest,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'source_binding':bind(HERE/'source-manifest.json'),'files':len(selected),'explicit_carriers':len(contracts),'unsupported_descriptors':len(unsupported),'expected_tests':35}),flush=True)
if __name__=='__main__':main()
