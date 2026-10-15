"""Record proven current failure, private scope repair and pending qualification."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
API=BASE/'api-v84'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def main():
    parent_path=BASE/'api-v83/receipts/R03-0120.json'
    parent=load(parent_path)
    manifest=load(API/'source-manifest.json')
    checked_path=RUN/'API84-Machine-owner-policy-authoring-checks-0001.json'
    checked=load(checked_path)
    assert checked['result']=='PASS' and checked['unchanged_method_ASTs']==323
    diagnosis_path=RUN/'API83-original-Machine-generation-diagnosis-0001.json'
    diagnosis=load(diagnosis_path)
    assert diagnosis['result']=='PASS' and diagnosis['actual_cases']==1
    assert diagnosis['observed']['peer_closed'] and not diagnosis['observed']['resource_closed']
    assert not diagnosis['observed']['actual_Session_expired']
    rows={row['path']:row for row in parent['files']}
    for row in manifest['files']+checked['files']+diagnosis['files']:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    paths=[parent_path,API/'source-manifest.json',API/'contract-profile.json',checked_path,diagnosis_path,
           RUN/'API83-Machine-seven-read-observation-0001.json',
           RUN/'qualify-API84-Machine-seven-read-observation-0001.py',
           RUN/'API84-Machine-seven-read-observation-0001.json',
           RUN/'qualify-API84-Machine-seven-read-observation-0002.py',
           RUN/'qualify-API84-machine-lifecycle-full-0001.py',
           RUN/'run-API84-machine-lifecycle-full-0001.py',
           RUN/'API80-machine-lifecycle-full-0001.json',RUN/'API80-machine-lifecycle-full-terminal-0001.json',
           Path(__file__).resolve()]
    for path in paths:rows[bind(path)['path']]=bind(path)
    actual_path=RUN/'API84-Machine-seven-read-observation-0002.json'
    actual=load(actual_path) if actual_path.exists() else None
    if actual is not None:
        rows[bind(actual_path)['path']]=bind(actual_path)
        for row in actual['files']:rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    mistaken=load(RUN/'API84-Machine-seven-read-observation-0001.json')
    assert any(row['path']=='product/lab/release-candidates/v1/interface/api-v83/source-manifest.json' for row in mistaken['files'])
    value={**parent,'files':[rows[key] for key in sorted(rows)],'parent_progress_binding':bind(parent_path),
           'current_API_version':84,'source_binding':bind(API/'source-manifest.json'),
           'profile_binding':bind(API/'contract-profile.json'),'retained_predecessor_methods':323,
           'unchanged_method_ASTs':323,'exact_handler_count_expectation_revisions':0,
           'Machine_owner_policy_authoring_checks_binding':bind(checked_path),
           'Machine_original_generator_refusal_binding':bind(diagnosis_path),
           'current_Machine_failure_diagnosed':'Original fact-copy scope registers Machine host but unchanged parent policy guard requires its own exact channel; known refusal confirmed before actual Session expiry.',
           'actual_Machine_observation_job':54929,
           'actual_Machine_repair_case_binding':bind(actual_path) if actual is not None else None,
           'actual_Machine_repair_case_posture':actual['result'] if actual is not None else 'running',
           'first_API84_labeled_case_actual_selection':'API83; preserved immutable misselection. Successor0002 asserts exact API84 source/profile hashes and path.',
           'remaining_obligations':[
               'Observe the same actual API84 job54929: original seven-read method with parent-owned test observer. Preserve exact terminal and source/profile selection; initial mislabeled0001selectedAPI83 and is not candidate84 evidence.',
               'After affected case passes, run full original14Machine+6termination selection and qualify private scope wrong-parent/source/resource/callback refusals without replacing clocks or grants.',
               'Create actual current controlled lesson/application/evidence episode and qualify positive lesson.apply/assess, conflicts/overrides, instruction precedence and exact action bounds.',
               'Implement all11 original missing operations: '+','.join(parent['remaining_unimplemented_operations'])+'.',
               'Finish R03,R05,R06,R07 and S02 complete exact package before sole actual R08 owner response; preserve A01-A04 scope.'],
           'change':'Proved current original Machine Context generator failure: fact-scope policy host mismatch closes peer while Session remains live and unexpired. API84 privately composes actual owner policy custody with actual Machine Actor using original sealed-copy class and original pure generator; original transport/auth/clock/permissions/protocol/vault bytes and323testASTs unchanged.7authoring checks pass. Current repaired seven-read case54929 running with independently asserted API84 source/profile.23handlers/11missing unchanged. All original40API79/80suite outcomes preserved; neither wholeMachine norAPIqualified.',
           'current_Agent_qualified':False,'current_Machine_qualified':False,'whole_API_qualified':False,
           'task_complete':False,'goal_complete':False,
           'claim_ceiling':'Actual current known generator refusal and exact private custody repair/source checks. Repaired current Machine, positive lesson application/outcomes, fullAPI and owner admission remain unqualified.'}
    output=API/'receipts/R03-0122.json';output.parent.mkdir(exist_ok=True)
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','binding':bind(output),'bound_files':len(rows),'authored_handlers':23,
                      'remaining_handlers':11,'actual_repaired_case_posture':value['actual_Machine_repair_case_posture']}),flush=True)


if __name__=='__main__':main()
