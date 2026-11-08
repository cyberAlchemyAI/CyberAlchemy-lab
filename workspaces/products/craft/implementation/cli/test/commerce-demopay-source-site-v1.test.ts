/** Original remote source sites remain source/profile bindings without IO. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
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
import {createCommerceDemoPaySourceSiteOwnerV1,assertCommerceDemoPaySourceSiteOwnerV1} from '../src/commerce/commerce-demopay-source-site-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

test('exact selected DemoPay source calls bind without issuing a native port or effect',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-demopay-sites-')),sourceRoot=path.join(root,'source');
 cpSync(candidate,sourceRoot,{recursive:true});
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(sourceRoot),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map(m=>m.path)),texts=captured.files.filter(f=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(sourceRoot,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(sourceRoot,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(sourceRoot,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models);
 const assemblies=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblies.assembly();
 try{
  assert.throws(()=>createCommerceDemoPaySourceSiteOwnerV1(sources,capture,semantics,semantic,stage,source,plans,assemblies,{...assembly} as any),code('ForeignOwner'));
  const sites=createCommerceDemoPaySourceSiteOwnerV1(sources,capture,semantics,semantic,stage,source,plans,assemblies,assembly);
  assertCommerceDemoPaySourceSiteOwnerV1(sites);
  const captureParent=plans.bindOperation('Payments.DispatchOriginalCapture'),capturePaths=sites.paths(captureParent);
  assert.equal(capturePaths.length,1);
  const captureSite=sites.bind(captureParent,capturePaths[0]!),captureView=sites.inspect(captureSite);
  assert.equal(captureView.target,'Shop.DemoPay.Capture');assert.equal(captureView.method,'Capture');
  assert.equal(captureView.parent_operation,'Payments.DispatchOriginalCapture');
  assert.equal(captureView.source_capture_sha256,captured.capture_sha256);
  assert.equal(captureView.selected_family_sha256,assemblies.inspect(assembly).selected_family_sha256);
  assert.match(captureView.qualification,/no-invocation-frame-intent-port-or-provider-effect/);
  const inspectParent=plans.bindOperation('Payments.ReconcilePayment'),inspectPaths=sites.paths(inspectParent);
  assert.equal(inspectPaths.length,1);
  assert.equal(sites.inspect(sites.bind(inspectParent,inspectPaths[0]!)).target,'Shop.DemoPay.InspectCapture');
  assert.throws(()=>sites.bind(captureParent,'$.body[999].call'),code('UnknownSourceSite'));
  assert.throws(()=>sites.inspect({...captureSite}),code('ForeignSite'));
  assert.throws(()=>sites.assertInvocation(captureSite,{} as any,{} as any),code('ForeignOwner'));
  assert.throws(()=>sites.paths(plans.bindOperation('Orders.PlaceOrder')),code('ForeignParent'));
  const file=path.join(sourceRoot,'profiles/demopay-wire.json'),before=readFileSync(file);
  try{writeFileSync(file,Buffer.from(before).fill(0x20,0,1));assert.throws(()=>sites.inspect(captureSite),code('StaleOwner'));}
  finally{writeFileSync(file,before);}
  assert.throws(()=>sites.inspect(captureSite),code('StaleOwner'));
 }finally{rmSync(root,{recursive:true,force:true});}
});
