import {readFileSync} from 'node:fs';
import path from 'node:path';
import {bind} from '../../lab-runtime/alchlang/shared-records/snapshots.mjs';
export function projectionMaterials(native){
 const all=Object.entries(native.projection.subjects),encode=entries=>Buffer.from(JSON.stringify({subjects:Object.fromEntries(entries)}));
 return new Map([['inventory/native-schemas.json',Buffer.from(JSON.stringify({documents:native.schema_documents??{}}))],['inventory/native-records.json',encode(all.filter(([,r])=>r.category==='artifact-instance'))],['inventory/native-governance.json',encode(all.filter(([,r])=>r.category!=='artifact-instance'))]]);
}
export function projectConsumers({registry,source,selected,native,root,workspace,material}){
 const subjects=new Map(),edges=[],unresolved=[],provenance=[],external=[];
 const add=(ref,binding,kind)=>{if(!subjects.has(ref))subjects.set(ref,{ref,binding,kind,dependencies:[]});};
 const file=name=>bind(name,readFileSync(path.join(root,name)));
 const version=e=>e.definition_id+'@'+e.version;
 const identities=new Map(Object.entries(registry.current_lookup)),definitionRef=v=>'definition:'+v;
 for(const e of registry.entries)add(definitionRef(version(e)),bind(e.body.path,material(e.body)), 'definition');
 const nativeSubjects=native.projection.subjects,partitions=projectionMaterials(native);
 for(const [key,row]of Object.entries(nativeSubjects)){
  const name=row.category==='artifact-instance'?'inventory/native-records.json':'inventory/native-governance.json';
  add('record:'+key,bind(name,partitions.get(name)),row.category);
  subjects.get('record:'+key).selector='/subjects/'+key.replaceAll('~','~0').replaceAll('/','~1');
 }
 for(const [ref,contract]of Object.entries(native.projection.contracts)){
  const carrier='carrier:'+ref,name='inventory/native-governance.json';
  add(carrier,bind(name,partitions.get(name)),'carrier');
  subjects.get(carrier).selector='/subjects/'+ref.replaceAll('~','~0').replaceAll('/','~1');
  const schema='schema:'+contract.schema_path,schemaName='inventory/native-schemas.json';
  if(native.schema_documents?.[contract.schema_path]){
   add(schema,bind(schemaName,partitions.get(schemaName)),'schema');
   subjects.get(schema).selector='/documents/'+contract.schema_path.replaceAll('~','~0').replaceAll('/','~1');
   subjects.get(carrier).dependencies.push(schema);
  }else unresolved.push({from:carrier,to:schema,kind:'schema',reason:'Exact native schema document unavailable'});
 }
 const known=new Map([...identities].map(([id,v])=>[id,definitionRef(v)]));
 for(const e of registry.entries)known.set(version(e),definitionRef(version(e)));
 for(const [key,row]of Object.entries(nativeSubjects)){if(row.category==='definition')continue;known.set(key,'record:'+key);if(!known.has(row.identity)||['admitted-current','local-admitted-current'].includes(row.effective_state))known.set(row.identity,'record:'+key);}
 function edge(from,target,kind,location){
  const to=known.get(target)??(subjects.has(target)?target:null);
  const item={from,to:to??target,kind,location};
  if(to){edges.push(item);if(['normative','carrier','schema','generation','selection','reader','declared-consumer'].includes(kind))subjects.get(from).dependencies.push(to);}
  else unresolved.push(item);
 }
 function refs(value,from,location='',kind='provenance'){
  if(Array.isArray(value)){value.forEach((x,i)=>refs(x,from,location+'/'+i,kind));return;}
  if(!value||typeof value!=='object')return;
  for(const [key,child]of Object.entries(value)){
   const field=location+'/'+key;
   if(key==='primary_consumer_refs'&&Array.isArray(child)){
    for(const target of child){
     const consumer=known.get(target);
     if(consumer)edge(consumer,from,'declared-consumer',field);
     else external.push({ref:target,declared_by:from,location:field,standing:'declared consumer outside enumerated native/source inventory; not proven covered'});
    }
    continue;
   }
   const next=['semantic_definition_refs','definition_refs','depends_on'].includes(key)?'normative':kind;
   if(typeof child==='string'&&(key.endsWith('_ref')||key==='ref'||key==='target')){
    if(next==='normative'||known.has(child))edge(from,child,next,field);
    else provenance.push({from,target:child,kind:next,location:field});
   }else if(Array.isArray(child)&&next==='normative'){child.forEach((item,i)=>{if(typeof item==='string')edge(from,item,next,field+'/'+i);else refs(item,from,field+'/'+i,next);});}
   else refs(child,from,field,next);
  }
 }
 for(const e of registry.entries){
  const ref=definitionRef(version(e)),body=JSON.parse(material(e.body));refs(body,ref);
  for(const role of ['schema','generator']){
   const b=e[role],id=role+':'+b.path;add(id,bind(b.path,material(b)),role);edge(ref,id,role,'/'+role);
  }
  const carrier=e.carrier.ref,id='carrier:'+carrier;
  add(id,bind(e.carrier.descriptor.path,material(e.carrier.descriptor)),'carrier');edge(ref,id,'carrier','/carrier');
  refs(JSON.parse(material(e.carrier.descriptor)),id);
 }
 for(const [carrier,contract]of Object.entries(native.projection.contracts)){const row=nativeSubjects[carrier];if(row)refs(row.record,'carrier:'+carrier);}
 for(const [key,row]of Object.entries(nativeSubjects)){const ref='record:'+key;refs(row.record,ref);const carrier='carrier:'+row.carrier_ref;if(subjects.has(carrier))edge(ref,carrier,'carrier','/carrier_ref');}
 for(const entry of registry.entries){
  const key=version(entry),directory=source.locations?.[key]?.directory;if(!directory)continue;
  const definition=definitionRef(key);
  for(const role of ['projection','lineage','evidence']){
   const b=directory[role],ref=role+':'+key;add(ref,bind(b.ref??b.path,material(b)),role);
   edge(ref,definition,'generation','/directory/'+role);
   if(role==='evidence'){edge(ref,'projection:'+key,'generation','/projection');edge(ref,'lineage:'+key,'generation','/lineage');}
  }
 }
 const registryRef='registry:shared-definitions';add(registryRef,bind('registry.json',material({ref:'registry.json'})),'registry');
 for(const [id,v]of identities)edge(registryRef,definitionRef(v),'selection','/current_lookup/'+id);
 for(const [ref,name]of [['reader:lab.catalog-reader','implementation/lab-runtime/alchlang/shared-records/catalog.mjs'],['reader:define.catalog-reader','workspaces/products/define/implementation/cli/alchlang/preparation/cli.mjs']]){
  add(ref,file(name),'reader');edge(ref,registryRef,'reader','/catalog');
 }
 const execution=JSON.parse(readFileSync(path.join(root,'authority/profiles/shared-records/current.json')));
 add('runtime:shared-definitions',file(execution.execution_manifest.path),'runtime');edge('runtime:shared-definitions',registryRef,'reader','/registry');
 const catalog=JSON.parse(readFileSync(path.join(root,'implementation/lab-workspaces/v2/catalog.json')));
 for(const name of Object.values(catalog.profiles)){const profile=JSON.parse(readFileSync(path.join(root,name)));add(profile.workspace_ref,file(name),'workspace');edge(profile.workspace_ref,'reader:lab.catalog-reader','reader','/catalog');refs(profile,profile.workspace_ref);}
 for(const subject of subjects.values())subject.dependencies=[...new Set(subject.dependencies)].sort();
 return {version:1,scope:workspace,source_cut:native.baseline.snapshot_digest,cursor:'snapshot:'+selected.revision+':'+selected.digest,subjects:[...subjects.values()].sort((a,b)=>a.ref.localeCompare(b.ref)),edges,provenance,unresolved:unresolved.length,unresolved_references:unresolved,external_subjects:external,coverage:{registry_versions:registry.entries.length,current_definitions:identities.size,native_subjects:Object.keys(nativeSubjects).length,workspace_profiles:Object.keys(catalog.profiles).length,source_snapshot_bound:true,claim:'Enumerated registry, native subjects, selected carrier/schema/generator and maintained readers/profiles. Undeclared repository consumers are outside this inventory; unresolved references are explicit.'}};
}
