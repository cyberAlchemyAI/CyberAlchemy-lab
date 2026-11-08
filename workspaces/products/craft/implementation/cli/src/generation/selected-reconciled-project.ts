import {assertInterfaceData} from '../typed-backend/interface.js';
import type {CompiledProjectGraph} from '../input/project-model.js';
import type {RealizationProfile} from './exact-uint64.js';
import {sha256} from '../input/source-manifest.js';
import {getReconciledSource} from './reconciled-sources.js';
import * as ts from './reconciled-project.js';
import * as py from './reconciled-python-project.js';
import * as rust from './reconciled-rust-project.js';
import {decodeReconciledPythonSelection, type ReconciledPythonSelection} from './reconciled-python-selection.js';
import {decodeReconciledRustSelection, type ReconciledRustSelection} from './reconciled-rust-selection.js';

export type SelectedReconciledCompilation = ts.ReconciledCompilationSelection | ReconciledPythonSelection | ReconciledRustSelection;
export type SelectedReconciledProject = ts.ReconciledProjectPlan | py.ReconciledPythonProjectPlan | rust.ReconciledRustProjectPlan;
export const PYTHON_CLI_EXTENSION_SHA256 = '30872ce46e3756ebc4a4402a82a476bcdadf96c1054e62237bc4342e91b1d652';
export function selectedReconciledExtension(selection: SelectedReconciledCompilation) {
  if (selection.language !== 'python') return {};
  if (sha256(getReconciledSource('python_cli')) !== PYTHON_CLI_EXTENSION_SHA256) throw new TypeError('DS_RECONCILED_PYTHON: CLI extension drift');
  return {language_extension_sha256: PYTHON_CLI_EXTENSION_SHA256};
}

/** Dispatch is explicit data selection, never a fallback after planner failure. */
export function decodeSelectedReconciledCompilation(value: unknown): SelectedReconciledCompilation {
  assertInterfaceData(value);
  return value !== null && typeof value === 'object' && 'language' in value && value.language === 'python'
    ? decodeReconciledPythonSelection(value)
    : value !== null && typeof value === 'object' && 'language' in value && value.language === 'rust'
      ? decodeReconciledRustSelection(value) : ts.decodeReconciledCompilationSelection(value);
}

/** Check identity before reading any plan properties, including discriminants. */
export function assertSelectedReconciledProject(value: unknown): asserts value is SelectedReconciledProject {
  try {
    ts.assertReconciledProjectPlan(value);
    // The TypeScript identity registry serves both explicit compiler versions.
    // This legacy dispatcher must not narrow a genuine v2 plan to the v1 type.
    if (value.selection.schema_version !== ts.RECONCILED_COMPILATION_VERSION) {
      throw new TypeError('DS_RECONCILED_COMPILATION: use the explicit composed project API for v2 plans');
    }
  } catch (error) {
    try {py.assertReconciledPythonProjectPlan(value);} catch {
      try {rust.assertReconciledRustProjectPlan(value);} catch {throw error;}
    }
  }
}
export function isReconciledPythonProject(plan: SelectedReconciledProject): plan is py.ReconciledPythonProjectPlan {
  assertSelectedReconciledProject(plan);
  return plan.schema_version === 'domainspec.reconciled-python-project-plan/v1-candidate';
}
export function isReconciledRustProject(plan: SelectedReconciledProject): plan is rust.ReconciledRustProjectPlan {
  assertSelectedReconciledProject(plan);
  return plan.schema_version === 'domainspec.reconciled-rust-project-plan/v1-candidate';
}
export function selectedRealizationMatches(selection: SelectedReconciledCompilation, profile: RealizationProfile | undefined): boolean {
  return profile === undefined || selection.language === 'typescript' && profile === selection.value_profile;
}
export function planSelectedReconciledProject(sourceRoot: string, value: unknown): SelectedReconciledProject {
  const selection = decodeSelectedReconciledCompilation(value);
  return selection.language === 'python' ? py.planReconciledPythonProject(sourceRoot, selection) : selection.language === 'rust' ? rust.planReconciledRustProject(sourceRoot, selection) : ts.planReconciledProject(sourceRoot, selection);
}
export function planCompiledSelectedReconciledProject(graph: CompiledProjectGraph, value: unknown): SelectedReconciledProject {
  const selection = decodeSelectedReconciledCompilation(value);
  return selection.language === 'python' ? py.planCompiledReconciledPythonProject(graph, selection) : selection.language === 'rust' ? rust.planCompiledReconciledRustProject(graph, selection) : ts.planCompiledReconciledProject(graph, selection);
}
export function selectSelectedReconciledArtifacts(plan: SelectedReconciledProject, roots: readonly string[] | null = null) {
  return isReconciledPythonProject(plan) ? py.selectReconciledPythonArtifacts(plan, roots) : isReconciledRustProject(plan) ? rust.selectReconciledRustArtifacts(plan, roots) : ts.selectReconciledArtifacts(plan, roots);
}
export function selectedReconciledIdentity(plan: SelectedReconciledProject) {
  const resolved = isReconciledPythonProject(plan) || isReconciledRustProject(plan) ? plan : plan.resolved;
  return {project_id: resolved.certificate.project_id, resolved_plan_sha256: resolved.plan_sha256, source_manifest_sha256: resolved.semantic_sources.manifest_sha256};
}
