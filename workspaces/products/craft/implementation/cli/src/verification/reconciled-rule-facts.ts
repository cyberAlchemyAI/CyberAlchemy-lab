import type {CompiledProjectGraph} from '../input/project-model.js';
import type {TypedType,ValueExpression} from '../typed-operation/contracts.js';
import type {SumRecipe} from './reconciled-value-context.js';
import {createRecordRuleReference} from './reconciled-rule-reference.js';
import {canonicalJson} from '../input/source-manifest.js';
export class RuleFactsCapacity extends Error {}
export type FactRecipe=SumRecipe & Readonly<{field?:string}>;
/** Structural samples deliberately never consult factory validators or owned providers. */
export function createRuleFacts(graph:CompiledProjectGraph,selector:string){
 const facts=createStructuralFacts(graph,[selector]);return {...facts,rule:facts.reference.rules.get(selector)!};
}
export function createStructuralFacts(graph:CompiledProjectGraph,roots:readonly string[],extra:readonly ValueExpression[]=[]){
 const reference=createRecordRuleReference(graph);
 const literals=reference.seeds(roots,extra),cache=new Map<string,FactRecipe[]>();let expanded=0;
 const bounded=(rows:FactRecipe[])=>{const unique=[...new Map(rows.map(r=>[canonicalJson(r),r])).values()];expanded+=unique.length;if(expanded>4096)throw new RuleFactsCapacity('bounded Rule fact expansion exceeded');return unique;};
 const vectors=(columns:readonly FactRecipe[][]):FactRecipe[][]=>{
  if(!columns.length)return [[]];const rows:FactRecipe[][]=[],base=columns.map(c=>c[0]!),seen=new Set<string>();
  const add=(row:FactRecipe[])=>{const key=canonicalJson(row);if(seen.has(key))return;seen.add(key);if(rows.length>=4096)throw new RuleFactsCapacity('bounded Rule vector expansion exceeded');rows.push(row);};
  for(let n=0;n<Math.max(...columns.map(c=>c.length));n++){
   add(columns.map(c=>c[n%c.length]!));
   add(columns.map((c,i)=>c[(n+i)%c.length]!));
   add(columns.map((c,i)=>c[(n+c.length-i%c.length)%c.length]!));
  }
  for(let i=0;i<columns.length;i++)for(const value of columns[i]!){const row=[...base];row[i]=value;add(row);}
  return [...new Map(rows.map(r=>[canonicalJson(r),r])).values()];
 };
 const samples=(type:TypedType,depth=0):FactRecipe[]=>{
  if(depth>64)throw new RuleFactsCapacity('bounded Rule fact depth exceeded');
  const id=canonicalJson(type),existing=cache.get(id);if(existing)return existing;
  let rows:FactRecipe[]=[];
  if(type.kind==='scalar'){
   const seeds=literals.filter(l=>l.type===type.name).map(l=>l.value);
   if(type.name==='UInt64'){
    const values=new Set(['0','1','2','9007199254740991','9007199254740993','18446744073709551615',...seeds.map(String)]);
    for(const seed of [...values])for(const v of [BigInt(seed)-1n,BigInt(seed)+1n])if(v>=0n&&v<=18446744073709551615n)values.add(String(v));
    rows=[...values].sort((a,b)=>BigInt(a)<BigInt(b)?-1:BigInt(a)>BigInt(b)?1:0).flatMap(value=>(['string','bigint',...(BigInt(value)<=9007199254740991n?['number']:[])] as const).map(format=>({tag:'scalar',value,format} as FactRecipe)));
   }else rows=type.name==='Bool'?[{tag:'scalar',value:false},{tag:'scalar',value:true}]:[...new Set(['','alpha','β😀','é','e\u0301',...seeds.map(String)])].map(value=>({tag:'scalar',value}));
  }else if(type.kind==='optional')rows=[{tag:'null'},...samples(type.element,depth+1)];
  else if(type.kind==='list'||type.kind==='set'){
   const values=samples(type.element,depth+1),groups=new Map<string,FactRecipe[]>();
   for(const r of values){const k=reference.key(type.element,reference.fact(type.element,r));groups.set(k,[...(groups.get(k)??[]),r]);}
   const unique=[...groups.values()].map(g=>g[0]!);
   rows=[{tag:type.kind,items:[]},...values.map(r=>({tag:type.kind,items:[r]}))];
   for(const group of [...groups.values()].slice(1))for(const r of group)rows.push({tag:type.kind,items:[unique[0]!,r]},{tag:type.kind,items:[r,unique[0]!]});
   if(type.kind==='list'){
    rows.push({tag:'list',items:[values[0]!,values[0]!]});
    const state=(r:FactRecipe):unknown=>r.tag==='scalar'?{tag:'scalar',value:r.value}:{tag:r.tag,variant:r.variant,...(r.input?{input:state(r.input)}:{}),...(r.payload?{payload:state(r.payload)}:{}),...(r.items?{items:r.items.map(state)}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,v])=>[k,state(v)]))}:{})};
    for(const group of groups.values())for(const r of [...new Map(group.map(r=>[canonicalJson(state(r)),r])).values()].slice(1))rows.push({tag:'list',items:[group[0]!,r]},{tag:'list',items:[r,group[0]!]});
   }
  }else if(type.kind==='sum'){
   for(const v of type.variants)if(v.payload)for(const payload of samples(v.payload,depth+1))rows.push({tag:'sum',variant:v.name,payload});else rows.push({tag:'sum',variant:v.name});
  }else{
   const d=reference.get(type.selector);
   if(d.kind==='Enum')rows=samples({kind:'sum',variants:d.contract.variants},depth+1).map(input=>({tag:'named',selector:type.selector,input}));
   else{const fields=[...d.contract.properties].sort((a,b)=>a.name<b.name?-1:1);rows=vectors(fields.map(f=>samples(f.type,depth+1))).map(v=>({tag:'record',selector:type.selector,fields:Object.fromEntries(fields.map((f,i)=>[f.name,v[i]!]))}));}
  }
  const result=bounded(rows);cache.set(id,result);return result;
 };
 const bad=(base:FactRecipe,mode:string,field?:string):FactRecipe=>({tag:'bad',base,mode,...(field?{field}:{})});
 const negative=(type:TypedType,r:FactRecipe):FactRecipe[]=>{
  const out:FactRecipe[]=[],add=(m:string,field?:string)=>out.push(bad(r,m,field));
  if(type.kind==='scalar'){
   const base:FactRecipe={tag:'null'};
   return (type.name==='UInt64'?['negative','overflow','padded','unsafe','fraction','nan','infinity','null','boolean','coercion']:type.name==='String'?['number','null','coercion']:['string','number','null','coercion']).map(mode=>bad(base,mode));
  }
  if(type.kind==='optional')return [bad({tag:'null'},'undefined'),...(r.tag==='null'?[]:negative(type.element,r).filter(n=>n.mode!=='null'))];
  if(type.kind==='list'||type.kind==='set'){
   for(const m of ['null','object','collection-extra','collection-symbol','collection-inherited'])add(m);
   if(r.items!.length){for(const m of ['sparse','collection-getter','collection-hidden'])add(m);if(type.kind==='set')add('duplicate');for(const child of negative(type.element,r.items![0]!))out.push({...r,items:[child,...r.items!.slice(1)]});}
  }else if(type.kind==='sum'){
   for(const m of ['null','array','extra','symbol','getter','inherited','missing-variant','unknown-variant'])add(m);
   const v=type.variants.find(v=>v.name===r.variant)!;add(v.payload?'missing-payload':'surplus-payload');
   if(v.payload)for(const child of negative(v.payload,r.payload!))out.push({...r,payload:child});
  }else{
   const d=reference.get(type.selector);
   if(d.kind==='Enum')return negative({kind:'sum',variants:d.contract.variants},r.input!).map(input=>({...r,input}));
   for(const m of ['null','array','extra','symbol','inherited'])add(m);
   for(const f of d.contract.properties){
    for(const m of ['getter','non-enumerable'])add(m,f.name);
    if(f.type.kind!=='optional')add('missing-field',f.name);
    for(const child of negative(f.type,r.fields![f.name]!))out.push({...r,fields:{...r.fields,[f.name]:child}});
   }
  }return out;
 };
 const omissions=(type:TypedType,r:FactRecipe):{recipe:FactRecipe;normalized:FactRecipe}[]=>{
  if(type.kind==='named'){
   const d=reference.get(type.selector);
   if(d.kind==='Enum')return omissions({kind:'sum',variants:d.contract.variants},r.input!).map(p=>({recipe:{...r,input:p.recipe},normalized:{...r,input:p.normalized}}));
   return d.contract.properties.flatMap(f=>[
    ...(f.type.kind==='optional'?[{recipe:bad(r,'missing-field',f.name),normalized:{...r,fields:{...r.fields,[f.name]:{tag:'null'}}}}]:[]),
    ...omissions(f.type,r.fields![f.name]!).map(p=>({recipe:{...r,fields:{...r.fields,[f.name]:p.recipe}},normalized:{...r,fields:{...r.fields,[f.name]:p.normalized}}}))
   ]);
  }
  if(type.kind==='optional')return r.tag==='null'?[]:omissions(type.element,r);
  if(type.kind==='list'||type.kind==='set')return r.items!.length?omissions(type.element,r.items![0]!).map(p=>({recipe:{...r,items:[p.recipe,...r.items!.slice(1)]},normalized:{...r,items:[p.normalized,...r.items!.slice(1)]}})):[];
  if(type.kind==='sum'){const v=type.variants.find(v=>v.name===r.variant)!;return v.payload?omissions(v.payload,r.payload!).map(p=>({recipe:{...r,payload:p.recipe},normalized:{...r,payload:p.normalized}})):[];}
  return [];
 };
 return {reference,samples,vectors,negative,omissions,bad};
}
