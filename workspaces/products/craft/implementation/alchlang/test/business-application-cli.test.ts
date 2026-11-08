import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {createBusinessApplicationFixture} from '../../../../../../../craft/projects/domainspec-v2/impl/cli/test/helpers/business-profile.js';
// Open questions: default fresh installed command discovery BA18 and publication remains held.
test('actual public CLI supports select/check/plan/view/generate/verify for one application without functions or technical companions',t=>{
 const f=createBusinessApplicationFixture(t,'node-http-entry-local-v2'),root=path.resolve(import.meta.dirname,'..'),out=path.join(f.root,'output'),lock=path.join(f.root,'lock.json');
 const run=(command:string,extra:string[]=[])=>spawnSync(process.execPath,[path.join(root,'dist/core-cli.js'),'profile',command,f.file,...extra],{encoding:'utf8',maxBuffer:16*1024*1024});
 const selected=run('select');assert.equal(selected.status,0,selected.stderr);const selection=JSON.parse(selected.stdout);writeFileSync(lock,JSON.stringify(selection.lock));assert.equal(existsSync(out),false);
 for(const command of ['check','plan','view']){const result=run(command,['--lock',lock]);assert.equal(result.status,0,result.stderr);const body=JSON.parse(result.stdout);if(command==='check')assert.equal(body.status,'checked');if(command==='plan'){assert.equal(body.composition.components.filter((c:any)=>c.role==='domain-function').length,0);assert.ok(body.files['applications/receiveNotice/src/profile-entry.ts']);}if(command==='view')assert.equal(body.business.application_models[0].id,'commerce');assert.equal(existsSync(out),false);}
 const built=run('generate',['--lock',lock,'--out',out]);assert.equal(built.status,0,built.stderr);assert.ok(existsSync(path.join(out,'.profile-complete.json')));const verified=run('verify',['--lock',lock,'--out',out]);assert.equal(verified.status,0,verified.stderr);assert.equal(JSON.parse(verified.stdout).status,'verified');
 const occupied=run('generate',['--lock',lock,'--out',out]);assert.notEqual(occupied.status,0);assert.ok(existsSync(path.join(out,'.profile-complete.json')));
 const source=path.join(f.root,'domain.alch');writeFileSync(source,readFileSync(source,'utf8')+'\n');const stale=run('plan',['--lock',lock]);assert.notEqual(stale.status,0);assert.match(stale.stderr,/PROFILE_LOCK_STALE/);
});
