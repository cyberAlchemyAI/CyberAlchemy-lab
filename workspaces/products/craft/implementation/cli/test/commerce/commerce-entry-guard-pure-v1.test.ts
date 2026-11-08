import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {stripTypeScriptTypes} from 'node:module';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
import {createCommerceEntryGuardPureOwnerV1} from '../../src/commerce/commerce-entry-guard-pure-v1.js';
import {generateCommerceValueCodecBundle} from '../../src/commerce/commerce-value-codec-generation.js';

test('original Entry guard evaluates its source Rule for the selected observation',async()=>{
 const root=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(root,'application.alch'),
  checked=sources.inspect(capture),semantics=createCoreCommerceSemanticOwner(sources),
  stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(root,'application.alch'),
  paths=new Set(checked.reconstruction.modules.map(module=>module.path)),
  texts=checked.files.filter(file=>paths.has(file.path)),
  bounds=JSON.parse(readFileSync(root+'/contracts/compute-bounds.json','utf8')),
  domain=createCommerceComputationDomainOwner(stage,source),
  baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',bounds.computation.limits));
 const entry=stage.moduleContracts(source).flatMap(module=>module.entries)
  .find(row=>row.id==='Orders.RecordCheckoutObservationEntry');
 assert.ok(entry);
 const dir=mkdtempSync(path.join(tmpdir(),'commerce-guard-'));
 writeFileSync(path.join(dir,'package.json'),'{"type":"module"}\n');
 for(const file of generateCommerceValueCodecBundle(stage,source,domain,baseline).files)
  writeFileSync(path.join(dir,file.path.replace(/\.ts$/,'.js')),stripTypeScriptTypes(file.text));
 const loaded=await import(pathToFileURL(path.join(dir,'values-and-codecs.js')).href);
 const guard=createCommerceEntryGuardPureOwnerV1(stage,source,domain,baseline,entry,loaded.createCommerceValueCodecs());
 try{
  const none={kind:'none'},progress={orderId:'order-1',state:'AwaitingStock',
   reserveCommandId:'reserve-1',captureAttemptKey:'capture-1',allocateCommandId:'allocate-1',
   releaseCommandId:'release-1',confirmCommandId:'confirm-1',cancelCommandId:'cancel-1',
   reserveResult:none,reserveRejected:none,paymentResult:none,allocationResult:none,releaseResult:none,
   captureDispatched:false,workerOwner:{kind:'some',value:'worker-1'},workerEpoch:1n,version:2n};
  const path='$.access.resource_condition.expression.right';
  assert.equal(guard.evaluate(path,[progress,{kind:'ReserveUnknown',commandId:'reserve-1'}]),true);
  assert.equal(guard.evaluate(path,[progress,{kind:'ReserveUnknown',commandId:'wrong-reserve'}]),false);
  assert.throws(()=>guard.evaluate('$.unrelated',[progress,{kind:'ReserveUnknown',commandId:'reserve-1'}]));
 }finally{guard.dispose();domain.dispose(baseline);stage.dispose(source);sources.dispose(capture);rmSync(dir,{recursive:true,force:true});}
});
