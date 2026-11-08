/** Source-bound causal input for a Query invoked by a protected Workflow step.
 * The parent step, durable state and Query Entry must still pass fresh Auth.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {evaluateCommerceFlowDataV1} from './commerce-flow-expression-data-v1.js';
import {assertCommerceWorkflowProtectedCallBindingV1,type CommerceWorkflowProtectedCallBindingV1}
 from './commerce-workflow-protected-call-binding-v1.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1}
 from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1}
 from './commerce-service-storage-v1.js';
import type {EntryContractV1} from './commerce-data-v1.js';

export class CommerceWorkflowDelegatedQueryErrorV1 extends Error {
 readonly code='ForeignWorkflowCall' as const;
 constructor(detail:string){super(detail);this.name='CommerceWorkflowDelegatedQueryErrorV1';}
}
const bad=(detail:string):never=>{throw new CommerceWorkflowDelegatedQueryErrorV1(detail);};
const record=(value:unknown):value is Record<string,unknown>=>!!value&&typeof value==='object'&&
 !Array.isArray(value)&&!host.isProxy(value)&&[Object.prototype,null].includes(Object.getPrototypeOf(value));
const fieldPath=(value:unknown):readonly string[]=>{
 if(!record(value))return [];
 if(value.op==='var'&&typeof value.name==='string')return [value.name];
 if(value.op==='field'&&typeof value.field==='string')return [...fieldPath(value.value),value.field];
 return [];
};
const guardedParameters=(expression:unknown,causalName:string):ReadonlySet<string>=>{
 const covered=new Set<string>();let nodes=0;
 const visit=(value:unknown,depth:number):void=>{
  if(!record(value))bad('source Query resource condition must be a conjunction of causal equalities');
  const node=value as Record<string,unknown>;
  if(++nodes>4096||depth>64)bad('source Query resource condition exceeds its bound');
  if(node.op==='binary'&&node.operator==='and'){
   visit(node.left,depth+1);visit(node.right,depth+1);return;
  }
  if(node.op!=='binary'||node.operator!=='eq')
   bad('source Query resource condition must be a conjunction of causal equalities');
  const left=fieldPath(node.left),right=fieldPath(node.right);
  if(left.length===2&&left[0]==='input'&&right.length===2&&right[0]===causalName)
   covered.add(left[1]!);
  else if(right.length===2&&right[0]==='input'&&left.length===2&&left[0]===causalName)
   covered.add(right[1]!);
  else bad('source Query equality must bind input to original causal data');
 };
 visit(expression,0);return covered;
};

export interface CommerceWorkflowDelegatedQueryV1 {
 readonly arguments:Readonly<Record<string,unknown>>;
 readonly causal_projection:Readonly<Record<string,unknown>>;
 recheck():void;
}

/** The Query can use only a field of the version-pinned durable Workflow
 * record or of the already dispatched parent call. Its resource condition
 * must admit the exact arguments produced at the source read call. */
export function deriveCommerceWorkflowDelegatedQueryV1(
 protectedCall:CommerceWorkflowProtectedCallBindingV1,
 workflow:CommerceWorkflowCoordinationBindingV1,
 storage:CommerceServiceStorageOwnerV1,
 entry:EntryContractV1,
 sourceSha:string,
 argumentsAtCall:Readonly<Record<string,unknown>>,
):CommerceWorkflowDelegatedQueryV1 {
 assertCommerceWorkflowProtectedCallBindingV1(protectedCall);
 assertCommerceWorkflowCoordinationBindingV1(workflow);
 assertCommerceServiceStorageOwnerV1(storage);
 if(!record(argumentsAtCall))bad('source Query arguments must be a plain record');
 const argumentKeys=Reflect.ownKeys(argumentsAtCall),descriptors=Object.getOwnPropertyDescriptors(argumentsAtCall);
 if(argumentKeys.length>64||argumentKeys.some(key=>typeof key!=='string'||
  !descriptors[key]?.enumerable||!Object.hasOwn(descriptors[key]!,'value')))
  bad('source Query arguments must be a bounded data-only record');
 const argumentsCopy=coreFreeze(Object.assign(Object.create(null),argumentsAtCall));
 const inspect=()=>{
  const parent=protectedCall.recheck(),selected=workflow.inspect(),store=storage.inspect(),access=entry.access;
  const causal=access.resource_bindings.length===1?access.resource_bindings[0]:null;
  if(parent.source_capture_sha256!==sourceSha||selected.source_capture_sha256!==sourceSha||
   store.source_capture_sha256!==sourceSha||parent.store_id!==store.store_id||
   parent.workflow!==selected.workflow.name||parent.caller_service!==selected.owner_service||
   store.service!==selected.owner_service||parent.phase!=='Dispatched'||
   entry.invokes.role!=='Query'||entry.service===parent.caller_service||
   access.principal_kind!=='service'||access.caller!==parent.caller_service||
   access.worker_lifetime!=='not-applicable'||access.resource_phase!=='causal-before-invocation'||
   access.matching_replay_resource_check!=='same-causal-input'||
   access.current_action!=='before-replay-and-effects'||!access.resource_condition||
   !causal||causal.origin.kind!=='workflow-journal'||
   causal.origin.declaration!==parent.workflow||
   causal.abi!=='craft.commerce-causal-call/v1-candidate'||
   causal.selector.split('/').at(-1)!=='original-step-journal'||
   entry.parameters.length!==Object.keys(argumentsCopy).length||
   entry.parameters.some(parameter=>!Object.hasOwn(argumentsCopy,parameter.name))||
   !causal.required_fields.length||causal.required_fields.length!==Object.keys(causal.fields).length||
   causal.required_fields.some(field=>!Object.hasOwn(causal.fields,field)))
   bad('parent Workflow and source Query Entry differ');
  const resourceCondition=access.resource_condition,causalBinding=causal;
  if(!resourceCondition||!causalBinding)bad('checked Query resource condition and causal binding required');
  const condition=resourceCondition as NonNullable<typeof resourceCondition>,binding=causalBinding as NonNullable<typeof causalBinding>;
  const guarded=guardedParameters(condition.expression,binding.name);
  if(entry.parameters.some(parameter=>!guarded.has(parameter.name)))
   bad('every source Query argument must be bound to original causal data');
  const progressValue=storage.inspectStoredRecord(selected.workflow.durable_state,0,{orderId:parent.order_id});
  if(!record(progressValue)||progressValue.orderId!==parent.order_id||progressValue.version!==parent.progress_version)
   bad('version-pinned original Workflow state required');
  const progress=progressValue as Record<string,unknown>;
  const projection:Record<string,unknown>=Object.create(null);
  for(const field of binding.required_fields){
   const fromParent=Object.hasOwn(parent.causal_projection,field),fromProgress=Object.hasOwn(progress,field);
   if(!fromParent&&!fromProgress||fromParent&&fromProgress&&
    !isDeepStrictEqual(parent.causal_projection[field],progress[field]))
    bad('original causal field missing or contradictory');
   projection[field]=fromParent?parent.causal_projection[field]:progress[field];
  }
  if(Object.hasOwn(projection,'orderId')&&projection.orderId!==parent.order_id)
   bad('causal order differs from dispatched parent');
  let fuel=0;
  const allowed=evaluateCommerceFlowDataV1(condition.expression,
   '$.access.resource_condition.expression',
   Object.freeze({input:argumentsCopy,[binding.name]:coreFreeze(projection)}),{
    charge(){if(++fuel>4096)bad('source Query resource guard exceeded its bound');},
    pure(){return bad('source Query resource guard requires an unsupported pure call');},
    native(){return bad('source Query resource guard requires an unsupported native call');},
    context(){return bad('source Query resource guard requires an unsupported context');},
    isNullaryEnum(){return false;},
   });
  if(allowed!==true)bad('source Query resource guard denied the delegated arguments');
  return coreFreeze(projection);
 };
 const initial=inspect();
 const owner:CommerceWorkflowDelegatedQueryV1=Object.freeze({arguments:argumentsCopy,
  causal_projection:initial,recheck(){if(!isDeepStrictEqual(inspect(),initial))bad('causal Query evidence changed');}});
 return owner;
}
