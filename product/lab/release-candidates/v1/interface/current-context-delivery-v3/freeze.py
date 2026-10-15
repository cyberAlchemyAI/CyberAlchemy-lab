"""Freeze exact delivery/protocol/schema/import closure before host/key effects."""
import ast
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
MAPPED=HERE.parent/'current-mapped-context-v2'
PARENT=HERE.parent/'current-context-delivery-v2'
API=HERE.parent/'api-v25'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists()
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path']
        rows[row['path']]=row
    for p in [RUN/'current-mapping-checks-proof-0002.json',RUN/'current-mapping-audit-proof-0002.json',RUN/'current-context-audit-proof-0002.json',RUN/'current-Agent-development-observation-failed-proof-0002.json',RUN/'current-Agent-API27-complete-failed-proof-0001.json',PARENT/'source-manifest.json']:
        for row in json.loads(p.read_bytes())['files']:add(row)
        add(bind(p))
    # Schema use imports the protocol module and pure source-byte helpers. No API
    # transport/handler is invoked. Bind their full declared schema/profile inputs.
    protocol_paths=[API/'protocol.py',API/'source_bridge.py',API/'authentication.schema.json',API/'source-manifest.json',
        HERE.parent/'inspection/lab_operator.py',HERE.parent/'coupling/loader.py',HERE.parent/'corrections-v1/loader.py']
    for p in [API/'schema-inputs.json',API/'contract-profile.json']:
        value=json.loads(p.read_bytes());add(bind(p))
        for row in value['files']:add(row)
        for key in ['original_operation_catalog_binding','original_schema_inputs_binding']:
            if key in value:add(value[key])
    for p in protocol_paths:add(bind(p))
    for p in (API/'schemas').glob('*.schema.json'):add(bind(p))
    context=RUN/'context-R03-current-context-delivery-0003.json';c=json.loads(context.read_bytes());assert c['strict_coverage']=='PASS'
    for row in c['source_bindings']:add(row)
    add(bind(context))
    original=methods(PARENT/'test_original_delivery.py');new=methods(HERE/'test_original_delivery.py')
    assert original==new and len(original)==38
    oldraw=methods(PARENT/'test_raw_delivery.py');newraw=methods(HERE/'test_raw_delivery.py')
    retained=[k for k in oldraw if newraw.get(k)==oldraw[k]];assert len(retained)==8 and len(newraw)==9
    for p in HERE.rglob('*'):
        if p.is_file():
            if p.suffix=='.py':ast.parse(p.read_bytes())
            add(bind(p))
    environment={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
    assert environment=={'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}
    m={'schema_version':'lab-current-context-delivery-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'qualified_mapper_source_binding':bind(MAPPED/'source-manifest.json'),'qualified_mapper_package_binding':bind(MAPPED/'packages/0001/manifest.json'),
        'current_API_profile_binding':bind(API/'contract-profile.json'),'API_protocol_code_binding':bind(API/'protocol.py'),'API_schema_inputs_binding':bind(API/'schema-inputs.json'),'API_source_manifest_provenance_binding':bind(API/'source-manifest.json'),
        'protocol_dependency_scope':'Exact selected schema/profile/module-import closure. No API transport/handler invocation or wholeAPI qualification is inferred.','context_binding':bind(context),'environment':environment,'original38assertion_ASTs_preserved':True,'retained_raw_methods':retained,'source_specific_raw_method_successors':[],'additional_lifetime_method':'test_47_declared_lifetime_keeps_actual_request_host_and_source_bounds','expected_tests':47,'original46assertion_ASTs_preserved':True,'lifetime_policy_binding':bind(HERE/'lifetime-policy.json'),
        'frozen_before_owned_hostpermission_key_or_view_effects':True,'authority_effect':'none','actual_owner_outcome':None,'current_Agent_qualified':False}
    p=HERE/'source-manifest.json'
    with p.open('x') as f:json.dump(m,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(p),'files':len(rows),'expected_tests':47}),flush=True)
if __name__=='__main__':main()
