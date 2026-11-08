/** Actual source StoreObservation -> original native transaction component.
 * Explicit business rows are fixture input; no invocation/Auth/worker authority
 * or whole application acceptance is claimed. Open Questions: ../../docs/COMMERCE-CONTRACTS.md. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,cpSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceTechnicalModelOwnerV5} from '../../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../../src/profile-engine/family-v5.js';
import {createCommerceSqliteFamilyOwnerV1} from '../../src/commerce/commerce-sqlite-family-v1.js';
import {createCommerceSqliteTransactionOwnerV1} from '../../src/commerce/commerce-sqlite-transaction-owner-v1.js';
import {openCommerceSqliteUnitOfWorkV1} from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-unit-of-work.js';
const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
let root:string,plans:any,family:any,bundle:any,programs:any,program:any,operation:any,codecs:any,values:any,serial=0;
const stores:any[]=[];
const checked=(result:any)=>{assert.equal(result.ok,true,JSON.stringify(result.error));return result.value;};
before(async()=>{
 root=mkdtempSync(path.join(tmpdir(),'craft-observation-transaction-'));
 const sourceRoot=path.join(root,'source');cpSync(path.join(repository,'examples/ecommerce-target-candidate'),sourceRoot,{recursive:true});
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(sourceRoot),actual=sources.inspect(capture),modulePaths=new Set(actual.reconstruction.modules.map((m:any)=>m.path)),texts=actual.files.filter((f:any)=>modulePaths.has(f.path)),limits=JSON.parse(readFileSync(path.join(sourceRoot,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(sourceRoot,'application.alch'),domain=createCommerceComputationDomainOwner(stage,source),baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 values=domain.inspect(baseline).contract.values;plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 const models=createCommerceTechnicalModelOwnerV5(),families=createCommerceFamilyOwnerV5(models),model=await models.checkTechnicalSource(sourceRoot,'profiles/implementation.alch'),parameters=stage.inspect(source).application.parameters,selectedFamily=families.derive(model,parameters,{kind:'local-effects',omitted_capabilities:'unsupported-not-silently-executed',targets:[{module:'Orders',name:'PlaceOrder',role:'Operation'}]});
 family=createCommerceSqliteFamilyOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,selectedFamily);
 bundle=family.materialize(family.bindService('orders'),path.join(root,'repository'));
 const directory=family.inspectBundle(bundle).directory;
 codecs=(await import(pathToFileURL(path.join(directory,'values-and-codecs.js')).href)).createCommerceValueCodecs();
 programs=await createCommerceSqliteTransactionOwnerV1(sources,capture,stage,source,domain,baseline,plans,family,bundle,path.join(root,'identity'));
 operation=plans.bindOperation('Orders.RecordCheckoutObservation');const tx=plans.inspectOperation(operation).transactions.find((t:any)=>t.plan.name==='RecordObservation');assert.ok(tx);program=await programs.bind(operation,plans.bindTransaction(operation,tx.path));
 console.log('Observation transaction fixture: '+root);
});
after(()=>{for(const store of stores)store.close();family?.dispose();plans?.dispose();});
function pure(sourcePath:string,args:any[]){const call=plans.bindPureCall(operation,sourcePath),view=call.owner.inspect(call.handle),input=Object.fromEntries(view.callee.parameters.map((p:any,i:number)=>[p.name,args[i]])),wire=checked(codecs.encodeComputationParameters(codecs.schemaForCallableArguments(view.callee.declaration),input)),result=call.owner.evaluateBoundParameters(call.handle,wire).observation.result;assert.equal(result.ok,true,JSON.stringify(result.error));return checked(codecs.decodeComputationValue(checked(codecs.checkCommerceSchema({...values,root:view.callee.result})),result.wire));}
function input(){
 const order={id:'observation-order',customerId:'component-customer',quoteId:'component-quote',currency:'USD',payableMinor:100n,lines:[{quantity:1n,sku:'component-sku'}],status:'AwaitingStock',version:1n};
 const progress={orderId:order.id,state:'AwaitingStock',reserveCommandId:'reserve-command',captureAttemptKey:'capture-command',allocateCommandId:'allocate-command',releaseCommandId:'release-command',confirmCommandId:'confirm-command',cancelCommandId:'cancel-command',reserveResult:{kind:'none'},reserveRejected:{kind:'none'},paymentResult:{kind:'none'},allocationResult:{kind:'none'},releaseResult:{kind:'none'},captureDispatched:false,workerOwner:{kind:'some',value:'component-worker'},workerEpoch:1n,version:2n};
 const reservation={reservationId:'component-reservation',orderId:order.id,lines:order.lines,linesFingerprint:'a'.repeat(64),reserveCommandId:progress.reserveCommandId,lastCommandId:progress.reserveCommandId,status:'Reserved',version:1n};
 const observation={kind:'ReserveApplied',reservation},signal=pure('$.body[10].value.expression.arguments[1]',[observation]),proposal=pure('$.body[10].value.expression',[progress.state,signal]);assert.equal(proposal.tag,'transition');assert.equal(proposal.state,'AwaitingPayment');
 const nextProgress=pure('$.body[12].value.expression',[progress,observation,proposal.state]);assert.equal(nextProgress.version,3n);assert.equal(nextProgress.reserveResult.kind,'some');
 return {order,progress,nextProgress,orderId:order.id,expectedOrderVersion:1n,expectedProgressVersion:2n};
}
async function execute(change:(data:any)=>void=()=>{}){
 const values=input(),stored=structuredClone(values);change(stored);
 const store:any=await openCommerceSqliteUnitOfWorkV1(family,bundle,path.join(root,'store-'+(++serial)+'.sqlite'),'create');stores.push(store);
 const claim=(id:string)=>{const acquired=store.claimCommand({logicalEntryId:'component-fixture',principalId:'component-fixture',commandId:id,fingerprint:'b'.repeat(64),transactionNamespace:'1'.repeat(64)});assert.equal(acquired.kind,'claimed');return acquired.command;};
 const seeded=store.apply(claim('seed'),[{kind:'create',entity:'Orders.Order',value:stored.order},{kind:'create',entity:'Orders.CheckoutProgress',value:stored.progress}],true);assert.equal(seeded.kind,'committed');
 const frame=Object.fromEntries(programs.inspect(program).frame.map((f:any)=>[f.name,(values as any)[f.name]]));
 const result=store.applySourceTransaction(programs,program,claim('observation'),frame);
 const diagnostic={kind:result.kind,frame:Object.keys(frame),source_failure:result.rollback?store.inspectDisposition(result.rollback).source_failure:null};console.log(JSON.stringify(diagnostic));
 return {store,result,diagnostic};
}
test('a Mapping-derived nextProgress cannot replace the original read row required by RecordObservation CAS',async()=>{
 const {store,result,diagnostic}=await execute();assert.equal(result.kind,'committed',JSON.stringify(diagnostic));
 const row=store.readRow('Orders.CheckoutProgress',0,{orderId:'observation-order'}),progress=store.inspectRow(row).value;assert.equal(progress.state,'AwaitingPayment');assert.equal(progress.version,3n);assert.equal(progress.reserveResult.kind,'some');
 const order=store.inspectRow(store.readRow('Orders.Order',0,{id:'observation-order'})).value;assert.equal(order.status,'AwaitingPayment');assert.equal(order.version,2n);
});
test('RecordObservation retains stale-version rejection and atomic rollback',async()=>{
 const {store,result}=await execute(data=>{data.progress.version=3n;});assert.equal(result.kind,'version-conflict');
 const order=store.inspectRow(store.readRow('Orders.Order',0,{id:'observation-order'})).value;assert.equal(order.version,1n);assert.equal(order.status,'AwaitingStock');
});
test('RecordObservation rejects a same-version change to the original progress row',async()=>{
 const {store,result}=await execute(data=>{data.progress.reserveCommandId='different-reserve-command';});assert.equal(result.kind,'version-conflict');
 const order=store.inspectRow(store.readRow('Orders.Order',0,{id:'observation-order'})).value;assert.equal(order.version,1n);assert.equal(order.status,'AwaitingStock');
});
