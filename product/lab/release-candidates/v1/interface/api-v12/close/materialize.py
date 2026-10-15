"""Bind the selected partial R03 proof, immutable predecessors and review members."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=BASE.parents[5]
EXPECTED_PROFILE='e1ea018567f49955ce14f756f83f156d4522599682742475c2a0ec5812c26e44'
EXPECTED_PARENT='e7024defe45d00ae4093dfe3152a288fc6fc05a27237623f76bbf73dab1b8c21'

def digest(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(Path(path).read_bytes())
def binding(path):return {'path':Path(path).relative_to(ROOT).as_posix(),'sha256':digest(Path(path).read_bytes())}
def require(value,message):
    if not value:raise ValueError(message)

def main():
    require(digest((BASE/'contract-profile.json').read_bytes())==EXPECTED_PROFILE,'selected profile differs')
    audit=load(BASE/'audit/result.json');process=load(BASE/'receipts/processes/0001/result.json')
    tests=load(BASE/'receipts/attempts/0001/terminal.json');regression=load(BASE/'receipts/parent-regression/0001/terminal.json')
    require(audit['result']==process['result']==tests['result']==regression['result']=='PASS','selected proof incomplete')
    require(tests['tests_run']==47 and regression['tests_run']==157 and len(process['children'])==7
        and len(process['checks'])==29 and len(audit['checks'])==135,'selected terminal scope differs')
    for b in load(BASE/'audit/source-manifest.json')['files']:
        require(digest((ROOT/b['path']).read_bytes())==b['sha256'],'independent audit source changed')
    parent=BASE.parent/'api-v4/receipts/R03-0007.json'
    require(digest(parent.read_bytes())==EXPECTED_PARENT,'immutable four-reader proof changed')
    files={}
    def add(b):
        path=ROOT/b['path'];require(path.is_file() and not path.is_symlink() and digest(path.read_bytes())==b['sha256'],'bound evidence changed: '+b['path'])
        if b['path'] in files:require(files[b['path']]==b,'contradictory byte binding')
        files[b['path']]=b
    for b in load(parent)['files']:add(b)
    add(binding(parent))
    # Failure/supersession history is evidence only, never a selected target.
    attempts=[]
    for version in range(5,13):
        tree=BASE.parent/('api-v'+str(version))
        require(tree.is_dir(),'missing preserved candidate predecessor')
        for path in sorted(tree.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:continue
            if path==BASE/'receipts/R03-0008.json':continue
            add(binding(path))
        attempts.append({'version':'api-v'+str(version),'selected':version==12,
            'source_binding':binding(tree/'source-manifest.json'),
            'test_observations':[binding(p) for p in sorted((tree/'receipts/attempts').glob('*/terminal.json'))],
            'process_observations':[binding(p) for p in sorted((tree/'receipts/processes').glob('*/terminal.json'))]})
    run=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
    add(binding(run/'context-R03-preparation.json'));add(binding(run/'authorization.json'))
    dag=load(run/'dag.json')
    for task in ('R01','C13','W01','R02'):
        node=next(n for n in dag['nodes'] if n['id']==task)
        require(node['status'].startswith('complete') or node['status']=='satisfied-scoped','dependency incomplete: '+task)
        for b in node.get('completion_evidence',[]):
            add({'path':b['path'],'sha256':b['sha256']})
            for original in load(ROOT/b['path']).get('files',[]):add(original)
    profile=load(BASE/'contract-profile.json');catalog=load(ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json')
    supported=profile['implemented_operations'];remaining=[r['operation'] for r in catalog['operations'] if r['operation'] not in supported]
    require(len(supported)==7 and len(remaining)==27,'whole original API scope narrowed')
    members=load(BASE/'review-members.json')
    require(len(members['members'])==5 and all(m['actual_owner_outcome'] is None and m['admission_posture']=='candidate-unadmitted' for m in members['members']), 'candidate owner boundary differs')
    checks=[{'suite':'selected-candidate-guards','test_count':47,'result':'PASS'},
        {'suite':'immutable-four-reader-regression-under-selected-environment','test_count':157,'result':'PASS'},
        *process['checks'],*audit['checks']]
    result={'schema_version':'lab-R03-candidate-preparation-proof/v1-candidate','task':'R03','result':'PASS','task_complete':False,
        'selected_profile_binding':binding(BASE/'contract-profile.json'),'parent_binding':binding(parent),
        'selected_implementation_root':BASE.relative_to(ROOT).as_posix(),'supported_operations':supported,'remaining_operations':remaining,
        'independent_review_members':5,'observed_checks':368,'new_guard_tests':47,'parent_regression_tests':157,
        'actual_process_checks':29,'independent_audit_checks':135,'terminal_real_processes':7,'actual_process_interruptions':2,
        'wire_frames_verified':45,'exact_original_api_calls_verified':13,'checks':checks,'attempt_history':attempts,
        'source_effects_applied':0,'canonical_effects_applied':0,'actual_owner_outcome':None,'human_pilot_outcome':None,
        'active_Agent_Sessions_created':0,'private_keys_exported':False,'Session_memory_exported':False,
        'owned_fixture_roots_removed':True,'authority_effect':'none','goal_complete':False,
        'remaining_obligations':['Implement the remaining 27 real API handlers and their complete original preconditions/postconditions.',
            'Close full carrier-specific semantic reference and declared schema/privacy closure before affected use.',
            'Integrate fresh source-bound Agent Context/Ontology delivery, assignment/capability authority, ephemeral Session identity/memory and exact termination.',
            'Integrate exact final proposal/Decision/owner review, authorized transactions, workflow/action/learning/ontology/projection/file/package/install and release journeys.',
            'Retain broader scoped candidate queues, complete current/historical joins, realistic complete review/receipt/why-path examples and all original R03 acceptance criteria.',
            'R04 actual human pilot; R05 final selected environment/package integration; S02 complete owner/registry/target/schema/core closure; actual R08 owner outcomes.'],
        'claim_ceiling':'Selected partial candidate operator APIs and exact real observations only. Construction pass, semantic reference closure, owner decision, admission, Work satisfaction, activation and stable release remain independent.',
        'files':sorted(files.values(),key=lambda b:b['path']),'recorded_at':datetime.now(timezone.utc).isoformat()}
    output=BASE/'receipts/R03-0008.json';require(not output.exists(),'partial proof already exists')
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':'PASS','task_complete':False,'checks':368,'file_bindings':len(files),'receipt':binding(output)}))

if __name__=='__main__':main()
