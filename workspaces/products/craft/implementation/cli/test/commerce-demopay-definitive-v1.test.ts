/** Original generated definitive Payment tails through selected application owners. */
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

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const json=(value:unknown)=>JSON.stringify(value,(_key,member)=>typeof member==='bigint'?member.toString():member);

test('selected generated Capture records both definitive provider outcomes',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-definitive-capture-'));
 let owner:Awaited<ReturnType<typeof createCommerceApplicationAssemblyV1>>|undefined;
 let native:Awaited<ReturnType<typeof produceCommerceAuthNativeOwnerV1>>|undefined;
 try{
  owner=await createCommerceApplicationAssemblyV1(candidate,path.join(root,'generated'));
  const storage=await owner.openServiceStorage('payments');
  const sent:{attemptKey:string;body:Record<string,unknown>}[]=[];
  owner.openDemoPayDispatch({async exchange(request){
   assert.equal(request.origin,'https://demopay.invalid');
   assert.equal(request.method,'POST');assert.equal(request.path,'/v1/capture');
   assert.equal(request.headers['demopay-protocol'],'1');
   const body=JSON.parse(Buffer.from(request.body).toString('utf8')) as Record<string,unknown>;
   const attemptKey=body.attemptKey;
   if(attemptKey!=='attempt-captured'&&attemptKey!=='attempt-declined')throw new Error('UnexpectedCaptureAttempt');
   sent.push({attemptKey,body});
   const status=attemptKey==='attempt-captured'?'Captured':'DefinitivelyDeclined';
   const providerReference=attemptKey==='attempt-captured'?'provider-captured':'provider-declined';
   return {status:200,headers:{'content-type':'application/json; charset=utf-8','demopay-protocol':'1'},
    body:Buffer.from(JSON.stringify({...body,status,providerReference}),'utf8')};
  }});
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  const {auth,entries}=await owner.openSelectedEntryAuth(native);
  const entryId='Payments.CapturePaymentEntry',entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry);
  try{
   for(const [index,case_ ] of ([
    {attemptKey:'attempt-captured',orderId:'order-captured',amountMinor:25n,status:'Captured',providerReference:'provider-captured'},
    {attemptKey:'attempt-declined',orderId:'order-declined',amountMinor:30n,status:'Declined',providerReference:'provider-declined'},
   ] as const).entries()){
    // Each case gets a fresh native session because generated execution can
    // exceed the fixture's bounded session lifetime.
    const subject='service-'+definition.access.caller,evidence='definitive-'+index;
    const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'definitive-session-'+index,
     routes:[{entry:entryId,permission:definition.access.auth_permission}]});
    const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence,
     principal_kind:'service',service_id:definition.access.caller,scope:definition.access.auth_permission.scope});
    let invocation:Awaited<ReturnType<typeof entries.begin>>|undefined;
    try{
     const input={orderId:case_.orderId,attemptKey:case_.attemptKey,amountMinor:case_.amountMinor,currency:'USD'};
     const started=await entries.begin(actor,entryId,Buffer.from(json(input)),input);
     assert.equal(started.ok,true,json(started));if(!started.ok)continue;
     invocation=started;
     const runtime=await owner.openGeneratedOperation(started.invocation);
     let outcome:Readonly<Record<string,unknown>>|undefined,error:unknown;
     try{outcome=await runtime.run(started.invocation);}catch(cause){error=cause;}
     const persisted=storage.inspectStoredRecord('Payments.PaymentAttempt',0,{attemptKey:case_.attemptKey}) as Record<string,unknown>|null;
     const diagnostic=json({case:case_.status,sent,persisted,outcome,
      error:error instanceof Error?{name:error.name,message:error.message,code:(error as any).code}:error});
     assert.equal(sent.length,index+1,diagnostic);
     assert.deepEqual(sent[index]!.body,{attemptKey:case_.attemptKey,orderId:case_.orderId,
      amountMinor:case_.amountMinor.toString(),currency:'USD'},diagnostic);
     assert.ok(persisted,diagnostic);
     assert.equal(persisted.status,case_.status,diagnostic);
     assert.equal(persisted.dispatchState,'Dispatched',diagnostic);
     assert.equal(persisted.version,3n,diagnostic);
     assert.equal((persisted.providerReference as Record<string,unknown>).kind,'some',diagnostic);
     assert.equal((persisted.providerReference as Record<string,unknown>).value,case_.providerReference,diagnostic);
     const definitive=(persisted.priorDefinitive as Record<string,unknown>);
     assert.equal(definitive.kind,'some',diagnostic);
     assert.equal((definitive.value as Record<string,unknown>).status,case_.status,diagnostic);
     assert.equal((definitive.value as Record<string,unknown>).providerReference,case_.providerReference,diagnostic);
     if(error)throw error;
     assert.ok(outcome,diagnostic);
     assert.equal(outcome.kind,'returned',diagnostic);
     assert.equal((outcome.value as Record<string,unknown>).kind,case_.status,diagnostic);
     const view=(outcome.value as Record<string,unknown>).value as Record<string,unknown>;
     assert.equal(view.attemptKey,case_.attemptKey,diagnostic);
     assert.equal(view.status,case_.status,diagnostic);
     assert.equal(view.version,3n,diagnostic);
    }finally{if(invocation?.ok)entries.retire(invocation.invocation);auth.disposeActor(actor);}
   }
  }finally{auth.disposeEntry(entry);}
 }finally{owner?.close();await native?.dispose();rmSync(root,{recursive:true,force:true});}
});
