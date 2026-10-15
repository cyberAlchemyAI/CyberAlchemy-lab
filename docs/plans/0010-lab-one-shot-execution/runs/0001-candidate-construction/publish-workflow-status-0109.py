"""Show the actual qualification boundary and preserve a resumable handoff."""
import hashlib, json
from pathlib import Path
RUN=Path(__file__).resolve().parent; ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'; API=BASE/'api-v74'
def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    progress=API/'receipts/R03-0109.json'; value=load(progress)
    current_path=sorted((RUN/'currentness-receipts').glob('*.json'))[-1]
    current=load(current_path)
    assert current['result']=='PASS' and current['completed_tasks']==36 and current['total_tasks']==46
    assert any(row['task']=='R03' and row['receipt']==bind(progress)['path'] for row in current['active_receipt_checks'])
    workflow=value['API74_focused_workflow_qualified']
    diagnostic=value['Machine_read_diagnostic_result']
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0109.md'
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

The unchanged API50 diagnostic expired during proof creation before any Machine
reply. It does not establish the historical full-suite cause or current Machine
behavior. Current Service.reply already handles a cleared context. API72 and API73
refused fixture defects; API74 preserves production guards and corrects those
inputs. A separate measured API72 full source check took 3.481 seconds over its
1,563,089,321 selected bytes; this is not attribution of the Machine expiry.

API74 is a frozen component candidate for exact workflow composition. Its private
selection identifies every generated challenge member and a separately provisioned
review preference. A public caller cannot add, remove or alter a member. Separate
Decision cores and required owner roles remain separate inside one review package.
All 320 predecessor test methods are unchanged. This component freeze is not S02's
complete package freeze.

Current API74 selected workflow qualified: **{str(workflow).lower()}**.
Unchanged-source Machine read diagnostic result: **{diagnostic or 'running'}**.
Historical full-suite Machine cause established: **false**.

The selected actual workflow passed one case and five public calls: submission,
five-member preparation, pending review, retry and inspection. It retained ten
required role responses and all four semantic/owner gaps. This qualifies that
selected sequence; the full refusal cases and current Machine read selection
are running sequentially under the same exact source/profile.

## Next implementation work

1. Complete the current API74 full three-case workflow suite and unchanged current
   Machine read selection using the exact live follow-on handle.
2. Implement separately bound Evidence Set, Challenge Event and User Decision
   Preference reference resolvers. Preserve the fourth gap for actual owner outcomes.
   Artifact versions, Decisions and operational receipts retain distinct types.
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
    handoff=load(RUN/'custody-integration-handoff-0093.json')
    jobs=[]
    jobs.append({'session_id':72154,'command':'run-API74-after-focused-0001.py',
                 'next_action':'Poll this exact follow-on driver; full workflow then unchanged current-source Machine read. Do not restart exclusive outputs.'})
    handoff.update(current_progress_binding=bind(progress),currentness_binding=bind(current_path),
        current_status_binding=bind(status),current_API_source_binding=value['source_binding'],
        current_API_profile_binding=value['profile_binding'],same_live_jobs=jobs,
        next_action=value['remaining_obligations'],generated_workflow_outcomes=value['generated_workflow_outcomes'])
    handoff['closed_jobs_do_not_repoll']=sorted(set(handoff['closed_jobs_do_not_repoll']+[12989,22838,37814,58905,64858,13011,58168,85337,97774]))
    handoff['new_scoped_evidence']['workflow_composition_API74']='Actual focused workflow PASS: one case, five calls, five member cores, ten required role responses and four retained gaps. Full current workflow and Machine read remain pending.'
    handoff_path=RUN/'custody-integration-handoff-0094.json';emit(handoff_path,handoff)
    index=RUN/'R03-CURRENT-PROGRESS-0109.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate',
        'publisher_binding':bind(Path(__file__).resolve()),'carrier_resolver_design_successor_binding':bind(RUN/'GENERATED-CARRIER-RESOLVER-DESIGN-0002.md'),'progress_binding':bind(progress),
        'currentness_binding':bind(current_path),'status_binding':bind(status),'handoff_binding':bind(handoff_path),
        'closed_tasks':36,'total_tasks':46,'authored_handlers':21,'unimplemented_operations':13,
        'API71_preparation_selected_qualified':True,'API74_focused_workflow_qualified':workflow,
        'Machine_read_diagnostic_result':diagnostic,'whole_API_qualified':False,
        'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status)}),flush=True)
if __name__=='__main__':main()
