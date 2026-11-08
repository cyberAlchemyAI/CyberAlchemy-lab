import assert from 'node:assert/strict';
import fs from 'node:fs';import path from 'node:path';import test from 'node:test';
import {workflowFixture} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture,order,eventParameters} from '../helpers/workflow-values.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorWorkflowSurface} from '../../src/verification/reconciled-cross-generator-workflow-surface.ts';
import {createWorkflowProtocolReference} from '../../src/verification/reconciled-cross-generator-workflow-reference.ts';
import {createCrossGeneratorWorkflowControls,assertCrossGeneratorWorkflowControls,crossGeneratorWorkflowProbe,crossGeneratorWorkflowBatchProbes,checkCrossGeneratorWorkflowObservations,expandWorkflowProtocolCase} from '../../src/verification/reconciled-cross-generator-workflow.ts';
import {operationValueRecipe} from '../../src/verification/reconciled-operation-cases.ts';
import {workflowVerificationDefinitions} from '../../src/verification/reconciled-workflow-controls.ts';
import {createWorkflowProtocolCases} from '../../src/verification/reconciled-workflow-protocol-cases.ts';
import {createWorkflowCases} from '../../src/verification/reconciled-workflow-cases.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';

const project=path.resolve(import.meta.dirname,'../../../..'),base=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const read=(name:string)=>fs.readFileSync(path.join(base,name),'utf8');
const definition=read('cross-generator-workflow-contract.json'),operationDefinition=read('cross-generator-operation-contract.json'),protocol=read('cross-generator-workflow-protocol-contract.json'),boundaryDefinition=read('cross-generator-verification-contract.json');
const casesDefinition=read('cross-generator-workflow-cases-contract.json');
type Fixture=ReturnType<typeof workflowFixture>;
function context(f:Fixture,layout='domain'){
 const graph=f.graph,plan=planCompiledReconciledProject(graph,{...f.selection,module_root:layout}),boundary=createCrossGeneratorBoundary(graph,plan,boundaryDefinition);
 const surface=createCrossGeneratorWorkflowSurface(graph,plan,boundary,definition,operationDefinition),selector=surface.rows[0]!.selector;
 const reference=createWorkflowProtocolReference(graph,plan,surface,selector,protocol);
 const controls=()=>createCrossGeneratorWorkflowControls(graph,plan,boundary,definition,operationDefinition,protocol,casesDefinition);
 return {graph,plan,boundary,surface,reference,controls};
}
function seed(r:ReturnType<typeof context>['reference'],input:unknown={amount:'7'}){
 return {input:operationValueRecipe(input),identity:{workflow_execution_id:'execution-one',failure_occurrence_id:'failure-one'},capture:false,
  steps:r.binding.workflow.steps.map(s=>({step_id:s.step_id,mode:'committed',reads:[],clocks:r.binding.operations.find(o=>o.action.bindings.selector===s.operation_ref)!.action.events.filter(e=>e.contract.occurred_at_policy==='generated').map(e=>({slot:e.slot,value:'time-'+s.step_id}))}))};
}
const handle=(id:string,index:number)=>['identity','return:'+id+':'+index];
const operations=(calls:any[])=>calls.filter(c=>c.role==='operation');
const compensations=(calls:any[])=>calls.filter(c=>c.method==='compensation.arguments');

test('Workflow protocol retains each repeated occurrence and exact original-value handoffs',t=>{
 const c=context(workflowValuesFixture(t,{events:true})),v=c.reference.expected('case-0',seed(c.reference,{amount:order(),...eventParameters()})),calls=v.calls;
 assert.equal(calls.length,14);assert.equal(calls[0]!.method,'capture');assert.equal(calls.at(-1)!.method,'result');
 assert.deepEqual(calls[0]!.arguments,['array',[['source-input','case-0']]]);
 for(let i=0;i<4;i++){
  const a=1+i*3,op=a+1,capture=a+2,step=c.reference.binding.workflow.steps[i]!.step_id;
  assert.equal(calls[a]!.method,'step.arguments');assert.equal(calls[a]!.occurrence,step);
  assert.deepEqual(calls[a]!.arguments,['array',[handle('case-0',0),['array',Array.from({length:i},(_,j)=>handle('case-0',3+j*3))]]]);
  assert.deepEqual(calls[op]!.arguments,['array',[handle('case-0',a),['identity','dependency:case-0:commerce:perform']]]);
  assert.equal(calls[op]!.awaited,true);
  assert.deepEqual(calls[capture]!.arguments,['array',[handle('case-0',0),['string',step],['identity','operation-value:case-0:'+op]]]);
 }
 assert.equal(new Set(operations([...calls]).map(c=>c.occurrence)).size,4);
 assert.ok(calls.every(c=>c.result.kind==='value'&&/^[a-f0-9]{64}$/.test(c.result.data_sha256)));
 assert.equal(compensations([...calls]).length,0);
 assert.ok(Object.isFrozen(v.calls));
 const again=c.reference.expected('case-1',seed(c.reference,{amount:order(),...eventParameters()}));
 assert.notDeepEqual(again.calls[1]!.arguments,calls[1]!.arguments);assert.deepEqual(again.semantic,v.semantic);
});

test('typed Event identity negatives reject at capture before any Workflow effects',t=>{
 const c=context(workflowValuesFixture(t,{events:true})),valid={amount:order(),...eventParameters()};
 const positive=c.reference.expected('valid-event-ids',seed(c.reference,valid));
 assert.equal(positive.calls.length,14);assert.equal(operations([...positive.calls]).length,4);
 for(const event of ['post','undo'] as const)for(const identity of ['o','01','-1','18446744073709551616','1\n',9007199254740992]){
  const raw=structuredClone(valid);raw[event].payload['order-id']=identity as any;
  const rejected=c.reference.expected('invalid-event-id',seed(c.reference,raw));
  assert.equal(rejected.calls.length,1);assert.equal(rejected.calls[0]!.method,'capture');
  assert.deepEqual(rejected.calls[0]!.result,{kind:'error',name:'TypeError'});
  assert.equal(rejected.semantic.rejected,true);assert.deepEqual(operations([...rejected.calls]),[]);
  assert.deepEqual(rejected.semantic.port_trace,[]);assert.deepEqual(rejected.semantic.clock_calls,[]);
  assert.deepEqual(rejected.semantic.read_requests,[]);assert.deepEqual(rejected.semantic.batches,[]);
 }
 assert.deepEqual(valid,{amount:order(),...eventParameters()},'negative mutations cannot corrupt shared valid witnesses');
});

test('settlement modes preserve stopped prefixes and selected recovery order without compensation execution',t=>{
 for(const options of [{},{dependencies:[[],['undo-first'],['undo-second']]},{noCompensations:true}]){
  const c=context(workflowFixture(t,options)),s=seed(c.reference);
  for(const mode of ['committed','rejected','indeterminate','begin-throw','commit-throw','rollback-throw','receipt-empty','receipt-unknown','receipt-extra','receipt-null','receipt-getter','receipt-inherited','receipt-symbol','receipt-hidden','receipt-array','receipt-undefined']){
   for(let at=0;at<4;at++){
    const v=structuredClone(s);v.steps[at]!.mode=mode;
    const result=c.reference.expected('case-0',v),calls=[...result.calls],normal=mode==='committed'||mode==='rollback-throw';
    assert.equal(operations(calls).length,normal?4:at+1);
    const captures=calls.filter(c=>c.method==='captureResult');assert.equal(captures.length,normal?4:at);
    const cs=compensations(calls);
    const recoverable=['rejected','begin-throw'].includes(mode)&&!options.noCompensations;
    assert.equal(cs.length,recoverable?at:0);
    if(recoverable&&at===3)assert.deepEqual(cs.map(c=>c.occurrence),options.dependencies?['undo-first','undo-second','undo-third']:['undo-third','undo-second','undo-first']);
    assert.ok(operations(calls).every(c=>c.provider==='commerce:perform'));
    if(!normal)assert.ok(!calls.some(c=>c.method==='result'));
   }
  }
 }
});

test('invalid identities and hostile input recipes preserve zero effects and actual capture rejection',t=>{
 const c=context(workflowFixture(t)),s=seed(c.reference);
 for(const mode of ['getter','non-enumerable','symbol','inherited','extra','missing-field','null','array']){
  const v={...s,input:{tag:'bad',base:s.input,mode,field:'amount'}};
  const r=c.reference.expected('case-0',v);assert.equal(r.calls.length,1,mode);assert.deepEqual(r.calls[0]!.result,{kind:'error',name:'TypeError'});
  assert.equal(r.semantic.rejected,true);assert.deepEqual(r.semantic.port_trace,[]);
 }
 const invalid={...s,identity:{...s.identity,workflow_execution_id:'Upper'}};
 assert.deepEqual(c.reference.expected('case-0',invalid).calls,[]);
 let reads=0;const active=Object.defineProperty({...s},'input',{enumerable:true,get(){reads++;return s.input;}});
 assert.throws(()=>c.reference.expected('case-0',active));assert.equal(reads,0);
 assert.throws(()=>c.reference.expected('../case',s),/case identity/);
 assert.throws(()=>createWorkflowProtocolReference(c.graph,c.plan,c.surface,c.surface.rows[0]!.selector,protocol+' '),/definition drift/);
 const other=context(workflowFixture(t),'application/domain');
 assert.throws(()=>createWorkflowProtocolReference(c.graph,other.plan,c.surface,c.surface.rows[0]!.selector,protocol),/foreign surface/);
});

test('full scalar and compound Workflow case families retain existing independent semantics in both layouts',async t=>{
 for(const compound of [false,true])for(const layout of ['domain','application/domain'])await t.test((compound?'compound':'scalar')+':'+layout,t=>{
  const c=context(compound?workflowValuesFixture(t,{events:true}):workflowFixture(t),layout),control=c.controls(),r=control.rows[0]!;
  assert.equal(r.state,'ready',r.state==='not_evaluable'?r.reason:'');if(r.state!=='ready')return;
  const d=workflowVerificationDefinitions(),defs={binding:d.binding,execution:d.execution,values:d.values,outcomes:d.outcomes},node=c.graph.nodes.find(n=>n.kind==='Workflow')!;
  const original=createWorkflowProtocolCases(node,c.graph,c.plan,defs,casesDefinition);
  if(!compound){
   const prior=createWorkflowCases(node,c.graph,c.plan,defs,d.cases);
   assert.deepEqual(original.recipes,prior.recipes);assert.deepEqual(original.coverage,prior.coverage);assert.deepEqual(original.search,prior.search);
   original.cases.forEach((v,i)=>{assert.deepEqual({...v,expected:prior.cases[i]!.expected},prior.cases[i]);assert.equal((v.expected as any).value,sha256((prior.cases[i]!.expected as any).value));});
  }
  assert.equal(r.cases.length,original.cases.length);assert.deepEqual(r.dimensions,original.coverage);
  r.cases.forEach((entry,i)=>assert.equal(entry.expected.semantic_sha256,(original.cases[i]!.expected as any).value));
  assert.equal(r.modules.some(m=>m.selector==='commerce:undo'||m.selector==='commerce:released'),false);
  const probe=crossGeneratorWorkflowProbe(control);assert.ok(probe.rows[0]!.cases.every((v:Pick<(typeof r.cases)[number],'id'|'data'>)=>Object.keys(v).sort().join(',')==='data,id'));
  assert.ok(!JSON.stringify(probe).includes('"expected"'));
  const batches=crossGeneratorWorkflowBatchProbes(control);
  assert.equal(batches.length,r.batches.length);assert.ok(batches.every(v=>Buffer.byteLength(canonicalJson(v))<=8388608&&v.batch.count<=4096));
  assert.deepEqual(batches.flatMap(v=>v.rows[0]!.cases.map((c:any)=>c.id)),r.cases.map(c=>c.id));
  if(compound)assert.ok(batches.length>1,'full compound family spans batches');
  const expected=c.reference.expected(r.cases[0]!.id,expandWorkflowProtocolCase(r.recipes,r.cases[0]!.data));
  assert.deepEqual({calls:expected.calls,semantic_sha256:sha256(canonicalJson(expected.semantic))},r.cases[0]!.expected);
  t.diagnostic(JSON.stringify({layout,compound,cases:r.cases.length,calls:r.cases.reduce((n,v)=>n+v.expected.calls.length,0),batches:batches.length,family_bytes:Buffer.byteLength(canonicalJson(r))}));
 });
});

test('comparison is exact, no expected answers leak, and source coverage does not imply native proof',t=>{
 const c=context(workflowFixture(t)),control=c.controls(),r=control.rows[0]!;
 assert.equal(r.state,'ready');if(r.state!=='ready')return;
 // Comparator unit fixture, deliberately not claimed to be native execution.
 const observed={controls_sha256:control.controls_sha256,rows:[{selector:r.selector,identity:r.identity,descriptor:r.descriptor,material_descriptor:r.material_descriptor,batches:r.batches,cases:r.cases.map(v=>({id:v.id,...v.expected}))}]};
 const result=checkCrossGeneratorWorkflowObservations(control,observed);
 assert.equal(result.tested_case_count,r.cases.length);assert.equal(result.retained_execution,'not_evaluable');assert.equal(result.public_cross_generator_behavior,'not_evaluable');
 assert.ok(result.uncovered_runtime_edge_count>0);
 for(const mutate of [(v:any)=>v.rows[0].cases.pop(),(v:any)=>v.rows[0].cases[0].calls.reverse(),(v:any)=>v.rows[0].cases[0].calls[2].arguments=['array',[]],(v:any)=>v.rows[0].identity.workflow=false,
  (v:any)=>v.rows[0].descriptor=null,(v:any)=>v.rows[0].material_descriptor=null,(v:any)=>v.rows[0].cases[0].semantic_sha256='0'.repeat(64),(v:any)=>v.extra=true]){
  const bad=structuredClone(observed);mutate(bad);assert.throws(()=>checkCrossGeneratorWorkflowObservations(control,bad),/observation mismatch/);
 }
 assert.throws(()=>checkCrossGeneratorWorkflowObservations(control,crossGeneratorWorkflowProbe(control)),/observation mismatch/);
 assert.throws(()=>assertCrossGeneratorWorkflowControls(structuredClone(control)),/registered/);
 assert.throws(()=>createCrossGeneratorWorkflowControls(c.graph,c.plan,c.boundary,definition,operationDefinition,protocol+' ',casesDefinition),/definition drift/);
 for(const e of control.coverage.filter(e=>e.state==='direct-protocol-selected')){
  const source=c.boundary.edges.find(s=>s.edge_sha256===e.edge_sha256)!;
  assert.equal(source.importer_path,r.provider_path);assert.equal(source.category,'generated-runtime');assert.equal(source.type_only,false);
 }
});

test('distinct forward Operations keep separate dependencies while repeated occurrences share only their selector slot',t=>{
 const f=workflowFixture(t),source=path.join(f.root,'source'),read=(p:string)=>JSON.parse(fs.readFileSync(path.join(source,p),'utf8')),write=(p:string,v:unknown)=>fs.writeFileSync(path.join(source,p),JSON.stringify(v));
 const feature=read('specs/commerce/feature.json'),op=read('specs/commerce/nodes/perform.json');
 op.node_id='other';op.body.failure_continuation='return-other-error';write('specs/commerce/nodes/other.json',op);feature.nodes.push('other');
 for(const [from,relationship] of [['allowed','enforces'],['flow','orchestrates']]){
  const edge_id=from+'-'+relationship+'-other';feature.edges.push(edge_id);
  write('specs/commerce/edges/'+edge_id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'commerce',edge_id,relationship,source_node_id:from,target_node_id:'other',scope:'feature'});
 }
 const flow=read('specs/commerce/nodes/flow.json');flow.body.typed_contract.steps[1].operation_ref='commerce:other';flow.body.typed_contract.steps[3].operation_ref='commerce:other';
 write('specs/commerce/nodes/flow.json',flow);write('specs/commerce/feature.json',feature);
 const selection:any=structuredClone(f.selection),action=structuredClone(selection.operations[0]);action.selector='commerce:other';action.result.value={op:'literal',type:'UInt64',value:'11'};selection.operations.push(action);
 const c=context({...f,graph:loadCompiledProjectGraph(source),selection}),s=seed(c.reference),calls=operations([...c.reference.expected('case-0',s).calls]);
 assert.deepEqual(calls.map(x=>x.provider),['commerce:perform','commerce:other','commerce:perform','commerce:other']);
 assert.deepEqual(calls.map(x=>x.arguments[1][1]),['commerce:perform','commerce:other','commerce:perform','commerce:other'].map(x=>['identity','dependency:case-0:'+x]));
 for(let at=0;at<4;at++){const stopped=structuredClone(s);stopped.steps[at]!.mode='rejected';assert.equal(operations([...c.reference.expected('case-0',stopped).calls]).length,at+1);}
});

test('generated clocks and transactional reads and writes remain part of each complete semantic commitment',t=>{
 const f=workflowValuesFixture(t,{events:true}),source=path.join(f.root,'source'),read=(p:string)=>JSON.parse(fs.readFileSync(path.join(source,p),'utf8')),write=(p:string,v:unknown)=>fs.writeFileSync(path.join(source,p),JSON.stringify(v));
 const feature=read('specs/commerce/feature.json'),selection:any=structuredClone(f.selection);
 for(const op of selection.operations){
  const id=op.selector.split(':')[1],node=read('specs/commerce/nodes/'+id+'.json');
  node.body.reads=['current-order'];node.body.writes=['order-state'];write('specs/commerce/nodes/'+id+'.json',node);
  const edge_id=id+'-reads-order';feature.edges.push(edge_id);write('specs/commerce/edges/'+edge_id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'commerce',edge_id,relationship:'reads',source_node_id:id,target_node_id:'order',scope:'feature'});
  op.reads=[{slot:'current-order',target:'commerce:order',parameter:'current',key:{op:'path',root:'amount',properties:['TEST-ORDER#id']}}];
  op.writes=[{slot:'order-state',target:'commerce:order',mode:'replace',value:{op:'path',root:'amount',properties:[]}}];
  op.result.value={op:'path',root:'current',properties:[]};
 }
 const posted=read('specs/commerce/nodes/posted.json');posted.body.occurred_at_policy='generated';write('specs/commerce/nodes/posted.json',posted);write('specs/commerce/feature.json',feature);
 const c=context({...f,graph:loadCompiledProjectGraph(source),selection}),parameters:any={amount:order(),...eventParameters()};delete parameters.post.occurredAt;
 const s:any=seed(c.reference,parameters);s.steps.forEach((v:any)=>v.reads=[{slot:'current-order',value:operationValueRecipe(order('1','read-'+v.step_id))}]);
 const initial=c.reference.expected('case-0',s);assert.equal(initial.semantic.read_requests.length,4);assert.equal(initial.semantic.clock_calls.length,4);assert.equal(initial.semantic.batches.length,4);
 for(let at=0;at<4;at++)for(const change of [(v:any)=>v.clocks[0].mode='throw',(v:any)=>v.clocks[0].value='',(v:any)=>v.reads[0].throws=true,(v:any)=>v.reads[0].value={tag:'null'},(v:any)=>v.mode='commit-throw']){
  const bad=structuredClone(s);change(bad.steps[at]);const result=c.reference.expected('case-0',bad);
  assert.equal(operations([...result.calls]).length,at+1);assert.notEqual(sha256(canonicalJson(result.semantic)),sha256(canonicalJson(initial.semantic)));
 }
 const missing=structuredClone(s);missing.steps.forEach((v:any)=>v.clocks[0].mode='missing');
 assert.deepEqual(c.reference.expected('case-0',missing).semantic.clock_calls,[]);
});

test('oversized source family is wholly unavailable rather than a passing prefix',t=>{
 const f=workflowFixture(t),source=path.join(f.root,'source'),file=path.join(source,'specs/commerce/nodes/flow.json'),flow=JSON.parse(fs.readFileSync(file,'utf8')),selection:any=structuredClone(f.selection);
 const ids=['first','second','third','last',...Array.from({length:124},(_,i)=>'step-'+i)];
 flow.body.typed_contract.steps=ids.map(step_id=>({step_id,operation_ref:'commerce:perform'}));fs.writeFileSync(file,JSON.stringify(flow));
 selection.workflows[0].steps=ids.map((step_id,i)=>({step_id,arguments:[{parameter:'amount',value:i?{op:'step-result',step_id:ids[i-1],properties:[]}:{op:'input',name:'amount',properties:[]}}],events:[]}));
 const c=context({...f,graph:loadCompiledProjectGraph(source),selection}),control=c.controls(),r=control.rows[0]!;
 assert.equal(r.state,'not_evaluable');assert.ok(!Object.hasOwn(r,'cases'));assert.equal(crossGeneratorWorkflowProbe(control).rows.length,0);
 assert.ok(control.coverage.every(e=>e.state==='not_evaluable'));
 assert.throws(()=>checkCrossGeneratorWorkflowObservations(control,{controls_sha256:control.controls_sha256,rows:[]}),/no ready/);
});
