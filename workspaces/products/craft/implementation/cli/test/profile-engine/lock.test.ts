import assert from 'node:assert/strict';
import {mkdirSync,mkdtempSync,readFileSync,writeFileSync,cpSync,rmSync,symlinkSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {loadProfileProject,assertProfileSnapshotCurrent,profileSnapshotFiles} from '../../src/profile-engine/loader.ts';
import {createProfileLock,validateProfileLock} from '../../src/profile-engine/lock.ts';
import {PROFILE_ROLE_CONTRACTS,sha256} from '../../src/profile-engine/contracts.ts';

// Open questions: PE19 exact complete core/tool freeze manifests. These tests exercise declared closure loading.
function fixture(t:{after(fn:()=>void):void}){
 const root=mkdtempSync(path.join(os.tmpdir(),'profile-lock-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 cpSync(path.join(import.meta.dirname,'fixtures/quote-business'),root,{recursive:true});mkdirSync(path.join(root,'profiles'),{recursive:true});
 const write=(name:string,data:any)=>{const file=path.join(root,name);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,typeof data==='string'?data:JSON.stringify(data,null,2)+'\n');return file;};
 write('engine.js','export const version=1;');write('tool.js','// inert identity bytes');
 const identity={engine:[{key:'engine.js',path:path.join(root,'engine.js')}],tools:[{key:'tool.js',path:path.join(root,'tool.js')}]};
 const pkg=(id:string,dependencies:any[]=[])=>({schema_version:'craft.profile-package/v1',id,version:'1.0.0',engine:'craft.profile-engine/v1',conflict_policy:'reject',dependencies,capabilities:[{role:'shared-http-port',descriptor_ref:PROFILE_ROLE_CONTRACTS['shared-http-port'].descriptor_ref,recipe_ref:PROFILE_ROLE_CONTRACTS['shared-http-port'].recipe_ref}],budgets:{operations:100,rows:100,join_pairs:100,depth:16,bytes:8192},rules:[{id:'defaults',op:'defaults',as:'defaults',values:{method:'POST'}}],assets:[{id:'runtime',path:'runtime.mjs',kind:'native',sha256:sha256('throw Error("MUST_NOT_RUN");'),includes:[],holes:{}}]});
 const save=(p:any,relative='profiles/'+p.id)=>{write(relative+'/runtime.mjs','throw Error("MUST_NOT_RUN");');return write(relative+'/profile.json',p);};
 const project=JSON.parse(readFileSync(path.join(root,'project.json'),'utf8'));project.profiles=[{id:'rootPack',version:'1.0.0',path:'profiles/rootPack'}];write('project.json',project);save(pkg('rootPack'));
 return {root,identity,write,pkg,save,project,load:()=>loadProfileProject(path.join(root,'project.json'),identity)};
}
test('transitive package/asset/source/core/tool bytes yield portable deterministic locks without execution',t=>{
 const f=fixture(t);const child=f.pkg('basePack'),childFile=f.save(child);f.save(f.pkg('rootPack',[{id:'basePack',version:'1.0.0',path:'../basePack',sha256:sha256(readFileSync(childFile))}]));
 const a=f.load(),b=f.load();assert.equal(a.lock.lock_sha256,b.lock.lock_sha256);assert.deepEqual(a.packages.map(p=>p.id),['basePack','rootPack']);assert.ok(profileSnapshotFiles(a).some(p=>p.key==='asset:basePack:runtime'));
 assertProfileSnapshotCurrent(a);const moved=mkdtempSync(path.join(os.tmpdir(),'profile-lock-moved-'));t.after(()=>rmSync(moved,{recursive:true,force:true}));cpSync(f.root,moved,{recursive:true});
 const relocated=loadProfileProject(path.join(moved,'project.json'),{engine:[{key:'engine.js',path:path.join(moved,'engine.js')}],tools:[{key:'tool.js',path:path.join(moved,'tool.js')}]});assert.equal(a.lock.lock_sha256,relocated.lock.lock_sha256);
 assert.throws(()=>assertProfileSnapshotCurrent(JSON.parse(JSON.stringify(a))),/PROFILE_SNAPSHOT_UNREGISTERED/);
 f.write('profiles/basePack/runtime.mjs','changed');assert.throws(()=>assertProfileSnapshotCurrent(a),/PROFILE_SNAPSHOT_STALE/);assert.throws(()=>f.load(),/PROFILE_ASSET_DIGEST/);
});
test('locks bind source, engine and tool drift and reject forged self-digests',t=>{
 const f=fixture(t),initial=f.load();for(const file of ['quote.alch','engine.js','tool.js']){
  const old=readFileSync(path.join(f.root,file),'utf8');f.write(file,old+'\n');assert.throws(()=>assertProfileSnapshotCurrent(initial),/PROFILE_SNAPSHOT_STALE/);assert.throws(()=>loadProfileProject(path.join(f.root,'project.json'),f.identity,initial.lock),/PROFILE_LOCK_STALE/);f.write(file,old);
 }
 assertProfileSnapshotCurrent(initial);const bad=JSON.parse(JSON.stringify(initial.lock));bad.source_sha256='f'.repeat(64);assert.throws(()=>validateProfileLock(bad),/PROFILE_LOCK_DIGEST/);
 assert.throws(()=>createProfileLock({...initial.lock,packages:[...initial.lock.packages,...initial.lock.packages]}),/PROFILE_LOCK_CONFLICT/);
});
test('dependency identity/version/digest conflicts and cycles reject',t=>{
 const f=fixture(t);const b=f.pkg('basePack',[{id:'rootPack',version:'1.0.0',path:'../rootPack',sha256:'0'.repeat(64)}]),bFile=f.save(b);f.save(f.pkg('rootPack',[{id:'basePack',version:'1.0.0',path:'../basePack',sha256:sha256(readFileSync(bFile))}]));assert.throws(()=>f.load(),/PROFILE_DEPENDENCY_CYCLE/);
 const plain=f.pkg('basePack');f.save(plain);f.save(f.pkg('rootPack',[{id:'basePack',version:'2.0.0',path:'../basePack',sha256:sha256(readFileSync(path.join(f.root,'profiles/basePack/profile.json')))}]));assert.throws(()=>f.load(),/PROFILE_DEPENDENCY_VERSION/);
 const rival=f.pkg('rootPack');f.save(rival,'profiles/rival');const child=f.pkg('basePack',[{id:'rootPack',version:'1.0.0',path:'../rival',sha256:sha256(readFileSync(path.join(f.root,'profiles/rival/profile.json')))}]);const file=f.save(child);f.save(f.pkg('rootPack',[{id:'basePack',version:'1.0.0',path:'../basePack',sha256:sha256(readFileSync(file))}]));assert.throws(()=>f.load(),/PROFILE_DEPENDENCY_CONFLICT/);
});
test('package roots/assets cannot use symlinks and declared byte budgets apply',t=>{
 const f=fixture(t);const asset=path.join(f.root,'profiles/rootPack/runtime.mjs');rmSync(asset);symlinkSync(path.join(f.root,'engine.js'),asset);assert.throws(()=>f.load(),/PROFILE_PATH_SYMLINK/);rmSync(asset);f.write('profiles/rootPack/runtime.mjs','throw Error("MUST_NOT_RUN");');
 const small=f.pkg('rootPack');small.budgets.bytes=1;f.save(small);assert.throws(()=>f.load(),/PROFILE_CLOSURE_BUDGET/);
});

test('declared dependency pins and package-root symlinks reject before loading assets',t=>{
 const f=fixture(t);f.save(f.pkg('basePack'));f.save(f.pkg('rootPack',[{id:'basePack',version:'1.0.0',path:'../basePack',sha256:'f'.repeat(64)}]));assert.throws(()=>f.load(),/PROFILE_DEPENDENCY_DIGEST/);
 f.save(f.pkg('rootPack'));symlinkSync(path.join(f.root,'profiles/rootPack'),path.join(f.root,'profiles/alias'),'dir');f.project.profiles[0].path='profiles/alias';f.write('project.json',f.project);assert.throws(()=>f.load(),/PROFILE_PATH_SYMLINK/);
});
