import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {workflowFixture} from '../helpers/workflow-verification.ts';
import {publicFixture, publicSelection} from '../helpers/composition-project.ts';
import {planCompiledReconciledProject, selectReconciledArtifacts} from '../../src/generation/reconciled-project.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCrossGeneratorBoundary, assertCrossGeneratorBoundary, CROSS_GENERATOR_DEFINITION_SHA256} from '../../src/verification/reconciled-cross-generator-boundary.ts';
const project = path.resolve(import.meta.dirname, '../../../..');
const definition = fs.readFileSync(path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation/cross-generator-verification-contract.json'), 'utf8');
const sorted = (xs: readonly string[]) => [...xs].sort();

test('boundary accounts for every request, module, source pin and import without claiming behavior', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const b = createCrossGeneratorBoundary(f.graph, plan, definition);
  assert.equal(sha256(definition), CROSS_GENERATOR_DEFINITION_SHA256);
  assertCrossGeneratorBoundary(b);
  assert.deepEqual(b.requests.map(({module_paths, ...r}) => r), plan.resolved.requests);
  assert.equal(b.counts.modules, plan.resolved.artifacts.length);
  assert.equal(b.counts.imports, plan.resolved.modules.reduce((n, m) => n + m.imports.length, 0));
  assert.equal(b.counts.imports, b.counts.generated_runtime_imports + b.counts.generated_type_only_imports + b.counts.native_library_imports);
  assert.equal(b.counts.roots, f.graph.nodes.length);
  assert.equal(b.behavior_status, 'not_evaluable'); assert.equal(b.authority_effect, 'none');
  assert.equal(b.excluded_composition_plan_sha256, null);
  const {boundary_sha256, ...body} = b;
  assert.equal(sha256(canonicalJson(body)), boundary_sha256);
  for (const r of b.requests) assert.deepEqual(r.module_paths, plan.resolved.modules.filter(m => m.request_sha256s.includes(r.request_sha256)).map(m => m.relative_path));
  for (const m of plan.resolved.modules) assert.deepEqual(b.edges.filter(e => e.importer_path === m.relative_path).map(e => e.import_index), m.imports.map((_, i) => i));
  for (const e of b.edges) {
    const original = plan.resolved.modules.find(m => m.relative_path === e.importer_path)!.imports[e.import_index]!;
    for (const key of Object.keys(original)) assert.deepEqual((e as any)[key], (original as any)[key]);
    if (e.target_path) assert.equal(e.target_sha256, plan.resolved.artifacts.find(a => a.relative_path === e.target_path)!.sha256);
  }
});

test('overlapping generator ownership retains Workflow-to-Operation and Operation-to-Rule boundaries', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const b = createCrossGeneratorBoundary(f.graph, plan, definition);
  const workflow = b.edges.find(e => e.importer_selectors.includes('commerce:flow') && e.target_selectors.includes('commerce:perform') && e.category === 'generated-runtime');
  assert.ok(workflow); assert.equal(workflow.cross_generator_kind, true);
  assert.ok(workflow.shared_request_sha256s.length > 0, 'shared workflow request must not erase the Operation generator boundary');
  assert.ok(workflow.target_generator_kinds.includes('operations'));
  assert.ok(workflow.target_generator_kinds.includes('workflows'));
  const guard = b.edges.find(e => e.importer_selectors.includes('commerce:perform') && e.target_selectors.includes('commerce:allowed') && e.category === 'generated-runtime');
  assert.ok(guard); assert.equal(guard.cross_generator_kind, true);
  assert.ok(b.counts.shared_modules > 0); assert.equal(b.counts.support_modules, 0);
  for (const e of b.edges) assert.equal(e.cross_generator_kind, e.importer_generator_kinds.some(a => e.target_generator_kinds.some(c => a !== c)));
});

test('type-only imports and native-library imports have separate explicit denominators', t => {
  const f = workflowFixture(t), b = createCrossGeneratorBoundary(f.graph, planCompiledReconciledProject(f.graph, f.selection), definition);
  assert.ok(b.counts.generated_type_only_imports > 0);
  assert.ok(b.counts.native_library_imports > 0);
  for (const e of b.edges.filter(e => e.category === 'generated-type-only')) assert.equal(e.type_only, true);
  for (const e of b.edges.filter(e => e.category === 'native-standard-library')) {
    assert.equal(e.specifier, 'node:crypto'); assert.equal(e.target_path, null);
    assert.deepEqual(e.target_request_sha256s, []); assert.equal(e.cross_generator_kind, false);
  }
  assert.equal(b.counts.cross_generator_runtime_imports, b.edges.filter(e => e.cross_generator_kind && !e.type_only && e.target_path !== null).length);
});

test('every source root retains the exact public native closure including shared dependencies', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const b = createCrossGeneratorBoundary(f.graph, plan, definition);
  for (const root of b.roots) {
    const expected = selectReconciledArtifacts(plan, [root.selector]);
    assert.deepEqual(root.module_paths, sorted(expected.artifacts.map(a => a.relative_path)));
    assert.equal(root.public_view_sha256, expected.view_sha256);
    const set = new Set(root.module_paths);
    assert.deepEqual(root.edge_sha256s, sorted(b.edges.filter(e => set.has(e.importer_path)).map(e => e.edge_sha256)));
    for (const e of b.edges.filter(e => root.edge_sha256s.includes(e.edge_sha256))) if (e.target_path) assert.ok(set.has(e.target_path));
  }
  assert.ok(b.roots.find(r => r.selector === 'commerce:flow')!.module_paths.some(p => b.modules.find(m => m.relative_path === p)!.request_sha256s.length > 1));
});

test('ownerless Enum runtime remains in both qualified Enum closures without merging their source identities', t => {
  const f = publicFixture(t);
  for (const feature of ['alpha', 'beta']) {
    const manifest = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/' + feature + '/feature.json'), 'utf8'));
    manifest.nodes.push('mode'); f.write('specs/' + feature + '/feature.json', manifest);
    f.write('specs/' + feature + '/nodes/mode.json', {schema_version: 'domainspec.node/v1', feature_id: feature, node_id: 'mode', kind: 'Enum',
      body: {description: 'Distinct qualified mode.', values: ['On', 'Off'], typed_contract: {schema_version: 'domainspec.typed-sum/v1',
        ontology_node: 'BOUNDARY-' + feature.toUpperCase() + '-MODE', variants: ['On', 'Off'].map(name => ({name, payload: null, ontology_variant: 'BOUNDARY-' + feature.toUpperCase() + '-MODE#' + name}))}}});
  }
  const graph = loadCompiledProjectGraph(f.source), plan = planCompiledReconciledProject(graph, publicSelection());
  const b = createCrossGeneratorBoundary(graph, plan, definition);
  const support = b.modules.find(m => m.relative_path === 'domain/runtime/enum.ts');
  assert.ok(support); assert.equal(support.artifact_role, 'shared-support');
  assert.deepEqual(support.qualified_selectors, []); assert.deepEqual(support.metatypes, []);
  assert.ok(b.counts.support_modules > 0);
  for (const selector of ['alpha:mode', 'beta:mode']) {
    const root = b.roots.find(r => r.selector === selector)!;
    assert.ok(root.module_paths.includes(support.relative_path));
    assert.deepEqual(root.module_paths, selectReconciledArtifacts(plan, [selector]).artifacts.map(a => a.relative_path));
    assert.ok(b.edges.some(e => e.importer_selectors.includes(selector) && e.target_path === support.relative_path));
  }
  assert.notDeepEqual(b.roots.find(r => r.selector === 'alpha:mode')!.owned_module_paths, b.roots.find(r => r.selector === 'beta:mode')!.owned_module_paths);
});

test('captured plans work after source removal and remain deterministic across module-root relocation', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const before = createCrossGeneratorBoundary(f.graph, plan, definition);
  fs.rmSync(path.join(f.root, 'source'), {recursive: true}); // Exact fixture owned by this test.
  assert.deepEqual(createCrossGeneratorBoundary(f.graph, plan, definition), before);
  const relocated = createCrossGeneratorBoundary(f.graph, planCompiledReconciledProject(f.graph, {...f.selection, module_root: 'application/domain'}), definition);
  assert.deepEqual(relocated.counts, before.counts);
  assert.deepEqual(relocated.modules.map(m => m.relative_path.replace(/^application\//, '')), before.modules.map(m => m.relative_path));
  assert.deepEqual(relocated.edges.map(e => [e.import_index, e.specifier, e.category, e.cross_generator_kind]), before.edges.map(e => [e.import_index, e.specifier, e.category, e.cross_generator_kind]));
  assert.notEqual(relocated.boundary_sha256, before.boundary_sha256);
});

test('whole-plan identity retains but does not pretend to cover separately verified composition artifacts', t => {
  const f = publicFixture(t), plan = planCompiledReconciledProject(f.graph, publicSelection());
  const b = createCrossGeneratorBoundary(f.graph, plan, definition);
  assert.equal(b.excluded_composition_plan_sha256, plan.composition!.plan_sha256);
  assert.equal(b.project_plan_sha256, plan.plan_sha256);
  assert.deepEqual(b.modules.map(m => m.relative_path), plan.resolved.modules.map(m => m.relative_path));
  assert.ok(b.modules.some(m => m.qualified_selectors.includes('alpha:compute')));
  assert.ok(b.modules.some(m => m.qualified_selectors.includes('beta:compute')));
  assert.equal(b.modules.some(m => m.relative_path.startsWith('compositions/')), false);
  assert.equal(b.behavior_status, 'not_evaluable');
});

test('forged graph, plan, inventory and drifted definition reject; registered output is deeply immutable', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const b = createCrossGeneratorBoundary(f.graph, plan, definition);
  assert.throws(() => createCrossGeneratorBoundary(structuredClone(f.graph), plan, definition));
  assert.throws(() => createCrossGeneratorBoundary(f.graph, structuredClone(plan), definition));
  assert.throws(() => createCrossGeneratorBoundary(f.graph, plan, definition + ' '), /definition drift/);
  assert.throws(() => assertCrossGeneratorBoundary(structuredClone(b)), /registered boundary/);
  assert.throws(() => assertCrossGeneratorBoundary(null), /registered boundary/);
  const foreign = workflowFixture(t, {noCompensations: true});
  assert.throws(() => createCrossGeneratorBoundary(foreign.graph, plan, definition), /cross-graph/);
  const immutable = (v: unknown): void => {if (v && typeof v === 'object') {assert.equal(Object.isFrozen(v), true); Object.values(v).forEach(immutable);}};
  immutable(b);
  assert.throws(() => (b.edges as any[]).pop(), TypeError);
  assert.throws(() => { (b.modules[0] as any).sha256 = '0'.repeat(64); }, TypeError);
});
