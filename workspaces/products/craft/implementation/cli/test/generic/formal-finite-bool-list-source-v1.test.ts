/** Source-bound replay for the smallest all-canonical-input formal domain.
 * Keep this separate from the fast synthetic table tests because source capture
 * and currentness are intentionally expensive.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createGenericSemanticOwner} from '../../src/generic/semantic-reconstruction.js';
import {createGenericComputationDomainOwner} from '../../src/generic/computation-domain.js';
import {createGenericSourceComputation} from '../../src/generic/pure-source-stage.js';
import {exportCheckedGenericFiniteBoolListFormalModelV1} from '../../src/generic/formal-finite-bool-list-v1.js';

const root=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const contracts=path.join(root,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C05');
const limits=JSON.parse(readFileSync(path.join(contracts,'profile.json'),'utf8')).limits;
const bounds=readFileSync(path.join(contracts,'bounds.json'),'utf8');
const source=`module Tiny version 1

calculation Keep:
  pure
  input values List<Bool,2>
  result List<Bool,2>
  expression map(values,item:Bool => item)
`;

test('original checked Bool-list calculation exhaustively agrees with formal wire model',async()=>{
 const dir=mkdtempSync(path.join(tmpdir(),'craft-c15-bool-list-'));
 try{
  mkdirSync(path.join(dir,'source'));mkdirSync(path.join(dir,'contracts'));
  writeFileSync(path.join(dir,'source/business.alch'),source);
  writeFileSync(path.join(dir,'contracts/bounds.json'),bounds);
  writeFileSync(path.join(dir,'application.alch'),
   'module CraftGenerated.Root version 1\ninterface Application:\n'+
   '  kind application-composition\n  source source/business.alch\n'+
   '  computation-bounds contracts/bounds.json\n');
  const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(dir,'application.alch');
  const semantics=createGenericSemanticOwner(sources),semantic=await semantics.check(capture);
  const texts=sources.inspect(capture).files.filter(row=>row.path.endsWith('.alch'))
   .map(row=>({path:row.path,text:row.text}));
  const proposal=createGenericSourceComputation(texts,'Tiny.Keep',limits).contract;
  const domain=await createGenericComputationDomainOwner(sources,capture,semantics,semantic);
  const handle=domain.check(proposal);
  const model=exportCheckedGenericFiniteBoolListFormalModelV1(domain,handle);
  assert.equal(model.source_binding,'original-owner-checked-reference-and-formal-parity');
  assert.equal(model.observations.length,7);
  for(const row of model.observations){
   assert.equal(row.result.ok,true);
   if(row.result.ok)
    assert.deepEqual(JSON.parse(Buffer.from(row.result.wire_hex,'hex').toString()),row.values);
  }
 }finally{rmSync(dir,{recursive:true,force:true});}
});
