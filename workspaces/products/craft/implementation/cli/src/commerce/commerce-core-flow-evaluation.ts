/** Closed typed callsite data for structured roles; never executes or acquires
 * a native owner. Public producer-schema integration remains separate.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import type {ExprV1} from './commerce-data-v1.js';
import type {CoreContextRequirement} from './commerce-core-context.js';
import type {CoreNativeExpressionCall} from './commerce-core-flow-expression.js';
import type {CoreValueType} from './commerce-core-types.js';
import {coreFreeze,coreSourceFail as fail,type CoreSourceRange} from './commerce-core-syntax.js';

type FlowMember<T>=T extends ExprV1?CoreFlowEvaluation:T extends readonly(infer V)[]?readonly FlowMember<V>[]:T extends object?{readonly [K in keyof T]:FlowMember<T[K]>}:T;
type FlowPure<T>=T extends unknown?{readonly [K in keyof T]:FlowMember<T[K]>}:never;
export type CoreFlowEvaluation=FlowPure<ExprV1>|{
 readonly op:'native_observation';readonly context:string;readonly source_type:string;readonly abi:string;readonly method:string;
 readonly arguments:readonly {readonly parameter:string|null;readonly value:CoreFlowEvaluation;readonly allowed_text:readonly string[]|null}[];
 readonly result:CoreValueType;readonly placement:'original-source-expression-callsite';readonly custody:'required-from-original-native-owner';
}|{
 readonly op:'private_context';readonly binding:string;readonly source_type:string;readonly abi:string;
 readonly fields:readonly {readonly name:string;readonly type:CoreValueType}[];readonly public_constructor:false;readonly custody:'required-from-original-native-owner';
};
export interface CoreFlowLocalRecord {readonly name:string;readonly fields:readonly {readonly name:string;readonly type:CoreValueType}[];readonly public_constructor:false;readonly qualification:'source-local-projection-data-only'}
export function buildCoreFlowEvaluation(expression:ExprV1,result:CoreValueType,calls:readonly CoreNativeExpressionCall[],env:ReadonlyMap<string,CoreValueType>,contexts:ReadonlyMap<string,CoreContextRequirement>,records:ReadonlyMap<string,readonly {readonly name:string;readonly type:CoreValueType}[]>,where:CoreSourceRange):{readonly evaluation:CoreFlowEvaluation;readonly local_records:readonly CoreFlowLocalRecord[]} {
 const native=new Map(calls.map(c=>[c.binding,c])),local=new Map<string,CoreFlowLocalRecord>();let nodes=0;
 if(native.size!==calls.length)fail('InvalidContract',where,'duplicate native expression binding');
 const retain=(type:CoreValueType,depth=0):void=>{
  if(depth>64)fail('ResourceLimit',where,'source-local projection nesting limit');
  if(type.kind==='List'||type.kind==='optional')return retain(type.value,depth+1);
  if(type.kind==='outcome'){retain(type.state,depth+1);retain(type.intent,depth+1);return;}
  if(type.kind!=='record'||!records.has(type.name)||local.has(type.name))return;
  const fields=records.get(type.name)!;local.set(type.name,{name:type.name,fields,public_constructor:false,qualification:'source-local-projection-data-only'});
  for(const field of fields)retain(field.type,depth+1);
 };
 const lower=(value:unknown,depth=0):unknown=>{
  if(!value||typeof value!=='object')return value;
  if(++nodes>65536||depth>128)fail('ResourceLimit',where,'native expression evaluation expansion limit');
  if(Array.isArray(value))return value.map(v=>lower(v,depth+1));
  const v=value as Record<string,unknown>;
  if(v.op==='var'&&typeof v.name==='string'){
   const call=native.get(v.name);
   if(call){retain(call.result);return {op:'native_observation',context:call.context,source_type:call.source_type,abi:call.abi,method:call.method,arguments:call.arguments.map(a=>{
    for(const record of a.value.local_records){const previous=local.get(record.name);if(previous&&JSON.stringify(previous)!==JSON.stringify(record))fail('InvalidContract',where,'inconsistent nested private projection');local.set(record.name,record);}
    return {parameter:a.parameter,value:a.value.evaluation,allowed_text:a.allowed_text};
   }),result:call.result,placement:call.placement,custody:call.custody};}
   const context=contexts.get(v.name);if(context){for(const field of context.properties)retain(field.type);return {op:'private_context',binding:v.name,source_type:context.source_type,abi:context.abi,fields:context.properties,public_constructor:false,custody:'required-from-original-native-owner'};}
   const type=env.get(v.name);if(type)retain(type);
  }
  // Typed binder/literal annotations can refer to source-local records even
  // when their runtime variable is supplied by a loop or match payload.
  if(v.kind==='record'&&typeof v.name==='string')retain({kind:'record',name:v.name});
  const out:Record<string,unknown>={};for(const [key,child]of Object.entries(v))out[key]=lower(child,depth+1);return out;
 };
 retain(result);const evaluation=lower(expression) as CoreFlowEvaluation;
 // Nested native arguments were checked separately. Charge their inlined
 // trees too, including repeated branch positions, before exposing data.
 const pending:{value:unknown;depth:number}[]=[{value:evaluation,depth:0}];let expanded=0;
 while(pending.length){const {value,depth}=pending.pop()!;if(!value||typeof value!=='object')continue;if(++expanded>65536||depth>128)fail('ResourceLimit',where,'complete native expression evaluation expansion limit');for(const child of Object.values(value))pending.push({value:child,depth:depth+1});}
 return coreFreeze({evaluation,local_records:[...local.values()].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0)});
}
