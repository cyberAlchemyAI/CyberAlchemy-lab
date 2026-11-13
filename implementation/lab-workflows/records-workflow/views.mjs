import {readFileSync,writeFileSync,mkdirSync,renameSync,existsSync,lstatSync} from 'node:fs';
import path from 'node:path';
import {isDeepStrictEqual} from 'node:util';
import {Snapshots,bind} from '../../lab-runtime/alchlang/shared-records/snapshots.mjs';
import {verifyLocations,currentLocation} from '../../lab-runtime/alchlang/shared-records/locations.mjs';
import {enforce} from './kernel.mjs';
function target(root,name){
 if(!name||path.isAbsolute(name)||name.split('/').some(p=>!p||p==='..')||name.includes('\\'))throw Error('view-path-invalid');
 const file=path.resolve(root,name);if(!file.startsWith(root+path.sep))throw Error('view-path-outside-repository');
 let cursor=path.dirname(file);while(cursor.startsWith(root+path.sep)){if(existsSync(cursor)&&lstatSync(cursor).isSymbolicLink())throw Error('view-symlink-parent');cursor=path.dirname(cursor);}
 if(existsSync(file)&&lstatSync(file).isSymbolicLink())throw Error('view-symlink-target');
 return file;
}
const json=x=>Buffer.from(JSON.stringify(x,null,2)+'\n');
export async function expectedViews(active,trust){
 const root=active.root,db=new Snapshots(active.database,{readOnly:true,trust});
 try{
  const selected=db.current(active.workspace);if(!selected)throw Error('view-publication-required');
  const sourceMaterial=db.material(selected.digest,'source.json'),publication=db.inspectPublication(active.workspace,sourceMaterial.manifest.operation);
  if(!publication||!isDeepStrictEqual(publication.selected,{...selected}))throw Error('view-publication-unverified');
  const source=JSON.parse(sourceMaterial.bytes),registryRaw=db.material(selected.digest,'registry.json').bytes,registry=JSON.parse(registryRaw),read=b=>db.material(selected.digest,b.ref??b.path).bytes;
  await verifyLocations(source,registry,read,{requiredProtocol:trust.layout_policy?.required_protocol});
  if(source.layout_protocol!=='workspace-definition-layout/v2')throw Error('canonical-views-not-bound');
  if(!/^authority\/admissions\/directory-views\/[A-Za-z0-9._-]+$/.test(source.view_root??''))throw Error('canonical-view-root-required');
  const views=new Map(),rows=[],registryPath=source.view_root+'/registry.json',sourcePath=source.view_root+'/source.json';
  views.set(registryPath,registryRaw);views.set(sourcePath,sourceMaterial.bytes);
  for(const e of registry.entries.filter(e=>registry.current_lookup[e.definition_id]===e.definition_id+'@'+e.version)){
   const x=currentLocation(e,source,read),d=x.location.directory;
   for(const key of ['body','projection','lineage','evidence'])views.set(d[key].ref??d[key].path,read(d[key]));
   rows.push({definition_id:e.definition_id,version:e.version,term:x.body.term,path:x.expected,sha256:e.body.sha256,workspace:x.profile.workspace_ref,home:x.profile.home.path,standing:e.standing,owner_disposition:e.owner_disposition,original_binding:e.body,predecessor:e.predecessor});
  }
  const binding=(name,raw)=>({path:name,sha256:bind(name,raw).sha256,bytes:raw.length});
  const pointer={schema_version:'lab-definition-registry-selection/v1',status:'owner-admitted-current',decision:source.admission_decision,registry:binding(registryPath,registryRaw),source:binding(sourcePath,sourceMaterial.bytes),selector:{...selected},reader_protocol:'snapshot-selector/v1',legacy_registry:source.legacy_registry,index:'authority/definitions/DEFINITIONS-INDEX.md',compatibility:'Current v2 directory views derive from the authenticated publication; retained bodies and owner decisions are unchanged.'};
  views.set('authority/definitions/current.json',json(pointer));
  if(source.record_catalog)views.set('authority/records/catalog.json',read(source.record_catalog));
  for(const location of Object.values(source.record_locations??{}))for(const key of ['body','human','custody']){
   const b=location[key];views.set(b.ref??b.path,read(b));
  }

  const provenance={schema_version:'lab-canonical-definition-layout/v1',status:'canonical-current',authority_effect:'Projection of the verified shared Lab publication; acceptance remains in bound owner dispositions.',source_registry:pointer.registry,source:pointer.source,source_cut:sourceMaterial.manifest.cut,selector:{...selected}};
  function markdown(local,home){return ['# Definitions','','Canonical current Definition/v2 records. Names identify folders; stable IDs remain in records and references.','','The shared Lab registry selects these admitted versions. Prior admitted versions remain immutable historical dependencies.','','| Definition | Workspace | Version |','| --- | --- | --- |',...local.toSorted((a,b)=>a.term.localeCompare(b.term)).map(e=>'| ['+e.term+']('+path.posix.relative(path.posix.join(home,'authority/definitions'),path.posix.join(path.posix.dirname(e.path),'DEFINITION.md'))+') | '+e.workspace+' | '+e.version+' |'),''].join('\n');}
  for(const home of new Set(['.',...rows.map(e=>e.home)])){
   const local=home==='.'?rows:rows.filter(e=>e.home===home),base=path.posix.join(home,'authority/definitions');
   views.set(base+'/V2-CATALOG.json',json({...provenance,entries:local}));
   for(const name of ['DEFINITIONS-INDEX.md','V2-DEFINITIONS-INDEX.md'])views.set(base+'/'+name,Buffer.from(markdown(local,home)));
  }
  return {selected:{...selected},views,root,publication};
 }finally{db.close();}
}
export async function inspectViews(active,trust){
 const expected=await expectedViews(active,trust),mismatches=[];
 for(const [name,raw]of expected.views){try{if(!readFileSync(target(expected.root,name)).equals(raw))mismatches.push(name);}catch{mismatches.push(name);}}
 await enforce('EnforceViews',{selector_bound:isDeepStrictEqual(expected.selected,active.selector),registry_pointer_current:!mismatches.includes('authority/definitions/current.json'),directory_assets_current:!mismatches.some(n=>/\/(definition.json|DEFINITION.md|field-lineage.json|evidence.json)$/.test(n)),indexes_current:!mismatches.some(n=>!/\/(definition.json|DEFINITION.md|field-lineage.json|evidence.json)$/.test(n))});
 return {status:'ready',selector:expected.selected,files:expected.views.size,mismatches};
}
export async function reconcileViews(active,trust,{interruptAfter=Infinity}={}){
 const expected=await expectedViews(active,trust),journal=target(expected.root,'.local/lab-runtime/shared/view-reconciliation.json');
 mkdirSync(path.dirname(journal),{recursive:true});
 const record={schema_version:'lab-view-reconciliation/v1',selector:expected.selected,publication:expected.publication.operation,status:'in-progress',files:[...expected.views].map(([name,raw])=>bind(name,raw))};
 writeFileSync(journal,json(record));
 let count=0;
 // Publish the pointer last. Repeating after interruption compares exact bytes.
 const members=[...expected.views].sort(([a],[b])=>(a==='authority/definitions/current.json')-(b==='authority/definitions/current.json'));
 for(const [name,raw]of members){
  const file=target(expected.root,name);mkdirSync(path.dirname(file),{recursive:true});
  if(!existsSync(file)||!readFileSync(file).equals(raw)){const staging=file+'.reconcile-'+process.pid;writeFileSync(staging,raw,{flag:'wx'});renameSync(staging,file);}
  if(++count===interruptAfter)throw Error('injected-view-interruption');
 }
 writeFileSync(journal,json({...record,status:'completed'}));
 return inspectViews({...active,selector:expected.selected},trust);
}
