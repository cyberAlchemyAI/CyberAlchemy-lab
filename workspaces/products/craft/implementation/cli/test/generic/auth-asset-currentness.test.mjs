/** Selected native-asset custody in isolated physical component fixtures.
 * No edit to a shared executing package, no caller manifest or Auth allow.
 * Open Questions: ../../docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {syncBuiltinESMExports} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const cli=fileURLToPath(new URL('../../',import.meta.url));
const stale=error=>error?.diagnostics?.[0]?.code==='StaleOwner';
const stamp=stat=>[stat.dev,stat.ino,stat.mode,stat.size,stat.mtimeNs,stat.ctimeNs].map(String);
async function fixture(run){
 const root=fs.mkdtempSync(path.join(tmpdir(),'craft-auth-asset-custody-')),sdk=path.join(root,'sdk');
 fs.mkdirSync(sdk);
 try{
  for(const relative of ['package.json','dist/generic/auth-asset.js','dist/commerce/commerce-core-physical.js','dist/commerce/commerce-core-syntax.js','dist/commerce/commerce-core-grammar.js','dist/profile-engine/contracts.js','profiles/generic-v1/family.json']){
   const target=path.join(sdk,relative);fs.mkdirSync(path.dirname(target),{recursive:true});fs.copyFileSync(path.join(cli,relative),target);
  }
  fs.cpSync(path.join(cli,'contracts'),path.join(sdk,'contracts'),{recursive:true});
  fs.cpSync(path.join(cli,'profiles/generic-v1/assets/auth'),path.join(sdk,'profiles/generic-v1/assets/auth'),{recursive:true});
  const api=await import(pathToFileURL(path.join(sdk,'dist/generic/auth-asset.js')).href);
  const profiles=path.join(sdk,'profiles'),family=JSON.parse(fs.readFileSync(path.join(profiles,'generic-v1/family.json'),'utf8'));
  const binary=path.join(profiles,'generic-v1',family.asset.binary.path);
  await run({root,sdk,api,profiles,binary,payloads:new Set([binary,...family.asset.libraries.map(row=>row.path)])});
 }finally{assert.equal(fs.realpathSync(root),root);assert.equal(path.dirname(root),fs.realpathSync(tmpdir()));assert.ok(path.basename(root).startsWith('craft-auth-asset-custody-'));fs.rmSync(root,{recursive:true,force:true});}
}
test('selected asset captures original payload bytes once and checks every later use without rereading payloads',async()=>fixture(async f=>{
 const original=fs.readFileSync;let payloadBytes=0,payloadReads=0;
 fs.readFileSync=function(file,...args){const value=original.call(this,file,...args);if(f.payloads.has(String(file))){payloadReads++;payloadBytes+=typeof value==='string'?Buffer.byteLength(value):value.byteLength;}return value;};syncBuiltinESMExports();
 try{
  const asset=f.api.loadOriginalGenericAuthAsset(path.join(f.root,'native-work'));
  assert.ok(payloadReads>0&&payloadBytes>0,'positive control: initial capture really reads selected native bytes');
  const captured={payloadReads,payloadBytes};payloadReads=0;payloadBytes=0;
  for(let n=0;n<8;n++)f.api.assertGenericSelectedAuthAsset(asset);
  assert.equal(payloadReads,0,'unchanged use checks retain original capture instead of hashing payloads again');
  assert.equal(payloadBytes,0);
  assert.throws(()=>f.api.assertGenericSelectedAuthAsset({...asset}),error=>error?.diagnostics?.[0]?.code==='ForeignOwner');
  console.error('selected-asset-currentness '+JSON.stringify({captured,subsequent_checks:8,subsequent_payload_bytes:payloadBytes}));
 }finally{fs.readFileSync=original;syncBuiltinESMExports();}
}));
test('same-length native byte change and restored mtime invalidate the original selected owner, even after restoring bytes',async()=>fixture(async f=>{
 const asset=f.api.loadOriginalGenericAuthAsset(path.join(f.root,'native-work')),before=fs.statSync(f.binary),bytes=fs.readFileSync(f.binary),changed=Buffer.from(bytes);
 changed[Math.min(changed.length-1,128)]^=1;
 fs.writeFileSync(f.binary,changed);fs.utimesSync(f.binary,before.atime,before.mtime);
 assert.throws(()=>f.api.assertGenericSelectedAuthAsset(asset),stale);
 fs.writeFileSync(f.binary,bytes);fs.utimesSync(f.binary,before.atime,before.mtime);
 assert.throws(()=>f.api.assertGenericSelectedAuthAsset(asset),stale);
 const fresh=f.api.loadOriginalGenericAuthAsset(path.join(f.root,'fresh-native-work'));f.api.assertGenericSelectedAuthAsset(fresh);
}));
test('same-byte new inode and executable-mode changes cannot reuse a selected owner',async()=>fixture(async f=>{
 let asset=f.api.loadOriginalGenericAuthAsset(path.join(f.root,'native-work'));
 const replacement=path.join(f.root,'replacement');fs.copyFileSync(f.binary,replacement);fs.chmodSync(replacement,0o755);fs.renameSync(replacement,f.binary);
 assert.throws(()=>f.api.assertGenericSelectedAuthAsset(asset),stale);
 asset=f.api.loadOriginalGenericAuthAsset(path.join(f.root,'fresh-native-work'));fs.chmodSync(f.binary,0o644);
 assert.throws(()=>f.api.assertGenericSelectedAuthAsset(asset),stale);
}));
test('selected assets reject an aliased ancestor rather than following it',async()=>fixture(async f=>{
 const asset=f.api.loadOriginalGenericAuthAsset(path.join(f.root,'native-work')),saved=path.join(f.sdk,'profiles-saved');
 fs.renameSync(f.profiles,saved);fs.symlinkSync(saved,f.profiles,'dir');
 try{assert.throws(()=>f.api.assertGenericSelectedAuthAsset(asset),stale);}
 finally{fs.unlinkSync(f.profiles);fs.renameSync(saved,f.profiles);}
}));
test('a parent replaced after binary fstat cannot reuse surviving leaf files in the same check',async()=>fixture(async f=>{
 const asset=f.api.loadOriginalGenericAuthAsset(path.join(f.root,'native-work')),before=stamp(fs.statSync(f.binary,{bigint:true})),saved=path.join(f.sdk,'profiles-saved'),original=fs.fstatSync;
 let replaced=false;
 fs.fstatSync=function(fd,...args){const value=original.call(this,fd,...args);let target;try{target=fs.readlinkSync('/proc/self/fd/'+fd);}catch{}
  if(!replaced&&target===f.binary){fs.renameSync(f.profiles,saved);fs.mkdirSync(f.profiles);fs.renameSync(path.join(saved,'generic-v1'),path.join(f.profiles,'generic-v1'));replaced=true;}
  return value;
 };syncBuiltinESMExports();
 try{assert.throws(()=>f.api.assertGenericSelectedAuthAsset(asset),stale);assert.equal(replaced,true,'the actual descriptor observation triggers the ancestor replacement');assert.deepEqual(stamp(fs.statSync(f.binary,{bigint:true})),before,'the original binary inode and file stamps really survive');}
 finally{fs.fstatSync=original;syncBuiltinESMExports();if(replaced){fs.renameSync(path.join(f.profiles,'generic-v1'),path.join(saved,'generic-v1'));fs.rmdirSync(f.profiles);fs.renameSync(saved,f.profiles);}}
}));
