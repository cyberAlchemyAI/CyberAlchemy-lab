import {createHash} from 'node:crypto';
import {existsSync, mkdtempSync, readFileSync, readdirSync, renameSync, rmSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {compileLocalHost, buildLocalHost} from './local-host.js';
import {compileEventExecution} from './event-execution.js';
import {loadDomainSpecCompiler} from './domainspec-cli.js';

const fail=(s:string):never=>{throw Error('STATE_MIGRATION: '+s);};
const sha=(s:string|Buffer)=>createHash('sha256').update(s).digest('hex');
const safe=(s:string)=>/^[A-Za-z][A-Za-z0-9_]*$/.test(s)&&!['constructor','prototype','__proto__'].includes(s);

/** A structural extension: existing record bytes are opaque to the generated default Mapping. */
export async function compileStateMigration(source:string) {
  const lines:string[]=[], values:Record<string,string>={};let id='',block=false,profiles=0;
  for(const line of source.split(/\r?\n/)) {
    if(line==='profile local-host-migration-v1'){profiles++;lines.push('profile local-host-v1');continue;}
    if(!line.trim()||line.trimStart().startsWith('#')){lines.push(line);continue;}
    const header=/^migration ([a-z][a-z0-9-]{0,63}):$/.exec(line);
    if(header){if(id)fail('one migration required');id=header[1];block=true;lines.push('');continue;}
    if(block&&/^\s/.test(line)) {
      const m=/^  (from-contract|subject|mapper|field) (.+)$/.exec(line);
      if(!m||Object.hasOwn(values,m[1]))fail('invalid migration declaration');
      values[m![1]]=m![2];lines.push('');continue;
    }
    block=false;lines.push(line);
  }
  if(profiles!==1||!id||Object.keys(values).length!==4||!/^[a-f0-9]{64}$/.test(values['from-contract']??'')||!safe(values.subject??'')||!safe(values.mapper??''))fail('complete source-bound migration required');
  const field=/^([A-Za-z][A-Za-z0-9_]*) default (string|integer|boolean) (.+)$/.exec(values.field);
  if(!field||!safe(field[1]))fail('one literal scalar addition required');
  const name=field![1],scalar=field![2];let value:unknown;
  try{value=JSON.parse(field![3]);}catch{fail('JSON literal default required');}
  if(scalar==='string'?(typeof value!=='string'||!value.length):scalar==='integer'?!Number.isSafeInteger(value):typeof value!=='boolean')fail('default type');
  const baseline=lines.join('\n');const host=await compileLocalHost(baseline);
  const {config}=await compileEventExecution(host.normalized);
  if(config.model.facts.some(f=>f.id===name)||!config.model.facts.some(f=>f.subject_ref===values.subject))fail('new field and existing subject required');
  const executions=config.executions.filter(e=>config.model.actions.find(a=>a.id===e.operation)?.subject_refs.includes(values.subject));
  const mappings=[...new Set(executions.map(e=>e.state))];
  if(!mappings.length||config.executions.some(e=>mappings.includes(e.payload)))fail('separate state and payload mappings required');
  // Lower the additive declaration into the existing event model; request/event fields stay unchanged.
  const normalized=baseline.split('\n').flatMap(line=>line===`entity ${values.subject}:`?[line,`  ${name}: ${scalar} optional`]:mappings.some(m=>line===`mapping ${m}:`)?[line,`  field ${name} default ${scalar} ${JSON.stringify(value)}`]:[line]).join('\n');
  await compileLocalHost(normalized);
  const contract={schema_version:'domainspec.declarative-function/v1',records:{StateAddition:{[name]:{string:'String',integer:'Int',boolean:'Bool'}[scalar]}},roots:{},calculations:{},
    nodes:[{id:values.mapper,kind:'Mapping',ontology:'ALCH-STATE-MIGRATION',meaning:'Compute the explicit scalar default for a structural state extension',target:'StateAddition',fields:{[name]:{op:'literal',value}}}],
    assertions:[],results:[{condition:{op:'literal',value:true},value:{op:'call',name:values.mapper,args:[]}}],output:'StateAddition'};
  const compiler=await loadDomainSpecCompiler();const generated=compiler.compileDeclarativeFunction(contract);
  return {normalized,generated,manifest:{profile:'alch.state-migration/v1',id,from_contract:values['from-contract'],subject:values.subject,
    field:name,scalar,default:value,mapper:values.mapper,operations:executions.map(e=>e.operation),state_mappings:mappings,
    mapper_sha256:sha(generated.source),compiler:compiler.binding,source_sha256:sha(source),authority_effect:'none'}};
}

export async function buildStateMigration(file:string,output:string) {
  if(path.extname(file)!=='.alch'||existsSync(output))fail('source extension or existing output');
  const source=readFileSync(file,'utf8'),plan=await compileStateMigration(source);
  const stage=mkdtempSync(path.join(path.dirname(path.resolve(output)),'.alch-migration-'));
  try {
    const input=path.join(stage,'host.alch'),bundle=path.join(stage,'bundle');writeFileSync(input,plan.normalized);
    await buildLocalHost(input,bundle);
    const json=(name:string,v:unknown)=>writeFileSync(path.join(bundle,name),JSON.stringify(v,null,2)+'\n');
    writeFileSync(path.join(bundle,'authored.alch'),source);
    const host=JSON.parse(readFileSync(path.join(bundle,'host.json'),'utf8'));host.source_sha256=sha(source);json('host.json',host);
    const hostPlan=JSON.parse(readFileSync(path.join(bundle,'host-plan.json'),'utf8'));
    hostPlan.source_sha256=sha(source);hostPlan.migration={declaration:plan.manifest.id,contract:'migration.json',steps:['rehearse','drain','provision-generation','migrate','validate','select']};json('host-plan.json',hostPlan);
    const ontology=JSON.parse(readFileSync(path.join(bundle,'host-ontology.json'),'utf8'));
    ontology.source_sha256=sha(source);
    ontology.nodes.push({id:plan.manifest.id,type:'StateMigration'},{id:plan.manifest.mapper,type:'Mapping'});
    ontology.relations.push({from:plan.manifest.id,type:'uses',to:plan.manifest.mapper});json('host-ontology.json',ontology);
    json('migration.json',plan.manifest);json('migration.contract.json',plan.generated.contract);json('migration.trace.json',plan.generated.trace);
    writeFileSync(path.join(bundle,'migration.mjs'),plan.generated.source);
    writeFileSync(path.join(bundle,'migrate.mjs'),`import {execute} from './migration.mjs';\nimport {readFileSync} from 'node:fs';\nconst rows=JSON.parse(readFileSync(0,'utf8'));\nconst extension=execute({},{});\nconst result=rows.map(row=>{if(!row||typeof row!=='object'||Array.isArray(row)||Object.keys(extension).some(k=>Object.hasOwn(row,k)))throw Error('STATE_FIELD_CONFLICT');return {...row,...extension};});\nprocess.stdout.write(JSON.stringify(result));\n`);
    const walk=(d:string):string[]=>readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(d,e.name)):[path.join(d,e.name)]);
    json('host-manifest.json',{profile:'local-host-migration-v1',files:Object.fromEntries(walk(bundle).filter(p=>path.basename(p)!=='host-manifest.json').sort().map(p=>[path.relative(bundle,p),sha(readFileSync(p))])),authority_effect:'none'});
    if(readFileSync(file,'utf8')!==source)fail('source changed');renameSync(bundle,output);
    return {status:'built',profile:'local-host-migration-v1',output:path.resolve(output),authority_effect:'none'};
  }finally{rmSync(stage,{recursive:true,force:true});}
}
