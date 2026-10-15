"""Publish synchronized scoped progress, retained failures and actual remaining gates."""
import hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 progress=BASE/'api-v47/receipts/R03-0083.json';v=load(progress)
 assert v['result']=='PASS' and v['pure_typed_wire_full_cases']==144 and not v['task_complete']
 current=RUN/'currentness-receipts/0148.json';c=load(current)
 assert c['result']=='PASS' and c['completed_tasks']==36 and c['total_tasks']==46
 assert any(r['task']=='R03' and r['receipt']==progress.relative_to(ROOT).as_posix() for r in c['active_receipt_checks'])
 assert load(RUN/'R03-0083-currentness-terminal-0001.json')['actual_exit_code']==0
 status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0083.md'
 text=f'''# Lab operational foundation: candidate progress

The existing candidate development authorization covers continued implementation
and verification. The sole owner admission decision remains R08, after complete
S02. This package has no R08 outcome.

## Current state

| Item | State |
| --- | --- |
| Candidate tasks | 36 of46 closed; R03 and R06 in progress |
| Public contracts | 34 declared;16 handlers authored |
| Operation qualifications | 13 historical scoped qualifications;21 original qualifications remain |
| Typed extension | Frozen v11:144 PASS,0 failures,0 errors |
| Exact signed-source diagnostic | Complete catalog,4 public predecessors and hypothetical coupled postimage PASS |
| Actual transaction scope | Original refusal preserved; hypothetical configuration unprovisioned |
| API45 full failure suite |18 cases:16 PASS,2 FAIL,0 ERROR; actual exit1 |
| API45 owned cleanup | All18 registered fixture cleanup paths completed |
| API46 | Original cases14/15 running; result not yet established |
| API47 | Known-outcome read scope frozen; full original failure18 serialized after API46 |
| Typed host routing | Closed internal route/design frozen;8 offline shape checks PASS |
| Additional scope refusal | Original effect-authority refusal remains a refusal;1 pure check PASS |
| Deadline measurement | Diagnostic completed and reproduces failure; normal deadline qualification outstanding |
| Owner decision | R08 pending complete S02 |

## Typed host composition

A frozen closed internal routing schema binds exact proposal/inspection, helper
source/proof, catalog profile/review/capture, representation profile, canonical
authority, complete schema destinations and optional exact scope hypothesis.
Eight offline shape checks pass. They use explicit shape-only fixtures; semantic
path/inventory checks and actual signed policy/host integration remain open.

The ordered composition keeps independently authenticated Actor/current cut,
complete catalog and prospective successor impact, original source/schema/core
checks, scoped candidate writes and durable journal/retry/recovery separate from
owner review and admission. The public request/result contracts remain unchanged.
No additional public handler is registered by this routing package.

A separate pure original-engine probe confirms that `effect outside provisioned
authority` cannot be reinterpreted as a scope hypothesis. Actual inputs stay
unchanged. This is additional refusal evidence, separate from the144-case suite.

The unchanged original API46 cases14 and15 are selected before owned fixtures.
One driver waits for the same verified CPU diagnostic to terminate before running
them. It stops if that process disappears without a terminal record; it never
restarts the diagnostic on an observation timeout. Their result is not established
by this progress record.

## Scope preparation

V11 retains every original128 test method and adds16 exact scope preparation
cases. Its closed profile binds the complete ordered coupled target group,
Decision cores, schemas, inspection/impact and independently selected catalog,
representation and runtime source pins. The selected signed replay verifies121
current carriers,41 Relation Kinds,390 catalog materials and4 public predecessors.

The runtime's actual scope stays `project:cyberalchemy-v2-to-lab-migration`; the
Relation Kind body retains `scope:integrated-lab-relation-model`. The original
engine refuses `target outside authorized scope`. The diagnostic separately pins
a synthetic candidate profile and checks the complete original-engine postimage
against copied hypothetical scope configuration. It preserves actual inputs,
source reader exit/freshness guards and the original refusal. Operational
preparation remains false. No genuine semantic review or operational grant is
supplied by this diagnostic.

## Deadline measurement observation

The original case12 CPU diagnostic completed with its original failure retained:
1 test,1 assertion failure,0 errors;1776.967 seconds elapsed. The measurement
records375,445 original byte reads,42 producer preflight calls and274 source
verification calls across setup/call/cleanup. These cumulative timings overlap
and profiling affects them; they do not qualify normal delivery or establish a
single causal phase. The original API46 cases14/15 have started sequentially
after this diagnostic. Their outcome is not established in this progress record.

## Retained runtime failures and candidate repair

API45 case12 delivers `indeterminate` after the real deadline where the original
test expects `conflict`. The saved journal records a failed outcome. Repeated source-verification costs were measured; normal deadline causality and
successor behavior remain unqualified. The real900-second bound, clocks and actual
source/policy reads remain unchanged.

Case15 rejects invalid schema but loses its required failed validation report.
Its generic exception discards the staged evidence buffer. API46 selects new
Failure Preparation/v5 and Classification Preparation/v7 compositions: when
failed validation has every exact stable core verified, the existing known-rule
exception allows original exit guards to complete before the failed report
commits. Incomplete cores retain the original uncertain/pending path.

All293 original API test methods and34 public contract schemas remain unchanged.
The only API source changes select the two new compositions. The static check
proves each preparation AST changes only by that conditional branch; all other
source/policy/journal/clock predicates remain. API46 is not runtime qualified.
All18 API45 owned fixture cleanup paths completed despite2 retained assertions;
that cleanup result does not make the failed suite pass.

## Measured successor and full verification

API47 retains the API46 validation-report fix and adds existing read-scope
composition around both known-rule-failure pure predicate sequences. Static
comparison verifies the original predicates by flattening that added scope:
every other original Service AST, all293 test methods and34 public schemas stay
unchanged. Actual permission reads, real clocks and the900-second bound remain;
durable journal completion and reply delivery stay outside the pure scope.
The candidate's normal deadline behavior and full runtime remain unqualified.

The same API46 core/schema job37740 continues with its original two cases. A
separate serialized driver21283 waits for its actual terminal and completed
source/cleanup guards before running the complete unchanged18-case API47 failure
suite. It preserves either predecessor assertion result and never replaces a
missing job merely because observation timed out. No full successor PASS is
established by this progress record.

## Completion route and decision

1. Complete the same API46 core/schema job and preserve its actual result. Then
   run the serialized complete API47 original failure18 and verify actual deadline
   delivery within the unchanged bound and original guards.
2. Complete every other full current successor suite and original source,
   permission, refusal, uncertainty/retry/recovery and cleanup criterion.
3. Integrate the typed operation with authenticated current source, Actor,
   independently scoped permission and durable journal/retry/recovery. Replace
   synthetic diagnostic targets with genuinely reviewed complete model changes.
4. Complete governed authority resolvers and all21 remaining original qualifications.
5. Obtain genuine R05 participant evidence, finish R06/R07 and freeze complete S02.
6. Present the exact package and validation evidence for the sole R08 admission
   decision. Subsequent operational effects require their applicable authority.

No additional owner admission checkpoint is introduced during candidate work.
Genuine participant evidence and scoped operational authority cannot be replaced
by fixture outcomes. The plan remains active and incomplete.

Currentness148 passed: {len(c['active_receipt_checks'])} active receipt checks,
{c['original_preparation_files']} preserved preparation files and
{c['original_bound_sources']} baseline sources, with no changes. R03-0083 binds
{len(v['files']):,} files and retains incomplete task criteria.
'''
 with status.open('x') as f:f.write(text)
 parent=RUN/'custody-integration-handoff-0070.json';h=load(parent)
 h.update(parent_handoff_binding=bind(parent),progress_receipt_binding=bind(progress),currentness_binding=bind(current),status_binding=bind(status))
 h['currentness_process']={'state':'terminal-PASS','actual_exit_code':0,'receipt_binding':bind(current),'terminal_binding':bind(RUN/'R03-0083-currentness-terminal-0001.json')}
 h['typed_frozen_source_binding']=bind(BASE/'typed-extension-preparation-v11/source-manifest.json')
 h['typed_source_selection_proof_binding']=bind(BASE/'typed-extension-preparation-v11/receipts/proof-0001.json')
 h['current_API_source_binding']=bind(BASE/'api-v47/source-manifest.json')
 h['current_API_profile_binding']=bind(BASE/'api-v47/contract-profile.json')
 h['closed_jobs_do_not_repoll']=sorted(set(h['closed_jobs_do_not_repoll']+[36293,65988,65603,24861,77557,12588,43746,53686,97204,40442,1993,50677,17921,43273,76878,95707,51392,21437]))
 diagnostic_terminal=RUN/'API45-failure12-cpu-measurement-terminal-0001.json'
 if diagnostic_terminal.exists():
  h['same_live_jobs']=[];h['closed_jobs_do_not_repoll']=sorted(set(h['closed_jobs_do_not_repoll']+[43273]));h['deadline_diagnostic_terminal_binding']=bind(diagnostic_terminal)
 else:
  h['same_live_jobs']=[{'session_id':43273,'initial_chunk_id':'bdc601','last_live_chunk_id':'07a25b','state':'last-observed-running','suite':'API45 unchanged original case12 CPU diagnostic','source_binding':bind(BASE/'api-v45/source-manifest.json'),'profile_binding':bind(BASE/'api-v45/contract-profile.json'),'runner_binding':bind(RUN/'profile-API45-failure12-0001.py'),'log_path':(RUN/'API45-failure12-cpu-measurement-0001.log').relative_to(ROOT).as_posix(),'report_path':(RUN/'API45-failure12-cpu-measurement-0001.json').relative_to(ROOT).as_posix(),'terminal_path':diagnostic_terminal.relative_to(ROOT).as_posix(),'full_suite_verdict':None,'normal_runtime_qualified':False}]
 focused_terminal=RUN/'API46-core-schema-focused-terminal-0001.json'
 if focused_terminal.exists():
  h['closed_jobs_do_not_repoll']=sorted(set(h['closed_jobs_do_not_repoll']+[37740]))
  h['focused_original_case_terminal_observation_binding']=bind(focused_terminal)
 else:
  h['same_live_jobs'].append({'session_id':37740,'initial_chunk_id':'be1b45','last_live_chunk_id':'b7f6ec','state':'last-observed-running-serialized-driver','suite':'API46 unchanged original core/schema cases14/15 after same43273 diagnostic','source_binding':bind(BASE/'api-v46/source-manifest.json'),'profile_binding':bind(BASE/'api-v46/contract-profile.json'),'runner_binding':bind(RUN/'verify-API46-core-schema-original-cases-0001.py'),'driver_binding':bind(RUN/'run-API46-core-schema-after-diagnostic-0001.py'),'selection_binding':bind(RUN/'API46-core-schema-selection-0001.json'),'log_path':(RUN/'API46-core-schema-focused-0001.log').relative_to(ROOT).as_posix(),'terminal_path':focused_terminal.relative_to(ROOT).as_posix(),'whole_API_qualified':False})
 full_terminal=RUN/'API47-failure18-terminal-0001.json'
 if full_terminal.exists():
  h['closed_jobs_do_not_repoll']=sorted(set(h['closed_jobs_do_not_repoll']+[21283]))
  h['full_API47_failure_terminal_observation_binding']=bind(full_terminal)
 else:
  h['same_live_jobs'].append({'session_id':21283,'initial_chunk_id':'19e08f','last_live_chunk_id':'0f399c','state':'last-observed-running-serialized-driver','suite':'Complete original API47 failure18 after same37740 predecessor','source_binding':bind(BASE/'api-v47/source-manifest.json'),'profile_binding':bind(BASE/'api-v47/contract-profile.json'),'driver_binding':bind(RUN/'run-API47-full-failure-after-core-schema-0001.py'),'log_path':(RUN/'current-API47-failure18-0001.log').relative_to(ROOT).as_posix(),'terminal_path':full_terminal.relative_to(ROOT).as_posix(),'whole_API_qualified':False})
 h['deadline_diagnostic_measurement_binding']=bind(RUN/'API45-failure12-cpu-measurement-0001.json')
 h['deadline_source_cost_finding_binding']=bind(RUN/'API45-known-outcome-source-cost-finding-0001.json')
 h['new_scoped_evidence'].update(API47_known_outcome='FROZEN: original predicate ASTs,293 methods/34 schemas retained; existing pure read composition added before original durable finish/delivery. Normal runtime qualification outstanding.')
 h['new_scoped_evidence'].update(typed_routing_shape='PASS8: frozen closed internal route and ordered design only; no public handler or grant.',additional_original_scope_refusal='PASS1: actual original effect-authority error remains a refusal on hypothetical copies; no scope hypothesis returned.')
 h['new_scoped_evidence'].update(typed_full144='PASS: frozen v11 retains128 predecessor methods and adds16 exact coupled scope profile cases.',actual_scope_hypothesis='PASS over actual signed preimage; synthetic targets, actual scope refusal retained, hypothetical unprovisioned configuration, no operational readiness or grant.',current_public_failure18='TERMINAL FAIL: API45 original18,16 PASS2 FAIL0 ERROR, actual exit1. Cases12/15 fail; all18 registered owned fixture cleanup paths completed.',known_validation_retention='API46 frozen with conditional known structural refusal evidence retention after complete exact cores. All293 inherited methods/34 contracts retained; runtime verification outstanding.')
 h['next_action']=['43273 diagnostic TERMINAL MEASURED, original test FAIL, actual exit0; do not repoll. Its costs overlap and profiling does not qualify normal deadline delivery.','Continue SAME37740 serial driver if live. It waits for43273 terminal before unchanged original API46 cases14/15; bind actual result/terminal and preserve original clocks and bodies.','Continue SAME21283 serial driver if live; after37740 terminal it runs the complete original API47 failure18. Preserve actual terminal/18-case result and qualify actual delivery under unchanged900-second bound and all original guards.','Integrate frozen typed host routing with a declared successor signed policy, full typed-v11/current-source/Actor checks, independently scoped candidate permission and public journal/retry/recovery; synthetic diagnostic profile grants no authority.','Complete every remaining original qualification, governed authority resolvers, genuine R05/R06/R07/S02 and sole actual R08 owner decision.']
 h['terminal_bindings'].extend(bind(RUN/name) for name in ['typed-extension-v11-freeze-terminal-0001.json','typed-extension-wire144-terminal-0001.json','typed-actual-source-comparison-terminal-0010.json','API45-failure18-terminal-0001.json','API46-freeze-terminal-0001.json','R03-0083-evidence-builder-terminal-0001.json','R03-0083-record-progress-terminal-0001.json','R03-0083-currentness-terminal-0001.json','typed-scope-other-backend-refusal-terminal-0001.json','typed-host-routing-shape-terminal-0001.json','API45-failure12-cpu-measurement-terminal-0001.json','API47-freeze-terminal-0001.json'])
 handoff=RUN/'custody-integration-handoff-0071.json';put(handoff,h)
 index=RUN/'R03-CURRENT-PROGRESS-0083.json';put(index,{'schema_version':'lab-current-progress-index/v1-candidate','publisher_binding':bind(Path(__file__).resolve()),'progress_binding':bind(progress),'currentness_binding':bind(current),'status_binding':bind(status),'handoff_binding':bind(handoff),'closed_tasks':36,'total_tasks':46,'authority_effect':'none','task_complete':False,'goal_complete':False})
 print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),'handoff':bind(handoff),'authority_effect':'none','goal_complete':False}),flush=True)
if __name__=='__main__':main()
