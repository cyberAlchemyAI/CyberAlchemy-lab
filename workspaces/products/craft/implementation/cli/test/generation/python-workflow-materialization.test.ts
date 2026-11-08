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
import {renderWorkflowMaterialization} from '../../src/generation/workflow-materialization-source.ts';
import {planPythonWorkflowMaterialization} from '../../src/generation/python-workflow-materialization.ts';
import {planConfiguredPythonOperations,PYTHON_OPERATION_VERSION} from '../../src/generation/configured-python-operations.ts';

const materialContract = read('profile-compiler-reconciliation/workflow-materialization-contract.json');
function parameters() {
 const post=(id:string)=>({occurrence:{'event-id':id},payload:{'order-id':'order-a',delta:'-1'},occurredAt:'2026-09-13'});
 const undo=(id:string)=>({occurrence:{'event-id':id},payload:{'order-id':'order-a'}});
 return {order:{id:'order-a'},amount:'18446744073709551615',post_first:post('p1'),post_second:post('p2'),undo_first:undo('u1'),undo_second:undo('u2')};
}
type Candidate=ReturnType<typeof planPythonWorkflowMaterialization>;
function native(f:Omit<ReturnType<typeof fixture>,'fields'> & {fields:ReturnType<typeof fixture>['fields']|null},p:Candidate,params:any=parameters(),returns:any=[{id:'first-result'},{id:'second-result'},{id:'third-result'}],operations:ReturnType<typeof planConfiguredPythonOperations>|null=null){
 const root=fs.mkdtempSync(path.join(f.temp,'python-'));
 const artifacts=new Map(p.artifacts.map(a=>[a.relative_path,a]));
 for(const a of operations?.artifacts??[]){const prior=artifacts.get(a.relative_path);if(prior)assert.equal(a.content,prior.content,'shared runtime/type identity');else artifacts.set(a.relative_path,a);}
 for(const a of artifacts.values()){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const data={root,plan:p,workflow:f.workflow,model:f.fields?.model??null,parameters:params,returns,operations:operations?.modules??null};
 const result=JSON.parse(execFileSync('/usr/bin/python3',['-B',path.join(import.meta.dirname,'python-workflow-materialization-runtime.py')],{input:JSON.stringify(data),encoding:'utf8',stdio:['pipe','pipe','pipe']}));
 const observed=JSON.parse(execFileSync('/usr/bin/python3',['-B',path.join(import.meta.dirname,'python-workflow-materialization-observer.py')],{input:JSON.stringify(data),encoding:'utf8',stdio:['pipe','pipe','pipe']}));
 assert.equal(observed.whole_source,true);
 return result;
}

test('Python Workflow materialization preserves exact occurrences, immutable capture and Operation wire inputs at relocated roots',t=>{
 const f=fixture(t),legacy=renderWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract);
 for(const root of ['application','relocated/kernel']){
  const p=planPythonWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract,root);
  assert.deepEqual(p,planPythonWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract,root));
  assert.ok(Object.isFrozen(p));assert.equal(p.descriptor.event_construction,'not-performed');
  assert.equal(native(f,p).steps,3);assert.equal(p.artifacts.some(a=>a.relative_path.includes('/operations/')),false);
 }
 assert.deepEqual(renderWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract),legacy);
});

test('Python Workflow materialization covers nested values, optionals, lists, sets, named Enums and sums without factories',t=>{
 const f=fixture(t),wrap=(kind:string,element:any)=>({kind,element});
 const prop=(owner:string,name:string,type:any,identity=false)=>({ontology_property:'FIXTURE-'+owner+'#'+name,name,type,identity,meaning:name,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one'});
 f.node('money','Value Object',{fields:['amount'],invariant_refs:['commerce:allowed'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-MONEY',properties:[prop('MONEY','amount',scalar('UInt64'))]}});
 f.node('status','Enum',{values:['Ready','Draft'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:['Ready','Draft'].map(name=>({name,payload:null,ontology_variant:'FIXTURE-STATUS#'+name}))}});
 const money=named('commerce:money'),sum={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-CHOICE#None',payload:null},{name:'Some',ontology_variant:'FIXTURE-CHOICE#Some',payload:money}]};
 const properties=[prop('ORDER','id',scalar(),true),prop('ORDER','maybe',wrap('optional',money)),prop('ORDER','items',wrap('list',money)),prop('ORDER','unique',wrap('set',money)),prop('ORDER','status',named('commerce:status')),prop('ORDER','choice',sum)];
 f.node('order','Entity',{fields:properties.map(p=>p.name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-ORDER',properties}});
 const built={...f,...f.build()},params:any=parameters();
 params.order={id:'o',items:[{amount:'4'},{amount:'4'}],unique:[{amount:'6'},{amount:'5'}],status:{variant:'Ready'},choice:{variant:'Some',payload:{amount:'18446744073709551615'}}};
 const p=planPythonWorkflowMaterialization(built.graph,built.workflow,built.fields,materialContract,'application');
 assert.equal(native(built,p,params,['first','second','third'].map(id=>({...params.order,id}))).steps,3);
 assert.equal(p.artifacts.some(a=>a.relative_path.includes('/entities/')||a.relative_path.includes('/rules/')),false);
});

test('Python Workflow materialization lowers explicit ontology paths, literals, list images and to_set',t=>{
 const f=fixture(t),b=structuredClone(f.bindings);
 b.inputs.push({name:'orders',type:{kind:'list',element:named('commerce:order')}});
 b.steps[0].arguments[1].value=literal('UInt64','18446744073709551615');
 b.result={type:{kind:'set',element:scalar()},value:{op:'to_set',value:input('orders','FIXTURE-ORDER#id')}};
 const workflow=compileWorkflowBindings(f.graph,f.boundary,f.fields,f.actions,b,contract),built={...f,workflow};
 const p=planPythonWorkflowMaterialization(f.graph,workflow,f.fields,materialContract,'application');
 assert.equal(native(built,p,{...parameters(),orders:[{id:'b'},{id:'a'},{id:'b'},{id:'😀'},{id:'\ue000'}]}).steps,3);
});

test('Python Workflow materialization rejects unregistered/stale/unsafe inputs and kills compiling same-type binding and ownership mutations',t=>{
 const f=fixture(t),p=planPythonWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract,'application');
 assert.throws(()=>planPythonWorkflowMaterialization(f.graph,{...f.workflow},f.fields,materialContract,'application'),/UNVALIDATED/);
 assert.throws(()=>planPythonWorkflowMaterialization(f.graph,f.workflow,{...f.fields},materialContract,'application'));
 assert.throws(()=>planPythonWorkflowMaterialization(f.graph,f.workflow,null,materialContract,'application'));
 assert.throws(()=>planPythonWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract+' ','application'),/contract drift/);
 for(const root of ['../escape','weakref','class',''])assert.throws(()=>planPythonWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract,root));
 const original=p.artifacts.find(a=>a.relative_path===p.relative_path)!.content;
 const changes=[
  (s:string)=>s.replace('p3 = r["second"]\n    p4 = r["third"]','p3 = r["third"]\n    p4 = r["third"]'),
  (s:string)=>s.replace('r = _prefix(input, results, 0, 0)','r = _prefix(input, results, 0, 3)'),
  (s:string)=>s.replace('"notice_input": input["post_second"]','"notice_input": input["post_first"]'),
  (s:string)=>s.replace('_result_inputs.get(row) is not input','False'),
  (s:string)=>s.replace(' or input not in _inputs',''),
  (s:string)=>s.replace('row.step_id != ids[i]','False').replace('type(row) is not classes[i]','type(row) not in classes'),
 ];
 for(const change of changes){
  const copy=structuredClone(p),provider=copy.artifacts.find(a=>a.relative_path===p.relative_path)!,changed=change(original);assert.notEqual(changed,original);
  execFileSync('/usr/bin/python3',['-c','import ast,sys;compile(ast.parse(sys.stdin.read()),"<mutation>","exec")'],{input:changed});
  provider.content=changed;provider.sha256=sha256(changed);provider.size_bytes=Buffer.byteLength(changed);
  assert.throws(()=>native(f,copy),(e:any)=>/ARGUMENT_BINDING|RESULT_BINDING|MISSING_BOUNDARY_REJECTION|INCORRECT_BOUNDARY_REJECTION/.test(e.stderr));
 }
});

test('Python Workflow materialization supports a single scalar step with no Event, field model or compensation',t=>{
 const f=fixture(t);
 f.sourceWorkflow.steps=[{step_id:'only',operation_ref:'commerce:post'}];f.sourceWorkflow.compensations=[];
 f.edges.splice(f.edges.indexOf('flow-release'),1);f.edges.splice(f.edges.indexOf('post-event'),1);
 f.node('post','Operation',{reads:[],writes:[],effects:[],guard:'allowed',failure_continuation:'return-post-error'});f.save();
 const graph=loadCompiledProjectGraph(f.source),cert=createCompiledProjectCertificate(graph),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:cert.graph_sha256},boundaryContract);
 const definition={...f.definitions[0],inputs:[],events:[],result:{type:scalar('UInt64'),value:literal('UInt64','7')}};
 const action=compileOperationActionBindings(graph,boundary,null,definition,actionContract);
 const bindings={schema_version:WORKFLOW_BINDINGS_VERSION,selector:'commerce:flow',inputs:[],event_inputs:[],steps:[{step_id:'only',action_sha256:action.action_sha256,arguments:[],events:[]}],compensations:[],result:{type:scalar('UInt64'),value:result('only')}};
 const workflow=compileWorkflowBindings(graph,boundary,null,[action],bindings,contract),p=planPythonWorkflowMaterialization(graph,workflow,null,materialContract,'application');
 assert.equal(native({...f,workflow,fields:null},p,{},['7']).steps,1);
 assert.equal(p.artifacts.some(a=>a.relative_path.includes('event_values')||a.relative_path.includes('event_references')),false);
});

test('Python Workflow wire arguments execute unchanged native Operations and preserve shared Event reference types',t=>{
 const f=fixture(t);
 f.node('identity-valid','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-IDENTITY-VALID',parameters:[{name:'id',type:scalar()}],expression:{op:'lt',left:literal('String',''),right:at('id')}}});
 const built={...f,...f.build()},bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8'),base='profile-compiler-reconciliation/';
 const rules={configuration:read(base+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),python:bytes('development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json'),
 rule_contract:read(base+'string-order-rule-contract.json'),collection_contract:read(base+'rule-collection-value-contract.json'),predicate_contract:read(base+'rule-collection-predicate-contract.json'),numeric_contract:read(base+'rule-numeric-contract.json'),exact_contract:read(base+'rule-exact-contract.json'),literal_contract:read(base+'rule-exact-literal-contract.json'),structured_contract:read(base+'rule-structured-value-contract.json'),field_contract:fieldContract};
 const operations=planConfiguredPythonOperations(built.graph,built.boundary,built.fields,{schema_version:PYTHON_OPERATION_VERSION,language:'python',module_root:'application',actions:built.actions,factories:[{selector:'commerce:order',base_validators:[{rule:'commerce:identity-valid',arguments:[{parameter:'id',field:'id'}]}],extensions:[]}]},{operation_contract:read(base+'operation-generation-contract.json'),factory_contract:read(base+'factory-structured-rule-contract.json'),rules,events:{configuration:rules.configuration,base:rules.base,python:rules.python,event_contract:read(base+'event-generation-contract.json')}});
 const p=planPythonWorkflowMaterialization(built.graph,built.workflow,built.fields,materialContract,'application');
 assert.equal(native(built,p,parameters(),[{id:'first'},{id:'second'},{id:'third'}],operations).operation_calls,3);
});

test('Python Workflow materialization whole-source audit rejects runtime-invisible effects, extra code and false public types',t=>{
 const f=fixture(t),p=planPythonWorkflowMaterialization(f.graph,f.workflow,f.fields,materialContract,'application');
 const original=p.artifacts.find(a=>a.relative_path===p.relative_path)!.content;
 const changes=[
  (s:string)=>s+'\ndef _hidden_effect():\n    open("unrequested", "w").close()\n',
  (s:string)=>s.replace('def _fail():','if False:\n    import os\n\ndef _fail():'),
  (s:string)=>s.replace('    count = 0','    hidden = globals().get("_transient", None)\n    globals()["_transient"] = True\n    globals().pop("_transient")\n    count = 0'),
  (s:string)=>s.replace('WorkflowValue = _Shape0','WorkflowValue = object'),
  (s:string)=>s.replace('    return copy(value, 0)','    return copy(value, 0)\n    raise RuntimeError("unreachable")'),
 ];
 for(const change of changes){
  const copy=structuredClone(p),a=copy.artifacts.find(a=>a.relative_path===p.relative_path)!,changed=change(original);assert.notEqual(changed,original);
  execFileSync('/usr/bin/python3',['-c','import ast,sys;compile(ast.parse(sys.stdin.read()),"<mutation>","exec")'],{input:changed});
  a.content=changed;a.sha256=sha256(changed);a.size_bytes=Buffer.byteLength(changed);copy.provider_sha256=a.sha256;
  // native() executes the complete runtime oracle first. Only a source-audit
  // diagnostic qualifies this control; a native failure cannot count as a kill.
  assert.throws(()=>native(f,copy),(e:any)=>/PYTHON_WORKFLOW_MATERIALIZATION_OBSERVER:AST:/.test(e.stderr));
 }
 const copy=structuredClone(p),init=copy.artifacts.find(a=>a.relative_path==='application/__init__.py')!;
 init.content='temporary = True\ndel temporary\n';init.sha256=sha256(init.content);init.size_bytes=Buffer.byteLength(init.content);
 assert.throws(()=>native(f,copy),(e:any)=>/PYTHON_WORKFLOW_MATERIALIZATION_OBSERVER:nonempty package initializer/.test(e.stderr));
});
