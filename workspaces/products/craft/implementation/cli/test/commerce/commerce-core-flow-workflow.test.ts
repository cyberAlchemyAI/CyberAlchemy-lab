/** Source-level Workflow qualification. No provider or live owner is created.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
import {auditCoreCommerceWorkflowSources,checkCoreCommerceWorkflowSources,checkCoreCommerceWorkflowProposal,type CoreWorkflowStep} from '../../src/commerce/commerce-core-flow-workflow.js';
const entry=(entry:string,target:string,event=false)=>`entry Demo.${entry}:
  invokes Demo.${target}
  interaction ${event?'event':'request-response'}
  access:
    authenticated service
    permission demo.${entry}
    auth-resource demo
    auth-action ${entry}
    auth-scope test
    auth-route test:Demo.${entry}
    caller demo
    context Worker
    native-requires craft.context.current-owner/v1-candidate
    current-action before replay-and-effects
${event?'    producer demo\n':''}`;
const declarations=`module Demo version 1
value-object Id:
  carrier String
  representation transparent-scalar
  utf8-bytes 1..16
enum Status:
  value Start
  value Done
  value NeedsReview
enum Observation:
  variant Recorded value UInt64
enum Result:
  variant Done value UInt64
  variant Pending key Id
  variant Other value Bool
entity Progress:
  id Id
  state Status
  workerOwner optional<Id>
  workerEpoch UInt64
  version UInt64
  identity id
  immutable id
value-object Snapshot:
  progress Progress
value-object Commit:
  fresh Bool
event Started:
  version 1
  id Id
interface Worker:
  kind trusted-context
  abi craft.test-worker/v1-candidate
  custody private-registered-local-worker-owner
  fields context.json#/worker/properties
  serializable false
  public-constructor forbidden
interface Identity:
  kind native-producer
  abi craft.test-identities/v1-candidate
  custody private-registered-source-profile-callsite
  signatures context.json#/identity_producers/methods
query ReadSnapshot:
  input id Id
  source row Progress
  output Snapshot
  where row.id == id
  project Snapshot(progress=row)
  on-missing fail missing
operation Claim:
  input id Id
  input expectedVersion UInt64
  context worker Worker
  output Progress
  read row Progress by id=id
    on-missing fail missing
  transaction ClaimWork:
    atomic-participants Progress
    update claimed Progress by id=id expected-version expectedVersion:
      workerOwner <- some(worker.workerId)
      workerEpoch <- row.workerEpoch + 1
      version <- row.version + 1
  return claimed
operation Observe:
  input id Id
  input expectedVersion UInt64
  input observation Observation
  output Commit
  read row Progress by id=id
    on-missing fail missing
  transaction Record:
    atomic-participants Progress
    update recorded Progress by id=id expected-version expectedVersion:
      state <- Status.Done
      version <- row.version + 1
  return Commit(fresh=true)
query Inspect:
  input id Id
  input observation Observation
  source row Progress
  output Result
  where row.id == id
  project Result.Pending(id)
operation Run:
  input value UInt64
  output Result
  return Result.Done(value)
interface Internal:
  kind internal
  exposes ReadSnapshot, Claim, Observe, Inspect, Run
interface Application:
  kind application-composition
  service demo module Demo
  formal-claims optional
`;
const workflow=`workflow Flow:
  owner demo
  scope cross-service
  input event Started
  context worker Worker
  context identities Identity
  correlation event.id
  input-entry Demo.StartEntry
  input-producer demo
  input-inbox identity logicalEntryId, event.id compare identities.fingerprint(event)
  durable-state Progress
  ownership compare-and-set workerOwner, workerEpoch, version
  recovery no-lease-steal; native quiescent-predecessor evidence required
  input-ack after inbox-and-work-schedule commit
  snapshot-operation Demo.ReadEntry
    input id <- event.id
    result snapshot Snapshot
    require snapshot.progress.id == event.id
    immutable-inputs snapshot.progress.id
    before-each-step reread current order/progress versions and ownership
    on-missing fail missing
    on-unavailable suspend same-state
  claim-operation Demo.ClaimEntry
    input id <- snapshot.progress.id
    input expectedVersion <- snapshot.progress.version
    result claim Progress
    bind-native-claim worker to committed claim before dispatch
    on-contention stop-this-worker
    on-unknown suspend ownership-unresolved
  observation-operation Demo.ObserveEntry
    input id <- snapshot.progress.id
    input expectedVersion <- snapshot.progress.version
    input observation <- step.observation
    result observed Commit
    after-observation reread snapshot; then-target requires observed.fresh and matching current state, otherwise resume
    on-contention reread snapshot then reapply original observation; never repeat remote call
    on-unknown invokes Demo.InspectEntry(id=snapshot.progress.id,observation=step.observation); no fresh continuation ticket or rollback inference
    on-evidence-conflict persist EvidenceConflict using original step command
  resume:
    Start -> run
    Done -> finish done
    NeedsReview -> suspend needs-review
  step run:
    invokes Demo.RunEntry
    input value <- 0
    result result Result
    on Done(value) observe Observation.Recorded(value) then finish done
    on Pending(key) suspend Start retaining original command
    on-call-failure suspend Start
  step inspect:
    invokes Demo.InspectEntry
    input id <- snapshot.progress.id
    input observation <- Observation.Recorded(0)
    result inspected Result
    on Done(value) observe Observation.Recorded(value) then finish done
    on Pending(key) suspend Start retaining original attempt; do-not-assume-rollback
    on-call-failure suspend Start
  step mark:
    local-observation Observation.Recorded(0)
    commit-before run
    on-unknown inspect original observation before any provider dispatch
    next run only after fresh acknowledged local commit or native never-dispatched journal evidence
  step review:
    requires persisted snapshot.progress.state == Status.NeedsReview
    suspend needs-review
  terminal done:
    require persisted Demo.Progress.state == Done
    effects none
`;
const entries=entry('StartEntry','Flow',true)+entry('ReadEntry','ReadSnapshot')+entry('ClaimEntry','Claim')+entry('ObserveEntry','Observe')+entry('InspectEntry','Inspect')+entry('RunEntry','Run');
const asset={source_module:'Demo@1',worker:{abi:'craft.test-worker/v1-candidate',properties:{workerId:'Id'}},identity_producers:{abi:'craft.test-identities/v1-candidate',methods:{fingerprint:{parameters:['Started'],result:'Id'}}}};
const fixture=(flow=workflow,decl=declarations,access=entries)=>({sources:[{path:'application.alch',text:decl+flow+access}],assets:[{path:'context.json',text:JSON.stringify(asset)}]});
const check=(flow=workflow,decl=declarations,access=entries)=>{const f=fixture(flow,decl,access);return checkCoreCommerceWorkflowSources(f.sources,f.assets);};
const result=(flow=workflow)=>check(flow).workflows[0]!;
const remote=(steps:readonly CoreWorkflowStep[],name='run')=>{const r=steps.find(s=>s.name===name);if(r?.kind!=='remote')assert.fail('not a remote step');return r;};
const failure=(run:()=>unknown,code?:string)=>assert.throws(run,(e:unknown)=>e instanceof CoreCommerceSourceError&&(!code||e.diagnostics[0]!.code===code));
function historicalSource(){const owner=createCoreCommerceSourceOwner(),handle=owner.prepare(fileURLToPath(new URL('../../../../../../../implementation/craft-alchlang-commerce-2026-10-16/evidence/EC07/binding-repair-before/',import.meta.url)).replace(/\/$/,'')),inspection=owner.inspect(handle),paths=new Set(inspection.reconstruction.modules.map(m=>m.path));return {owner,handle,sources:inspection.files.filter(f=>paths.has(f.path)),assets:inspection.files.filter(f=>f.path.endsWith('.json'))};}
test('preserved pre-repair Workflow exposes the same unqualified ABI binding without accepting the source',()=>{const f=historicalSource(),r=auditCoreCommerceWorkflowSources(f.sources,f.assets);assert.equal(r.workflows.length,0);assert.equal(r.complete,false);assert.equal(r.diagnostics[0]!.workflow,'Orders.Checkout.Checkout');assert.equal(r.diagnostics[0]!.diagnostics[0]!.code,'UnknownReference');assert.match(r.diagnostics[0]!.diagnostics[0]!.message,/CancellationReason/);f.owner.assertCurrent(f.handle);f.owner.dispose(f.handle);});
test('isolated explicit annotation repair checks the actual 15-step, 16-resume-case Workflow without source mutation',()=>{const f=historicalSource(),assets=f.assets.map(a=>{if(a.path!=='contracts/context.json')return a;const d=JSON.parse(a.text);d.identity_producers.methods.orderActionFingerprint.parameters[2].type='optional<Shop.Events.CancellationReason>';return {...a,text:JSON.stringify(d)};}),r=checkCoreCommerceWorkflowSources(f.sources,assets);assert.equal(r.workflows[0]!.steps.length,15);assert.equal(r.workflows[0]!.resume.length,16);assert.equal(r.workflows[0]!.terminals.length,2);assert.equal(r.workflows[0]!.qualification,'typed-workflow-source-only');f.owner.assertCurrent(f.handle);f.owner.dispose(f.handle);});
test('driver signatures and input expressions retain source order',()=>{const r=result();assert.deepEqual(r.drivers.map(d=>d.kind),['snapshot','claim','observation']);assert.deepEqual(r.drivers[2]!.call.arguments.map(a=>a.parameter),['id','expectedVersion','observation']);assert.equal(r.drivers[2]!.inspection!.role,'Query');});
test('source snapshot missing failure is retained exactly rather than replaced by a generic code',()=>assert.deepEqual(result(workflow.replace('on-missing fail missing','on-missing reject custom-missing')).drivers[0]!.on_missing,{kind:'reject',code:'custom-missing'}));
test('claim metadata requires actual private worker evidence rather than row data as a capability',()=>{const r=result();assert.ok(r.drivers[1]!.requirements.includes('original-private-worker-and-quiescent-predecessor-evidence'));assert.ok(r.native_requirements.includes('fresh-entry-decisions-independent-of-worker-lifetime'));assert.equal(Object.hasOwn(r,'native_owner'),false);});
test('observation contention retains the exact original value and never redispatches',()=>assert.ok(result().drivers[2]!.requirements.includes('contention-reapply-original-observation-never-redispatch')));
test('unknown observations cannot manufacture a continuation or infer rollback',()=>assert.ok(result().drivers[2]!.requirements.includes('unknown-retains-original-ticket-no-fresh-continuation-or-rollback-inference')));
test('the observation driver cannot replace the original step value with another well-typed observation',()=>failure(()=>check(workflow.replace('input observation <- step.observation','input observation <- Observation.Recorded(0)')),'InvalidContract'));
test('unknown observation inspection must retain the exact original observation and identity',()=>{
 failure(()=>check(workflow.replace('observation=step.observation','observation=Observation.Recorded(0)')),'InvalidContract');
 failure(()=>check(workflow.replace('Demo.InspectEntry(id=snapshot.progress.id','Demo.InspectEntry(id="another"')),'InvalidContract');
});
test('unhandled variants and call failures retain fixed suspension defaults',()=>{const r=result(),s=remote(r.steps);assert.deepEqual(s.unhandled_variants,['Other']);assert.equal(s.fallback,'suspend-same-persisted-state-retaining-original-journal');assert.equal(r.defaults.max_transitions_per_resume,64);assert.equal(r.defaults.transition_limit,'suspend-retaining-original-journal');});
test('resume targets distinguish persisted states, control suspensions and declared terminals',()=>{const r=result();assert.deepEqual(r.resume[2]!.action,{kind:'suspend',category:'control',target:'needs-review'});assert.deepEqual(r.resume[1]!.action,{kind:'finish',target:'done'});assert.deepEqual(remote(r.steps).branches[1]!.action,{kind:'suspend',category:'persisted-state',target:'Start'});});
test('guarded repeated variant cases preserve first-match source order',()=>{const r=result(workflow.replace('    on Done(value) observe Observation.Recorded(value) then finish done','    on Done(value) when value > 0 observe Observation.Recorded(value) then finish done\n    on Done(value) suspend Start')),s=remote(r.steps);assert.equal(s.branches[0]!.guard!.type.kind,'Bool');assert.equal(s.branches[1]!.variant,'Done');});
test('a guard with no unguarded final pattern retains the variant in the fallback set',()=>{const s=remote(result(workflow.replace('on Done(value) observe','on Done(value) when value > 0 observe')).steps);assert.ok(s.unhandled_variants.includes('Done'));});
test('branch payload binders do not leak between steps or fallback channels',()=>failure(()=>check(workflow.replace('on-call-failure suspend Start','on-call-failure observe Observation.Recorded(value) then finish done')),'UnknownReference'));
test('local observations require original acknowledged commit or never-dispatched evidence',()=>{const s=result().steps.find(s=>s.kind==='local-observation');assert.equal(s?.kind,'local-observation');if(s?.kind==='local-observation'){assert.equal(s.commit_before,'run');assert.ok(s.requirements.includes('fresh-acknowledged-local-commit-or-original-never-dispatched-journal-evidence'));}});
test('retaining an original attempt survives a following uncertainty restriction',()=>{const b=remote(result().steps,'inspect').branches[1]!;assert.equal(b.retaining,'attempt');assert.equal(b.restriction,'do-not-assume-rollback');});
test('unknown commit may continue only to a read-only inspection step',()=>{const r=result(workflow.replace('    on-call-failure suspend Start','    on-unknown continue inspect; do-not-release\n    on-call-failure suspend Start'));assert.equal(remote(r.steps).branches.at(-2)!.channel,'unknown');failure(()=>check(workflow.replace('    on-call-failure suspend Start','    on-unknown continue run; do-not-release\n    on-call-failure suspend Start')),'InvalidContract');});
test('terminal checks use current persisted Entity projections and produce no domain effects',()=>{const t=result().terminals[0]!;assert.deepEqual(t.persisted_sources,['Demo.Progress']);assert.equal(t.effects,'none');assert.equal(t.on_false,'suspend-same-state');assert.equal(t.guard.type.kind,'Bool');});
test('persisted Entity aliases cannot be accessed as ordinary pre-dispatch data',()=>failure(()=>check(workflow.replace('correlation event.id','correlation Demo.Progress.id')),'TypeMismatch'));
test('review guards retain an original persisted-state evidence requirement',()=>{const r=result().steps.find(s=>s.kind==='review');assert.equal(r?.kind,'review');if(r?.kind==='review')assert.equal(r.required_evidence,'original-current-persisted-state');});
for(const [label,flow,code]of [
 ['undeclared owner',workflow.replace('owner demo','owner other'),'InvalidContract'],
 ['undeclared producer',workflow.replace('input-producer demo','input-producer other'),'UnknownReference'],
 ['wrong ingress entry',workflow.replace('input-entry Demo.StartEntry','input-entry Demo.ReadEntry'),'TypeMismatch'],
 ['wrong durable role',workflow.replace('durable-state Progress','durable-state Snapshot'),'InvalidContract'],
 ['missing ownership field',workflow.replace('workerOwner, workerEpoch, version','workerOwner, absent, version'),'UnknownReference'],
 ['duplicate ownership field',workflow.replace('workerOwner, workerEpoch, version','workerOwner, version, version'),'DuplicateSymbol'],
 ['incompatible ownership types',workflow.replace('workerOwner, workerEpoch, version','workerEpoch, version, workerOwner'),'TypeMismatch'],
 ['record correlation',workflow.replace('correlation event.id','correlation event'),'TypeMismatch'],
 ['nontext fingerprint',workflow.replace('compare identities.fingerprint(event)','compare 1'),'TypeMismatch'],
 ['missing original entry identity',workflow.replace('identity logicalEntryId, event.id','identity event.id'),'MissingMapping'],
 ['duplicate inbox key',workflow.replace('logicalEntryId, event.id','logicalEntryId, event.id, event.id'),'DuplicateSymbol'],
 ['unknown inbox key',workflow.replace('logicalEntryId, event.id','logicalEntryId, missing'),'UnknownReference'],
 ['wrong snapshot role',workflow.replace('snapshot-operation Demo.ReadEntry','snapshot-operation Demo.ClaimEntry'),'TypeMismatch'],
 ['missing snapshot input',workflow.replace('    input id <- event.id\n',''),'MissingMapping'],
 ['wrong snapshot input type',workflow.replace('input id <- event.id','input id <- true'),'TypeMismatch'],
 ['duplicate snapshot input',workflow.replace('    input id <- event.id','    input id <- event.id\n    input id <- event.id'),'DuplicateSymbol'],
 ['wrong snapshot result',workflow.replace('result snapshot Snapshot','result snapshot Commit'),'TypeMismatch'],
 ['nonBool snapshot guard',workflow.replace('require snapshot.progress.id == event.id','require snapshot.progress.id'),'TypeMismatch'],
 ['immutable input outside snapshot',workflow.replace('immutable-inputs snapshot.progress.id','immutable-inputs event.id'),'InvalidContract'],
 ['unknown immutable field',workflow.replace('immutable-inputs snapshot.progress.id','immutable-inputs snapshot.progress.missing'),'UnknownReference'],
 ['observation expects wrong type',workflow.replace('input observation <- step.observation','input observation <- true'),'TypeMismatch'],
 ['unknown inspection named argument',workflow.replace('Demo.InspectEntry(id=snapshot.progress.id,observation=step.observation)','Demo.InspectEntry(other=snapshot.progress.id,observation=step.observation)'),'UnknownReference'],
 ['mutating unknown observation inspection',workflow.replace('Demo.InspectEntry(id=snapshot.progress.id,observation=step.observation)','Demo.ObserveEntry(id=snapshot.progress.id,expectedVersion=0,observation=step.observation)'),'TypeMismatch'],
 ['unknown resume state',workflow.replace('Start -> run','Absent -> run'),'UnknownReference'],
 ['nonBool resume guard',workflow.replace('Start -> run','Start when event.id -> run'),'TypeMismatch'],
 ['unreachable resume case',workflow.replace('Start -> run','Start -> run\n    Start when true -> run'),'InvalidContract'],
 ['unknown resume step',workflow.replace('Start -> run','Start -> absent'),'UnknownReference'],
 ['unknown terminal',workflow.replace('Done -> finish done','Done -> finish absent'),'UnknownReference'],
 ['unknown suspend state',workflow.replace('on Pending(key) suspend Start','on Pending(key) suspend Absent'),'UnknownReference'],
 ['duplicate step',workflow.replace('step inspect:','step run:'),'DuplicateSymbol'],
 ['duplicate terminal',workflow+ '  terminal done:\n    require persisted true\n    effects none\n','DuplicateSymbol'],
 ['step terminal collision',workflow.replace('terminal done:','terminal run:'),'DuplicateSymbol'],
 ['unknown step entry',workflow.replace('invokes Demo.RunEntry','invokes Demo.Absent'),'UnknownReference'],
 ['step bypasses entry',workflow.replace('invokes Demo.RunEntry','invokes Demo.Run'),'TypeMismatch'],
 ['wrong step argument',workflow.replace('input value <- 0','input value <- true'),'TypeMismatch'],
 ['wrong step result',workflow.replace('result result Result','result result Commit'),'TypeMismatch'],
 ['unknown variant',workflow.replace('on Done(value)','on Missing(value)'),'UnknownReference'],
 ['wrong payload type',workflow.replace('on Pending(key) suspend Start retaining original command','on Pending(key) observe Observation.Recorded(key) then finish done'),'TypeMismatch'],
 ['nonBool pattern guard',workflow.replace('on Done(value) observe','on Done(value) when value observe'),'TypeMismatch'],
 ['unreachable pattern',workflow.replace('on Done(value) observe Observation.Recorded(value) then finish done','on Done(value) observe Observation.Recorded(value) then finish done\n    on Done(value) when true suspend Start'),'InvalidContract'],
 ['duplicate grouped pattern',workflow.replace('on Pending(key) suspend Start','on Pending(key), Pending(key) suspend Start'),'InvalidContract'],
 ['grouped incompatible payload',workflow.replace('on Done(value) observe','on Done(value), Other(value) observe'),'TypeMismatch'],
 ['invalid observation type',workflow.replace('observe Observation.Recorded(value)','observe true'),'TypeMismatch'],
 ['branch binder shadows input',workflow.replace('on Done(value)','on Done(event)'),'DuplicateSymbol'],
 ['unknown local target',workflow.replace('commit-before run','commit-before absent'),'UnknownReference'],
 ['different local targets',workflow.replace('commit-before run','commit-before inspect'),'InvalidContract'],
 ['wrong local observation',workflow.replace('local-observation Observation.Recorded(0)','local-observation true'),'TypeMismatch'],
 ['nonBool terminal guard',workflow.replace('require persisted Demo.Progress.state == Done','require persisted Demo.Progress.id'),'TypeMismatch'],
 ['foreign persisted Entity',workflow.replace('require persisted Demo.Progress.state == Done','require persisted Other.Progress.state == Done'),'UnknownReference'],
 ['unbound remote result in failure',workflow.replace('on-call-failure suspend Start','on-call-failure require result == Result.Done(1) then finish done'),'UnknownReference'],
]as const)test('rejects '+label,()=>failure(()=>check(flow),code));
test('a producer mismatch with its ingress entry rejects',()=>failure(()=>check(workflow,declarations,entries.replace('producer demo','producer other')),'InvalidContract'));
test('an event entry cannot masquerade as a remote request-response entry',()=>failure(()=>check(workflow,declarations,entries.replace('entry Demo.RunEntry:\n  invokes Demo.Run\n  interaction request-response','entry Demo.RunEntry:\n  invokes Demo.Run\n  interaction event')),'TypeMismatch'));
test('worker context binding cannot be an identity producer',()=>failure(()=>check(workflow.replace('context worker Worker','context worker Identity')),'InvalidContract'));
test('observation commit requires its actual fresh Bool field',()=>failure(()=>check(workflow,declarations.replace('  fresh Bool','  fresh UInt64')),'MissingMapping'));
test('a variant guard narrows its Optional payload only on the matching true path',()=>{
 const decl=declarations.replace('enum Result:','value-object Maybe:\n  count optional<UInt64>\nenum Result:\n  variant Optional value Maybe');
 const flow=workflow.replace('    on Pending(key) suspend Start retaining original command','    on Optional(value) when present(value.count) observe Observation.Recorded(value.count) then finish done\n    on Pending(key) suspend Start retaining original command');
 assert.ok(remote(check(flow,decl).workflows[0]!.steps).branches.some(b=>b.variant==='Optional'&&b.guard));
 failure(()=>check(flow.replace(' when present(value.count)',''),decl),'TypeMismatch');
 failure(()=>check(flow.replace(' when present(value.count)',' when absent(value.count)'),decl),'TypeMismatch');
});
test('worker custody must be declared as a local worker owner',()=>failure(()=>check(workflow,declarations.replace('custody private-registered-local-worker-owner','custody private-registered-service-entry-owner')),'InvalidContract'));
test('duplicate call failure channels cannot be silently replaced',()=>failure(()=>check(workflow.replace('on-call-failure suspend Start','on-call-failure suspend Start\n    on-call-failure suspend same-state')),'DuplicateSymbol'));
test('unknown inspection cannot accept omitted or positional arguments',()=>{
 for(const replacement of ['Demo.InspectEntry(id=snapshot.progress.id)','Demo.InspectEntry(snapshot.progress.id,step.observation)'])failure(()=>check(workflow.replace('Demo.InspectEntry(id=snapshot.progress.id,observation=step.observation)',replacement)),'MissingMapping');
});
test('a step cannot invoke a Workflow recursively through its ingress',()=>failure(()=>check(workflow.replace('invokes Demo.RunEntry','invokes Demo.StartEntry')),'TypeMismatch'));
test('Workflow proposal data is wholly reconstructed without restoring any owner',()=>{const f=fixture(),proposal=JSON.parse(JSON.stringify(check()));const r=checkCoreCommerceWorkflowProposal(f.sources,f.assets,proposal);assert.notEqual(r,proposal);assert.equal(r.complete,true);assert.equal(Object.hasOwn(r,'accepted'),false);});
for(const field of ['owner','correlation','input_entry','inbox_identity','durable_state','ownership','drivers','resume','steps','terminals','defaults','native_requirements','qualification'])test('rejects Workflow proposal forgery '+field,()=>{const f=fixture(),proposal=JSON.parse(JSON.stringify(check()));proposal.workflows[0][field]='forged';failure(()=>checkCoreCommerceWorkflowProposal(f.sources,f.assets,proposal),'InvalidContract');});
test('proposal accessors reject without running code',()=>{const f=fixture();let called=false;failure(()=>checkCoreCommerceWorkflowProposal(f.sources,f.assets,{get workflows(){called=true;return [];}}),'InvalidContract');assert.equal(called,false);});
