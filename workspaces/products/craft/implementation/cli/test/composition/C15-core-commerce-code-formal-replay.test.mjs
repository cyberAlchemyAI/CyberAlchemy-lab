/** Claim-free code and bounded formal exports from one selected Commerce
 * application. The full qualification assertion follows C14's executable
 * completion. Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.ts';
import {createCoreCommerceServiceArtifactOwner}
 from '../../src/generic/core-commerce-service-artifact-owner.ts';
import {createCommerceApplicationAssemblyV1}
 from '../../src/commerce/commerce-application-assembly-v1.ts';
import {createCommerceApplicationFormalApiV1}
 from '../../src/commerce/commerce-application-formal-api-v1.ts';
import {CoreCommerceFormalExactRequestErrorV1}
 from '../../src/commerce/commerce-core-formal-exact-request-v1.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');
const workflow='Orders.Checkout.Checkout';
const calculation='Orders.PayableTotal';
const sha256=value=>createHash('sha256').update(value).digest('hex');

test('C15 completed Commerce emits code and optional bounded formal models from the same claim-free source/profile',
 {skip:process.env.CRAFT_C15_COMMERCE_FULL_REPLAY!=='1'},async()=>{
  const work=mkdtempSync('/var/tmp/craft-c15-code-formal-');
  let artifacts,assembly,formal,sourceOwner,capture,successful=false;
  try{
   // Check absence of authored claims from the captured AlchLang declarations,
   // rather than relying on a flag that merely permits them to be omitted.
   sourceOwner=createCoreCommerceSourceOwner();capture=sourceOwner.prepare(source);
   const captured=sourceOwner.inspect(capture);
   assert.deepEqual(captured.reconstruction.modules.flatMap(module=>module.declarations)
    .filter(declaration=>declaration.surface==='FormalClaim'),[]);

   // Ordinary application materialization runs before any formal owner is
   // opened. Its artifact identity must be the same identity formal exports
   // later recheck, rather than a second fixture or handwritten model.
   artifacts=await createCoreCommerceServiceArtifactOwner(source,path.join(work,'generated'));
   const generated=artifacts.inspect();
   const graph=JSON.parse(readFileSync(path.join(work,'generated/artifacts/system-graph.json'),'utf8'));
   const bridge=JSON.parse(readFileSync(path.join(work,'generated/artifacts/business-system-bridge.json'),'utf8'));
   assert.equal(generated.source_capture_sha256,captured.capture_sha256);
   assert.equal(graph.source_capture_sha256,generated.source_capture_sha256);
   assert.equal(bridge.source_capture_sha256,generated.source_capture_sha256);
   assert.equal(graph.family_sha256,generated.family_sha256);
   assert.equal(bridge.family_sha256,generated.family_sha256);
   assert.deepEqual(generated.services.map(service=>service.id),
    ['catalog','fulfillment','inventory','orders','payments']);
   assert.ok(generated.services.every(service=>service.files.some(file=>file.path==='store.sqlite')));
   assert.ok(graph.nodes.some(node=>node.id==='workflow:'+workflow));
   assert.ok(graph.nodes.some(node=>node.id==='event:Shop.Events.OrderConfirmed'));
   assert.ok(generated.routes.some(route=>route.entry==='Orders.PlaceOrderEntry'));
   assert.equal(generated.authority_effect,'none');

   assembly=await createCommerceApplicationAssemblyV1(source,path.join(work,'formal-selected-application'));
   formal=createCommerceApplicationFormalApiV1(source,assembly);
   const selected=assembly.inspect(),formalSelection=formal.inspect();
   for(const identity of [selected,formalSelection]){
    assert.equal(identity.application,generated.application);
    assert.equal(identity.source_capture_sha256,generated.source_capture_sha256);
    assert.equal(identity.family_sha256,generated.family_sha256);
   }
   assert.equal(formalSelection.formal_claims_required,false);

   const structure=formal.exportStructure(workflow);
   const alloy=formal.exportArtifacts(workflow);
   const temporal=formal.exportTemporal(workflow);
   const pure=formal.exportPureUint64(calculation);
   assert.equal(structure.language,'alloy');
   assert.equal(structure.workflow,workflow);
   assert.equal(alloy.model.structure_sha256,structure.structure_sha256);
   assert.equal(alloy.files.find(file=>file.relative_path==='core-commerce-structure.als')?.content,
    structure.alloy);
   assert.equal(temporal.language,'tla+');
   assert.equal(temporal.workflow,workflow);
   assert.equal(temporal.structure_sha256,structure.structure_sha256);
   assert.equal(pure.language,'smtlib2');
   assert.equal(pure.selector,calculation);
   assert.match(structure.alloy,/fact ExactCheckedStructure/);
   assert.match(temporal.tla,/MODULE CoreCommercePossibleRoutes/);
   assert.match(pure.smtlib2,/\(bvsub Input0 Input1\)/);
   assert.equal(sha256(structure.alloy),structure.alloy_sha256);
   assert.equal(sha256(temporal.tla),temporal.tla_sha256);
   assert.equal(sha256(pure.smtlib2),pure.smtlib2_sha256);
   for(const model of [structure,temporal,pure]){
    assert.equal(model.application,generated.application);
    assert.equal(model.source_capture_sha256,generated.source_capture_sha256);
    assert.equal(model.family_sha256,generated.family_sha256);
    assert.equal(model.executable_sha256,structure.executable_sha256);
   }
   assert.deepEqual(structure.services.map(service=>service.id),generated.services.map(service=>service.id));
   assert.ok(structure.claim_ceiling.includes('structure-only'));
   assert.ok(temporal.unsupported_semantics.includes('recovery-fencing'));
   assert.ok(pure.unsupported_semantics.includes('input-output-wire-validation'));

   // A partial projection cannot be silently promoted into an exact model of
   // execution, persistence, Auth, event delivery, or recovery.
   for(const selector of [calculation,'Orders.PlaceOrderEntry',workflow]){
    assert.throws(()=>formal.requireExactModel(selector),error=>{
     if(!(error instanceof CoreCommerceFormalExactRequestErrorV1))return false;
     assert.equal(error.code,'UnsupportedTranslation');
     assert.equal(error.selector,selector);
     assert.equal(error.application,generated.application);
     assert.equal(error.source_capture_sha256,generated.source_capture_sha256);
     assert.equal(error.executable_sha256,structure.executable_sha256);
     assert.ok(error.missing_semantics.includes('native-transaction-precondition-outcomes-commit-rollback-and-disposition-proof'));
     assert.ok(error.missing_semantics.includes('temporal-guards-observations-persistence-and-recovery'));
     return true;
    });
   }
   assert.throws(()=>formal.exportArtifacts(workflow,'tla+'),error=>error?.code==='UnsupportedLanguage');
   artifacts.assertCurrent();formal.assertCurrent();
   if(process.env.CRAFT_C15_COMMERCE_STRUCTURE_ONLY!=='1'){
    assert.equal(generated.complete_application,true);
    assert.deepEqual(generated.missing_complete_application_classes,[]);
   }
   successful=true;
  }finally{
   formal?.close();assembly?.close();artifacts?.close();
   if(sourceOwner&&capture)sourceOwner.dispose(capture);
   if(successful)rmSync(work,{recursive:true,force:true});
   else console.error('C15 code/formal replay diagnostic fixture retained at '+work);
  }
 });
