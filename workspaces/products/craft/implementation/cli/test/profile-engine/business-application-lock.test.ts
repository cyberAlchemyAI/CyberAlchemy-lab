import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdtempSync,writeFileSync,readFileSync,rmSync,symlinkSync,truncateSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {loadProfileProjectV2,assertProfileSnapshotCurrent,profileSnapshotFiles} from '../../src/profile-engine/loader.js';
import {prepareBusinessInputV2,assertBusinessInputV2Current} from '../../src/profile-engine/business-input-v2.js';
import {evaluateProfile} from '../../src/profile-engine/evaluate.js';
// Open questions: actual graph/normalization and complete tool closure qualify at BA04/BA15.
function fixture(t:any){const root=mkdtempSync(path.join(os.tmpdir(),'business-input-'));t.after(()=>rmSync(root,{recursive:true,force:true}));cpSync(path.join(import.meta.dirname,'fixtures/business-notice'),root,{recursive:true});cpSync(path.resolve(import.meta.dirname,'../../profiles/node-http-entry-local-v2'),path.join(root,'profile'),{recursive:true});const file=path.join(root,'project.json'),project=JSON.parse(readFileSync(file,'utf8'));project.profiles[0].path='profile';writeFileSync(file,JSON.stringify(project,null,2)+'\n');writeFileSync(path.join(root,'core'),'test-core');writeFileSync(path.join(root,'tool'),'test-tool');return {root,file,project,identity:{engine:[{key:'core',path:path.join(root,'core')}],tools:[{key:'tool',path:path.join(root,'tool')}]}};}

test('v2 captures exact original business/semantic/formal/native closure without executing package code',t=>{
 const f=fixture(t),s=loadProfileProjectV2(f.file,f.identity),input=prepareBusinessInputV2(s);assert.equal(input.applications.length,1);assert.equal(input.applications[0]!.model.id,'commerce');assert.ok(input.applications[0]!.selectors.some(r=>r.selector==='operation:ReceiveNotice'));assert.equal(input.applications[0]!.semantics.claim_meanings.IdentityClaim!.owner_acceptance.outcome,'accepted');assert.ok(profileSnapshotFiles(s).some(file=>file.relative==='runtime/empty-settlement.ts'));assert.equal(input.snapshot.project.integration_configuration,undefined);
 assert.deepEqual(JSON.parse(JSON.stringify(input.metadata_tables.applications.rows)),[{id:'receiveNotice',source:'domain.alch',selector:'ReceiveNotice',application_id:'commerce',mapping_ref:'MessageToOrder'}]);assert.ok(Object.isFrozen(input.metadata_tables.applications.rows));const evaluated=evaluateProfile(input.runtime.data,input.metadata_tables);assert.equal(evaluated.emissions.find(e=>e.role==='application-operation')!.fields.project_ref,'domain.alch');
 assert.throws(()=>assertBusinessInputV2Current(JSON.parse(JSON.stringify(input))),/UNREGISTERED/);assert.throws(()=>assertProfileSnapshotCurrent(JSON.parse(JSON.stringify(s))),/UNREGISTERED/);
 const again=loadProfileProjectV2(f.file,f.identity,s.lock);assert.deepEqual(again.lock,s.lock);
});
for(const target of ['domain.alch','business-semantics.json','profile/formal/profile.json','profile/formal/identity.json','profile/runtime/empty-settlement.ts','profile/runtime/application-http.mts','core','tool'])test('currentness rejects '+target+' drift',t=>{
 const f=fixture(t),s=loadProfileProjectV2(f.file,f.identity),input=prepareBusinessInputV2(s);const p=path.join(f.root,target);writeFileSync(p,readFileSync(p,'utf8')+'\n');assert.throws(()=>assertBusinessInputV2Current(input),/STALE/);assert.throws(()=>loadProfileProjectV2(f.file,f.identity,s.lock));
});
test('source semantics stay explicit and technical clauses/symlinks reject',t=>{
 for(const mutation of ['runtime','owner','mapping','symlink']){const f=fixture(t),p=path.join(f.root,'domain.alch');let source=readFileSync(p,'utf8');if(mutation==='runtime')source+='runtime-profile Hidden:\n  target typescript\n';if(mutation==='owner')source=source.replace('owner business-author','owner other-owner');if(mutation==='mapping')source=source.replace('mapping MessageToOrder:','mapping DifferentMapping:');if(mutation==='symlink'){const moved=path.join(f.root,'real.alch');writeFileSync(moved,source);rmSync(p);symlinkSync(moved,p);}else writeFileSync(p,source);assert.throws(()=>prepareBusinessInputV2(loadProfileProjectV2(f.file,f.identity)));}
});
test('multiple model inputs retain distinct model identity and conflicts never resolve by profile order',t=>{
 const f=fixture(t);cpSync(path.join(f.root,'domain.alch'),path.join(f.root,'other.alch'));cpSync(path.join(f.root,'business-semantics.json'),path.join(f.root,'other.json'));f.project.application_models.push({id:'other',source:'other.alch',semantics:'other.json'});f.project.application_intents.push({...f.project.application_intents[0],id:'otherNotice',application_id:'other'});writeFileSync(f.file,JSON.stringify(f.project));const input=prepareBusinessInputV2(loadProfileProjectV2(f.file,f.identity));assert.deepEqual(input.applications.map(a=>a.model.id),['commerce','other']);assert.equal(new Set(input.applications.flatMap(a=>a.selectors.map(s=>s.application_id))).size,2);
 cpSync(path.resolve(import.meta.dirname,'../../profiles/node-http-shared-ports-v2'),path.join(f.root,'shared'),{recursive:true});f.project.profiles.push({id:'node-http-shared-ports-v2',version:'1.0.0',path:'shared'});writeFileSync(f.file,JSON.stringify(f.project));assert.throws(()=>prepareBusinessInputV2(loadProfileProjectV2(f.file,f.identity)),/RUNTIME_AMBIGUOUS/);
});
test('v2 source/asset lock and application tables retain identity after relocation',t=>{
 const f=fixture(t),initial=loadProfileProjectV2(f.file,f.identity),moved=mkdtempSync(path.join(os.tmpdir(),'business-relocated-'));t.after(()=>rmSync(moved,{recursive:true,force:true}));cpSync(f.root,moved,{recursive:true});
 const identity={engine:[{key:'core',path:path.join(moved,'core')}],tools:[{key:'tool',path:path.join(moved,'tool')}]},relocated=loadProfileProjectV2(path.join(moved,'project.json'),identity,initial.lock);assert.deepEqual(relocated.lock,initial.lock);assert.deepEqual(prepareBusinessInputV2(relocated).metadata_tables,prepareBusinessInputV2(initial).metadata_tables);
});
test('v2 source closure refuses file and selected asset budgets before parsing or execution',t=>{
 const f=fixture(t);truncateSync(path.join(f.root,'business-semantics.json'),16777217);assert.throws(()=>loadProfileProjectV2(f.file,f.identity),/FILE_BUDGET/);
 const small=fixture(t),profileFile=path.join(small.root,'profile/profile.json'),pkg=JSON.parse(readFileSync(profileFile,'utf8'));pkg.budgets.bytes=1;writeFileSync(profileFile,JSON.stringify(pkg));assert.throws(()=>loadProfileProjectV2(small.file,small.identity),/CLOSURE_BUDGET/);
});
