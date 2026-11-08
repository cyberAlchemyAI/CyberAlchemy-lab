/** Pure enforcement through the existing source/domain/kernel owners.
 * Open Questions: docs/POLICY-ENFORCEMENT.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createGenericSemanticOwner} from '../../src/generic/semantic-reconstruction.js';
import {createGenericComputationDomainOwner} from '../../src/generic/computation-domain.js';
import {createGenericSourceComputation} from '../../src/generic/pure-source-stage.js';
import {evaluateGenericComputationObserved} from '../../src/commerce/commerce-computation-evaluate.js';
import {deriveGenericComputationEnvironment} from '../../src/commerce/commerce-computation-environment.js';
import {lowerOperationContract} from '../../src/generic/pure-operation.js';
import {createCoreGenericEffectContracts} from '../../src/commerce/commerce-core-role-contracts.js';
import {createCoreGenericComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.js';
import {GENERIC_VALUE_CAPABILITIES} from '../../src/generic/composition-capabilities.js';

const limits={max_input_bytes:65536,max_output_bytes:65536,max_value_bytes:32768,max_items:100,max_iterations:100,max_ast_nodes:4096,max_ast_depth:64,max_call_depth:32,fuel:200000};
const source=`module EligibilityTest version 1
enum Reason:
  value Stale wire "source-stale"
  value Denied wire "preference-denied"
enum Admission:
  variant Allow
  variant Reject reason Reason
calculation Allowed:
  pure
  result Admission
  expression Admission.Allow()
calculation Rejected:
  pure
  input reason Reason
  result Admission
  expression Admission.Reject(reason=reason)
policy Eligibility:
  input current Bool
  input permitted Bool
  input divisor UInt64
  result Admission
  ordered-cases:
    stale when not current -> Rejected(reason=Reason.Stale)
    denied when not permitted -> Rejected(reason=Reason.Denied)
    evaluated when 1 / divisor > 0 -> Allowed()
    otherwise -> Allowed()
operation Update:
  input current Bool
  input permitted Bool
  input divisor UInt64
  output Bool
  enforce Eligibility(current=current,permitted=permitted,divisor=divisor)
  return current
interface Application:
  kind application-composition
  computation-bounds contracts/bounds.json
`;
const sources=(text=source)=>[{path:'business.alch',text}];
const compile=(text=source,l=limits)=>createGenericSourceComputation(sources(text),'EligibilityTest.Update',l).contract;
async function domainFixture(text=source,l=limits){
 const directory=mkdtempSync(path.join(tmpdir(),'craft-enforce-pure-'));
 try{
  mkdirSync(path.join(directory,'contracts'));
  writeFileSync(path.join(directory,'business.alch'),text);
  writeFileSync(path.join(directory,'contracts/bounds.json'),JSON.stringify({schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits:l}}));
  const sourceOwner=createCoreCommerceSourceOwner(),capture=sourceOwner.prepare(directory,'business.alch'),semantics=createGenericSemanticOwner(sourceOwner),semantic=await semantics.check(capture),owner=await createGenericComputationDomainOwner(sourceOwner,capture,semantics,semantic),contract=compile(text,l),handle=owner.check(contract);
  return {contract,run:(input:unknown)=>evaluateGenericComputationObserved(owner,handle,new Uint8Array(Buffer.from(JSON.stringify(input)))),close:()=>rmSync(directory,{recursive:true,force:true})};
 }catch(error){rmSync(directory,{recursive:true,force:true});throw error;}
}
const value=(result:ReturnType<typeof evaluateGenericComputationObserved>['result'])=>{assert.equal(result.ok,true);if(!result.ok)assert.fail();return JSON.parse(Buffer.from(result.wire).toString('utf8'));};

test('EN03 lowers one Policy call into a typed let and exhaustive finite matches',()=>{
 const contract=compile();assert.equal(contract.expression.op,'let');deriveGenericComputationEnvironment(contract);
 const pending:unknown[]=[contract.expression];let policyCalls=0,matches=0;
 while(pending.length){const v=pending.pop();if(!v||typeof v!=='object')continue;if('op'in v){if(v.op==='call'&&'declaration'in v&&v.declaration==='EligibilityTest.Eligibility')policyCalls++;if(v.op==='match_variant')matches++;}pending.push(...Object.values(v));}
 assert.equal(policyCalls,1);assert.equal(matches,2);
});
test('EN03 actual source-bound pure execution preserves first rejection and skips later failing predicate',async()=>{
 const f=await domainFixture();try{
  for(const [input,expected]of [[{current:false,permitted:false,divisor:'0'},'source-stale'],[{current:true,permitted:false,divisor:'0'},'preference-denied']] as const){
   const observed=f.run(input);assert.deepEqual(value(observed.result),{tag:'Rejected',fields:{code:expected}});
   const selected=observed.policy_decisions.filter(x=>x.policy==='EligibilityTest.Eligibility');assert.equal(selected.length,1);assert.equal(selected[0]!.invocation_entered,true);
  }
  const observed=f.run({current:true,permitted:true,divisor:'1'});assert.deepEqual(value(observed.result),{tag:'Returned',fields:{value:true}});assert.equal(observed.policy_decisions.filter(x=>x.policy==='EligibilityTest.Eligibility').length,1);
 }finally{f.close();}
});
test('EN03 computation errors remain original faults rather than business rejection',async()=>{
 const f=await domainFixture();try{
  const observed=f.run({current:true,permitted:true,divisor:'0'});assert.equal(observed.result.ok,false);if(observed.result.ok)assert.fail();assert.equal(observed.result.error.code,'DivideByZero');
  const bad=f.run({current:true,permitted:true,divisor:'not-a-number'});assert.equal(bad.result.ok,false);
 }finally{f.close();}
});
test('EN03 multiple reached enforcement sites evaluate once each and first rejection stops the next site',async()=>{
 const text=source.replace('  return current','  enforce Eligibility(current=current,permitted=permitted,divisor=divisor)\n  return current'),f=await domainFixture(text);try{
  const denied=f.run({current:false,permitted:true,divisor:'0'});assert.deepEqual(value(denied.result),{tag:'Rejected',fields:{code:'source-stale'}});assert.equal(denied.policy_decisions.filter(x=>x.policy==='EligibilityTest.Eligibility').length,1);
  const allowed=f.run({current:true,permitted:true,divisor:'1'});assert.deepEqual(value(allowed.result),{tag:'Returned',fields:{value:true}});assert.equal(allowed.policy_decisions.filter(x=>x.policy==='EligibilityTest.Eligibility').length,2);
 }finally{f.close();}
});
test('EN03 generated binders cannot capture an authored parameter or continuation',async()=>{
 const text=source.replace('operation Update:\n','operation Update:\n  input GeneratedEnforce0 Bool\n').replace('  return current','  return GeneratedEnforce0'),f=await domainFixture(text);try{
  assert.equal(f.contract.expression.op,'let');if(f.contract.expression.op==='let')assert.notEqual(f.contract.expression.binding.name,'GeneratedEnforce0');
  assert.deepEqual(value(f.run({GeneratedEnforce0:false,current:true,permitted:true,divisor:'1'}).result),{tag:'Returned',fields:{value:false}});
 }finally{f.close();}
});
test('EN03 lowers only the actual finite source-derived Policy result and retains construction bounds',()=>{
 const raw=sources(),base=createCoreGenericComputationContract(raw,'EligibilityTest.Allowed',limits),plan=createCoreGenericEffectContracts(raw,[]).find(x=>x.operation.name==='Update')!;
 const tampered=structuredClone(plan),step=tampered.body[0]!;assert.equal(step.kind,'enforce-policy');if(step.kind!=='enforce-policy')return;
 (step.rejections[0] as {code:string}).code='a-different-code';assert.throws(()=>lowerOperationContract(base,tampered,['EligibilityTest.Update']),/rejection table differs/);
 assert.throws(()=>compile(source,{...limits,max_ast_nodes:8}),/bound/);
});
test('EN03 sequential enforcement shares the original total fuel allowance',async()=>{
 const first=await domainFixture();let used:number;try{const observed=first.run({current:true,permitted:true,divisor:'1'}).result;assert.equal(observed.ok,true);used=observed.fuel_used;}finally{first.close();}
 const text=source.replace('  return current','  enforce Eligibility(current=current,permitted=permitted,divisor=divisor)\n  return current'),f=await domainFixture(text,{...limits,fuel:used!+1});try{
  const observed=f.run({current:true,permitted:true,divisor:'1'}).result;assert.equal(observed.ok,false);if(observed.ok)assert.fail();assert.equal(observed.error.code,'ResourceLimit');assert.equal(observed.fuel_used,used!+1);
 }finally{f.close();}
});
test('EN03 conditional enforcement runs only at the reached original source site',async()=>{
 const text=source.replace('  enforce Eligibility(current=current,permitted=permitted,divisor=divisor)\n  return current','  when current:\n    enforce Eligibility(current=current,permitted=permitted,divisor=divisor)\n  otherwise:\n    return false\n  return current'),f=await domainFixture(text);try{
  const skipped=f.run({current:false,permitted:false,divisor:'0'});assert.deepEqual(value(skipped.result),{tag:'Returned',fields:{value:false}});assert.equal(skipped.policy_decisions.length,0);
  const reached=f.run({current:true,permitted:false,divisor:'0'});assert.deepEqual(value(reached.result),{tag:'Rejected',fields:{code:'preference-denied'}});assert.equal(reached.policy_decisions.filter(x=>x.policy==='EligibilityTest.Eligibility').length,1);
 }finally{f.close();}
});
test('EN03 original public generation emits pure enforcement with reference/native parity',async()=>{
 const directory=mkdtempSync(path.join(tmpdir(),'craft-enforce-pure-generated-'));try{
  // The public application composer supplies its own root Interface. The
  // original business file contains business declarations only.
  mkdirSync(path.join(directory,'contracts'));writeFileSync(path.join(directory,'business.alch'),source.slice(0,source.indexOf('interface Application:')));
  writeFileSync(path.join(directory,'contracts/bounds.json'),JSON.stringify({schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits}}));
  const profile=path.join(directory,'profile.json'),selection={schema_version:'craft.generic-pure-profile/v1-candidate',id:'node-bounded-values',target:'node-esm',capabilities:[...GENERIC_VALUE_CAPABILITIES].filter(x=>x!=='operation-policy-enforcement' as string),limits};
  writeFileSync(profile,JSON.stringify(selection));
  await assert.rejects(()=>createGenericCompositionOwner().prepare({sourcePath:path.join(directory,'business.alch'),profilePath:profile}),/operation-policy-enforcement/);
  writeFileSync(profile,JSON.stringify({...selection,capabilities:[...selection.capabilities,'operation-policy-enforcement']}));
  const owner=createGenericCompositionOwner(),handle=await owner.prepare({sourcePath:path.join(directory,'business.alch'),profilePath:profile}),review=owner.review(handle,'enforcement-focused-local');
  owner.accept(handle,{decision_id:'enforcement-focused-local',owner:'enforcement-focused-local',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,'decision.json'));
  const outputDirectory=path.join(directory,'generated');owner.generate(handle,{operation:'EligibilityTest.Update',outputDirectory});
  const generated=await import(pathToFileURL(path.join(outputDirectory,'operation.mjs')).href);
  for(const input of [{current:false,permitted:false,divisor:'0'},{current:true,permitted:false,divisor:'0'},{current:true,permitted:true,divisor:'1'},{current:true,permitted:true,divisor:'0'}]){
   const wire=new Uint8Array(Buffer.from(JSON.stringify(input))),reference=owner.evaluateReference(handle,{operation:'EligibilityTest.Update'},wire),actual=generated.evaluate(wire);
   assert.deepEqual(actual,reference,'actual generated evaluator matches value/fault and original shared fuel');
  }
 }finally{rmSync(directory,{recursive:true,force:true});}
});
