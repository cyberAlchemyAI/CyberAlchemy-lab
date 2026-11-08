/** A fresh process must adopt the exact generated repository before reopening its durable store.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
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
import {createCommerceServiceStorageOwnerV1} from '../src/commerce/commerce-service-storage-v1.js';
import {deriveCommerceCommandTransactionNamespaceV1} from '../src/commerce/commerce-command-identity-binding-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:unknown)=>Boolean(error&&typeof error==='object'&&
 ((error as {code?:string}).code===name||(error as {diagnostics?:readonly {code?:string}[]}).diagnostics?.[0]?.code===name));

async function context(){
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map(module=>module.path));
 const texts=captured.files.filter(file=>paths.has(file.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source);
 const limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch');
 const families=createCommerceFamilyOwnerV5(models);
 const assemblies=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families);
 const assembly=assemblies.assembly();
 const open=(directory:string,mode:'create'|'reopen')=>createCommerceServiceStorageOwnerV1(
  sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblies,assembly,
  'payments',directory,mode);
 return {open,dispose(){assemblies.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);}};
}

async function reopenedInChild(directory:string,expectedStoreId:string){
 const selected=await context();
 try{
  const storage=await selected.open(directory,'reopen');
  try{
   assert.equal(storage.inspect().store_id,expectedStoreId);
   const payment=storage.inspectStoredRecord('Payments.PaymentAttempt',0,{attemptKey:'process-attempt'}) as
    {orderId:string;amountMinor:bigint;status:string;version:bigint}|null;
   assert.ok(payment);assert.equal(payment.orderId,'process-order');assert.equal(payment.amountMinor,25n);
   assert.equal(payment.status,'Intent');assert.equal(payment.version,1n);
  }finally{storage.close();}
 }finally{selected.dispose();}
}

async function refusedWhileActiveInChild(directory:string){
 const selected=await context();
 try{await assert.rejects(selected.open(directory,'reopen'),code('PredecessorActive'));}
 finally{selected.dispose();}
}

if(process.argv[2]==='--reopen-child'){
 const directory=process.argv[3],expectedStoreId=process.argv[4];
 if(!directory||!expectedStoreId)throw Error('child arguments required');
 await reopenedInChild(directory,expectedStoreId);
}else if(process.argv[2]==='--active-child'){
 const directory=process.argv[3];if(!directory)throw Error('child directory required');
 await refusedWhileActiveInChild(directory);
}else{
 test('fresh process reopens exact generated repository and refuses modified or extra members',async()=>{
  const root=mkdtempSync(path.join(tmpdir(),'commerce-process-reopen-')),directory=path.join(root,'payments');
  const selected=await context();
  try{
   const storage=await selected.open(directory,'create');
   let storeId:string;
   try{
    storeId=storage.inspect().store_id;
    const tx=await storage.bindTransaction('Payments.CapturePayment','PrepareCapture','Payments.CapturePaymentEntry');
    const key={logicalEntryId:'Payments.CapturePaymentEntry',principalId:'process-service',commandId:'process-command',
     fingerprint:'a'.repeat(64),transactionNamespace:deriveCommerceCommandTransactionNamespaceV1('Payments.CapturePayment','PrepareCapture')};
    const frame={orderId:'process-order',attemptKey:'process-attempt',amountMinor:25n,currency:'USD',requestFingerprint:'a'.repeat(64)};
    const applied=storage.apply(tx,key,frame);
    assert.equal(applied.kind,'applied');if(applied.kind==='applied')assert.equal(applied.outcome.kind,'committed');
    execFileSync(process.execPath,['--import','tsx',fileURLToPath(import.meta.url),'--active-child',directory],
     {cwd:fileURLToPath(new URL('../',import.meta.url)),encoding:'utf8',stdio:'pipe',timeout:600000});
   }finally{storage.close();}
   execFileSync(process.execPath,['--import','tsx',fileURLToPath(import.meta.url),'--reopen-child',directory,storeId!],
    {cwd:fileURLToPath(new URL('../',import.meta.url)),encoding:'utf8',stdio:'pipe',timeout:600000});

   const repository=path.join(directory,'repository'),module=path.join(repository,'values-and-codecs.js');
   const original=readFileSync(module,'utf8');writeFileSync(module,original+'\n');
   await assert.rejects(selected.open(directory,'reopen'),code('StaleOwner'));
   writeFileSync(module,original);
   const extra=path.join(repository,'package.json');writeFileSync(extra,'{"type":"commonjs"}\n');
   await assert.rejects(selected.open(directory,'reopen'),code('InvalidContract'));
  }finally{selected.dispose();rmSync(root,{recursive:true,force:true});}
 });
}
