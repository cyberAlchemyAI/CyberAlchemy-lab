import type { SupportedLanguage } from '../meta-types/types.js';
import type { RealizationProfile } from './exact-uint64.js';
import type { SystemIntegrationSelectionV1 } from '../system-integration/types.js';
import { assertInterfaceData } from '../typed-backend/interface.js';
import { canonicalJson, sha256 } from '../input/source-manifest.js';
import { assertSelectedReconciledProject as assertReconciledProjectPlan, decodeSelectedReconciledCompilation as decodeReconciledCompilationSelection, planSelectedReconciledProject as planReconciledProject, selectSelectedReconciledArtifacts as selectReconciledArtifacts, selectedRealizationMatches, type SelectedReconciledProject as ReconciledProjectPlan } from './selected-reconciled-project.js';
import { createReconciledOutputReceipt, publishReconciledProject, ReconciledOutputError } from './reconciled-output.js';
import {selectedReconciledExtension} from './selected-reconciled-project.js';

export const RECONCILED_INSTANTIATION_API_DEFINITION_SHA256 = 'c7101ec286e7b967204cf5f3a83f4801e78c25278007f21aa074611dcc28399f';
type Scope = 'node' | 'project';
const registered = new WeakMap<object, { project: ReconciledProjectPlan; scope: Scope; roots: readonly string[] | null }>();
function fail(pointer: string, message: string): never { throw new ReconciledOutputError('DS_RECONCILED_INSTANTIATION', pointer, message); }

function wrap<K extends Scope>(project: ReconciledProjectPlan, scope: K, roots: readonly string[] | null) {
  assertReconciledProjectPlan(project);
  const view = selectReconciledArtifacts(project, roots);
  const receipt = createReconciledOutputReceipt(project, roots);
  const body = {
    schema_version: 'domainspec.reconciled-instantiation-plan/v1-candidate' as const,
    definition_sha256: RECONCILED_INSTANTIATION_API_DEFINITION_SHA256,
    ...selectedReconciledExtension(project.selection),
    instantiation_scope: scope,
    project,
    artifacts: view.artifacts,
    receipt,
    authority_effect: 'none' as const,
  };
  const plan = Object.freeze({ ...body, plan_sha256: sha256(canonicalJson(body)) });
  registered.set(plan, { project, scope, roots });
  return plan;
}

/** A checked project is explicit: a detached decoded node is not compiler context. */
export function planReconciledNodeInstantiation(selector: unknown, language: SupportedLanguage, systemIntegration: SystemIntegrationSelectionV1 | null, realizationProfile: RealizationProfile | undefined, project: unknown) {
  assertReconciledProjectPlan(project);
  if (typeof selector !== 'string') fail('/node', 'a qualified selector string and checked project are required');
  if (systemIntegration !== null) fail('/system-integration', 'reconciled instantiation does not support a system-integration overlay');
  if (language !== project.selection.language || !selectedRealizationMatches(project.selection, realizationProfile)) fail('/compilation-selection', 'language or numeric realization conflicts with checked project');
  return wrap(project, 'node', Object.freeze([selector]));
}

export function planReconciledProjectInstantiation(sourceRoot: string, languages: readonly SupportedLanguage[], value: unknown) {
  const selection = decodeReconciledCompilationSelection(value);
  assertInterfaceData(languages);
  if (!Array.isArray(languages) || languages.length === 0 || languages.length > 256 || [...new Set(languages)].some(language => language !== selection.language)) fail('/languages', 'reconciled project instantiation requires the single selected language');
  return wrap(planReconciledProject(sourceRoot, selection), 'project', null);
}

export type ReconciledNodeInstantiationPlan = ReturnType<typeof planReconciledNodeInstantiation>;
export type ReconciledProjectInstantiationPlan = ReturnType<typeof planReconciledProjectInstantiation>;
export type ReconciledInstantiationPlan = ReconciledNodeInstantiationPlan | ReconciledProjectInstantiationPlan;
export type ReconciledInstantiationPublication = ReturnType<typeof publishReconciledProject>;

export function publishReconciledInstantiation(value: unknown, targetRoot: unknown, scope: Scope): ReconciledInstantiationPublication {
  const entry = value !== null && typeof value === 'object' ? registered.get(value) : undefined;
  if (!entry) fail('/plan', 'registered reconciled instantiation plan required');
  if (entry.scope !== scope) fail('/plan', 'instantiation publication scope does not match the registered plan');
  return publishReconciledProject(entry.project, targetRoot, entry.roots);
}
