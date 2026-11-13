import {readFileSync} from 'node:fs';
import path from 'node:path';
import {isDeepStrictEqual} from 'node:util';
import {Snapshots,bind,sameBinding} from '../../lab-runtime/alchlang/shared-records/snapshots.mjs';
import {digest} from '../../lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {verifyPlanningEvidence} from '../../lab-runtime/alchlang/shared-records/evidence.mjs';
import {nativePort} from '../../lab-runtime/alchlang/shared-records/ports.mjs';
import {verifyLocations} from '../../lab-runtime/alchlang/shared-records/locations.mjs';
import {verifyDirectoryPackages} from './directories.mjs';
import {enforce} from './kernel.mjs';
import {planRecordCustody} from './records.mjs';
import {verifyRecordReviews} from './record-review.mjs';
import {projectRecordCatalog} from './catalog.mjs';
import {reconcileViews} from './views.mjs';
const json=x=>Buffer.from(JSON.stringify(x,null,2)+'\n');
function authorized(binding,root,read){
 const raw=read(binding),auth=JSON.parse(raw);
 if(digest(raw)!==binding.sha256||raw.length!==Number(binding.bytes)||!auth.verbatim||!auth.scope?.includes('directory-view-publication'))throw Error('view-authorization-required');
 return auth;
}
export async function prepareDirectoryView(active,trust,{operation,viewRoot,authorization}){
 const db=new Snapshots(active.database,{trust}),files={};
 const add=(name,raw)=>{files[name]=Buffer.from(raw).toString('base64');return bind(name,Buffer.from(raw));};
 try{
  const previous=db.current(active.workspace),src=db.material(previous.digest,'source.json'),publication=db.inspectPublication(active.workspace,src.manifest.operation);
  if(!publication||!isDeepStrictEqual(publication.selected,{...previous}))throw Error('previous-publication-not-authenticated');
  for(const b of src.manifest.files)add(b.ref,db.material(previous.digest,b.ref).bytes);
  const source=JSON.parse(src.bytes),registry=JSON.parse(db.material(previous.digest,'registry.json').bytes),pointer=JSON.parse(readFileSync(path.join(active.root,'authority/definitions/current.json')));
  const archiveName='evidence/definitions/full-v2-layout/define-packages.tar.gz',archive=add(archiveName,readFileSync(path.join(active.root,archiveName)));
  source.layout_protocol='workspace-definition-layout/v2';source.view_root=viewRoot;source.admission_decision=pointer.decision;source.legacy_registry=pointer.legacy_registry;
  source.view_authorization=add(authorization.path,readFileSync(path.join(active.root,authorization.path)));
  if(!sameBinding(source.view_authorization,authorization))throw Error('view-authorization-binding-mismatch');
  authorized(authorization,active.root,b=>Buffer.from(files[b.ref??b.path],'base64'));
  source.directory_predecessor={...previous};
  const native=nativePort({action:'record-projection',store:active.native_store,require_current:true});source.directory_native_head=native.head;
  const profiles={};for(const [key,name]of Object.entries(JSON.parse(Buffer.from(files[source.layout.catalog.ref??source.layout.catalog.path],'base64')).profiles)){const raw=readFileSync(path.join(active.root,name));add(name,raw);profiles[key]=JSON.parse(raw);}
  source.record_catalog=add('records/catalog.json',json(projectRecordCatalog(native,profiles)));
  for(const entry of registry.entries.filter(e=>registry.current_lookup[e.definition_id]===e.definition_id+'@'+e.version)){
   const key=entry.definition_id+'@'+entry.version,l=source.locations[key],base=path.posix.dirname(l.body.ref??l.body.path),assets={};
   for(const [role,name]of Object.entries({body:'definition.json',projection:'DEFINITION.md',lineage:'field-lineage.json',evidence:'evidence.json'}))assets[role]=add(base+'/'+name,readFileSync(path.join(active.root,base,name)));
   const receipt={protocol:'verified-definition-directory/v1',definition_id:entry.definition_id,version:entry.version,assets,package_archive:archive,package_prefix:entry.definition_id+'/pack',verifier:'define-alch:inspect+materialize',outcome:'PASS'};
   l.directory={protocol:'definition-directory/v1',...assets,verification:add('directory-verifications/'+entry.definition_id+'.json',json(receipt))};
  }
  add('source.json',json(source));
  const read=b=>Buffer.from(files[b.ref??b.path],'base64');
  await verifyLocations(source,registry,read,{requiredProtocol:'workspace-definition-layout/v2'});
  const packageVerification=await verifyDirectoryPackages(source,registry,read);
  const staged=db.stage(active.workspace,operation,native.baseline.snapshot_digest,files);
  const value={workspace:active.workspace,operation_ref:operation,source_cut:native.baseline.snapshot_digest,bundle:staged.binding,expected_selector:bind('selector',Buffer.from(JSON.stringify(previous)))};
  return {operation:'PublishDirectoryView',scope:active.workspace,cut:native.baseline.snapshot_digest,input:{value},files,packageVerification,expected:previous};
 }finally{db.close();}
}
export async function publishDirectoryView(request,trust,active){
 if(request.operation!=='PublishDirectoryView')throw Error('directory-publication-operation-required');
 const checked=verifyPlanningEvidence(request,trust,{historical:true}),value=checked.input.value,db=new Snapshots(active.database,{trust});
 try{
  if(value.workspace!==active.workspace)throw Error('directory-publication-workspace-mismatch');
  const prior=db.inspectPublication(value.workspace,value.operation_ref);
  if(prior){
   if(prior.artifact_digest!==digest(checked.bytes))throw Error('publication-operation-conflict');
   return {...prior,replayed:true,views:await reconcileViews({...active,selector:prior.selected},trust)};
  }
  verifyPlanningEvidence(request,trust);
  const previous=db.current(active.workspace),previousSource=db.material(previous.digest,'source.json'),original=db.inspectPublication(active.workspace,previousSource.manifest.operation);
  const staged=db.stage(value.workspace,value.operation_ref,value.source_cut,request.files);
  if(!sameBinding(staged.binding,value.bundle))throw Error('directory-publication-bundle-mismatch');
  const read=b=>{const m=db.material(staged.binding.sha256,b.ref??b.path);if(!sameBinding(m.binding,b))throw Error('directory-publication-member-mismatch');return m.bytes;};
  const source=JSON.parse(db.material(staged.binding.sha256,'source.json').bytes),registryBytes=db.material(staged.binding.sha256,'registry.json').bytes;
  const previousLayout=JSON.parse(previousSource.bytes);
  for(const [key,location]of Object.entries(source.locations??{})){
   const priorLocation=previousLayout.locations?.[key];
   if(!priorLocation||location.workspace!==priorLocation.workspace||(location.body.ref??location.body.path)!==(priorLocation.body.ref??priorLocation.body.path))throw Error('metadata-publication-custody-change-refused');
   const oldProfile=JSON.parse(db.material(previous.digest,priorLocation.profile.ref??priorLocation.profile.path).bytes),newProfile=JSON.parse(read(location.profile));
   if(oldProfile.home.path!==newProfile.home.path||oldProfile.workspace_ref!==newProfile.workspace_ref)throw Error('metadata-publication-custody-change-refused');
  }

  authorized(source.view_authorization,active.root,read);
  await verifyLocations(source,JSON.parse(registryBytes),read,{requiredProtocol:trust.layout_policy.required_protocol});
  await verifyDirectoryPackages(source,JSON.parse(registryBytes),read);
  const native=nativePort({action:'record-projection',store:active.native_store,require_current:true});
  if(!source.record_catalog)throw Error('record-catalog-required');
  const profiles=Object.fromEntries(Object.entries(JSON.parse(read(source.layout.catalog)).profiles).map(([key,name])=>{
   const profileBinding=staged.manifest.files.find(b=>b.ref===name);if(!profileBinding)throw Error('record-catalog-profile-not-in-snapshot');
   return [key,JSON.parse(read(profileBinding))];
  }));
  let assignments=[];
  if(source.record_construction){
   const constructionRequest=JSON.parse(read(source.record_construction)),checkedConstruction=verifyPlanningEvidence(constructionRequest.construction,trust,{historical:true});
   verifyRecordReviews(constructionRequest,checkedConstruction.input.value,trust,native);
   const bundle=JSON.parse(read(constructionRequest.record_review_bundle));assignments=bundle.reviews;
   for(const [version,l]of Object.entries(source.record_locations??{})){
    const row=native.projection.subjects[version],assignment=assignments.find(a=>a.version_ref===version&&a.workspace===l.workspace);
    if(!row||!assignment||!isDeepStrictEqual(JSON.parse(read(l.body)),row.record))throw Error('record-directory-native-body-mismatch');
    const custody=JSON.parse(read(l.custody));read(l.human);
    if(custody.version_ref!==version||custody.workspace!==l.workspace||custody.body_binding.sha256!==l.body.sha256||custody.human.binding.sha256!==l.human.sha256)throw Error('record-custody-manifest-mismatch');
    if(custody.assignment.owner_decision.sha256!==assignment.decision.sha256||custody.assignment.workspace_scope!==assignment.workspace_scope)throw Error('record-custody-owner-assignment-mismatch');
    const profile=Object.values(profiles).find(p=>p.workspace_ref===l.workspace);
    const expected=await planRecordCustody({root:active.root,profile,native,version_ref:version,assignment:custody.assignment});
    if(!read(l.human).equals(Buffer.from(expected.human.bytes_base64,'base64'))||expected.body_binding.sha256!==l.body.sha256||(l.body.ref??l.body.path)!==expected.body_binding.ref)throw Error('record-registered-projection-mismatch');

   }
  }
  if(!isDeepStrictEqual(JSON.parse(read(source.record_catalog)),projectRecordCatalog(native,profiles,assignments)))throw Error('record-catalog-native-projection-mismatch');
  await enforce('EnforceViewPublication',{previous_authenticated:!!original&&isDeepStrictEqual(original.selected,{...previous}),registry_unchanged:registryBytes.equals(db.material(previous.digest,'registry.json').bytes),selector_current:isDeepStrictEqual(source.directory_predecessor,{...previous})&&sameBinding(bind('selector',Buffer.from(JSON.stringify(previous))),value.expected_selector),native_head_verified:isDeepStrictEqual(source.directory_native_head,native.head)&&value.source_cut===native.baseline.snapshot_digest,directory_verified:true,owner_authorized:true});
  const result=db.publish({workspace:value.workspace,operation:value.operation_ref,expected:previous,snapshot:staged.binding.sha256,artifactDigest:digest(checked.bytes),evidence:{operation:request.operation,scope:request.scope,cut:request.cut,artifact:request.artifact,receipt:request.receipt}});
  return {...result,views:await reconcileViews({...active,selector:result.selected},trust)};
 }finally{db.close();}
}

export function refreshDirectoryView(prepared,active,recordInputs=null){
 const files={...prepared.files},add=(name,raw)=>{files[name]=raw.toString('base64');return bind(name,raw);};
 const source=JSON.parse(Buffer.from(files['source.json'],'base64')),native=nativePort({action:'record-projection',store:active.native_store,require_current:true});
 source.directory_native_head=native.head;
 const catalogName=source.layout.catalog.ref??source.layout.catalog.path,catalogRaw=readFileSync(path.join(active.root,catalogName)),catalog=JSON.parse(catalogRaw),profiles={};
 source.layout.catalog=add(catalogName,catalogRaw);
 for(const [key,name]of Object.entries(catalog.profiles))profiles[key]=JSON.parse(readFileSync(path.join(active.root,name)));
 for(const [key,l]of Object.entries(source.locations)){
  const name=l.profile.ref??l.profile.path,raw=readFileSync(path.join(active.root,name)),profile=JSON.parse(raw),old=JSON.parse(Buffer.from(files[name],'base64'));
  if(profile.workspace_ref!==old.workspace_ref||profile.home.path!==old.home.path)throw Error('directory-refresh-custody-change-requires-owner-review');
  l.profile=add(name,raw);
 }
 for(const name of Object.values(catalog.profiles))add(name,readFileSync(path.join(active.root,name)));
 let assignments=[];
 if(recordInputs){
  const request=JSON.parse(readFileSync(recordInputs.request)),trust=recordInputs.trust,checked=verifyPlanningEvidence(request.construction,trust,{historical:true});
  verifyRecordReviews(request,checked.input.value,trust,native);
  const bundle=JSON.parse(readFileSync(path.join(active.root,request.record_review_bundle.ref??request.record_review_bundle.path)));
  assignments=bundle.reviews;
  source.record_construction=add(path.relative(active.root,recordInputs.request),readFileSync(recordInputs.request));
  const wanted=[request.record_review_bundle,...bundle.reviews.flatMap(r=>[r.body,r.decision])];
  for(const review of bundle.reviews){const decision=JSON.parse(readFileSync(path.join(active.root,review.decision.ref??review.decision.path)));wanted.push(decision.authorization,decision.role_assignment);}
  for(const b of wanted){const name=b.ref??b.path,raw=readFileSync(path.join(active.root,name));if(digest(raw)!==b.sha256)throw Error('record-input-original-drift');add(name,raw);}
  source.record_locations={};
  for(const location of recordInputs.locations){
   const entry={workspace:location.workspace};
   for(const key of ['body','human','custody'])entry[key]=add(location[key],readFileSync(path.join(active.root,location[key])));
   source.record_locations[location.version_ref]=entry;
  }
 }
 source.record_catalog=add('records/catalog.json',json(projectRecordCatalog(native,profiles,assignments)));
 add('source.json',json(source));
 const db=new Snapshots(active.database);
 try{
  const staged=db.stage(active.workspace,prepared.input.value.operation_ref,native.baseline.snapshot_digest,files);
  return {...prepared,files,cut:native.baseline.snapshot_digest,input:{value:{...prepared.input.value,source_cut:native.baseline.snapshot_digest,bundle:staged.binding}}};
 }finally{db.close();}
}
