import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,cpSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {root,node} from './package-construction-build.mjs';
import {inspectPackage} from './runtime/package.mjs';
const R=path.resolve(root,'../../../../../..'),dir=mkdtempSync(path.join(root,'.local/frozen-inspection-proof-')),checks=[];
const source=path.join(R,'workspaces/products/define/implementation/cli/alchlang/tests/fixtures/package');
const report=await inspectPackage(source);assert.equal(report.frozen_integrity,'verified');checks.push('actual-retained-package-native-inspection');
const restored=path.join(dir,'restored');assert.deepEqual(await inspectPackage(source,{destination:restored}),report);
const manifest=JSON.parse(readFileSync(path.join(source,'manifest.json')));
assert.deepEqual(readFileSync(path.join(restored,'manifest.json')),readFileSync(path.join(source,'manifest.json')));
for(const row of Object.values(manifest.members))assert.deepEqual(readFileSync(path.join(restored,row.path)),readFileSync(path.join(source,row.path)));
checks.push('exact-required-byte-reconstruction');
await assert.rejects(()=>inspectPackage(source,{destination:restored}));checks.push('existing-destination-preserved');
const corrupt=path.join(dir,'corrupt');cpSync(source,corrupt,{recursive:true});writeFileSync(path.join(corrupt,'pack.json'),'{}\n');await assert.rejects(()=>inspectPackage(corrupt));checks.push('corrupt-member-refused');
for(const [label,mutate]of [
 ['embedded-digest',v=>v.applications[0].meaning_ref.sha256='0'.repeat(64)],
 ['embedded-pack-identity',v=>v.applications[0].meaning_ref.pack_id='pack:unrelated-fixture'],
 ['embedded-selector-depth',v=>v.applications[0].meaning_ref.selector='/working_meanings/0/statement'],
 ['embedded-identity',v=>v.applications[0].meaning_ref.entry_id='meaning:unrelated-fixture']]){
 const target=path.join(dir,label);cpSync(source,target,{recursive:true});const pack=JSON.parse(readFileSync(path.join(target,'pack.json')));mutate(pack);
 const raw=Buffer.from(JSON.stringify(pack)+'\n'),sha=createHash('sha256').update(raw).digest('hex');writeFileSync(path.join(target,'pack.json'),raw);
 const changed=structuredClone(manifest),row=changed.members[changed.pack_binding.member_id];row.sha256=sha;row.bytes=raw.length;changed.pack_binding.sha256=sha;changed.pack_binding.bytes=raw.length;writeFileSync(path.join(target,'manifest.json'),JSON.stringify(changed)+'\n');
 await assert.rejects(()=>inspectPackage(target),/native-operation-refused/);checks.push('native-negative:'+label);
}
for(const relative of ['workspaces/products/define/implementation/cli/alchlang/tests/fixtures/materialization-package']){assert.equal((await inspectPackage(path.join(R,relative))).frozen_integrity,'verified');checks.push('actual-package:'+relative);}
await assert.rejects(()=>inspectPackage(path.join(R,'workspaces/products/define/implementation/cli/alchlang/tests/fixtures/obsolete-pack-v2')),/structural-contract-invalid/);checks.push('obsolete-Pack-v2-refused');
const guard=path.join(dir,'no-legacy');mkdirSync(guard);writeFileSync(path.join(guard,'sitecustomize.py'),`import sys,importlib.abc\nclass NoLegacy(importlib.abc.MetaPathFinder):\n def find_spec(self,fullname,path=None,target=None):\n  if fullname.split('.')[0]=='define_core':raise RuntimeError('legacy-Define-engine-forbidden')\nsys.meta_path.insert(0,NoLegacy())\n`);
const script=path.join(dir,'guarded.mjs');writeFileSync(script,`import {inspectPackage} from ${JSON.stringify(path.join(root,'runtime/package.mjs'))};console.log(JSON.stringify(await inspectPackage(${JSON.stringify(source)})));`);
const guarded=spawnSync(node,[script],{encoding:'utf8',env:{...process.env,PYTHONPATH:guard},maxBuffer:8*1024*1024});assert.equal(guarded.status,0,guarded.stderr);assert.deepEqual(JSON.parse(guarded.stdout),report);checks.push('legacy-engine-import-actively-blocked');
function cli(args){const p=spawnSync(node,[path.join(root,'runtime/cli.mjs'),...args],{encoding:'utf8',env:{...process.env,PYTHONPATH:guard},maxBuffer:8*1024*1024});assert.equal(p.status,0,p.stderr);return JSON.parse(p.stdout);}
const inspected=cli(['inspect','--package',source]);assert.equal(inspected.api_version,'define.api/v1');assert.equal(inspected.operation,'inspect');assert.equal(inspected.data.root_sha256,report.root_sha256);checks.push('actual-inspect-CLI-with-engine-blocked');
const cliRestored=path.join(dir,'cli-restored'),reconstructed=cli(['reconstruct','--package',source,'--output',cliRestored]);assert.equal(reconstructed.data.posture,'exact-frozen-reconstruction');assert.deepEqual(reconstructed.observed_writes,[cliRestored]);
for(const row of Object.values(manifest.members))assert.deepEqual(readFileSync(path.join(cliRestored,row.path)),readFileSync(path.join(source,row.path)));checks.push('actual-reconstruct-CLI-exact-bytes-with-engine-blocked');
const receipt={schema_version:'define-frozen-inspection-verification/v1',status:'PASS',checks,check_count:checks.length,inspection_reconstruction_cli_cutover:true,full_cli_cutover:false,scope:'Actual retained package inspection and exact reconstruction through current AlchLang and shared byte adapters; preparation/materialization not inferred.'};writeFileSync(path.join(root,'.local/FROZEN-INSPECTION-VERIFICATION.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));