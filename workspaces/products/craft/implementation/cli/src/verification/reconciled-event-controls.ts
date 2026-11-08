import type {CompiledProjectGraph,FieldSpec} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {createEffectAuditRunner} from './reconciled-effect-audit.js';
import {eventReferenceIdentity} from '../generation/event-reference-identity.js';
export const SEMANTIC_EVENT_DEFINITION_SHA256='59e72f308474d6dff92d8cf32a2166dc02ec4a7160c34b9785f575af4fa763a9';
export const EVENT_EFFECT_AUDIT_RUNNER=createEffectAuditRunner('EVENT_EFFECT_AUDIT','domainspec.event-effect-observation/v1-candidate');
type Atom=Readonly<{kind:'string'|'number'|'bigint'|'boolean'|'bad';value:string}>;
type Input={occurrence:Record<string,Atom>;payload:Record<string,Atom>;occurredAt?:Atom};
type Change=Readonly<{target:'input'|'occurrence'|'payload';mode:string;field?:string}>;
type Clock=Readonly<{kind:'return'|'throw'|'absent'|'undefined'|'null'|'number';value?:Atom}>;
type Source={event_type:string;version:string;occurrence_id:FieldSpec;occurred_at_policy:'required'|'generated';payload:readonly FieldSpec[]};
export interface EventControls{
 readonly selector:string;readonly kind:'Event';readonly state:'ready';readonly adapter:'event';
 readonly contract_sha256:string;readonly relative_path:string;readonly callable:string;readonly names:readonly string[];
 readonly module_paths:readonly string[];readonly native_imports:readonly {relative_path:string;imports:readonly {specifier:string;target_path:string}[]}[];
 readonly occurrence_fields:readonly string[];readonly payload_fields:readonly string[];readonly cases:readonly SemanticCase[];
}
const atom=(kind:Atom['kind'],value:string):Atom=>({kind,value}),s=(value:string)=>atom('string',value);
const bad=(value:string)=>atom('bad',value),copy=<T>(v:T):T=>JSON.parse(JSON.stringify(v));
class EventCapacity extends Error{}
function eventModule(node:CompiledProjectGraph['nodes'][number],plan:ReconciledProjectPlan){
 const callable='event'+node.selector.split(':')[1]!.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
 const modules=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(node.selector)&&m.exports.some(e=>e.name===callable&&e.kind==='value'));
 if(modules.length!==1)throw new TypeError('DS_EVENT_CONTROLS:unique native constructor required');
 const paths=new Set<string>(),visit=(p:string)=>{
  if(paths.has(p))return;paths.add(p);const m=plan.resolved.modules.find(m=>m.relative_path===p);
  if(!m||m.qualified_selectors.some(s=>s!==node.selector))throw new TypeError('DS_EVENT_CONTROLS:foreign module dependency');
  for(const i of m.imports){if(!i.target_path)throw new TypeError('DS_EVENT_CONTROLS:external dependency');visit(i.target_path);}
 };visit(modules[0]!.relative_path);
 return {callable,relative_path:modules[0]!.relative_path,module_paths:[...paths].sort(),native_imports:[...paths].sort().map(relative_path=>({relative_path,imports:plan.resolved.modules.find(m=>m.relative_path===relative_path)!.imports.map(i=>({specifier:i.specifier,target_path:i.target_path!}))}))};
}
export function createEventEffectAudit(graph:CompiledProjectGraph,plan:ReconciledProjectPlan){
 const nodes=graph.nodes.filter(n=>n.kind==='Event');
 return {definition_sha256:SEMANTIC_EVENT_DEFINITION_SHA256,roots:nodes.map(n=>n.selector).sort(),module_paths:[...new Set(nodes.flatMap(n=>eventModule(n,plan).module_paths))].sort()};
}
type ReferenceScalars=ReadonlyMap<string,'String'|'UInt64'>;
const fieldKind=(field:FieldSpec,references:ReferenceScalars)=>field.type_ref.kind==='reference'?(references.get(field.type_ref.selector)==='UInt64'?'uint64':'reference'):field.type_ref.name;
function values(field:FieldSpec,references:ReferenceScalars):Atom[]{
 const name=fieldKind(field,references),label=field.field_id;
 if(name==='boolean')return [atom('boolean','true'),atom('boolean','false')];
 if(name==='integer')return ['-9223372036854775808','9223372036854775807','-9007199254740992','9007199254740992','-1','0','1'].flatMap(n=>[s(n),atom('bigint',n),...(BigInt(n)>=-9007199254740991n&&BigInt(n)<=9007199254740991n?[atom('number',n)]:[])]).concat([atom('number','-0'),atom('number','9007199254740991'),atom('number','-9007199254740991')]);
 if(name==='uint64')return ['0','1','9007199254740992','18446744073709551615'].flatMap(n=>[s(n),atom('bigint',n),...(BigInt(n)<=9007199254740991n?[atom('number',n)]:[])]).concat([atom('number','9007199254740991')]);
 if(name==='decimal')return ['0.25','-1.5','0','-0','1.7976931348623157e+308','5e-324'].map(n=>atom('number',n));
 return [s('value:'+label),s('other:'+label),s(' \n'),...(name==='string'?[s('')]:[])];
}
function invalid(field:FieldSpec,references:ReferenceScalars):Atom[]{
 const name=fieldKind(field,references);
 const common=['null','undefined','object','array','coercion','symbol','function'].map(bad);
 if(name==='integer')return [...common,atom('boolean','true'),...['9223372036854775808','-9223372036854775809'].flatMap(n=>[s(n),atom('bigint',n)]),...['01','-0','+1','1\n',' 1','1.0','1e2',''].map(s),...['NaN','Infinity','-Infinity','9007199254740992','-9007199254740992','1.5'].map(n=>atom('number',n))];
 if(name==='uint64')return [...common,atom('boolean','true'),...['-1','18446744073709551616'].flatMap(n=>[s(n),atom('bigint',n)]),...['01','-0','+1','1\n',' 1','1.0','1e2',''].map(s),...['NaN','Infinity','-Infinity','9007199254740992','-1','1.5'].map(n=>atom('number',n))];
 if(name==='decimal')return [...common,s('1'),atom('boolean','false'),atom('bigint','1'),...['NaN','Infinity','-Infinity'].map(n=>atom('number',n))];
 if(name==='boolean')return [...common,s('true'),atom('number','1'),atom('bigint','1')];
 return [...common,atom('boolean','true'),atom('number','1'),atom('bigint','1'),...(name==='string'?[]:[s('')])];
}
/** Source-value interpretation uses carrier validity and mathematical bounds, not the emitted helpers. */
function normalize(field:FieldSpec,value:Atom,references:ReferenceScalars):Atom{
 const name=fieldKind(field,references),invalid=()=>{throw new TypeError('EVENT_INPUT');};
 if(name==='boolean'){if(value.kind!=='boolean')return invalid();return value;}
 if(name==='integer'){
  if(!['string','number','bigint'].includes(value.kind))return invalid();
  if(value.kind==='string'&&!/^(?:0|-[1-9]\d*|[1-9]\d*)$/.test(value.value))return invalid();
  if(value.kind==='number'&&!Number.isSafeInteger(Number(value.value)))return invalid();
  let n:bigint;try{n=value.kind==='number'?BigInt(Number(value.value)):BigInt(value.value);}catch{return invalid();}
  if(n<-(2n**63n)||n>=2n**63n)return invalid();return atom('bigint',n.toString());
 }
 if(name==='uint64'){
  if(!['string','number','bigint'].includes(value.kind))return invalid();
  if(value.kind==='string'&&!/^(?:0|[1-9]\d*)$/.test(value.value))return invalid();
  if(value.kind==='number'&&!Number.isSafeInteger(Number(value.value)))return invalid();
  let n:bigint;try{n=value.kind==='number'?BigInt(Number(value.value)):BigInt(value.value);}catch{return invalid();}
  if(n<0n||n>=2n**64n)return invalid();return atom('bigint',n.toString());
 }
 if(name==='decimal'){if(value.kind!=='number'||!Number.isFinite(Number(value.value)))return invalid();return atom('number',String(Number(value.value)));}
 if(value.kind!=='string'||name!=='string'&&value.value.length===0)return invalid();return value;
}
export function createEventSemanticCases(node:CompiledProjectGraph['nodes'][number],binding:SemanticCase,references:ReferenceScalars=new Map()){
 const source=node.body as unknown as Source,fields=[...source.payload].sort((a,b)=>a.field_id<b.field_id?-1:a.field_id>b.field_id?1:0);
 const identity={selector:node.selector,kind:'Event' as const},cases:SemanticCase[]=[],generated=source.occurred_at_policy==='generated';let caseBytes=256;
 const baseline:Input={occurrence:{[source.occurrence_id.field_id]:values(source.occurrence_id,references)[0]!},payload:Object.fromEntries(fields.map(f=>[f.field_id,values(f,references)[0]!])),...(!generated?{occurredAt:s('supplied:time')}: {})};
 const defaultClock:Clock=generated?{kind:'return',value:s('fixture:time')}:{kind:'absent'},time:FieldSpec={field_id:'occurredAt',required:true,type_ref:{kind:'primitive',name:'timestamp'}};
 const push=(input:Input,changes:Change[]=[],clock:Clock=defaultClock,repeat=false)=>{
  if(cases.length>=4096)throw new EventCapacity('bounded Event case capacity exceeded');
  let calls=0,result:unknown;
  try{
   if(changes.some(c=>!['null-prototype','frozen'].includes(c.mode)))throw new TypeError('EVENT_INPUT');
   const occurrence=Object.fromEntries([source.occurrence_id].map(f=>[f.field_id,normalize(f,input.occurrence[f.field_id]!,references)]));
   const payload:Record<string,Atom>={};
   for(const f of fields){if(!Object.hasOwn(input.payload,f.field_id)){if(f.required)throw new TypeError('EVENT_INPUT');continue;}payload[f.field_id]=normalize(f,input.payload[f.field_id]!,references);}
   let occurredAt:Atom;
   if(generated){
    if(Object.hasOwn(input,'occurredAt')||!['return','throw'].includes(clock.kind))throw new TypeError('EVENT_INPUT');
    calls++;if(clock.kind==='throw')throw 'clock';
    occurredAt=normalize(time,clock.value!,references);
   }else{if(!Object.hasOwn(input,'occurredAt'))throw new TypeError('EVENT_INPUT');occurredAt=normalize(time,input.occurredAt!,references);}
   const value={type:source.event_type,version:source.version,occurrence,payload,occurredAt},values=[value];
   if(repeat){values.push(copy(value));if(generated)calls++;}
   result={kind:'value',values,detached:true,fresh:true};
  }catch(e){if(e!=='clock'&&!(e instanceof TypeError))throw e;result={kind:'error',name:e==='clock'?'Error':'TypeError',message:e==='clock'?'EVENT_CLOCK_SENTINEL':'EVENT_INPUT',same_clock_error:e==='clock'};}
  const recipe={input,changes,clock,repeat};
  const next:SemanticCase={id:'case-'+cases.length,mode:'event',format:'string',values:[canonicalJson(recipe)],expected:{kind:'value',value:canonicalJson({result,clock_calls:calls})}};
  caseBytes+=Buffer.byteLength(canonicalJson(next))+1;if(caseBytes>8388608)throw new EventCapacity('bounded Event serialized case capacity exceeded');
  cases.push(next);
 };
 try{
  caseBytes+=Buffer.byteLength(canonicalJson(binding))+1;if(caseBytes>8388608)throw new EventCapacity('bounded Event serialized case capacity exceeded');cases.push(binding);
  push(copy(baseline));push(copy(baseline),[],defaultClock,true);
  const absent=copy(baseline);for(const f of fields)if(!f.required)delete absent.payload[f.field_id];push(absent);
  for(const target of ['occurrence','payload'] as const)for(const f of target==='occurrence'?[source.occurrence_id]:fields){
   for(const value of [...values(f,references),...invalid(f,references)]){const input=copy(baseline);input[target][f.field_id]=value;push(input);}
   if(!f.required){const input=copy(baseline);delete input.payload[f.field_id];push(input);}
  }
  for(const target of ['input','occurrence','payload'] as const){
   const names=target==='input'?(generated?['occurrence','payload']:['occurrence','occurredAt','payload']):target==='occurrence'?[source.occurrence_id.field_id]:fields.map(f=>f.field_id);
   for(const mode of ['null-prototype','frozen','null','undefined','array','inherited','extra','symbol'])push(copy(baseline),[{target,mode}]);
   for(const field of names)for(const mode of ['getter','non-enumerable',...(target==='payload'&&!fields.find(f=>f.field_id===field)!.required?[]:['missing'])])push(copy(baseline),[{target,mode,field}]);
  }
  if(generated){
   const extra=copy(baseline);extra.occurredAt=s('forbidden:supplied');push(extra);
   for(const clock of [{kind:'return',value:s('other:fixture')},{kind:'throw'},{kind:'absent'},{kind:'undefined'},{kind:'null'},{kind:'number'},...invalid(time,references).map(value=>({kind:'return',value})),{kind:'return',value:bad('promise')}] as Clock[])push(copy(baseline),[],clock);
  }else{
   for(const value of [...values(time,references),...invalid(time,references)])push({...copy(baseline),occurredAt:value});
   push(copy(baseline),[],{kind:'throw'});push(copy(baseline),[],{kind:'return',value:s('must:not:call')});
  }
  return {...identity,state:'ready' as const,contract_sha256:sha256(canonicalJson(source)),names:fields.map(f=>f.field_id),occurrence_fields:[source.occurrence_id.field_id],payload_fields:fields.map(f=>f.field_id),cases};
 }catch(e){if(e instanceof EventCapacity)return {...identity,state:'not_evaluable' as const,reason:e.message};throw e;}
}
export function createEventControls(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan):EventControls|Readonly<{selector:string;kind:'Event';state:'not_evaluable';reason:string}>{
 const source=node.body as unknown as Source,generated=source.occurred_at_policy==='generated';
 const module=eventModule(node,plan),provider=plan.resolved.artifacts.find(a=>module.module_paths.includes(a.relative_path)&&a.relative_path.endsWith('.provider.ts'));
 if(!provider)throw new TypeError('DS_EVENT_CONTROLS:missing provider');
 const sourceEvidence=(selector:string)=>{const n=graph.nodes.find(n=>n.selector===selector)!;const row=graph.source_manifest.sources.find(s=>s.relative_path==='specs/'+n.feature_id+'/nodes/'+n.node_id+'.json')!;return {relative_path:row.relative_path,sha256:row.sha256,source_type:row.source_type,source_id:row.source_id};};
 const references=[...new Set([source.occurrence_id,...source.payload].flatMap(f=>f.type_ref.kind==='reference'?[f.type_ref.selector]:[]))].sort().map(selector=>{const target=graph.nodes.find(n=>n.selector===selector)!;return {selector,kind:target.kind,source:sourceEvidence(selector),body_sha256:sha256(canonicalJson(target.body)),semantics:'reference-not-embedding'};});
 const descriptor={schema_version:'domainspec.generated-event-descriptor/v1-candidate',protocol_id:'typescript.bound-event/v1',selector:node.selector,source:sourceEvidence(node.selector),contract_sha256:sha256(canonicalJson(source)),event_type:source.event_type,version:source.version,occurrence_id:source.occurrence_id,occurred_at_policy:source.occurred_at_policy,payload:source.payload,references,value_profile:'domainspec.event-values/v1-candidate',return_semantics:'immutable-occurrence-data',effect_contract:generated?'explicit-clock-only':'none',publication:false,occurrence_registration:false,distributed_exactly_once_claim:false,primary_callable_count:1,provider:{sha256:provider.sha256},authority_effect:'none'};
 const binding:SemanticCase={id:'case-0',mode:'event-descriptor',format:'string',values:[],expected:{kind:'value',value:canonicalJson({...descriptor,descriptor_sha256:sha256(canonicalJson(descriptor))})}};
 const referenceScalars=new Map(references.map(reference=>[reference.selector,eventReferenceIdentity(graph,reference.selector,reason=>{throw new TypeError('DS_EVENT_CONTROLS:'+reason);}).scalar] as const));
 const shared=createEventSemanticCases(node,binding,referenceScalars);
 return shared.state==='ready'?{...shared,adapter:'event',...module}:shared;
}
