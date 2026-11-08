import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {businessApplicationFixture} from '../helpers/business-application.ts';
import {compileRequestApplicationBindingV1} from '../../src/system-integration/application-binding-v1.ts';
import {composeRequestApplicationPlanV1,assertRequestApplicationPlanV1} from '../../src/generation/request-application-plan-v1.ts';
import {assertWholeApplicationPlan,mergeWholeApplicationArtifactsV1,validateOperationRequestContracts,typescriptRuntimeMappingArtifact,typescriptRequestHandlerArtifact} from '../../src/generation/whole-application-v1.ts';
import {selectReconciledProjectArtifacts} from '../../src/generation/reconciled-project-layout.ts';
import {assertRequestSchema} from '../helpers/request-schema.ts';
// Open questions: public profile workflow BA08–12 and installed use BA18.
test('minimal plan invokes actual generated Mapping/Operation and preserves empty settlement outcomes',async t=>{
 const f=await businessApplicationFixture(t),binding=compileRequestApplicationBindingV1(f.graph,f.source,f.plan),plan=composeRequestApplicationPlanV1(f.plan,binding);assertRequestApplicationPlanV1(plan);assert.throws(()=>assertWholeApplicationPlan(plan),/SNAPSHOT/);
 assert.deepEqual(plan,composeRequestApplicationPlanV1(f.plan,binding));assert.equal(plan.handlers[0]!.operation_ref,'commerce:receive-notice');assert.ok(plan.artifacts.some(a=>a.relative_path.endsWith('/mappings/message-to-order.ts')));assert.ok(plan.artifacts.some(a=>a.relative_path.endsWith('/operations/receive-notice.ts')));assert.ok(plan.artifacts.every(a=>!a.relative_path.includes('migrations')&&!a.relative_path.includes('persistence')&&!a.relative_path.includes('messaging')&&!a.relative_path.includes('observation')));
 const generated=path.join(f.root,'generated');for(const file of plan.artifacts){const target=path.join(generated,file.relative_path);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,file.content);}
 const repo=path.resolve(f.cli,'../../../../..'),alch=path.join(repo,'language/capabilities/alchlang/plans/general-compiler-v1/implementation'),tsc=path.join(alch,'node_modules/typescript/bin/tsc');
 assertRequestSchema(path.join(f.cli,'contracts'),'request-application-plan-v1.schema.json',plan,{...plan,schema_version:'domainspec.whole-application-plan/v1-candidate'});
 const probe=spawnSync(process.execPath,[tsc,'--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--strict','--skipLibCheck','--noEmit',...plan.native_type_dependencies],{cwd:generated,encoding:'utf8'});assert.equal(probe.status,0,probe.stdout+probe.stderr);
 const run=`import assert from 'node:assert/strict';import {APPLICATION_REQUEST_HANDLERS as handlers} from './src/integrations/application-request-handlers.ts';
 async function main(){let begins=0,commits=0;const call=handlers['request-mapping:commerce:receiveNotice'];const store={begin:async()=>{begins++;return {read:async()=>{throw Error('no reads')},commit:async batch=>{commits++;assert.deepEqual(batch,{writes:[],events:[]});return {status:'committed'}},rollback:async()=>{throw Error('unexpected rollback')}}}};const result=await call({payload:{id:'7'}},{store});assert.equal(result.status,'committed');assert.deepEqual(result.value,{id:7n});assert.equal(begins,1);assert.equal(commits,1);await assert.rejects(call({payload:{id:'invalid'}},{store}));assert.equal(begins,1);const uncertain=await call({payload:{id:'8'}},{store:{begin:async()=>({read:async()=>{throw Error('no reads')},commit:async()=>({status:'indeterminate'}),rollback:async()=>{throw Error('uncertain rollback')}})}});assert.equal(uncertain.status,'indeterminate');}main().catch(e=>{console.error(e);process.exitCode=1});`;
 const executed=spawnSync(process.execPath,[path.join(alch,'node_modules/tsx/dist/cli.mjs'),'--eval',run],{cwd:generated,encoding:'utf8'});assert.equal(executed.status,0,executed.stdout+executed.stderr);
});
test('minimal plan refuses forged dependencies and retains shared request/import/path collision checks',async t=>{
 const f=await businessApplicationFixture(t),binding=compileRequestApplicationBindingV1(f.graph,f.source,f.plan),plan=composeRequestApplicationPlanV1(f.plan,binding);
 assert.throws(()=>assertRequestApplicationPlanV1(structuredClone(plan)),/SNAPSHOT/);assert.throws(()=>composeRequestApplicationPlanV1(structuredClone(f.plan),binding));assert.throws(()=>composeRequestApplicationPlanV1(f.plan,structuredClone(binding)),/SNAPSHOT/);
 const requests=structuredClone(binding.application_graph.operation_requests);requests[0]!.bindings[0]!.parameters[0]!.parameter='other';assert.throws(()=>validateOperationRequestContracts(f.plan,requests,binding.application_graph.runtime_bindings),/OPERATION_REQUEST/);
 const mappings=structuredClone(binding.application_graph.runtime_bindings);mappings[0]!.result_type={kind:'scalar',name:'Bool'};assert.throws(()=>validateOperationRequestContracts(f.plan,binding.application_graph.operation_requests,mappings),/OPERATION_REQUEST/);
 const view=selectReconciledProjectArtifacts(f.plan),withoutMapping=structuredClone(view) as any;withoutMapping.modules=withoutMapping.modules.filter((m:any)=>!m.relative_path.endsWith('/mappings/message-to-order.ts'));assert.throws(()=>typescriptRuntimeMappingArtifact(withoutMapping,binding.application_graph.runtime_bindings),/RUNTIME_MAPPING/);
 const duplicate=structuredClone(view) as any,module=duplicate.modules.find((m:any)=>m.relative_path.endsWith('/mappings/message-to-order.ts'));duplicate.modules.push({...module,relative_path:'src/features/commerce/domain/mappings/duplicate.ts'});assert.throws(()=>typescriptRuntimeMappingArtifact(duplicate,binding.application_graph.runtime_bindings),/RUNTIME_MAPPING/);
 const missingExport=structuredClone(view) as any;missingExport.modules.find((m:any)=>m.relative_path.endsWith('/operations/receive-notice.ts')).exports=[];assert.throws(()=>typescriptRequestHandlerArtifact(missingExport,binding),/OPERATION_REQUEST/);
 const artifact=plan.artifacts.find(a=>a.relative_path.endsWith('application-request-handlers.ts'))!;assert.throws(()=>mergeWholeApplicationArtifactsV1([{artifact,owner:'reconciled-application'},{artifact,owner:'whole-application-composer'}]),/COLLISION/);
 assert.throws(()=>mergeWholeApplicationArtifactsV1([{artifact:{...artifact,content:artifact.content.replace('./runtime-bindings.js','./missing.js')},owner:'whole-application-composer'}]),/IMPORT/);
});
