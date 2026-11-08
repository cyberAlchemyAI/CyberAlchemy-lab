/** A bounded pre-claim read for the checked Core Workflow claim Operation.
 * It returns only source-declared arguments from an original committed claim
 * and durable row. The generated Operation still owns the final CAS.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {assertCommerceWorkflowCoordinationBindingV1,
 type CommerceWorkflowCoordinationBindingV1} from '../commerce/commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,
 type CommerceWorkScheduleClaimV1} from '../commerce/commerce-service-storage-v1.js';
import type {CoreExpression} from '../commerce/commerce-core-expression.js';

const MAX_U64=(1n<<64n)-1n;
const pathOf=(value:CoreExpression):readonly string[]=>{
 if(value.kind==='name')return value.name.split('.');
 if(value.kind==='field')return [...pathOf(value.value),value.field];
 return [];
};
const field=(value:object,name:string):unknown=>{
 const descriptor=Object.getOwnPropertyDescriptor(value,name);
 if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))
  throw new Error('original durable progress field is missing');
 return descriptor.value;
};

export type CoreCommerceWorkerClaimInput=
 Readonly<{kind:'ready';entry:string;operation:string;service:string;
  parameters:Readonly<Record<string,string|bigint>>;source_capture_sha256:string;
  qualification:'source-selected-durable-progress-claim-input-only;fresh-entry-auth-and-generated-CAS-required'}>|
 Readonly<{kind:'not-ready';reason:'durable-progress-missing'|'prior-owner-changed';authority_effect:'none'}>;

export function selectCoreCommerceWorkerClaimInput(
 binding:CommerceWorkflowCoordinationBindingV1,
 storage:CommerceServiceStorageOwnerV1,
 claim:CommerceWorkScheduleClaimV1,
):CoreCommerceWorkerClaimInput {
 assertCommerceWorkflowCoordinationBindingV1(binding);
 assertCommerceServiceStorageOwnerV1(storage);
 storage.assertWorkScheduleClaimCurrent(claim);
 const source=binding.inspect(),store=storage.inspect(),committed=storage.inspectWorkScheduleClaim(claim),
  workflow=source.workflow;
 if(store.service!==source.owner_service||store.source_capture_sha256!==source.source_capture_sha256||
  committed.store_id!==store.store_id||committed.workflow!==workflow.name||
  committed.source_capture_sha256!==source.source_capture_sha256||
  committed.consumer_entry_id!==workflow.input_entry||
  typeof committed.order_id!=='string'||!committed.order_id)
  throw new Error('claim input requires the exact original committed Workflow claim');
 const snapshots=workflow.drivers.filter(driver=>driver.kind==='snapshot'),
  claims=workflow.drivers.filter(driver=>driver.kind==='claim');
 if(snapshots.length!==1||claims.length!==1)
  throw new Error('one checked snapshot and claim driver required');
 const snapshot=snapshots[0]!,driver=claims[0]!,snapshotName=snapshot.call.binding,
  guard=snapshot.guard?.source,ownership=workflow.ownership;
 if(!snapshotName||snapshot.call.role!=='Query'||driver.call.role!=='Operation'||
  ownership.length!==3||ownership[0]!.field!=='workerOwner'||
  ownership[1]!.field!=='workerEpoch'||ownership[2]!.field!=='version'||
  !guard||guard.kind!=='binary'||guard.operator!=='=='||driver.call.arguments.length!==2)
  throw new Error('checked Core Workflow claim/snapshot native family required');
 const correlation=pathOf(workflow.correlation.source),left=pathOf(guard.left),right=pathOf(guard.right),
  guarded=isDeepStrictEqual(left,correlation)?right:isDeepStrictEqual(right,correlation)?left:[];
 if(correlation.length<2||correlation[0]!==workflow.parameters[0]?.name||
  !isDeepStrictEqual(guarded,[snapshotName,'order','id']))
  throw new Error('snapshot guard must bind the original Workflow correlation');
 const expectedVersion=[snapshotName,'progress',ownership[2]!.field],parameters:Record<string,string|bigint>=Object.create(null);
 let correlationParameter:string|null=null,versionParameter:string|null=null;
 for(const argument of driver.call.arguments){
  const path=pathOf(argument.value.source);
  if(isDeepStrictEqual(path,guarded)){correlationParameter=argument.parameter;parameters[argument.parameter]=committed.order_id;}
  else if(isDeepStrictEqual(path,expectedVersion)){versionParameter=argument.parameter;parameters[argument.parameter]=0n;}
  else throw new Error('claim argument lacks a checked correlation or progress version source');
 }
 if(correlationParameter!=='orderId'||versionParameter!=='expectedProgressVersion'||Object.keys(parameters).length!==2)
  throw new Error('exact source claim correlation and version arguments required');
 const row=storage.inspectStoredRecord(workflow.durable_state,0,{orderId:committed.order_id});
 if(row===null)return Object.freeze({kind:'not-ready' as const,reason:'durable-progress-missing' as const,authority_effect:'none' as const});
 if(typeof row!=='object'||Array.isArray(row)||host.isProxy(row)||
  ![Object.prototype,null].includes(Object.getPrototypeOf(row)))
  throw new Error('source-owned durable progress row required');
 const orderId=field(row,'orderId'),version=field(row,ownership[2]!.field),
  workerOwner=field(row,ownership[0]!.field),workerEpoch=field(row,ownership[1]!.field);
 if(orderId!==committed.order_id||typeof version!=='bigint'||version<1n||version>=MAX_U64||
  typeof workerEpoch!=='bigint')
  throw new Error('durable progress identity, epoch or version changed');
 if(workerEpoch!==committed.prior_worker_epoch)
  return Object.freeze({kind:'not-ready' as const,reason:'prior-owner-changed' as const,authority_effect:'none' as const});
 const prior=committed.prior_worker_owner,owner=workerOwner&&typeof workerOwner==='object'&&!Array.isArray(workerOwner)&&
  !host.isProxy(workerOwner)?workerOwner as Record<string,unknown>:null;
 if(!owner||owner.kind!==prior.kind||prior.kind==='none'&&Object.keys(owner).length!==1||
  prior.kind==='some'&&(Object.keys(owner).length!==2||owner.value!==prior.value))
  return Object.freeze({kind:'not-ready' as const,reason:'prior-owner-changed' as const,authority_effect:'none' as const});
 parameters[versionParameter]=version;
 storage.assertWorkScheduleClaimCurrent(claim);
 return Object.freeze({kind:'ready' as const,entry:driver.call.entry,operation:driver.call.target,
  service:workflow.owner,parameters:Object.freeze(parameters),source_capture_sha256:source.source_capture_sha256,
  qualification:'source-selected-durable-progress-claim-input-only;fresh-entry-auth-and-generated-CAS-required' as const});
}
