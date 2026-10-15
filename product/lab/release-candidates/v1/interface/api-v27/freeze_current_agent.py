"""Freeze selected new Context, complete predecessor closure and real regression inputs."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PARENT=HERE.parent/'api-v25';CONTEXT=HERE.parent/'current-context-delivery-v2'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'receipts').exists()
    context=RUN/'context-R03-current-Agent-API-0002.json';c=json.loads(context.read_bytes());assert c['strict_coverage']=='PASS' and c['blockers']==[]
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path'];rows[row['path']]=row
    parent=PARENT/'receipts/R03-0031.json';receipt=json.loads(parent.read_bytes());assert receipt['result']=='PASS' and receipt['Context_construction_from_new_episode_qualified'] and not receipt['current_Agent_qualified']
    for row in receipt['files']:add(row)
    add(bind(parent))
    failed=RUN/'current-Agent-API-failed-proof-0001.json'
    for row in json.loads(failed.read_bytes())['files']:add(row)
    add(bind(failed))
    for row in c['source_bindings']:add(row)
    add(bind(context))
    profile=json.loads((PARENT/'contract-profile.json').read_bytes())
    assert len(profile['implemented_operations'])==13
    profile['files']=[bind(HERE/(ROOT/r['path']).relative_to(PARENT) if (ROOT/r['path']).is_relative_to(PARENT) else ROOT/r['path']) for r in profile['files']]
    profile['selected_current_context_source_binding']=bind(CONTEXT/'source-manifest.json')
    profile['selected_current_context_package_binding']=bind(CONTEXT/'packages/0001/manifest.json')
    profile['claim_ceiling']='Thirteen candidate handlers selecting exact new episode Context/source/mapper. All146 integration and134 metadata/export checks plus4 current control checks pending. No governing owner coverage, canonical admission, remaining21APIs or full46criteria inferred.'
    put(HERE/'contract-profile.json',profile)
    allowed={
        'run_session_checks.py':{'test_29_source_and_period_unchanged','test_30_current_handler_profile_retains_all_original_contracts','test_31_frozen_producer_modules_retain_original_origins'},
        'test_custody_sessions.py':{'test_29_source_and_period_unchanged','test_30_current_handler_profile_retains_all_original_contracts','test_31_frozen_producer_modules_retain_original_origins'},
        'test_custody_api.py':{'test_11_fixed_original_period_and_owned_host_scope'}}
    counts={};diffs={}
    for name in ['test_preparation.py','test_preparation_corrected.py','run_session_checks.py','test_custody_sessions.py','test_custody_api.py','test_guarded_reads.py','test_metadata_scope.py','test_export_kernel.py','test_file_exports.py']:
        old=methods(PARENT/name);new=methods(HERE/name);assert old.keys()==new.keys(),name
        changed={k for k in old if old[k]!=new[k]};assert changed==allowed.get(name,set()),(name,changed)
        counts[name]=len(new);diffs[name]=sorted(changed)
    assert sum(len(v) for v in diffs.values())==7 and len(methods(HERE/'test_current_controls.py'))==4
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            if p.suffix=='.py':ast.parse(p.read_bytes())
            add(bind(p))
    environment={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
    assert environment=={'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}
    manifest={'schema_version':'lab-current-Agent-API-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'environment':environment,'parent_receipt_binding':bind(parent),'current_Context_source_binding':bind(CONTEXT/'source-manifest.json'),'current_Context_package_binding':bind(CONTEXT/'packages/0001/manifest.json'),'context_binding':bind(context),'test_method_counts':counts,'source_specific_test_method_successors':diffs,'unchanged_test_methods':sum(counts.values())-7,'expected_regression_cases':{'integration':146,'metadata_and_export':134,'independent_current_controls':4},'fixture_successors':{'legacy_Session_journeys':'New actual custody source and backend; legacy method behaviors retained except explicit period/path/profile assertions. Old source branch preserved and actual expired grant refusal tested.','metadata':'Current source view with exact frozen original-expired period fixture; all22 test method ASTs unchanged.'},'freeze_precedes_host_key_workspace_or_Session_effects':True,'authority_effect':'none','actual_owner_outcome':None,'current_Agent_qualified':False,'task_complete':False}
    put(HERE/'source-manifest.json',manifest)
    print(json.dumps({'result':'FROZEN','source_binding':bind(HERE/'source-manifest.json'),'profile_binding':bind(HERE/'contract-profile.json'),'files':len(rows),'original_unchanged_method_ASTs':manifest['unchanged_test_methods'],'source_specific_method_successors':7,'expected_suite_counts':manifest['expected_regression_cases']}),flush=True)
if __name__=='__main__':main()
