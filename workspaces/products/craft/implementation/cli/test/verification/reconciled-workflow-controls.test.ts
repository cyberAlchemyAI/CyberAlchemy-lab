import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {workflowFixture, workflowProject, stepIds} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture, named} from '../helpers/workflow-values.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createWorkflowControls, workflowVerificationDefinitions, SEMANTIC_WORKFLOW_DEFINITION_SHA256} from '../../src/verification/reconciled-workflow-controls.ts';
import {createWorkflowEffectAudit} from '../../src/verification/reconciled-workflow-effect-audit.ts';
import {createWorkflowOrchestrationAudit} from '../../src/verification/reconciled-workflow-orchestration-audit.ts';
import {createReconciledSemanticControls, renderSemanticCases, SEMANTIC_RUNNER} from '../../src/verification/reconciled-semantic-controls.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {WORKFLOW_SEMANTIC_RUNNER} from '../../src/verification/reconciled-workflow-runner.ts';

test('Workflow recipe expansion bounds cycles, references, occurrence order and aggregate decoded payload', t => {
  const f = workflowFixture(t), module = path.join(f.root, 'expand.mjs'), client = path.join(f.root, 'expand-test.mjs');
  fs.writeFileSync(module, WORKFLOW_SEMANTIC_RUNNER + '\nexport {expandWorkflowCase};\n');
  fs.writeFileSync(client, String.raw`
import assert from 'node:assert/strict';import {expandWorkflowCase as expand} from './expand.mjs';
const row={workflow_steps:[{step_id:'first'}],recipes:[{tag:'string',value:'ok'}]},data={input:0,steps:[{step_id:'first',reads:[]}]};
assert.equal(expand(row,data).input.value,'ok');
for(const input of [-1,0.5,Number.MAX_SAFE_INTEGER+1,1])assert.throws(()=>expand(row,{...data,input}),/WORKFLOW_RECIPE/);
for(const value of ['-1','01','1e0','9007199254740992'])assert.throws(()=>expand({...row,recipes:[{tag:'ref',value}]},data),/WORKFLOW_RECIPE/);
assert.throws(()=>expand({...row,recipes:[{tag:'ref',value:'0'}]},data),/WORKFLOW_RECIPE/);
assert.throws(()=>expand(row,{...data,steps:[{step_id:'other',reads:[]}]}),/WORKFLOW_OCCURRENCES/);
assert.throws(()=>expand(row,{...data,steps:[]}),/WORKFLOW_OCCURRENCES/);
const chain=Array.from({length:130},(_,i)=>i===129?{tag:'null'}:{tag:'ref',value:String(i+1)});
assert.throws(()=>expand({...row,recipes:chain},data),/WORKFLOW_RECIPE_CAPACITY/);
const broad={tag:'list',items:Array.from({length:32769},()=>({tag:'ref',value:'0'}))};
assert.throws(()=>expand({...row,recipes:[{tag:'null'},broad]},{...data,input:1}),/WORKFLOW_RECIPE_CAPACITY/);
// UTF-8 size, including repeated reads, is charged while expanding.
const unicode={...row,recipes:[{tag:'string',value:'\u20ac'.repeat(1500000)}]};
assert.equal(expand(unicode,data).input.value.length,1500000);
assert.throws(()=>expand(unicode,{...data,steps:[{step_id:'first',reads:[{value:0}]}]}),/WORKFLOW_RECIPE_CAPACITY/);
console.log(JSON.stringify({reference_and_capacity_controls:14}));
`);
  assert.equal(JSON.parse(execFileSync(process.execPath, [client], {encoding: 'utf8'})).reference_and_capacity_controls, 14);
});

test('public source, snapshot and actual CLI verify typed and Event Workflow cases in both layouts', t => {
  let observedCases = 0;
  for (const events of [false, true]) {
    const f = workflowValuesFixture(t, events ? {type: named('choice'), events: true} : {type: named('money')}), n = nativeContext(f);
    const reports = publicClient(f, n, String.raw`
import {publishReconciledProject} from './dist/generation/reconciled-output.js';
const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),file=path.join(source,'selection.json'),reports=[];
fs.writeFileSync(file,JSON.stringify(selection));
for(const output_layout of [undefined,'domainspec.application-layout/v1']){
 const target=path.join(path.dirname(source),output_layout?'application':'plain'),selected={...tools,target_root:target,...(output_layout?{output_layout}:{})};
 publishReconciledProject(plan,target,null,output_layout);
 let report;
 if(output_layout){
  const args=['./dist/cli/main.js','verify-project',source,'--compilation-selection',file,'--target-root',target,'--typescript-root',tools.typescript_root,'--node-type-root',tools.node_type_root,'--lean-executable',tools.lean_executable,'--output-layout',output_layout];
  const result=cp.spawnSync(process.execPath,args,{encoding:'utf8',timeout:150000,maxBuffer:32*1024*1024});
  if(result.status!==1||result.stderr)throw Error('CLI boundary:'+result.status+':'+result.stderr);
  report=JSON.parse(result.stdout);
 }else report=` + (events ? 'verifyReconciledSourceProject(source,selection,selected)' : 'verifyCompiledReconciledProject(graph,selection,selected)') + String.raw`;
 reports.push(report);
}
console.log(JSON.stringify(reports));
`);
    for (const report of reports) {
      assert.equal(report.result, 'incomplete', JSON.stringify(report.checks));
      for (const id of [...workflowChecks,'strict-native-compilation','selected-generator-semantic-controls','lean-structural-kernel','exact-output-currentness','semantic-workspace-currentness','verification-workspace-cleanup']) assert.equal(get(report,id)?.result, 'pass', id + ':' + JSON.stringify(get(report,id)));
      const tested = get(report,'selected-generator-semantic-controls').evidence.tested.find((r: any) => r.selector === 'commerce:flow');
      assert.ok(tested && tested.case_count > 100, JSON.stringify(tested)); observedCases += tested.case_count;
    }
  }
  t.diagnostic(JSON.stringify({native_workflow_cases: observedCases, reports: 4, real_lean: true}));
});

function nativeContext(f: ReturnType<typeof workflowFixture>) {
  const cliRoot = path.join(workflowProject, 'impl/cli'), src = path.join(cliRoot, 'src'), dist = path.join(f.root, 'dist');
  const require = createRequire(import.meta.url), types = require.resolve('@types/node/package.json', {paths: process.execArgv.filter(a => a.endsWith('loader.mjs')).map(p => path.dirname(p))}), deps = path.dirname(path.dirname(path.dirname(types)));
  const undici = path.dirname(createRequire(fs.realpathSync(types)).resolve('undici-types/package.json'));
  const lean = process.env.DOMAINSPEC_LEAN!; assert.ok(lean && path.isAbsolute(lean), 'explicit installed Lean required'); const leanRoot = path.dirname(path.dirname(lean));
  const image = nativeToolchainImage();
  assert.equal(image, NATIVE_TEST_IMAGE_ID);
  fs.mkdirSync(path.join(f.root, 'scratch')); fs.writeFileSync(path.join(f.root, 'package.json'), '{"type":"module"}');
  const docker = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(),
    '--mount', 'type=bind,source=' + cliRoot + ',target=' + cliRoot + ',readonly', '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly',
    '--mount', 'type=bind,source=' + undici + ',target=' + undici + ',readonly', '--mount', 'type=bind,source=' + leanRoot + ',target=' + leanRoot + ',readonly', '--mount', 'type=bind,source=' + f.root + ',target=' + f.root,
    '--workdir', f.root, '--env', 'TMPDIR=' + path.join(f.root, 'scratch'), image];
  const execute = (args: string[]) => {
    try {return execFileSync('docker', [...docker, ...args], {encoding: 'utf8', timeout: 600000, maxBuffer: 32 * 1024 * 1024});}
    catch (e) {const error = e as any; throw Error(String(error.code ?? '') + ':' + String(error.stdout) + String(error.stderr));}
  };
  execute(['tsc', '--ignoreConfig', '--strict', '--skipLibCheck', '--declaration', '--types', 'node', '--typeRoots', path.join(deps, '@types'), '--target', 'ES2022', '--module', 'NodeNext', '--rootDir', src, '--outDir', dist, path.join(src, 'index.ts'), path.join(src, 'cli/main.ts')]);
  const options = {typescript_root: '/opt/node-toolchain/node_modules/typescript', node_type_root: path.join(deps, '@types'), lean_executable: lean};
  const run = (body: string) => {const file = path.join(f.root, 'client.mjs'); fs.writeFileSync(file, body); return JSON.parse(execute(['node', file]));};
  return {run, options};
}
const workflowChecks = ['workflow-source-effect-audit', 'workflow-native-effect-audit', 'workflow-effect-audit-currentness', 'workflow-source-orchestration-audit', 'workflow-native-orchestration-audit', 'workflow-orchestration-audit-currentness'];
const get = (report: any, id: string) => report.checks.find((c: any) => c.id === id);

function mixedWorkflow(t: Parameters<typeof workflowFixture>[0]) {
  const f = largeWorkflow(t), source = path.join(f.root, 'source'), feature = 'ready', selection: any = structuredClone(f.selection);
  const copy = (v: unknown) => JSON.parse(JSON.stringify(v).replaceAll('commerce:', feature + ':').replaceAll('FIXTURE-', 'READY-FIXTURE-'));
  for (const kind of ['nodes','edges']) {
    const target = path.join(source, 'specs', feature, kind); fs.mkdirSync(target, {recursive: true});
    for (const file of fs.readdirSync(path.join(source, 'specs/commerce', kind))) {
      const row = copy(JSON.parse(fs.readFileSync(path.join(source, 'specs/commerce', kind, file), 'utf8'))); row.feature_id = feature;
      if (row.kind === 'Workflow') row.body.typed_contract.steps = row.body.typed_contract.steps.slice(0, 4);
      fs.writeFileSync(path.join(target, file), JSON.stringify(row));
    }
  }
  const manifest = JSON.parse(fs.readFileSync(path.join(source, 'specs/commerce/feature.json'), 'utf8')); manifest.feature_id = feature;
  fs.writeFileSync(path.join(source, 'specs', feature, 'feature.json'), JSON.stringify(manifest));
  selection.operations.push(...copy(f.selection.operations)); const workflow = copy(f.selection.workflows[0]); workflow.steps = workflow.steps.slice(0, 4); selection.workflows.push(workflow);
  const project = JSON.parse(fs.readFileSync(path.join(source, 'project.json'), 'utf8')); project.features.push(feature); fs.writeFileSync(path.join(source, 'project.json'), JSON.stringify(project));
  return {...f, graph: loadCompiledProjectGraph(source), selection};
}

test('public partial coverage audits all sources and filters native metadata to ready Workflow scopes', t => {
  const f = mixedWorkflow(t), n = nativeContext(f), report = publicClient(f, n, String.raw`
const original=cp.spawnSync;cp.spawnSync=(command,args,settings)=>command===tools.lean_executable?{status:1,stdout:'',stderr:'isolated partial-coverage test; not Lean evidence'}:original(command,args,settings);syncBuiltinESMExports();
try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);console.log(JSON.stringify(executeReconciledVerification(graph,plan,tools)));}finally{cp.spawnSync=original;syncBuiltinESMExports();}
`);

  // WPE-T04: a passing ready-only lane is not a complete source audit.
  const nativeAuditIds = ['workflow-native-effect-audit','workflow-native-orchestration-audit'];
  for (const id of [...workflowChecks.filter(id => !nativeAuditIds.includes(id)),'semantic-workspace-currentness','verification-workspace-cleanup']) assert.equal(get(report, id)?.result, 'pass', id + ':' + JSON.stringify(report.checks));
  for (const [index, id] of nativeAuditIds.entries()) {
    const audit = get(report,id), evidence = audit.evidence;
    const suffixes = index === 0 ? ['application/operations/perform.provider.ts','application/operations/perform.ts','application/workflows/flow.material.ts','application/workflows/flow.provider.ts','application/workflows/flow.ts','domain/rules/allowed.ts'] : ['application/workflows/flow.provider.ts'];
    const expected = (feature: string) => suffixes.map(suffix => 'domain/features/' + feature + '/src/' + suffix);
    assert.equal(audit.result,'not_evaluable'); assert.equal(audit.executed,true);
    assert.equal(evidence.original_standalone_result,'pass','retain the original ready-only success');
    assert.equal(evidence.scope,'complete-source-workflow-audit-path-and-root-union');
    assert.deepEqual(evidence.required_workflow_selectors,['commerce:flow','ready:flow']);
    assert.deepEqual(evidence.missing_workflow_selectors,['commerce:flow']);
    assert.deepEqual(evidence.required_source_paths,[...expected('commerce'),...expected('ready')]);
    assert.deepEqual(evidence.missing_source_paths,expected('commerce'));
    for (const origin of ['original-standalone-native','original-retained-workflow-native']) {
      assert.deepEqual(evidence.origins.filter((o: any) => o.origin === origin).map((o: any) => o.source_path).sort(),expected('ready'));
    }
    assert.ok(evidence.modules.every((m: any) => m.violations.length === 0));
  }
  assert.deepEqual(get(report,'workflow-source-effect-audit').evidence.selectors, ['commerce:flow','ready:flow']);
  assert.deepEqual(get(report,'workflow-native-effect-audit').evidence.selectors, ['ready:flow']);
  assert.equal(get(report,'workflow-source-orchestration-audit').evidence.module_count, 2);
  assert.equal(get(report,'workflow-native-orchestration-audit').evidence.module_count, 1);
  const semantic = get(report,'selected-generator-semantic-controls');
  assert.equal(semantic.result, 'not_evaluable'); assert.equal(semantic.executed, true);
  assert.deepEqual(semantic.blocked_by,nativeAuditIds);
  assert.ok(semantic.evidence.tested.some((r: any) => r.selector === 'ready:flow'));
  assert.ok(!semantic.evidence.tested.some((r: any) => r.selector === 'commerce:flow'));
  assert.ok(semantic.evidence.remaining.some((r: any) => r.selector === 'commerce:flow'));
});

test('native import resolution grants only the bound Workflow provider its exact crypto exception', t => {
  const f = workflowFixture(t), root = f.root, script = path.join(root, 'semantic.mjs'), cases = path.join(root, 'cases.json'), provider = path.join(root, 'root.js'), child = path.join(root, 'child.js');
  fs.writeFileSync(path.join(root, 'package.json'), '{"type":"module"}'); fs.writeFileSync(script, SEMANTIC_RUNNER);
  const source = 'import {createHash} from "node:crypto";import {operation} from "./child.js";export const workflow=Object.freeze(async()=>null);';
  fs.writeFileSync(provider, source); fs.writeFileSync(child, 'export const operation=Object.freeze(()=>null);');
  const edge = {specifier: './child.js', target_path: 'child.ts'}, crypto = {specifier: 'node:crypto', target_path: null};
  const row = {selector: 'alpha:flow', adapter: 'workflow', relative_path: 'root.ts', provider_path: 'root.ts', callable: 'workflow', workflow_steps: [], recipes: [], cases: [],
    native_imports: [{relative_path: 'root.ts', imports: [crypto, edge, edge]}, {relative_path: 'child.ts', imports: []}]};
  const operation = {selector: 'alpha:operation', adapter: 'operation', relative_path: 'child.ts', callable: 'operation', recipes: [], cases: [], native_imports: [{relative_path: 'child.ts', imports: []}]};
  const run = (rows: any[]) => {fs.writeFileSync(cases, JSON.stringify({rows})); return execFileSync(process.execPath, ['--permission', '--allow-fs-read=' + root, script, cases, root], {encoding: 'utf8', stdio: 'pipe'});};
  assert.deepEqual(JSON.parse(run([row, operation])), [{selector: row.selector, cases: []}, {selector: operation.selector, cases: []}]);
  for (const change of [
    (r: any) => r.provider_path = 'foreign.ts',
    (r: any) => r.native_imports[0].imports[0].specifier = 'node:fs',
    (r: any) => r.native_imports[1].imports.push(crypto)
  ]) {const next = structuredClone(row); change(next); assert.throws(() => run([next]), /WORKFLOW_NATIVE_IMPORT_BOUNDARY/);}
  assert.throws(() => run([{...row, adapter: 'operation'}]), /OPERATION_NATIVE_IMPORT_BOUNDARY/);
  assert.throws(() => run([{...row, native_imports: [{relative_path: 'root.ts', imports: [crypto, edge, {...edge, target_path: 'other.ts'}]}]}]), /SEMANTIC_NATIVE_IMPORT_CONFLICT/);
  assert.throws(() => run([row, {...operation, native_imports: [{relative_path: 'child.ts', imports: [{specifier: './missing.js', target_path: 'missing.ts'}]}]}]), /SEMANTIC_NATIVE_IMPORT_CONFLICT/);
  fs.writeFileSync(provider, source.replace('./child.js', './child.js?changed')); assert.throws(() => run([row]), /WORKFLOW_NATIVE_IMPORT_BOUNDARY/);
  fs.writeFileSync(provider, source); fs.writeFileSync(child, 'import "node:fs";export const operation=Object.freeze(()=>null);');
  assert.throws(() => run([row, operation]), error => /WORKFLOW_NATIVE_IMPORT_BOUNDARY/.test(String(error)) && /OPERATION_NATIVE_IMPORT_BOUNDARY/.test(String(error)));
});

function largeWorkflow(t: Parameters<typeof workflowFixture>[0], count = 128) {
  const f = workflowFixture(t), source = path.join(f.root, 'source'), file = path.join(source, 'specs/commerce/nodes/flow.json'), flow = JSON.parse(fs.readFileSync(file, 'utf8')), selection: any = structuredClone(f.selection);
  const ids = [...stepIds, ...Array.from({length: count - 4}, (_, i) => 'step-' + i)];
  flow.body.typed_contract.steps = ids.map(step_id => ({step_id, operation_ref: 'commerce:perform'})); fs.writeFileSync(file, JSON.stringify(flow));
  selection.workflows[0].steps = ids.map((step_id, i) => ({step_id, arguments: [{parameter: 'amount', value: i ? {op: 'step-result', step_id: ids[i - 1], properties: []} : {op: 'input', name: 'amount', properties: []}}], events: []}));
  return {...f, graph: loadCompiledProjectGraph(source), selection};
}

test('whole-node capacity rejects all cases while retaining both source audit obligations', t => {
  const f = largeWorkflow(t), plan = planCompiledReconciledProject(f.graph, f.selection), row = createWorkflowControls(f.graph.nodes.find(n => n.kind === 'Workflow')!, f.graph, plan);
  assert.equal(row.state, 'not_evaluable'); assert.equal('cases' in row, false); assert.match((row as any).reason, /bounded Workflow/);
  const all = createReconciledSemanticControls(f.graph, plan), audit = auditProfiles(f, plan);
  assert.equal(all.node_count, f.graph.nodes.length); assert.equal(all.rows.find(r => r.kind === 'Workflow')!.state, 'not_evaluable');
  assert.deepEqual(audit.effects.roots, ['commerce:flow']); assert.deepEqual(audit.orchestration.roots, ['commerce:flow']);
  assert.equal(audit.orchestration.workflow_modules[0]!.expected.steps.length, 128);
});

test('deep owned Order capacity remains explicit instead of discarding typed cases', t => {
  const f = workflowValuesFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const row = createWorkflowControls(f.graph.nodes.find(n => n.kind === 'Workflow')!, f.graph, plan);
  assert.equal(row.state, 'not_evaluable'); assert.equal('cases' in row, false);
  assert.match((row as any).reason, /bounded Workflow serialized suite exceeds 8 MiB/);
  assert.deepEqual(auditProfiles(f,plan).effects.roots, ['commerce:flow']);
});

test('project byte capacity never truncates a Workflow and retains all source closures', t => {
  const f = largeWorkflow(t, 16), source = path.join(f.root, 'source'), manifest = JSON.parse(fs.readFileSync(path.join(source, 'specs/commerce/feature.json'), 'utf8')), selection: any = structuredClone(f.selection);
  const features = ['commerce', 'commerce-other'];
  for (const feature of features.slice(1)) {
    const copy = (v: unknown) => JSON.parse(JSON.stringify(v).replaceAll('commerce:', feature + ':').replaceAll('FIXTURE-', feature.toUpperCase() + '-FIXTURE-'));
    for (const kind of ['nodes', 'edges']) {
      const target = path.join(source, 'specs', feature, kind); fs.mkdirSync(target, {recursive: true});
      for (const file of fs.readdirSync(path.join(source, 'specs/commerce', kind))) {
        const row = copy(JSON.parse(fs.readFileSync(path.join(source, 'specs/commerce', kind, file), 'utf8'))); row.feature_id = feature;
        fs.writeFileSync(path.join(target, file), JSON.stringify(row));
      }
    }
    fs.writeFileSync(path.join(source, 'specs', feature, 'feature.json'), JSON.stringify({...manifest, feature_id: feature}));
    selection.operations.push(...copy(f.selection.operations)); selection.workflows.push(...copy(f.selection.workflows));
  }
  const project = JSON.parse(fs.readFileSync(path.join(source, 'project.json'), 'utf8')); project.features = features; fs.writeFileSync(path.join(source, 'project.json'), JSON.stringify(project));
  const graph = loadCompiledProjectGraph(source), plan = planCompiledReconciledProject(graph, selection), controls = createReconciledSemanticControls(graph, plan), rows = controls.rows.filter(r => r.kind === 'Workflow'), audit = auditProfiles({...f, graph, selection}, plan);
  assert.equal(rows.length, 2); assert.ok(rows.some(r => r.state === 'ready')); assert.ok(rows.some(r => r.state === 'not_evaluable'));
  for (const row of rows) if (row.state === 'not_evaluable') {assert.equal('cases' in row, false); assert.match(row.reason, /bounded semantic case capacity/);}
  assert.deepEqual(audit.effects.roots, rows.map(r => r.selector).sort()); assert.deepEqual(audit.orchestration.roots, audit.effects.roots);
  assert.equal(controls.case_count, controls.rows.reduce((n, r) => n + (r.state === 'ready' ? r.cases.length : 0), 0));
  assert.ok(Buffer.byteLength(renderSemanticCases(controls)) <= 8388608);
  t.diagnostic(JSON.stringify({workflows: rows.length, ready: rows.filter(r => r.state === 'ready').length, unavailable: rows.filter(r => r.state === 'not_evaluable').length, bytes: Buffer.byteLength(renderSemanticCases(controls))}));
});

function publicClient(f: ReturnType<typeof workflowFixture>, n: ReturnType<typeof nativeContext>, body: string) {
  return n.run("import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';\n" +
    "import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification,verifyCompiledReconciledProject,verifyReconciledSourceProject} from './dist/index.js';\n" +
    "const source=" + JSON.stringify(path.join(f.root, 'source')) + ",selection=" + JSON.stringify(f.selection) + ",tools=" + JSON.stringify(n.options) + ";\n" + body);
}

test('public Workflow verification rejects native behavior, structural, effect and audit-custody mutations', t => {
  const f = workflowFixture(t), n = nativeContext(f);
  const reports = publicClient(f, n, String.raw`
const original=cp.spawnSync,reports=[];
const modes=['clean','descriptor','material-result','missing-await','wrong-argument','terminal-stop','prefix-template','crypto-helper','native-date','native-class',
 'source-pin','effect-source-omit','effect-native-phase','effect-native-hash','effect-source-script','effect-native-script','effect-native-input',
 'structure-source-omit','structure-native-phase','structure-native-hash','structure-source-script','structure-native-script','structure-native-input',
 'late-effect','late-structure','late-module'];
for(const mode of modes){
 let calls=0,changed=false;const scripts={};
 cp.spawnSync=(command,args,settings)=>{
  if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated Workflow mutation; not Lean evidence'};
  if(args.includes('--permission'))calls++;
  const config=args[args.indexOf('--project')+1],provider='domain/features/commerce/src/application/workflows/flow.provider';
  if(mode==='source-pin'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json')){fs.appendFileSync(path.join(path.dirname(config),provider+'.ts'),'\n// source changed\n');changed=true;}
  const result=original(command,args,settings);
  if(result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json')&&['descriptor','material-result','missing-await','wrong-argument','terminal-stop','prefix-template','crypto-helper','native-date','native-class'].includes(mode)){
   let file=path.join(path.dirname(config),'modules',provider+'.js');
   if(mode==='descriptor')file=file.replace('.provider.js','.js');
   if(mode==='material-result')file=file.replace('.provider.js','.material.js');
   const old=fs.readFileSync(file,'utf8');let next=old;
   if(mode==='descriptor')next=old.replace('typescript.bound-workflow/v1','typescript.bound-workflow/wrong');
   if(mode==='material-result')next=old.replace('export const result = (input, results) => {','export const result = (input, results) => { return 0n;');
   if(mode==='missing-await')next=old.replace('raw = await call0(args, dep0)','raw = call0(args, dep0)');
   if(mode==='wrong-argument')next=old.replace('material.steps["first"].arguments(input, results)','material.steps["second"].arguments(input, results)');
   if(mode==='terminal-stop')next=old.replace('if (settlement.commit_status !== "committed")','if (false && settlement.commit_status !== "committed")');
   if(mode==='prefix-template')next=old.replace('["for_step"]: "third"','["for_step"]: "first"');
   if(mode==='crypto-helper')next=old.replace("createHash('sha256')","createHash('sha1')");
   if(mode==='native-date')next=old+'\nvoid Date.now();\n';
   if(mode==='native-class')next=old+'\nclass UnselectedWorkflow {}\n';
   if(next===old)throw Error('Workflow mutant not installed:'+mode);fs.writeFileSync(file,next);changed=true;
   const syntax=original(process.execPath,['--check',file],{encoding:'utf8',timeout:60000});if(syntax.status!==0)throw Error('Workflow mutant syntax:'+mode+':'+syntax.stderr);
  }
  const script=args.find(a=>String(a).endsWith('/workflow-effects.mjs')||String(a).endsWith('/workflow-orchestration-effects.mjs'));
  if(script&&result.status===0){
   const kind=String(script).endsWith('/workflow-effects.mjs')?'effect':'structure',observed=JSON.parse(result.stdout);scripts[kind]=script;
   if(mode===kind+'-source-omit'&&observed.phase==='source'){observed.modules.pop();result.stdout=JSON.stringify(observed);changed=true;}
   if(mode===kind+'-native-phase'&&observed.phase==='native'){observed.phase='source';result.stdout=JSON.stringify(observed);changed=true;}
   if(mode===kind+'-native-hash'&&observed.phase==='native'){observed.modules[0].source_sha256='0'.repeat(64);result.stdout=JSON.stringify(observed);changed=true;}
   if(mode===kind+'-'+observed.phase+'-script'){fs.appendFileSync(script,'\n// changed script\n');changed=true;}
   if(mode===kind+'-native-input'&&observed.phase==='native'){fs.appendFileSync(args.at(-1),' ');changed=true;}
  }
  if(args.includes('--permission')&&result.status===0){
   if(mode==='late-effect'||mode==='late-structure'){fs.appendFileSync(scripts[mode.slice(5)],'\n// late drift\n');changed=true;}
   if(mode==='late-module'){fs.appendFileSync(path.join(settings.cwd,'modules',provider+'.js'),' ');changed=true;}
  }
  return result;
 };syncBuiltinESMExports();
 try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),report=executeReconciledVerification(graph,plan,tools);reports.push({mode,calls,changed,report});}
 finally{cp.spawnSync=original;syncBuiltinESMExports();}
}
console.log(JSON.stringify(reports));
`);

  for (const {mode, calls, changed, report} of reports) {
    const semantic = get(report, 'selected-generator-semantic-controls');
    assert.ok(mode === 'clean' || changed, 'mutation reached:' + mode);
    if (mode === 'clean') {assert.equal(semantic.result, 'pass', JSON.stringify(semantic)); assert.ok(calls > 0);}
    else if (mode === 'descriptor' || mode === 'material-result') {assert.equal(semantic.result, 'fail', mode + ':' + JSON.stringify(semantic)); assert.ok(calls > 0); assert.match(semantic.reason, /observation mismatch/);}
    else if (['missing-await','wrong-argument','terminal-stop','prefix-template'].includes(mode)) {assert.equal(get(report, 'workflow-native-orchestration-audit').result, 'fail', mode); assert.equal(calls, 0);}
    else if (['crypto-helper','native-date','native-class'].includes(mode)) {assert.equal(get(report, 'workflow-native-effect-audit').result, 'fail', mode); assert.equal(calls, 0);}
    else if (mode.startsWith('late-')) {
      assert.ok(calls > 0); assert.equal(semantic.result, 'not_evaluable', mode);
      const id = mode === 'late-module' ? 'semantic-workspace-currentness' : mode === 'late-effect' ? 'workflow-effect-audit-currentness' : 'workflow-orchestration-audit-currentness';
      assert.equal(get(report, id).result, 'fail', mode);
      if (mode !== 'late-module') for (const phase of ['source','native']) assert.equal(get(report, mode === 'late-effect' ? 'workflow-' + phase + '-effect-audit' : 'workflow-' + phase + '-orchestration-audit').result, 'not_evaluable');
    } else {
      const structural = mode.startsWith('structure'), phase = mode.includes('native') ? 'native' : 'source';
      const id = structural ? 'workflow-' + phase + '-orchestration-audit' : 'workflow-' + phase + '-effect-audit';
      assert.equal(get(report, id).result, 'fail', mode + ':' + JSON.stringify(report.checks)); assert.equal(calls, 0, mode);
    }
    assert.equal(get(report, 'verification-workspace-cleanup').result, 'pass', mode);
  }
  t.diagnostic(JSON.stringify({native_or_evidence_mutations: reports.length - 1, clean_controls: 1, lean: 'isolated in this mutation test'}));
});
function auditProfiles(f: ReturnType<typeof workflowFixture>, plan = planCompiledReconciledProject(f.graph, f.selection)) {
  const d = workflowVerificationDefinitions();
  return {effects: createWorkflowEffectAudit(f.graph, plan, d.binding, d.effects), orchestration: createWorkflowOrchestrationAudit(f.graph, plan, d)};
}

test('complete public Workflow rows retain source cases, independent binding and exact external-import ownership', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection), node = f.graph.nodes.find(n => n.kind === 'Workflow')!;
  const row = createWorkflowControls(node, f.graph, plan); assert.equal(row.state, 'ready'); if (row.state !== 'ready') return;
  const all = createReconciledSemanticControls(f.graph, plan);
  assert.equal(all.adapter_definitions.workflow, SEMANTIC_WORKFLOW_DEFINITION_SHA256);
  assert.equal(canonicalJson(all.rows.find(r => r.selector === node.selector)), canonicalJson(row));
  assert.equal(canonicalJson(createWorkflowControls(node, f.graph, plan)), canonicalJson(row));
  assert.deepEqual(row.workflow_steps.map(s => s.step_id), stepIds);
  assert.equal(row.cases[0]!.mode, 'workflow-descriptor'); assert.ok(row.cases.length > 100); assert.ok(Object.isFrozen(row));
  assert.deepEqual(row.native_imports.flatMap(m => m.imports.filter(i => i.target_path === null).map(i => [m.relative_path, i.specifier])), [[row.provider_path, 'node:crypto']]);
  assert.ok(!row.module_paths.some(p => p.endsWith('/undo.ts')));
  assert.ok(row.cases.some(c => c.id === row.search.success_case_id)); assert.ok(Object.keys(row.coverage).length > 100);
  assert.equal(JSON.parse(renderSemanticCases(all)).rows.length, all.ready_count);
  const audit = auditProfiles(f, plan); assert.deepEqual(audit.orchestration.module_paths, [row.provider_path]); assert.deepEqual(audit.effects.module_paths, row.module_paths);
});

test('public Workflow verification executes real native dependencies with both audit scopes and final custody', t => {
  const f = workflowFixture(t), n = nativeContext(f);
  const report = n.run("import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';\n" +
    "const graph=loadCompiledProjectGraph(" + JSON.stringify(path.join(f.root, 'source')) + "),plan=planCompiledReconciledProject(graph," + JSON.stringify(f.selection) + ");\n" +
    "console.log(JSON.stringify(executeReconciledVerification(graph,plan," + JSON.stringify(n.options) + ")));");
  for (const id of [...workflowChecks, 'operation-source-effect-audit', 'operation-native-effect-audit', 'selected-generator-semantic-controls', 'semantic-workspace-currentness', 'verification-workspace-cleanup', 'lean-structural-kernel']) {
    assert.equal(get(report, id)?.result, 'pass', id + ':' + JSON.stringify(report.checks.filter((c: any) => c.result !== 'pass')));
  }
  const wf = report.semantic_coverage.rows.find((r: any) => r.kind === 'Workflow'); assert.equal(wf.adapter_status, 'ready'); assert.ok(wf.case_count > 100);
  assert.equal(get(report, 'workflow-source-orchestration-audit').evidence.module_count, 1);
  assert.ok(get(report, 'workflow-source-effect-audit').evidence.module_count > 1);
 const coverage=report.cross_generator_coverage;
 assert.equal(get(report,'cross-generator-behavior').result,'pass');
 assert.equal(get(report,'cross-generator-currentness').result,'pass');
 assert.equal(get(report,'verification-workspace-cleanup').result,'pass');
 assert.equal(coverage.public_result,'pass');
 assert.deepEqual(coverage.blocked_by,[]);
 assert.deepEqual(coverage.execution.currentness_issues,[]);
 assert.equal(coverage.evidence_scope,'sealed-historical-report-not-a-live-retained-receipt');
 assert.equal(coverage.execution.result,'pass');
 assert.equal(coverage.retained_workspace_state,'removed');
 assert.equal(fs.existsSync(coverage.execution.workspace),false);
 const retained=coverage.execution.retained.find((r:any)=>r.family==='workflow');
 assert.ok(retained,'actual retained Workflow execution is required');
 const row=coverage.execution.rows.find((r:any)=>r.family==='workflow'&&r.selector===wf.selector);
 assert.equal(row.result,'pass');assert.equal(row.executed,true);
 assert.equal(row.case_count,wf.case_count-1,'retained protocol covers every non-descriptor standalone case');
 assert.equal(retained.outcome.tested_case_count,row.case_count);
 assert.deepEqual(report.checks.filter((c:any)=>c.result==='not_evaluable').map((c:any)=>c.id).sort(),['exact-output-currentness','safe-output-separate-from-planning']);
  assert.equal(report.result, 'incomplete');
  t.diagnostic(JSON.stringify({workflow_cases: wf.case_count, checks: report.checks.length}));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
