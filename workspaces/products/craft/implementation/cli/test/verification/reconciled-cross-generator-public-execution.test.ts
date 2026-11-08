import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {crossGeneratorPublicFixture} from '../helpers/cross-generator-public.ts';
import {workflowFixture} from '../helpers/workflow-verification.ts';
import {stateMachineFixture} from '../helpers/state-machine-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {prepareCrossGeneratorVerification} from '../../src/verification/reconciled-cross-generator-public.ts';
import {executePreparedCrossGeneratorVerification, assertCrossGeneratorAggregateCurrent, retainedWorkflowExecutionBindings} from '../../src/verification/reconciled-cross-generator-public-execution.ts';

const project = path.resolve(import.meta.dirname, '../../../..'), cli = path.join(project, 'impl/cli');
function native(t: any, kind: 'scalar' | 'compound' | 'state' | 'rule-only' = 'scalar', module_root = 'domain') {
  const f = kind === 'compound' ? crossGeneratorPublicFixture(t) : kind === 'state' ? stateMachineFixture(t) : workflowFixture(t);
  let source = 'source' in f ? f.source : path.join(f.root, 'source'), selection = {...f.selection, module_root};
  if (kind === 'rule-only') {
    const rule = fs.readFileSync(path.join(source, 'specs/commerce/nodes/allowed.json'), 'utf8');
    source = path.join(f.root, 'only-rule'); fs.mkdirSync(path.join(source, 'specs/commerce/nodes'), {recursive: true});
    fs.writeFileSync(path.join(source, 'project.json'), JSON.stringify({schema_version: 'domainspec.project/v1', project_id: 'rule-only', features: ['commerce'], cross_feature_edges: []}));
    fs.writeFileSync(path.join(source, 'specs/commerce/feature.json'), JSON.stringify({schema_version: 'domainspec.feature/v1', feature_id: 'commerce', nodes: ['allowed'], edges: []}));
    fs.writeFileSync(path.join(source, 'specs/commerce/nodes/allowed.json'), rule);
    selection = {...selection, factories: [], operations: [], workflows: []};
  }
  const require = createRequire(import.meta.url), types = fs.realpathSync(require.resolve('@types/node/package.json', {paths: process.execArgv.filter(a => a.endsWith('loader.mjs')).map(p => path.dirname(p))}));
  const nodeRoot = path.dirname(types), deps = path.dirname(path.dirname(nodeRoot)), undici = path.dirname(createRequire(types).resolve('undici-types/package.json'));
  const dist = path.join(f.root, 'dist'); fs.mkdirSync(dist); fs.writeFileSync(path.join(f.root, 'package.json'), '{"type":"module"}');
  const image = nativeToolchainImage();
  assert.equal(image, NATIVE_TEST_IMAGE_ID);
  const docker = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(),
    '--mount', 'type=bind,source=' + project + ',target=' + project + ',readonly', '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly',
    '--mount', 'type=bind,source=' + undici + ',target=' + undici + ',readonly', '--mount', 'type=bind,source=' + f.root + ',target=' + f.root, '--workdir', f.root, image];
  const command = (args: string[]) => {
    try {return execFileSync('docker', [...docker, ...args], {encoding: 'utf8', stdio: 'pipe', timeout: 600000, maxBuffer: 16777216});}
    catch (e: any) {throw Error([e.message, e.stdout, e.stderr].filter(Boolean).join('\n'));}
  };
  command(['tsc', '--ignoreConfig', '--strict', '--types', 'node', '--typeRoots', path.join(deps, '@types'), '--target', 'ES2022', '--module', 'NodeNext',
    '--rootDir', path.join(cli, 'src'), '--outDir', dist, path.join(cli, 'src/verification/reconciled-cross-generator-public-execution.ts')]);
  const prefix = String.raw`import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import cp from 'node:child_process'; import {syncBuiltinESMExports,createRequire} from 'node:module';
import {loadCompiledProjectGraph} from './dist/input/project-model.js';
import {planCompiledReconciledProject} from './dist/generation/reconciled-project.js';
import {prepareCrossGeneratorVerification,crossGeneratorPreparationBindings} from './dist/verification/reconciled-cross-generator-public.js';
import {crossGeneratorWorkflowBatchProbes} from './dist/verification/reconciled-cross-generator-workflow.js';
import {createWorkflowProtocolCases} from './dist/verification/reconciled-workflow-protocol-cases.js';
import {workflowVerificationDefinitions} from './dist/verification/reconciled-workflow-controls.js';
import {getCrossGeneratorSource} from './dist/verification/cross-generator-sources.js';
import {executePreparedCrossGeneratorVerification,assertCrossGeneratorAggregateCurrent,retainedWorkflowExecutionBindings} from './dist/verification/reconciled-cross-generator-public-execution.js';
import {assertCrossGeneratorWorkflowExecutionCurrent} from './dist/verification/reconciled-cross-generator-workflow-execution.js';
import {canonicalJson,sha256} from './dist/input/source-manifest.js';
const sourcePath=__SOURCE__,selection=__SELECTION__,root=__ROOT__;
const graph=loadCompiledProjectGraph(sourcePath),plan=planCompiledReconciledProject(graph,selection),prepared=prepareCrossGeneratorVerification(graph,plan);
const options={workspace_parent:root,typescript_root:'/opt/node-toolchain/node_modules/typescript',node_types_root:__TYPES__};
const execute=()=>executePreparedCrossGeneratorVerification(prepared,graph,plan,options);
const assertWorkflowCustody=r=>{
 const bound=retainedWorkflowExecutionBindings(r,prepared,graph,plan);
 assert.ok(Object.isFrozen(bound)&&Object.isFrozen(bound.rows));
 assert.equal(bound.binding,crossGeneratorPreparationBindings(prepared,graph,plan).bindings.workflow);
 assert.deepEqual(bound.rows,r.rows.filter(row=>row.family==='workflow'));
 const summary=r.retained.find(row=>row.family==='workflow');
 if(summary){
  assert.ok(bound.receipt);assertCrossGeneratorWorkflowExecutionCurrent(bound.receipt);
  assert.equal(bound.receipt,retainedWorkflowExecutionBindings(r,prepared,graph,plan).receipt);
  assert.notEqual(bound.receipt,summary);assert.equal(bound.receipt.observation_sha256,summary.observation_sha256);
  assert.equal(bound.receipt.controls_sha256,bound.binding.value.controls.controls_sha256);
  assert.equal(bound.receipt.audit_sha256,bound.binding.value.audit.audit_sha256);
  assert.equal(bound.receipt.surface_sha256,bound.binding.value.surface.surface_sha256);
  assert.deepEqual(bound.receipt.audits,summary.audits);assert.equal(Object.keys(bound.receipt.audits).length,6);
  assert.deepEqual(bound.receipt.outcome,summary.outcome);
  assert.throws(()=>assertCrossGeneratorWorkflowExecutionCurrent(structuredClone(bound.receipt)),/registered execution/);
 }else assert.equal(bound.receipt,null);
 assert.throws(()=>retainedWorkflowExecutionBindings(structuredClone(r),prepared,graph,plan),/registered aggregate/);
 assert.throws(()=>retainedWorkflowExecutionBindings(r,structuredClone(prepared),graph,plan),/foreign aggregate/);
 assert.throws(()=>retainedWorkflowExecutionBindings(r,prepared,structuredClone(graph),plan),/foreign aggregate/);
 assert.throws(()=>retainedWorkflowExecutionBindings(r,prepared,graph,structuredClone(plan)),/foreign aggregate/);
 const other=prepareCrossGeneratorVerification(graph,plan);assert.equal(other.preparation_sha256,prepared.preparation_sha256);
 assert.throws(()=>retainedWorkflowExecutionBindings(r,other,graph,plan),/foreign aggregate/);
 return bound;
};
const assertWorkflowTransport=()=>{
 const binding=crossGeneratorPreparationBindings(prepared,graph,plan).bindings.workflow;assert.equal(binding.state,'prepared');
 const controls=binding.value.controls,probes=crossGeneratorWorkflowBatchProbes(controls);
 for(const row of controls.rows.filter(r=>r.state==='ready')){
  assert.ok(row.batches.length<=4);const selected=probes.filter(p=>p.rows[0].selector===row.selector);
  assert.deepEqual(selected.flatMap(p=>p.rows[0].cases.map(c=>c.id)),row.cases.map(c=>c.id));
  for(const payload of selected){
   assert.ok(payload.batch.count<=4096);assert.ok(Buffer.byteLength(canonicalJson(payload))<=8388608);
   assert.ok(payload.rows[0].cases.every(c=>Object.keys(c).sort().join(',')==='data,id'));
   const observation={controls_sha256:controls.controls_sha256,selector:row.selector,identity:row.identity,descriptor:row.descriptor,material_descriptor:row.material_descriptor,batch:payload.batch,cases:row.cases.slice(payload.batch.start,payload.batch.start+payload.batch.count).map(c=>({id:c.id,...c.expected}))};
   assert.ok(Buffer.byteLength(canonicalJson(observation))<=8388608);
  }
 }
};
`;
  return {...f, source, selection, run: (body: string) => {
    const client = path.join(f.root, 'client.mjs');
    fs.writeFileSync(client, prefix.replace('__SOURCE__', JSON.stringify(source)).replace('__SELECTION__', JSON.stringify(selection)).replace('__ROOT__', JSON.stringify(f.root)).replace('__TYPES__', JSON.stringify(nodeRoot)) + body);
    return JSON.parse(command(['node', client]));
  }};
}

test('aggregate rejects cloned inputs, active options, unsafe workspace roots and source drift before any write', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection), p = prepareCrossGeneratorVerification(f.graph, plan);
  const toolsRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-aggregate-negative-tools-'));
  t.after(() => fs.rmSync(toolsRoot, {recursive: true, force: true}));
  const typescriptRoot = path.join(toolsRoot, 'typescript'), nodeTypesRoot = path.join(toolsRoot, 'node-types');
  fs.mkdirSync(typescriptRoot); fs.mkdirSync(nodeTypesRoot);
  const options = {workspace_parent: f.root, typescript_root: typescriptRoot, node_types_root: nodeTypesRoot}, before = fs.readdirSync(f.root);
  const run = (prepared = p, opts = options) => executePreparedCrossGeneratorVerification(prepared, f.graph, plan, opts);
  const rejectedBeforeWrite = (action: () => unknown, expected: RegExp) => {
    assert.throws(action, expected);
    assert.deepEqual(fs.readdirSync(f.root), before);
    assert.deepEqual(fs.readdirSync(typescriptRoot), []);
    assert.deepEqual(fs.readdirSync(nodeTypesRoot), []);
  };
  rejectedBeforeWrite(() => run(structuredClone(p)), /registered preparation/);
  rejectedBeforeWrite(() => executePreparedCrossGeneratorVerification(p, f.graph, structuredClone(plan), options), /foreign/);
  rejectedBeforeWrite(() => assertCrossGeneratorAggregateCurrent(p), /registered aggregate/);
  let receiptReads = 0;
  const activeReceipt = Object.defineProperty({}, 'report_sha256', {get() {receiptReads++; return 'fake';}});
  for (const value of [p, structuredClone(p), activeReceipt, null, false]) {
    rejectedBeforeWrite(() => retainedWorkflowExecutionBindings(value, p, f.graph, plan), /registered aggregate/);
  }
  assert.equal(receiptReads, 0);
  let reads = 0; const active: any = {...options};
  Object.defineProperty(active, 'typescript_root', {enumerable: true, get() {reads++; return '/tmp';}});
  rejectedBeforeWrite(() => run(p, active), /closed data tool options/); assert.equal(reads, 0);
  rejectedBeforeWrite(() => run(p, {...options, extra: true} as any), /closed data tool options/);
  for (const workspace_parent of [f.graph.project_root, typescriptRoot, nodeTypesRoot]) {
    rejectedBeforeWrite(() => run(p, {...options, workspace_parent}), /inside source or tool root/);
  }
  const file = path.join(f.root, 'source/specs/commerce/nodes/allowed.json'), original = fs.readFileSync(file);
  try {
    fs.appendFileSync(file, ' ');
    rejectedBeforeWrite(() => run(), /original source changed/);
  } finally { fs.writeFileSync(file, original); }
  assert.deepEqual(fs.readFileSync(file), original);
  assert.deepEqual(fs.readdirSync(f.root), before);
});

test('all seven families execute together over the complete compound model in both layouts', t => {
  for (const layout of ['domain', 'application/domain']) {
    const f = native(t, 'compound', layout), result = f.run(`
assertWorkflowTransport();const r=execute(); assertCrossGeneratorAggregateCurrent(r);assertWorkflowCustody(r);
assert.equal(r.result,'pass',JSON.stringify({families:r.families,issues:r.currentness_issues,rows:r.rows.filter(x=>!['pass','inapplicable'].includes(x.result))}));
assert.equal(r.retained_family_count,7);assert.equal(r.executed_family_count,7);assert.equal(r.roots.length,14);assert.equal(r.edges.length,50);
assert.ok(r.families.every(f=>f.result==='pass'));assert.ok(r.edges.filter(e=>e.behavior_required).every(e=>e.execution_status==='pass'));
assert.deepEqual(r.currentness_issues,[]);
const workflow=r.retained.find(x=>x.family==='workflow');assert.equal(workflow.outcome.tested_case_count,12472);assert.equal(workflow.outcome.tested_call_count,20369);
assert.equal(Object.keys(workflow.audits).length,6);for(const family of r.retained.filter(x=>x.family!=='workflow'))assert.equal(Object.keys(family.audits).length,2);
assert.equal(r.rows.find(x=>x.family==='workflow').batch_count,4);
assert.equal(r.rows.find(x=>x.family==='value-producer'&&x.selector==='commerce:priority').case_count,1);
assert.equal(r.public_cross_generator_behavior,'not_evaluable');assert.equal(r.authority_effect,'none');
const {report_sha256,...body}=r;assert.equal(sha256(canonicalJson(body)),report_sha256);
assert.throws(()=>assertCrossGeneratorAggregateCurrent(structuredClone(r)),/registered aggregate/);
console.log(JSON.stringify({result:r.result,families:r.retained_family_count,cases:workflow.outcome.tested_case_count,calls:workflow.outcome.tested_call_count,edges:r.edges.length}));
`); t.diagnostic(JSON.stringify({layout, ...result}));
  }
});

test('unavailable factory witnesses stay incomplete while the other full compound native families execute', t => {
  const f = native(t, 'compound'), file = path.join(f.source, 'specs/commerce/nodes/positive.json'), raw = JSON.parse(fs.readFileSync(file, 'utf8'));
  raw.body.typed_contract.expression = {op: 'eq', left: {op: 'literal', type: 'Bool', value: true}, right: {op: 'literal', type: 'Bool', value: true}};
  fs.writeFileSync(file, JSON.stringify(raw));
  const result = f.run(`
assertWorkflowTransport();const r=execute();assertCrossGeneratorAggregateCurrent(r);assertWorkflowCustody(r);
assert.equal(r.result,'incomplete',JSON.stringify({families:r.families,issues:r.currentness_issues}));
assert.equal(r.families.find(f=>f.family==='factory-rule').result,'incomplete');
assert.ok(r.rows.some(row=>row.family==='factory-rule'&&row.state==='not_evaluable'&&row.result==='not_evaluable'&&!row.executed));
assert.ok(r.retained.some(f=>f.family==='owned-values'));assert.ok(r.retained.some(f=>f.family==='workflow'));
const d=workflowVerificationDefinitions(),original=createWorkflowProtocolCases(graph.nodes.find(n=>n.kind==='Workflow'),graph,plan,{execution:d.execution,binding:d.binding,values:d.values,outcomes:d.outcomes},getCrossGeneratorSource('workflow_cases'));
const workflow=crossGeneratorPreparationBindings(prepared,graph,plan).bindings.workflow.value.controls.rows[0];
assert.equal(original.cases.length,12167);assert.equal(r.retained.find(f=>f.family==='workflow').outcome.tested_case_count,original.cases.length);
assert.deepEqual(workflow.dimensions,original.coverage);assert.deepEqual(workflow.cases.map(c=>({id:c.id,data:c.data,semantic_sha256:c.expected.semantic_sha256})),original.cases.map(c=>({id:c.id,data:JSON.parse(c.values[0]),semantic_sha256:c.expected.value})));
assert.ok(r.edges.some(e=>e.behavior_required&&e.execution_status==='not_evaluable'));
assert.equal(r.public_cross_generator_behavior,'not_evaluable');
console.log(JSON.stringify({result:r.result,retained:r.retained_family_count,remaining:r.rows.filter(r=>r.result==='not_evaluable').map(r=>[r.family,r.selector])}));
`);t.diagnostic(JSON.stringify(result));
});

test('an Operation native mismatch cannot be erased by a successful Workflow covering the same wrapper', t => {
  const f = native(t), result = f.run(`
const original=cp.spawnSync;let injected=false;
cp.spawnSync=function(file,args,...rest){
 const out=original.call(this,file,args,...rest);
 const index=args.findIndex(a=>String(a).endsWith('/runner.mjs'));
 if(!injected&&index>=0&&JSON.parse(fs.readFileSync(args[index+1],'utf8')).rows[0]?.adapter==='operation-protocol'){
  const value=JSON.parse(out.stdout);value.rows[0].cases.pop();out.stdout=JSON.stringify(value);injected=true;
 }
 return out;
};syncBuiltinESMExports();
const r=execute();cp.spawnSync=original;syncBuiltinESMExports();
assert.ok(injected);assert.equal(r.result,'fail');assert.equal(r.families.find(f=>f.family==='operation').result,'fail');
assert.equal(r.families.find(f=>f.family==='workflow').result,'pass');assert.ok(r.rows.filter(x=>x.family==='operation').every(x=>x.result==='fail'&&x.executed));
assertWorkflowCustody(r);
assert.ok(r.edges.some(e=>e.observations.some(w=>w.family==='operation'&&w.result==='fail')&&e.observations.some(w=>w.family==='workflow'&&w.result==='pass')));
assertCrossGeneratorAggregateCurrent(r);
console.log(JSON.stringify({result:r.result,retained:r.retained_family_count,injected}));
`);t.diagnostic(JSON.stringify(result));
});

test('an earlier retained Operation altered during Workflow observation invalidates the aggregate', t => {
  const f = native(t), result = f.run(`
const original=cp.spawnSync;let changed;
cp.spawnSync=function(file,args,...rest){
 const out=original.call(this,file,args,...rest);
 if(!changed&&args.some(a=>String(a).endsWith('/observer.mjs'))){
  const workflowRoot=rest[0].cwd,aggregate=path.dirname(workflowRoot),operation=fs.readdirSync(aggregate).find(p=>p.startsWith('ds-cross-generator-run-'));
  changed=path.join(aggregate,operation,'observations.json');fs.appendFileSync(changed,' ');
 }
 return out;
};syncBuiltinESMExports();
const r=execute();cp.spawnSync=original;syncBuiltinESMExports();
assert.ok(changed);assert.equal(r.result,'fail');assert.ok(r.currentness_issues.some(i=>i.scope==='operation'));
assert.ok(r.rows.filter(x=>x.family==='operation').every(x=>x.result==='not_evaluable'&&x.executed));
assert.throws(()=>assertCrossGeneratorAggregateCurrent(r),/currentness/);
console.log(JSON.stringify({result:r.result,scopes:r.currentness_issues.map(i=>i.scope)}));
`);t.diagnostic(JSON.stringify(result));
});

test('retained source, native, audit, observer input, result and aggregate manifests all remain in currentness custody', t => {
  const f = native(t), result = f.run(`
const r=execute();assert.equal(r.result,'pass');assertCrossGeneratorAggregateCurrent(r);
const bound=assertWorkflowCustody(r);
const audited=path.join(bound.receipt.workspace,'native-effects-audit-observation.json'),originalAudit=fs.readFileSync(audited);
fs.appendFileSync(audited,' ');assert.throws(()=>retainedWorkflowExecutionBindings(r,prepared,graph,plan),/currentness/);fs.writeFileSync(audited,originalAudit);
assert.equal(retainedWorkflowExecutionBindings(r,prepared,graph,plan).receipt,bound.receipt);
const operation=r.retained.find(f=>f.family==='operation'),walk=dir=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);
const files=[...Object.keys(r.aggregate_files),...['observations.json','cases.json','source-audit-observation.json','native-audit-observation.json'].map(p=>path.join(operation.workspace,p)),
walk(path.join(operation.workspace,'source')).find(p=>p.endsWith('.ts')),walk(path.join(operation.workspace,'native')).find(p=>p.endsWith('.js')),path.join(sourcePath,'specs/commerce/nodes/allowed.json')];
for(const file of files){const old=fs.readFileSync(file);fs.appendFileSync(file,' ');assert.throws(()=>assertCrossGeneratorAggregateCurrent(r),/currentness/,file);fs.writeFileSync(file,old);assertCrossGeneratorAggregateCurrent(r);}
const extra=path.join(r.workspace,'unregistered.json');fs.writeFileSync(extra,'{}');assert.throws(()=>assertCrossGeneratorAggregateCurrent(r),/entry set/);fs.unlinkSync(extra);assertCrossGeneratorAggregateCurrent(r);
const old=path.join(root,'retained-operation-moved');fs.renameSync(operation.workspace,old);fs.mkdirSync(operation.workspace);assert.throws(()=>assertCrossGeneratorAggregateCurrent(r),/identity changed/);fs.rmdirSync(operation.workspace);fs.renameSync(old,operation.workspace);assertCrossGeneratorAggregateCurrent(r);
console.log(JSON.stringify({checked_files:files.length,result:r.result}));
`);t.diagnostic(JSON.stringify(result));
});

test('fresh declaration dependency selection is checked even when only the CommonJS families execute', t => {
  const f = native(t, 'state'), result = f.run(`
const own=path.join(root,'declaration-fixture'),ownNode=path.join(own,'@types/node');
fs.mkdirSync(path.dirname(ownNode),{recursive:true});fs.cpSync(options.node_types_root,ownNode,{recursive:true});
const dependency=path.dirname(createRequire(path.join(options.node_types_root,'package.json')).resolve('undici-types/package.json'));
const ownUndici=path.join(own,'node_modules/undici-types');fs.mkdirSync(path.dirname(ownUndici),{recursive:true});fs.cpSync(dependency,ownUndici,{recursive:true});options.node_types_root=ownNode;
const r=execute();assert.equal(r.result,'incomplete');assert.ok(r.retained.some(f=>f.family==='state-machine'));assert.ok(r.retained.every(f=>f.family!=='workflow'));assertCrossGeneratorAggregateCurrent(r);
const guardless=r.rows.find(row=>row.family==='state-machine'&&row.reason==='no Rule guard protocol; guardless reducer behavior belongs to standalone controls');assert.ok(guardless);assert.equal(guardless.state,'not_evaluable');assert.equal(guardless.result,'not_evaluable');
const declarations=path.join(ownNode,'index.d.ts'),old=fs.readFileSync(declarations);fs.appendFileSync(declarations,' ');assert.throws(()=>assertCrossGeneratorAggregateCurrent(r),/toolchain|dependency/);fs.writeFileSync(declarations,old);assertCrossGeneratorAggregateCurrent(r);
const shadow=path.join(own,'@types/node_modules/undici-types');fs.mkdirSync(path.dirname(shadow),{recursive:true});fs.symlinkSync(ownUndici,shadow);
assert.throws(()=>assertCrossGeneratorAggregateCurrent(r),/dependency selection changed/);
fs.unlinkSync(shadow);assertCrossGeneratorAggregateCurrent(r);
console.log(JSON.stringify({result:r.result,retained:r.retained_family_count,shadow_rejected:true}));
`);t.diagnostic(JSON.stringify(result));
});

test('a zero-edge Rule-only graph is explicitly inapplicable and creates no aggregate workspace', t => {
  const f = native(t, 'rule-only'), result = f.run(`
const before=fs.readdirSync(root);const r=execute();assertCrossGeneratorAggregateCurrent(r);
const bound=assertWorkflowCustody(r);assert.equal(bound.receipt,null);assert.deepEqual(bound.rows,[]);
assert.equal(r.result,'inapplicable');assert.equal(r.workspace,null);assert.equal(r.executed_family_count,0);assert.equal(r.roots.length,1);assert.equal(r.edges.length,0);
assert.deepEqual(fs.readdirSync(root),before);assert.equal(r.public_cross_generator_behavior,'not_evaluable');
console.log(JSON.stringify({result:r.result,roots:r.roots.length}));
`);t.diagnostic(JSON.stringify(result));
});

test('source drift during the final manifest write downgrades earlier passes before returning', t => {
  const f = native(t), result = f.run(`
const original=fs.writeFileSync,file=path.join(sourcePath,'specs/commerce/nodes/allowed.json');let injected=false;
fs.writeFileSync=function(target,...args){
 const result=original.call(this,target,...args);
 if(!injected&&String(target).endsWith('/outcomes.json')){injected=true;fs.appendFileSync(file,' ');}
 return result;
};
const r=execute();fs.writeFileSync=original;
assert.ok(injected);assert.equal(r.result,'fail');assert.ok(r.currentness_issues.some(i=>i.scope==='source'));
assert.ok(r.rows.filter(r=>r.state==='ready').every(r=>r.result==='not_evaluable'));
assert.ok(r.edges.filter(e=>e.behavior_required).every(e=>e.execution_status!=='pass'));
assert.throws(()=>assertCrossGeneratorAggregateCurrent(r),/currentness/);
console.log(JSON.stringify({result:r.result,source_drift_rejected:injected}));
`);t.diagnostic(JSON.stringify(result));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
