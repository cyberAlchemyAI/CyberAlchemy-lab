import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {validateProfilePackageV2} from '../../src/profile-engine/contracts-v2.js';
import {dataDigest} from '../../src/profile-engine/contracts.js';
// Open questions: final application transport/assembly/native qualification BA07–BA18.
const base=path.resolve(import.meta.dirname,'../../profiles');
test('early locked formal and no-effects runtime assets exist for both architecture packages',()=>{
 for(const id of ['node-http-entry-local-v2','node-http-shared-ports-v2']){
  const folder=path.join(base,id),p=validateProfilePackageV2(JSON.parse(readFileSync(path.join(folder,'profile.json'),'utf8')));
  for(const asset of p.assets)assert.equal(createHash('sha256').update(readFileSync(path.join(folder,asset.path))).digest('hex'),asset.sha256);
  const profile=JSON.parse(readFileSync(path.join(folder,'formal/profile.json'),'utf8'));assert.equal(dataDigest(profile),'bc6b15bbe27641b6e5dd7a88774f8c587a52d64359e24a9d2a1bf198c706f856');
  assert.equal(profile.formal_claim_role,'canonical-source');assert.equal(p.application_runtime.settlement,'empty-effects/v1');
 }
});
test('generated no-effects settlement can serve callers without handwritten native ports and isolates transactions',async()=>{
 const {createEmptyEffectsStore}=await import(pathToFileURL(path.join(base,'node-http-entry-local-v2/runtime/empty-settlement.ts')).href);
 const first=await createEmptyEffectsStore().begin(),second=await createEmptyEffectsStore().begin();
 assert.deepEqual(await first.commit({writes:[],events:[]}),{status:'committed'});
 assert.deepEqual(await first.commit({writes:[],events:[]}),{status:'rejected'});
 assert.deepEqual(await second.commit({writes:[],events:[]}),{status:'committed'});
 const nonempty=await createEmptyEffectsStore().begin();assert.deepEqual(await nonempty.commit({writes:[{forbidden:true}],events:[]}),{status:'rejected'});await nonempty.rollback();assert.deepEqual(await nonempty.commit({writes:[],events:[]}),{status:'rejected'});
 const tx=await createEmptyEffectsStore().begin();await assert.rejects(()=>tx.read({}),/READ_UNSUPPORTED/);
 let getter=0;const bad=Object.defineProperty({events:[]},'writes',{get(){getter++;return[];},enumerable:true});await assert.rejects(()=>tx.commit(bad),/BATCH/);assert.equal(getter,0);
});
