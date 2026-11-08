/** One real generated Commerce Capture path through the selected application. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCommerceApplicationAssemblyV1} from '../src/commerce/commerce-application-assembly-v1.js';
import {produceCommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {registerCommerceEntryFixtureActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url)),candidate=path.join(repo,'examples/ecommerce-target-candidate');
const json=(value:unknown)=>JSON.stringify(value,(_key,member)=>typeof member==='bigint'?member.toString():member);

test('selected application sends one protected DemoPay Capture after durable original dispatch',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-assembly-capture-'));
 let owner:Awaited<ReturnType<typeof createCommerceApplicationAssemblyV1>>|undefined,native:Awaited<ReturnType<typeof produceCommerceAuthNativeOwnerV1>>|undefined;
 try{
  owner=await createCommerceApplicationAssemblyV1(candidate,path.join(root,'generated'));
  const storage=await owner.openServiceStorage('payments'),sent:{path:string;body:Record<string,unknown>}[]=[];
  owner.openDemoPayDispatch({async exchange(request){
   assert.equal(request.origin,'https://demopay.invalid');assert.equal(request.method,'POST');assert.equal(request.path,'/v1/capture');
   assert.equal(request.headers['demopay-protocol'],'1');
   const body=JSON.parse(Buffer.from(request.body).toString('utf8')) as Record<string,unknown>;
   sent.push({path:request.path,body});
   return {status:200,headers:{'content-type':'application/json; charset=utf-8','demopay-protocol':'1'},
    body:Buffer.from(JSON.stringify({...body,status:'Pending',providerReference:null}),'utf8')};
  }});
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  const {auth,entries}=await owner.openSelectedEntryAuth(native),entryId='Payments.CapturePaymentEntry';
  const entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry),subject='service-'+definition.access.caller,evidence='assembly-capture-evidence';
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'assembly-capture-session',routes:[{entry:entryId,permission:definition.access.auth_permission}]});
  const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence,principal_kind:'service',service_id:definition.access.caller,scope:definition.access.auth_permission.scope});
  try{
   const input={orderId:'order-one',attemptKey:'attempt-one',amountMinor:25n,currency:'USD'},wire=Buffer.from(json(input));
   const started=await entries.begin(actor,entryId,wire,input);assert.equal(started.ok,true,json(started));if(!started.ok)return;
   const runtime=await owner.openGeneratedOperation(started.invocation);
   let outcome:Readonly<Record<string,unknown>>|undefined,error:unknown;
   try{outcome=await runtime.run(started.invocation);}catch(cause){error=cause;}
   const persisted=storage.inspectStoredRecord('Payments.PaymentAttempt',0,{attemptKey:input.attemptKey}) as Record<string,unknown>|null;
   const diagnostic=json({sent,persisted,outcome,error:error instanceof Error?{name:error.name,message:error.message,code:(error as any).code}:error});
   assert.equal(sent.length,1,diagnostic);
   assert.deepEqual(sent[0]!.body,{attemptKey:input.attemptKey,orderId:input.orderId,amountMinor:'25',currency:'USD'},diagnostic);
   assert.ok(persisted,diagnostic);
   assert.equal(persisted.dispatchState,'Dispatched',diagnostic);
   assert.ok(typeof persisted.version==='bigint'&&persisted.version>=2n,diagnostic);
   if(error)throw error;
   assert.ok(outcome,diagnostic);
   assert.equal(outcome.kind,'returned',diagnostic);
   assert.equal((outcome.value as Record<string,unknown>).kind,'Unknown',diagnostic);
   assert.equal(persisted.status,'Unknown',diagnostic);
   entries.retire(started.invocation);
  }finally{auth.disposeActor(actor);auth.disposeEntry(entry);}
 }finally{owner?.close();await native?.dispose();rmSync(root,{recursive:true,force:true});}
});
