import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCommerceTechnicalModelOwnerV5} from '../../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../../src/profile-engine/family-v5.js';
import {projectCoreServiceTopologyV1} from '../../src/generic/core-topology-bridge.js';
import {checkCoreApplicationProfileSelectionV1,selectCoreApplicationFamilyV1} from '../../src/generic/core-application-family.js';

const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');

test('original application selection binds checked topology to typed application-family requirements',async()=>{
 const sources=createCoreCommerceSourceOwner(),source=sources.prepare(candidate);
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(source);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch');
 const families=createCommerceFamilyOwnerV5(models);
 try{
  const result=selectCoreApplicationFamilyV1(sources,source,semantics,semantic,models,model,families),selected=result.selection;
  assert.equal(selected.application,'Shop.Application.Ecommerce');
  assert.equal(selected.services.length,5);
  assert.equal(selected.parameters.tablePrefix,'shop_');
  assert.equal(selected.native_requirements.length,10);
  assert.equal(families.inspect(result.family).descriptor.scope.kind,'application');
  assert.deepEqual(JSON.parse(JSON.stringify(families.inspect(result.family).descriptor.scope.targets)),[{module:'Shop.Application',role:'Interface',name:'Ecommerce'}]);
  assert.equal(selected.qualification,'original-application-selected-family-requirements-only;native-and-runtime-admission-not-established');
  assert.equal(selected.authority_effect,'none');
  assert.equal(Object.isFrozen(selected),true);

  const topology=projectCoreServiceTopologyV1(sources,source,semantics,semantic),technical=models.inspect(model);
  const raw=JSON.parse(readFileSync(new URL('../../../../../../../examples/ecommerce-target-candidate/profiles/selection.json',import.meta.url),'utf8'));
  const where={path:'profiles/selection.json',start:0,end:0};
  // A distinct valid table prefix is a legitimate new profile variant; the
  // original-source selector still selects the captured source bytes above.
  assert.deepEqual(checkCoreApplicationProfileSelectionV1({...raw,parameters:{...raw.parameters,tablePrefix:'other_'}},technical,topology,where).tablePrefix,'other_');
  assert.throws(()=>checkCoreApplicationProfileSelectionV1({...raw,selection_mapping:'Wrong.Mapping'},technical,topology,where),/InvalidContract/);
  assert.throws(()=>checkCoreApplicationProfileSelectionV1({...raw,services:['orders']},technical,topology,where),/InvalidContract/);
  assert.throws(()=>checkCoreApplicationProfileSelectionV1({...raw,parameters:{...raw.parameters,requestBytes:8192}},technical,topology,where),/InvalidContract/);
  families.dispose(result.family);
 }finally{models.dispose(model);semantics.dispose(semantic);sources.dispose(source);}
});
