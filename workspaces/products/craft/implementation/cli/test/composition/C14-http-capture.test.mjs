import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {prepareGenericTransactionSources} from '../../src/generic/public-sdk.ts';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.ts';
import {createGenericHttpSourceContract} from '../../src/generic/entry-http-source.ts';
import {projectGenericHttpTransport} from '../../src/generic/http-projection.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const evidence=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence');
const domains=[
 {name:'CaseDesk',fixture:path.join(evidence,'C14/three-app-authoring-contract-001/casedesk'),ids:['CaseDeskHttp.Read','CaseDeskHttp.Resolve'],entries:['CaseDesk.ReadCaseEntry','CaseDesk.ResolveCaseEntry'],mappings:['CaseDesk.HttpCaseResponse','CaseDesk.HttpResolutionResponse']},
 {name:'Schedule',fixture:path.join(evidence,'C09/schedule-http-second-domain-source-001/fixture'),ids:['ScheduleHttp.ReadDay','ScheduleHttp.Reserve'],entries:['Schedule.ReadDayScheduleEntry','Schedule.ReserveBookingEntry'],mappings:['Schedule.HttpDayResponse','Schedule.HttpBookingResponse']},
];

function physicalBase(row,work){
 if(row.name==='Schedule')return {sourcePath:path.join(row.fixture,'business.alch'),profilePath:path.join(row.fixture,'contracts/selected-profile.json'),httpPath:path.join(row.fixture,'contracts/http-profile.json')};
 const root=path.join(work,'physical');mkdirSync(path.join(root,'contracts'),{recursive:true});
 writeFileSync(path.join(root,'business.alch'),readFileSync(path.join(row.fixture,'business.alch')));
 const profileText=readFileSync(path.join(row.fixture,'selected-profile.json'),'utf8'),profile=JSON.parse(profileText);
 writeFileSync(path.join(root,'contracts/selected-profile.json'),profileText);
 writeFileSync(path.join(root,'contracts/bounds.json'),JSON.stringify({schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits:profile.limits}},null,2)+'\n');
 writeFileSync(path.join(root,'contracts/transactions.json'),JSON.stringify(profile.transaction_bounds,null,2)+'\n');
 return {sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json'),httpPath:path.join(row.fixture,'http-profile.json')};
}

for(const row of domains)test(`C14 ${row.name} checked HTTP source binds both routes to protected Entries and response Mappings`,()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-http-source-')),physical=physicalBase(row,work),base=prepareGenericTransactionSources({sourcePath:physical.sourcePath,profilePath:physical.profilePath}),root=path.join(work,'captured');
 const owner=createCoreCommerceSourceOwner('atomic-state-entry');let capture;
 try{
  for(const file of base.sources.inspect(base.source).files){const destination=path.join(root,file.path);mkdirSync(path.dirname(destination),{recursive:true});writeFileSync(destination,file.path==='application.alch'?file.text+'  http-bindings contracts/http-profile.json\n':file.text);}
  writeFileSync(path.join(root,'contracts/http-profile.json'),readFileSync(physical.httpPath));
  capture=owner.prepare(root,'application.alch');
  const checked=createGenericHttpSourceContract(owner.inspect(capture));
  assert.deepEqual(checked.contract.entries.map(entry=>entry.route.id),row.ids);
  assert.deepEqual(checked.contract.entries.map(entry=>entry.route.method),['GET','POST']);
  assert.deepEqual(checked.contract.entries.map(entry=>entry.route.entry),row.entries);
  assert.deepEqual(checked.contract.entries.map(entry=>entry.route.response_mapping),row.mappings);
  assert.ok(checked.contract.entries.every(entry=>entry.entry_contract_sha256&&entry.response_mapping_sha256));
  assert.ok(checked.contract.entries.every(entry=>entry.profile_source.path==='contracts/http-profile.json'));
  const topology=projectGenericHttpTransport(checked.contract);
  assert.deepEqual(topology.nodes.filter(node=>node.kind==='injected-http-handler').map(node=>node.id),row.ids.map(id=>'http:'+id));
  assert.deepEqual(topology.edges.map(edge=>edge.to),row.entries.map(entry=>'entry:'+entry));
  assert.deepEqual(topology.bridge_links.map(link=>link.mapping),row.mappings);
 }finally{
  if(capture)owner.dispose(capture);
  base.semantics.dispose(base.semantic);base.sources.dispose(base.source);
  base.expandedSemantics.dispose(base.expandedSemantic);base.expandedSources.dispose(base.expanded);
  rmSync(work,{recursive:true,force:true});
 }
});

test('C14 checked HTTP source rejects a route set spanning services before generation',()=>{
 const row=domains[1],work=mkdtempSync(path.join(tmpdir(),'craft-c14-cross-service-')),physical=physicalBase(row,work),base=prepareGenericTransactionSources({sourcePath:physical.sourcePath,profilePath:physical.profilePath}),root=path.join(work,'captured');
 const owner=createCoreCommerceSourceOwner('atomic-state-entry');let capture;
 try{
  for(const file of base.sources.inspect(base.source).files){const destination=path.join(root,file.path);mkdirSync(path.dirname(destination),{recursive:true});writeFileSync(destination,file.path==='application.alch'?file.text+'  http-bindings contracts/http-profile.json\n':file.text);}
  const profile=JSON.parse(readFileSync(physical.httpPath,'utf8'));profile.routes[1].service='AnotherService';
  writeFileSync(path.join(root,'contracts/http-profile.json'),JSON.stringify(profile));
  capture=owner.prepare(root,'application.alch');
  assert.throws(()=>createGenericHttpSourceContract(owner.inspect(capture)),error=>error.diagnostics?.[0]?.code==='UnsupportedCapability');
 }finally{
  if(capture)owner.dispose(capture);
  base.semantics.dispose(base.semantic);base.sources.dispose(base.source);
  base.expandedSemantics.dispose(base.expandedSemantic);base.expandedSources.dispose(base.expanded);
  rmSync(work,{recursive:true,force:true});
 }
});

test('C14 declarative route change changes checked transport topology on the same business source',()=>{
 const row=domains[1],work=mkdtempSync(path.join(tmpdir(),'craft-c14-profile-change-')),physical=physicalBase(row,work),base=prepareGenericTransactionSources({sourcePath:physical.sourcePath,profilePath:physical.profilePath});
 const owner=createCoreCommerceSourceOwner('atomic-state-entry'),captures=[];
 try{
  const original=JSON.parse(readFileSync(physical.httpPath,'utf8')),checked=[];
  for(const [index,profile] of [original,{...original,routes:[{...original.routes[0],path:'/calendar/{dayId}'},original.routes[1]]}].entries()){
   const root=path.join(work,'captured-'+index);
   for(const file of base.sources.inspect(base.source).files){const destination=path.join(root,file.path);mkdirSync(path.dirname(destination),{recursive:true});writeFileSync(destination,file.path==='application.alch'?file.text+'  http-bindings contracts/http-profile.json\n':file.text);}
   writeFileSync(path.join(root,'contracts/http-profile.json'),JSON.stringify(profile));
   const capture=owner.prepare(root,'application.alch');captures.push(capture);
   const contract=createGenericHttpSourceContract(owner.inspect(capture));checked.push({contract,topology:projectGenericHttpTransport(contract.contract)});
  }
  assert.notEqual(checked[0].contract.transport_semantics_sha256,checked[1].contract.transport_semantics_sha256);
  assert.equal(checked[0].contract.base.derivation.executable_semantics_sha256,checked[1].contract.base.derivation.executable_semantics_sha256);
  assert.notDeepEqual(checked[0].topology.nodes.filter(node=>node.kind==='injected-http-handler'),checked[1].topology.nodes.filter(node=>node.kind==='injected-http-handler'));
 }finally{
  for(const capture of captures)owner.dispose(capture);
  base.semantics.dispose(base.semantic);base.sources.dispose(base.source);
  base.expandedSemantics.dispose(base.expandedSemantic);base.expandedSources.dispose(base.expanded);
  rmSync(work,{recursive:true,force:true});
 }
});
