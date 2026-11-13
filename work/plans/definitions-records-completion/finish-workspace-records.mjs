import assert from 'node:assert/strict';import {readFileSync,writeFileSync} from 'node:fs';import path from 'node:path';
import {activation} from '../../../implementation/lab-runtime/alchlang/shared-records/activation.mjs';
import {loadTrust} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {nativePort} from '../../../implementation/lab-runtime/alchlang/shared-records/ports.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {planRecordCustody,placeAdmittedRecord} from '../../../implementation/lab-workflows/records-workflow/records.mjs';
import {refreshDirectoryView} from '../../../implementation/lab-workflows/records-workflow/publication.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),Q=path.join(here,'workspace-records'),load=f=>JSON.parse(readFileSync(f)),put=(f,v)=>writeFileSync(f,JSON.stringify(v,null,2)+'\n'),active=activation({required:true}),trust=loadTrust(active.trust);
const applied=load(path.join(Q,'NATIVE-APPLICATION.json')),request=load(path.join(Q,'native-apply.json')),native=nativePort({action:'record-projection',store:active.native_store,require_current:true});
const committed=nativePort({action:'committed',store:active.native_store,operation:request.proposal.proposal_id});assert.deepEqual(committed.proposal,request.proposal);
const targets=load(path.join(Q,'TARGETS.json')).records,bundle=load(path.join(Q,'artifact-bundle.json')),locations=[];
for(const key of [...new Set(targets.map(t=>t.workspace_key))]){
 const file=path.join(root,'workspaces/products',key,'WORKSPACE.json'),profile=load(file),wanted='product:'+key;
 if(profile.primary_subject.ref!==null&&profile.primary_subject.ref!==wanted)throw Error('workspace-already-bound-to-another-product');
 if(profile.primary_subject.ref===null){profile.primary_subject.ref=wanted;profile.revision='2.0.1';put(file,profile);}
 const bindingFile=path.join(root,profile.model_binding_ref),binding=load(bindingFile);binding.profile_sha256=digest(readFileSync(file));binding.profile_revision=profile.revision;binding.primary_subject=profile.primary_subject;put(bindingFile,binding);
}
for(const row of targets){
 const profile=load(path.join(root,'workspaces/products',row.workspace_key,'WORKSPACE.json')),review=bundle.reviews.find(r=>r.version_ref===row.version),body=native.projection.subjects[row.version].record;
 const assignment={version_ref:row.version,workspace:row.workspace,workspace_scope:row.workspace_scope,owner:row.owner,owner_decision:review.decision,native_authority_scope:row.scope,semantic_project:null,body_sha256:digest(Buffer.from(JSON.stringify(body)))};
 const plan=await planRecordCustody({root,profile,native,version_ref:row.version,assignment});placeAdmittedRecord(root,plan);
 locations.push({version_ref:row.version,workspace:row.workspace,body:plan.folder+'/'+plan.filename,human:plan.folder+'/'+plan.human.filename,custody:plan.folder+'/custody.json'});
 if(row.workspace_key==='define'&&row.carrier.includes('product-identity')){
  put(path.join(root,'workspaces/products/define/product/product-source.ref.json'),{format:'native-record-reference/v1',authority_effect:'none',subject_ref:'product:define',version_ref:row.version,workspace:row.workspace,source:plan.folder+'/'+plan.filename,standing:native.projection.subjects[row.version].effective_state,native_operation:request.proposal.proposal_id});
 }
}
put(path.join(Q,'CUSTODY.json'),{status:'PASS',native_head:native.head,locations});
const prepared=load(path.join(here,'.local/DIRECTORY-VIEW-PREPARED.json')),enriched=refreshDirectoryView(prepared,active,{request:path.join(Q,'native-apply.json'),locations,trust});put(path.join(here,'.local/DIRECTORY-VIEW-READY.json'),enriched);
console.log(JSON.stringify({status:'PASS',records:targets.length,locations:locations.length,native_head:native.head,bundle:enriched.input.value.bundle}));
