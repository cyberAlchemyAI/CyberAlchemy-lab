import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {TypedType, ValueExpression} from '../typed-operation/contracts.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {freezeWorkflow} from '../typed-backend/workflow-occurrences.js';
import {createWorkflowExecutionReference, WorkflowExecutionCapacity, type WorkflowExecutionCase, type createBoundWorkflowExecutionReference} from './reconciled-workflow-execution-reference.js';
import {createBoundEffectfulOperationReference} from './reconciled-operation-effect-reference.js';
import type {FactoryBinding} from '../generation/configured-factories.js';
import {OperationReferenceUnsupported, type OperationFixtureMode} from './reconciled-operation-reference.js';
import {operationValueRecipe} from './reconciled-operation-cases.js';
import {createStructuralFacts, RuleFactsCapacity, type FactRecipe} from './reconciled-rule-facts.js';
import {createOwnedValueContext, isWitnessUnavailable} from './reconciled-value-context.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';

export const WORKFLOW_CASES_DEFINITION_SHA256 = '8e63a066cff9503aee8338e19dea2784aa71b54ecab8bb4ba038cfaa8b1c8810';
export class WorkflowCasesUnavailable extends Error {}
const modes: readonly OperationFixtureMode[] = ['committed', 'rejected', 'indeterminate', 'begin-throw', 'commit-throw', 'rollback-throw', 'receipt-empty', 'receipt-unknown', 'receipt-extra', 'receipt-null', 'receipt-getter', 'receipt-inherited', 'receipt-symbol', 'receipt-hidden', 'receipt-array', 'receipt-undefined'];
const capacity = (reason: string): never => {throw new WorkflowCasesUnavailable('bounded Workflow ' + reason);};
const field = (tagged: any, name: string): any => tagged?.[0] === 'record' ? tagged[1].find((r: any) => r[0] === name)?.[1] : undefined;
// Only the independent reference supplies these tags; native outputs never seed cases.
function expectedRecipe(tagged: any): FactRecipe {
  const [tag, value] = tagged;
  if (tag === 'null') return {tag: 'null'};
  if (tag === 'bigint' || tag === 'number') return {tag: 'scalar', value: String(value), format: tag};
  if (tag === 'string' || tag === 'boolean') return {tag: 'scalar', value};
  if (tag === 'array') return {tag: 'list', items: value.map(expectedRecipe)};
  if (tag === 'record') return {tag: 'fields', fields: Object.fromEntries(value.map(([k, v]: [string, any]) => [k, expectedRecipe(v)]))};
  throw new OperationReferenceUnsupported('Workflow read-key oracle tag');
}

export function createWorkflowCases(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledProjectPlan,
  definitions: Parameters<typeof createWorkflowExecutionReference>[3], definition: string) {
  if (typeof definition !== 'string' || sha256(definition) !== WORKFLOW_CASES_DEFINITION_SHA256) throw new TypeError('WORKFLOW_CASES:definition drift');
  const oracle = createWorkflowExecutionReference(node, graph, plan, definitions);
  return createWorkflowSemanticCases(graph, oracle, plan.selection.factories,
    selector => createOwnedValueContext(graph.nodes.find(n => n.selector === selector)!, graph, plan), definition);
}

/** Preserve all source cases and capacity boundaries across native targets. */
export function createWorkflowSemanticCases(graph: CompiledProjectGraph, oracle: ReturnType<typeof createBoundWorkflowExecutionReference>,
  factories: readonly FactoryBinding[], ownedContext: (selector: string) => Pick<ReturnType<typeof createOwnedValueContext>, 'samples'>,
  definition: string) {
  if (typeof definition !== 'string' || sha256(definition) !== WORKFLOW_CASES_DEFINITION_SHA256) throw new TypeError('WORKFLOW_CASES:definition drift');
  const w = oracle.workflow, b = w.bindings;
  const actions = new Map(oracle.actions.map(action => [action.bindings.selector, action]));
  const owned = createBoundEffectfulOperationReference(graph, oracle.actions[0]!, factories);
  const literals: ValueExpression[] = [];
  const literalSeeds = (v: any): void => {
    if (!v || typeof v !== 'object') return;
    if (v.op === 'literal') literals.push(v);
    for (const x of Object.values(v)) if (Array.isArray(x)) x.forEach(literalSeeds); else if (x && typeof x === 'object') literalSeeds(x);
  };
  literalSeeds(b); oracle.actions.forEach(action => literalSeeds(action.bindings));
  const facts = createStructuralFacts(graph, [...new Set([...oracle.actions.flatMap(action => action.bindings.guards.map(g => g.selector)), ...factories.flatMap(f => f.base_validators.map(v => v.rule))])], literals);
  const contexts = new Map<string, ReturnType<typeof ownedContext>>(), sampleCache = new Map<string, FactRecipe[]>(); let expansion = 0;
  const convert = (r: FactRecipe): FactRecipe => r.tag === 'enum' ? {tag: 'named', selector: r.selector!, input: {tag: 'sum', variant: r.variant!}} :
    {...r, ...(r.input ? {input: convert(r.input)} : {}), ...(r.payload ? {payload: convert(r.payload)} : {}), ...(r.items ? {items: r.items.map(convert)} : {}), ...(r.fields ? {fields: Object.fromEntries(Object.entries(r.fields).map(([k, v]) => [k, convert(v)]))} : {})};
  function samples(type: TypedType, depth = 0): FactRecipe[] {
    if (depth > 64) capacity('owned witness depth exceeded');
    const key = canonicalJson(type), prior = sampleCache.get(key); if (prior) return prior;
    let ownedRows: FactRecipe[] = [];
    if (type.kind === 'named') {
      let c = contexts.get(type.selector);
      if (!c) {c = ownedContext(type.selector); contexts.set(type.selector, c);}
      ownedRows = c.samples(type).map(convert);
    } else if (type.kind === 'optional') ownedRows = [{tag: 'null'}, ...samples(type.element, depth + 1)];
    else if (type.kind === 'sum') ownedRows = type.variants.flatMap(v => v.payload ? samples(v.payload, depth + 1).map(payload => ({tag: 'sum', variant: v.name, payload})) : [{tag: 'sum', variant: v.name}]);
    else if ('element' in type) ownedRows = [{tag: type.kind, items: []}, ...samples(type.element, depth + 1).map(value => ({tag: type.kind, items: [value]}))];
    const rows = [...new Map([...ownedRows, ...facts.samples(type)].map(r => [canonicalJson(r), r])).values()];
    expansion += rows.length; if (expansion > 4096) capacity('witness expansion exceeded');
    const valid: FactRecipe[] = [], structural: FactRecipe[] = [];
    for (const r of rows) {
      try {owned.checkOwned(type, r); valid.push(r);} catch (e) {if (e instanceof OperationReferenceUnsupported || !(e instanceof TypeError)) throw e; structural.push(r);}
    }
    const result = [...valid, ...structural]; sampleCache.set(key, result); return result;
  }
  const eventSamples = (f: any, name: string): FactRecipe[] => {
    const type = f.type_ref.kind === 'reference' ? (owned.eventReferenceScalar(f.type_ref.selector) === 'UInt64' ? 'uint64' : 'reference') : f.type_ref.name;
    return (type === 'integer' ? ['0', '1', '-1', '-9223372036854775808', '9223372036854775807', 0, 1, -1, 0n, 1n, -1n] : type === 'uint64' ? ['0', '1', '9007199254740992', '18446744073709551615', 0, 1, 0n, 1n] : type === 'decimal' ? [0, 1.5, -1.5] : type === 'boolean' ? [false, true] : type === 'string' ? ['', name, 'β😀'] : [name, 'β😀']).map(operationValueRecipe);
  };
  const eventInputs = Object.fromEntries(w.event_inputs.map(e => [e.name, {tag: 'fields', fields: {
    occurrence: {tag: 'fields', fields: {[e.contract.occurrence_id.field_id]: eventSamples(e.contract.occurrence_id, e.name)[0]!}},
    payload: {tag: 'fields', fields: Object.fromEntries(e.contract.payload.map(f => [f.field_id, eventSamples(f, e.name)[0]!]))},
    ...(e.contract.occurred_at_policy === 'required' ? {occurredAt: operationValueRecipe('time-' + e.name)} : {})
  }} as FactRecipe]));
  const reads = w.steps.flatMap((s, step) => actions.get(s.operation_ref)!.reads.map((r, index) => ({step, index, read: r})));
  const inputColumns = b.inputs.map(p => samples(p.type)), readColumns = reads.map(r => samples({kind: 'named', selector: r.read.target})), columns = [...inputColumns, ...readColumns];
  const success = (e: ReturnType<typeof oracle.expected>) => field(e.outcome, 'status')?.[1] === 'succeeded';
  const score = (e: ReturnType<typeof oracle.expected>) => success(e) ? 1000000 : e.batches.length * 1000 + e.port_trace.length;
  const prepare = (vector: readonly FactRecipe[]) => {
    let c: WorkflowExecutionCase = {input: {tag: 'fields', fields: {...eventInputs, ...Object.fromEntries(b.inputs.map((p, i) => [p.name, vector[i]!]))}},
      identity: {workflow_execution_id: 'execution-one', failure_occurrence_id: 'failure-one'}, capture: false,
      steps: w.steps.map((s, i) => ({step_id: s.step_id, mode: 'committed', reads: reads.filter(r => r.step === i).map(r => ({slot: r.read.slot, value: vector[b.inputs.length + reads.indexOf(r)]!})), clocks: actions.get(s.operation_ref)!.events.filter(e => e.contract.occurred_at_policy === 'generated').map(e => ({slot: e.slot, value: 'time-' + s.step_id + '-' + e.slot}))}))};
    // A later read can depend on an earlier read/result. Each restart repairs only
    // reached identity fields; the independent interpreter still owns execution.
    for (let pass = 0; pass <= reads.length; pass++) {
      const expected = oracle.expected(c); let changed = false;
      const steps = c.steps.map(s => ({...s, reads: [...s.reads]}));
      for (const raw of expected.read_requests as {step_id: string; value: unknown}[]) {
        const step = w.steps.findIndex(s => s.step_id === raw.step_id), slot = field(raw.value, 'slot')?.[1];
        const r = reads.find(r => r.step === step && r.read.slot === slot);
        if (!r) throw new OperationReferenceUnsupported('Workflow source read request missing');
        const seed = steps[step]!.reads[r.index]!, key = expectedRecipe(field(raw.value, 'key'));
        if (!seed.value.fields) throw new OperationReferenceUnsupported('Workflow source read witness is not a record');
        if (canonicalJson(seed.value.fields[r.read.identity.name]) !== canonicalJson(key)) {
          steps[step]!.reads[r.index] = {...seed, value: {...seed.value, fields: {...seed.value.fields, [r.read.identity.name]: key}}}; changed = true;
        }
      }
      if (!changed) return {candidate: c, expected};
      c = {...c, steps};
    }
    return capacity('read witness alignment exceeded source read count');
  };
  let baseline: ReturnType<typeof prepare> | undefined, attempts = 0;
  const scored: {vector: readonly FactRecipe[]; score: number}[] = [], searched = new Set<string>();
  const consider = (vector: readonly FactRecipe[]) => {
    const key = canonicalJson(vector); if (searched.has(key) || attempts >= 4096) return;
    searched.add(key); attempts++; const p = prepare(vector); scored.push({vector, score: score(p.expected)}); if (success(p.expected)) baseline = p;
  };
  for (const vector of facts.vectors(columns)) {consider(vector); if (baseline) break;}
  for (let round = 0; !baseline && round < 3 && attempts < 4096; round++) {
    const seeds = [...scored].sort((a, b) => b.score - a.score).slice(0, 32);
    search: for (const seed of seeds) for (let i = 0; i < columns.length; i++) for (const value of columns[i]!) {
      const vector = [...seed.vector]; vector[i] = value; consider(vector); if (baseline || attempts >= 4096) break search;
    }
  }
  if (!baseline) capacity('source search found no complete success witness after ' + attempts + ' candidates; not an unsatisfiability proof');
  const base = baseline!.candidate, recipes: FactRecipe[] = [], cases: SemanticCase[] = [], coverage: Record<string, string> = {}, interned = new Map<string, number>(), seen = new Map<string, string>(); let bytes = 256;
  const charge = (v: unknown) => {bytes += Buffer.byteLength(canonicalJson(v)) + 1; if (bytes > 8388608) capacity('serialized suite exceeds 8 MiB');};
  const intern = (r: FactRecipe): number => {
    const link = (v: FactRecipe): FactRecipe => ({tag: 'ref', value: String(intern(v))});
    const row = {...r, ...(r.base ? {base: link(r.base)} : {}), ...(r.input ? {input: link(r.input)} : {}), ...(r.payload ? {payload: link(r.payload)} : {}), ...(r.items ? {items: r.items.map(link)} : {}), ...(r.fields ? {fields: Object.fromEntries(Object.entries(r.fields).map(([k, v]) => [k, link(v)]))} : {})};
    const text = canonicalJson(row), prior = interned.get(text); if (prior !== undefined) return prior;
    charge(row); const id = recipes.length; recipes.push(row); interned.set(text, id); return id;
  };
  const add = (label: string, c: WorkflowExecutionCase) => {
    const data = {...c, input: intern(c.input), steps: c.steps.map(s => ({...s, reads: s.reads.map(r => ({...r, value: intern(r.value)}))}))};
    const key = canonicalJson(data); let id = seen.get(key);
    if (!id) {
      if (cases.length >= 4095) capacity('case capacity exceeded');
      id = 'case-' + cases.length;
      const row: SemanticCase = {id, mode: 'workflow', format: 'string', values: [key], expected: {kind: 'value', value: canonicalJson(oracle.expected(c))}};
      charge(row); cases.push(row); seen.set(key, id);
    }
    if (Object.hasOwn(coverage, label)) throw new TypeError('WORKFLOW_CASES:duplicate dimension');
    coverage[label] = id; charge({[label]: id});
  };
  const input = (r: FactRecipe): WorkflowExecutionCase => ({...base, input: r});
  const member = (name: string, r: FactRecipe) => input({...base.input, fields: {...base.input.fields, [name]: r}});
  const step = (at: number, change: (s: WorkflowExecutionCase['steps'][number]) => WorkflowExecutionCase['steps'][number]) => ({...base, steps: base.steps.map((s, i) => i === at ? change(s) : s)});
  // Keep empty/nonempty collections, optional presence and every sampled sum
  // branch distinct, without repeating scalar-carrier/value-only negatives.
  const shape = (r: FactRecipe): unknown => ({tag: r.tag, ...(r.variant ? {variant: r.variant} : {}),
    ...(r.input ? {input: shape(r.input)} : {}), ...(r.payload ? {payload: shape(r.payload)} : {}),
    ...(r.items ? {items: r.items.slice(0, 2).map(shape)} : {}), ...(r.fields ? {fields: Object.fromEntries(Object.entries(r.fields).map(([k, v]) => [k, shape(v)]))} : {})});
  const shapes = (rows: readonly FactRecipe[]) => [...rows.reduce((out, r) => {const key = canonicalJson(shape(r)); if (!out.has(key)) out.set(key, r); return out;}, new Map<string, FactRecipe>()).values()];
  add('baseline', base);
  for (const [i, s] of w.steps.entries()) for (const mode of modes) add('settlement/' + s.step_id + '/' + mode, step(i, s => ({...s, mode})));
  add('capture', {...base, capture: true});
  for (const name of ['workflow_execution_id', 'failure_occurrence_id'] as const) for (const value of ['identity-two', '', 'invalid\n', 'x'.repeat(257), 'Upper', 'a--b']) {
    add('identity/' + name + '/' + JSON.stringify(value), {...base, identity: {...base.identity, [name]: value}});
    add('recovery-identity/' + name + '/' + JSON.stringify(value), {...step(w.steps.length - 1, s => ({...s, mode: 'rejected'})), identity: {...base.identity, [name]: value}});
  }
  for (const mode of ['null', 'array', 'inherited', 'extra', 'symbol', 'frozen', 'null-prototype']) add('input/' + mode, input(facts.bad(base.input, mode)));
  for (const [i, p] of b.inputs.entries()) {
    const seed = base.input.fields![p.name]!;
    for (const mode of ['getter', 'non-enumerable', 'missing-field']) add('input/' + p.name + '/' + mode, input(facts.bad(base.input, mode, p.name)));
    inputColumns[i]!.forEach((r, n) => add('sample/' + p.name + '/' + n, member(p.name, r)));
    shapes([seed, ...inputColumns[i]!]).forEach((shape, at) => {
      facts.negative(p.type, shape).forEach((r, n) => add('negative/' + p.name + '/' + at + '/' + n, member(p.name, r)));
      facts.omissions(p.type, shape).forEach((r, n) => add('omission/' + p.name + '/' + at + '/' + n, member(p.name, r.recipe)));
    });
  }
  for (const r of reads) {
    const seed = base.steps[r.step]!.reads[r.index]!, prefix = 'read/' + w.steps[r.step]!.step_id + '/' + r.read.slot + '/';
    const change = (value: FactRecipe, throws = false, rollback = false) => step(r.step, s => ({...s, ...(rollback ? {mode: 'rollback-throw'} : {}), reads: s.reads.map((v, i) => i === r.index ? {...v, value, throws} : v)}));
    add(prefix + 'absent', change({tag: 'null'})); add(prefix + 'throws', change(seed.value, true)); add(prefix + 'rollback-throws', change({tag: 'null'}, false, true));
    shapes([seed.value, ...readColumns[reads.indexOf(r)]!]).forEach((shape, at) => {
      facts.negative({kind: 'named', selector: r.read.target}, shape).forEach((v, n) => add(prefix + 'negative/' + at + '/' + n, change(v)));
      facts.omissions({kind: 'named', selector: r.read.target}, shape).forEach((v, n) => add(prefix + 'omission/' + at + '/' + n, change(v.recipe)));
    });
    facts.samples(r.read.identity.type).forEach((v, n) => add(prefix + 'identity/' + n, change({...seed.value, fields: {...seed.value.fields, [r.read.identity.name]: v}})));
    readColumns[reads.indexOf(r)]!.forEach((v, n) => add(prefix + 'sample/' + n, change({...v, fields: {...v.fields, [r.read.identity.name]: seed.value.fields![r.read.identity.name]!}})));
  }
  for (const e of w.event_inputs) {
    const seed = base.input.fields![e.name]!, prefix = 'event/' + e.name + '/';
    for (const mode of ['getter', 'non-enumerable', 'missing-field']) add(prefix + mode, input(facts.bad(base.input, mode, e.name)));
    for (const mode of ['null', 'array', 'extra', 'symbol', 'inherited', 'getter', 'non-enumerable', 'frozen', 'null-prototype']) add(prefix + 'shape/' + mode, member(e.name, facts.bad(seed, mode, 'payload')));
    for (const [group, fields] of [['occurrence', [e.contract.occurrence_id]], ['payload', e.contract.payload]] as const) for (const f of fields) {
      const parent = seed.fields![group]!, change = (v: FactRecipe) => member(e.name, {...seed, fields: {...seed.fields, [group]: v}});
      const values = [...eventSamples(f, e.name), ...[null, true, '', '01', '-0', '9223372036854775808', '-9223372036854775809', 9007199254740992, 1.5].map(operationValueRecipe)];
      values.forEach((v, n) => add(prefix + group + '/' + f.field_id + '/value/' + n, change({...parent, fields: {...parent.fields, [f.field_id]: v}})));
      for (const mode of ['missing-field', 'getter', 'non-enumerable', 'extra', 'symbol']) add(prefix + group + '/' + f.field_id + '/' + mode, change(facts.bad(parent, mode, f.field_id)));
    }
    for (const [i, value] of [null, '', 0, 'supplied-time'].entries()) add(prefix + 'time/' + i, member(e.name, {...seed, fields: {...seed.fields, occurredAt: operationValueRecipe(value)}}));
    for (const mode of ['missing-field', 'getter', 'non-enumerable']) add(prefix + 'time/' + mode, member(e.name, facts.bad(seed, mode, 'occurredAt')));
  }
  for (const [i, s] of base.steps.entries()) for (const clock of s.clocks) {
    const prefix = 'clock/' + s.step_id + '/' + clock.slot + '/';
    add(prefix + 'missing', {...base, steps: base.steps.map((v, j) => w.steps[j]!.operation_ref === w.steps[i]!.operation_ref ? {...v, clocks: v.clocks.map(c => c.slot === clock.slot ? {...c, mode: 'missing'} : c)} : v)});
    add(prefix + 'throws', step(i, s => ({...s, clocks: s.clocks.map(c => c.slot === clock.slot ? {...c, mode: 'throw'} : c)})));
    for (const [n, value] of ['', null, 0, 'other-time'].entries()) add(prefix + 'value/' + n, step(i, s => ({...s, clocks: s.clocks.map(c => c.slot === clock.slot ? {...c, value} : c)})));
  }
  const result = {recipes, cases, coverage, search: {attempts, success_case_id: coverage.baseline!}};
  if (Buffer.byteLength(canonicalJson(result)) > 8388608) capacity('serialized suite exceeds 8 MiB');
  return freezeWorkflow(result);
}

export const isWorkflowCasesCapacity = (e: unknown): e is Error => e instanceof WorkflowCasesUnavailable || e instanceof WorkflowExecutionCapacity || e instanceof OperationReferenceUnsupported || e instanceof RuleFactsCapacity || isWitnessUnavailable(e);
