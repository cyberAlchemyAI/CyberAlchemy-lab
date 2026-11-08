/** A checked effect intent can establish an Entry resource equality before effects.
 * This only proves a source assignment from a live current-invocation context;
 * it does not execute or commit the declared transaction.
 * Open Questions: docs/COMMERCE-AUTH-READY-BRIDGE-V1.md#open-questions. */
import type {EntryContractV1,EffectPlanV1,FlowExprV1,OperationControlStepV1,TransactionStepV1} from './commerce-data-v1.js';

type Field={binding:string;name:string;kind:'var'|'private-context';sourceType:string|null;abi:string|null};
const field=(value:FlowExprV1):Field|null=>{
 if(value.op!=='field')return null;
 if(value.value.op==='var')return {binding:value.value.name,name:value.field,kind:'var',sourceType:null,abi:null};
 if(value.value.op==='private_context'&&value.value.public_constructor===false&&value.value.custody==='required-from-original-native-owner')
  return {binding:value.value.binding,name:value.field,kind:'private-context',sourceType:value.value.source_type,abi:value.value.abi};
 return null;
};
const same=(a:Field,b:Field)=>a.binding===b.binding&&a.name===b.name&&a.kind===b.kind&&a.sourceType===b.sourceType&&a.abi===b.abi;

/** Fail closed for all expressions, resource origins, and effect paths outside
 * the exact immutable-context-to-create-field equality supported here. */
export function qualifiesCommerceEffectIntentV1(entry:EntryContractV1,plan:EffectPlanV1,scope:Readonly<Record<string,unknown>>):boolean {
 const access=entry.access,bindings=access.resource_bindings;
 if(plan.operation.module+'.'+plan.operation.name!==entry.invokes.module+'.'+entry.invokes.name||
    entry.invokes.role!=='Operation'||plan.service!==entry.service||
    access.resource_phase!=='fresh-intent-before-effects'||bindings.length!==2||
    access.resource_condition?.local_records.length!==0)return false;
 const current=bindings.find(b=>b.origin.kind==='current-invocation'),intent=bindings.find(b=>b.origin.kind==='fresh-effect-intent');
 if(!current||!intent||current===intent||current.custody!=='required-from-original-registered-owner'||intent.custody!=='required-from-original-registered-owner'||
    current.type.kind!=='private-projection'||current.type.source_type!==access.context.source_type||
    !plan.contexts.some(c=>c.binding===current.name&&c.source_type===access.context.source_type&&c.abi===access.context.abi)||
    intent.type.kind!=='data'||intent.type.type.kind!=='record'||
    intent.origin.declaration!==plan.operation.module+'.'+plan.operation.name||!intent.origin.transaction||!intent.origin.binding)return false;
 const intentEntity=intent.type.type.name;
 const condition=access.resource_condition?.expression;
 if(!condition||condition.op!=='binary'||condition.operator!=='eq')return false;
 const left=field(condition.left),right=field(condition.right);
 if(!left||!right)return false;
 const intentSide=left.binding===intent.name&&right.binding===current.name?left:
  right.binding===intent.name&&left.binding===current.name?right:null;
 const contextSide=intentSide===left?right:intentSide===right?left:null;
 if(!intentSide||!contextSide||intentSide.kind!=='var'||contextSide.kind!=='private-context'||
    contextSide.sourceType!==access.context.source_type||contextSide.abi!==access.context.abi||
    !intent.required_fields.includes(intentSide.name)||!current.required_fields.includes(contextSide.name)||
    !Object.hasOwn(scope,contextSide.name)||scope.kind!=='customer'||typeof scope[contextSide.name]!=='string'||!scope[contextSide.name])return false;
 // A later let/read/call binder cannot replace the native context that the
 // create assignment and access condition both name.
 if(plan.body.some(step=>'name' in step&&(step.name===current.name||step.name===intent.name)||
    step.kind==='read-set'&&(step.item===current.name||step.item===intent.name)))return false;
 const transactions=plan.body.filter((step):step is Extract<OperationControlStepV1,{kind:'transaction'}>=>
  step.kind==='transaction'&&step.transaction.name===intent.origin.transaction);
 if(transactions.length!==1)return false;
 const transaction=transactions[0]!.transaction;
 const creates=transaction.body.filter((step):step is Extract<TransactionStepV1,{kind:'mutation'}>=>
  step.kind==='mutation'&&step.operation==='create'&&step.binding===intent.origin.binding&&step.target===intentEntity);
 if(creates.length!==1||transaction.body.some(step=>step.kind==='let'&&(step.name===current.name||step.name===intent.name)||
    step.kind==='mutation'&&step.binding===intent.origin.binding&&step!==creates[0]))return false;
 const assigned=creates[0]!.fields.filter(f=>f.name===intentSide.name);
 return assigned.length===1&&assigned[0]!.value.local_records.length===0&&
  !!field(assigned[0]!.value.expression)&&same(field(assigned[0]!.value.expression)!,contextSide);
}
