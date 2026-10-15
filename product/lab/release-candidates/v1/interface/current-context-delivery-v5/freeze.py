"""Freeze Context5 only after the actual fact-scope helper is qualified."""
import ast
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PARENT=HERE.parent/'current-context-delivery-v4'
MAPPED=HERE.parent/'current-mapped-context-v2'
HELPER=HERE.parent/'fact-read-scope-v1'
API=HERE.parent/'api-v25'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists()
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path']
        rows[row['path']]=row
    qualified=PARENT/'receipts/R03-0036.json';helper=HELPER/'receipts/proof-0001.json'
    q=json.loads(qualified.read_bytes());h=json.loads(helper.read_bytes())
    assert q['result']=='PASS' and q['selected_methods']==48
    assert h['result']=='PASS' and h['tests_run']==h['expected_tests']==18
    assert h['actual_terminal_exit_code']==0 and not h['integration_qualified']
    parents=[qualified,helper,RUN/'current-Agent-development-observation-failed-proof-0003.json',RUN/'source-guard-profile-proof-0002.json']
    for p in parents:
        for row in json.loads(p.read_bytes())['files']:add(row)
        add(bind(p))
    context=RUN/'context-R03-current-context-delivery-0005.json';c=json.loads(context.read_bytes())
    assert c['strict_coverage']=='PASS' and c['blockers']==[]
    for row in c['source_bindings']:add(row)
    add(bind(context))
    counts={}
    for name in ['test_original_delivery.py','test_raw_delivery.py']:
        original=methods(PARENT/name);new=methods(HERE/name)
        assert all(new.get(k)==v for k,v in original.items()),name
        counts[name]={'retained':len(original),'new':sorted(set(new)-set(original))}
    assert sum(v['retained'] for v in counts.values())==48
    assert counts['test_original_delivery.py']['new']==['test_49_actual_fact_scope_keeps_original_sources_and_permission','test_50_actual_revocation_during_fact_scope_still_refused']
    assert counts['test_raw_delivery.py']['new']==[]
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            if p.suffix=='.py':ast.parse(p.read_bytes())
            add(bind(p))
    environment={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
    assert environment=={'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}
    manifest={'schema_version':'lab-current-context-delivery-source/v1-candidate','files':[rows[k] for k in sorted(rows)],
        'qualified_mapper_source_binding':bind(MAPPED/'source-manifest.json'),'qualified_mapper_package_binding':bind(MAPPED/'packages/0001/manifest.json'),
        'current_API_profile_binding':bind(API/'contract-profile.json'),'API_protocol_code_binding':bind(API/'protocol.py'),'API_schema_inputs_binding':bind(API/'schema-inputs.json'),
        'API_source_manifest_provenance_binding':bind(API/'source-manifest.json'),
        'protocol_dependency_scope':'Original selected API25 schemas/profile only; no transport/handler or wholeAPI qualification.',
        'qualified_fact_scope_binding':bind(helper),'qualified_parent_Context_binding':bind(qualified),
        'context_binding':bind(context),'environment':environment,'original48assertion_ASTs_preserved':True,
        'test_method_preservation':counts,'expected_tests':50,
        'external_dependency_bindings':[rows[k] for k in sorted(rows) if Path(k).is_absolute()],
        'lifetime_policy_binding':bind(HERE/'lifetime-policy.json'),
        'frozen_before_owned_hostpermission_key_or_view_effects':True,'authority_effect':'none','actual_owner_outcome':None,
        'current_Agent_qualified':False,'task_complete':False}
    p=HERE/'source-manifest.json'
    with p.open('x') as f:json.dump(manifest,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(p),'files':len(rows),'expected_tests':50}),flush=True)
if __name__=='__main__':main()
