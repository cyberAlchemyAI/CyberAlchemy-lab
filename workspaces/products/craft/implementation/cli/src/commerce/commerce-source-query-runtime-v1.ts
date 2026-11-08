/** Checked local Query execution over the original selected service store.
 * Private WorkerContext and CustomerContext reads require their corresponding
 * original selected invocation; callers cannot supply context values.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {isDeepStrictEqual,types as host} from 'node:util';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {evaluateCommerceFlowDataV1,COMMERCE_TRANSACTION_DATA_OPERATORS_V1} from './commerce-flow-expression-data-v1.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1,type CommerceLocalReadHandleV1} from './commerce-local-plan-owner-v1.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1} from './commerce-service-storage-v1.js';
import {assertCoreCommerceStageSourceOwner,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {assertCommerceSourceQueryOutputCodecV1,type CommerceSourceQueryOutputCodecV1} from './commerce-source-query-output-codec-v1.js';
import {CommerceSelectedScopedResourceNotFoundV1,type CommerceSelectedEntryAuthOwnerV1} from './commerce-selected-entry-auth-v1.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import type {FlowExprV1,ExprV1,ReadPlanV1} from './commerce-data-v1.js';
import type {CommerceNativeValue} from './commerce-native-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-flow-expression-data-v1'+ext,'commerce-local-plan-owner-v1'+ext,'commerce-computation-domain'+ext,'commerce-service-storage-v1'+ext,'commerce-core-stage-owner'+ext,'commerce-source-query-output-codec-v1'+ext,'commerce-selected-entry-auth-v1'+ext]);
export class CommerceSourceQueryErrorV1 extends Error {constructor(readonly code:string){super(code);this.name='CommerceSourceQueryErrorV1';}}
const bad=(code:string):never=>{throw new CommerceSourceQueryErrorV1(code);};
const frozen=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){for(const x of Object.values(v))frozen(x);Object.freeze(v);}return v;};
const closed=(v:unknown,keys:readonly string[])=>{if(!v||typeof v!=='object'||Array.isArray(v)||host.isProxy(v as object)||![Object.prototype,null].includes(Object.getPrototypeOf(v)))bad('InputType');const subject=v as object,names=Reflect.ownKeys(subject),ds=Object.getOwnPropertyDescriptors(subject);if(names.length!==keys.length||names.some(k=>typeof k!=='string'||!keys.includes(k))||keys.some(k=>!ds[k]?.enumerable||!Object.hasOwn(ds[k]!,'value')))bad('InputType');};
type QueryQualification='source-selected-internal-query-result;entry-and-worker-custody-separate'|'source-selected-worker-query-result;original-entry-and-worker-custody'|'source-selected-customer-query-result;original-entry-and-resource-custody'|'source-selected-service-query-result;original-entry-and-causal-resource-custody';
export type CommerceSourceQueryResultV1={readonly kind:'returned';readonly value:CommerceNativeValue;readonly qualification:QueryQualification}|{readonly kind:'rejected'|'failed';readonly code:string;readonly qualification:QueryQualification};
export interface CommerceSourceQueryRowWitnessV1 {readonly kind:'original-selected-source-query-row/v1-candidate'}
export interface CommerceSourceQueryRuntimeV1 {readonly query:string;execute(parameters:Readonly<Record<string,CommerceNativeValue>>):CommerceSourceQueryResultV1;executeWorker(selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle):CommerceSourceQueryResultV1;selectedEntryMode(entryId:string):'scoped-row'|'causal-service';executeSelectedService(selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle):CommerceSourceQueryResultV1;select(selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle):CommerceSourceQueryRowWitnessV1;releaseSelected(witness:CommerceSourceQueryRowWitnessV1,selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle):CommerceSourceQueryResultV1;assertCurrent():void;dispose():void;}
const owners=new WeakSet<object>();
export function assertCommerceSourceQueryRuntimeV1(owner:CommerceSourceQueryRuntimeV1):void {if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();}
/** This owner has no public context-constructor or untrusted predicate/SQL port.
 * Queries with private contexts cannot execute until an original native owner
 * supplies the checked context join. */
export function createCommerceSourceQueryRuntimeV1(stage:CoreCommerceStageSourceOwner,stageSource:CommerceSourceHandle,plans:CommerceLocalPlanOwnerV1,read:CommerceLocalReadHandleV1,domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,storage:CommerceServiceStorageOwnerV1,codec:CommerceSourceQueryOutputCodecV1):CommerceSourceQueryRuntimeV1 {
 assertCoreCommerceStageSourceOwner(stage);assertCommerceLocalPlanOwnerV1(plans);assertCommerceComputationDomainOwner(domain);assertCommerceServiceStorageOwnerV1(storage);assertCommerceSourceQueryOutputCodecV1(codec);pin.assertCurrent();stage.assertCurrent(stageSource);
 const view=plans.inspectRead(read),plan=view.plan,source=domain.inspect(baseline),store=storage.inspect();
 if(plan.kind!=='local'||plan.service!==store.service||view.source_capture_sha256!==source.source_capture_sha256||store.source_capture_sha256!==view.source_capture_sha256||stage.inspect(stageSource).source_sha256!==view.source_capture_sha256||codec.query!==view.query||codec.source_capture_sha256!==view.source_capture_sha256||codec.plan_sha256!==view.plan_sha256)bad('ForeignOwner');
 const scopedEntries=stage.moduleContracts(stageSource).flatMap(module=>module.entries).filter(entry=>entry.invokes.module+'.'+entry.invokes.name===view.query&&entry.access.resource_phase==='scoped-read-before-response'&&entry.access.resource_bindings.some(binding=>binding.origin.kind==='scoped-query-row'));
 if(scopedEntries.length>1)bad('AmbiguousScopedEntry');
 const scopedEntry=scopedEntries[0];
 const scopedBinding=scopedEntry?.access.resource_bindings.find(binding=>binding.origin.kind==='scoped-query-row');
 const scopedType=scopedBinding?.type,scopedRecord=scopedType?.kind==='data'&&scopedType.type.kind==='record'?scopedType.type.name:null;
 if(scopedEntry&&(!scopedBinding||scopedBinding.origin.declaration!==view.query||!scopedBinding.origin.binding||!scopedRecord||plan.kind!=='local'||!plan.sources.some(row=>row.binding===scopedBinding.origin.binding&&row.entity===scopedRecord)))bad('InvalidScopedBinding');
 const workerEntries=stage.moduleContracts(stageSource).flatMap(module=>module.entries).filter(entry=>
  entry.invokes.role==='Query'&&entry.invokes.module+'.'+entry.invokes.name===view.query&&
  entry.access.worker_lifetime==='requires-original-local-worker-owner');
 const serviceEntries=stage.moduleContracts(stageSource).flatMap(module=>module.entries).filter(entry=>
  entry.invokes.role==='Query'&&entry.invokes.module+'.'+entry.invokes.name===view.query&&
  entry.service===store.service&&entry.access.principal_kind==='service'&&
  entry.access.worker_lifetime==='not-applicable'&&entry.access.resource_phase==='causal-before-invocation'&&
  entry.access.resource_bindings.length===1&&entry.access.resource_bindings[0]!.origin.kind==='workflow-journal'&&
  entry.access.resource_condition!==null);
 const functions=new Map(source.contract.functions.map(f=>[f.name,f]));
 let nodes=0;const calls=new Map<string,string>(),scanned=new Set<string>(),active=new Set<string>();
 const scan=(e:FlowExprV1|ExprV1,p:string)=>{if(++nodes>65536||p.length>8192)bad('QueryBound');if(e.op==='native_observation'||e.op==='private_context'){if(p.startsWith('$pure.'))bad('UnsupportedQueryExpression');return;}if(!COMMERCE_TRANSACTION_DATA_OPERATORS_V1.includes(e.op))bad('UnsupportedQueryExpression');
  if(e.op==='call'){const f=functions.get(e.declaration);if(!f)throw new CommerceSourceQueryErrorV1('UnknownReference');calls.set(p,e.declaration);if(active.has(f.name))bad('RecursiveQueryCall');if(!scanned.has(f.name)){active.add(f.name);scan(f.body,'$pure.'+f.name+'.body');active.delete(f.name);scanned.add(f.name);}}
  for(const [key,value]of Object.entries(e)){if(key==='type'||key==='result')continue;if(Array.isArray(value))value.forEach((item,i)=>{if(item&&typeof item==='object'&&'op'in item)scan(item as FlowExprV1,p+'.'+key+'['+i+']');});else if(value&&typeof value==='object'&&'op'in value)scan(value as FlowExprV1,p+'.'+key);else if(key==='fields'&&value&&typeof value==='object')for(const [name,item]of Object.entries(value))if(item&&typeof item==='object'&&'op'in item)scan(item as FlowExprV1,p+'.fields.'+name);}
 };
 const local=plan as Extract<ReadPlanV1,{kind:'local'}>;
 // SQLite slots are derived copies of source expressions. Private context
 // acquisition must use the expression's original Query path, since the
 // invocation owner rejects synthetic slot paths such as $.slots.s0.
 const sourceSlotPath=(expression:FlowExprV1):string=>{
  const matches:string[]=[];let visited=0;
  const walk=(value:unknown,at:string,depth:number):void=>{
   if(!value||typeof value!=='object')return;
   if(++visited>65536||depth>128||at.length>8192)bad('QueryBound');
   if(isDeepStrictEqual(value,expression))matches.push(at);
   if(Array.isArray(value))value.forEach((item,index)=>walk(item,at+'['+index+']',depth+1));
   else for(const [key,item] of Object.entries(value))walk(item,at+'.'+key,depth+1);
  };
  for(const [index,source] of local.sources.entries())if(source.join)walk(source.join.expression,'$.sources['+index+'].join.expression',0);
  walk(local.predicate.expression,'$.predicate.expression',0);
  if(!matches.length)bad('ForeignSourceSlot');
  return matches.sort()[0]!;
 };
 for(const [i,s]of local.sources.entries())if(s.join)scan(s.join.expression,'$.sources['+i+'].join.expression');
 scan(local.predicate.expression,'$.predicate.expression');scan(local.projection.expression,'$.projection.expression');
 for(const [i,g]of local.guards.entries())scan(g.condition.expression,'$.guards['+i+'].condition.expression');
 for(const a of [local.on_missing,local.on_unavailable])if(a.kind==='return')scan(a.value.expression,a===local.on_missing?'$.on_missing.value.expression':'$.on_unavailable.value.expression');
 const paramNames=local.parameters.map(p=>p.name),hasPrivate=local.contexts.length>0,
  workerContext=hasPrivate&&local.contexts.length===1&&local.contexts[0]!.source_type==='Shop.Values.WorkerContext'&&
   local.contexts[0]!.abi==='craft.commerce-worker-context/v1-candidate'&&workerEntries.length===1&&
   workerEntries[0]!.access.resource_phase==='causal-before-invocation'&&
   workerEntries[0]!.access.principal_kind==='service'&&workerEntries[0]!.service===store.service;
 type ContextSelection={readonly auth:CommerceSelectedEntryAuthOwnerV1;readonly invocation:CommerceOperationInvocationHandle;readonly kind:'worker'|'customer'};
 let disposed=false;
 const current=()=>{if(disposed)bad('DisposedOwner');pin.assertCurrent();stage.assertCurrent(stageSource);plans.assertReadCurrent(read);domain.assertCurrent(baseline);codec.assertCurrent();const actual=storage.inspect();if(actual.store_id!==store.store_id||actual.schema_sha256!==store.schema_sha256||actual.service!==store.service)bad('StaleOwner');};
 const checkedContext=(selectedContext:ContextSelection)=>{
  storage.assertSelectedAssembly(selectedContext.auth);
  const selected=selectedContext.auth.inspectInvocation(selectedContext.invocation);
  if(selected.role!=='Query'||selected.operation!==view.query||selected.service!==store.service||
   selected.source_sha256!==view.source_capture_sha256)bad('ForeignOwner');
  if(selectedContext.kind==='worker'){
   if(!workerContext||scopedEntry||selected.entry!==workerEntries[0]!.id||
    selected.actual_business_resource_owners_qualified!==true)bad('NativeContextCustodyRequired');
  }else{
   if(!scopedEntry||selected.entry!==scopedEntry.id||local.contexts.length!==1||
    local.contexts[0]!.source_type!=='Shop.Values.CustomerContext'||
    scopedEntry.access.principal_kind!=='customer'||
    selectedContext.auth.principalIdentity(selectedContext.invocation).kind!=='customer')bad('NativeContextCustodyRequired');
  }
 };
 // Selection/projection check the owner and selected context at their synchronous
 // boundaries; each native Auth read still checks its live invocation.
 const evaluate=(expression:FlowExprV1|ExprV1,p:string,env:Readonly<Record<string,any>>,budget:{used:number},stack:readonly string[],context:ContextSelection|null):any=>evaluateCommerceFlowDataV1(expression as FlowExprV1,p,env,{
  charge(){if(++budget.used>source.contract.limits.fuel)bad('ResourceLimit');},
  pure(at,args){const declaration=calls.get(at),f=declaration?functions.get(declaration):undefined;if(!f)throw new CommerceSourceQueryErrorV1('ForeignSourceCall');if(stack.includes(f.name)||stack.length>=source.contract.limits.max_call_depth)bad('RecursiveQueryCall');if(args.length!==f.parameters.length)bad('InputType');const scope=Object.create(null);f.parameters.forEach((parameter,i)=>scope[parameter.name]=args[i]);return evaluate(f.body,'$pure.'+f.name+'.body',scope,budget,[...stack,f.name],context);},
  native(at,args){if(!context||context.kind!=='worker')return bad('NativeContextCustodyRequired');return context.auth.workerObservation(context.invocation,at,args as CommerceNativeValue[]);},
  context(at){if(!context)return bad('NativeContextCustodyRequired');return context.auth.context(context.invocation,at);},
  isNullaryEnum(name){const declaration=source.contract.values.enums.find(e=>e.name===name);if(!declaration)throw new CommerceSourceQueryErrorV1('UnknownReference');return declaration.variants.every(v=>Object.keys(v.fields).length===0);},
 });
 const action=(kind:'missing'|'unavailable',env:Readonly<Record<string,any>>,budget:{used:number},context:ContextSelection|null):CommerceSourceQueryResultV1=>{const a=kind==='missing'?local.on_missing:local.on_unavailable,qualification=context?.kind==='customer'?'source-selected-customer-query-result;original-entry-and-resource-custody' as const:'source-selected-internal-query-result;entry-and-worker-custody-separate' as const;if(a.kind==='reject'||a.kind==='fail')return frozen({kind:a.kind==='reject'?'rejected' as const:'failed' as const,code:a.code,qualification});if(a.kind!=='return')throw new CommerceSourceQueryErrorV1('UnsupportedQueryAction');return frozen({kind:'returned' as const,value:codec.copy(evaluate(a.value.expression,'$.on_'+kind+'.value.expression',env,budget,[],context)),qualification});};
 type Selected={row:Readonly<Record<string,CommerceNativeValue>>;parameters:Readonly<Record<string,CommerceNativeValue>>;budget:{used:number};context:ContextSelection|null};
 const witnesses=new WeakMap<object,{auth:CommerceSelectedEntryAuthOwnerV1;invocation:CommerceOperationInvocationHandle;selection:Selected|CommerceSourceQueryResultV1;used:boolean}>();
 const selectRow=(parameters:Readonly<Record<string,CommerceNativeValue>>,context:ContextSelection|null):Selected|CommerceSourceQueryResultV1=>{current();closed(parameters,paramNames);if(hasPrivate&&!context)bad('NativeContextCustodyRequired');if(context)checkedContext(context);const env:Record<string,CommerceNativeValue>=Object.assign(Object.create(null),parameters),budget={used:0},slots:Record<string,CommerceNativeValue>=Object.create(null);
   // The actual generated slot sequence is reconstructed from the source Query
   // by the selected storage owner. This caller supplies values, never SQL.
   const mapped=storage.querySlots(read);for(const slot of mapped){
    let at='$.slots.'+slot.id;
    if(slot.origin==='private-context-scalar'){
     const expression=slot.expression;
     if(expression.op!=='field')throw new CommerceSourceQueryErrorV1('ForeignSourceSlot');
     const privateContext=expression.value;
     if(privateContext.op!=='private_context')throw new CommerceSourceQueryErrorV1('ForeignSourceSlot');
     if(!local.contexts.some(declaration=>declaration.binding===privateContext.binding&&
       declaration.source_type===privateContext.source_type&&declaration.abi===privateContext.abi))bad('ForeignSourceSlot');
     at=sourceSlotPath(expression);
    }
    slots[slot.id]=evaluate(slot.expression,at,env,budget,[],context);
   }
   let observation:ReturnType<CommerceServiceStorageOwnerV1['executeSourceQuery']>;try{observation=storage.executeSourceQuery(read,slots);}catch(error){if(error&&typeof error==='object'&&(error as {code?:unknown}).code==='NativeReadUnavailable')return action('unavailable',env,budget,context);throw error;}
   if(observation.query!==view.query||observation.requires_original_context_owner!==hasPrivate||observation.rows.length>local.max_rows)bad('InvalidQuery');
   let selected:Readonly<Record<string,CommerceNativeValue>>|null=null;
   for(const row of observation.rows){const scope=Object.assign(Object.create(null),parameters,row);let joined=true;for(const [i,s]of local.sources.entries())if(s.join&&evaluate(s.join.expression,'$.sources['+i+'].join.expression',scope,budget,[],context)!==true)joined=false;if(!joined||evaluate(local.predicate.expression,'$.predicate.expression',scope,budget,[],context)!==true)continue;for(const [i,g]of local.guards.entries())if(evaluate(g.condition.expression,'$.guards['+i+'].condition.expression',scope,budget,[],context)!==true)return action('missing',env,budget,context);if(selected)bad('QueryBound');selected=row;}
   if(!selected)return action('missing',env,budget,context);current();if(context)checkedContext(context);return {row:selected,parameters,budget,context};};
 const project=(selection:Selected):CommerceSourceQueryResultV1=>{if(selection.context)checkedContext(selection.context);const scope=Object.assign(Object.create(null),selection.parameters,selection.row),projected=evaluate(local.projection.expression,'$.projection.expression',scope,selection.budget,[],selection.context),value=local.wrap_projection_some?frozen({kind:'some' as const,value:projected}):projected;current();if(selection.context)checkedContext(selection.context);return frozen({kind:'returned' as const,value:codec.copy(value),qualification:selection.context?.kind==='worker'?'source-selected-worker-query-result;original-entry-and-worker-custody' as const:selection.context?.kind==='customer'?'source-selected-customer-query-result;original-entry-and-resource-custody' as const:'source-selected-internal-query-result;entry-and-worker-custody-separate' as const});};
 const selectedAuthCurrent=(auth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle)=>{storage.assertSelectedAssembly(auth);const v=auth.inspectInvocation(invocation);if(!scopedEntry||v.source_sha256!==view.source_capture_sha256||v.operation!==view.query||v.role!=='Query'||v.service!==store.service||v.entry!==scopedEntry.id)bad('ForeignOwner');};
 const serviceAuthCurrent=(auth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle)=>{
  storage.assertSelectedAssembly(auth);
  const v=auth.inspectInvocation(invocation),entry=serviceEntries.find(candidate=>candidate.id===v.entry),
   principal=auth.principalIdentity(invocation);
  if(scopedEntry||hasPrivate||workerEntries.length||!entry||
   v.source_sha256!==view.source_capture_sha256||v.operation!==view.query||v.role!=='Query'||
   v.service!==store.service||v.actual_business_resource_owners_qualified!==true||
   principal.kind!=='service'||principal.id!==entry.access.caller)
   bad('ForeignOwner');
 };
 const owner:CommerceSourceQueryRuntimeV1=Object.freeze({query:view.query,execute(parameters:Readonly<Record<string,CommerceNativeValue>>){if(scopedEntry)bad('ScopedQueryGuardRequired');const selection=selectRow(parameters,null);return 'row'in selection?project(selection):selection;},
  executeWorker(auth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle){const worker={auth,invocation,kind:'worker' as const};const parameters=frozen({...auth.parameters(invocation)}),selection=selectRow(parameters,worker);if('row'in selection)return project(selection);checkedContext(worker);return frozen({...selection,qualification:'source-selected-worker-query-result;original-entry-and-worker-custody' as const});},
  selectedEntryMode(entryId:string){current();if(scopedEntry?.id===entryId)return 'scoped-row' as const;
   if(serviceEntries.some(entry=>entry.id===entryId))return 'causal-service' as const;
   return bad('ForeignOwner');},
  executeSelectedService(auth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle){
   current();serviceAuthCurrent(auth,invocation);
   const parameters=frozen({...auth.parameters(invocation)}),selection=selectRow(parameters,null);
   serviceAuthCurrent(auth,invocation);
   const result='row'in selection?project(selection):selection;
   serviceAuthCurrent(auth,invocation);
   return frozen({...result,qualification:'source-selected-service-query-result;original-entry-and-causal-resource-custody' as const});
  },
  select(auth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle){current();selectedAuthCurrent(auth,invocation);const parameters=frozen({...auth.parameters(invocation)}),context=hasPrivate?{auth,invocation,kind:'customer' as const}:null;const selection=selectRow(parameters,context);const witness=Object.freeze({kind:'original-selected-source-query-row/v1-candidate' as const});witnesses.set(witness,{auth,invocation,selection,used:false});return witness;},
  releaseSelected(witness:CommerceSourceQueryRowWitnessV1,auth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle){current();const state=witness&&typeof witness==='object'?witnesses.get(witness):undefined;if(!state||state.auth!==auth||state.invocation!==invocation)return bad('ForeignOwner');if(state.used)bad('AlreadyConsumed');state.used=true;selectedAuthCurrent(auth,invocation);const parameters='row'in state.selection?state.selection.parameters:frozen({...auth.parameters(invocation)}),context=hasPrivate?{auth,invocation,kind:'customer' as const}:null,fresh=selectRow(parameters,context);if(('row'in fresh)!==('row'in state.selection)||'row'in fresh&&'row'in state.selection&&!isDeepStrictEqual(fresh.row,state.selection.row))bad('StaleSelectedRow');if(!('row'in state.selection))return state.selection.kind==='failed'?state.selection:frozen({kind:'rejected' as const,code:scopedEntry!.access.on_resource_missing_or_false,qualification:context?'source-selected-customer-query-result;original-entry-and-resource-custody' as const:'source-selected-internal-query-result;entry-and-worker-custody-separate' as const});const selectedRecord=state.selection.row[scopedBinding!.origin.binding!];if(!selectedRecord||typeof selectedRecord!=='object'||Array.isArray(selectedRecord))bad('InvalidScopedRow');try{auth.assertScopedQueryRow(invocation,view.query,view.source_capture_sha256,selectedRecord);}catch(error){if(error instanceof CommerceSelectedScopedResourceNotFoundV1)return frozen({kind:'rejected' as const,code:scopedEntry!.access.on_resource_missing_or_false,qualification:context?'source-selected-customer-query-result;original-entry-and-resource-custody' as const:'source-selected-internal-query-result;entry-and-worker-custody-separate' as const});throw error;}return project(state.selection);},
  assertCurrent:current,dispose(){disposed=true;}});
 owners.add(owner);current();return owner;
}
