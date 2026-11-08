import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {policyFixture} from '../helpers/cross-generator-policy.ts';
import {executeCrossGeneratorPolicy} from '../../src/verification/reconciled-cross-generator-execution.ts';
const project = path.resolve(import.meta.dirname, '../../../..'), cli = path.join(project, 'impl/cli'), base = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const definitions = Object.fromEntries(['cross-generator-policy', 'cross-generator-verification', 'cross-generator-execution'].map(k => [k, fs.readFileSync(path.join(base, k + '-contract.json'), 'utf8')]));

function native(t: any, moduleRoot = 'domain') {
  const f = policyFixture(t, moduleRoot), require = createRequire(import.meta.url), types = require.resolve('@types/node/package.json', {paths: process.execArgv.filter(a => a.endsWith('loader.mjs')).map(p => path.dirname(p))}), deps = path.dirname(path.dirname(path.dirname(types)));
  const dist = path.join(f.root, 'dist'); fs.mkdirSync(dist); fs.writeFileSync(path.join(f.root, 'package.json'), '{"type":"module"}');
  const image = nativeToolchainImage();
  assert.equal(image, NATIVE_TEST_IMAGE_ID);
  const docker = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(), '--mount', 'type=bind,source=' + project + ',target=' + project + ',readonly', '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly', '--mount', 'type=bind,source=' + f.root + ',target=' + f.root, '--workdir', f.root, image];
  const command = (args: string[]) => {try {return execFileSync('docker', [...docker, ...args], {encoding: 'utf8', timeout: 240000, maxBuffer: 33554432});} catch (e: any) {throw Error([e.message, e.stdout, e.stderr].filter(Boolean).join('\n'));}};
  command(['tsc', '--ignoreConfig', '--strict', '--skipLibCheck', '--types', 'node', '--typeRoots', path.join(deps, '@types'), '--target', 'ES2022', '--module', 'NodeNext', '--rootDir', path.join(cli, 'src'), '--outDir', dist, path.join(cli, 'src/verification/reconciled-cross-generator-execution.ts')]);
  const client = path.join(f.root, 'client.mjs');
  const prefix = `import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
import {loadCompiledProjectGraph} from './dist/input/project-model.js';import {planCompiledReconciledProject} from './dist/generation/reconciled-project.js';
import {createCrossGeneratorBoundary} from './dist/verification/reconciled-cross-generator-boundary.js';
import {createCrossGeneratorPolicyControls} from './dist/verification/reconciled-cross-generator-policy.js';
import {executeCrossGeneratorPolicy,assertCrossGeneratorExecutionCurrent} from './dist/verification/reconciled-cross-generator-execution.js';
const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),selection=${JSON.stringify(f.selection)},plan=planCompiledReconciledProject(graph,selection),definitions=${JSON.stringify(definitions)};
const boundary=createCrossGeneratorBoundary(graph,plan,definitions['cross-generator-verification']),controls=createCrossGeneratorPolicyControls(graph,plan,boundary,definitions['cross-generator-policy']),definition=definitions['cross-generator-execution'];
const options={workspace_parent:${JSON.stringify(f.root)},typescript_root:'/opt/node-toolchain/node_modules/typescript'};
`;
  return {...f, run: (body: string) => {fs.writeFileSync(client, prefix + body); return JSON.parse(command(['node', client]));}};
}

test('private executor rejects unregistered inputs, foreign plans, changed definition and active options before writing', t => {
  const f = policyFixture(t), other = policyFixture(t, 'other/root'), definition = definitions['cross-generator-execution']!;
  const options = {workspace_parent: f.root, typescript_root: '/not-installed'};
  assert.throws(() => executeCrossGeneratorPolicy(structuredClone(f.plan), f.controls, definition, options), /registered/);
  assert.throws(() => executeCrossGeneratorPolicy(f.plan, structuredClone(f.controls), definition, options), /registered/);
  assert.throws(() => executeCrossGeneratorPolicy(other.plan, f.controls, definition, options), /foreign plan/);
  assert.throws(() => executeCrossGeneratorPolicy(f.plan, f.controls, definition + ' ', options), /definition drift/);
  let reads = 0; const active: any = {typescript_root: '/tmp'}; Object.defineProperty(active, 'workspace_parent', {enumerable: true, get() {reads++; return f.root;}});
  assert.throws(() => executeCrossGeneratorPolicy(f.plan, f.controls, definition, active), /closed data tool options/); assert.equal(reads, 0);
  assert.equal(fs.readdirSync(f.root).some(p => p.startsWith('ds-cross-generator-run-')), false);
});

test('actual source/native audits and Rule traces pass in both roots with complete retained custody', t => {
  for (const moduleRoot of ['domain', 'application/domain']) {
    const f = native(t, moduleRoot), result = f.run(String.raw`
const r=executeCrossGeneratorPolicy(plan,controls,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.outcome.tested_policy_count,4);assert.equal(r.outcome.tested_case_count,746);assert.equal(r.outcome.tested_call_count,1372);
assert.deepEqual(r.outcome.remaining.map(x=>x.selector),['alpha:constant']);assert.equal(r.outcome.public_cross_generator_behavior,'not_evaluable');assert.ok(r.outcome.uncovered_runtime_edge_count>0);
assert.ok(Object.isFrozen(r.native_modules));assert.equal(Object.keys(r.audits).length,2);
assert.throws(()=>assertCrossGeneratorExecutionCurrent(structuredClone(r)),/registered/);
const cases=JSON.parse(fs.readFileSync(path.join(r.workspace,'cases.json')));assert.ok(cases.rows.every(x=>x.cases.every(c=>!Object.hasOwn(c,'expected'))));
assert.ok(r.native_modules.every(m=>/\/(policies|rules)\//.test(m.relative_path)));
let changes=0;
for(const relative of ['cases.json','runner.mjs','observations.json','source-audit-observation.json','source/'+controls.rows.find(x=>x.state==='ready').relative_path,'native/'+r.native_modules[0].relative_path]){
 const p=path.join(r.workspace,relative),before=fs.readFileSync(p);fs.appendFileSync(p,'\n');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);fs.writeFileSync(p,before);assertCrossGeneratorExecutionCurrent(r);changes++;
}
const extra=path.join(r.workspace,'extra');fs.mkdirSync(extra);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/unexpected/);fs.rmdirSync(extra);
const p=path.join(r.workspace,'runner.mjs'),before=fs.readFileSync(p);fs.unlinkSync(p);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);
fs.symlinkSync(path.join(r.workspace,'cases.json'),p);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/nonsymbolic|symbolic/);fs.unlinkSync(p);fs.writeFileSync(p,before);assertCrossGeneratorExecutionCurrent(r);
console.log(JSON.stringify({module_root:selection.module_root,...r.outcome,modules:r.native_modules.length,audits:2,custody_mutations:changes+3}));
`);
    assert.equal(result.custody_mutations, 9); t.diagnostic(JSON.stringify(result));
  }
});

test('captured source stays authoritative and an all-unavailable family cannot produce a passing run', t => {
  const f = native(t), result = f.run(String.raw`
// The source root is test-owned; selection and controls were captured before these edits.
const sourceFile=__SOURCE_FILE__;
const original=fs.readFileSync(sourceFile);fs.writeFileSync(sourceFile,'changed authoring bytes after snapshot');
const receipt=executeCrossGeneratorPolicy(plan,controls,definition,options);assertCrossGeneratorExecutionCurrent(receipt);fs.writeFileSync(sourceFile,original);
for(const row of controls.rows){const file=path.join(path.dirname(sourceFile),row.selector.split(':')[1]+'.json'),node=JSON.parse(fs.readFileSync(file));node.body.typed_contract.inputs=[{name:'total',type:{kind:'scalar',name:'UInt64'}}];node.body.typed_contract.cases=[{target:'alpha:compute',rule:{selector:'alpha:high',arguments:[{parameter:'amount',value:{op:'literal',type:'UInt64',value:'101'}}]}}];fs.writeFileSync(file,JSON.stringify(node));}
const nextGraph=loadCompiledProjectGraph(path.resolve(path.dirname(sourceFile),'../../..')),nextPlan=planCompiledReconciledProject(nextGraph,selection),nextBoundary=createCrossGeneratorBoundary(nextGraph,nextPlan,definitions['cross-generator-verification']),nextControls=createCrossGeneratorPolicyControls(nextGraph,nextPlan,nextBoundary,definitions['cross-generator-policy']);
assert.ok(nextControls.rows.every(r=>r.state==='not_evaluable'));
const before=fs.readdirSync(options.workspace_parent);assert.throws(()=>executeCrossGeneratorPolicy(nextPlan,nextControls,definition,options),/no ready interoperability families/);assert.deepEqual(fs.readdirSync(options.workspace_parent),before);
console.log(JSON.stringify({captured_source_custody:true,all_unavailable_rejected:true}));
`.replace('__SOURCE_FILE__', JSON.stringify(path.join(f.source, 'specs/alpha/nodes/choose.json'))));
  assert.equal(result.all_unavailable_rejected, true);
});

test('independent AST audits reject unexpected source and CommonJS bindings before native behavior', t => {
  const f = native(t), result = f.run(String.raw`
const r=executeCrossGeneratorPolicy(plan,controls,definition,options),root=r.workspace;
let rejected=0;
for(const stage of ['source','native']){
 const extension=stage==='source'?'.ts':'.js',relative=controls.rows.find(x=>x.selector==='alpha:choose').relative_path.replace(/\.ts$/,extension);
 const file=path.join(root,stage,relative),original=fs.readFileSync(file,'utf8');
 const audit=()=>JSON.parse(cp.execFileSync(process.execPath,[path.join(root,'audit.mjs'),options.typescript_root,path.join(root,stage+'-audit-config.json'),path.join(root,stage+'-audit-input.json')],{encoding:'utf8',timeout:60000}));
 assert.ok(audit().modules.every(m=>m.violations.length===0));
 const mutations=stage==='source'?[
  s=>'import {readFileSync} from "node:fs";\n'+s,
  s=>s+'\nexport const extra = 1;',
  s=>s+'\nconst dynamic = () => import("node:fs");',
  s=>s+'\nconst ambient = () => process.cwd();'
 ]:[
  s=>'const foreign=require("node:fs");\n'+s,
  s=>s+'\nexports.extra=1;',
  s=>s+'\nconst alias=require; alias("node:fs");',
  s=>s+'\nfunction nested(){return require("node:fs");}',
  s=>s.replace('exports.policyChoose = Object.freeze', 'exports.extra = Object.freeze'),
  s=>s+'\nmodule.exports={};',
  s=>s.replace('.select,', '["select"],'),
  s=>s+'\nprocess.cwd();'
 ];
 for(const mutate of mutations){const text=mutate(original);assert.notEqual(text,original);fs.writeFileSync(file,text);assert.ok(audit().modules.some(m=>m.violations.length>0));assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);rejected++;}
 fs.writeFileSync(file,original);assertCrossGeneratorExecutionCurrent(r);
}
console.log(JSON.stringify({independent_surface_mutants:rejected}));
`);
  assert.equal(result.independent_surface_mutants, 12); t.diagnostic(JSON.stringify(result));
});

test('complete compiler package custody detects library, platform executable and extra tool-file drift', t => {
  const f = native(t), result = f.run(String.raw`
const packageRoot=path.join(options.workspace_parent,'tool-copy','node_modules');fs.mkdirSync(packageRoot,{recursive:true});
fs.cpSync(options.typescript_root,path.join(packageRoot,'typescript'),{recursive:true});
fs.cpSync('/opt/node-toolchain/node_modules/@typescript',path.join(packageRoot,'@typescript'),{recursive:true});
options.typescript_root=path.join(packageRoot,'typescript');
const r=executeCrossGeneratorPolicy(plan,controls,definition,options);assertCrossGeneratorExecutionCurrent(r);
let mutations=0;
for(const p of [path.join(options.typescript_root,'lib/getExePath.js'),path.join(options.typescript_root,'dist/api/sync/api.js'),path.join(packageRoot,'@typescript/typescript-linux-x64/lib/tsc')]){
 const original=fs.readFileSync(p);fs.appendFileSync(p,'\n');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/toolchain changed/);fs.writeFileSync(p,original);assertCrossGeneratorExecutionCurrent(r);mutations++;
}
const extra=path.join(options.typescript_root,'extra');fs.writeFileSync(extra,'x');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/toolchain changed/);fs.unlinkSync(extra);assertCrossGeneratorExecutionCurrent(r);
const originalSpawn=cp.spawnSync,tool=path.join(options.typescript_root,'lib/getExePath.js'),before=fs.readFileSync(tool);let injected=false;
cp.spawnSync=function(exe,args,...rest){const out=originalSpawn.call(cp,exe,args,...rest);if(args[0]===path.join(options.typescript_root,'bin/tsc')){fs.appendFileSync(tool,'\n');injected=true;}return out;};syncBuiltinESMExports();
try{assert.throws(()=>executeCrossGeneratorPolicy(plan,controls,definition,options),/toolchain changed/);assert.ok(injected);}finally{cp.spawnSync=originalSpawn;syncBuiltinESMExports();fs.writeFileSync(tool,before);}
assertCrossGeneratorExecutionCurrent(r);
console.log(JSON.stringify({tool_mutations:mutations+1,in_flight_tool_rejections:1,compiler_files:Object.keys(r.tool_files.typescript).length,platform_files:Object.keys(r.tool_files.platform).length}));
`);
  assert.equal(result.tool_mutations, 4); t.diagnostic(JSON.stringify(result));
});

test('in-flight source, native and final artifact mutations reject and private runner cannot write or spawn', t => {
  const f = native(t), result = f.run(String.raw`
let rejected=0;
for(const trigger of ['source-audit-input.json','native-audit-input.json','observations.json']){
 const original=fs.writeFileSync;let injected=false;
 fs.writeFileSync=function(file,...args){const out=original.call(fs,file,...args);if(String(file).endsWith('/'+trigger)){original.call(fs,path.join(path.dirname(String(file)),'unexpected'),'changed');injected=true;}return out;};
 try{assert.throws(()=>executeCrossGeneratorPolicy(plan,controls,definition,options),e=>/artifact changed or unexpected/.test(e.message));assert.ok(injected);rejected++;}finally{fs.writeFileSync=original;}
}
const p=path.join(options.workspace_parent,'permission.mjs');fs.writeFileSync(p,"import fs from 'node:fs';import cp from 'node:child_process';let n=0;try{fs.writeFileSync('must-not-exist','x')}catch(e){if(e.code==='ERR_ACCESS_DENIED')n++}try{cp.spawnSync(process.execPath,['-e','0'])}catch(e){if(e.code==='ERR_ACCESS_DENIED')n++}process.stdout.write(String(n));");
assert.equal(cp.execFileSync(process.execPath,['--permission','--allow-fs-read='+p,'--disable-proto=throw',p],{encoding:'utf8',env:{LANG:'C',TZ:'UTC'}}),'2');
const originalSpawn=cp.spawnSync;let changed=false;
cp.spawnSync=function(exe,args,...rest){const out=originalSpawn.call(cp,exe,args,...rest);if(args.includes('--permission')){const observation=JSON.parse(out.stdout);observation.rows.pop();out.stdout=JSON.stringify(observation);changed=true;}return out;};syncBuiltinESMExports();
try{assert.throws(()=>executeCrossGeneratorPolicy(plan,controls,definition,options),/native observation mismatch/);assert.ok(changed);}finally{cp.spawnSync=originalSpawn;syncBuiltinESMExports();}
console.log(JSON.stringify({in_flight_rejections:rejected,observation_prefix_rejections:1,permission_denials:2}));
`);
  assert.equal(result.in_flight_rejections, 3); t.diagnostic(JSON.stringify(result));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
