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
import {planConfiguredPythonWorkflow,PYTHON_WORKFLOW_VERSION} from '../../src/generation/configured-python-workflows.ts';
import {inspectOperationSettlement,observeWorkflowStep,evaluateWorkflowOutcomeJournal,WORKFLOW_OUTCOME_JOURNAL_VERSION} from '../../src/typed-operation/workflow-outcomes.ts';

const base='profile-compiler-reconciliation/',bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8');
const rules={configuration:read(base+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),python:bytes('development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json'),
 rule_contract:read(base+'string-order-rule-contract.json'),collection_contract:read(base+'rule-collection-value-contract.json'),predicate_contract:read(base+'rule-collection-predicate-contract.json'),numeric_contract:read(base+'rule-numeric-contract.json'),exact_contract:read(base+'rule-exact-contract.json'),literal_contract:read(base+'rule-exact-literal-contract.json'),structured_contract:read(base+'rule-structured-value-contract.json'),field_contract:fieldContract};
const sources={workflow_contract:read(base+'workflow-generation-contract.json'),materialization_contract:read(base+'workflow-materialization-contract.json'),outcome_contract:read(base+'workflow-outcome-contract.json'),recovery_contract:policyContract,
 operations:{operation_contract:read(base+'operation-generation-contract.json'),factory_contract:read(base+'factory-structured-rule-contract.json'),rules,events:{configuration:rules.configuration,base:rules.base,python:rules.python,event_contract:read(base+'event-generation-contract.json')}}};
function candidate(t:any,change?:(f:ReturnType<typeof fixture>)=>void){
 const f=fixture(t);
 f.node('identity-valid','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-IDENTITY-VALID',parameters:[{name:'id',type:scalar()}],expression:{op:'lt',left:literal('String',''),right:at('id')}}});
 change?.(f);const c={...f,...f.build()};
 const selection:any={schema_version:PYTHON_WORKFLOW_VERSION,language:'python',module_root:'application',workflow:c.workflow,policy:c.policy,actions:c.actions.filter(a=>[...c.workflow.steps,...c.workflow.compensations].some(s=>s.operation_ref===a.bindings.selector)),factories:[{selector:'commerce:order',base_validators:[{rule:'commerce:identity-valid',arguments:[{parameter:'id',field:'id'}]}],extensions:[]}]};
 return {...c,selection,plan:()=>planConfiguredPythonWorkflow(c.graph,c.boundary,c.fields,selection,sources)};
}
const ids={workflow_execution_id:'execution-one',failure_occurrence_id:'failure-one'};
function parameters(){
 const post=(id:string)=>({occurrence:{'event-id':id},payload:{'order-id':'o',delta:'-1'},occurredAt:'2026-09-13'}),undo=(id:string)=>({occurrence:{'event-id':id},payload:{'order-id':'o'}});
 return {order:{id:'o'},amount:'18446744073709551615',post_first:post('p1'),post_second:post('p2'),undo_first:undo('u1'),undo_second:undo('u2')};
}
function cases(f:ReturnType<typeof candidate>){
 const rows:any[]=[];
 for(const mode of ['success','reject','indeterminate','invalid-receipt','throw-before','throw-after','begin-throw','threw','cancelled','malformed','active','committed-bad','not-started','final-bad','binding-bad']){
  const indices=mode==='success'||mode==='final-bad'?[-1]:mode==='binding-bad'?[2]:[0,1,2];
  for(const index of indices){
   const observations=[],count=index<0?f.workflow.steps.length:index+1;
   for(let i=0;i<count;i++){
    const s=f.workflow.steps[i]!,bad=i===index;let event:any={kind:'returned',outcome:{status:'committed',value:null}};
    if(bad){
     if(['threw','cancelled'].includes(mode))event={kind:'threw'};
     else if(mode==='not-started')event={kind:'not-started'};
     else if(['malformed','active'].includes(mode))event={kind:'returned',outcome:{garbage:true}};
     else if(mode!=='committed-bad')event={kind:'returned',outcome:{status:mode==='begin-throw'?'failed':mode==='reject'||mode==='binding-bad'?'rejected':'indeterminate',stage:mode==='begin-throw'?'begin':'commit',code:mode==='begin-throw'?'BEGIN_FAILED':mode==='reject'||mode==='binding-bad'?'COMMIT_REJECTED':mode==='indeterminate'?'COMMIT_INDETERMINATE':mode==='invalid-receipt'?'INVALID_COMMIT_RECEIPT':'COMMIT_UNCERTAIN',continuation:s.failure_continuation,cleanupFailed:false}};
    }
    observations.push(observeWorkflowStep(f.workflow,s.step_id,event,sources.outcome_contract));
   }
   const local_error=mode==='committed-bad'?'committed-result-invalid':mode==='final-bad'?'result-materialization-failed':null;
   const expected=evaluateWorkflowOutcomeJournal(f.policy,{schema_version:WORKFLOW_OUTCOME_JOURNAL_VERSION,...ids,failure_occurrence_id:mode==='success'?null:ids.failure_occurrence_id,observations,local_error});
   rows.push({mode,index,expected});
  }
 }
 return rows;
}
type Plan=ReturnType<typeof planConfiguredPythonWorkflow>;
function native(f:ReturnType<typeof candidate>,p:Plan=f.plan(),selectedCases=cases(f)){
 const root=fs.mkdtempSync(path.join(f.temp,'python-'));
 for(const a of p.artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const vectors=[null,true,0,{z:'\ud800',a:'😀',pair:'\ud83d\ude00',controls:'\b\f\n\r\t"\\',line:'\u2028\u2029'}, {'\ue000':'bmp','😀':'astral'}].map(value=>({value,digest:sha256(canonicalJson(value))}));
 const metadata=[];
 const continuation=f.workflow.steps[0]!.failure_continuation;
 for(const status of ['failed','rejected','indeterminate'])for(const stage of ['input','begin','read','guard','write-validation','event','result','commit'])for(const code of ['OPERATION_INPUT','BEGIN_FAILED','OPERATION_FAILED','READ_NOT_FOUND','RULE_REJECTED:commerce:allowed','COMMIT_REJECTED','COMMIT_INDETERMINATE','INVALID_COMMIT_RECEIPT','COMMIT_UNCERTAIN','INVALID'])for(const cleanupFailed of [false,true]){
  const value={status,stage,code,continuation,cleanupFailed};metadata.push({value,expected:inspectOperationSettlement(value,continuation)});
 }
 const allowed=new Set([...f.workflow.bindings.inputs,...f.workflow.bindings.event_inputs].map(p=>p.name));
 const data={root,plan:p,workflow:f.workflow,model:f.fields?.model??null,nodes:Object.fromEntries(f.graph.nodes.map(n=>[n.selector,{kind:n.kind,body:n.body}])),parameters:Object.fromEntries(Object.entries(parameters()).filter(([name])=>allowed.has(name))),ids,cases:selectedCases,vectors,metadata};
 const result=JSON.parse(execFileSync('/usr/bin/python3',['-B',path.join(import.meta.dirname,'python-workflow-runtime.py')],{input:JSON.stringify(data),encoding:'utf8',stdio:['pipe','pipe','pipe']}));
 const observed=JSON.parse(execFileSync('/usr/bin/python3',['-B',path.join(import.meta.dirname,'python-workflow-observer.py')],{input:JSON.stringify(data),encoding:'utf8',stdio:['pipe','pipe','pipe']}));
 assert.equal(observed.whole_source,true);
 return result;
}

test('Native Python Workflow preserves source occurrence execution, all failure prefixes and exact existing recovery hashes',t=>{
 const f=candidate(t);
 for(const root of ['application','relocated/kernel']){
  const p=planConfiguredPythonWorkflow(f.graph,f.boundary,f.fields,{...f.selection,module_root:root},sources);
  assert.deepEqual(p,planConfiguredPythonWorkflow(f.graph,f.boundary,f.fields,{...f.selection,module_root:root},sources));
  assert.ok(Object.isFrozen(p));assert.equal(p.modules[0].descriptor.compensation_execution,false);
  assert.equal(native(f,p).cases,cases(f).length);
 }
});

test('Python Workflow applies authored ordered and unconstrained compensation graphs only to needed prefixes',t=>{
 for(const mode of ['unordered','forward-order','no-compensation']){
  const f=candidate(t,f=>{for(const c of f.sourceWorkflow.compensations)c.depends_on=[];if(mode==='forward-order')f.sourceWorkflow.compensations[1].depends_on=['first'];if(mode==='no-compensation')f.sourceWorkflow.compensations=[];});
  const selected=cases(f).filter(c=>['success','reject','throw-after','committed-bad','binding-bad'].includes(c.mode));
  assert.equal(native(f,f.plan(),selected).cases,selected.length);
 }
});

test('Python Workflow rejects stale identity, unsafe roots and unregistered policy without changing checked domain sources',t=>{
 const f=candidate(t),p=f.plan(),build=(s:any=f.selection,source:any=sources)=>planConfiguredPythonWorkflow(f.graph,f.boundary,f.fields,s,source);
 for(const delta of [{language:'typescript'},{workflow:{...f.workflow}},{policy:{...f.policy}},{actions:[]},{module_root:'../escape'},{module_root:'asyncio'}])assert.throws(()=>build({...f.selection,...delta}));
 for(const key of ['workflow_contract','materialization_contract','outcome_contract','recovery_contract'])assert.throws(()=>build(f.selection,{...sources,[key]:(sources as any)[key]+' '}));
 let invoked=0;assert.throws(()=>build({...f.selection,get policy(){invoked++;return f.policy;}}),/inert/);assert.equal(invoked,0);
 const other=candidate(t);assert.throws(()=>build({...f.selection,policy:other.policy}),/identity/);
 assert.deepEqual(build(),p);
});

test('Native Python Workflow controls kill compiling await, occurrence, uncertainty and recovery binding mutations',t=>{
 const f=candidate(t),p=f.plan(),m=p.modules[0],original=p.artifacts.find(a=>a.relative_path===m.provider_path)!.content;
 for(const change of [
  (s:string)=>s.replace('raw1 = await call0(args1, dep0)','raw1 = call0(args1, dep0)'),
  (s:string)=>s.replace('_material.steps["second"].operation_input','_material.steps["first"].operation_input'),
  (s:string)=>s.replace('commit_status="indeterminate", origin=origin','commit_status="not-committed", origin=origin'),
  (s:string)=>s.replace('observations.append(_observe(1, settlement1))','observations.append(_observe(0, settlement1))'),
  (s:string)=>s.replace('arguments=_material.compensations["first"].arguments','arguments=_material.compensations["second"].arguments'),
  (s:string)=>s.replace('if any(type(k) is not str for k in value) or type(value.get("status")) is not str:', 'if value.get("status") == "ignored":\n            pass\n        if any(type(k) is not str for k in value) or type(value.get("status")) is not str:'),
 ]){
  const copy=structuredClone(p),provider=copy.artifacts.find(a=>a.relative_path===m.provider_path)!,changed=change(original);assert.notEqual(changed,original);
  execFileSync('/usr/bin/python3',['-c','import ast,sys;compile(ast.parse(sys.stdin.read()),"<mutation>","exec")'],{input:changed});provider.content=changed;provider.sha256=sha256(changed);provider.size_bytes=Buffer.byteLength(changed);
  assert.throws(()=>native(f,copy),(e:any)=>/WORKFLOW_EVALUATION|BINDINGS_STATUS|WORKFLOW_STATUS|RECOVERY_ARGUMENT|SETTLEMENT_METADATA|ACTIVE_VALUE_EXECUTED_AND_CAUGHT/.test(e.stderr));
 }
});

test('Python Workflow joins distinct forward Operations and their explicit generated Event clocks',t=>{
 const f=candidate(t);f.sourceWorkflow.steps[2].operation_ref='commerce:release';f.save();
 const c=f.compile(),bindings=structuredClone(f.bindings);
 for(const step of bindings.steps){const ref=f.sourceWorkflow.steps.find((s:any)=>s.step_id===step.step_id).operation_ref;step.action_sha256=c.actions.find(a=>a.bindings.selector===ref)!.action_sha256;}
 for(const comp of bindings.compensations)comp.action_sha256=c.actions.find(a=>a.bindings.selector==='commerce:release')!.action_sha256;
 bindings.steps[2].events[0].input='undo_second';
 const workflow=compileWorkflowBindings(c.graph,c.boundary,c.fields,c.actions,bindings,contract);
 const policy=selectWorkflowRecoveryPolicy(workflow,{schema_version:WORKFLOW_RECOVERY_POLICY_VERSION,workflow_sha256:workflow.workflow_sha256,contract_sha256:WORKFLOW_RECOVERY_CONTRACT_SHA256,dependency_semantics:'needed-compensations-only',tie_break:'reverse-completion'},policyContract);
 const selection={...f.selection,workflow,policy,actions:c.actions},p=planConfiguredPythonWorkflow(c.graph,c.boundary,c.fields,selection,sources);
 const built={...f,...c,workflow,policy,selection};
 assert.equal(native(built,p).cases,cases(built).length);
});

test('Python Workflow whole-source controls reject runtime-invisible code even with refreshed artifact and descriptor hashes',t=>{
 const f=candidate(t),p=f.plan(),m=p.modules[0],original=p.artifacts.find(a=>a.relative_path===m.provider_path)!.content;
 const changes=[
  (s:string)=>s+'\ndef _hidden_compensation():\n    raise RuntimeError("undeclared")\n',
  (s:string)=>s.replace('    results = []','    globals()["_temporary"] = True\n    globals().pop("_temporary")\n    results = []'),
  (s:string)=>s.replace('async def execute(', 'if False:\n    import os\n\nasync def execute('),
  (s:string)=>s.replace('    value: WorkflowValue','    value: object'),
  (s:string)=>s.replace('def _digest(v):','def _digest(v):\n    if False:\n        raise RuntimeError("hidden")'),
  (s:string)=>s.replace('-> _material._Arguments4','-> _material._Arguments3'),
 ];
 for(const change of changes){
  const copy=structuredClone(p),provider=copy.artifacts.find(a=>a.relative_path===m.provider_path)!,changed=change(original);assert.notEqual(changed,original);
  execFileSync('/usr/bin/python3',['-c','import ast,sys;compile(ast.parse(sys.stdin.read()),"<mutation>","exec")'],{input:changed});
  provider.content=changed;provider.sha256=sha256(changed);provider.size_bytes=Buffer.byteLength(changed);
  const descriptor=copy.modules[0].descriptor,oldProvider=descriptor.provider_sha256,oldDescriptor=descriptor.descriptor_sha256;
  descriptor.provider_sha256=provider.sha256;const {descriptor_sha256:_,...body}=descriptor;descriptor.descriptor_sha256=sha256(canonicalJson(body));
  const wrapper=copy.artifacts.find(a=>a.relative_path===m.relative_path)!;
  wrapper.content=wrapper.content.replaceAll(oldProvider,descriptor.provider_sha256).replaceAll(oldDescriptor,descriptor.descriptor_sha256);wrapper.sha256=sha256(wrapper.content);wrapper.size_bytes=Buffer.byteLength(wrapper.content);
  const {plan_sha256:__,...planBody}=copy;copy.plan_sha256=sha256(canonicalJson(planBody));
  assert.throws(()=>native(f,copy),(e:any)=>/PYTHON_WORKFLOW_OBSERVER:(orchestration complete AST|reviewed settlement AST changed)/.test(e.stderr));
 }
 for(const target of [m.relative_path,'application/__init__.py']){
  const copy=structuredClone(p),a=copy.artifacts.find(a=>a.relative_path===target)!;
  a.content+='\n_temporary = True\ndel _temporary\n';a.sha256=sha256(a.content);a.size_bytes=Buffer.byteLength(a.content);
  assert.throws(()=>native(f,copy),(e:any)=>/PYTHON_WORKFLOW_OBSERVER:public wrapper complete AST|PYTHON_WORKFLOW_MATERIALIZATION_OBSERVER:nonempty package initializer/.test(e.stderr));
 }
});
