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
import {planConfiguredWorkflow,CONFIGURED_WORKFLOW_VERSION} from '../../src/generation/configured-workflows.ts';
import {inspectOperationSettlement,observeWorkflowStep,evaluateWorkflowOutcomeJournal,WORKFLOW_OUTCOME_JOURNAL_VERSION} from '../../src/typed-operation/workflow-outcomes.ts';
const bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8'),base='development/reconciliation-v1/profile-compiler-reconciliation/';
const rules={configuration:bytes(base+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),typescript:bytes('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json'),
 rule_contract:bytes(base+'string-order-rule-contract.json'),collection_contract:bytes(base+'rule-collection-value-contract.json'),predicate_contract:bytes(base+'rule-collection-predicate-contract.json'),numeric_contract:bytes(base+'rule-numeric-contract.json'),exact_contract:bytes(base+'rule-exact-contract.json'),literal_contract:bytes(base+'rule-exact-literal-contract.json'),structured_contract:bytes(base+'rule-structured-value-contract.json'),field_contract:bytes('development/reconciliation-v1/contracts/exact-field-and-reference-model.json')};
const operationSources={operation_contract:bytes(base+'operation-generation-contract.json'),factory_contract:bytes(base+'factory-structured-rule-contract.json'),enum_provider:bytes('impl/architecture-conformance/typescript/runtime/enum/index.ts'),rules,
 events:{configuration:rules.configuration,base:rules.base,typescript:rules.typescript,event_contract:bytes(base+'event-generation-contract.json')}};
const sources={workflow_contract:bytes(base+'workflow-generation-contract.json'),materialization_contract:bytes(base+'workflow-materialization-contract.json'),outcome_contract:bytes(base+'workflow-outcome-contract.json'),recovery_contract:policyContract,operations:operationSources};
function candidate(t:any,change?:(f:ReturnType<typeof fixture>)=>void){
 const f=fixture(t);
 f.node('identity-valid','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-IDENTITY-VALID',parameters:[{name:'id',type:scalar()}],expression:{op:'lt',left:literal('String',''),right:at('id')}}});
 change?.(f);
 const c={...f,...f.build()};
 const selection:any={schema_version:CONFIGURED_WORKFLOW_VERSION,language:'typescript',module_root:'application',workflow:c.workflow,policy:c.policy,actions:c.actions.filter(a=>[...c.workflow.steps,...c.workflow.compensations].some(s=>s.operation_ref===a.bindings.selector)),factories:[{selector:'commerce:order',base_validators:[{rule:'commerce:identity-valid',arguments:[{parameter:'id',field:'id'}]}],extensions:[]}]};
 return {...c,selection,plan:()=>planConfiguredWorkflow(c.graph,c.boundary,c.fields,selection,sources)};
}
function native(f:ReturnType<typeof candidate>,plan=f.plan()){
 const root=fs.mkdtempSync(path.join(f.temp,'native-'));
 for(const a of plan.artifacts){const p=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,a.content);}
 const chain=JSON.parse(fs.readFileSync(path.resolve(project,'../../toolchains/node-typescript/toolchain.json'),'utf8'));
 const image=nativeToolchainImage(chain.container_image);
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:[path.join(project,'impl'),...process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))]}),deps=path.dirname(path.dirname(path.dirname(types)));
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--mount','type=bind,source='+deps+',target='+deps+',readonly','--workdir',root,image];
 const compile=(...files:string[])=>execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),...plan.artifacts.map(a=>path.join(root,a.relative_path)),...files],{encoding:'utf8',stdio:'pipe'});
 compile();const entry=plan.modules[0]!,js=(p:string)=>path.join(root,'js',p.replace(/\.ts$/,'.js'));
 return {root,plan,compile,docker,js,require,run:require(js(entry.relative_path))[entry.callable],provider:require(js(entry.provider_path)),material:require(js(entry.material_path))};
}
const parameters=()=>{
 const post=(id:string)=>({occurrence:{'event-id':id},payload:{'order-id':'o',delta:'-1'},occurredAt:'2026-09-09'});
 const undo=(id:string)=>({occurrence:{'event-id':id},payload:{'order-id':'o'}});
 return {order:{id:'o'},amount:'18446744073709551615',post_first:post('p1'),post_second:post('p2'),undo_first:undo('u1'),undo_second:undo('u2')};
};
const ids={workflow_execution_id:'execution-one',failure_occurrence_id:'failure-one'};
function provider(failureIndex=-1,mode='reject'){
 let calls=0;const commits:any[]=[],trace:string[]=[];
 const dependency={store:{begin:async()=>{
  const i=calls++;trace.push('begin:'+i);
  return {read:async()=>{throw Error('undeclared read');},rollback:async()=>{trace.push('rollback:'+i);},
   commit:async(batch:any)=>{trace.push('commit:'+i);if(i===failureIndex&&mode==='reject')return {status:'rejected'};if(i===failureIndex&&mode==='throw-before')throw Error('unknown');commits.push(batch);if(i===failureIndex&&mode==='throw-after')throw Error('lost acknowledgement');return {status:'committed'};}};
 }}};
 return {dependency,commits,trace,count:()=>calls};
}
test('native Workflow awaits real generated Operations and returns exact R01 evidence with owned result',async t=>{
 const f=candidate(t),n=native(f),store=provider(),raw=parameters();
 const result=await n.run(raw,ids,{'commerce:post':store.dependency});
 assert.equal(result.status,'succeeded');assert.equal(result.value.id,'o');assert.equal(store.count(),3);assert.equal(store.commits.length,3);
 assert.deepEqual(store.trace,['begin:0','commit:0','begin:1','commit:1','begin:2','commit:2']);assert.ok(Object.isFrozen(result));assert.ok(Object.isFrozen(result.value));
 const observations=f.workflow.steps.map(s=>observeWorkflowStep(f.workflow,s.step_id,{kind:'returned',outcome:{status:'committed',value:{id:'o'}}},sources.outcome_contract));
 assert.deepEqual(result.evaluation,evaluateWorkflowOutcomeJournal(f.policy,{schema_version:WORKFLOW_OUTCOME_JOURNAL_VERSION,...ids,failure_occurrence_id:null,observations,local_error:null}));
 assert.equal(result.recovery_bindings,null);
});
test('every known failure prefix preserves selected recovery intent and typed compensation bindings without dispatch',async t=>{
 const f=candidate(t),n=native(f);
 for(let i=0;i<3;i++){
  const s=provider(i),r=await n.run(parameters(),ids,{'commerce:post':s.dependency});
  assert.equal(r.status,'forward-stopped');assert.equal(s.count(),i+1);assert.equal(s.commits.length,i);
  const expected=planSelectedWorkflowRecovery(f.policy,{schema_version:WORKFLOW_FAILURE_JOURNAL_VERSION,...ids,completed_step_ids:f.workflow.steps.slice(0,i).map(s=>s.step_id),failed_step_id:f.workflow.steps[i]!.step_id,failed_commit_status:'not-committed'});
  assert.deepEqual(r.evaluation.recovery,expected);
  if(i===0){assert.equal(r.bindings_status,'not-required');assert.equal(r.recovery_bindings,null);}
  else{
   const intent=expected.recovery_intent!;assert.equal(r.recovery_bindings.intent_id,intent.intent_id);
   assert.deepEqual(r.recovery_bindings.bindings.map((b:any)=>b.compensation_id),intent.plan.map(p=>p.compensation_id));
   for(const b of r.recovery_bindings.bindings){assert.equal(b.arguments.amount,18446744073709551615n);assert.equal(b.arguments.order.id,'o');assert.equal(b.invocation_identity,intent.plan.find(p=>p.compensation_id===b.compensation_id)!.invocation_identity);assert.ok(Object.isFrozen(b.arguments));assert.equal(Object.hasOwn(b.arguments.notice_input,'occurredAt'),false);}
  }
 }
});
test('uncertain commits at every position require reconciliation even when the provider did commit',async t=>{
 const f=candidate(t),n=native(f);
 for(let i=0;i<3;i++)for(const mode of ['throw-before','throw-after']){
  const s=provider(i,mode),r=await n.run(parameters(),ids,{'commerce:post':s.dependency});
  assert.equal(s.count(),i+1);assert.equal(s.commits.length,i+(mode==='throw-after'?1:0));
  assert.equal(r.evaluation.recovery_status,'reconciliation-required');assert.equal(r.recovery_bindings,null);
  assert.deepEqual(r.evaluation.completed_step_ids,f.workflow.steps.slice(0,i).map(s=>s.step_id));
 }
});

function observeNative(f:ReturnType<typeof candidate>,n:ReturnType<typeof native>){
 const m=n.plan.modules[0]!;
 fs.writeFileSync(path.join(n.root,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'commonjs'},files:n.plan.artifacts.map(a=>a.relative_path)}));
 const prefix_templates=f.workflow.steps.map((failed,i)=>{
  const r=planSelectedWorkflowRecovery(f.policy,{schema_version:WORKFLOW_FAILURE_JOURNAL_VERSION,...ids,completed_step_ids:f.workflow.steps.slice(0,i).map(s=>s.step_id),failed_step_id:failed.step_id,failed_commit_status:'not-committed'}),intent=r.recovery_intent;
  return {steps:f.workflow.steps.slice(0,i).map(s=>({step_id:s.step_id,operation_ref:s.operation_ref,action_sha256:s.action_sha256})),plan:intent?intent.plan.map(({invocation_identity,...row})=>row):[],plan_digest:intent?.plan_digest??null};
 });
 const expected={provider_path:m.provider_path,module_root:'application',occurrences:f.sourceWorkflow,bindings:f.bindings,policy_sha256:f.policy.policy_sha256,
  actions:Object.fromEntries(n.plan.operation_plan.modules.map(m=>[m.selector,m.descriptor])),
  wf:{hash:f.workflow.workflow_sha256,selector:f.workflow.bindings.selector,steps:f.workflow.steps.map(s=>({step_id:s.step_id,operation_ref:s.operation_ref,action_sha256:s.action_sha256}))},prefix_templates};
 fs.writeFileSync(path.join(n.root,'expected.json'),JSON.stringify(expected));
 fs.copyFileSync(path.join(project,'impl/cli/tools/observe-configured-workflows.mjs'),path.join(n.root,'observer.mjs'));
 try{return JSON.parse(execFileSync('docker',[...n.docker,'node',path.join(n.root,'observer.mjs'),n.root,path.join(n.root,'expected.json')],{encoding:'utf8',stdio:'pipe'}));}
 catch(e:any){if(e.stdout)return JSON.parse(e.stdout);throw e;}
}
test('native settlement specialization agrees with R01 across malformed metadata and every failure stage',t=>{
 const n=native(candidate(t)),inspect=n.provider.inspectOperationSettlement;
 for(const stage of ['input','begin','read','guard','write-validation','event','result','commit','unknown'])
  for(const status of ['failed','rejected','indeterminate','unknown'])
   for(const code of ['OPERATION_INPUT','BEGIN_FAILED','OPERATION_FAILED','READ_NOT_FOUND','READ_IDENTITY_MISMATCH','RULE_REJECTED:commerce:allowed','COMMIT_REJECTED','COMMIT_INDETERMINATE','INVALID_COMMIT_RECEIPT','COMMIT_UNCERTAIN','UNKNOWN'])
    for(const cleanupFailed of [false,true]){
     const value={stage,status,code,cleanupFailed,continuation:'return-post-error'};
     assert.deepEqual(inspect(value,'return-post-error'),inspectOperationSettlement(value,'return-post-error'));
    }
 let read=0;const payload={};Object.defineProperty(payload,'id',{enumerable:true,get(){read++;return 'o';}});
 for(const value of [undefined,null,{},42,{status:'committed',value:payload},{status:'committed',value:1n,extra:1},{status:'failed',stage:'input',code:'OPERATION_INPUT',continuation:'other',cleanupFailed:false}])assert.deepEqual(inspect(value,'return-post-error'),inspectOperationSettlement(value,'return-post-error'));
 assert.equal(read,0);
});
test('malformed or throwing imported dependencies preserve uncertainty; invalid committed values preserve committed evidence',async t=>{
 const f=candidate(t),n=native(f),op=n.plan.operation_plan.modules.find(m=>m.selector==='commerce:post')!,exports=n.require(n.js(op.relative_path)),original=exports[op.callable];
 for(const kind of ['throws','malformed','bad-value','getter']){
  let count=0,getters=0;
  const replacement=Object.assign(async()=>{
   count++;if(count===1)return {status:'committed',value:{id:'first'}};
   if(kind==='throws')throw Error('dependency');
   if(kind==='malformed')return {status:'success',value:{id:'x'}};
   if(kind==='getter'){const value={};Object.defineProperty(value,'id',{enumerable:true,get(){getters++;return 'o';}});return {status:'committed',value};}
   return {status:'committed',value:{id:17}};
  },{descriptor:original.descriptor});
  exports[op.callable]=replacement;
  const r=await n.run(parameters(),ids,{'commerce:post':provider().dependency});
  assert.equal(count,2);assert.equal(getters,0);assert.equal(r.recovery_bindings,null);
  if(kind==='bad-value'||kind==='getter'){assert.equal(r.status,'orchestration-error');assert.deepEqual(r.evaluation.completed_step_ids,['first','second']);assert.equal(r.evaluation.recovery_status,'not-evaluable');}
  else{assert.equal(r.status,'forward-stopped');assert.equal(r.evaluation.recovery_status,'reconciliation-required');assert.deepEqual(r.evaluation.completed_step_ids,['first']);}
 }
 exports[op.callable]=original;
 const replacement=Object.assign(async()=>{throw Error('must not run');},{descriptor:{...original.descriptor,action_sha256:'0'.repeat(64)}});
 exports[op.callable]=replacement;
 await assert.rejects(n.run(parameters(),ids,{'commerce:post':provider().dependency}),/identity/);
});
test('input and dependency slots are captured before suspension and each commit is awaited before next step',async t=>{
 const f=candidate(t),n=native(f),raw=parameters();
 let release!:()=>void;const gate=new Promise<void>(resolve=>release=resolve),seen:any[]=[];let begun=0;
 const dependency={store:{begin:async()=>{const i=begun++;return {read:async()=>null,rollback:async()=>{},commit:async(batch:any)=>{seen.push(batch);if(i===0)await gate;return {status:'committed'};}};}}};
 const dependencies={'commerce:post':dependency},pending=n.run(raw,ids,dependencies);
 await new Promise(resolve=>setImmediate(resolve));
 assert.equal(begun,1);raw.order.id='mutated';raw.post_second.payload['order-id']='mutated';
 dependencies['commerce:post']={store:{begin:async()=>{throw Error('replaced slot');}}} as any;
 release();const r=await pending;
 assert.equal(r.status,'succeeded');assert.equal(r.value.id,'o');assert.equal(begun,3);assert.equal(seen[1].events[0].value.payload['order-id'],'o');
});
test('entry validation rejects hostile input, identities and dependency descriptors before effects',async t=>{
 const n=native(candidate(t)),s=provider();let getters=0;
 for(const identity of [{...ids,failure_occurrence_id:''},{...ids,workflow_execution_id:'bad id'},{...ids,extra:true}])await assert.rejects(n.run(parameters(),identity,{'commerce:post':s.dependency}));
 const p=parameters();Object.defineProperty(p.order,'id',{enumerable:true,get(){getters++;return 'x';}});
 await assert.rejects(n.run(p,ids,{'commerce:post':s.dependency}));
 const dependencies={};Object.defineProperty(dependencies,'commerce:post',{enumerable:true,get(){getters++;return s.dependency;}});
 await assert.rejects(n.run(parameters(),ids,dependencies));assert.equal(getters,0);assert.equal(s.count(),0);
});
test('selected constrained and unconstrained recovery and no-compensation workflows compile and execute',async t=>{
 for(const kind of ['ordered','unordered','none']){
  const f=candidate(t,f=>{
   f.sourceWorkflow.compensations[0].depends_on=[];
   f.sourceWorkflow.compensations[1].depends_on=kind==='ordered'?['first']:[];
   if(kind==='none')f.sourceWorkflow.compensations=[];
  }),n=native(f),s=provider(2),r=await n.run(parametersFor(f),ids,{'commerce:post':s.dependency});
  if(kind==='none'){assert.equal(r.bindings_status,'not-required');assert.equal(r.recovery_bindings,null);}
  else assert.deepEqual(r.recovery_bindings.bindings.map((b:any)=>b.compensation_id),kind==='ordered'?['first','second']:['second','first']);
  assert.equal(s.count(),3);assert.equal(observeNative(f,n).result,'pass');
 }
});
function parametersFor(f:ReturnType<typeof candidate>){
 const p:any=parameters();for(const k of ['post_first','post_second','undo_first','undo_second'])if(!f.workflow.event_inputs.some(e=>e.name===k))delete p[k];return p;
}
test('independent AST observer rejects compiling await, order, argument, pin, prefix and effect mutants',async t=>{
 const f=candidate(t),n=native(f),file=path.join(n.root,n.plan.modules[0]!.provider_path),source=fs.readFileSync(file,'utf8');
 assert.equal(observeNative(f,n).result,'pass');
 const mutants=[
  source.replace('raw=await call0(args,dep0);','raw=call0(args,dep0);'),
  source.replace('args=material.steps["first"].arguments(input,results)','args=material.steps["second"].arguments(input,results)'),
  source.replace('observations.push(observe(0,settlement))','observations.push(observe(1,settlement))'),
  source.replace('if(settlement.commit_status!=="committed")return stopped(input,results,observations,ids);','if(false)return stopped(input,results,observations,ids);'),
  source.replace(n.plan.modules[0]!.descriptor.operation_imports[0]!.descriptor_sha256,'0'.repeat(64)),
  source.replace("observations.filter(r=>r.settlement.commit_status==='committed')","observations.filter(r=>r.settlement.commit_status!=='committed')"),
  'import {operationRelease as forbidden} from "../operations/release.js";\n'+source.replace('let value:ReturnType<typeof material.result>;','void forbidden(material.compensations["first"].arguments(input,results),{store:{begin:async()=>({read:async()=>null,rollback:async()=>{},commit:async()=>({status:"committed"})})},clocks:{notice:()=>"2026-09-09"}});let value:ReturnType<typeof material.result>;'),
  source+'\nconst dispatch=()=>undefined;dispatch();\n'
 ];
 for(const content of mutants){assert.notEqual(content,source);fs.writeFileSync(file,content);n.compile();const observed=observeNative(f,n);assert.equal(observed.result,'fail',JSON.stringify(observed));}
});

test('distinct reserve, payment and submit Operations preserve exact native import and call order',async t=>{
 const f=candidate(t),operations=['reserve-stock','capture-payment','submit-order'];
 const edge=(id:string,relationship:string,from:string,to:string)=>{f.edges.push(id);f.write('specs/commerce/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',edge_id:id,feature_id:'commerce',relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
 f.edges.splice(f.edges.indexOf('flow-post'),1);
 for(const [i,id]of operations.entries()){
  f.node(id,'Operation',{reads:[],writes:[],effects:['notice'],guard:'allowed',failure_continuation:'return-'+id+'-error'});
  f.node(id+'-done','Event',{event_type:id+'-done',version:'1',occurrence_id:{field_id:'event-id',type_ref:{kind:'primitive',name:'uuid'},required:true},occurred_at_policy:'required',payload:[{field_id:'order-id',type_ref:{kind:'reference',selector:'commerce:order'},required:true},{field_id:'delta',type_ref:{kind:'primitive',name:'integer'},required:false}]});
  edge(id+'-guard','enforces','allowed',id);edge(id+'-event','produces',id,id+'-done');edge('flow-'+id,'orchestrates','flow',id);
  const definition={...structuredClone(f.definitions[0]),selector:'commerce:'+id};definition.events[0].target='commerce:'+id+'-done';f.definitions.push(definition);
  f.sourceWorkflow.steps[i].operation_ref='commerce:'+id;
 }
 f.save();const c=f.compile(),b=structuredClone(f.bindings);
 b.event_inputs=b.event_inputs.filter((e:any)=>e.name.startsWith('undo_'));
 for(const [i,s]of b.steps.entries()){
  s.action_sha256=c.actions.find(a=>a.bindings.selector==='commerce:'+operations[i])!.action_sha256;
  s.events[0].input='post_'+s.step_id;b.event_inputs.push({name:s.events[0].input,event_ref:'commerce:'+operations[i]+'-done'});
 }
 for(const s of b.compensations)s.action_sha256=c.actions.find(a=>a.bindings.selector==='commerce:release')!.action_sha256;
 const actions=c.actions.filter(a=>a.bindings.selector!=='commerce:post');
 const workflow=compileWorkflowBindings(c.graph,c.boundary,c.fields,actions,b,contract);
 const policy=selectWorkflowRecoveryPolicy(workflow,{...f.selection.policy.selection,workflow_sha256:workflow.workflow_sha256},policyContract);
 const selection={...f.selection,workflow,policy,actions};
 const updated={...f,...c,bindings:b,workflow,policy,selection,plan:()=>planConfiguredWorkflow(c.graph,c.boundary,c.fields,selection,sources)};
 const n=native(updated),trace:string[]=[];
 const dependencies=Object.fromEntries(operations.map(name=>['commerce:'+name,{store:{begin:async()=>{trace.push(name);return {read:async()=>null,rollback:async()=>{},commit:async()=>({status:'committed'})};}}}]));
 const input={...parameters(),post_third:parameters().post_second};
 const r=await n.run(input,ids,dependencies);assert.equal(r.status,'succeeded');assert.deepEqual(trace,operations);assert.equal(observeNative(updated,n).result,'pass');
 const p=n.plan.modules[0]!.provider_path,original=n.plan.artifacts.find(a=>a.relative_path===p)!.content;
 const changed=original.replace('raw=await call1(args,dep1);','raw=await call0(args,dep0);');assert.notEqual(changed,original);
 const mutated=native(updated,{...n.plan,artifacts:n.plan.artifacts.map(a=>a.relative_path===p?{...a,content:changed}:a)});
 assert.equal(observeNative(updated,mutated).result,'fail');
 trace.length=0;await mutated.run(input,ids,dependencies);assert.notDeepEqual(trace,operations);
});
test('planner rejects stale identities, definitions, incomplete action closure and unsafe module paths without caller mutation',t=>{
 const f=candidate(t),build=(s=f.selection,c=sources)=>planConfiguredWorkflow(f.graph,f.boundary,f.fields,s,c);
 const plan=build();assert.ok(Object.isFrozen(plan));assert.equal(Object.isFrozen(f.selection),false);assert.equal(Object.isFrozen(f.selection.actions),false);
 assert.deepEqual(build(),plan);
 for(const selection of [{...f.selection,workflow:{...f.workflow}},{...f.selection,policy:{...f.policy}},{...f.selection,language:'python'},{...f.selection,module_root:'../escape'},{...f.selection,module_root:'CON'},{...f.selection,actions:f.selection.actions.slice(0,1)},{...f.selection,extra:true}])assert.throws(()=>build(selection));
 for(const key of ['workflow_contract','materialization_contract','outcome_contract','recovery_contract'])assert.throws(()=>build(f.selection,{...sources,[key]:(sources as any)[key]+' '}));
 const changed=structuredClone(f.bindings);changed.result.value=result('first');
 const workflow=compileWorkflowBindings(f.graph,f.boundary,f.fields,f.actions,changed,contract);
 assert.throws(()=>build({...f.selection,workflow}));
 let calls=0;const accessor={...f.selection};Object.defineProperty(accessor,'workflow',{enumerable:true,get(){calls++;return f.workflow;}});
 assert.throws(()=>build(accessor));assert.equal(calls,0);
 fs.rmSync(f.source,{recursive:true,force:true});assert.deepEqual(build(),plan);
});
test('native Workflow declarations preserve typed inputs outcomes and materialized compensation arguments',t=>{
 const n=native(candidate(t)),m=n.plan.modules[0]!,relative='./'+m.relative_path.replace(/\.ts$/,'');
 const file=path.join(n.root,'consumer.ts');
 fs.writeFileSync(file,'import {'+m.callable+',type WorkflowInput,type WorkflowDependencies} from '+JSON.stringify(relative)+';\ndeclare const input:WorkflowInput;declare const dependencies:WorkflowDependencies;\nasync function use(){const r=await '+m.callable+'(input,{workflow_execution_id:"run",failure_occurrence_id:"failure"},dependencies);if(r.status==="succeeded"){const id:string=r.value.id;}else if(r.recovery_bindings){for(const b of r.recovery_bindings.bindings){const amount:bigint=b.arguments.amount;const id:string=b.arguments.order.id;}}}\n// @ts-expect-error exact Workflow fields\nconst invalid:WorkflowInput={order:{id:"x"}};\n// @ts-expect-error identity is explicit and separate\n'+m.callable+'(input,dependencies);\n');
 n.compile(file);
});
test('local final and recovery binding failures never invent a failed Operation or execute compensation',async t=>{
 const f=candidate(t),n=native(f),material=n.material,original=material.result;
 material.result=()=>{throw Error('bad final');};
 const s=provider(),r=await n.run(parameters(),ids,{'commerce:post':s.dependency});
 assert.equal(r.status,'orchestration-error');assert.deepEqual(r.evaluation.completed_step_ids,['first','second','third']);assert.equal(r.evaluation.recovery_status,'not-evaluable');assert.equal(s.count(),3);
 material.result=original;
 const originalComps=material.compensations;material.compensations={...originalComps,first:{...originalComps.first,arguments:()=>{throw Error('binding');}}};
 const failed=provider(2),recovery=await n.run(parameters(),ids,{'commerce:post':failed.dependency});
 assert.equal(recovery.bindings_status,'failed');assert.equal(recovery.evaluation.recovery.workflow_evaluation_result,'recovery-required');assert.ok(recovery.evaluation.recovery.recovery_intent);assert.equal(recovery.recovery_bindings,null);assert.equal(failed.count(),3);
});

test('generated Workflow retains Operation guards, result invariants and cleanup evidence',async t=>{
 for(const kind of ['guard','cleanup','result']){
  const f=candidate(t,f=>{if(kind!=='result')f.definitions[0].guards[0].arguments[0].value=literal('Bool',false);}),n=native(f);
  let begins=0,commits=0,rollbacks=0;
  const dependency={store:{begin:async()=>{begins++;return {read:async()=>null,commit:async()=>{commits++;return {status:'committed'};},rollback:async()=>{rollbacks++;if(kind==='cleanup')throw Error('cleanup');}};}}};
  const p=parameters();if(kind==='result')p.order.id='';
  const r=await n.run(p,ids,{'commerce:post':dependency});
  assert.equal(r.status,'forward-stopped');assert.equal(begins,1);assert.equal(commits,0);assert.equal(rollbacks,1);
  assert.equal(r.evaluation.failure.stage,kind==='result'?'result':'guard');
  assert.equal(r.evaluation.failure.cleanup_failed,kind==='cleanup');
  assert.equal(r.evaluation.recovery.workflow_evaluation_result,'not-required');
 }
});
test('argument preparation failure is not-started rather than an invented returned Operation failure',async t=>{
 const f=candidate(t),n=native(f),steps=n.material.steps;
 n.material.steps={...steps,second:{...steps.second,arguments:()=>{throw Error('preparation');}}};
 const s=provider(),r=await n.run(parameters(),ids,{'commerce:post':s.dependency});
 assert.equal(s.count(),1);assert.deepEqual(r.evaluation.completed_step_ids,['first']);assert.equal(r.evaluation.failure.origin,'not-started');assert.equal(r.evaluation.failure.status,null);assert.equal(r.evaluation.failure.continuation,null);assert.equal(r.bindings_status,'ready');
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
