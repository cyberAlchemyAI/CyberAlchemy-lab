import {decodeTypedRecordContract, decodeTypedSumContract, isCanonicalUInt64Decimal, type TypedRecordContract, type TypedSumContract, type TypedType} from '../typed-operation/contracts.js';
import {canonicalJson, sha256} from './source-manifest.js';

// Internal DSR-009 candidate; not a project input profile or persistence schema.
// Contract and unresolved decisions: development/reconciliation-v1/contracts/FIELD-REFERENCE-REPORT.md.
export const FIELD_MODEL_VERSION = 'domainspec.field-reference-model/v1-candidate';
export const FIELD_VALUE_PROFILE = 'json-safe-uint64/v1-candidate';
export const EXACT_FIELD_MODEL_VERSION = 'domainspec.field-reference-model/v2-candidate';
export const EXACT_FIELD_VALUE_PROFILE = 'exact-uint64/v1-candidate';
type Declaration = Readonly<{selector: string; kind: 'Entity' | 'Value Object'; contract: TypedRecordContract; invariant_refs: readonly string[]}>
  | Readonly<{selector: string; kind: 'Enum'; contract: TypedSumContract; invariant_refs: readonly string[]}>;
type Binding = Readonly<{owner: string; field: string; kind: 'identity-reference' | 'field-projection'; target: string; projection: readonly string[]}>;
export interface FieldReferenceModel {
  readonly schema_version: typeof FIELD_MODEL_VERSION | typeof EXACT_FIELD_MODEL_VERSION;
  readonly value_profile: typeof FIELD_VALUE_PROFILE | typeof EXACT_FIELD_VALUE_PROFILE;
  readonly declarations: readonly Declaration[];
  readonly bindings: readonly Binding[];
  readonly model_sha256: string;
  readonly authority_effect: 'none';
}
export class FieldReferenceError extends Error {
  constructor(readonly code: string, readonly pointer: string) {super(`${code}:${pointer}`); this.name = 'FieldReferenceError';}
}
function fail(code: string, pointer: string): never {throw new FieldReferenceError(code, pointer);}
function object(value: unknown, pointer: string): Record<string, unknown> {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) fail('FIELD_SHAPE', pointer);
  return value as Record<string, unknown>;
}
function exact(value: unknown, keys: readonly string[], pointer: string): Record<string, unknown> {
  const result = object(value, pointer);
  if (Object.keys(result).sort().join('|') !== [...keys].sort().join('|')) fail('FIELD_SHAPE', pointer);
  return result;
}
function jsonOnly(value: unknown, pointer = '/', depth = 0, exactValues = false): void {
  if (depth > 96) fail('FIELD_DEPTH', pointer);
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return;
  if (typeof value === 'number' && Number.isFinite(value)) return;
  if (exactValues && typeof value === 'bigint') return;
  if (typeof value !== 'object' || value === null) fail('FIELD_JSON', pointer);
  if (!Array.isArray(value) && Object.getPrototypeOf(value) !== Object.prototype && Object.getPrototypeOf(value) !== null) fail('FIELD_JSON', pointer);
  if (exactValues && Array.isArray(value) && Object.getPrototypeOf(value) !== Array.prototype) fail('FIELD_JSON', pointer);
  const descriptors = Object.getOwnPropertyDescriptors(value);
  for (const key of Reflect.ownKeys(descriptors)) {
    if (typeof key !== 'string') fail('FIELD_JSON', pointer);
    if (Array.isArray(value) && key === 'length') continue;
    const descriptor = descriptors[key]!;
    if (!('value' in descriptor) || !descriptor.enumerable) fail('FIELD_JSON', pointer);
    jsonOnly(descriptor.value, `${pointer}/${key}`, depth + 1, exactValues);
  }
  if (Array.isArray(value) && (Object.keys(value).length !== value.length || Array.from({length: value.length}, (_, i) => i).some(i => !Object.hasOwn(value, i)))) fail('FIELD_JSON', pointer);
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object') {Object.values(value).forEach(freeze); Object.freeze(value);}
  return value;
}
const snapshots = new WeakSet<object>();
const selectorPattern = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const localPattern = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
function identifier(value: unknown, pattern: RegExp, pointer: string): string {
  if (typeof value !== 'string' || !pattern.test(value)) fail('FIELD_IDENTIFIER', pointer);
  return value;
}
function named(type: TypedType): string[] {
  if (type.kind === 'named') return [type.selector];
  if (type.kind === 'reference') return [];
  if (type.kind === 'scalar') return [];
  if (type.kind === 'sum') return type.variants.flatMap(v => v.payload ? named(v.payload) : []);
  return named(type.element);
}
function unwrap(type: TypedType): TypedType {
  return type.kind === 'optional' || type.kind === 'list' || type.kind === 'set' ? unwrap(type.element) : type;
}

/** Validate candidate declarations and reference bindings without synthesizing domain edges. */
export function compileFieldReferenceModel(input: unknown): FieldReferenceModel {
  jsonOnly(input);
  const raw = exact(input, ['schema_version', 'value_profile', 'declarations', 'bindings'], '/');
  const exactValues = raw.schema_version === EXACT_FIELD_MODEL_VERSION;
  if ((!exactValues && raw.schema_version !== FIELD_MODEL_VERSION) || raw.value_profile !== (exactValues ? EXACT_FIELD_VALUE_PROFILE : FIELD_VALUE_PROFILE)) fail('FIELD_VERSION', '/');
  if (!Array.isArray(raw.declarations) || !raw.declarations.length || raw.declarations.length > 256 || !Array.isArray(raw.bindings) || raw.bindings.length > 1024) fail('FIELD_LIMIT', '/');
  const declarations: Declaration[] = raw.declarations.map((entry: unknown, i: number): Declaration => {
    const p = `/declarations/${i}`, d = exact(entry, ['selector', 'kind', 'contract', 'invariant_refs'], p);
    const selector = identifier(d.selector, selectorPattern, p);
    if (!Array.isArray(d.invariant_refs) || d.invariant_refs.some(r => typeof r !== 'string' || !selectorPattern.test(r)) || new Set(d.invariant_refs).size !== d.invariant_refs.length) fail('FIELD_INVARIANT', p);
    const invariant_refs = [...d.invariant_refs].sort() as string[];
    if (d.kind === 'Enum') {
      if (invariant_refs.length) fail('FIELD_INVARIANT', p);
      return {selector, kind: 'Enum', contract: decodeTypedSumContract(d.contract, p), invariant_refs};
    }
    if (d.kind !== 'Entity' && d.kind !== 'Value Object') fail('FIELD_KIND', p);
    const contract = decodeTypedRecordContract(d.contract, p);
    const identities = contract.properties.filter(f => f.identity);
    if ((d.kind === 'Entity' && (identities.length !== 1 || invariant_refs.length)) || (d.kind === 'Value Object' && (identities.length || !invariant_refs.length))) fail('FIELD_IDENTITY', p);
    return {selector, kind: d.kind, contract, invariant_refs};
  }).sort((a, b) => a.selector < b.selector ? -1 : a.selector > b.selector ? 1 : 0);
  const bySelector = new Map(declarations.map(d => [d.selector, d]));
  if (bySelector.size !== declarations.length) fail('FIELD_DUPLICATE', '/declarations');
  const get = (s: string): Declaration => bySelector.get(s) ?? fail('FIELD_DANGLING', s);
  const property = (s: string, name: string) => {
    const d = get(s);
    if (d.kind === 'Enum') return fail('FIELD_PROJECTION', s);
    return d.contract.properties.find(p => p.name === name) ?? fail('FIELD_PROJECTION', `${s}#${name}`);
  };
  // Named type use is embedding, never an implicit identity or database reference.
  const heights = new Map<string, number>();
  function visit(s: string, active: readonly string[]): number {
    if (active.includes(s)) fail('FIELD_EMBEDDING_CYCLE', [...active, s].join(' -> '));
    if (active.length > 32) fail('FIELD_DEPTH', s);
    const cached = heights.get(s);
    if (cached !== undefined) {
      if (active.length + cached > 32) fail('FIELD_DEPTH', s);
      return cached;
    }
    const d = get(s), types = d.kind === 'Enum' ? d.contract.variants.flatMap(v => v.payload ? [v.payload] : []) : d.contract.properties.map(p => p.type);
    let height = 0;
    for (const dependency of types.flatMap(named).sort()) height = Math.max(height, 1 + visit(dependency, [...active, s]));
    if (active.length + height > 32) fail('FIELD_DEPTH', s);
    heights.set(s, height);
    return height;
  }
  declarations.forEach(d => visit(d.selector, []));
  function identityType(type: TypedType): boolean {
    if (type.kind === 'scalar') return type.name === 'String' || type.name === 'UInt64';
    if (type.kind !== 'named') return false;
    const d = get(type.selector);
    return d.kind === 'Value Object' && d.contract.properties.every(p => identityType(p.type));
  }
  for (const d of declarations) if (d.kind === 'Entity' && !identityType(d.contract.properties.find(p => p.identity)!.type)) fail('FIELD_IDENTITY_TYPE', d.selector);
  const bindings: Binding[] = raw.bindings.map((entry: unknown, i: number): Binding => {
    const p = `/bindings/${i}`, b = exact(entry, ['owner', 'field', 'kind', 'target', 'projection'], p);
    if (b.kind !== 'identity-reference' && b.kind !== 'field-projection') fail('FIELD_BINDING_KIND', p);
    if (!Array.isArray(b.projection) || !b.projection.length || b.projection.length > 16) fail('FIELD_PROJECTION', p);
    return {owner: identifier(b.owner, selectorPattern, p), field: identifier(b.field, localPattern, p), kind: b.kind,
      target: identifier(b.target, selectorPattern, p), projection: b.projection.map((x: unknown) => identifier(x, localPattern, p))};
  }).sort((a, b) => `${a.owner}#${a.field}` < `${b.owner}#${b.field}` ? -1 : 1);
  const bindingMap = new Map(bindings.map(b => [`${b.owner}#${b.field}`, b]));
  if (bindingMap.size !== bindings.length) fail('FIELD_DUPLICATE', '/bindings');
  function projection(b: Binding, active: readonly string[]): TypedType {
    const key = `${b.owner}#${b.field}`;
    if (active.includes(key)) fail('FIELD_REFERENCE_CYCLE', [...active, key].join(' -> '));
    if (active.length > 32) fail('FIELD_DEPTH', key);
    let owner = b.target, result: TypedType = {kind: 'named', selector: owner};
    for (let i = 0; i < b.projection.length; i++) {
      const name = b.projection[i]!, field = property(owner, name);
      const next = bindingMap.get(`${owner}#${name}`);
      // Check metadata dependencies without erasing the declared field's wrappers.
      if (next) projection(next, [...active, key]);
      result = field.type;
      if (i < b.projection.length - 1) {
        if (result.kind !== 'named') fail('FIELD_PROJECTION', key);
        owner = result.selector;
      }
    }
    return result;
  }
  for (const b of bindings) {
    const source = property(b.owner, b.field), target = get(b.target);
    if (source.identity) fail('FIELD_IDENTITY_BINDING', `${b.owner}#${b.field}`);
    if (b.kind === 'identity-reference' && (target.kind !== 'Entity' || b.projection.length !== 1 || !property(b.target, b.projection[0]!).identity)) fail('FIELD_REFERENCE_IDENTITY', b.target);
    const expected = b.kind === 'identity-reference' ? unwrap(source.type) : source.type;
    if (canonicalJson(expected) !== canonicalJson(projection(b, []))) fail('FIELD_REFERENCE_TYPE', `${b.owner}#${b.field}`);
  }
  const body = {schema_version: exactValues ? EXACT_FIELD_MODEL_VERSION : FIELD_MODEL_VERSION, value_profile: exactValues ? EXACT_FIELD_VALUE_PROFILE : FIELD_VALUE_PROFILE, declarations, bindings, authority_effect: 'none'} as const;
  const model = freeze({...body, model_sha256: sha256(canonicalJson(body))});
  snapshots.add(model);
  return model;
}

/** Candidate typed-value equality key; exact-profile UInt64 inputs may be bigint.
 * Not invariant execution, lookup, persistence encoding or referential integrity. */
export function fieldValueKey(model: FieldReferenceModel, selector: string, input: unknown): string {
  if (!snapshots.has(model)) fail('FIELD_UNCHECKED', '/model');
  const exactValues = model.value_profile === EXACT_FIELD_VALUE_PROFILE;
  jsonOnly(input, '/', 0, exactValues);
  const declarations = new Map(model.declarations.map(d => [d.selector, d]));
  function value(type: TypedType, data: unknown, pointer: string, depth: number): unknown {
    if (depth > 64) fail('FIELD_DEPTH', pointer);
    if (type.kind === 'scalar') {
      if (type.name === 'String' && typeof data === 'string') return ['String', data];
      if (type.name === 'Bool' && typeof data === 'boolean') return ['Bool', data];
      if (type.name === 'UInt64' && exactValues) {
        if (typeof data !== 'bigint' && !(typeof data === 'number' && Number.isSafeInteger(data) && data >= 0) && !isCanonicalUInt64Decimal(data)) return fail('FIELD_VALUE_TYPE', pointer);
        const normalized = BigInt(data);
        if (normalized < 0n || normalized > 18446744073709551615n) return fail('FIELD_VALUE_TYPE', pointer);
        return ['UInt64', normalized.toString()];
      }
      if (type.name === 'UInt64' && typeof data === 'number' && Number.isSafeInteger(data) && data >= 0) return ['UInt64', data];
      return fail('FIELD_VALUE_TYPE', pointer);
    }
    if (type.kind === 'optional') return data === null ? ['absent'] : value(type.element, data, pointer, depth + 1);
    if (type.kind === 'list' || type.kind === 'set') {
      if (!Array.isArray(data)) fail('FIELD_VALUE_TYPE', pointer);
      const keys = data.map((v, i) => canonicalJson(value(type.element, v, `${pointer}/${i}`, depth + 1)));
      if (type.kind === 'set' && new Set(keys).size !== keys.length) fail('FIELD_SET_DUPLICATE', pointer);
      return [type.kind, type.kind === 'set' ? keys.sort() : keys];
    }
    if (type.kind === 'sum') {
      const row = object(data, pointer), variant = type.variants.find(v => v.name === row.variant);
      if (!variant) fail('FIELD_VARIANT', pointer);
      exact(data, variant.payload ? ['variant', 'payload'] : ['variant'], pointer);
      return ['sum', variant.name, variant.payload ? value(variant.payload, row.payload, pointer + '/payload', depth + 1) : null];
    }
    const d = declarations.get(type.selector) ?? fail('FIELD_DANGLING', type.selector);
    if (d.kind === 'Enum') return [d.selector, value({kind: 'sum', variants: d.contract.variants}, data, pointer, depth + 1)];
    const record = object(data, pointer), properties = d.contract.properties;
    if (Object.keys(record).some(key => !properties.some(p => p.name === key))) fail('FIELD_EXTRA', pointer);
    const fields = properties.map(p => {
      const present = Object.hasOwn(record, p.name);
      if (!present && p.type.kind !== 'optional') fail('FIELD_MISSING', pointer + '/' + p.name);
      return [p.name, value(p.type, present ? record[p.name] : null, pointer + '/' + p.name, depth + 1)] as const;
    }).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0);
    return [d.kind, d.selector, d.kind === 'Entity' ? fields.find(([name]) => properties.find(p => p.name === name)!.identity) : fields];
  }
  return canonicalJson(value({kind: 'named', selector}, input, '/', 0));
}
