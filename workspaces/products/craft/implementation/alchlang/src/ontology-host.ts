import {createHash} from 'node:crypto';
import {existsSync,mkdirSync,mkdtempSync,readFileSync,readdirSync,renameSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {compileLocalHost,buildLocalHost} from './local-host.js';
import {compileEventExecution} from './event-execution.js';
import {loadDomainSpecCompiler} from './domainspec-cli.js';

const hash=(v:string|Buffer)=>createHash('sha256').update(v).digest('hex');
const fail=(v:string):never=>{throw Error('ONTOLOGY_HOST: '+v);};
type Property={id:string;name:string;type:string;required:boolean;owner:string;default?:unknown};
export type HostOntology={schema_version:string;domain:string;source_sha256:string;status:string;authority_effect:string;
  records:Record<string,{id:string;properties:Property[]}>;operations:any[];mappings:any[]};

/** The runtime facts and schema properties are projections of these same typed records. */
export function factsFromOntology(o:HostOntology) {
  return Object.entries(o.records).flatMap(([subject,r])=>r.properties.map(p=>({id:p.name,subject_ref:subject,type:p.type,required:p.required,owner:p.owner})));
}
function propertySchema(p:Property):any {
  const schema:any=p.type==='integer'?{type:'integer',minimum:-9007199254740991,maximum:9007199254740991}:
    p.type==='boolean'?{type:'boolean'}:p.type==='record'?{type:'object'}:{type:'string',minLength:1};
  if(p.type==='timestamp'){schema.format='date-time';schema.pattern='^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z$';}
  if(Object.hasOwn(p,'default'))schema.default=p.default;
  return schema;
}
export function schemasFromOntology(o:HostOntology) {
  const record=(properties:Property[],required:string[])=>({$schema:'https://json-schema.org/draft/2020-12/schema',type:'object',properties:Object.fromEntries(properties.map(p=>[p.name,propertySchema(p)])),required,additionalProperties:false});
  const facts=Object.fromEntries(Object.entries(o.records).map(([name,r])=>[name,record(r.properties,r.properties.filter(p=>p.required).map(p=>p.name))]));
  const states=Object.fromEntries(o.operations.map(op=>{
    const m=o.mappings.find(m=>m.id===op.state),props=o.records[op.subject].properties;
    const fields=m.clauses.map((c:any)=>props.find(p=>p.name===c.target_field)!);
    const schema=record(fields,fields.map((p:Property)=>p.name));
    for(const c of m.clauses)if(c.source_field&&!props.find(p=>p.name===c.source_field)!.required)schema.properties[c.target_field]={anyOf:[schema.properties[c.target_field],{type:'null'}]};
    return [op.operation,schema];
  }));
  return {schema_version:'alch.host-schemas/v1',ontology_sha256:hash(JSON.stringify(o)),facts,states,authority_effect:'none'};
}

export async function compileOntologyHost(source:string) {
  const defaults=new Map<string,{subject:string;name:string;type:string;value:unknown}>();let subject='',profiles=0;
  const lines=source.split(/\r?\n/).map(line=>{
    if(line==='profile ontology-host-v1'){profiles++;return 'profile local-host-v1';}
    const entity=/^entity ([A-Za-z][A-Za-z0-9_]*):$/.exec(line);
    if(entity)subject=entity[1];else if(line.trim()&&!/^\s|^#/.test(line))subject='';
    if(!subject||line.trimStart().startsWith('#')||!line.includes(' default '))return line;
    const field=/^  ([A-Za-z][A-Za-z0-9_]*): (string|integer|boolean) optional default (.+)$/.exec(line);
    if(!field||['constructor','prototype','__proto__'].includes(field[1]))fail('default requires an optional scalar property');
    let value:unknown;try{value=JSON.parse(field![3]);}catch{fail('literal default required');}
    const type=field![2];
    if(type==='string'?(typeof value!=='string'||!value.length):type==='integer'?!Number.isSafeInteger(value):typeof value!=='boolean')fail('default type');
    const key=subject+'.'+field![1];if(defaults.has(key))fail('duplicate default');
    defaults.set(key,{subject,name:field![1],type,value});return `  ${field![1]}: ${type} optional`;
  });
  if(profiles!==1)fail('one ontology-host-v1 profile required');
  const baseline=lines.join('\n');const host=await compileLocalHost(baseline);const {config}=await compileEventExecution(host.normalized);
  const records:HostOntology['records']={};
  for(const f of config.model.facts){
    if(f.subject_ref===null)fail('host facts require an entity subject');
    const subject=f.subject_ref!;
    const id='ALCH-'+hash(JSON.stringify([config.model.domain_id,'entity',f.subject_ref])).slice(0,24).toUpperCase();
    records[subject]??={id,properties:[]};
    const d=defaults.get(f.subject_ref+'.'+f.id);
    records[subject].properties.push({id:id+'#'+f.id,name:f.id,type:f.type,required:f.required,owner:f.owner,...(d?{default:d.value}:{})});
  }
  const operations:any[]=config.executions.map(e=>({...e,subject:config.model.actions.find(a=>a.id===e.operation)!.subject_refs[0]}));
  const mappings=structuredClone(config.model.mappings);
  for(const d of defaults.values()){
    const stateIds=[...new Set(operations.filter(op=>op.subject===d.subject).map(op=>op.state))];
    if(!stateIds.length||operations.some(op=>stateIds.includes(op.payload)))fail('default requires distinct state mappings');
    for(const id of stateIds){const m=mappings.find(m=>m.id===id)!;
      if(m.clauses.some(c=>c.target_field===d.name))fail('default mapping is derived; remove duplicate clause');
      m.clauses.push({target_field:d.name,source_field:null,default_value:{value_type:d.type as any,value:d.value}});
    }
  }
  const ontology:HostOntology={schema_version:'alch.typed-host-ontology/v1',domain:config.model.domain_id,source_sha256:hash(source),status:'generated-scaffold',authority_effect:'none',records,operations,mappings};
  // Emit legacy syntax from the derived mapping clauses, retaining all original source clauses.
  const normalized:string[]=[];let current='';
  const finish=()=>{if(!current)return;const original=config.model.mappings.find(m=>m.id===current)!;
    for(const c of ontology.mappings.find(m=>m.id===current)!.clauses.filter((c:any)=>!original.clauses.some(x=>x.target_field===c.target_field)))normalized.push(`  field ${c.target_field} default ${c.default_value.value_type} ${JSON.stringify(c.default_value.value)}`);
    current='';};
  for(const line of lines){if(line.trim()&&!/^\s|^#/.test(line)){finish();const m=/^mapping ([A-Za-z][A-Za-z0-9_]*):$/.exec(line);if(m)current=m[1];}normalized.push(line);}finish();
  const lowered=normalized.join('\n');const loweredHost=await compileLocalHost(lowered);const actual=(await compileEventExecution(loweredHost.normalized)).config;
  if(JSON.stringify(actual.model.facts)!==JSON.stringify(factsFromOntology(ontology)))fail('fact projection drift');
  for(const m of ontology.mappings)if(JSON.stringify(actual.model.mappings.find(x=>x.id===m.id)!.clauses)!==JSON.stringify(m.clauses))fail('mapping projection drift');
  const compiler=await loadDomainSpecCompiler();const generated=[];
  for(const [subject,r] of Object.entries(ontology.records))for(const p of r.properties.filter(p=>Object.hasOwn(p,'default'))){
    const identity=hash(p.id).slice(0,24),mapper='Default_'+identity;
    const contract={schema_version:'domainspec.declarative-function/v1',records:{Addition:{[p.name]:{string:'String',integer:'Int',boolean:'Bool'}[p.type]}},roots:{},calculations:{},
      nodes:[{id:mapper,kind:'Mapping',ontology:r.id,meaning:'Default for '+p.id,target:'Addition',fields:{[p.name]:{op:'literal',value:p.default}}}],assertions:[],
      results:[{condition:{op:'literal',value:true},value:{op:'call',name:mapper,args:[]}}],output:'Addition'};
    const output=compiler.compileDeclarativeFunction(contract);
    generated.push({directory:'defaults/'+identity,output,descriptor:{profile:'alch.state-migration/v1',id:'add-'+identity,subject,property_id:p.id,field:p.name,scalar:p.type,default:p.default,mapper,
      operations:ontology.operations.filter(op=>op.subject===subject).map(op=>op.operation),state_mappings:[...new Set(ontology.operations.filter(op=>op.subject===subject).map(op=>op.state))],mapper_sha256:hash(output.source),compiler:compiler.binding,source_sha256:hash(source),authority_effect:'none'}});
  }
  return {normalized:lowered,ontology,schemas:schemasFromOntology(ontology),generated};
}

export async function buildOntologyHost(file:string,output:string){
  if(path.extname(file)!=='.alch'||existsSync(output))fail('source extension or existing output');
  const source=readFileSync(file,'utf8'),plan=await compileOntologyHost(source),stage=mkdtempSync(path.join(path.dirname(path.resolve(output)),'.alch-ontology-'));
  try{
    const input=path.join(stage,'host.alch'),bundle=path.join(stage,'bundle');writeFileSync(input,plan.normalized);await buildLocalHost(input,bundle);
    const json=(name:string,value:unknown)=>writeFileSync(path.join(bundle,name),JSON.stringify(value,null,2)+'\n');
    writeFileSync(path.join(bundle,'authored.alch'),source);
    for(const name of ['host.json','host-plan.json']){const data=JSON.parse(readFileSync(path.join(bundle,name),'utf8'));data.source_sha256=hash(source);data.typed_ontology='typed-ontology.json';data.schemas='schemas.json';json(name,data);}
    json('typed-ontology.json',plan.ontology);json('schemas.json',plan.schemas);
    const hostOntology=JSON.parse(readFileSync(path.join(bundle,'host-ontology.json'),'utf8'));hostOntology.source_sha256=hash(source);hostOntology.typed_records='typed-ontology.json';json('host-ontology.json',hostOntology);
    for(const g of plan.generated){mkdirSync(path.join(bundle,g.directory),{recursive:true});json(g.directory+'/descriptor.json',g.descriptor);json(g.directory+'/contract.json',g.output.contract);json(g.directory+'/trace.json',g.output.trace);
      writeFileSync(path.join(bundle,g.directory,'migration.mjs'),g.output.source);
      writeFileSync(path.join(bundle,g.directory,'migrate.mjs'),`import {execute} from './migration.mjs';\nimport {readFileSync} from 'node:fs';\nconst extension=execute({},{});\nconst rows=JSON.parse(readFileSync(0,'utf8'));\nprocess.stdout.write(JSON.stringify(rows.map(row=>{if(!row||typeof row!=='object'||Array.isArray(row)||Object.keys(extension).some(k=>Object.hasOwn(row,k)))throw Error('STATE_FIELD_CONFLICT');return {...row,...extension};})));\n`);
    }
    json('default-mappers.json',plan.generated.map(g=>({property_id:g.descriptor.property_id,directory:g.directory})));
    const walk=(d:string):string[]=>readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(d,e.name)):[path.join(d,e.name)]);
    json('host-manifest.json',{profile:'ontology-host-v1',files:Object.fromEntries(walk(bundle).filter(f=>path.relative(bundle,f)!=='host-manifest.json').sort().map(f=>[path.relative(bundle,f),hash(readFileSync(f))])),authority_effect:'none'});
    if(readFileSync(file,'utf8')!==source)fail('source drift');renameSync(bundle,output);
    return {status:'built',profile:'ontology-host-v1',output:path.resolve(output),authority_effect:'none'};
  }finally{rmSync(stage,{recursive:true,force:true});}
}
