import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,readdirSync,cpSync,renameSync,rmSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {loadDomainSpecCompiler} from './domainspec-cli.js';

const fail=(s:string):never=>{throw Error('SEMANTIC_HOST: '+s)};
const hash=(s:string|Buffer)=>createHash('sha256').update(s).digest('hex');
const safe=(s:string)=>/^[A-Za-z][A-Za-z0-9_-]*$/.test(s)&&!['constructor','prototype','__proto__'].includes(s);
type Property={id:string;type:string;required:boolean;default?:unknown};
type RecordType={name:string;kind:string;properties:Property[];line:number;from?:string};
type Block={kind:string;id:string;line:number;fields:Record<string,string>};
const scalar=(type:string,value:unknown):boolean=>type==='integer'?Number.isSafeInteger(value):type==='boolean'?typeof value==='boolean':type==='record'?!!value&&typeof value==='object'&&!Array.isArray(value):typeof value==='string'&&(type==='string'||value.length>0);
const dsType=(p:Property)=>({integer:'Int',boolean:'Bool',record:'Opaque'}[p.type]??'String')+(p.required?'':'?');

/** A single parsed representation owns schemas, ontology relationships and both execution plans. */
export async function compileSemanticHost(source:string){
 const globals:Record<string,string>={},records:Record<string,RecordType>={},blocks:Block[]=[];let current:RecordType|Block|undefined;
 for(const [offset,line] of source.split(/\r?\n/).entries()){
  if(!line.trim()||line.trimStart().startsWith('#'))continue;
  if(/^\s/.test(line)){
   if(!current||!line.startsWith('  ')||line.startsWith('   '))fail(`indentation at ${offset+1}`);
   if('properties' in current!){
    const from=/^  from ([A-Za-z][A-Za-z0-9_]*)$/.exec(line);
    if(from){if(current.from||current.properties.length||!['event','projection'].includes(current.kind))fail('record derivation');current.from=from[1];continue;}
    const p=/^  ([A-Za-z][A-Za-z0-9_]*): (identifier|timestamp|string|integer|boolean|record) (required|optional)(?: default (.+))?$/.exec(line);
    if(!p||!safe(p[1])||current.from||current.properties.some(x=>x.id===p[1]))fail(`property at ${offset+1}`);
    const property:Property={id:p![1],type:p![2],required:p![3]==='required'};
    if(p![4]!==undefined){if(current.kind!=='entity')fail('defaults belong to entity state');try{property.default=JSON.parse(p![4]);}catch{fail('literal default');}if(!scalar(property.type,property.default)||property.type==='record'||property.type==='timestamp')fail('default type');}
    current.properties.push(property);
   }else{
    const f=/^  ([a-z-]+) (\S.*)$/.exec(line);if(!f||Object.hasOwn(current!.fields,f[1]))fail(`duplicate field at ${offset+1}`);current!.fields[f![1]]=f![2];
   }continue;
  }
  current=undefined;
  const header=/^(entity|command|event|projection|operation|delivery) ([A-Za-z][A-Za-z0-9_-]*):$/.exec(line);
  if(header){const [,kind,id]=header;if(!safe(id)||records[id]||blocks.some(b=>b.id===id))fail('duplicate/reserved declaration');
   if(['entity','command','event','projection'].includes(kind)){if(!/^[A-Za-z][A-Za-z0-9_]*$/.test(id))fail('record name');current={name:id,kind,properties:[],line:offset+1};records[id]=current;}
   else{current={kind,id,line:offset+1,fields:{}};blocks.push(current);}continue;
  }
  const g=/^(profile|domain|owner|actor|boundary|binding) ([A-Za-z][A-Za-z0-9_-]*)$/.exec(line);
  if(!g||Object.hasOwn(globals,g[1]))fail(`unknown/duplicate declaration at ${offset+1}`);globals[g![1]]=g![2];
 }
 for(const k of ['profile','domain','owner','actor','boundary','binding'])if(!globals[k]||!safe(globals[k]))fail('explicit '+k+' required');
 if(globals.profile!=='semantic-host-v1'||globals.binding!=='sqlite-event-store-v2')fail('unsupported profile or binding');
 const bindingBytes=readFileSync(new URL('./event-templates/semantic-binding.json',import.meta.url));
 const binding=JSON.parse(bindingBytes.toString());
 if(!binding.records||['OutboxMessage','InboxReceipt','EventEnvelope'].some(name=>!Array.isArray(binding.records[name])||!binding.records[name].length))fail('missing binding-owned type');
 if(binding.schema_version!=='domainspec.alch-system-types/v1'||binding.binding_id!==globals.binding||binding.version!==2)fail('binding type version');
 for(const [name,properties] of Object.entries(binding.records)){
  if(!Array.isArray(properties)||properties.some(p=>!safe(p.id)||!['identifier','timestamp','string','integer','boolean','record'].includes(p.type)||typeof p.required!=='boolean')||new Set(properties.map(p=>p.id)).size!==properties.length)fail('incompatible binding-owned type');
  if(records[name])fail('binding-owned type collision: '+name);
  records[name]={name,kind:'system',properties:properties as Property[],line:0};
 }
 const resolve=(r:RecordType,active=new Set<string>()):void=>{
  if(!r.from)return;if(active.has(r.name))fail('record cycle');active.add(r.name);
  const parent=records[r.from];if(!parent||parent.kind!==(r.kind==='event'?'entity':'event'))fail('record role: '+r.name);resolve(parent,active);r.properties=structuredClone(parent.properties).map(p=>({id:p.id,type:p.type,required:p.required}));active.delete(r.name);
 };
 for(const r of Object.values(records)){resolve(r);if(!r.properties.length)fail('empty type: '+r.name);}
 const needRecord=(name:string,kind:string)=>{const r=records[name];if(!r||r.kind!==kind)fail('expected '+kind+': '+name);return r;};
 const operations=blocks.filter(b=>b.kind==='operation'),deliveries=blocks.filter(b=>b.kind==='delivery');
 if(operations.length!==2||deliveries.length!==1)fail('one producer, consumer and delivery supported');
 const delivery=deliveries[0],d=delivery.fields;
 const required=['producer','consumer','max-attempts','max-receives','visibility-seconds','retention-seconds','dead-letter'];
 if(required.some(k=>!d[k])||Object.keys(d).some(k=>!required.includes(k)))fail('delivery fields');
 const positive=(key:string)=>{const n=Number(d[key]);if(!/^[1-9][0-9]*$/.test(d[key])||!Number.isSafeInteger(n)||n>2147483647)fail('delivery number '+key);return n;};
 if(!safe(d['dead-letter'])||d['dead-letter']===delivery.id||records[d['dead-letter']]||operations.some(o=>o.id===d['dead-letter']))fail('dead-letter channel identity');
 const producer=operations.find(o=>o.id===d.producer),consumer=operations.find(o=>o.id===d.consumer);
 if(!producer||!consumer||producer===consumer)fail('delivery roles');
 const executions:any[]=[],mappings:any[]=[],actions:any[]=[],transitions:any[]=[];
 for(const op of [producer!,consumer!]){
  const isProducer=op===producer,b=op.fields,allowed=isProducer?['input','state','key','transition','emits','assign']:['on','state','key','assign'];
  if(Object.keys(b).some(k=>!allowed.includes(k))||(isProducer?['input','state','key','transition','emits']:['on','state','key']).some(k=>!b[k]))fail('operation fields '+op.id);
  const input=needRecord(isProducer?b.input:b.on,isProducer?'command':'event');
  const state=needRecord(b.state,isProducer?'entity':'projection');
  if(!input.properties.some(p=>p.id===b.key&&p.required&&p.type==='identifier')||!state.properties.some(p=>p.id===b.key&&p.required&&p.type==='identifier'))fail('explicit typed identity required');
  let transition:any;
  if(isProducer){const t=/^([A-Za-z][A-Za-z0-9_]*) ([A-Za-z][A-Za-z0-9_-]*) -> ([A-Za-z][A-Za-z0-9_-]*)$/.exec(b.transition);if(!t)fail('transition syntax');
   if(!state.properties.some(p=>p.id===t![1]&&p.type==='string'&&p.required&&!Object.hasOwn(p,'default'))||input.properties.some(p=>p.id===t![1]))fail('transition field belongs to persisted state');
   transition={field:t![1],from:t![2],to:t![3]};transitions.push({operation:op.id,subject:state.name,...transition});
   needRecord(b.emits,'event');if(consumer!.fields.on!==b.emits)fail('consumer event mismatch');
  }
  const assignments:Record<string,unknown>={};
  if(b.assign){const a=/^([A-Za-z][A-Za-z0-9_]*) (.+)$/.exec(b.assign);if(!a)fail('assignment syntax');let v;try{v=JSON.parse(a![2]);}catch{fail('assignment literal');}const p=state.properties.find(p=>p.id===a![1]);if(!p||!scalar(p.type,v)||p.type==='record'||a![1]===b.key||a![1]===transition?.field)fail('assignment target');assignments[a![1]]=v;}
  if(transition)assignments[transition.field]=transition.to;
  const clauses=state.properties.map(p=>{
   const src=input.properties.find(x=>x.id===p.id);
   if(src&&src.type!==p.type)fail('mapping type: '+p.id);
   if(Object.hasOwn(assignments,p.id))return {target_field:p.id,source_field:null,default_value:{value:assignments[p.id]},mode:'assignment'};
   if(Object.hasOwn(p,'default'))return {target_field:p.id,source_field:p.id,default_value:{value:p.default},mode:'fallback'};
   if(!src||p.required&&!src.required)fail('missing total state mapping: '+p.id);
   return {target_field:p.id,source_field:p.id,mode:'copy'};
  });
  // Unknown command properties are never silently discarded.
  if(input.properties.some(p=>!state.properties.some(s=>s.id===p.id)))fail('unconsumed input property');
  mappings.push({id:state.name+'_Map',source_ref:input.name,target_ref:state.name,clauses,total:true});
  executions.push({operation:op.id,kind:isProducer?'producer':'consumer',input:input.name,subject:state.name,storage:state.kind+':'+state.name,key:b.key,state:state.name+'_Map',...(transition?{transition}:{}),...(isProducer?{payload:b.emits+'_Map'}:{})});
  actions.push({id:op.id,subject_refs:[state.name],actor_refs:[globals.actor],authority_boundary_ref:globals.boundary,precondition_rule_refs:[],permission_refs:[]});
 }
 const state=records[producer!.fields.state],event=records[producer!.fields.emits];
 const eventClauses=event.properties.map(p=>{const s=state.properties.find(x=>x.id===p.id);if(!s||s.type!==p.type||p.required&&!s.required)fail('event mapping type');return {target_field:p.id,source_field:p.id,mode:'copy'};});
 if(!event.properties.some(p=>p.id===producer!.fields.key&&p.required)||consumer!.fields.key!==producer!.fields.key)fail('event identity preservation');
 mappings.push({id:event.name+'_Map',source_ref:state.name,target_ref:event.name,clauses:eventClauses,total:true});
 const compiler=await loadDomainSpecCompiler(),generated=[];
 for(const m of mappings){
  const input=records[m.source_ref],output=records[m.target_ref];
  // An opaque JSON object is a named, uninspected record; no nested business fields are invented.
  const types={Opaque:{},Input:Object.fromEntries(input.properties.map(p=>[p.id,dsType(p)])),Output:Object.fromEntries(output.properties.map(p=>[p.id,dsType(p)]))};
  const fields=Object.fromEntries(m.clauses.map((c:any)=>{
   const p=input.properties.find(p=>p.id===c.source_field);
   const src={op:'path',path:['input',c.source_field]},lit={op:'literal',value:c.default_value?.value};
   return [c.target_field,c.mode==='assignment'?lit:c.mode==='fallback'?(p?(p.required?src:{op:'call',name:'coalesce',args:[src,lit]}):lit):src];
  }));
  const contract={schema_version:'domainspec.declarative-function/v1',records:types,roots:{input:'Input'},calculations:{},nodes:[{id:'Map',kind:'Mapping',ontology:'ALCH-'+hash(globals.domain+':'+m.id).slice(0,24).toUpperCase(),meaning:'Typed '+m.source_ref+' to '+m.target_ref,target:'Output',fields}],assertions:[],results:[{condition:{op:'literal',value:true},value:{op:'call',name:'Map',args:[]}}],output:'Output'};
  const outputGenerated=compiler.compileDeclarativeFunction(contract);generated.push({id:m.id,...outputGenerated});
 }
 const backfills:any[]=[];
 for(const record of Object.values(records).filter(r=>['entity','projection'].includes(r.kind))){
  let origin=record;while(origin.from)origin=records[origin.from];
  for(const property of origin.properties.filter(p=>Object.hasOwn(p,'default'))){
   const contract={schema_version:'domainspec.declarative-function/v1',records:{Addition:{[property.id]:dsType({...property,required:true})}},roots:{},calculations:{},nodes:[{id:'Default',kind:'Mapping',ontology:'ALCH-'+hash(globals.domain+':'+record.name+':'+property.id).slice(0,24).toUpperCase(),meaning:'Backfill missing '+record.name+'.'+property.id,target:'Addition',fields:{[property.id]:{op:'literal',value:property.default}}}],assertions:[],results:[{condition:{op:'literal',value:true},value:{op:'call',name:'Default',args:[]}}],output:'Addition'};
   backfills.push({storage:record.kind+':'+record.name,field:property.id,file:record.name+'_'+property.id+'.mjs',...compiler.compileDeclarativeFunction(contract)});
  }
 }
 const nodes=[...Object.values(records).map(r=>({id:r.name,kind:r.kind,properties:r.properties,line:r.line,derived_from:r.from??null})),...operations.map(o=>({id:o.id,kind:'operation',line:o.line})),{id:globals.actor,kind:'actor'},{id:globals.boundary,kind:'boundary',owner:globals.owner},{id:globals.binding,kind:'binding',version:binding.version,source_sha256:hash(bindingBytes)},{id:delivery.id,kind:'delivery',...d},{id:d['dead-letter'],kind:'dead-letter-channel'},...mappings.map(m=>({id:m.id,kind:'Mapping',...m})),...transitions.map(t=>({id:t.operation+':transition',kind:'transition',...t})),{id:'atomic-state-outbox',kind:'effect',guarantee:'atomic-state-and-outbox',binding:globals.binding},{id:'invoke-permission',kind:'permission',actor:globals.actor,boundary:globals.boundary}];
 if(new Set(nodes.map(n=>n.id)).size!==nodes.length)fail('ambiguous generated or authored identity');
 const relations=executions.flatMap(e=>[{from:e.operation,type:'input',to:e.input},{from:e.operation,type:'writes',to:e.subject},{from:e.operation,type:'actor',to:globals.actor},{from:e.operation,type:'boundary',to:globals.boundary},{from:e.operation,type:'maps',to:e.state}]);
 relations.push({from:producer!.id,type:'emits',to:event.name},{from:consumer!.id,type:'consumes',to:event.name},{from:producer!.id,type:'performs',to:'atomic-state-outbox'},{from:'atomic-state-outbox',type:'imports',to:'OutboxMessage'},{from:consumer!.id,type:'imports',to:'InboxReceipt'});
 const ontology={schema_version:'alch.semantic-ontology/v2',domain:globals.domain,source_sha256:hash(source),records,nodes:nodes.map(n=>({...n,stable_id:'ALCH-'+hash(globals.domain+':'+n.kind+':'+n.id).slice(0,24).toUpperCase()})),relations,status:'generated-scaffold',authority_effect:'none'};
 const propertySchema=(p:Property):any=>p.type==='record'?{$ref:'#/$defs/portableObject'}:p.type==='integer'?{type:'integer',minimum:-9007199254740991,maximum:9007199254740991}:p.type==='boolean'?{type:'boolean'}:{type:'string',...(p.type!=='string'?{minLength:1}:{}),...(p.type==='timestamp'?{format:'date-time',pattern:'^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z$'}:{})};
 const portable={$defs:{portableObject:{type:'object',additionalProperties:{$ref:'#/$defs/portableValue'}},portableValue:{anyOf:[{type:['null','boolean','string']},{type:'integer',minimum:-9007199254740991,maximum:9007199254740991},{type:'array',items:{$ref:'#/$defs/portableValue'}},{$ref:'#/$defs/portableObject'}]}}};
 const schemas=Object.fromEntries(Object.entries(records).map(([name,r])=>[name,{$schema:'https://json-schema.org/draft/2020-12/schema',...portable,type:'object',properties:Object.fromEntries(r.properties.map(p=>[p.id,propertySchema(p)])),required:r.properties.filter(p=>p.required).map(p=>p.id),additionalProperties:false}]));

 const config={schema_version:'alch.semantic-execution/v2',binding_digest:hash(source),model:{domain_id:globals.domain,facts:Object.values(records).flatMap(r=>r.properties.map(p=>({...p,subject_ref:r.name}))),mappings,actions,rules:[],permissions:[],transitions},executions,event:event.name,aggregate:state.name,transport:delivery.id,max_attempts:positive('max-attempts'),max_receives:positive('max-receives'),retention_ms:positive('retention-seconds')*1000,dead_letter:d['dead-letter'],lease_ms:positive('visibility-seconds')*1000,observation:{stages:[],attributes:[],cardinalityBudget:1000},authority_effect:'none'};
 const persistence=JSON.parse(readFileSync(new URL('../../extensions/generatable-operation-patterns-v1/bindings/sqlite-transactional-outbox.binding-set.json',import.meta.url),'utf8'));
 const ref=(id:string)=>globals.domain.toLowerCase()+':'+id.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/_/g,'-').toLowerCase(),ceiling='intent-send-acceptance-delivery-and-commit-remain-distinct';
 const bindingSet={...persistence,binding_set_id:globals.domain+'-semantic',subject_ref:ref(producer!.id),
  message_channels:[{channel_id:delivery.id,purpose:'delivery',allowed_event_refs:[ref(event.name)],publisher_operation_refs:[ref(producer!.id)],consumer_operation_refs:[ref(consumer!.id)],evidence_boundary:ceiling},{channel_id:d['dead-letter'],purpose:'dead-letter',allowed_event_refs:[ref(event.name)],publisher_operation_refs:[],consumer_operation_refs:[],evidence_boundary:ceiling}],
  delivery_policies:[{policy_id:'delivery-policy',semantics:'at-least-once',acknowledgement_boundary:'provider-accepted',ordering_scope:'none',visibility_timeout_seconds:positive('visibility-seconds'),retention_seconds:positive('retention-seconds'),max_receive_count:positive('max-receives'),dead_letter_channel_ref:d['dead-letter'],deduplication_owner_ref:'consumer:inbox-message-id',evidence_boundary:ceiling}],
  transport_failure_policies:[{policy_id:'failure-policy',retry_eligibility:'idempotent-message-id-only',max_attempts:positive('max-attempts'),backoff:'exponential-bounded',unknown_outcome:'reconcile-by-message-id',terminal_action:'dead-letter',evidence_boundary:ceiling}],
  transport_bindings:[{binding_id:delivery.id,mode:'message',direction:'publish-subscribe',operation_ref:ref(producer!.id),event_ref:ref(event.name),channel_ref:delivery.id,delivery_policy_ref:'delivery-policy',failure_policy_ref:'failure-policy',envelope_profile_ref:'envelope:domainspec-event-json-v1',evidence_boundary:ceiling}]};
 const targets=Object.fromEntries((['typescript','rust'] as const).map(t=>[t,compiler.compileEventBindings(bindingSet,t)]));
 return {config,ontology,schemas,generated,backfills,binding,bindingSet,targets,compiler:compiler.binding};
}

export async function buildSemanticHost(file:string,output:string){
 if(path.extname(file)!=='.alch'||existsSync(output))fail('source extension or existing output');
 const source=readFileSync(file,'utf8'),plan=await compileSemanticHost(source),stage=mkdtempSync(path.join(path.dirname(path.resolve(output)),'.alch-semantic-'));
 try{
  const json=(name:string,value:unknown)=>writeFileSync(path.join(stage,name),JSON.stringify(value,null,2)+'\n');
  writeFileSync(path.join(stage,'source.alch'),source);json('config.json',plan.config);json('typed-ontology.json',plan.ontology);json('schemas.json',plan.schemas);json('binding.json',plan.binding);json('binding-set.json',plan.bindingSet);for(const [target,b] of Object.entries(plan.targets)){json(target+'.manifest.json',b.manifest);writeFileSync(path.join(stage,'bindings.'+(target==='rust'?'rs':'ts')),b.source);}json('compiler.json',plan.compiler);
  mkdirSync(path.join(stage,'backfills'));json('backfills.json',plan.backfills.map(g=>({storage:g.storage,field:g.field,file:g.file})));for(const g of plan.backfills){writeFileSync(path.join(stage,'backfills',g.file),g.source);json('backfills/'+g.file+'.contract.json',g.contract);json('backfills/'+g.file+'.trace.json',g.trace);}
  mkdirSync(path.join(stage,'mappers'));for(const g of plan.generated){writeFileSync(path.join(stage,'mappers',g.id+'.mjs'),g.source);json('mappers/'+g.id+'.contract.json',g.contract);json('mappers/'+g.id+'.trace.json',g.trace);}
  writeFileSync(path.join(stage,'mappers.mjs'),plan.generated.map((g,i)=>`import {execute as m${i}} from './mappers/${g.id}.mjs';`).join('\n')+'\nexport const mappers={'+plan.generated.map((g,i)=>JSON.stringify(g.id)+`: f=>m${i}({input:f},{})`).join(',')+'};\n');
  cpSync(new URL('./event-templates/semantic-handler.mjs',import.meta.url),path.join(stage,'handler.mjs'));
  mkdirSync(path.join(stage,'rust/src'),{recursive:true});for(const f of ['lib.rs','main.rs'])cpSync(new URL('./event-templates/semantic-'+f,import.meta.url),path.join(stage,'rust/src',f));
  cpSync(path.join(stage,'config.json'),path.join(stage,'rust/config.json'));
  // Rust lowering consumes the public DomainSpec typed contract, not a parallel mapping DSL.
  const rustExpr=(e:any):string=>{
   if(e.op==='literal')return `json!(${JSON.stringify(e.value)})`;
   if(e.op==='path'&&e.path.length===2&&e.path[0]==='input')return `f[${JSON.stringify(e.path[1])}].clone()`;
   if(e.op==='call'&&e.name==='coalesce'&&e.args.length===2)return `{let value=${rustExpr(e.args[0])};if value.is_null(){${rustExpr(e.args[1])}}else{value}}`;
   return fail('unsupported DomainSpec Rust mapping expression');
  };
  const rustMappings=plan.generated.map(g=>{
   const node=(g.contract as any).nodes[0];
   const fields=Object.entries(node.fields).map(([key,e]:[string,any])=>{
    const insert=`o.insert(${JSON.stringify(key)}.into(),${rustExpr(e)});`;
    return e.op==='path'?`if f.get(${JSON.stringify(e.path[1])}).is_some(){${insert}}`:insert;
   }).join('');
   return `${JSON.stringify(g.id)}=>{${fields}},`;
  }).join('');
  writeFileSync(path.join(stage,'rust/src/mappings.rs'),`// Lowered from DomainSpec generated Mapping contracts.\nfn mapping(_c:&V,id:&V,f:&V)->V{let mut o=serde_json::Map::new();match s(id){${rustMappings}_=>unreachable!("validated mapping")};V::Object(o)}\n`);

  writeFileSync(path.join(stage,'rust/Cargo.toml'),'[package]\nname="alch-event"\nversion="0.2.0"\nedition="2021"\n[dependencies]\nserde_json="=1.0.149"\nrusqlite={version="=0.32.1",features=["bundled"]}\nchrono={version="=0.4.45",default-features=false,features=["std"]}\n');
  const target=path.join(tmpdir(),'alch-semantic-rust-target');
  mkdirSync(target,{recursive:true});
  // Hold a build lock through the binary copy: different source variants share the dependency cache.
  execFileSync('/usr/bin/flock',[path.join(target,'alch-build.lock'),'/bin/sh','-c','cargo build --offline --manifest-path "$1" --target-dir "$2" && cp "$2/debug/alch-event" "$3"','alch-build',path.join(stage,'rust/Cargo.toml'),target,path.join(stage,'alch-event')],{stdio:'pipe',maxBuffer:16*1024*1024});
  let repo=path.dirname(fileURLToPath(import.meta.url));while(!existsSync(path.join(repo,'cyberAlchemy-v2/agent-routing/profile.json'))){const parent=path.dirname(repo);if(parent===repo)fail('provisioner repository');repo=parent;}
  const provisioner=path.join(repo,'cyberAlchemy-v2/work-orchestration-implementation/extensions/alch-host-provisioning-v1');
  const producer=plan.config.executions[0],consumer=plan.config.executions[1],action=plan.config.model.actions[0];
  json('host.json',{profile:'semantic-host-v1',id:plan.config.transport,runtime:'rust',provisioner:'ansible-local-v1',provisioner_root:provisioner,provisioner_host_sha256:hash(readFileSync(path.join(provisioner,'host.py'))),provisioner_manifest_sha256:hash(readFileSync(path.join(provisioner,'source-manifest.json'))),events:'local',isolation:'bubblewrap',consumer:{operation:consumer.operation,actors:action.actor_refs,boundary:action.authority_boundary_ref},transport:plan.config.transport,listen:'127.0.0.1',operation:producer.operation,actors:action.actor_refs,boundary:action.authority_boundary_ref,timeout_ms:5000,max_request_bytes:65536,endpoint:`/functions/${plan.config.transport}/${producer.operation}`,source_sha256:hash(source),authority_effect:'none'});
  cpSync(new URL('./event-templates/semantic-serve.py',import.meta.url),path.join(stage,'serve.py'));cpSync(new URL('./event-templates/local_worker.py',import.meta.url),path.join(stage,'local_worker.py'));
  const walk=(dir:string):string[]=>readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);
  json('manifest.json',{profile:'semantic-host-v1',source_sha256:hash(source),files:Object.fromEntries(walk(stage).sort().map(p=>[path.relative(stage,p),hash(readFileSync(p))])),authority_effect:'none'});
  cpSync(path.join(stage,'manifest.json'),path.join(stage,'host-manifest.json'));
  if(readFileSync(file,'utf8')!==source)fail('source drift');renameSync(stage,output);return {status:'built',profile:'semantic-host-v1',output:path.resolve(output),authority_effect:'none'};
 }finally{rmSync(stage,{recursive:true,force:true});}
}
