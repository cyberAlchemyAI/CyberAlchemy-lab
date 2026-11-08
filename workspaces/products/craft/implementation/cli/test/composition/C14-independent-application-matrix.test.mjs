/** Input-boundary check for the three independent C14 application replays.
 * This does not claim that generation, runtime, or installed archives passed.
 * Open Questions: goals/plans/craft-alchlang-generic-applications-2026-10-18-r5/BUILD-MODE.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const evidence=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence');
const applications=Object.freeze([
 {name:'CaseDesk',root:path.join(evidence,'C14/three-app-authoring-contract-001/casedesk'),
  business:'business.alch',profile:'selected-profile.json',module:'CaseDesk',operation:'ResolveCase'},
 {name:'Schedule',root:path.join(evidence,'C09/schedule-http-second-domain-source-001/fixture'),
  business:'business.alch',profile:'contracts/selected-profile.json',module:'Schedule',operation:'ReserveBooking'},
 {name:'Commerce',root:path.join(repository,'examples/ecommerce-target-candidate'),
  business:'application.alch',profile:'profiles/implementation.alch',module:'Shop.Application',operation:null},
]);
const hash=value=>createHash('sha256').update(value).digest('hex');

test('C14 three application proofs start from distinct business and profile inputs',()=>{
 const roots=new Set(),business=new Set(),profiles=new Set();
 for(const application of applications){
  const root=realpathSync(application.root),businessPath=realpathSync(path.join(root,application.business)),
   profilePath=realpathSync(path.join(root,application.profile));
  assert.equal(roots.has(root),false,`${application.name}: independent source root required`);
  roots.add(root);
  const text=readFileSync(businessPath,'utf8'),profile=readFileSync(profilePath);
  assert.match(text,new RegExp(`^module ${application.module.replace('.',String.raw`\.`)} version 1$`,'m'));
  if(application.operation)assert.match(text,new RegExp(`^operation ${application.operation}:$`,'m'));
  business.add(hash(text));profiles.add(hash(profile));
 }
 assert.equal(roots.size,3);
 assert.equal(business.size,3,'separate business inputs required');
 assert.equal(profiles.size,3,'separate implementation profiles required');
});

test('C14 Commerce boundary is the original five-service composition, not a reduced fixture',()=>{
 const root=applications[2].root,application=readFileSync(path.join(root,'application.alch'),'utf8');
 const services=[...application.matchAll(/^  service ([a-z]+) module ([A-Z][A-Za-z0-9]*)$/gm)]
  .map(match=>({id:match[1],module:match[2]}));
 assert.deepEqual(services,[
  {id:'catalog',module:'Catalog'},{id:'orders',module:'Orders'},
  {id:'inventory',module:'Inventory'},{id:'payments',module:'Payments'},
  {id:'fulfillment',module:'Fulfillment'},
 ]);
 for(const service of services){
  assert.match(application,new RegExp(`^  source services/${service.id}\\.alch$`,'m'));
  assert.match(readFileSync(path.join(root,'services',service.id+'.alch'),'utf8'),
   new RegExp(`^module ${service.module} version 1$`,'m'));
 }
 const profile=readFileSync(path.join(root,'profiles/implementation.alch'),'utf8');
 assert.match(profile,/^  field messaging <- SelectedFamily\.EventInboxOutbox$/m);
 assert.match(readFileSync(path.join(root,'contracts/access.alch'),'utf8'),
  /^entry Fulfillment\.OnOrderConfirmed:$/m);
});
