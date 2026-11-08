/** Checked data projection for a selected root or local command transaction. The scope
 * remains caller data until generated Operation control issues its own scope
 * handle; this module never grants a journal claim or provider effect.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {types as host} from 'node:util';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCommerceCommandIdentityBindingOwnerV1,type CommerceCommandIdentityBindingOwnerV1,type CommerceCommandIdentityBindingV1} from './commerce-command-identity-binding-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1} from './commerce-selected-entry-auth-v1.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1} from './commerce-local-plan-owner-v1.js';
import {assertCommerceSqliteTransactionOwnerV1,type CommerceSqliteTransactionOwnerV1,type CommerceSqliteSourceProgramHandleV1} from './commerce-sqlite-transaction-owner-v1.js';
import type {CommerceOperationInvocationHandle} from './commerce-stages-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-command-identity-binding-v1'+ext,'commerce-selected-entry-auth-v1'+ext,'commerce-local-plan-owner-v1'+ext,'commerce-sqlite-transaction-owner-v1'+ext]);
export class CommerceCommandIdentityProjectionErrorV1 extends Error {constructor(readonly code:string){super(code);this.name='CommerceCommandIdentityProjectionErrorV1';}}
const bad=(code:string):never=>{throw new CommerceCommandIdentityProjectionErrorV1(code);};

/** Data checks only. Custody still comes from the selected original invocation
 * and the generated scope owner at the call site. */
export function checkCommerceCommandPrincipalDataV1(scope:'selected-service'|'authenticated-principal',principal:unknown):string {
 if(!principal||typeof principal!=='object'||host.isProxy(principal)||Array.isArray(principal))bad('ForeignPrincipal');
 const kind=Object.getOwnPropertyDescriptor(principal,'kind'),id=Object.getOwnPropertyDescriptor(principal,'id');
 if(!kind||!Object.hasOwn(kind,'value')||!id||!Object.hasOwn(id,'value')||kind.value!==(scope==='selected-service'?'service':'customer')||typeof id.value!=='string'||!id.value.length)return bad('ForeignPrincipal');
 return id.value as string;
}
export function selectCommerceCheckedScopePathDataV1(copied:Readonly<Record<string,unknown>>,selector:string):unknown {
 if(typeof selector!=='string'||selector.length>256||! /^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*){0,8}$/.test(selector))bad('InputType');
 let value:unknown=copied;
 for(const name of selector.split('.')){
  if(!value||typeof value!=='object'||host.isProxy(value)||Array.isArray(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))bad('InputType');
  const descriptor=Object.getOwnPropertyDescriptor(value,name);
  if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))return bad('InputType');
  value=descriptor.value;
 }
 return value;
}

export interface CommerceCommandIdentityDataProjectionV1 {
 readonly logicalEntryId:string;readonly principalId:string;readonly commandId:string;readonly fingerprint:string;readonly transactionNamespace:string;
 readonly source_capture_sha256:string;readonly selected_family_sha256:string;readonly operation:string;readonly transaction_path:string;
 readonly principal_custody:'original-selected-auth-scope';readonly generated_scope_proven:false;readonly qualification:'checked-selected-command-identity-data-only;generated-scope-and-journal-claim-pending';readonly authority_effect:'none';
}

/** Requires original checked owners, validates every source-scope value through
 * the generated codec, and then projects a key. The raw scope is still untrusted
 * caller data, so this result must not be accepted as a claim or dispatch permit. */
export function projectCommerceCommandIdentityDataV1(
 bindings:CommerceCommandIdentityBindingOwnerV1,binding:CommerceCommandIdentityBindingV1,
 selected:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,
 plans:CommerceLocalPlanOwnerV1,programs:CommerceSqliteTransactionOwnerV1,program:CommerceSqliteSourceProgramHandleV1,
 evaluatedScope:unknown,
):CommerceCommandIdentityDataProjectionV1 {
 pin.assertCurrent();assertCommerceCommandIdentityBindingOwnerV1(bindings);assertCommerceSelectedEntryAuthOwnerV1(selected);
 assertCommerceLocalPlanOwnerV1(plans);assertCommerceSqliteTransactionOwnerV1(programs);
 const b=bindings.inspect(binding),target=b.operation.module+'.'+b.operation.name;
 const invocationView=selected.inspectInvocation(invocation),selection=selected.inspect(),operation=plans.inspectOperation(selected.operation(invocation)),programView=programs.inspect(program);
 if(b.invocation_kind==='selected-root'){
  if(invocationView.depth!==0||invocationView.parent_call_path!==null)bad('ForeignInvocation');
 }else selected.assertSelectedLocalChild(invocation,b.root_entry,target);
 if(invocationView.role!=='Operation'||invocationView.operation!==target||invocationView.entry!==b.root_entry||invocationView.service!==b.service||
  invocationView.source_sha256!==b.source_capture_sha256||selection.source_capture_sha256!==b.source_capture_sha256||
  selection.family_sha256!==b.selected_family_sha256||operation.operation!==target||operation.plan.service!==b.service||
  operation.plan_sha256!==b.operation_plan_sha256||operation.source_capture_sha256!==b.source_capture_sha256||
  programView.operation!==target||programView.service!==b.service||programView.transaction_path!==b.transaction_path||
  programView.source_capture_sha256!==b.source_capture_sha256||programView.family_sha256!==b.selected_family_sha256)
  bad('ForeignBinding');
 const principal=selected.principalIdentity(invocation);
 const principalId=checkCommerceCommandPrincipalDataV1(b.principal_scope,principal);
 const copied=programs.copySourceScope(program,evaluatedScope);
 const commandId=selectCommerceCheckedScopePathDataV1(copied,b.command_id_binding),fingerprint=selectCommerceCheckedScopePathDataV1(copied,b.fingerprint_binding);
 if(typeof commandId!=='string'||!commandId.length||Buffer.byteLength(commandId)>256||Buffer.from(commandId).toString('utf8')!==commandId||
  typeof fingerprint!=='string'||! /^[a-f0-9]{64}$/.test(fingerprint))bad('InputType');
 programs.assertCurrent(program);selected.inspectInvocation(invocation);bindings.inspect(binding);
 return Object.freeze({logicalEntryId:b.journal_entry,principalId,commandId:commandId as string,fingerprint:fingerprint as string,transactionNamespace:b.transaction_namespace_sha256,
  source_capture_sha256:b.source_capture_sha256,selected_family_sha256:b.selected_family_sha256,operation:target,transaction_path:b.transaction_path,
  principal_custody:'original-selected-auth-scope' as const,generated_scope_proven:false as const,qualification:'checked-selected-command-identity-data-only;generated-scope-and-journal-claim-pending' as const,authority_effect:'none' as const});
}
