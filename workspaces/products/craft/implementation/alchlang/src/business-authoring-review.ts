import {readFileSync,statSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import type {BusinessDecision,BusinessReviewSubject,LegacyMeaningSubject} from './business-authoring-protocol.js';
import type {BusinessPreviewSelection,DetailedBusinessSemanticPreview} from './business-authoring-carriers.js';
import {assertBusinessSemanticPreviewCurrent} from './business-authoring-carriers.js';
import {businessCanonical,businessHash,businessReject} from './business-authoring-model.js';
import {assertLoweredDirectBusinessV2Current} from './business-authoring-carriers.js';
import type {LoweredDirectBusinessV2} from './business-authoring-stages-v2.js';
import type {BusinessReviewOwnerV2,BusinessRecipeSelectionV2,PreparedBusinessReviewV2,CapturedBusinessDecisionV2,AcceptedBusinessReviewV2} from './business-authoring-identity-protocol-v2.js';

// Public genuine-producer join only. Open questions: B06.2 accepted materialization
// and B07.3 CLI/selection workflow; contracts/business-review-decision-api.md.
export interface BusinessAuthoringReviewSurface<Selection extends BusinessPreviewSelection=BusinessPreviewSelection> {
 readonly kind:'prepared-business-authoring-review';readonly selection:Selection;readonly model_id:string;
 readonly review:BusinessReviewSubject;readonly subject:BusinessDecision['subject'];
 readonly legacy_meaning_subjects:readonly LegacyMeaningSubject[];readonly definition_closure:BusinessDecision['definition_closure'];
 readonly review_sha256:string;readonly authority_effect:'none';
}
/** Trusted public Core SDK, never supplied by an implementation profile. */
export interface BusinessAuthoringReviewEngine<Selection extends BusinessPreviewSelection,Review extends BusinessAuthoringReviewSurface<Selection>> {
 prepareBusinessAuthoringReview(selection:Selection,modelId:string,subject:BusinessReviewSubject):Review;
 assertBusinessAuthoringReviewCurrent(review:Review):void;
}
export interface PreparedBusinessReview<Selection extends BusinessPreviewSelection=BusinessPreviewSelection,Review extends BusinessAuthoringReviewSurface<Selection>=BusinessAuthoringReviewSurface<Selection>> {
 readonly kind:'prepared-alch-business-review';readonly preview:DetailedBusinessSemanticPreview<Selection>;readonly review:Review;readonly authority_effect:'none';
}
export interface BusinessReviewDecisionRequest {readonly decision_id:string;readonly owner:string;readonly outcome:'accepted'|'declined';readonly reviewed_digest:string}
export interface CapturedBusinessDecisionSurface<Review=BusinessAuthoringReviewSurface> {
 readonly kind:'captured-business-decision';readonly review:Review;readonly decision:BusinessDecision;
 readonly file:Readonly<{path:string;sha256:string;bytes:number}>;readonly authority_effect:'none';
}
export interface AcceptedBusinessDecisionSurface<Review=BusinessAuthoringReviewSurface,Capture=CapturedBusinessDecisionSurface<Review>> {
 readonly kind:'accepted-business-decision';readonly review:Review;readonly capture:Capture;readonly subject:BusinessDecision['subject'];
 readonly legacy_meaning_subjects:readonly LegacyMeaningSubject[];readonly definition_closure:BusinessDecision['definition_closure'];readonly authority_effect:'none';
}
export interface BusinessReviewDecisionEngine<Review,Capture,Accepted> {
 recordBusinessDecision(review:Review,request:BusinessReviewDecisionRequest,absoluteNewFilePath:string):Capture;
 captureBusinessDecision(review:Review,absoluteFilePath:string):Capture;
 assertBusinessDecisionCurrent(capture:Capture):void;
 requireAcceptedBusinessDecision(review:Review,capture:Capture):Accepted;
 assertAcceptedBusinessDecisionCurrent(accepted:Accepted):void;
}
export interface PreparedBusinessReviewDecision<Prepared=PreparedBusinessReview,Capture=CapturedBusinessDecisionSurface> {
 readonly kind:'prepared-alch-business-review-decision';readonly prepared:Prepared;readonly capture:Capture;readonly authority_effect:'none';
}
export interface AcceptedBusinessReviewDecision<Prepared=PreparedBusinessReview,Capture=CapturedBusinessDecisionSurface,Accepted=AcceptedBusinessDecisionSurface> {
 readonly kind:'accepted-alch-business-review-decision';readonly prepared:Prepared;
 readonly decision:PreparedBusinessReviewDecision<Prepared,Capture>;readonly accepted:Accepted;readonly authority_effect:'none';
}
type ReviewOwner={preview:DetailedBusinessSemanticPreview;review:BusinessAuthoringReviewSurface;assertReview:(value:BusinessAuthoringReviewSurface)=>void};
type DecisionOwner={prepared:PreparedBusinessReview;capture:CapturedBusinessDecisionSurface;assertCapture:(value:CapturedBusinessDecisionSurface)=>void};
type AcceptanceOwner={prepared:PreparedBusinessReview;decision:PreparedBusinessReviewDecision;accepted:AcceptedBusinessDecisionSurface;assertAccepted:(value:AcceptedBusinessDecisionSurface)=>void};
const reviews=new WeakMap<object,ReviewOwner>(),decisions=new WeakMap<object,DecisionOwner>(),acceptances=new WeakMap<object,AcceptanceOwner>();
const ownPath=fileURLToPath(import.meta.url);
function implementation():string {const stat=statSync(ownPath,{bigint:true});return businessHash(readFileSync(ownPath))+':'+[stat.dev,stat.ino,stat.size,stat.mtimeNs,stat.ctimeNs].join(':');}
const originalImplementation=implementation();
function reject(message:string):never {return businessReject('BUSINESS_REVIEW_JOIN','business.alch',1,1,message);}
function currentImplementation():void {if(implementation()!==originalImplementation)reject('review/decision producer join implementation changed');}
const same=(a:unknown,b:unknown)=>businessCanonical(a)===businessCanonical(b);

export function prepareBusinessReview<Selection extends BusinessPreviewSelection,Review extends BusinessAuthoringReviewSurface<Selection>>(
 preview:DetailedBusinessSemanticPreview<Selection>,engine:BusinessAuthoringReviewEngine<Selection,Review>,
):PreparedBusinessReview<Selection,Review> {
 assertBusinessSemanticPreviewCurrent(preview);currentImplementation();
 const assertReview=engine.assertBusinessAuthoringReviewCurrent.bind(engine);
 const review=engine.prepareBusinessAuthoringReview(preview.prepared.selection,preview.model_id,preview.review);assertReview(review);
 if(review.kind!=='prepared-business-authoring-review'||review.selection!==preview.prepared.selection||review.model_id!==preview.model_id||review.authority_effect!=='none'||!same(review.review,preview.review)||!same(review.legacy_meaning_subjects,preview.legacy_meaning_subjects))reject('Core review must retain the exact genuine preview and selection correspondence');
 const value=Object.freeze({kind:'prepared-alch-business-review' as const,preview,review,authority_effect:'none' as const});
 reviews.set(value,{preview,review,assertReview:assertReview as ReviewOwner['assertReview']});assertPreparedBusinessReviewCurrent(value);return value;
}
export function assertPreparedBusinessReviewCurrent<Selection extends BusinessPreviewSelection,Review extends BusinessAuthoringReviewSurface<Selection>>(value:PreparedBusinessReview<Selection,Review>):void {
 const state=value&&typeof value==='object'?reviews.get(value):undefined;if(!state)reject('registered original Alch business review required');
 currentImplementation();assertBusinessSemanticPreviewCurrent(state.preview);state.assertReview(state.review);
 if(value.preview!==state.preview||value.review!==state.review||!same(state.review.review,state.preview.review))reject('genuine preview/Core review correspondence changed');
}

function retainDecision<Selection extends BusinessPreviewSelection,Review extends BusinessAuthoringReviewSurface<Selection>,Capture extends CapturedBusinessDecisionSurface<Review>,Accepted>(
 prepared:PreparedBusinessReview<Selection,Review>,capture:Capture,engine:BusinessReviewDecisionEngine<Review,Capture,Accepted>,
):PreparedBusinessReviewDecision<PreparedBusinessReview<Selection,Review>,Capture> {
 assertPreparedBusinessReviewCurrent(prepared);const assertCapture=engine.assertBusinessDecisionCurrent.bind(engine);assertCapture(capture);
 if(capture.review!==prepared.review||capture.authority_effect!=='none'||!same(capture.decision.subject,prepared.review.subject)||!same(capture.decision.legacy_meaning_subjects,prepared.review.legacy_meaning_subjects)||!same(capture.decision.definition_closure,prepared.review.definition_closure))reject('decision capture must retain this exact original review and reviewed scope');
 const value=Object.freeze({kind:'prepared-alch-business-review-decision' as const,prepared,capture,authority_effect:'none' as const});
 decisions.set(value,{prepared,capture,assertCapture:assertCapture as DecisionOwner['assertCapture']});assertPreparedBusinessReviewDecisionCurrent(value);return value;
}
/** Writes only the explicit new local record through Core; no owner outcome is inferred. */
export function recordBusinessReviewDecision<Selection extends BusinessPreviewSelection,Review extends BusinessAuthoringReviewSurface<Selection>,Capture extends CapturedBusinessDecisionSurface<Review>,Accepted>(
 prepared:PreparedBusinessReview<Selection,Review>,request:BusinessReviewDecisionRequest,absoluteNewFilePath:string,engine:BusinessReviewDecisionEngine<Review,Capture,Accepted>,
):PreparedBusinessReviewDecision<PreparedBusinessReview<Selection,Review>,Capture> {
 assertPreparedBusinessReviewCurrent(prepared);return retainDecision(prepared,engine.recordBusinessDecision(prepared.review,request,absoluteNewFilePath),engine);
}
export function captureBusinessReviewDecision<Selection extends BusinessPreviewSelection,Review extends BusinessAuthoringReviewSurface<Selection>,Capture extends CapturedBusinessDecisionSurface<Review>,Accepted>(
 prepared:PreparedBusinessReview<Selection,Review>,absoluteFilePath:string,engine:BusinessReviewDecisionEngine<Review,Capture,Accepted>,
):PreparedBusinessReviewDecision<PreparedBusinessReview<Selection,Review>,Capture> {
 assertPreparedBusinessReviewCurrent(prepared);return retainDecision(prepared,engine.captureBusinessDecision(prepared.review,absoluteFilePath),engine);
}
export function assertPreparedBusinessReviewDecisionCurrent<Selection extends BusinessPreviewSelection,Review extends BusinessAuthoringReviewSurface<Selection>,Capture extends CapturedBusinessDecisionSurface<Review>>(value:PreparedBusinessReviewDecision<PreparedBusinessReview<Selection,Review>,Capture>):void {
 const state=value&&typeof value==='object'?decisions.get(value):undefined;if(!state)reject('registered original Alch decision capture required');
 assertPreparedBusinessReviewCurrent(state.prepared);state.assertCapture(state.capture);
 if(value.prepared!==state.prepared||value.capture!==state.capture)reject('Alch decision producer correspondence changed');
}
/** Exact accepted decision scope only. Accepted carriers/statuses remain B06.2. */
export function requireAcceptedBusinessReviewDecision<Selection extends BusinessPreviewSelection,Review extends BusinessAuthoringReviewSurface<Selection>,Capture extends CapturedBusinessDecisionSurface<Review>,Accepted extends AcceptedBusinessDecisionSurface<Review,Capture>>(
 prepared:PreparedBusinessReview<Selection,Review>,decision:PreparedBusinessReviewDecision<PreparedBusinessReview<Selection,Review>,Capture>,engine:BusinessReviewDecisionEngine<Review,Capture,Accepted>,
):AcceptedBusinessReviewDecision<PreparedBusinessReview<Selection,Review>,Capture,Accepted> {
 assertPreparedBusinessReviewCurrent(prepared);assertPreparedBusinessReviewDecisionCurrent(decision);
 if(decision.prepared!==prepared)reject('decision belongs to another original Alch review; explicitly recapture for a new equivalent review');
 const accepted=engine.requireAcceptedBusinessDecision(prepared.review,decision.capture),assertAccepted=engine.assertAcceptedBusinessDecisionCurrent.bind(engine);assertAccepted(accepted);
 if(accepted.review!==prepared.review||accepted.capture!==decision.capture||decision.capture.decision.outcome!=='accepted'||!same(accepted.subject,prepared.review.subject)||!same(accepted.legacy_meaning_subjects,prepared.review.legacy_meaning_subjects)||!same(accepted.definition_closure,prepared.review.definition_closure))reject('only the exact explicit accepted scope may cross this join');
 const value=Object.freeze({kind:'accepted-alch-business-review-decision' as const,prepared,decision,accepted,authority_effect:'none' as const});
 acceptances.set(value,{prepared,decision,accepted,assertAccepted:assertAccepted as AcceptanceOwner['assertAccepted']});assertAcceptedBusinessReviewDecisionCurrent(value);return value;
}
export function assertAcceptedBusinessReviewDecisionCurrent<Selection extends BusinessPreviewSelection,Review extends BusinessAuthoringReviewSurface<Selection>,Capture extends CapturedBusinessDecisionSurface<Review>,Accepted extends AcceptedBusinessDecisionSurface<Review,Capture>>(value:AcceptedBusinessReviewDecision<PreparedBusinessReview<Selection,Review>,Capture,Accepted>):void {
 const state=value&&typeof value==='object'?acceptances.get(value):undefined;if(!state)reject('registered original accepted Alch business decision required');
 assertPreparedBusinessReviewCurrent(state.prepared);assertPreparedBusinessReviewDecisionCurrent(state.decision);state.assertAccepted(state.accepted);
 if(value.prepared!==state.prepared||value.decision!==state.decision||value.accepted!==state.accepted)reject('accepted decision scope correspondence changed');
}

/** Successor direct-source adapter. Original Core objects cross the join unchanged;
 * source-only component acceptances and accepted flags have no application custody.
 * Open Questions: J01/J02/K02 actual SDK selection and L02 input materialization. */
export interface DirectBusinessReviewOwnerV2 extends BusinessReviewOwnerV2 {
 recordDecision?(review:PreparedBusinessReviewV2,request:BusinessReviewDecisionRequest,file:string):CapturedBusinessDecisionV2;
}
export interface PreparedAlchDirectBusinessReviewV2 {
 readonly kind:'prepared-alch-direct-business-review-v2';readonly lowered:LoweredDirectBusinessV2;
 readonly review:PreparedBusinessReviewV2;readonly authority_effect:'none';
}
export interface CapturedAlchDirectBusinessDecisionV2 {
 readonly kind:'captured-alch-direct-business-decision-v2';readonly prepared:PreparedAlchDirectBusinessReviewV2;
 readonly decision:CapturedBusinessDecisionV2;readonly authority_effect:'none';
}
export interface AcceptedAlchDirectBusinessReviewV2 {
 readonly kind:'accepted-alch-direct-business-review-v2';readonly prepared:PreparedAlchDirectBusinessReviewV2;
 readonly decision:CapturedAlchDirectBusinessDecisionV2;readonly accepted:AcceptedBusinessReviewV2;readonly authority_effect:'none';
}
const directMethodKeys=['prepare','assertCurrent','captureDecision','assertDecisionCurrent','requireAccepted','assertAcceptedCurrent','recordDecision'] as const;
type DirectReviewState={lowered:LoweredDirectBusinessV2;review:PreparedBusinessReviewV2;owner:DirectBusinessReviewOwnerV2;methods:readonly unknown[]};
const directReviews=new WeakMap<object,DirectReviewState>();
const directDecisions=new WeakMap<object,{prepared:PreparedAlchDirectBusinessReviewV2;decision:CapturedBusinessDecisionV2}>();
const directAcceptances=new WeakMap<object,{prepared:PreparedAlchDirectBusinessReviewV2;decision:CapturedAlchDirectBusinessDecisionV2;accepted:AcceptedBusinessReviewV2}>();
function directState(value:PreparedAlchDirectBusinessReviewV2):DirectReviewState {
 const state=value&&typeof value==='object'?directReviews.get(value):undefined;if(!state)reject('original registered direct Alch review required');
 currentImplementation();assertLoweredDirectBusinessV2Current(state.lowered);
 if(directMethodKeys.some((key,i)=>state.owner[key]!==state.methods[i]))reject('exact public Core review owner methods changed');
 state.owner.assertCurrent(state.review);
 if(value.lowered!==state.lowered||value.review!==state.review||!same(state.review.subject,state.lowered.review))reject('original direct source/Core subject correspondence changed');
 return state;
}
export function prepareDirectBusinessReviewV2(lowered:LoweredDirectBusinessV2,selection:BusinessRecipeSelectionV2,owner:DirectBusinessReviewOwnerV2):PreparedAlchDirectBusinessReviewV2 {
 assertLoweredDirectBusinessV2Current(lowered);currentImplementation();
 const methods=directMethodKeys.map(key=>owner[key]);
 const review=owner.prepare(selection,lowered.business.data.identity.namespace,lowered.review);owner.assertCurrent(review);
 if(review.kind!=='prepared-business-review-v2'||review.selection!==selection||review.model_id!==lowered.business.data.identity.namespace||!same(review.subject,lowered.review)||review.authority_effect!=='none')reject('actual selected Core review and exact current direct subject required');
 const model=selection.models.find(row=>row.model_id===review.model_id);
 if(!model||!same(model.source,lowered.business.source)||!same(model.spec,lowered.business.data)||!same(review.source_capture,model.capture))reject('selected source/capture and original Alch source must correspond');
 const value:PreparedAlchDirectBusinessReviewV2=Object.freeze({kind:'prepared-alch-direct-business-review-v2',lowered,review,authority_effect:'none'});
 directReviews.set(value,{lowered,review,owner,methods});assertPreparedDirectBusinessReviewV2Current(value);return value;
}
export function assertPreparedDirectBusinessReviewV2Current(value:PreparedAlchDirectBusinessReviewV2):void{directState(value);}
function retainDirectDecision(prepared:PreparedAlchDirectBusinessReviewV2,decision:CapturedBusinessDecisionV2):CapturedAlchDirectBusinessDecisionV2 {
 const state=directState(prepared);state.owner.assertDecisionCurrent(decision);
 if(decision.kind!=='captured-business-decision-v2'||decision.review!==state.review||decision.authority_effect!=='none')reject('original Core decision for this exact selected review required');
 const value:CapturedAlchDirectBusinessDecisionV2=Object.freeze({kind:'captured-alch-direct-business-decision-v2',prepared,decision,authority_effect:'none'});
 directDecisions.set(value,{prepared,decision});assertCapturedDirectBusinessDecisionV2Current(value);return value;
}
export function captureDirectBusinessReviewDecisionV2(prepared:PreparedAlchDirectBusinessReviewV2,file:string):CapturedAlchDirectBusinessDecisionV2 {
 const state=directState(prepared);return retainDirectDecision(prepared,state.owner.captureDecision(state.review,file));
}
export function recordDirectBusinessReviewDecisionV2(prepared:PreparedAlchDirectBusinessReviewV2,request:BusinessReviewDecisionRequest,file:string):CapturedAlchDirectBusinessDecisionV2 {
 const state=directState(prepared);if(typeof state.owner.recordDecision!=='function')reject('actual public Core decision recording owner required');
 return retainDirectDecision(prepared,state.owner.recordDecision(state.review,request,file));
}
export function assertCapturedDirectBusinessDecisionV2Current(value:CapturedAlchDirectBusinessDecisionV2):void {
 const state=value&&typeof value==='object'?directDecisions.get(value):undefined;if(!state)reject('original registered direct Alch decision required');
 const parent=directState(state.prepared);parent.owner.assertDecisionCurrent(state.decision);
 if(value.prepared!==state.prepared||value.decision!==state.decision||state.decision.review!==parent.review)reject('original decision/source scope changed');
}
export function requireAcceptedDirectBusinessReviewV2(prepared:PreparedAlchDirectBusinessReviewV2,decision:CapturedAlchDirectBusinessDecisionV2):AcceptedAlchDirectBusinessReviewV2 {
 const state=directState(prepared);assertCapturedDirectBusinessDecisionV2Current(decision);
 if(decision.prepared!==prepared)reject('decision belongs to another original direct review');
 const accepted=state.owner.requireAccepted(state.review,decision.decision);state.owner.assertAcceptedCurrent(accepted);
 if(accepted.kind!=='accepted-business-review-v2'||accepted.review!==state.review||accepted.decision!==decision.decision||accepted.authority_effect!=='none')reject('only exact original accepted Core scope can cross the direct join');
 const value:AcceptedAlchDirectBusinessReviewV2=Object.freeze({kind:'accepted-alch-direct-business-review-v2',prepared,decision,accepted,authority_effect:'none'});
 directAcceptances.set(value,{prepared,decision,accepted});assertAcceptedDirectBusinessReviewV2Current(value);return value;
}
export function assertAcceptedDirectBusinessReviewV2Current(value:AcceptedAlchDirectBusinessReviewV2):void {
 const state=value&&typeof value==='object'?directAcceptances.get(value):undefined;if(!state)reject('original registered direct Alch acceptance required');
 const parent=directState(state.prepared);assertCapturedDirectBusinessDecisionV2Current(state.decision);parent.owner.assertAcceptedCurrent(state.accepted);
 if(value.prepared!==state.prepared||value.decision!==state.decision||value.accepted!==state.accepted)reject('accepted direct original owner correspondence changed');
}
