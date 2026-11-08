import assert from 'node:assert/strict';
import test from 'node:test';
import {existsSync,readFileSync,writeFileSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {createRequire,syncBuiltinESMExports} from 'node:module';
import {execFileSync} from 'node:child_process';
import {createProfileFixture,useShippedProfile} from '../profile-engine/profile-fixture.js';
import {prepareProfileProject,planProfileProject,generateProfileProject,verifyProfileProject,disposeProfileProject,runProfileProjectCommand} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-engine.js';
// Open questions: PE14 Operation join and PE23 fresh installed consumer.
const alchRoot=path.resolve(import.meta.dirname,'../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation');
test('public planning is inert after registered preparation; help and JSON diagnostics expose scope',async t=>{
 const f=createProfileFixture(t),prepared=await prepareProfileProject(path.join(f.root,'project.json'));t.after(()=>disposeProfileProject(prepared));
 const require=createRequire(import.meta.url),saved:{object:any;key:string;value:any}[]=[];let attempts=0;
 for(const [object,key]of [[require('node:fs'),'writeFileSync'],[require('node:fs'),'readFileSync'],[require('node:child_process'),'execFileSync'],[globalThis,'fetch']] as const){saved.push({object,key,value:(object as any)[key]});(object as any)[key]=()=>{attempts++;throw Error('plan IO');};}syncBuiltinESMExports();
 try{const plan=planProfileProject(prepared);assert.equal(plan.authority_effect,'none');assert.ok(plan.files['app/index.mjs']);assert.equal(attempts,0);assert.throws(()=>planProfileProject(JSON.parse(JSON.stringify(prepared))),/PROFILE_PROJECT_UNREGISTERED/);}finally{for(const s of saved.reverse())s.object[s.key]=s.value;syncBuiltinESMExports();}
 let stdout='',stderr='';assert.equal(await runProfileProjectCommand(['--help'],{stdout:v=>stdout+=v,stderr:v=>stderr+=v}),0);assert.match(stdout,/select\|check\|plan\|generate\|view\|verify/);assert.match(stdout,/unproved/);assert.match(stdout,/publication.*deferred/);
 assert.equal(await runProfileProjectCommand(['generate',path.join(f.root,'project.json')],{stdout:v=>stdout+=v,stderr:v=>stderr+=v}),1);assert.match(stderr,/PROFILE_COMMAND_OUTPUT/);assert.equal(existsSync(path.join(f.root,'output')),false);
 const help=execFileSync(process.execPath,[path.join(alchRoot,'dist/core-cli.js'),'profile','--help'],{encoding:'utf8'});assert.match(help,/external wire configuration/);
});
test('public generation repeats byte-for-byte, verifies inventory and rejects stale lock/output',async t=>{
 const f=useShippedProfile(createProfileFixture(t)),project=path.join(f.root,'project.json'),first=await prepareProfileProject(project);const lock=planProfileProject(first).lock;
 const a=path.join(f.root,'output-a'),b=path.join(f.root,'output-b');generateProfileProject(first,a);assert.equal(verifyProfileProject(first,a).status,'verified');disposeProfileProject(first);
 const second=await prepareProfileProject(project,lock);t.after(()=>disposeProfileProject(second));generateProfileProject(second,b);
 const inventory=(folder:string):Record<string,string>=>Object.fromEntries(readdirSync(folder,{withFileTypes:true}).flatMap(item=>item.isDirectory()?Object.entries(inventory(path.join(folder,item.name))).map(([key,value])=>[item.name+'/'+key,value]):[[item.name,readFileSync(path.join(folder,item.name),'utf8')]]));
 assert.deepEqual(inventory(a),inventory(b));writeFileSync(path.join(a,'app/index.mjs'),'export const changed=true;');assert.throws(()=>verifyProfileProject(second,a),/PROFILE_OUTPUT_ARTIFACT_STALE/);
 const config=JSON.parse(readFileSync(path.join(f.root,'provider.json'),'utf8'));config.bindings[0].operation.location_ref='changed-provider';writeFileSync(path.join(f.root,'provider.json'),JSON.stringify(config));await assert.rejects(()=>prepareProfileProject(project,lock),/PROFILE_LOCK_STALE/);
});
