import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {
  RECONCILED_PYTHON_COMPILATION_VERSION,
  RECONCILED_PYTHON_PROFILE,
} from '../../src/generation/reconciled-python-selection.ts';
import {planCompiledReconciledRustProject} from '../../src/generation/reconciled-rust-project.ts';
import {
  RECONCILED_RUST_COMPILATION_VERSION,
  RECONCILED_RUST_PROFILE,
} from '../../src/generation/reconciled-rust-selection.ts';

export const domainSpecRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../../');
export const commerceCorpusRoot = path.join(
  domainSpecRoot,
  'development/reconciliation-v1/profile-compiler-reconciliation/parallel/r13-commerce',
);
export const commerceSourceRoot = path.join(commerceCorpusRoot, 'source');

export function loadCommerceCorpus() {
  const selection = JSON.parse(fs.readFileSync(path.join(commerceCorpusRoot, 'selection.json'), 'utf8'));
  const values = JSON.parse(fs.readFileSync(path.join(commerceCorpusRoot, 'values.json'), 'utf8'));
  const scenarios = JSON.parse(fs.readFileSync(path.join(commerceCorpusRoot, 'scenarios.json'), 'utf8'));
  const graph = loadCompiledProjectGraph(commerceSourceRoot);
  const common = {
    module_root: selection.module_root,
    layout_version: selection.layout_version,
    field_bindings: selection.field_bindings,
    factories: selection.factories,
    operations: selection.operations,
    workflows: selection.workflows,
  };
  const typescript = planCompiledReconciledProject(graph, selection);
  const pythonSelection = {
    schema_version: RECONCILED_PYTHON_COMPILATION_VERSION,
    profile_id: RECONCILED_PYTHON_PROFILE,
    language: 'python' as const,
    ...common,
  };
  const rustSelection = {
    schema_version: RECONCILED_RUST_COMPILATION_VERSION,
    profile_id: RECONCILED_RUST_PROFILE,
    language: 'rust' as const,
    ...common,
  };
  return {
    graph,
    values,
    scenarios,
    selections: {typescript: selection, python: pythonSelection, rust: rustSelection},
    plans: {
      typescript,
      python: planCompiledReconciledPythonProject(graph, pythonSelection),
      rust: planCompiledReconciledRustProject(graph, rustSelection),
    },
  };
}

export function writeArtifacts(root: string, artifacts: readonly {relative_path: string; content: string}[]): void {
  for (const artifact of artifacts) {
    const file = path.join(root, artifact.relative_path);
    if (!file.startsWith(root + path.sep)) throw new TypeError('R13_ARTIFACT_ESCAPE');
    fs.mkdirSync(path.dirname(file), {recursive: true});
    fs.writeFileSync(file, artifact.content, {flag: 'wx'});
  }
}
