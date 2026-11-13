#!/usr/bin/env node
import {spawnSync} from 'node:child_process';
import {node as pinnedNode} from '../../lab-runtime/alchlang/shared-records/build.mjs';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,readdirSync,renameSync,rmSync} from 'node:fs';
import path from 'node:path';import {tmpdir} from 'node:os';import {createHash} from 'node:crypto';
import {Snapshots} from '../../lab-runtime/alchlang/shared-records/snapshots.mjs';
import {activation} from '../../lab-runtime/alchlang/shared-records/activation.mjs';
import {loadTrust} from '../../lab-runtime/alchlang/shared-records/implementation.mjs';
import {materializeCli} from '../../../workspaces/products/define/implementation/cli/alchlang/runtime/package.mjs';
import {reviewEvolution} from '../records-workflow/evolution.mjs';
import {place,destination,source,semanticDigest,folderName} from './kernel.mjs';
const root=path.resolve(import.meta.dirname,'../../..'),sha=b=>createHash('sha256').update(b).digest('hex'),load=f=>JSON.parse(readFileSync(f));
export async function placePackage(request,{dryRun=false}={}){
 const catalog=load(path.join(root,'implementation/lab-workspaces/v2/catalog.json')),profile=catalog.profiles[request.workspace];
 if(!profile)throw Error('workspace-not-selected');
 const workspace=load(path.join(root,profile)),homes=load(path.join(root,'authority/definitions/maintenance-homes.json')).homes;
 const temporary=mkdtempSync(path.join(tmpdir(),'lab-definition-placement-')),out=path.join(temporary,'materialized');
 try{
  await materializeCli(path.resolve(request.package),out);
  const definitions=path.join(out,'definitions'),plans=[];
  for(const name of readdirSync(definitions)){
   const dir=path.join(definitions,name),raw=readFileSync(path.join(dir,'definition.json')),definition=JSON.parse(raw);
   let expectedHome=homes[definition.definition_id]??workspace.home.path;
   const selected=load(path.join(root,'authority/definitions/current.json')),registryRaw=readFileSync(path.join(root,selected.registry.path));assert.equal(sha(registryRaw),selected.registry.sha256,'registry-binding-mismatch');const registry=JSON.parse(registryRaw),current=registry.entries.find(e=>registry.current_lookup[e.definition_id]===e.definition_id+'@'+e.version&&e.definition_id===definition.definition_id);const originalFile=current?path.join(root,current.body.path):request.original?path.resolve(request.original):null;let original=originalFile?load(originalFile):definition;if(current)assert.equal(sha(readFileSync(originalFile)),current.body.sha256,'original-body-drift');if(current&&request.original)assert.equal(sha(readFileSync(path.resolve(request.original))),current.body.sha256,'substituted-original-body');
   assert.equal(original.definition_id,definition.definition_id,'original-identity-mismatch');
   if(request.evolution){
    if(!current)throw Error('reviewed-evolution-requires-current-predecessor');
    const active=activation({required:true}),trust=loadTrust(active.trust),db=new Snapshots(active.database,{readOnly:true,trust});
    try{
     const selected=db.current(active.workspace);
     const evolution=await reviewEvolution(request.evolution,trust,b=>{
      const q=trust.materials?.[b.ref??b.path];
      return q?.sha256===b.sha256?readFileSync(q.path):db.material(selected.digest,b.ref??b.path).bytes;
     });
     assert.deepEqual(evolution.previous,original,'evolution-foreign-predecessor');assert.deepEqual(evolution.target,definition,'evolution-foreign-target');
     assert.equal(evolution.previous_home,expectedHome,'evolution-foreign-previous-home');assert.equal(evolution.home,workspace.home.path,'evolution-foreign-target-home');
     expectedHome=evolution.home;original=definition;
    }finally{db.close();}
   }

   const norm=semanticDigest(original),body=sha(raw);
   const plan=await place({workspace:workspace.workspace_ref,workspace_selected:true,expected_home:expectedHome,actual_home:workspace.home.path,name:original.term,observed_name:definition.term,folder:folderName(definition.term),expected_folder:folderName(original.term),definition_id:definition.definition_id,observed_id:definition.definition_id,version:definition.version,observed_version:definition.version,owner:original.semantic_owner_ref,observed_owner:definition.semantic_owner_ref,expected_body:body,observed_body:body,expected_normative:norm,observed_normative:semanticDigest(definition),full_v2:definition.schema_version==='cyberalchemy-lab-definition/v2'});
   plans.push({plan,target:destination(root,plan),directory:dir});
  }
  if(!dryRun)for(const item of plans){
   const records=['definition.json','DEFINITION.md','field-lineage.json'];
   if(existsSync(item.target)){
    for(const name of records)assert.deepEqual(readFileSync(path.join(item.target,name)),readFileSync(path.join(item.directory,name)),'existing-version-conflict');
    const evidenceRaw=readFileSync(path.join(item.target,'evidence.json')),evidence=JSON.parse(evidenceRaw),manifestSha=sha(readFileSync(path.join(request.package,'manifest.json')));
    if(evidence.package_manifest_sha256){assert.equal(evidence.package_manifest_sha256,manifestSha,'existing-evidence-package-conflict');assert.deepEqual(evidence.plan,item.plan,'existing-evidence-plan-conflict');}
    else{
     const active=activation({required:true}),db=new Snapshots(active.database,{readOnly:true,trust:loadTrust(active.trust)});
     try{
      const selected=db.current(active.workspace),sourceMaterial=db.material(selected.digest,'source.json');
      db.inspectPublication(active.workspace,sourceMaterial.manifest.operation);
      const source=JSON.parse(sourceMaterial.bytes),key=item.plan.definition_id+'@'+item.plan.version,d=source.locations?.[key]?.directory;
      if(!d)throw Error('existing-evidence-not-published');
      const binding=d.evidence,original=db.material(selected.digest,binding.ref??binding.path);
      assert.equal(sha(evidenceRaw),binding.sha256,'existing-evidence-conflict');assert.equal(evidenceRaw.length,Number(binding.bytes),'existing-evidence-conflict');assert.deepEqual(evidenceRaw,original.bytes,'existing-evidence-conflict');
      const receipt=JSON.parse(db.material(selected.digest,d.verification.ref??d.verification.path).bytes);
      // The authenticated verifier receipt binds the original portable package manifest.
      if(receipt.package_manifest_sha256)assert.equal(receipt.package_manifest_sha256,manifestSha,'existing-evidence-package-conflict');
     }finally{db.close();}
    }
    continue;
   }
   mkdirSync(path.dirname(item.target),{recursive:true});
   const staging=mkdtempSync(path.join(path.dirname(item.target),'.placement-'));
   try{for(const name of records)writeFileSync(path.join(staging,name),readFileSync(path.join(item.directory,name)),{flag:'wx'});writeFileSync(path.join(staging,'evidence.json'),JSON.stringify({authority_effect:'none',placement_source:source,plan:item.plan,package_manifest_sha256:sha(readFileSync(path.join(request.package,'manifest.json'))),owner_review:'separate; generation is not admission'},null,2)+'\n',{flag:'wx'});renameSync(staging,item.target);}catch(e){rmSync(staging,{recursive:true,force:true});throw e;}
  }
  return {status:'PASS',mode:dryRun?'plan':'candidate-placement',authority_effect:'none',source,plans:plans.map(x=>({placement:x.plan,destination:path.relative(root,x.target)}))};
 }finally{rmSync(temporary,{recursive:true,force:true});}
}
if(process.argv[1]===import.meta.filename){
 if(path.resolve(process.execPath)!==path.resolve(pinnedNode)){const child=spawnSync(pinnedNode,[import.meta.filename,...process.argv.slice(2)],{stdio:'inherit'});process.exit(child.status??2);}
 const args=process.argv.slice(2),at=args.indexOf('--file');
 if(at<0)throw Error('request-file-required: --file {package,workspace,original?} [--dry-run]');
 console.log(JSON.stringify(await placePackage(load(path.resolve(args[at+1])),{dryRun:args.includes('--dry-run')})));
}
