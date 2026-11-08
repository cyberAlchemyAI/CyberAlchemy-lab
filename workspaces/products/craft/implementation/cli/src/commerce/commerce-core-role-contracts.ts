/** Independent source -> separate closed role producer contracts. This data
 * never supplies original source/review/input/native custody or executes roles.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {reconstructCoreCommerceSources,type CoreCommerceReconstruction} from './commerce-core-reconstruction.js';
import {coreValueAstType} from './commerce-core-pure.js';
import {coreGenericAdmissionMode,type CoreGenericAdmissionMode,type CoreValueType} from './commerce-core-types.js';
import type {CoreCapturedAsset} from './commerce-core-context.js';
import type {CoreFlowExpression} from './commerce-core-flow-expression.js';
import type {CoreFlowEvaluation} from './commerce-core-flow-evaluation.js';
import {checkCoreCommerceQuerySources} from './commerce-core-flow-query.js';
import {checkCoreCommerceOperationSources,checkCoreGenericOperationSources} from './commerce-core-flow-operation.js';
import {checkCoreCommerceWorkflowSources} from './commerce-core-flow-workflow.js';
import {checkCoreCommerceEntrySources} from './commerce-core-flow-entry.js';
import type {RoleSelectorV1,RoleExpressionV1,FlowExprV1,ReadPlanV1,EffectPlanV1,WorkflowContractV1,EntryContractV1,ResourceBindingV1} from './commerce-data-v1.js';

type Source=readonly {readonly path:string;readonly text:string}[];
const qualification='independent-source-role-contract-data-only' as const;
const fields=(values:readonly {readonly name:string;readonly type:CoreValueType}[])=>Object.fromEntries(values.map(f=>[f.name,coreValueAstType(f.type)]));
function evaluation(value:CoreFlowEvaluation):FlowExprV1 {
 if(value.op==='native_observation')return {...value,result:coreValueAstType(value.result),arguments:value.arguments.map(a=>({...a,value:evaluation(a.value)}))};
 if(value.op==='private_context')return {...value,fields:fields(value.fields)};
 const visit=(v:unknown):unknown=>Array.isArray(v)?v.map(visit):v&&typeof v==='object'?'op'in v?evaluation(v as CoreFlowEvaluation):Object.fromEntries(Object.entries(v).map(([key,child])=>[key,visit(child)])):v;
 return Object.fromEntries(Object.entries(value).map(([key,child])=>[key,visit(child)])) as FlowExprV1;
}
function expression(value:CoreFlowExpression):RoleExpressionV1 {
 return {result:coreValueAstType(value.type),expression:evaluation(value.evaluation),local_records:value.local_records.map(r=>({...r,fields:fields(r.fields)}))};
}
/** A structural walk within an already independently checked role, not a
 * universal execution IR. Every role keeps its own closed control variants. */
function project(value:unknown):unknown {
 if(Array.isArray(value))return value.map(project);
 if(!value||typeof value!=='object')return value;
 const v=value as Record<string,unknown>;
 if(v.qualification==='typed-source-expression-only')return expression(value as CoreFlowExpression);
 if(typeof v.kind==='string'&&['UInt64','Bool','String','literal','record','enum','refinement','variant','optional','List','outcome'].includes(v.kind))return coreValueAstType(value as CoreValueType);
 return Object.fromEntries(Object.entries(v).map(([key,child])=>[key,project(child)]));
}
function selectors(model:CoreCommerceReconstruction){
 const declarations=new Map(model.modules.flatMap(m=>m.declarations).map(d=>[d.id,d]));
 return {role:(name:string):RoleSelectorV1=>{
  const d=declarations.get(name);if(!d?.meta_type)fail('UnknownReference',{path:model.modules[0]!.path,start:0,end:0},'exact declared meta-type selector required');
  return {module:d.module,role:d.meta_type,name:d.name};
 },service:(name:string)=>model.ownership.find(o=>o.declaration===name)?.service??null};
}
export function createCoreCommerceReadContracts(sources:Source,assets:readonly CoreCapturedAsset[]):readonly ReadPlanV1[] {
 const model=reconstructCoreCommerceSources(sources),select=selectors(model),checked=checkCoreCommerceQuerySources(sources,assets);
 return coreFreeze(checked.queries.map(q=>{const {name,result,qualification:_qualification,...rest}=q;return {...project(rest) as object,schema_version:'craft.commerce-read/v1-candidate',query:select.role(name),service:select.service(name),output:coreValueAstType(result),...q.kind==='local'?{cross_service_tables:false}:{},qualification} as ReadPlanV1;}));
}
export function createCoreCommerceEffectContracts(sources:Source,assets:readonly CoreCapturedAsset[]):readonly EffectPlanV1[] {
 const model=reconstructCoreCommerceSources(sources),select=selectors(model),checked=checkCoreCommerceOperationSources(sources,assets);
 return coreFreeze(checked.operations.map(o=>{const {name,qualification:_qualification,...rest}=o;return {...project(rest) as object,schema_version:'craft.commerce-effects/v1-candidate',operation:select.role(name),service:select.service(name),qualification} as EffectPlanV1;}));
}
export function createCoreCommerceWorkflowContracts(sources:Source,assets:readonly CoreCapturedAsset[]):readonly WorkflowContractV1[] {
 const model=reconstructCoreCommerceSources(sources),select=selectors(model),checked=checkCoreCommerceWorkflowSources(sources,assets);
 return coreFreeze(checked.workflows.map(w=>{const {name,owner,qualification:_qualification,...rest}=w;return {...project(rest) as object,schema_version:'craft.commerce-workflow/v1-candidate',workflow:select.role(name),service:owner,qualification} as WorkflowContractV1;}));
}
export function createCoreCommerceEntryContracts(sources:Source,assets:readonly CoreCapturedAsset[]):readonly EntryContractV1[] {
 const model=reconstructCoreCommerceSources(sources),select=selectors(model),checked=checkCoreCommerceEntrySources(sources,assets);
 return coreFreeze(checked.entries.map(e=>{
  const {invokes,result,access}=e;
  const resource_bindings:ResourceBindingV1[]=access.resource_bindings.map(b=>({name:b.binding,type:b.kind==='data'?{kind:'data',type:{kind:'record',name:b.source_type}}:{kind:'private-projection',source_type:b.source_type,abi:b.abi,fields:fields(b.fields)},abi:b.abi,selector:b.selector,fields:fields(b.fields),required_fields:b.required_fields,projection_family:b.projection_family,source_document:b.source_document,origin:b.origin,custody:b.custody,public_constructor:b.public_constructor}));
  return {id:e.id,service:e.service,interaction:e.interaction,parameters:e.parameters.map(p=>({name:p.name,type:coreValueAstType(p.type)})),event_argument:e.event_argument,native_requirements:e.native_requirements,schema_version:'craft.commerce-entry/v1-candidate',invokes:select.role(invokes),output:result?coreValueAstType(result):null,access:{...access,resource_bindings,resource_condition:access.resource_condition?expression(access.resource_condition):null},qualification};
 }));
}
function compare<T>(sources:Source,actual:T,proposal:unknown):T {
 const where={path:sources[0]?.path??'application.alch',start:0,end:0};let proposed:string;
 try{proposed=dataDigest(proposal);}catch{return fail('InvalidContract',where,'closed inert role-contract proposal required');}
 if(proposed!==dataDigest(actual))fail('InvalidContract',where,'role contracts differ from fresh independent source reconstruction');return actual;
}
export const checkCoreCommerceReadContractsProposal=(sources:Source,assets:readonly CoreCapturedAsset[],proposal:unknown)=>compare(sources,createCoreCommerceReadContracts(sources,assets),proposal);
export const checkCoreCommerceEffectContractsProposal=(sources:Source,assets:readonly CoreCapturedAsset[],proposal:unknown)=>compare(sources,createCoreCommerceEffectContracts(sources,assets),proposal);
export const checkCoreCommerceWorkflowContractsProposal=(sources:Source,assets:readonly CoreCapturedAsset[],proposal:unknown)=>compare(sources,createCoreCommerceWorkflowContracts(sources,assets),proposal);
export const checkCoreCommerceEntryContractsProposal=(sources:Source,assets:readonly CoreCapturedAsset[],proposal:unknown)=>compare(sources,createCoreCommerceEntryContracts(sources,assets),proposal);

/** Source-derived closed zero-effect projection; no legacy effect contract cast. */
export function createCoreGenericEffectContracts(sources:Source,assets:readonly CoreCapturedAsset[],mode:CoreGenericAdmissionMode='bounded-values',selected?:readonly string[]):readonly import('../generic/computation-data-v1.js').GenericEffectPlanV1[]{
 coreGenericAdmissionMode(mode);
 const model=reconstructCoreCommerceSources(sources,(mode==='keyed-query-entry'||(mode==='atomic-state-entry'||mode==='external-read-entry'||mode==='external-write-entry'||mode==='event-handoff-entry'))?mode:'legacy'),select=selectors(model),checked=checkCoreGenericOperationSources(sources,assets,mode);
 type Step=typeof checked.operations[number]['body'][number];type Action=Extract<Step,{kind:'action'}>['action'];
 const expr=(e:Extract<Action,{kind:'return'}>['value']):import('../generic/computation-data-v1.js').GenericRoleExpressionV1=>{
  if(e.native_calls.length||e.context_reads.length||e.local_records.length)fail('UnsupportedCapability',{path:'generic-role',start:0,end:0},'generic pure role cannot carry native/private projections');
  return {result:coreValueAstType(e.type),expression:e.expression,local_records:[]};
 };
 const action=(a:Action):import('../generic/computation-data-v1.js').GenericOperationActionV1=>{if(a.kind==='return')return {kind:'return',value:expr(a.value)};if(a.kind==='reject'||a.kind==='fail')return a;return fail('UnsupportedCapability',{path:'generic-role',start:0,end:0},'generic Operation action must be pure return/reject/fail');};
 const steps=(rows:readonly Step[]):import('../generic/computation-data-v1.js').GenericOperationControlStepV1[]=>rows.map(s=>{
  if(s.kind==='enforce-policy')return {...s,value:expr(s.value)};
  if(s.kind==='guard')return {kind:'guard',condition:expr(s.condition),on_false:action(s.on_false)};
  if(s.kind==='conditional')return {kind:'conditional',condition:expr(s.condition),then:steps(s.then),otherwise:steps(s.otherwise)};
  if(s.kind==='action')return {kind:'action',action:action(s.action)};
  return fail('UnsupportedCapability',{path:'generic-role',start:0,end:0},'generic Operation step is outside zero-effect guard/conditional/action scope');
 });
 return coreFreeze(checked.operations.filter(o=>selected===undefined||selected.includes(o.name)).map(o=>{if(o.contexts.length||o.protocol||select.service(o.name)&&(mode!=='keyed-query-entry'&&(mode!=='atomic-state-entry'&&mode!=='external-read-entry'&&mode!=='external-write-entry'&&mode!=='event-handoff-entry')))fail('UnsupportedCapability',{path:'generic-role',start:0,end:0},'generic C05 has no native service/protocol/context');return {schema_version:'craft.generic-effects/v1-candidate',operation:select.role(o.name),service:null,parameters:o.parameters.map(p=>({name:p.name,type:coreValueAstType(p.type)})),contexts:[],result:coreValueAstType(o.result),body:steps(o.body),protocol:null,qualification};}));
}
