import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {loadCompiledProjectGraph,evaluateCompiledObligationWitness,validateCompiledProjectGraphObligations} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate,createCompiledSemanticGraph} from '../../src/compilation/certificate.ts';
import {createMetaTypeFormalizationProjection,materializeLeanMetaTypeFormalization} from '../../src/formalization/projection.ts';
import {FORMALIZATION_LEAN_MODULE_FILENAMES} from '../../src/formalization/kernel.ts';
import {createCheckedInterchange} from '../../src/assurance/checked-interchange.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
import {relationshipEvidenceId} from '../../src/input/relationship-identity.ts';
const fixture=path.resolve(import.meta.dirname,'../../fixtures/input-roots/canonical-project');
function colliding(t:any){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-owned-edge-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));fs.cpSync(fixture,root,{recursive:true});
 const rename=(owner:string|null,prior:string)=>{
  const folder=owner?'specs/'+owner+'/':'',manifest=path.join(root,owner?folder+'feature.json':'project.json'),key=owner?'edges':'cross_feature_edges';
  const document=JSON.parse(fs.readFileSync(manifest,'utf8'));document[key]=document[key].map((v:string)=>v===prior?'shared':v);fs.writeFileSync(manifest,JSON.stringify(document));
  const previous=path.join(root,folder+'edges/'+prior+'.json'),edge=JSON.parse(fs.readFileSync(previous,'utf8'));edge.edge_id='shared';fs.writeFileSync(path.join(root,folder+'edges/shared.json'),JSON.stringify(edge));fs.unlinkSync(previous);
 };
 rename('alpha','customer-performs-settle');rename('beta','audit-owns-settled');rename(null,'alpha-to-beta');
 return root;
}
test('unambiguous graph identities retain deterministic certificates under the Value Object maps authority',()=>{
 const graph=loadCompiledProjectGraph(fixture);
 for(const edge of graph.relationships)assert.equal(relationshipEvidenceId(structuredClone(edge),graph.relationships),edge.edge_id);
 // Successor expectations bind the owner-approved maps target extension, not the historical authority.
 const expected={"certificate":"d7e0d1c028ec9c90d03054ae2364f4cc6bf48943ab6f3a9b44fc84af5db8c001","projection":"194adf0c85c461bd3f1fd49353e8f94157d79f04cc33f8f66b790ea6920fbf28","semantic":"18d573e937c3f09a238954500c38a13fa0ca4eb16c34101a97ae857c5afed2e5"};
 assert.equal(sha256(canonicalJson(createCompiledProjectCertificate(graph))),expected.certificate);
 assert.equal(sha256(canonicalJson(createCompiledSemanticGraph(graph))),expected.semantic);
 assert.equal(sha256(canonicalJson(createMetaTypeFormalizationProjection(graph))),expected.projection);
});
test('feature and project edges with the same local ID retain all witnesses and finite references',t=>{
 const graph=loadCompiledProjectGraph(colliding(t));validateCompiledProjectGraphObligations(graph);
 for(const edge of graph.relationships)assert.equal(relationshipEvidenceId(structuredClone(edge),graph.relationships),relationshipEvidenceId(edge,graph.relationships));
 const witnesses=graph.obligation_witnesses.filter(w=>w.edge_id==='shared');
 assert.ok(witnesses.length>3);assert.equal(new Set(graph.obligation_witnesses.map(w=>w.witness_id)).size,graph.obligation_witnesses.length);
 assert.deepEqual([...new Set(witnesses.map(w=>w.witness_id.split(':').slice(0,-1).join(':')))].sort(),['feature:alpha:shared','feature:beta:shared','project:shared']);
 for(const w of witnesses){
  assert.equal(evaluateCompiledObligationWitness(graph,w).outcome,'pass');
  assert.deepEqual(evaluateCompiledObligationWitness({...graph,relationships:[...graph.relationships].reverse()},w),evaluateCompiledObligationWitness(graph,w));
 }
 const projection=createMetaTypeFormalizationProjection(graph);
 const edges=projection.project_graph.edges,w=projection.render_payload.applicable_witnesses;
 assert.equal(new Set(edges.map(e=>e.edge_id)).size,edges.length);
 assert.equal(new Set(w.map(x=>x.witness_id)).size,w.length);
 assert.deepEqual(w.map(x=>x.witness_id).sort(),graph.obligation_witnesses.map(x=>x.witness_id).sort());
 for(const x of w)assert.equal(edges.filter(e=>e.edge_id===x.edge_id).length,1);
 assert.equal(projection.render_payload.graph_certificate.denominators.witness_count,graph.obligation_witnesses.length);
});
test('qualified lookup keeps hostile endpoint, predicate, ID, missing and ambiguous-edge checks',t=>{
 const graph=loadCompiledProjectGraph(colliding(t)),w=graph.obligation_witnesses.find(w=>w.witness_id.startsWith('feature:alpha:shared:'))!;
 for(const change of [
  (v:any)=>v.witness_id='shared:'+v.obligation_id,
  (v:any)=>v.witness.target_selector='beta:missing',
  (v:any)=>v.witness.source_selector='beta:customer',
  (v:any)=>v.witness.scope='project',
  (v:any)=>v.predicate.relationship_id='owns'
 ]){const altered=structuredClone(w);change(altered);assert.throws(()=>evaluateCompiledObligationWitness(graph,altered),/MTCLI|witness|edge|predicate|obligation/);}
 const edge=graph.relationships.find(e=>e.edge_id==='shared'&&e.scope==='feature'&&e.source.feature_id==='alpha')!;
 assert.throws(()=>evaluateCompiledObligationWitness({...graph,relationships:graph.relationships.filter(e=>e!==edge)},w),/edge|witness/);
 assert.throws(()=>evaluateCompiledObligationWitness({...graph,relationships:[...graph.relationships,edge]},w),/edge|witness/);
 assert.throws(()=>validateCompiledProjectGraphObligations({...graph,obligation_witnesses:graph.obligation_witnesses.filter(x=>x!==w)}),/omitted or changed/);
});
test('the Lean kernel checks the distinct owned-edge witnesses in the generated finite projection',t=>{
 const graph=loadCompiledProjectGraph(colliding(t)),parent=fs.mkdtempSync(path.join(os.tmpdir(),'ds-owned-edge-proof-'));
 t.after(()=>fs.rmSync(parent,{recursive:true,force:true}));
 const target=path.join(parent,'proof','Current.lean'),lean=process.env.DOMAINSPEC_LEAN??'lean';
 const version=spawnSync(lean,['--version'],{encoding:'utf8',timeout:10000});assert.equal(version.status,0,String(version.error??'')+version.stderr);assert.match(version.stdout,/version 4\.33\.1/);
 materializeLeanMetaTypeFormalization(graph,target);
 for(const file of [...FORMALIZATION_LEAN_MODULE_FILENAMES,'Current.lean']){
  const args=file==='Current.lean'?[file]:['-o',file.replace(/\.lean$/,'.olean'),file];
  const r=spawnSync(lean,args,{cwd:path.dirname(target),encoding:'utf8',env:{...process.env,LEAN_PATH:'.'},timeout:60000,maxBuffer:32*1024*1024});
  assert.equal(r.status,0,String(r.error??'')+r.stdout+r.stderr);
 }
 const decoder='DomainSpecCheckedInterchangeDecoder.lean',input=path.join(parent,'interchange.json');
 fs.copyFileSync(path.resolve(import.meta.dirname,'../../lean',decoder),path.join(path.dirname(target),decoder));
 const interchange=createCheckedInterchange(graph);
 const decode=(value:unknown)=>{
  fs.writeFileSync(input,canonicalJson(value)+'\n');
  return spawnSync(lean,['--run',decoder,input],{cwd:path.dirname(target),encoding:'utf8',env:{...process.env,LEAN_PATH:'.'},timeout:60000,maxBuffer:32*1024*1024});
 };
 const valid=decode(interchange);assert.equal(valid.status,0,String(valid.error??'')+valid.stdout+valid.stderr);assert.ok(valid.stdout.startsWith('pass\t'));
 const hostile:any=structuredClone(interchange);
 const w=hostile.compiled_graph.obligation_witnesses.find((w:any)=>w.witness_id.startsWith('feature:alpha:shared:'));
 w.witness.source_selector='beta:customer';
 hostile.compiled_certificate.obligation_witnesses=structuredClone(hostile.compiled_graph.obligation_witnesses);
 hostile.compiled_certificate.graph_sha256=sha256(canonicalJson(hostile.compiled_graph));
 const {certificate_sha256,...certificate}=hostile.compiled_certificate;hostile.compiled_certificate.certificate_sha256=sha256(canonicalJson(certificate));
 const {interchange_sha256,...body}=hostile;hostile.interchange_sha256=sha256(canonicalJson(body));
 const invalid=decode(hostile);assert.notEqual(invalid.status,0);assert.match(invalid.stdout+invalid.stderr,/detailed-witness:/);
});
