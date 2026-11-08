import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {FactoryBinding} from '../generation/configured-factories.js';
import type {TypedRecordContract,TypedType} from '../typed-operation/contracts.js';
import type {SumRecipe} from './reconciled-sum-controls.js';
import {canonicalJson} from '../input/source-manifest.js';
import {createRecordRuleReference} from './reconciled-rule-reference.js';
export const SEMANTIC_RECORD_WITNESS_DEFINITION_SHA256='a7302b5f05ec2d6ac0ee364662b99bc80291242960bb54629f8a319b4fb4c806';
export class RecordWitnessUnavailable extends Error {}
export interface RecordWitnessProbe {readonly recipe:SumRecipe;readonly expected:Readonly<{ok:boolean;failure_codes:readonly string[];trace:Readonly<{route:'create';phases:readonly string[];validators:readonly Readonly<{rule:string;outcome:'pass'|'fail'}>[]} >}>;}
export interface RecordWitnessDependency {
 readonly selector:string;readonly relative_path:string;readonly symbol:string;readonly callable:string;
 readonly kind:'Entity'|'Value Object';readonly plain:false;readonly record:TypedRecordContract;readonly binding:FactoryBinding;
 probes:readonly RecordWitnessProbe[];
}
type Reference=ReturnType<typeof createRecordRuleReference>;
export function evaluateRecordWitness(d:RecordWitnessDependency,reference:Reference,recipe:SumRecipe,validators=d.binding.base_validators):RecordWitnessProbe['expected']{
  const facts=reference.fact({kind:'named',selector:d.selector},recipe),trace:{rule:string;outcome:'pass'|'fail'}[]=[];
  for(const v of validators){
   const rule=reference.rules.get(v.rule)!;
   const args=new Map(v.arguments.map(a=>{let value=facts;for(const segment of a.path??[a.field!])value=value[segment];return [a.parameter,{type:rule.parameters.find(p=>p.name===a.parameter)!.type,value}] as const;}));
   const outcome=reference.evaluate(v.rule,args)?'pass':'fail';trace.push({rule:v.rule,outcome});
   if(outcome==='fail')return {ok:false,failure_codes:['RULE_FAIL:'+v.rule],trace:{route:'create',phases:['normalize'],validators:trace}};
  }
  return {ok:true,failure_codes:[],trace:{route:'create',phases:['normalize',...(d.kind==='Entity'?['resolve-identity']:[]),'form','freeze'],validators:trace}};
 }
/** Bounded deterministic search is a witness finder, never a satisfiability claim. */
export function recordWitnesses(d:RecordWitnessDependency,reference:Reference,samples:(t:TypedType)=>SumRecipe[]):SumRecipe[]{
 const fields=[...d.record.properties].sort((a,b)=>a.name<b.name?-1:1),values=fields.map(f=>samples(f.type));
 if(values.some(v=>!v.length))throw new RecordWitnessUnavailable('record has no child witness:'+d.selector);
 const seen=new Set<string>(),accepted:SumRecipe[]=[],probes:RecordWitnessProbe[]=[],failures=new Set<string>();
 let attempts=0;
 const add=(vector:readonly SumRecipe[])=>{
  if(attempts++>=4096)return;
  const recipe:SumRecipe={tag:'record',selector:d.selector,fields:Object.fromEntries(fields.map((f,i)=>[f.name,vector[i]!]))},encoded=canonicalJson(recipe);
  if(seen.has(encoded))return;seen.add(encoded);
  const expected=evaluateRecordWitness(d,reference,recipe);
  if(expected.ok){if(accepted.length<16){accepted.push(recipe);probes.push({recipe,expected});}}
  else {const key=canonicalJson(expected);if(!failures.has(key)){failures.add(key);probes.push({recipe,expected});}}
 };
 // Complete vectors first, then each independent field, then Cartesian search.
 const baseline=values.map(v=>v[0]!);
 const width=Math.max(...values.map(v=>v.length));
 for(let n=0;n<width;n++)add(values.map(v=>v[n%v.length]!));
 for(let i=0;i<values.length;i++)for(const value of values[i]!){const vector=[...baseline];vector[i]=value;add(vector);}
 const visit=(i:number,vector:SumRecipe[])=>{if(attempts>=4096)return;if(i===values.length){add(vector);return;}for(const value of values[i]!){visit(i+1,[...vector,value]);if(attempts>=4096)break;}};
 visit(0,[]);
 if(!accepted.length)throw new RecordWitnessUnavailable('no satisfying base factory witness found within bounded search for '+d.selector+'; not an unsatisfiability proof');
 d.probes=probes;return accepted;
}
export function resolveRecordWitness(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,selector:string,reference:Reference):RecordWitnessDependency{
 const declaration=reference.get(selector);
 if(declaration.kind==='Enum')throw new TypeError('DS_RECORD_WITNESS:record required');
 const name=selector.split(':')[1]!.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join(''),symbol=name+'ValueComponent',callable='create'+name+'Factory';
 const matches=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(selector)&&m.exports.some(e=>e.kind==='value'&&e.name===symbol)&&m.exports.some(e=>e.kind==='value'&&e.name===callable));
 if(matches.length!==1)throw new TypeError('DS_RECORD_WITNESS:unique owned factory module required:'+selector);
 const binding=plan.selection.factories.find(f=>f.selector===selector);
 if(!binding||!binding.base_validators.length)throw new TypeError('DS_RECORD_WITNESS:explicit checked base validators required:'+selector);
 if(!graph.nodes.some(n=>n.selector===selector))throw new TypeError('DS_RECORD_WITNESS:source required');
 return {selector,relative_path:matches[0]!.relative_path,symbol,callable,kind:declaration.kind,plain:false,record:declaration.contract,binding,probes:[]};
}
