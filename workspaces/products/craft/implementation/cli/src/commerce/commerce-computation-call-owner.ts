/** Original Operation source-to-pure-callee bindings; no Operation/native owner.
 * Open Questions: docs/COMMERCE-COMPUTATION-CALLS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCoreCommerceStageSourceOwner,createCoreCommerceSemanticStageComponent,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {createCoreCommerceComputationContract} from './commerce-core-pure-contract.js';
import {evaluateCommerceComputationObserved} from './commerce-computation-evaluate.js';
import {compileCommerceComputationTypeScript} from './commerce-computation-native.js';
import {adaptCommercePureCallResult} from './commerce-computation-call-runtime.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {EffectPlanV1,RoleExpressionV1,OperationActionV1,FlowExprV1,SourceIdentityV1,SourceSpanV1,BinderV1,ValueTypeV1,EvaluationErrorActionV1,PureDeclarationV1} from './commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['commerce-computation-call-runtime'+ext,'commerce-computation-kernel'+ext,'commerce-computation-environment'+ext,'commerce-computation-domain'+ext,'commerce-computation-evaluate'+ext,'commerce-computation-native'+ext,'commerce-core-stage-owner'+ext,'commerce-core-pure-contract'+ext,'../profile-engine/contracts'+ext]);
const where={path:'application.alch',start:0,end:0};
export interface CommercePureCallHandle {readonly kind:'original-commerce-pure-call-binding/v1-candidate'}
export type CommerceCallActionReference={readonly kind:OperationActionV1['kind'];readonly code:string|null;readonly subject_sha256:string};
export interface CommerceCallAdapterSpec {readonly direct_guard:boolean;readonly on_false:CommerceCallActionReference|null;readonly on_error:CommerceCallActionReference|null;readonly requires_rollback:boolean}
export interface CommercePureCallInspection {
 readonly kind:'commerce-source-pure-call-binding/v1-candidate';readonly caller:string;readonly source:SourceIdentityV1;readonly span:SourceSpanV1;
 readonly source_capture_sha256:string;readonly caller_plan_sha256:string;readonly expression_path:string;readonly role_path:string;readonly role_expression:RoleExpressionV1;
 readonly callee:{readonly declaration:string;readonly kind:PureDeclarationV1['kind'];readonly source:SourceIdentityV1;readonly span:SourceSpanV1;readonly parameters:readonly BinderV1[];readonly result:ValueTypeV1;readonly rounding:PureDeclarationV1['rounding'];readonly on_evaluation_error:EvaluationErrorActionV1|null;readonly contract_sha256:string};
 readonly arguments:readonly FlowExprV1[];readonly enclosing_statement_path:string|null;readonly direct_role_call:boolean;readonly adapter:CommerceCallAdapterSpec;
 readonly acquisition_requirements:readonly {readonly expression_path:string;readonly node:FlowExprV1}[];
 readonly input_contract:'already-bound-pure-parameters-only;original-argument-evaluation-order-and-native-custody-required-from-caller';
 readonly budget_scope:'original-captured-budget-per-checked-pure-evaluation;not-a-whole-operation-or-caller-loop-account';
 readonly code_epoch_sha256:string;readonly binding_sha256:string;
 readonly qualification:'original-source-call-and-pure-component-only;not-operation-native-or-application-execution';readonly authority_effect:'none';
}
export interface CommercePureCallOwner {
 paths(plan:EffectPlanV1):readonly string[];
 bind(plan:EffectPlanV1,expressionPath:string):CommercePureCallHandle;
 inspect(handle:CommercePureCallHandle):CommercePureCallInspection;
 evaluateBoundParameters(handle:CommercePureCallHandle,input:Uint8Array):ReturnType<typeof adaptCommercePureCallResult>;
 compilePure(handle:CommercePureCallHandle):ReturnType<typeof compileCommerceComputationTypeScript>;
 assertCurrent(handle:CommercePureCallHandle):void;dispose(handle:CommercePureCallHandle):void;
}
type Scope={kind:'guard'|'let'|'other';statement:string|null;role_path:string;role:RoleExpressionV1;on_false:OperationActionV1|null;on_error:OperationActionV1|null;rollback:boolean;direct:string};
type Call={path:string;node:Extract<FlowExprV1,{op:'call'}>;scope:Scope};
const registered=new WeakSet<object>();
export function assertCommercePureCallOwner(owner:CommercePureCallOwner):void {if(!owner||typeof owner!=='object'||!registered.has(owner))fail('ForeignOwner',where,'original source-pure-call owner required');}
const actionRef=(action:OperationActionV1|null):CommerceCallActionReference|null=>action?coreFreeze({kind:action.kind,code:action.kind==='fail'||action.kind==='reject'?action.code:null,subject_sha256:dataDigest(action)}):null;
// This is a layout walk. It preserves the source tree; it is never an execution
// schedule and never acquires or moves a native observation/private context.
function callsIn(plan:EffectPlanV1):Call[]{
 const out:Call[]=[];let nodes=0;
 const budget=(depth:number)=>{if(++nodes>65536||depth>128)fail('ResourceLimit',where,'bounded source call layout required');};
 const expression=(value:any,p:string,scope:Scope,depth:number)=>{
  if(!value||typeof value!=='object')return;budget(depth);
  if(!Array.isArray(value)&&value.op==='call')out.push({path:p,node:value,scope});
  if(Array.isArray(value))value.forEach((v,i)=>expression(v,p+'['+i+']',scope,depth+1));
  else for(const [key,v]of Object.entries(value))expression(v,p+'.'+key,scope,depth+1);
 };
 const role=(value:RoleExpressionV1,p:string,kind:Scope['kind'],statement:string|null,on_false:OperationActionV1|null,on_error:OperationActionV1|null,rollback:boolean,depth:number)=>{
  let node=value.expression,direct=p+'.expression';while(node.op==='let'){node=node.body;direct+='.body';}
  expression(value.expression,p+'.expression',{kind,statement,role_path:p,role:value,on_false,on_error,rollback,direct:node.op==='call'?direct:''},depth);
 };
 const walk=(value:any,p:string,rollback:boolean,depth:number)=>{
  if(!value||typeof value!=='object')return;budget(depth);
  if(Array.isArray(value)){value.forEach((v,i)=>walk(v,p+'['+i+']',rollback,depth+1));return;}
  if(value.expression&&value.result&&Array.isArray(value.local_records)){role(value,p,'other',null,null,null,rollback,depth+1);return;}
  for(const [key,v]of Object.entries(value)){
   const next=p+'.'+key;
   if(value.kind==='guard'&&key==='condition')role(v as RoleExpressionV1,next,'guard',p,value.on_false,null,rollback,depth+1);
   else if(value.kind==='let'&&key==='value')role(v as RoleExpressionV1,next,'let',p,null,value.on_error??null,rollback,depth+1);
   else walk(v,next,rollback||key==='transaction',depth+1);
  }
 };
 walk(plan,'$',false,0);return out;
}
export function createCommercePureCallOwner(stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle):CommercePureCallOwner {
 assertCoreCommerceStageSourceOwner(stage);assertCommerceComputationDomainOwner(domain);pin.assertCurrent();stage.assertCurrent(source);domain.assertCurrent(baseline);
 const initial=domain.inspect(baseline),capture=stage.inspect(source);if(initial.source_capture_sha256!==capture.source_sha256)fail('ForeignOwner',where,'callee domain and caller must share their exact original source capture');
 const component=createCoreCommerceSemanticStageComponent(stage,source),owned=new WeakMap<object,{inspection:CommercePureCallInspection;callee:CommerceComputationDomainHandle;disposed:boolean}>();
 const parents=()=>{pin.assertCurrent();stage.assertCurrent(source);domain.assertCurrent(baseline);};
 const checked=(proposal:EffectPlanV1)=>{
  parents();const inert=captureJson(proposal) as unknown as EffectPlanV1,values={...initial.contract.values,root:inert.result},result=component.checkEffects(inert,values);if(!result.ok){const d=result.diagnostics[0]!;fail(d.code,d,d.message);}return result.value;
 };
 const current=(handle:CommercePureCallHandle)=>{const state=handle&&typeof handle==='object'?owned.get(handle):undefined;if(!state)fail('ForeignOwner',where,'original source-call token from this exact factory required');if(state.disposed)fail('DisposedOwner',where,'source-call binding disposed');parents();domain.assertCurrent(state.callee);return state;};
 const owner:CommercePureCallOwner=Object.freeze({
  paths(proposal:EffectPlanV1){const plan=checked(proposal);return coreFreeze(callsIn(plan).map(c=>c.path));},
  bind(proposal:EffectPlanV1,expressionPath:string){
   const plan=checked(proposal);if(typeof expressionPath!=='string'||expressionPath.length>8192)fail('InvalidContract',where,'original bounded callsite path required');
   const row=callsIn(plan).find(c=>c.path===expressionPath);if(!row)fail('UnknownReference',where,'selected source path must be a declared pure call');
   const declaration=initial.contract.functions.find(f=>f.name===row.node.declaration);if(!declaration)fail('UnknownReference',where,'source call must target an original pure declaration');
   const module=stage.moduleContracts(source).find(m=>m.source.module===plan.operation.module),caller=module?.declarations.find(d=>dataDigest(d.selector)===dataDigest(plan.operation));if(!module||!caller)fail('UnknownReference',where,'original Operation declaration/span required');
   const texts=capture.modules.map(m=>({path:m.identity.artifact.path,text:m.text})),callee=domain.check(createCoreCommerceComputationContract(texts,declaration.name,initial.contract.limits)),pure=domain.inspect(callee),symbol=pure.symbols.find(s=>s.selector.module+'.'+s.selector.name===declaration.name)!;
   const scope=row.scope,direct=scope.direct===row.path,adapter:CommerceCallAdapterSpec={direct_guard:direct&&scope.kind==='guard'&&declaration.result.kind==='scalar'&&declaration.result.name==='Bool',on_false:direct&&scope.kind==='guard'?actionRef(scope.on_false):null,on_error:actionRef(scope.on_error),requires_rollback:scope.rollback};
   const acquisition_requirements:{expression_path:string;node:FlowExprV1}[]=[];
   const retain=(v:any,p:string)=>{if(!v||typeof v!=='object')return;if(v.op==='native_observation'||v.op==='private_context')acquisition_requirements.push({expression_path:p,node:v});if(Array.isArray(v))v.forEach((x,i)=>retain(x,p+'['+i+']'));else for(const [key,x]of Object.entries(v))retain(x,p+'.'+key);};retain(scope.role.expression,scope.role_path+'.expression');
   const subject={kind:'commerce-source-pure-call-binding/v1-candidate' as const,caller:plan.operation.module+'.'+plan.operation.name,source:module.source,span:caller.span,source_capture_sha256:capture.source_sha256,caller_plan_sha256:dataDigest(plan),expression_path:row.path,role_path:scope.role_path,role_expression:scope.role,callee:{declaration:declaration.name,kind:declaration.kind,source:symbol.source,span:symbol.span,parameters:declaration.parameters,result:declaration.result,rounding:declaration.rounding,on_evaluation_error:declaration.on_evaluation_error,contract_sha256:pure.contract_sha256},arguments:row.node.arguments,enclosing_statement_path:scope.statement,direct_role_call:direct,adapter,acquisition_requirements,input_contract:'already-bound-pure-parameters-only;original-argument-evaluation-order-and-native-custody-required-from-caller' as const,budget_scope:'original-captured-budget-per-checked-pure-evaluation;not-a-whole-operation-or-caller-loop-account' as const,code_epoch_sha256:pin.sha256,qualification:'original-source-call-and-pure-component-only;not-operation-native-or-application-execution' as const,authority_effect:'none' as const};
   const inspection:CommercePureCallInspection=coreFreeze({...subject,binding_sha256:dataDigest(subject)}),handle=Object.freeze({kind:'original-commerce-pure-call-binding/v1-candidate' as const});owned.set(handle,{inspection,callee,disposed:false});current(handle);return handle;
  },
  inspect(handle:CommercePureCallHandle){return current(handle).inspection;},
  evaluateBoundParameters(handle:CommercePureCallHandle,input:Uint8Array){const s=current(handle),observed=evaluateCommerceComputationObserved(domain,s.callee,input),result=adaptCommercePureCallResult(observed,s.inspection.adapter);current(handle);return result;},
  compilePure(handle:CommercePureCallHandle){const s=current(handle),result=compileCommerceComputationTypeScript(domain,s.callee);current(handle);return result;},
  assertCurrent(handle:CommercePureCallHandle){current(handle);},dispose(handle:CommercePureCallHandle){const s=current(handle);s.disposed=true;domain.dispose(s.callee);},
 });registered.add(owner);return owner;
}
