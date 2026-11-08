import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {workflowFixture} from '../helpers/workflow-verification.ts';
import {crossGeneratorPublicFixture} from '../helpers/cross-generator-public.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {prepareCrossGeneratorVerification} from '../../src/verification/reconciled-cross-generator-public.ts';
import {createReconciledSemanticControls} from '../../src/verification/reconciled-semantic-controls.ts';
import {bindRetainedWorkflowPublicEvidence, assertWorkflowPublicEvidenceCurrent} from '../../src/verification/reconciled-workflow-public-evidence.ts';

test('binding rejects unregistered or active evidence without native effects', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const controls = createReconciledSemanticControls(f.graph, plan), preparation = prepareCrossGeneratorVerification(f.graph, plan);
  const before = fs.readdirSync(f.root);
  let reads = 0;
  const active = Object.defineProperty({}, 'receipt', {get() {reads++; throw Error('must not call');}});
  for (const value of [null, false, {}, active, preparation, structuredClone(preparation)]) {
    assert.throws(() => bindRetainedWorkflowPublicEvidence(f.graph, plan, controls, preparation, value), /registered aggregate/);
    assert.throws(() => assertWorkflowPublicEvidenceCurrent(value), /registered evidence binding/);
  }
  assert.throws(() => bindRetainedWorkflowPublicEvidence(f.graph, plan, structuredClone(controls), preparation, active), /registered semantic/);
  assert.equal(reads, 0); assert.deepEqual(fs.readdirSync(f.root), before);
});

function native(t: any, compound = false, module_root = 'domain', changeRule = false, noWorkflow = false) {
  const f = compound ? crossGeneratorPublicFixture(t) : workflowFixture(t);
  let source = path.join(f.root, 'source'), selection = {...f.selection, module_root};
  if (noWorkflow) {
    const rule = fs.readFileSync(path.join(source, 'specs/commerce/nodes/allowed.json'));
    source = path.join(f.root, 'only-rule'); fs.mkdirSync(path.join(source, 'specs/commerce/nodes'), {recursive: true});
    fs.writeFileSync(path.join(source, 'project.json'), JSON.stringify({schema_version: 'domainspec.project/v1', project_id: 'rule-only', features: ['commerce'], cross_feature_edges: []}));
    fs.writeFileSync(path.join(source, 'specs/commerce/feature.json'), JSON.stringify({schema_version: 'domainspec.feature/v1', feature_id: 'commerce', nodes: ['allowed'], edges: []}));
    fs.writeFileSync(path.join(source, 'specs/commerce/nodes/allowed.json'), rule);
    selection = {...selection, factories: [], operations: [], workflows: []};
  }
  if (changeRule) {
    const file = path.join(source, 'specs/commerce/nodes/positive.json'), row = JSON.parse(fs.readFileSync(file, 'utf8'));
    row.body.typed_contract.expression = {op: 'eq', left: {op: 'literal', type: 'Bool', value: true}, right: {op: 'literal', type: 'Bool', value: true}};
    fs.writeFileSync(file, JSON.stringify(row));
  }
  const cli = path.resolve(import.meta.dirname, '../..'), require = createRequire(import.meta.url);
  const types = fs.realpathSync(require.resolve('@types/node/package.json', {paths: process.execArgv.filter(a => a.endsWith('loader.mjs')).map(p => path.dirname(p))}));
  const nodeRoot = path.dirname(types), deps = path.dirname(path.dirname(nodeRoot)), undici = path.dirname(createRequire(types).resolve('undici-types/package.json'));
  const image = nativeToolchainImage(), dist = path.join(f.root, 'dist');
  assert.equal(image, NATIVE_TEST_IMAGE_ID);
  const docker = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(),
    '--mount', 'type=bind,source=' + cli + ',target=' + cli + ',readonly', '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly',
    '--mount', 'type=bind,source=' + undici + ',target=' + undici + ',readonly', '--mount', 'type=bind,source=' + f.root + ',target=' + f.root, '--workdir', f.root, image];
  const run = (args: string[]) => {
    try {return execFileSync('docker', [...docker, ...args], {encoding: 'utf8', timeout: 600000, maxBuffer: 16777216});}
    catch (e: any) {throw Error([e.message, e.stdout, e.stderr].filter(Boolean).join('\n'));}
  };
  fs.writeFileSync(path.join(f.root, 'package.json'), '{"type":"module"}');
  run(['tsc', '--ignoreConfig', '--strict', '--types', 'node', '--typeRoots', path.join(deps, '@types'), '--target', 'ES2022', '--module', 'NodeNext',
    '--rootDir', path.join(cli, 'src'), '--outDir', dist, path.join(cli, 'src/verification/reconciled-workflow-public-evidence.ts')]);
  return {run(body: string) {
    const prefix = `import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';
import {loadCompiledProjectGraph} from './dist/input/project-model.js';
import {planCompiledReconciledProject} from './dist/generation/reconciled-project.js';
import {prepareCrossGeneratorVerification} from './dist/verification/reconciled-cross-generator-public.js';
import {createReconciledSemanticControls} from './dist/verification/reconciled-semantic-controls.js';
import {executePreparedCrossGeneratorVerification} from './dist/verification/reconciled-cross-generator-public-execution.js';
import {bindRetainedWorkflowPublicEvidence,assertWorkflowPublicEvidenceCurrent} from './dist/verification/reconciled-workflow-public-evidence.js';
const source=${JSON.stringify(source)},root=${JSON.stringify(f.root)},selection=${JSON.stringify(selection)};
const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
const semantic=createReconciledSemanticControls(graph,plan),preparation=prepareCrossGeneratorVerification(graph,plan);
const aggregate=executePreparedCrossGeneratorVerification(preparation,graph,plan,{workspace_parent:root,typescript_root:'/opt/node-toolchain/node_modules/typescript',node_types_root:${JSON.stringify(nodeRoot)}});
const before=JSON.stringify(semantic),binding=bindRetainedWorkflowPublicEvidence(graph,plan,semantic,preparation,aggregate);
assert.equal(JSON.stringify(semantic),before);assertWorkflowPublicEvidenceCurrent(binding);
const count=graph.nodes.filter(n=>n.kind==='Workflow').length;
assert.equal(binding.workflow_count,count);assert.equal(binding.retained_status,count?'observed':'inapplicable');assert.equal(binding.rows.length,count);
assert.ok(binding.facets.length===6&&binding.facets.every(f=>f.status===(count?'observed':'inapplicable')&&f.missing_source_paths.length===0&&f.missing_workflow_selectors.length===0));
assert.ok(binding.facets.every(f=>f.observed.length===f.required_source_paths.length&&(!count||f.input_sha256&&f.observation_sha256)));
assert.equal(binding.public_fulfillment,'not_evaluable');assert.equal(binding.authority_effect,'none');
assert.throws(()=>assertWorkflowPublicEvidenceCurrent(structuredClone(binding)),/registered evidence binding/);
assert.throws(()=>bindRetainedWorkflowPublicEvidence(graph,plan,semantic,preparation,structuredClone(aggregate)),/registered aggregate/);
`;
    const file = path.join(f.root, 'binding-client.mjs'); fs.writeFileSync(file, prefix + body);
    return run(['node', file]).trim();
  }};
}

test('scalar retained binding keeps standalone cases and original audit origins, and rejects later drift and cleanup', t => {
  const f = native(t);
  t.diagnostic(f.run(`
assert.equal(binding.rows[0].standalone.case_count,134);assert.equal(binding.rows[0].evidence.case_count,133);
const nativeFacet=binding.facets.find(f=>f.facet==='native:effects'),file=nativeFacet.observed[0].artifact_path;
const original=fs.readFileSync(file);fs.appendFileSync(file,' ');
assert.throws(()=>assertWorkflowPublicEvidenceCurrent(binding),/currentness/);
fs.writeFileSync(file,original);assertWorkflowPublicEvidenceCurrent(binding);
assert.equal(binding.rows[0].evidence.batch_observation_sha256s.length,binding.rows[0].evidence.batches.length);
fs.rmSync(aggregate.workspace,{recursive:true});assert.throws(()=>assertWorkflowPublicEvidenceCurrent(binding),/currentness/);
console.log('scalar-binding-pass');`));
});

test('complete compound retained evidence binds every case, call and audit path in both layouts', t => {
  for (const layout of ['domain', 'application/domain']) {
    const f = native(t, true, layout);
    t.diagnostic(f.run(`
const row=binding.rows[0];assert.equal(row.standalone.state,'not_evaluable');assert.equal(row.evidence.case_count,12472);
assert.equal(row.evidence.call_count,20369);assert.equal(row.evidence.batches.length,4);
assert.equal(aggregate.result,'pass');assert.equal(aggregate.roots.length,14);assert.equal(aggregate.edges.length,50);
assert.ok(binding.facets.every(f=>f.required_source_paths.every(p=>p.startsWith(selection.module_root+'/'))));
console.log('compound-binding-pass:'+selection.module_root);`));
  }
});

test('observed Workflow binding preserves evaluable Rule semantics and unavailable factory rejection witnesses', t => {
  const f = native(t, true, 'domain', true);
  t.diagnostic(f.run(`
assert.equal(binding.rows[0].evidence.case_count,12167);assert.equal(aggregate.result,'incomplete');
assert.ok(aggregate.rows.some(r=>r.family==='factory-rule'&&r.result==='not_evaluable'));
const rule=semantic.rows.find(r=>r.selector==='commerce:positive');assert.equal(rule.kind,'Rule');assert.equal(rule.state,'ready');assert.ok(rule.cases.length>0);
assert.ok(aggregate.rows.some(r=>r.family==='factory-rule'&&r.result==='not_evaluable'&&r.reason));
assert.ok(aggregate.rows.some(r=>r.family==='operation'&&r.result==='not_evaluable'));
assert.equal(binding.rows.length,1);assert.equal(binding.rows[0].kind,'Workflow');
console.log('independent-obligations-preserved');`));
});

test('zero-Workflow binding preserves a zero-edge source root without claiming native observations', t => {
  const f = native(t, false, 'domain', false, true);
  t.diagnostic(f.run(`
assert.equal(binding.node_count,1);assert.equal(binding.workflow_count,0);assert.deepEqual(binding.rows,[]);
assert.equal(aggregate.workspace,null);assert.equal(aggregate.executed_family_count,0);assert.equal(aggregate.edges.length,0);
assert.ok(binding.facets.every(f=>f.input_sha256===null&&f.observation_sha256===null&&f.observed.length===0));
console.log('zero-workflow-inapplicable');`));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
