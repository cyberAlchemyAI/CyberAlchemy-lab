/** Original-byte observations and calls into checked AlchLang. No domain expression interpreter. */
import path from 'node:path';
import {openJsonPort} from '../../../../../../../implementation/artifact-runtime/json-pipe.mjs';
import {inspectPackage,materializePackage} from '../runtime/package.mjs';
import {decodeOriginalJson} from '../runtime/wire.mjs';
import {transition,variant,canonical} from '../runtime/runtime.mjs';
import {evaluate,selectors,facts,authorValue} from './native.mjs';
import {document,documentMap,verifyBindings,binding} from './journal.mjs';
const genericPort=path.resolve(import.meta.dirname,'../../../../../../../implementation/artifact-runtime/json-port.py');
export const unobservedUse=()=>({outcome:'not-observed',obligations:[],claim_ceiling:'No matching package observation; no use completeness established.'});
export const observedHead=(current,cut)=>({session_ref:current.session_id,revision:current.revision,source_cut:cut,closed:current.closed});
export function addDocument(documents,value,{raw=false}={}){const d=document(raw?Buffer.from(value):Buffer.from(canonical(value)));if(!documents.some(x=>x.binding.path===d.binding.path))documents.push(d);return d.binding;}
export async function expectedReports(current,cut,documents){const snapshot=addDocument(documents,current),subject=await evaluate(selectors.subject,{observed:observedHead(current,cut),snapshot,intended_use:current.scope.intended_use});return {subject,candidate_entries:addDocument(documents,current.materialization_selection),candidate_count:await authorValue('Define.Work.SelectedCandidateCount',current),evidence_entries:addDocument(documents,current.evidence_bindings),evidence_count:String(current.evidence_bindings.length)};}
export async function observePackage(current,actor,wantedUse,{directory=null,memoryMembers=null,capture=null}={}){
 const result=await inspectPackage(directory,{observe:true,memoryMembers,capture,deriveReadiness:true});const {observation}=result;
 await transition(current,{command_id:'observe-define-package',session_id:current.session_id,project:current.scope.project,work:current.scope.work,actor,expected_revision:current.revision,payload:variant('Confirm',{package_sha256:observation.package_binding.sha256,request_sha256:observation.request_binding.sha256,actor})},observation);
 const key=await evaluate(selectors.readinessKey,{wanted_use:wantedUse}),nativeUse=result.readiness[key];if(!nativeUse)throw Error('missing-native-use-observation');
 const count=await authorValue('Define.Work.SelectedCandidateCount',current),required=await evaluate(selectors.proofRequired,{wanted_use:wantedUse,selected_candidates:count});
 if(required)await materializePackage(directory,null,{verifyOnly:true,memoryMembers});
 return {...result,native_use:nativeUse,declared_native_use:result.declared_readiness[key],materialization_verified:required};
}
export async function assessmentInput(current,check,documents,packageObservation=null){
 const snapshot=addDocument(documents,current),proof=packageObservation?.derivation,binding_derivation=proof?{schema_version:'cal.define.use-readiness-derivation/v1',request:addDocument(documents,Buffer.from(proof.request_bytes_base64,'base64'),{raw:true}),capture:addDocument(documents,Buffer.from(proof.capture_bytes_base64,'base64'),{raw:true}),application_checks:addDocument(documents,proof.application_report),field_observations:addDocument(documents,proof.field_observations),declared:packageObservation.declared_native_use,derived:packageObservation.native_use}:null;
 return {value:check,observed_snapshot:snapshot,observed_facts:await facts(current),selected_candidates:await authorValue('Define.Work.SelectedCandidateCount',current),applications:await authorValue('Define.Work.ParameterApplicationCount',current),materialization_verified:packageObservation?.materialization_verified??false,native_use:packageObservation?.native_use??unobservedUse(),binding_derivation,package_members:null};
}
export function membersFromBinding(selected,bytes){if(!selected)throw Error('actual-package-proof-required');const rows=decodeOriginalJson(bytes.get(selected.path));if(!Array.isArray(rows)||rows.length>100)throw Error('package-proof-member-bound');const members=new Map();for(const row of rows){verifyBindings(row.binding,bytes);if(members.has(row.path))throw Error('duplicate-package-proof-member');members.set(row.path,bytes.get(row.binding.path));}return members;}
export function attachMembers(members,documents){return addDocument(documents,Array.from(members,([name,raw])=>({path:name,binding:addDocument(documents,raw,{raw:true})})));}
async function pointer(port,raw,selector){const value=decodeOriginalJson(raw);return port.request({operation:'observe-pointer',value,selector});}
export async function checkedFields(command,input,bytes){
 const port=openJsonPort(genericPort);
 try{
  if(command==='contribute')return {...input,source:await pointer(port,bytes.get(input.value.source_binding.path),input.value.source_selector),target:await pointer(port,bytes.get(input.draft_document.path),input.value.target_selector)};
  const manifest=decodeOriginalJson(bytes.get(input.manifest.path));if(!Array.isArray(manifest.requirements)||!Array.isArray(manifest.contributions))throw Error('field-manifest-shape');verifyBindings(manifest,bytes);
  await evaluate(selectors.manifest,{value:{schema_version:manifest.schema_version,draft_document:manifest.draft_document,requirement_count:String(manifest.requirements.length),contribution_count:String(manifest.contributions.length)}});
  const draft=bytes.get(manifest.draft_document.path),requirements=[];
  for(const value of manifest.requirements){const target=await pointer(port,draft,value.target_selector);await evaluate(selectors.requirement,{value,target});requirements.push(binding(Buffer.from(value.target_selector)).sha256);}
  const contributions=[];for(const value of manifest.contributions){const field_key=binding(Buffer.from(value.target_selector)).sha256,source=await pointer(port,bytes.get(value.source_binding.path),value.source_selector),target=await pointer(port,draft,value.target_selector);contributions.push(await evaluate(selectors.resolution,{value,field_key,source,target}));}
  return {...input,requirements,contributions};
 }finally{await port.close();}
}
export async function typedHandoffInput(current,cut,input,documents,actor){
 const bytes=verifyBindings(input.value,documents),reports={inventory:decodeOriginalJson(bytes.get(input.value.candidate_inventory.path)),obligations:decodeOriginalJson(bytes.get(input.value.open_obligations.path)),evidence:decodeOriginalJson(bytes.get(input.value.session.note_manifest.path)),assessment:decodeOriginalJson(bytes.get(input.value.preparation_assessment.path))};verifyBindings(reports,bytes);
 const expected=await expectedReports(current,cut,documents);
 // Pure early refusal only. Publication still requires the independently observed proof below.
 await evaluate(selectors.handoff,{...input,reports,expected,recomputed:reports.assessment.assessment,effective_check:reports.assessment.check,actual_native_use:reports.assessment.native_use,actual_binding_derivation:reports.assessment.binding_derivation});
 const members=membersFromBinding(input.package_members,bytes),observation=await observePackage(current,actor,reports.assessment.check.requested_use,{memoryMembers:members});
 if(input.value.package_binding.sha256!==observation.observation.package_binding.sha256||input.value.request_binding.sha256!==observation.observation.request_binding.sha256)throw Error('handoff-package-proof-mismatch');
 const args={...await assessmentInput(current,reports.assessment.check,documents,observation),package_members:input.package_members},recomputed=await evaluate(selectors.assess,args),effective_check=await evaluate(selectors.effective,{value:reports.assessment.check,observed_facts:args.observed_facts,selected_candidates:args.selected_candidates,applications:args.applications,materialization_verified:args.materialization_verified,native_use:args.native_use});
 return {...input,reports,expected,recomputed,effective_check,actual_native_use:observation.native_use,actual_binding_derivation:args.binding_derivation};
}
export async function typedAcknowledgementInput(current,cut,input,documents,history){
 const bytes=documentMap(documents),handoff_document=decodeOriginalJson(bytes.get(input.value.handoff.path)),response_document=decodeOriginalJson(bytes.get(input.value.actual_response.path));verifyBindings(response_document,bytes);
 const prior=history.find(e=>e.preparation?.command==='handoff'&&canonical(e.preparation.output)===canonical(handoff_document)),known=prior?.preparation.output??null;
 if(prior){const original=documentMap(prior.preparation.documents);function capture(value){if(!value||typeof value!=='object')return;if(value.digest_kind==='original-file-sha256'){const raw=original.get(value.path);if(!raw)throw Error('recorded-handoff-document-missing');addDocument(documents,raw,{raw:true});return;}for(const child of Object.values(value))capture(child);}capture(handoff_document);}
 return {...input,handoff_document,response_document,observed:observedHead(current,cut),known_handoff:known};
}
