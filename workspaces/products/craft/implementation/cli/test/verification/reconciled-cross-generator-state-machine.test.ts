import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {stateMachineFixture} from '../helpers/state-machine-project.ts';
import {executeCrossGeneratorStateMachine, executeCrossGeneratorPolicy} from '../../src/verification/reconciled-cross-generator-execution.ts';
const project = path.resolve(import.meta.dirname, '../../../..'), cli = path.join(project, 'impl/cli'), base = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const definitions = Object.fromEntries(['cross-generator-state-machine', 'cross-generator-verification', 'cross-generator-execution'].map(k => [k, fs.readFileSync(path.join(base, k + '-contract.json'), 'utf8')]));

function native(t: any, moduleRoot = 'domain', prepare: (f: any) => void = () => {}) {
  const f = stateMachineFixture(t, moduleRoot), require = createRequire(import.meta.url), types = require.resolve('@types/node/package.json', {paths: process.execArgv.filter(a => a.endsWith('loader.mjs')).map(p => path.dirname(p))}), deps = path.dirname(path.dirname(path.dirname(types)));
  prepare(f); f.save();
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
import {createCrossGeneratorStateMachineControls} from './dist/verification/reconciled-cross-generator-state-machine.js';
import {executeCrossGeneratorStateMachine,assertCrossGeneratorExecutionCurrent} from './dist/verification/reconciled-cross-generator-execution.js';
const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),selection=${JSON.stringify(f.selection)},plan=planCompiledReconciledProject(graph,selection),definitions=${JSON.stringify(definitions)};
const boundary=createCrossGeneratorBoundary(graph,plan,definitions['cross-generator-verification']),controls=createCrossGeneratorStateMachineControls(graph,plan,boundary,definitions['cross-generator-state-machine']),definition=definitions['cross-generator-state-machine'];
const options={workspace_parent:${JSON.stringify(f.root)},typescript_root:'/opt/node-toolchain/node_modules/typescript'};
`;
  return {...f, run: (body: string) => {fs.writeFileSync(client, prefix + body); return JSON.parse(command(['node', client]));}};
}

import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorStateMachineControls, crossGeneratorStateMachineProbe, checkCrossGeneratorStateMachineObservations} from '../../src/verification/reconciled-cross-generator-state-machine.ts';
import {createStateMachineControls} from '../../src/verification/reconciled-state-machine-controls.ts';
const definition = definitions['cross-generator-state-machine']!;
function control(f: ReturnType<typeof stateMachineFixture>) {
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection),boundary=createCrossGeneratorBoundary(graph,plan,definitions['cross-generator-verification']!);
 return {graph,plan,boundary,c:createCrossGeneratorStateMachineControls(graph,plan,boundary,definition)};
}

test('a State Machine callee reached by another guard cannot cover its unvisited nested caller edge',t=>{
 const f=stateMachineFixture(t),file=path.join(f.source,'specs/alpha/nodes/forward.json'),raw=JSON.parse(fs.readFileSync(file,'utf8'));
 const allowed=JSON.parse(fs.readFileSync(path.join(f.source,'specs/alpha/nodes/allowed.json'),'utf8'));
 raw.body.typed_contract.expression={op:'all',terms:[allowed.body.typed_contract.expression,{op:'any',terms:[
  {op:'eq',left:{op:'literal',type:'Bool',value:true},right:{op:'literal',type:'Bool',value:true}},raw.body.typed_contract.expression,
 ]}]};fs.writeFileSync(file,JSON.stringify(raw));
 const selected=path.join(f.source,'specs/alpha/nodes/lifecycle.json'),state=JSON.parse(fs.readFileSync(selected,'utf8'));
 state.body.typed_contract.transitions[1].guard={selector:'alpha:allowed',arguments:state.body.typed_contract.transitions[0].guard.arguments};fs.writeFileSync(selected,JSON.stringify(state));
 const {c}=control(f),row=c.rows.find(r=>r.selector==='alpha:lifecycle')!;
 assert.equal(row.state,'not_evaluable');if(row.state==='not_evaluable')assert.match(row.reason,/unvisited.*edge/);
 assert.equal(crossGeneratorStateMachineProbe(c).rows.some(r=>r.selector==='alpha:lifecycle'),false);
 assert.equal(c.coverage.some(e=>e.state_machine_selectors.includes('alpha:lifecycle')),false);
});


test('source guard traces preserve standalone outcomes and keep initial, invalid and no-transition calls empty', t => {
 const f=stateMachineFixture(t),{graph,plan,boundary,c}=control(f),row=c.rows.find(r=>r.selector==='alpha:lifecycle')!;
 if(row.state!=='ready')throw Error(row.reason);assert.equal(row.state,'ready');
 const previous=createStateMachineControls(graph.nodes.find(n=>n.selector===row.selector)!,graph,plan);if(previous.state!=='ready')throw Error(previous.reason);assert.equal(previous.state,'ready');
 assert.deepEqual(row.cases.map(({expected,...input})=>({...input,expected:expected.outcome})),previous.cases);
 assert.equal(row.declared_pair_count,6);assert.equal(row.cases.length,647);
 assert.ok(row.rule_edge_visits.length>0);assert.ok(row.rule_edge_visits.every(e=>e.calls>0));
 assert.equal(row.rule_edge_visits.reduce((n,e)=>n+e.calls,0),row.cases.reduce((n,c)=>n+c.expected.calls.length,0));
 assert.deepEqual(row.rule_edge_visits.map(e=>e.edge_sha256),boundary.edges.filter(e=>!e.type_only&&(
  e.importer_path===row.relative_path.replace(/\.ts$/,'.provider.ts')||row.rules.some(r=>r.relative_path===e.importer_path)
 )).map(e=>e.edge_sha256));
 assert.ok(row.cases.some(c=>c.expected.calls.length===2&&c.expected.calls[1].parent===0));
 for(const c of row.cases)if(c.mode==='initial-state'||c.expected.outcome.kind==='error'||c.expected.outcome.kind==='value'&&c.expected.outcome.value.includes('no-transition'))assert.deepEqual(c.expected.calls,[]);
 assert.ok(c.rows.some(r=>r.state==='not_evaluable'&&r.selector==='alpha:guardless'));
 assert.deepEqual(c.coverage.map(e=>e.edge_sha256),boundary.edges.map(e=>e.edge_sha256));
 assert.ok(c.coverage.some(e=>e.status==='non-runtime'));assert.ok(c.coverage.some(e=>e.status==='not_evaluable'));
 const probe=crossGeneratorStateMachineProbe(c);assert.equal(probe.rows.length,1);assert.ok(probe.rows[0].cases.every(c=>!Object.hasOwn(c,'expected')));
 assert.equal('rule_edge_visits' in probe.rows[0],false);
 assert.throws(()=>crossGeneratorStateMachineProbe(structuredClone(c)),/registered/);
 assert.throws(()=>createCrossGeneratorStateMachineControls(graph,plan,structuredClone(boundary),definition),/registered/);
 assert.throws(()=>createCrossGeneratorStateMachineControls(graph,plan,boundary,definition+' '),/definition drift/);
 const other=control(stateMachineFixture(t,'other/domain'));assert.throws(()=>createCrossGeneratorStateMachineControls(graph,plan,other.boundary,definition),/foreign boundary/);
 assert.deepEqual(row.cases,other.c.rows.find(r=>r.selector===row.selector)?.state==='ready'?(other.c.rows.find(r=>r.selector===row.selector) as any).cases:null);
 assert.throws(()=>executeCrossGeneratorPolicy(plan,c as any,definitions['cross-generator-execution']!,{workspace_parent:f.root,typescript_root:'/tmp'}),/registered/);
 assert.throws(()=>executeCrossGeneratorStateMachine(plan,structuredClone(c),definition,{workspace_parent:f.root,typescript_root:'/tmp'}),/registered/);
});

test('private native guard execution audits typed exports, initial forwarding and nested calls in both module roots', t => {
 for(const moduleRoot of ['domain','application/domain']){
  const f=native(t,moduleRoot),result=f.run(String.raw`
const r=executeCrossGeneratorStateMachine(plan,controls,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.outcome.tested_state_machine_count,1);assert.equal(r.outcome.tested_case_count,647);assert.equal(r.outcome.tested_call_count,152);assert.equal(r.native_modules.length,4);
assert.deepEqual(r.outcome.remaining.map(x=>x.selector),['alpha:guardless']);assert.equal(r.outcome.public_cross_generator_behavior,'not_evaluable');
assert.ok(r.native_modules.every(m=>/\/(state-machines|rules)\//.test(m.relative_path)));assert.throws(()=>assertCrossGeneratorExecutionCurrent(structuredClone(r)),/registered/);
const input=JSON.parse(fs.readFileSync(path.join(r.workspace,'cases.json')));assert.ok(input.rows.every(x=>x.cases.every(c=>!Object.hasOwn(c,'expected'))));
const nativeAudit=JSON.parse(fs.readFileSync(path.join(r.workspace,'native-audit-observation.json'))),sourceAudit=JSON.parse(fs.readFileSync(path.join(r.workspace,'source-audit-observation.json')));
assert.ok(nativeAudit.modules.every(m=>m.violations.length===0));assert.ok(sourceAudit.modules.some(m=>m.exports.includes('Outcome')));assert.ok(nativeAudit.modules.every(m=>!m.exports.includes('Outcome')));
const output=JSON.parse(fs.readFileSync(path.join(r.workspace,'observations.json')));assert.deepEqual(output.rows[0].cases[0].calls,[]);assert.equal(output.rows[0].cases[0].outcome.value,'draft');
const provider=path.join(r.workspace,'native',selection.module_root,'features/alpha/src/domain/state-machines/lifecycle.provider.js');const saved=fs.readFileSync(provider);fs.appendFileSync(provider,'\n');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);fs.writeFileSync(provider,saved);assertCrossGeneratorExecutionCurrent(r);
console.log(JSON.stringify({module_root:selection.module_root,...r.outcome,modules:r.native_modules.length,audits:2,retained_drift_rejected:true}));
`);assert.equal(result.tested_state_machine_count,1);t.diagnostic(JSON.stringify(result));
 }
});

test('missing guard sensitivity and capacity retain whole families without a passing prefix', t => {
 for(const mode of ['constant','capacity','unvisited']){
  const f=stateMachineFixture(t);
  if(mode==='constant')f.c.transitions[0].guard.arguments[0].value={op:'literal',type:'UInt64',value:'101'};
  if(mode==='capacity')f.c.inputs=Array.from({length:128},(_,i)=>({name:i===0?'amount':'field_'+i,type:{kind:'scalar',name:'UInt64'}}));
  if(mode==='unvisited'){
   f.node('shadowed','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-SHADOWED',parameters:[{name:'amount',type:{kind:'scalar',name:'UInt64'}}],expression:{op:'eq',left:{op:'path',root:'amount',properties:[]},right:{op:'path',root:'amount',properties:[]}}}});
   const file=path.join(f.source,'specs/alpha/nodes/forward.json'),node=JSON.parse(fs.readFileSync(file,'utf8'));
   node.body.typed_contract.expression={op:'any',terms:[{op:'eq',left:{op:'literal',type:'Bool',value:true},right:{op:'literal',type:'Bool',value:true}},{op:'rule_ref',selector:'alpha:shadowed',arguments:[{parameter:'amount',value:{op:'path',root:'amount',properties:[]}}]}]};fs.writeFileSync(file,JSON.stringify(node));
  }
  f.node('lifecycle','State Machine',{typed_contract:f.c});f.save();const {c}=control(f),row=c.rows.find(r=>r.selector==='alpha:lifecycle')!;
  assert.equal(row.state,'not_evaluable',mode);assert.equal('cases' in row,false);assert.equal(crossGeneratorStateMachineProbe(c).rows.length,0);
 }
});

test('native repeated guard calls and list-to-set, optional and sum facts retain exact source traces', t => {
 const f=native(t,'domain',f=>{
  const ruleFile=path.join(f.source,'specs/alpha/nodes/forward.json'),rule=JSON.parse(fs.readFileSync(ruleFile,'utf8'));rule.body.typed_contract.expression={op:'all',terms:[rule.body.typed_contract.expression,rule.body.typed_contract.expression]};fs.writeFileSync(ruleFile,JSON.stringify(rule));
  const scalar=(name:string)=>({kind:'scalar',name}),at=(root:string)=>({op:'path',root,properties:[]});
  f.node('contains','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-CONTAINS',parameters:[{name:'values',type:{kind:'set',element:scalar('String')}}],expression:{op:'contains',left:at('values'),right:{op:'literal',type:'String',value:'approved'}}}});
  const file=path.join(f.source,'specs/alpha/nodes/guardless.json'),raw=JSON.parse(fs.readFileSync(file,'utf8'));
  raw.body.typed_contract.inputs=[{name:'values',type:{kind:'list',element:scalar('String')}},{name:'note',type:{kind:'optional',element:scalar('String')}},{name:'choice',type:{kind:'sum',variants:[{name:'None',payload:null,ontology_variant:'TEST-CHOICE#None'},{name:'Amount',payload:scalar('UInt64'),ontology_variant:'TEST-CHOICE#Amount'}]}}];
  raw.body.typed_contract.transitions[0].guard={selector:'alpha:contains',arguments:[{parameter:'values',value:{op:'to_set',value:at('values')}}]};fs.writeFileSync(file,JSON.stringify(raw));
 });
 const result=f.run(String.raw`
const r=executeCrossGeneratorStateMachine(plan,controls,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.outcome.tested_state_machine_count,2);assert.deepEqual(r.outcome.remaining,[]);
const rows=JSON.parse(fs.readFileSync(path.join(r.workspace,'observations.json'))).rows;
assert.ok(rows.find(r=>r.selector==='alpha:lifecycle').cases.some(c=>c.calls.length===3&&c.calls[1].selector===c.calls[2].selector&&c.calls[1].parent===0&&c.calls[2].parent===0));
assert.ok(rows.find(r=>r.selector==='alpha:guardless').cases.some(c=>c.calls.length===1&&c.calls[0].selector==='alpha:contains'));
assert.ok(r.native_modules.every(m=>!m.relative_path.includes('/events/')));
console.log(JSON.stringify({...r.outcome,repeated_nested_calls_observed:true,structured_facts_observed:true}));
`);assert.equal(result.tested_state_machine_count,2);t.diagnostic(JSON.stringify(result));
});

test('strict-compiling predicate, argument, omitted, duplicate, eager and intent-order mutants cannot pass', t => {
 const f=native(t),result=f.run(String.raw`
const r=executeCrossGeneratorStateMachine(plan,controls,definition,options),root=r.workspace,provider=selection.module_root+'/features/alpha/src/domain/state-machines/lifecycle.provider.ts',rule=selection.module_root+'/features/alpha/src/domain/rules/allowed.ts';
const original=new Map([provider,rule].map(p=>[p,fs.readFileSync(path.join(root,'source',p),'utf8')]));
const compile=()=>cp.execFileSync(process.execPath,[path.join(options.typescript_root,'bin/tsc'),'--project',path.join(root,'compiler.json'),'--pretty','false'],{encoding:'utf8',timeout:60000});
const observe=()=>JSON.parse(cp.execFileSync(process.execPath,['--permission','--allow-fs-read='+root,'--disable-proto=throw',path.join(root,'runner.mjs'),path.join(root,'cases.json'),path.join(root,'native')],{encoding:'utf8',timeout:60000,maxBuffer:16777216}));
const {checkCrossGeneratorStateMachineObservations}=await import('./dist/verification/reconciled-cross-generator-state-machine.js');
const mutations=[
 ['predicate',rule,s=>s.replace('100n < p0','101n < p0')],
 ['argument',provider,s=>s.replace('["amount"]:p0','["amount"]:101n')],
 ['omitted',provider,s=>s.replace('if(!condition0({["amount"]:p0}))','void condition0; if(p0<=100n)')],
 ['duplicate',provider,s=>s.replace('if(!condition0(', 'condition0({["amount"]:p0}); if(!condition0(')],
 ['eager',provider,s=>s.replace('  checkData(parameters);','  condition0({["amount"]:101n});\n  checkData(parameters);')],
 ['intent-order',provider,s=>s.replaceAll('"primary"','"__swap__"').replaceAll('"audit"','"primary"').replaceAll('"__swap__"','"audit"')]
];
for(const [name,p,mutate]of mutations){for(const [file,text]of original)fs.writeFileSync(path.join(root,'source',file),text);const changed=mutate(original.get(p));assert.notEqual(changed,original.get(p),name);fs.writeFileSync(path.join(root,'source',p),changed);compile();
 const audit=JSON.parse(cp.execFileSync(process.execPath,[path.join(root,'audit.mjs'),options.typescript_root,path.join(root,'native-audit-config.json'),path.join(root,'native-audit-input.json')],{encoding:'utf8',timeout:60000}));assert.ok(audit.modules.every(m=>m.violations.length===0),name);
 assert.throws(()=>checkCrossGeneratorStateMachineObservations(controls,observe()),/native observation mismatch/,name);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);
}
for(const [file,text]of original)fs.writeFileSync(path.join(root,'source',file),text);compile();checkCrossGeneratorStateMachineObservations(controls,observe());assertCrossGeneratorExecutionCurrent(r);
console.log(JSON.stringify({strict_compiling_semantic_mutants:mutations.length}));
`);assert.equal(result.strict_compiling_semantic_mutants,6);t.diagnostic(JSON.stringify(result));
});

test('complete native observations reject missing, reordered, forged and active outcomes or traces', t => {
 const f=native(t),result=f.run(String.raw`
const r=executeCrossGeneratorStateMachine(plan,controls,definition,options),baseline=JSON.parse(fs.readFileSync(path.join(r.workspace,'observations.json')));
const {checkCrossGeneratorStateMachineObservations}=await import('./dist/verification/reconciled-cross-generator-state-machine.js');
const calls=v=>v.rows[0].cases.find(c=>c.calls.length===2).calls;
const mutations=[v=>v.rows.pop(),v=>v.rows.push(v.rows[0]),v=>v.rows[0].cases.pop(),v=>v.rows[0].cases.reverse(),v=>v.rows[0].cases.push(v.rows[0].cases[0]),v=>{v.controls_sha256='0'.repeat(64);},v=>{v.extra=true;},v=>calls(v).pop(),v=>calls(v).reverse(),v=>{calls(v)[1].parent=null;},v=>{calls(v)[0].input=['null'];},v=>{calls(v)[0].result=!calls(v)[0].result;},v=>{v.rows[0].cases[0].calls=[calls(v)[0]];},v=>{v.rows[0].cases[0].getter_reads=1;},v=>{v.rows[0].cases[0].input_changed=true;}];
for(const mutate of mutations){const v=structuredClone(baseline);mutate(v);assert.throws(()=>checkCrossGeneratorStateMachineObservations(controls,v),/native observation mismatch/);}
let reads=0;const active={};Object.defineProperty(active,'rows',{enumerable:true,get(){reads++;return baseline.rows;}});assert.throws(()=>checkCrossGeneratorStateMachineObservations(controls,active));assert.equal(reads,0);
assertCrossGeneratorExecutionCurrent(r);console.log(JSON.stringify({observation_rejections:mutations.length,output_getter_reads:reads}));
`);assert.equal(result.observation_rejections,15);t.diagnostic(JSON.stringify(result));
});

test('independent State Machine audit rejects type/runtime conflation, initial getter drift and Event imports', t => {
 const f=native(t),result=f.run(String.raw`
const r=executeCrossGeneratorStateMachine(plan,controls,definition,options),root=r.workspace,relative=selection.module_root+'/features/alpha/src/domain/state-machines/lifecycle';let rejected=0;
for(const stage of ['source','native']){
 const file=path.join(root,stage,relative+(stage==='source'?'.ts':'.js')),original=fs.readFileSync(file,'utf8');
 const audit=()=>JSON.parse(cp.execFileSync(process.execPath,[path.join(root,'audit.mjs'),options.typescript_root,path.join(root,stage+'-audit-config.json'),path.join(root,stage+'-audit-input.json')],{encoding:'utf8',timeout:60000}));
 const mutations=stage==='source'?[
  s=>s.replace('export type {State,Trigger,Parameters,Outcome}','export {State,Trigger,Parameters,Outcome}'),
  s=>s.replace('export {initialState};','export {initialState as wrong};'),
  s=>s+'\nimport "../events/completed.js";'
 ]:[
  s=>s.replace('return lifecycle_provider_js_1.initialState;','return "closed";'),
  s=>s+'\nexports.Outcome=1;',
  s=>s+'\nconst event=require("../events/completed.js");',
  s=>s+'\nfunction hidden(){return require("node:fs");}'
 ];
 for(const mutate of mutations){const text=mutate(original);assert.notEqual(text,original);fs.writeFileSync(file,text);assert.ok(audit().modules.some(m=>m.violations.length>0));rejected++;}fs.writeFileSync(file,original);assertCrossGeneratorExecutionCurrent(r);
}
console.log(JSON.stringify({state_surface_mutants:rejected}));
`);assert.equal(result.state_surface_mutants,7);t.diagnostic(JSON.stringify(result));
});

test('all-unavailable controls and in-flight native drift cannot produce a receipt', t => {
 const f=native(t),result=f.run(String.raw`
const original=cp.spawnSync;let injected=false;
cp.spawnSync=function(exe,args,...rest){const out=original.call(cp,exe,args,...rest);if(args.includes('--permission')){const runner=args.find(a=>a.endsWith('/runner.mjs'));fs.appendFileSync(path.join(path.dirname(runner),'native',selection.module_root,'features/alpha/src/domain/state-machines/lifecycle.provider.js'),'\n');injected=true;}return out;};syncBuiltinESMExports();
try{assert.throws(()=>executeCrossGeneratorStateMachine(plan,controls,definition,options),/artifact changed/);assert.ok(injected);}finally{cp.spawnSync=original;syncBuiltinESMExports();}
const source=__SOURCE__,file=path.join(source,'specs/alpha/nodes/lifecycle.json'),node=JSON.parse(fs.readFileSync(file));node.body.typed_contract.transitions[0].guard.arguments[0].value={op:'literal',type:'UInt64',value:'101'};fs.writeFileSync(file,JSON.stringify(node));
const g=loadCompiledProjectGraph(source),p=planCompiledReconciledProject(g,selection),b=createCrossGeneratorBoundary(g,p,definitions['cross-generator-verification']),c=createCrossGeneratorStateMachineControls(g,p,b,definition);
assert.ok(c.rows.every(r=>r.state==='not_evaluable'));const before=fs.readdirSync(options.workspace_parent);assert.throws(()=>executeCrossGeneratorStateMachine(p,c,definition,options),/no ready interoperability/);assert.deepEqual(fs.readdirSync(options.workspace_parent),before);
console.log(JSON.stringify({in_flight_native_drift_rejected:true,empty_pass_rejected:true}));
`.replace('__SOURCE__',JSON.stringify(f.source)));assert.equal(result.empty_pass_rejected,true);t.diagnostic(JSON.stringify(result));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
