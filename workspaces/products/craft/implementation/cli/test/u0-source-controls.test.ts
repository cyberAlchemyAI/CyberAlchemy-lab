import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
// Actual compiled frontend/source projections and independently checked Core DTOs.
// No selected/native custody is asserted by these source-component controls.
// Open Questions: V02 CONTEXT; installed carrier coverage remains H01/V03.
const core=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),repo=path.resolve(core,'../../../../..'),alch=path.join(repo,'language/capabilities/alchlang/plans/general-compiler-v1/implementation'),out=path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/V02'),run=fs.mkdtempSync(path.join(out,'source-')),original=fs.readFileSync(path.join(core,'test/profile-engine/fixtures/u0-v2/business.alch'),'utf8'),observed:any[]=[],sha=(v:string)=>crypto.createHash('sha256').update(v).digest('hex');
const resolver=await import(pathToFileURL(path.join(alch,'dist/business-authoring-resolve.js')).href),carrier=await import(pathToFileURL(path.join(alch,'dist/business-authoring-carriers.js')).href),api=(await import(pathToFileURL(path.join(core,'dist/index.js')).href)).profileEngine;
function lower(name:string,text:string){const root=path.join(run,name);fs.mkdirSync(root);fs.writeFileSync(path.join(root,'business.alch'),text);const business=resolver.prepareBusinessSpecFileV2(root,'business.alch'),lowered=carrier.lowerDirectBusinessV2(business);const checked=api.checkCoreDirectBusinessRecipeV2({source:business.source,spec:business.data,executable:lowered.executable,assurance:lowered.assurance});return {business,lowered,checked};}
const optional=`
definition Eligibility:
  requirement Processing
  input item Submission
  meaning "Supplied eligibility."
  boolean-field item.verified

formal-claim EligibilityClaim version 1:
  requirement Processing
  supersedes none
  profile fol-core/1-candidate
  sort SubmissionValue interpreted-as Submission
  predicate Eligible(SubmissionValue) defined-by Eligibility
  constant current: SubmissionValue
  proposition Eligible(current)
  ceiling "One supplied flag; no proof."
  subject CanProcess
  subject Process
`;
test('capture-only, claim-only and executable changes retire precisely different source subjects',()=>{
 const base=lower('baseline',original),space=lower('whitespace',original+'\n# physical capture changes\n'),claims=lower('claims',original+optional),claimChange=lower('claim-change',original+optional.replace('proposition Eligible(current)','proposition not Eligible(current)')),meaning=lower('meaning',original.replace('verified Bool','approved Bool').replace('condition item.verified','condition item.approved'));
 assert.deepEqual(space.lowered.executable,base.lowered.executable);assert.deepEqual(space.lowered.assurance,base.lowered.assurance);assert.notEqual(space.business.source.sha256,base.business.source.sha256);
 assert.equal(claims.checked.executable_sha256,base.checked.executable_sha256);assert.notEqual(claims.checked.assurance_sha256,base.checked.assurance_sha256);assert.notEqual(claims.business.source.sha256,base.business.source.sha256);assert.notEqual(meaning.checked.executable_sha256,base.checked.executable_sha256);assert.equal(claimChange.checked.executable_sha256,claims.checked.executable_sha256);assert.notEqual(claimChange.checked.assurance_sha256,claims.checked.assurance_sha256);
 for(const [id,value]of [['baseline',base],['source-whitespace-recapture',space],['claim-only-recapture',claims],['claim-only-change',claimChange],['executable-field-change',meaning]] as const)observed.push({id,source_sha256:value.business.source.sha256,executable_sha256:value.checked.executable_sha256,assurance_sha256:value.checked.assurance_sha256,scope:'actual independently checked source data; no selected/native handle'});
});
test('missing executable declarations and unsupported capability/carrier cannot become a compilable direct cell',()=>{
 const cases:[string,string][]=[['missing-condition',original.replace('  condition item.verified\n','')],['missing-guard',original.replace('  requires CanProcess(item: request)\n','')],['missing-rule',original.replace(/rule CanProcess:[\s\S]*?\n\noperation/,'operation')],['missing-return',original.replace('  returns request\n','')],['protected-entry',original.replace('  permission public','  permission protected')],['nonempty-effects',original.replace('  effects none','  effects write Submission')],['source-carrier-unsupported',JSON.stringify({systemOntology:{},businessModel:{},accepted:true})],['wrong-entry-binding',original.replace('  invokes Process','  invokes Missing')],['wrong-guard-binding',original.replace('requires CanProcess(item: request)','requires CanProcess(other: request)')]];
 for(const [id,text]of cases){assert.notEqual(text,original,id);assert.throws(()=>lower(id,text),undefined,id);observed.push({id,source_sha256:sha(text),result:'rejected by actual frontend/Core source pipeline'});}
 fs.writeFileSync(path.join(run,'source-controls-observation.json'),JSON.stringify({schema_version:'craft.u0-source-controls/v1-candidate',observed,authority_effect:'none',open_questions_ref:'../CONTEXT.md#open-questions'},null,2)+'\n',{flag:'wx'});
});
