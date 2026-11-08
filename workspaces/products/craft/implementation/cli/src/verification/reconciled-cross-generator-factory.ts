import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertReconciledProjectPlan, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {assertCrossGeneratorBoundary, type CrossGeneratorBoundary} from './reconciled-cross-generator-boundary.js';
import {assertPolicyData} from '../typed-backend/policy-rules.js';
import type {RuleExpression} from '../typed-operation/contracts.js';
import {createFactoryControls} from './reconciled-factory-controls.js';
import {createRecordRuleReference} from './reconciled-rule-reference.js';
import {isWitnessUnavailable, WitnessUnavailable, type SumRecipe} from './reconciled-value-context.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';

export const CROSS_GENERATOR_FACTORY_DEFINITION_SHA256 = 'c9f8eb24edf603e5600c7eaf64e3504c08a102f106d6be5141e18dcfde95dfab';
const fail = (s: string): never => {throw new TypeError('CROSS_GENERATOR_FACTORY:' + s);};
const same = (a: unknown, b: unknown, s: string) => {if (canonicalJson(a) !== canonicalJson(b)) fail(s);};
const sorted = (xs: readonly string[]) => [...new Set(xs)].sort();
const pascal = (s: string) => s.split('-').map(p => p[0]!.toUpperCase() + p.slice(1)).join('');
function freeze<T>(v: T): T {if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);} return v;}
const registered = new WeakSet<object>();
const dependencies = (e: RuleExpression): string[] => e.op === 'rule_ref' ? [e.selector] : e.op === 'all' || e.op === 'any' ? e.terms.flatMap(dependencies) : e.op === 'not' ? dependencies(e.term) : e.op === 'exists' || e.op === 'exactly_one' || e.op === 'unique' ? dependencies(e.where) : [];
function wire(v: any): unknown {
  if (v === null) return ['null'];
  if (typeof v === 'bigint') return ['bigint', v.toString()];
  if (typeof v !== 'object') return [typeof v, v];
  if (Array.isArray(v)) return ['array', v.map(wire)];
  return ['object', Object.keys(v).sort().map(k => [k, wire(v[k])])];
}

export function createCrossGeneratorFactoryControls(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, boundary: CrossGeneratorBoundary, definition: string) {
  if (typeof definition !== 'string' || sha256(definition) !== CROSS_GENERATOR_FACTORY_DEFINITION_SHA256) fail('definition drift');
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan); assertCrossGeneratorBoundary(boundary);
  same(createCompiledProjectCertificate(graph), plan.resolved.certificate, 'cross-graph plan');
  same(boundary.project_plan_sha256, plan.plan_sha256, 'foreign boundary');
  same(boundary.source_manifest_sha256, graph.source_manifest.manifest_sha256, 'foreign source');
  const config = JSON.parse(getReconciledSource('configuration'));
  for (const [kind, role] of [['Entity', 'domain/entities'], ['Value Object', 'domain/value-objects'], ['Rule', 'domain/rules']])
    if (config.types.find((t: any) => t.kind === kind)?.role !== role) fail('configured native roles');
  const modulePath = (selector: string, role: string) => {const [feature, id] = selector.split(':'); return plan.selection.module_root + '/features/' + feature + '/src/domain/' + role + '/' + id + '.ts';};
  const reference = createRecordRuleReference(graph);
  const rows = graph.nodes.filter(n => n.kind === 'Entity' || n.kind === 'Value Object').map(node => {
    const binding = plan.selection.factories.find(f => f.selector === node.selector) ?? fail('selected factory required');
    const rootPath = modulePath(node.selector, node.kind === 'Entity' ? 'entities' : 'value-objects'), callable = 'create' + pascal(node.node_id) + 'Factory';
    const validators = [
      ...binding.base_validators.map((v, i) => ({...v, occurrence: 'base:' + i})),
      ...binding.extensions.flatMap(e => e.validators.map((v, i) => ({...v, occurrence: 'extension:' + e.id + ':' + i}))),
    ];
    const selectedRules = new Set<string>();
    const visit = (s: string) => {if (selectedRules.has(s)) return; selectedRules.add(s); dependencies((reference.rules.get(s) ?? fail('missing source Rule')).expression).forEach(visit);};
    validators.forEach(v => visit(v.rule));
    const rules = [...selectedRules].sort().map(selector => ({selector, relative_path: modulePath(selector, 'rules'), callable: 'rule' + pascal(selector.split(':')[1]!), contract_sha256: sha256(canonicalJson(reference.rules.get(selector)))}));
    const root = boundary.roots.find(r => r.selector === node.selector) ?? fail('missing factory closure');
    const modules = root.module_paths.map(p => boundary.modules.find(m => m.relative_path === p) ?? fail('missing closure module'));
    const nativeRoot = modules.find(m => m.relative_path === rootPath) ?? fail('source-derived factory path');
    if (!nativeRoot.qualified_selectors.includes(node.selector) || !nativeRoot.exports.some(e => e.kind === 'value' && e.name === callable)) fail('source-derived factory export');
    for (const r of rules) {
      const m = modules.find(m => m.relative_path === r.relative_path) ?? fail('source-derived Rule path');
      same(m.qualified_selectors, [r.selector], 'Rule module owner');
      same(m.exports, [{name: r.callable, kind: 'value'}], 'Rule module export');
      const expected = sorted(dependencies(reference.rules.get(r.selector)!.expression));
      const edges = boundary.edges.filter(e => e.importer_path === r.relative_path);
      same(edges.map(e => e.target_path), expected.map(s => modulePath(s, 'rules')), 'Rule imports');
      for (const e of edges) {
        if (e.category !== 'generated-runtime' || e.namespace || e.reexport) fail('Rule import category');
        const target = rules.find(r => r.relative_path === e.target_path) ?? fail('foreign Rule edge');
        same(e.names, [target.callable], 'Rule import name');
      }
    }
    const direct = sorted(validators.map(v => v.rule));
    const directEdges = boundary.edges.filter(e => e.importer_path === rootPath && rules.some(r => r.relative_path === e.target_path));
    same(directEdges.map(e => e.target_path), direct.map(s => modulePath(s, 'rules')), 'factory Rule bindings');
    for (const e of directEdges) {
      if (e.category !== 'generated-runtime' || e.namespace || e.reexport) fail('factory Rule import category');
      same(e.names, [rules.find(r => r.relative_path === e.target_path)!.callable], 'factory Rule import name');
    }
    const protocolEdges = boundary.edges.filter(e => directEdges.includes(e) || rules.some(r => r.relative_path === e.importer_path));
    const common = {selector: node.selector, kind: node.kind, relative_path: rootPath, callable, modules, rules, protocol_edge_sha256s: protocolEdges.map(e => e.edge_sha256)};
    const unmet = (reason: string) => ({...common, state: 'not_evaluable' as const, reason});
    try {
      const factory = createFactoryControls(node, graph, plan);
      if (factory.state !== 'ready') return unmet(factory.reason);
      same(factory.relative_path, rootPath, 'factory control path'); same(factory.callable, callable, 'factory control callable');
      same(factory.module_paths, root.module_paths, 'factory control complete closure');
      const reached = new Set<string>(), outcomes = new Map<string, Set<boolean>>(), called = new Set<string>(), edgeVisits = new Map<string, number>();
      let calls = 0, accepted = false, rejected = false;
      const cases = factory.cases.map(c => {
        const request = JSON.parse(c.values[0]!) as {route: string; chain: string[]; input: SumRecipe & {field?: string}};
        const predicted = c.expected.kind === 'value' ? JSON.parse(c.expected.value) : null;
        accepted ||= predicted?.ok === true;
        rejected ||= predicted?.failure_codes?.some((s: string) => s.startsWith('RULE_FAIL:')) === true;
        const sequence = [
          ...validators.filter(v => v.occurrence.startsWith('base:')),
          ...request.chain.flatMap(id => validators.filter(v => v.occurrence.startsWith('extension:' + id + ':'))),
        ];
        const trace: {selector: string; parent: number | null; arity: number; input: unknown; result: boolean}[] = [];
        if (predicted?.trace.validators.length) {
          let recipe: SumRecipe & {field?: string} = request.input;
          if (recipe.tag === 'bad') {
            if (recipe.mode === 'frozen' || recipe.mode === 'null-prototype') recipe = recipe.base!;
            else if (recipe.mode === 'missing-field') recipe = {...recipe.base!, fields: {...recipe.base!.fields!, [recipe.field!]: {tag: 'null'}}};
            else fail('source-valid normalization recipe');
          }
          const facts = reference.fact(factory.shape, recipe);
          for (const [i, validator] of predicted.trace.validators.entries()) {
            const v = sequence[i] ?? fail('validator occurrence coverage');
            if (v.rule !== validator.rule) fail('source validator order');
            const rule = reference.rules.get(v.rule)!;
            const args = new Map(v.arguments.map(a => {
              let value = facts; for (const field of a.path ?? [a.field!]) value = value[field];
              return [a.parameter, {type: rule.parameters.find(p => p.name === a.parameter)!.type, value}] as const;
            }));
            const observed = reference.traceEvaluation(v.rule, args), offset = trace.length;
            if (observed.result !== (validator.outcome === 'pass')) fail('source validator outcome');
            reached.add(v.occurrence); if (!outcomes.has(v.occurrence)) outcomes.set(v.occurrence, new Set()); outcomes.get(v.occurrence)!.add(observed.result);
            for (const call of observed.calls) {
              const importer = call.parent === null ? rootPath : modulePath(observed.calls[call.parent]!.selector, 'rules');
              const target = modulePath(call.selector, 'rules');
              const edges = protocolEdges.filter(e => e.importer_path === importer && e.target_path === target);
              if (edges.length !== 1) fail('source call requires one exact protocol edge');
              const edge = edges[0]!.edge_sha256; edgeVisits.set(edge, (edgeVisits.get(edge) ?? 0) + 1);
              called.add(call.selector); trace.push({selector: call.selector, parent: call.parent === null ? null : offset + call.parent, arity: 1, input: wire(call.input), result: call.result});
            }
          }
        }
        calls += trace.length; if (calls > 65536) throw new WitnessUnavailable('factory interoperability trace capacity');
        const {expected, ...input} = c;
        return {...input, expected: {id: c.id, outcome: expected, calls: trace, getter_reads: 0, input_changed: false}};
      });
      if (!accepted || !rejected) return unmet('finite factory witnesses lack accepted and Rule-rejected outcomes');
      if (validators.some(v => !reached.has(v.occurrence)) || rules.some(r => !called.has(r.selector))) return unmet('finite factory witnesses leave selected validator occurrences or Rules unvisited');
      if (protocolEdges.some(e => !edgeVisits.has(e.edge_sha256))) return unmet('finite factory witnesses leave an unvisited caller-to-Rule protocol edge');
      const {cases: originalCases, ...details} = factory;
      const row = {...common, ...details, cases, protocol_edge_visits: protocolEdges.map(e => ({edge_sha256: e.edge_sha256, calls: edgeVisits.get(e.edge_sha256)!})), validator_outcomes: validators.map(v => ({occurrence: v.occurrence, rule: v.rule, outcomes: [...outcomes.get(v.occurrence)!].sort()}))};
      if (Buffer.byteLength(canonicalJson(row)) > 8388608) return unmet('factory interoperability serialized family capacity');
      return row;
    } catch (e) {if (isWitnessUnavailable(e)) return unmet(e.message); throw e;}
  });
  const coverage = boundary.edges.map(e => ({edge_sha256: e.edge_sha256, category: e.category,
    factory_selectors: rows.filter(r => r.state === 'ready' && r.protocol_edge_sha256s.includes(e.edge_sha256)).map(r => r.selector),
    status: e.category !== 'generated-runtime' ? 'non-runtime' as const : rows.some(r => r.state === 'ready' && r.protocol_edge_sha256s.includes(e.edge_sha256)) ? 'protocol-selected' as const : 'not_evaluable' as const}));
  const body = {schema_version: 'domainspec.cross-generator-factory-controls/v1-candidate' as const, definition_sha256: CROSS_GENERATOR_FACTORY_DEFINITION_SHA256,
    boundary_sha256: boundary.boundary_sha256, project_plan_sha256: plan.plan_sha256, source_manifest_sha256: graph.source_manifest.manifest_sha256,
    rows, coverage, scope: 'finite-factory-rule-interoperability' as const, authority_effect: 'none' as const};
  const result = freeze({...body, controls_sha256: sha256(canonicalJson(body))}); registered.add(result); return result;
}
export type CrossGeneratorFactoryControls = ReturnType<typeof createCrossGeneratorFactoryControls>;
export function assertCrossGeneratorFactoryControls(v: unknown): asserts v is CrossGeneratorFactoryControls {
  if (!v || typeof v !== 'object' || !registered.has(v)) fail('registered controls required');
}
/** Helper witness expectations and target expected answers never enter the child. */
export function crossGeneratorFactoryProbe(controls: CrossGeneratorFactoryControls) {
  assertCrossGeneratorFactoryControls(controls);
  const rows = controls.rows.flatMap(r => r.state !== 'ready' ? [] : [{
    selector: r.selector, kind: r.kind, adapter: r.adapter, relative_path: r.relative_path, callable: r.callable,
    rules: r.rules, modules: r.modules.map(m => ({relative_path: m.relative_path, sha256: m.sha256})),
    shape: r.shape, baseline: r.baseline,
    dependencies: Object.fromEntries(Object.entries(r.dependencies).map(([s, d]) => {
      if (d.kind === 'Enum') return [s, d];
      const {binding, probes, ...native} = d; return [s, {...native, probes: []}];
    })),
    cases: r.cases.map(({expected, ...input}) => input),
  }]);
  return freeze({controls_sha256: controls.controls_sha256, rows});
}
export function checkCrossGeneratorFactoryObservations(controls: CrossGeneratorFactoryControls, observation: unknown) {
  assertCrossGeneratorFactoryControls(controls); assertPolicyData(observation);
  const expected = {controls_sha256: controls.controls_sha256, rows: controls.rows.flatMap(r => r.state !== 'ready' ? [] : [{selector: r.selector, cases: r.cases.map(c => c.expected)}])};
  if (!expected.rows.length) fail('no executable factory family');
  same(observation, expected, 'native observation mismatch');
  return freeze({controls_sha256: controls.controls_sha256, tested_factory_count: expected.rows.length,
    tested_case_count: expected.rows.reduce((n, r) => n + r.cases.length, 0),
    tested_call_count: expected.rows.reduce((n, r) => n + r.cases.reduce((s, c) => s + c.calls.length, 0), 0),
    remaining: controls.rows.filter(r => r.state === 'not_evaluable').map(r => ({selector: r.selector, reason: r.reason})),
    uncovered_runtime_edge_count: controls.coverage.filter(e => e.status === 'not_evaluable').length,
    public_cross_generator_behavior: 'not_evaluable' as const, authority_effect: 'none' as const});
}
