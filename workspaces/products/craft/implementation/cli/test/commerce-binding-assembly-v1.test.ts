/** Requirements-only original late-binding assembly custody. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCommerceTechnicalModelOwnerV5} from '../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../src/profile-engine/family-v5.js';
import {createCommerceBindingAssemblyOwnerV1,assertCommerceBindingAssemblyOwnerV1} from '../src/commerce/commerce-binding-assembly-v1.js';
import {projectCoreServiceTopologyV1} from '../src/generic/core-topology-bridge.js';
import {checkCoreApplicationProfileSelectionV1} from '../src/generic/core-application-family.js';

const candidate=fileURLToPath(new URL('../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');
const code=(name:string)=>(error:any)=>error?.diagnostics?.[0]?.code===name;

test('only the original selected Core application issues a current requirements assembly',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-binding-assembly-')),sourceRoot=path.join(root,'source');cpSync(candidate,sourceRoot,{recursive:true});
 const sources=createCoreCommerceSourceOwner(),source=sources.prepare(sourceRoot);
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(source);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(sourceRoot,'profiles/implementation.alch');
 const families=createCommerceFamilyOwnerV5(models);
 let owner:any;
 try{
  owner=createCommerceBindingAssemblyOwnerV1(sources,source,semantics,semantic,models,model,families);
  assertCommerceBindingAssemblyOwnerV1(owner);
  const assembly=owner.assembly(),inspection=owner.inspect(assembly),family=owner.family(assembly);
  assert.equal(inspection.selection.services.length,5);
  assert.equal(inspection.selection.native_requirements.length,10);
  assert.equal(inspection.selected_family_sha256,families.inspect(family).family_sha256);
  assert.equal(inspection.native_basis_qualified,false);
  assert.equal(inspection.imported_output_qualified,false);
  assert.equal(inspection.bound_application_qualified,false);
  assert.equal(Object.isFrozen(inspection),true);
  assert.throws(()=>owner.inspect({...assembly}),code('ForeignOwner'));
  assert.throws(()=>owner.family({...assembly}),code('ForeignOwner'));
  assert.throws(()=>assertCommerceBindingAssemblyOwnerV1({...owner}),code('ForeignOwner'));
  const otherModels=createCommerceTechnicalModelOwnerV5(),otherFamilies=createCommerceFamilyOwnerV5(otherModels);
  assert.throws(()=>createCommerceBindingAssemblyOwnerV1(sources,source,semantics,semantic,models,model,otherFamilies),code('ForeignOwner'));
  const selected=JSON.parse(readFileSync(path.join(sourceRoot,'profiles/selection.json'),'utf8'));
  const topology=projectCoreServiceTopologyV1(sources,source,semantics,semantic),technical=models.inspect(model),where={path:'profiles/selection.json',start:0,end:0};
  assert.throws(()=>checkCoreApplicationProfileSelectionV1({...selected,selection_mapping:'Other.Mapping'},technical,topology,where),code('InvalidContract'));
  assert.throws(()=>checkCoreApplicationProfileSelectionV1({...selected,services:['other']},technical,topology,where),code('InvalidContract'));
  const file=path.join(sourceRoot,'profiles/selection.json');writeFileSync(file,readFileSync(file,'utf8')+'\n');
  assert.throws(()=>models.assertCurrent(model),code('StaleOwner'));
  assert.throws(()=>families.assertCurrent(family),code('StaleOwner'));
  assert.throws(()=>owner.assertCurrent(assembly),code('StaleOwner'));
 }finally{rmSync(root,{recursive:true,force:true});}
});
