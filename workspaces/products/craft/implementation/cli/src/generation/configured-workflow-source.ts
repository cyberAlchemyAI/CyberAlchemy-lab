import {assertCheckedWorkflowBindings,type CheckedWorkflowBindings} from '../typed-operation/workflow-bindings.js';
import {assertCheckedWorkflowRecoveryPolicy,planSelectedWorkflowRecovery,WORKFLOW_FAILURE_JOURNAL_VERSION,type CheckedWorkflowRecoveryPolicy} from '../typed-operation/workflow-recovery.js';
import {WORKFLOW_OUTCOME_CONTRACT_SHA256} from '../typed-operation/workflow-outcomes.js';
import {WORKFLOW_SETTLEMENT_SUPPORT} from './workflow-settlement-source.js';
import {composedWorkflowSettlementSupport} from './composed-workflow-settlement-source.js';
const q=JSON.stringify;
const fail=(m:string):never=>{throw new TypeError('DS_WORKFLOW_SOURCE:'+m);};
function literal(v:unknown):string{
 if(Array.isArray(v))return 'Object.freeze(['+v.map(literal).join(',')+'])';
 if(v&&typeof v==='object')return 'Object.freeze({'+Object.entries(v).map(([k,x])=>'['+q(k)+']:'+literal(x)).join(',')+'})';
 return JSON.stringify(v);
}
export interface WorkflowOperationImport {readonly selector:string;readonly path:string;readonly symbol:string;readonly local:string;readonly action_sha256:string;readonly descriptor_sha256:string;}

const runtime=String.raw`
type StepMeta=Readonly<{step_id:string;operation_ref:string;action_sha256:string}>;
type PlanEntry=Readonly<{compensation_id:string;for_step:string;operation_ref:string;action_sha256:string;depends_on:readonly string[];inactive_dependencies:readonly string[];arguments:readonly unknown[];events:readonly unknown[];failure_continuation:string}>;
type PrefixTemplate=Readonly<{steps:readonly StepMeta[];plan:readonly PlanEntry[];plan_digest:string|null}>;
export type WorkflowIdentity=Readonly<{workflow_execution_id:string;failure_occurrence_id:string}>;
type Observation=Readonly<{schema_version:'domainspec.workflow-step-observation/v1-candidate';contract_sha256:string;workflow_sha256:string;step_id:string;operation_ref:string;action_sha256:string;settlement:OperationSettlement;evidence:'caller-supplied';authority_effect:'none';observation_sha256:string}>;
type LocalError='committed-result-invalid'|'result-materialization-failed'|null;
const observe=(index:number,settlement:OperationSettlement):Observation=>{
 const step=wf.steps[index]!;
 const body={schema_version:'domainspec.workflow-step-observation/v1-candidate' as const,contract_sha256:outcomeContract,workflow_sha256:wf.hash,...step,settlement,evidence:'caller-supplied' as const,authority_effect:'none' as const};
 return freeze({...body,observation_sha256:digest(body)});
};
const recover=(completed:readonly string[],failed:Observation,ids:WorkflowIdentity)=>{
 const template=prefixTemplates[completed.length]!;
 const journal={schema_version:'domainspec.workflow-failure-journal/v1-candidate' as const,workflow_execution_id:ids.workflow_execution_id,failure_occurrence_id:ids.failure_occurrence_id,completed_step_ids:completed,failed_step_id:failed.step_id,failed_commit_status:failed.settlement.commit_status};
 const common={schema_version:'domainspec.workflow-recovery-evaluation/v1-candidate' as const,workflow_sha256:wf.hash,policy_sha256:policyHash,journal,journal_sha256:digest(journal),commit_evidence:'caller-supplied' as const,intent_registration:'not-performed' as const,compensation_execution:false as const,authority_effect:'none' as const};
 if(failed.settlement.commit_status==='indeterminate')return freeze({...common,status:'reconciliation-required' as const,workflow_evaluation_result:null,recovery_intent:null,unknown_step_id:failed.step_id});
 if(!template.plan.length)return freeze({...common,status:'evaluated' as const,workflow_evaluation_result:'not-required' as const,recovery_intent:null});
 const completed_step_journal_digest=digest({schema_version:'domainspec.workflow-completed-prefix/v1-candidate',workflow_sha256:wf.hash,workflow_execution_id:ids.workflow_execution_id,steps:template.steps});
 const plan_digest=template.plan_digest!;
 const body={schema_version:'domainspec.workflow-recovery-intent/v3-candidate' as const,workflow_selector:wf.selector,workflow_sha256:wf.hash,policy_sha256:policyHash,workflow_execution_id:ids.workflow_execution_id,failure_occurrence_id:ids.failure_occurrence_id,failed_step_id:failed.step_id,completed_step_journal_digest,plan_digest};
 const intent_id=digest(body);
 const plan=template.plan.map(row=>({...row,invocation_identity:digest({schema_version:'domainspec.compensation-invocation/v2-candidate',intent_id,plan_digest,compensation_id:row.compensation_id,operation_ref:row.operation_ref,action_sha256:row.action_sha256})}));
 return freeze({...common,status:'evaluated' as const,workflow_evaluation_result:'recovery-required' as const,recovery_intent:{...body,intent_id,semantic_status:'required' as const,plan}});
};
const evaluate=(observations:readonly Observation[],ids:WorkflowIdentity,local_error:LocalError)=>{
 const last=observations.at(-1),failed=last&&last.settlement.commit_status!=='committed'?last:null;
 const completed_step_ids=observations.filter(r=>r.settlement.commit_status==='committed').map(r=>r.step_id);
 const common={schema_version:'domainspec.workflow-outcome-evaluation/v1-candidate' as const,workflow_sha256:wf.hash,policy_sha256:policyHash,workflow_execution_id:ids.workflow_execution_id,failure_occurrence_id:failed||local_error?ids.failure_occurrence_id:null,completed_step_ids,observations,evidence:'caller-supplied' as const,result_validation:'not-performed' as const,execution:'not-performed' as const,authority_effect:'none' as const};
 if(failed){const recovery=recover(completed_step_ids,failed,ids);return freeze({...common,status:'forward-stopped' as const,failure:failed.settlement,local_error:null,recovery_status:recovery.status,recovery});}
 if(local_error)return freeze({...common,status:'orchestration-error' as const,failure:null,local_error,recovery_status:'not-evaluable' as const,recovery:null});
 return freeze({...common,status:completed_step_ids.length===wf.steps.length?'forward-complete' as const:'awaiting-next-step' as const,failure:null,local_error:null,recovery_status:'not-evaluated' as const,recovery:null});
};
type Evaluation=ReturnType<typeof evaluate>;
type Intent=NonNullable<NonNullable<Evaluation['recovery']>['recovery_intent']>;
export type WorkflowOutcome=
 | Readonly<{status:'succeeded';value:ReturnType<typeof material.result>;evaluation:Evaluation;recovery_bindings:null}>
 | Readonly<{status:'forward-stopped'|'orchestration-error';evaluation:Evaluation;bindings_status:'ready'|'not-required'|'not-evaluable'|'failed';recovery_bindings:RecoveryBindings|null}>;
const imported=(fn:unknown,selector:string,action:string,descriptor:string):void=>{
 if(typeof fn!=='function')return fail('Operation callable');
 const p=Object.getOwnPropertyDescriptor(fn,'descriptor');if(!p||!Object.hasOwn(p,'value'))return fail('Operation descriptor');
 const d=p.value;if(!d||typeof d!=='object')return fail('Operation descriptor');
 for(const [key,expected]of [['selector',selector],['action_sha256',action],['descriptor_sha256',descriptor]]){
  const p=Object.getOwnPropertyDescriptor(d,key!);if(!p||!Object.hasOwn(p,'value')||p.value!==expected)return fail('Operation identity');
 }
};
const stopped=(input:material.CapturedInput,results:readonly material.CapturedResult[],observations:readonly Observation[],ids:WorkflowIdentity,local_error:LocalError=null):WorkflowOutcome=>{
 const evaluation=evaluate(observations,ids,local_error),intent=evaluation.recovery?.recovery_intent;
 if(!intent)return freeze({status:local_error?'orchestration-error':'forward-stopped',evaluation,bindings_status:evaluation.recovery?.workflow_evaluation_result==='not-required'?'not-required':'not-evaluable',recovery_bindings:null});
 try{return freeze({status:'forward-stopped',evaluation,bindings_status:'ready',recovery_bindings:prepareBindings(input,results,intent)});}
 catch{return freeze({status:'forward-stopped',evaluation,bindings_status:'failed',recovery_bindings:null});}
};
`;

export function renderConfiguredWorkflow(workflow:CheckedWorkflowBindings,policy:CheckedWorkflowRecoveryPolicy,materialPath:string,imports:readonly WorkflowOperationImport[]):string{
 assertCheckedWorkflowBindings(workflow);assertCheckedWorkflowRecoveryPolicy(policy);
 if(policy.workflow!==workflow)return fail('policy identity');
 // All failure prefixes are selected at compile time by the unchanged pure planner.
 const templates=workflow.steps.map((failed,i)=>{
  const planned=planSelectedWorkflowRecovery(policy,{schema_version:WORKFLOW_FAILURE_JOURNAL_VERSION,workflow_execution_id:'compile-execution',failure_occurrence_id:'compile-failure',completed_step_ids:workflow.steps.slice(0,i).map(s=>s.step_id),failed_step_id:failed.step_id,failed_commit_status:'not-committed'});
  const intent=planned.recovery_intent;
  return {steps:workflow.steps.slice(0,i).map(s=>({step_id:s.step_id,operation_ref:s.operation_ref,action_sha256:s.action_sha256})),
   plan:intent?intent.plan.map(({invocation_identity:_id,...row})=>row):[],plan_digest:intent?.plan_digest??null};
 });
 const dependencyTypes=imports.map(i=>'readonly '+q(i.selector)+':Parameters<typeof '+i.local+'>[1]').join(';');
 const wf={hash:workflow.workflow_sha256,selector:workflow.bindings.selector,steps:workflow.steps.map(s=>({step_id:s.step_id,operation_ref:s.operation_ref,action_sha256:s.action_sha256}))};
 const bindingTypes=workflow.compensations.map(c=>'Readonly<{intent_id:string;plan_digest:string;invocation_identity:string;compensation_id:'+q(c.compensation_id)+';operation_ref:'+q(c.operation_ref)+';action_sha256:'+q(c.action_sha256)+';arguments:ReturnType<typeof material.compensations['+q(c.compensation_id)+']["arguments"]>}>').join('|')||'never';
 const prepare='export type RecoveryBinding='+bindingTypes+';\nexport type RecoveryBindings=Readonly<{schema_version:"domainspec.workflow-recovery-bindings/v1-candidate";intent_id:string;plan_digest:string;bindings:readonly RecoveryBinding[];compensation_execution:false;authority_effect:"none"}>;\n'+
  'const prepareBindings=(input:material.CapturedInput,results:readonly material.CapturedResult[],intent:Intent):RecoveryBindings=>{\n const bindings:RecoveryBinding[]=[];\n for(const row of intent.plan){\n'+workflow.compensations.map(c=>
   '  if(row.compensation_id==='+q(c.compensation_id)+'){if(row.operation_ref!=='+q(c.operation_ref)+'||row.action_sha256!=='+q(c.action_sha256)+')return fail("compensation identity");bindings.push(Object.freeze({intent_id:intent.intent_id,plan_digest:intent.plan_digest,invocation_identity:row.invocation_identity,compensation_id:'+q(c.compensation_id)+',operation_ref:'+q(c.operation_ref)+',action_sha256:'+q(c.action_sha256)+',arguments:material.compensations['+q(c.compensation_id)+'].arguments(input,results)}));continue;}\n').join('')+
  '  return fail("unknown compensation");\n }\n return freeze({schema_version:"domainspec.workflow-recovery-bindings/v1-candidate",intent_id:intent.intent_id,plan_digest:intent.plan_digest,bindings,compensation_execution:false,authority_effect:"none"});\n};\n';
 const execute='export const execute=async(parameters:WorkflowInput,executionIdentity:WorkflowIdentity,dependencies:WorkflowDependencies):Promise<WorkflowOutcome>=>{\n'+
  ' const e=own(executionIdentity,["workflow_execution_id","failure_occurrence_id"]);const ids=Object.freeze({workflow_execution_id:identity(e.workflow_execution_id!.value),failure_occurrence_id:identity(e.failure_occurrence_id!.value)});\n'+
  ' const input=material.capture(parameters);\n const d=own(dependencies,'+q(imports.map(i=>i.selector))+');\n'+
  imports.map((i,n)=>' const call'+n+'='+i.local+';imported(call'+n+','+q(i.selector)+','+q(i.action_sha256)+','+q(i.descriptor_sha256)+');const dep'+n+'=d['+q(i.selector)+']!.value as Parameters<typeof '+i.local+'>[1];\n').join('')+
  ' const results:material.CapturedResult[]=[];const observations:Observation[]=[];\n'+
  workflow.steps.map((s,n)=>{
   const i=imports.findIndex(i=>i.selector===s.operation_ref&&i.action_sha256===s.action_sha256);if(i<0)return fail('missing exact forward import');
   return ' {\n  let args:ReturnType<typeof material.steps['+q(s.step_id)+']["arguments"]>;\n'+
    '  try{args=material.steps['+q(s.step_id)+'].arguments(input,results);}catch{observations.push(observe('+n+',notStarted()));return stopped(input,results,observations,ids);}\n'+
    '  let raw:unknown;\n  try{raw=await call'+i+'(args,dep'+i+');}catch{observations.push(observe('+n+',unknown("threw")));return stopped(input,results,observations,ids);}\n'+
    '  const settlement=inspectOperationSettlement(raw,'+q(s.failure_continuation)+(workflow.composition_contract_sha256?','+literal(s.precommit_stages??[]):'')+');observations.push(observe('+n+',settlement));\n'+
    '  if(settlement.commit_status!=="committed")return stopped(input,results,observations,ids);\n'+
    '  try{results.push(material.captureResult(input,'+q(s.step_id)+',Object.getOwnPropertyDescriptor(raw,"value")!.value));}catch{return stopped(input,results,observations,ids,"committed-result-invalid");}\n }\n';
  }).join('')+
  ' let value:ReturnType<typeof material.result>;\n try{value=material.result(input,results);}catch{return stopped(input,results,observations,ids,"result-materialization-failed");}\n'+
  ' return freeze({status:"succeeded",value,evaluation:evaluate(observations,ids,null),recovery_bindings:null});\n};\n';
 return 'import {createHash} from "node:crypto";\nimport * as material from '+q(materialPath)+';\nexport type {WorkflowInput} from '+q(materialPath)+';\nimport type {WorkflowInput} from '+q(materialPath)+';\n'+
  imports.map(i=>'import {'+i.symbol+' as '+i.local+'} from '+q(i.path)+';\n').join('')+
  'export type WorkflowDependencies=Readonly<{'+dependencyTypes+'}>;\n'+
  'const wf='+literal(wf)+';\nconst policyHash='+q(policy.policy_sha256)+';\nconst outcomeContract='+q(WORKFLOW_OUTCOME_CONTRACT_SHA256)+';\n'+
  'const prefixTemplates:readonly PrefixTemplate[]='+literal(templates)+';\n'+(workflow.composition_contract_sha256?composedWorkflowSettlementSupport():WORKFLOW_SETTLEMENT_SUPPORT)+runtime+prepare+execute;
}
