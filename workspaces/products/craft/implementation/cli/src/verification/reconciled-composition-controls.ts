import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {createCompositionCases} from './reconciled-composition-cases.js';
import {createCompositionBinding} from './reconciled-composition-binding.js';
import {createCompositionEffectAudit, COMPOSITION_EFFECT_AUDIT_RUNNER} from './reconciled-composition-effect-audit.js';
import {COMPOSITION_BEHAVIOR_RUNNER} from './reconciled-composition-runner.js';
export const COMPOSITION_CONTROLS_DEFINITION_SHA256 = '8f8714cfc38849af5b99ece356eaf3c992d6e5f64542763f2298ca7a796fadc8';
export interface CompositionControlDefinitions {binding: string; reference: string; cases: string; effects: string; controls: string;}
const registrations = new WeakMap<object, () => void>();
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
export function createCompositionControls(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, id: string, definitions: CompositionControlDefinitions) {
  if (sha256(definitions.controls) !== COMPOSITION_CONTROLS_DEFINITION_SHA256) throw new TypeError('COMPOSITION_CONTROLS:definition drift');
  const owned = {...definitions}, family = createCompositionCases(graph, plan, id, owned), effect = createCompositionEffectAudit(family.binding, owned.effects);
  const artifacts = [...plan.resolved.artifacts, ...plan.composition!.artifacts];
  const sources = family.binding.modules.map(m => {
    const a = artifacts.find(a => a.relative_path === m.relative_path);
    if (!a || a.sha256 !== m.source_sha256 || sha256(a.content) !== a.sha256) throw new TypeError('COMPOSITION_CONTROLS:source artifact drift');
    return {relative_path: a.relative_path, content: a.content, sha256: a.sha256};
  });
  if (sources.some(s => Buffer.byteLength(s.content) > 8388608) || sources.reduce((n, s) => n + Buffer.byteLength(s.content), 0) > 67108864) throw new TypeError('COMPOSITION_CONTROLS:source capacity');
  const body = {schema_version: 'domainspec.composition-controls/v1-candidate' as const, definition_sha256: COMPOSITION_CONTROLS_DEFINITION_SHA256,
    family, effect, definitions: owned, sources, runner: COMPOSITION_BEHAVIOR_RUNNER, runner_sha256: sha256(COMPOSITION_BEHAVIOR_RUNNER),
    audit_runner: COMPOSITION_EFFECT_AUDIT_RUNNER, audit_runner_sha256: sha256(COMPOSITION_EFFECT_AUDIT_RUNNER), authority_effect: 'none' as const};
  const result = freeze({...body, control_sha256: sha256(canonicalJson(body))});
  registrations.set(result, () => {const current = createCompositionBinding(graph, plan, id, owned.binding); if (current.binding_sha256 !== family.binding.binding_sha256) throw new TypeError('COMPOSITION_CONTROLS:source binding drift');});
  return result;
}
export type CompositionControls = ReturnType<typeof createCompositionControls>;
export function assertCompositionControls(value: unknown): asserts value is CompositionControls {
  if (!value || typeof value !== 'object' || !registrations.has(value)) throw new TypeError('COMPOSITION_CONTROLS:registered control required');
  registrations.get(value)!();
}
