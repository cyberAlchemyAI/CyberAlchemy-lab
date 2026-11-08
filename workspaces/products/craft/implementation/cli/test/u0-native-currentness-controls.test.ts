import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
// Isolated complete physical public SDK copies. No edit to the executing shared SDK.
// Open Questions: V02 CONTEXT; these are real native-loader/capture controls,
// distinct from original complete request execution and installed qualification.
const core=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),repo=path.resolve(core,'../../../../..'),out=path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/V02'),run=fs.mkdtempSync(path.join(out,'native-')),observed:any[]=[],sha=(v:Buffer|string)=>crypto.createHash('sha256').update(v).digest('hex');
async function fixture(name:string){const root=path.join(run,name);fs.mkdirSync(root);for(const name of ['dist','contracts','package.json'])fs.cpSync(path.join(core,name),path.join(root,name),{recursive:true});fs.mkdirSync(path.join(root,'profiles'));fs.cpSync(path.join(core,'profiles/node-http-entry-u0-v4'),path.join(root,'profiles/node-http-entry-u0-v4'),{recursive:true});const api=(await import(pathToFileURL(path.join(root,'dist/index.js')).href)).profileEngine;return {root,api};}
function record(id:string,value:unknown){observed.push({id,value});process.stdout.write('V02 '+id+'\n');fs.writeFileSync(path.join(run,'native-currentness-observation.json'),JSON.stringify({schema_version:'craft.u0-native-currentness-controls/v1-candidate',observed,scope:'actual original loader/basis/capture in isolated SDK copies; no original joined execution claim',authority_effect:'none',open_questions_ref:'../CONTEXT.md#open-questions'},null,2)+'\n');}
test('actual captured native asset byte and same-byte inode changes invalidate old original handles',async()=>{
 for(const kind of ['byte-drift','inode-replacement']){const f=await fixture(kind),loaded=await f.api.loadBusinessU0ProfileV4(),file=path.join(f.root,'profiles/node-http-entry-u0-v4/runtime/u0-values.js'),before=fs.statSync(file,{bigint:true}),bytes=fs.readFileSync(file);f.api.assertLoadedU0ProfileV4Current(loaded);
 if(kind==='byte-drift')fs.appendFileSync(file,'\n// isolated V02 asset drift\n');else{fs.renameSync(file,file+'.original');fs.writeFileSync(file,bytes);assert.notEqual(fs.statSync(file,{bigint:true}).ino,before.ino);assert.equal(sha(fs.readFileSync(file)),sha(bytes));}
 assert.throws(()=>f.api.assertLoadedU0ProfileV4Current(loaded),/original bytes or physical closure changed/);record('native-asset-'+kind,{old_asset_sha256:sha(bytes),new_asset_sha256:sha(fs.readFileSync(file)),old_inode:String(before.ino),new_inode:String(fs.statSync(file,{bigint:true}).ino),basis:loaded.basis.basis_sha256});}
});
test('valid configuration change needs fresh native basis/source capture and preserves business meaning',async()=>{
 const f=await fixture('configuration'),root=path.join(run,'business');fs.mkdirSync(root);fs.copyFileSync(path.join(core,'test/profile-engine/fixtures/u0-v2/business.alch'),path.join(root,'business.alch'));
 const first=await f.api.createBusinessU0RuntimeV4(),old=first.captureSource('dispatching',root,'business.alch'),manifest=path.join(f.root,'profiles/node-http-entry-u0-v4/profile.json'),profile=JSON.parse(fs.readFileSync(manifest,'utf8'));profile.configuration.body_timeout_ms=2001;fs.writeFileSync(manifest,JSON.stringify(profile,null,2)+'\n');assert.throws(()=>first.assertCurrent());
 const next=await f.api.createBusinessU0RuntimeV4(),fresh=next.captureSource('dispatching',root,'business.alch');assert.equal(old.source.sha256,fresh.source.sha256);assert.equal(old.source.text,fresh.source.text);assert.notEqual(first.basis.basis_sha256,next.basis.basis_sha256);assert.notEqual(old.capture.capture_sha256,fresh.capture.capture_sha256);assert.equal(next.basis.configuration.body_timeout_ms,2001);assert.notEqual(first.basis.sdk_sha256,next.basis.sdk_sha256);next.assertCurrent();record('config-recapture',{same_source_sha256:fresh.source.sha256,old_capture_sha256:old.capture.capture_sha256,new_capture_sha256:fresh.capture.capture_sha256,old_basis_sha256:first.basis.basis_sha256,new_basis_sha256:next.basis.basis_sha256,old_sdk_sha256:first.basis.sdk_sha256,new_sdk_sha256:next.basis.sdk_sha256,profile_manifest_is_part_of_sdk:true});next.dispose();
});
test('unknown ABI and insufficient/extra configuration fields cannot load as qualified native contracts',async()=>{
 const f=await fixture('invalid-contract'),file=path.join(f.root,'profiles/node-http-entry-u0-v4/profile.json'),base=JSON.parse(fs.readFileSync(file,'utf8'));
 for(const [id,change]of [['native-unknown-abi',(v:any)=>v.abi='guessed'],['config-domain',(v:any)=>v.configuration.request_bytes=0],['config-extra',(v:any)=>v.configuration.hidden=true]] as [string,(v:any)=>void][]){const value=structuredClone(base);change(value);assert.throws(()=>f.api.validateProfilePackageV4(value));fs.writeFileSync(file,JSON.stringify(value));await assert.rejects(()=>f.api.loadBusinessU0ProfileV4());record(id,'closed contract and actual loader reject; no basis fabricated');}
});
