"""Show the actual qualification boundary and preserve a resumable handoff."""
import hashlib, json
from pathlib import Path
RUN=Path(__file__).resolve().parent; ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'; API=BASE/'api-v72'
def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    progress=API/'receipts/R03-0108.json'; value=load(progress)
    current_path=sorted((RUN/'currentness-receipts').glob('*.json'))[-1]
    current=load(current_path)
    assert current['result']=='PASS' and current['completed_tasks']==36 and current['total_tasks']==46
    assert any(row['task']=='R03' and row['receipt']==bind(progress)['path'] for row in current['active_receipt_checks'])
    workflow=value['API72_focused_workflow_qualified']
    diagnostic=value['Machine_read_diagnostic_result']
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0108.md'
    text=f'''# Lab implementation and final review boundary

**36/46 tasks closed; 21/34 public handlers authored; 13 operations missing.**
R03 and R06 remain in progress. The complete plan and API remain unqualified.

## Completed work

API71's actual submission, generated preparation, exact retry and operation
inspection passed: one case, four public calls, no failures or errors. The original
schema/core, source integrity, privacy and cleanup checks completed. Two original
carrier semantic gaps and all owner/admission limitations remain explicit.
The completed report and log were recovered after its tool process handle was
unavailable; no process exit code is inferred.

API72 is a frozen component candidate for exact workflow composition. Its private
selection identifies every generated challenge member and a separately provisioned
review preference. A public caller cannot add, remove or alter a member. Separate
Decision cores and required owner roles remain separate inside one review package.
All 317 predecessor test methods are unchanged. This component freeze is not S02's
complete package freeze.

Current API72 selected workflow qualified: **{str(workflow).lower()}**.
Unchanged-source Machine read diagnostic result: **{diagnostic or 'running'}**.
Historical full-suite Machine cause established: **false**.

The selected workflow check covers actual submission, five-member preparation,
pending review, retry and inspection. The intended review retains both declared
roles for each member, all semantic/operational gaps and no owner outcome.
An authored or running check does not qualify those observations.

## Next implementation work

1. Finish the Machine diagnostic, then execute the current API72 selected workflow
   check and its refusal cases against the frozen source/profile.
2. Implement separately bound Evidence Set and Challenge Event reference resolvers.
   Artifact versions, Decisions and operational receipts retain their distinct types.
3. Qualify affected inherited selections and the outstanding Machine termination
   cases using fresh owned fixtures and real original clocks.
4. Finish the missing public handlers, actual R05 owner journeys, R06 privacy work
   and R07 acceptance measurements.
5. Compose and verify the entire exact package at S02, then present it once at R08.

## Governance result

Continue candidate implementation and isolated validation under the existing
construction authorization. No additional intermediate admission is required for
this work. Technical failures require repair and actual evidence.

The final review must include all exact targets, independent Decision cores,
required owner voices, revised examples, source cuts, validation and applicable
effects. Only a real owner response can supply its outcomes.

A01-A04 retain independently scoped admission/application and operational
acceptance requirements. Existing stores, canonical admission before R08,
activation, external effects, push and deployment remain outside this grant.

Progress receipt: `{progress.relative_to(ROOT)}`.
Currentness receipt: `{current_path.name}`.
'''
    with status.open('x') as stream:stream.write(text)
    handoff=load(RUN/'custody-integration-handoff-0092.json')
    jobs=[]
    if diagnostic is None:
        jobs.append({'session_id':37814,'command':'diagnose-API50-machine-read-0001.py',
                     'next_action':'Poll this exact tool session; do not restart the exclusive diagnostic.'})
    handoff.update(current_progress_binding=bind(progress),currentness_binding=bind(current_path),
        current_status_binding=bind(status),current_API_source_binding=value['source_binding'],
        current_API_profile_binding=value['profile_binding'],same_live_jobs=jobs,
        next_action=value['remaining_obligations'],generated_workflow_outcomes=value['generated_workflow_outcomes'])
    handoff['closed_jobs_do_not_repoll']=sorted(set(handoff['closed_jobs_do_not_repoll']+[12989,22838]))
    handoff['new_scoped_evidence']['workflow_composition_API72']='Frozen exact private composition; actual selected qualification recorded only if completed. API71 preparation has its own source-bound PASS.'
    handoff_path=RUN/'custody-integration-handoff-0093.json';emit(handoff_path,handoff)
    index=RUN/'R03-CURRENT-PROGRESS-0108.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate',
        'publisher_binding':bind(Path(__file__).resolve()),'progress_binding':bind(progress),
        'currentness_binding':bind(current_path),'status_binding':bind(status),'handoff_binding':bind(handoff_path),
        'closed_tasks':36,'total_tasks':46,'authored_handlers':21,'unimplemented_operations':13,
        'API71_preparation_selected_qualified':True,'API72_focused_workflow_qualified':workflow,
        'Machine_read_diagnostic_result':diagnostic,'whole_API_qualified':False,
        'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status)}),flush=True)
if __name__=='__main__':main()
