import type {CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledProjectSnapshot} from '../input/project-model.js';
import {decodeOperationActionBindings} from '../typed-operation/action-bindings.js';
import type {TypedType} from '../typed-operation/contracts.js';
import {createStructuralFacts,type FactRecipe} from './reconciled-rule-facts.js';
import {createMappingReference} from './reconciled-mapping-reference.js';

export class OperationReferenceUnsupported extends Error {}
export type OperationFixtureMode='committed'|'rejected'|'indeterminate'|'begin-throw'|'commit-throw'|'rollback-throw'|
 'receipt-empty'|'receipt-unknown'|'receipt-extra'|'receipt-null'|'receipt-getter'|'receipt-inherited'|'receipt-symbol'|'receipt-hidden'|'receipt-array'|'receipt-undefined';
/** Tagged values make a bigint/string or list/record substitution observable. */
export function operationReferenceValue(v:any):unknown{
 if(v===null)return ['null'];
 if(typeof v==='bigint')return ['bigint',v.toString()];
 if(typeof v!=='object')return [typeof v,v];
 if(Array.isArray(v))return ['array',v.map(operationReferenceValue)];
 return ['record',Object.keys(v).sort().map(k=>[k,operationReferenceValue(v[k])])];
}
/** Verification oracle, not an executor. Call after public source/binding checking.
 * This first slice refuses effects and owned records rather than fabricating a store or validator.
 */
export function createRecordFreeOperationReference(graph:CompiledProjectGraph,value:unknown){
 assertCompiledProjectSnapshot(graph);
 const bindings=decodeOperationActionBindings(value),node=graph.nodes.find(n=>n.selector===bindings.selector);
 if(node?.kind!=='Operation')throw new TypeError('OPERATION_REFERENCE:source Operation required');
 const unsupported=(why:string):never=>{throw new OperationReferenceUnsupported('OPERATION_REFERENCE_UNSUPPORTED:'+why);};
 if(bindings.reads.length||bindings.writes.length||bindings.events.length)unsupported('Entity reads/writes and Event controls pending');
 const facts=createStructuralFacts(graph,bindings.guards.map(g=>g.selector),[bindings.result.value,...bindings.guards.flatMap(g=>g.arguments.map(a=>a.value))]);
 const reference=createMappingReference(graph),seen=new Set<string>();
 const checkType=(t:TypedType,depth=0):void=>{
  if(depth>64)unsupported('type depth');
  if(t.kind==='scalar')return;
  if(t.kind==='optional'||t.kind==='list'||t.kind==='set'){checkType(t.element,depth+1);return;}
  if(t.kind==='sum'){for(const v of t.variants)if(v.payload)checkType(v.payload,depth+1);return;}
  const d=reference.get(t);if(d.kind!=='Enum')unsupported('owned record '+t.selector);
  if(seen.has(t.selector))unsupported('recursive Enum closure '+t.selector);
  seen.add(t.selector);for(const v of d.variants)if(v.payload)checkType(v.payload,depth+1);seen.delete(t.selector);
 };
 bindings.inputs.forEach(p=>checkType(p.type));checkType(bindings.result.type);
 // Guard references may introduce types not present in the Operation input list.
 const rules=new Set<string>();
 const checkRule=(selector:string)=>{
  if(rules.has(selector))return;rules.add(selector);
  const rule=facts.reference.rules.get(selector);if(!rule)throw new TypeError('OPERATION_REFERENCE:missing Rule');
  rule.parameters.forEach(p=>checkType(p.type));
  const walk=(v:any):void=>{if(!v||typeof v!=='object')return;if(v.op==='rule_ref')checkRule(v.selector);for(const x of Object.values(v))if(Array.isArray(x))x.forEach(walk);else walk(x);};walk(rule.expression);
 };bindings.guards.forEach(g=>checkRule(g.selector));
 const expected=(recipe:FactRecipe,mode:OperationFixtureMode='committed')=>{
  const trace:string[]=[],batches:unknown[]=[];
  const finish=(outcome:unknown)=>({outcome:operationReferenceValue(outcome),trace,batches,read_calls:0,
   settled_before_begin:false,settled_before_commit:false,settled_before_rollback:false,getter_reads:0,input_changed:false});
  const failure=(status:string,stage:string,code:string,cleanupFailed=false)=>({status,stage,code,continuation:node.body.failure_continuation,cleanupFailed});
  let scope:Map<string,{type:TypedType;value:any}>;
  try{
   const fields=reference.members(recipe,'OPERATION_INPUT');
   if(Object.keys(fields).length!==bindings.inputs.length||bindings.inputs.some(p=>!Object.hasOwn(fields,p.name)))throw new TypeError('OPERATION_INPUT');
   scope=new Map(bindings.inputs.map(p=>[p.name,{type:p.type,value:reference.normalize(p.type,fields[p.name]!,'OPERATION_INPUT')}]));
  }catch(e){if(e instanceof TypeError&&e.message==='OPERATION_INPUT')return finish(failure('failed','input','OPERATION_INPUT'));throw e;}
  trace.push('begin');
  if(mode==='begin-throw'){trace.push('begin-rejected');return finish(failure('failed','begin','BEGIN_FAILED'));}
  trace.push('begin-resolved');
  for(const guard of bindings.guards)if(!facts.reference.guard(guard,scope)){
   trace.push('rollback',mode==='rollback-throw'?'rollback-rejected':'rollback-resolved');
   return finish(failure('rejected','guard','RULE_REJECTED:'+guard.selector,mode==='rollback-throw'));
  }
  const result=reference.value(bindings.result.value,scope).value;
  trace.push('commit');batches.push(operationReferenceValue({writes:[],events:[]}));
  trace.push(mode==='commit-throw'?'commit-rejected':'commit-resolved');
  if(mode==='committed'||mode==='rollback-throw')return finish({status:'committed',value:result});
  if(mode==='rejected')return finish(failure('rejected','commit','COMMIT_REJECTED'));
  if(mode==='indeterminate')return finish(failure('indeterminate','commit','COMMIT_INDETERMINATE'));
  return finish(failure('indeterminate','commit',['receipt-unknown','receipt-empty'].includes(mode)?'INVALID_COMMIT_RECEIPT':'COMMIT_UNCERTAIN'));
 };
 return {bindings,facts,expected};
}
