/** The selected original five-service Core application yields an honest
 * source/profile-bound structural Alloy view without a formal claim. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCommerceWorkflowCoordinationBindingV1} from '../../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {createCommerceApplicationAssemblyV1} from '../../src/commerce/commerce-application-assembly-v1.js';
import {exportCoreCommerceFormalStructureV1,assertCoreCommerceFormalStructureCurrentV1}
 from '../../src/commerce/commerce-core-formal-structure-v1.js';
import {createCoreCommerceFormalArtifactsV1,publishCoreCommerceFormalArtifactsV1}
 from '../../src/commerce/commerce-core-formal-artifacts-v1.js';
import {exportCoreCommercePureUint64SmtV1,assertCoreCommercePureUint64SmtCurrentV1}
 from '../../src/commerce/commerce-core-formal-uint64-v1.js';
import {exportCoreCommerceFormalTemporalV1,assertCoreCommerceFormalTemporalCurrentV1}
 from '../../src/commerce/commerce-core-formal-temporal-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(7),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const error=(code:string)=>(actual:unknown)=>{
 const row=actual as {code?:unknown;diagnostics?:readonly {code?:unknown}[]};
 return row?.code===code||row?.diagnostics?.[0]?.code===code;
};

test('C15 selected original Commerce structure binds five services, the checked Workflow and one profile',async()=>{
 const scratch=mkdtempSync(path.join(tmpdir(),'core-commerce-formal-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate);
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 let assembly:Awaited<ReturnType<typeof createCommerceApplicationAssemblyV1>>|undefined;
 try{
  const binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout');
  assembly=await createCommerceApplicationAssemblyV1(candidate,path.join(scratch,'application'));
  const model=exportCoreCommerceFormalStructureV1(sources,capture,semantics,semantic,binding,assembly);
  assert.equal(model.language,'alloy');
  assert.equal(model.application,'Shop.Application.Ecommerce');
  assert.equal(model.workflow,'Orders.Checkout.Checkout');
  assert.deepEqual(model.services.map(row=>row.id),['catalog','fulfillment','inventory','orders','payments']);
  assert.ok(model.steps.some(row=>row.name==='reserve'&&row.kind==='remote'));
  assert.ok(model.steps.some(row=>row.name==='mark-capture-dispatched'&&row.kind==='local-observation'));
  assert.ok(model.branches.some(row=>row.from==='reserve'&&row.observes));
  assert.ok(model.persisted_states.some(row=>row.name==='StockUncertain'));
  assert.ok(model.branches.some(row=>row.action==='suspend'&&row.target==='StockUncertain'));
  assert.ok(model.control_targets.some(row=>row.name==='needs-review'));
  assert.ok(model.resume.some(row=>row.from_state==='StockUncertain'&&row.action==='step'&&row.target==='reconcile-stock'));
  assert.match(model.alloy,/module CoreCommerceCheckedStructure/);
  assert.match(model.alloy,/fact ExactCheckedStructure/);
  assert.match(model.alloy,/W0\.workflowSteps = /);
  assert.match(model.alloy,/\.kind = RemoteStep/);
  assert.match(model.alloy,/assert EveryBranchHasExactlyOneStep/);
  assert.match(model.alloy,/assert ResumeTargetsMatchAction/);
  assert.deepEqual(model.unsupported_formal_languages,['tla+']);
  assert.equal(model.source_capture_sha256,assembly.inspect().source_capture_sha256);
  assert.equal(model.family_sha256,assembly.inspect().family_sha256);
  assert.match(model.exporter_code_sha256,/^[a-f0-9]{64}$/);
  assert.ok(model.alloy.includes(`// source_capture_sha256: ${model.source_capture_sha256}`));
  assert.ok(model.alloy.includes(`// family_sha256: ${model.family_sha256}`));
  const artifacts=createCoreCommerceFormalArtifactsV1(sources,capture,semantics,semantic,binding,assembly);
  assert.equal(artifacts.files.length,2);
  assert.equal(artifacts.files[0]!.content,model.alloy);
  assert.equal(artifacts.files[0]!.sha256,model.alloy_sha256);
  assert.equal(JSON.parse(artifacts.files[1]!.content).structure_sha256,model.structure_sha256);
  assert.deepEqual(artifacts.model,model);
  assert.equal(artifacts.model.claim_ceiling,model.claim_ceiling);
  assert.deepEqual(assembly.exportFormalStructure('Orders.Checkout.Checkout'),model);
  assert.deepEqual(assembly.exportFormalArtifacts('Orders.Checkout.Checkout'),artifacts);
  assert.throws(()=>assembly.exportFormalStructure('Orders.Checkout.Checkout','tla+'),error('UnsupportedLanguage'));
  assert.throws(()=>createCoreCommerceFormalArtifactsV1(sources,capture,semantics,semantic,binding,assembly,'tla+'),
   error('UnsupportedLanguage'));
  assert.throws(()=>publishCoreCommerceFormalArtifactsV1(sources,capture,semantics,semantic,binding,assembly,'relative/formal'),
   error('InvalidFormalTarget'));
  const target=path.join(scratch,'formal');
  const published=assembly.publishFormalStructure('Orders.Checkout.Checkout',target);
  assert.equal(readFileSync(path.join(target,'core-commerce-structure.als'),'utf8'),published.model.alloy);
  assert.equal(JSON.parse(readFileSync(path.join(target,'core-commerce-structure.json'),'utf8')).alloy_sha256,published.model.alloy_sha256);
  assert.throws(()=>assembly.publishFormalStructure('Orders.Checkout.Checkout',target),
   error('DS_ATOMIC_EXISTS'));
  assert.doesNotThrow(()=>assertCoreCommerceFormalStructureCurrentV1(sources,capture,semantics,semantic,binding,assembly!,model));
  assert.throws(()=>assertCoreCommerceFormalStructureCurrentV1(sources,capture,semantics,semantic,binding,assembly!,
   {...model,alloy:model.alloy+'\n'}),error('InvalidModel'));
  assert.throws(()=>assertCoreCommerceFormalStructureCurrentV1(sources,capture,semantics,semantic,binding,assembly!,
   {...model,branches:model.branches.slice(1)}),error('InvalidModel'));
  assert.throws(()=>exportCoreCommerceFormalStructureV1(sources,{...capture},semantics,semantic,binding,assembly!),error('ForeignOwner'));
  assert.throws(()=>exportCoreCommerceFormalStructureV1(sources,capture,semantics,semantic,binding,{...assembly!}),error('ForeignOwner'));
  const pure=exportCoreCommercePureUint64SmtV1(sources,capture,semantics,semantic,assembly,'Orders.PayableTotal');
  assert.deepEqual(assembly.exportPureUint64Formal('Orders.PayableTotal'),pure);
  assert.equal(pure.language,'smtlib2');
  assert.equal(pure.service,'orders');
  assert.deepEqual(pure.arithmetic_ops,['subtract','add','add']);
  assert.deepEqual(pure.declared_error_annotation,{kind:'fail',code:'calculation-failed'});
  assert.match(pure.smtlib2,/\(bvsub Input0 Input1\)/);
  assert.match(pure.smtlib2,/\(bvadd N0Value Input2\)/);
  assert.match(pure.smtlib2,/\(define-fun ActionAttached \(\) Bool \(not \(= Status #b00\)\)\)/);
  assert.deepEqual(pure.unsupported_semantics,['fuel-and-byte-budgets','input-output-wire-validation',
   'non-arithmetic-error-annotation','declared-failure-action-execution','generated-native-parity','solver-proof']);
  assert.equal(pure.family_sha256,assembly.inspect().family_sha256);
  assert.doesNotThrow(()=>assertCoreCommercePureUint64SmtCurrentV1(sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',pure));
  assert.throws(()=>assertCoreCommercePureUint64SmtCurrentV1(sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',
   {...pure,smtlib2:pure.smtlib2+'\n'}),error('InvalidModel'));
  assert.throws(()=>assertCoreCommercePureUint64SmtCurrentV1(sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',
   {...pure,declared_error_annotation:{kind:'fail',code:'forged'}}),error('InvalidModel'));
  assert.throws(()=>exportCoreCommercePureUint64SmtV1(sources,capture,semantics,semantic,assembly!,'Orders.MerchandiseSubtotal'),
   error('UnsupportedExpression'));
  const temporal=exportCoreCommerceFormalTemporalV1(sources,capture,semantics,semantic,binding,assembly);
  assert.deepEqual(assembly.exportFormalTemporal('Orders.Checkout.Checkout'),temporal);
  assert.equal(temporal.language,'tla+');
  assert.equal(temporal.application,model.application);
  assert.equal(temporal.workflow,model.workflow);
  assert.equal(temporal.source_capture_sha256,model.source_capture_sha256);
  assert.equal(temporal.family_sha256,model.family_sha256);
  assert.equal(temporal.structure_sha256,model.structure_sha256);
  const location=(kind:string,name:string)=>temporal.locations.find(row=>row.kind===kind&&row.name===name)?.atom;
  assert.ok(temporal.edges.some(row=>row.kind==='select-resume'&&
   row.from===location('persisted-state','StockUncertain')&&row.to===location('step','reconcile-stock')));
  assert.ok(temporal.edges.some(row=>row.kind==='remote-branch'&&row.source.startsWith('reserve/')&&
   row.to===location('step','mark-capture-dispatched')&&row.observation_commit_omitted));
  assert.ok(temporal.edges.some(row=>row.kind==='local-next'&&
   row.from===location('step','mark-capture-dispatched')&&row.to===location('step','capture')&&
   row.observation_commit_omitted));
  assert.ok(temporal.edges.some(row=>row.kind==='review-suspend'&&
   row.from===location('step','review')&&row.to===location('control-target','needs-review')));
  assert.match(temporal.tla,/MODULE CoreCommercePossibleRoutes/);
  assert.match(temporal.tla,/Spec == Init \/\\ \[\]\[Next\]_cursor/);
  assert.ok(!temporal.tla.includes('THEOREM'));
  assert.ok(temporal.unsupported_semantics.includes('recovery-fencing'));
  assert.doesNotThrow(()=>assertCoreCommerceFormalTemporalCurrentV1(sources,capture,semantics,semantic,binding,assembly!,temporal));
  assert.throws(()=>assertCoreCommerceFormalTemporalCurrentV1(sources,capture,semantics,semantic,binding,assembly!,
   {...temporal,tla:temporal.tla+'\n'}),error('InvalidModel'));
  assert.throws(()=>exportCoreCommerceFormalTemporalV1(sources,{...capture},semantics,semantic,binding,assembly!),
   error('ForeignOwner'));
 }finally{
  assembly?.close();stage.dispose(source);semantics.dispose(semantic);sources.dispose(capture);
  rmSync(scratch,{recursive:true,force:true});
 }
});
