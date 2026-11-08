import { assertInterfaceData } from '../typed-backend/interface.js';
import { decodeValueExpression, type ValueExpression } from './contracts.js';

export const OPERATION_VALUE_COMPOSITION_VERSION = 'domainspec.operation-value-composition/v1-candidate' as const;
export interface ValueConnectionArgument { readonly parameter: string; readonly value: ValueExpression }
export type OperationValueConnection = Readonly<{
  kind: 'query'; name: string; selector: string; source_slot: string;
  arguments: readonly ValueConnectionArgument[]; absence: 'preserve' | 'require-present';
}> | Readonly<{ kind: 'mapping'; name: string; selector: string; arguments: readonly ValueConnectionArgument[] }>;
export interface OperationValueComposition {
  readonly schema_version: typeof OPERATION_VALUE_COMPOSITION_VERSION;
  readonly operation_ref: string;
  readonly bindings: readonly OperationValueConnection[];
}
const fail = (message: string): never => { throw new TypeError('OPERATION_VALUE_COMPOSITION:' + message); };
const local = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
const selector = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
function identifier(value: unknown, pattern: RegExp): string {
  return typeof value === 'string' && value.length <= 256 && pattern.exec(value)?.[0] === value ? value : fail('invalid identifier');
}
function object(value: unknown, keys: string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).length !== keys.length || keys.some(key => !Object.hasOwn(value, key))) return fail('closed object required');
  return value as Record<string, unknown>;
}
function array(value: unknown, max: number): unknown[] {
  if (!Array.isArray(value) || value.length > max) return fail('bounded array required');
  return value;
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
}
function roots(value: ValueExpression): string[] {
  return value.op === 'path' ? [value.root] : value.op === 'to_set' ? roots(value.value) : [];
}

/** Syntax only; never accepts checked-action custody or authorizes generation. */
export function decodeOperationValueComposition(value: unknown): OperationValueComposition {
  // Existing inert JSON-data validation runs before reading caller members.
  assertInterfaceData(value);
  const input = object(value, ['schema_version', 'operation_ref', 'bindings']);
  if (input.schema_version !== OPERATION_VALUE_COMPOSITION_VERSION) fail('unsupported version');
  const operation_ref = identifier(input.operation_ref, selector);
  const bindings = array(input.bindings, 256).map((raw): OperationValueConnection => {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return fail('binding object required');
    const kind = (raw as Record<string, unknown>).kind;
    if (kind !== 'query' && kind !== 'mapping') return fail('only declared Query and Mapping calls are supported');
    const row = object(raw, kind === 'query' ? ['kind', 'name', 'selector', 'source_slot', 'arguments', 'absence'] : ['kind', 'name', 'selector', 'arguments']);
    const name = identifier(row.name, local), target = identifier(row.selector, selector);
    const args = array(row.arguments, 128).map(raw => {
      const argument = object(raw, ['parameter', 'value']);
      return { parameter: identifier(argument.parameter, local), value: decodeValueExpression(argument.value, '/bindings/arguments/value', true) };
    });
    if (new Set(args.map(arg => arg.parameter)).size !== args.length) fail('duplicate argument');
    args.sort((a, b) => a.parameter < b.parameter ? -1 : a.parameter > b.parameter ? 1 : 0);
    if (kind === 'mapping') return { kind, name, selector: target, arguments: args };
    if (row.absence !== 'preserve' && row.absence !== 'require-present') return fail('explicit absence behavior required');
    if (typeof row.source_slot !== 'string' || !row.source_slot.trim() || row.source_slot.length > 256 || /[\u0000-\u001f\u007f]/.test(row.source_slot)) fail('explicit source slot required');
    return { kind, name, selector: target, source_slot: row.source_slot as string, arguments: args, absence: row.absence as 'preserve' | 'require-present' };
  });
  if (new Set(bindings.map(binding => binding.name)).size !== bindings.length) fail('duplicate value name');
  bindings.sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
  const names = new Set(bindings.map(binding => binding.name));
  const dependencies = new Map(bindings.map(binding => [binding.name, binding.arguments.flatMap(arg => roots(arg.value)).filter(root => names.has(root))]));
  const active = new Set<string>(), done = new Set<string>();
  const visit = (name: string): void => {
    if (active.has(name)) fail('cyclic value bindings');
    if (done.has(name)) return;
    active.add(name); for (const dependency of dependencies.get(name)!) visit(dependency);
    active.delete(name); done.add(name);
  };
  bindings.forEach(binding => visit(binding.name));
  return freeze({ schema_version: OPERATION_VALUE_COMPOSITION_VERSION, operation_ref, bindings });
}
