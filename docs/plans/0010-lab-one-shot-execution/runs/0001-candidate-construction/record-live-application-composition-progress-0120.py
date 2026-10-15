"""Bind actual current Session composition and retain all remaining plan work."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
API=BASE/'api-v83'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def main():
    parent_path=API/'receipts/R03-0119.json'
    parent=load(parent_path)
    actual_path=RUN/'API83-live-application-composition-0002.json'
    actual=load(actual_path)
    assert actual['result']=='PASS' and actual['cases_run']==1
    assert actual['failure_count']==actual['error_count']==0
    assert len(actual['phases'])==5 and all(phase['result']=='PASS' for phase in actual['phases'])
    assert actual['actual_clock_and_source_guards_unchanged'] and not actual['application_runtime_qualified']
    report79=RUN/'API79-machine-lifecycle-full-0001.json'
    terminal79=RUN/'API79-machine-lifecycle-full-terminal-0001.json'
    assert load(report79)['actual_cases']==20 and load(terminal79)['actual_exit_code']==1
    rows={row['path']:row for row in parent['files']}
    for row in actual['files']:rows[row['path']]=row
    for path in [parent_path,actual_path,report79,terminal79,
                 RUN/'qualify-API83-Machine-seven-read-observation-0001.py',Path(__file__).resolve()]:
        rows[bind(path)['path']]=bind(path)
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    value={**parent,'files':[rows[key] for key in sorted(rows)],'parent_progress_binding':bind(parent_path),
           'actual_composition_qualification_binding':bind(actual_path),'actual_composition_qualification_posture':'PASS',
           'actual_live_application_policy_and_Session_composition_qualified':True,
           'actual_composition_job':None,'actual_Machine_observation_job':60417,
           'API79_original20_terminal_binding':bind(terminal79),'API79_original20_report_binding':bind(report79),
           'API79_original_case_count':20,'API79_original_case_passes':19,'API79_original_case_errors':1,
           'remaining_obligations':[
               'Observe same API80 original20case job19391 and API83 original seven-read method diagnosis job60417. The latter explicitly retains parent-owned test observation after peer disposal; runtime source/clock/permission callbacks remain unchanged.',
               'Create actual current controlled lesson/application/evidence episode and qualify positive lesson.apply and lesson.assess, exact conflict/override, stale Session/cut and instruction/action bounds. Actual policy/Session composition alone does not establish application.',
               'Implement all11 remaining original public operations: '+','.join(parent['remaining_unimplemented_operations'])+'.',
               'Complete original R03,R05 journeys,R06 privacy,R07 acceptance and S02 exact complete package before sole actual R08 owner response; retain separately scoped A01-A04.'],
           'change':'API83 actual candidate policy/Session composition passed1actual case with5phases: exact authenticated policy and closed-schema refusals, original current Context/Session opening with original900second ceiling, exact journal retry without new resource, actual closing/RAM disposal, and refusal of new-key identity reuse after closure. Original real clocks/source guards remained. API79 full20completed19passes1observation-helper error; preserve exact terminal. API83 original seven-read method now runs with explicitly declared parent-owned observation to retain returned transport outcomes even after peer closes.23handlers/11missing and36/46tasksclosed remain. No positive Lesson Application, outcome, current Machine/fullAPI qualification, admission or owner outcome.',
           'lesson_apply_actual_runtime_qualified':False,'lesson_assess_actual_runtime_qualified':False,
           'whole_API_qualified':False,'task_complete':False,'goal_complete':False,
           'claim_ceiling':'Actual policy/Session composition and exact original suite observations only. Positive lesson/application/outcome, current Machine, fullAPI and whole-plan admission remain.'}
    output=API/'receipts/R03-0120.json'
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','binding':bind(output),'bound_files':len(rows),'actual_composition_cases':1,'authored_handlers':23,'remaining_handlers':11}),flush=True)


if __name__=='__main__':main()
