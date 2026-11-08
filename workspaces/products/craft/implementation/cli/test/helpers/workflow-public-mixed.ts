import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import type {TestContext} from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {crossGeneratorPublicFixture} from './cross-generator-public.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import type {OperationActionBindings} from '../../src/typed-operation/action-bindings.ts';

/** Distinct Workflow/Operation roots share values and Rules, not orchestrates targets. */
export function mixedWorkflowPublicFixture(t: TestContext) {
  const f = crossGeneratorPublicFixture(t), selection = structuredClone(f.selection);
  const originalPath = path.join(f.source, 'specs/commerce/nodes/flow.json');
  const originalBytes = fs.readFileSync(originalPath), originalSelection = structuredClone(selection.workflows[0]!);
  const extra = JSON.parse(originalBytes.toString('utf8'));
  extra.node_id = 'oversized-flow';
  extra.body.description = 'Additional ordered occurrences with distinct Operations and shared value dependencies.';
  extra.body.typed_contract.ontology_workflow = 'FIXTURE-OVERSIZED-FLOW';
  const authored = structuredClone(originalSelection);
  authored.selector = 'commerce:oversized-flow';
  for (const input of authored.event_inputs) input.event_ref = input.event_ref.replace('commerce:', 'commerce:oversized-');
  for (const step of extra.body.typed_contract.steps) step.operation_ref = 'commerce:oversized-perform';
  for (const compensation of extra.body.typed_contract.compensations) compensation.operation_ref = 'commerce:oversized-undo';
  for (let index = 0; index < 60; index++) {
    const step_id = 'extra-' + index;
    extra.body.typed_contract.steps.push({step_id, operation_ref: 'commerce:oversized-perform'});
    // The existing last-step arguments refer to an earlier occurrence, so these
    // remain lawful without introducing new Operation or value semantics.
    authored.steps.push({...structuredClone(originalSelection.steps.at(-1)!), step_id});
  }
  selection.workflows.push(authored);
  fs.writeFileSync(path.join(f.source, 'specs/commerce/nodes/oversized-flow.json'), JSON.stringify(extra));
  const manifestPath = path.join(f.source, 'specs/commerce/feature.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  manifest.nodes.push(extra.node_id);
  for (const id of ['posted', 'released']) {
    const event = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/commerce/nodes/' + id + '.json'), 'utf8'));
    event.node_id = 'oversized-' + id;
    event.body.event_type = event.node_id;
    manifest.nodes.push(event.node_id);
    fs.writeFileSync(path.join(f.source, 'specs/commerce/nodes/' + event.node_id + '.json'), JSON.stringify(event));
  }
  const edge = (source_node_id: string, relationship: string, target_node_id: string) => {
    const edge_id = source_node_id + '-' + relationship + '-' + target_node_id;
    manifest.edges.push(edge_id);
    fs.writeFileSync(path.join(f.source, 'specs/commerce/edges/' + edge_id + '.json'), JSON.stringify({
      schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id,
      source_node_id, target_node_id, relationship, scope: 'feature'
    }));
  };
  for (const id of ['perform', 'undo']) {
    const target_node_id = 'oversized-' + id;
    const operation = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/commerce/nodes/' + id + '.json'), 'utf8'));
    operation.node_id = target_node_id;
    manifest.nodes.push(target_node_id);
    fs.writeFileSync(path.join(f.source, 'specs/commerce/nodes/' + target_node_id + '.json'), JSON.stringify(operation));
    const action = {...structuredClone(selection.operations.find((o: Pick<OperationActionBindings, 'selector'>) => o.selector === 'commerce:' + id)!), selector: 'commerce:' + target_node_id};
    for (const event of action.events) event.target = event.target.replace('commerce:', 'commerce:oversized-');
    selection.operations.push(action);
    edge('allowed', 'enforces', target_node_id);
    edge(target_node_id, 'produces', id === 'perform' ? 'oversized-posted' : 'oversized-released');
    const edge_id = 'oversized-flow-orchestrates-' + target_node_id;
    manifest.edges.push(edge_id);
    fs.writeFileSync(path.join(f.source, 'specs/commerce/edges/' + edge_id + '.json'), JSON.stringify({
      schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id,
      source_node_id: extra.node_id, target_node_id, relationship: 'orchestrates', scope: 'feature'
    }));
  }
  fs.writeFileSync(manifestPath, JSON.stringify(manifest));
  assert.deepEqual(fs.readFileSync(originalPath), originalBytes);
  assert.deepEqual(selection.workflows[0], originalSelection);
  return {...f, graph: loadCompiledProjectGraph(f.source), selection, originalBytes, originalSelection};
}

/** Real public verifier in the pinned native toolchain; all effects are test-owned. */
export function runPublicWorkflowCoverage(f: {root: string; selection: unknown}, body: string) {
  const cli = path.resolve(import.meta.dirname, '../..'), source = path.join(f.root, 'source');
  const require = createRequire(import.meta.url);
  const types = fs.realpathSync(require.resolve('@types/node/package.json', {paths: process.execArgv.filter(a => a.endsWith('loader.mjs')).map(p => path.dirname(p))}));
  const deps = path.dirname(path.dirname(path.dirname(types))), undici = path.dirname(createRequire(types).resolve('undici-types/package.json'));
  const lean = process.env.DOMAINSPEC_LEAN!; assert.ok(lean && path.isAbsolute(lean), 'explicit installed Lean required');
  const leanRoot = path.dirname(path.dirname(lean)), image = nativeToolchainImage();
  assert.equal(image, NATIVE_TEST_IMAGE_ID);
  const scratch = path.join(f.root, 'scratch'); fs.mkdirSync(scratch);
  fs.writeFileSync(path.join(f.root, 'package.json'), '{"type":"module"}');
  const docker = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(),
    '--mount', 'type=bind,source=' + cli + ',target=' + cli + ',readonly', '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly',
    '--mount', 'type=bind,source=' + undici + ',target=' + undici + ',readonly', '--mount', 'type=bind,source=' + leanRoot + ',target=' + leanRoot + ',readonly',
    '--mount', 'type=bind,source=' + f.root + ',target=' + f.root, '--workdir', f.root, '--env', 'TMPDIR=' + scratch, image];
  const run = (args: string[]) => {
    try {return execFileSync('docker', [...docker, ...args], {encoding: 'utf8', timeout: 600000, maxBuffer: 32 * 1024 * 1024});}
    catch (e: any) {throw Error([e.message, e.stdout, e.stderr].filter(Boolean).join('\n'));}
  };
  run(['tsc', '--ignoreConfig', '--strict', '--types', 'node', '--typeRoots', path.join(deps, '@types'), '--target', 'ES2022', '--module', 'NodeNext',
    '--rootDir', path.join(cli, 'src'), '--outDir', path.join(f.root, 'dist'), path.join(cli, 'src/index.ts')]);
  const prefix = `import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';
import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
import {canonicalJson,sha256} from './dist/input/source-manifest.js';
import {createWorkflowControls,workflowVerificationDefinitions} from './dist/verification/reconciled-workflow-controls.js';
import {createWorkflowBinding} from './dist/verification/reconciled-workflow-binding.js';
const source=${JSON.stringify(source)},selection=${JSON.stringify(f.selection)},scratch=${JSON.stringify(scratch)};
const tools=${JSON.stringify({typescript_root: '/opt/node-toolchain/node_modules/typescript', node_type_root: path.join(deps, '@types'), lean_executable: lean})};
const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),execute=()=>executeReconciledVerification(graph,plan,tools);
`;
  const file = path.join(f.root, 'coverage-client.mjs'); fs.writeFileSync(file, prefix + body);
  return run(['node', file]).trim();
}

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from './native-toolchain-image.ts';
