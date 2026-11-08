/** EN08 compares actual original-kernel business behavior; no simulator.
 * Open Questions: docs/POLICY-ENFORCEMENT.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,mkdirSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createGenericSemanticOwner} from '../../src/generic/semantic-reconstruction.js';
import {createGenericComputationDomainOwner} from '../../src/generic/computation-domain.js';
import {createGenericSourceComputation} from '../../src/generic/pure-source-stage.js';
import {evaluateGenericComputation} from '../../src/commerce/commerce-computation-evaluate.js';
import {crmEligibilityGuards,extractCrmEligibility,inlineCrmEligibility,secondDomain,secondDomainInline,secondDomainLibrary} from './policy-enforcement-fixtures.js';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const crm=path.join(repository,'implementation/craft-ai-reference-apps/crm');
const business=readFileSync(path.join(crm,'journey.alch'),'utf8');
const bounds=readFileSync(path.join(crm,'contracts/bounds.json'),'utf8');
const limits=JSON.parse(readFileSync(path.join(crm,'journey-profile.json'),'utf8')).limits;
const cases=JSON.parse(readFileSync(path.join(crm,'fixtures/journey-cases.json'),'utf8'));
const returned=(value:unknown)=>({tag:'Returned',fields:{value}});
const rejected=(code:string)=>({tag:'Rejected',fields:{code}});
function fixture(source:string,operation:string,library?:string){
 const directory=mkdtempSync(path.join(tmpdir(),'craft-enforcement-equivalence-'));mkdirSync(path.join(directory,'source'));mkdirSync(path.join(directory,'contracts'));
 writeFileSync(path.join(directory,'source/business.alch'),source);writeFileSync(path.join(directory,'contracts/bounds.json'),bounds);
 if(library)writeFileSync(path.join(directory,'source/library.alch'),library);
 writeFileSync(path.join(directory,'application.alch'),'module CraftGenerated.Root version 1\ninterface Application:\n  kind application-composition\n  source source/business.alch\n'+(library?'  source source/library.alch\n':'')+'  computation-bounds contracts/bounds.json\n');
 try{
  const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(directory,'application.alch'),semantics=createGenericSemanticOwner(sources),semantic=semantics.check(capture);
  const texts=sources.inspect(capture).files.filter(x=>x.path.endsWith('.alch')).map(x=>({path:x.path,text:x.text}));
  const contract=createGenericSourceComputation(texts,operation,limits).contract;
  const domain=createGenericComputationDomainOwner(sources,capture,semantics,semantic),handle=domain.check(contract);
  return {evaluate(input:unknown){const result=evaluateGenericComputation(domain,handle,new Uint8Array(Buffer.from(JSON.stringify(input))));return result.ok?{ok:true as const,value:JSON.parse(Buffer.from(result.wire).toString('utf8')),fuel_used:result.fuel_used}:result;},cleanup:()=>rmSync(directory,{recursive:true,force:true})};
 }catch(error){rmSync(directory,{recursive:true,force:true});throw error;}
}
test('EN08 original inline CRM characterization covers all19labelledcases',()=>{
 const original=fixture(inlineCrmEligibility(business),'CrmOperations.PrepareContactUpdate');
 try{for(const row of cases){const result=original.evaluate(row.input);assert.equal(result.ok,row.expected.ok,row.id);if(result.ok)assert.deepEqual(result.value,row.expected.value,row.id);}}
 finally{original.cleanup();}
});
test('EN08 CRM original versus extracted typed Policy retains every labelled case and all12denials',()=>{
 const original=fixture(inlineCrmEligibility(business),'CrmOperations.PrepareContactUpdate'),extracted=fixture(extractCrmEligibility(business),'CrmOperations.PrepareContactUpdate');
 try{
  const observedCodes=new Set<string>();
  for(const row of cases){
   const a=original.evaluate(row.input),b=extracted.evaluate(row.input);
   assert.equal(a.ok,row.expected.ok,row.id);assert.equal(b.ok,a.ok,row.id);
   if(a.ok&&b.ok){assert.deepEqual(a.value,row.expected.value,row.id);assert.deepEqual(b.value,a.value,row.id);if(a.value.tag==='Rejected')observedCodes.add(a.value.fields.code);}
   else if(!a.ok&&!b.ok){assert.equal(b.error.code,a.error.code,row.id);}
  }
  assert.deepEqual([...observedCodes].sort(),crmEligibilityGuards.map(x=>x[1]).sort());
 }finally{original.cleanup();extracted.cleanup();}
});
test('EN08 CRM multiple failures retain first failure and unchanged successful business outputs',()=>{
 const original=fixture(inlineCrmEligibility(business),'CrmOperations.PrepareContactUpdate'),extracted=fixture(extractCrmEligibility(business),'CrmOperations.PrepareContactUpdate');
 try{
  const input=structuredClone(cases[0].input);input.request.sourceCurrent=false;input.request.releaseAllowed=false;input.request.identityVerified=false;input.request.contactAllowed=false;input.request.approval.approved=false;
  for(const expected of ['source-stale','disclosure-denied','identity-unverified','preference-denied','approval-stale']){
   const a=original.evaluate(input),b=extracted.evaluate(input);assert.equal(a.ok,true);assert.equal(b.ok,true);if(!a.ok||!b.ok)throw Error('unexpected computation failure');assert.deepEqual(a.value,rejected(expected));assert.deepEqual(b.value,a.value);
   if(expected==='source-stale')input.request.sourceCurrent=true;else if(expected==='disclosure-denied')input.request.releaseAllowed=true;else if(expected==='identity-unverified')input.request.identityVerified=true;else if(expected==='preference-denied')input.request.contactAllowed=true;
  }
  const happy=extracted.evaluate(cases[0].input);assert.equal(happy.ok,true);if(happy.ok)assert.deepEqual(happy.value,cases[0].expected.value);
 }finally{original.cleanup();extracted.cleanup();}
});
test('EN08 unrelated imported nominal admission types reuse enforce and short-circuit a later fault',()=>{
 const original=fixture(secondDomainInline,'ResearchDesk.Publish',secondDomainLibrary),extracted=fixture(secondDomain,'ResearchDesk.Publish',secondDomainLibrary);
 try{
  for(const [input,expected]of [[{approved:false,divisor:'0'},rejected('approval-needed')],[{approved:true,divisor:'1'},rejected('calculation-rejected')],[{approved:true,divisor:'2'},returned(true)]]as const){const a=original.evaluate(input),b=extracted.evaluate(input);assert.equal(a.ok,true);assert.equal(b.ok,true);if(a.ok&&b.ok){assert.deepEqual(a.value,expected);assert.deepEqual(b.value,a.value);}}
  const a=original.evaluate({approved:true,divisor:'0'}),b=extracted.evaluate({approved:true,divisor:'0'});assert.equal(a.ok,false);assert.equal(b.ok,false);if(!a.ok&&!b.ok){assert.equal(a.error.code,'DivideByZero');assert.equal(b.error.code,a.error.code);}
 }finally{original.cleanup();extracted.cleanup();}
});
