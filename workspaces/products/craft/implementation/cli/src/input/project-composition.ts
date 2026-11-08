import {validatePortableSource} from '../typed-backend/portable-function.js';
import {renderRustComposition} from '../generation/rust-composition.js';
import fs from 'node:fs';
import path from 'node:path';
import {canonicalJson, sha256, type SourceManifestV1} from './source-manifest.js';
import {compileDeclarativeFunction,mappingInputs} from '../typed-backend/declarative-function.js';
import {normalizeCompositionOntology} from './composition-ontology.js';

/** Project composition is an opt-in compiler profile, not a new admitted meta-type. */
export interface CompiledComposition {
 id:string;
 source:any;
 dependency_graph:unknown;
 artifacts:Record<string,string>;
 validation:{profile:'domainspec.project-composition/v1'; result:'pass'; ontology_admitted:false; authority_effect:'none'};
}
type CoreNode={selector:string;kind:string;body:any};
const fail=(s:string):never=>{throw Error('DS_PROJECT_COMPOSITION: '+s);};
const same=(a:unknown,b:unknown,label:string)=>{if(canonicalJson(a)!==canonicalJson(b))fail(label);};
const safe=(s:unknown):s is string=>typeof s==='string'&&/^[A-Za-z_][A-Za-z0-9_]*$/.test(s)&&!['__proto__','constructor','prototype'].includes(s);
function obj(v:any){if(!v||typeof v!=='object'||Array.isArray(v))fail('object required');}
function keys(v:any,required:string[],optional:string[]=[]){obj(v);if(required.some(k=>!Object.hasOwn(v,k))||Object.keys(v).some(k=>![...required,...optional].includes(k)))fail('unknown/missing member');}
function names(v:any){obj(v);if(Object.keys(v).some(k=>!safe(k)))fail('unsafe name');}
const scalar=(t:string)=>['string','identifier','timestamp'].includes(t)?'String':t==='integer'?'Int':t==='boolean'?'Bool':t;
const text=(v:any)=>JSON.stringify(v,null,2)+'\n';
const env=(v:any)=>typeof v==='string'&&/^[A-Z][A-Z0-9_]*$/.test(v);
function limits(v:any){if(!Number.isInteger(v.timeout)||v.timeout<1||v.timeout>30000||!Number.isInteger(v.maxBytes)||v.maxBytes<1||v.maxBytes>1048576)fail('boundary limits');}

function validateBoundary(model:any,bindings:any,c:any){
 keys(model,['schemas','integrations','flows','endpoint'],['portability','modules']);same(model.portability??null,c.portability??null,'portability profile binding');same(model.flows,{},'procedural flows unsupported');
 names(model.schemas);names(model.integrations);
 for(const [name,fields] of Object.entries(model.schemas) as [string,any][]){
  names(fields);if(!Object.keys(fields).length)fail('empty schema');const record:Record<string,string>={};
  for(const [field,s]of Object.entries(fields) as [string,any][]){
   keys(s,['type'],['items','optional','nullable','min','max','const','pattern']);
   const t=s.type==='list'?s.items:s.type;
   if(typeof t!=='string'||!['string','identifier','timestamp','integer','boolean'].includes(t)&&!Object.hasOwn(model.schemas,t))fail('unknown boundary type');
   if(s.type==='list'){if(!Number.isInteger(s.max)||!['string','identifier'].includes(t)&&!Object.hasOwn(model.schemas,t))fail('list contract');}else if(Object.hasOwn(s,'items'))fail('unexpected items');
   for(const k of ['optional','nullable'])if(Object.hasOwn(s,k)&&s[k]!==true)fail('invalid optional/nullable');
   for(const k of ['min','max'])if(Object.hasOwn(s,k)&&(!Number.isSafeInteger(s[k])||s[k]<0))fail('schema bound');
   if(s.min!==undefined&&s.type!=='integer'||s.max!==undefined&&!['integer','string','identifier','timestamp','list'].includes(s.type)||s.min>s.max)fail('schema bound type');
   if(s.pattern!==undefined){if(!['string','identifier','timestamp'].includes(s.type)||typeof s.pattern!=='string'||s.pattern.length>256)fail('pattern type');try{new RegExp(s.pattern);}catch{fail('pattern');}}
   if(Object.hasOwn(s,'const')){if(s.const===null){if(!s.nullable)fail('null constant');}else if(scalar(s.type)==='String'?typeof s.const!=='string':s.type==='integer'?!Number.isSafeInteger(s.const):s.type==='boolean'?typeof s.const!=='boolean':true)fail('constant type');}
   record[field]=(s.type==='list'?scalar(t)+'[]':scalar(t))+(s.optional||s.nullable?'?':'');
  }
  same(c.records[name],record,'boundary record mismatch '+name);
 }
 for(const [alias,m]of Object.entries(model.modules??{})as [string,any][]){
  if(!/^[A-Z][A-Za-z0-9]*$/.test(alias)||model.portability!=='node-rust-v1')fail('module alias/profile');keys(m,['source_sha256','source_text','input','output','schemas','statuses']);
  if(typeof m.source_text!=='string'||m.source_sha256!==sha256(m.source_text)||!Object.hasOwn(m.schemas,m.input)||!Object.hasOwn(m.schemas,m.output))fail('module source/interface');names(m.schemas);names(m.statuses);
  for(const [name,fields]of Object.entries(m.schemas)as [string,any][]){const qualified:any={};for(const [field,s]of Object.entries(fields)as [string,any][]){const t=s.type==='list'?s.items:s.type;qualified[field]={...s,...(Object.hasOwn(m.schemas,t)?s.type==='list'?{items:alias+'__'+t}:{type:alias+'__'+t}:{})};}same(model.schemas[alias+'__'+name],qualified,'module schema binding');}
  if(!Object.keys(m.statuses).length||Object.values(m.statuses).some((s:any)=>!Number.isInteger(s)||s<200||s>599||[204,205,304].includes(s)))fail('module statuses');
 }
 const ep=model.endpoint;
 keys(ep,['id','target','runtime','method','path','input','output','authEnv','maxBytes','timeout','errorStatus','statuses','errors','result']);
 if(!safe(ep.id)||!safe(ep.result)||!((ep.target==='node-http'&&ep.runtime==='node>=26.8.1')||(ep.target==='rust-http'&&ep.runtime==='rust>=1.94'))||ep.method!=='POST'||typeof ep.path!=='string'||!/^\/[A-Za-z0-9/_-]*$/.test(ep.path)||!env(ep.authEnv)||!Object.hasOwn(model.schemas,ep.input)||!Object.hasOwn(model.schemas,ep.output))fail('endpoint contract');
 if(ep.target==='rust-http')for(const fields of Object.values(model.schemas) as any[])for(const field of Object.values(fields) as any[])if(field.pattern!==undefined){
  // Deliberately bounded common regex syntax; reject JS-only escapes/lookarounds before generation.
  if(!/^[A-Za-z0-9_^$[\]{}()+*?|, -]+$/.test(field.pattern)||field.pattern.includes('(?'))fail('unsupported Rust pattern syntax');
  for(const count of field.pattern.matchAll(/\{([0-9]+)(?:,([0-9]*))?\}/g))if(Number(count[1])>1000||count[2]&&Number(count[2])>1000)fail('Rust pattern repetition limit');
 }
 limits(ep);if(!Number.isInteger(ep.errorStatus)||ep.errorStatus<400||ep.errorStatus>599)fail('error status');
 for(const statuses of [ep.statuses,ep.errors]){names(statuses);for(const s of Object.values(statuses) as number[])if(!Number.isInteger(s)||s<200||s>599||[204,205,304].includes(s))fail('HTTP status');}
 if(!Object.keys(ep.statuses).length)fail('status required');same(c.output,ep.output,'endpoint output mismatch');
 function selector(s:any){if(typeof s!=='string'||!/^input(?:\.[A-Za-z_][A-Za-z0-9_]*)+$/.test(s))fail('input selector');let t=ep.input;for(const p of s.split('.').slice(1)){if(!safe(p)||!Object.hasOwn(model.schemas[t]??{},p))fail('unresolved selector '+s);t=model.schemas[t][p].type;}return t;}
 for(const b of Object.values(model.integrations) as any[]){
  keys(b,['query','transport','output','timeout','maxBytes'],['provided','urlEnv','secretEnv','module','input']);names(b.query);limits(b);
  if(['module-local','module-http'].includes(b.transport)){
   const m=model.modules?.[b.module];const mapped=typeof b.input==='string'&&!b.input.startsWith('input.');const mapping=mapped?c.nodes.find((n:any)=>n.id===b.input):undefined;const inputType=mapped?(mapping?.kind==='Mapping'&&!mappingInputs(mapping).length?mapping.target:null):selector(b.input);if(!m||inputType!==b.module+'__'+m.input||b.output!==b.module+'__'+m.output||b.provided!==undefined||Object.keys(b.query).length)fail('module invocation interface');
   if(b.transport==='module-http'&&(!env(b.urlEnv)||!env(b.secretEnv))||b.transport==='module-local'&&(b.urlEnv!==undefined||b.secretEnv!==undefined))fail('module transport environment');continue;
  }
  if(b.module!==undefined||b.input!==undefined)fail('unexpected module fields');
  if(!['provided','http-get','provided-or-http'].includes(b.transport)||!Object.hasOwn(model.schemas,b.output))fail('integration contract');
  if(b.transport==='provided'){if(b.urlEnv||b.secretEnv||Object.keys(b.query).length)fail('provided transport conflict');}else if(!env(b.urlEnv))fail('URL environment reference');
  if(b.secretEnv!==undefined&&!env(b.secretEnv))fail('secret environment reference');
  if(b.transport==='http-get'){if(b.provided!==undefined)fail('http transport conflict');}else if(selector(b.provided)!==b.output)fail('provided type mismatch');
  for(const s of Object.values(b.query))if(!['string','identifier','integer'].includes(selector(s)))fail('query scalar required');
 }
 if(!Array.isArray(bindings))fail('binding array');const roots:Record<string,string>={input:ep.input},used=new Set();
 for(const b of bindings){keys(b,['name','integration'],['condition','input']);if(Object.hasOwn(b,'condition')&&!['module-local','module-http'].includes(model.integrations[b.integration]?.transport))fail('guard requires module binding');if(!safe(b.name)||Object.hasOwn(roots,b.name)||!Object.hasOwn(model.integrations,b.integration))fail('unresolved/duplicate binding');const i=model.integrations[b.integration];if(i.transport.startsWith('module-')&&!i.input.startsWith('input.'))same(b.input??null,{mapping:i.input,type:i.module+'__'+model.modules[i.module].input},'binding input mapping closure');else if(Object.hasOwn(b,'input'))fail('unexpected binding input mapping');roots[b.name]=i.output;used.add(b.integration);}
 if(bindings.some((b:any)=>Object.hasOwn(b,'condition')||Object.hasOwn(b,'input'))||c.bindings)same(c.bindings??null,bindings.map(({name,condition,input}:any)=>({name,...(condition?{condition}:{}),...(input?{input}:{})})),'binding guard closure');
 same(Object.keys(model.integrations).sort(),[...used].sort(),'unbound integration');same(c.roots,roots,'root closure');
}

export function compileProjectComposition(source:any,nodes:readonly CoreNode[]):CompiledComposition {
 keys(source,['schema_version','id','source_text','contract','core_bindings','model','bindings','ontology']);
 if(source.schema_version!=='domainspec.project-composition/v1'||typeof source.id!=='string'||!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(source.id)||typeof source.source_text!=='string')fail('composition profile');
 const compiled=compileDeclarativeFunction(source.contract),c=compiled.contract;
 validatePortableSource(source);
 validateBoundary(source.model,source.bindings,c);
 names(source.core_bindings);
 const expected=[...Object.keys(c.records).filter(k=>!Object.hasOwn(source.model.schemas,k)),...Object.keys(c.calculations)].sort();
 same(Object.keys(source.core_bindings).sort(),expected,'core binding set');
 const coreContracts:Record<string,any>={},coreDependencies:any[]=[];
 for(const [name,b]of Object.entries(source.core_bindings) as [string,any][]){
  keys(b,['selector','fields']);names(b.fields);if(Object.values(b.fields).some(v=>!safe(v))||new Set(Object.values(b.fields)).size!==Object.keys(b.fields).length)fail('core field bindings');
  const n=nodes.find(n=>n.selector===b.selector);if(!n)fail('missing core selector '+b.selector);
  const tc=n!.body.typed_contract;if(!tc)fail('typed core required');coreContracts[name]=tc;
  if(Object.hasOwn(c.calculations,name)){
   if(n!.kind!=='Calculation'||tc.schema_version!=='domainspec.typed-calculation/v1')fail('calculation kind');
   same(Object.keys(b.fields).sort(),[...c.calculations[name]!].sort(),'calculation argument set');
   same(c.calculations[name]!.map(k=>b.fields[k]),tc.inputs.map((v:any)=>v.name),'calculation argument order');
   for(const v of [...tc.inputs,{type:tc.result}])same(v.type,{kind:'scalar',name:'UInt64'},'calculation UInt64 contract');
  }else{
   if(!['Entity','Value Object','ValueObject'].includes(n!.kind)||tc.schema_version!=='domainspec.typed-record/v1')fail('record kind');
   same(Object.keys(b.fields).sort(),Object.keys(c.records[name]!).sort(),'record field set');
   same(Object.values(b.fields).sort(),tc.properties.map((p:any)=>p.name).sort(),'record property set');
   for(const [field,type]of Object.entries(c.records[name]!)){const p=tc.properties.find((p:any)=>p.name===b.fields[field]);if(p.type.kind!=='scalar')fail('unsupported core field type');same(type,p.type.name+(p.cardinality==='one'?'':'?'),'core field type '+field);}
  }
  coreDependencies.push({name,selector:b.selector,fields:b.fields});
 }
 const o=normalizeCompositionOntology(source.ontology);
 if(o.source_format==='domainspec-json'){
  let authored:unknown;try{authored=JSON.parse(source.source_text);}catch{fail('direct JSON source syntax');}
  same(authored,source.contract,'direct JSON source contract');
 }
 if(o.status!=='generated-scaffold'||o.authority_effect!=='none'||o.ontology_admitted!==false||o.source?.sha256!==sha256(source.source_text)||!Array.isArray(o.nodes)||!Array.isArray(o.references))fail('ontology source/claim');
 same(o.composition_trace,compiled.trace,'ontology composition trace');
 const os=new Map<string,any>(),ids=new Set<string>();
 for(const n of o.nodes){if(!safe(n.name)||os.has(n.name)||typeof n.id!=='string'||ids.has(n.id)||n.source?.sha256!==o.source.sha256||!Number.isInteger(n.source.line)||n.source.line<1||n.source.line>source.source_text.split('\n').length||typeof n.meaning?.text!=='string'||!n.meaning.text.trim())fail('ontology identity/source');os.set(n.name,n);ids.add(n.id);}
 const expectedNames=[...Object.keys(c.records),...Object.keys(c.calculations),...c.nodes.map(n=>n.id),...Object.keys(source.model.integrations),source.model.endpoint.id,source.model.endpoint.result];
 same([...os.keys()].sort(),expectedNames.sort(),'ontology declaration closure');
 for(const n of c.nodes){const on=os.get(n.id);same(on.typed_contract,n,'ontology typed behavior');same(on.id,n.ontology,'ontology behavior identity');same(on.meaning.text,n.meaning,'ontology meaning');}
 for(const [name,tc]of Object.entries(coreContracts)){const on=os.get(name);same(on.typed_contract,tc,'ontology core contract');same(on.id,tc.ontology_node??tc.ontology_calculation,'ontology core identity');}
 for(const [name,tc]of Object.entries(coreContracts)){
  const on=os.get(name),binding=source.core_bindings[name];
  if(Object.hasOwn(c.records,name)){
   if(!Array.isArray(on.properties))fail('ontology properties');
   same(on.properties.map((p:any)=>p.name).sort(),Object.keys(c.records[name]!).sort(),'ontology property names');
   for(const [field,compiledField]of Object.entries(binding.fields)){
    const p=on.properties.find((p:any)=>p.name===field),target=tc.properties.find((p:any)=>p.name===compiledField);
    same(p.ontology,target.ontology_property,'core property identity binding');same(p.meaning,target.meaning,'core property meaning');
   }
  }else{same(on.inputs,c.calculations[name],'ontology calculation inputs');same(on.result,'UInt64','ontology calculation result');}
 }
 for(const [name,record]of Object.entries(c.records))same(os.get(name).record_type,record,'ontology record');
 for(const [name,s]of Object.entries(source.model.schemas))same(os.get(name).constraints,s,'ontology schema constraints');
 for(const [name,b]of Object.entries(source.model.integrations))same(os.get(name).binding,b,'ontology integration');
 same(os.get(source.model.endpoint.id).binding,source.model.endpoint,'ontology endpoint');
 const result=os.get(source.model.endpoint.result);same(result.assertions,c.assertions,'ontology assertions');same(result.cases,c.results,'ontology cases');if(c.bindings)same(result.bindings,source.bindings,'ontology guarded bindings');
 const expectedRefs=new Set<string>();
 const add=(from:string,to:string,role:string)=>{if(!os.has(from)||!os.has(to))fail('unresolved ontology dependency');expectedRefs.add(canonicalJson({source:os.get(from).id,target:os.get(to).id,role,evidence:os.get(from).source}));};
 function expression(owner:string,e:any,locals=new Set<string>()){
  if(e.op==='path'){const head=e.path[0],target=c.roots[head]??(os.has(head)?head:null);if(!locals.has(head)&&target)add(owner,target,'depends-on');return;}
  if(e.op==='call'){if(os.has(e.name))add(owner,e.name,'calls');for(const a of e.args)expression(owner,a,locals);return;}
  if(e.op!=='literal'){expression(owner,e.collection,locals);expression(owner,e.where,new Set([...locals,e.binding]));}
 }
 for(const n of c.nodes){
  if(n.kind==='Mapping'){add(n.id,n.target!,'maps-to');for(const input of mappingInputs(n)){const sourceType=c.schema_version==='domainspec.declarative-function/v1'?input.type:input.type.replace(/\?|\[\]/g,'');if(os.has(sourceType))add(n.id,sourceType,'maps-from');}for(const e of Object.values(n.fields!))expression(n.id,e,new Set(mappingInputs(n).map(p=>p.name)));}
  if(n.kind==='Query'){expression(n.id,n.source);expression(n.id,n.where,new Set([n.binding!]));expression(n.id,n.select,new Set([n.binding!]));}
  if(n.kind==='Rule')expression(n.id,n.expression);
 }
 if(source.model.modules){same(o.module_imports,Object.fromEntries(Object.entries(source.model.modules).map(([alias,m]:[string,any])=>[alias,{source_sha256:m.source_sha256,input:m.input,output:m.output}])),'ontology module imports');}
 const ep=source.model.endpoint;
 add(ep.id,ep.result,'exposes');add(ep.id,ep.input,'input');add(ep.id,ep.output,'output');add(ep.result,ep.output,'returns');
 for(const a of c.assertions)expression(ep.result,a.condition);
 for(const v of c.results){expression(ep.result,v.condition);expression(ep.result,v.value);}
 for(const b of source.bindings){if(b.input)add(b.integration,b.input.mapping,'input-mapping');if(b.condition){expression(b.integration,b.condition);add(ep.result,b.integration,'conditionally-binds');}add(ep.result,b.integration,'binds');add(b.integration,source.model.integrations[b.integration].output,'output');add(b.integration,ep.input,'request-context');}
 for(const [name,record]of Object.entries(c.records))for(const type of Object.values(record)){const target=type.replace(/\?$/,'').replace(/\[\]$/,'');if(os.has(target))add(name,target,'property-type');}
 for(const [name,fields]of Object.entries(c.calculations))for(const field of fields){const owners=Object.keys(coreContracts).filter(k=>Object.hasOwn(c.records[k]??{},field));if(owners.length!==1)fail('calculation input owner');add(name,owners[0]!,'input-type-context');}
 same(o.references.map((r:any)=>canonicalJson(r)).sort(),[...expectedRefs].sort(),'ontology dependency set');

 return {id:source.id,source,dependency_graph:{behavior:compiled.trace,core:coreDependencies,roots:c.roots,result:c.results,bindings:source.bindings},artifacts:{...(source.model.endpoint.target==='rust-http'?renderRustComposition(c,source.core_bindings,source.model):{'behavior.mjs':compiled.source}),'composition.json':text(c),'composition-trace.json':text(compiled.trace),'ontology.json':text(source.ontology),'function.json':text(source.model),'bindings.json':text(source.bindings),[o.source_format==='domainspec-json'?'source.json':'source.alch']:source.source_text},validation:{profile:'domainspec.project-composition/v1',result:'pass',ontology_admitted:false,authority_effect:'none'}};
}

export function loadProjectCompositions(root:string,manifest:SourceManifestV1,nodes:readonly CoreNode[]):readonly CompiledComposition[]{
 return manifest.sources.filter(s=>s.source_type==='composition').map(s=>{
  const bytes=fs.readFileSync(path.join(root,s.relative_path));if(sha256(bytes)!==s.sha256)fail('composition source drift');
  const compiled=compileProjectComposition(JSON.parse(bytes.toString('utf8')),nodes);if(compiled.id!==s.source_id)fail('composition source identity');return compiled;
 });
}
