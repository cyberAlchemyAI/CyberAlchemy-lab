import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_VERSION, COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {compileOperationActionBindings, OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';
import {compileWorkflowBindings, WORKFLOW_BINDINGS_VERSION} from '../../src/typed-operation/workflow-bindings.ts';
import {WORKFLOW_OCCURRENCES_VERSION} from '../../src/typed-backend/workflow-occurrences.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {selectWorkflowRecoveryPolicy, planSelectedWorkflowRecovery, decodeWorkflowFailureJournal, assertCheckedWorkflowRecoveryPolicy, WORKFLOW_RECOVERY_POLICY_VERSION, WORKFLOW_FAILURE_JOURNAL_VERSION, WORKFLOW_RECOVERY_CONTRACT_SHA256} from '../../src/typed-operation/workflow-recovery.ts';

const project = path.resolve(import.meta.dirname, '../../../..');
const read = (p: string) => fs.readFileSync(path.join(project, 'development/reconciliation-v1', p), 'utf8');
const contract = read('profile-compiler-reconciliation/workflow-binding-contract.json');
const actionContract = read('profile-compiler-reconciliation/operation-action-contract.json');
const boundaryContract = read('contracts/composition-boundary.json');
const fieldContract = read('contracts/exact-field-and-reference-model.json');
const scalar = (name = 'String') => ({kind: 'scalar', name});
const named = (selector: string) => ({kind: 'named', selector});
const input = (name: string, ...properties: string[]) => ({op: 'input', name, properties});
const result = (step_id: string, ...properties: string[]) => ({op: 'step-result', step_id, properties});
const policyContract = read('profile-compiler-reconciliation/workflow-recovery-policy-contract.json');
const at = (root: string) => ({op: 'path', root, properties: []});
const literal = (type: string, value: any) => ({op: 'literal', type, value});

function baseFixture(t: any) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-workflow-bindings-'));
  t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const source = path.join(temp, 'source'), nodes: string[] = [], edges: string[] = [];
  const write = (p: string, v: any) => {const file = path.join(source, p); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, JSON.stringify(v, null, 2) + '\n');};
  const node = (id: string, kind: string, body: any) => {if (!nodes.includes(id)) nodes.push(id); write('specs/commerce/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'commerce', node_id: id, kind, body: {description: id, ...body}});};
  const edge = (id: string, relationship: string, from: string, to: string) => {if (!edges.includes(id)) edges.push(id); write('specs/commerce/edges/' + id + '.json', {schema_version: 'domainspec.edge/v1', edge_id: id, feature_id: 'commerce', relationship, source_node_id: from, target_node_id: to, scope: 'feature'});};
  node('order', 'Entity', {fields: ['id'], typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'FIXTURE-ORDER', properties: [{ontology_property: 'FIXTURE-ORDER#id', name: 'id', type: scalar(), cardinality: 'one', identity: true, meaning: 'order identity'}]}});
  node('allowed', 'Rule', {predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-ALLOWED', parameters: [{name: 'allowed', type: scalar('Bool')}], expression: {op: 'eq', left: at('allowed'), right: literal('Bool', true)}}});
  for (const id of ['posted', 'released']) node(id, 'Event', {event_type: id, version: '1', occurrence_id: {field_id: 'event-id', type_ref: {kind: 'primitive', name: 'uuid'}, required: true}, occurred_at_policy: id === 'posted' ? 'required' : 'generated', payload: [{field_id: 'order-id', type_ref: {kind: 'reference', selector: 'commerce:order'}, required: true}, {field_id: 'delta', type_ref: {kind: 'primitive', name: 'integer'}, required: false}]});
  const inputs: any[] = [{name: 'order', type: named('commerce:order')}, {name: 'amount', type: scalar('UInt64')}];
  const definitions: any[] = [];
  for (const [id, event] of [['post', 'posted'], ['release', 'released']]) {
    node(id!, 'Operation', {reads: [], writes: [], effects: ['notice'], guard: 'allowed', failure_continuation: 'return-' + id + '-error'});
    edge(id + '-guard', 'enforces', 'allowed', id!); edge(id + '-event', 'produces', id!, event!);
    definitions.push({schema_version: OPERATION_ACTION_BINDINGS_VERSION, selector: 'commerce:' + id, inputs: structuredClone(inputs), reads: [], writes: [], guards: [{selector: 'commerce:allowed', arguments: [{parameter: 'allowed', value: literal('Bool', true)}]}], events: [{slot: 'notice', target: 'commerce:' + event, parameter: 'notice_input'}], result: {type: named('commerce:order'), value: at('order')}, atomicity: 'state-and-outbox', continuation: 'awaited-settlement'});
  }
  const workflow: any = {schema_version: WORKFLOW_OCCURRENCES_VERSION, ontology_workflow: 'FIXTURE-POST-TWICE', steps: [{step_id: 'first', operation_ref: 'commerce:post'}, {step_id: 'second', operation_ref: 'commerce:post'}], compensations: [{compensation_id: 'first', for_step: 'first', operation_ref: 'commerce:release', depends_on: ['second']}, {compensation_id: 'second', for_step: 'second', operation_ref: 'commerce:release', depends_on: []}]};
  const save = () => {
    node('flow', 'Workflow', {typed_contract: workflow});
    write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'workflow-bindings', features: ['commerce'], cross_feature_edges: []});
    write('specs/commerce/feature.json', {schema_version: 'domainspec.feature/v1', feature_id: 'commerce', nodes, edges});
  };
  edge('flow-post', 'orchestrates', 'flow', 'post'); edge('flow-release', 'orchestrates', 'flow', 'release'); save();
  const compile = () => {
    const graph = loadCompiledProjectGraph(source), certificate = createCompiledProjectCertificate(graph);
    const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, boundaryContract);
    const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: ['commerce:order'], bindings: []}, fieldContract);
    const actions = definitions.map(d => compileOperationActionBindings(graph, boundary, fields, d, actionContract));
    const call = (id: string, compensation = false): any => ({[compensation ? 'compensation_id' : 'step_id']: id, action_sha256: actions[compensation ? 1 : 0]!.action_sha256,
      arguments: [{parameter: 'order', value: compensation ? result(id) : id === 'first' ? input('order') : result('first')}, {parameter: 'amount', value: input('amount')}],
      events: [{parameter: 'notice_input', input: (compensation ? 'undo_' : 'post_') + id}]});
    const bindings: any = {schema_version: WORKFLOW_BINDINGS_VERSION, selector: 'commerce:flow', inputs: structuredClone(inputs),
      event_inputs: ['first', 'second'].flatMap(id => [{name: 'post_' + id, event_ref: 'commerce:posted'}, {name: 'undo_' + id, event_ref: 'commerce:released'}]),
      steps: [call('first'), call('second')], compensations: [call('first', true), call('second', true)], result: {type: named('commerce:order'), value: result('second')}};
    return {graph, boundary, fields, actions, bindings, check: (b: any = bindings, a = actions, c = contract) => compileWorkflowBindings(graph, boundary, fields, a, b, c)};
  };
  return {temp, source, write, node, save, workflow, definitions, edges, compile, ...compile()};
}

function fixture(t: any) {
  const f = baseFixture(t);
  f.workflow.steps.push({step_id: 'third', operation_ref: 'commerce:post'});
  const build = () => {
    if (!f.workflow.compensations.length) {
      const i = f.edges.indexOf('flow-release'); if (i >= 0) f.edges.splice(i, 1);
    }
    f.save(); const c = f.compile(), b = c.bindings;
    const stepTemplates = structuredClone(b.steps), compTemplates = structuredClone(b.compensations);
    b.steps = f.workflow.steps.map((s: any, i: number) => ({...structuredClone(stepTemplates[i === 0 ? 0 : 1]), step_id: s.step_id}));
    b.compensations = f.workflow.compensations.map((s: any) => {
      const call = {...structuredClone(compTemplates[s.for_step === 'first' ? 0 : 1]), compensation_id: s.compensation_id};
      call.arguments[0].value = result(s.for_step); return call;
    });
    const used = new Set([...b.steps, ...b.compensations].flatMap((c: any) => c.events.map((e: any) => e.input)));
    b.event_inputs = b.event_inputs.filter((i: any) => used.has(i.name));
    const refs = new Set([...f.workflow.steps, ...f.workflow.compensations].map((s: any) => s.operation_ref));
    const workflow = compileWorkflowBindings(c.graph, c.boundary, c.fields, c.actions.filter(a => refs.has(a.bindings.selector)), b, contract);
    const selection: any = {schema_version: WORKFLOW_RECOVERY_POLICY_VERSION, workflow_sha256: workflow.workflow_sha256,
      contract_sha256: WORKFLOW_RECOVERY_CONTRACT_SHA256, dependency_semantics: 'needed-compensations-only', tie_break: 'reverse-completion'};
    const policy = selectWorkflowRecoveryPolicy(workflow, selection, policyContract);
    return {...c, workflow, selection, policy, plan: (j: any) => planSelectedWorkflowRecovery(policy, j)};
  };
  return {...f, sourceWorkflow: f.workflow, build, ...build()};
}
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {renderWorkflowMaterialization} from '../../src/generation/workflow-materialization-source.ts';

const materialContract = read('profile-compiler-reconciliation/workflow-materialization-contract.json');
function native(f: ReturnType<typeof fixture>, content = renderWorkflowMaterialization(f.graph,f.workflow, f.fields, materialContract).content) {
  const root = fs.mkdtempSync(path.join(f.temp, 'native-')), file = path.join(root, 'material.ts');
  fs.writeFileSync(file, content);
  const chain = JSON.parse(fs.readFileSync(path.resolve(project, '../../toolchains/node-typescript/toolchain.json'), 'utf8'));
  const image = nativeToolchainImage(chain.container_image);
  const docker = ['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--workdir',root,image];
  const compile = (...files: string[]) => execFileSync('docker', [...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),file,...files], {encoding:'utf8',stdio:'pipe'});
  compile();
  return {root, content, compile, docker, module:createRequire(import.meta.url)(path.join(root,'js/material.js'))};
}
function parameters() {
  const posted = (id: string) => ({occurrence:{'event-id':id}, payload:{'order-id':'order-a',delta:'-1'}, occurredAt:'2026-09-09'});
  const undo = (id: string) => ({occurrence:{'event-id':id},payload:{'order-id':'order-a'}});
  return {order:{id:'order-a'},amount:'18446744073709551615',post_first:posted('p1'),post_second:posted('p2'),undo_first:undo('u1'),undo_second:undo('u2')};
}
function oracle(m: any) {
  const raw=parameters(), cap=m.capture(raw), rows=['first','second','third'].map((id)=>m.captureResult(cap,id,{id:id+'-result'}));
  assert.equal(cap.amount,18446744073709551615n);
  assert.deepEqual(m.steps.first.arguments(cap,[]).order,{id:'order-a'});
  assert.equal(m.steps.second.arguments(cap,rows.slice(0,1)).order.id,'first-result');
  assert.equal(m.steps.third.arguments(cap,rows.slice(0,2)).order.id,'first-result');
  assert.equal(m.steps.second.arguments(cap,rows.slice(0,1)).notice_input.occurrence['event-id'],'p2');
  assert.equal(m.compensations.first.arguments(cap,rows.slice(0,1)).order.id,'first-result');
  assert.equal(m.compensations.second.arguments(cap,rows.slice(0,2)).order.id,'second-result');
  assert.equal(m.result(cap,rows).id,'second-result');
  raw.order.id='mutated';
  assert.equal(cap.order.id,'order-a');
  assert.throws(()=>m.steps.second.arguments(cap,[]));
  assert.throws(()=>m.steps.first.arguments(cap,rows));
  return {cap,rows};
}
test('native materialization preserves occurrences, exact values, typed exports and immutable capture', t => {
  const f=fixture(t), n=native(f), m=n.module, {cap,rows}=oracle(m);
  for(const x of [cap,cap.order,cap.post_first,cap.post_first.payload,rows[0],rows[0].value,m.steps,m.compensations,m.result(cap,rows)])assert.ok(Object.isFrozen(x));
  const source={id:'owned'}, own=m.captureResult(cap,'first',source);source.id='changed';assert.equal(own.value.id,'owned');
  assert.equal(m.descriptor.workflow_sha256,f.workflow.workflow_sha256);
  const consumer=path.join(n.root,'consumer.ts');
  fs.writeFileSync(consumer, 'import {capture,steps,captureResult,result,type WorkflowInput} from "./material";\ndeclare const input:WorkflowInput;const c=capture(input);const first=steps.first.arguments(c,[]);const amount:bigint=first.amount;const id:string=first.order.id;const delta:bigint|undefined=first.notice_input.payload.delta;const r=captureResult(c,"first",{id});\n// @ts-expect-error invalid occurrence\ncaptureResult(c,"fourth",{id});\n// @ts-expect-error normalized integer is bigint\nconst wrong:string=first.amount;\n');
  n.compile(consumer);
});
test('prefix availability rejects forged, cross-capture, sparse, accessor and reordered results', t => {
  const m=native(fixture(t)).module, {cap,rows}=oracle(m), other=m.capture(parameters());
  const bad=[[],rows.slice(0,1),[rows[1],rows[0]], [rows[0],rows[0]], [{...rows[0]},rows[1]], [m.captureResult(other,'first',{id:'x'}),rows[1]],new Array(2)];
  let invoked=0;const getter:any=[];Object.defineProperty(getter,'0',{enumerable:true,get(){invoked++;return rows[0];}});getter.length=2;bad.push(getter);
  for(const r of bad)assert.throws(()=>m.steps.third.arguments(cap,r));
  assert.equal(invoked,0);
  assert.throws(()=>m.steps.first.arguments({...cap},[]));
  assert.throws(()=>m.compensations.second.arguments(cap,rows.slice(0,1)));
  assert.throws(()=>m.result(cap,rows.slice(0,2)));
  assert.throws(()=>m.captureResult(cap,'fourth',{id:'x'}));
  assert.equal(m.compensations.first.arguments(cap,rows).order.id,'first-result');
});
test('Event input normalization preserves optional absence, signed range and time policy without construction', t => {
  const m=native(fixture(t)).module, p=parameters();
  delete (p.post_first.payload as any).delta;
  const cap=m.capture(p);
  assert.equal(Object.hasOwn(cap.post_first.payload,'delta'),false);
  assert.equal(Object.hasOwn(cap.undo_first,'occurredAt'),false);
  for(const value of ['-9223372036854775808','9223372036854775807']){const v=parameters();v.post_first.payload.delta=value;assert.equal(m.capture(v).post_first.payload.delta,BigInt(value));}
  for(const value of ['9223372036854775808','-9223372036854775809',null,undefined,1.5]){const v=parameters();(v.post_first.payload as any).delta=value;assert.throws(()=>m.capture(v));}
  for(const alter of [(v:any)=>delete v.post_first.occurredAt,(v:any)=>v.undo_first.occurredAt='unexpected',(v:any)=>v.post_first.occurrence['event-id']='',(v:any)=>v.post_first.payload['order-id']='']){const v=parameters();alter(v);assert.throws(()=>m.capture(v));}
});
test('capture bounds inert input and result data without getters, coercion or caller aliases', t => {
  const m=native(fixture(t)).module;
  let called=0;const v=parameters();Object.defineProperty(v.order,'id',{enumerable:true,get(){called++;return 'x';}});
  assert.throws(()=>m.capture(v));assert.equal(called,0);
  const cap=m.capture(parameters()), result:any={};Object.defineProperty(result,'id',{enumerable:true,get(){called++;return 'x';}});
  assert.throws(()=>m.captureResult(cap,'first',result));assert.equal(called,0);
  const cycle:any={id:'x'};cycle.next=cycle;
  for(const order of [cycle,new Date(),{id:'x',unknown:1},{id:{toString(){called++;return 'x';}}}])assert.throws(()=>m.capture({...parameters(),order}));
  assert.equal(called,0);
  for(const amount of ['18446744073709551616','-1',9007199254740992,NaN,Infinity])assert.throws(()=>m.capture({...parameters(),amount}));
  assert.throws(()=>m.capture({...parameters(),extra:true}));
});
test('renderer rejects unregistered inputs and stale contract; output is reproducible from checked snapshots', t => {
  const f=fixture(t), a=renderWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract);
  assert.throws(()=>renderWorkflowMaterialization(f.graph,{...f.workflow},f.fields,materialContract));
  assert.throws(()=>renderWorkflowMaterialization(f.graph,f.workflow,{...f.fields},materialContract));
  assert.throws(()=>renderWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract+' '));
  const other=fixture(t);assert.throws(()=>renderWorkflowMaterialization(f.graph,f.workflow,other.fields,materialContract+' '));
  fs.rmSync(f.source,{recursive:true,force:true});
  assert.deepEqual(renderWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract),a);
  assert.equal(a.sha256,sha256(a.content));assert.equal(a.descriptor_sha256,sha256(canonicalJson(a.descriptor)));
  assert.equal(a.descriptor.commit_evidence,'not-established');
  assert.equal(a.descriptor.event_construction,'not-performed');
});
test('independent behavior oracle kills compiling same-type binding, prefix and capture mutants', t => {
  const f=fixture(t), source=renderWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract).content;
  const mutants=[
    source.replace(/(export const result=[\s\S]*?r\[)"second"(\])/,'$1"third"$2'),
    source.replace('r["first"] as','r["second"] as'),
    source.replace('const r=prefix(input,results,0,0);','const r=prefix(input,results,0,3);'),
    source.replace('["notice_input"]:input["post_second"]','["notice_input"]:input["post_first"]')
  ];
  for(const content of mutants){assert.notEqual(content,source);const m=native(f,content).module;assert.throws(()=>oracle(m));}
});

test('nested values retain optional, list, set, named Enum, Value Object and sum semantics', t => {
  const f=fixture(t), wrap=(kind:string,element:any)=>({kind,element});
  const prop=(owner:string,name:string,type:any,identity=false)=>({ontology_property:'FIXTURE-'+owner+'#'+name,name,type,identity,meaning:name,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one'});
  f.node('money','Value Object',{fields:['amount'],invariant_refs:['commerce:allowed'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-MONEY',properties:[prop('MONEY','amount',scalar('UInt64'))]}});
  f.node('status','Enum',{values:['Ready','Draft'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:['Ready','Draft'].map(name=>({name,payload:null,ontology_variant:'FIXTURE-STATUS#'+name}))}});
  const money=named('commerce:money'), sum={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-CHOICE#None',payload:null},{name:'Some',ontology_variant:'FIXTURE-CHOICE#Some',payload:money}]};
  const properties=[prop('ORDER','id',scalar(),true),prop('ORDER','maybe',wrap('optional',money)),prop('ORDER','items',wrap('list',money)),prop('ORDER','unique',wrap('set',money)),prop('ORDER','status',named('commerce:status')),prop('ORDER','choice',sum)];
  f.node('order','Entity',{fields:properties.map(p=>p.name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-ORDER',properties}});
  const built={...f,...f.build()}, m=native(built).module, p:any=parameters();
  p.order={id:'o',items:[{amount:'4'},{amount:'4'}],unique:[{amount:'6'},{amount:'5'}],status:{variant:'Ready'},choice:{variant:'Some',payload:{amount:'18446744073709551615'}}};
  const cap=m.capture(p);
  assert.equal(cap.order.maybe,null);assert.equal(cap.order.items.length,2);assert.equal(cap.order.unique.length,2);
  assert.equal(cap.order.choice.payload.amount,18446744073709551615n);
  const rows=['first','second','third'].map(id=>m.captureResult(cap,id,p.order));
  assert.deepEqual(m.result(cap,rows),cap.order);
  for(const alter of [(v:any)=>v.order.unique.push({amount:'5'}),(v:any)=>v.order.status={variant:'Unknown'},(v:any)=>v.order.choice={variant:'None',payload:{amount:'1'}},(v:any)=>v.order.items[0].amount='-1']){const v=structuredClone(p);alter(v);assert.throws(()=>m.capture(v));}
  p.order.items[0].amount='9';assert.equal(cap.order.items[0].amount,4n);
});
test('checked ontology paths, literals, variants and explicit to_set specialize without new domain calls', t => {
  const f=fixture(t), b=structuredClone(f.bindings);
  b.inputs.push({name:'orders',type:{kind:'list',element:named('commerce:order')}});
  b.steps[0].arguments[1].value=literal('UInt64','18446744073709551615');
  b.result={type:{kind:'set',element:scalar()},value:{op:'to_set',value:input('orders','FIXTURE-ORDER#id')}};
  const checked=compileWorkflowBindings(f.graph,f.boundary,f.fields,f.actions,b,contract);
  const m=native({...f,workflow:checked}).module, p={...parameters(),orders:[{id:'b'},{id:'a'},{id:'b'}]};
  const cap=m.capture(p), rows=['first','second','third'].map(id=>m.captureResult(cap,id,{id}));
  assert.equal(m.steps.first.arguments(cap,[]).amount,18446744073709551615n);
  assert.deepEqual([...m.result(cap,rows)].sort(),['a','b']);assert.equal(cap.orders.length,3);
  f.node('status','Enum',{values:['Ready','Draft'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:['Ready','Draft'].map(name=>({name,payload:null,ontology_variant:'FIXTURE-STATUS#'+name}))}});
  // Enum use must be selected explicitly as a field root, not invented by expression lowering.
  f.save();const graph=loadCompiledProjectGraph(f.source),certificate=createCompiledProjectCertificate(graph);
  const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},boundaryContract);
  const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:['commerce:order','commerce:status'],bindings:[]},fieldContract);
  const actions=f.definitions.map(d=>compileOperationActionBindings(graph,boundary,fields,d,actionContract));
  const v=structuredClone(f.bindings);
  for(const c of [...v.steps,...v.compensations])c.action_sha256=actions[c.compensation_id?1:0]!.action_sha256;
  v.result={type:named('commerce:status'),value:{op:'variant',selector:'FIXTURE-STATUS#Ready'}};
  const workflow=compileWorkflowBindings(graph,boundary,fields,actions,v,contract), vm=native({...f,fields,workflow}).module, vi=vm.capture(parameters());
  assert.deepEqual(vm.result(vi,['first','second','third'].map(id=>vm.captureResult(vi,id,{id}))),{variant:'Ready'});
  assert.throws(()=>renderWorkflowMaterialization(f.graph,f.workflow,fields,materialContract));
});

test('independent native AST observer detects undeclared effects and missing owned-capture or prefix checks', t => {
  const f=fixture(t), n=native(f);
  fs.writeFileSync(path.join(n.root,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'commonjs'},files:['material.ts']}));
  fs.writeFileSync(path.join(n.root,'expected.json'),JSON.stringify({steps:f.bindings.steps,compensations:f.bindings.compensations,occurrences:f.sourceWorkflow}));
  const observer=String.raw`import fs from 'node:fs';
import {API} from '/opt/node-toolchain/node_modules/typescript/dist/api/sync/api.js';
import {SyntaxKind as K} from '/opt/node-toolchain/node_modules/typescript/dist/ast/index.js';
const root=process.cwd(),expected=JSON.parse(fs.readFileSync(root+'/expected.json','utf8')),api=new API({cwd:root});
const need=(c,m)=>{if(!c)throw Error(m)},txt=n=>n?.getText(),compact=n=>txt(n)?.replace(/\s+/g,'');
try {
 const snapshot=api.updateSnapshot({openProjects:[root+'/tsconfig.json']}),project=snapshot.getProject(root+'/tsconfig.json');
 const source=project.program.getSourceFile(root+'/material.ts'),declarations=new Map(),calls=[];
 const visit=n=>{
  if(n.kind===K.VariableDeclaration)declarations.set(txt(n.name),n.initializer);
  if(n.kind===K.CallExpression)calls.push(n);
  need(![K.ClassDeclaration,K.ImportDeclaration,K.AwaitExpression].includes(n.kind),'impure structure');
  if(n.kind===K.Identifier)need(!['Date','fetch','process','eval','Function','setTimeout','setInterval','require','clock','store','publish','dispatch'].includes(txt(n)),'ambient effect');
  n.forEachChild(visit);
 };source.forEachChild(visit);
 const capture=declarations.get('capture'),captureResult=declarations.get('captureResult'),prefix=declarations.get('prefix');
 need(capture?.kind===K.ArrowFunction&&compact(capture.body).includes('ruleData(captureData(value),'),'owned input capture');
 need(compact(captureResult.body).includes('.normalize(captureData(raw))'),'owned result capture');
 need(compact(prefix.body).includes('resultInputs.get(row)!==input')&&compact(prefix.body).includes('row.step_id!==ids[i]'),'input and occurrence identity');
 const object=n=>{need(n?.kind===K.CallExpression&&txt(n.expression)==='Object.freeze'&&n.arguments[0]?.kind===K.ObjectLiteralExpression,'frozen object');return n.arguments[0];};
 const members=n=>new Map(object(n).properties.map(p=>[p.name.kind===K.ComputedPropertyName?p.name.expression.text:txt(p.name),p.initializer]));
 for(const [group,rows]of [['steps',expected.steps],['compensations',expected.compensations]]){
  const emitted=members(declarations.get(group));need(emitted.size===rows.length,'exact occurrence set');
  rows.forEach((row,index)=>{
   const id=row.step_id??row.compensation_id,call=members(emitted.get(id));
   need(call.get('action_sha256')?.text===row.action_sha256,'action identity');
   const occurrence=expected.occurrences[group==='steps'?'steps':'compensations'].find(s=>(s.step_id??s.compensation_id)===id);
   need(call.get('operation_ref')?.text===occurrence.operation_ref,'Operation identity');
   const count=group==='steps'?index:expected.occurrences.steps.findIndex(s=>s.step_id===occurrence.for_step)+1;
   const body=compact(call.get('arguments').body);
   need(body.includes('prefix(input,results,'+count+','+(group==='steps'?count:expected.steps.length)+')'),'required prefix');
   for(const event of row.events)need(body.includes('['+JSON.stringify(event.parameter)+']:input['+JSON.stringify(event.input)+']'),'Event input binding');
  });
 }
 need(!calls.some(c=>txt(c.expression)?.endsWith('.make')),'no Event construction');
 console.log(JSON.stringify({result:'pass'}));
} finally {api.close();}
`;
  fs.writeFileSync(path.join(n.root,'observer.mjs'),observer);
  const observe=()=>execFileSync('docker',[...n.docker,'node',path.join(n.root,'observer.mjs')],{encoding:'utf8',stdio:'pipe'});
  assert.equal(JSON.parse(observe()).result,'pass');
  const mutants=[
    n.content.replace('ruleData(captureData(value),','ruleData(value,'),
    n.content.replaceAll('.normalize(captureData(raw))','.normalize(raw)'),
    n.content.replace('resultInputs.get(row)!==input','!resultInputs.has(row)'),
    n.content.replace('const r=prefix(input,results,0,0);','const r=prefix(input,results,0,3);'),
    n.content+'\nconst clock=Date.now();\n'
  ];
  for(const content of mutants){assert.notEqual(content,n.content);fs.writeFileSync(path.join(n.root,'material.ts'),content);n.compile();assert.throws(observe);}
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
