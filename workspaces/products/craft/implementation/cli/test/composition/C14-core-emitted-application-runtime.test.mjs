/** Opt-in integration of the actual emitted application module with the
 * original source-selected owner and native Auth. The full Event/Workflow
 * effect and process-recovery tests remain separate acceptance cases.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCoreCommerceServiceArtifactOwner}
 from '../../src/generic/core-commerce-service-artifact-owner.ts';
import {produceCommerceAuthNativeOwnerV1}
 from '../../src/commerce/commerce-auth-ready-bridge-v1.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');

test('C14 emitted application module opens checked HTTP/Auth, Workflow and Event selectors',
 {skip:process.env.CRAFT_C14_EMITTED_RUNTIME_RUN!=='1'},async()=>{
 const root=mkdtempSync('/var/tmp/craft-c14-emitted-runtime-');
 let owner,native,app,success=false;
 try{
  const output=path.join(root,'generated');
  owner=await createCoreCommerceServiceArtifactOwner(source,output);
  const emitted=await import(pathToFileURL(path.join(output,'artifacts','application.mjs')).href);
  assert.equal(emitted.applicationId,owner.inspect().application);
  assert.ok(emitted.workflowIds.includes('Orders.Checkout.Checkout'));
  assert.ok(emitted.eventEntryIds.includes('Fulfillment.OnOrderConfirmed'));
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  app=await emitted.createGeneratedCommerceApplication(owner,native);
  app.assertCurrent();
  assert.equal(app.auth.inspect().source_sha256,owner.inspect().source_capture_sha256);
  assert.ok(app.inspectWorkerActorRequirements('Orders.Checkout.Checkout').length>0);
  assert.equal(app.inspectEventActorRequirement('Fulfillment.OnOrderConfirmed').entry,
   'Fulfillment.OnOrderConfirmed');
  assert.deepEqual(await app.relayWorkflowPage('Orders.Checkout.Checkout',null,8),
   {results:[],next_cursor:null});
  assert.deepEqual(app.scanReadyEventPage('Fulfillment.OnOrderConfirmed',null,8),
   {occurrence_ids:[],next_cursor:null});
  assert.throws(()=>app.inspectWorkerActorRequirements('Missing.Workflow'),
   /NOT_SELECTED/);
  assert.throws(()=>app.inspectEventActorRequirement('Missing.Event'),
   /NOT_SELECTED/);
  app.close();app=undefined;
  success=true;
 }finally{
  app?.close();owner?.close();await native?.dispose();
  if(success)rmSync(root,{recursive:true,force:true});
  else console.error('C14 emitted runtime diagnostic fixture retained at '+root);
 }
});
