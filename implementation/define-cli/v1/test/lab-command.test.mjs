import assert from 'node:assert/strict';
import {test,before,after} from 'node:test';
import {mkdtempSync,readFileSync,writeFileSync,existsSync,rmSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {join,resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {inspectRuntime} from '../src/runtime-integrity.mjs';
import {digest} from '../src/canonical.mjs';
const root=resolve(import.meta.dirname,'../../../..'),cli=join(root,'define/define');let dir,result;
const command=args=>spawnSync(cli,args,{cwd:tmpdir(),encoding:'utf8',timeout:60000,maxBuffer:16*1024*1024});
before(()=>{
 dir=mkdtempSync(join(tmpdir(),'lab-define-command-'));
 const r=command(['run','--goal','Define complete export','--intent','Investigate missing rows','--context','Account A, filters F, snapshot S','--consumer','incident-investigator','--input',join(root,'implementation/define-cli/v1/fixtures/incident-input.json'),'--output',join(dir,'pack.json'),'--json']);
 assert.equal(r.status,0,r.stderr);result=JSON.parse(r.stdout);
});
after(()=>rmSync(dir,{recursive:true,force:true}));
test('Repository launcher generates an exact Lab-bound language-reviewed candidate',()=>{
 assert.equal(result.ok,true);assert.equal(result.validation.handoff_ready,true);assert.equal(result.validation.validation_scope,'deterministic-structure-and-language-quality');assert.equal(result.lab_binding.envelope.source_epoch,result.definition_pack.source_epoch);
});
test('Repository CLI compiles the reviewed pack with the actual Lab Craft compiler',()=>{
 const r=command(['compile','--input',join(dir,'pack.json'),'--out',join(dir,'compiled'),'--json']);assert.equal(r.status,0,r.stderr);assert.equal(JSON.parse(r.stdout).ok,true);assert.ok(existsSync(join(dir,'compiled/handoff-receipt.json')));
});
test('CLI rejects a mismatched context binding before compiling',()=>{
 const bad=structuredClone(result);bad.lab_binding.envelope.head='forged';writeFileSync(join(dir,'bad.json'),JSON.stringify(bad));const r=command(['compile','--input',join(dir,'bad.json'),'--out',join(dir,'bad')]);assert.equal(r.status,3);assert.match(r.stderr,/context-binding-mismatch/);assert.equal(existsSync(join(dir,'bad')),false);
});
test('CLI rejects a correctly hashed but expired context',()=>{
 const bad=structuredClone(result);bad.lab_binding.envelope.expires_at='2000-01-01T00:00:00Z';bad.definition_pack.context_envelope_digest=digest(bad.lab_binding.envelope);const {pack_id,...body}=bad.definition_pack;bad.definition_pack.pack_id='definition-pack:'+digest(body);writeFileSync(join(dir,'expired.json'),JSON.stringify(bad));const r=command(['compile','--input',join(dir,'expired.json'),'--out',join(dir,'expired')]);assert.equal(r.status,3);assert.match(r.stderr,/stale-Lab-context/);
});
test('Runtime integrity rejects altered dependency bytes',()=>{
 const manifest=JSON.parse(readFileSync(join(root,'implementation/define-cli/v1/runtime-manifest.json')));manifest.files[0].sha256='0'.repeat(64);manifest.inventory_sha256=digest(manifest.files);const file=join(dir,'manifest.json');writeFileSync(file,JSON.stringify(manifest));assert.throws(()=>inspectRuntime({manifestPath:file}),/runtime-source-drift/);
});
test('Reuse requires a selected exact current Lab definition',async()=>{
 const {composeDefineContext,runDefineSession}=await import('../index.mjs');const context=composeDefineContext({consumer:'fixture'});const r=runDefineSession({goal:'Reuse a meaning',intent:'Keep the source boundary',context:'Local review',consumer:'fixture',concepts:['Definition'],responses:[{concept_id:'concept:'+digest('Definition').slice(0,16),action:'reuse',payload:{definition_ref:'unowned:invented'}}],context_result:context});assert.equal(r.ok,false);assert.match(r.reason_codes.join(','),/selected-current-exact-definition/);
});
test('Inspect resolves the actual current Definition identity',async()=>{
 const {callLab}=await import('../src/context-adapter.mjs');const r=callLab('inspect',{subject:'cal.definition.definition'});assert.equal(r.category,'definition');assert.equal(r.axes.status,'admitted-current');assert.equal(r.version_ref,'cal.definition.definition@1.0.0-candidate.1');
});
test('Successor result schema accepts the Lab binding and rejects undeclared fields',async()=>{
 const {callLab}=await import('../src/context-adapter.mjs');assert.equal(callLab('validate-result',{result}).valid,true);assert.throws(()=>callLab('validate-result',{result:{...result,undeclared:true}}),/invalid Lab Define result/);
});
