import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createGenericCompositionOwner,createGenericBundledApplicationOwner} from '../../src/generic/public-sdk.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const evidence=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence');
const caseDesk=path.join(evidence,'C14/three-app-authoring-contract-001/casedesk');
const schedule=path.join(evidence,'C09/schedule-http-second-domain-source-001/fixture');
const cases=[
 {name:'CaseDesk',source:caseDesk,entry:'CaseDesk.ResolveCaseEntry',read:'CaseDesk.ReadCaseEntry',operation:'CaseDesk.ResolveCase',entity:'CaseDesk.CaseFile',rule:'CaseDesk.MayResolve',service:'CaseDeskService'},
 {name:'Schedule',source:schedule,entry:'Schedule.ReserveBookingEntry',read:'Schedule.ReadDayScheduleEntry',operation:'Schedule.ReserveBooking',entity:'Schedule.DaySchedule',rule:'Schedule.NoOverlap',service:'ScheduleService'},
];

function physicalClosure(row,work){
 const root=path.join(work,'authored');mkdirSync(path.join(root,'contracts'),{recursive:true});
 if(row.name==='Schedule'){cpSync(row.source,root,{recursive:true});return root;}
 writeFileSync(path.join(root,'business.alch'),readFileSync(path.join(row.source,'business.alch')));
 const profileText=readFileSync(path.join(row.source,'selected-profile.json'),'utf8');
 writeFileSync(path.join(root,'contracts/selected-profile.json'),profileText);
 const profile=JSON.parse(profileText);
 writeFileSync(path.join(root,'contracts/bounds.json'),JSON.stringify({schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits:profile.limits}},null,2)+'\n');
 writeFileSync(path.join(root,'contracts/transactions.json'),JSON.stringify(profile.transaction_bounds,null,2)+'\n');
 return root;
}
function accept(owner,handle,label,decisionPath){const review=owner.review(handle,label);owner.accept(handle,{decision_id:label,owner:label,outcome:'accepted',reviewed_digest:review.review_sha256},decisionPath);}

for(const row of cases)test(`C14 ${row.name} independent business source reaches a fresh generated owner with real graph and bridge links`,async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-domain-')),root=physicalClosure(row,work),owner=createGenericCompositionOwner();let handle,generated,generatedHandle;
 try{
  handle=await owner.prepare({sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json')});
  const source=owner.inspect(handle),logical=source.logical;
  for(const business of [row.read,row.entry,row.operation,row.entity,row.rule])assert.ok(logical.nodes.some(n=>n.id===business),`${row.name}: checked business node ${business}`);
  assert.ok(source.transaction_contract.entries.some(e=>e.entry===row.entry));
  accept(owner,handle,`C14-${row.name}-source`,path.join(work,'source-decision.json'));
  const output=path.join(work,'generated'),manifest=owner.generate(handle,{entry:row.entry,outputDirectory:output});
  const system=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8'));
  const bridge=JSON.parse(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'));
  assert.ok(system.nodes.some(n=>n.id==='operation:'+row.operation&&n.kind==='stateful-operation-assembly'));
  assert.ok(system.nodes.some(n=>n.id==='storage:'+row.service&&n.kind==='sqlite-atomic-command-store'));
  assert.ok(bridge.links.some(l=>l.business===row.operation&&l.system==='operation:'+row.operation));
  assert.ok(bridge.links.some(l=>l.business===row.entry&&l.system==='generated:'+row.entry));
  assert.ok(manifest.files.some(f=>f.path==='application.mjs'));
  const modulePath=path.join(output,'application.mjs'),bundle=JSON.parse(readFileSync(modulePath,'utf8').split('const bundle=')[1].split(';\nexport function')[0]);
  generated=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle);generatedHandle=await generated.prepare();
  const fresh=generated.inspect(generatedHandle);assert.equal(fresh.transaction_contract.application_namespace,source.transaction_contract.application_namespace);
  assert.ok(fresh.transaction_contract.entries.some(e=>e.entry===row.read));
  accept(generated,generatedHandle,`C14-${row.name}-generated`,path.join(work,'generated-decision.json'));
  generated.assertCurrent(generatedHandle);
 }finally{if(generatedHandle)try{generated.dispose(generatedHandle);}catch{}if(handle)try{owner.dispose(handle);}catch{}rmSync(work,{recursive:true,force:true});}
});
