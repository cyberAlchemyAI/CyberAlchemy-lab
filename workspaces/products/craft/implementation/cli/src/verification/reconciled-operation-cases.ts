import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {TypedType} from '../typed-operation/contracts.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import type {createOperationBinding} from './reconciled-operation-binding.js';
import {createEffectfulOperationReference,type OperationEffectFixture} from './reconciled-operation-effect-reference.js';
import {OperationReferenceUnsupported,type OperationFixtureMode} from './reconciled-operation-reference.js';
import {captureOperationRecipe} from './reconciled-operation-values.js';
import {RuleFactsCapacity,type FactRecipe} from './reconciled-rule-facts.js';
import {createOwnedValueContext,isWitnessUnavailable} from './reconciled-value-context.js';
import {canonicalJson} from '../input/source-manifest.js';
import type {CheckedOperationAction} from '../typed-operation/action-bindings.js';

export class OperationCasesUnavailable extends Error {}
const vectorOrigins=new WeakMap<object,readonly string[]>();
/** Private provenance carrier: does not change the complete semantic case payload. */
export function operationVectorCaseIds(source:object):readonly string[]{
 const ids=vectorOrigins.get(source);if(!ids)throw new TypeError('OPERATION_CASE_ORIGIN:registered source required');return ids;
}
export function operationValueRecipe(v:any):FactRecipe{
 if(v===null)return {tag:'null'};
 if(typeof v==='bigint')return {tag:'scalar',value:String(v),format:'bigint'};
 if(typeof v==='number')return {tag:'scalar',value:String(v),format:'number'};
 if(typeof v!=='object')return {tag:'scalar',value:v};
 if(Array.isArray(v))return {tag:'list',items:v.map(operationValueRecipe)};
 return {tag:'fields',fields:Object.fromEntries(Object.entries(v).map(([k,x])=>[k,operationValueRecipe(x)]))};
}
export function createOperationCases(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,binding:ReturnType<typeof createOperationBinding>){
 return createOperationSemanticCases(binding.action,createEffectfulOperationReference(graph,plan,binding.action),
  selector=>createOwnedValueContext(graph.nodes.find(n=>n.selector===selector)!,graph,plan));
}
export function createOperationSemanticCases(action:CheckedOperationAction,oracle:ReturnType<typeof createEffectfulOperationReference>,ownedContext:(selector:string)=>Pick<ReturnType<typeof createOwnedValueContext>,'samples'>){
 const b=action.bindings,facts=oracle.facts;
 const capacity=(reason:string):never=>{throw new OperationCasesUnavailable('bounded Operation '+reason);};
 const recipes:FactRecipe[]=[],interned=new Map<string,number>(),cases:SemanticCase[]=[],seen=new Set<string>();let bytes=256;
 const intern=(r:FactRecipe):number=>{
  const link=(v:FactRecipe):FactRecipe=>({tag:'ref',value:String(intern(v))});
  const row={...r,...(r.base?{base:link(r.base)}:{}),...(r.input?{input:link(r.input)}:{}),...(r.payload?{payload:link(r.payload)}:{}),...(r.items?{items:r.items.map(link)}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,v])=>[k,link(v)]))}:{})};
  const text=canonicalJson(row),old=interned.get(text);if(old!==undefined)return old;
  bytes+=Buffer.byteLength(text)+1;if(bytes>8388608)capacity('serialized cases exceed 8 MiB');
  const id=recipes.length;recipes.push(row);interned.set(text,id);return id;
 };
 const add=(input:FactRecipe,fixture:OperationEffectFixture,mode:OperationFixtureMode='committed',capture=false,observed?:ReturnType<typeof oracle.expected>)=>{
  const data={input:intern(input),reads:fixture.reads.map(r=>({...r,value:intern(r.value)})),clocks:fixture.clocks,mode,capture};
  const key=canonicalJson(data);if(seen.has(key))return;seen.add(key);if(cases.length>=4095)capacity('case capacity exceeded');
  // Witness selection may already have evaluated these exact input/fixture/mode bytes.
  // Reuse that local observation, never an expectation from another case or binding.
  const expected=observed??oracle.expected(input,fixture,mode);
  const c:SemanticCase={id:'case-'+cases.length,mode:'operation',format:'string',values:[key],expected:{kind:'value',value:canonicalJson(expected)}};
  bytes+=Buffer.byteLength(canonicalJson(c))+1;if(bytes>8388608)capacity('serialized cases exceed 8 MiB');cases.push(c);
 };
 const status=(observation:ReturnType<typeof oracle.expected>,field:string):unknown=>(observation.outcome as any)[1].find((p:any)=>p[0]===field)?.[1]?.[1];
 const eventFieldSamples=(field:any,slot:string):FactRecipe[]=>{
  const type=field.type_ref.kind==='reference'?(oracle.eventReferenceScalar(field.type_ref.selector)==='UInt64'?'uint64':'reference'):field.type_ref.name;
  const values=type==='integer'?['0','1','-1','-9223372036854775808','9223372036854775807',0,1,-1,0n,1n,-1n]:type==='uint64'?['0','1','9007199254740992','18446744073709551615',0,1,0n,1n]:type==='decimal'?[0,1.5,-1.5]:type==='boolean'?[false,true]:type==='string'?['',slot,'β😀']:[slot,'β😀'];
  return values.map(operationValueRecipe);
 };
 const eventInputs=Object.fromEntries(action.events.map(e=>[e.parameter,{tag:'fields',fields:{occurrence:{tag:'fields',fields:{[e.contract.occurrence_id.field_id]:eventFieldSamples(e.contract.occurrence_id,e.slot)[0]!}},payload:{tag:'fields',fields:Object.fromEntries(e.contract.payload.filter(f=>f.required).map(f=>[f.field_id,eventFieldSamples(f,e.slot)[0]!]))},...(e.contract.occurred_at_policy==='required'?{occurredAt:operationValueRecipe('time-'+e.slot)}:{})}} as FactRecipe]));
 const clocks=action.events.filter(e=>e.contract.occurred_at_policy==='generated').map(e=>({slot:e.slot,value:'time-'+e.slot}));
 const ownedContexts=new Map<string,ReturnType<typeof ownedContext>>(),ownedCache=new Map<string,FactRecipe[]>();let ownedExpansion=0;
 const convert=(r:FactRecipe):FactRecipe=>r.tag==='enum'?{tag:'named',selector:r.selector!,input:{tag:'sum',variant:r.variant!}}:
  {...r,...(r.input?{input:convert(r.input)}:{}),...(r.payload?{payload:convert(r.payload)}:{}),...(r.items?{items:r.items.map(convert)}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,v])=>[k,convert(v)]))}:{})};
 const ownedSamples=(type:TypedType,depth=0):FactRecipe[]=>{
  if(depth>64)capacity('owned witness depth exceeded');const key=canonicalJson(type),prior=ownedCache.get(key);if(prior)return prior;
  let rows:FactRecipe[];
	  if(type.kind==='named'){
   let context=ownedContexts.get(type.selector);if(!context){context=ownedContext(type.selector);ownedContexts.set(type.selector,context);}
   rows=context.samples(type).map(convert);
	  }else if(type.kind==='scalar'||type.kind==='reference')rows=facts.samples(type);
  else if(type.kind==='optional')rows=[{tag:'null'},...ownedSamples(type.element,depth+1)];
  else if(type.kind==='sum')rows=type.variants.flatMap(v=>v.payload?ownedSamples(v.payload,depth+1).map(payload=>({tag:'sum',variant:v.name,payload})):[{tag:'sum',variant:v.name}]);
  else rows=[{tag:type.kind,items:[]},...ownedSamples(type.element,depth+1).map(value=>({tag:type.kind,items:[value]}))];
  ownedExpansion+=rows.length;if(ownedExpansion>4096)capacity('owned witness expansion exceeded');ownedCache.set(key,rows);return rows;
 };
 const samples=(type:TypedType):FactRecipe[]=>{
  const structural=[...new Map([...ownedSamples(type),...facts.samples(type)].map(r=>[canonicalJson(r),r])).values()],valid:FactRecipe[]=[],other:FactRecipe[]=[];
  // Prioritize selected owned witnesses without removing structural-only inputs.
  for(const recipe of structural){try{oracle.checkOwned(type,recipe);valid.push(recipe);}catch(e){if(e instanceof OperationReferenceUnsupported)throw e;if(!(e instanceof TypeError))throw e;other.push(recipe);}}
  return [...valid,...other];
 };
 const inputColumns=b.inputs.map(p=>samples(p.type)),readColumns=action.reads.map(r=>facts.samples({kind:'named',selector:r.target}));
 const vectors=facts.vectors([...inputColumns,...readColumns]);
 const make=(vector:readonly FactRecipe[])=>{
  const input:FactRecipe={tag:'fields',fields:{...eventInputs,...Object.fromEntries(b.inputs.map((p,i)=>[p.name,vector[i]!]))}};
  const scope=new Map(b.inputs.map((p,i)=>[p.name,{type:p.type,value:oracle.values.normalize(p.type,captureOperationRecipe(vector[i]!))}]));
  const reads=action.reads.map((r,i)=>{
   const row=structuredClone(vector[b.inputs.length+i]!);
   if(!row.fields)throw new OperationReferenceUnsupported('Operation read witness must be a source record');
   const key=oracle.values.value(r.key,scope).value;
   return {slot:r.slot,value:{...row,fields:{...row.fields,[r.identity.name]:operationValueRecipe(key)}}};
  });return {input,fixture:{reads,clocks} as OperationEffectFixture};
 };
 let baseline:ReturnType<typeof make>|null=null,abortWitness:ReturnType<typeof make>|null=null;
 const scored:{vector:readonly FactRecipe[];score:number}[]=[],searched=new Set<string>();let attempts=0;
 const score=(e:ReturnType<typeof oracle.expected>)=>{
  const stage=status(e,'stage');if(status(e,'status')==='committed')return 10000;
  if(stage==='guard')return 100+b.guards.findIndex(g=>'RULE_REJECTED:'+g.selector===status(e,'code'));
  return stage==='write-validation'?1000:stage==='event'?2000:stage==='result'?3000:0;
 };
 for(const vector of vectors){
  const c=make(vector),expected=oracle.expected(c.input,c.fixture);
  if(status(expected,'status')==='committed'&&!baseline)baseline=c;
  if(status(expected,'stage')==='guard'&&!abortWitness)abortWitness=c;
  scored.push({vector,score:score(expected)});searched.add(canonicalJson(vector));attempts++;
  add(c.input,c.fixture,'committed',false,expected);
 }
 const vectorIds=Object.freeze(cases.map(c=>c.id));
 // A bounded local search composes individually valid values across relational
 // guards. It changes fixture values only; Rules and selected validators stay fixed.
 const columns=[...inputColumns,...readColumns];
 for(let round=0;!baseline&&round<3&&attempts<4096;round++){
  const seeds=scored.sort((a,b)=>b.score-a.score).slice(0,32),found:typeof scored=[];
  search:for(const seed of seeds)for(let i=0;i<columns.length;i++)for(const value of columns[i]!){
   const vector=[...seed.vector];vector[i]=value;const key=canonicalJson(vector);if(searched.has(key))continue;
   if(attempts>=4096)break search;attempts++;searched.add(key);
   const c=make(vector),expected=oracle.expected(c.input,c.fixture),rank=score(expected);found.push({vector,score:rank});
   if(status(expected,'stage')==='guard'&&!abortWitness)abortWitness=c;
   if(status(expected,'status')==='committed'){baseline=c;add(c.input,c.fixture,'committed',false,expected);break search;}
  }
  scored.push(...found);
 }
 if(!baseline)capacity('source search found no complete preparation/commit witness after '+attempts+' candidates (best stage score '+Math.max(...scored.map(s=>s.score))+'); not an unsatisfiability proof');
 const base=baseline!;
 for(const mode of ['committed','rejected','indeterminate','begin-throw','commit-throw','rollback-throw','receipt-empty','receipt-unknown','receipt-extra','receipt-null','receipt-getter','receipt-inherited','receipt-symbol','receipt-hidden','receipt-array','receipt-undefined'] as OperationFixtureMode[]){add(base.input,base.fixture,mode);if(abortWitness)add(abortWitness.input,abortWitness.fixture,mode);}
 if(b.inputs.length||b.events.length)add(base.input,base.fixture,'committed',true);
 for(const mode of ['null','array','inherited','extra','symbol','frozen','null-prototype'])add(facts.bad(base.input,mode),base.fixture);
 for(const p of b.inputs){
  const seed=base.input.fields![p.name]!;
  for(const mode of ['getter','non-enumerable','missing-field'])add(facts.bad(base.input,mode,p.name),base.fixture);
  for(const invalid of facts.negative(p.type,seed))add({...base.input,fields:{...base.input.fields,[p.name]:invalid}},base.fixture);
  for(const omission of facts.omissions(p.type,seed))add({...base.input,fields:{...base.input.fields,[p.name]:omission.recipe}},base.fixture);
  // Other inputs/reads remain at the accepted witness so value checks stay reachable.
  // With one input and no reads, vectors already emitted every identical candidate.
  // Keep the accepted-surroundings pass for multiple inputs or any read dependency.
  if(b.inputs.length!==1||action.reads.length)for(const value of inputColumns[b.inputs.indexOf(p)]!)add({...base.input,fields:{...base.input.fields,[p.name]:value}},base.fixture);
 }
 for(const [i,read]of action.reads.entries()){
  const row=base.fixture.reads[i]!,type:TypedType={kind:'named',selector:read.target};
  const withRow=(value:FactRecipe,throws=false)=>({...base.fixture,reads:base.fixture.reads.map((r,j)=>j===i?{...r,value,throws}:r)});
  add(base.input,withRow({tag:'null'}));add(base.input,withRow(row.value,true));add(base.input,withRow({tag:'null'}),'rollback-throw');
  for(const invalid of facts.negative(type,row.value))add(base.input,withRow(invalid));
  for(const value of facts.samples(read.identity.type))add(base.input,withRow({...row.value,fields:{...row.value.fields,[read.identity.name]:value}}));
 }
 for(const event of action.events){
  const seed=base.input.fields![event.parameter]!,change=(value:FactRecipe)=>({...base.input,fields:{...base.input.fields,[event.parameter]:value}});
  for(const mode of ['getter','non-enumerable','missing-field'])add(facts.bad(base.input,mode,event.parameter),base.fixture);
  for(const mode of ['null','array','extra','symbol','inherited','getter','non-enumerable','frozen','null-prototype'])add(change(facts.bad(seed,mode,'payload')),base.fixture);
  for(const [group,fields]of [['occurrence',[event.contract.occurrence_id]],['payload',event.contract.payload]] as const){
   for(const field of fields){
    const parent=seed.fields![group]!,set=(v:FactRecipe)=>change({...seed,fields:{...seed.fields,[group]:{...parent,fields:{...parent.fields,[field.field_id]:v}}}});
    for(const value of eventFieldSamples(field,event.slot))add(set(value),base.fixture);
    add(change({...seed,fields:{...seed.fields,[group]:facts.bad(parent,'missing-field',field.field_id)}}),base.fixture);
    for(const mode of ['getter','non-enumerable','extra','symbol'])add(change({...seed,fields:{...seed.fields,[group]:facts.bad(parent,mode,field.field_id)}}),base.fixture);
    for(const value of [null,true,'', '01','-0','9223372036854775808','-9223372036854775809',9007199254740992,1.5])add(set(operationValueRecipe(value)),base.fixture);
   }
  }
  if(event.contract.occurred_at_policy==='generated'){
   add(change({...seed,fields:{...seed.fields,occurredAt:operationValueRecipe('supplied')}}),base.fixture);
   for(const mode of ['missing','throw'] as const)add(base.input,{...base.fixture,clocks:base.fixture.clocks.map(c=>c.slot===event.slot?{...c,mode}:c)});
   for(const value of ['',null,0])add(base.input,{...base.fixture,clocks:base.fixture.clocks.map(c=>c.slot===event.slot?{...c,value}:c)});
  }else for(const value of [null,'',0])add(change({...seed,fields:{...seed.fields,occurredAt:operationValueRecipe(value)}}),base.fixture);
 }
 const result={recipes,cases};vectorOrigins.set(result,vectorIds);return result;
}
export const isOperationCapacity=(e:unknown):e is Error=>e instanceof OperationCasesUnavailable||e instanceof OperationReferenceUnsupported||e instanceof RuleFactsCapacity||isWitnessUnavailable(e);
