import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {publicFixture, publicSelection} from '../helpers/composition-project.ts';
import {createCompositionControls, assertCompositionControls, COMPOSITION_CONTROLS_DEFINITION_SHA256} from '../../src/verification/reconciled-composition-controls.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {sha256} from '../../src/input/source-manifest.ts';
import {compileDeclarativeFunction} from '../../src/typed-backend/declarative-function.ts';
import {executeCompositionControls} from '../../src/verification/reconciled-composition-execution.ts';
const project = path.resolve(import.meta.dirname, '../../../..'), cli = path.join(project, 'impl/cli'), base = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const definitions = Object.fromEntries(['binding', 'reference', 'cases', 'effects', 'controls'].map(key => [key, fs.readFileSync(path.join(base, key === 'effects' ? 'semantic-composition-effect-audit-contract.json' : 'semantic-composition-' + key + '-contract.json'), 'utf8')])) as any;
function native(t: any, noCalculations = false) {
  const f = publicFixture(t), require = createRequire(import.meta.url), types = require.resolve('@types/node/package.json', {paths: process.execArgv.filter(a => a.endsWith('loader.mjs')).map(p => path.dirname(p))}), deps = path.dirname(path.dirname(path.dirname(types)));
  if (noCalculations) {
    const source = structuredClone(f.composition), c = source.contract; c.calculations = {}; delete source.core_bindings.Net; delete source.core_bindings.Other;
    c.nodes.find((n: any) => n.id === 'Emit').fields = {net: {op: 'call', name: 'text', args: [{op: 'path', path: ['Parsed', 'qty']}]}, other: {op: 'call', name: 'text', args: [{op: 'path', path: ['Parsed', 'rebate']}]}};
    source.source_text = JSON.stringify(c, null, 2) + '\n'; const hash = sha256(source.source_text); source.ontology.source.sha256 = hash; source.ontology.composition_trace = compileDeclarativeFunction(c).trace as any;
    source.ontology.nodes = source.ontology.nodes.filter((n: any) => !['Net', 'Other'].includes(n.name));
    for (const n of source.ontology.nodes) {n.source.sha256 = hash; if (n.name === 'Emit') n.typed_contract = c.nodes.find((n: any) => n.id === 'Emit');}
    source.ontology.references = source.ontology.references.filter((r: any) => !['TEST-ALPHA', 'TEST-BETA'].includes(r.source) && !['TEST-ALPHA', 'TEST-BETA'].includes(r.target)); source.ontology.references.forEach((r: any) => {r.evidence.sha256 = hash;}); f.write('compositions/calculate.json', source);
  }
  const dist = path.join(f.root, 'dist'); fs.mkdirSync(dist); fs.writeFileSync(path.join(f.root, 'package.json'), '{"type":"module"}');
  const image = nativeToolchainImage(); assert.equal(image, NATIVE_TEST_IMAGE_ID);
  const docker = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(), '--mount', 'type=bind,source=' + project + ',target=' + project + ',readonly', '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly', '--mount', 'type=bind,source=' + f.root + ',target=' + f.root, '--workdir', f.root, image];
  const command = (args: string[]) => {try {return execFileSync('docker', [...docker, ...args], {encoding: 'utf8', timeout: 240000, maxBuffer: 33554432});} catch (e: any) {throw Error([e.message, e.stdout, e.stderr].filter(Boolean).join('\n'));}};
  command(['tsc', '--ignoreConfig', '--strict', '--skipLibCheck', '--types', 'node', '--typeRoots', path.join(deps, '@types'), '--target', 'ES2022', '--module', 'NodeNext', '--rootDir', path.join(cli, 'src'), '--outDir', dist, path.join(cli, 'src/verification/reconciled-composition-execution.ts')]);
  const client = path.join(f.root, 'client.mjs');
  const prefix = `import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {createHash} from 'node:crypto';
import {loadCompiledProjectGraph} from './dist/input/project-model.js';import {planCompiledReconciledProject} from './dist/generation/reconciled-project.js';
import {createCompositionControls,assertCompositionControls} from './dist/verification/reconciled-composition-controls.js';
import {executeCompositionControls,assertCompositionExecutionCurrent} from './dist/verification/reconciled-composition-execution.js';
const hash=v=>createHash('sha256').update(v).digest('hex'),graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(publicSelection())}),definitions=${JSON.stringify(definitions)},control=createCompositionControls(graph,plan,'calculate',definitions);
const options={workspace_parent:${JSON.stringify(f.root)},typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:${JSON.stringify(path.join(deps, '@types'))}};
`;
  return {...f, run: (body: string) => {fs.writeFileSync(client, prefix + body); return JSON.parse(command(['node', client]));}};
}

test('control identity is registered, immutable, definition-pinned and source-owned', t => {
  const f = publicFixture(t), plan = planCompiledReconciledProject(f.graph, publicSelection()), control = createCompositionControls(f.graph, plan, 'calculate', definitions);
  assertCompositionControls(control); assert.ok(Object.isFrozen(control.sources)); assert.ok(Object.isFrozen(control.family.cases)); assert.equal(sha256(definitions.controls), COMPOSITION_CONTROLS_DEFINITION_SHA256);
  assert.throws(() => assertCompositionControls(structuredClone(control)), /registered/); assert.throws(() => createCompositionControls(f.graph, plan, 'calculate', {...definitions, controls: definitions.controls + '\n'}), /definition drift/);
  assert.throws(() => createCompositionControls(structuredClone(f.graph), plan, 'calculate', definitions), /unvalidated or changed/);
  assert.equal(control.sources.length, 6); assert.ok(control.sources.every(s => !s.relative_path.endsWith('server.mjs')));
  let reads = 0; const options: any = {typescript_root: '/tmp', node_type_root: '/tmp'}; Object.defineProperty(options, 'workspace_parent', {enumerable: true, get() {reads++; return '/tmp';}});
  assert.throws(() => executeCompositionControls(control, options), /closed data tool options/); assert.equal(reads, 0);
});

test('no-Calculation composition executes only its behavior and inert adapter', t => {
  const f = native(t, true), result = f.run(String.raw`
const result=executeCompositionControls(control,options);assertCompositionExecutionCurrent(result);assert.equal(result.modules.length,2);assert.ok(control.family.binding.bridges.every(b=>b.role==='structural-record'));
console.log(JSON.stringify({cases:result.cases,modules:result.modules.length}));
`);
  assert.equal(result.modules, 2); assert.ok(result.cases > 0); t.diagnostic(JSON.stringify(result));
});

test('private execution performs real audits, restricted behavior and retained-currentness validation', t => {
  const f = native(t), result = f.run(String.raw`
const result=executeCompositionControls(control,options);assertCompositionExecutionCurrent(result);
assert.equal(result.result,'pass');assert.equal(result.cases,control.family.cases.length);assert.equal(Object.keys(result.audits).length,2);
assert.throws(()=>assertCompositionExecutionCurrent(structuredClone(result)),/registered/);
const input=JSON.parse(fs.readFileSync(path.join(result.workspace,'cases.json')));assert.ok(input.cases.every(c=>!Object.hasOwn(c,'expected')));
const output=JSON.parse(fs.readFileSync(path.join(result.workspace,'observations.json')));assert.ok(output.cases.every(c=>c.input_changed===false));
assert.equal(output.cases.length,result.cases);
const file=path.join(result.workspace,'observations.json'),before=fs.readFileSync(file);fs.writeFileSync(file,Buffer.concat([before,Buffer.from('\n')]));assert.throws(()=>assertCompositionExecutionCurrent(result),/artifact changed/);fs.writeFileSync(file,before);assertCompositionExecutionCurrent(result);
const extra=path.join(result.workspace,'extra.txt');fs.writeFileSync(extra,'late');assert.throws(()=>assertCompositionExecutionCurrent(result),/unexpected/);fs.unlinkSync(extra);assertCompositionExecutionCurrent(result);
const runner=path.join(result.workspace,'runner.mjs'),saved=fs.readFileSync(runner);fs.unlinkSync(runner);fs.symlinkSync(file,runner);assert.throws(()=>assertCompositionExecutionCurrent(result),/symbolic/);fs.unlinkSync(runner);fs.writeFileSync(runner,saved);assertCompositionExecutionCurrent(result);
console.log(JSON.stringify({cases:result.cases,audits:2,currentness_mutations:3,files:Object.keys(result.files).length}));
`);
  assert.ok(result.cases > 100); assert.equal(result.currentness_mutations, 3); t.diagnostic(JSON.stringify(result));
});

test('executed compiling semantic mutations disagree while bound effect and import mutations reject', t => {
  const f = native(t), result = f.run(String.raw`
const receipt=executeCompositionControls(control,options),root=receipt.workspace,nativeRoot=path.join(root,'native'),runner=path.join(root,'runner.mjs'),inputFile=path.join(root,'cases.json');
const originalInput=fs.readFileSync(inputFile,'utf8'),expected=JSON.parse(fs.readFileSync(path.join(root,'observations.json'),'utf8'));
const provider=control.sources.find(s=>s.relative_path.includes('/alpha/')&&s.relative_path.endsWith('.provider.ts'));
assert.ok(provider);const sourceFile=path.join(root,'source',provider.relative_path),nativePath=provider.relative_path.replace(/\.ts$/,'.js'),originalSource=fs.readFileSync(sourceFile,'utf8'),nativeFile=path.join(nativeRoot,nativePath),originalNative=fs.readFileSync(nativeFile,'utf8');
const auditInput=path.join(root,'effects-native.json'),auditConfig=path.join(root,'native-audit.json'),auditScript=path.join(root,'effects.mjs');
const audit=()=>JSON.parse(cp.execFileSync(process.execPath,[auditScript,options.typescript_root,auditConfig,auditInput],{encoding:'utf8',timeout:60000}));
const run=()=>{const input=JSON.parse(originalInput);input.modules=input.modules.map(m=>({...m,sha256:hash(fs.readFileSync(path.join(nativeRoot,m.relative_path)))}));const text=JSON.stringify(input);fs.writeFileSync(inputFile,text);return JSON.parse(cp.execFileSync(process.execPath,['--permission','--allow-fs-read='+root,'--disable-proto=throw','--max-old-space-size=256',runner,inputFile,nativeRoot,control.runner_sha256,hash(text)],{encoding:'utf8',timeout:60000,maxBuffer:33554432}));};
const changed=originalSource.replace(/checked\(([^()]+)-([^()]+)\)/,'checked($1+$2)');assert.notEqual(changed,originalSource);fs.writeFileSync(sourceFile,changed);
cp.execFileSync(process.execPath,[path.join(options.typescript_root,'bin/tsc'),'--project',path.join(root,'compiler.json'),'--pretty','false'],{encoding:'utf8',timeout:60000});
assert.ok(audit().modules.every(m=>m.violations.length===0));const mutant=run();assert.ok(mutant.cases.some((c,i)=>JSON.stringify(c)!==JSON.stringify(expected.cases[i])));assert.throws(()=>assertCompositionExecutionCurrent(receipt),/changed/);
fs.writeFileSync(sourceFile,originalSource);fs.writeFileSync(nativeFile,originalNative);fs.writeFileSync(inputFile,originalInput);
const behavior=path.join(nativeRoot,control.family.binding.behavior_path),originalBehavior=fs.readFileSync(behavior,'utf8');
const mutation=originalBehavior.replace('const n=BigInt(value);','const n=BigInt(Number(value));');assert.notEqual(mutation,originalBehavior);fs.writeFileSync(behavior,mutation);assert.ok(audit().modules.every(m=>m.violations.length===0));assert.ok(run().cases.some((c,i)=>JSON.stringify(c)!==JSON.stringify(expected.cases[i])));
fs.writeFileSync(behavior,originalBehavior+'\nprocess.cwd();\n');assert.ok(audit().modules.some(m=>m.violations.length));
fs.writeFileSync(behavior,"import fs from 'node:fs';\n"+originalBehavior);assert.ok(audit().modules.some(m=>m.violations.length));
console.log(JSON.stringify({executed_semantic_mutants:2,rejected_effect_or_import_mutants:2}));
`);
  assert.equal(result.executed_semantic_mutants, 2); t.diagnostic(JSON.stringify(result));
});

test('runner rejects drift, malformed complete inputs and target mutations without returning a prefix', t => {
  const f = native(t), result = f.run(String.raw`
const receipt=executeCompositionControls(control,options),root=receipt.workspace,inputFile=path.join(root,'cases.json'),runner=path.join(root,'runner.mjs'),nativeRoot=path.join(root,'native'),text=fs.readFileSync(inputFile,'utf8'),input=JSON.parse(text);
const run=(inputHash=hash(fs.readFileSync(inputFile)),runnerHash=control.runner_sha256)=>cp.spawnSync(process.execPath,['--permission','--allow-fs-read='+root,'--disable-proto=throw','--max-old-space-size=256',runner,inputFile,nativeRoot,runnerHash,inputHash],{encoding:'utf8',timeout:60000,maxBuffer:33554432,env:{LANG:'C',TZ:'UTC'}});
let count=0;const rejects=(r)=>{assert.notEqual(r.status,0);assert.equal(r.stdout,'');count++;};
rejects(run('0'.repeat(64)));rejects(run(hash(text),'0'.repeat(64)));
for(const mutate of [v=>v.cases.push(v.cases[0]),v=>v.cases[0].input=['number','01'],v=>v.modules[0].relative_path='../escape.js',v=>v.modules[0].sha256='0'.repeat(64),v=>v.cases[0].expected='forged',v=>v.cases=Array.from({length:4096},(_,i)=>({...v.cases[0],id:String(i)}))]){const v=structuredClone(input);mutate(v);fs.writeFileSync(inputFile,JSON.stringify(v));rejects(run());}fs.writeFileSync(inputFile,text);
const behavior=path.join(nativeRoot,input.behavior_path),original=fs.readFileSync(behavior,'utf8');const changed=original.replace('export function execute(', 'export function execute(').replace(/(export function execute\([^)]*\)\s*\{)/,'$1 arguments[0].input.qty="mutated";');assert.notEqual(changed,original);fs.writeFileSync(behavior,changed);const v=structuredClone(input);v.modules.find(m=>m.relative_path===input.behavior_path).sha256=hash(changed);fs.writeFileSync(inputFile,JSON.stringify(v));rejects(run());
console.log(JSON.stringify({whole_runner_rejections:count}));
`);
  assert.equal(result.whole_runner_rejections, 9);
});

test('late changes during execution cannot produce a passing receipt and restricted process cannot write or spawn', t => {
  const f = native(t), result = f.run(String.raw`
const original=fs.writeFileSync;let injected=false;
fs.writeFileSync=function(file,...args){const out=original.call(fs,file,...args);if(String(file).endsWith('/observations.json')){original.call(fs,path.join(path.dirname(String(file)),'late.txt'),'changed');injected=true;}return out;};
try{assert.throws(()=>executeCompositionControls(control,options),e=>e.phase==='final-currentness'&&/unexpected/.test(e.message));assert.ok(injected);}finally{fs.writeFileSync=original;}
const probe=path.join(options.workspace_parent,'permission.mjs');fs.writeFileSync(probe,"import fs from 'node:fs';import cp from 'node:child_process';let denied=0;try{fs.writeFileSync('should-not-exist','x')}catch(e){if(e.code==='ERR_ACCESS_DENIED')denied++}try{cp.spawnSync(process.execPath,['-e','0'])}catch(e){if(e.code==='ERR_ACCESS_DENIED')denied++}process.stdout.write(String(denied));");
assert.equal(cp.execFileSync(process.execPath,['--permission','--allow-fs-read='+probe,'--disable-proto=throw',probe],{encoding:'utf8',env:{LANG:'C',TZ:'UTC'}}),'2');
console.log(JSON.stringify({late_currentness:1,permission_denials:2}));
`);
  assert.equal(result.permission_denials, 2);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
