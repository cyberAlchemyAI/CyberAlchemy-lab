import test from 'node:test';
import assert from 'node:assert/strict';
import {businessApplicationFixture} from '../helpers/business-application.ts';
import {compileRequestApplicationBindingV1} from '../../src/system-integration/application-binding-v1.ts';
import {composeRequestApplicationPlanV1} from '../../src/generation/request-application-plan-v1.ts';
import {prepareRequestApplicationCallable,assertApplicationCallableCurrent} from '../../src/profile-engine/application-adapter.ts';
import {assertBusinessInputV2Current} from '../../src/profile-engine/business-input-v2.ts';
import {renderApplicationCallableSource} from '../../src/profile-engine/application-adapter.ts';
import {mkdirSync,writeFileSync,readFileSync} from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
// Open questions: default settlement/transport assembly BA07/09 and public workflow BA12.
test('request callable uses owning minimal plan assertions and retains original/derived identities',async t=>{
 const f=await businessApplicationFixture(t),binding=compileRequestApplicationBindingV1(f.graph,f.source,f.plan),plan=composeRequestApplicationPlanV1(f.plan,binding),intent=f.input.snapshot.project.application_intents[0]!;
 const lineage={application_id:'commerce',original_source:'domain.alch',original_source_sha256:f.derived.original_source_sha256,original_semantics_sha256:f.derived.original_semantics_sha256,derived_source_sha256:f.derived.source_sha256,derivation_sha256:f.derived.derivation_sha256,line_map:f.derived.line_map},current=()=>assertBusinessInputV2Current(f.input);
 const callable=prepareRequestApplicationCallable(f.graph,plan,binding,intent,lineage,current);assertApplicationCallableCurrent(callable);assert.equal(callable.kind,'request-application');assert.equal(callable.intent.source,'domain.alch');assert.equal(callable.intent.mapping_binding_ref,'request-mapping:commerce:receiveNotice');assert.equal(callable.intent.operation_ref,'commerce:receive-notice');assert.equal(callable.artifact_plan,plan);assert.equal('whole' in callable,false);assert.equal(callable.lineage.line_map.filter(row=>row.origin==='adapter').length,1);
 assert.throws(()=>assertApplicationCallableCurrent({...callable}),/UNREGISTERED/);assert.throws(()=>prepareRequestApplicationCallable(f.graph,structuredClone(plan),binding,intent,lineage,current),/SNAPSHOT/);assert.throws(()=>prepareRequestApplicationCallable(f.graph,plan,structuredClone(binding),intent,lineage,current),/SNAPSHOT/);assert.throws(()=>prepareRequestApplicationCallable(f.graph,plan,binding,intent,{...lineage,application_id:'other'},current),/JOIN/);
 const generated=path.join(f.root,'assembled'),write=(relative:string,content:string)=>{const target=path.join(generated,relative);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,content);};
 for(const artifact of plan.artifacts)write(artifact.relative_path,artifact.content);
 write('src/profile-entry.ts',renderApplicationCallableSource(callable,undefined,{settlement_import:'./empty-settlement.js',transport_import:'./application-http.mjs'}));
 write('src/empty-settlement.ts',readFileSync(path.join(f.cli,'profiles/node-http-entry-local-v2/runtime/empty-settlement.ts'),'utf8'));write('src/application-http.mts',readFileSync(path.join(f.cli,'profiles/node-http-entry-local-v2/runtime/application-http.mts'),'utf8'));write('package.json','{"type":"module"}');
 const alch=path.join(path.resolve(f.cli,'../../../../..'),'language/capabilities/alchlang/plans/general-compiler-v1/implementation');
 const native=spawnSync(process.execPath,[path.join(alch,'node_modules/typescript/bin/tsc'),'--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--strict','--skipLibCheck','--noEmit','src/profile-entry.ts'],{cwd:generated,encoding:'utf8'});assert.equal(native.status,0,native.stdout+native.stderr);
 const runner=`import assert from 'node:assert/strict';import {handler,invoke} from './src/profile-entry.ts';async function main(){const result=await invoke({payload:{id:'7'}});assert.equal(result.status,'returned');assert.equal(result.value.id,7n);const request=()=>new Request('https://example.invalid/receiveNotice',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({payload:{id:'9'}})});const response=await handler(request());assert.equal(response.status,200);assert.equal((await response.json()).value.id,'9');const missing=await handler(request(),{},{applications:{receiveNotice:null}});assert.equal(missing.status,503);const observed=await invoke({payload:{id:'10'}},undefined,{observe:()=>{throw Error('observer')}});assert.equal(observed.status,'returned');assert.equal((await handler(request(),{},{cancellation:'required'})).status,409);}main().catch(e=>{console.error(e);process.exitCode=1});`;
 const run=spawnSync(process.execPath,[path.join(alch,'node_modules/tsx/dist/cli.mjs'),'--eval',runner],{cwd:generated,encoding:'utf8'});assert.equal(run.status,0,run.stdout+run.stderr);
});
