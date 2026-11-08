/** Focused checked-source admission, not generated/runtime proof.
 * Open Questions: docs/POLICY-ENFORCEMENT.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkCoreGenericOperationSources} from '../../src/commerce/commerce-core-flow-operation.js';
import {isPolicyRejectionCode} from '../../src/commerce/commerce-policy-enforcement.js';

export const admissionSource=`module AdmissionTest version 1
enum Code:
  value Stale wire "source-stale"
  value Denied wire "preference-denied"
enum Admission:
  variant Allow
  variant Reject reason Code
calculation AllowUpdate:
  pure
  result Admission
  expression Admission.Allow()
calculation RejectUpdate:
  pure
  input reason Code
  result Admission
  expression Admission.Reject(reason=reason)
policy Eligibility:
  input current Bool
  result Admission
  ordered-cases:
    stale when not current -> RejectUpdate(reason=Code.Stale)
    otherwise -> AllowUpdate()
operation Update:
  input current Bool
  output Bool
  enforce Eligibility(current=current)
  return current
interface Application:
  kind application-composition
  computation-bounds contracts/bounds.json
`;
const check=(text=admissionSource)=>checkCoreGenericOperationSources([{path:'admission.alch',text}]);
test('EN01 explicit FailureCode validator agrees with existing schemas and boundaries',()=>{
 for(const name of ['commerce-effects-v1','generic-computation-v1','generic-transaction-v1','commerce-values-v1']){
  const s=JSON.parse(readFileSync(new URL('../../contracts/'+name+'.schema.json',import.meta.url),'utf8')).$defs.FailureCode;
  assert.equal(s.maxLength,128);assert.equal(s.pattern,'^[A-Za-z_][A-Za-z0-9_-]*$');
 }
 for(const good of ['A','_','a'.repeat(128),'source-stale'])assert.equal(isPolicyRejectionCode(good),true);
 for(const bad of ['','a'.repeat(129),'1bad','bad.code','bad code','é'])assert.equal(isPolicyRejectionCode(bad),false);
});
test('EN02 source yields one checked typed Policy enforcement with finite original codes',()=>{
 const op=check().operations.find(x=>x.name==='AdmissionTest.Update')!;const step=op.body[0]!;
 assert.equal(step.kind,'enforce-policy');if(step.kind!=='enforce-policy')return;
 assert.equal(step.policy,'AdmissionTest.Eligibility');assert.equal(step.result_enum,'AdmissionTest.Admission');assert.equal(step.reason_enum,'AdmissionTest.Code');
 assert.deepEqual(step.rejections.map(x=>x.code),['source-stale','preference-denied']);
 assert.equal(step.value.type.kind,'enum');assert.equal(step.source_site.path,'admission.alch');assert.ok(step.source_site.end>step.source_site.start);
});
test('EN02 rejects non-Policy callable, implicit wires, invalid wires and extra result fields',()=>{
 for(const text of [admissionSource.replace('enforce Eligibility(current=current)','enforce AllowUpdate()'),admissionSource.replace(' wire "source-stale"',''),admissionSource.replace('"source-stale"','"1bad"'),admissionSource.replace('variant Allow','variant Allow extra Bool')])assert.throws(()=>check(text));
});
test('EN02 accepts renamed nominal admission types and keeps ordinary guards supported',()=>{
 assert.doesNotThrow(()=>check(admissionSource.replaceAll('AdmissionTest','OtherDomain').replaceAll('Admission','Verdict')));
 const inline=admissionSource.replace('enforce Eligibility(current=current)','on not current reject source-stale');assert.equal(check(inline).operations[0]!.body[0]!.kind,'conditional');
});
