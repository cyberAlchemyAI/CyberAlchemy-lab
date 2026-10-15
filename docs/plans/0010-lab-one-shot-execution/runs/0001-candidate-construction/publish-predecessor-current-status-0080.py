"""Publish a new status and handoff only after exact scoped proof synchronization."""
import hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 progress=BASE/'api-v45/receipts/R03-0080.json';v=load(progress)
 assert v['result']=='PASS' and v['pure_typed_wire_full_cases']==128 and not v['task_complete']
 current=RUN/'currentness-receipts/0145.json';c=load(current)
 assert c['result']=='PASS' and c['completed_tasks']==36 and c['total_tasks']==46
 assert any(x['task']=='R03' and x['receipt']==progress.relative_to(ROOT).as_posix() for x in c['active_receipt_checks'])
 obs=load(ROOT/v['current_public_suite_observation_binding']['path'])
 signed=load(RUN/'typed-actual-source-comparison-0009.json')
 assert signed['actual_public_predecessor_binding']['result']=='PASS'
 assert signed['actual_preimage_candidate_postimage']['reason']=='target outside authorized scope'
 status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0080.md'
 text=f'''# Lab operational foundation: candidate progress

Candidate construction continues under the existing authorization. R08 remains
this package's sole admission decision, after complete S02. R08 has no outcome
for this package.

## Current state

| Item | State |
| --- | --- |
| Candidate tasks | 36 of 46 closed; R03 and R06 in progress |
| Public contracts | 34 declared; 16 handlers authored |
| Operation qualifications | 13 historical scoped qualifications; 21 original qualifications remain |
| Typed extension | Frozen v10 passes all128 pure checks |
| Signed replay | Complete catalog and all4 public predecessor bindings pass; original runtime refuses semantic scope mismatch |
| Current runtime | Frozen API45 original failure18 continues on36293; snapshot: {obs['printed_method_PASS_count']} PASS, {obs['printed_method_FAIL_count']} FAIL, {obs['printed_method_ERROR_count']} ERROR |
| Owner decision | R08 pending complete S02 |

## What changed

The public predecessor adapter verifies the independently selected representation
profile, exact original source bytes and selectors, schema binding, identity,
carrier and five-axis public header. It retains the original physical metadata
and runtime predecessor version separately. All114 original foundation cases,
12 representation cases and2 historical meta carrier cases pass on frozen v10.

A current catalog declaration may have a public read representation under the
historical Artifact Type/v2 meta carrier. Its historical lifecycle stays separate
from the current declaration and supplies no new admission. Proposed successor
registrations remain checked by the unchanged original custody engine.

The exact signed replay passes all4 predecessor bindings and the original reader
exit/freshness guards. It still matches121 current carriers,41 Relation Kinds,
390 catalog material bindings and281 predecessor/Definition references. Distinct
capture envelopes,19 noncatalog material differences and71 additional runtime
materials do not establish executable equivalence.

The original runtime now refuses `target outside authorized scope` after the
representation adapter passes. Its Project scope remains
`project:cyberalchemy-v2-to-lab-migration`; the original Relation Kind body retains
`scope:integrated-lab-relation-model`. A separately declared complete typed scope
preparation profile remains required. The owner-instance scope preparation profile
covers different categories and coupled groups and supplies no typed scope grant.

## Verification and retained failures

Frozen v9 completed all126 cases with4 failures and2 errors because it incorrectly
required the declared historical meta carrier to be current. Those receipts and
the failed signed replay diagnostic are preserved. V10 retains all126 predecessor
method ASTs and adds2 explicit historical representation cases; all128 pass.
Earlier authoring failures remain recorded as development evidence.

API45 original case12 printed FAIL: expected `conflict`, actual `indeterminate`.
The exact saved journal records a failed outcome; its public reply reports deadline
expiry after claim/evidence. Case13 exact failure retry subsequently passed.
The cause of excessive duration is not established. The same18-case invocation
continues. Real clocks, actual policy reads and the original900-second limit stay
unchanged. A full API or deadline qualification is not claimed.

The separate API45 strict control successor remains frozen and unrun. All293
original API methods and34 original contract schemas remain unchanged. Historical
API44 scoped controls/termination evidence and explicitly interrupted predecessor
jobs remain separate from current source qualification.

## Next work and the final decision

1. Complete the same API45 suite, measure and repair the deadline failure, then
   qualify the complete successor suites and every original refusal/cleanup case.
2. Declare exact coupled typed semantic scope preparation and integrate the actual
   authenticated current source, Actor, permission and durable journal/retry/recovery.
3. Complete governed internal/specialized authority resolvers and all21 outstanding
   original operation qualifications.
4. Obtain genuine R05 participant evidence and finish R06, R07 and complete S02.
5. Present the complete exact package and validation evidence for the actual R08
   owner decision. Subsequent effects require their applicable scoped authority.

The plan remains active. Currentness145 passed after R03-0080 synchronization:
38 active receipt checks,77 preparation files and887 baseline sources, with no
changes. R03-0080 binds {len(v['files']):,} files and retains incomplete task criteria.
No actual public typed operation, canonical admission, owner outcome, activation,
deployment or complete plan is established by these scoped results.
'''
 with status.open('x') as f:f.write(text)
 parent=RUN/'custody-integration-handoff-0067.json';h=load(parent)
 h['parent_handoff_binding']=bind(parent);h['progress_receipt_binding']=bind(progress)
 h['currentness_binding']=bind(current);h['status_binding']=bind(status)
 h['currentness_process']={'state':'terminal-PASS','actual_exit_code':0,'receipt_binding':bind(current),'terminal_binding':bind(RUN/'R03-0080-currentness-terminal-0001.json')}
 h['typed_frozen_source_binding']=bind(BASE/'typed-extension-preparation-v10/source-manifest.json')
 h['typed_source_selection_proof_binding']=bind(BASE/'typed-extension-preparation-v10/receipts/proof-0001.json')
 h['closed_jobs_do_not_repoll']=sorted(set(h['closed_jobs_do_not_repoll']+[26171,11510,17738,35627,39134,44303,63239,64275,69200,73967,66048,6282,66752,94846,80580,56307,80408,55773,25905,10652,66287,45006]))
 h['same_live_jobs'][0].update(printed_PASS_cases_at_latest_observation=obs['printed_method_PASS_count'],printed_FAIL_cases_at_latest_observation=obs['printed_method_FAIL_count'],printed_ERROR_cases_at_latest_observation=obs['printed_method_ERROR_count'],last_live_chunk_id='5baa36',log_snapshot_binding=obs['log_snapshot_binding'],last_observation_binding=v['current_public_suite_observation_binding'])
 h['new_scoped_evidence'].pop('typed_full98',None)
 h['new_scoped_evidence'].update(typed_full128='PASS: complete frozen v10 pure suite; all126 predecessor methods retained, including corrected historical meta representation and2 new historical cases.',actual_catalog_binding='PASS: separately pinned signed replay,390 exact materials,281 predecessor/Definition refs,121 carriers and41 Relation Kinds; executable envelopes remain distinct.',actual_public_predecessor_binding='PASS: all4 exact public headers bind separately to original physical metadata, including historical meta carrier; source reader exit guards complete.',actual_scope_refusal='Original unchanged runtime refuses target outside authorized scope; semantic body and Project transaction scopes retained.',current_public_failure18='Same36293 invocation remains incomplete; case12 deadline FAIL, case13 exact retry PASS.')
 h['next_action']=['Continue SAME36293 invocation; preserve full actual terminal and complete18 report; case12 already printed FAIL.','Measure actual deadline phases and repair within the original900-second bound, real clocks and source/policy guards; do not infer timing cause.','Declare exact whole coupled typed semantic scope preparation without using owner-instance scope grants or rewriting original body/config scope.','Integrate typed-v10 with actual authenticated current source, Actor, permission and durable public journal/retry/recovery; no public typed handler is qualified.','Complete all original qualifications and governed internal/specialized resolvers, genuine R05/R06/R07/S02, then sole actual R08 owner decision.']
 h['terminal_bindings'].extend([bind(RUN/name) for name in ['typed-extension-wire128-terminal-0001.json','typed-extension-wire126-terminal-0001.json','typed-actual-source-comparison-terminal-0009.json','typed-actual-source-comparison-terminal-0008.json','typed-public-predecessor-authoring-terminal-0001.json','typed-public-predecessor-authoring-terminal-0002.json']])
 handoff=RUN/'custody-integration-handoff-0068.json';put(handoff,h)
 index=RUN/'R03-CURRENT-PROGRESS-0080.json';put(index,{'schema_version':'lab-current-progress-index/v1-candidate','publisher_binding':bind(Path(__file__).resolve()),'progress_binding':bind(progress),'currentness_binding':bind(current),'status_binding':bind(status),'handoff_binding':bind(handoff),'closed_tasks':36,'total_tasks':46,'authority_effect':'none','task_complete':False,'goal_complete':False})
 print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),'handoff':bind(handoff),'authority_effect':'none','goal_complete':False}),flush=True)
if __name__=='__main__':main()
