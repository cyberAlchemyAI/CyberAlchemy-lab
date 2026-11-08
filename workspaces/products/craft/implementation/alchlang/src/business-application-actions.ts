import {symbol,json,digest} from './domainspec-profile.js';
import {prepareApplicationExecutable} from './application-executable.js';
import {assertDerivedBusinessApplicationCurrent,type DerivedBusinessApplicationBindings} from './business-application-bindings.js';
import type {BusinessApplicationInput} from './business-application-protocol.js';
import type {DomainSpecCompiler} from './domainspec-cli.js';
import {assertDerivedDirectBusinessBindingsV2Current,type DerivedDirectBusinessBindingsV2} from './business-application-bindings.js';
import {businessCanonical,businessHash,businessReject,freezeBusinessData} from './business-authoring-model.js';

export interface DirectOperationActionsV2 {
 readonly kind:'direct-operation-actions-v2';readonly bindings:DerivedDirectBusinessBindingsV2;
 readonly plan:Readonly<{
  operation_ref:string;input:Readonly<{name:string;type:Readonly<{kind:'named';selector:string}>}>;
  output:Readonly<{kind:'named';selector:string}>;
  guards:readonly Readonly<{rule_ref:string;arguments:readonly Readonly<{parameter:string;value:Readonly<{op:'path';root:string;properties:readonly []}>}>[]}>[];
  result:Readonly<{op:'path';root:string;properties:readonly []}>;rejection:Readonly<{kind:'authored-guard-rejection';code:string}>;effects:readonly [];
 }>;
 readonly actions_sha256:string;readonly authority_effect:'none';
}
const directActions=new WeakMap<object,{bindings:DerivedDirectBusinessBindingsV2;fingerprint:string}>();
/** Direct actions have no store, transaction, observer or evaluator callback port.
 * Open Questions: actual checked Core plan and native generation at L02/U05/G01. */
export function deriveDirectBusinessApplicationActionsV2(bindings:DerivedDirectBusinessBindingsV2):DirectOperationActionsV2 {
 assertDerivedDirectBusinessBindingsV2Current(bindings);
 const operation=bindings.lowered.business.data.operations[0]!,guard=operation.guards[0]!,rule=bindings.lowered.business.data.rules[0]!;
 const argument=guard.arguments[0]!;
 if(guard.rule_ref!==rule.id||argument.parameter!==rule.input.name||argument.value.root!==operation.input.name||argument.value.path.length||operation.result.root!==operation.input.name||operation.result.path.length||operation.effects.length)businessReject('BUSINESS_DIRECT_ACTION',bindings.lowered.business.source.path,1,1,'exact direct guard/result/rejection correspondence required');
 const type={kind:'named' as const,selector:bindings.formation.selectors.entity};
 const plan:DirectOperationActionsV2['plan']={operation_ref:bindings.formation.selectors.operation,input:{name:operation.input.name,type},output:type,guards:[{rule_ref:bindings.rule.selector,arguments:[{parameter:argument.parameter,value:{op:'path',root:argument.value.root,properties:[]}}]}],result:{op:'path',root:operation.result.root,properties:[]},rejection:{kind:'authored-guard-rejection',code:operation.on_rejection},effects:[]};
 const actions_sha256=businessHash(businessCanonical(plan));
 const result=Object.freeze({kind:'direct-operation-actions-v2' as const,bindings,plan:freezeBusinessData(plan,bindings.lowered.business.source.path),actions_sha256,authority_effect:'none' as const});
 directActions.set(result,{bindings,fingerprint:actions_sha256});assertDirectOperationActionsV2Current(result);return result;
}
export function assertDirectOperationActionsV2Current(value:DirectOperationActionsV2):void {
 const state=value&&typeof value==='object'?directActions.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'original direct actions required');
 assertDerivedDirectBusinessBindingsV2Current(state.bindings);
 if(value.bindings!==state.bindings||businessHash(businessCanonical(value.plan))!==state.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',state.bindings.lowered.business.source.path,1,1,'direct actions changed');
}
// Open questions: registered graph, request, native and installed qualification BA04–BA18.
export function deriveBusinessApplicationActions(input:BusinessApplicationInput,derived:DerivedBusinessApplicationBindings,compiler:DomainSpecCompiler) {
 assertDerivedBusinessApplicationCurrent(derived);
 const application=input.applications.find(a=>a.model.id===derived.application_id);if(!application)throw Error('BUSINESS_APPLICATION_MODEL_UNKNOWN');
 const formation=derived.projection.formation,files=derived.projection.projectFiles,semantics=application.semantics;
 const fail=(code:string,id:string):never=>{throw new Error(code+':'+id);};
 const node=(selector:string):any=>{const [feature,id]=selector.split(':');const file=files[`specs/${feature}/nodes/${id}.json`];if(!file)return fail('BUSINESS_ACTION_REFERENCE_UNKNOWN',selector);return JSON.parse(file).body;};
 const qualified=(id:string)=>{const normalized=formation.symbols[id];if(!normalized)return fail('BUSINESS_ACTION_REFERENCE_UNKNOWN',id);return formation.feature+':'+normalized;};
 const same=(a:unknown,b:unknown)=>json(a)===json(b);
 function pathValue(raw:any,inputType:any,root:string){
  let type=inputType;const properties:string[]=[];
  for(const part of raw.path){if(type.kind!=='named')fail('BUSINESS_ACTION_PATH_UNSUPPORTED',part);const field=node(type.selector).typed_contract?.properties?.find((p:any)=>p.name===symbol(part,'_'));if(!field)fail('BUSINESS_ACTION_FIELD_UNKNOWN',part);properties.push(field.ontology_property);type=field.type;}
  return {type,value:{op:'path',root,properties}};
 }
 function guards(rows:readonly any[],inputType:any,root:string,expected:readonly string[]){
  if(!same([...rows.map(g=>qualified(g.rule))].sort(),[...expected].sort()))fail('BUSINESS_ACTION_GUARD_COVERAGE',root);
  return rows.map(g=>{const selector=qualified(g.rule),parameters=node(selector).typed_contract.parameters as {name:string;type:any}[];
   if(!same(Object.keys(g.arguments).map(k=>symbol(k,'_')).sort(),parameters.map(p=>p.name).sort()))fail('BUSINESS_ACTION_GUARD_ARGUMENTS',g.rule);
   return {selector,arguments:parameters.map(parameter=>{const key=Object.keys(g.arguments).find(k=>symbol(k,'_')===parameter.name)!;const selected=pathValue(g.arguments[key],inputType,root);if(!same(selected.type,parameter.type))fail('BUSINESS_ACTION_GUARD_TYPE',g.rule);return {parameter:parameter.name,value:selected.value};})};
  });
 }
 const shapes=formation.operationShapes.operations as any[];
 if(!same(Object.keys(semantics.operation_behaviors).sort(),formation.model.declarations.filter(d=>d.kind==='operation').map(d=>d.id).sort()))fail('BUSINESS_ACTION_OPERATION_COVERAGE',derived.application_id);
 const operations=shapes.map(shape=>{
  const declaration=formation.model.declarations.find(d=>d.kind==='operation'&&qualified(d.id)===shape.operation_ref)!;
  if(declaration.kind!=='operation'||declaration.reads.length||declaration.writes.length||declaration.produces.length)fail('BUSINESS_APPLICATION_EFFECT_UNSUPPORTED',declaration.id);
  const behavior=semantics.operation_behaviors[declaration.id],root=symbol(behavior.input_name,'_');const result=pathValue(behavior.result,shape.input,root);
  if(!same(result.type,shape.output))fail('BUSINESS_ACTION_RESULT_TYPE',declaration.id);
  return {schema_version:'domainspec.operation-action-bindings/v1-candidate',selector:shape.operation_ref,inputs:[{name:root,type:shape.input}],reads:[],guards:guards(behavior.guards,shape.input,root,shape.guard_rule_refs),writes:[],events:[],result:{type:shape.output,value:result.value},atomicity:'state-and-outbox',continuation:'awaited-settlement'};
 });
 const factoryDeclarations=formation.model.declarations.filter(d=>d.kind==='entity'||d.kind==='value-object');
 const unknown=Object.keys(semantics.value_invariant_bindings).filter(id=>!factoryDeclarations.some(d=>d.id===id));if(unknown.length)fail('BUSINESS_FACTORY_INVARIANT_UNKNOWN',unknown[0]!);
 const factories=factoryDeclarations.map(declaration=>{
  const selector=qualified(declaration.id),required=(semantics.declarations[declaration.id].invariants??[]) as string[],rows=semantics.value_invariant_bindings[declaration.id]??[];
  const typed=guards(rows,{kind:'named',selector},'value',required.map(qualified));
  return {selector,base_validators:typed.map((g:any)=>({rule:g.selector,arguments:g.arguments.map((argument:any)=>{const raw=rows.find((r:any)=>qualified(r.rule)===g.selector).arguments;const key=Object.keys(raw).find(k=>symbol(k,'_')===argument.parameter)!;if(raw[key].path.length!==1)fail('BUSINESS_FACTORY_INVARIANT_PATH_UNSUPPORTED',declaration.id);return {parameter:argument.parameter,field:symbol(raw[key].path[0],'_')};})})),extensions:[]};
 });
 const selection={schema_version:'domainspec.reconciled-compilation/v1-candidate',profile_id:'domainspec.reconciled-typescript/v1-candidate',language:'typescript',module_root:'application',layout_version:'domainspec.existing-profile-layout/v1-candidate',value_profile:'domainspec.typescript-exact-uint64/v1',field_bindings:[],factories,operations,workflows:[]};
 const execution={schema_version:'alchlang.application-execution/v1-candidate',projection_sha256:digest(json(derived.projection)),selection};
 const prepared=prepareApplicationExecutable(derived.source,derived.bindings,derived.sources,derived.interpretation,execution,compiler);assertDerivedBusinessApplicationCurrent(derived);
 return {execution,prepared};
}
