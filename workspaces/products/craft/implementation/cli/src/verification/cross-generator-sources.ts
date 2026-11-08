import {CROSS_GENERATOR_SOURCE_SNAPSHOT} from './cross-generator-sources.generated.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';

export const CROSS_GENERATOR_SOURCE_CAPSULE_SHA256 = '78165252aaa9d48c288c920ae580bf2c03e955c2f50a698d32e2c412a93ff4a2';
export type CrossGeneratorSourceId = typeof CROSS_GENERATOR_SOURCE_SNAPSHOT.sources[number]['id'];
const fail = (reason: string): never => {throw new TypeError('CROSS_GENERATOR_SOURCES:' + reason);};
function freeze<T>(v: T): T {
  if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);}
  return v;
}
/** A caller cannot select a new contract by recomputing its digest. */
export function validateCrossGeneratorSourceCapsule(value: unknown) {
  assertInterfaceData(value);
  if (!value || typeof value !== 'object' || Array.isArray(value)) return fail('capsule');
  const v = value as typeof CROSS_GENERATOR_SOURCE_SNAPSHOT;
  if (canonicalJson(Object.keys(v).sort()) !== canonicalJson(['schema_version', 'authority_effect', 'selection_sha256', 'sources', 'capsule_sha256'].sort())) fail('closed capsule');
  const {capsule_sha256, ...body} = v;
  if (capsule_sha256 !== CROSS_GENERATOR_SOURCE_CAPSULE_SHA256 || sha256(canonicalJson(body)) !== CROSS_GENERATOR_SOURCE_CAPSULE_SHA256) fail('selected capsule drift');
  for (const row of v.sources) if (sha256(row.content) !== row.sha256 || Buffer.byteLength(row.content) !== row.size_bytes) fail('source content drift');
  return freeze(structuredClone(v));
}
const capsule = validateCrossGeneratorSourceCapsule(CROSS_GENERATOR_SOURCE_SNAPSHOT);
export function getCrossGeneratorSourceCapsule() {return capsule;}
export function getCrossGeneratorSource(id: CrossGeneratorSourceId): string {
  if (typeof id !== 'string') return fail('source ID');
  return capsule.sources.find(s => s.id === id)?.content ?? fail('unknown source:' + id);
}
