import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {sha256} from '../input/source-manifest.js';
import {createCompositionControls, COMPOSITION_CONTROLS_DEFINITION_SHA256} from './reconciled-composition-controls.js';
import {COMPOSITION_BINDING_DEFINITION_SHA256} from './reconciled-composition-binding.js';
import {CompositionReferenceUnavailable, COMPOSITION_REFERENCE_DEFINITION_SHA256} from './reconciled-composition-reference.js';
import {CompositionCasesUnavailable, COMPOSITION_CASES_DEFINITION_SHA256} from './reconciled-composition-cases.js';
import {CompositionCaseValueUnavailable} from './reconciled-composition-case-values.js';
import {COMPOSITION_EFFECT_DEFINITION_SHA256} from './reconciled-composition-effect-audit.js';

export const COMPOSITION_PUBLIC_DEFINITION_SHA256 = 'fc721c2721660dfc0892c4586d3d47c383101c4938c9e8e053adf012422e86bb';
export function compositionVerificationDefinitions() {
  const values = {
    binding: getReconciledSource('semantic_composition_binding'), reference: getReconciledSource('semantic_composition_reference'),
    cases: getReconciledSource('semantic_composition_cases'), effects: getReconciledSource('composition_effect_audit'),
    controls: getReconciledSource('semantic_composition_controls'), public: getReconciledSource('semantic_composition_public')
  };
  const pins = {binding: COMPOSITION_BINDING_DEFINITION_SHA256, reference: COMPOSITION_REFERENCE_DEFINITION_SHA256,
    cases: COMPOSITION_CASES_DEFINITION_SHA256, effects: COMPOSITION_EFFECT_DEFINITION_SHA256,
    controls: COMPOSITION_CONTROLS_DEFINITION_SHA256, public: COMPOSITION_PUBLIC_DEFINITION_SHA256};
  for (const key of Object.keys(values) as (keyof typeof values)[]) if (sha256(values[key]) !== pins[key]) throw new TypeError('COMPOSITION_PUBLIC:definition drift:' + key);
  return Object.freeze(values);
}

/** A finite search limit is not a source/binding error or an unsatisfiability proof. */
export function createPublicCompositionControls(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, id: string) {
  const definitions = compositionVerificationDefinitions();
  try {
    return Object.freeze({id, state: 'ready' as const, control: createCompositionControls(graph, plan, id, definitions)});
  } catch (error) {
    if (!(error instanceof CompositionCasesUnavailable || error instanceof CompositionReferenceUnavailable || error instanceof CompositionCaseValueUnavailable)) throw error;
    return Object.freeze({id, state: 'not_evaluable' as const, reason: error.message,
      missing: Object.freeze(error instanceof CompositionCasesUnavailable ? [...error.missing] : [])});
  }
}
