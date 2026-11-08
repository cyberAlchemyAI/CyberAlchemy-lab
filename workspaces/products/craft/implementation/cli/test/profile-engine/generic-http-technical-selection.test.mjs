import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {createGenericHttpTechnicalSelectionOwner} from '../../src/profile-engine/generic-http-technical-selection.ts';
import {createGenericHttpCompositionOwner} from '../../src/generic/public-sdk.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const evidence=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence');
const technical=path.join(evidence,'C14/technical-http-v2-source-001');
const cases=[
  {name:'CaseDesk',root:path.join(evidence,'C14/three-app-authoring-contract-001/casedesk'),entry:'CaseDesk.ResolveCaseEntry',route:'CaseDeskHttp.Resolve'},
  {name:'Schedule',root:path.join(evidence,'C09/schedule-http-second-domain-source-001/fixture'),entry:'Schedule.ReserveBookingEntry',route:'ScheduleHttp.Reserve'},
];
const sha=(value)=>createHash('sha256').update(value).digest('hex');
function copyBusiness(row,root){
  mkdirSync(path.join(root,'contracts'),{recursive:true});
  const source=readFileSync(path.join(row.root,'business.alch'));
  writeFileSync(path.join(root,'business.alch'),source);
  const profilePath=row.name==='CaseDesk'?path.join(row.root,'selected-profile.json'):path.join(row.root,'contracts/selected-profile.json');
  const profileText=readFileSync(profilePath),profile=JSON.parse(profileText);
  writeFileSync(path.join(root,'contracts/selected-profile.json'),profileText);
  if(row.name==='CaseDesk'){
    writeFileSync(path.join(root,'contracts/bounds.json'),JSON.stringify({schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits:profile.limits}}));
    writeFileSync(path.join(root,'contracts/transactions.json'),JSON.stringify(profile.transaction_bounds));
  }else for(const name of ['bounds.json','transactions.json'])writeFileSync(path.join(root,'contracts',name),readFileSync(path.join(row.root,'contracts',name)));
  return {sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json'),httpProfilePath:path.join(root,'contracts/http-profile.json'),businessSha:sha(source),baseHttpProfilePath:row.name==='CaseDesk'?path.join(row.root,'http-profile.json'):path.join(row.root,'contracts/http-profile.json')};
}

for(const row of cases)test(`C14 ${row.name} selected technical Mapping changes the emitted HTTP route with unchanged business bytes`,async()=>{
  const work=mkdtempSync(path.join(tmpdir(),'craft-c14-technical-http-')),appRoot=path.join(work,'app');
  const technicalOwner=createGenericHttpTechnicalSelectionOwner(),httpOwner=createGenericHttpCompositionOwner();
  let technicalHandle,httpHandle;
  try{
    const input=copyBusiness(row,appRoot);
    assert.equal(JSON.parse(readFileSync(input.baseHttpProfilePath,'utf8')).route_prefix,'/api');
    technicalHandle=technicalOwner.prepare({technicalRoot:technical,selectionPath:path.join(technical,'selection.json'),baseHttpProfilePath:input.baseHttpProfilePath,outputHttpProfilePath:input.httpProfilePath});
    const derivation=technicalOwner.inspect(technicalHandle);
    assert.equal(derivation.mapping,'Craft.HttpTechnical.SelectHttp');
    assert.equal(derivation.route_family,'ApiV2');
    assert.equal(derivation.route_prefix,'/api/v2');
    assert.equal(derivation.technical_mapping_source.artifact.sha256,sha(readFileSync(path.join(technical,'source/profile.alch'))));
    assert.match(derivation.adapter_code_epoch_sha256,/^[0-9a-f]{64}$/);
    assert.equal(derivation.derived_http_profile_file.sha256,sha(readFileSync(input.httpProfilePath)));
    assert.equal(sha(readFileSync(input.sourcePath)),input.businessSha);
    httpHandle=await httpOwner.prepare({sourcePath:input.sourcePath,profilePath:input.profilePath,httpProfilePath:input.httpProfilePath});
    const inspection=httpOwner.inspect(httpHandle);
    const route=inspection.http_contract.entries.find(entry=>entry.route.id===row.route);
    assert.ok(route);
    assert.equal(inspection.http_contract.profile.route_prefix,'/api/v2');
    assert.equal(inspection.http_profile.sha256,derivation.derived_http_profile_file.sha256);
    assert.ok(inspection.source.original_files.some(file=>file.role==='primary-source'&&file.original.sha256===input.businessSha));
    const review=httpOwner.review(httpHandle,`C14-${row.name}-technical-http`);
    httpOwner.accept(httpHandle,{decision_id:`C14-${row.name}-technical-http`,owner:`C14-${row.name}-technical-http`,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'decision.json'));
    const output=path.join(work,'generated');
    const lineage=technicalOwner.generateJoined(technicalHandle,httpOwner,httpHandle,{entry:row.entry,outputDirectory:output});
    assert.equal(lineage.mapping_source.artifact.sha256,derivation.technical_mapping_source.artifact.sha256);
    assert.equal(lineage.derived_http_profile_file.sha256,derivation.derived_http_profile_file.sha256);
    assert.deepEqual(lineage.generated_files.map(file=>file.name),['http-plan.json','system-graph.json','business-system-bridge.json']);
    const manifest=JSON.parse(readFileSync(path.join(output,'manifest.json'),'utf8'));
    const graph=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8'));
    const bridge=JSON.parse(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'));
    const plan=JSON.parse(readFileSync(path.join(output,'http-plan.json'),'utf8'));
    assert.equal(plan.contract.profile.route_prefix,'/api/v2');
    assert.equal(lineage.transport_semantics_sha256,plan.transport_semantics_sha256);
    assert.ok(graph.nodes.some(node=>node.kind==='injected-http-handler'&&node.route.id===row.route&&node.transport_semantics_sha256===inspection.transport_semantics_sha256));
    assert.ok(bridge.links.some(link=>link.transport_semantics_sha256===inspection.transport_semantics_sha256));
    assert.equal(manifest.http_profile.sha256,derivation.derived_http_profile_file.sha256);
    assert.equal(sha(readFileSync(input.sourcePath)),input.businessSha);
    technicalOwner.assertCurrent(technicalHandle);
  }finally{if(httpHandle)try{httpOwner.dispose(httpHandle);}catch{}if(technicalHandle)try{technicalOwner.dispose(technicalHandle);}catch{}rmSync(work,{recursive:true,force:true});}
});

test('C14 technical selection rejects an unknown native slot before derived HTTP output',()=>{
  const work=mkdtempSync(path.join(tmpdir(),'craft-c14-technical-negative-')),selection=path.join(work,'selection.json'),output=path.join(work,'contracts/http-profile.json');
  const owner=createGenericHttpTechnicalSelectionOwner();
  try{
    mkdirSync(path.dirname(output));
    const invalid=JSON.parse(readFileSync(path.join(technical,'selection.json'),'utf8'));
    invalid.slot='arbitrary-node-callback';
    writeFileSync(selection,JSON.stringify(invalid));
    assert.throws(()=>owner.prepare({technicalRoot:technical,selectionPath:selection,baseHttpProfilePath:path.join(cases[0].root,'http-profile.json'),outputHttpProfilePath:output}));
    assert.throws(()=>readFileSync(output));
  }finally{rmSync(work,{recursive:true,force:true});}
});

test('C14 technical selection rejects an unknown route family before derived HTTP output',()=>{
  const work=mkdtempSync(path.join(tmpdir(),'craft-c14-technical-family-negative-')),selection=path.join(work,'selection.json'),output=path.join(work,'contracts/http-profile.json');
  const owner=createGenericHttpTechnicalSelectionOwner();
  try{
    mkdirSync(path.dirname(output));
    const invalid=JSON.parse(readFileSync(path.join(technical,'selection.json'),'utf8'));
    invalid.parameters.options.routeFamily='AnyFramework';
    writeFileSync(selection,JSON.stringify(invalid));
    assert.throws(()=>owner.prepare({technicalRoot:technical,selectionPath:selection,baseHttpProfilePath:path.join(cases[0].root,'http-profile.json'),outputHttpProfilePath:output}));
    assert.throws(()=>readFileSync(output));
  }finally{rmSync(work,{recursive:true,force:true});}
});

test('C14 technical selection rejects a changed authored selection after derivation',()=>{
  const work=mkdtempSync(path.join(tmpdir(),'craft-c14-technical-stale-')),selection=path.join(work,'selection.json'),output=path.join(work,'contracts/http-profile.json');
  const owner=createGenericHttpTechnicalSelectionOwner();
  try{
    mkdirSync(path.dirname(output));
    const original=readFileSync(path.join(technical,'selection.json'),'utf8');
    writeFileSync(selection,original);
    const handle=owner.prepare({technicalRoot:technical,selectionPath:selection,baseHttpProfilePath:path.join(cases[0].root,'http-profile.json'),outputHttpProfilePath:output});
    assert.equal(owner.inspect(handle).route_prefix,'/api/v2');
    writeFileSync(selection,original+'\n');
    assert.throws(()=>owner.assertCurrent(handle),error=>error.diagnostics?.[0]?.code==='StaleOwner');
  }finally{rmSync(work,{recursive:true,force:true});}
});
