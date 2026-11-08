import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, {type TestContext} from 'node:test';
import {decodeWorkflowOccurrences, workflowOperationRefs, WORKFLOW_OCCURRENCE_DEFINITION_SHA256} from '../../src/typed-backend/workflow-occurrences.ts';
import {decodeBody, loadCompiledProjectGraph, selectCompiledProjectNode} from '../../src/input/project-model.ts';
import {planWorkflowOccurrenceMigration} from '../../src/input/workflow-migration.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {planInstantiation} from '../../src/generation/plan-instantiation.ts';
import {createMetaTypeFormalizationProjection} from '../../src/formalization/projection.ts';
import {runInMemoryProject} from '../../src/runtime/in-memory.ts';
import {runCli} from '../../src/cli/main.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';

const project = path.resolve(import.meta.dirname, '../../../..');
const contract = (): any => ({schema_version:'domainspec.workflow-occurrences/v1',ontology_workflow:'TEST-SETTLEMENT-WORKFLOW',
  steps:[{step_id:'primary',operation_ref:'alpha:settle'},{step_id:'secondary',operation_ref:'alpha:settle'},{step_id:'other-feature',operation_ref:'beta:settle'}],
  compensations:[{compensation_id:'undo-primary',for_step:'primary',operation_ref:'alpha:reverse',depends_on:['undo-secondary']},
    {compensation_id:'undo-secondary',for_step:'secondary',operation_ref:'alpha:reverse',depends_on:[]}]});
function fixture(t: TestContext, body: any = {description:'Occurrence workflow.',typed_contract:contract()}) {
  const folder=fs.mkdtempSync(path.join(os.tmpdir(),'ds-workflow-occurrences-'));
  t.after(()=>fs.rmSync(folder,{recursive:true,force:true}));
  fs.cpSync(path.join(project,'impl/cli/fixtures/input-roots/canonical-project'),folder,{recursive:true});
  const read=(p:string)=>JSON.parse(fs.readFileSync(path.join(folder,p),'utf8'));
  const write=(p:string,v:unknown)=>fs.writeFileSync(path.join(folder,p),JSON.stringify(v,null,2)+'\n');
  const addNode=(feature:string,id:string,kind:string,body:unknown)=>{
    const f=read('specs/'+feature+'/feature.json');f.nodes.push(id);write('specs/'+feature+'/feature.json',f);
    write('specs/'+feature+'/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:feature,node_id:id,kind,body});
  };
  const operation={description:'Explicit operation.',reads:[],writes:[],effects:[],guard:'valid',failure_continuation:'return-error'};
  addNode('alpha','flow','Workflow',body);addNode('alpha','reverse','Operation',operation);
  addNode('alpha','charge','Operation',operation);addNode('alpha','refund','Operation',operation);addNode('beta','settle','Operation',operation);
  const addEdge=(selector:string)=>{
    const [feature,id]=selector.split(':'),edge='flow-'+feature+'-'+id;
    if(feature==='alpha'){
      const f=read('specs/alpha/feature.json');f.edges.push(edge);write('specs/alpha/feature.json',f);
      write('specs/alpha/edges/'+edge+'.json',{schema_version:'domainspec.edge/v1',edge_id:edge,feature_id:'alpha',relationship:'orchestrates',source_node_id:'flow',target_node_id:id,scope:'feature'});
    }else{
      const p=read('project.json');p.cross_feature_edges.push(edge);write('project.json',p);
      write('edges/'+edge+'.json',{schema_version:'domainspec.edge/v1',edge_id:edge,source_feature_id:'alpha',source_node_id:'flow',target_feature_id:feature,target_node_id:id,relationship:'orchestrates',scope:'project'});
    }
  };
  const refs=body.typed_contract?workflowOperationRefs(body.typed_contract):[...new Set([...body.steps,...body.compensations].filter((s:string)=>s!=='none'))].map(id=>'alpha:'+id);
  refs.forEach(addEdge);
  return {folder,read,write,addEdge,graph:()=>loadCompiledProjectGraph(folder)};
}

test('Workflow occurrence decoder is definition-bound, owned and preserves repeated concepts in ordered distinct steps',()=>{
  const source=contract(),decoded=decodeWorkflowOccurrences(source);
  assert.deepEqual(decoded,source);assert.notEqual(decoded.steps,source.steps);assert.ok(Object.isFrozen(decoded.compensations[0]!.depends_on));
  assert.deepEqual(workflowOperationRefs(decoded),['alpha:reverse','alpha:settle','beta:settle']);
  source.steps[0].step_id='changed';assert.equal(decoded.steps[0]!.step_id,'primary');
  assert.equal(sha256(fs.readFileSync(path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation/workflow-occurrence-contract.json'),'utf8')),WORKFLOW_OCCURRENCE_DEFINITION_SHA256);
  const separate=contract();separate.compensations[0].compensation_id='primary';assert.doesNotThrow(()=>decodeWorkflowOccurrences(separate));
});

test('Workflow source rejects identity collapse, unknown targets, cycles, malformed versions and hostile data',()=>{
  for(const change of [
    (c:any)=>c.extra=true,(c:any)=>c.schema_version='future',(c:any)=>c.steps=[],(c:any)=>c.steps[1].step_id='primary',
    (c:any)=>c.steps[0].operation_ref='settle',(c:any)=>c.steps[0].step_id+='\n',
    (c:any)=>c.compensations[1].compensation_id='undo-primary',(c:any)=>c.compensations[0].for_step='missing',
    (c:any)=>c.compensations[1].for_step='primary',(c:any)=>c.compensations[1].depends_on=['undo-primary'],
    (c:any)=>c.compensations[0].depends_on=['undo-primary'],(c:any)=>c.compensations[0].depends_on=['missing'],
    (c:any)=>c.compensations[0].depends_on=['undo-secondary','undo-secondary'],(c:any)=>delete c.steps[1],
    (c:any)=>c.steps=Array.from({length:129},(_,i)=>({step_id:'step-'+i,operation_ref:'alpha:settle'})),
  ]){const c=contract();change(c);assert.throws(()=>decodeWorkflowOccurrences(c),/MTCLI_WORKFLOW_OCCURRENCE/);}
  let reads=0;const c=contract();Object.defineProperty(c.steps[0],'operation_ref',{get(){reads++;return 'alpha:settle';},enumerable:true});
  assert.throws(()=>decodeWorkflowOccurrences(c));assert.equal(reads,0);
  for(const hidden of [Symbol('hidden'),'hidden']){const c=contract();Object.defineProperty(c,hidden,{value:true,enumerable:false});assert.throws(()=>decodeWorkflowOccurrences(c));}
});

test('Actual graph and source lint accept repeated steps and same bare Operation names across declared features without duplicate edges',t=>{
  const f=fixture(t),graph=f.graph(),node=selectCompiledProjectNode(graph,'alpha:flow');
  assert.equal((node.body.typed_contract as any).steps.length,3);
  assert.equal(node.relationships.filter(r=>r.relationship==='orchestrates').length,3);
  const before=fs.readFileSync(path.join(f.folder,'specs/alpha/nodes/flow.json'),'utf8'),out:string[]=[],err:string[]=[];
  assert.equal(runCli(['lint',f.folder],{stdout:s=>out.push(s),stderr:s=>err.push(s)}),0);assert.deepEqual(err,[]);
  assert.equal(JSON.parse(out.join('')).result,'pass');assert.equal(fs.readFileSync(path.join(f.folder,'specs/alpha/nodes/flow.json'),'utf8'),before);
  assert.deepEqual(f.graph(),graph);
});

test('Canonical closure rejects missing, surplus, wrong-feature and non-Operation references',t=>{
  const missing=fixture(t);const feature=missing.read('specs/alpha/feature.json');feature.edges=feature.edges.filter((s:string)=>s!=='flow-alpha-reverse');missing.write('specs/alpha/feature.json',feature);
  assert.throws(()=>missing.graph(),/orchestrates must cover exactly/);
  const surplus=fixture(t);surplus.addEdge('alpha:charge');assert.throws(()=>surplus.graph(),/orchestrates must cover exactly/);
  for(const target of ['gamma:settle','alpha:customer','alpha:charge']){
    const f=fixture(t),n=f.read('specs/alpha/nodes/flow.json');n.body.typed_contract.steps[2].operation_ref=target;f.write('specs/alpha/nodes/flow.json',n);
    assert.throws(()=>f.graph(),/Workflow reference must resolve|orchestrates must cover exactly/);
  }
});

test('Step ordering and compensation retargeting change meaning while concept-level edge coverage stays orthogonal',t=>{
  const f=fixture(t),before=f.graph(),n=f.read('specs/alpha/nodes/flow.json');
  [n.body.typed_contract.steps[0],n.body.typed_contract.steps[1]]=[n.body.typed_contract.steps[1],n.body.typed_contract.steps[0]];f.write('specs/alpha/nodes/flow.json',n);
  const after=f.graph();assert.deepEqual(after.relationships,before.relationships);
  assert.notEqual(createCompiledProjectCertificate(before).graph_sha256,createCompiledProjectCertificate(after).graph_sha256);
  assert.equal((after.nodes.find(n=>n.selector==='alpha:flow')!.body.typed_contract as any).steps[0].step_id,'secondary');
  n.body.typed_contract.compensations[0].for_step='other-feature';f.write('specs/alpha/nodes/flow.json',n);
  const retarget=f.graph();assert.deepEqual(retarget.relationships,after.relationships);
  assert.notEqual(createCompiledProjectCertificate(after).graph_sha256,createCompiledProjectCertificate(retarget).graph_sha256);
});

test('Legacy behavior remains separate and old generation, runtime and proof reject the new source explicitly',t=>{
  const body={description:'Legacy.',steps:['reserve','charge'],compensations:[]};assert.deepEqual(decodeBody('Workflow',body).steps,body.steps);
  assert.throws(()=>decodeBody('Workflow',{...body,steps:['reserve','reserve']}),/duplicate array member/);
  const f=fixture(t),graph=f.graph(),node=selectCompiledProjectNode(graph,'alpha:flow');
  for(const language of ['typescript','python','rust'] as const)assert.throws(()=>planInstantiation(node,language),/MTCLI_WORKFLOW_PROFILE_REQUIRED/);
  assert.throws(()=>createMetaTypeFormalizationProjection(graph),/Workflow occurrences require successor formalization/);
  assert.throws(()=>runInMemoryProject(f.folder,{schema_version:'domainspec.runtime-invocation/v1',invocation_id:'flow',provider:'in-memory-v1',steps:[{step_id:'run-flow',selector:'alpha:flow',input:{}}]}),/occurrence-aware executor/);
});

test('Explicit migration preserves legacy order and recovery dependencies without writing or inventing identities',t=>{
  const f=fixture(t,{description:'Legacy migration.',steps:['settle','charge'],compensations:['reverse','refund'],compensation_dependencies:['reverse:depends-on:refund']});
  const graph=f.graph(),bytes=fs.readFileSync(path.join(f.folder,'specs/alpha/nodes/flow.json'),'utf8');
  const selection={ontology_workflow:'TEST-MIGRATED-FLOW',step_ids:['settle-first','charge-second'],compensation_ids:['reverse-first','refund-second']};
  const plan=planWorkflowOccurrenceMigration(graph,'alpha:flow',selection);
  assert.deepEqual(plan,planWorkflowOccurrenceMigration(graph,'alpha:flow',selection));
  assert.equal(plan.writes_performed,false);assert.equal(plan.validation_ceiling,'candidate-body-not-replacement-graph');
  assert.deepEqual(plan.candidate_body.typed_contract.steps,[{step_id:'settle-first',operation_ref:'alpha:settle'},{step_id:'charge-second',operation_ref:'alpha:charge'}]);
  assert.deepEqual(plan.candidate_body.typed_contract.compensations[0],{compensation_id:'reverse-first',for_step:'settle-first',operation_ref:'alpha:reverse',depends_on:['refund-second']});
  assert.equal(fs.readFileSync(path.join(f.folder,'specs/alpha/nodes/flow.json'),'utf8'),bytes);
  const {migration_sha256,...rest}=plan;assert.equal(migration_sha256,sha256(canonicalJson(rest)));selection.step_ids[0]='caller-change';assert.equal((plan.selection as any).step_ids[0],'settle-first');
  const node=f.read('specs/alpha/nodes/flow.json');node.body=plan.candidate_body;f.write('specs/alpha/nodes/flow.json',node);
  const migrated=f.graph();assert.deepEqual(migrated.relationships,graph.relationships);
});

test('Migration rejects forged snapshots, malformed IDs and absent-compensation ambiguity',t=>{
  const f=fixture(t,{description:'One compensation.',steps:['settle','charge'],compensations:['reverse','none']});const graph=f.graph();
  const selection={ontology_workflow:'TEST-MIGRATION',step_ids:['first','second'],compensation_ids:['undo-first',null]};
  assert.equal(planWorkflowOccurrenceMigration(graph,'alpha:flow',selection).candidate_body.typed_contract.compensations.length,1);
  for(const s of [{...selection,step_ids:['first']},{...selection,step_ids:['first','first']},{...selection,compensation_ids:['undo-first','invented']},{...selection,compensation_ids:[null,null]},{...selection,extra:true}])assert.throws(()=>planWorkflowOccurrenceMigration(graph,'alpha:flow',s));
  assert.throws(()=>planWorkflowOccurrenceMigration(structuredClone(graph),'alpha:flow',selection),/unvalidated/);
  assert.throws(()=>planWorkflowOccurrenceMigration(graph,'alpha:settle',selection),/legacy Workflow required/);
  assert.throws(()=>planWorkflowOccurrenceMigration(fixture(t).graph(),'alpha:flow',selection),/legacy Workflow required/);
  let reads=0;const hostile={...selection,get step_ids(){reads++;return ['first','second'];}};assert.throws(()=>planWorkflowOccurrenceMigration(graph,'alpha:flow',hostile));assert.equal(reads,0);
});
