import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {decodeTypedSumContract,type TypedType,type TypedSumContract} from '../typed-operation/contracts.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {createRecordRuleReference,RuleWitnessCapacity} from './reconciled-rule-reference.js';
import {recordWitnesses,resolveRecordWitness,RecordWitnessUnavailable,type RecordWitnessDependency} from './reconciled-record-witness.js';

export interface SumRecipe {
 readonly tag:string;readonly value?:string|boolean;readonly format?:'string'|'bigint'|'number';
 readonly variant?:string;readonly payload?:SumRecipe;readonly items?:readonly SumRecipe[];
 readonly selector?:string;readonly input?:SumRecipe;readonly mode?:string;readonly base?:SumRecipe;
 readonly fields?:Readonly<Record<string,SumRecipe>>;
}
export type Dependency=Readonly<{kind:'Enum';selector:string;relative_path:string;symbol:string;plain:boolean;contract:TypedSumContract}>|RecordWitnessDependency;
export class WitnessUnavailable extends Error {}
export const isWitnessUnavailable=(error:unknown):error is Error=>error instanceof WitnessUnavailable||error instanceof RecordWitnessUnavailable||error instanceof RuleWitnessCapacity;
const fail=(message:string):never=>{throw new TypeError('DS_RECONCILED_VALUE_CONTEXT:'+message);};
const part=(s:string)=>s.length+':'+s;
const shape=(c:TypedSumContract):TypedType=>({kind:'sum',variants:c.variants});
const badRecipe=(base:SumRecipe,mode:string):SumRecipe=>({tag:'bad',base,mode});
/** Native lookup is supplied by the selected backend, never a fabricated plan. */
export interface OwnedValueBindings {
 readonly record:(selector:string,reference:ReturnType<typeof createRecordRuleReference>)=>RecordWitnessDependency;
 readonly enumeration:(selector:string,contract:TypedSumContract)=>Extract<Dependency,{kind:'Enum'}>;
 readonly closure:(root:Dependency,dependencies:Readonly<Record<string,Dependency>>)=>string[];
}
export function createBoundOwnedValueContext(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,bindings:OwnedValueBindings,includeExtensions=false){
  const valueContract=sha256(getReconciledSource('factory')),dependencies:Record<string,Dependency>={},reference=createRecordRuleReference(graph);
  const collect=(selector:string,depth=0)=>{
   if(depth>64)throw new WitnessUnavailable('bounded sum witness depth exceeded');
   if(dependencies[selector])return;
   const n=graph.nodes.find(n=>n.selector===selector)??fail('missing checked dependency:'+selector);
   const walk=(t:TypedType)=>{if(t.kind==='named')collect(t.selector,depth+1);else if(t.kind==='sum')for(const v of t.variants){if(v.payload)walk(v.payload);}else if('element' in t)walk(t.element);};
   if(n.kind==='Entity'||n.kind==='Value Object'){
    const record=bindings.record(selector,reference);dependencies[selector]=record;
    record.record.properties.forEach(p=>walk(p.type));return;
   }
   if(n.kind!=='Enum')throw new WitnessUnavailable('sum requires unsupported named witness:'+selector+' ('+n.kind+')');
   const contract=decodeTypedSumContract(n.body.typed_contract);
   dependencies[selector]=bindings.enumeration(selector,contract);
   walk(shape(contract));
  };collect(node.selector);
  const root=dependencies[node.selector]!;
  const rootShape:TypedType=root.kind==='Enum'?shape(root.contract):{kind:'named',selector:node.selector};
  const ref=(t:TypedType,r:SumRecipe):{key:string;view:unknown;owned_key?:string}=>{
   if(t.kind==='scalar')return {key:part(t.name)+part(t.name==='Bool'?(r.value?'1':'0'):String(r.value)),view:{kind:t.name,value:r.value}};
   if(t.kind==='optional'){if(r.tag==='null')return {key:part('Optional')+part('absent'),view:null};const child=ref(t.element,r);return {key:part('Optional')+part('present')+part(child.key),view:child.view};}
   if(t.kind==='list'||t.kind==='set'){
    const entries=r.items!.map(v=>ref(t.element,v));if(t.kind==='set')entries.sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0);
    return {key:part(t.kind==='set'?'Set':'List')+part(String(entries.length))+entries.map(e=>part(e.key)).join(''),view:{kind:t.kind,frozen:true,plain:true,items:entries.map(e=>e.view)}};
   }
   if(t.kind==='sum'){
    const v=t.variants.find(v=>v.name===r.variant)??fail('witness variant'),child=v.payload?ref(v.payload,r.payload!):null;
    return {key:part('Sum')+part(v.name)+(child?part('payload')+part(child.key):part('no-payload')),view:{kind:'sum',variant:v.name,frozen:true,keys:child?['payload','variant']:['variant'],...(child?{payload:child.view}:{})}};
   }
   const d=dependencies[t.selector]??fail('witness dependency');
   if(d.kind!=='Enum'){
    const fields=[...d.record.properties].sort((a,b)=>a.name<b.name?-1:1),values=fields.map(f=>ref(f.type,r.fields![f.name]!));
    const tag=(type:TypedType):string=>type.kind==='scalar'?type.name:type.kind==='sum'?'Sum':type.kind==='named'?(dependencies[type.selector]!.kind==='Entity'?'Entity':dependencies[type.selector]!.kind==='Value Object'?'ValueObject':dependencies[type.selector]!.plain?'Enum':'Sum'):type.kind[0]!.toUpperCase()+type.kind.slice(1);
    const key=part(t.selector)+part(valueContract)+fields.map((f,i)=>d.kind==='Entity'&&!f.identity?'':part(f.name)+part(tag(f.type))+part(values[i]!.key)).join('');
    return {key:part(d.kind==='Entity'?'Entity':'ValueObject')+part(key),owned_key:key,view:{kind:'named-record',selector:t.selector,record_kind:d.kind,owned:true,frozen:true,fields_frozen:true,fields_keys:fields.map(f=>f.name),fields:Object.fromEntries(fields.map((f,i)=>[f.name,values[i]!.view]))}};
   }
   if(d.plain)return {key:part('Enum')+part(part(t.selector)+part(valueContract)+part(r.variant!)),view:{kind:'named-enum',selector:t.selector,owned:true,frozen:true,variant:r.variant}};
   const child=ref(shape(d.contract),r.input!);
   return {key:part('NamedSum')+part(part(t.selector)+part(valueContract)+part(child.key)),view:{kind:'named-sum',selector:t.selector,owned:true,value:child.view}};
  };
  let expansion=0;
  const count=<T>(values:T[]):T[]=>{expansion+=values.length;if(expansion>4096)throw new WitnessUnavailable('bounded sum witness expansion exceeded');return values;};
  const recordCache=new Map<string,SumRecipe[]>(),literals=reference.seeds(Object.values(dependencies).flatMap(d=>d.kind==='Enum'?[]:[...d.binding.base_validators,...(includeExtensions?d.binding.extensions.flatMap(e=>e.validators):[])].map(v=>v.rule)));
  const samples=(t:TypedType,depth=0):SumRecipe[]=>{
   if(depth>64)throw new WitnessUnavailable('bounded sum witness depth exceeded');
   if(t.kind==='scalar'){
    const seeds=literals.filter(l=>l.type===t.name).map(l=>l.value);
    return count(t.name==='UInt64'?[...new Set(['0','1','9007199254740993','18446744073709551615',...seeds.map(String)])].flatMap(value=>(['string','bigint',...(BigInt(value)<=9007199254740991n?['number']:[])] as const).map(format=>({tag:'scalar',value,format} as SumRecipe))):t.name==='Bool'?[{tag:'scalar',value:false},{tag:'scalar',value:true}]:[...new Set(['','alpha','β😀',...seeds.map(String)])].map(value=>({tag:'scalar',value})));
   }
   if(t.kind==='optional')return count([{tag:'null'},...samples(t.element,depth+1)]);
   if(t.kind==='list'||t.kind==='set'){
    const values=samples(t.element,depth+1),unique=[...new Map(values.map(r=>[ref(t.element,r).key,r])).values()],out:SumRecipe[]=[{tag:t.kind,items:[]}];
    for(const r of values)out.push({tag:t.kind,items:[r]});
    if(unique.length>1){out.push({tag:t.kind,items:[unique[0]!,unique[1]!]},{tag:t.kind,items:[unique[1]!,unique[0]!]});}
    if(t.kind==='list')out.push({tag:t.kind,items:[unique[0]!,unique[0]!]});
    return count(out);
   }
   if(t.kind==='sum'){const out:SumRecipe[]=[];for(const v of [...t.variants].sort((a,b)=>a.name<b.name?-1:1)){if(v.payload)for(const payload of samples(v.payload,depth+1))out.push({tag:'sum',variant:v.name,payload});else out.push({tag:'sum',variant:v.name});}return count(out);}
   const d=dependencies[t.selector]!;
   if(d.kind!=='Enum'){
    if(!recordCache.has(t.selector))recordCache.set(t.selector,recordWitnesses(d,reference,child=>samples(child,depth+1)));
    return count(recordCache.get(t.selector)!);
   }
   return count<SumRecipe>(d.plain?d.contract.variants.map(v=>({tag:'enum',selector:t.selector,variant:v.name})):samples(shape(d.contract),depth+1).map(input=>({tag:'named',selector:t.selector,input})));
  };
  const negative=(t:TypedType,r:SumRecipe):{recipe:SumRecipe;error:string}[]=>{
   const out:{recipe:SumRecipe;error:string}[]=[],bad=(mode:string,error:string)=>out.push({recipe:badRecipe(r,mode),error});
   if(t.kind==='scalar'){
    const error=t.name==='UInt64'?'INVALID_UINT64':'INVALID_COMPONENT';
    for(const mode of t.name==='UInt64'?['negative','overflow','padded','unsafe','fraction','null','coercion']:t.name==='String'?['number','null','coercion']:['string','null','coercion'])bad(mode,error);
   }else if(t.kind==='optional'){
    let leaf=t.element;while(leaf.kind==='optional')leaf=leaf.element;
    const dep=leaf.kind==='named'?dependencies[leaf.selector]:null;
    const error=leaf.kind==='scalar'?(leaf.name==='UInt64'?'INVALID_UINT64':'INVALID_COMPONENT'):leaf.kind==='list'||leaf.kind==='set'?'INVALID_COLLECTION':leaf.kind==='sum'?'INVALID_SUM':dep!.kind==='Entity'?'UNOWNED_ENTITY':dep!.kind==='Value Object'?'UNOWNED_COMPONENT':dep!.plain?'UNOWNED_ENUM_CASE':'UNOWNED_SUM_CASE';
    bad('undefined',error);
    if(r.tag!=='null')out.push(...negative(t.element,r).filter(n=>!(n.recipe.tag==='bad'&&n.recipe.mode==='null')));
   }
   else if(t.kind==='list'||t.kind==='set'){
    for(const mode of ['null','object','collection-extra','collection-symbol','collection-inherited'])bad(mode,'INVALID_COLLECTION');
    if(r.items!.length){for(const mode of ['sparse','collection-getter'])bad(mode,'INVALID_COLLECTION');if(t.kind==='set')bad('duplicate','DUPLICATE_SET_VALUE');for(const child of negative(t.element,r.items![0]!))out.push({recipe:{...r,items:[child.recipe,...r.items!.slice(1)]},error:child.error});}
   }else if(t.kind==='sum'){
    for(const mode of ['null','array','extra','symbol','getter','inherited'])bad(mode,'INVALID_SUM');
    for(const mode of ['missing-variant','unknown-variant'])bad(mode,'INVALID_SUM_VARIANT');
    const v=t.variants.find(v=>v.name===r.variant)!;bad(v.payload?'missing-payload':'surplus-payload','INVALID_SUM_PAYLOAD');
    if(v.payload)for(const child of negative(v.payload,r.payload!))out.push({recipe:{...r,payload:child.recipe},error:child.error});
   }else{
    const d=dependencies[t.selector]!,error=d.kind==='Entity'?'UNOWNED_ENTITY':d.kind==='Value Object'?'UNOWNED_COMPONENT':d.plain?'UNOWNED_ENUM_CASE':'UNOWNED_SUM_CASE';
    for(const mode of ['raw-named','clone-named','foreign-named'])bad(mode,error);
    if(d.kind==='Enum'&&!d.plain)for(const child of negative(shape(d.contract),r.input!))out.push({recipe:{...r,input:child.recipe},error:child.error});
   }
   if(out.length>4096)throw new WitnessUnavailable('bounded sum negative expansion exceeded');return out;
  };
  const module_paths=bindings.closure(root,dependencies);
  for(const d of Object.values(dependencies))if(!module_paths.includes(d.relative_path))fail('dependency outside native sum closure:'+d.selector);
  return {root,rootShape,valueContract,dependencies,reference,ref,samples,negative,module_paths};
}

/** Existing TypeScript binding and case behavior remain unchanged. */
export function createOwnedValueContext(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan,includeExtensions=false){
 return createBoundOwnedValueContext(node,graph,{
  record:(selector,reference)=>resolveRecordWitness(graph,plan,selector,reference),
  enumeration:(selector,contract)=>{
   const symbol=selector.split(':')[1]!.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('')+'ValueComponent';
   const modules=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(selector)&&m.exports.some(e=>e.name===symbol&&e.kind==='value'));
   if(modules.length!==1)fail('unique checked sum component required:'+selector);
   return {kind:'Enum',selector,relative_path:modules[0]!.relative_path,symbol,plain:contract.variants.every(v=>v.payload===null),contract};
  },
  closure:(root)=>{
   const paths=new Set<string>(),visit=(relative:string)=>{if(paths.has(relative))return;paths.add(relative);const m=plan.resolved.modules.find(m=>m.relative_path===relative)??fail('missing native closure');for(const i of m.imports)visit(i.target_path??fail('external sum import'));};
   visit(root.relative_path);return [...paths].sort();
  },
 },includeExtensions);
}
