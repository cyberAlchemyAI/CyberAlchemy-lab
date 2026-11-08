import path from 'node:path';
import {digest} from './domainspec-profile.js';
import type {Expression} from './declarative-profile.js';

type Row = {text:string; line:number};
export type DerivedDeclaration = {
 name:string; kind:string; key:string; ontology:string; identity_origin:'authored'|'derived';
 meaning:string; meaning_origin:'authored'|'derived-structural'; meaning_line:number; key_origin:'authored'|'derived'; line:number; rows:Row[];
 identity?:{field:string; origin:'authored'|'derived-single-identifier'};
 properties:{name:string; ontology:string; type:string; required:boolean; meaning:string; meaning_origin:'authored'|'derived-structural'; meaning_line:number; line:number}[];
};
const fail=(message:string):never=>{throw Error('ALCH_ONTOLOGY: '+message);};
const namePattern=/^[A-Za-z_][A-Za-z0-9_]*$/;
const idPattern=/^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$/;
const string=(text:string):string=>{let v:unknown;try{v=JSON.parse(text);}catch{return fail('quoted annotation required');}if(typeof v!=='string'||!v.trim())return fail('nonempty annotation required');return v;};
const coreKinds=new Set(['entity','value-object','calculation']);
const compositionKinds=new Set(['mapping','query','rule']);
const kinds:Record<string,string|null>={entity:'Entity','value-object':'Value Object',calculation:'Calculation',mapping:'Mapping',query:'Query',rule:'Rule',result:'Query',endpoint:'Interface',schema:null,integration:null};

/** Elaborates missing bindings for the existing compiler; generated descriptions assert structure only. */
export function elaborateOntology(source:string){
 const domain=/^domain ([a-zA-Z0-9_-]+)(?:\s|$)/m.exec(source)?.[1];if(!domain)fail('domain required');
 const lines=source.split(/\r?\n/),blocks:{kind:string;name:string;line:number;rows:Row[]}[]=[],preamble:string[]=[];
 let current:typeof blocks[number]|undefined;
 for(let index=0;index<lines.length;index++){
  const line=lines[index],m=/^(entity|value-object|schema|calculation|mapping|query|rule|result|integration|endpoint|ontology) (\w+):$/.exec(line);
  if(m){current={kind:m[1],name:m[2],line:index+1,rows:[]};blocks.push(current);}
  else if(current&&(!line.trim()||/^\s/.test(line)||line.startsWith('#')))current.rows.push({text:line,line:index+1});
  else {current=undefined;preamble.push(line);}
 }
 const declarations=blocks.filter(b=>b.kind!=='ontology');
 const names=new Set<string>();for(const b of declarations){if(names.has(b.name))fail('ambiguous declaration name '+b.name);names.add(b.name);}
 const overrides=new Map<string,typeof blocks[number]>();
 for(const b of blocks.filter(b=>b.kind==='ontology')){if(!names.has(b.name)||overrides.has(b.name))fail('unknown/duplicate ontology target '+b.name);overrides.set(b.name,b);}
 const records:DerivedDeclaration[]=[],emitted:string[]=[...preamble],ids=new Set<string>(),stableKeys=new Set<string>();
 for(const b of declarations){
  const annotations=new Map<string,string>(),annotationLines=new Map<string,number>(),propertyOverrides=new Map<string,{ontology:string;meaning:string;line:number}>();
  const put=(key:string,value:string,line:number)=>{if(annotations.has(key))fail('duplicate annotation '+b.name+'.'+key);annotations.set(key,value);annotationLines.set(key,line);};
  const rows:Row[]=[];
  for(const row of b.rows){const m=/^  (key|ontology|meaning|identity) (.+)$/.exec(row.text);
   if(m)put(m[1],m[1]==='identity'?m[2]:string(m[2]),row.line);else rows.push(row);
  }
  for(const row of overrides.get(b.name)?.rows??[]){const text=row.text.trim();if(!text||text.startsWith('#'))continue;
   const property=/^property (\w+) ("(?:[^"\\]|\\.)*") ("(?:[^"\\]|\\.)*")$/.exec(text);
   if(property){if(propertyOverrides.has(property[1]))fail('duplicate property override');propertyOverrides.set(property[1],{ontology:string(property[2]),meaning:string(property[3]),line:row.line});continue;}
   const m=/^(id|meaning|identity) (.+)$/.exec(text);if(!m)fail('unsupported ontology override '+text);put(m![1]==='id'?'ontology':m![1],m![1]==='identity'?m![2]:string(m![2]),row.line);
  }
  const key=annotations.get('key')??b.name;if(!namePattern.test(key))fail('stable key must be an identifier');
  const stableKey=JSON.stringify([domain,b.kind,key]);if(stableKeys.has(stableKey))fail('duplicate stable key');stableKeys.add(stableKey);
  const id=annotations.get('ontology')??`ALCH-${digest(stableKey).slice(0,24).toUpperCase()}`;
  if(!idPattern.test(id)||ids.has(id))fail('invalid/duplicate ontology identity '+id);ids.add(id);
  const meaning=annotations.get('meaning')??`${kinds[b.kind]??(b.kind==='schema'?'Boundary record':'Integration binding')} ${b.name}, structurally derived from its Alch declaration.`;
  const properties:DerivedDeclaration['properties']=[];
  if(['entity','value-object','schema'].includes(b.kind))for(const row of rows){const m=/^  (\w+): (\w+(?:\[\])?)(.*)$/.exec(row.text);if(!m)continue;const override=propertyOverrides.get(m[1]);
   const propertyId=override?.ontology??`${id}#${m[1]}`;if(propertyId!==`${id}#${m[1]}`)fail('property must belong to declaration '+b.name+'.'+m[1]);
   properties.push({name:m[1],ontology:propertyId,type:m[2],required:b.kind==='schema'?!/\boptional\b/.test(m[3]):/\brequired\b/.test(m[3]),meaning:override?.meaning??`${m[1]} is a ${m[2]} property of ${b.name}.`,meaning_origin:override?'authored':'derived-structural',meaning_line:override?.line??row.line,line:row.line});
  }
  if([...propertyOverrides.keys()].some(k=>!properties.some(p=>p.name===k)))fail('unknown property override '+b.name);
  let identity:DerivedDeclaration['identity'];
  if(annotations.has('identity')){const field=annotations.get('identity')!;if(b.kind!=='entity'||!properties.some(p=>p.name===field&&p.required&&['identifier','string'].includes(p.type)))fail('invalid explicit identity '+b.name);identity={field,origin:'authored'};}
  else if(b.kind==='entity'){const candidates=properties.filter(p=>p.type==='identifier'&&p.required);if(candidates.length!==1)fail(`entity ${b.name} needs an identity annotation: expected exactly one required identifier`);identity={field:candidates[0].name,origin:'derived-single-identifier'};}
  const d:DerivedDeclaration={name:b.name,kind:b.kind,key,ontology:id,identity_origin:annotations.has('ontology')?'authored':'derived',meaning,meaning_origin:annotations.has('meaning')?'authored':'derived-structural',meaning_line:annotationLines.get('meaning')??b.line,key_origin:annotations.has('key')?'authored':'derived',line:b.line,rows:rows.filter(r=>r.text.trim()&&!r.text.trimStart().startsWith('#')),properties,...(identity?{identity}:{})};records.push(d);
  emitted.push(`${b.kind} ${b.name}:`);
  if(compositionKinds.has(b.kind))emitted.push('  ontology '+JSON.stringify(id),'  meaning '+JSON.stringify(meaning));
  emitted.push(...rows.map(r=>r.text));
  if(coreKinds.has(b.kind)){
   emitted.push('',`ontology ${b.name}:`,'  id '+JSON.stringify(id),'  meaning '+JSON.stringify(meaning));
   if(identity)emitted.push('  identity '+identity.field);
   for(const p of properties)emitted.push(`  property ${p.name} ${JSON.stringify(p.ontology)} ${JSON.stringify(p.meaning)}`);
  }
 }
 return {source:emitted.join('\n'),domain:domain!,source_sha256:digest(source),declarations:records};
}

type Parsed = {ontologySource:ReturnType<typeof elaborateOntology>;contract:any;coreContracts:Record<string,unknown>;model:any;boundaryBindings:{name:string;integration:string;condition?:Expression;input?:{mapping:string;type:string}}[]};
export function deriveOntology(parsed:Parsed,trace:any,sourcePath:string){
 // Provenance names the source with its content digest, independently of the build host.
 sourcePath=path.basename(sourcePath);
 const origin=parsed.ontologySource,decls=new Map(origin.declarations.map(d=>[d.name,d]));
 const source=(line:number)=>({path:sourcePath,line,sha256:origin.source_sha256});
 const references:{source:string;target:string;role:string;evidence:ReturnType<typeof source>}[]=[];
 const add=(from:string,to:string,role:string)=>{if(!decls.has(from)||!decls.has(to))fail(`unresolved scaffold reference ${from} -> ${to}`);const row={source:decls.get(from)!.ontology,target:decls.get(to)!.ontology,role,evidence:source(decls.get(from)!.line)};if(!references.some(r=>r.source===row.source&&r.target===row.target&&r.role===role))references.push(row);};
 const roots:Record<string,string>={input:parsed.model.endpoint.input,...Object.fromEntries(parsed.boundaryBindings.map(b=>[b.name,parsed.model.integrations[b.integration].output]))};
 function expression(owner:string,e:Expression,locals=new Set<string>()){
  if(e.op==='path'){const head=e.path[0];if(!locals.has(head)){const target=roots[head]??(decls.has(head)?head:null);if(target)add(owner,target,'depends-on');}return;}
  if(e.op==='call'){if(decls.has(e.name))add(owner,e.name,'calls');for(const a of e.args)expression(owner,a,locals);return;}
  if(e.op!=='literal'){expression(owner,e.collection,locals);expression(owner,e.where,new Set([...locals,e.binding]));}
 }
 for(const n of parsed.contract.nodes){
  if(n.kind==='Mapping'){add(n.id,n.target,'maps-to');if(n.input&&decls.has(n.input.type))add(n.id,n.input.type,'maps-from');for(const e of Object.values(n.fields))expression(n.id,e as Expression,new Set(n.input?[n.input.name]:[]));}
  if(n.kind==='Query'){expression(n.id,n.source);expression(n.id,n.where,new Set([n.binding]));expression(n.id,n.select,new Set([n.binding]));}
  if(n.kind==='Rule')expression(n.id,n.expression);
 }
 const result=parsed.model.endpoint.result,endpoint=parsed.model.endpoint.id;
 add(endpoint,result,'exposes');add(endpoint,parsed.model.endpoint.input,'input');add(endpoint,parsed.model.endpoint.output,'output');
 add(result,parsed.model.endpoint.output,'returns');
 for(const a of parsed.contract.assertions)expression(result,a.condition);
 for(const r of parsed.contract.results){expression(result,r.condition);expression(result,r.value);}
 for(const b of parsed.boundaryBindings){if(b.input)add(b.integration,b.input.mapping,'input-mapping');if(b.condition){expression(b.integration,b.condition);add(result,b.integration,'conditionally-binds');}add(result,b.integration,'binds');add(b.integration,parsed.model.integrations[b.integration].output,'output');add(b.integration,parsed.model.endpoint.input,'request-context');}
 for(const d of origin.declarations){
  for(const p of d.properties){const target=p.type.replace(/\[\]$/,'');if(decls.has(target))add(d.name,target,'property-type');}
  if(d.kind==='calculation')for(const field of parsed.contract.calculations[d.name]??[]){const owners=origin.declarations.filter(r=>['entity','value-object'].includes(r.kind)&&r.properties.some(p=>p.name===field));if(owners.length!==1)fail('ambiguous calculation input owner '+field);add(d.name,owners[0].name,'input-type-context');}
 }
 const nodes=origin.declarations.map(d=>({id:d.ontology,name:d.name,kind:d.kind,meta_type:kinds[d.kind],stable_key:d.key,key_origin:d.key_origin,identity_origin:d.identity_origin,meaning:{text:d.meaning,origin:d.meaning_origin,source:source(d.meaning_line)},source:source(d.line),...(d.identity?{entity_identity:d.identity}:{}),properties:d.properties.map(p=>({...p,source:source(p.line),meaning_source:source(p.meaning_line)})),clauses:d.rows.map(r=>({text:r.text.trim(),source:source(r.line)})),typed_contract:parsed.contract.nodes.find((n:any)=>n.id===d.name)??parsed.coreContracts[d.name]??null,record_type:parsed.contract.records[d.name]??null,...(d.kind==='schema'?{constraints:parsed.model.schemas[d.name]}:{}),...(d.kind==='integration'?{binding:parsed.model.integrations[d.name]}:{}),...(d.kind==='endpoint'?{binding:parsed.model.endpoint}:{}),...(d.kind==='result'?{assertions:parsed.contract.assertions,cases:parsed.contract.results,...(parsed.contract.bindings?{bindings:parsed.boundaryBindings}:{})}:{}),...(d.kind==='calculation'?{inputs:parsed.contract.calculations[d.name],result:'UInt64'}:{})}));
 return {...(parsed.model.modules?{module_imports:Object.fromEntries(Object.entries(parsed.model.modules).map(([alias,m]:[string,any])=>[alias,{source_sha256:m.source_sha256,input:m.input,output:m.output}]))}:{}),schema_version:'alchlang.derived-ontology/v1',domain:origin.domain,source:{path:sourcePath,sha256:origin.source_sha256},nodes,references,composition_trace:trace,status:'generated-scaffold',reference_semantics:'compiler dependencies; not admitted ontology relationships',authority_effect:'none',ontology_admitted:false};
}
export function explainOntology(ontology:ReturnType<typeof deriveOntology>,selector:string){
 const matches=ontology.nodes.filter(n=>n.name===selector||n.id===selector);if(matches.length!==1)fail('unknown or ambiguous declaration '+selector);const node=matches[0];
 const dependencies=ontology.references.filter(r=>r.source===node.id).map(r=>({role:r.role,name:ontology.nodes.find(n=>n.id===r.target)!.name,id:r.target,source:r.evidence}));
 return {schema_version:'alchlang.ontology-explanation/v1',subject:node.name,answer:node.meaning.text,meaning_origin:node.meaning.origin,definition:node,dependencies,claim:'static source explanation; no invocation outcome observed',authority_effect:'none'};
}
