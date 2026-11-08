import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {sha256} from '../input/source-manifest.js';
import type {DeclarativeFunctionContract, DeclarativeExpression, DeclarativeNode} from '../typed-backend/declarative-function.js';
import type {TypedCalculationContract, NumericExpression} from '../typed-backend/contracts.js';

export const COMPOSITION_REFERENCE_DEFINITION_SHA256 = 'ee1085c3f524c2adc5e99bf32a02ff6d54a11045b3fb5c73eae1dd14ca90d23b';
export class CompositionReferenceUnavailable extends Error {
  constructor(reason: string) { super('COMPOSITION_REFERENCE_UNAVAILABLE:' + reason); this.name = 'CompositionReferenceUnavailable'; }
}
const unavailable = (reason: string): never => { throw new CompositionReferenceUnavailable(reason); };
const fault = (code: string): never => { throw Object.assign(new Error(code), {code}); };
const maximum = 18446744073709551615n;
type Scope = Record<string, any>;
type Event = Readonly<Record<string, unknown>>;
export interface ReferenceCalculation {
  readonly contract: TypedCalculationContract;
  readonly arguments: readonly {authored_name: string; core_name: string}[];
}
export type CompositionReferenceRequest = Readonly<{mode: 'execute' | 'validate-input'; binding?: string; phase?: 'guard' | 'input'}>;
export type CompositionReferenceResult = Readonly<{
  outcome: Readonly<{kind: 'value'; value: unknown} | {kind: 'error'; code: string}>;
  observations: readonly Event[];
}>;
const inputs = (node: DeclarativeNode) => node.inputs ?? (node.input ? [node.input] : []);
const builtins = new Set(['eq', 'ne', 'lt', 'lte', 'gt', 'gte', 'and', 'or', 'not', 'present', 'lower', 'uint64', 'optional_uint64', 'decimal', 'format', 'text', 'coalesce', 'count', 'one', 'first', 'distinct', 'sort', 'column']);

/** This is a verifier fixture boundary, not a replacement for product validation. */
function capture<T>(value: T, budget = {visits: 0, bytes: 0}): T {
  const text = (value: string) => { if ((budget.bytes += Buffer.byteLength(value)) > 8388608) unavailable('capture byte capacity'); };
  const active = new Set<object>(), copies = new Map<object, any>();
  function copy(v: any, depth: number): any {
    if (++budget.visits > 20000 || depth > 64) unavailable('capture capacity');
    if (typeof v === 'string' || typeof v === 'bigint') { text(v.toString()); return v; }
    if (v === null || v === undefined || typeof v === 'boolean') return v;
    if (typeof v === 'number') return Number.isFinite(v) ? v : unavailable('non-finite number');
    if (typeof v !== 'object') return unavailable('inert data required');
    if (active.has(v)) unavailable('cyclic fixture');
    if (copies.has(v)) return copies.get(v);
    const array = Array.isArray(v), proto = Object.getPrototypeOf(v);
    if (array ? proto !== Array.prototype : proto !== Object.prototype && proto !== null) unavailable('custom prototype');
    const keys = Reflect.ownKeys(v);
    if (keys.some(k => typeof k !== 'string')) unavailable('symbol property');
    if (array ? v.length > 4096 || keys.length !== v.length + 1 : keys.length > 2048) unavailable('capture shape/capacity');
    const out: any = array ? [] : Object.create(proto);
    active.add(v); copies.set(v, out);
    const names = array ? Array.from({length: v.length}, (_, i) => String(i)) : keys as string[];
    for (const key of names) {
      text(key);
      const descriptor = Object.getOwnPropertyDescriptor(v, key);
      if (!descriptor || !Object.hasOwn(descriptor, 'value') || !descriptor.enumerable) unavailable('own enumerable data required');
      Object.defineProperty(out, key, {value: copy(descriptor!.value, depth + 1), enumerable: true});
    }
    active.delete(v);
    return Object.freeze(out);
  }
  return copy(value, 0);
}

function errorCode(error: unknown): string {
  const e = error as {code?: unknown; message?: unknown} | null;
  if (typeof e?.code === 'string' && /^[A-Z][A-Z0-9_]*$/.test(e.code)) return e.code;
  return String(e?.message ?? '').match(/\bCALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)\b/)?.[0] ?? 'EVALUATION_FAILED';
}
function unsigned(value: any): bigint {
  if (typeof value === 'string') {
    if (!value.length || value.length > 1 && value[0] === '0' || [...value].some(c => c < '0' || c > '9')) fault('FUNCTION_UINT64');
  } else if (typeof value === 'number') {
    if (!Number.isSafeInteger(value)) fault('FUNCTION_UINT64');
  } else if (typeof value !== 'bigint') fault('FUNCTION_UINT64');
  const n = BigInt(value);
  if (n < 0n || n > maximum) fault('FUNCTION_UINT64');
  return n;
}

/** Independent AST arithmetic: no production evaluator or generated program is read. */
function calculate(binding: ReferenceCalculation, values: Scope, tick: () => void): bigint {
  const contract = binding.contract;
  if (contract.schema_version !== 'domainspec.typed-calculation/v1' || contract.result.kind !== 'scalar' || contract.result.name !== 'UInt64' || contract.inputs.some(p => p.type.kind !== 'scalar' || p.type.name !== 'UInt64')) unavailable('unsupported Calculation');
  const renamed = new Map<string, bigint>();
  for (const argument of binding.arguments) {
    // The selected exact Calculation surface normalizes bigint, canonical strings
    // and safe integers. Its input TypeError has no domain code; composition
    // observation therefore normalizes it to EVALUATION_FAILED.
    try { renamed.set(argument.core_name, unsigned(values[argument.authored_name])); }
    catch { throw new TypeError('CALCULATION_INPUT'); }
  }
  const visit = (e: NumericExpression): bigint => {
    tick();
    if (e.op === 'literal') return BigInt(e.value);
    if (e.op === 'input') return renamed.get(e.name) ?? unavailable('missing core argument');
    const left = visit(e.left), right = visit(e.right);
    let result: bigint;
    switch (e.op) {
      case 'add': result = left + right; break;
      case 'subtract': result = left - right; break;
      case 'multiply': result = left * right; break;
      case 'divide': {
        if (!right) fault('CALCULATION_DIVIDE_BY_ZERO');
        const remainder = left % right;
        if (remainder && contract.division_rounding === 'reject') fault('CALCULATION_INEXACT');
        result = left / right + (remainder && contract.division_rounding === 'ceil' ? 1n : 0n); break;
      }
      default: return unavailable('unsupported arithmetic');
    }
    if (result < 0n) fault('CALCULATION_UNDERFLOW');
    if (result > maximum) fault('CALCULATION_OVERFLOW');
    return result;
  };
  return visit(contract.expression);
}

/** Private conformance kernel. Callers supply a compiler-validated contract.
 * This entry does not establish source validation/provenance; use the bound entry
 * below for project verification. It accepts inert source arithmetic, never code. */
export function evaluateCompositionReference(
  source: DeclarativeFunctionContract, callerRoots: unknown,
  sourceCalculations: Readonly<Record<string, ReferenceCalculation>> = {},
  request: CompositionReferenceRequest = {mode: 'execute'}
): CompositionReferenceResult {
  const sourceBudget = {visits: 0, bytes: 0}, evidenceBudget = {visits: 0, bytes: 0};
  const c = capture(source, sourceBudget), capturedRoots = capture(callerRoots, sourceBudget) as Scope, calculations = capture(sourceCalculations, sourceBudget), options = capture(request, sourceBudget);
  const roots = Object.fromEntries(Object.keys(c.roots).map(name => [name, capturedRoots[name]]));
  if (!['domainspec.declarative-function/v1', 'domainspec.declarative-function/v2'].includes(c.schema_version)) unavailable('unsupported source profile');
  if (!['execute', 'validate-input'].includes(options.mode)) unavailable('unsupported request');
  let steps = 0;
  const tick = () => { if (++steps > 100000) unavailable('evaluation capacity'); };
  const nodes = new Map(c.nodes.map(n => [n.id, n])), memo = new Map<string, any>(), active = new Set<string>();
  const observations: Event[] = [];
  const emit = (event: Event) => { tick(); observations.push(capture(event, evidenceBudget)); };
  const observed = (declaration: string, node_kind: string, compute: () => any): any => {
    emit({kind: 'node-start', declaration, node_kind});
    try {
      const value = compute();
      emit({kind: 'node-result', declaration, node_kind, ...(node_kind === 'Query' ? {count: value.length} : {value})});
      return value;
    } catch (error) {
      if (error instanceof CompositionReferenceUnavailable) throw error;
      emit({kind: 'node-error', declaration, node_kind, code: errorCode(error)}); throw error;
    }
  };
  const nodeValue = (name: string, args: any[] = []): any => {
    tick();
    const node = nodes.get(name) ?? unavailable('missing declaration');
    const parameters = inputs(node);
    if (args.length !== parameters.length) unavailable('Mapping arity');
    if (!parameters.length && memo.has(name)) return memo.get(name);
    if (active.has(name)) unavailable('cyclic declaration');
    active.add(name);
    try {
      const value = observed(name, node.kind, () => {
        const scope = {...roots};
        parameters.forEach((p, i) => { scope[p.name] = args[i]; });
        if (node.kind === 'Rule') return evaluate(node.expression!, scope);
        if (node.kind === 'Mapping') {
          const fields: Scope = {};
          for (const [name, expression] of Object.entries(node.fields!)) fields[name] = evaluate(expression, scope);
          return Object.freeze(fields);
        }
        if (node.kind !== 'Query') return unavailable('unsupported declaration');
        const rows = evaluate(node.source!, scope) as any[], selected: any[] = [];
        emit({kind: 'query-start', declaration: name, total: rows.length});
        for (let index = 0; index < rows.length; index++) {
          tick(); const row = rows[index], accepted = evaluate(node.where!, {...scope, [node.binding!]: row});
          emit({kind: 'query-row', declaration: name, index, accepted, row});
          if (accepted) selected.push(row);
        }
        const result: any[] = [];
        for (const row of selected) result.push(evaluate(node.select!, {...scope, [node.binding!]: row}));
        return result;
      });
      if (!parameters.length) memo.set(name, value);
      return value;
    } finally { active.delete(name); }
  };
  const evaluate = (e: DeclarativeExpression, scope: Scope): any => {
    tick();
    if (e.op === 'literal') return e.value;
    if (e.op === 'path') {
      const head = e.path[0]!;
      let value = Object.hasOwn(scope, head) ? scope[head] : nodeValue(head);
      for (const field of e.path.slice(1)) value = value[field];
      return value;
    }
    if (e.op === 'exists' || e.op === 'forall' || e.op === 'exactly_one') {
      const rows = evaluate(e.collection, scope); let count = 0;
      for (const row of rows) {
        const matches = evaluate(e.where, {...scope, [e.binding]: row});
        if (e.op === 'exists' && matches) return true;
        if (e.op === 'forall' && !matches) return false;
        if (matches) count++;
      }
      return e.op === 'forall' || e.op === 'exactly_one' && count === 1;
    }
    if (e.op !== 'call') return unavailable('unsupported expression');
    const arg = (index: number) => evaluate(e.args[index]!, scope);
    // These three operators deliberately do not evaluate their unused argument.
    if (e.name === 'and') return arg(0) && arg(1);
    if (e.name === 'or') return arg(0) || arg(1);
    if (e.name === 'coalesce') return arg(0) ?? arg(1);
    const args = e.args.map(value => evaluate(value, scope)), [a, b] = args;
    if (nodes.has(e.name)) return nodeValue(e.name, args);
    if (Object.hasOwn(c.calculations, e.name)) {
      const binding = calculations[e.name] ?? unavailable('missing Calculation binding');
      const values = Object.fromEntries(c.calculations[e.name]!.map((name, i) => [name, args[i]]));
      return observed(e.name, 'Calculation', () => calculate(binding, values, tick));
    }
    switch (e.name) {
      case 'eq': return a === b;
      case 'ne': return a !== b;
      case 'lt': return a < b;
      case 'lte': return a <= b;
      case 'gt': return a > b;
      case 'gte': return a >= b;
      case 'not': return !a;
      case 'present': return a != null;
      case 'lower': return c.portability ? [...a].map(ch => ch >= 'A' && ch <= 'Z' ? ch.toLowerCase() : ch).join('') : a.toLowerCase();
      case 'uint64': return unsigned(a);
      case 'optional_uint64': return a == null ? null : unsigned(a);
      case 'decimal': {
        const parts = a.split('.');
        const digits = (s: string) => !!s.length && [...s].every(ch => ch >= '0' && ch <= '9');
        if (parts.length > 2 || !digits(parts[0]) || parts[0].length > 1 && parts[0][0] === '0' || parts.length === 2 && (b === 0 || !digits(parts[1]) || parts[1].length > b)) fault('FUNCTION_DECIMAL');
        const fraction = parts[1] ?? '';
        return unsigned(BigInt(parts[0]) * 10n ** BigInt(b) + BigInt(fraction.padEnd(b, '0') || '0'));
      }
      case 'format': {
        const text = unsigned(a).toString();
        if (!b) return text;
        const padded = text.padStart(b + 1, '0'); return padded.slice(0, -b) + '.' + padded.slice(-b);
      }
      case 'text': return a.toString();
      case 'count': return a.length;
      case 'one': if (a.length !== 1) fault('DS_QUERY_CARDINALITY'); return a[0];
      case 'first': if (!a.length) fault('DS_QUERY_EMPTY'); return a[0];
      case 'distinct': {
        const seen = new Set(), values = [];
        for (const value of a) { tick(); if (!seen.has(value)) {seen.add(value); values.push(value);} }
        return values;
      }
      case 'sort': return [...a].sort((left, right) => {tick(); return left < right ? -1 : left > right ? 1 : 0;});
      case 'column': return a.map((row: Scope) => {tick(); return row[b];});
      default: return unavailable('unsupported builtin');
    }
  };
  const assertion = (index: number, phase: 'input' | 'behavior') => {
    const source = c.assertions[index]!, passed = evaluate(source.condition, roots);
    emit({kind: 'assertion', index, phase, code: source.code, passed});
    if (!passed) fault(source.code);
  };
  const inputOnly = (e: DeclarativeExpression): boolean => {
    tick();
    if (e.op === 'literal') return true;
    if (e.op === 'path') return e.path[0] === 'input';
    return e.op === 'call' && builtins.has(e.name) && e.args.every(inputOnly);
  };
  const run = (): any => {
    if (options.mode === 'validate-input') {
      c.assertions.forEach((a, i) => { if (inputOnly(a.condition)) assertion(i, 'input'); }); return undefined;
    }
    if (c.bindings?.length && options.binding !== undefined) {
      const binding = c.bindings.find(b => b.name === options.binding);
      if (options.phase === 'input') {
        if (!binding?.input) fault('FUNCTION_BINDING_INPUT_REQUIRED');
        return nodeValue(binding!.input!.mapping);
      }
      if (!binding?.condition) fault('FUNCTION_BINDING_REQUIRED');
      return evaluate(binding!.condition!, roots);
    }
    c.assertions.forEach((_, i) => assertion(i, 'behavior'));
    const matches: number[] = [];
    c.results.forEach((result, index) => {
      const passed = evaluate(result.condition, roots); emit({kind: 'result-case', index, passed});
      if (passed) matches.push(index);
    });
    if (matches.length !== 1) fault('DS_RESULT_CARDINALITY');
    const index = matches[0]!; emit({kind: 'selected-case', index});
    return evaluate(c.results[index]!.value, roots);
  };
  let outcome: CompositionReferenceResult['outcome'];
  try { outcome = {kind: 'value', value: capture(run(), evidenceBudget)}; }
  catch (error) {
    if (error instanceof CompositionReferenceUnavailable) throw error;
    outcome = {kind: 'error', code: errorCode(error)};
  }
  return Object.freeze({outcome: Object.freeze(outcome), observations: Object.freeze(observations)});
}

/** Project-owned reference. Does not consult composition artifacts or execute an
 * application endpoint, adapter, factory, or transport provider. */
export function createCompositionReference(graph: CompiledProjectGraph, id: string, definition: string) {
  if (sha256(definition) !== COMPOSITION_REFERENCE_DEFINITION_SHA256) unavailable('definition drift');
  assertCompiledProjectSnapshot(graph);
  const composition = graph.compositions?.find(c => c.id === id) ?? unavailable('unknown composition');
  const contract = capture(composition.source.contract) as DeclarativeFunctionContract;
  const calculations: Record<string, ReferenceCalculation> = {};
  for (const [name, arguments_] of Object.entries(contract.calculations)) {
    const binding = composition.source.core_bindings[name];
    const node = graph.nodes.find(n => n.selector === binding.selector) ?? unavailable('unknown Calculation owner');
    if (node.kind !== 'Calculation') unavailable('Calculation owner kind');
    calculations[name] = capture({contract: node.body.typed_contract as unknown as TypedCalculationContract,
      arguments: arguments_.map(authored_name => ({authored_name, core_name: binding.fields[authored_name]}))});
  }
  return Object.freeze({id, source_sha256: sha256(composition.source.source_text),
    evaluate: (roots: unknown, request?: CompositionReferenceRequest) => evaluateCompositionReference(contract, roots, calculations, request)});
}
