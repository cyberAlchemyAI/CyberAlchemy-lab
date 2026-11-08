import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {createBusinessApplicationFixture} from '../helpers/business-profile.ts';
import {prepareProfileProject,planProfileProject,disposeProfileProject} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-engine.js';
// Open questions: final frozen/installed replay BA15/18. No real providers or publication.
test('public v2 preparation rejects missing shared dependency and source-selected route collisions',async t=>{
 for(const mode of ['missing-port','route-collision']){
  const f=createBusinessApplicationFixture(t,'node-http-shared-ports-v2',true),profile=path.join(f.root,'profile');const {cpSync}=await import('node:fs');cpSync(f.project.profiles[0].path,profile,{recursive:true});f.project.profiles[0].path='profile';writeFileSync(f.file,JSON.stringify(f.project));const file=path.join(profile,'profile.json'),pkg=JSON.parse(readFileSync(file,'utf8'));
  if(mode==='missing-port')pkg.rules=pkg.rules.filter((r:any)=>r.id!=='shared-transport');else pkg.rules.find((r:any)=>r.role==='application-operation').fields.route={literal:'/same'};writeFileSync(file,JSON.stringify(pkg));
  await assert.rejects(()=>prepareProfileProject(f.file),mode==='missing-port'?/SHARED_PORT_REQUIRED/:/ROUTE_CONFLICT/);
 }
});
test('public plan cannot claim currentness after authored source changes',async t=>{
 const f=createBusinessApplicationFixture(t,'node-http-entry-local-v2'),prepared=await prepareProfileProject(f.file);t.after(()=>disposeProfileProject(prepared));const source=path.join(f.root,'domain.alch'),before=readFileSync(source,'utf8');writeFileSync(source,before+'\n');assert.throws(()=>planProfileProject(prepared),/STALE/);writeFileSync(source,before);
 assert.equal(planProfileProject(prepared).composition.components.filter((c:any)=>c.role==='application-operation').length,1);
});
