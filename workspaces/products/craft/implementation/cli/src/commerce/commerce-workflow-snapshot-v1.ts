/** A worker snapshot is a read from the original selected Query, not caller data.
 * Rechecking detects changed source rows before a later workflow step prepares
 * its own journal/command. This owner issues no dispatch or commit authority.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {isDeepStrictEqual,types as host} from 'node:util';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1} from './commerce-service-storage-v1.js';
import {assertCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1,type CommerceWorkerContextV1} from './commerce-worker-context-v1.js';
import {assertCommerceSourceQueryRuntimeV1,type CommerceSourceQueryRuntimeV1} from './commerce-source-query-runtime-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1} from './commerce-selected-entry-auth-v1.js';
import type {CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import type {CoreExpression} from './commerce-core-expression.js';
import type {CommerceNativeValue} from './commerce-native-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-workflow-coordination-binding-v1'+ext,'commerce-service-storage-v1'+ext,
 'commerce-worker-context-v1'+ext,'commerce-source-query-runtime-v1'+ext,
 'commerce-selected-entry-auth-v1'+ext,
]);
export class CommerceWorkflowSnapshotErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowSnapshotErrorV1';}
}
function bad(code:string):never {throw new CommerceWorkflowSnapshotErrorV1(code);}
const fieldPath=(source:CoreExpression):readonly string[]=>{
 if(source.kind==='name'){
  const parts=source.name.split('.');
  if(parts.length>16||parts.some(part=>!/^[A-Za-z_][A-Za-z0-9_-]*$/.test(part)))bad('UnsupportedSnapshotShape');
  return parts;
 }
 if(source.kind==='field'){
  if(!/^[A-Za-z_][A-Za-z0-9_-]*$/.test(source.field))bad('UnsupportedSnapshotShape');
  return [...fieldPath(source.value),source.field];
 }
 return [];
};
const get=(value:unknown,path:readonly string[]):unknown=>{
 let at=value;
 for(const name of path){
  if(!at||typeof at!=='object'||Array.isArray(at)||host.isProxy(at))bad('InvalidSnapshot');
  const descriptor=Object.getOwnPropertyDescriptor(at,name);
  if(!descriptor)bad('InvalidSnapshot');
  if(!descriptor.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidSnapshot');
  at=descriptor.value;
 }
 return at;
};
const snapshotCopy=(value:unknown):CommerceNativeValue=>{
 let nodes=0;
 const copy=(v:unknown,depth:number):CommerceNativeValue=>{
  if(++nodes>65536||depth>64)bad('SnapshotBound');
  if(typeof v==='boolean'||typeof v==='string'||typeof v==='bigint')return v;
  if(!v||typeof v!=='object')bad('InvalidSnapshot');
  if(host.isProxy(v))bad('InvalidSnapshot');
  if(Array.isArray(v)){
   if(Object.getPrototypeOf(v)!==Array.prototype||v.length>65536||Reflect.ownKeys(v).length!==v.length+1)bad('InvalidSnapshot');
   const out:CommerceNativeValue[]=[];
   for(let index=0;index<v.length;index++){
    const descriptor=Object.getOwnPropertyDescriptor(v,String(index));
    if(!descriptor||!descriptor.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidSnapshot');
    out.push(copy(descriptor.value,depth+1));
   }
   return Object.freeze(out);
  }
  if(![Object.prototype,null].includes(Object.getPrototypeOf(v)))bad('InvalidSnapshot');
  const names=Reflect.ownKeys(v),descriptors=Object.getOwnPropertyDescriptors(v),out:Record<string,CommerceNativeValue>=Object.create(null);
  if(names.length>65536)bad('SnapshotBound');
  for(const name of names){
   if(typeof name!=='string')bad('InvalidSnapshot');
   const descriptor=descriptors[name];
   if(!descriptor||!descriptor.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidSnapshot');
   out[name]=copy(descriptor.value,depth+1);
  }
  return Object.freeze(out);
 };
 return copy(value,0);
};

export interface CommerceWorkflowSnapshotHandleV1 {
 readonly kind:'original-worker-snapshot/v1-candidate';
}
export interface CommerceWorkflowSnapshotInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly entry_id:string;readonly query_id:string;readonly invocation_id:string;
 readonly order_id:string;readonly worker_id:string;readonly worker_epoch:bigint;
 readonly progress_version:bigint;readonly value:CommerceNativeValue;
 readonly qualification:'original-source-worker-query-snapshot;recheck-before-step;no-dispatch-authority';
 readonly authority_effect:'none';
}
export type CommerceWorkflowSnapshotReadV1=
 {readonly kind:'snapshot';readonly handle:CommerceWorkflowSnapshotHandleV1}|
 {readonly kind:'rejected'|'failed';readonly code:string;readonly authority_effect:'none'};
export interface CommerceWorkflowSnapshotOwnerV1 {
 read():CommerceWorkflowSnapshotReadV1;
 inspect(handle:CommerceWorkflowSnapshotHandleV1):CommerceWorkflowSnapshotInspectionV1;
 recheck(handle:CommerceWorkflowSnapshotHandleV1):CommerceWorkflowSnapshotInspectionV1;
 assertCurrent():void;
 dispose():void;
}
const owners=new WeakSet<object>();
/** Brand only. Follow immediately with a private method that checks currentness. */
export function assertCommerceWorkflowSnapshotOwnerBrandV1(owner:CommerceWorkflowSnapshotOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');
}
export function assertCommerceWorkflowSnapshotOwnerV1(owner:CommerceWorkflowSnapshotOwnerV1):void {
 assertCommerceWorkflowSnapshotOwnerBrandV1(owner);owner.assertCurrent();
}
/** Bound to one fresh worker Query invocation. A new process/claim creates a
 * new owner; a prior witness cannot survive worker or storage retirement. */
export function createCommerceWorkflowSnapshotOwnerV1(
 binding:CommerceWorkflowCoordinationBindingV1,storage:CommerceServiceStorageOwnerV1,
 workerOwner:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1,
 query:CommerceSourceQueryRuntimeV1,selectedAuth:CommerceSelectedEntryAuthOwnerV1,
 invocation:CommerceOperationInvocationHandle,
):CommerceWorkflowSnapshotOwnerV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCommerceServiceStorageOwnerV1(storage);
 assertCommerceWorkerContextOwnerV1(workerOwner);assertCommerceSourceQueryRuntimeV1(query);
 assertCommerceSelectedEntryAuthOwnerV1(selectedAuth);pin.assertCurrent();
 const selected=binding.inspect(),store=storage.inspect(),worker=workerOwner.inspectContext(workerContext),
  authorized=selectedAuth.inspectInvocation(invocation),workflow=selected.workflow;
 const snapshots=workflow.drivers.filter(driver=>driver.kind==='snapshot'),claims=workflow.drivers.filter(driver=>driver.kind==='claim');
 if(snapshots.length!==1||claims.length!==1||!snapshots[0]!.call.binding||
    snapshots[0]!.call.role!=='Query'||workflow.ownership.length!==3||
    workflow.owner!==store.service||selected.source_capture_sha256!==store.source_capture_sha256||
    worker.workflow!==workflow.name||worker.source_capture_sha256!==selected.source_capture_sha256||
    worker.store_id!==store.store_id||!worker.progress_claim_qualified||
    authorized.entry!==snapshots[0]!.call.entry||authorized.operation!==snapshots[0]!.call.target||
    authorized.role!=='Query'||authorized.service!==store.service||
    authorized.source_sha256!==selected.source_capture_sha256||
    authorized.actual_business_resource_owners_qualified!==true||query.query!==authorized.operation)
  bad('ForeignOwner');
 const snapshot=snapshots[0]!,bindingName=snapshot.call.binding!,versionField=workflow.ownership[2]!.field;
 const versionPaths=claims[0]!.call.arguments.map(argument=>fieldPath(argument.value.source))
  .filter(parts=>parts.length>=3&&parts[0]===bindingName&&parts.at(-1)===versionField);
 if(versionPaths.length!==1)bad('UnsupportedSnapshotShape');
 const progressPath=versionPaths[0]!.slice(1,-1),correlation=fieldPath(workflow.correlation.source);
 if(progressPath.length===0||correlation.length<2||correlation[0]!==workflow.parameters[0]?.name)
  bad('UnsupportedSnapshotShape');
 const correlationField=correlation.at(-1)!;
 const guard=snapshot.guard?.source;
 if(!guard)bad('UnsupportedSnapshotGuard');
 if(guard.kind!=='binary')bad('UnsupportedSnapshotGuard');
 if(guard.operator!=='==')bad('UnsupportedSnapshotGuard');
 const left=fieldPath(guard.left),right=fieldPath(guard.right),
  snapshotGuardPath=left[0]===bindingName&&isDeepStrictEqual(right,correlation)?left.slice(1):
   right[0]===bindingName&&isDeepStrictEqual(left,correlation)?right.slice(1):null;
 if(!snapshotGuardPath||snapshotGuardPath.length===0)bad('UnsupportedSnapshotGuard');
 const guardedPath:readonly string[]=snapshotGuardPath;
 const handles=new WeakMap<object,CommerceWorkflowSnapshotInspectionV1>();
 let disposed=false;
 const current=()=>{
  if(disposed)bad('DisposedOwner');pin.assertCurrent();binding.assertCurrent();query.assertCurrent();
  const now=workerOwner.inspectContext(workerContext),actual=storage.inspect(),entry=selectedAuth.inspectInvocation(invocation);
  if(now.workflow!==worker.workflow||now.source_capture_sha256!==worker.source_capture_sha256||
     now.store_id!==worker.store_id||now.order_id!==worker.order_id||now.worker_id!==worker.worker_id||
     now.worker_epoch!==worker.worker_epoch||!now.progress_claim_qualified||
     actual.store_id!==store.store_id||actual.schema_sha256!==store.schema_sha256||
     entry.root_invocation_id!==authorized.root_invocation_id||entry.entry!==authorized.entry||
     entry.operation!==authorized.operation||entry.role!=='Query'||
     entry.source_sha256!==authorized.source_sha256||entry.service!==authorized.service)
   bad('StaleOwner');
 };
 const readValue=():{value:CommerceNativeValue;version:bigint}|{kind:'rejected'|'failed';code:string}=>{
  current();const result=query.executeWorker(selectedAuth,invocation);
  if(result.kind!=='returned')return {kind:result.kind,code:result.code};
  if(result.qualification!=='source-selected-worker-query-result;original-entry-and-worker-custody')bad('ForeignOwner');
  const value=snapshotCopy(result.value),progress=get(value,progressPath),owner=get(progress,[workflow.ownership[0]!.field]),
   epoch=get(progress,[workflow.ownership[1]!.field]),version=get(progress,[versionField]),
   orderId=get(progress,[correlationField]),guardId=get(value,guardedPath);
  const ownerRecord=owner&&typeof owner==='object'&&!Array.isArray(owner)?owner as Record<string,unknown>:null;
  // The private WorkerContext and its durable Progress claim are checked by
  // current() before this Query and again below. Repeat only the exact
  // optional-owner shape/value comparison here; owns() and assertOrder()
  // would each reread the same native claim within this synchronous read.
  const owned=!!ownerRecord&&Object.keys(ownerRecord).length===2&&
   ownerRecord.kind==='some'&&ownerRecord.value===worker.worker_id;
  if(typeof orderId!=='string'||orderId!==worker.order_id||guardId!==worker.order_id||
     typeof epoch!=='bigint'||epoch!==worker.worker_epoch||typeof version!=='bigint'||version<1n||
     !owned)bad('ForeignWorkerSnapshot');
  current();return {value,version};
 };
 const owner:CommerceWorkflowSnapshotOwnerV1=Object.freeze({
  read(){const result=readValue();if('kind'in result)return Object.freeze({...result,authority_effect:'none' as const});
   const handle:CommerceWorkflowSnapshotHandleV1=Object.freeze({kind:'original-worker-snapshot/v1-candidate'});
   const inspection:CommerceWorkflowSnapshotInspectionV1=Object.freeze({workflow:workflow.name,
    source_capture_sha256:selected.source_capture_sha256,store_id:store.store_id,
    entry_id:snapshot.call.entry,query_id:snapshot.call.target,invocation_id:authorized.root_invocation_id,
    order_id:worker.order_id,worker_id:worker.worker_id,worker_epoch:worker.worker_epoch,
    progress_version:result.version,value:result.value,
    qualification:'original-source-worker-query-snapshot;recheck-before-step;no-dispatch-authority',authority_effect:'none'});
   handles.set(handle,inspection);return Object.freeze({kind:'snapshot' as const,handle});
  },
  inspect(handle:CommerceWorkflowSnapshotHandleV1){current();return handles.get(handle)??bad('ForeignOwner');},
  recheck(handle:CommerceWorkflowSnapshotHandleV1){
   if(disposed)bad('DisposedOwner');
   const prior=handles.get(handle)??bad('ForeignOwner'),next=readValue();
   if('kind'in next||next.version!==prior.progress_version||!isDeepStrictEqual(next.value,prior.value))bad('StaleSnapshot');
   return prior;
  },
  assertCurrent:current,
  dispose(){disposed=true;},
 });
 owners.add(owner);current();return owner;
}
