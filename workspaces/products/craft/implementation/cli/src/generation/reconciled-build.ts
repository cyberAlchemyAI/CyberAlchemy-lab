import type { SupportedLanguage } from '../meta-types/types.js';
import type { RealizationProfile } from './exact-uint64.js';
import type { OutputLayout } from './output-layout.js';
import { canonicalJson, sha256 } from '../input/source-manifest.js';
import { assertSelectedReconciledProject as assertReconciledProjectPlan, decodeSelectedReconciledCompilation as decodeReconciledCompilationSelection, selectedRealizationMatches, type SelectedReconciledProject as ReconciledProjectPlan } from './selected-reconciled-project.js';
import { createReconciledOutputReceipt, publishReconciledProject, ReconciledOutputError } from './reconciled-output.js';
import {assertReconciledOutputLayout,reconciledLayoutDefinitionSha256,reconciledOutputView} from './reconciled-output-layout.js';
import {selectedReconciledExtension} from './selected-reconciled-project.js';

export const RECONCILED_BUILD_API_DEFINITION_SHA256 = 'b6fde22f9fe06a2492b629a71e44a08682bc489bbd405dfbe04ff3dd2c11628a';
const registered = new WeakMap<object, {project:ReconciledProjectPlan;outputLayout:OutputLayout|undefined}>();

/** Validate the explicit selection before accessing a source root or snapshot. */
export function selectReconciledBuild(language: SupportedLanguage, realizationProfile: RealizationProfile | undefined, outputLayout: OutputLayout | undefined, value: unknown) {
  const selection = decodeReconciledCompilationSelection(value);
  if (language !== selection.language || !selectedRealizationMatches(selection, realizationProfile)) {
    throw new ReconciledOutputError('DS_RECONCILED_BUILD_SELECTION', '/compilation-selection', 'DS_RECONCILED_BUILD_SELECTION: language or numeric realization conflicts with selection');
  }
  assertReconciledOutputLayout(outputLayout);
  return selection;
}

/** Preserve the public build shape without pretending its receipt is legacy assurance. */
export function createReconciledBuild(plan: ReconciledProjectPlan,outputLayout?:OutputLayout) {
  assertReconciledProjectPlan(plan);
  const view = reconciledOutputView(plan,null,outputLayout);
  const receipt = createReconciledOutputReceipt(plan,null,outputLayout);
  const body = {
    schema_version: 'domainspec.reconciled-build-plan/v1-candidate' as const,
    definition_sha256: RECONCILED_BUILD_API_DEFINITION_SHA256,
    ...selectedReconciledExtension(plan.selection),
    ...(outputLayout===undefined?{}:{output_layout:outputLayout,layout_definition_sha256:reconciledLayoutDefinitionSha256(outputLayout)}),
    project: plan,
    artifacts: view.artifacts,
    receipt,
    authority_effect: 'none' as const,
  };
  const result = Object.freeze({ ...body, plan_sha256: sha256(canonicalJson(body)) });
  registered.set(result, {project:plan,outputLayout});
  return result;
}
export type ReconciledBuildPlan = ReturnType<typeof createReconciledBuild>;
export type ReconciledBuildPublication = ReturnType<typeof publishReconciledProject>;

export function publishReconciledBuild(value: unknown, targetRoot: unknown): ReconciledBuildPublication {
  const binding = value !== null && typeof value === 'object' ? registered.get(value) : undefined;
  if (!binding) throw new ReconciledOutputError('DS_RECONCILED_BUILD_PLAN', '/plan', 'registered reconciled build plan required');
  return publishReconciledProject(binding.project, targetRoot,null,binding.outputLayout);
}
