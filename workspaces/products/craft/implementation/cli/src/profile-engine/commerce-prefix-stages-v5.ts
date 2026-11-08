/** Original public selected-source stages for the finite pure component slice.
 * Whole application checking/code/API/views remain separate original tasks.
 * Open Questions: docs/COMMERCE-SDK-V5.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest,captureJson} from './contracts.js';
import {assertCommerceNativeOwnerV5,commerceNativeStageParentsV5,type createCommerceNativeOwnerV5} from './commerce-native-v5.js';
import {createCoreCommerceReviewOwner,type CoreCommerceReviewCapture,type CoreCommerceDecisionCapture} from '../commerce/commerce-core-review-owner.js';
import {createCoreCommerceInputOwner,type CoreCommerceSourceAuthoringInput} from '../commerce/commerce-core-input-owner.js';
import {createCoreCommerceObligationOwner,type CoreCommerceObligationCapture} from '../commerce/commerce-core-obligation-owner.js';
import {pinCoreImplementation,readCorePhysicalFile,writeCoreExclusiveFile,type CorePhysicalFile} from '../commerce/commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import type {CommerceSourceHandle,CommerceProfileHandle,CommerceNativeBasisHandle,CommerceSelectionHandle,CommerceEarlyRequestHandle,CommerceReviewHandle,CommerceDecisionHandle,CommerceInputHandle,CommerceSelectionOwner,CommerceReviewOwner} from '../commerce/commerce-stages-v1.js';
import type {CommerceSourcePrefixHandleV5} from './commerce-native-v5.js';
import type {CommerceNativeBindingHandleV5} from './commerce-native-v5.js';
import type {CommerceProducedPureHandleV5} from './commerce-native-producer-v5.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-native-v5'+ext,'../commerce/commerce-core-review-owner'+ext,'../commerce/commerce-core-input-owner'+ext,'../commerce/commerce-core-obligation-owner'+ext]);
const where={path:'commerce-prefix-stages-v5',start:0,end:0};
type Native=ReturnType<typeof createCommerceNativeOwnerV5>;
type Parents=ReturnType<typeof commerceNativeStageParentsV5>;
type Context={parents:Parents;profile:CommerceProfileHandle;basis:CommerceNativeBasisHandle;reviewOwner:string;decisionRoot:string;reviews:ReturnType<typeof createCoreCommerceReviewOwner>;inputs:ReturnType<typeof createCoreCommerceInputOwner>;obligations:ReturnType<typeof createCoreCommerceObligationOwner>;disposed:boolean};
type Selected={context:Context;inspection:Readonly<Record<string,unknown>>};
type Early={selection:CommerceSelectionHandle;obligation:CoreCommerceObligationCapture;inspection:Readonly<Record<string,unknown>>};
type Review={selection:CommerceSelectionHandle;early:CommerceEarlyRequestHandle;original:CoreCommerceReviewCapture;inspection:Readonly<Record<string,unknown>>};
type Decision={review:CommerceReviewHandle;original:CoreCommerceDecisionCapture;physical:CorePhysicalFile;outcome:'accept'|'reject'};
type Input={selection:CommerceSelectionHandle;early:CommerceEarlyRequestHandle;decision:CommerceDecisionHandle;original:CoreCommerceSourceAuthoringInput};
export interface CommerceAcceptedNativeBindingV5 {readonly kind:'original-accepted-commerce-native-binding/v5-candidate'}
const token=<T>(kind:string)=>Object.freeze({kind}) as unknown as T;

export function createCommercePrefixStagesV5(native:Native){
 assertCommerceNativeOwnerV5(native);pin.assertCurrent();
 const contexts=new WeakMap<object,Context>(),selections=new WeakMap<object,Selected>(),earlyRequests=new WeakMap<object,Early>(),reviews=new WeakMap<object,Review>(),decisions=new WeakMap<object,Decision>(),inputs=new WeakMap<object,Input>(),products=new WeakMap<object,CommerceInputHandle>(),bindings=new WeakMap<object,{input:CommerceInputHandle;original:CommerceNativeBindingHandleV5;disposed:boolean}>();
 const requireOriginal=<T>(map:WeakMap<object,T>,handle:unknown,kind:string):T=>{
  const row=handle&&typeof handle==='object'?map.get(handle):undefined;
  if(!row)fail('ForeignOwner',where,'original '+kind+' from this exact stage owner required');
  pin.assertCurrent();assertCommerceNativeOwnerV5(native);return row;
 };
 const contextCurrent=(c:Context)=>{if(c.disposed)fail('DisposedOwner',where,'selected source stages disposed');c.parents.current();};
 const selectedState=(h:CommerceSelectionHandle)=>{const s=requireOriginal(selections,h,'selection');contextCurrent(s.context);return s;};
 const earlyState=(h:CommerceEarlyRequestHandle)=>{const s=requireOriginal(earlyRequests,h,'early request'),c=selectedState(s.selection).context;c.obligations.assertCurrent(s.obligation);return s;};
 const reviewState=(h:CommerceReviewHandle)=>{const s=requireOriginal(reviews,h,'review'),c=selectedState(s.selection).context,e=earlyState(s.early);if(e.selection!==s.selection)fail('ForeignOwner',where,'exact original early request required');c.reviews.assertCurrent(s.original);return s;};
 const decisionState=(h:CommerceDecisionHandle)=>{const s=requireOriginal(decisions,h,'decision'),r=reviewState(s.review),c=selectedState(r.selection).context;c.reviews.assertDecisionCurrent(s.original);if(readCorePhysicalFile(s.physical.file.path).fingerprint!==s.physical.fingerprint)fail('StaleOwner',where,'selected decision file changed or was replaced');return s;};
 const inputState=(h:CommerceInputHandle)=>{const s=requireOriginal(inputs,h,'input'),c=selectedState(s.selection).context,d=decisionState(s.decision),r=reviewState(d.review);if(r.selection!==s.selection||r.early!==s.early||earlyState(s.early).selection!==s.selection||d.outcome!=='accept')fail('ForeignOwner',where,'exact accepted source/selection/early/decision lineage required');c.inputs.assertCurrent(s.original);return s;};
 const bindingState=(h:CommerceAcceptedNativeBindingV5)=>{const s=requireOriginal(bindings,h,'accepted native binding');if(s.disposed)fail('DisposedOwner',where,'accepted native binding disposed');inputState(s.input);native.inspectBinding(s.original);return s;};
 let decisionCounter=0;

 const selection:CommerceSelectionOwner=Object.freeze({
  select(source:CommerceSourceHandle,profile:CommerceProfileHandle,basis:CommerceNativeBasisHandle){
   const c=requireOriginal(contexts,source,'prepared source');contextCurrent(c);
   if(c.profile!==profile||c.basis!==basis)fail('ForeignOwner',where,'exact original loaded profile and native basis required');
   const p=c.parents,b=p.basis,sourceData=p.stage.inspect(p.source),app=sourceData.application;
   if(dataDigest(app.profile_source)!==dataDigest(b.profile.technical_source)||app.profile_mapping!==b.profile.family_mapping||dataDigest(app.parameters)!==dataDigest(b.profile.parameters))fail('InvalidContract',where,'actual application profile source, Mapping and parameters must match the loaded family');
   if(b.profile.scope.kind!=='pure-pricing')fail('UnsupportedCapability',where,'only the actually implemented finite pure selection is available');
   const subject={source_sha256:sourceData.source_sha256,profile_sha256:b.profile_sha256,native_basis_sha256:b.native_basis_sha256,sdk_sha256:b.sdk_sha256,scope:b.profile.scope};
   const inspection=coreFreeze({...subject,selection_sha256:dataDigest(subject),stage:'selected-pure-source',output_sha256:null,authority_effect:'none',qualification:'pure-source-selection-only;not-application-or-entry-acceptance'}),h=token<CommerceSelectionHandle>('original-commerce-selection/v5-candidate');
   selections.set(h,{context:c,inspection});selectedState(h);return h;
  },
  prepareEarly(h:CommerceSelectionHandle){
   const s=selectedState(h),c=s.context,p=c.parents,profile=p.basis.profile;
   const obligation=c.obligations.prepare(p.capture,p.semantic);
   for(const required of profile.obligations){const resolved=profile.resolved_dependencies.filter(d=>d.semantic_abi===required.abi);if(resolved.length!==1||required.required_exports.some(name=>!resolved[0]!.exports.includes(name)))fail('NativeImplementationUnavailable',where,'each selected early primitive requires its actual loaded ABI and complete exports');}
   const sourceObligations=c.obligations.inspect(obligation),subject={selection_sha256:s.inspection.selection_sha256,targets:profile.scope.targets,native_obligations:profile.obligations,source_obligation_sha256:dataDigest(sourceObligations),omitted_capabilities:profile.scope.omitted_capabilities};
   const inspection=coreFreeze({...subject,early_request_sha256:dataDigest(subject),qualification:'selected-source-obligations;runtime-and-application-witnesses-still-required',authority_effect:'none'}),result=token<CommerceEarlyRequestHandle>('original-commerce-early-request/v5-candidate');
   earlyRequests.set(result,{selection:h,obligation,inspection});earlyState(result);return result;
  },
  assertCurrent(h:CommerceSelectionHandle){selectedState(h);},
 });

 // Explicit early request is a prerequisite. No method invents an acceptance.
 const reviewWithEarly=(source:CommerceSourceHandle,s:CommerceSelectionHandle,e:CommerceEarlyRequestHandle)=>{
  const chosen=selectedState(s),c=chosen.context;
  if(c.parents.source!==source||earlyState(e).selection!==s)fail('ForeignOwner',where,'exact source/selection/early parents required');
  const original=c.reviews.prepare(c.parents.semantic,c.reviewOwner),originalInspection=c.reviews.inspect(original),subject={selection_sha256:chosen.inspection.selection_sha256,early_request_sha256:earlyState(e).inspection.early_request_sha256,source_review_sha256:originalInspection.review_sha256,owner:c.reviewOwner};
  const inspection=coreFreeze({...subject,review_sha256:dataDigest(subject),source_review:originalInspection,qualification:'explicit-selected-pure-source-review;not-whole-application-approval',authority_effect:'none'}),h=token<CommerceReviewHandle>('original-commerce-selected-review/v5-candidate');
  reviews.set(h,{selection:s,early:e,original,inspection});reviewState(h);return h;
 };
 const latestEarly=new WeakMap<object,CommerceEarlyRequestHandle>();
 const publicSelection:CommerceSelectionOwner=Object.freeze({...selection,prepareEarly(h:CommerceSelectionHandle){const e=selection.prepareEarly(h);latestEarly.set(h,e);return e;}});
 const reviewOwner:CommerceReviewOwner=Object.freeze({
  review(source:CommerceSourceHandle,s:CommerceSelectionHandle){selectedState(s);const e=latestEarly.get(s);if(!e)fail('InvalidContract',where,'prepare an original early request before review');return reviewWithEarly(source,s,e);},
  recordDecision(h:CommerceReviewHandle,outcome:'accept'|'reject'){
   const r=reviewState(h),c=selectedState(r.selection).context;
   if(outcome!=='accept'&&outcome!=='reject')fail('InvalidContract',where,'explicit accept or reject outcome required');
   const id='decision-'+String(++decisionCounter),sourceFile=path.join(c.decisionRoot,id+'-source.json'),selectedFile=path.join(c.decisionRoot,id+'-selected.json'),sourceReview=c.reviews.inspect(r.original);
   const original=c.reviews.recordDecision(r.original,{decision_id:id,owner:c.reviewOwner,outcome:outcome==='accept'?'accepted':'declined',reviewed_digest:sourceReview.review_sha256},sourceFile),sourceDecision=c.reviews.inspectDecision(original);
   const physical=writeCoreExclusiveFile(selectedFile,JSON.stringify({schema_version:'craft.commerce-selected-source-decision/v5-candidate',decision_id:id,outcome,owner:c.reviewOwner,review_sha256:r.inspection.review_sha256,selection_sha256:selectedState(r.selection).inspection.selection_sha256,early_request_sha256:earlyState(r.early).inspection.early_request_sha256,source_decision:sourceDecision.file,authority_effect:'none',open_questions_ref:'docs/COMMERCE-SDK-V5.md#open-questions'},null,2)+'\n');
   const result=token<CommerceDecisionHandle>('original-commerce-selected-decision/v5-candidate');decisions.set(result,{review:h,original,physical,outcome});decisionState(result);return result;
  },
  assertCurrent(h:CommerceDecisionHandle){decisionState(h);},
 });

 return Object.freeze({selection:publicSelection,reviews:reviewOwner,
  prepare(prefix:CommerceSourcePrefixHandleV5,request:{reviewOwner:string;decisionRoot:string}){
   pin.assertCurrent();const p=commerceNativeStageParentsV5(native,prefix),value=captureJson(request) as typeof request;
   if(!value||typeof value!=='object'||Object.keys(value).sort().join(',')!=='decisionRoot,reviewOwner'||typeof value.reviewOwner!=='string'||!value.reviewOwner.trim()||value.reviewOwner.length>256||/[\u0000-\u001f\u007f]/.test(value.reviewOwner)||typeof value.decisionRoot!=='string'||!path.isAbsolute(value.decisionRoot)||path.normalize(value.decisionRoot)!==value.decisionRoot)fail('InvalidContract',where,'closed explicit review owner and normalized absolute decision directory required');
   if(contexts.has(p.source))fail('InvalidContract',where,'one prepared stage context per original source prefix');
   const profile=token<CommerceProfileHandle>('original-loaded-commerce-profile/v5-candidate'),basis=token<CommerceNativeBasisHandle>('original-loaded-commerce-native-basis/v5-candidate'),review=createCoreCommerceReviewOwner(p.semantics),c:Context={parents:p,profile,basis,reviewOwner:value.reviewOwner,decisionRoot:value.decisionRoot,reviews:review,inputs:createCoreCommerceInputOwner(p.semantics,review),obligations:createCoreCommerceObligationOwner(p.sources,p.semantics),disposed:false};
   contexts.set(p.source,c);contextCurrent(c);return Object.freeze({source:p.source,profile,basis});
  },
  inspectSelection(h:CommerceSelectionHandle){return selectedState(h).inspection;},
  inspectEarly(h:CommerceEarlyRequestHandle){return earlyState(h).inspection;},
  inspectReview(h:CommerceReviewHandle){return reviewState(h).inspection;},
  inspectDecision(h:CommerceDecisionHandle){const d=decisionState(h);return coreFreeze({outcome:d.outcome,file:d.physical.file,review_sha256:reviewState(d.review).inspection.review_sha256,authority_effect:'none'});},
  formInput(source:CommerceSourceHandle,s:CommerceSelectionHandle,e:CommerceEarlyRequestHandle,d:CommerceDecisionHandle):CommerceInputHandle{
   const c=selectedState(s).context,decision=decisionState(d),r=reviewState(decision.review);
   if(c.parents.source!==source||earlyState(e).selection!==s||r.selection!==s||r.early!==e)fail('ForeignOwner',where,'exact original selected source/early/review/decision required');
   if(decision.outcome!=='accept')fail('InvalidContract',where,'an explicit accepted selected-source decision is required');
   const accepted=c.reviews.requireAccepted(r.original,decision.original),original=c.inputs.form(c.parents.capture,c.parents.semantic,r.original,accepted),h=token<CommerceInputHandle>('original-commerce-selected-input/v5-candidate');
   inputs.set(h,{selection:s,early:e,decision:d,original});inputState(h);return h;
  },
  inspectInput(h:CommerceInputHandle){const s=inputState(h),c=selectedState(s.selection).context,d=decisionState(s.decision);return coreFreeze({stage:'selected-accepted-pure-input',source_input:c.inputs.inspect(s.original),selection:selectedState(s.selection).inspection,early_request:earlyState(s.early).inspection,selected_review:reviewState(d.review).inspection,decision_file:d.physical.file,qualification:'accepted-input-for-selected-pure-components;not-checked-whole-application',authority_effect:'none'});},
  assertInputCurrent(h:CommerceInputHandle){inputState(h);},
  async produceForInput(h:CommerceInputHandle,output:string){const s=inputState(h),c=selectedState(s.selection).context,product=await native.produceForSource(c.parents.prefix,output);inputState(h);products.set(product,h);return product;},
  async bindForInput(h:CommerceInputHandle,product:CommerceProducedPureHandleV5){const s=inputState(h),c=selectedState(s.selection).context;if(products.get(product)!==h)fail('ForeignOwner',where,'actual component output emitted through this exact accepted input required');const original=await native.bindComponents(c.parents.prefix,product);inputState(h);const binding=token<CommerceAcceptedNativeBindingV5>('original-accepted-commerce-native-binding/v5-candidate');bindings.set(binding,{input:h,original,disposed:false});bindingState(binding);return binding;},
  nativeApi(binding:CommerceAcceptedNativeBindingV5){
   const s=bindingState(binding),api=native.native(s.original);
   const wrap=(group:'values'|'pure')=>Object.freeze(Object.fromEntries(Object.entries(api[group]).map(([name,method])=>[name,(...args:unknown[])=>{bindingState(binding);const result=(method as (...values:unknown[])=>unknown)(...args);bindingState(binding);return result;}])));
   return Object.freeze({values:wrap('values'),pure:wrap('pure')}) as unknown as typeof api;
  },
  inspectBinding(binding:CommerceAcceptedNativeBindingV5){const s=bindingState(binding),i=inputState(s.input),d=decisionState(i.decision);return coreFreeze({native:native.inspectBinding(s.original),selection_sha256:selectedState(i.selection).inspection.selection_sha256,early_request_sha256:earlyState(i.early).inspection.early_request_sha256,review_sha256:reviewState(d.review).inspection.review_sha256,decision_file:d.physical.file,qualification:'accepted-selected-pure-component-binding;not-whole-application',authority_effect:'none'});},
  disposeBinding(binding:CommerceAcceptedNativeBindingV5){const s=bindingState(binding);native.disposeBinding(s.original);s.disposed=true;},
  dispose(source:CommerceSourceHandle){const c=requireOriginal(contexts,source,'prepared source');contextCurrent(c);c.disposed=true;},
 });
}
