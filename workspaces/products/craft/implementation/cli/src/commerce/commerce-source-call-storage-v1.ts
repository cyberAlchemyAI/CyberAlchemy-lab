/** Authorized source-local call to selected SQLite transaction custody.
 * No command claim, quiescence witness, provider dispatch or mutation is issued.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1} from './commerce-selected-entry-auth-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,type CommerceServiceStorageLocalTransactionV1,type CommerceServiceStorageLocalTransactionInspectionV1} from './commerce-service-storage-v1.js';
import type {CommerceOperationInvocationHandle} from './commerce-stages-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-selected-entry-auth-v1'+ext,'commerce-service-storage-v1'+ext]);
const where={path:'source-call-storage',start:0,end:0};
export interface CommerceSourceCallStorageHandleV1 {readonly kind:'original-selected-source-call-storage/v1-candidate'}
export interface CommerceSourceCallStorageOwnerV1 {
 derive(root:CommerceOperationInvocationHandle,targetOperation:string,boundArguments:unknown,transaction:string):Promise<CommerceSourceCallStorageHandleV1>;
 inspect(handle:CommerceSourceCallStorageHandleV1):CommerceServiceStorageLocalTransactionInspectionV1;
 retire(handle:CommerceSourceCallStorageHandleV1):void;
 assertCurrent():void;dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceSourceCallStorageOwnerV1(owner:CommerceSourceCallStorageOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner',where,'original selected source-call storage owner required');owner.assertCurrent();
}

/** The original selected Auth owner issues the child, and the exact selected
 * storage owner binds only its checked source transaction program. */
export function createCommerceSourceCallStorageOwnerV1(selected:CommerceSelectedEntryAuthOwnerV1,storage:CommerceServiceStorageOwnerV1):CommerceSourceCallStorageOwnerV1 {
 assertCommerceSelectedEntryAuthOwnerV1(selected);assertCommerceServiceStorageOwnerV1(storage);pin.assertCurrent();
 const service=storage.inspect().service,sourceSha=storage.inspect().source_capture_sha256,familySha=storage.inspect().family_sha256;
 if(selected.inspect().source_capture_sha256!==sourceSha||selected.inspect().family_sha256!==familySha)
  fail('ForeignOwner',where,'selected source and storage family required');
 const active=new WeakMap<object,{root:CommerceOperationInvocationHandle;child:CommerceOperationInvocationHandle;program:CommerceServiceStorageLocalTransactionV1;inspection:CommerceServiceStorageLocalTransactionInspectionV1}>();
 const issued=new Set<CommerceSourceCallStorageHandleV1>();let disposed=false;
 const current=()=>{
  if(disposed)fail('DisposedOwner',where,'source-call storage owner disposed');pin.assertCurrent();selected.assertCurrent();storage.assertCurrent();
  const s=storage.inspect(),a=selected.inspect();
  if(s.service!==service||s.source_capture_sha256!==sourceSha||s.family_sha256!==familySha||a.source_capture_sha256!==sourceSha||a.family_sha256!==familySha)
   fail('StaleOwner',where,'selected source-call storage identities changed');
 };
 const row=(h:CommerceSourceCallStorageHandleV1)=>{current();const state=h&&typeof h==='object'?active.get(h):undefined;if(!state)fail('ForeignOwner',where,'exact selected source-call storage handle required');return state;};
 const owner:CommerceSourceCallStorageOwnerV1=Object.freeze({
  async derive(root:CommerceOperationInvocationHandle,targetOperation:string,boundArguments:unknown,transaction:string){
   current();const outer=selected.inspectInvocation(root);
   if(outer.depth!==0||outer.role!=='Operation'||outer.service!==service||outer.source_sha256!==sourceSha||outer.parent_call_path!==null)
    fail('ForeignOwner',where,'selected root Operation Entry for this service required');
   const sourceCallPath=selected.localCallPath(root,targetOperation);
   const child=selected.deriveLocalCall(root,sourceCallPath,boundArguments);
   try{
    const local=await storage.bindLocalTransaction(selected,child,transaction);current();
    const inspection=storage.inspectLocalTransaction(local),next=selected.inspectInvocation(child),original=selected.inspectInvocation(root);
    if(inspection.root_entry!==outer.entry||inspection.local_call_path!==sourceCallPath||inspection.operation!==targetOperation||inspection.operation!==next.operation||inspection.service!==service||
     next.entry!==original.entry||next.service!==service||next.source_sha256!==sourceSha||original.depth!==0)
     fail('ForeignOwner',where,'bound source transaction must preserve selected root and local call');
    const h=Object.freeze({kind:'original-selected-source-call-storage/v1-candidate' as const});
    active.set(h,{root,child,program:local,inspection:coreFreeze(inspection)});issued.add(h);return h;
   }catch(error){try{selected.retire(child);}catch{}throw error;}
  },
  inspect(h:CommerceSourceCallStorageHandleV1){const state=row(h),root=selected.inspectInvocation(state.root),child=selected.inspectInvocation(state.child),now=storage.inspectLocalTransaction(state.program);
   if(root.depth!==0||root.entry!==now.root_entry||root.service!==service||child.operation!==now.operation||child.parent_call_path!==now.local_call_path||
    now.transaction_path!==state.inspection.transaction_path||now.schema_sha256!==state.inspection.schema_sha256)
    fail('StaleOwner',where,'selected root, child, transaction and store no longer join');
   return state.inspection;
  },
  retire(h:CommerceSourceCallStorageHandleV1){const state=row(h);selected.retire(state.child);active.delete(h);issued.delete(h);},
  assertCurrent:current,
  dispose(){if(disposed)return;for(const h of issued){const state=active.get(h);if(state)try{selected.retire(state.child);}catch{}}issued.clear();disposed=true;},
 });owners.add(owner);current();return owner;
}
