import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
import {createCommerceWorkflowCoordinationBindingV1} from '../../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {createCommerceIdentityCallOwner} from '../../src/commerce/commerce-identity-call-owner.js';
import {createCommerceWorkflowStepArgumentsOwnerV1,CommerceWorkflowStepArgumentsErrorV1} from '../../src/commerce/commerce-workflow-step-arguments-v1.js';

const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');
test('current checked Workflow step arguments bind to original native callsites and remain inert',async()=>{
 const temp=mkdtempSync(path.join(tmpdir(),'workflow-step-arguments-')),directory=path.join(temp,'native');mkdirSync(directory);
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map(m=>m.path)),texts=captured.files.filter(f=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source);
 const limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout');
 const calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline);
 try{
  const owner=await createCommerceWorkflowStepArgumentsOwnerV1(binding,semantics,semantic,calls,stage,source,domain,baseline,directory);
  owner.assertCurrent();
  assert.throws(()=>owner.inspect({kind:'original-workflow-step-arguments/v1-candidate'}),
   (error:unknown)=>error instanceof CommerceWorkflowStepArgumentsErrorV1&&error.code==='ForeignOwner');
  const fakeResume=Object.freeze({workflow:binding.inspect().workflow.name,assertCurrent(){},dispose(){}});
  assert.throws(()=>owner.evaluate(fakeResume as never,{} as never,{} as never,{} as never),
   (error:unknown)=>Boolean(error&&typeof error==='object'&&
    (error as {code?:string;diagnostics?:readonly {code:string}[]}).code==='ForeignOwner'));
  assert.equal(calls.paths(semantics.inspect(semantic).workflows[0]!).filter(p=>p.startsWith('$.steps[')).length,6);
  owner.dispose();
 }finally{semantics.dispose(semantic);sources.dispose(capture);rmSync(temp,{recursive:true,force:true});}
});
