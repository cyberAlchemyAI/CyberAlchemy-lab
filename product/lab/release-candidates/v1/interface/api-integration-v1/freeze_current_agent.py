"""Freeze API31 only against the exact qualified Context5 and fact helper."""
import ast
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PARENT=HERE.parent/'api-v30'
CONTEXT=HERE.parent/'current-context-delivery-v5'
HELPER=HERE.parent/'fact-read-scope-v1'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,value):
    with p.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'contract-profile.json').exists()
    qualified=CONTEXT/'receipts/qualification-0001.json';q=json.loads(qualified.read_bytes())
    assert q['result']=='PASS' and q['selected_methods']==50 and q['actual_check_exit_code']==0 and q['actual_audit_exit_code']==0
    helper=HELPER/'receipts/proof-0001.json';h=json.loads(helper.read_bytes())
    assert h['result']=='PASS' and h['tests_run']==h['expected_tests']==18 and h['actual_terminal_exit_code']==0
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path']
        rows[row['path']]=row
    parents=[qualified,helper,PARENT/'receipts/R03-0038.json',RUN/'current-Agent-development-observation-failed-proof-0003.json',RUN/'source-guard-profile-proof-0002.json']
    for path in parents:
        for row in json.loads(path.read_bytes())['files']:add(row)
        add(bind(path))
    context=RUN/'context-R03-current-Agent-API-0006.json';c=json.loads(context.read_bytes());assert c['strict_coverage']=='PASS' and c['blockers']==[]
    for row in c['source_bindings']:add(row)
    add(bind(context))
    pin=bind(CONTEXT/'source-manifest.json')['sha256']
    for name in ['source_bridge.py','custody_context_sessions.py']:
        path=HERE/name;text=path.read_text();assert text.count('UNFROZEN_CONTEXT5_SOURCE_PIN')==1
        path.write_text(text.replace('UNFROZEN_CONTEXT5_SOURCE_PIN',pin))
    counts={};added={}
    for path in PARENT.glob('*.py'):
        old=methods(path)
        if not old:continue
        new=methods(HERE/path.name);assert all(new.get(k)==v for k,v in old.items()),path.name
        counts[path.name]=len(old);added[path.name]=sorted(set(new)-set(old))
    assert sum(counts.values())==224
    assert sum(len(v) for v in added.values())==4 and len(methods(HERE/'test_current_controls.py'))==11
    profile=json.loads((PARENT/'contract-profile.json').read_bytes())
    profile['files']=[bind(HERE/(ROOT/row['path']).relative_to(PARENT) if (ROOT/row['path']).is_relative_to(PARENT) else ROOT/row['path']) for row in profile['files']]
    for name in ['scope.py','__init__.py']:profile['files'].append(bind(HELPER/name))
    profile['selected_current_context_source_binding']=bind(CONTEXT/'source-manifest.json')
    profile['selected_current_context_package_binding']=bind(CONTEXT/'packages/0001/manifest.json')
    profile['qualified_fact_scope_binding']=bind(helper)
    profile['claim_ceiling']='Thirteen candidate handlers with verified pure fact scopes and live host permission checks. All146integration,134metadata/export and11controls pending. Actual Agent lifecycle,21remainingAPIs and full46criteria remain unqualified.'
    put(HERE/'contract-profile.json',profile)
    for path in HERE.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            if path.suffix=='.py':ast.parse(path.read_bytes())
            add(bind(path))
    environment={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
    assert environment=={'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}
    manifest={'schema_version':'lab-current-Agent-API-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'environment':environment,
        'parent_partial_receipt_binding':bind(PARENT/'receipts/R03-0038.json'),'qualified_Context_binding':bind(qualified),
        'current_Context_source_binding':bind(CONTEXT/'source-manifest.json'),'current_Context_package_binding':bind(CONTEXT/'packages/0001/manifest.json'),
        'context_binding':bind(context),'original224assertion_ASTs_preserved':True,'test_method_counts':counts,'additional_methods':added,
        'expected_regression_cases':{'integration':146,'metadata_and_export':134,'independent_current_controls':11},
        'original_public_operations':34,'implemented_operations':13,'remaining_public_operations':21,
        'freeze_precedes_host_key_workspace_or_Session_effects':True,'authority_effect':'none','actual_owner_outcome':None,
        'current_Agent_qualified':False,'task_complete':False}
    put(HERE/'source-manifest.json',manifest)
    print(json.dumps({'result':'FROZEN','source_binding':bind(HERE/'source-manifest.json'),'profile_binding':bind(HERE/'contract-profile.json'),'files':len(rows),'original224method_ASTs_preserved':True,'additional_controls':4}),flush=True)
if __name__=='__main__':main()
