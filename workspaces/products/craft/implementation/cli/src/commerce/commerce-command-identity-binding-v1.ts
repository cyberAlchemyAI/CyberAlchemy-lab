/** Checked profile command identity for one original local source transaction.
 * This owner issues no command, execution frame, store access or dispatch permit.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {types as host} from 'node:util';
import {createHash} from 'node:crypto';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {createCoreValueTypes} from './commerce-core-types.js';
import {createCoreContextCatalog} from './commerce-core-context.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1,type CommerceLocalOperationHandleV1} from './commerce-local-plan-owner-v1.js';
import {assertCommerceBindingAssemblyOwnerV1,type CommerceBindingAssemblyOwnerV1} from './commerce-binding-assembly-v1.js';
import {inspectCommerceTransactionSourceScopeV1} from './commerce-sqlite-transaction-owner-v1.js';
import type {CommerceBindingAssemblyHandle} from './commerce-stages-v1.js';
import type {EntryContractV1,OperationCallV1,RoleSelectorV1,ValueTypeV1,RefinementDefinitionV1,RecordDefinitionV1} from './commerce-data-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-core-source-owner'+ext,'commerce-core-semantic-owner'+ext,'commerce-core-context'+ext,'commerce-computation-domain'+ext,'commerce-local-plan-owner-v1'+ext,'commerce-binding-assembly-v1'+ext,'commerce-sqlite-transaction-owner-v1'+ext]);
export class CommerceCommandIdentityBindingErrorV1 extends Error {constructor(readonly code:string){super(code);this.name='CommerceCommandIdentityBindingErrorV1';}}
const bad=(code:string):never=>{throw new CommerceCommandIdentityBindingErrorV1(code);};
const frozen=<T>(value:T):T=>{if(value&&typeof value==='object'&&!Object.isFrozen(value)){for(const v of Object.values(value))frozen(v);Object.freeze(value);}return value;};
function closed(value:unknown,keys:readonly string[]):asserts value is Record<string,any> {
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))bad('InvalidContract');
 const names=Reflect.ownKeys(value as object),descriptors=Object.getOwnPropertyDescriptors(value as object);
 if(names.length!==keys.length||names.some(name=>typeof name!=='string'||!keys.includes(name))||keys.some(name=>!descriptors[name]?.enumerable||!Object.hasOwn(descriptors[name]!,'value')))bad('InvalidContract');
}
function sourceName(value:unknown):string {if(typeof value!=='string'||value.length>256||! /^[A-Za-z_][A-Za-z0-9_.]*$/.test(value))bad('InvalidContract');return value as string;}
/** Stable declared identity, independent of positional source paths and source
 * capture hashes. The store still rejects a different source or native epoch. */
export function deriveCommerceCommandTransactionNamespaceV1(operation:string,transaction:string):string {
 const selected=sourceName(operation),named=sourceName(transaction);
 if(!selected.includes('.')||named.includes('.'))bad('InvalidContract');
 return createHash('sha256').update(JSON.stringify(['craft.command-transaction-namespace/v1',1,selected,named])).digest('hex');
}
export interface CommerceCommandIdentityProfileRowV1 {
 /** Omission inherits the only source Entry that reaches this Operation. */
 readonly root_entry:string|null;readonly journal_entry:string|null;readonly operation:RoleSelectorV1;readonly transaction:string;
 readonly invocation_kind:'selected-root'|'selected-local-child';
 readonly principal_scope:'authenticated-principal'|'selected-service';readonly command_id_binding:string;readonly fingerprint_binding:string|null;
 readonly claim:'fresh-only';readonly existing:'observe-only-no-dispatch';readonly unresolved:'retain-original-no-reclaim';
}
export interface CommerceCommandIdentityProfileV1 {readonly schema_version:'craft.command-identity-bindings/v1-candidate';readonly bindings:readonly CommerceCommandIdentityProfileRowV1[]}
/** Structural validation is data-only. It cannot issue an original binding. */
export function checkCommerceCommandIdentityProfileShapeV1(value:unknown):CommerceCommandIdentityProfileV1 {
 closed(value,['schema_version','bindings']);if(value.schema_version!=='craft.command-identity-bindings/v1-candidate'||!Array.isArray(value.bindings)||host.isProxy(value.bindings)||Object.getPrototypeOf(value.bindings)!==Array.prototype||value.bindings.length<1||value.bindings.length>32||Reflect.ownKeys(value.bindings).length!==value.bindings.length+1)bad('InvalidContract');
 const seen=new Set<string>();const rows=value.bindings.map((row:unknown,index:number)=>{
  if(!Object.hasOwn(value.bindings,index))bad('InvalidContract');
  if(!row||typeof row!=='object'||host.isProxy(row))bad('InvalidContract');
  const required=['operation','transaction','invocation_kind','principal_scope','command_id_binding','claim','existing','unresolved'];
  closed(row,[...required,...['root_entry','journal_entry','fingerprint_binding'].filter(k=>Object.hasOwn(row as object,k))]);
  closed(row.operation,['module','name','role']);
  const root=Object.hasOwn(row,'root_entry')?sourceName(row.root_entry):null,journal=Object.hasOwn(row,'journal_entry')?sourceName(row.journal_entry):null;
  const module=sourceName(row.operation.module),name=sourceName(row.operation.name),transaction=sourceName(row.transaction),command=sourceName(row.command_id_binding),fingerprint=Object.hasOwn(row,'fingerprint_binding')?sourceName(row.fingerprint_binding):null;
  if(row.operation.role!=='Operation'||!['selected-root','selected-local-child'].includes(row.invocation_kind)||!['authenticated-principal','selected-service'].includes(row.principal_scope)||row.claim!=='fresh-only'||row.existing!=='observe-only-no-dispatch'||row.unresolved!=='retain-original-no-reclaim'||command===fingerprint)bad('InvalidContract');
  if(row.principal_scope==='authenticated-principal'&&journal!==null&&root!==journal)bad('InvalidContract');
  const identity=JSON.stringify([root,module,name,transaction]);if(seen.has(identity))bad('DuplicateSymbol');seen.add(identity);
  return frozen({root_entry:root,journal_entry:journal,operation:frozen({module,name,role:'Operation' as const}),transaction,invocation_kind:row.invocation_kind as CommerceCommandIdentityProfileRowV1['invocation_kind'],principal_scope:row.principal_scope as CommerceCommandIdentityProfileRowV1['principal_scope'],command_id_binding:command,fingerprint_binding:fingerprint,claim:'fresh-only' as const,existing:'observe-only-no-dispatch' as const,unresolved:'retain-original-no-reclaim' as const});
 });
 return frozen({schema_version:'craft.command-identity-bindings/v1-candidate' as const,bindings:rows});
}
/** Pure type check over the original plan's lexical scope; never a key issuer. */
export function checkCommerceCommandIdentityScopeV1(row:CommerceCommandIdentityProfileRowV1,scope:readonly {readonly name:string;readonly type:ValueTypeV1}[],refinements:readonly RefinementDefinitionV1[],records:readonly RecordDefinitionV1[]=[]):Readonly<{command_id_type:ValueTypeV1;fingerprint_type:ValueTypeV1;fingerprint_binding:string}> {
 const vars=new Map(scope.map(v=>[v.name,v.type])),definitions=new Map(refinements.map(r=>[r.name,r])),recordTypes=new Map(records.map(r=>[r.name,r]));
 const resolve=(selector:string):ValueTypeV1=>{
  const parts=selector.split('.');if(parts.length>9||parts.some(p=>!p))bad('InvalidContract');
  let type=vars.get(parts[0]!);if(!type)return bad('UnknownFrameBinding');
  for(const field of parts.slice(1)){
   if(type.kind!=='record')return bad('TypeMismatch');
   const record=recordTypes.get(type.name);if(!record)return bad('UnknownFrameBinding');
   const next=record.fields[field];if(!next)return bad('UnknownFrameBinding');type=next;
  }
  return type;
 };
 const bounds=(type:ValueTypeV1)=>type.kind==='string'?{max:type.max_bytes,min:0,pattern:null}:type.kind==='refinement'?(()=>{const r=definitions.get(type.name);if(!r||r.carrier.kind!=='string')bad('TypeMismatch');return {max:r!.max_utf8_bytes,min:r!.min_utf8_bytes,pattern:r!.pattern};})():bad('TypeMismatch');
 const fingerprintType=(type:ValueTypeV1)=>{if(type.kind!=='refinement')return false;const r=definitions.get(type.name);return !!r&&r.carrier.kind==='string'&&r.min_utf8_bytes===64&&r.max_utf8_bytes===64&&r.pattern==='^[a-f0-9]{64}$';};
 const candidates:string[]=[];
 if(row.fingerprint_binding===null){
  const walk=(selector:string,type:ValueTypeV1,seen:ReadonlySet<string>,depth:number)=>{
   if(fingerprintType(type)){candidates.push(selector);return;}
   if(depth>=8||type.kind!=='record'||seen.has(type.name))return;
   const record=recordTypes.get(type.name);if(!record)return;
   const next=new Set(seen);next.add(type.name);
   for(const [field,child] of Object.entries(record.fields))walk(selector+'.'+field,child,next,depth+1);
  };
  for(const [name,type] of vars)walk(name,type,new Set(),0);
  if(!candidates.length)bad('MissingFingerprint');if(candidates.length!==1)bad('AmbiguousFingerprint');
 }
 const fingerprintBinding=row.fingerprint_binding??candidates[0]!;
 if(row.command_id_binding===fingerprintBinding)bad('InvalidContract');
 const command=resolve(row.command_id_binding),fingerprint=resolve(fingerprintBinding);
 const id=bounds(command!),hash=bounds(fingerprint!);
 if(id.max>256||id.min>256||hash.min!==64||hash.max!==64||hash.pattern!=='^[a-f0-9]{64}$')bad('TypeMismatch');
 return frozen({command_id_type:command!,fingerprint_type:fingerprint!,fingerprint_binding:fingerprintBinding});
}
export interface CommerceCommandIdentityBindingV1 {readonly kind:'original-checked-command-identity-binding/v1-candidate'}
export interface CommerceCommandIdentityBindingInspectionV1 extends CommerceCommandIdentityProfileRowV1 {
 readonly root_entry:string;readonly journal_entry:string;readonly fingerprint_binding:string;
 readonly service:string;readonly transaction_path:string;readonly source_capture_sha256:string;readonly selected_family_sha256:string;
 readonly transaction_namespace_sha256:string;
 readonly operation_plan_sha256:string;readonly profile_path:string;readonly profile_sha256:string;
 readonly command_id_type:ValueTypeV1;readonly fingerprint_type:ValueTypeV1;
 readonly qualification:'original-checked-source-profile-command-identity-only;no-claim-frame-or-effect';readonly authority_effect:'none';
}
export interface CommerceCommandIdentityBindingOwnerV1 {
 bind(rootEntry:string,operation:CommerceLocalOperationHandleV1,transactionPath:string):CommerceCommandIdentityBindingV1;
 inspect(handle:CommerceCommandIdentityBindingV1):CommerceCommandIdentityBindingInspectionV1;
 assertCurrent():void;dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceCommandIdentityBindingOwnerV1(owner:CommerceCommandIdentityBindingOwnerV1):void {if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();}

/** The profile document is reached through the original application parameters
 * reference. An arbitrary JSON object or path cannot mint a binding. */
export function createCommerceCommandIdentityBindingOwnerV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,
 plans:CommerceLocalPlanOwnerV1,assemblies:CommerceBindingAssemblyOwnerV1,assembly:CommerceBindingAssemblyHandle,
):CommerceCommandIdentityBindingOwnerV1 {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);assertCommerceComputationDomainOwner(domain);assertCommerceLocalPlanOwnerV1(plans);assertCommerceBindingAssemblyOwnerV1(assemblies);pin.assertCurrent();semantics.assertSource(semantic,capture);
 const original=sources.inspect(capture),checked=semantics.inspect(semantic),values=domain.inspect(baseline).contract.values,selected=assemblies.inspect(assembly),types=createCoreValueTypes(original.reconstruction);
 if(checked.source_capture_sha256!==original.capture_sha256||selected.selection.source_capture_sha256!==original.capture_sha256||domain.inspect(baseline).source_capture_sha256!==original.capture_sha256)bad('ForeignSource');
 const application=[...types.declarations.values()].find(d=>d.interface_kind==='application-composition')??bad('MissingMapping');
 const profileAsset=createCoreContextCatalog(types,original.files.filter(f=>f.path.endsWith('.json'))).asset(application,['parameters'])??bad('MissingMapping');
 if(profileAsset.doc.schema_version!=='craft.commerce-profile-selection/v1-candidate')bad('MissingMapping');
 const file=original.files.find(f=>f.path===profileAsset.path)??bad('ForeignProfile');
 const profile=checkCommerceCommandIdentityProfileShapeV1(profileAsset.doc.command_identity_bindings);
 const entries=new Map<string,EntryContractV1>(checked.entries.map(e=>[e.id,e]));
 const selectedServices=new Set(selected.selection.services.map(s=>s.id));
 const reachable=(entry:EntryContractV1,target:string,service:string)=>{
  if(entry.invokes.role!=='Operation'||entry.service!==service)return false;
  const queue=[entry.invokes.module+'.'+entry.invokes.name],seen=new Set<string>();
  while(queue.length){if(seen.size>128)bad('SourceBound');const id=queue.shift()!;if(seen.has(id))continue;seen.add(id);
   let plan:ReturnType<typeof plans.inspectOperation>;
   try{plan=plans.inspectOperation(plans.bindOperation(id));}
   catch(error){const diagnostic=(error as {diagnostics?:readonly {code?:string;message?:string}[]})?.diagnostics?.[0];
    if(diagnostic?.code==='UnsupportedCapability'&&diagnostic.message==='native/replay conformance protocols cannot become local invocable plans')continue;
    throw error;}
   if(plan.plan.service!==service)bad('ForeignSource');
   if(id===target)return true;
   const visit=(value:unknown,depth:number)=>{if(depth>128)bad('SourceBound');if(!value||typeof value!=='object')return;if(Array.isArray(value)){for(const v of value)visit(v,depth+1);return;}
    if('target'in value&&'authorization'in value&&'role'in value){const call=value as OperationCallV1;if(call.role==='Operation'&&call.entry===null&&call.authorization==='original-local-context-forwarding-required')queue.push(call.target);}
    for(const v of Object.values(value))visit(v,depth+1);
   };visit(plan.plan.body,0);
  }return false;
 };
 const views=new Map<string,CommerceCommandIdentityBindingInspectionV1>();
 for(const row of profile.bindings){
  const op=plans.bindOperation(row.operation.module+'.'+row.operation.name),view=plans.inspectOperation(op),service=view.plan.service;
  if(!service||!selectedServices.has(service)||view.source_capture_sha256!==original.capture_sha256)bad('ForeignSource');
  const possible=row.root_entry===null?[...entries.values()].filter(e=>e.service===service&&reachable(e,view.operation,service)):[];
  if(row.root_entry===null&&possible.length!==1)bad(possible.length?'AmbiguousEntry':'MissingEntry');
  const rootId=row.root_entry??possible[0]!.id,journalId=row.journal_entry??rootId;
  const root=entries.get(rootId),journal=entries.get(journalId);
  if(!root||!journal)return bad('ForeignEntry');
  if(root.service!==service||journal.service!==service||!reachable(root,view.operation,service)||!reachable(journal,view.operation,service))bad('ForeignEntry');
  if(root.access.principal_kind!==(row.principal_scope==='authenticated-principal'?'customer':'service'))bad('ForeignPrincipal');
  const direct=root!.invokes.role==='Operation'&&root!.invokes.module+'.'+root!.invokes.name===view.operation;
  if(row.invocation_kind==='selected-root'&&!direct||row.invocation_kind==='selected-local-child'&&direct)bad('ForeignEntry');
  const matches=view.transactions.filter(t=>t.plan.name===row.transaction);if(matches.length!==1)bad(matches.length?'DuplicateSymbol':'UnknownReference');
  const transaction=matches[0]!,scope=inspectCommerceTransactionSourceScopeV1(plans,op,transaction.path),bindingTypes=checkCommerceCommandIdentityScopeV1(row,scope,values.refinements,values.records);
  const key=JSON.stringify([rootId,view.operation,transaction.path]);if(views.has(key))bad('DuplicateSymbol');
  views.set(key,frozen({...row,root_entry:rootId,journal_entry:journalId,service:service!,transaction_path:transaction.path,transaction_namespace_sha256:deriveCommerceCommandTransactionNamespaceV1(view.operation,row.transaction),source_capture_sha256:original.capture_sha256,selected_family_sha256:selected.selected_family_sha256,operation_plan_sha256:view.plan_sha256,profile_path:file.path,profile_sha256:file.sha256,...bindingTypes,qualification:'original-checked-source-profile-command-identity-only;no-claim-frame-or-effect' as const,authority_effect:'none' as const}));
 }
 const bindings=new WeakMap<object,CommerceCommandIdentityBindingInspectionV1>();let disposed=false;
 const current=()=>{if(disposed)bad('DisposedOwner');pin.assertCurrent();sources.assertCurrent(capture);semantics.assertSource(semantic,capture);domain.assertCurrent(baseline);plans.assertCurrent();assemblies.assertCurrent(assembly);};
 const owner:CommerceCommandIdentityBindingOwnerV1=Object.freeze({
  bind(rootEntry:string,operation:CommerceLocalOperationHandleV1,transactionPath:string){current();const view=plans.inspectOperation(operation),key=JSON.stringify([rootEntry,view.operation,transactionPath]),found=views.get(key);if(!found||view.plan_sha256!==found.operation_plan_sha256||view.source_capture_sha256!==found.source_capture_sha256)bad('MissingMapping');const h=Object.freeze({kind:'original-checked-command-identity-binding/v1-candidate' as const});bindings.set(h,found!);return h;},
  inspect(h:CommerceCommandIdentityBindingV1){current();const found=h&&typeof h==='object'?bindings.get(h):undefined;if(!found)bad('ForeignOwner');return found!;},
  assertCurrent:current,dispose(){disposed=true;},
 });owners.add(owner);current();return owner;
}
