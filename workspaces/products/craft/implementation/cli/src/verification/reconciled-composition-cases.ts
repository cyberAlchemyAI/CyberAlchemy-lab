import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {DeclarativeFunctionContract as Contract, DeclarativeExpression as E} from '../typed-backend/declarative-function.js';
import {sha256, canonicalJson} from '../input/source-manifest.js';
import {createCompositionBinding} from './reconciled-composition-binding.js';
import {createCompositionReference, evaluateCompositionReference, type ReferenceCalculation, type CompositionReferenceRequest as Request, type CompositionReferenceResult as Result} from './reconciled-composition-reference.js';
import {encodeCompositionCaseValue as encode, decodeCompositionCaseValue as decode, type CompositionCaseValue} from './reconciled-composition-case-values.js';

export const COMPOSITION_CASES_DEFINITION_SHA256 = 'f9d81d73ec70a14d8797c33a9d417635c15d89383a7a1618bfc3cdda2cb1d07a';
export class CompositionCasesUnavailable extends Error {
  constructor(reason: string, readonly missing: readonly string[] = []) {super('COMPOSITION_CASES_UNAVAILABLE:' + reason); this.name = 'CompositionCasesUnavailable'; Object.freeze(missing);}
}
const fail = (reason: string): never => {throw new CompositionCasesUnavailable(reason);};
const clone = <T>(v: T): T => decode(encode(v)) as T;
const key = (v: unknown) => JSON.stringify(encode(v));
function freeze<T>(v: T): T {if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);} return v;}
const maximum = 18446744073709551615n;
const omitted = Symbol('omitted');
type Slot = {path: string[]; values: unknown[]};
export interface CompositionBehaviorCase {readonly id: string; readonly group: string; readonly request: Request; readonly input: CompositionCaseValue; readonly expected: CompositionCaseValue;}

/** Conservative source dependencies: unknown reachability stays required. */
function coverage(c: Contract) {
  const nodes = new Map(c.nodes.map(n => [n.id, n])), reachable = new Set<string>();
  const literal = (e: E | undefined, value: unknown) => e?.op === 'literal' && e.value === value;
  function declaration(name: string) {
    if (reachable.has(name)) return;
    const n = nodes.get(name);
    if (!n && !Object.hasOwn(c.calculations, name)) return;
    reachable.add(name); if (!n) return;
    const locals = new Set((n.inputs ?? (n.input ? [n.input] : [])).map(p => p.name));
    if (n.kind === 'Mapping') Object.values(n.fields!).forEach(e => expression(e, locals));
    else if (n.kind === 'Rule') expression(n.expression!, locals);
    else {expression(n.source!, locals); locals.add(n.binding!); expression(n.where!, locals); if (!literal(n.where, false)) expression(n.select!, locals);}
  }
  function expression(e: E, locals = new Set<string>()) {
    if (e.op === 'literal') return;
    if (e.op === 'path') {if (!locals.has(e.path[0]!)) declaration(e.path[0]!); return;}
    if (e.op !== 'call') {expression(e.collection, locals); expression(e.where, new Set([...locals, e.binding])); return;}
    declaration(e.name);
    const first = e.args[0];
    const lazy = e.name === 'and' && literal(first, false) || e.name === 'or' && literal(first, true) || e.name === 'coalesce' && first?.op === 'literal' && first.value !== null;
    (lazy ? e.args.slice(0, 1) : e.args).forEach(a => expression(a, locals));
  }
  c.assertions.forEach(a => expression(a.condition));
  c.results.forEach(r => {expression(r.condition); if (!literal(r.condition, false)) expression(r.value);});
  c.bindings?.forEach(b => {if (b.condition) expression(b.condition); if (b.input) declaration(b.input.mapping);});
  return {declarations: [...c.nodes.map(n => n.id), ...Object.keys(c.calculations)].map(id => ({id, required: reachable.has(id)})),
    results: c.results.map((r, index) => ({index, required: !literal(r.condition, false)}))};
}

function typedInputs(c: Contract) {
  const literals: (string | number | boolean | null)[] = [];
  function walk(v: any) {if (!v || typeof v !== 'object') return; if (v.op === 'literal') literals.push(v.value); Object.values(v).forEach(walk);}
  walk(c);
  const strings = ['1', '0', '2', '', 'a', 'b', 'A', 'ÄAZİ', 'é', 'e\u0301', '9007199254740991', '9007199254740993', '18446744073709551615', '18446744073709551616', '1.25', '0.01', 'bad', '01', '-1', '1\n'];
  const integers = [0, 1, -1, 2, Number.MAX_SAFE_INTEGER, Number.MIN_SAFE_INTEGER];
  const unsigned = [0n, 1n, 2n, 9007199254740991n, 9007199254740992n, 9007199254740993n, maximum - 1n, maximum];
  for (const l of literals) {
    if (typeof l === 'string') {
      strings.push(l, l.toLowerCase(), l.toUpperCase());
      if (/^(?:0|[1-9][0-9]{0,19})$/.test(l)) for (const n of [BigInt(l) - 1n, BigInt(l), BigInt(l) + 1n]) if (n >= 0n && n <= maximum) unsigned.push(n);
    }
    if (typeof l === 'number' && Number.isSafeInteger(l)) {
      for (const n of [l, l - 1, l + 1]) if (Number.isSafeInteger(n)) {integers.push(n); strings.push(String(n)); if (n >= 0) unsigned.push(BigInt(n));}
    }
  }
  const unique = (values: unknown[]) => {const seen = new Set<string>(); return values.filter(v => {const k = v === omitted ? 'omitted' : key(v); if (seen.has(k)) return false; seen.add(k); return true;});};
  const primitive: Record<string, unknown[]> = {String: unique(strings), Int: unique(integers), UInt64: unique(unsigned), Bool: [false, true], Null: [null]};
  function seed(type: string, stack: string[] = [], rank = 0, budget = {visits: 0}): any {
    if (stack.length > 64 || ++budget.visits > 20000) return fail('type seed capacity');
    if (type.endsWith('?')) {try {return seed(type.slice(0, -1), [...stack, type], rank, budget);} catch (e) {if (e instanceof CompositionCasesUnavailable && e.message.endsWith(':recursive type')) return null; throw e;}}
    if (type.endsWith('[]')) {try {return [seed(type.slice(0, -2), [...stack, type], rank, budget)];} catch (e) {if (e instanceof CompositionCasesUnavailable && e.message.endsWith(':recursive type')) return []; throw e;}}
    if (primitive[type]) return primitive[type]![rank % primitive[type]!.length];
    if (stack.includes(type)) return fail('recursive type');
    const fields = c.records[type] ?? fail('unknown source type');
    return Object.fromEntries(Object.entries(fields).map(([name, t]) => [name, seed(t, [...stack, type], rank, budget)]));
  }
  const slots: Slot[] = [];
  function add(path: string[], values: unknown[]) {values = unique(values); if (values.length > 256 || slots.length >= 512) fail('slot capacity'); slots.push({path, values});}
  function inspect(type: string, path: string[], stack: string[] = [], allowOmission = true) {
    if (type.endsWith('?')) {add(path, [seed(type), null, undefined, ...(allowOmission ? [omitted] : [])]); if (seed(type) !== null) inspect(type.slice(0, -1), path, stack, allowOmission); return;}
    if (type.endsWith('[]')) {
      const t = type.slice(0, -2); if (stack.includes(t)) {add(path, [[]]); return;}
      const a = seed(t), b = seed(t, [], 1); add(path, [[], [a], [a, a], [a, b], [b, a]]);
      inspect(t, [...path, '0'], stack, false); return;
    }
    if (primitive[type]) {add(path, primitive[type]!); return;}
    if (stack.includes(type)) return;
    for (const [name, t] of Object.entries(c.records[type]!)) inspect(t, [...path, name], [...stack, type]);
  }
  const initial = Object.fromEntries(Object.entries(c.roots).map(([name, t]) => [name, seed(t)]));
  for (const [name, t] of Object.entries(c.roots)) inspect(t, [name]);
  function change(root: unknown, slot: Slot, value: unknown) {
    const out: any = clone(root); let at = out, template: any = initial;
    for (const part of slot.path.slice(0, -1)) {
      template = template[part];
      if (at[part] === null || typeof at[part] !== 'object') at[part] = clone(template);
      at = at[part];
    }
    const last = slot.path.at(-1)!;
    if (value === omitted) delete at[last]; else at[last] = clone(value);
    return out;
  }
  return {initial, slots, change, lockstep: (rank: number) => Object.fromEntries(Object.entries(c.roots).map(([name, t]) => [name, seed(t, [], rank)]))};
}

function build(source: Contract, evaluate: (roots: unknown, request: Request) => Result, definition: string) {
  if (sha256(definition) !== COMPOSITION_CASES_DEFINITION_SHA256) throw new TypeError('COMPOSITION_CASES:definition drift');
  const c = clone(source), inputs = typedInputs(c), required = coverage(c);
  const requests: Request[] = [{mode: 'execute'}, {mode: 'validate-input'}];
  for (const b of c.bindings ?? []) {if (b.condition) requests.push({mode: 'execute', binding: b.name, phase: 'guard'}); if (b.input) requests.push({mode: 'execute', binding: b.name, phase: 'input'});}
  const requestKey = (r: Request) => JSON.stringify(r);
  const obligations = [...requests.map(r => 'phase:' + requestKey(r)), ...required.declarations.filter(r => r.required).map(r => 'node:' + r.id), ...required.results.filter(r => r.required).map(r => 'result:' + r.index)];
  const witnessed = new Map<string, {roots: unknown; request: Request}>(), probes = new Set<string>();
  let ordinary: unknown, attempts = 0, evaluations = 0;
  const beam: {roots: unknown; score: number; serial: number}[] = [];
  function observe(roots: unknown) {
    const identity = sha256(key(roots)); if (probes.has(identity) || attempts >= 4096) return;
    probes.add(identity); attempts++; let score = 0;
    for (const request of requests) {
      const result = evaluate(roots, request); evaluations++;
      const hits: string[] = [];
      if (result.outcome.kind === 'value') {hits.push('phase:' + requestKey(request)); score += 100; if (request === requests[0] && ordinary === undefined) ordinary = clone(roots);}
      for (const event of result.observations) {
        if (event.kind === 'node-result') {hits.push('node:' + event.declaration); score += 2;}
        if (event.kind === 'selected-case') hits.push('result:' + event.index);
        if (event.kind === 'assertion' && event.passed) score++;
      }
      for (const hit of hits) if (!witnessed.has(hit)) witnessed.set(hit, {roots: clone(roots), request});
    }
    beam.push({roots: clone(roots), score, serial: attempts}); beam.sort((a, b) => b.score - a.score || a.serial - b.serial); if (beam.length > 8) beam.pop();
  }
  observe(inputs.initial);
  for (let rank = 1; rank < 32 && obligations.some(o => !witnessed.has(o)); rank++) observe(inputs.lockstep(rank));
  for (let round = 0; round < 3 && obligations.some(o => !witnessed.has(o)) && attempts < 4096; round++) {
    const parents = beam.slice();
    search: for (const parent of parents) for (const slot of inputs.slots) for (const value of slot.values) {
      if (attempts >= 4096) break search;
      observe(inputs.change(parent.roots, slot, value));
    }
  }
  const missing = obligations.filter(o => !witnessed.has(o));
  if (missing.length) throw new CompositionCasesUnavailable('required witness not found within finite search; not an unsatisfiability proof', missing);
  const cases: CompositionBehaviorCase[] = [], identities = new Set<string>(); let bytes = 0;
  function add(roots: unknown, request: Request, group: string) {
    const input = encode(roots), identity = JSON.stringify([request, input]); if (identities.has(identity)) return;
    const expected = encode(evaluate(roots, request)); evaluations++;
    const row = {id: 'composition-' + String(cases.length).padStart(4, '0'), group, request, input, expected};
    bytes += Buffer.byteLength(JSON.stringify(row));
    if (cases.length >= 4095 || bytes > 8388608) fail('final family capacity');
    identities.add(identity); cases.push(row);
  }
  for (const obligation of obligations) {const w = witnessed.get(obligation)!; add(w.roots, w.request, 'witness:' + obligation);}
  const familyRoots = new Map<string, unknown>([[key(ordinary), ordinary]]);
  for (const obligation of obligations) {const roots = witnessed.get(obligation)!.roots; familyRoots.set(key(roots), roots);}
  for (const roots of familyRoots.values()) for (const request of requests) {
    add(roots, request, 'baseline');
    for (const slot of inputs.slots) for (const value of slot.values) add(inputs.change(roots, slot, value), request, 'slot:' + slot.path.join('.'));
  }
  // Exercise the already-declared error behavior, without adding new phases.
  if (c.bindings?.length) for (const phase of ['guard', 'input'] as const) {
    let missingName = '_missing'; while (c.bindings.some(b => b.name === missingName)) missingName += '_';
    add(ordinary, {mode: 'execute', binding: missingName, phase}, 'missing-binding');
    for (const b of c.bindings) if (phase === 'guard' ? !b.condition : !b.input) add(ordinary, {mode: 'execute', binding: b.name, phase}, 'missing-binding-phase');
  }
  return freeze({schema_version: 'domainspec.composition-cases/v1-candidate' as const, definition_sha256: COMPOSITION_CASES_DEFINITION_SHA256,
    contract_sha256: sha256(canonicalJson(c)), cases, coverage: {...required, required: obligations, witnessed: obligations}, search: {input_probes: attempts, reference_evaluations: evaluations, slots: inputs.slots.length}, encoded_case_bytes: bytes, authority_effect: 'none' as const});
}

/** Fixture kernel only: source must already have passed compiler validation. */
export function createCompositionContractCases(source: Contract, calculations: Record<string, ReferenceCalculation>, definition: string) {
  const c = clone(source), bindings = clone(calculations);
  return build(c, (roots, request) => evaluateCompositionReference(c, roots, bindings, request), definition);
}
const registered = new WeakSet<object>();
export function createCompositionCases(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, id: string, definitions: {binding: string; reference: string; cases: string}) {
  const binding = createCompositionBinding(graph, plan, id, definitions.binding);
  const reference = createCompositionReference(graph, id, definitions.reference);
  const family = build(graph.compositions!.find(c => c.id === id)!.source.contract, reference.evaluate, definitions.cases);
  const result = freeze({...family, binding}); registered.add(result); return result;
}
export type CompositionCaseFamily = ReturnType<typeof createCompositionCases>;
export function assertCompositionCaseFamily(value: unknown): asserts value is CompositionCaseFamily {
  if (!value || typeof value !== 'object' || !registered.has(value)) throw new TypeError('COMPOSITION_CASES:registered family required');
}
