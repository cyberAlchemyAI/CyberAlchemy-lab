import type { BoundReference, EvidenceState } from './operational-evidence.js';

export const RECOVERY_IDS = Object.freeze(Array.from({ length: 30 }, (_, i) => `R01-F${String(i + 1).padStart(2, '0')}`));
export const RECOVERY_ROLES = Object.freeze(['subject', 'candidate_artifact', 'configuration', 'fixture', 'environment', 'recovery_runtime', 'coordination_schema', 'operation_schema', 'scenario_contract', 'source_manifest', 'runtime_manifest', 'producer', 'observer', 'adapter', 'evaluator', 'receipt_schema', 'attribute_policy', 'evaluation_policy']);
export const RECOVERY_SCHEMA_VERSION = 'domainspec.orodi.recovery-test-bundle/v1-candidate';
export type Schema = { type?: string; properties?: Record<string, Schema>; required?: string[]; additionalProperties?: false; items?: Schema; enum?: readonly unknown[]; pattern?: string; minLength?: number; minItems?: number; maxItems?: number; anyOf?: Schema[] };
const string: Schema = { type: 'string', minLength: 1 };
const nullable = (s: Schema): Schema => ({ anyOf: [s, { type: 'null' }] });
const array = (items: Schema, minItems = 0, maxItems = 10000): Schema => ({ type: 'array', items, minItems, maxItems });
const object = (properties: Record<string, Schema>): Schema => ({ type: 'object', properties, required: Object.keys(properties), additionalProperties: false });
const enumeration = (...values: unknown[]): Schema => ({ enum: values });
const reference = object({ ref: string, version: string, sha256: { type: 'string', pattern: '^[0-9a-f]{64}$' } });
const utc: Schema = { type: 'string', pattern: '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d{3})?Z$' };
export const recoveryScenarioSchema: Schema = object({
  schema_version: enumeration('domainspec.orodi.recovery-scenarios/v1-candidate'),
  scenarios: array(object({ id: enumeration(...RECOVERY_IDS), evidence_class: enumeration('runtime-product-test', 'formation-only', 'mixed'), checks: array(object({ pointer: { type: 'string' }, equals: {} }), 1, 1000) }), 30, 30),
});
export const recoveryBundleSchema: Schema = object({
  schema_version: enumeration(RECOVERY_SCHEMA_VERSION),
  binding: object({ schema_version: enumeration('domainspec.orodi.recovery-test-binding/v1-candidate'), binding_id: string, created_at: utc, expires_at: utc, invalidation_key_digest: { type: 'string', pattern: '^[0-9a-f]{64}$' }, references: object(Object.fromEntries(RECOVERY_ROLES.map(r => [r, reference]))), owners: object(Object.fromEntries(['recovery-runtime', 'operation', 'ORODI-profile', 'evidence-producer', 'observer', 'evaluator'].map(r => [r, string]))), authority_effect: enumeration('none') }),
  claim_mode: enumeration('historical-record-integrity', 'fresh-local-recovery-product-test'),
  documents: array(object({ reference, content: string }), 18, 1000),
  records: array(object({ scenario_id: enumeration(...RECOVERY_IDS), repetition: enumeration(1, 2), source: reference, pointer: { type: 'string' }, origin: enumeration('historical', 'fresh', 'workflow'), execution: enumeration('completed', 'started', 'not-started'), producer: reference, observer: nullable(reference), capture_started_at_utc: nullable(utc), capture_finished_at_utc: nullable(utc), cause: nullable(string) }), 0, 120),
  authority_effect: enumeration('none'),
});
export type RecoveryBinding = { schema_version: string; binding_id: string; created_at: string; expires_at: string; invalidation_key_digest: string; references: Record<string, BoundReference>; owners: Record<string, string>; authority_effect: 'none' };
export type RecoveryRecord = { scenario_id: string; repetition: number; source: BoundReference; pointer: string; origin: 'historical' | 'fresh' | 'workflow'; execution: 'completed' | 'started' | 'not-started'; producer: BoundReference; observer: BoundReference | null; capture_started_at_utc: string | null; capture_finished_at_utc: string | null; cause: string | null };
export type RecoveryBundle = { schema_version: string; binding: RecoveryBinding; claim_mode: 'historical-record-integrity' | 'fresh-local-recovery-product-test'; documents: { reference: BoundReference; content: string }[]; records: RecoveryRecord[]; authority_effect: 'none' };
export type RecoveryReceipt = { scenario_id: string; repetition: number; state: EvidenceState; reasons: string[]; source: BoundReference | null; pointer: string | null; original_runtime_outcome: unknown; original_cause: string | null };
