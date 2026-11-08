/** Explicit v2 successor: exact authored literals and standalone pure values. */
export const EXACT_CALCULATION_VERSION = 'domainspec.typed-calculation/v2';
export type ExactNumericExpression =
  | Readonly<{op: 'literal'; value: string}>
  | Readonly<{op: 'input'; name: string}>
  | Readonly<{op: 'add' | 'subtract' | 'multiply' | 'divide'; left: ExactNumericExpression; right: ExactNumericExpression}>;
export interface ExactCalculationContract {
  readonly schema_version: typeof EXACT_CALCULATION_VERSION;
  readonly ontology_calculation: string;
  readonly inputs: readonly Readonly<{name: string; type: Readonly<{kind: 'scalar'; name: 'UInt64'}>}>[];
  readonly result: Readonly<{kind: 'scalar'; name: 'UInt64'}>;
  readonly division_rounding: 'floor' | 'ceil' | 'reject';
  readonly expression: ExactNumericExpression;
}
const fail = (reason: string): never => {throw Object.assign(new TypeError('MTCLI_EXACT_CALCULATION:' + reason), {code: 'MTCLI_EXACT_CALCULATION', exitCode: 22});};
function inert(value: unknown, depth = 0, budget = {nodes: 0}): void {
  if (++budget.nodes > 30000 || depth > 64) fail('data bounds');
  if (value === null || typeof value === 'string' || typeof value === 'boolean' || typeof value === 'number' && Number.isFinite(value)) return;
  if (!value || typeof value !== 'object') fail('JSON data required');
  const array = Array.isArray(value), proto = Object.getPrototypeOf(value);
  if (array ? proto !== Array.prototype : proto !== Object.prototype && proto !== null) fail('plain data required');
  const descriptors = Object.getOwnPropertyDescriptors(value);
  if (array) {
    const length = descriptors.length!.value;
    if (length > 128 || Reflect.ownKeys(descriptors).length !== length + 1) fail('dense bounded array required');
    for (let i = 0; i < length; i++) if (!Object.hasOwn(descriptors, String(i))) fail('dense array required');
  }
  for (const key of Reflect.ownKeys(descriptors)) {
    if (array && key === 'length') continue;
    const descriptor = descriptors[key as string];
    if (typeof key !== 'string' || !descriptor || !Object.hasOwn(descriptor, 'value') || !descriptor.enumerable) fail('inert fields required');
    inert(descriptor!.value, depth + 1, budget);
  }
}
function keys(value: unknown, expected: readonly string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).length !== expected.length || expected.some(k => !Object.hasOwn(value, k))) return fail('closed fields');
  return value as Record<string, unknown>;
}
const id = (value: unknown, pattern: RegExp): string => typeof value === 'string' && value.length <= 256 && pattern.exec(value)?.[0] === value ? value : fail('identifier');
const local = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
const scalar = (value: unknown) => {
  const t = keys(value, ['kind', 'name']);
  if (t.kind !== 'scalar' || t.name !== 'UInt64') fail('UInt64 required');
  return Object.freeze({kind: 'scalar' as const, name: 'UInt64' as const});
};
export function decodeExactCalculation(value: unknown): ExactCalculationContract {
  inert(value);
  const c = keys(value, ['schema_version', 'ontology_calculation', 'inputs', 'result', 'division_rounding', 'expression']);
  if (c.schema_version !== EXACT_CALCULATION_VERSION) fail('source version');
  if (!['floor', 'ceil', 'reject'].includes(c.division_rounding as string)) fail('rounding');
  if (!Array.isArray(c.inputs) || c.inputs.length > 128) return fail('inputs');
  const inputs = c.inputs.map(value => {
    const p = keys(value, ['name', 'type']);
    return Object.freeze({name: id(p.name, local), type: scalar(p.type)});
  });
  const names = new Set(inputs.map(p => p.name));
  if (names.size !== inputs.length) fail('duplicate input');
  let nodes = 0;
  const expression = (value: unknown, depth = 0): ExactNumericExpression => {
    if (++nodes > 4096 || depth > 32) return fail('expression bounds');
    const e = value as Record<string, unknown>;
    if (!e || typeof e !== 'object') return fail('expression');
    if (e.op === 'literal') {
      keys(e, ['op', 'value']);
      if (typeof e.value !== 'string' || e.value.length > 20 || /^(0|[1-9][0-9]*)$/.exec(e.value)?.[0] !== e.value || BigInt(e.value) > 18446744073709551615n) return fail('canonical UInt64 decimal literal required');
      return Object.freeze({op: 'literal', value: e.value});
    }
    if (e.op === 'input') {
      keys(e, ['op', 'name']); const name = id(e.name, local);
      if (!names.has(name)) fail('undeclared input:' + name);
      return Object.freeze({op: 'input', name});
    }
    if (!['add', 'subtract', 'multiply', 'divide'].includes(e.op as string)) return fail('operator');
    keys(e, ['op', 'left', 'right']);
    return Object.freeze({op: e.op as 'add' | 'subtract' | 'multiply' | 'divide', left: expression(e.left, depth + 1), right: expression(e.right, depth + 1)});
  };
  return Object.freeze({schema_version: EXACT_CALCULATION_VERSION,
    ontology_calculation: id(c.ontology_calculation, /^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+(?:#[A-Za-z][A-Za-z0-9_]*)?$/),
    inputs: Object.freeze(inputs), result: scalar(c.result), division_rounding: c.division_rounding as ExactCalculationContract['division_rounding'], expression: expression(c.expression)});
}
