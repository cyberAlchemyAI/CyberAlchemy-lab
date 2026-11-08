import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledPythonProject, getPythonDecisionVerificationContext} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {createPythonSemanticControls} from '../../src/verification/reconciled-python-semantic-controls.ts';
import {createRuleSemanticCases} from '../../src/verification/reconciled-rule-controls.ts';
import {createPolicySemanticCases} from '../../src/verification/reconciled-policy-controls.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';

test('Python decisions reuse complete source cases, preserve ordered selection, and never execute strategy targets', t => {
  const f = pythonAllTypesFixture(t);
  const feature = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/feature.json'), 'utf8'));
  const scalar = (name: string): any => ({kind: 'scalar', name}), at = (root: string): any => ({op: 'path', root, properties: []});
  const lit = (type: string, value: unknown): any => ({op: 'literal', type, value});
  const node = (id: string, kind: string, body: any) => {
    feature.nodes.push(id);
    f.write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind, body: {description: id, ...body}});
  };
  const rule = (id: string, parameters: any[], expression: any, version = 'v2') =>
    node(id, 'Rule', {predicate: 'structured:domainspec.typed-rule/' + version, typed_contract: {schema_version: 'domainspec.typed-rule/' + version, ontology_rule: 'FIXTURE-' + id.toUpperCase(), parameters, expression}});
  const numbers = {name: 'numbers', type: {kind: 'list', element: scalar('UInt64')}}, flags = {name: 'flags', type: {kind: 'list', element: scalar('Bool')}};
  rule('large', [numbers], {op: 'exists', collection: at('numbers'), binding: 'n', where: {op: 'lt', left: lit('UInt64', '100'), right: at('n')}});
  rule('one', [flags], {op: 'exactly_one', collection: at('flags'), binding: 'b', where: {op: 'eq', left: at('b'), right: lit('Bool', true)}});
  rule('unique', [numbers], {op: 'unique', collection: at('numbers'), binding: 'n', where: {op: 'eq', left: at('n'), right: at('n')}});
  rule('forward', [numbers], {op: 'rule_ref', selector: 'alpha:large', arguments: [{parameter: 'numbers', value: at('numbers')}]});
  rule('legacy-compare', [{name: 'value', type: scalar('String')}], {op: 'lt', left: lit('String', '\u{10000}'), right: at('value')}, 'v1');
  for (const [id, type] of [['entity', {kind: 'named', selector: 'alpha:order'}], ['value', {kind: 'named', selector: 'alpha:money'}], ['sum', {kind: 'named', selector: 'alpha:answer'}]] as const)
    rule('equal-' + id, [{name: 'left', type}, {name: 'right', type}], {op: 'eq', left: at('left'), right: at('right')});
  const policy = (id: string, inputs: any[], cases: any[], default_target: string) => {
    node(id, 'Policy', {typed_contract: {schema_version: 'domainspec.typed-policy/v2', ontology_policy: 'FIXTURE-' + id.toUpperCase(), inputs, cases, default_target}});
    for (const target of new Set([...cases.map(c => c.target), default_target])) {
      const targetId = target.split(':')[1], edge_id = id + '-applies-' + targetId;
      feature.edges.push(edge_id);
      f.write('specs/alpha/edges/' + edge_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'alpha', edge_id, relationship: 'applies', source_node_id: id, target_node_id: targetId, scope: 'feature'});
    }
  };
  policy('ordered', [numbers, flags], [
    {target: 'alpha:post', rule: {selector: 'alpha:forward', arguments: [{parameter: 'numbers', value: at('numbers')}]}},
    {target: 'alpha:legacy-total', rule: {selector: 'alpha:one', arguments: [{parameter: 'flags', value: at('flags')}]}}
  ], 'alpha:total');
  policy('constant', [{name: 'value', type: scalar('Bool')}], [{target: 'alpha:post', rule: {selector: 'alpha:allowed', arguments: [{parameter: 'value', value: lit('Bool', true)}]}}], 'alpha:total');
  f.write('specs/alpha/feature.json', feature);
  const graph = loadCompiledProjectGraph(f.source);
  const plan = planCompiledReconciledPythonProject(graph, {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, layout_version: RESOLVED_ARTIFACT_LAYOUT, language: 'python', module_root: 'relocated/native', field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows});
  const controls = createPythonSemanticControls(graph, plan), context = getPythonDecisionVerificationContext(plan);
  assert.throws(() => getPythonDecisionVerificationContext(structuredClone(plan)), /registered/);
  assert.equal(canonicalJson(context).includes('"artifacts"'), false);
  const decisions = controls.rows.filter(r => ['Rule', 'Policy'].includes(r.kind));
  for (const row of decisions) {
    if (row.selector === 'alpha:constant') {
      assert.equal(row.state, 'not_evaluable'); assert.match((row as any).reason, /input-sensitivity/); continue;
    }
    assert.equal(row.state, 'ready', row.selector + ':' + (row as any).reason);
    if (row.state !== 'ready') throw new Error('ready decision required');
    const node = graph.nodes.find(n => n.selector === row.selector)!;
    const source = row.kind === 'Rule' ? createRuleSemanticCases(node, graph) : createPolicySemanticCases(node, graph);
    assert.deepEqual(row.cases, source.cases); assert.deepEqual(row.recipes, source.recipes);
  }
  const ordered = controls.rows.find(r => r.selector === 'alpha:ordered') as any;
  assert.deepEqual(ordered.source_predicted_targets, ['alpha:legacy-total', 'alpha:post', 'alpha:total']);
  assert.deepEqual(ordered.source_predicted_branches, [-1, 0, 1]);
  const before = fs.readdirSync(f.temp), report = execute(graph, plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks));
  assert.equal(report.result, 'not_evaluable');
  for (const row of decisions.filter(r => r.state === 'ready')) {
    const observed = report.semantic_rows!.find(r => r.selector === row.selector)!;
    assert.equal(observed.result, 'pass', JSON.stringify(report.checks));
    assert.equal(observed.binding_controls, row.kind === 'Rule' ? 0 : 3);
    assert.equal(observed.compiling_substitutions, 2);
  }
  assert.deepEqual(fs.readdirSync(f.temp), before);

  // A separate bounded probe makes target execution fail immediately, while
  // importing and invoking the generated Policy remains successful.
  const root = path.join(f.temp, 'poisoned-targets');
  for (const artifact of plan.artifacts) {
    const file = path.join(root, artifact.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, artifact.content);
  }
  const targets = plan.modules.filter(m => m.qualified_selectors.some(s => ['alpha:post', 'alpha:total', 'alpha:legacy-total'].includes(s)));
  for (const m of targets) fs.writeFileSync(path.join(root, m.relative_path), 'raise RuntimeError("STRATEGY_EXECUTED")\n');
  const m = context.policies.find(m => m.selector === 'alpha:ordered')!;
  const script = [
    'import importlib, json, pathlib, sys',
    'd=json.load(sys.stdin)',
    'sys.path.insert(0,d["root"])',
    'm=importlib.import_module(d["module"]["import_name"])',
    'call=getattr(m,d["module"]["callable"])',
    'assert call({"numbers":[101],"flags":[True]})=="alpha:post"',
    'assert call({"numbers":[1],"flags":[True]})=="alpha:legacy-total"',
    'assert call({"numbers":[1],"flags":[False]})=="alpha:total"',
    'assert all(p[:-3].replace("/",".") not in sys.modules for p in d["targets"])',
    'print("selection-only")'
  ].join('\n');
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', script], {input: JSON.stringify({root, module: m, targets: targets.map(m => m.relative_path)}), encoding: 'utf8', timeout: 30000});
  assert.equal(result.status, 0, result.stderr); assert.equal(result.stdout.trim(), 'selection-only');
  t.diagnostic(JSON.stringify({nodes: controls.rows.length, decisions: decisions.length, executed_decisions: decisions.filter(r => r.state === 'ready').length, cases: controls.case_count, control_bytes: Buffer.byteLength(canonicalJson(controls))}));
});
