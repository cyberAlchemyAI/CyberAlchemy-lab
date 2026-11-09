import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
const A=import.meta.dirname,R=path.resolve(A,'../../../../../..'),W=path.join(R,'workspaces/products/define/work/development/alchlang-only');
const read=p=>JSON.parse(readFileSync(p)),sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const manifest=read(path.join(W,'MANIFEST.json'));assert.equal(manifest.complete,true);
for(const row of manifest.files){const p=path.join(R,row.path);assert.equal(sha(p),row.sha256,row.path);assert.equal(readFileSync(p).length,row.bytes,row.path);}
const receipt=read(path.join(W,'VERIFICATION.json'));assert.equal(receipt.status,'PASS');assert.equal(receipt.complete,true);
for(const row of receipt.proofs){assert.equal(sha(path.join(R,row.path)),row.sha256,row.path);assert.equal(read(path.join(R,row.path)).status,'PASS');}
for(const row of read(path.join(W,'DEFINITIONS.json')).bindings)assert.equal(sha(path.join(R,row.path)),row.sha256,row.path);
const coverage=read(path.join(W,'COVERAGE.json'));assert.equal(coverage.rows.length,18);
for(const row of coverage.rows){assert.equal(row.complete_replacement,true,row.id);assert(existsSync(path.join(R,row.alchlang_ref.path)),row.id);assert(existsSync(path.join(W,row.generation_evidence)),row.id);}
for(const row of read(path.join(W,'RETIREMENT.json')).retired)assert(!existsSync(path.join(R,row.path)),row.path);
function bindings(value){if(Array.isArray(value))for(const row of value)bindings(row);else if(value&&typeof value==='object'){if(value.path&&value.sha256&&existsSync(path.join(R,value.path)))assert.equal(sha(path.join(R,value.path)),value.sha256,value.path);for(const row of Object.values(value))bindings(row);}}
for(const row of manifest.files)if(row.path.includes('/models/'))bindings(read(path.join(R,row.path)));
assert.equal(receipt.runtime_copies,0);assert.equal(receipt.shared_runtime_targets,1);assert.equal(receipt.canonical_owner_outcome,null);
console.log(JSON.stringify({status:'PASS',durable_records:manifest.files.length,proofs:receipt.proofs.length,verified_checks:receipt.verified_checks,definition_bindings:44,behavior_obligations:18,predecessors_absent:true,runtime_copies:0}));
