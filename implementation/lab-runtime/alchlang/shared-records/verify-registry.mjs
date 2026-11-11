import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { registryAssessment } from './ports.mjs';
import { bind } from './snapshots.mjs';
import { digest } from './verified-projection.mjs';

const root=path.resolve(import.meta.dirname,'../../../..');
const registry=JSON.parse(readFileSync(path.join(root,'authority/definitions/registry.json')));
const home=mkdtempSync(path.join(tmpdir(),'lab-all-registry-'));
const materials=new Map();
function capture(name,raw) {const bytes=Buffer.from(raw);materials.set(name,bytes);return bind(name,bytes);}
const owner=name=>capture('decision:'+name,JSON.stringify({decision_ref:name}));
const schema=capture('definition-v1-schema',readFileSync(path.join(root,'authority/artifact-types/definition/v1/schema.json')));
const generator=capture('definition-v1-generator',readFileSync(path.join(root,'authority/artifact-types/definition/v1/generator.py')));
const descriptor=capture('definition-v1-descriptor',readFileSync(path.join(root,'authority/artifact-types/definition/v1/candidates/0002-post-foundation-01/artifact.json')));
const admission=capture('definition-v1-admission',readFileSync(path.join(root,'authority/admissions/definition-complete-lab-model/v1/artifact-type-admission.json')));
const entries=[];
for (const [index,entry] of registry.entries.entries()) {
  const raw=readFileSync(path.join(root,entry.path));
  assert.equal(digest(raw),entry.sha256);
  const body=capture(entry.path,raw);
  const input=path.join(home,'definition.json'),output=path.join(home,'DEFINITION.md');
  writeFileSync(input,raw);
  const run=spawnSync('python3',['-B',path.join(root,'authority/artifact-types/definition/v1/generator.py'),input,'--output',output],{encoding:'utf8'});
  assert.equal(run.status,0,run.stderr);
  const projection=capture('projection:'+index,readFileSync(output));
  entries.push({definition_id:entry.definition_id,version:entry.version,body,
    carrier:{ref:'cal.artifact-type.definition/v1',descriptor,admission},schema,generator,
    owner_disposition:owner(entry.admission_decision_ref),
    standing:registry.current_lookup[entry.definition_id]===entry.definition_id+'@'+entry.version?'admitted-current':'admitted-retained',
    predecessor:null,projection});
}
const material=binding=>{
  const raw=materials.get(binding.ref ?? binding.path);
  if (!raw || digest(raw)!==binding.sha256 || raw.length!==Number(binding.bytes)) throw Error('material-mismatch');
  return raw;
};
const proposed={entries,current_lookup:registry.current_lookup};
const carriers={'cal.artifact-type.definition/v1':{schema,generator,descriptor,admission}};
const result=registryAssessment(registry,proposed,material,carriers,[]);
assert.equal(result.retained,189);
assert.equal(result.current,183);
assert.throws(()=>registryAssessment(registry,{...proposed,entries:[...entries,entries[0]]},material,carriers,[]),/duplicate-version/);
const modified=structuredClone(proposed);modified.entries[0].standing='withdrawn';
assert.throws(()=>registryAssessment(registry,modified,material,carriers,[]),/lifecycle-change/);
const changedOwner=structuredClone(proposed);changedOwner.entries[0].owner_disposition=owner('decision:unrelated');
assert.throws(()=>registryAssessment(registry,changedOwner,material,carriers,[]),/decision-changed/);
const changedContract=structuredClone(proposed);changedContract.entries[0].schema={...schema,sha256:'0'.repeat(64)};
assert.throws(()=>registryAssessment(registry,changedContract,material,carriers,[]),/material-mismatch/);
const receipt={status:'PASS',retained:result.retained,current:result.current,
 checks:['all-189-original-bodies-schema-validated','all-189-original-generators-reconstructed',
 'all-current-and-retained-selections-preserved','duplicate-version-refused',
 'unapproved-lifecycle-change-refused','changed-original-decision-refused','changed-carrier-schema-refused'],
 scope:'Actual retained Lab Definition/v1 bodies, schemas and deterministic projections. Generated Decision-reference carriers are test projections of the admitted registry references.'};
writeFileSync(path.join(import.meta.dirname,'REGISTRY-VERIFICATION.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify(receipt));
