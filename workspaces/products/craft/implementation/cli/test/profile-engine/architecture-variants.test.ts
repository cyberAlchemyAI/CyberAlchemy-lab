import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createProfileFixture,useShippedProfile} from './profile-fixture.js';
import {prepareProfileProject,planProfileProject,generateProfileProject,disposeProfileProject} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-engine.js';
// Independent structure and outcome expectations. Open questions: PE16/19 full matrix.
test('package-only shared transport has a distinct owner and real typed-port dependencies',async t=>{
 let frozen:{engine:string;tools:string}|undefined;
 for(const name of ['node-http-entry-local-v1','node-http-shared-ports-v1']){
  const f=useShippedProfile(createProfileFixture(t),name),prepared=await prepareProfileProject(path.join(f.root,'project.json'));t.after(()=>disposeProfileProject(prepared));const plan=planProfileProject(prepared),lock=plan.lock;
  const identity={engine:lock.engine_sha256,tools:lock.tool_sha256};if(frozen)assert.deepEqual(identity,frozen,'all shared compiler/engine/tool bytes must stay frozen');else frozen=identity;
  const shared=plan.composition.components.filter((c:any)=>c.role==='shared-http-port'),entries=plan.composition.components.filter((c:any)=>c.role==='http-entry');
  assert.equal(shared.length,name==='node-http-shared-ports-v1'?1:0);
  for(const entry of entries){assert.equal(entry.owner,name);if(shared.length){assert.ok(entry.depends_on.includes(shared[0].id));assert.match(plan.files[entry.artifact_paths[0]]!,/infrastructure\/http-port\.mjs/);}else assert.equal(entry.depends_on.length,1);}
  if(shared.length){assert.equal(shared[0].owner,name);assert.equal(shared[0].artifact_paths[0],'infrastructure/http-port.mjs');assert.match(plan.files['infrastructure/http-port.mjs']!,/export const httpPort/);}
  const output=path.join(f.root,'output');const result=generateProfileProject(prepared,output);if(shared.length)assert.ok(result.qualification.checked_files.includes('infrastructure/http-port.mjs'));
  const service=await import(pathToFileURL(path.join(output,'app/index.mjs')).href),oracle=JSON.parse(readFileSync(path.join(f.root,'oracle.json'),'utf8'));
  for(const c of oracle.cases){const response=await service.handler(new Request('https://test.invalid/'+c.intent,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(c.input)}),{DEPENDENCY_INVENTORY_URL:'https://inventory.invalid/stock'},{fetch:async()=>new Response(JSON.stringify(c.external))});const body=await response.json();if(c.expected_error)assert.equal(body.error,c.expected_error,name+':'+c.id);else assert.deepEqual(body,c.expected,name+':'+c.id);}
 }
});
