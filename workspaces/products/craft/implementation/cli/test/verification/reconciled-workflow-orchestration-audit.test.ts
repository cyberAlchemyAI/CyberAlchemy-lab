import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {workflowFixture, workflowProject, stepIds} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture, named} from '../helpers/workflow-values.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {createWorkflowOrchestrationAudit, WORKFLOW_ORCHESTRATION_AUDIT_RUNNER, WORKFLOW_ORCHESTRATION_DEFINITION_SHA256} from '../../src/verification/reconciled-workflow-orchestration-audit.ts';
import {createWorkflowCases, isWorkflowCasesCapacity} from '../../src/verification/reconciled-workflow-cases.ts';

const base = path.join(workflowProject, 'development/reconciliation-v1/profile-compiler-reconciliation');
const definition = fs.readFileSync(path.join(base, 'semantic-workflow-orchestration-contract.json'), 'utf8');
const bindingDefinition = fs.readFileSync(path.join(base, 'semantic-workflow-binding-contract.json'), 'utf8');
const definitions = {binding: bindingDefinition, outcomes: fs.readFileSync(path.join(base, 'semantic-workflow-controls-contract.json'), 'utf8'), orchestration: definition};
function selected(f: ReturnType<typeof workflowFixture>) {
  const plan = planCompiledReconciledProject(f.graph, f.selection);
  return {plan, profile: createWorkflowOrchestrationAudit(f.graph, plan, definitions)};
}
function fixture(f: ReturnType<typeof workflowFixture>) {
  const {plan, profile} = selected(f), root = fs.mkdtempSync(path.join(f.root, 'orchestration-audit-'));
  for (const a of plan.resolved.artifacts) {const p = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(p), {recursive: true}); fs.writeFileSync(p, a.content);}
  const require = createRequire(import.meta.url), typeFile = require.resolve('@types/node/package.json', {paths: [path.join(workflowProject, 'impl'), ...process.execArgv.filter(p => p.endsWith('loader.mjs')).map(p => path.dirname(p))]}), deps = path.dirname(path.dirname(path.dirname(typeFile)));
  fs.writeFileSync(path.join(root, 'package.json'), '{"type":"module"}');
  const sourceConfig = path.join(root, 'tsconfig.source.json'), nativeConfig = path.join(root, 'tsconfig.native.json');
  fs.writeFileSync(sourceConfig, JSON.stringify({compilerOptions: {strict: true, skipLibCheck: true, target: 'ES2022', module: 'NodeNext', moduleResolution: 'NodeNext', types: ['node'], typeRoots: [path.join(deps, '@types')], rootDir: root, outDir: path.join(root, 'js')}, files: plan.resolved.artifacts.map(a => path.join(root, a.relative_path))}));
  fs.writeFileSync(nativeConfig, JSON.stringify({compilerOptions: {allowJs: true, checkJs: false, noEmit: true, target: 'ES2022', module: 'NodeNext', moduleResolution: 'NodeNext', types: []}, files: profile.module_paths.map(p => path.join(root, 'js', p.replace(/\.ts$/, '.js')))}));
  const chain = JSON.parse(fs.readFileSync(path.resolve(workflowProject, '../../toolchains/node-typescript/toolchain.json'), 'utf8'));
  const image = nativeToolchainImage(chain.container_image);
  assert.equal(image, NATIVE_TEST_IMAGE_ID);
  const docker = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(), '--mount', 'type=bind,source=' + root + ',target=' + root, '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly', '--workdir', root, image];
  const command = (args: string[]) => {
    try {return execFileSync('docker', [...docker, ...args], {encoding: 'utf8', stdio: 'pipe'});} catch (e) {const error = e as any; throw new Error([error.message, error.stdout, error.stderr].filter(Boolean).join('\n'));}
  };
  const compile = () => command(['tsc', '-p', sourceConfig, '--pretty', 'false']);
  const script = path.join(root, 'workflow-orchestration.mjs'); fs.writeFileSync(script, WORKFLOW_ORCHESTRATION_AUDIT_RUNNER);
  const input = (phase: 'source' | 'native'): any => ({phase, definition, module_root: phase === 'source' ? root : path.join(root, 'js'), module_paths: profile.module_paths.map(p => p.replace(/\.ts$/, phase === 'native' ? '.js' : '.ts')), workflow_modules: structuredClone(profile.workflow_modules)});
  const audit = (phase: 'source' | 'native', change?: (input: any) => void) => {
    const row = input(phase); change?.(row); const p = path.join(root, 'audit-' + phase + '.json'); fs.writeFileSync(p, JSON.stringify(row));
    return JSON.parse(command(['node', script, '/opt/node-toolchain/node_modules/typescript', phase === 'source' ? sourceConfig : nativeConfig, p]));
  };
  const freshProviderHashes = (row: any) => {row.workflow_modules = row.workflow_modules.map((m: any) => ({...m, source_sha256: sha256(fs.readFileSync(path.join(root, m.relative_path), 'utf8'))}));};
  return {root, plan, profile, input, audit, compile, freshProviderHashes};
}
const violations = (o: any) => o.modules.flatMap((m: any) => m.violations.map((v: any) => ({...v, module: m.relative_path})));


test('strict-compiling execution mutations cannot pass by retaining expected-looking fragments', t => {
  const c = fixture(workflowFixture(t)), p = path.join(c.root, c.profile.module_paths[0]!), original = fs.readFileSync(p, 'utf8');
  const changes: [string, (s: string) => string][] = [
    ['reordered source occurrence blocks', s => {const blocks = s.match(/ \{\n  let args:[\s\S]*?\n \}\n/g)!; assert.equal(blocks.length, 4); return s.replace(blocks[0]! + blocks[1]!, blocks[1]! + blocks[0]!);}],
    ['wrong argument occurrence', s => s.replace('args=material.steps["first"]', 'args=material.steps["second"]')],
    ['wrong argument result scope', s => s.replace('.arguments(input,results);', '.arguments(input,results.slice(0,0));')],
    ['missing await', s => s.replace('raw=await call0(args,dep0)', 'raw=call0(args,dep0)')],
    ['unreachable correct call', s => s.replace('raw=await call0(args,dep0)', 'if(false){raw=await call0(args,dep0);}raw=null')],
    ['optional call', s => s.replace('await call0(args,dep0)', 'await call0?.(args,dep0)')],
    ['extra call', s => s.replace('raw=await call0(args,dep0);', 'raw=await call0(args,dep0);raw=await call0(args,dep0);')],
    ['copied arguments', s => s.replace('call0(args,dep0)', 'call0({...args},dep0)')],
    ['mutable captured call', s => s.replace('const call0=', 'let call0=')],
    ['wrong dependency scope', s => s.replace('call0(args,dep0)', 'call0(args,{...dep0})')],
    ['wrong returned occurrence', s => s.replace('observe(0,settlement)', 'observe(1,settlement)')],
    ['unknown changed to not-started', s => s.replace('observe(0,unknown("threw"))', 'observe(0,notStarted())')],
    ['wrong continuation', s => s.replace('inspectOperationSettlement(raw,"return-perform-error")', 'inspectOperationSettlement(raw,"return-undo-error")')],
    ['disabled terminal stop', s => s.replace('if(settlement.commit_status!=="committed")', 'if(false && settlement.commit_status!=="committed")')],
    ['wrong result occurrence', s => s.replace('captureResult(input,"first"', 'captureResult(input,"second"')],
    ['wrong result value', s => s.replace('Object.getOwnPropertyDescriptor(raw,"value")!.value', '0n')],
    ['result capture before terminal stop', s => s.replace('  if(settlement.commit_status!=="committed")return stopped(input,results,observations,ids);\n  try{results.push(material.captureResult(input,"first",Object.getOwnPropertyDescriptor(raw,"value")!.value));}catch{return stopped(input,results,observations,ids,"committed-result-invalid");}',
      '  try{results.push(material.captureResult(input,"first",Object.getOwnPropertyDescriptor(raw,"value")!.value));}catch{return stopped(input,results,observations,ids,"committed-result-invalid");}\n  if(settlement.commit_status!=="committed")return stopped(input,results,observations,ids);')],
    ['early final materialization', s => s.replace(' let value:ReturnType<typeof material.result>;', ' material.result(input,results);\n let value:ReturnType<typeof material.result>;')],
    ['wrong final result scope', s => s.replace('value=material.result(input,results)', 'value=material.result(input,results.slice(0,0))')],
    ['early successful result', s => s.replace('export const execute=async(', 'export const execute=async(').replace(' const results:material.CapturedResult[]=[];', ' if(false)return null as never;\n const results:material.CapturedResult[]=[];')],
    ['parameter default', s => s.replace('parameters:WorkflowInput,', 'parameters:WorkflowInput={} as WorkflowInput,')],
    ['action pin drift', s => s.replace(c.profile.workflow_modules[0]!.expected.imports[0]!.action_sha256 + '","', '0'.repeat(64) + '","')]
  ];
  for (const [name, mutate] of changes) {
    const next = mutate(original); assert.notEqual(next, original, name); fs.writeFileSync(p, next); c.compile();
    for (const phase of ['source', 'native'] as const) assert.ok(violations(c.audit(phase, c.freshProviderHashes)).some((v: any) => v.code === 'execute-protocol'), phase + ':' + name);
  }
  t.diagnostic(JSON.stringify({strict_compiling_mutations: changes.length, phase_rejections: changes.length * 2}));
});

test('recovery metadata and typed preparation mutations are checked independently in both phases', t => {
  const c = fixture(workflowFixture(t)), p = path.join(c.root, c.profile.module_paths[0]!), original = fs.readFileSync(p, 'utf8');
  const e = c.profile.workflow_modules[0]!.expected;
  const changes: [string, (s: string) => string, string][] = [
    ['selected policy', s => s.replace('const policyHash="' + e.policy_sha256 + '"', 'const policyHash="' + '0'.repeat(64) + '"'), 'metadata-protocol'],
    ['prefix order', s => s.replace('["for_step"]:"third"', '["for_step"]:"first"'), 'metadata-protocol'],
    ['prefix graph edge', s => s.replace('["depends_on"]:Object.freeze([])', '["depends_on"]:Object.freeze(["undo-first"])'), 'metadata-protocol'],
    ['prefix digest', s => s.replace('["plan_digest"]:"', '["plan_digest"]:"0'), 'metadata-protocol'],
    ['include uncommitted steps', s => s.replace("observations.filter(r=>r.settlement.commit_status==='committed')", 'observations.filter(r=>true)'), 'recovery-boundaries'],
    ['disable uncertainty stop', s => s.replace("if(failed.settlement.commit_status==='indeterminate')", "if(false && failed.settlement.commit_status==='indeterminate')"), 'recovery-boundaries'],
    ['wrong prefix template', s => s.replace('prefixTemplates[completed.length]', 'prefixTemplates[0]'), 'recovery-boundaries'],
    ['wrong compensation materializer', s => s.replace('material.compensations["undo-first"].arguments', 'material.compensations["undo-second"].arguments'), 'compensation-protocol'],
    ['wrong compensation result scope', s => s.replace('arguments:material.compensations["undo-first"].arguments(input,results)', 'arguments:material.compensations["undo-first"].arguments(input,[])'), 'compensation-protocol'],
    ['skip compensation occurrence', s => s.replace('for(const row of intent.plan){', 'for(const row of intent.plan.slice(1)){'), 'compensation-protocol'],
    ['false execution claim', s => s.replace('compensation_execution:false,authority_effect:"none"', 'compensation_execution:true as false,authority_effect:"none"'), 'compensation-protocol']
  ];
  for (const [name, mutate, code] of changes) {
    const next = mutate(original); assert.notEqual(next, original, name); fs.writeFileSync(p, next); c.compile();
    for (const phase of ['source', 'native'] as const) assert.ok(violations(c.audit(phase, c.freshProviderHashes)).some((v: any) => v.code === code), phase + ':' + name);
  }
  t.diagnostic(JSON.stringify({strict_compiling_mutations: changes.length, phase_rejections: changes.length * 2}));
});

function distinct(t: Parameters<typeof workflowFixture>[0]) {
  const f = workflowFixture(t), source = path.join(f.root, 'source');
  const read = (p: string) => JSON.parse(fs.readFileSync(path.join(source, p), 'utf8'));
  const write = (p: string, v: unknown) => fs.writeFileSync(path.join(source, p), JSON.stringify(v));
  const feature = read('specs/commerce/feature.json'), op = read('specs/commerce/nodes/perform.json');
  op.node_id = 'other'; op.body.failure_continuation = 'return-other-error'; write('specs/commerce/nodes/other.json', op); feature.nodes.push('other');
  for (const [from, relationship] of [['allowed', 'enforces'], ['flow', 'orchestrates']]) {
    const edge_id = from + '-' + relationship + '-other'; feature.edges.push(edge_id);
    write('specs/commerce/edges/' + edge_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id, relationship, source_node_id: from, target_node_id: 'other', scope: 'feature'});
  }
  const flow = read('specs/commerce/nodes/flow.json'); flow.body.typed_contract.steps[1].operation_ref = 'commerce:other'; flow.body.typed_contract.steps[3].operation_ref = 'commerce:other';
  write('specs/commerce/nodes/flow.json', flow); write('specs/commerce/feature.json', feature);
  const selection: any = structuredClone(f.selection), action = structuredClone(selection.operations[0]);
  action.selector = 'commerce:other'; action.result.value = {op: 'literal', type: 'UInt64', value: '11'}; selection.operations.push(action);
  return {...f, graph: loadCompiledProjectGraph(source), selection};
}

test('distinct Operation imports, exact dependency slots and repeated calls cannot be substituted', t => {
  const c = fixture(distinct(t)), p = path.join(c.root, c.profile.module_paths[0]!), original = fs.readFileSync(p, 'utf8');
  c.compile(); for (const phase of ['source', 'native'] as const) assert.deepEqual(violations(c.audit(phase)), []);
  assert.deepEqual(c.profile.workflow_modules[0]!.expected.steps.map(s => s.operation_ref), ['commerce:perform','commerce:other','commerce:perform','commerce:other']);
  const changes: [string, (s: string) => string, string][] = [
    ['wrong forward call', s => s.replace('raw=await call1(args,dep1)', 'raw=await call0(args,dep1)'), 'execute-protocol'],
    ['wrong dependency', s => s.replace('raw=await call1(args,dep1)', 'raw=await call1(args,dep0)'), 'execute-protocol'],
    ['wrong callable capture', s => s.replace('const call1=forward1', 'const call1=forward0'), 'execute-protocol'],
    ['wrong dependency capture', s => s.replace('const dep1=d["commerce:perform"]', 'const dep1=d["commerce:other"]'), 'execute-protocol'],
    ['wrong imported module', s => s.replace('import {operationPerform as forward1} from ' + JSON.stringify(c.profile.workflow_modules[0]!.expected.imports[1]!.path), 'import {operationOther as forward1} from ' + JSON.stringify(c.profile.workflow_modules[0]!.expected.imports[0]!.path)), 'module-protocol'],
    ['foreign exported call alias', s => s + '\nexport const escape=forward0;\n', 'module-protocol'],
    ['external forward call', s => s + '\nconst extra=()=>forward0({amount:7n},{} as never);\n', 'call-scope']
  ];
  for (const [name, mutate, code] of changes) {
    const next = mutate(original); assert.notEqual(next, original, name); fs.writeFileSync(p, next); c.compile();
    for (const phase of ['source', 'native'] as const) assert.ok(violations(c.audit(phase, c.freshProviderHashes)).some((v: any) => v.code === code), phase + ':' + name);
  }
  t.diagnostic(JSON.stringify({strict_compiling_mutations: changes.length, phase_rejections: changes.length * 2}));
});

test('source-only type wrappers and formatting do not change the executable protocol', t => {
  const c = fixture(workflowFixture(t)), p = path.join(c.root, c.profile.module_paths[0]!), original = fs.readFileSync(p, 'utf8');
  const changed = original.replace('raw=await call0(args,dep0)', 'raw = (await ((call0))(args as typeof args, (dep0!)))').replace('args=material.steps["first"]', 'args /* argument role */ = (material.steps["first"])');
  assert.notEqual(changed, original); fs.writeFileSync(p, changed); c.compile();
  for (const phase of ['source', 'native'] as const) assert.deepEqual(violations(c.audit(phase, c.freshProviderHashes)), []);
});

test('invalid requests and source drift fail closed; native-only structure drift remains observable', t => {
  const c = fixture(workflowFixture(t)); c.compile();
  for (const change of [
    (v: any) => v.definition += '\n', (v: any) => v.phase = 'other', (v: any) => v.module_root = 'relative',
    (v: any) => v.module_paths.push(v.module_paths[0]), (v: any) => v.module_paths[0] = '../escape.ts',
    (v: any) => v.workflow_modules = [], (v: any) => v.workflow_modules.push(v.workflow_modules[0]),
    (v: any) => v.workflow_modules[0].relative_path = 'foreign.ts', (v: any) => v.workflow_modules[0].source_sha256 = '0'.repeat(64),
    (v: any) => v.workflow_modules[0].extra = true
  ]) assert.throws(() => c.audit('source', change), /WORKFLOW_ORCHESTRATION:/);
  const source = c.audit('source'), nativePath = c.profile.module_paths[0]!.replace(/\.ts$/, '.js'), nativeFile = path.join(c.root, 'js', nativePath), before = fs.readFileSync(nativeFile, 'utf8');
  const changed = before.replace('raw = await call0(args, dep0)', 'raw = call0(args, dep0)'); assert.notEqual(changed, before); fs.writeFileSync(nativeFile, changed);
  assert.deepEqual(c.audit('source'), source); const native = c.audit('native');
  assert.ok(violations(native).some((v: any) => v.code === 'execute-protocol')); assert.equal(native.modules[0].source_sha256, sha256(changed));
  fs.appendFileSync(path.join(c.root, c.profile.module_paths[0]!), '\n// source drift\n'); assert.throws(() => c.audit('source'), /source drift/);
});

test('orchestration profile remains complete when finite witness generation exceeds its fixed budget', t => {
  const f = workflowFixture(t), source = path.join(f.root, 'source'), file = path.join(source, 'specs/commerce/nodes/flow.json'), flow = JSON.parse(fs.readFileSync(file, 'utf8')), selection: any = structuredClone(f.selection);
  const ids = [...stepIds, ...Array.from({length: 124}, (_, i) => 'step-' + i)];
  flow.body.typed_contract.steps = ids.map(step_id => ({step_id, operation_ref: 'commerce:perform'})); fs.writeFileSync(file, JSON.stringify(flow));
  selection.workflows[0].steps = ids.map((step_id, i) => ({step_id, arguments: [{parameter: 'amount', value: i ? {op: 'step-result', step_id: ids[i - 1], properties: []} : {op: 'input', name: 'amount', properties: []}}], events: []}));
  const graph = loadCompiledProjectGraph(source), c = fixture({...f, graph, selection});
  const executionDefinitions: any = Object.fromEntries(Object.entries({execution: 'semantic-workflow-execution-contract.json', binding: 'semantic-workflow-binding-contract.json', values: 'semantic-workflow-values-contract.json', outcomes: 'semantic-workflow-controls-contract.json'}).map(([k, p]) => [k, fs.readFileSync(path.join(base, p), 'utf8')]));
  assert.throws(() => createWorkflowCases(graph.nodes.find(n => n.kind === 'Workflow')!, graph, c.plan, executionDefinitions, fs.readFileSync(path.join(base, 'semantic-workflow-cases-contract.json'), 'utf8')), isWorkflowCasesCapacity);
  assert.equal(c.profile.workflow_modules[0]!.expected.steps.length, 128); c.compile();
  for (const phase of ['source', 'native'] as const) assert.deepEqual(violations(c.audit(phase)), []);
});

test('profile preserves source ownership, definitions, graph brands and independent selected prefixes', t => {
  const f = workflowFixture(t), {plan, profile} = selected(f);
  assert.equal(sha256(definition), WORKFLOW_ORCHESTRATION_DEFINITION_SHA256);
  assert.deepEqual(profile.roots, ['commerce:flow']); assert.ok(Object.isFrozen(profile.workflow_modules[0]!.expected));
  assert.equal(canonicalJson(createWorkflowOrchestrationAudit(f.graph, plan, definitions)), canonicalJson(profile));
  assert.throws(() => createWorkflowOrchestrationAudit({...f.graph} as any, plan, definitions));
  assert.throws(() => createWorkflowOrchestrationAudit(f.graph, {...plan} as any, definitions));
  for (const k of Object.keys(definitions)) assert.throws(() => createWorkflowOrchestrationAudit(f.graph, plan, {...definitions, [k]: (definitions as any)[k] + '\n'}), /definition drift/);
  assert.throws(() => createWorkflowOrchestrationAudit(workflowFixture(t, {noCompensations: true}).graph, plan, definitions), /cross-graph/);
  assert.equal(profile.workflow_modules[0]!.expected.imports.length, 1);
  assert.deepEqual(profile.workflow_modules[0]!.expected.prefix_templates[3]!.plan.map(c => c.compensation_id), ['undo-third', 'undo-second', 'undo-first']);
  const constrained = selected(workflowFixture(t, {dependencies: [[], ['undo-first'], ['undo-second']], declarationOrder: [2, 0, 1]}));
  assert.deepEqual(constrained.profile.workflow_modules[0]!.expected.prefix_templates[3]!.plan.map(c => c.compensation_id), ['undo-first', 'undo-second', 'undo-third']);
});

test('clean TypeScript and strict-emitted ESM pass exact executable and recovery protocols', t => {
  for (const f of [workflowFixture(t), workflowFixture(t, {dependencies: [[], ['undo-first'], ['undo-second']]}), workflowFixture(t, {noCompensations: true}), workflowValuesFixture(t, {type: named('choice'), events: true})]) {
    const c = fixture(f); c.compile();
    for (const phase of ['source', 'native'] as const) {
      const o = c.audit(phase); assert.equal(o.schema_version, 'domainspec.workflow-orchestration-observation/v1-candidate');
      assert.equal(o.phase, phase); assert.equal(o.definition_sha256, WORKFLOW_ORCHESTRATION_DEFINITION_SHA256);
      assert.deepEqual(violations(o), []);
      assert.deepEqual(o.modules.map((m: any) => m.relative_path), c.input(phase).module_paths);
      for (const m of o.modules) assert.equal(m.source_sha256, sha256(fs.readFileSync(path.join(c.input(phase).module_root, m.relative_path), 'utf8')));
    }
  }
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
