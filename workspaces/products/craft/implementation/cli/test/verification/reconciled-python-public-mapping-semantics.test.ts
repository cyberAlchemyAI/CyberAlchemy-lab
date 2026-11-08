import {CLI_VERSION} from '../../src/version.ts';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {pythonPublicMappingFixture} from './reconciled-python-public-mapping-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {getPythonPublicMappingVerificationContext, planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {createMappingSemanticCases} from '../../src/verification/reconciled-mapping-controls.ts';
import {createPythonPublicMappingControls} from '../../src/verification/reconciled-python-public-mapping-controls.ts';
import {createPythonSemanticControls} from '../../src/verification/reconciled-python-semantic-controls.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';

test('Python public Mapping detects altered totals, field order, nullish fallback, collections, input checks and effects', t => {
  const f = pythonPublicMappingFixture(t, 'collections'), {graph, plan} = selected(f), controls = createPythonSemanticControls(graph, plan);
  const root = path.join(f.temp, 'sensitivity');
  for (const a of plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const load = (name: string, source: string, bindings = '') => name + "={'__name__':'observer'" + bindings + '}\nexec(' + JSON.stringify(source) + ',' + name + ')\n';
  const program = 'import types\n' + load('base', getReconciledSource('python_operation_observer'))
    + load('api', getReconciledSource('python_interface_observer'), ", 'base':types.SimpleNamespace(**base)")
    + load('observer', getReconciledSource('python_public_mapping_observer'), ", 'api':types.SimpleNamespace(**api)")
    + load('owned', getReconciledSource('python_owned_semantics'))
    + load('facts', getReconciledSource('python_state_machine_semantics'), ", 'owned':types.SimpleNamespace(**owned)")
    + load('operations', getReconciledSource('python_operation_semantics'), ", 'owned':types.SimpleNamespace(**owned), 'facts':types.SimpleNamespace(**facts)")
    + load('runner', getReconciledSource('python_public_mapping_semantics'), ", 'owned':types.SimpleNamespace(**owned), 'facts':types.SimpleNamespace(**facts), 'operations':types.SimpleNamespace(**operations), 'interface':types.SimpleNamespace(**api)") + String.raw`
import dataclasses,importlib,json,sys
d=json.load(sys.stdin);sys.path.insert(0,d['root'])
def preceding(value):
    return {'rows':[{'selector':r['selector'],'kind':r['kind'],'result':'not_evaluable','executed':False} for r in value['controls']['rows']], 'toolchain_files':{}}
row=next(r for r in d['controls']['rows'] if r['selector']=='alpha:map-full')
module=importlib.import_module(row['module']['import_name']);original=module._map_values
runner['run'](d,preceding,observer['observe'])
rejected=[]
for mutation in ('wrong-total','field-order','false-fallback','list-order','mutable-output','input-extra','unexpected-effect'):
    def altered(parameters):
        if mutation=='input-extra' and type(parameters) is dict:
            parameters={k:v for k,v in parameters.items() if k in ('response','memo','fallback','order_total')}
        result=original(parameters)
        if mutation=='unexpected-effect': sys.audit('socket.__new__')
        if mutation=='mutable-output': return dict(result.entries)
        if mutation=='field-order': return dataclasses.replace(result,entries=tuple(reversed(result.entries)))
        changed=[]
        for key,value in result.entries:
            if mutation=='wrong-total' and key=='explicit_total': value+=1
            if mutation=='false-fallback' and key=='memo' and parameters['memo']=='': value=parameters['fallback']
            if mutation=='list-order' and key=='value': value=tuple(reversed(value))
            changed.append((key,value))
        return dataclasses.replace(result,entries=tuple(changed))
    module._map_values=altered
    try: runner['run'](d,preceding,observer['observe'])
    except ValueError as error:
        assert any(s in str(error) for s in ('outcome:','frozen projection fact','effect or coercion')),str(error)
        rejected.append(mutation)
    else: raise AssertionError('survived:'+mutation)
    finally: module._map_values=original
print(json.dumps(rejected))
`;
  const launcher = "import io,json,sys\ne=json.load(sys.stdin)\nsys.stdin=io.StringIO(json.dumps(e['request']))\nexec(e['program'])\n";
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', launcher], {input: JSON.stringify({program, request: {root, controls}}), encoding: 'utf8', timeout: 30000, maxBuffer: 2 * 1024 * 1024});
  assert.equal(result.status, 0, result.stderr); assert.equal(JSON.parse(result.stdout).length, 7);
});

test('public Mapping independently observes a direct Interface whose semantic budget is pending', t => {
  const f = pythonPublicMappingFixture(t), file = path.join(f.source, 'specs/alpha/nodes/api.json');
  const api = JSON.parse(fs.readFileSync(file, 'utf8'));
  while (api.body.typed_contract.contracts.length < 128) {
    const i = api.body.typed_contract.contracts.length;
    api.body.typed_contract.contracts.push({contract_id: 'unused-' + i, ontology_contract: 'TEST-UNUSED-' + i, fields: [{name: 'amount', type: {kind: 'scalar', name: 'UInt64'}, meaning: 'amount', ontology_field: 'TEST-UNUSED#amount'}]});
  }
  fs.writeFileSync(file, JSON.stringify(api));
  const {graph, plan} = selected(f), controls = createPythonSemanticControls(graph, plan);
  const boundary = controls.rows.find(r => r.kind === 'Interface')!;
  assert.equal(boundary.state, 'not_evaluable'); assert.equal('cases' in boundary, false);
  const report = execute(graph, plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.semantic_rows!.filter(r => r.kind === 'Mapping' && r.result === 'pass').length, 3, JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.semantic_rows!.find(r => r.kind === 'Interface')!.executed, false);
});

test('public Mapping keeps cross-Interface endpoint uses and qualified imports separate', t => {
  const f = pythonPublicMappingFixture(t);
  const foreign = structuredClone(f.contracts.full); foreign.ontology_mapping = 'TEST-FOREIGN-MAPPING';
  foreign.inputs[0].type.interface_selector = 'alpha:foreign-api'; foreign.inputs[0].use.interface_selector = 'alpha:foreign-api';
  f.contracts.foreign = foreign; f.save();
  const api = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/nodes/api.json'), 'utf8'));
  api.node_id = 'foreign-api'; api.body.typed_contract.ontology_interface = 'TEST-FOREIGN-API';
  api.body.typed_contract.operations[0].operation_ref = 'alpha:foreign-perform';
  fs.writeFileSync(path.join(f.source, 'specs/alpha/nodes/foreign-api.json'), JSON.stringify(api));
  const operation = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/nodes/perform.json'), 'utf8'));
  operation.node_id = 'foreign-perform';
  fs.writeFileSync(path.join(f.source, 'specs/alpha/nodes/foreign-perform.json'), JSON.stringify(operation));
  f.selection.operations.push({...structuredClone(f.selection.operations[0]), selector: 'alpha:foreign-perform'});
  const feature = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/feature.json'), 'utf8'));
  feature.nodes.push('foreign-api', 'foreign-perform'); feature.edges.push('foreign-api-exposes-perform', 'allowed-enforces-foreign-perform');
  fs.writeFileSync(path.join(f.source, 'specs/alpha/edges/foreign-api-exposes-perform.json'), JSON.stringify({schema_version: 'domainspec.edge/v1', feature_id: 'alpha', edge_id: 'foreign-api-exposes-perform', relationship: 'exposes', source_node_id: 'foreign-api', target_node_id: 'foreign-perform', scope: 'feature'}));
  fs.writeFileSync(path.join(f.source, 'specs/alpha/edges/allowed-enforces-foreign-perform.json'), JSON.stringify({schema_version: 'domainspec.edge/v1', feature_id: 'alpha', edge_id: 'allowed-enforces-foreign-perform', relationship: 'enforces', source_node_id: 'allowed', target_node_id: 'foreign-perform', scope: 'feature'}));
  fs.writeFileSync(path.join(f.source, 'specs/alpha/feature.json'), JSON.stringify(feature));
  const {graph, plan} = selected(f), controls = createPythonSemanticControls(graph, plan);
  const row = controls.rows.find(r => r.selector === 'alpha:map-foreign') as any;
  assert.deepEqual(row.interfaces.map((i: any) => i.selector), ['alpha:api', 'alpha:foreign-api']);
  assert.equal(row.mapping.contract.inputs[0].use.interface_selector, 'alpha:foreign-api');
  const report = execute(graph, plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, graph.nodes.length, JSON.stringify(report.checks.filter(c => c.result === 'fail')));
});

function selected(f: ReturnType<typeof pythonPublicMappingFixture>) {
  const graph = loadCompiledProjectGraph(f.source), s = f.selection;
  const plan = planCompiledReconciledPythonProject(graph, {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python',
    module_root: s.module_root, layout_version: s.layout_version, field_bindings: s.field_bindings, factories: s.factories, operations: s.operations, workflows: []});
  return {graph, plan};
}
const compiler100Baselines = [{"variant":"scalar","rows":[{"selector":"alpha:map-empty","cases":12,"sha256":"be69defccbd63d747bfc7494ca9a7e43d41712cda8a34cfc58720c3ed2900c38"},{"selector":"alpha:map-full","cases":204,"sha256":"dc7c55f02c05fb0f4bd54e47910d1f92f1a5204dbe574a4c35d06311324eb579"},{"selector":"alpha:map-partial","cases":204,"sha256":"71e28c042cd877ccba197ff81fba6648059dd41270cc80745dc31f0ca24f5b51"}],"artifacts_sha256":"a46ea5a3434059ed105aaffe804874e7e1cb705954e6ead1dea52e3eaa70c2ef"},{"variant":"collections","rows":[{"selector":"alpha:map-empty","cases":12,"sha256":"be69defccbd63d747bfc7494ca9a7e43d41712cda8a34cfc58720c3ed2900c38"},{"selector":"alpha:map-full","cases":474,"sha256":"ef087eec20235fb2272d4b5eaed027978b94c125f9b5aa345184befad719ae2b"},{"selector":"alpha:map-partial","cases":474,"sha256":"aa8f6d3aa8dd0d1188a63dc183479c93a8c102573a4a5288df172ead660d5e3b"}],"artifacts_sha256":"5d00fc83ea3b79e43c8bac21fc5c16412248e28db87768d256fb409cafa85826"},{"variant":"domain","rows":[{"selector":"alpha:map-domain","cases":52,"sha256":"d3dd8748408880ae815a54ec2b872a953d45874ae2d6590c992849c209aa611b"},{"selector":"alpha:map-empty","cases":12,"sha256":"be69defccbd63d747bfc7494ca9a7e43d41712cda8a34cfc58720c3ed2900c38"},{"selector":"alpha:map-full","cases":242,"sha256":"e05a837f735571cc0a1d058ded05a9081413c0b80619d696ec9ba3ce9a0ec2db"},{"selector":"alpha:map-partial","cases":242,"sha256":"8a24db2d859c732e90666e56054f8b93775a2638661fb72ae2e32c9aabd62422"}],"artifacts_sha256":"3461395a76c6b10b8298e2894541fc3977dfb8d403cc383df8a20b90514618cc"}];
// Compiler identity belongs to certificate/field/action hashes embedded in these
// artifacts and owned-value keys. Preserve the original 1.0 byte pins, and pin
// 1.3 explicitly after reproducing the old bytes with only historical compiler
// identity in an isolated diagnostic. Business cases and negative oracles below
// remain unchanged. This does not treat a diagnostic preload as current proof.
const compiler130Pins:Record<string,{artifacts_sha256:string;suite_sha256?:string}> = {"scalar":{"artifacts_sha256":"bbfe2a153b3bb7033cc295d58418c7305fbf70febd4cfe34617f12f3b8fc9e77"},"collections":{"artifacts_sha256":"caf892a7234dc4cdadd1e9789e6d0db8ba19126bb498fe365abb88f9726a0c33"},"domain":{"artifacts_sha256":"e385aeb14a49e770e9195019beafb97f03e1428e0ad3797d699656c7c31f5285"}};
const baselineVersions:Record<string,typeof compiler100Baselines> = {
 '1.0.0':compiler100Baselines,
 '1.3.0':compiler100Baselines.map(row=>({...row,...compiler130Pins[row.variant]})),
};
const baselines=baselineVersions[String(CLI_VERSION)];
assert.ok(baselines,'explicit compiler-specific artifact baseline required');
for (const baseline of baselines) test('Python public Mapping preserves complete source cases and native projection: ' + baseline.variant, t => {
  const f = pythonPublicMappingFixture(t, baseline.variant), {graph, plan} = selected(f);
  assert.equal(sha256(canonicalJson(plan.artifacts)), baseline.artifacts_sha256);
  assert.equal(canonicalJson(getPythonPublicMappingVerificationContext(plan)).includes('"artifacts"'), false);
  assert.throws(() => getPythonPublicMappingVerificationContext(structuredClone(plan)), /registered/);
  for (const source of baseline.rows) {
    const node = graph.nodes.find(n => n.selector === source.selector)!, shared = createMappingSemanticCases(node, graph), row = createPythonPublicMappingControls(node, graph, plan);
    assert.equal(sha256(canonicalJson({cases: shared.cases, recipes: shared.recipes})), source.sha256);
    assert.equal(shared.cases.length, source.cases);
    assert.equal(row.state, 'ready', (row as any).reason); if (row.state !== 'ready') continue;
    assert.deepEqual(row.recipes, shared.recipes);
    assert.deepEqual(row.cases.slice(1), shared.cases.map(c => c.expected.kind === 'error' ? {...c, expected: {kind: 'error', name: 'TypeError', message: 'MAPPING_INPUT'}} : c));
    assert.equal(row.cases.length, source.cases + 1);
    assert.throws(() => createPythonPublicMappingControls(structuredClone(node), graph, plan), /registered source/);
  }
  const controls = createPythonSemanticControls(graph, plan), before = fs.readdirSync(f.temp);
  const report = execute(graph, plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  for (const source of baseline.rows) assert.deepEqual(report.semantic_rows!.find(r => r.selector === source.selector), {selector: source.selector, kind: 'Mapping', result: 'pass', executed: true,
    case_count: source.cases + 1, native_form: 'pass', binding_controls: 3, compiling_substitutions: 2}, JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.residue, null); assert.equal(report.result, 'not_evaluable'); assert.deepEqual(fs.readdirSync(f.temp), before);
  if (baseline.variant !== 'domain') assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, graph.nodes.length);
  t.diagnostic(JSON.stringify({variant: baseline.variant, nodes: graph.nodes.length, mapping_cases: baseline.rows.reduce((n, r) => n + r.cases + 1, 0), cases: controls.case_count, control_bytes: Buffer.byteLength(canonicalJson(controls))}));
});

test('Python public Mapping case capacity retains whole rows instead of passing a prefix', t => {
  const f = pythonPublicMappingFixture(t);
  f.contracts.full.inputs.push(...Array.from({length: 124}, (_, i) => ({name: 'unused_' + i, type: {kind: 'scalar', name: 'UInt64'}, use: null})));
  f.save();
  const {graph, plan} = selected(f), node = graph.nodes.find(n => n.selector === 'alpha:map-full')!, row = createPythonPublicMappingControls(node, graph, plan);
  assert.equal(row.state, 'not_evaluable'); assert.equal('cases' in row, false); assert.match((row as any).reason, /bounded Mapping/);
  assert.equal(plan.node_selectors.length, graph.nodes.length);
});
