/** Original-owner parity of the C05 Mapping/Policy/collection chain.
 * This is deliberately a focused source-bound replay, separate from the
 * lightweight checked-contract diagnostic.
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
import {evaluateGenericComputation} from '../../src/commerce/commerce-computation-evaluate.js';
import {exportCheckedGenericPureExpressionFormalFromWireV1}
 from '../../src/generic/formal-pure-expression-v1.js';

const root=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const contracts=path.join(root,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C05');
const source=readFileSync(path.join(contracts,'request.alch'),'utf8');
const bounds=readFileSync(path.join(contracts,'bounds.json'),'utf8');
const limits=JSON.parse(readFileSync(path.join(contracts,'profile.json'),'utf8')).limits;
const oracle=JSON.parse(readFileSync(path.join(contracts,'oracle-v1.json'),'utf8'));

test('C05 original Mapping/Policy/collection reference matches optional formal wire witness',async()=>{
 const dir=mkdtempSync(path.join(tmpdir(),'craft-c15-c05-pure-'));
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
  const proposal=createGenericSourceComputation(texts,'ReviewDesk.ToDecision',limits).contract;
  const domain=await createGenericComputationDomainOwner(sources,capture,semantics,semantic);
  const handle=domain.check(proposal);
  const inputs:Uint8Array[]=[];
  for(const flagged of [false,true]){
   const request={...structuredClone(oracle.positive_input),flagged};
   inputs.push(new Uint8Array(Buffer.from(JSON.stringify({request}))));
  }
  inputs.push(new Uint8Array(Buffer.from('{"request":{},"request":{}}')));
  inputs.push(new Uint8Array([0xff]));
  for(const wire of inputs){
   const observed=evaluateGenericComputation(domain,handle,wire);
   const formal=exportCheckedGenericPureExpressionFormalFromWireV1(domain,handle,wire);
   assert.equal(formal.source_binding,'original-owner-checked');
   assert.equal(formal.input_mode,'same-account-wire-input');
   const expected=observed.ok?
    {ok:true,wire_hex:Buffer.from(observed.wire).toString('hex'),fuel_used:observed.fuel_used}:
    {ok:false,code:observed.error.code,expression_path:observed.error.expression_path,
     index_path:observed.error.index_path,call_path:observed.error.call_path,
     fuel_used:observed.fuel_used};
   assert.deepEqual(formal.result,expected);
  }
 }finally{rmSync(dir,{recursive:true,force:true});}
});
