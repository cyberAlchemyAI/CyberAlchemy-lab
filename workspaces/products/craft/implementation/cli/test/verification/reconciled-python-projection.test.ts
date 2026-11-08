import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {decodeReconciledPythonSelection, RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {createReconciledPythonVerificationProjection, validateReconciledPythonVerificationProjection, renderReconciledPythonVerificationProjection} from '../../src/verification/reconciled-python-projection.ts';

function fixture(t: any) {
  const f = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(f.source);
  const selection = decodeReconciledPythonSelection({schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'commerce', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows});
  return {...f, graph, selection, plan: planCompiledReconciledPythonProject(graph, selection)};
}

test('Python verification preparation binds every source node, relationship, native module and closure without executing evidence', t => {
  const f = fixture(t), before = canonicalJson(f.graph), files = fs.readdirSync(f.temp);
  const projection = createReconciledPythonVerificationProjection(f.graph, f.plan);
  assert.equal(projection.denominators.project_metatype_count, 13);
  assert.equal(projection.denominators.node_count, 21);
  assert.equal(projection.denominators.python_module_count, f.plan.artifacts.length);
  assert.equal(projection.denominators.semantic_obligation_count, f.graph.nodes.length);
  assert.deepEqual(projection.semantic_graph.relationships, f.graph.relationships);
  assert.deepEqual(projection.source_manifest, f.graph.source_manifest);
  assert.deepEqual(projection.compilation_selection, f.selection);
  assert.deepEqual(projection.native_projection.artifacts.map(a => a.relative_path), f.plan.modules.map(m => m.relative_path));
  assert.ok(projection.native_projection.artifacts.every(a => !Object.hasOwn(a, 'content')));
  assert.ok(projection.native_projection.source_references.every(a => !Object.hasOwn(a, 'content')));
  for (const view of projection.native_projection.node_views) {
    const roots = new Set(f.plan.modules.filter(m => m.qualified_selectors.includes(view.selector)).map(m => m.relative_path));
    const pending = [...roots];
    while (pending.length) {
      const next = pending.pop();
      for (const i of f.plan.modules.find(m => m.relative_path === next)!.imports) if (i.target_path !== null && !roots.has(i.target_path)) {roots.add(i.target_path); pending.push(i.target_path);}
    }
    assert.deepEqual(view.artifact_paths, [...roots].sort());
  }
  assert.equal(projection.verification_status, 'not-executed');
  assert.ok(projection.semantic_obligations.every(row => row.state === 'not-executed' && row.module_paths.length > 0));
  assert.ok(projection.evidence_requirements.every(row => row.required && row.state === 'not-executed'));
  assert.deepEqual(projection.evidence_requirements.map(row => row.id).sort(), ['source-currentness', 'compiled-graph-obligations', 'source-and-selection-preservation', 'isolated-exact-source-replay', 'strict-native-compilation', 'native-package-imports', 'independent-module-surface-observation', 'selected-generator-semantic-controls', 'cross-generator-behavior', 'successor-formalization-currentness', 'lean-structural-kernel', 'exact-output-currentness', 'toolchain-currentness', 'verification-workspace-currentness', 'verification-workspace-cleanup'].sort());
  for (const key of ['native_compilation', 'semantic_observation', 'formal_verification'] as const) assert.equal(projection[key], 'not-performed');
  assert.equal(projection.authority_effect, 'none');
  assert.deepEqual(fs.readdirSync(f.temp), files); assert.equal(canonicalJson(f.graph), before);
  fs.renameSync(f.source, f.source + '-moved');
  assert.deepEqual(createReconciledPythonVerificationProjection(f.graph, f.plan), projection);
  assert.deepEqual(validateReconciledPythonVerificationProjection(structuredClone(projection), f.graph, f.plan), projection);
  assert.equal(renderReconciledPythonVerificationProjection(projection), canonicalJson(projection) + '\n');
  t.diagnostic(JSON.stringify({nodes: projection.denominators.node_count, modules: projection.denominators.python_module_count, projection_bytes: Buffer.byteLength(canonicalJson(projection))}));
});

test('Python verification preparation rejects forged identities, dropped evidence and recomputed caller digests', t => {
  const f = fixture(t), projection = createReconciledPythonVerificationProjection(f.graph, f.plan);
  assert.throws(() => createReconciledPythonVerificationProjection(structuredClone(f.graph), f.plan), /unvalidated/);
  assert.throws(() => createReconciledPythonVerificationProjection(f.graph, structuredClone(f.plan)), /registered/);
  assert.throws(() => renderReconciledPythonVerificationProjection(structuredClone(projection)), /registered/);
  const changedNode = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/beta/nodes/total.json'), 'utf8'));
  changedNode.body.typed_contract.expression.value = '8'; f.write('specs/beta/nodes/total.json', changedNode);
  assert.throws(() => createReconciledPythonVerificationProjection(loadCompiledProjectGraph(f.source), f.plan), /certificate mismatch/);
  for (const mutate of [
    (v: any) => v.native_projection.modules.pop(),
    (v: any) => v.native_projection.artifacts.pop(),
    (v: any) => v.native_projection.node_views[0].artifact_paths.pop(),
    (v: any) => v.semantic_obligations.pop(),
    (v: any) => v.semantic_graph.relationships.reverse(),
    (v: any) => v.evidence_requirements.pop(),
    (v: any) => {v.semantic_obligations[0].state = 'pass';},
    (v: any) => {v.native_compilation = 'pass';},
    (v: any) => {v.compilation_selection.module_root = 'different';},
  ]) {
    const changed: any = structuredClone(projection); mutate(changed);
    const {projection_sha256, ...body} = changed; changed.projection_sha256 = sha256(canonicalJson(body));
    assert.throws(() => validateReconciledPythonVerificationProjection(changed, f.graph, f.plan), /changed verification inputs/);
  }
  let reads = 0; const active = {...projection}; Object.defineProperty(active, 'semantic_graph', {enumerable: true, get() {reads++; return projection.semantic_graph;}});
  assert.throws(() => validateReconciledPythonVerificationProjection(active, f.graph, f.plan)); assert.equal(reads, 0);
});
