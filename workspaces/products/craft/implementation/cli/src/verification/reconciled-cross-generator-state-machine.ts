import path from 'node:path';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertReconciledProjectPlan, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {assertCrossGeneratorBoundary, type CrossGeneratorBoundary} from './reconciled-cross-generator-boundary.js';
import {decodeTypedStateMachineContract} from '../typed-backend/state-machine.js';
import {assertPolicyData} from '../typed-backend/policy-rules.js';
import {decodeTypedRuleContract, type RuleExpression} from '../typed-operation/contracts.js';
import {createStructuralFacts, RuleFactsCapacity, type FactRecipe} from './reconciled-rule-facts.js';
import {createStructuralCases} from './reconciled-structural-cases.js';
import {RuleWitnessCapacity} from './reconciled-rule-reference.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';

export const CROSS_GENERATOR_STATE_MACHINE_DEFINITION_SHA256 = '6a2bd9e0b4c19889efc99964e002de42fb94a34508585fb4067e3ea7dc73efca';
const fail = (reason: string): never => {throw new TypeError('CROSS_GENERATOR_STATE_MACHINE:' + reason);};
const same = (a: unknown, b: unknown, reason: string) => {if (canonicalJson(a) !== canonicalJson(b)) fail(reason);};
const sorted = (xs: readonly string[]) => [...new Set(xs)].sort();
const pascal = (s: string) => s.split('-').map(w => w[0]!.toUpperCase() + w.slice(1)).join('');
const relative = (from: string, to: string) => {const p = path.posix.relative(path.posix.dirname(from), to).replace(/\.ts$/, '.js'); return p.startsWith('.') ? p : './' + p;};
const dependencies = (e: RuleExpression): string[] => e.op === 'rule_ref' ? [e.selector] : e.op === 'all' || e.op === 'any' ? e.terms.flatMap(dependencies) : e.op === 'not' ? dependencies(e.term) : e.op === 'exists' || e.op === 'exactly_one' || e.op === 'unique' ? dependencies(e.where) : [];
function freeze<T>(v: T): T {if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);} return v;}
function wire(v: any): unknown {
  if (v === null) return ['null']; if (typeof v === 'bigint') return ['bigint', v.toString()]; if (typeof v !== 'object') return [typeof v, v];
  return Array.isArray(v) ? ['array', v.map(wire)] : ['object', Object.keys(v).sort().map(k => [k, wire(v[k])])];
}
const registered = new WeakSet<object>();
type Call = {selector: string; parent: number | null; arity: number; input: unknown; result: boolean};
type Outcome = {kind: 'value'; value: string} | {kind: 'error'; name: string; message: string};
type Case = {id: string; mode: string; format: string; values: string[]; expected: {id: string; outcome: Outcome; calls: Call[]; getter_reads: number; input_changed: boolean}};

export function createCrossGeneratorStateMachineControls(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, boundary: CrossGeneratorBoundary, definition: string) {
  if (typeof definition !== 'string' || sha256(definition) !== CROSS_GENERATOR_STATE_MACHINE_DEFINITION_SHA256) fail('definition drift');
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan); assertCrossGeneratorBoundary(boundary);
  same(createCompiledProjectCertificate(graph), plan.resolved.certificate, 'foreign graph'); same(boundary.project_plan_sha256, plan.plan_sha256, 'foreign boundary'); same(boundary.source_manifest_sha256, graph.source_manifest.manifest_sha256, 'foreign source');
  const config = JSON.parse(getReconciledSource('configuration'));
  if (config.types.find((t: any) => t.kind === 'State Machine')?.role !== 'domain/state-machines' || config.types.find((t: any) => t.kind === 'Rule')?.role !== 'domain/rules') fail('configured native roles');
  const modulePath = (selector: string, kind: string) => {const [feature, id] = selector.split(':'); return `${plan.selection.module_root}/features/${feature}/src/domain/${kind}/${id}.ts`;};
  const rulesBySelector = new Map(graph.nodes.filter(n => n.kind === 'Rule').map(n => [n.selector, decodeTypedRuleContract(n.body.typed_contract)]));
  const rows = graph.nodes.filter(n => n.kind === 'State Machine').map(node => {
    const contract = decodeTypedStateMachineContract(node.body.typed_contract), guards = contract.transitions.flatMap(t => t.guard ? [t.guard] : []), selected = new Set<string>();
    const visit = (s: string) => {if (selected.has(s)) return; selected.add(s); dependencies((rulesBySelector.get(s) ?? fail('missing Rule')).expression).forEach(visit);}; guards.forEach(g => visit(g.selector));
    const rules = [...selected].sort().map(selector => ({selector, relative_path: modulePath(selector, 'rules'), callable: 'rule' + pascal(selector.split(':')[1]!), contract_sha256: sha256(canonicalJson(rulesBySelector.get(selector)))}));
    const wrapper = modulePath(node.selector, 'state-machines'), provider = wrapper.replace(/\.ts$/, '.provider.ts'), callable = 'transition' + pascal(node.node_id);
    const typeExports = ['Outcome', 'Parameters', 'State', 'Trigger'];
    const imp = (from: string, to: string, names: string[], type_only = false, reexport = false) => ({specifier: relative(from, to), names, target_path: to, type_only, reexport});
    const expectedModules = [
      {selector: node.selector, relative_path: wrapper, callable, initial_state: contract.initial, value_exports: ['initialState', callable].sort(), type_exports: typeExports, imports: [imp(wrapper, provider, ['initialState', 'reduce']), imp(wrapper, provider, typeExports, true, true)]},
      {selector: node.selector, relative_path: provider, callable: 'reduce', initial_state: contract.initial, value_exports: ['initialState', 'reduce'], type_exports: typeExports, imports: sorted(guards.map(g => g.selector)).map(s => imp(provider, modulePath(s, 'rules'), ['rule' + pascal(s.split(':')[1]!)]))},
      ...rules.map(r => ({...r, value_exports: [r.callable], type_exports: [] as string[], imports: sorted(dependencies(rulesBySelector.get(r.selector)!.expression)).map(s => imp(r.relative_path, modulePath(s, 'rules'), ['rule' + pascal(s.split(':')[1]!)]))})),
    ].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1);
    const modules = expectedModules.map(m => {
      const native = boundary.modules.find(n => n.relative_path === m.relative_path) ?? fail('missing module'), edges = boundary.edges.filter(e => e.importer_path === m.relative_path);
      same(native.qualified_selectors, [m.selector], 'module owner');
      same(native.exports, [...m.type_exports.map(name => ({name, kind: 'type'})), ...m.value_exports.map(name => ({name, kind: 'value'}))].sort((a, b) => a.name < b.name ? -1 : 1), 'source exports');
      same(edges.map(e => ({specifier: e.specifier, names: e.names, target_path: e.target_path, type_only: e.type_only, reexport: e.reexport})), m.imports, 'source imports');
      if (edges.some(e => e.namespace || e.category === 'native-standard-library' || e.reexport && !e.type_only)) fail('unsupported native boundary');
      return {...m, sha256: native.sha256, edge_sha256s: edges.map(e => e.edge_sha256)};
    });
    same(modules.map(m => m.relative_path), boundary.roots.find(r => r.selector === node.selector)!.module_paths, 'complete native closure');
    // Wrapper forwarding is bound by surface audits; only actual Rule calls have trace parents.
    const rulePaths = new Set(rules.map(r => r.relative_path));
    const ruleEdges = boundary.edges.filter(e => !e.type_only && (e.importer_path === provider || rulePaths.has(e.importer_path)));
    const edgeVisits = new Map<string, number>();
    const common = {selector: node.selector, contract_sha256: sha256(canonicalJson(contract)), relative_path: wrapper, callable, modules, rules};
    const unmet = (reason: string) => ({...common, state: 'not_evaluable' as const, reason});
    if (!guards.length) return unmet('no Rule guard protocol; guardless reducer behavior belongs to standalone controls');
    try {
      const states = [...contract.states].sort(), triggers = sorted(contract.transitions.map(t => t.trigger_event_ref));
      const pairs = states.flatMap(state => triggers.map(trigger => ({state, trigger, transition: contract.transitions.find(t => t.source_state === state && t.trigger_event_ref === trigger)})));
      const capacity = (): never => {throw new RuleFactsCapacity('bounded guard interoperability capacity');};
      if (pairs.length > 4096) capacity();
      const facts = createStructuralFacts(graph, [...selected], guards.flatMap(g => g.arguments.map(a => a.value)));
      const called = new Set<string>(), sensitivity = new Map<string, Set<boolean>>(); let predictions = 0, traceCalls = 0;
      const structural = createStructuralCases(contract.inputs, facts, scope => {
        predictions += pairs.length; if (predictions > 4096) capacity();
        return canonicalJson(pairs.map(({state, transition: t}) => {
          let calls: Call[] = [];
          const result = (outcome: unknown) => ({outcome, calls});
          if (!t) return result({status: 'rejected', state, reason: 'no-transition', output_intents: []});
          if (t.guard) {
            const trace = facts.reference.traceGuard(t.guard, scope); traceCalls += trace.calls.length; if (traceCalls > 65536) capacity();
            const outcomes = sensitivity.get(t.transition_id) ?? new Set<boolean>(); outcomes.add(trace.result); sensitivity.set(t.transition_id, outcomes);
            calls = trace.calls.map(c => {
              const importer = c.parent === null ? provider : modulePath(trace.calls[c.parent]!.selector, 'rules');
              const edges = ruleEdges.filter(e => e.importer_path === importer && e.target_path === modulePath(c.selector, 'rules'));
              if (edges.length !== 1) fail('source call requires one exact Rule edge');
              const edge = edges[0]!.edge_sha256; edgeVisits.set(edge, (edgeVisits.get(edge) ?? 0) + 1);
              called.add(c.selector); return {selector: c.selector, parent: c.parent, arity: 1, input: wire(c.input), result: c.result};
            });
            if (!trace.result) return result({status: 'rejected', state, reason: 'guard', output_intents: []});
          }
          return result({status: 'transitioned', state: t.target_state, transition_id: t.transition_id, output_intents: t.output_intents});
        }));
      }, 'state-machine', 'STATE_MACHINE_INPUT');
      if (rules.some(r => !called.has(r.selector)) || contract.transitions.some(t => t.guard && sensitivity.get(t.transition_id)?.size !== 2)) return unmet('finite witnesses leave a selected Rule unvisited or guarded transition without true/false sensitivity');
      if (ruleEdges.some(e => !edgeVisits.has(e.edge_sha256))) return unmet('finite witnesses leave an unvisited caller-to-Rule protocol edge');
      const cases: Case[] = [];
      const push = (mode: string, values: string[], outcome: Outcome, calls: Call[] = []) => {if (cases.length >= 4096) capacity(); const id = 'case-' + cases.length; cases.push({id, mode, format: 'string', values, expected: {id, outcome, calls, getter_reads: 0, input_changed: false}});};
      const symbol = (value: string): FactRecipe => ({tag: 'scalar', format: 'string', value});
      push('initial-state', [], {kind: 'value', value: contract.initial});
      for (const c of structural.cases) {
        const outcomes = c.expected.kind === 'value' ? JSON.parse(c.expected.value) : null;
        pairs.forEach((p, i) => push('state-machine', [c.values[0]!, canonicalJson(symbol(p.state)), canonicalJson(symbol(p.trigger))], outcomes ? {kind: 'value', value: canonicalJson(outcomes[i].outcome)} : c.expected as Outcome, outcomes?.[i].calls ?? []));
      }
      const baseline = structural.cases.find(c => c.expected.kind === 'value')!;
      for (const side of ['state', 'trigger']) {
        const valid = symbol(side === 'state' ? states[0]! : triggers[0]!);
        const invalid: FactRecipe[] = [symbol('__semantic_unknown__'), ...['null', 'undefined', 'number', 'boolean', 'array', 'object', 'coercion'].map(mode => ({tag: 'bad' as const, base: valid, mode}))];
        invalid.forEach(v => push('state-machine', [baseline.values[0]!, canonicalJson(side === 'state' ? v : symbol(states[0]!)), canonicalJson(side === 'trigger' ? v : symbol(triggers[0]!))], {kind: 'error', name: 'TypeError', message: 'STATE_MACHINE_INPUT'}));
      }
      const row = {...common, state: 'ready' as const, adapter: 'state-machine' as const, cases, recipes: structural.recipes, declared_pair_count: pairs.length,
        rule_edge_visits: ruleEdges.map(e => ({edge_sha256: e.edge_sha256, calls: edgeVisits.get(e.edge_sha256)!}))};
      if (Buffer.byteLength(canonicalJson(row)) > 8388608) return unmet('serialized guard interoperability capacity'); return row;
    } catch (error) {if (error instanceof RuleFactsCapacity || error instanceof RuleWitnessCapacity) return unmet(error.message); throw error;}
  });
  const coverage = boundary.edges.map(e => ({edge_sha256: e.edge_sha256, category: e.category, state_machine_selectors: rows.filter(r => r.state === 'ready' && r.modules.some(m => m.edge_sha256s.includes(e.edge_sha256))).map(r => r.selector), status: e.category !== 'generated-runtime' ? 'non-runtime' as const : rows.some(r => r.state === 'ready' && r.modules.some(m => m.edge_sha256s.includes(e.edge_sha256))) ? 'protocol-selected' as const : 'not_evaluable' as const}));
  const body = {schema_version: 'domainspec.cross-generator-state-machine-controls/v1-candidate' as const, definition_sha256: CROSS_GENERATOR_STATE_MACHINE_DEFINITION_SHA256, boundary_sha256: boundary.boundary_sha256, project_plan_sha256: plan.plan_sha256, source_manifest_sha256: graph.source_manifest.manifest_sha256, rows, coverage, scope: 'finite-rule-state-machine-guard-interoperability' as const, authority_effect: 'none' as const};
  const result = freeze({...body, controls_sha256: sha256(canonicalJson(body))}); registered.add(result); return result;
}
export type CrossGeneratorStateMachineControls = ReturnType<typeof createCrossGeneratorStateMachineControls>;
export function assertCrossGeneratorStateMachineControls(v: unknown): asserts v is CrossGeneratorStateMachineControls {if (!v || typeof v !== 'object' || !registered.has(v)) fail('registered controls required');}
export function crossGeneratorStateMachineProbe(c: CrossGeneratorStateMachineControls) {
  assertCrossGeneratorStateMachineControls(c);
  return freeze({controls_sha256: c.controls_sha256, rows: c.rows.flatMap(r => r.state !== 'ready' ? [] : [{selector: r.selector, adapter: r.adapter, relative_path: r.relative_path, callable: r.callable, rules: r.rules, modules: r.modules.map(m => ({relative_path: m.relative_path, sha256: m.sha256})), recipes: r.recipes, cases: r.cases.map(({expected, ...input}) => input)}])});
}
export function checkCrossGeneratorStateMachineObservations(c: CrossGeneratorStateMachineControls, observed: unknown) {
  assertCrossGeneratorStateMachineControls(c); assertPolicyData(observed);
  const rows = c.rows.flatMap(r => r.state !== 'ready' ? [] : [{selector: r.selector, cases: r.cases.map(c => c.expected)}]);
  same(observed, {controls_sha256: c.controls_sha256, rows}, 'native observation mismatch');
  return freeze({controls_sha256: c.controls_sha256, tested_state_machine_count: rows.length, tested_case_count: rows.reduce((n, r) => n + r.cases.length, 0), tested_call_count: rows.reduce((n, r) => n + r.cases.reduce((v, c) => v + c.calls.length, 0), 0), remaining: c.rows.filter(r => r.state === 'not_evaluable').map(r => ({selector: r.selector, reason: r.reason})), uncovered_runtime_edge_count: c.coverage.filter(e => e.status === 'not_evaluable').length, public_cross_generator_behavior: 'not_evaluable' as const, authority_effect: 'none' as const});
}
