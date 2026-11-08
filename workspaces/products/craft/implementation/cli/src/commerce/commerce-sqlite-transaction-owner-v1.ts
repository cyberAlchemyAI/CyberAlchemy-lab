/** Original source transaction programs. Frame data is not a complete generated
 * Operation, protected invocation, native context or selected public ABI.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17/CONTEXT.md. */
import path from 'node:path';
import {mkdirSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {types as host} from 'node:util';
import {dataDigest} from '../profile-engine/contracts.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceStageSourceOwner,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1,type CommerceLocalOperationHandleV1,type CommerceLocalTransactionHandleV1} from './commerce-local-plan-owner-v1.js';
import {assertCommerceSqliteFamilyOwnerV1,type CommerceSqliteFamilyOwnerV1,type CommerceRepositoryBundleHandleV1} from './commerce-sqlite-family-v1.js';
import {createCommerceIdentityCallOwner} from './commerce-identity-call-owner.js';
import {createCommerceIdentityComponentOwner,type CommerceIdentityComponentHandle} from './commerce-identity-component.js';
import {assertCommerceEntryContextOwnerV1,type CommerceEntryContextOwnerV1,type CommerceInvocationAuthorizationV1} from './commerce-entry-context-v1.js';
import {isCommerceSourceInvocationOwnerV1,assertCommerceSourceInvocationOwnerV1,type CommerceSourceInvocationOwnerV1} from './commerce-source-invocation-owner-v1.js';
import {isCommerceSelectedEntryAuthOwnerV1,assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1} from './commerce-selected-entry-auth-v1.js';
import type {CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import {COMMERCE_TRANSACTION_DATA_OPERATORS_V1,evaluateCommerceFlowDataV1,CommerceFlowDataErrorV1} from './commerce-flow-expression-data-v1.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {ValueTypeV1,RoleExpressionV1,FlowExprV1,TransactionPlanV1,TransactionStepV1,OperationActionV1,OperationControlStepV1} from './commerce-data-v1.js';
import type {CommerceNativeValue} from './commerce-native-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-flow-expression-data-v1'+ext,'commerce-local-plan-owner-v1'+ext,'commerce-sqlite-family-v1'+ext,'commerce-identity-call-owner'+ext,'commerce-identity-component'+ext,'commerce-entry-context-v1'+ext,'commerce-source-invocation-owner-v1'+ext,'commerce-selected-entry-auth-v1'+ext,'commerce-core-physical'+ext,'../profile-engine/contracts'+ext]);
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){for(const x of Object.values(v))freeze(x);Object.freeze(v);}return v;};
export class CommerceSqliteSourceProgramErrorV1 extends Error {readonly code:string;readonly source_path:string;readonly source_action:OperationActionV1|null;constructor(code:string,p:string,action:OperationActionV1|null=null){super(code);this.name='CommerceSqliteSourceProgramErrorV1';this.code=code;this.source_path=p;this.source_action=action;}}
function bad(code:string,p='$',action:OperationActionV1|null=null):never {throw new CommerceSqliteSourceProgramErrorV1(code,p,action);}
export interface CommerceSqliteSourceProgramHandleV1 {readonly kind:'original-source-sqlite-transaction-program/v1-candidate'}
export type CommerceSqliteProgramAuthorizationV1={readonly owner:CommerceEntryContextOwnerV1;readonly invocation:CommerceInvocationAuthorizationV1}|{readonly owner:CommerceSourceInvocationOwnerV1;readonly invocation:CommerceOperationInvocationHandle}|{readonly owner:CommerceSelectedEntryAuthOwnerV1;readonly invocation:CommerceOperationInvocationHandle};
export type CommerceSqliteSourceInstructionV1={readonly source_path:string;readonly step:
 {readonly kind:'create';readonly entity:string;readonly value:CommerceNativeValue}|
 {readonly kind:'event';readonly entity:string;readonly value:CommerceNativeValue}|
 {readonly kind:'update-key';readonly entity:string;readonly key_index:number;readonly key:CommerceNativeValue;readonly expected_version:bigint;readonly expected_row:CommerceNativeValue;readonly changes:Readonly<Record<string,CommerceNativeValue>>}|
 {readonly kind:'require-absent';readonly entity:string;readonly key_index:number;readonly key:CommerceNativeValue}|
 {readonly kind:'capacity';readonly entity:string;readonly maximum:number}};
export interface CommerceSqliteSourceProgramInspectionV1 {readonly operation:string;readonly transaction_path:string;readonly source_capture_sha256:string;readonly family_sha256:string;readonly schema_sha256:string;readonly service:string;readonly program_sha256:string;readonly plan:TransactionPlanV1;readonly frame:readonly {readonly name:string;readonly type:ValueTypeV1}[];readonly private_context_paths:readonly string[];readonly native_observation_paths:readonly string[];readonly pure_call_paths:readonly string[];readonly qualification:'original-source-transaction-only;outer-operation-frame-and-protected-invocation-not-established';readonly authority_effect:'none'}
export interface CommerceSqliteTransactionOwnerV1 {
 bind(operation:CommerceLocalOperationHandleV1,transaction:CommerceLocalTransactionHandleV1):Promise<CommerceSqliteSourceProgramHandleV1>;
 inspect(program:CommerceSqliteSourceProgramHandleV1):CommerceSqliteSourceProgramInspectionV1;
 /** Data-only validation of the complete generated lexical scope. This does not
  * prove that the values were produced by generated Operation control. */
 copySourceScope(program:CommerceSqliteSourceProgramHandleV1,scope:unknown):Readonly<Record<string,CommerceNativeValue>>;
 execution(program:CommerceSqliteSourceProgramHandleV1,frame:Readonly<Record<string,CommerceNativeValue>>,authorization?:CommerceSqliteProgramAuthorizationV1):Generator<CommerceSqliteSourceInstructionV1,CommerceNativeValue,CommerceNativeValue|undefined>;
 assertCurrent(program:CommerceSqliteSourceProgramHandleV1):void;
}
const owners=new WeakSet<object>();
export function assertCommerceSqliteTransactionOwnerV1(owner:CommerceSqliteTransactionOwnerV1):void {if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');}
/** Typed lexical bindings visible to the generated control at an exact source
 * transaction. This is source inspection, never a frame or effect capability. */
function inspectTransactionSourceScope(plans:CommerceLocalPlanOwnerV1,operation:CommerceLocalOperationHandleV1,transactionPath:string):Readonly<{bindings:readonly {readonly name:string;readonly type:ValueTypeV1}[];reads:readonly string[]}> {
 assertCommerceLocalPlanOwnerV1(plans);const view=plans.inspectOperation(operation);
 if(typeof transactionPath!=='string'||!view.transactions.some(t=>t.path===transactionPath))bad('UnknownSourcePath',transactionPath);
 let found:{scope:Map<string,ValueTypeV1>;reads:Set<string>}|null=null;
 const walk=(body:readonly OperationControlStepV1[],at:string,scope:Map<string,ValueTypeV1>,reads:Set<string>):void=>{
  for(let i=0;i<body.length;i++){
   const step=body[i]!,p=at+'['+i+']';
   if((step.kind==='transaction'||step.kind==='present'&&step.transaction)&&p+'.transaction'===transactionPath){if(found)bad('DuplicateSymbol',p);found={scope:new Map(scope),reads:new Set(reads)};}
   if(step.kind==='let'){scope.set(step.name,step.value.result);reads.delete(step.name);}
   else if(step.kind==='read'||step.kind==='read-set'){
    if(step.kind==='read-set'){const inner=new Map(scope),innerReads=new Set(reads);inner.set(step.item,step.source.result.kind==='list'?step.source.result.element:bad('InvalidSourceType',p));innerReads.delete(step.item);walk(step.body,p+'.body',inner,innerReads);}
    scope.set(step.name,step.type);reads.add(step.name);
   }else if(step.kind==='call'){scope.set(step.name,step.call.result);reads.delete(step.name);}
   else if(step.kind==='count'){scope.set(step.name,step.result);reads.delete(step.name);}
   else if(step.kind==='conditional'){walk(step.then,p+'.then',new Map(scope),new Set(reads));walk(step.otherwise,p+'.otherwise',new Map(scope),new Set(reads));}
  }
 };
 walk(view.plan.body,'$.body',new Map(view.plan.parameters.map(b=>[b.name,b.type])),new Set());
 const result=found as {scope:Map<string,ValueTypeV1>;reads:Set<string>}|null;
 if(!result)bad('UnknownSourcePath',transactionPath);
 return freeze({bindings:[...result!.scope].map(([name,type])=>({name,type})),reads:[...result!.reads]});
}
export function inspectCommerceTransactionSourceScopeV1(plans:CommerceLocalPlanOwnerV1,operation:CommerceLocalOperationHandleV1,transactionPath:string):readonly {readonly name:string;readonly type:ValueTypeV1}[] {
 return inspectTransactionSourceScope(plans,operation,transactionPath).bindings;
}
/** All dispatch/codecs/identity components are constructed from original owners;
 * no caller evaluator, SQL string, JS hook or native-context data override. */
export async function createCommerceSqliteTransactionOwnerV1(sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,plans:CommerceLocalPlanOwnerV1,family:CommerceSqliteFamilyOwnerV1,bundle:CommerceRepositoryBundleHandleV1,identityDirectory:string):Promise<CommerceSqliteTransactionOwnerV1> {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceStageSourceOwner(stage);assertCommerceComputationDomainOwner(domain);assertCommerceLocalPlanOwnerV1(plans);assertCommerceSqliteFamilyOwnerV1(family);pin.assertCurrent();const captureView=sources.inspect(capture),domainView=domain.inspect(baseline),repository=family.inspectBundle(bundle);if(domainView.source_capture_sha256!==captureView.capture_sha256||repository.source_capture_sha256!==captureView.capture_sha256||stage.inspect(source).source_sha256!==captureView.capture_sha256)bad('ForeignOwner');
 const component=await family.loadDataComponent(bundle),model=component.inspect(),module=await import(pathToFileURL(path.join(repository.directory,'values-and-codecs.js')).href);family.assertBundleCurrent(bundle);const codecs=module.createCommerceValueCodecs(),values=domainView.contract.values,records=new Map<string,any>(values.records.map(r=>[r.name,r])),identityCalls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline),identityComponents=createCommerceIdentityComponentOwner(identityCalls,stage,source,domain,baseline);
 if(!path.isAbsolute(identityDirectory)||path.normalize(identityDirectory)!==identityDirectory)bad('InvalidContract');
 type State={op:CommerceLocalOperationHandleV1;tx:CommerceLocalTransactionHandleV1;view:CommerceSqliteSourceProgramInspectionV1;locals:Map<string,any>;sourceRecords:Map<string,any>;pure:Map<string,ReturnType<CommerceLocalPlanOwnerV1['bindPureCall']>>;native:Map<string,ReturnType<typeof identityCalls.bind>>;identity:CommerceIdentityComponentHandle|null;schemas:Map<string,any>;readFrameNames:ReadonlySet<string>};const programs=new WeakMap<object,State>();
 const sourceRecords=new Map<string,any>(model.tables.map((table:any)=>[table.entity,table.record]));
 const current=()=>{pin.assertCurrent();sources.assertCurrent(capture);stage.assertCurrent(source);domain.assertCurrent(baseline);plans.assertCurrent();family.assertBundleCurrent(bundle);};
 const owned=(h:CommerceSqliteSourceProgramHandleV1)=>{current();const s=h&&typeof h==='object'?programs.get(h):undefined;if(!s)bad('ForeignProgram');plans.assertOperationCurrent(s.op);plans.inspectTransaction(s.tx);for(const p of s.pure.values())p.owner.assertCurrent(p.handle);if(s.identity)identityComponents.assertCurrent(s.identity);return s;};
 const schema=(s:State,type:ValueTypeV1)=>{const key=dataDigest(type),old=s.schemas.get(key);if(old)return old;const result=codecs.checkCommerceSchema({...values,root:type});if(!result.ok)bad('InvalidSourceType');s.schemas.set(key,result.value);return result.value;};
 const copy=(s:State,type:ValueTypeV1,value:any,p:string)=>{
  let nodes=0,bytes=0;
  const hasLocal=(t:ValueTypeV1):boolean=>t.kind==='record'?s.locals.has(t.name)||s.sourceRecords.has(t.name):t.kind==='list'||t.kind==='optional'?hasLocal(t.element):false;
  const measure=(v:any,at:string)=>{bytes+=Buffer.byteLength(JSON.stringify(v,(_k,x)=>typeof x==='bigint'?String(x):x));if(bytes>domainView.contract.limits.max_value_bytes)bad('InputBound',at);};
  const closed=(v:any,keys:string[],at:string)=>{if(!v||typeof v!=='object'||host.isProxy(v)||Array.isArray(v)||![Object.prototype,null].includes(Object.getPrototypeOf(v))||Reflect.ownKeys(v).length!==keys.length)bad('InputType',at);for(const name of keys){const d=Object.getOwnPropertyDescriptor(v,name);if(!d?.enumerable||!Object.hasOwn(d,'value'))bad('InputType',at);}};
  const visit=(t:ValueTypeV1,v:any,at:string,depth:number):any=>{if(++nodes>65536||depth>32)bad('InputBound',at);
   if(!hasLocal(t)){const result=codecs.copyCommerceValue(schema(s,t),v);if(!result.ok)bad('InputType',at);measure(result.value,at);return result.value;}
   if(t.kind==='record'){const fields=(s.locals.get(t.name)??s.sourceRecords.get(t.name)).fields,names=Object.keys(fields);closed(v,names,at);bytes+=2+names.reduce((n,k)=>n+Buffer.byteLength(JSON.stringify(k))+2,0);const out=Object.create(null);for(const [name,field]of Object.entries(fields))out[name]=visit(field as ValueTypeV1,v[name],at+'.'+name,depth+1);if(bytes>domainView.contract.limits.max_value_bytes)bad('InputBound',at);return freeze(out);}
   if(t.kind==='list'){if(!Array.isArray(v)||host.isProxy(v)||Object.getPrototypeOf(v)!==Array.prototype||v.length<t.min_items||v.length>t.max_items||v.length>domainView.contract.limits.max_items||Reflect.ownKeys(v).length!==v.length+1)bad('InputType',at);bytes+=2+v.length;const out:any[]=[];for(let i=0;i<v.length;i++){const d=Object.getOwnPropertyDescriptor(v,String(i));if(!d?.enumerable||!Object.hasOwn(d,'value'))bad('InputType',at);out.push(visit(t.element,d.value,at+'['+i+']',depth+1));}return freeze(out);}
   if(t.kind==='optional'){const d=v&&typeof v==='object'&&!host.isProxy(v)?Object.getOwnPropertyDescriptor(v,'kind'):undefined,none=d&&Object.hasOwn(d,'value')&&d.value==='none';closed(v,none?['kind']:['kind','value'],at);if(none){measure({kind:'none'},at);return freeze({kind:'none'});}if(v.kind!=='some')bad('InputType',at);bytes+=24;return freeze({kind:'some',value:visit(t.element,v.value,at+'.value',depth+1)});}
   return bad('InvalidSourceType',at);
  };return visit(type,value,p,0);
 };
 const selectedAuthorization=(selected:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,s:State,p:string)=>{
  assertCommerceSelectedEntryAuthOwnerV1(selected);
  const view=selected.inspectInvocation(invocation),selection=selected.inspect();
  const root=view.depth===0&&view.parent_call_path===null;
  const local=view.depth>=1&&view.parent_call_path!==null;
  if(view.role!=='Operation'||(!root&&!local)||view.operation!==s.view.operation||view.service!==s.view.service||
   view.source_sha256!==s.view.source_capture_sha256||selection.source_capture_sha256!==s.view.source_capture_sha256||selection.family_sha256!==s.view.family_sha256)
   bad('ForeignInvocation',p);
  if(local)selected.assertSelectedLocalChild(invocation,view.entry,s.view.operation);
  const checked=plans.inspectOperation(selected.operation(invocation)),bound=plans.inspectOperation(s.op);
  if(checked.operation!==bound.operation||checked.plan.service!==s.view.service||checked.plan_sha256!==bound.plan_sha256)
   bad('ForeignInvocation',p);
 };
 const owner:CommerceSqliteTransactionOwnerV1=Object.freeze({
  async bind(op:CommerceLocalOperationHandleV1,tx:CommerceLocalTransactionHandleV1){current();const operation=plans.inspectOperation(op),transaction=plans.inspectTransaction(tx);if(operation.source_capture_sha256!==repository.source_capture_sha256||operation.plan.service!==repository.service||!operation.transactions.some(t=>t.path===transaction.path&&dataDigest(t)===dataDigest(transaction)))bad('ForeignProgram');if(transaction.plan.participants.some(e=>!model.tables.some((t:any)=>t.entity===e)))bad('ForeignServiceScope');
   const sourceScope=inspectTransactionSourceScope(plans,op,transaction.path),env=new Map(sourceScope.bindings.map(b=>[b.name,b.type])),updatedEntities=new Set<string>();
   const locals=new Map<string,any>(),free=new Map<string,ValueTypeV1>(),pure=new Map<string,ReturnType<CommerceLocalPlanOwnerV1['bindPureCall']>>(),native=new Map<string,ReturnType<typeof identityCalls.bind>>(),contexts:string[]=[];
   const expr=(e:any,p:string,bound:Map<string,ValueTypeV1>)=>{if(!COMMERCE_TRANSACTION_DATA_OPERATORS_V1.includes(e.op))bad('UnsupportedCapability',p);if(e.op==='binary'&&!['eq','and','or','lt','lte','gt','gte','add','subtract','multiply'].includes(e.operator))bad('UnsupportedCapability',p);if(e.op==='var'&&!bound.has(e.name)){const type=env.get(e.name);if(!type)bad('UnknownFrameBinding',p);free.set(e.name,type);}if(e.op==='private_context')contexts.push(p);if(e.op==='call')pure.set(p,plans.bindPureCall(op,p));if(e.op==='native_observation'){if(e.abi!=='craft.commerce-identity/v1-candidate')bad('UnsupportedNativeProducer',p);native.set(p,identityCalls.bind(operation.plan,p));}
    const visit=(value:any,path:string,scope=bound)=>{if(!value||typeof value!=='object')return;if(Array.isArray(value)){value.forEach((v,i)=>visit(v,path+'['+i+']',scope));return;}if(value.op){expr(value,path,scope);return;}for(const [key,x]of Object.entries(value))visit(x,path+'.'+key,scope);};
    if(e.op==='let'){visit(e.value,p+'.value');const inner=new Map(bound);inner.set(e.binding.name,e.binding.type);visit(e.body,p+'.body',inner);}else for(const [key,x]of Object.entries(e))if(key!=='op'&&key!=='type'&&key!=='result'&&key!=='fields'||key==='fields'&&e.op!=='private_context')visit(x,p+'.'+key);
   };
   const role=(r:RoleExpressionV1,p:string,bound:Map<string,ValueTypeV1>)=>{for(const local of r.local_records){const old=locals.get(local.name);if(old&&dataDigest(old)!==dataDigest(local))bad('InvalidSourceType',p);locals.set(local.name,local);}expr(r.expression,p+'.expression',bound);};
   const body=(steps:readonly TransactionStepV1[],p:string,scope:Map<string,ValueTypeV1>)=>{steps.forEach((step,i)=>{const at=p+'['+i+']';if(step.kind==='mutation'){if(step.operation==='update')updatedEntities.add(step.target);if(step.key)step.key.values.forEach((v,j)=>role(v.value,at+'.key.values['+j+'].value',scope));if(step.expected_version)role(step.expected_version,at+'.expected_version',scope);step.fields.forEach((f,j)=>role(f.value,at+'.fields['+j+'].value',scope));scope.set(step.binding,{kind:'record',name:step.target});}else if(step.kind==='let'){role(step.value,at+'.value',scope);scope.set(step.name,step.value.result);}else if(step.kind==='guard')role(step.condition,at+'.condition',scope);else if(step.kind==='require-absent')step.key.values.forEach((v,j)=>role(v.value,at+'.key.values['+j+'].value',scope));else if(step.kind==='for'){role(step.source,at+'.source',scope);if(step.source.result.kind!=='list')bad('InvalidSourceType',at);body(step.body,at+'.body',new Map([...scope,[step.item,step.source.result.element] as const]));}else if(step.kind==='conditional'){role(step.condition,at+'.condition',scope);body(step.then,at+'.then',new Map(scope));body(step.otherwise,at+'.otherwise',new Map(scope));}});};body(transaction.plan.body,transaction.path+'.body',new Map());
   // A derived next-state record is not the original row observed by a read.
   // Keep relevant original reads in the native frame even when transaction
   // field expressions mention only a Mapping's calculated replacement.
   const containsUpdatedRow=(type:ValueTypeV1,seen=new Set<string>()):boolean=>{
    if(type.kind==='optional'||type.kind==='list')return containsUpdatedRow(type.element,seen);
    if(type.kind!=='record')return false;
    if(updatedEntities.has(type.name))return true;
    if(seen.has(type.name))return false;
    const record=records.get(type.name)??locals.get(type.name)??sourceRecords.get(type.name);
    if(!record)return false;
    const next=new Set(seen);next.add(type.name);
    return Object.values(record.fields).some(field=>containsUpdatedRow(field as ValueTypeV1,next));
   };
   const readFrameNames=new Set(sourceScope.reads.filter(name=>containsUpdatedRow(env.get(name)!)));
   for(const name of readFrameNames)free.set(name,env.get(name)!);
   let identity:CommerceIdentityComponentHandle|null=null;if(native.size){const directory=path.join(identityDirectory,dataDigest({operation:operation.operation,path:transaction.path}));mkdirSync(directory,{mode:0o700});identity=await identityComponents.materialize([...native.values()],directory);}
   const view:CommerceSqliteSourceProgramInspectionV1=freeze({operation:operation.operation,transaction_path:transaction.path,source_capture_sha256:operation.source_capture_sha256,family_sha256:repository.family_sha256,schema_sha256:repository.schema_sha256,service:repository.service,program_sha256:dataDigest({source:operation.source_capture_sha256,path:transaction.path,plan:transaction.plan,frame:[...free],original_reads:[...readFrameNames]}),plan:transaction.plan,frame:[...free].map(([name,type])=>({name,type})),private_context_paths:contexts,native_observation_paths:[...native.keys()],pure_call_paths:[...pure.keys()],qualification:'original-source-transaction-only;outer-operation-frame-and-protected-invocation-not-established',authority_effect:'none'}),h=Object.freeze({kind:'original-source-sqlite-transaction-program/v1-candidate' as const});programs.set(h,{op,tx,view,locals,sourceRecords,pure,native,identity,schemas:new Map(),readFrameNames});owned(h);return h;
  },
  inspect(h:CommerceSqliteSourceProgramHandleV1){return owned(h).view;},assertCurrent(h:CommerceSqliteSourceProgramHandleV1){owned(h);},
  copySourceScope(h:CommerceSqliteSourceProgramHandleV1,scope:unknown){
   const s=owned(h),bindings=inspectCommerceTransactionSourceScopeV1(plans,s.op,s.view.transaction_path),names=bindings.map(b=>b.name);
   if(!scope||typeof scope!=='object'||Array.isArray(scope)||host.isProxy(scope)||![Object.prototype,null].includes(Object.getPrototypeOf(scope))||Reflect.ownKeys(scope).length!==names.length)bad('InputType',s.view.transaction_path);
   const out:Record<string,CommerceNativeValue>=Object.create(null);
   for(const binding of bindings){const descriptor=Object.getOwnPropertyDescriptor(scope,binding.name);if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('InputType',s.view.transaction_path+'.'+binding.name);out[binding.name]=copy(s,binding.type,descriptor.value,s.view.transaction_path+'.'+binding.name);}
   owned(h);return freeze(out);
  },
  *execution(h:CommerceSqliteSourceProgramHandleV1,frame:Readonly<Record<string,CommerceNativeValue>>,authorization?:CommerceSqliteProgramAuthorizationV1):Generator<CommerceSqliteSourceInstructionV1,CommerceNativeValue,CommerceNativeValue|undefined>{
   if(authorization){if(host.isProxy(authorization)||Reflect.ownKeys(authorization).length!==2||!['owner','invocation'].every(name=>{const d=Object.getOwnPropertyDescriptor(authorization,name);return d?.enumerable&&Object.hasOwn(d,'value');}))bad('InputType');}const s=owned(h);if(authorization){if(isCommerceSelectedEntryAuthOwnerV1(authorization.owner)){selectedAuthorization(authorization.owner,authorization.invocation as CommerceOperationInvocationHandle,s,'$');}else if(isCommerceSourceInvocationOwnerV1(authorization.owner)){assertCommerceSourceInvocationOwnerV1(authorization.owner);authorization.owner.assertTarget(authorization.invocation as CommerceOperationInvocationHandle,plans,s.view.source_capture_sha256,s.view.operation);}else{assertCommerceEntryContextOwnerV1(authorization.owner);const v=authorization.owner.inspectInvocation(authorization.invocation as CommerceInvocationAuthorizationV1);if(v.operation!==s.view.operation||v.source_sha256!==s.view.source_capture_sha256)bad('ForeignInvocation');}}const env:any=Object.create(null),types=new Map(s.view.frame.map(b=>[b.name,b.type])),keys=s.view.frame.map(b=>b.name);if(!frame||typeof frame!=='object'||Array.isArray(frame)||host.isProxy(frame)||![Object.prototype,null].includes(Object.getPrototypeOf(frame))||Reflect.ownKeys(frame).length!==keys.length)bad('InputType');for(const name of keys){const d=Object.getOwnPropertyDescriptor(frame,name);if(!d?.enumerable||!Object.hasOwn(d,'value'))bad('InputType');env[name]=copy(s,types.get(name)!,d.value,'$.frame.'+name);}
   let fuel=0,iterations=0;const charge=(p:string)=>{if(++fuel>domainView.contract.limits.fuel)bad('ResourceLimit',p);};
   const evaluate=(r:RoleExpressionV1,p:string,scope:any)=>{try{const value=evaluateCommerceFlowDataV1(r.expression,p+'.expression',scope,{charge,isNullaryEnum(name){return values.enums.find(e=>e.name===name)!.variants.every(v=>Object.keys(v.fields).length===0);},pure(at,args){const call=s.pure.get(at);if(!call)bad('ForeignCallsite',at);const view=call.owner.inspect(call.handle),input:any=Object.create(null);view.callee.parameters.forEach((b,i)=>{input[b.name]=args[i];});const encoded=codecs.encodeComputationParameters(codecs.schemaForCallableArguments(view.callee.declaration),input);if(!encoded.ok)bad('InputType',at);const result=call.owner.evaluateBoundParameters(call.handle,encoded.value);if(!result.observation.result.ok)bad('CalculationFailed',at);const decoded=codecs.decodeComputationValue(schema(s,view.callee.result),result.observation.result.wire);if(!decoded.ok)bad('CalculationFailed',at);return decoded.value;},native(at,args){const call=s.native.get(at);if(!call||!s.identity)bad('NativeCustodyRequired',at);const result=identityComponents.evaluateBoundParameters(s.identity,call,args);if(!result.ok)bad('NativeProducerRejected',at);return result.value;},context(at){if(!authorization)bad('NativeContextCustodyRequired',at);if(isCommerceSelectedEntryAuthOwnerV1(authorization.owner)){
    // execution() checked the exact selected Operation before this synchronous
    // source program began. The selected context method rechecks the live
    // invocation and source path, so repeating the whole authorization join
    // for each field of the same transaction adds no custody evidence.
    return authorization.owner.context(authorization.invocation as CommerceOperationInvocationHandle,at);
   }if(isCommerceSourceInvocationOwnerV1(authorization.owner)){assertCommerceSourceInvocationOwnerV1(authorization.owner);const original=authorization.invocation as CommerceOperationInvocationHandle;authorization.owner.assertTarget(original,plans,s.view.source_capture_sha256,s.view.operation);return authorization.owner.context(original,at);}assertCommerceEntryContextOwnerV1(authorization.owner);const invocation=authorization.owner.inspectInvocation(authorization.invocation as CommerceInvocationAuthorizationV1);if(invocation.operation!==s.view.operation||invocation.source_sha256!==s.view.source_capture_sha256)bad('ForeignInvocation',at);const principal=authorization.owner.inspectScope(authorization.owner.principalScope(authorization.invocation as CommerceInvocationAuthorizationV1));const original:any=at.match(/[^.[\]]+/g)!.slice(1).reduce((value:any,key:string)=>value[key],plans.inspectOperation(s.op).plan);if(original.source_type!=='Shop.Values.CustomerContext'&&original.source_type!=='Shop.Values.ServiceContext'||principal.kind!==(original.source_type==='Shop.Values.CustomerContext'?'customer':'service'))bad('NativeContextCustodyRequired',at);const out=Object.create(null);for(const name of Object.keys(original.fields))out[name]=principal[name];return out;}});return copy(s,r.result,value,p);}catch(error){if(error instanceof CommerceFlowDataErrorV1)bad(error.code,error.source_path);throw error;}};
   const aliases:any=Object.create(null),canonical=(value:any)=>JSON.stringify(value,(_k,v)=>typeof v==='bigint'?String(v):v);
   const original=(entity:string,key:any,scope:any,bindings:Map<string,ValueTypeV1>,p:string)=>{const found:any[]=[];const visit=(value:any,type:ValueTypeV1,depth:number)=>{charge(p);if(depth>32)bad('ResourceLimit',p);if(type.kind==='record'){if(type.name===entity&&Object.keys(key).every(k=>canonical(value[k])===canonical(key[k])))found.push(value);const record=records.get(type.name)??s.locals.get(type.name);for(const [name,t]of Object.entries(record.fields))visit(value[name],t as ValueTypeV1,depth+1);}else if(type.kind==='optional'&&value.kind==='some')visit(value.value,type.element,depth+1);else if(type.kind==='list')value.forEach((v:any)=>visit(v,type.element,depth+1));};// Prefer exact source-read provenance. If this target has no matching
    // observed read, retain the existing parameter/call-return component path.
    for(const [name,type]of bindings)if(s.readFrameNames.has(name)&&Object.hasOwn(scope,name))visit(scope[name],type,0);
    if(!found.length)for(const [name,type]of bindings)if(Object.hasOwn(scope,name))visit(scope[name],type,0);
    if(!found.length||found.some(v=>canonical(v)!==canonical(found[0])))bad('OriginalRowRequired',p);return found[0];};
   const walk=function*(steps:readonly TransactionStepV1[],p:string,scope:any,bindings:Map<string,ValueTypeV1>):Generator<CommerceSqliteSourceInstructionV1,void,CommerceNativeValue|undefined>{for(let i=0;i<steps.length;i++){const step=steps[i]!,at=p+'['+i+']';charge(at);if(step.kind==='mutation'){const fields:any=Object.create(null);for(let j=0;j<step.fields.length;j++){const field=step.fields[j]!;fields[field.name]=evaluate(field.value,at+'.fields['+j+'].value',scope);}let instruction:CommerceSqliteSourceInstructionV1['step'];if(step.operation==='update'){const key=Object.fromEntries(step.key!.values.map((v,j)=>[v.field,evaluate(v.value,at+'.key.values['+j+'].value',scope)])),table=model.tables.find((t:any)=>t.entity===step.target),index=table.keys.findIndex((k:string[])=>dataDigest(k)===dataDigest(step.key!.key));if(index<0)bad('InvalidSourceKey',at);instruction={kind:'update-key',entity:step.target,key_index:index,key,expected_version:evaluate(step.expected_version!,at+'.expected_version',scope),expected_row:original(step.target,key,scope,bindings,at),changes:fields};}else instruction={kind:step.operation==='record-event'?'event':'create',entity:step.target,value:copy(s,{kind:'record',name:step.target},fields,at)};const row=yield freeze({source_path:at,step:instruction});if(row===undefined)bad('MissingNativeRow',at);scope[step.binding]=copy(s,{kind:'record',name:step.target},row,at);bindings.set(step.binding,{kind:'record',name:step.target});if(p===s.view.transaction_path+'.body')aliases[step.binding]=scope[step.binding];}
     else if(step.kind==='let'){try{scope[step.name]=evaluate(step.value,at+'.value',scope);bindings.set(step.name,step.value.result);if(p===s.view.transaction_path+'.body')aliases[step.name]=scope[step.name];}catch(e){if(e instanceof CommerceSqliteSourceProgramErrorV1)bad(e.code,e.source_path,step.on_error);throw e;}}
     else if(step.kind==='guard'){if(evaluate(step.condition,at+'.condition',scope)!==true)bad('SourceGuardFalse',at,step.on_false);}
     else if(step.kind==='for'){const items=evaluate(step.source,at+'.source',scope);if(step.source.result.kind!=='list')bad('InvalidSourceType',at);for(const item of items){if(++iterations>domainView.contract.limits.max_iterations)bad('IterationBound',at);yield*walk(step.body,at+'.body',Object.assign(Object.create(null),scope,{[step.item]:item}),new Map([...bindings,[step.item,step.source.result.element] as const]));}}
     else if(step.kind==='conditional'){const yes=evaluate(step.condition,at+'.condition',scope);yield*walk(yes?step.then:step.otherwise,at+(yes?'.then':'.otherwise'),Object.assign(Object.create(null),scope),new Map(bindings));}
     else if(step.kind==='capacity'){yield freeze({source_path:at,step:{kind:'capacity',entity:step.entity,maximum:step.maximum}});}
     else{const key=Object.fromEntries(step.key.values.map((v,j)=>[v.field,evaluate(v.value,at+'.key.values['+j+'].value',scope)])),table=model.tables.find((t:any)=>t.entity===step.entity),index=table.keys.findIndex((k:string[])=>dataDigest(k)===dataDigest(step.key.key));if(index<0)bad('InvalidSourceKey',at);yield freeze({source_path:at,step:{kind:'require-absent',entity:step.entity,key_index:index,key}});}
    }};yield*walk(s.view.plan.body,s.view.transaction_path+'.body',env,types);owned(h);return freeze(aliases);
  },
 });owners.add(owner);current();return owner;
}
