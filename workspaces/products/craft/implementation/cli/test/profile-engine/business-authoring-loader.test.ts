import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,linkSync,mkdirSync,mkdtempSync,readFileSync,renameSync,rmSync,symlinkSync,truncateSync,writeFileSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {validateBusinessAuthoringProject,validateProfilePackageV3} from '../../src/profile-engine/contracts-v3.js';
import {loadBusinessAuthoringProject,assertBusinessAuthoringSnapshotCurrent} from '../../src/profile-engine/loader-v3.js';
import {loadProfileProject,loadProfileProjectV2,assertProfileSnapshotCurrent} from '../../src/profile-engine/loader.js';
import {dataDigest,PROFILE_ROLE_CONTRACTS,ProfileRejected} from '../../src/profile-engine/contracts.js';

// B05.1 custody tests. These synthetic decision bytes do not establish business acceptance.
// Open questions: docs/BUSINESS-AUTHORING-CONTRACTS.md; recipe execution is B05.2.
const cli=path.resolve(import.meta.dirname,'../..');
const hash=(bytes:string|Buffer)=>createHash('sha256').update(bytes).digest('hex');
const plain=(value:unknown)=>JSON.parse(JSON.stringify(value));
const authoring=()=>({contract:'craft.business-authoring-contracts/1-candidate',input_schema:'alchlang.business-spec/v1-candidate',recipe_ref:'ground-entity-bool-operation/v1-candidate',logic_profile:'fol-core/1-candidate',target:'node-typescript',effects:'none',wire:{schema_version:'craft.operation-json-post/v1-candidate',method:'POST',body:'whole-input',route_prefix:'/',request_bytes:16384,timeout_ms:2000}});
function fixture(t:{after(fn:()=>void):void},variant='node-http-entry-local-v2'){
 const root=mkdtempSync(path.join(os.tmpdir(),'business-authoring-loader-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 const write=(relative:string,value:unknown)=>{const file=path.join(root,relative);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,typeof value==='string'?value:JSON.stringify(value,null,2)+'\n');return file;};
 cpSync(path.join(cli,'profiles',variant),path.join(root,'profile'),{recursive:true});
 const profile=JSON.parse(readFileSync(path.join(root,'profile/profile.json'),'utf8'));
 Object.assign(profile,{schema_version:'craft.profile-package/v3-candidate',id:variant.replace(/v2$/,'v3'),engine:'craft.profile-engine/v3-candidate',authoring:authoring()});
 if(variant==='node-http-api-prefix-v2')profile.authoring.wire.route_prefix='/api/';
 write('profile/profile.json',profile);
 write('business.alch','model Delivery\n  Boolean guard source captured, not parsed by this loader\n');
 const project={schema_version:'craft.business-authoring-project/v1-candidate',id:'delivery',models:[{id:'delivery',source:'business.alch'}],profiles:[{id:profile.id,version:profile.version,path:'profile'}],decisions:[] as any[]};
 const file=write('project.json',project);
 write('core/engine.ts',readFileSync(path.join(cli,'src/profile-engine/loader-v3.ts'),'utf8'));
 write('tools/protocol.ts',readFileSync(path.join(cli,'src/profile-engine/business-authoring-protocol.ts'),'utf8'));
 const identity={engine:[{key:'engine.ts',path:path.join(root,'core/engine.ts')}],tools:[{key:'protocol.ts',path:path.join(root,'tools/protocol.ts')}]};
 const decision=()=>({schema_version:'craft.business-decision/v1-candidate',decision_id:'synthetic-inspection-only',owner:'delivery-team',outcome:'declined',subject:{model_id:'delivery',version:'1',canonicalization:'craft.business-review-keysort/v1',digest_algorithm:'sha256',digest:'a'.repeat(64)},legacy_meaning_subjects:[{meaning_id:'synthetic-only',version:'1',canonicalization:'domainspec-json-keysort-excluding-acceptance-v1',digest_algorithm:'sha256',digest:'c'.repeat(64)}],definition_closure:{definition_ids:['synthetic-only'],digest_algorithm:'sha256',digest:'b'.repeat(64)},authority_effect:'none'});
 const technical=(id='technical',role:'environment'|'operational-expectation'|'application-operation'='environment')=>({schema_version:'craft.profile-package/v1',id,version:'1.0.0',engine:'craft.profile-engine/v1',conflict_policy:'reject',dependencies:[] as any[],capabilities:[{role,descriptor_ref:PROFILE_ROLE_CONTRACTS[role].descriptor_ref,recipe_ref:PROFILE_ROLE_CONTRACTS[role].recipe_ref}],budgets:{operations:100,rows:100,join_pairs:100,depth:16,bytes:1048576},rules:[{id:'defaults',op:'defaults',as:'technical',values:{}}],assets:[{id:'inert',path:'inert.mjs',kind:'native',sha256:hash('throw Error("NEVER_EXECUTE_PACKAGE_CODE");'),includes:[],holes:{}}]});
 const saveTechnical=(pkg=technical(),relative='profile/technical')=>{write(relative+'/inert.mjs','throw Error("NEVER_EXECUTE_PACKAGE_CODE");');write(relative+'/profile.json',pkg);return {id:pkg.id,version:pkg.version,path:relative.replace(/^profile\//,''),sha256:hash(readFileSync(path.join(root,relative,'profile.json')))};};
 return {root,file,identity,write,project,profile,decision,technical,saveTechnical,load:(lock?:unknown)=>loadBusinessAuthoringProject(file,identity,lock),saveProject:()=>write('project.json',project),saveProfile:()=>write('profile/profile.json',profile)};
}
function rejected(fn:()=>unknown,code:string,pointer?:string){assert.throws(fn,(error:unknown)=>error instanceof ProfileRejected&&error.code===code&&(pointer===undefined||error.pointer===pointer));}

test('v3 distinct immutable snapshot captures exact project/model/assets and an inspection-only empty decision set',t=>{
 const f=fixture(t),snapshot=f.load();assert.equal(snapshot.kind,'business-authoring-snapshot');
 assert.equal(snapshot.packages[0]!.data.schema_version,'craft.profile-package/v3-candidate');
 assert.deepEqual(Object.keys(snapshot.sources).sort(),['business.alch','project.json']);
 assert.equal(snapshot.sources['business.alch']!.sha256,hash(readFileSync(path.join(f.root,'business.alch'))));
 assert.equal(snapshot.packages[0]!.manifest_sha256,hash(readFileSync(path.join(f.root,'profile/profile.json'))));
 assert.equal(Object.keys(snapshot.packages[0]!.assets).length,4);
 assert.ok(Object.isFrozen(snapshot)&&Object.isFrozen(snapshot.project.models)&&Object.isFrozen(snapshot.packages[0]!.assets)&&Object.isFrozen(snapshot.lock.packages));
 assert.equal(snapshot.lock.decision_sha256,dataDigest([]));
 const {lock_sha256,...body}=snapshot.lock;assert.equal(lock_sha256,dataDigest(body));assert.deepEqual(f.load(snapshot.lock).lock,snapshot.lock);
 assertBusinessAuthoringSnapshotCurrent(snapshot);
 rejected(()=>assertProfileSnapshotCurrent(snapshot as any),'PROFILE_SNAPSHOT_UNREGISTERED');
 for(const forged of [plain(snapshot),{...snapshot},Object.create(snapshot),{}])rejected(()=>assertBusinessAuthoringSnapshotCurrent(forged as any),'BUSINESS_PROFILE_SNAPSHOT_UNREGISTERED');
});
for(const variant of ['node-http-shared-ports-v2','node-http-api-prefix-v2'])test('supported technical variant has explicit compatible runtime '+variant,t=>{
 const snapshot=fixture(t,variant).load();assert.equal(snapshot.packages.length,1);assertBusinessAuthoringSnapshotCurrent(snapshot);
});
test('locks bind engine, tool, source, decisions and full selected packages with portable relocation',t=>{
 const f=fixture(t);f.project.decisions=[{model_id:'delivery',path:'decisions/inspection.json'}];f.write('decisions/inspection.json',f.decision());f.saveProject();
 const snapshot=f.load();assert.ok(snapshot.sources['decisions/inspection.json']);
 const moved=mkdtempSync(path.join(os.tmpdir(),'business-authoring-moved-'));t.after(()=>rmSync(moved,{recursive:true,force:true}));cpSync(f.root,moved,{recursive:true});
 const relocated=loadBusinessAuthoringProject(path.join(moved,'project.json'),{engine:[{key:'engine.ts',path:path.join(moved,'core/engine.ts')}],tools:[{key:'protocol.ts',path:path.join(moved,'tools/protocol.ts')}]},snapshot.lock);
 assert.deepEqual(relocated.lock,snapshot.lock);
 const after=f.decision();after.outcome='accepted';f.write('decisions/inspection.json',after);
 rejected(()=>assertBusinessAuthoringSnapshotCurrent(snapshot),'BUSINESS_PROFILE_SNAPSHOT_STALE');
 const fresh=f.load();assert.equal(fresh.lock.source_sha256,snapshot.lock.source_sha256);assert.notEqual(fresh.lock.decision_sha256,snapshot.lock.decision_sha256);
 rejected(()=>f.load(snapshot.lock),'BUSINESS_PROFILE_LOCK_STALE');
});
test('dependencies are captured transitively; identical repeated references share the selected owner',t=>{
 const f=fixture(t),child=f.technical('leaf','operational-expectation');
 f.saveTechnical(child,'profile/technical/leaf');const parent=f.technical();parent.dependencies=[{id:'leaf',version:'1.0.0',path:'leaf',sha256:hash(readFileSync(path.join(f.root,'profile/technical/leaf/profile.json')))}];
 f.profile.dependencies=[f.saveTechnical(parent)];f.saveProfile();
 f.project.profiles.push({id:'leaf',version:'1.0.0',path:'profile/technical/leaf'});f.saveProject();
 const snapshot=f.load();assert.deepEqual(snapshot.packages.map(pkg=>pkg.id),['leaf',f.profile.id,'technical']);
 const leaf=snapshot.packages[0]!;assert.equal(leaf.assets.inert!.text,'throw Error("NEVER_EXECUTE_PACKAGE_CODE");');assertBusinessAuthoringSnapshotCurrent(snapshot);
 f.write('profile/technical/leaf/inert.mjs','throw Error("changed");');rejected(()=>assertBusinessAuthoringSnapshotCurrent(snapshot),'BUSINESS_PROFILE_SNAPSHOT_STALE');
});
for(const [name,change,code,pointer] of [
 ['unknown semantic map',(p:any)=>p.semantics={},'BUSINESS_SCHEMA_UNKNOWN','/semantics'],
 ['duplicate model id',(p:any)=>p.models.push({id:'delivery',source:'other.alch'}),'BUSINESS_PROFILE_DUPLICATE_ID','/models'],
 ['duplicate source',(p:any)=>p.models.push({id:'other',source:'business.alch'}),'BUSINESS_PROFILE_DUPLICATE_ID','/models/source'],
 ['duplicate profile',(p:any)=>p.profiles.push({...p.profiles[0]}),'BUSINESS_PROFILE_DUPLICATE_ID','/profiles'],
 ['unknown decision model',(p:any)=>p.decisions.push({model_id:'other',path:'decision.json'}),'BUSINESS_PROFILE_DECISION_MODEL','/decisions/0/model_id'],
 ['source traversal',(p:any)=>p.models[0].source='../outside.alch','BUSINESS_SCHEMA_VALUE','/models/0/source'],
 ['drive path',(p:any)=>p.models[0].source='C:outside.alch','BUSINESS_PROFILE_PATH_ESCAPE','/models/0/source'],
 ['non-exact version',(p:any)=>p.profiles[0].version='latest','BUSINESS_PROFILE_VERSION','/profiles/0/version'],
] as [string,(p:any)=>void,string,string][])test('project rejects '+name,t=>{const f=fixture(t);change(f.project);rejected(()=>validateBusinessAuthoringProject(f.project),code,pointer);});
for(const [name,change,code] of [
 ['recipe',(p:any)=>p.authoring.recipe_ref='execute-js','BUSINESS_SCHEMA_CONST'],
 ['logic',(p:any)=>p.authoring.logic_profile='other/1','BUSINESS_SCHEMA_CONST'],
 ['target',(p:any)=>p.authoring.target='python','BUSINESS_SCHEMA_CONST'],
 ['effects',(p:any)=>p.authoring.effects='database','BUSINESS_SCHEMA_CONST'],
 ['wire method',(p:any)=>p.authoring.wire.method='GET','BUSINESS_SCHEMA_CONST'],
 ['wire input',(p:any)=>p.authoring.wire.body='infer','BUSINESS_SCHEMA_CONST'],
 ['unknown evaluator',(p:any)=>p.evaluate='js','BUSINESS_SCHEMA_UNKNOWN'],
 ['unknown role contract',(p:any)=>p.capabilities[0].descriptor_ref='invented','BUSINESS_PROFILE_ROLE_MAPPING_UNSUPPORTED'],
 ['duplicate asset',(p:any)=>p.assets.push({...p.assets[0]}),'BUSINESS_PROFILE_DUPLICATE_ID'],
 ['runtime asset missing',(p:any)=>p.application_runtime.formal_profile_asset='missing','BUSINESS_PROFILE_RUNTIME_ASSET_REQUIRED'],
 ['runtime wrong asset kind',(p:any)=>p.assets[0].kind='native','BUSINESS_PROFILE_RUNTIME_ASSET_REQUIRED'],
 ['transport mismatch',(p:any)=>p.application_runtime.transport='shared','BUSINESS_PROFILE_TRANSPORT_COMPATIBILITY'],
 ['wire exceeds actual native limit',(p:any)=>p.authoring.wire.timeout_ms=30001,'BUSINESS_PROFILE_WIRE_COMPATIBILITY'],
 ['dependency traversal',(p:any)=>p.dependencies=[{id:'bad',version:'1.0.0',path:'../bad',sha256:'0'.repeat(64)}],'BUSINESS_PROFILE_PATH_ESCAPE'],
] as [string,(p:any)=>void,string][])test('package rejects '+name,t=>{const f=fixture(t);change(f.profile);rejected(()=>validateProfilePackageV3(f.profile),code);});
test('listed missing/malformed decisions reject but absence is valid inspection',t=>{
 const f=fixture(t);assert.equal(f.load().project.decisions.length,0);f.project.decisions=[{model_id:'delivery',path:'decision.json'}];f.saveProject();
 rejected(()=>f.load(),'BUSINESS_PROFILE_FILE_MISSING');f.write('decision.json',{});rejected(()=>f.load(),'BUSINESS_SCHEMA_REQUIRED');
 f.write('decision.json',f.decision());assert.equal(f.load().project.decisions.length,1);
});
for(const relative of ['project.json','business.alch','profile/profile.json','profile/formal/profile.json','profile/formal/identity.json','profile/runtime/empty-settlement.ts','profile/runtime/application-http.mts','core/engine.ts','tools/protocol.ts'])test('currentness detects selected byte drift '+relative,t=>{
 const f=fixture(t),snapshot=f.load();f.write(relative,readFileSync(path.join(f.root,relative),'utf8')+'\n');rejected(()=>assertBusinessAuthoringSnapshotCurrent(snapshot),'BUSINESS_PROFILE_SNAPSHOT_STALE');assert.throws(()=>f.load(snapshot.lock));
});
test('currentness detects selected typed additions/removals and identical-byte replacement',t=>{
 const f=fixture(t),snapshot=f.load();f.project.models.push({id:'extra',source:'extra.alch'});f.write('extra.alch','model Extra');f.saveProject();rejected(()=>assertBusinessAuthoringSnapshotCurrent(snapshot),'BUSINESS_PROFILE_SNAPSHOT_STALE');
 const second=f.load();rmSync(path.join(f.root,'extra.alch'));rejected(()=>assertBusinessAuthoringSnapshotCurrent(second),'BUSINESS_PROFILE_FILE_MISSING');
 const g=fixture(t),old=g.load(),original=path.join(g.root,'business.alch');g.write('replacement.alch',readFileSync(original,'utf8'));renameSync(path.join(g.root,'replacement.alch'),original);rejected(()=>assertBusinessAuthoringSnapshotCurrent(old),'BUSINESS_PROFILE_SNAPSHOT_STALE');
 const h=fixture(t),stable=h.load();h.write('unselected.txt','unrelated files are not selected inputs');assertBusinessAuthoringSnapshotCurrent(stable);
});
test('symlink and hardlink substitution fail for source, package and tool paths',t=>{
 for(const relative of ['business.alch','profile/formal/profile.json','tools/protocol.ts']){
  const f=fixture(t),snapshot=f.load(),target=path.join(f.root,relative);f.write('replacement',readFileSync(target,'utf8'));rmSync(target);symlinkSync(path.join(f.root,'replacement'),target);rejected(()=>assertBusinessAuthoringSnapshotCurrent(snapshot),'BUSINESS_PROFILE_PATH_SYMLINK');assert.throws(()=>f.load());
 }
 const f=fixture(t);renameSync(path.join(f.root,'profile'),path.join(f.root,'real-profile'));symlinkSync(path.join(f.root,'real-profile'),path.join(f.root,'profile'),'dir');rejected(()=>f.load(),'BUSINESS_PROFILE_PATH_SYMLINK');
 const g=fixture(t);rmSync(path.join(g.root,'tools/protocol.ts'));linkSync(path.join(g.root,'core/engine.ts'),path.join(g.root,'tools/protocol.ts'));rejected(()=>g.load(),'BUSINESS_PROFILE_FILE_ALIAS');
});
test('self-rehashed incompatible formal/identity/native assets still reject',t=>{
 for(const assetId of ['formal-profile','identity-algorithm','empty-settlement','application-http']){
  const f=fixture(t),asset=f.profile.assets.find((row:any)=>row.id===assetId),file=path.join(f.root,'profile',asset.path);
  const value=asset.kind==='data'?JSON.stringify({changed:'incompatible'}):'throw Error("DO_NOT_EXECUTE");';f.write('profile/'+asset.path,value);asset.sha256=hash(readFileSync(file));f.saveProfile();
  rejected(()=>f.load(),'BUSINESS_PROFILE_RUNTIME_COMPATIBILITY');
 }
});
test('ambiguous owner selection rejects in either package order; technical role collisions reject',t=>{
 for(const reverse of [false,true]){
  const f=fixture(t);cpSync(path.join(f.root,'profile'),path.join(f.root,'other'),{recursive:true});const other={...f.profile,id:'other'};f.write('other/profile.json',other);f.project.profiles.push({id:'other',version:'1.0.0',path:'other'});if(reverse)f.project.profiles.reverse();f.saveProject();rejected(()=>f.load(),'BUSINESS_PROFILE_RUNTIME_AMBIGUOUS');
 }
 const f=fixture(t);f.profile.dependencies=[f.saveTechnical(f.technical('competing','application-operation'))];f.saveProfile();rejected(()=>f.load(),'BUSINESS_PROFILE_ROLE_OWNER_AMBIGUOUS');
 const g=fixture(t);g.profile.dependencies=[g.saveTechnical()];delete g.profile.authoring;g.profile.schema_version='craft.profile-package/v1';g.profile.engine='craft.profile-engine/v1';g.profile.assets=[];g.profile.capabilities=[{role:'environment',descriptor_ref:PROFILE_ROLE_CONTRACTS.environment.descriptor_ref,recipe_ref:PROFILE_ROLE_CONTRACTS.environment.recipe_ref}];delete g.profile.application_runtime;g.profile.rules=[{id:'default',op:'defaults',as:'unused',values:{}}];g.saveProfile();rejected(()=>g.load(),'BUSINESS_PROFILE_RUNTIME_AMBIGUOUS');
});
test('dependency exact pins, versions, roots and repeated cached pins cannot conflict',t=>{
 for(const mutation of ['digest','version','cached-pin','same-id-other-root']){
  const f=fixture(t),reference=f.saveTechnical();f.profile.dependencies=[reference];
  if(mutation==='digest')reference.sha256='0'.repeat(64);if(mutation==='version')reference.version='2.0.0';
  if(mutation==='cached-pin'){
   // Capture child first as an explicit selection, then demand a conflicting cached dependency pin.
   f.project.profiles.unshift({id:reference.id,version:reference.version,path:'profile/technical'});f.saveProject();reference.sha256='0'.repeat(64);
  }
  if(mutation==='same-id-other-root'){f.saveTechnical(f.technical(),'profile/rival');f.project.profiles.push({id:'technical',version:'1.0.0',path:'profile/rival'});f.saveProject();}
  f.saveProfile();rejected(()=>f.load(),mutation==='digest'?'BUSINESS_PROFILE_DEPENDENCY_DIGEST':mutation==='version'?'BUSINESS_PROFILE_DEPENDENCY_VERSION':'BUSINESS_PROFILE_DEPENDENCY_CONFLICT');
 }
});
test('file, package, depth and identity budgets fail closed',t=>{
 const f=fixture(t);truncateSync(path.join(f.root,'business.alch'),16777217);rejected(()=>f.load(),'BUSINESS_PROFILE_FILE_BUDGET');
 const g=fixture(t);g.profile.budgets.bytes=1;g.saveProfile();rejected(()=>g.load(),'BUSINESS_PROFILE_CLOSURE_BUDGET');
 const h=fixture(t);h.identity.engine=[];rejected(()=>h.load(),'BUSINESS_PROFILE_IDENTITY_MISSING');
 const i=fixture(t);i.identity.tools.push({...i.identity.tools[0]!});rejected(()=>i.load(),'BUSINESS_PROFILE_IDENTITY_CONFLICT');
 const j=fixture(t);j.identity.tools[0]!.path=j.identity.engine[0]!.path;rejected(()=>j.load(),'BUSINESS_PROFILE_IDENTITY_CONFLICT');
 const k=fixture(t);k.profile.budgets.depth=0;rejected(()=>validateProfilePackageV3(k.profile),'BUSINESS_SCHEMA_LIMIT');
});
test('finite transitive depth budget rejects before ownership selection or package execution',t=>{
 const f=fixture(t);let child:ReturnType<typeof f.saveTechnical>|undefined;
 for(let level=34;level>=1;level--){
  const relative='profile/'+Array.from({length:level},()=> 'nested').join('/'),pkg=f.technical('depth'+level);
  if(child)pkg.dependencies=[{...child,path:'nested'}];
  child=f.saveTechnical(pkg,relative);
 }
 f.profile.dependencies=[{...child!,path:'nested'}];f.saveProfile();
 rejected(()=>f.load(),'BUSINESS_PROFILE_DEPENDENCY_BUDGET');
});
test('file kind, invalid UTF-8 and invalid JSON never become captured selected input',t=>{
 const f=fixture(t);rmSync(path.join(f.root,'business.alch'));mkdirSync(path.join(f.root,'business.alch'));rejected(()=>f.load(),'BUSINESS_PROFILE_FILE_KIND');
 const g=fixture(t);writeFileSync(path.join(g.root,'business.alch'),Buffer.from([0xff,0xfe]));rejected(()=>g.load(),'BUSINESS_PROFILE_FILE_ENCODING');
 const h=fixture(t);h.write('profile/profile.json','{ invalid JSON');rejected(()=>h.load(),'BUSINESS_PROFILE_FILE_JSON');
});
test('UTF-8 BOM is retained in source capture and never silently removed from JSON',t=>{
 const f=fixture(t),text='\ufeff'+readFileSync(path.join(f.root,'business.alch'),'utf8');f.write('business.alch',text);
 const source=f.load().sources['business.alch']!;
 assert.equal(source.text,text);assert.equal(Buffer.byteLength(source.text!),source.bytes);assert.equal(hash(source.text!),source.sha256);
 const g=fixture(t);g.write('profile/profile.json','\ufeff'+readFileSync(path.join(g.root,'profile/profile.json'),'utf8'));rejected(()=>g.load(),'BUSINESS_PROFILE_FILE_JSON');
});
test('regular-to-FIFO substitution between lstat and open rejects without blocking',t=>{
 const f=fixture(t),target=path.join(f.root,'business.alch');
 // A child deadline makes this a real nonblocking regression instead of risking a hung runner.
 const script=`
  import fs from 'node:fs';
  import {syncBuiltinESMExports} from 'node:module';
  import {execFileSync} from 'node:child_process';
  import {loadBusinessAuthoringProject} from ${JSON.stringify(pathToFileURL(path.join(cli,'src/profile-engine/loader-v3.ts')).href)};
  const original=fs.openSync,target=${JSON.stringify(target)};let swapped=false;
  fs.openSync=function(file,flags,...rest){
   if(String(file)===target&&!swapped){swapped=true;fs.unlinkSync(target);execFileSync('mkfifo',[target]);}
   return original.call(fs,file,flags,...rest);
  };
  syncBuiltinESMExports();
  try{loadBusinessAuthoringProject(${JSON.stringify(f.file)},${JSON.stringify(f.identity)});throw Error('FIFO accepted');}
  catch(error){if(!swapped||error.code!=='BUSINESS_PROFILE_FILE_DRIFT')throw error;process.stdout.write('FIFO rejected');}
 `;
 assert.equal(execFileSync(process.execPath,['--import','tsx','--input-type=module','-e',script],{cwd:cli,timeout:5000,encoding:'utf8'}),'FIFO rejected');
});
test('pinned lock must be closed, immutable-shaped and exactly equal, including ordering and self digest',t=>{
 const f=fixture(t),snapshot=f.load();
 const malformed=plain(snapshot.lock);malformed.extra=true;rejected(()=>f.load(malformed),'BUSINESS_SCHEMA_UNKNOWN','/extra');
 const bad=plain(snapshot.lock);bad.source_sha256='0'.repeat(64);rejected(()=>f.load(bad),'BUSINESS_PROFILE_LOCK_DIGEST','/lock_sha256');
 const different=plain(snapshot.lock);different.packages[0].version='2.0.0';const {lock_sha256:_,...body}=different;different.lock_sha256=dataDigest(body);rejected(()=>f.load(different),'BUSINESS_PROFILE_LOCK_STALE');
 let calls=0;const getter={get schema_version(){calls++;return snapshot.lock.schema_version;}};assert.throws(()=>f.load(getter),/PROFILE_DATA_ACCESSOR/);assert.equal(calls,0);
});
test('no supplied accessor, proxy or old v2 data is silently admitted',t=>{
 const f=fixture(t);let calls=0;const getter={get engine(){calls++;return f.identity.engine;},tools:f.identity.tools};assert.throws(()=>loadBusinessAuthoringProject(f.file,getter as any),/PROFILE_DATA_ACCESSOR/);assert.equal(calls,0);
 assert.throws(()=>validateProfilePackageV3(new Proxy(f.profile,{})),/PROFILE_DATA_PROXY/);
 const old=JSON.parse(readFileSync(path.join(cli,'profiles/node-http-entry-local-v2/profile.json'),'utf8'));rejected(()=>validateProfilePackageV3(old),'BUSINESS_SCHEMA_REQUIRED','/authoring');
 f.write('profile/profile.json',old);rejected(()=>f.load(),'BUSINESS_SCHEMA_REQUIRED','/authoring');
});
test('existing v1/v2 loaders and exact locks remain separate and available',t=>{
 for(const version of ['v1','v2']){
  const f=fixture(t),source=version==='v1'?'quote-business':'business-notice';cpSync(path.join(import.meta.dirname,'fixtures',source),path.join(f.root,'legacy'),{recursive:true});cpSync(path.join(cli,'profiles','node-http-entry-local-'+version),path.join(f.root,'legacy/profile'),{recursive:true});
  const file=path.join(f.root,'legacy/project.json'),project=JSON.parse(readFileSync(file,'utf8'));project.profiles=[{id:'node-http-entry-local-'+version,version:'1.0.0',path:'profile'}];writeFileSync(file,JSON.stringify(project));
  const loader=version==='v1'?loadProfileProject:loadProfileProjectV2,snapshot=loader(file,f.identity);assertProfileSnapshotCurrent(snapshot);assert.deepEqual(loader(file,f.identity,snapshot.lock).lock,snapshot.lock);
  rejected(()=>assertBusinessAuthoringSnapshotCurrent(snapshot as any),'BUSINESS_PROFILE_SNAPSHOT_UNREGISTERED');
 }
});
