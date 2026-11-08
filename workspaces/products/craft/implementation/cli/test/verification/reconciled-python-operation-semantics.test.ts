import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {operationFixture, valueOperationFixture} from '../helpers/cross-generator-operation.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {getPythonOperationVerificationContext, planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {createPythonSemanticControls} from '../../src/verification/reconciled-python-semantic-controls.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';

function plan(f: {source: string; selection: any}) {
  const graph = loadCompiledProjectGraph(f.source), selected = planCompiledReconciledPythonProject(graph, {
    schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python',
    module_root: 'relocated/operation-app', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: f.selection.field_bindings,
    factories: f.selection.factories, operations: f.selection.operations, workflows: []});
  return {graph, plan: selected};
}

test('Python Operations retain complete effectful source cases and execute ordered reads, writes, events and deferred failures', t => {
  const f = operationFixture(t), selected = plan(f), controls = createPythonSemanticControls(selected.graph, selected.plan);
  const row = controls.rows.find(r => r.kind === 'Operation') as any;
  assert.equal(row.state, 'ready', row.reason);
  assert.throws(() => getPythonOperationVerificationContext(structuredClone(selected.plan)), /registered/);
  assert.equal(canonicalJson(getPythonOperationVerificationContext(selected.plan)).includes('"artifacts"'), false);
  // Preserve the existing complete source digest, apart from the explicit native
  // receipt-code transport. This avoids rebuilding a TypeScript project here.
  const original = row.cases.filter((c: any) => c.mode === 'operation').map((source: any) => {
    const c = structuredClone(source), fixture = JSON.parse(c.values[0]), expected = JSON.parse(c.expected.value);
    const code = expected.outcome[1].find((f: any) => f[0] === 'code'), stage = expected.outcome[1].find((f: any) => f[0] === 'stage');
    if (fixture.mode.startsWith('receipt-') && !['receipt-empty', 'receipt-unknown'].includes(fixture.mode) && stage?.[1][1] === 'commit' && code?.[1][1] === 'INVALID_COMMIT_RECEIPT') code[1][1] = 'COMMIT_UNCERTAIN';
    c.expected.value = canonicalJson(expected); return c;
  });
  assert.equal(original.length, 1903);
  assert.equal(sha256(canonicalJson({recipes: row.recipes, cases: original})), 'a0be2819f1eaa590dbf56d0840f7d6c383d474c1ff46bcbf28af426dffdd2d49');
  assert.deepEqual(row.cases.filter((c: any) => c.mode === 'operation-native-cancel').map((c: any) => c.id), ['native-cancel-begin', 'native-cancel-read', 'native-cancel-commit', 'native-cancel-rollback']);
  const before = fs.readdirSync(f.temp), report = execute(selected.graph, selected.plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.result, 'not_evaluable'); assert.equal(report.residue, null);
  assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, 9, JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.deepEqual(report.semantic_rows!.find(r => r.kind === 'Operation'), {selector: row.selector, kind: 'Operation', result: 'pass', executed: true,
    case_count: row.cases.length, native_form: 'pass', binding_controls: 3, compiling_substitutions: 2});
  assert.deepEqual(fs.readdirSync(f.temp), before);

  const root = path.join(f.temp, 'sensitivity');
  for (const a of selected.plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const load = (name: string, source: string, bindings = '') => name + "={'__name__':'observer'" + bindings + '}\nexec(' + JSON.stringify(source) + ',' + name + ')\n';
  const program = 'import types\n' + load('observer', getReconciledSource('python_operation_observer'))
    + load('event_observer', getReconciledSource('python_event_observer')) + load('owned', getReconciledSource('python_owned_semantics'))
    + load('facts', getReconciledSource('python_state_machine_semantics'), ", 'owned':types.SimpleNamespace(**owned)")
    + load('runner', getReconciledSource('python_operation_semantics'), ", 'owned':types.SimpleNamespace(**owned), 'facts':types.SimpleNamespace(**facts)") + String.raw`
import asyncio,copy,dataclasses,importlib,json,sys
d=json.load(sys.stdin);sys.path.insert(0,d['root'])
def preceding(value):
    return {'rows':[{'selector':r['selector'],'kind':r['kind'],'result':'not_evaluable','executed':False} for r in value['controls']['rows']], 'toolchain_files':{}}
row=next(r for r in d['controls']['rows'] if r['kind']=='Operation')
# The full public verifier above ran every source case. Mutation sensitivity
# uses one already-verified case per outcome/mode/capture boundary.
seen=set();selected=[]
for c in row['cases']:
    if c['mode']=='operation-descriptor': selected.append(c);continue
    value=json.loads(c['expected']['value']);outcome=dict(value['outcome'][1]);fixture=json.loads(c['values'][0])
    key=json.dumps([outcome.get('status'),outcome.get('stage'),outcome.get('code'),fixture['mode'],fixture['capture'],fixture.get('cancel')],sort_keys=True)
    if key not in seen: seen.add(key);selected.append(c)
row['cases']=selected
module=importlib.import_module(row['module']['import_name']);original=module._execute
provider=importlib.import_module(row['module']['provider_path'][:-3].replace('/','.'))
owners={k:v for k,v in vars(provider).items() if k.startswith('_own') and callable(v)}
rejected=[]
for mutation in ('wrong-result','skip-factory','write-order','event-order','duplicate-commit','late-capture','false-settlement'):
    changed=copy.deepcopy(d)
    if mutation=='wrong-result':
        async def wrong(p,dep):
            result=await original(p,dep)
            return dataclasses.replace(result,value='wrong-result') if result.status=='committed' else result
        module._execute=wrong
    elif mutation=='skip-factory':
        for k in owners: setattr(provider,k,lambda value:None)
    elif mutation in ('write-order','event-order','duplicate-commit'):
        class Tx:
            def __init__(self,t): self.t=t
            async def read(self,r): return await self.t.read(r)
            async def rollback(self): return await self.t.rollback()
            async def commit(self,b):
                if mutation=='write-order': b=dataclasses.replace(b,writes=tuple(reversed(b.writes)))
                if mutation=='event-order': b=dataclasses.replace(b,events=tuple(reversed(b.events)))
                receipt=await self.t.commit(b)
                if mutation=='duplicate-commit': await self.t.commit(b)
                return receipt
        async def wrapped(p,dep):
            class Store:
                async def begin(self): return Tx(await dep['store'].begin())
            return await original(p,{**dep,'store':Store()})
        module._execute=wrapped
    elif mutation=='late-capture':
        async def late(p,dep): await asyncio.sleep(0);return await original(p,dep)
        module._execute=late
    else:
        target=next(r for r in changed['controls']['rows'] if r['kind']=='Operation')
        c=next(c for c in target['cases'] if c['mode']=='operation')
        value=json.loads(c['expected']['value']);value['settled_before_commit']=True;c['expected']['value']=json.dumps(value)
    try: runner['run'](changed,preceding,observer['observe'],event_observer['observe'])
    except ValueError as error:
        assert 'outcome:' in str(error),str(error);rejected.append(mutation)
    else: raise AssertionError('survived:'+mutation)
    finally:
        module._execute=original
        for k,v in owners.items(): setattr(provider,k,v)
print(json.dumps(rejected))
`;
  const launcher = "import io,json,sys\ne=json.load(sys.stdin)\nsys.stdin=io.StringIO(json.dumps(e['request']))\nexec(e['program'])\n";
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', launcher], {input: JSON.stringify({program, request: {root, controls}}), encoding: 'utf8', timeout: 30000, maxBuffer: 2 * 1024 * 1024});
  assert.equal(result.status, 0, result.stderr); assert.equal(JSON.parse(result.stdout).length, 7);
  t.diagnostic(JSON.stringify({nodes: controls.rows.length, executed: 9, cases: controls.case_count, operation_cases: row.cases.length, control_bytes: Buffer.byteLength(canonicalJson(controls))}));
});

test('Python Operations support actual Enum-only results without inventing a record or factory', t => {
  const f = valueOperationFixture(t), selected = plan(f), controls = createPythonSemanticControls(selected.graph, selected.plan);
  assert.equal(selected.plan.selection.factories.length, 0);
  const report = execute(selected.graph, selected.plan, {python_executable: '/usr/bin/python3', temporary_parent: f.root});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, 4, JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.result, 'not_evaluable');
  t.diagnostic(JSON.stringify({nodes: controls.rows.length, cases: controls.case_count, controls_bytes: Buffer.byteLength(canonicalJson(controls))}));
});

test('Python Operation capacity leaves a whole pending row with no passing prefix', t => {
  const f = valueOperationFixture(t);
  f.selection.operations[0].inputs.push(...Array.from({length: 126}, (_, i) => ({name: 'unused_' + i, type: {kind: 'scalar', name: 'UInt64'}})));
  const selected = plan(f), controls = createPythonSemanticControls(selected.graph, selected.plan), row = controls.rows.find(r => r.kind === 'Operation')!;
  assert.equal(row.state, 'not_evaluable'); assert.equal('cases' in row, false);
  assert.match((row as any).reason, /bounded Operation/);
  assert.equal(controls.rows.length, selected.graph.nodes.length);
});
