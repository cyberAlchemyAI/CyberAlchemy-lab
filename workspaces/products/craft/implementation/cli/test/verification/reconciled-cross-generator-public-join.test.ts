import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {crossGeneratorPublicFixture} from '../helpers/cross-generator-public.ts';
import {workflowFixture} from '../helpers/workflow-verification.ts';

const project=path.resolve(import.meta.dirname,'../../../..');
function native(t:any,compound=false,module_root='domain',ruleOnly=false){
 const f=compound?crossGeneratorPublicFixture(t):workflowFixture(t);
 let source=path.join(f.root,'source'),selection={...f.selection,module_root};
 if(ruleOnly){
  const rule=fs.readFileSync(path.join(source,'specs/commerce/nodes/allowed.json'));
  source=path.join(f.root,'only-rule');fs.mkdirSync(path.join(source,'specs/commerce/nodes'),{recursive:true});
  fs.writeFileSync(path.join(source,'project.json'),JSON.stringify({schema_version:'domainspec.project/v1',project_id:'rule-only',features:['commerce'],cross_feature_edges:[]}));
  fs.writeFileSync(path.join(source,'specs/commerce/feature.json'),JSON.stringify({schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes:['allowed'],edges:[]}));
  fs.writeFileSync(path.join(source,'specs/commerce/nodes/allowed.json'),rule);selection={...selection,factories:[],operations:[],workflows:[]};
 }
 const require=createRequire(import.meta.url),types=fs.realpathSync(require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}));
 const deps=path.dirname(path.dirname(path.dirname(types))),undici=path.dirname(createRequire(types).resolve('undici-types/package.json'));
 const lean=process.env.DOMAINSPEC_LEAN!;assert.ok(lean&&path.isAbsolute(lean),'explicit installed Lean required');
 const leanRoot=path.dirname(path.dirname(lean)),image=nativeToolchainImage();
 assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const scratch=path.join(f.root,'scratch');fs.mkdirSync(scratch);fs.writeFileSync(path.join(f.root,'package.json'),'{"type":"module"}');
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),
 '--mount','type=bind,source='+project+',target='+project+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly',
 '--mount','type=bind,source='+undici+',target='+undici+',readonly','--mount','type=bind,source='+leanRoot+',target='+leanRoot+',readonly',
 '--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',f.root,'--env','TMPDIR='+scratch,image];
 const command=(args:string[])=>{try{return execFileSync('docker',[...docker,...args],{encoding:'utf8',timeout:600000,maxBuffer:32*1024*1024});}catch(e:any){throw Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'));}};
 command(['tsc','--ignoreConfig','--strict','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext',
 '--rootDir',path.join(project,'impl/cli/src'),'--outDir',path.join(f.root,'dist'),path.join(project,'impl/cli/src/index.ts')]);
 const prefix=[
 "import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';",
 "import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification,verifyReconciledSourceProject,renderReconciledVerificationExecution,publishReconciledProject} from './dist/index.js';",
 "import {canonicalJson,sha256} from './dist/input/source-manifest.js';",
 'const sourcePath='+JSON.stringify(source)+',selection='+JSON.stringify(selection)+',root='+JSON.stringify(f.root)+',scratch='+JSON.stringify(scratch)+';',
 'const tools='+JSON.stringify({typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:path.join(deps,'@types'),lean_executable:lean})+';',
 "const graph=loadCompiledProjectGraph(sourcePath),plan=planCompiledReconciledProject(graph,selection),execute=()=>executeReconciledVerification(graph,plan,tools);",
 "const check=(r,id)=>r.checks.find(c=>c.id===id);",
 "const aggregateDirectory=()=>{const run=fs.readdirSync(scratch).find(p=>p.startsWith('domainspec-reconciled-verify-'));assert.ok(run);const parent=path.join(scratch,run);const child=fs.readdirSync(parent).find(p=>p.startsWith('ds-cross-generator-aggregate-'));assert.ok(child);return path.join(parent,child);};"
 ].join('\n')+'\n';
 return {...f,source,run:(body:string)=>{const file=path.join(f.root,'client.mjs');fs.writeFileSync(file,prefix+body);return JSON.parse(command(['node',file]));}};
}

test('public verification joins the complete seven-family compound model in both layouts and seals historical evidence',async t=>{
 for(const layout of ['domain','application/domain'])await t.test(layout,t=>{
  const f=native(t,true,layout),observed=f.run(`
const target=path.join(root,'output');publishReconciledProject(plan,target);tools.target_root=target;
const inventory=dir=>Object.fromEntries(fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?Object.entries(inventory(path.join(dir,e.name))):[[path.join(dir,e.name),sha256(fs.readFileSync(path.join(dir,e.name)))]]));
const sourceBefore=inventory(sourcePath),targetBefore=inventory(target);
const r=selection.module_root==='domain'?execute():verifyReconciledSourceProject(sourcePath,selection,tools),coverage=r.cross_generator_coverage;
assert.equal(r.result,'incomplete',JSON.stringify(r.checks.filter(c=>c.result==='fail')));
assert.deepEqual(r.checks.filter(c=>c.result==='not_evaluable').map(c=>c.id).sort(),['safe-output-separate-from-planning']);
const publicWorkflow=r.workflow_public_coverage;
assert.equal(check(r,'workflow-public-evidence-binding').result,'pass');assert.equal(check(r,'workflow-public-evidence-currentness').result,'pass');
assert.equal(check(r,'selected-generator-semantic-controls').result,'pass');assert.equal(check(r,'selected-generator-semantic-controls').evidence.fulfilled_node_count,14);
assert.equal(publicWorkflow.binding.rows[0].standalone.state,'not_evaluable');assert.equal(publicWorkflow.binding.rows[0].evidence.case_count,12472);
assert.equal(publicWorkflow.standalone_checks.find(c=>c.id==='selected-generator-semantic-controls').result,'not_evaluable');
assert.equal(publicWorkflow.standalone_checks.find(c=>c.id==='workflow-native-effect-audit').result,'not_evaluable');
assert.equal(publicWorkflow.standalone_checks.find(c=>c.id==='workflow-native-orchestration-audit').result,'not_evaluable');
assert.equal(r.semantic_coverage.ready_count,13);assert.equal(r.semantic_coverage.not_evaluable_count,1);
assert.equal(publicWorkflow.semantic_fulfillment.length,14);assert.ok(publicWorkflow.semantic_fulfillment.every(row=>row.result==='pass'));
assert.deepEqual(publicWorkflow.semantic_fulfillment.find(row=>row.kind==='Workflow').origins,['original-retained-workflow']);
assert.ok(publicWorkflow.semantic_fulfillment.filter(row=>row.kind!=='Workflow').every(row=>row.origins.join(',')==='original-standalone-native'));
assert.ok(publicWorkflow.audit_fulfillment.every(a=>a.result==='pass'&&a.evidence.missing_source_paths.length===0&&a.evidence.missing_workflow_selectors.length===0));
assert.ok(publicWorkflow.audit_fulfillment.every(a=>a.evidence.origins.length===a.evidence.required_source_paths.length&&a.evidence.origins.every(o=>o.origin==='original-retained-workflow-native')));
assert.deepEqual(publicWorkflow.retained_blocked_by,[]);assert.equal(publicWorkflow.evidence_scope,'sealed-historical-report-not-a-live-retained-receipt');
assert.equal(check(r,'cross-generator-behavior').result,'pass',JSON.stringify(r.checks.filter(c=>c.result!=='pass')));
assert.equal(check(r,'cross-generator-currentness').result,'pass');assert.equal(check(r,'verification-workspace-cleanup').result,'pass');
assert.equal(coverage.public_result,'pass');assert.equal(coverage.execution.result,'pass');assert.equal(coverage.execution.retained_family_count,7);
assert.equal(coverage.preparation.roots.length,14);assert.equal(coverage.execution.edges.length,50);
assert.ok(coverage.execution.edges.filter(e=>e.behavior_required).every(e=>e.execution_status==='pass'));
const workflow=coverage.execution.retained.find(f=>f.family==='workflow');assert.equal(workflow.outcome.tested_case_count,12472);assert.equal(workflow.outcome.tested_call_count,20369);
assert.equal(coverage.retained_workspace_state,'removed');assert.equal(fs.existsSync(coverage.execution.workspace),false);
assert.equal(coverage.evidence_scope,'sealed-historical-report-not-a-live-retained-receipt');
assert.deepEqual(JSON.parse(renderReconciledVerificationExecution(r)),r);assert.throws(()=>renderReconciledVerificationExecution(structuredClone(r)),/registered/);
assert.equal(check(r,'safe-output-separate-from-planning').result,'not_evaluable');
assert.deepEqual(inventory(sourcePath),sourceBefore);assert.deepEqual(inventory(target),targetBefore);assert.deepEqual(fs.readdirSync(scratch),[]);
console.log(JSON.stringify({layout:selection.module_root,cross_generator:coverage.public_result,families:7,cases:12472,overall:r.result,remaining:r.checks.filter(c=>c.result==='not_evaluable').map(c=>c.id)}));
`);t.diagnostic(JSON.stringify(observed));
 });
});

test('public aggregation preserves unavailable independent families while observing the entire changed-source Workflow',t=>{
 const f=native(t,true),file=path.join(f.source,'specs/commerce/nodes/positive.json'),raw=JSON.parse(fs.readFileSync(file,'utf8'));
 raw.body.typed_contract.expression={op:'eq',left:{op:'literal',type:'Bool',value:true},right:{op:'literal',type:'Bool',value:true}};fs.writeFileSync(file,JSON.stringify(raw));
 t.diagnostic(JSON.stringify(f.run(`
const r=execute(),coverage=r.cross_generator_coverage;
assert.equal(r.result,'incomplete',JSON.stringify(r.checks.filter(c=>c.result==='fail')));
assert.equal(check(r,'cross-generator-behavior').result,'not_evaluable',JSON.stringify(r.checks.filter(c=>c.result!=='pass')));
assert.equal(coverage.execution.result,'incomplete');assert.ok(coverage.execution.rows.some(row=>row.family==='factory-rule'&&row.result==='not_evaluable'));
assert.equal(coverage.execution.retained.find(f=>f.family==='workflow').outcome.tested_case_count,12167);
assert.equal(r.workflow_public_coverage.semantic_fulfillment.find(row=>row.kind==='Workflow').result,'pass');
assert.ok(r.workflow_public_coverage.semantic_fulfillment.some(row=>row.kind!=='Workflow'&&row.result==='not_evaluable'));
assert.equal(check(r,'selected-generator-semantic-controls').result,'not_evaluable');
assert.equal(check(r,'workflow-native-effect-audit').result,'pass');assert.equal(check(r,'workflow-native-orchestration-audit').result,'pass');
assert.equal(coverage.retained_workspace_state,'removed');assert.deepEqual(fs.readdirSync(scratch),[]);
console.log(JSON.stringify({cross_generator:coverage.public_result,overall:r.result,retained:coverage.execution.retained_family_count}));
`)));
});

test('public native mismatch remains a failure even when Workflow observes the same Operation wrapper successfully',t=>{
 const f=native(t);t.diagnostic(JSON.stringify(f.run(`
const original=cp.spawnSync;let injected=false;
cp.spawnSync=function(file,args,...rest){
 const out=original.call(this,file,args,...rest),i=args.findIndex(a=>String(a).endsWith('/runner.mjs'));
 if(!injected&&i>=0&&JSON.parse(fs.readFileSync(args[i+1],'utf8')).rows?.[0]?.adapter==='operation-protocol'){
  const value=JSON.parse(out.stdout);value.rows[0].cases.pop();out.stdout=JSON.stringify(value);injected=true;
 }return out;
};syncBuiltinESMExports();let r;try{r=execute();}finally{cp.spawnSync=original;syncBuiltinESMExports();}
assert.ok(injected);assert.equal(check(r,'cross-generator-behavior').result,'fail');assert.equal(r.result,'fail');
assert.equal(r.cross_generator_coverage.execution.families.find(f=>f.family==='workflow').result,'pass');
assert.equal(r.workflow_public_coverage.binding.retained_status,'observed');
assert.equal(check(r,'cross-generator-behavior').result,'fail');
assert.equal(check(r,'verification-workspace-cleanup').result,'pass');assert.deepEqual(fs.readdirSync(scratch),[]);
console.log(JSON.stringify({overall:r.result,cross_generator:check(r,'cross-generator-behavior').result,injected}));
`)));
});

test('public final currentness rejects an aggregate manifest changed by a later proof tool',t=>{
 const f=native(t);t.diagnostic(JSON.stringify(f.run(`
const original=cp.spawnSync;let changed=false;
cp.spawnSync=function(file,args,...rest){
 if(!changed&&file===tools.lean_executable&&args.some(a=>String(a).endsWith('/Audit.lean'))){
  fs.appendFileSync(path.join(aggregateDirectory(),'outcomes.json'),' ');changed=true;
 }return original.call(this,file,args,...rest);
};syncBuiltinESMExports();let r;try{r=execute();}finally{cp.spawnSync=original;syncBuiltinESMExports();}
assert.ok(changed);assert.equal(r.cross_generator_coverage.execution.result,'pass');
assert.equal(check(r,'cross-generator-currentness').result,'fail');
assert.equal(check(r,'workflow-public-evidence-currentness').result,'fail');
assert.ok(r.workflow_public_coverage.retained_blocked_by.includes('workflow-public-evidence-currentness'));
assert.ok(r.workflow_public_coverage.semantic_fulfillment.every(row=>!row.origins.includes('original-retained-workflow')));
assert.equal(check(r,'cross-generator-behavior').result,'not_evaluable');assert.ok(check(r,'cross-generator-behavior').blocked_by.includes('cross-generator-currentness'));
assert.equal(r.result,'fail');assert.deepEqual(fs.readdirSync(scratch),[]);
console.log(JSON.stringify({overall:r.result,blocked_by:check(r,'cross-generator-behavior').blocked_by}));
`)));
});

test('public zero-edge obligations are explicitly inapplicable, never described as observed native families',t=>{
 const f=native(t,false,'domain',true);t.diagnostic(JSON.stringify(f.run(`
const r=execute(),coverage=r.cross_generator_coverage;
assert.equal(check(r,'cross-generator-behavior').result,'pass');assert.equal(check(r,'cross-generator-behavior').evidence.native_result,'inapplicable');
assert.match(check(r,'cross-generator-behavior').reason,/zero native families/);
assert.equal(coverage.execution.result,'inapplicable');assert.equal(coverage.execution.executed_family_count,0);
assert.equal(coverage.execution.workspace,null);assert.equal(coverage.retained_workspace_state,'not_created');assert.equal(coverage.preparation.roots.length,1);
assert.equal(coverage.execution.edges.length,0);assert.equal(check(r,'cross-generator-currentness').result,'pass');assert.deepEqual(fs.readdirSync(scratch),[]);
assert.equal(r.workflow_public_coverage.workflow_count,0);assert.equal(r.workflow_public_coverage.binding,null);
assert.equal(r.workflow_public_coverage.retained_status,'inapplicable');assert.equal(r.workflow_public_coverage.semantic_fulfillment.length,1);
console.log(JSON.stringify({native_result:coverage.execution.result,executed_families:0,overall:r.result}));
`)));
});

test('late shared source and public native artifact changes revoke otherwise successful cross-generator evidence',async t=>{
 for(const mode of ['source','public-native'])await t.test(mode,t=>{
  const f=native(t);t.diagnostic(JSON.stringify(f.run(`
const mode=__MODE__,original=cp.spawnSync;let changed=false;
cp.spawnSync=function(file,args,...rest){
 if(!changed&&file===tools.lean_executable&&args.some(a=>String(a).endsWith('/Audit.lean'))){
  const target=mode==='source'?path.join(sourcePath,'specs/commerce/nodes/allowed.json'):path.join(path.dirname(aggregateDirectory()),'native',plan.resolved.artifacts.find(a=>a.relative_path.endsWith('.ts')).relative_path);
  fs.appendFileSync(target,' ');changed=true;
 }return original.call(this,file,args,...rest);
};syncBuiltinESMExports();let r;try{r=execute();}finally{cp.spawnSync=original;syncBuiltinESMExports();}
assert.ok(changed);assert.equal(r.cross_generator_coverage.execution.result,'pass');
const dependency=mode==='source'?'source-currentness':'verification-workspace-currentness';
assert.equal(check(r,dependency).result,'fail');assert.equal(check(r,'cross-generator-behavior').result,'not_evaluable');
assert.ok(check(r,'cross-generator-behavior').blocked_by.includes(dependency));
assert.equal(r.cross_generator_coverage.public_result,'not_evaluable');assert.equal(r.result,'fail');assert.deepEqual(fs.readdirSync(scratch),[]);
console.log(JSON.stringify({mode,overall:r.result,blocked_by:check(r,'cross-generator-behavior').blocked_by}));
`.replace('__MODE__',JSON.stringify(mode)))));
 });
});


test('public cleanup failure revokes a passing native result without claiming that retained files were removed',t=>{
 const f=native(t);t.diagnostic(JSON.stringify(f.run(`
const original=fs.rmSync;let prevented=false,owned;
fs.rmSync=function(dir,...rest){
 if(path.dirname(String(dir))===scratch&&path.basename(String(dir)).startsWith('domainspec-reconciled-verify-')){prevented=true;owned=dir;throw Error('injected owned cleanup failure');}
 return original.call(this,dir,...rest);
};let r;try{r=execute();}finally{fs.rmSync=original;}
assert.ok(prevented);assert.equal(r.cross_generator_coverage.execution.result,'pass');
assert.equal(check(r,'cross-generator-currentness').result,'pass');assert.equal(check(r,'verification-workspace-cleanup').result,'fail');
assert.equal(check(r,'cross-generator-behavior').result,'not_evaluable');assert.ok(check(r,'cross-generator-behavior').blocked_by.includes('verification-workspace-cleanup'));
assert.equal(r.cross_generator_coverage.retained_workspace_state,'cleanup_not_confirmed');assert.ok(fs.existsSync(r.cross_generator_coverage.execution.workspace));
assert.ok(r.workflow_public_coverage.retained_blocked_by.includes('verification-workspace-cleanup'));
assert.ok(r.workflow_public_coverage.semantic_fulfillment.every(row=>!row.origins.includes('original-retained-workflow')));
assert.equal(r.result,'fail');assert.equal(path.dirname(owned),scratch);original(owned,{recursive:true});assert.deepEqual(fs.readdirSync(scratch),[]);
console.log(JSON.stringify({overall:r.result,blocked_by:check(r,'cross-generator-behavior').blocked_by}));
`)));
});

test('public artifacts changed during final retained validation cannot reuse an earlier currentness pass',t=>{
 const f=native(t);t.diagnostic(JSON.stringify(f.run(`
const originalOpen=fs.openSync,originalSpawn=cp.spawnSync;let proofFinished=false,changed=false;
cp.spawnSync=function(file,args,...rest){const result=originalSpawn.call(this,file,args,...rest);if(file===tools.lean_executable&&args.some(a=>String(a).endsWith('/Audit.lean')))proofFinished=true;return result;};
fs.openSync=function(file,...rest){
 if(proofFinished&&!changed&&String(file).endsWith('/outcomes.json')){
  changed=true;const nativeRoot=path.join(path.dirname(path.dirname(String(file))),'native');
  const walk=dir=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);
  const target=walk(nativeRoot).find(p=>p.endsWith('.ts'));assert.ok(target);fs.appendFileSync(target,' ');
 }
 return originalOpen.call(this,file,...rest);
};syncBuiltinESMExports();let r;try{r=execute();}finally{fs.openSync=originalOpen;cp.spawnSync=originalSpawn;syncBuiltinESMExports();}
assert.ok(changed);assert.equal(r.result,'fail');assert.equal(check(r,'verification-workspace-currentness').result,'fail');
assert.equal(check(r,'cross-generator-currentness').result,'pass');
assert.equal(check(r,'cross-generator-behavior').result,'not_evaluable');
assert.ok(r.workflow_public_coverage.retained_blocked_by.includes('verification-workspace-currentness'));
assert.ok(r.workflow_public_coverage.semantic_fulfillment.every(row=>!row.origins.includes('original-retained-workflow')));
assert.deepEqual(fs.readdirSync(scratch),[]);console.log(JSON.stringify({late_public_artifact_rejected:changed,overall:r.result}));
`)));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
