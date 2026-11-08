import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject, RECONCILED_COMPILATION_VERSION, RECONCILED_TYPESCRIPT_PROFILE} from '../../src/generation/reconciled-project.ts';
import {planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {planCompiledReconciledRustProject} from '../../src/generation/reconciled-rust-project.ts';
import {RECONCILED_RUST_COMPILATION_VERSION, RECONCILED_RUST_PROFILE} from '../../src/generation/reconciled-rust-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {createReconciledRealizationMatrix, renderReconciledRealizationMatrix, CROSS_LANGUAGE_REALIZATION_MATRIX_SHA256} from '../../src/verification/reconciled-realization-matrix.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';

function fixture(t: any, variant = false) {
  const source = pythonAllTypesFixture(t);
  if (variant) {const file = path.join(source.source, 'specs/beta/nodes/total.json'), node = JSON.parse(fs.readFileSync(file, 'utf8')); node.body.description = 'different checked source'; fs.writeFileSync(file, JSON.stringify(node, null, 2) + '\n');}
  const graph = loadCompiledProjectGraph(source.source), common = {module_root: 'generated/domain', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: source.factories, operations: source.operations, workflows: source.workflows};
  const typescriptSelection = {schema_version: RECONCILED_COMPILATION_VERSION, profile_id: RECONCILED_TYPESCRIPT_PROFILE, language: 'typescript' as const, value_profile: EXACT_UINT64_PROFILE, ...common};
  const pythonSelection = {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python' as const, ...common};
  const rustSelection = {schema_version: RECONCILED_RUST_COMPILATION_VERSION, profile_id: RECONCILED_RUST_PROFILE, language: 'rust' as const, ...common};
  const plans = {typescript: planCompiledReconciledProject(graph, typescriptSelection), python: planCompiledReconciledPythonProject(graph, pythonSelection), rust: planCompiledReconciledRustProject(graph, rustSelection)};
  return {...source, graph, plans};
}

test('matrix binds all 13 metatypes across all three registered native plans', t => {
  const f = fixture(t), matrix = createReconciledRealizationMatrix(f.graph, f.plans);
  assert.equal(matrix.definition_sha256, CROSS_LANGUAGE_REALIZATION_MATRIX_SHA256); assert.deepEqual(matrix.denominators, {metatype_count: 13, language_count: 3, cell_count: 39, executed_cell_count: 0});
  assert.equal(new Set(matrix.cells.map(cell => cell.cell_id)).size, 39);
  for (const metatype of new Set(f.graph.nodes.map(node => node.kind))) for (const language of ['typescript', 'python', 'rust']) {
    const cell = matrix.cells.find(row => row.metatype === metatype && row.language === language); assert.ok(cell, metatype + '/' + language); assert.ok(cell.selectors.length); assert.ok(cell.generation_contracts.length); assert.ok(cell.generator_plan_sha256s.length); assert.ok(cell.module_paths.length); assert.equal(cell.required_observations.length, 5); assert.equal(cell.qualification_state, 'not-executed');
  }
  assert.equal(JSON.parse(renderReconciledRealizationMatrix(matrix)).matrix_sha256, matrix.matrix_sha256);
});

test('matrix construction is deterministic but cannot turn a clone into registered evidence', t => {
  const f = fixture(t), first = createReconciledRealizationMatrix(f.graph, f.plans), second = createReconciledRealizationMatrix(f.graph, f.plans); assert.equal(canonicalJson(first), canonicalJson(second)); assert.throws(() => renderReconciledRealizationMatrix(structuredClone(first) as any), /registered matrix/);
});

test('matrix rejects plans from different checked source and incomplete registered-plan substitutes', t => {
  const first = fixture(t), second = fixture(t, true); assert.throws(() => createReconciledRealizationMatrix(first.graph, {...first.plans, rust: second.plans.rust}), /source identity|graph certificate/); assert.throws(() => createReconciledRealizationMatrix(first.graph, {...first.plans, python: structuredClone(first.plans.python) as any}), /registered Python project/);
});
