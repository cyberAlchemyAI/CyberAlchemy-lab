"""Bind actual seven-read pass; retain full lifecycle and whole plan obligations."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v85'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def main():
    parent_path=API/'receipts/R03-0124.json';parent=load(parent_path)
    actual_path=RUN/'API85-Machine-seven-read-observation-0001.json';actual=load(actual_path)
    assert actual['result']=='PASS' and actual['actual_cases']==1 and actual['failures']==actual['errors']==0
    expected={'lab.status','catalog.get','artifact.query','artifact.inspect','context.get','session.inspect','operation.inspect'}
    assert {row['operation'] for row in actual['actual_calls']}==expected and len(actual['actual_calls'])==7
    assert all(row['kind']=='result' and not row['peer_closed'] and not row['resource_closed']
               and not row['observed_after_actual_Session_expiry'] for row in actual['actual_calls'])
    selection_path=RUN/'API85-independent-selection-0001.json';selection=load(selection_path)
    assert selection['source_binding']==bind(API/'source-manifest.json')
    assert selection['profile_binding']==bind(API/'contract-profile.json')
    assert selection['original_Machine_cases']==14 and selection['original_termination_cases']==6
    rows={row['path']:row for row in parent['files']}
    for row in actual['files']:rows[row['path']]=row
    for path in [parent_path,actual_path,selection_path,
                 RUN/'qualify-API85-machine-lifecycle-full-0001.py',
                 RUN/'run-API85-machine-lifecycle-full-0001.py',Path(__file__).resolve()]:rows[bind(path)['path']]=bind(path)
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    value={**parent,'files':[rows[key] for key in sorted(rows)],'parent_progress_binding':bind(parent_path),
           'actual_Machine_repair_case_binding':bind(actual_path),'actual_Machine_repair_case_posture':'PASS',
           'actual_Machine_public_read_case_passed':True,'actual_Machine_public_read_operations':7,
           'actual_Machine_observation_job':None,'actual_Machine_full20_job':21646,
           'actual_Machine_full20_selection_binding':bind(selection_path),
           'remaining_obligations':[
               'Observe same actual API85 full20case job21646 with exact independent selection; original14Machine+6termination. Affected seven-read method passed7actual domain results with peer/Session live and unexpired. Full lifecycle remains unqualified until all20 complete and pass.',
               'Qualify private scope wrong-parent/source/resource/callback refusals without replacing clocks/grants or original generator functions.',
               *parent['remaining_obligations'][2:]],
           'change':'API85 corrected original seven-read case passed1actual case and7actual domain results: status,catalog,query,inspect,Context,Session inspection andoperationinspection. Allobserved peer/Session flags live and actualexpiryfalse; original runtime callbacks/permissions/clocks remained. Original323methods retained with only1declared opaque-context fixture binding correction. Actual original14Machine+6termination fullselection21646started and remains required.23handlers/11missing and36/46taskclosure unchanged.4learning bodies+3relations remain unadmitted/unapplied.',
           'current_Machine_qualified':False,'whole_API_qualified':False,'task_complete':False,'goal_complete':False,
           'claim_ceiling':'Actual seven-read current Machine path only. Full lifecycle, remaining originalAPI operations, signed learning continuity/application/outcomes and final owner admission remain.'}
    output=API/'receipts/R03-0125.json'
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','binding':bind(output),'bound_files':len(rows),'actual_read_operations':7,
                      'full20_job':21646,'whole_API_qualified':False}),flush=True)


if __name__=='__main__':main()
