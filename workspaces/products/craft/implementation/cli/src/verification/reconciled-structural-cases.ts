import type {TypedParameter,TypedType} from '../typed-operation/contracts.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import {canonicalJson} from '../input/source-manifest.js';
import {RuleFactsCapacity,type FactRecipe,type createStructuralFacts} from './reconciled-rule-facts.js';
type Facts=ReturnType<typeof createStructuralFacts>;
type Scope=ReadonlyMap<string,Readonly<{type:TypedType;value:any}>>;
/** Shared data-only case transport; the caller supplies an independent source oracle. */
export function createStructuralCases(parameters:readonly TypedParameter[],facts:Facts,evaluate:(scope:Scope)=>string,mode='rule',inputError='RULE_INPUT'){
 const {reference,samples,vectors,negative,omissions,bad}=facts;
  const columns=parameters.map(p=>samples(p.type)),base=columns.map(c=>c[0]!),cases:SemanticCase[]=[],seen=new Set<string>();let bytes=0;
  const recipes:FactRecipe[]=[],recipeIds=new Map<string,number>();
  const intern=(r:FactRecipe):number=>{
   const link=(r:FactRecipe):FactRecipe=>({tag:'ref',value:String(intern(r))});
   const node:FactRecipe={...r,...(r.base?{base:link(r.base)}:{}),...(r.input?{input:link(r.input)}:{}),...(r.payload?{payload:link(r.payload)}:{}),...(r.items?{items:r.items.map(link)}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,v])=>[k,link(v)]))}:{})};
   const encoded=canonicalJson(node),existing=recipeIds.get(encoded);if(existing!==undefined)return existing;
   bytes+=Buffer.byteLength(encoded)+1;if(bytes>8388608)throw new RuleFactsCapacity('bounded Rule serialized case capacity exceeded');
   const id=recipes.length;recipes.push(node);recipeIds.set(encoded,id);return id;
  };
  const input=(values:readonly FactRecipe[]):FactRecipe=>({tag:'fields',fields:Object.fromEntries(parameters.map((p,i)=>[p.name,values[i]!]))});
  const uniqueSets=(t:TypedType,r:FactRecipe):boolean=>{
   if(t.kind==='scalar')return true;
   if(t.kind==='optional')return r.tag==='null'||uniqueSets(t.element,r);
   if(t.kind==='list'||t.kind==='set')return r.items!.every(v=>uniqueSets(t.element,v))&&(t.kind==='list'||new Set(r.items!.map(v=>reference.key(t.element,reference.fact(t.element,v)))).size===r.items!.length);
   if(t.kind==='sum'){const v=t.variants.find(v=>v.name===r.variant)!;return !v.payload||uniqueSets(v.payload,r.payload!);}
   const d=reference.get(t.selector);return d.kind==='Enum'?uniqueSets({kind:'sum',variants:d.contract.variants},r.input!):d.contract.properties.every(f=>uniqueSets(f.type,r.fields![f.name]!));
  };
  const push=(recipe:FactRecipe,normalized:readonly FactRecipe[]|null)=>{
   const encoded=String(intern(recipe));if(seen.has(encoded))return;seen.add(encoded);
   if(cases.length>=4096)throw new RuleFactsCapacity('bounded Rule case capacity exceeded');
   const valid=normalized&&parameters.every((p,i)=>uniqueSets(p.type,normalized[i]!));
   const expected:SemanticCase['expected']=valid?{kind:'value',value:evaluate(new Map(parameters.map((p,i)=>[p.name,{type:p.type,value:reference.fact(p.type,normalized![i]!)}])))}:{kind:'error',name:'TypeError',message:inputError};
   const row:SemanticCase={id:'case-'+cases.length,mode,format:'string',values:[encoded],expected};
   bytes+=Buffer.byteLength(canonicalJson(row))+1;if(bytes>8388608)throw new RuleFactsCapacity('bounded Rule serialized case capacity exceeded');
   cases.push(row);
  };
  for(const values of vectors(columns))push(input(values),values);
  const baseline=input(base);
  for(const mode of ['frozen','null-prototype'])push(bad(baseline,mode),base);
  for(const mode of ['null','array','number','string','undefined','coercion','inherited','extra','symbol'])push(bad(baseline,mode),null);
  // Each malformed structural shape is exercised once per parameter; concrete valid values remain in the positive corpus.
  const shape=(r:FactRecipe):unknown=>r.tag==='scalar'?{tag:'scalar'}:{tag:r.tag,variant:r.variant,...(r.input?{input:shape(r.input)}:{}),...(r.payload?{payload:shape(r.payload)}:{}),...(r.items?{items:r.items.map(shape)}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,v])=>[k,shape(v)]))}:{})};
  for(const [i,p] of parameters.entries()){
   for(const mode of ['getter','non-enumerable','missing-field'])push(bad(baseline,mode,p.name),null);
   const representatives=[...new Map(columns[i]!.map(r=>[canonicalJson(shape(r)),r])).values()];
   for(const r of representatives){
    for(const n of negative(p.type,r)){const values=[...base];values[i]=n;push(input(values),null);}
    for(const omission of omissions(p.type,r)){const values=[...base],normalized=[...base];values[i]=omission.recipe;normalized[i]=omission.normalized;push(input(values),normalized);}
   }
  }
 return {cases,recipes};
}
