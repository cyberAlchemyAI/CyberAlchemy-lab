import {createWorkflowControls, workflowVerificationDefinitions, SEMANTIC_WORKFLOW_DEFINITION_SHA256, type WorkflowControls} from './reconciled-workflow-controls.js';
import {WORKFLOW_SEMANTIC_RUNNER} from './reconciled-workflow-runner.js';
import {createOperationControls,SEMANTIC_OPERATION_DEFINITION_SHA256,type OperationControls} from './reconciled-operation-controls.js';
import {OPERATION_SEMANTIC_RUNNER} from './reconciled-operation-runner.js';
import {createInterfaceControls,SEMANTIC_INTERFACE_DEFINITION_SHA256,type InterfaceControls} from './reconciled-interface-controls.js';
import {INTERFACE_SEMANTIC_RUNNER} from './reconciled-interface-runner.js';
import {createQueryControls,SEMANTIC_QUERY_DEFINITION_SHA256,type QueryControls} from './reconciled-query-controls.js';
import {QUERY_SEMANTIC_RUNNER} from './reconciled-query-runner.js';
import {createMappingControls,SEMANTIC_MAPPING_DEFINITION_SHA256,type MappingControls} from './reconciled-mapping-controls.js';
import {MAPPING_SEMANTIC_RUNNER} from './reconciled-mapping-runner.js';
import {createEventControls,SEMANTIC_EVENT_DEFINITION_SHA256,type EventControls} from './reconciled-event-controls.js';
import {EVENT_SEMANTIC_RUNNER} from './reconciled-event-runner.js';
import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {createReconciledVerificationProjection} from './reconciled-projection.js';
import {decodeTypedCalculationContract,type TypedCalculationContract} from '../typed-backend/contracts.js';
import {decodeExactCalculation,type ExactCalculationContract} from '../typed-backend/calculation-exact.js';
import {expectedCalculation as expected} from './calculation-reference.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {createPlainEnumControls,PLAIN_ENUM_RUNNER,SEMANTIC_ENUM_DEFINITION_SHA256,type PlainEnumControls} from './reconciled-enum-controls.js';
import {createSumControls,SEMANTIC_SUM_DEFINITION_SHA256,type SumControls} from './reconciled-sum-controls.js';
import {SUM_SEMANTIC_RUNNER} from './reconciled-sum-runner.js';
import {SEMANTIC_RECORD_WITNESS_DEFINITION_SHA256} from './reconciled-record-witness.js';
import {createFactoryControls,SEMANTIC_FACTORY_DEFINITION_SHA256,type FactoryControls} from './reconciled-factory-controls.js';
import {FACTORY_SEMANTIC_RUNNER} from './reconciled-factory-runner.js';
import {createRuleControls,SEMANTIC_RULE_DEFINITION_SHA256,type RuleControls} from './reconciled-rule-controls.js';
import {RULE_SEMANTIC_RUNNER} from './reconciled-rule-runner.js';
import {createPolicyControls,SEMANTIC_POLICY_DEFINITION_SHA256,type PolicyControls} from './reconciled-policy-controls.js';
import {createStateMachineControls,SEMANTIC_STATE_MACHINE_DEFINITION_SHA256,type StateMachineControls} from './reconciled-state-machine-controls.js';

export const SEMANTIC_CONTROLS_DEFINITION_SHA256='9b8f46e65427dbc0b94b5ea56606f4a70f9482ef861271696f89a24d25441982';
type Calculation=TypedCalculationContract|ExactCalculationContract;
type Outcome=Readonly<{kind:'value';value:string}>|Readonly<{kind:'error';name:'RangeError'|'TypeError';message:string}>;
type BadInput=Readonly<{index:number;kind:string}>;
export interface SemanticCase {
 readonly id:string;readonly mode:string;readonly format:'string'|'bigint'|'number';
 readonly values:readonly string[];readonly bad?:BadInput;readonly expected:Outcome;
}
type Ready=WorkflowControls|OperationControls|InterfaceControls|QueryControls|MappingControls|EventControls|StateMachineControls|PolicyControls|RuleControls|FactoryControls|SumControls|PlainEnumControls|Readonly<{selector:string;kind:string;state:'ready';contract_sha256:string;relative_path:string;callable:string;names:readonly string[];module_paths:readonly string[];cases:readonly SemanticCase[]}>;
type Unmet=Readonly<{selector:string;kind:string;state:'not_evaluable';reason:string}>;
const max=18446744073709551615n,safe=9007199254740991n;
const fail=(message:string):never=>{throw new TypeError('DS_RECONCILED_SEMANTIC_CONTROLS:'+message);};
const registered=new WeakMap<object,{graph:CompiledProjectGraph;plan:ReconciledProjectPlan}>();
function freeze<T>(value:T):T{if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.values(value).forEach(freeze);Object.freeze(value);}return value;}
const error=(message:string):Outcome=>({kind:'error',name:message==='CALCULATION_INPUT'?'TypeError':'RangeError',message});

function cases(contract:Calculation):SemanticCase[]{
 const length=contract.inputs.length,base=Array.from({length},()=> '1'),vectors=new Map<string,string[]>();
 const add=(v:string[])=>vectors.set(canonicalJson(v),v);
 for(const v of [0n,1n,2n,3n,safe,safe+1n,max-1n,max])add(base.map(()=>String(v)));
 add(base.map((_,i)=>String(i+1)));add(base.map((_,i)=>String(length-i+3)));
 for(let i=0;i<length;i++)for(const v of [0n,2n,3n,safe+1n,max]){const values=[...base];values[i]=String(v);add(values);}
 const result:SemanticCase[]=[];
 const push=(mode:string,format:SemanticCase['format'],values:string[],outcome:Outcome,bad?:BadInput)=>{
  result.push({id:'case-'+result.length,mode,format,values,...(bad?{bad}:{}),expected:outcome});
 };
 for(const values of vectors.values()){
  const outcome=expected(contract,values);
  push('record','string',values,outcome);push('record','bigint',values,outcome);
  if(values.every(v=>BigInt(v)<=safe))push('record','number',values,outcome);
 }
 for(const mode of ['null-prototype','frozen'])push(mode,'string',base,expected(contract,base));
 for(const mode of ['null','array','inherited','extra','symbol','getter','non-enumerable',...(length?['missing']:[])])push(mode,'string',base,error('CALCULATION_INPUT'));
 for(let index=0;index<length;index++)for(const kind of ['negative','overflow','padded','decimal','signed','empty','nan','infinity','unsafe-number','fraction','null','boolean','coercion']){
  push('record','string',base,error('CALCULATION_INPUT'),{index,kind});
 }
 return result;
}

/** Pure preparation retains all source nodes, including adapters not yet implemented. */
export function createReconciledSemanticControls(graph:CompiledProjectGraph,plan:ReconciledProjectPlan){
 const input=createReconciledVerificationProjection(graph,plan);
 if(sha256(getReconciledSource('semantic_controls'))!==SEMANTIC_CONTROLS_DEFINITION_SHA256)fail('definition drift');
 if(sha256(getReconciledSource('semantic_enum_controls'))!==SEMANTIC_ENUM_DEFINITION_SHA256)fail('Enum definition drift');
 if(sha256(getReconciledSource('semantic_sum_controls'))!==SEMANTIC_SUM_DEFINITION_SHA256)fail('sum definition drift');
 if(sha256(getReconciledSource('semantic_record_witness'))!==SEMANTIC_RECORD_WITNESS_DEFINITION_SHA256)fail('record witness definition drift');
 if(sha256(getReconciledSource('semantic_factory_controls'))!==SEMANTIC_FACTORY_DEFINITION_SHA256)fail('factory definition drift');
 if(sha256(getReconciledSource('semantic_rule_controls'))!==SEMANTIC_RULE_DEFINITION_SHA256)fail('Rule definition drift');
 if(sha256(getReconciledSource('semantic_policy_controls'))!==SEMANTIC_POLICY_DEFINITION_SHA256)fail('Policy definition drift');
 if(sha256(getReconciledSource('semantic_state_machine_controls'))!==SEMANTIC_STATE_MACHINE_DEFINITION_SHA256)fail('State Machine definition drift');
 if(sha256(getReconciledSource('semantic_event_controls'))!==SEMANTIC_EVENT_DEFINITION_SHA256)fail('Event definition drift');
 if(sha256(getReconciledSource('semantic_mapping_controls'))!==SEMANTIC_MAPPING_DEFINITION_SHA256)fail('Mapping definition drift');
 if(sha256(getReconciledSource('semantic_interface_controls'))!==SEMANTIC_INTERFACE_DEFINITION_SHA256)fail('Interface definition drift');
 if(sha256(getReconciledSource('semantic_query_controls'))!==SEMANTIC_QUERY_DEFINITION_SHA256)fail('Query definition drift');
 if(sha256(getReconciledSource('semantic_operation_controls'))!==SEMANTIC_OPERATION_DEFINITION_SHA256)fail('Operation definition drift');
 workflowVerificationDefinitions();
 let total=0,bytes=256;
 const bounded=(ready:Ready):Ready|Unmet=>{
  const size=Buffer.byteLength(canonicalJson(ready))+1;
  if(ready.cases.length>4096||total+ready.cases.length>65536||bytes+size>8388608)return {selector:ready.selector,kind:ready.kind,state:'not_evaluable',reason:'bounded semantic case capacity exceeded'};
  total+=ready.cases.length;bytes+=size;return ready;
 };
 const rows:(Ready|Unmet)[]=graph.nodes.map(node=>{
  const identity={selector:node.selector,kind:node.kind};
  if(node.kind==='Workflow'){const ready=createWorkflowControls(node,graph,plan);return ready.state==='ready'?bounded(ready):ready;}
  if(node.kind==='Interface'){const ready=createInterfaceControls(node,graph,plan);return ready.state==='ready'?bounded(ready):ready;}
  if(node.kind==='Query'){const ready=createQueryControls(node,graph,plan);return ready.state==='ready'?bounded(ready):ready;}
  if(node.kind==='Operation'){const ready=createOperationControls(node,graph,plan);return ready.state==='ready'?bounded(ready):ready;}
  if(node.kind==='Mapping'){const ready=createMappingControls(node,graph,plan);return ready.state==='ready'?bounded(ready):ready;}
  if(node.kind==='Event'){const ready=createEventControls(node,graph,plan);return ready.state==='ready'?bounded(ready):ready;}
  if(node.kind==='State Machine'){
   const ready=createStateMachineControls(node,graph,plan);return ready.state==='ready'?bounded(ready):ready;
  }
  if(node.kind==='Policy'){
   const ready=createPolicyControls(node,graph,plan);return ready.state==='ready'?bounded(ready):ready;
  }
  if(node.kind==='Rule'){
   const ready=createRuleControls(node,graph,plan);return ready.state==='ready'?bounded(ready):ready;
  }
  if(node.kind==='Entity'||node.kind==='Value Object'){
   const ready=createFactoryControls(node,graph,plan);return ready.state==='ready'?bounded(ready):ready;
  }
  if(node.kind==='Enum'){
   const ready=createPlainEnumControls(node,plan)??createSumControls(node,graph,plan);
   return ready.state==='ready'?bounded(ready):ready;
  }
  if(node.kind!=='Calculation')return {...identity,state:'not_evaluable' as const,reason:'semantic adapter not implemented for '+node.kind};
  const raw=node.body.typed_contract as {schema_version?:unknown};
  const contract=raw.schema_version==='domainspec.typed-calculation/v2'?decodeExactCalculation(raw):decodeTypedCalculationContract(raw);
  const name=node.selector.split(':')[1]!,callable='calculate'+name.split('-').map(p=>p[0]!.toUpperCase()+p.slice(1)).join('');
  const modules=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(node.selector)&&m.exports.some(e=>e.name===callable&&e.kind==='value'));
  if(modules.length!==1)fail('unique Calculation callable required:'+node.selector);
  const module=modules[0]!,paths=new Set<string>();
  const visit=(relative:string)=>{
   if(paths.has(relative))return;paths.add(relative);
   const m=plan.resolved.modules.find(m=>m.relative_path===relative)??fail('missing native module');
   for(const i of m.imports){const target=i.target_path??fail('pure Calculation cannot import external modules');visit(target);}
  };visit(module.relative_path);
  return bounded({...identity,state:'ready',contract_sha256:sha256(canonicalJson(contract)),relative_path:module.relative_path,callable,names:contract.inputs.map(p=>p.name),module_paths:[...paths].sort(),cases:cases(contract)});
 });
 const body={schema_version:'domainspec.reconciled-semantic-controls/v1-candidate' as const,definition_sha256:SEMANTIC_CONTROLS_DEFINITION_SHA256,projection_sha256:input.projection_sha256,project_plan_sha256:plan.plan_sha256,rows,
  node_count:rows.length,ready_count:rows.filter(r=>r.state==='ready').length,not_evaluable_count:rows.filter(r=>r.state==='not_evaluable').length,case_count:total,
  adapter_definitions:{workflow:SEMANTIC_WORKFLOW_DEFINITION_SHA256,operation:SEMANTIC_OPERATION_DEFINITION_SHA256,interface:SEMANTIC_INTERFACE_DEFINITION_SHA256,query:SEMANTIC_QUERY_DEFINITION_SHA256,mapping:SEMANTIC_MAPPING_DEFINITION_SHA256,event:SEMANTIC_EVENT_DEFINITION_SHA256,plain_enum:SEMANTIC_ENUM_DEFINITION_SHA256,sum:SEMANTIC_SUM_DEFINITION_SHA256,record_witness:SEMANTIC_RECORD_WITNESS_DEFINITION_SHA256,factory:SEMANTIC_FACTORY_DEFINITION_SHA256,rule:SEMANTIC_RULE_DEFINITION_SHA256,policy:SEMANTIC_POLICY_DEFINITION_SHA256,state_machine:SEMANTIC_STATE_MACHINE_DEFINITION_SHA256},claim_scope:'bounded-differential-cases-not-universal-proof' as const,authority_effect:'none' as const};
 const result=freeze({...body,controls_sha256:sha256(canonicalJson(body))});registered.set(result,{graph,plan});return result;
}
export type ReconciledSemanticControls=ReturnType<typeof createReconciledSemanticControls>;
function assertControls(value:ReconciledSemanticControls):void{if(!registered.has(value))fail('registered semantic controls required');}
/** Equal serialized controls are not the original source-bound preparation. */
export function assertReconciledSemanticControlsFor(value:unknown,graph:CompiledProjectGraph,plan:ReconciledProjectPlan):asserts value is ReconciledSemanticControls{
 const binding=value&&typeof value==='object'?registered.get(value):undefined;
 if(!binding)return fail('registered semantic controls required');
 if(binding.graph!==graph||binding.plan!==plan)fail('foreign semantic controls input');
 createReconciledVerificationProjection(graph,plan);
}
export function semanticModulePaths(controls:ReconciledSemanticControls):readonly string[]{
 assertControls(controls);return [...new Set(controls.rows.flatMap(row=>row.state==='ready'?[...row.module_paths]:[]))].sort();
}
export function renderSemanticCases(controls:ReconciledSemanticControls):string{
 assertControls(controls);return canonicalJson({controls_sha256:controls.controls_sha256,rows:controls.rows.filter(r=>r.state==='ready')})+'\n';
}
/** Accept child JSON only when every named observation equals its independent expectation. */
export function checkSemanticObservations(controls:ReconciledSemanticControls,text:string){
 assertControls(controls);const observed=JSON.parse(text),expected=controls.rows.filter(r=>r.state==='ready').map(r=>({selector:r.selector,cases:r.cases.map(c=>({id:c.id,outcome:c.expected,getter_reads:0,input_changed:false}))}));
 if(canonicalJson(observed)!==canonicalJson(expected))fail('native semantic observation mismatch');
 return freeze({controls_sha256:controls.controls_sha256,node_count:controls.node_count,tested_node_count:controls.ready_count,case_count:controls.case_count,observation_sha256:sha256(canonicalJson(observed)),expected_sha256:sha256(canonicalJson(expected)),claim_scope:controls.claim_scope,
  tested:controls.rows.filter(r=>r.state==='ready').map(r=>({selector:r.selector,kind:r.kind,contract_sha256:r.contract_sha256,case_count:r.cases.length})),
  remaining:controls.rows.filter(r=>r.state==='not_evaluable').map(r=>({selector:r.selector,kind:r.kind,reason:r.reason}))});
}

export const SEMANTIC_RUNNER=String.raw`
import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';
const [caseFile,moduleRoot]=process.argv.slice(2),plan=JSON.parse(fs.readFileSync(caseFile,'utf8')),observations=[];
// Guard actual native resolution as well as the checked source import inventory.
const nativeImports=new Map(),importViolations=new Set();
const nativeUrl=p=>pathToFileURL(path.join(moduleRoot,p.replace(/\.ts$/,'.js'))).href;
for(const row of plan.rows)if(row.adapter==='workflow'||row.adapter==='operation'||row.adapter==='interface'||row.adapter==='query'||row.adapter==='policy'||row.adapter==='state-machine'||row.adapter==='event'||row.adapter==='mapping')for(const m of row.native_imports){
 const url=nativeUrl(m.relative_path),targets=new Map(),prior=nativeImports.get(url);
 const boundary=row.adapter==='workflow'?'WORKFLOW_NATIVE_IMPORT_BOUNDARY':row.adapter==='operation'?'OPERATION_NATIVE_IMPORT_BOUNDARY':row.adapter==='interface'?'INTERFACE_NATIVE_IMPORT_BOUNDARY':row.adapter==='query'?'QUERY_NATIVE_IMPORT_BOUNDARY':row.adapter==='mapping'?'MAPPING_NATIVE_IMPORT_BOUNDARY':row.adapter==='event'?'EVENT_NATIVE_IMPORT_BOUNDARY':row.adapter==='policy'?'POLICY_NATIVE_IMPORT_BOUNDARY':'STATE_MACHINE_NATIVE_IMPORT_BOUNDARY';
 for(const i of m.imports){
  if(i.target_path===null&&(row.adapter!=='workflow'||m.relative_path!==row.provider_path||i.specifier!=='node:crypto'))throw Error(boundary);
  const target=i.target_path===null?'node:crypto':nativeUrl(i.target_path);
  if(targets.has(i.specifier)&&targets.get(i.specifier)!==target)throw Error('SEMANTIC_NATIVE_IMPORT_CONFLICT');targets.set(i.specifier,target);
 }
 const entries=[...targets].sort(([a],[b])=>a<b?-1:a>b?1:0);
 if(prior&&JSON.stringify([...prior.imports])!==JSON.stringify(entries))throw Error('SEMANTIC_NATIVE_IMPORT_CONFLICT');
 if(prior)prior.boundaries.add(boundary);else nativeImports.set(url,{imports:new Map(entries),boundaries:new Set([boundary])});
}
if(nativeImports.size){
 const {registerHooks}=await import('node:module');
 registerHooks({resolve(specifier,context,nextResolve){
  const parent=context.parentURL?new URL(context.parentURL):null;
  if(parent){parent.search='';parent.hash='';}
  const allowed=parent?nativeImports.get(parent.href):undefined;
  if(!allowed)return nextResolve(specifier,context);
  const reject=()=>{for(const b of allowed.boundaries)importViolations.add(b);throw Error([...allowed.boundaries].sort().join('|'));};
  if(!allowed.imports.has(specifier))return reject();
  const resolved=nextResolve(specifier,context);
  if(resolved.url!==allowed.imports.get(specifier))return reject();
  return resolved;
 }});
}
${PLAIN_ENUM_RUNNER}
${SUM_SEMANTIC_RUNNER}
${FACTORY_SEMANTIC_RUNNER}
${RULE_SEMANTIC_RUNNER}
${EVENT_SEMANTIC_RUNNER}
${MAPPING_SEMANTIC_RUNNER}
${QUERY_SEMANTIC_RUNNER}
${INTERFACE_SEMANTIC_RUNNER}
${OPERATION_SEMANTIC_RUNNER}
${WORKFLOW_SEMANTIC_RUNNER}
for(const row of plan.rows){
 if(row.adapter==='workflow'){observations.push(await observeWorkflow(row));continue;}
 if(row.adapter==='interface'){observations.push(await observeInterface(row));continue;}
 if(row.adapter==='operation'){observations.push(await observeOperation(row));continue;}
 if(row.adapter==='query'){observations.push(await observeQuery(row));continue;}
 if(row.adapter==='mapping'){observations.push(await observeMapping(row));continue;}
 if(row.adapter==='event'){observations.push(await observeEvent(row));continue;}
 if(row.adapter==='rule'||row.adapter==='policy'||row.adapter==='state-machine'){observations.push(await observeRule(row));continue;}
 if(row.adapter==='factory'){observations.push(await observeFactory(row));continue;}
 if(row.adapter==='sum'){observations.push(await observeSum(row));continue;}
 if(row.adapter==='plain-enum'){observations.push(await observePlainEnum(row));continue;}
 const native=await import(pathToFileURL(path.join(moduleRoot,row.relative_path.replace(/\.ts$/,'.js'))).href),fn=native[row.callable],result=[];
 if(typeof fn!=='function')throw Error('missing semantic callable');
 for(const c of row.cases){
  let getter_reads=0;
  const values=c.values.map(v=>c.format==='bigint'?BigInt(v):c.format==='number'?Number(v):v);
  if(c.bad){
   const bad={negative:'-1',overflow:'18446744073709551616',padded:'01',decimal:'1.0',signed:'+1',empty:'',nan:NaN,infinity:Infinity,'unsafe-number':9007199254740992,fraction:1.5,null:null,boolean:true,coercion:{valueOf(){getter_reads++;return 1;}}};
   values[c.bad.index]=bad[c.bad.kind];
  }
  let input=Object.fromEntries(row.names.map((name,i)=>[name,values[i]])),extra='_unexpected';
  while(row.names.includes(extra))extra+='_';
  const first=row.names[0]??extra;
  switch(c.mode){
   case 'null-prototype':input=Object.assign(Object.create(null),input);break;
   case 'frozen':Object.freeze(input);break;
   case 'null':input=null;break;
   case 'array':input=[];break;
   case 'inherited':input=Object.assign(Object.create({unexpected:true}),input);break;
   case 'extra':input[extra]='1';break;
   case 'symbol':input[Symbol('unexpected')]='1';break;
   case 'getter':Object.defineProperty(input,first,{enumerable:true,configurable:true,get(){getter_reads++;return '1';}});break;
   case 'non-enumerable':Object.defineProperty(input,first,{enumerable:false,configurable:true,value:'1'});break;
   case 'missing':delete input[first];break;
  }
  const before=input===null?null:Object.getOwnPropertyDescriptors(input),prototype=input===null?null:Object.getPrototypeOf(input);
  let outcome;
  try{const value=fn(input);outcome=typeof value==='bigint'?{kind:'value',value:value.toString()}:{kind:'unexpected',type:typeof value};}
  catch(e){outcome={kind:'error',name:e?.name,message:e?.message};}
  const after=input===null?null:Object.getOwnPropertyDescriptors(input);
  const same=before===null?after===null:Object.getPrototypeOf(input)===prototype&&Reflect.ownKeys(before).length===Reflect.ownKeys(after).length&&Reflect.ownKeys(before).every(k=>{
   const a=before[k],b=after[k];return b&&['value','get','set','writable','enumerable','configurable'].every(p=>Object.is(a[p],b[p]));
  });
  result.push({id:c.id,outcome,getter_reads,input_changed:!same});
 }
 observations.push({selector:row.selector,cases:result});
}
if(importViolations.size)throw Error([...importViolations].sort().join('|'));
process.stdout.write(JSON.stringify(observations));
`;
