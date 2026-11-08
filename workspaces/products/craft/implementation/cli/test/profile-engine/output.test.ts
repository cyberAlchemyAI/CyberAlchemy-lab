import assert from 'node:assert/strict';
import {mkdirSync,readFileSync,writeFileSync,existsSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {createRequire,syncBuiltinESMExports} from 'node:module';
import test from 'node:test';
import {loadProfileProject} from '../../src/profile-engine/loader.js';
import {qualifyNativeFiles} from '../../src/profile-engine/native-check.js';
import {completeProfileOutput,verifyProfileOutput} from '../../src/profile-engine/output.js';
import {createProfileFixture} from './profile-fixture.js';
// Open questions: PE08 complete generated-output qualification and PE23 installed use.
const compiler=path.resolve(import.meta.dirname,'../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/node_modules/typescript/bin/tsc');
const files={'package.json':'{"type":"module"}\n','src/index.ts':'export function total(price:number,quantity:number):number{return price*quantity;}\n'};
function qualifiedFixture(t:{after(fn:()=>void):void}){const f=createProfileFixture(t),snapshot=loadProfileProject(path.join(f.root,'project.json'),{engine:f.identity.engine,tools:[{key:'typescript-entry',path:compiler},{key:'typescript-parser',path:path.join(path.dirname(path.dirname(compiler)),'lib/typescript.js')}]});const qualification=qualifyNativeFiles(snapshot,files,compiler);return {...f,snapshot,qualification};}
test('actual native check and atomic completion bind source/tool/files and reject tampering',t=>{
 const f=qualifiedFixture(t),target=path.join(f.root,'output');completeProfileOutput(f.snapshot,files,f.qualification,target);verifyProfileOutput(f.snapshot,target,files);
 assert.ok(existsSync(path.join(target,'.profile-complete.json')));
 writeFileSync(path.join(target,'src/index.ts'),'export const changed=true;');assert.throws(()=>verifyProfileOutput(f.snapshot,target,files),/PROFILE_OUTPUT_ARTIFACT_STALE/);
 const other=path.join(f.root,'other');assert.throws(()=>completeProfileOutput(f.snapshot,files,JSON.parse(JSON.stringify(f.qualification)),other),/PROFILE_NATIVE_QUALIFICATION_UNREGISTERED_OR_STALE/);assert.equal(existsSync(other),false);
});
test('missing marker, occupied destination, bad types and source drift reject',t=>{
 const f=qualifiedFixture(t),target=path.join(f.root,'partial');mkdirSync(target);assert.throws(()=>verifyProfileOutput(f.snapshot,target,files),/PROFILE_OUTPUT_INCOMPLETE/);
 writeFileSync(path.join(target,'foreign.txt'),'preserve');assert.throws(()=>completeProfileOutput(f.snapshot,files,f.qualification,target),/target already exists/);assert.equal(readFileSync(path.join(target,'foreign.txt'),'utf8'),'preserve');
 assert.throws(()=>qualifyNativeFiles(f.snapshot,{'wrong.ts':'const value:number="wrong";'},compiler),/PROFILE_NATIVE_CHECK_FAILED/);
 writeFileSync(path.join(f.root,'quote.alch'),readFileSync(path.join(f.root,'quote.alch'),'utf8')+'\n# drift');assert.throws(()=>completeProfileOutput(f.snapshot,files,f.qualification,path.join(f.root,'stale')),/PROFILE_SNAPSHOT_STALE/);assert.equal(existsSync(path.join(f.root,'stale')),false);
});
test('mid-write failure cleans only owned stage and never creates a complete target',t=>{
 const f=qualifiedFixture(t),target=path.join(f.root,'failed'),require=createRequire(import.meta.url),fs=require('node:fs'),original=fs.writeFileSync;let injected=false;
 fs.writeFileSync=(file:any,...args:any[])=>{if(typeof file==='number'&&!injected){injected=true;throw Error('injected write failure');}return original(file,...args);};syncBuiltinESMExports();
 try{assert.throws(()=>completeProfileOutput(f.snapshot,files,f.qualification,target),/injected write failure/);}finally{fs.writeFileSync=original;syncBuiltinESMExports();}
 assert.equal(existsSync(target),false);assert.ok(!readdirSync(f.root).some(p=>p.startsWith('.domainspec-profile-')));
});
test('a racing foreign destination is preserved by kernel no-replace',t=>{
 const f=qualifiedFixture(t),target=path.join(f.root,'race'),require=createRequire(import.meta.url),fs=require('node:fs'),original=fs.writeFileSync;let injected=false;
 fs.writeFileSync=(file:any,...args:any[])=>{if(typeof file==='number'&&!injected){injected=true;mkdirSync(target);original(path.join(target,'foreign.txt'),'foreign');}return original(file,...args);};syncBuiltinESMExports();
 try{assert.throws(()=>completeProfileOutput(f.snapshot,files,f.qualification,target),/target appeared during publication/);}finally{fs.writeFileSync=original;syncBuiltinESMExports();}
 assert.equal(readFileSync(path.join(target,'foreign.txt'),'utf8'),'foreign');assert.equal(existsSync(path.join(target,'.profile-complete.json')),false);
});
test('snapshot change during staging is caught before publication',t=>{
 const f=qualifiedFixture(t),target=path.join(f.root,'drift'),require=createRequire(import.meta.url),fs=require('node:fs'),original=fs.writeFileSync;let injected=false;
 fs.writeFileSync=(file:any,...args:any[])=>{if(typeof file==='number'&&!injected){injected=true;original(path.join(f.root,'quote.alch'),'changed source');}return original(file,...args);};syncBuiltinESMExports();
 try{assert.throws(()=>completeProfileOutput(f.snapshot,files,f.qualification,target),/PROFILE_SNAPSHOT_STALE/);}finally{fs.writeFileSync=original;syncBuiltinESMExports();}
 assert.equal(existsSync(target),false);
});
