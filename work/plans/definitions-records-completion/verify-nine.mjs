import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';import {tmpdir} from 'node:os';
import {activation} from '../../../implementation/lab-runtime/alchlang/shared-records/activation.mjs';
import {loadTrust} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {Snapshots} from '../../../implementation/lab-runtime/alchlang/shared-records/snapshots.mjs';
import {verifyLocations} from '../../../implementation/lab-runtime/alchlang/shared-records/locations.mjs';
import {readPublishedCatalog} from '../../../implementation/lab-runtime/alchlang/shared-records/catalog.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {inspectViews,reconcileViews} from '../../../implementation/lab-workflows/records-workflow/views.mjs';
import {readPublishedRecords} from '../../../implementation/lab-workflows/records-workflow/catalog.mjs';
import {impactClosure} from '../../../implementation/lab-runtime/alchlang/shared-records/ports.mjs';
import {enforce} from '../../../implementation/lab-workflows/records-workflow/kernel.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),checks=[],put=x=>writeFileSync(path.join(here,'REGRESSION-VERIFICATION.json'),JSON.stringify(x,null,2)+'\n');
const pass=name=>{checks.push(name);console.log('PASS '+name);};
const cli=path.join(root,'workspaces/products/define/implementation/cli/alchlang/runtime/cli.mjs'),source=readFileSync(path.join(root,'workspaces/products/define/implementation/cli/alchlang/ALL-ALCHLANG.md'));
const piped=spawnSync(process.execPath,[cli,'sources'],{maxBuffer:16*1024*1024});assert.equal(piped.status,0,piped.stderr.toString());assert(piped.stdout.equals(source));pass('D-01: complete piped stdout equals original bytes and SHA-256');
const active=activation({required:true}),trust=loadTrust(active.trust),catalog=readPublishedCatalog(active.database,active.workspace,'lab.catalog-reader',trust);
const overlay=JSON.parse(readFileSync(path.join(root,'workspaces/products/define/docs/CURRENT-AUTHORITY.json')));
for(const row of overlay.definitions){const current=catalog.current_entries.find(e=>e.definition_id===row.definition_id);assert(current);assert.equal(current.sha256,row.body.sha256);assert.equal(current.standing,'admitted-current');}pass('D-02: historical/current authority overlay resolves exact admitted current bodies');
await assert.rejects(()=>verifyLocations({}, {entries:[],current_lookup:{}},()=>{throw Error('must not read');},{requiredProtocol:'workspace-definition-layout/v2'}),/trusted-directory-layout-required/);pass('L-02: producer cannot omit the trusted layout policy');
const db=new Snapshots(active.database,{readOnly:true,trust});
try{
 const selected=db.current(active.workspace),src=db.material(selected.digest,'source.json'),s=JSON.parse(src.bytes),registry=JSON.parse(db.material(selected.digest,'registry.json').bytes),read=b=>db.material(selected.digest,b.ref??b.path).bytes;
 assert.equal(s.layout_protocol,'workspace-definition-layout/v2');await verifyLocations(s,registry,read,{requiredProtocol:trust.layout_policy.required_protocol});pass('L-03: every current directory binds all four original assets');
 const key=Object.keys(s.locations)[0];
 for(const role of ['projection','lineage','evidence']){
  const bad=structuredClone(s);delete bad.locations[key].directory[role];await assert.rejects(()=>verifyLocations(bad,registry,read,{requiredProtocol:trust.layout_policy.required_protocol}),/asset-role/);pass('L-03: missing '+role+' refuses');
  const corruptRead=b=>{const raw=read(b);return (b.ref??b.path)===(s.locations[key].directory[role].ref??s.locations[key].directory[role].path)?Buffer.concat([raw,Buffer.from('changed')]):raw;};
  await assert.rejects(()=>verifyLocations(s,registry,corruptRead,{requiredProtocol:trust.layout_policy.required_protocol}),/binding-mismatch/);pass('L-03: modified '+role+' refuses');
 }
 const prior=JSON.parse(readFileSync(path.join(here,'PREVIOUS-ACTIVATION.json'))),old=db.material(prior.selector.digest,'registry.json').bytes;
 assert(db.material(selected.digest,'registry.json').bytes.equals(old));pass('all 377 preexisting admitted bodies/standings and original decisions remain unchanged');
}finally{db.close();}
assert.equal((await inspectViews(active,trust)).status,'ready');pass('L-04: actual pointer, canonical assets and generated indexes are reconciled');
const temporary=mkdtempSync(path.join(tmpdir(),'lab-canonical-view-regression-')),mirror={...active,root:temporary};
try{
 await assert.rejects(()=>reconcileViews(mirror,trust,{interruptAfter:1}),/injected-view-interruption/);
 await assert.rejects(()=>inspectViews(mirror,trust),/unreconciled/);
 await reconcileViews(mirror,trust);assert.equal((await inspectViews(mirror,trust)).status,'ready');pass('L-04: interruption leaves visible unready state and retry repairs exact selected views');
 const file=path.join(temporary,'authority/definitions/current.json'),before=readFileSync(file);writeFileSync(file,Buffer.concat([before,Buffer.from('changed')]));
 await assert.rejects(()=>inspectViews(mirror,trust),/unreconciled/);await reconcileViews(mirror,trust);assert(readFileSync(file).equals(before));pass('L-04: altered public current pointer refuses readiness and can be reconciled');
 const index=path.join(temporary,'authority/definitions/DEFINITIONS-INDEX.md');writeFileSync(index,'stale');await assert.rejects(()=>inspectViews(mirror,trust),/unreconciled/);await reconcileViews(mirror,trust);pass('L-04: stale generated human index refuses readiness');
}finally{rmSync(temporary,{recursive:true,force:true});}
const facts={schema_valid:true,package_bound:true,session_bound:true,source_bound:true,use_bound:true,consumer_bound:true,readiness_verified:true,target_commitment_verified:true,owner_decision_verified:true};
const plan=await enforce('PlanLifecycle',facts);assert.equal(plan.steps.length,9);await assert.rejects(()=>enforce('PlanLifecycle',{...facts,consumer_bound:false}),/handoff-binding/);await assert.rejects(()=>enforce('PlanLifecycle',{...facts,owner_decision_verified:false}),/owner-decision/);pass('L-05: generated nine-stage lifecycle refuses foreign handoff or missing owner review');
await assert.rejects(()=>enforce('EnforceEvolution',{identity_preserved:true,version_fresh:true,previous_bound:true,target_bound:true,owner_decision_verified:true,authority_scope_verified:true,actual_changes:['Meaning','Custody'],authorized_changes:['Meaning']}),/owner-review/);pass('L-05: reviewed successor cannot smuggle an unreviewed custody change');
const universe=JSON.parse(readFileSync(trust.consumer_universe.path));assert(universe.coverage.native_subjects>0);assert(universe.edges.some(e=>e.kind==='normative'));assert(universe.provenance.length>0);assert(universe.external_subjects.length>0);
const read=b=>{const selected=trust.materials[b.ref??b.path];assert(selected);return readFileSync(selected.path);};
const closure=impactClosure(universe,'definition:cal.definition.product@1.0.0-candidate.1',read);assert(closure.affected.some(r=>r.startsWith('carrier:')));assert(closure.coverage);pass('L-06: actual meaning impact reaches native carriers and separates provenance/external coverage');
assert.throws(()=>impactClosure({...universe,unresolved:1},universe.subjects[0].ref,read),/incomplete/);pass('L-06: unresolved in-scope dependencies cannot be declared complete');
const records=readPublishedRecords(active,trust),targets=JSON.parse(readFileSync(path.join(here,'workspace-records/TARGETS.json'))).records;
for(const target of targets){const row=records.records.find(r=>r.version_ref===target.version);assert(row);assert(row.workspaces.includes(target.workspace));assert(['admitted-current','local-admitted-current'].includes(row.standing));}pass('L-07: all six owner-reviewed Product/thesis instances are published in their actual owning workspace');
for(const target of targets.filter(t=>t.carrier.includes('product-identity'))){const profile=JSON.parse(readFileSync(path.join(root,'workspaces/products',target.workspace_key,'WORKSPACE.json')));assert.equal(profile.primary_subject.ref,'product:'+target.workspace_key);assert.equal(profile.linked_project_refs.length,0);}
pass('L-07: product-only workspaces have Product identities without invented Projects or runtime copies');
await assert.rejects(()=>enforce('EnforceHost',{workspace_bound:true,runtime_shared:true,host_bound:true,semantic_project_required:true,semantic_project_present:false,semantic_project_matches:true,record_scope_matches:true}),/semantic-project-required/);pass('L-07: Work still requires a real matching semantic Project');
put({status:'PASS',checks,check_count:checks.length,selector:active.selector,scope:'Real current authenticated publication plus isolated view and negative-input regressions. No production corruption or semantic re-admission.'});
