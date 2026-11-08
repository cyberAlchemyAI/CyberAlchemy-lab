/** Zero-effect admission/lowering of the existing original EffectPlanV1.
 * This is compiler construction, never a runtime AST interpreter or callback.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {isPolicyRejectionCode,POLICY_ENFORCEMENT_REVISION} from '../commerce/commerce-policy-enforcement.js';
import {reconstructCoreCommerceSources} from '../commerce/commerce-core-reconstruction.js';
import {admitGenericComposition,GENERIC_OPERATION_CAPABILITIES,GENERIC_MAPPING_CAPABILITIES,GENERIC_CALCULATION_CAPABILITIES,GENERIC_SCALAR_OPERATORS} from './composition-capabilities.js';
import {createOrderedMappingComputation,pureMappingPin} from './pure-mapping.js';
import {checkCoreCommercePureSources,requireLegacyExpressionData} from '../commerce/commerce-core-pure.js';
import {createCoreCommerceComputationContract} from '../commerce/commerce-core-pure-contract.js';
import {createCoreCommerceEffectContracts} from '../commerce/commerce-core-role-contracts.js';
import type {GenericComputationContractV1,GenericEffectPlanV1,GenericExprV1,GenericOperationActionV1,GenericOperationControlStepV1} from './computation-data-v1.js';
import type {ComputationContractV1,ComputationLimitsV1,EffectPlanV1,OperationActionV1,OperationControlStepV1,ExprV1,RoleExpressionV1,ValueTypeV1} from '../commerce/commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url));
export const pureOperationPin=pinCoreImplementation(import.meta.url,['composition-capabilities'+ext,'pure-mapping'+ext,'../commerce/commerce-policy-enforcement'+ext,'../commerce/commerce-core-role-contracts'+ext,'../commerce/commerce-core-flow-operation'+ext,'../commerce/commerce-core-pure-contract'+ext]);
export const PURE_OPERATION_CONSTRUCTION_LIMITS=Object.freeze({control_steps:16384,control_nesting:64,lowered_expression_nodes:65536,lowered_expression_depth:128});
export const PURE_OPERATION_LOWERING_REVISION='craft.generic-zero-effect-operation/v1-candidate';
const at={path:'operation',start:0,end:0};
const allowedExpressions=new Set(['var','field','literal','unary','binary','call','let']);
export function assertPureOperationPlan(plan:EffectPlanV1,pureNames:ReadonlySet<string>,mapping=false,calculations=false):void {
 if(plan.contexts.length||plan.protocol!==null)fail('UnsupportedCapability',at,'pure Operation cannot bind private contexts or external/replay protocols');
 const type=(t:ValueTypeV1)=>{if(!(t.kind==='record'||t.kind==='scalar'&&(t.name==='Bool'||mapping&&t.name==='UInt64')))fail('UnsupportedCapability',at,'C02 parameters/results must be Bool or admitted flat Bool record');};
 plan.parameters.forEach(p=>type(p.type));type(plan.result);
 const expression=(value:RoleExpressionV1)=>{if(value.local_records.length)fail('UnsupportedCapability',at,'private local projection records are not admitted');const stack:any[]=[value.expression];let count=0;while(stack.length){if(++count>65536)fail('ResourceLimit',at,'finite operation expression bound');const e=stack.pop();if(!allowedExpressions.has(e.op))fail('UnsupportedCapability',at,'effect/native/future expression rejected: '+e.op);
  if(e.op==='call'&&!pureNames.has(e.declaration))fail('UnsupportedCapability',at,'only original admitted pure Rule callsites are executable');
  if(e.op==='literal'&&(e.type.kind!=='scalar'||!['Bool',...(mapping?['UInt64']:[])].includes(e.type.name)))fail('UnsupportedCapability',at,'C02 business expressions admit Bool literals only');
  if(e.op==='binary'&&!(calculations?GENERIC_SCALAR_OPERATORS:['and','or','eq']).includes(e.operator))fail('UnsupportedCapability',at,'C02 scalar arithmetic is not admitted');
  for(const v of Object.values(e)){if(v&&typeof v==='object'){if(Array.isArray(v))stack.push(...v.filter(x=>x&&typeof x==='object'&&'op'in x));else if('op'in v)stack.push(v);}}
 }};
 const action=(a:OperationActionV1)=>{if(a.kind==='return')expression(a.value);else if(a.kind!=='reject'&&a.kind!=='fail')fail('UnsupportedCapability',at,'Operation/Query invocation is not a pure Rule call');};
 const pending=[...plan.body];let count=0;while(pending.length){if(++count>16384)fail('ResourceLimit',at,'finite operation control bound');const s=pending.pop()!;
  if(s.kind==='guard'){expression(s.condition);action(s.on_false);}
  else if(s.kind==='conditional'){expression(s.condition);pending.push(...s.then,...s.otherwise);}
  else if(s.kind==='action')action(s.action);
  else if(s.kind==='enforce-policy')fail('UnsupportedCapability',s.source_site,'typed Policy enforcement requires the selected generic value consumer, not the legacy scalar Operation profile');
  else fail('UnsupportedCapability',at,'control step enters a later composition phase: '+s.kind);
 }
}
export function createPureOperationComputation(sources:readonly {path:string;text:string}[],assets:readonly {path:string;text:string}[],operation:string,limits:ComputationLimitsV1,mapping=false,calculations=false){
 if(calculations&&!mapping)fail('UnsupportedCapability',at,'Calculation composition requires ordered Mapping admission');
 pureOperationPin.assertCurrent();if(mapping)pureMappingPin.assertCurrent();const pure=checkCoreCommercePureSources(sources),plans=createCoreCommerceEffectContracts(sources,assets),names=new Set(pure.declarations.filter(d=>d.kind==='Rule'||mapping&&d.kind==='Mapping'||calculations&&(d.kind==='Calculation'||d.kind==='Policy')).map(d=>d.name));
 admitGenericComposition({reconstruction:reconstructCoreCommerceSources(sources)},pure,calculations?GENERIC_CALCULATION_CAPABILITIES:mapping?GENERIC_MAPPING_CAPABILITIES:GENERIC_OPERATION_CAPABILITIES);
 // Scan every admitted Operation, not just the selected branch/function.
 for(const plan of plans)assertPureOperationPlan(plan,names,mapping,calculations);
 const selected=plans.find(p=>p.operation.module+'.'+p.operation.name===operation);if(!selected)fail('UnknownReference',at,'exact original Operation selector required');
 if(pure.declarations.some(d=>d.on_evaluation_error!==null))fail('UnsupportedCapability',at,'callee evaluation-error handlers require later control lowering');
 const first=pure.declarations[0];if(!first)fail('MissingMapping',at,'C02 requires original Rule composition');
 const mapped=mapping?createOrderedMappingComputation(sources,first.name,limits,calculations):undefined;
 const base=mapped?.contract??createCoreCommerceComputationContract(sources,first.name,limits);
 const lowered=lowerOperationContract(base,selected,plans.map(p=>p.operation.module+'.'+p.operation.name));
 return requireLegacyExpressionData<{contract:ComputationContractV1;derivation:typeof lowered.derivation}>( {...lowered,derivation:{...lowered.derivation,...(mapped?{mapping:mapped.derivation}:{})}});
}
/** Shared closed control lowering; the actual source/domain owner remains mandatory. */
export function lowerOperationContract(base:ComputationContractV1|GenericComputationContractV1,selected:EffectPlanV1|GenericEffectPlanV1,operationNames:readonly string[]){
 const operation=selected.operation.module+'.'+selected.operation.name,limits=base.limits;
 const pureExpression=(value:RoleExpressionV1['expression']|GenericExprV1):GenericExprV1=>{
  const pending:unknown[]=[value];while(pending.length){const v=pending.pop();if(!v||typeof v!=='object')continue;if('op'in v&&(v.op==='native_observation'||v.op==='private_context'))fail('UnsupportedCapability',at,'native expression cannot enter pure control lowering');pending.push(...Object.values(v));}return value as GenericExprV1;
 };
 const internalName=operation+'.GeneratedOutcome';
 if([...base.functions,...base.values.records,...base.values.enums,...base.values.refinements].some(x=>x.name===internalName)||operationNames.includes(internalName))fail('DuplicateSymbol',at,'technical outcome identity collides with source declaration');
 const codeType:ValueTypeV1={kind:'string',max_bytes:256,max_scalars:256},result:ValueTypeV1={kind:'enum',name:internalName};
 const action=(a:OperationActionV1|GenericOperationActionV1):GenericExprV1=>{
  if(a.kind==='return')return {op:'enum_value',type_name:internalName,variant:'Returned',fields:{value:pureExpression(a.value.expression)}};
  if(a.kind==='reject'||a.kind==='fail'){if(Buffer.byteLength(a.code)>256||[...a.code].length>256)fail('ResourceLimit',at,'bounded authored failure code required');return {op:'enum_value',type_name:internalName,variant:a.kind==='reject'?'Rejected':'Failed',fields:{code:{op:'literal',type:codeType,value:a.code}}};}
  return fail('UnsupportedCapability',at,'effect call cannot enter pure lowering');
 };
 // Names are local compiler bindings, not source declarations. Reserve every
 // authored/IR binder and variable in the complete input before selecting one.
 // That also prevents a generated binding from capturing an outer continuation.
 const occupied=new Set<string>(selected.parameters.map(x=>x.name)),names:unknown[]=[selected,base],visitedNames=new Set<object>();let fresh=0;
 while(names.length){const v=names.pop();if(!v||typeof v!=='object')continue;
  if(visitedNames.has(v))continue;visitedNames.add(v);if(visitedNames.size>262144)fail('ResourceLimit',at,'bounded enforcement binding-name construction');
  if('name'in v&&typeof v.name==='string')occupied.add(v.name);
  if('binding'in v&&typeof v.binding==='string')occupied.add(v.binding);
  names.push(...Object.values(v));
 }
 const temporary=()=>{let name:string;do{name='GeneratedEnforce'+fresh++;}while(occupied.has(name));occupied.add(name);return name;};
 const enforcement=(s:Extract<OperationControlStepV1|GenericOperationControlStepV1,{kind:'enforce-policy'}>,next:GenericExprV1):GenericExprV1=>{
  const target=base.functions.find(f=>f.name===s.policy),admission=base.values.enums.find(e=>e.name===s.result_enum),reason=base.values.enums.find(e=>e.name===s.reason_enum),allow=admission?.variants.find(v=>v.name==='Allow'),reject=admission?.variants.find(v=>v.name==='Reject');
  // The original expression checker normalizes named arguments into typed lets
  // in source order before its terminal Policy call. Keep those lets intact.
  let invocation=s.value.expression,argumentLets=0;while(invocation.op==='let'){
   if(++argumentLets>PURE_OPERATION_CONSTRUCTION_LIMITS.lowered_expression_depth)fail('ResourceLimit',s.source_site,'bounded enforcement argument normalization');invocation=invocation.body;
  }
  if(s.semantics_revision!==POLICY_ENFORCEMENT_REVISION||!target||target.kind!=='Policy'||target.result.kind!=='enum'||target.result.name!==s.result_enum||s.value.result.kind!=='enum'||s.value.result.name!==s.result_enum||invocation.op!=='call'||invocation.declaration!==s.policy||!admission||admission.variants.length!==2||!allow||Object.keys(allow.fields).length||!reject||Object.keys(reject.fields).join(',')!=='reason'||reject.fields.reason?.kind!=='enum'||reject.fields.reason.name!==s.reason_enum||!reason||!reason.variants.length||reason.variants.length!==s.rejections.length||reason.variants.some(v=>Object.keys(v.fields).length)||s.reason_enum===s.result_enum)
   fail('InvalidContract',s.source_site,'enforce lowering requires the actual checked Policy and exact finite admission types');
  for(let i=0;i<s.rejections.length;i++){
   const row=s.rejections[i]!,variant=reason.variants[i]!;
   if(row.variant!==variant.name||row.wire!==variant.wire||row.code!==row.wire||!isPolicyRejectionCode(row.code))fail('InvalidContract',s.source_site,'enforce rejection table differs from the original typed reason enum');
  }
  if(new Set(s.rejections.map(r=>r.code)).size!==s.rejections.length)fail('InvalidContract',s.source_site,'enforce rejection table must be unique');
  const decision=temporary(),reasonBinding=temporary();
  return {op:'let',binding:{name:decision,type:{kind:'enum',name:s.result_enum}},value:pureExpression(s.value.expression),body:{op:'match_variant',value:{op:'var',name:decision},cases:[
   {variant:'Allow',binding:null,then:next},
   {variant:'Reject',binding:reasonBinding,then:{op:'match_variant',value:{op:'var',name:reasonBinding},cases:s.rejections.map(r=>({variant:r.variant,binding:null,then:action({kind:'reject',code:r.code})})),otherwise:null}},
  ],otherwise:null}};
 };
 // Continuations preserve source order and run only on the selected branch.
 // The original checker has already proven every reachable path returns.
 const lower=(steps:readonly (OperationControlStepV1|GenericOperationControlStepV1)[],continuation:GenericExprV1|null,depth=0):GenericExprV1|null=>{
  if(depth>64)fail('ResourceLimit',at,'bounded source control depth');let next=continuation;
  for(let i=steps.length-1;i>=0;i--){const s=steps[i]!;
   if(s.kind==='action')next=action(s.action);
   else if(s.kind==='guard'){if(!next)fail('MissingMapping',at,'guard continuation must terminate');next={op:'if',condition:pureExpression(s.condition.expression),then:next,else:action(s.on_false)};}
   else if(s.kind==='conditional'){const yes=lower(s.then,next,depth+1),no=lower(s.otherwise,next,depth+1);if(!yes||!no)fail('MissingMapping',at,'both conditional continuations must terminate');next={op:'if',condition:pureExpression(s.condition.expression),then:yes,else:no};}
   else if(s.kind==='enforce-policy'){if(!next)fail('MissingMapping',s.source_site,'enforce continuation must terminate');next=enforcement(s,next);}
   else fail('UnsupportedCapability',at,'unsupported operation control step');
  }return next;
 };
 const expression=lower(selected.body,null);if(!expression)fail('MissingMapping',at,'complete Operation result required');
 // Check the complete expanded continuation tree before recursive freezing or
 // digesting. Shared continuations count once per emitted occurrence. Stop at
 // the authored bound before a compact source can expand exponentially.
 const pending:{value:unknown;depth:number}[]=[{value:expression,depth:1}];let expandedNodes=0;
 while(pending.length){const {value,depth}=pending.pop()!;if(!value||typeof value!=='object')continue;const isExpression='op'in value;
  if(isExpression&&(++expandedNodes>limits.max_ast_nodes||depth>limits.max_ast_depth||expandedNodes>PURE_OPERATION_CONSTRUCTION_LIMITS.lowered_expression_nodes||depth>PURE_OPERATION_CONSTRUCTION_LIMITS.lowered_expression_depth))fail('ResourceLimit',at,'lowered Operation exceeds source AST node/depth limit');
  for(const child of Object.values(value))if(child&&typeof child==='object')pending.push({value:child,depth:depth+(isExpression?1:0)});
 }
 const contract=coreFreeze({...base,source_node:operation,inputs:selected.parameters,result,values:{...base.values,root:result,enums:[...base.values.enums,{name:internalName,variants:[{name:'Returned',wire:'Returned',fields:{value:selected.result}},{name:'Rejected',wire:'Rejected',fields:{code:codeType}},{name:'Failed',wire:'Failed',fields:{code:codeType}}]}]},expression});
 const derivation=coreFreeze({revision:PURE_OPERATION_LOWERING_REVISION,construction_limits:PURE_OPERATION_CONSTRUCTION_LIMITS,operation: selected.operation,effect_plan_sha256:dataDigest(selected),source_limits_sha256:dataDigest(limits),internal_types:[{name:internalName,kind:'technical-operation-outcome',origin:selected.operation,authored:false}],metering:'single-existing-native-kernel-budget;all-lowered-expression-and-codec-work',qualification:'zero-effect-Operation-only;not-stateful-runtime',authority_effect:'none'});
 pureOperationPin.assertCurrent();return coreFreeze({contract,derivation});
}
