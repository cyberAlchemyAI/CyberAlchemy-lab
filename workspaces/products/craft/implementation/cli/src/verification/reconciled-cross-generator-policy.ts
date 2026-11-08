import path from 'node:path';
import type {CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledProjectSnapshot} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertReconciledProjectPlan, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {assertCrossGeneratorBoundary, type CrossGeneratorBoundary} from './reconciled-cross-generator-boundary.js';
import {assertPolicyData, decodeTypedRulePolicyContract} from '../typed-backend/policy-rules.js';
import {decodeTypedRuleContract, type RuleExpression} from '../typed-operation/contracts.js';
import {createStructuralFacts, RuleFactsCapacity} from './reconciled-rule-facts.js';
import {createStructuralCases} from './reconciled-structural-cases.js';
import {RuleWitnessCapacity} from './reconciled-rule-reference.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';

export const CROSS_GENERATOR_POLICY_DEFINITION_SHA256 = '06d37e89a15097e5dcbbb493b996fc57e7117d9d3fa6a962ffd6609b116e5417';
const fail = (s: string): never => {throw new TypeError('CROSS_GENERATOR_POLICY:' + s);};
const same = (a: unknown, b: unknown, s: string) => {if (canonicalJson(a) !== canonicalJson(b)) fail(s);};
const sorted = (xs: readonly string[]) => [...new Set(xs)].sort();
const pascal = (s: string) => s.split('-').map(p => p[0]!.toUpperCase() + p.slice(1)).join('');
const relative = (from: string, to: string) => {const p = path.posix.relative(path.posix.dirname(from), to).replace(/\.ts$/, '.js'); return p.startsWith('.') ? p : './' + p;};
function freeze<T>(v: T): T {if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);} return v;}
const registered = new WeakSet<object>();
const dependencies = (e: RuleExpression): string[] => e.op === 'rule_ref' ? [e.selector] : e.op === 'all' || e.op === 'any' ? e.terms.flatMap(dependencies) : e.op === 'not' ? dependencies(e.term) : e.op === 'exists' || e.op === 'exactly_one' || e.op === 'unique' ? dependencies(e.where) : [];
/** Tagged value transport only, not a native implementation of Rule semantics. */
function wire(v: any): unknown {
  if (v === null) return ['null'];
  if (typeof v === 'bigint') return ['bigint', v.toString()];
  if (typeof v !== 'object') return [typeof v, v];
  if (Array.isArray(v)) return ['array', v.map(wire)];
  return ['object', Object.keys(v).sort().map(k => [k, wire(v[k])])];
}

export function createCrossGeneratorPolicyControls(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, boundary: CrossGeneratorBoundary, definition: string) {
  if (typeof definition !== 'string' || sha256(definition) !== CROSS_GENERATOR_POLICY_DEFINITION_SHA256) fail('definition drift');
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan); assertCrossGeneratorBoundary(boundary);
  same(createCompiledProjectCertificate(graph), plan.resolved.certificate, 'cross-graph plan');
  same(boundary.project_plan_sha256, plan.plan_sha256, 'foreign boundary');
  same(boundary.source_manifest_sha256, graph.source_manifest.manifest_sha256, 'foreign source');
  const config = JSON.parse(getReconciledSource('configuration'));
  if (config.types.find((t: any) => t.kind === 'Policy')?.role !== 'domain/policies' || config.types.find((t: any) => t.kind === 'Rule')?.role !== 'domain/rules') fail('configured native roles');
  const modulePath = (selector: string, kind: 'rules' | 'policies') => {const [feature, id] = selector.split(':'); return `${plan.selection.module_root}/features/${feature}/src/domain/${kind}/${id}.ts`;};
  const ruleNodes = new Map(graph.nodes.filter(n => n.kind === 'Rule').map(n => [n.selector, decodeTypedRuleContract(n.body.typed_contract)]));
  const rows = graph.nodes.filter(n => n.kind === 'Policy').map(node => {
    const contract = decodeTypedRulePolicyContract(node.body.typed_contract);
    const ruleSelectors = new Set<string>();
    const visit = (s: string) => {if (ruleSelectors.has(s)) return; ruleSelectors.add(s); for (const dep of dependencies((ruleNodes.get(s) ?? fail('missing source Rule')).expression)) visit(dep);};
    contract.cases.forEach(c => visit(c.rule.selector));
    const rules = [...ruleSelectors].sort().map(selector => ({selector, relative_path: modulePath(selector, 'rules'), callable: 'rule' + pascal(selector.split(':')[1]!), contract_sha256: sha256(canonicalJson(ruleNodes.get(selector)))}));
    const wrapper = modulePath(node.selector, 'policies'), provider = wrapper.replace(/\.ts$/, '.provider.ts');
    const callable = 'policy' + pascal(node.node_id);
    const expectedModules = [
      {selector: node.selector, relative_path: wrapper, callable, imports: [{specifier: relative(wrapper, provider), names: ['select'], target_path: provider}]},
      {selector: node.selector, relative_path: provider, callable: 'select', imports: sorted(contract.cases.map(c => c.rule.selector)).map(s => ({specifier: relative(provider, modulePath(s, 'rules')), names: ['rule' + pascal(s.split(':')[1]!)], target_path: modulePath(s, 'rules')}))},
      ...rules.map(r => ({...r, imports: sorted(dependencies(ruleNodes.get(r.selector)!.expression)).map(s => ({specifier: relative(r.relative_path, modulePath(s, 'rules')), names: ['rule' + pascal(s.split(':')[1]!)], target_path: modulePath(s, 'rules')}))})),
    ].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1);
    const modules = expectedModules.map(m => {
      const native = boundary.modules.find(n => n.relative_path === m.relative_path) ?? fail('missing source-derived module');
      same(native.qualified_selectors, [m.selector], 'module owner');
      same(native.exports, [{name: m.callable, kind: 'value'}], 'module exports');
      const edges = boundary.edges.filter(e => e.importer_path === m.relative_path);
      same(edges.map(e => ({specifier: e.specifier, names: e.names, target_path: e.target_path})), m.imports, 'source-derived imports');
      if (edges.some(e => e.category !== 'generated-runtime' || e.namespace || e.reexport)) fail('unsupported protocol import');
      return {...m, sha256: native.sha256, edge_sha256s: edges.map(e => e.edge_sha256)};
    });
    same(modules.map(m => m.relative_path), boundary.roots.find(r => r.selector === node.selector)!.module_paths, 'source-derived complete closure');
    // Wrapper forwarding is bound by surface audits; only actual Rule calls have trace parents.
    const rulePaths = new Set(rules.map(r => r.relative_path));
    const ruleEdges = boundary.edges.filter(e => !e.type_only && (e.importer_path === provider || rulePaths.has(e.importer_path)));
    const edgeVisits = new Map<string, number>();
    const common = {selector: node.selector, contract_sha256: sha256(canonicalJson(contract)), relative_path: wrapper, callable, modules, rules};
    const unmet = (reason: string) => ({...common, state: 'not_evaluable' as const, reason});
    try {
      const facts = createStructuralFacts(graph, [...ruleSelectors], contract.cases.flatMap(c => c.rule.arguments.map(a => a.value)));
      const targets = new Set<string>(), branches = new Set<number>(), called = new Set<string>(); let calls = 0;
      const structural = createStructuralCases(contract.inputs, facts, scope => {
        const result = facts.reference.tracePolicy(contract, scope);
        targets.add(result.target); branches.add(result.index); calls += result.calls.length;
        if (calls > 65536) throw new RuleFactsCapacity('Policy interoperability trace limit');
        const trace = result.calls.map(c => {
          const importer = c.parent === null ? provider : modulePath(result.calls[c.parent]!.selector, 'rules');
          const edges = ruleEdges.filter(e => e.importer_path === importer && e.target_path === modulePath(c.selector, 'rules'));
          if (edges.length !== 1) fail('source call requires one exact Rule edge');
          const edge = edges[0]!.edge_sha256; edgeVisits.set(edge, (edgeVisits.get(edge) ?? 0) + 1);
          called.add(c.selector); return {selector: c.selector, parent: c.parent, arity: 1, input: wire(c.input), result: c.result};
        });
        return canonicalJson({target: result.target, calls: trace});
      }, 'policy', 'POLICY_INPUT');
      if (targets.size < 2) return unmet('finite witnesses lack distinct selected targets');
      if (rules.some(r => !called.has(r.selector))) return unmet('finite witnesses leave a selected Rule unvisited; no unreachable-branch claim');
      if (ruleEdges.some(e => !edgeVisits.has(e.edge_sha256))) return unmet('finite witnesses leave an unvisited caller-to-Rule protocol edge');
      const cases = structural.cases.map(c => {
        const result = c.expected.kind === 'value' ? JSON.parse(c.expected.value) : null;
        const {expected, ...input} = c;
        return {...input, expected: {id: c.id, outcome: result ? {kind: 'value', value: result.target} : expected,
          calls: result?.calls ?? [], getter_reads: 0, input_changed: false}};
      });
      const row = {...common, state: 'ready' as const, adapter: 'policy' as const, recipes: structural.recipes, cases,
        rule_edge_visits: ruleEdges.map(e => ({edge_sha256: e.edge_sha256, calls: edgeVisits.get(e.edge_sha256)!})),
        source_predicted_targets: [...targets].sort(), source_predicted_branches: [...branches].sort((a, b) => a - b)};
      if (Buffer.byteLength(canonicalJson(row)) > 8388608) return unmet('Policy interoperability serialized family limit');
      return row;
    } catch (error) {if (error instanceof RuleFactsCapacity || error instanceof RuleWitnessCapacity) return unmet(error.message); throw error;}
  });
  const coverage = boundary.edges.map(e => ({edge_sha256: e.edge_sha256, category: e.category,
    policy_selectors: rows.filter(r => r.state === 'ready' && r.modules.some(m => m.edge_sha256s.includes(e.edge_sha256))).map(r => r.selector),
    status: e.category !== 'generated-runtime' ? 'non-runtime' as const : rows.some(r => r.state === 'ready' && r.modules.some(m => m.edge_sha256s.includes(e.edge_sha256))) ? 'protocol-selected' as const : 'not_evaluable' as const}));
  const body = {schema_version: 'domainspec.cross-generator-policy-controls/v1-candidate' as const, definition_sha256: CROSS_GENERATOR_POLICY_DEFINITION_SHA256,
    boundary_sha256: boundary.boundary_sha256, project_plan_sha256: plan.plan_sha256, source_manifest_sha256: graph.source_manifest.manifest_sha256,
    rows, coverage, scope: 'finite-rule-policy-interoperability' as const, authority_effect: 'none' as const};
  const result = freeze({...body, controls_sha256: sha256(canonicalJson(body))}); registered.add(result); return result;
}
export type CrossGeneratorPolicyControls = ReturnType<typeof createCrossGeneratorPolicyControls>;
export function assertCrossGeneratorPolicyControls(v: unknown): asserts v is CrossGeneratorPolicyControls {
  if (!v || typeof v !== 'object' || !registered.has(v)) fail('registered controls required');
}
/** Expected outcomes and traces are deliberately absent from the child payload. */
export function crossGeneratorPolicyProbe(controls: CrossGeneratorPolicyControls) {
  assertCrossGeneratorPolicyControls(controls);
  return freeze({controls_sha256: controls.controls_sha256, rows: controls.rows.flatMap(r => r.state !== 'ready' ? [] : [{
    selector: r.selector, adapter: r.adapter, relative_path: r.relative_path, callable: r.callable,
    rules: r.rules, modules: r.modules.map(m => ({relative_path: m.relative_path, sha256: m.sha256})), recipes: r.recipes,
    cases: r.cases.map(({expected, ...input}) => input),
  }])});
}
export function checkCrossGeneratorPolicyObservations(controls: CrossGeneratorPolicyControls, observation: unknown) {
  assertCrossGeneratorPolicyControls(controls); assertPolicyData(observation);
  const expected = {controls_sha256: controls.controls_sha256, rows: controls.rows.flatMap(r => r.state !== 'ready' ? [] : [{selector: r.selector, cases: r.cases.map(c => c.expected)}])};
  same(observation, expected, 'native observation mismatch');
  return freeze({controls_sha256: controls.controls_sha256, tested_policy_count: expected.rows.length,
    tested_case_count: expected.rows.reduce((n, r) => n + r.cases.length, 0),
    tested_call_count: expected.rows.reduce((n, r) => n + r.cases.reduce((s, c) => s + c.calls.length, 0), 0),
    remaining: controls.rows.filter(r => r.state === 'not_evaluable').map(r => ({selector: r.selector, reason: r.reason})),
    uncovered_runtime_edge_count: controls.coverage.filter(e => e.status === 'not_evaluable').length,
    public_cross_generator_behavior: 'not_evaluable' as const, authority_effect: 'none' as const});
}
