import {CLI_VERSION} from '../../src/version.ts';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {pythonInterfaceFixture, scalar, local, wrap, publicField} from './reconciled-python-interface-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {getPythonInterfaceVerificationContext, planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {createPythonInterfaceControls} from '../../src/verification/reconciled-python-interface-controls.ts';
import {createPythonSemanticControls} from '../../src/verification/reconciled-python-semantic-controls.ts';
import {createInterfaceSemanticCases} from '../../src/verification/reconciled-interface-controls.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';

test('Python Interface replay detects value, key, identity, mutability, version and effect substitutions', t => {
  const f = pythonInterfaceFixture(t), {graph, plan} = selected(f), controls = createPythonSemanticControls(graph, plan);
  const root = path.join(f.temp, 'sensitivity');
  for (const a of plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const load = (name: string, source: string, bindings = '') => name + "={'__name__':'observer'" + bindings + '}\nexec(' + JSON.stringify(source) + ',' + name + ')\n';
  const program = 'import types\n' + load('observer_base', getReconciledSource('python_operation_observer'))
    + load('observer', getReconciledSource('python_interface_observer'), ", 'base':types.SimpleNamespace(**observer_base)")
    + load('owned', getReconciledSource('python_owned_semantics'))
    + load('facts', getReconciledSource('python_state_machine_semantics'), ", 'owned':types.SimpleNamespace(**owned)")
    + load('operations', getReconciledSource('python_operation_semantics'), ", 'owned':types.SimpleNamespace(**owned), 'facts':types.SimpleNamespace(**facts)")
    + load('runner', getReconciledSource('python_interface_semantics'), ", 'owned':types.SimpleNamespace(**owned), 'facts':types.SimpleNamespace(**facts), 'operations':types.SimpleNamespace(**operations)") + String.raw`
import dataclasses,importlib,json,sys
d=json.load(sys.stdin);sys.path.insert(0,d['root'])
def preceding(value):
    return {'rows':[{'selector':r['selector'],'kind':r['kind'],'result':'not_evaluable','executed':False} for r in value['controls']['rows']], 'toolchain_files':{}}
row=next(r for r in d['controls']['rows'] if r['kind']=='Interface')
module=importlib.import_module(row['module']['import_name'])
normal,key,version=module.BoundaryValue.normalize,module.BoundaryValue.key,module.accepts_consumer_version
# Full baseline and the same complete Interface cases for each substitution.
runner['run'](d,preceding,observer['observe'])
rejected=[]
for mutation in ('wrong-value','wrong-key','identity-collapse','mutable-value','wrong-version','unexpected-effect'):
    if mutation=='wrong-value':
        def wrong(self,value):
            result=normal(self,value)
            return result+1 if type(result) is int else result
        module.BoundaryValue.normalize=wrong
    elif mutation=='wrong-key': module.BoundaryValue.key=lambda self,value:'wrong-key'
    elif mutation=='identity-collapse':
        def collapsed(self,value):
            result=key(self,value)
            return result.replace('6:shadow','8:response')
        module.BoundaryValue.key=collapsed
    elif mutation=='mutable-value':
        def mutable(self,value):
            result=normal(self,value)
            return dict(result.entries) if dataclasses.is_dataclass(result) and hasattr(result,'entries') else result
        module.BoundaryValue.normalize=mutable
    elif mutation=='wrong-version': module.accepts_consumer_version=lambda value:True
    else:
        def effect(self,value):
            sys.audit('socket.__new__')
            return normal(self,value)
        module.BoundaryValue.normalize=effect
    try: runner['run'](d,preceding,observer['observe'])
    except ValueError as error:
        assert any(s in str(error) for s in ('outcome:','immutable public fact','effect or coercion','stable normalized key')),str(error)
        rejected.append(mutation)
    else: raise AssertionError('survived:'+mutation)
    finally:
        module.BoundaryValue.normalize=normal;module.BoundaryValue.key=key;module.accepts_consumer_version=version
# Public boundaries have no runtime dependency on their declared application member.
# Poison that member after the native module has been unloaded; Interface-only
# replay must still work, and a source-level import would fail whole-source observation.
member=next(r for r in d['controls']['rows'] if r['kind']=='Operation')['module']['import_name']
sys.modules[member]=None
importlib.reload(module)
runner['run'](d,preceding,observer['observe'])
print(json.dumps(rejected))
`;
  const launcher = "import io,json,sys\ne=json.load(sys.stdin)\nsys.stdin=io.StringIO(json.dumps(e['request']))\nexec(e['program'])\n";
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', launcher], {input: JSON.stringify({program, request: {root, controls}}), encoding: 'utf8', timeout: 30000, maxBuffer: 2 * 1024 * 1024});
  assert.equal(result.status, 0, result.stderr); assert.equal(JSON.parse(result.stdout).length, 6);
});

function selected(f: ReturnType<typeof pythonInterfaceFixture>) {
  const graph = loadCompiledProjectGraph(f.source), s = f.selection;
  const plan = planCompiledReconciledPythonProject(graph, {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python',
    module_root: s.module_root, layout_version: s.layout_version, field_bindings: s.field_bindings, factories: s.factories, operations: s.operations, workflows: []});
  return {graph, plan};
}
const variants = [
  {name: 'scalar', mode: 'backward', type: scalar('UInt64'), domain: false},
  {name: 'containers', mode: 'exact', type: {kind: 'sum', variants: [{name: 'None', ontology_variant: 'TEST-OPTION#None', payload: null}, {name: 'Some', ontology_variant: 'TEST-OPTION#Some', payload: wrap('list', local('detail'))}]}, domain: false},
  {name: 'domain', mode: 'backward', type: wrap('set', {kind: 'named', selector: 'alpha:choice'}), domain: true},
];
const compiler100Baselines = [{"name":"scalar","cases":283,"suite_sha256":"bc9913cdb6b40d32dab07fe8672ad13a41ffdfa4a000d344aa10d72f78e36afe","artifacts_sha256":"f66fc72d674dde7ce05c758c080705c53ac98ca0f36427b2816e9f9b7525c531"},{"name":"containers","cases":900,"suite_sha256":"021a4155511cd6ee8da44bc46185416275cbe081aa409a9a3b6c5cb7be635de6","artifacts_sha256":"26b9073334c0c68373d3e2b9a5ef9ef9f91a99902ed90fd6aafebcf72ee2c46c"},{"name":"domain","cases":1023,"suite_sha256":"858943b6cda8a916ea6b0600e96da7bd89c1ec1947baf43aae5ad0f82d46f521","artifacts_sha256":"ecf549c716574739e9f66e69e70855db3ab268d167c97b0a9ed99d4690e5be46"}];
// Compiler identity belongs to certificate/field/action hashes embedded in these
// artifacts and owned-value keys. Preserve the original 1.0 byte pins, and pin
// 1.3 explicitly after reproducing the old bytes with only historical compiler
// identity in an isolated diagnostic. Business cases and negative oracles below
// remain unchanged. This does not treat a diagnostic preload as current proof.
const compiler130Pins:Record<string,{artifacts_sha256:string;suite_sha256?:string}> = {"scalar":{"suite_sha256":"bc9913cdb6b40d32dab07fe8672ad13a41ffdfa4a000d344aa10d72f78e36afe","artifacts_sha256":"67d5c33f8472aaaa7599e45cf98aab075d1e14692d4e2b02a9f3e3c047882bb7"},"containers":{"suite_sha256":"021a4155511cd6ee8da44bc46185416275cbe081aa409a9a3b6c5cb7be635de6","artifacts_sha256":"7e8de715f407dfed2c0aed5b96419881cbfd7bfb85e7b7e5b0f449217b4ecc86"},"domain":{"suite_sha256":"6da4c0bd8695a9dd4bc361142947f546608dc998ce7a8bde6cd966d9e63b6c30","artifacts_sha256":"2ec6b5a6a8f1c1d917ac7c8815daa4b10a883a66b0f0aff78d457dde1458b702"}};
const baselineVersions:Record<string,typeof compiler100Baselines> = {
 '1.0.0':compiler100Baselines,
 '1.3.0':compiler100Baselines.map(row=>({...row,...compiler130Pins[row.name]})),
};
const baselines=baselineVersions[String(CLI_VERSION)];
assert.ok(baselines,'explicit compiler-specific artifact baseline required');
for (const [index, variant] of variants.entries()) test('Python Interface shared cases and native boundaries: ' + variant.name, t => {
  const f = pythonInterfaceFixture(t, variant.mode, variant.type, variant.domain), {graph, plan} = selected(f);
  const node = graph.nodes.find(n => n.kind === 'Interface')!, row = createPythonInterfaceControls(node, graph, plan);
  assert.equal(row.state, 'ready', (row as any).reason); if (row.state !== 'ready') return;
  assert.equal(row.cases.length, baselines[index].cases);
  assert.equal(sha256(canonicalJson({cases: row.cases, recipes: row.recipes})), baselines[index].suite_sha256);
  assert.equal(sha256(canonicalJson(plan.artifacts)), baselines[index].artifacts_sha256);
  assert.equal(canonicalJson(getPythonInterfaceVerificationContext(plan)).includes('"artifacts"'), false);
  assert.throws(() => getPythonInterfaceVerificationContext(structuredClone(plan)), /registered/);
  assert.throws(() => createPythonInterfaceControls(structuredClone(node), graph, plan), /registered Interface/);
  assert.throws(() => createInterfaceSemanticCases(node, structuredClone(graph), plan.field_compilation_sha256), /unvalidated/);
  const shared = createInterfaceSemanticCases(node, graph, plan.field_compilation_sha256);
  assert.equal(shared.state, 'ready'); if (shared.state === 'ready') assert.deepEqual(row.cases, shared.cases);
  const before = fs.readdirSync(f.temp), controls = createPythonSemanticControls(graph, plan);
  const report = execute(graph, plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  const actual = report.semantic_rows!.find(r => r.selector === node.selector);
  assert.deepEqual(actual, {selector: node.selector, kind: 'Interface', result: 'pass', executed: true, case_count: row.cases.length, native_form: 'pass', binding_controls: 3, compiling_substitutions: 2}, JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.residue, null); assert.equal(report.result, 'not_evaluable'); assert.deepEqual(fs.readdirSync(f.temp), before);
  // The domain's deliberately false factory invariant must not prevent its
  // public structural Interface normalization from passing.
  if (!variant.domain) assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, graph.nodes.length);
  t.diagnostic(JSON.stringify({name: variant.name, nodes: graph.nodes.length, interface_cases: row.cases.length, cases: controls.case_count, control_bytes: Buffer.byteLength(canonicalJson(controls))}));
});

test('Python Interface overflow retains every source node and no passing prefix', t => {
  const f = pythonInterfaceFixture(t);
  f.contract.contracts = Array.from({length: 128}, (_, i) => ({contract_id: 'value-' + i, ontology_contract: 'TEST-VALUE-' + i, fields: [publicField('amount', scalar('UInt64'))]}));
  f.contract.operations[0].result = local('value-0'); f.save();
  const {graph, plan} = selected(f), row = createPythonInterfaceControls(graph.nodes.find(n => n.kind === 'Interface')!, graph, plan);
  assert.equal(row.state, 'not_evaluable'); assert.equal('cases' in row, false);
  assert.match((row as any).reason, /bounded Interface/);
  assert.equal(plan.node_selectors.length, graph.nodes.length);
});

test('Python Interface optional, Bool, Unicode metadata and exact named boundaries preserve all cases', t => {
  const f = pythonInterfaceFixture(t, 'backward', wrap('optional', scalar('Bool')));
  f.contract.contracts.find((c: any) => c.contract_id === 'detail').fields[0].meaning = 'Public 😀 e\u0301 and lone surrogate \ud800';
  f.save();
  const {graph, plan} = selected(f), controls = createPythonSemanticControls(graph, plan);
  const report = execute(graph, plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, graph.nodes.length, JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  const row = controls.rows.find(r => r.kind === 'Interface') as any;
  assert.ok(row.cases.some((c: any) => c.mode === 'interface-value' && c.expected.kind === 'value' && c.expected.value.includes('boolean')));
  assert.ok(row.cases.some((c: any) => c.mode === 'interface-value' && c.expected.kind === 'value' && c.expected.value.includes('null')));
});
