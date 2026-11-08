import test from 'node:test';
import assert from 'node:assert/strict';
import {reconstructCoreCommerceModule} from '../../dist/commerce/commerce-core-reconstruction.js';
import {checkGenericWorkflowSource,GENERIC_WORKFLOW_CAPABILITIES} from '../../dist/generic/workflow-source.js';
import {GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES} from '../../dist/generic/composition-capabilities.js';
import {dataDigest} from '../../dist/profile-engine/contracts.js';

const source=`module Demo version 1

entity State:
  id UInt64
  identity id

event Done version 1:
  payload UInt64
  from Demo.CommitOp
  delivered-to Audit.Receive

workflow Flow:
  owner DemoService
  scope generated-recoverable
  profile contracts/workflow-profile.json
  input id UInt64
  correlation id
  durable-state Demo.State
  start Demo.Begin
  step reserve invokes Demo.Reserve compensate-with Demo.Undo
  step commit invokes Demo.Commit on-unknown resume-original-command on-definite-failure compensate
  step delivery awaits Demo.Done delivered-to Audit.Receive
  recovery needed-compensations-only reverse-completion

entry Demo.Begin:
  invokes Demo.StartOp
  interaction request-response
  access:
    authenticated customer
    permission demo.begin
    auth-resource demo
    auth-action begin
    auth-scope demo

entry Demo.Reserve:
  invokes Demo.ReserveOp
  interaction request-response
  access:
    authenticated operator
    permission demo.reserve
    auth-resource demo
    auth-action reserve
    auth-scope demo

entry Demo.Undo:
  invokes Demo.UndoOp
  interaction request-response
  access:
    authenticated operator
    permission demo.undo
    auth-resource demo
    auth-action undo
    auth-scope demo

entry Demo.Commit:
  invokes Demo.CommitOp
  interaction request-response
  access:
    authenticated operator
    permission demo.commit
    auth-resource demo
    auth-action commit
    auth-scope demo

entry Audit.Receive:
  invokes Audit.ReceiveOp
  interaction event Demo.Done
  access:
    authenticated service
    permission audit.receive
    auth-resource audit
    auth-action receive
    auth-scope audit
`;
const profile={schema_version:'craft.generic-event-profile/v1-candidate',capabilities:[...GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES]};
const selection={schema_version:'craft.generic-workflow-profile/v1-candidate',workflow:'Demo.Flow',base_event_profile_sha256:dataDigest(profile),capabilities:[...GENERIC_WORKFLOW_CAPABILITIES],recovery:'needed-compensations-only/reverse-completion-v1',storage:'service-owned-fenced-workflow-journal/v1-candidate'};
function fixture(text=source){
 const module=reconstructCoreCommerceModule(text,'demo.alch'),ownership=module.declarations.map(d=>({declaration:d.id,service:d.id.startsWith('Audit.')?'AuditService':'DemoService',category:'service'}));
 const reconstruction={modules:[module],ownership,services:[{service:'DemoService',module:'Demo'},{service:'AuditService',module:'Audit'}]};
 const command=(entry,target,principal_kind='operator',service='DemoService')=>({entry,target,service,interaction:'request-response',target_role:'Operation',parameters:[{name:'id',type:{kind:'scalar',name:'UInt64'}}],access:{principal_kind,permission:'demo.command',resource:'demo',action:'command',scope:'demo',route:'commerce:'+entry}});
 const receiver={entry:'Audit.Receive',target:'Audit.ReceiveOp',service:'AuditService',interaction:'event',target_role:'Operation',parameters:[],access:{permission:'audit.receive'}};
 const app={admission_mode:'event-handoff-entry',entries:[command('Demo.Begin','Demo.StartOp','customer'),command('Demo.Reserve','Demo.ReserveOp'),command('Demo.Undo','Demo.UndoOp'),command('Demo.Commit','Demo.CommitOp'),receiver],stateful_operations:[{operation:'Demo.StartOp',preflight:[]},{operation:'Demo.ReserveOp',preflight:[]},{operation:'Demo.UndoOp',preflight:[]},{operation:'Demo.CommitOp',preflight:[{kind:'write-external',call:{binding_ref:'provider'}}]}],write_bindings:[{id:'provider'}],event_bindings:[{id:'done',event_selector:'Demo.Done',target_entry:'Audit.Receive',target_service:'AuditService',producer_operation:'Demo.CommitOp'}]};
 return {reconstruction,app};
}
const check=(s=source,appOverride)=>{const f=fixture(s);return checkGenericWorkflowSource(f.reconstruction,appOverride??f.app,profile,selection,'source-digest');};

test('C13 authored Workflow projects typed protected commands, durable provider, Event receiver and compensation order',()=>{
 const c=check();assert.equal(c.workflow,'Demo.Flow');assert.equal(c.correlation,'id');assert.equal(c.durable_state,'Demo.State');assert.deepEqual(c.steps.map(s=>s.kind),['local-command','provider-command','event-await']);assert.deepEqual(c.compensation_order,['reserve']);assert.equal(c.steps[1].provider_write_bindings[0],'provider');assert.equal(c.steps[2].event_binding,'done');assert.equal(c.authority_effect,'none');
});
for(const [name,change] of [
 ['missing compensation',s=>s.replace('compensate-with Demo.Undo','')],
 ['foreign state',s=>s.replace('durable-state Demo.State','durable-state Audit.State')],
 ['wrong receiver',s=>s.replace('delivered-to Audit.Receive\n  recovery','delivered-to Audit.Missing\n  recovery')],
 ['wrong correlation type',s=>s.replace('input id UInt64','input id Bool')],
 ['duplicate step name',s=>s.replace('step commit invokes','step reserve invokes')],
])test(`C13 rejects ${name}`,()=>assert.throws(()=>check(change(source))));
test('C13 rejects unbound durable provider write and wrong Event producer',()=>{
 const f=fixture();assert.throws(()=>checkGenericWorkflowSource(f.reconstruction,{...f.app,write_bindings:[]},profile,selection,'source-digest'));
 assert.throws(()=>checkGenericWorkflowSource(f.reconstruction,{...f.app,event_bindings:[{...f.app.event_bindings[0],producer_operation:'Demo.Other'}]},profile,selection,'source-digest'));
});
