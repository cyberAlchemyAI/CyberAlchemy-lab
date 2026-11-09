import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,mkdirSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {root,node,fingerprint} from './materialization-build.mjs';
const R=path.resolve(root,'../../../../../..'),directory=mkdtempSync(path.join(root,'.local/materialization-workflow-proof-')),checks=[];
const source=path.join(R,'workspaces/products/define/implementation/cli/alchlang/tests/fixtures/materialization-package');
const guard=path.join(directory,'no-legacy');mkdirSync(guard);writeFileSync(path.join(guard,'sitecustomize.py'),`import sys,importlib.abc\nclass NoLegacy(importlib.abc.MetaPathFinder):\n def find_spec(self,fullname,path=None,target=None):\n  if fullname.split('.')[0]=='define_core':raise RuntimeError('legacy-Define-engine-forbidden')\nsys.meta_path.insert(0,NoLegacy())\n`);
function cli(args,success=true){const p=spawnSync(node,[path.join(root,'runtime/cli.mjs'),...args],{encoding:'utf8',maxBuffer:8*1024*1024,env:{...process.env,PYTHONPATH:guard}});if(success){assert.equal(p.status,0,p.stderr);return JSON.parse(p.stdout);}assert.notEqual(p.status,0);return p.stderr;}
const output=path.join(directory,'output'),reply=cli(['materialize','--package',source,'--output',output]);assert.equal(reply.operation,'materialize');assert.equal(reply.outcome,'prepared');checks.push('actual-materialize-CLI-with-engine-actively-blocked');
const pack=JSON.parse(readFileSync(path.join(source,'pack.json'))),selection=pack.materialization_selection[0];
assert.deepEqual(readFileSync(path.join(output,'definitions/000/definition.json')),readFileSync(path.join(source,'inputs',selection.definition_binding.path)));checks.push('exact-selected-Definition-bytes-preserved');
assert.deepEqual(readFileSync(path.join(output,'definitions/000/field-lineage.json')),readFileSync(path.join(source,'inputs',selection.field_lineage_binding.path)));checks.push('exact-selected-lineage-bytes-preserved');
const priorProjection=path.join(R,'workspaces/products/define/implementation/cli/alchlang/tests/fixtures/materialization-DEFINITION.md');assert.deepEqual(readFileSync(path.join(output,'definitions/000/DEFINITION.md')),readFileSync(priorProjection));checks.push('same-shared-provider-Markdown-projection');
assert.equal(reply.data.report.actual_owner_outcome,null);assert.equal(reply.data.report.authority_effect,'none');assert.equal(reply.data.report.definitions[0].posture,'candidate-only');checks.push('candidate-only-no-owner-outcome');
assert.match(cli(['materialize','--package',source,'--output',output],false),/output-exists-or-unavailable/);checks.push('existing-output-preserved');
function fixture(label,mutate){
 const target=path.join(directory,label);mkdirSync(target);const manifest=JSON.parse(readFileSync(path.join(source,'manifest.json'))),raws=new Map(Object.values(manifest.members).map(row=>[row.path,readFileSync(path.join(source,row.path))]));
 mutate(raws);
 const hash=raw=>createHash('sha256').update(raw).digest('hex');
 function bindings(value){let changed=false;if(value&&typeof value==='object'){
  if(!Array.isArray(value)&&Object.keys(value).sort().join(',')==='bytes,digest_kind,path,sha256'){
   const raw=raws.get(value.path)??raws.get('inputs/'+value.path);if(raw&&(value.bytes!==raw.length||value.sha256!==hash(raw))){value.bytes=raw.length;value.sha256=hash(raw);changed=true;}
  }else for(const child of Object.values(value))changed=bindings(child)||changed;
 }return changed;}
 for(let attempt=0;attempt<20;attempt++){let changed=false;for(const [name,raw]of raws){let value;try{value=JSON.parse(raw);}catch{continue;}if(bindings(value)){raws.set(name,Buffer.from(JSON.stringify(value)+'\n'));changed=true;}}if(!changed)break;if(attempt===19)throw Error('negative-fixture-binding-cycle');}
 for(const row of Object.values(manifest.members)){const raw=raws.get(row.path);row.bytes=raw.length;row.sha256=hash(raw);const file=path.join(target,row.path);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,raw);}
 const body=manifest.members[manifest.pack_binding.member_id];manifest.pack_binding.bytes=body.bytes;manifest.pack_binding.sha256=body.sha256;writeFileSync(path.join(target,'manifest.json'),JSON.stringify(manifest)+'\n');return target;
}
const lineagePath='inputs/'+selection.field_lineage_binding.path;
for(const [label,mutate,expected]of [
 ['incomplete-lineage',raws=>{const body=JSON.parse(raws.get(lineagePath));body.fields.pop();raws.set(lineagePath,Buffer.from(JSON.stringify(body)+'\n'));},/incomplete-or-duplicate-field-lineage/],
 ['duplicate-lineage',raws=>{const body=JSON.parse(raws.get(lineagePath));body.fields[1].target_selector=body.fields[0].target_selector;raws.set(lineagePath,Buffer.from(JSON.stringify(body)+'\n'));},/incomplete-or-duplicate-field-lineage/],
 ['field-value-mismatch',raws=>{const body=JSON.parse(raws.get(lineagePath));body.fields.find(row=>row.target_selector==='/term').source_selector='/definition_id';raws.set(lineagePath,Buffer.from(JSON.stringify(body)+'\n'));},/incomplete-or-conflicting-field-lineage/],
 ['owner-route-gap',raws=>{const body=JSON.parse(raws.get('pack.json'));body.materialization_selection[0].owner_route=null;raws.set('pack.json',Buffer.from(JSON.stringify(body)+'\n'));},/materialization-owner-gap/]]){
 const from=fixture(label,mutate),destination=path.join(directory,label+'-output');
 assert.match(cli(['materialize','--package',from,'--output',destination],false),expected);assert.equal(existsSync(destination),false);checks.push('negative-with-rebound-valid-byte-closure:'+label);
}
const receipt={schema_version:'define-native-materialization-workflow-verification/v1',status:'PASS',source:fingerprint(),checks,check_count:checks.length,legacy_engine_runtime_imports:'actively blocked',preparation_confirmation_replacement:false};writeFileSync(path.join(root,'.local/NATIVE-MATERIALIZATION-WORKFLOW-VERIFICATION.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));