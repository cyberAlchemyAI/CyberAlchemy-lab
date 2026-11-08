import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {TypedType} from '../typed-operation/contracts.js';
import type {FactRecipe} from './reconciled-rule-facts.js';
import type {createOperationBinding} from './reconciled-operation-binding.js';
import type {createOperationProtocolReference} from './reconciled-cross-generator-operation-reference.js';
import {createEffectfulOperationReference} from './reconciled-operation-effect-reference.js';
import {captureOperationRecipe} from './reconciled-operation-values.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';

type Observation=ReturnType<ReturnType<typeof createOperationProtocolReference>['expected']>;
type Case={readonly id:string;readonly expected:Observation};
type Path=readonly (string|number)[];
type Failure={path:Path;owner:string;rule:string};
class SelectionBudget extends Error {}
/** Optimization budget only. Exhaustion preserves the full source family, never a prefix. */
export function createOperationProtocolSelection(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,binding:ReturnType<typeof createOperationBinding>){
 const b=binding.action.bindings,expr=b.result.value;
 const eligible=b.inputs.length===1&&binding.action.reads.length===0&&binding.action.writes.length===0&&
  expr.op==='path'&&expr.root===b.inputs[0]!.name&&expr.properties.length===0&&
  canonicalJson(b.inputs[0]!.type)===canonicalJson(b.result.type);
 const reference=eligible?createEffectfulOperationReference(graph,plan,binding.action):null;
 const factories=new Map(plan.selection.factories.map(f=>[f.selector,f]));
 const obligations=new Map<string,readonly string[]>(),reducible=new Set<string>();let work=0,disabled=!eligible;
 const tick=(depth=0)=>{if(depth>64||++work>4194304)throw new SelectionBudget();};
 const failures=(type:TypedType,value:any,at:Path=[],out:Failure[]=[],depth=0):Failure[]=>{
  tick(depth);
  if(type.kind==='scalar')return out;
  if(type.kind==='optional')return value===null?out:failures(type.element,value,at,out,depth+1);
  if(type.kind==='list'||type.kind==='set'){value.forEach((v:any,i:number)=>failures(type.element,v,[...at,i],out,depth+1));return out;}
  if(type.kind==='sum'){const variant=type.variants.find(v=>v.name===value.variant);if(!variant)throw new SelectionBudget();if(variant.payload)failures(variant.payload,value.payload,[...at,'payload'],out,depth+1);return out;}
  const definition=reference!.values.get(type);
  if(definition.kind==='Enum')return failures({kind:'sum',variants:definition.variants},value,at,out,depth+1);
  for(const p of definition.properties)failures(p.type as TypedType,value[p.name],[...at,p.name],out,depth+1);
  const factory=factories.get(type.selector);if(!factory?.base_validators.length)throw new SelectionBudget();
  for(const validator of factory.base_validators){
   const rule=reference!.facts.reference.rules.get(validator.rule);if(!rule)throw new SelectionBudget();
   const args=new Map(validator.arguments.map(a=>{
    let v=value;for(const key of a.path??[a.field!])v=v[key];
    const parameter=rule.parameters.find(p=>p.name===a.parameter);if(!parameter)throw new SelectionBudget();
    return [a.parameter,{type:parameter.type,value:v}] as const;
   }));
   if(!reference!.facts.reference.evaluate(validator.rule,args)){out.push({path:at,owner:type.selector,rule:validator.rule});break;}
  }
  return out;
 };
 const shape=(v:any,depth=0):unknown=>{
  tick(depth);
  if(v===null)return 'null';
  if(Array.isArray(v))return {length:v.length,items:v.map(x=>shape(x,depth+1))};
  if(typeof v==='object')return Object.fromEntries(Object.entries(v).map(([k,x])=>[k,k==='variant'?x:shape(x,depth+1)]));
  return typeof v;
 };
 const atoms=(v:any,at:Path=[],out:unknown[]=[],depth=0):unknown[]=>{
  tick(depth);if(v===null||typeof v!=='object')out.push([at,typeof v,String(v)]);
  else for(const[k,x]of Object.entries(v))atoms(x,[...at,k],out,depth+1);return out;
 };
 const normalizeTokens=(v:any,id:string,depth=0):unknown=>{
  tick(depth);
  if(Array.isArray(v)){
   const prefix='owned:'+id+':';
   if(v[0]==='owned'&&typeof v[1]==='string'&&v[1].startsWith(prefix))return ['owned','owned:CASE:'+v[1].slice(prefix.length)];
   return v.map(x=>normalizeTokens(x,id,depth+1));
  }
  if(v&&typeof v==='object')return Object.fromEntries(Object.entries(v).map(([k,x])=>[k,normalizeTokens(x,id,depth+1)]));
  return v;
 };
 const consider=(id:string,input:FactRecipe,observed:Observation,vectorOrigin:boolean)=>{
  if(disabled||!vectorOrigin)return;
  const outcome=Object.fromEntries((observed.semantic.outcome as any)[1].map(([k,v]:any)=>[k,v[1]]));
  if(outcome.status!=='failed'||outcome.stage!=='result')return;
  try{
   const raw=captureOperationRecipe(input),value=reference!.values.normalize(b.result.type,raw[b.inputs[0]!.name]);
   const invalid=failures(b.result.type,value);
   if(!invalid.length)throw new TypeError('OPERATION_SELECTION:missing result rejection');
   if(invalid.length>1)reducible.add(id);
   const first=canonicalJson(invalid[0]),keys=['shape:'+first+':'+canonicalJson(shape(raw))];
   for(const atom of atoms(raw))keys.push('atom:'+first+':'+canonicalJson(atom));
   for(let i=0;i<invalid.length;i++)for(let j=i+1;j<invalid.length;j++){tick();keys.push('invalid-pair:'+canonicalJson([invalid[i],invalid[j]]));}
   keys.push('protocol:'+canonicalJson(normalizeTokens(observed.calls,id)));
   obligations.set(id,[...new Set(keys)]);
  }catch(e){if(!(e instanceof SelectionBudget))throw e;disabled=true;obligations.clear();}
 };
 const select=<T extends Case>(cases:readonly T[])=>{
  const finish=(selected:readonly T[],reason:string,obligationCount:number)=>({
   cases:[...selected],
   selection:{policy:'obligation-boundary-v1',reason,source_case_count:cases.length,selected_case_count:selected.length,
    source_cases_sha256:sha256(canonicalJson(cases)),selected_ids_sha256:sha256(canonicalJson(selected.map(c=>c.id))),obligation_count:obligationCount}
  });
  if(disabled||!obligations.size)return finish(cases,disabled?(eligible?'optimizer-budget-full-family':'inapplicable-full-family'):'no-reducible-cases',0);
  const needed=new Set([...obligations.values()].flat()),selected=new Set(cases.filter(c=>!reducible.has(c.id)).map(c=>c.id));
  const count=needed.size;
  for(const id of selected)for(const key of obligations.get(id)??[])needed.delete(key);
  const owners=new Map<string,string[]>(),scores=new Map<string,number>();
  try{
   for(const [id,keys]of obligations){if(selected.has(id))continue;let score=0;for(const key of keys){tick();if(!needed.has(key))continue;score++;const rows=owners.get(key)??[];rows.push(id);owners.set(key,rows);}scores.set(id,score);}
   while(needed.size){
    let best:string|undefined,score=0;
    for(const c of cases){tick();if(selected.has(c.id))continue;const n=scores.get(c.id)??0;if(n>score){score=n;best=c.id;}}
    if(best===undefined)throw new TypeError('OPERATION_SELECTION:uncovered obligation');
    selected.add(best);for(const key of obligations.get(best)!){if(!needed.delete(key))continue;for(const id of owners.get(key)??[]){tick();scores.set(id,scores.get(id)!-1);}}
   }
  }catch(e){if(!(e instanceof SelectionBudget))throw e;return finish(cases,'optimizer-budget-full-family',count);}
  return finish(cases.filter(c=>selected.has(c.id)),'selected',count);
 };
 return {consider,select};
}
