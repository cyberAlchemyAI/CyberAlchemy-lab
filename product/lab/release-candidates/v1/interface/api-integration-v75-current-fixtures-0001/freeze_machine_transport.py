"""Freeze the Machine successor only after exact completed dependency proofs."""
import ast
import copy
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
PARENT=HERE.parent/'api-v34'
CONTEXT=HERE.parent/'current-context-delivery-v6'
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
CONTEXT_PIN='d3ecda8d3c796e402e87efa25036ca4867534966ad4e50acb83741dc4fa9b010'
PARENT_PIN='4b411975d34babbd275cc60856b259091b360aed4df737226867a563c1a2ac2c'


def bind(path):
    return {'path':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):return json.loads(path.read_bytes())


def put(path,value):
    with path.open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')


def methods(path):
    return {node.name:ast.dump(node,include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')}


def main():
    output=HERE/'source-manifest.json';profile_path=HERE/'contract-profile.json'
    bounded_context=RUN/'context-R03-machine-transport-0001.json'
    assert not output.exists() and not profile_path.exists() and not bounded_context.exists()
    source=PARENT/'source-manifest.json';assert bind(source)['sha256']==PARENT_PIN
    context_source=CONTEXT/'source-manifest.json';assert bind(context_source)['sha256']==CONTEXT_PIN
    context_proof=CONTEXT/'receipts/qualification-0001.json';proof=load(context_proof)
    assert proof['result']=='PASS'
    assert proof['source_binding']==bind(context_source)
    assert proof['actual_build_exit_code']==proof['actual_check_exit_code']==proof['actual_audit_exit_code']==0
    assert proof['actual_generated_carriers']==30 and proof['exact_native_joins']==25 and proof['raw_source_bodies']==23
    # Explicit full successful terminal and independent audit are separately
    # required even if a future qualification receipt changes its field names.
    terminals=load(RUN/'current-context-delivery-terminal-0006.json')
    assert terminals['selected_exit_codes']=={'build':0,'checks':0}
    assert terminals['build']['terminal_observed'] and terminals['checks']['terminal_observed']
    audit=load(RUN/'current-context-audit-terminal-0006.json')
    assert audit['terminal_observed'] and audit['exit_code']==0
    checks=load(CONTEXT/'receipts/checks.json')
    assert checks['result']=='PASS' and checks['tests_run']==checks['expected_tests']==50
    assert len(checks['cases'])==50 and all(row['result']=='PASS' for row in checks['cases'])
    assert checks['source_sha256']==CONTEXT_PIN
    controls=load(PARENT/'receipts/current-controls.json')
    termination=load(PARENT/'receipts/termination-boundary-checks-0002.json')
    assert controls['result']=='PASS' and controls['tests_run']==controls['expected_tests']==11
    assert termination['result']=='PASS' and termination['tests_run']==termination['expected_tests']==6
    assert all(row['result']=='PASS' for row in controls['cases']+termination['cases'])
    assert load(RUN/'current-Agent-controls-terminal-0008.json')['exit_code']==0
    assert load(RUN/'session-termination-boundary-terminal-0002.json')['exit_code']==0
    # Selection edits must occur only after completed Context qualification.
    bridge=(HERE/'source_bridge.py').read_text()
    sessions=(HERE/'custody_context_sessions.py').read_text()
    assert "path=HERE.parent/'current-context-delivery-v6'" in bridge and CONTEXT_PIN in bridge
    assert "DELIVERY_PIN='"+CONTEXT_PIN+"'" in sessions
    changed={'service.py','custody_context_sessions.py','source_bridge.py'}
    observed_fixture_helpers={'test_file_exports.py','test_review_api.py','test_custody_sessions.py','test_custody_api.py'}
    inherited=[]
    for old in PARENT.rglob('*'):
        if not old.is_file() or any(part in old.parts for part in ('receipts','__pycache__')):continue
        relative=old.relative_to(PARENT)
        if relative.as_posix() in ('source-manifest.json','contract-profile.json'):continue
        current=HERE/relative;assert current.is_file(),str(relative)
        if relative.as_posix() not in changed|observed_fixture_helpers:assert current.read_bytes()==old.read_bytes(),str(relative)
        if current.suffix=='.py':
            assert methods(current)==methods(old),str(relative)
            inherited.extend(str(relative)+':'+method for method in methods(old))
    assert len(inherited)==245
    assert len(methods(HERE/'test_machine_transport.py'))==14
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row,row['path']
        assert bind(ROOT/row['path'])==row,row['path'];rows[row['path']]=row
    for document in [load(source),load(context_source),proof]:
        for row in document['files']:add(row)
    inputs=[source,context_source,context_proof,RUN/'current-context-delivery-terminal-0006.json',
            RUN/'current-context-audit-terminal-0006.json',PARENT/'receipts/current-controls.json',
            PARENT/'receipts/termination-boundary-checks-0002.json',RUN/'current-Agent-controls-terminal-0008.json',
            RUN/'session-termination-boundary-terminal-0002.json',RUN/'authorization.json',HERE/'MACHINE-TRANSPORT.md']
    put(bounded_context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 actual Machine transport integration',
                        'strict_coverage':'PASS','blockers':[],'source_bindings':[bind(path) for path in inputs],
                        'constraints':['All245inherited assertion method ASTs remain unchanged.',
                                       'Full Context6original50 and independent audit precede selecting its exact pins.',
                                       'Original900second Session interval and fixed Source3Assignment period remain unchanged.',
                                       'Actual live Session/Agent and nonce signature; one peer per resource; roles empty and zero action budget.',
                                       'Borrowed service acquires no second Session custody lease.',
                                       'Every use rereads current source, schema and parent permission; no permission cache or callback replacement.',
                                       'All14new actual cases and complete original146/134/review/controls/termination suites and independent audit remain required.',
                                       'Final R08afterS02 remains the sole actual owner checkpoint; no canonical admission or activation.'],
                        'actual_owner_outcome':None,'authority_effect':'none'})
    profile=copy.deepcopy(load(PARENT/'contract-profile.json'))
    profile['files']=[bind(HERE/(ROOT/row['path']).relative_to(PARENT))
                      if (ROOT/row['path']).is_relative_to(PARENT) else row for row in profile['files']]
    profile['files'].append(bind(HERE/'machine_transport.py'))
    profile['machine_transport_context_binding']=bind(bounded_context)
    profile['qualified_context_proof_binding']=bind(context_proof)
    profile['claim_ceiling']='Fourteen authored public handlers and proposed host-bound Machine transport. All successor runtime suites and independent integrated audit remain required. No owner outcome, admission, activation or release.'
    assert len(profile['implemented_operations'])==14
    put(profile_path,profile)
    for path in inputs+[bounded_context]:add(bind(path))
    for path in HERE.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts and 'receipts' not in path.parts:
            if path.suffix=='.py':ast.parse(path.read_bytes())
            add(bind(path))
    manifest={'schema_version':'lab-actual-Machine-transport-source/v1-candidate',
              'files':[rows[key] for key in sorted(rows)],'environment':load(source)['environment'],
              'parent_source_binding':bind(source),'context_binding':bind(bounded_context),
              'qualified_context_proof_binding':bind(context_proof),'unchanged_inherited_methods':inherited,
              'new_actual_Machine_cases':14,'expected_regression_cases':load(source)['expected_regression_cases'],
              'changed_production_files':sorted(changed)+['machine_transport.py'],
              'fixture_helpers_with_durable_observation':sorted(observed_fixture_helpers),
              'original_contracts_preserved':34,'authored_handler_count':14,'qualified_public_handler_count':13,
              'remaining_qualified_operations':21,'whole_API_qualified':False,'current_Agent_qualified':False,
              'freeze_precedes_new_owned_fixture_effects':True,'time_bounds_extended':False,'permissions_cached':False,
              'task_complete':False,'goal_complete':False,'actual_owner_outcome':None,'authority_effect':'none'}
    put(output,manifest)
    print(json.dumps({'result':'FROZEN','files':len(rows),'source_binding':bind(output),
                      'profile_binding':bind(profile_path),'inherited_methods':245,'new_cases':14}),flush=True)


if __name__=='__main__':main()
