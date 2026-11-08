import {decodeTypedType, type ScalarName, type TypedType} from '../typed-operation/contracts.js';
import type {TypedValueDeclaration} from '../typed-operation/value-bindings.js';
import {decodeInterfaceVersionPolicy, type InterfaceVersionPolicy} from './interface-version-policy.js';

export const TYPED_INTERFACE_VERSION = 'domainspec.typed-interface/v1' as const;
export const NAMED_INTERFACE_DEFINITION_SHA256 = 'cfaaff5a40d3c84b128ffc572fa74652863241a8513bac8b63342fc1148fb4b5';
export type InterfacePublicType =
  | Readonly<{kind: 'scalar'; name: ScalarName}>
  | Readonly<{kind: 'named'; selector: string}>
  | Readonly<{kind: 'contract'; contract_id: string}>
  | Readonly<{kind: 'optional' | 'list' | 'set'; element: InterfacePublicType}>
  | Readonly<{kind: 'sum'; variants: readonly Readonly<{name: string; ontology_variant: string; payload: InterfacePublicType | null}>[]}>;
export interface InterfacePublicContract {
  readonly contract_id: string;
  readonly ontology_contract: string;
  readonly fields: readonly Readonly<{name: string; ontology_field: string; meaning: string; type: InterfacePublicType}>[];
}
export interface NamedInterfaceContract {
  readonly schema_version: typeof TYPED_INTERFACE_VERSION;
  readonly ontology_interface: string;
  readonly boundary_kind: 'external' | 'internal';
  readonly version_policy: InterfaceVersionPolicy;
  readonly contracts: readonly InterfacePublicContract[];
  readonly operations: readonly Readonly<{operation_id: string; operation_ref: string; request: InterfacePublicType; result: InterfacePublicType}>[];
}
const fail = (reason: string): never => {throw Object.assign(new TypeError('MTCLI_TYPED_INTERFACE: ' + reason), {code: 'MTCLI_TYPED_INTERFACE'});};
const local = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/, field = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
const selector = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const ontology = /^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+(?:#[A-Za-z][A-Za-z0-9_]*)?$/;
const identifier = (value: unknown, pattern: RegExp): string => typeof value === 'string' && value.length <= 256 && pattern.exec(value)?.[0] === value ? value : fail('invalid identifier');
export function assertInterfaceData(value: unknown): void {
  let nodes = 0;
  const visit = (v: unknown, depth: number): void => {
    if (++nodes > 100000 || depth > 64) fail('data limit');
    if (v === null || typeof v === 'string' || typeof v === 'boolean' || typeof v === 'number' && Number.isFinite(v)) return;
    if (!v || typeof v !== 'object') fail('plain JSON data required');
    const array = Array.isArray(v), prototype = Object.getPrototypeOf(v);
    if (array ? prototype !== Array.prototype : prototype !== Object.prototype && prototype !== null) fail('plain data required');
    const descriptors = Object.getOwnPropertyDescriptors(v);
    if (array) {
      const length = descriptors.length!.value as number;
      if (length > 1024 || Reflect.ownKeys(descriptors).length !== length + 1) fail('bounded dense array required');
      for (let i = 0; i < length; i++) if (!Object.hasOwn(descriptors, String(i))) fail('dense array required');
    }
    for (const key of Reflect.ownKeys(descriptors)) {
      if (array && key === 'length') continue;
      const d = descriptors[key as string];
      if (typeof key !== 'string' || !d || !Object.hasOwn(d, 'value') || !d.enumerable) fail('inert data fields required');
      visit(d!.value, depth + 1);
    }
  };
  visit(value, 0);
}
function keys(value: unknown, names: readonly string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).length !== names.length || names.some(n => !Object.hasOwn(value, n))) fail('closed fields required');
  return value as Record<string, unknown>;
}
function array(value: unknown, max: number, min = 0): unknown[] {
  if (!Array.isArray(value) || value.length < min || value.length > max) fail('array size');
  return value as unknown[];
}
function unique(values: readonly string[]): void {if (new Set(values).size !== values.length) fail('duplicate identity');}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);}
  return value;
}
function type(value: unknown, depth = 0): InterfacePublicType {
  if (depth > 16) fail('type depth');
  const v = value as Record<string, unknown>;
  if (!v || typeof v !== 'object') fail('public type required');
  if (v.kind === 'scalar' || v.kind === 'named') return decodeTypedType(value) as Extract<InterfacePublicType, {kind: 'scalar' | 'named'}>;
  if (v.kind === 'contract') {keys(v, ['kind', 'contract_id']); return {kind: 'contract', contract_id: identifier(v.contract_id, local)};}
  if (v.kind === 'optional' || v.kind === 'list' || v.kind === 'set') {
    keys(v, ['kind', 'element']); const element = type(v.element, depth + 1);
    if (element.kind === 'optional') fail('nested optional element is unsupported');
    return {kind: v.kind, element};
  }
  if (v.kind === 'sum') {
    keys(v, ['kind', 'variants']);
    const variants = array(v.variants, 128, 1).map(x => {
      const r = keys(x, ['name', 'ontology_variant', 'payload']);
      return {name: identifier(r.name, /^[A-Z][A-Za-z0-9]*$/), ontology_variant: identifier(r.ontology_variant, ontology), payload: r.payload === null ? null : type(r.payload, depth + 1)};
    });
    unique(variants.map(v => v.name)); unique(variants.map(v => v.ontology_variant));
    return {kind: 'sum', variants};
  }
  return fail('unsupported public type');
}
export function decodeNamedInterface(value: unknown): NamedInterfaceContract {
  assertInterfaceData(value);
  const c = keys(value, ['schema_version', 'ontology_interface', 'boundary_kind', 'version_policy', 'contracts', 'operations']);
  if (c.schema_version !== TYPED_INTERFACE_VERSION || c.boundary_kind !== 'external' && c.boundary_kind !== 'internal') fail('unsupported schema or boundary');
  const contracts = array(c.contracts, 128, 1).map(x => {
    const p = keys(x, ['contract_id', 'ontology_contract', 'fields']);
    const fields = array(p.fields, 256).map(x => {
      const f = keys(x, ['name', 'ontology_field', 'meaning', 'type']);
      if (typeof f.meaning !== 'string' || !f.meaning.trim()) fail('field meaning required');
      return {name: identifier(f.name, field), ontology_field: identifier(f.ontology_field, ontology), meaning: f.meaning as string, type: type(f.type)};
    });
    unique(fields.map(f => f.name)); unique(fields.map(f => f.ontology_field));
    return {contract_id: identifier(p.contract_id, local), ontology_contract: identifier(p.ontology_contract, ontology), fields};
  });
  unique(contracts.map(c => c.contract_id)); unique(contracts.map(c => c.ontology_contract));
  const operations = array(c.operations, 128, 1).map(x => {
    const m = keys(x, ['operation_id', 'operation_ref', 'request', 'result']);
    return {operation_id: identifier(m.operation_id, local), operation_ref: identifier(m.operation_ref, selector), request: type(m.request), result: type(m.result)};
  });
  unique(operations.map(o => o.operation_id)); unique(operations.map(o => o.operation_ref));
  const result = {schema_version: TYPED_INTERFACE_VERSION, ontology_interface: identifier(c.ontology_interface, ontology), boundary_kind: c.boundary_kind,
    version_policy: decodeInterfaceVersionPolicy(c.version_policy), contracts, operations} as NamedInterfaceContract;
  checkInterfacePublicClosure(result, [] , false);
  return freeze(result);
}

/** Public contracts retain local identities. Shared domain values retain their real metatype. */
export function checkInterfacePublicClosure(contract: NamedInterfaceContract, declarations: readonly TypedValueDeclaration[], checkDomain = true): void {
  const publicTypes = new Map(contract.contracts.map(c => [c.contract_id, c]));
  const domainTypes = new Map(declarations.map(c => [c.selector, c]));
  const active = new Set<string>(), done = new Set<string>();
  const expand = (id: string, action: () => void): void => {
    if (active.has(id)) fail('recursive value embedding: ' + id);
    if (done.has(id)) return;
    active.add(id); action(); active.delete(id); done.add(id);
  };
  const visit = (t: InterfacePublicType | TypedType): void => {
    if (t.kind === 'contract') {
      const c = publicTypes.get(t.contract_id) ?? fail('unresolved public contract: ' + t.contract_id);
      expand('public:' + c.contract_id, () => c.fields.forEach(f => visit(f.type)));
    } else if (t.kind === 'named' && checkDomain) {
      const d = domainTypes.get(t.selector) ?? fail('unresolved domain value: ' + t.selector);
      if (d.kind === 'Entity') fail('public Entity snapshot leak: ' + t.selector);
      expand('domain:' + t.selector, () => d.kind === 'Enum'
        ? d.contract.variants.forEach(v => {if (v.payload) visit(v.payload);})
        : d.contract.properties.forEach(f => visit(f.type)));
    } else if (t.kind === 'sum') t.variants.forEach(v => {if (v.payload) visit(v.payload);});
    else if (t.kind === 'optional' || t.kind === 'list' || t.kind === 'set') visit(t.element);
  };
  contract.contracts.forEach(c => visit({kind: 'contract', contract_id: c.contract_id}));
  contract.operations.forEach(o => {visit(o.request); visit(o.result);});
}
