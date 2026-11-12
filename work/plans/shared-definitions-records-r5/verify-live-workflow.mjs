import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import path from 'node:path';
import {main} from '../../../implementation/lab-runtime/alchlang/shared-records/cli.mjs';
import {loadTrust} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {deriveCarryForward} from '../../../implementation/lab-runtime/alchlang/shared-records/carry-forward.mjs';
import {bind} from '../../../implementation/lab-runtime/alchlang/shared-records/snapshots.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),old=path.join(root,'docs/decisions/0076-shared-definitions-records-activation');
const load=f=>JSON.parse(readFileSync(f)),put=(name,value)=>{const f=path.join(here,name);mkdirSync(path.dirname(f),{recursive:true});writeFileSync(f,JSON.stringify(value,null,2)+'\n');return f;};
const trustFile=path.join(here,'runtime-trust.json'),trust=loadTrust(trustFile);
const scope='workspace:cyberalchemy-lab:lab',issuer='principal:lab-shared-operator';
const key=path.join(process.env.HOME,'.config/cyberalchemy-lab/shared-records/operator.pem');
const proposal=load(path.join(old,'source-transition/proposal.json')),approval=load(path.join(old,'source-transition/approval.json')),cut=proposal.source_snapshot_digest;
const original=load(path.join(old,'native-apply.json'));
const carry={original_construction:original.construction,original_native_store:path.join(root,'.local/lab-runtime/shared/native-store'),
 original_operation:original.proposal.proposal_id,original_approval_artifact:original.approval_artifact,
 proposal,approval_artifact:readFileSync(path.join(old,'source-transition/approval.json')).toString('base64')};
const value=await deriveCarryForward(carry,trust,path.join(root,'.local/lab-runtime/shared/snapshots.sqlite'));
assert(value.reviews.every(review=>review.original_cut!==review.current_cut));
const records=[];
async function sealed(operation,input){
 const inputPath=put('.local/'+operation+'-input.json',input);
 const attest=put('.local/'+operation+'-attest.json',{artifact:inputPath,schema:operation,predicate:'qualified-operator-observation',operation,scope,cut});
 const observed=await main(['attest','--file',attest,'--trust',trustFile,'--issuer',issuer,'--key',key]);
 const request=put('.local/'+operation+'-issue.json',{selection_id:operation,operation,scope,cut,originals:[observed]});
 const issued=await main(['issue','--file',request,'--trust',trustFile,'--issuer',issuer,'--key',key]);
 const packet={operation,scope,cut,...issued};records.push({operation,original:observed,issued:packet});return packet;
}
const construction=await sealed('AssessCarriedConstructionEntry',{value});
const request={workspace:path.join(root,'WORKSPACE.json'),catalog:path.join(root,'implementation/lab-workspaces/v2/catalog.json'),
 project:'project:cyberalchemy-v2-to-lab-migration',store:path.join(root,'.local/lab-runtime/shared/current-store'),
 proposal,approval,approval_artifact:carry.approval_artifact,construction,carry_forward:carry};
const requestFile=put('CORRECTED-SOURCE-TRANSITION.json',request);
const applied=await main(['native-apply','--file',requestFile,'--trust',trustFile]);
assert.equal(applied.idempotent,true);
const impact=await main(['impact','--file',path.join(here,'operational/impact.json'),'--trust',trustFile]);
assert(impact.affected.includes('reader:define.catalog-reader'));assert(impact.affected.includes(scope));
const assessmentRequest=load(path.join(here,'operational/assessment.json'));
const results=await main(['assess','--file',path.join(here,'operational/assessment.json'),'--trust',trustFile]);
assert.equal(results.length,4);assert(results.every(x=>x.passed&&x.outcome==='Passed'));
const entry=bind('verified-construction-entry',Buffer.from(construction.artifact,'base64'));
const output=assessmentRequest.output;
const proof=(subject,predicate)=>({subject,scope:'construction',cut,predicate,issuer,
 policy:bind('r5-contract',readFileSync(path.join(here,'CONTRACTS.json'))),
 proof:bind('r5-authorization',readFileSync(path.join(here,'AUTHORIZATION.json')))});
const completion={entry_decision:'GenerationEntryPlanReady',expected_entry:entry,assessed_entry:entry,
 entry_receipt:{entry,selection:value.original.selection,specifications:value.current_specifications,evidence:proof(entry,'construction-entry')},
 expected_source_cut:cut,observed_source_cut:cut,output_manifest:output,assessed_output:output,
 independent_assessment:bind('independent-results',Buffer.from(JSON.stringify(results))),
 independence_review:bind('independent-executor',readFileSync(path.join(root,'implementation/lab-runtime/alchlang/shared-records/qualified_registry_check.py'))),
 required_checks:value.current_obligations,passed_checks:results.filter(r=>r.passed).map(r=>r.specification.obligation),failed_checks:'0',unknown_checks:'0',
 results:results.map(({specification,output,passed})=>({specification,output,passed})),assessment:proof(output,'independent-conformance')};
const completionPacket=await sealed('AssessConstructionCompletion',{value:completion});
const evaluation=await main(['evaluate','--file',put('.local/completion.json',completionPacket),'--trust',trustFile]);
assert.equal(evaluation.result,'ConformancePlanReady');
put('LIVE-WORKFLOW-VERIFICATION.json',{status:'PASS',original_owner_cuts_preserved:true,review_carry_forwards:value.reviews,
 native_exact_operation_replayed:applied.idempotent,impact,independent_checks:results,
 construction_completion:evaluation,receipts:records,canonical_definition_changes:0,Define_authority_changes:0});
console.log(JSON.stringify({status:'PASS',carry_forwards:value.reviews.length,impact_subjects:impact.universe,
 independent_checks:results.length,completion:evaluation.result}));
