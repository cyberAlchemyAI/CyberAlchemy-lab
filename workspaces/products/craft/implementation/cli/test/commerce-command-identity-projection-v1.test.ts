/** Data-only command identity projection, pending generated scope custody. */
import test from 'node:test';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,cpSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceTechnicalModelOwnerV5} from '../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../src/profile-engine/family-v5.js';
import {createCommerceBindingAssemblyOwnerV1} from '../src/commerce/commerce-binding-assembly-v1.js';
import {createCommerceSqliteFamilyOwnerV1} from '../src/commerce/commerce-sqlite-family-v1.js';
import {createCommerceSqliteTransactionOwnerV1,inspectCommerceTransactionSourceScopeV1} from '../src/commerce/commerce-sqlite-transaction-owner-v1.js';
import {produceCommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {createCommerceEntryContextOwnerV1,registerCommerceEntryFixtureActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {createCommerceSelectedEntryAuthOwnerV1} from '../src/commerce/commerce-selected-entry-auth-v1.js';
import {createCommerceCommandIdentityBindingOwnerV1} from '../src/commerce/commerce-command-identity-binding-v1.js';
import {projectCommerceCommandIdentityDataV1} from '../src/commerce/commerce-command-identity-projection-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

test('standalone selected root and local journal identity projections check full typed scope but grant no claim',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-command-projection-'));
 // This component test needs an eligible original Auth invocation, not a
 // forged Workflow journal. Use an owned standalone source variant with the
 // same permission and typed Operation, with authorization-only Entry access.
 // The unchanged production Entry's
 // grant-only denial is covered by commerce-fresh-generated-transaction-v1.
 const fixture=path.join(root,'source');cpSync(candidate,fixture,{recursive:true});
 const accessPath=path.join(fixture,'contracts/access.alch'),access=readFileSync(accessPath,'utf8');
 const first=access.indexOf('entry Payments.CapturePaymentEntry:'),last=access.indexOf('\nentry ',first+1);
 assert.ok(first>=0&&last>first);let entrySource=access.slice(first,last);
 const binding='    resource-binding causal OriginalOrderCall from craft.commerce-causal-call/v1-candidate#Orders.Checkout/original-step-journal\n';
 const guard='    resource-condition input.attemptKey == causal.captureAttemptKey and input.orderId == causal.orderId and input.amountMinor == causal.payableMinor and input.currency == causal.currency';
 assert.equal(entrySource.split(binding).length,2);assert.equal(entrySource.split(guard).length,2);
 entrySource=entrySource.replace(binding,'').replace(guard+'\n','').replace('    on-resource-false reject forbidden before effects\n','');
 writeFileSync(accessPath,access.slice(0,first)+entrySource+access.slice(last));
 const identitiesPath=path.join(fixture,'contracts/contract-identities.json'),identities=JSON.parse(readFileSync(identitiesPath,'utf8'));
 const accessIdentity=identities.modules.find((row:{artifact:{path:string}})=>row.artifact.path==='contracts/access.alch');assert.ok(accessIdentity);
 const accessBytes=readFileSync(accessPath);accessIdentity.artifact.sha256=createHash('sha256').update(accessBytes).digest('hex');accessIdentity.artifact.bytes=accessBytes.length;
 writeFileSync(identitiesPath,JSON.stringify(identities,null,2)+'\n');


 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(fixture),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(fixture,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(fixture,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(fixture,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models);
 const assemblyOwner=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblyOwner.assembly();
 const bindings=createCommerceCommandIdentityBindingOwnerV1(sources,capture,semantics,semantic,domain,baseline,plans,assemblyOwner,assembly);
 let native:Awaited<ReturnType<typeof produceCommerceAuthNativeOwnerV1>>|undefined,auth:Awaited<ReturnType<typeof createCommerceEntryContextOwnerV1>>|undefined,selected:Awaited<ReturnType<typeof createCommerceSelectedEntryAuthOwnerV1>>|undefined;
 try{
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  auth=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,path.join(root,'auth'));
  selected=await createCommerceSelectedEntryAuthOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,assemblyOwner,assembly,auth,path.join(root,'selected'));
  const entryId='Payments.CapturePaymentEntry',entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry),subject='service-'+definition.access.caller,evidence='identity-projection-evidence';
  const fixture=seed(native,{subject,evidence,session:'identity-projection-session',routes:[{entry:entryId,permission:definition.access.auth_permission}]});
  const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence,principal_kind:'service',service_id:definition.access.caller,scope:definition.access.auth_permission.scope});
  try{
   const input={orderId:'order-one',attemptKey:'attempt-one',amountMinor:25n,currency:'USD'},wire=Buffer.from(JSON.stringify(input,(_key,value)=>typeof value==='bigint'?String(value):value));
   const started=await selected.begin(actor,entryId,wire,input);assert.equal(started.ok,true,JSON.stringify(started));if(!started.ok)return;
   const rootInvocation=started.invocation,pathToChild=selected.localCallPath(rootInvocation,'Payments.DispatchOriginalCapture');
   const child=selected.deriveLocalCall(rootInvocation,pathToChild,{orderId:'order-one',attemptKey:'attempt-one',requestFingerprint:'a'.repeat(64)});
   const operation=selected.operation(child),operationView=plans.inspectOperation(operation),named=operationView.transactions.find(t=>t.plan.name==='MarkDispatched');assert.ok(named);
   const binding=bindings.bind(entryId,operation,named.path);
   const sqlite=createCommerceSqliteFamilyOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner.family(assembly));
   try{
    const service=sqlite.bindService('payments'),bundle=sqlite.materialize(service,path.join(root,'repository'));
    const programs=await createCommerceSqliteTransactionOwnerV1(sources,capture,stage,source,domain,baseline,plans,sqlite,bundle,path.join(root,'programs'));
    const rootOperation=selected.operation(rootInvocation),rootOperationView=plans.inspectOperation(rootOperation),prepare=rootOperationView.transactions.find(t=>t.plan.name==='PrepareCapture');assert.ok(prepare);
    const rootBinding=bindings.bind(entryId,rootOperation,prepare.path),rootProgram=await programs.bind(rootOperation,plans.bindTransaction(rootOperation,prepare.path));
    const rootAvailable:Record<string,unknown>={...input,requestFingerprint:'a'.repeat(64),prior:{kind:'none'}};
    const rootSourceScope=inspectCommerceTransactionSourceScopeV1(plans,rootOperation,prepare.path),rootScope=Object.fromEntries(rootSourceScope.map(v=>[v.name,rootAvailable[v.name]]));
    const rootResult=projectCommerceCommandIdentityDataV1(bindings,rootBinding,selected,rootInvocation,plans,programs,rootProgram,rootScope);
    assert.deepEqual([rootResult.logicalEntryId,rootResult.principalId,rootResult.commandId,rootResult.fingerprint],[entryId,definition.access.caller,'attempt-one','a'.repeat(64)]);
    assert.equal(rootResult.transactionNamespace,bindings.inspect(rootBinding).transaction_namespace_sha256);
    assert.equal(rootResult.generated_scope_proven,false);assert.equal(rootResult.authority_effect,'none');
    assert.throws(()=>projectCommerceCommandIdentityDataV1(bindings,rootBinding,selected,child,plans,programs,rootProgram,rootScope),code('ForeignInvocation'));
    assert.throws(()=>projectCommerceCommandIdentityDataV1(bindings,rootBinding,selected,rootInvocation,plans,programs,rootProgram,{...rootScope,requestFingerprint:'not-a-fingerprint'}),code('InputType'));
    const program=await programs.bind(operation,plans.bindTransaction(operation,named.path));
    const intent={attemptKey:'attempt-one',orderId:'order-one',amountMinor:25n,currency:'USD',requestFingerprint:'a'.repeat(64),status:'Intent',dispatchState:'Prepared',providerReference:{kind:'none'},priorDefinitive:{kind:'none'},version:1n};
    const available:Record<string,unknown>={...input,...selected.parameters(child),intent};
    const sourceScope=inspectCommerceTransactionSourceScopeV1(plans,operation,named.path),scope=Object.fromEntries(sourceScope.map(v=>[v.name,available[v.name]]));
    const result=projectCommerceCommandIdentityDataV1(bindings,binding,selected,child,plans,programs,program,scope);
    assert.deepEqual([result.logicalEntryId,result.principalId,result.commandId,result.fingerprint],[entryId,definition.access.caller,'attempt-one','a'.repeat(64)]);
    assert.equal(result.transactionNamespace,bindings.inspect(binding).transaction_namespace_sha256);
    assert.notEqual(result.transactionNamespace,rootResult.transactionNamespace);
    assert.equal(result.principal_custody,'original-selected-auth-scope');
    assert.equal(result.generated_scope_proven,false);assert.equal(result.authority_effect,'none');
    assert.throws(()=>projectCommerceCommandIdentityDataV1(bindings,{...binding},selected,child,plans,programs,program,scope),code('ForeignOwner'));
    assert.throws(()=>projectCommerceCommandIdentityDataV1(bindings,binding,selected,rootInvocation,plans,programs,program,scope),code('ForeignOwner'));
    assert.throws(()=>projectCommerceCommandIdentityDataV1(bindings,binding,selected,child,plans,programs,rootProgram,scope),code('ForeignBinding'));
    assert.throws(()=>projectCommerceCommandIdentityDataV1(bindings,binding,selected,child,plans,programs,program,{...scope,attemptKey:undefined}),code('InputType'));
    assert.throws(()=>projectCommerceCommandIdentityDataV1(bindings,binding,selected,child,plans,programs,program,{...scope,intent:{...intent,version:'not-an-integer'}}),code('InputType'));
    const missing={...scope};delete (missing as any).intent;
    assert.throws(()=>projectCommerceCommandIdentityDataV1(bindings,binding,selected,child,plans,programs,program,missing),code('InputType'));
    selected.retire(child);
    assert.throws(()=>projectCommerceCommandIdentityDataV1(bindings,binding,selected,child,plans,programs,program,scope),code('ForeignOwner'));
    assert.deepEqual(projectCommerceCommandIdentityDataV1(bindings,rootBinding,selected,rootInvocation,plans,programs,rootProgram,rootScope).principalId,definition.access.caller);
   }finally{sqlite.dispose();}
   selected.retire(rootInvocation);
  }finally{auth.disposeActor(actor);auth.disposeEntry(entry);}
 }finally{selected?.dispose();auth?.dispose();await native?.dispose();bindings.dispose();assemblyOwner.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});

import {seedCommerceAuthFixtureDatabaseV1 as seed} from './support/commerce-auth-fixture-provider-v1.js';
