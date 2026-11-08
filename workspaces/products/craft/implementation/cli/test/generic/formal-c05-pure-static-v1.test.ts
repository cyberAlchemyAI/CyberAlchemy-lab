/** Lightweight checked-contract smoke for the cumulative C05 pure chain.
 * This does not replace original-owner reference/native parity.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../../src/profile-engine/contracts.js';
import {createGenericSourceComputation} from '../../src/generic/pure-source-stage.js';
import {deriveGenericComputationEnvironment} from '../../src/commerce/commerce-computation-environment.js';
import {evaluateGenericPureExpressionFormalSliceV1} from '../../src/generic/formal-pure-expression-v1.js';

const root=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const dir=path.join(root,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C05');
const source=readFileSync(path.join(dir,'request.alch'),'utf8');
const limits=JSON.parse(readFileSync(path.join(dir,'profile.json'),'utf8')).limits;
const oracle=JSON.parse(readFileSync(path.join(dir,'oracle-v1.json'),'utf8'));
const app='module CraftGenerated.Root version 1\ninterface Application:\n'+
 '  kind application-composition\n  source business.alch\n'+
 '  computation-bounds contracts/bounds.json\n';
const texts=[{path:'application.alch',text:app},{path:'business.alch',text:source}];
const sha='a'.repeat(64);

test('C05 checked Mapping/Policy/collection source reaches frozen decision values',()=>{
 const contract=createGenericSourceComputation(texts,'ReviewDesk.ToDecision',limits).contract;
 const layout=deriveGenericComputationEnvironment(contract);
 for(const flagged of [false,true]){
  const request={...structuredClone(oracle.positive_input),flagged};
  const witness=evaluateGenericPureExpressionFormalSliceV1({contract,
   expression_types:layout.expressions,policy_actions:layout.policy_actions,
   source_capture_sha256:sha,contract_sha256:dataDigest(contract),
   executable_semantics_sha256:sha,code_epoch_sha256:sha},undefined,
   new Uint8Array(Buffer.from(JSON.stringify({request}))));
  assert.equal(witness.source_binding,'caller-context-unverified');
  assert.equal(witness.input_mode,'same-account-wire-input');
  assert.equal(witness.result.ok,true);
  if(witness.result.ok){
   const decision=JSON.parse(Buffer.from(witness.result.wire_hex,'hex').toString());
   assert.deepEqual(decision,{approved:true,decisionId:'23',items:[request.items[2],request.items[3],request.items[0]],
    scores:['4','8','8'],total:flagged?'30':'20',result:{tag:'Scored',fields:{total:flagged?'30':'20'}},
    note:{manual:null}});
   assert.ok(Number.isSafeInteger(witness.result.fuel_used));
  }
 }
});
