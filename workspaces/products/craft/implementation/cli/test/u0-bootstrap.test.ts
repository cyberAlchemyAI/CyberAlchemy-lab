import assert from 'node:assert/strict';
import test from 'node:test';
import {mkdtempSync,cpSync,mkdirSync,readFileSync,writeFileSync,rmSync,symlinkSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
// Plain Node only: exercise actual public compiled SDK, never TSX source rewriting.
// Open Questions: original selection/accepted/native witnesses belong to later tasks.
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const api=(await import(pathToFileURL(path.join(root,'dist/index.js')).href)).profileEngine;
const descriptor=JSON.parse(readFileSync(path.join(root,'profiles/node-http-entry-u0-v4/profile.json'),'utf8'));
const clone=()=>{const dir=mkdtempSync(path.join(os.tmpdir(),'craft-u0-bootstrap-'));for(const name of ['dist','contracts','package.json'])cpSync(path.join(root,name),path.join(dir,name),{recursive:true});mkdirSync(path.join(dir,'profiles'));cpSync(path.join(root,'profiles/node-http-entry-u0-v4'),path.join(dir,'profiles/node-http-entry-u0-v4'),{recursive:true});return dir;};
const profilePath=(dir:string)=>path.join(dir,'profiles/node-http-entry-u0-v4/profile.json');
const publicApi=async(dir:string)=>(await import(pathToFileURL(path.join(dir,'dist/index.js')).href)).profileEngine;

test('closed successor validator rejects old/unknown primitive, role, ABI, wire, configuration and asset contracts',()=>{
 assert.equal(api.validateProfilePackageV4(descriptor).id,'node-http-entry-u0-v4');
 const changes:[string,(value:any)=>void][]=[
  ['old descriptor',v=>{v.id='node-http-entry-v3';}],['old schema',v=>{v.schema_version='craft.profile-package/v3-candidate';}],
  ['ABI',v=>{v.abi='guessed';}],['capability',v=>{v.capabilities[0].recipe_ref='guessed';}],['wire',v=>{v.configuration.schema_version='unknown';}],
  ['config',v=>{v.configuration.request_bytes=0;}],['extra field',v=>{v.configuration.unspecified=true;}],['unknown role',v=>{v.assets[0].role='database';}],
  ['duplicate role',v=>{v.assets[1].role=v.assets[0].role;}],['duplicate path',v=>{v.assets[1].path=v.assets[0].path;}],['exports',v=>{v.assets[0].exports=[];}],
  ['path escape',v=>{v.assets[0].path='../runtime.js';}],['hash',v=>{v.assets[0].sha256='exact-version-locked';}],['bytes',v=>{v.assets[0].bytes=0;}],
  ['scalar',v=>{v.scalar_producer.path='src/pretend.ts';}],['tool operand',v=>{v.build.typescript='exact';}],['effect',v=>{v.effects='transaction';}],
 ];
 for(const [name,change]of changes){const value=structuredClone(descriptor);change(value);assert.throws(()=>api.validateProfilePackageV4(value),undefined,name);}
});

test('actual compiled public bootstrap resolves distinct real runtime exports and has no final callable',async()=>{
 const runtime=await api.createBusinessU0RuntimeV4();runtime.assertCurrent();
 assert.equal(runtime.kind,'business-u0-runtime-v4');assert.equal(runtime.basis.kind,'resolved-u0-native-basis');assert.equal(runtime.basis.artifacts.length,7);
 assert.equal(runtime.basis.artifacts.find((a:any)=>a.requirement.artifact_id==='node').resolved_version,process.versions.node);
 for(const row of runtime.native.assets(runtime.basis)){const bytes=readFileSync(row.artifact.path);assert.equal(createHash('sha256').update(bytes).digest('hex'),row.artifact.sha256);assert.equal(bytes.length,row.artifact.bytes);const record=runtime.basis.artifacts.find((a:any)=>a.requirement.artifact_id===row.basis_artifact_id);assert(record);for(const name of record.requirement.required_exports)assert(record.exports.includes(name));}
 assert.equal(Object.hasOwn(runtime,'callable'),false);assert.equal(Object.hasOwn(runtime.basis,'realized_sha256'),false);
 assert.throws(()=>runtime.native.assertCurrent(structuredClone(runtime.basis)));
 assert.throws(()=>runtime.recipes.assertCurrent({kind:'business-recipe-selection-v2'}));
 runtime.dispose();assert.throws(()=>runtime.assertCurrent());
});

test('public loader rejects drift in an actual native file, missing scalar and stale dist inventory',async()=>{
 for(const change of ['native','scalar','inventory','symlink']){const dir=clone();try{const own=await publicApi(dir);
  if(change==='native')writeFileSync(path.join(dir,'profiles/node-http-entry-u0-v4/runtime/u0-values.js'),'export const wrong=true;\n');
  if(change==='scalar')rmSync(path.join(dir,'dist/generation/configured-exact-uint64-source.js'));
  if(change==='symlink'){const file=path.join(dir,'profiles/node-http-entry-u0-v4/runtime/u0-values.js');rmSync(file);symlinkSync(path.join(root,'profiles/node-http-entry-u0-v4/runtime/u0-values.js'),file);}
  if(change==='inventory'){const loaded=await own.loadBusinessU0ProfileV4();writeFileSync(path.join(dir,'dist/unrecorded.js'),'export const value=1;\n');assert.throws(()=>own.assertLoadedU0ProfileV4Current(loaded));}else await assert.rejects(()=>own.loadBusinessU0ProfileV4());
 }finally{rmSync(dir,{recursive:true,force:true});}}
});

test('matching asset pins do not substitute for observing the actual required native export',async()=>{
 const dir=clone();try{const file=path.join(dir,'profiles/node-http-entry-u0-v4/runtime/u0-json-decode.js'),body=readFileSync(file,'utf8').replaceAll('decodeU0Json','absentRequiredDecoder');writeFileSync(file,body);
  const next=JSON.parse(readFileSync(profilePath(dir),'utf8')),asset=next.assets.find((a:any)=>a.role==='decoder'),old=asset.sha256;asset.sha256=createHash('sha256').update(body).digest('hex');const oldBytes=asset.bytes;asset.bytes=Buffer.byteLength(body);writeFileSync(profilePath(dir),JSON.stringify(next));
  const pins=path.join(dir,'dist/profile-engine/u0-runtime-pins.generated.js');let compiled=readFileSync(pins,'utf8').replaceAll(old,asset.sha256);compiled=compiled.replace('"bytes": '+oldBytes,'"bytes": '+asset.bytes);writeFileSync(pins,compiled);
  const own=await publicApi(dir);await assert.rejects(()=>own.loadBusinessU0ProfileV4(),/actual callable export missing/);
 }finally{rmSync(dir,{recursive:true,force:true});}
});

test('same-byte replacement of built SDK invalidates the original captured basis',async()=>{
 const dir=clone();try{const own=await publicApi(dir),loaded=await own.loadBusinessU0ProfileV4(),file=path.join(dir,'dist/profile-engine/contracts-v4.js'),bytes=readFileSync(file);rmSync(file);writeFileSync(file,bytes);assert.throws(()=>own.assertLoadedU0ProfileV4Current(loaded),/original bytes or physical closure changed/);}finally{rmSync(dir,{recursive:true,force:true});}
});

test('bootstrap independently captures original source bytes and invalidates them on physical edits',async()=>{
 const dir=mkdtempSync(path.join(os.tmpdir(),'craft-u0-source-capture-'));
 try{const file=path.join(dir,'business.alch');cpSync(path.join(root,'test/profile-engine/fixtures/u0-v2/business.alch'),file);
  const runtime=await api.createBusinessU0RuntimeV4(),captured=runtime.captureSource('dispatching',dir,'business.alch');
  assert.equal(captured.capture.source.sha256,createHash('sha256').update(readFileSync(file)).digest('hex'));assert.equal(captured.source.path,'business.alch');assert.equal(captured.capture.profiles[0].id,'node-http-entry-u0-v4');
  assert.throws(()=>runtime.captureSource('dispatching',dir,'business.alch'),/unique bounded model/);
  writeFileSync(file,readFileSync(file,'utf8')+'\n');assert.throws(()=>runtime.assertCurrent(),/original bytes or physical closure changed/);
 }finally{rmSync(dir,{recursive:true,force:true});}
});
