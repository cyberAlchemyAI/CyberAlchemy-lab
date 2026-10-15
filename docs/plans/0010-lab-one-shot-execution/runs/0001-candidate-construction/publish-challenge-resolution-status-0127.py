"""Publish current scoped result and an explicit full-plan continuation."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v86'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')


def main():
    progress=API/'receipts/R03-0127.json';p=load(progress)
    current=sorted((RUN/'currentness-receipts').glob('*.json'))[-1];c=load(current)
    assert c['result']=='PASS' and c['completed_tasks']==36 and c['total_tasks']==46
    assert any(row['task']=='R03' and row['receipt']==progress.relative_to(ROOT).as_posix() for row in c['active_receipt_checks'])
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0127.md'
    text='''# Lab candidate progress and next work

**36 of 46 tasks closed. 24 of 34 public handlers authored; 10 remain.**
R03 and R06 remain in progress. The complete API and Lab remain unqualified.

## Work completed in this increment

API86 adds `challenge.resolve` consequence preparation. Its private policy
selects an independent signed gate and exact original source records. It checks
Challenge Contract response mode, time window, evidence kinds and declared
routes. Semantic and governance proposals retain separate bindings. The
composed result preserves complete targets, connections, schemas and evidence.
Effects, target versions and Decision Scopes are checked as distinct types.
A proposed successor preserves the exact challenged predecessor and never
overwrites the existing version. Original proposal bytes reach validation.

Fifteen actual isolated component cases and seven bounded source/schema/control
cases passed. The first control run had one inherited Product fixture failure:
expected episode0003 versus actual signed/mapped episode0004. That failure is
preserved. The second run used one explicit external fixture input correction,
retaining all assertions and frozen source. A future successor must carry that
correction into its inherited fixture.

All323 inherited methods remain;320ASTs are unchanged. Three exact supported
handler count expectations changed23to24. Source, clock, Machine transport,
guarded reads/candidate writer and vault predecessors remain preserved.

## Validation still required

The component cases use isolated fixture inputs. They do not qualify an actual
public resolution or current owner recognition. Build a freshly owned signed
source containing exact Principal/key recognition, Challenge, Contract,
Decision, Effects, Decision Scopes and evidence. Then exercise the real channel,
native candidate validator, journal, retries, failures, deadlines and source
changes. No old disposed signer may be restored or old period extended.

The same API85 full20Machine/termination job21646 continues. Its seven-read
proof remains evidence for API85 only. No predecessor runtime qualification is
transferred to API86. Preserve the actual real expiry case and terminal result.

The earlier four learning bodies and three declared relations remain candidates.
Add explicit applicability and mapping closure in a fresh source, consume them
through a new actual Agent Context, perform a later controlled lesson application
and record its outcome. Prior repair is counterevidence, not proof of application.

## Remaining implementation and final review

'''
    text+='Missing original operations: '+', '.join('`'+name+'`' for name in p['remaining_unimplemented_operations'])+'.\n\n'
    text+='''Complete R03 public selections, R05 journeys, R06 privacy, R07 acceptance
and S02 exact whole-package review readiness before the sole actual R08 owner
response. A01-A04 retain their separately represented application scopes.

Existing candidate construction and isolated validation authorization continues.
Canonical admission before R08, existing/live stores, activation, external/tool
effects and publication remain excluded. This increment creates no intermediate
owner admission decision and does not complete the goal.
'''
    with status.open('x') as stream:stream.write(text)
    parent=RUN/'custody-integration-handoff-0107.json';handoff=RUN/'custody-integration-handoff-0108.json'
    value={'schema_version':'lab-full-plan-continuation/v2-candidate','parent_handoff_binding':bind(parent),
        'current_progress_binding':bind(progress),'current_status_binding':bind(status),'currentness_binding':bind(current),
        'current_API_source_binding':p['source_binding'],'current_API_profile_binding':p['profile_binding'],
        'execution_authorization_binding':bind(RUN/'authorization.json'),
        'same_live_jobs':p['same_predecessor_live_jobs'],
        'closed_jobs_do_not_repoll':sorted(set(load(parent)['closed_jobs_do_not_repoll']+[53934,70200,51047,36392,14499,29848])),
        'authored_handlers':24,'original_handlers':34,'closed_tasks':36,'original_tasks':46,
        'remaining_unimplemented_operations':p['remaining_unimplemented_operations'],
        'next_action':p['remaining_obligations'],
        'component_qualification_binding':p['isolated_resolution_contract_qualification_binding'],
        'control_qualification_binding':p['source_control_qualification_binding'],
        'new_public_resolution_qualified':False,'current_Machine_qualified':False,'whole_API_qualified':False,
        'task_complete':False,'goal_complete':False,'authority_effect':'none','actual_owner_outcome':None}
    emit(handoff,value)
    index=RUN/'R03-CURRENT-PROGRESS-0127.json'
    emit(index,{**{key:value[key] for key in ('authored_handlers','original_handlers','closed_tasks','original_tasks',
        'same_live_jobs','remaining_unimplemented_operations','current_Machine_qualified','whole_API_qualified','goal_complete','authority_effect')},
        'schema_version':'lab-current-progress-index/v2-candidate','publisher_binding':bind(Path(__file__).resolve()),
        'progress_binding':bind(progress),'currentness_binding':bind(current),'status_binding':bind(status),'handoff_binding':bind(handoff)})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),'handoff':bind(handoff)}),flush=True)


if __name__=='__main__':main()
