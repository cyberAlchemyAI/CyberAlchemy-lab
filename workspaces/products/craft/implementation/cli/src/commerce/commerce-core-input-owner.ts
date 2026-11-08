/** Genuine original source-authoring preparation; not CommerceInputHandle or
 * selected/native/checked/generated application custody. Future full assembly
 * must join actual profile/selection/early-request owners separately.
 * Open Questions: docs/COMMERCE-OWNERS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertCoreCommerceReviewOwner,type CoreCommerceReviewOwner,type CoreCommerceReviewCapture,type CoreCommerceAcceptedReview} from './commerce-core-review-owner.js';
import type {CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
const extension=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['commerce-core-physical'+extension]);
export interface CoreCommerceSourceAuthoringInput {readonly kind:'original-core-commerce-source-authoring-input/v1-candidate'}
export interface CoreCommerceInputOwner {form(source:CoreCommerceSourceCapture,semantic:CoreCommerceSemanticCapture,review:CoreCommerceReviewCapture,accepted:CoreCommerceAcceptedReview):CoreCommerceSourceAuthoringInput;inspect(input:CoreCommerceSourceAuthoringInput):Readonly<{application:string;source_capture_sha256:string;executable_sha256:string;assurance_sha256:string;review_sha256:string;qualification:'accepted-source-authoring-only;profile-selection-native-early-request-and-application-check-still-required';authority_effect:'none'}>;assertCurrent(input:CoreCommerceSourceAuthoringInput):void;dispose(input:CoreCommerceSourceAuthoringInput):void}
const registry=new WeakSet<object>();
export function assertCoreCommerceInputOwner(owner:CoreCommerceInputOwner):void {if(!owner||typeof owner!=='object'||!registry.has(owner))fail('ForeignOwner',{path:'application.alch',start:0,end:0},'original source-authoring input owner factory required');}
export function createCoreCommerceInputOwner(semantics:CoreCommerceSemanticOwner,reviews:CoreCommerceReviewOwner):CoreCommerceInputOwner {
 assertCoreCommerceSemanticOwner(semantics);assertCoreCommerceReviewOwner(reviews);pin.assertCurrent();const owned=new WeakMap<object,{source:CoreCommerceSourceCapture;semantic:CoreCommerceSemanticCapture;review:CoreCommerceReviewCapture;accepted:CoreCommerceAcceptedReview;disposed:boolean}>(),where={path:'application.alch',start:0,end:0};
 const state=(input:CoreCommerceSourceAuthoringInput)=>{const s=input&&typeof input==='object'?owned.get(input):undefined;if(!s)fail('ForeignOwner',where,'original input from this exact owner required');if(s.disposed)fail('DisposedOwner',where,'source-authoring input disposed');pin.assertCurrent();assertCoreCommerceSemanticOwner(semantics);assertCoreCommerceReviewOwner(reviews);semantics.assertSource(s.semantic,s.source);reviews.assertSemantic(s.review,s.semantic);reviews.assertAcceptedReview(s.accepted,s.review);return s;};
 const owner:CoreCommerceInputOwner=Object.freeze({form(source:CoreCommerceSourceCapture,semantic:CoreCommerceSemanticCapture,review:CoreCommerceReviewCapture,accepted:CoreCommerceAcceptedReview){pin.assertCurrent();semantics.assertSource(semantic,source);reviews.assertSemantic(review,semantic);reviews.assertAcceptedReview(accepted,review);const h=Object.freeze({kind:'original-core-commerce-source-authoring-input/v1-candidate' as const});owned.set(h,{source,semantic,review,accepted,disposed:false});state(h);return h;},inspect(input:CoreCommerceSourceAuthoringInput){const s=state(input),i=semantics.inspect(s.semantic),r=reviews.inspect(s.review);return coreFreeze({application:i.application,source_capture_sha256:i.source_capture_sha256,executable_sha256:i.executable_sha256,assurance_sha256:i.assurance_sha256,review_sha256:r.review_sha256,qualification:'accepted-source-authoring-only;profile-selection-native-early-request-and-application-check-still-required' as const,authority_effect:'none' as const});},assertCurrent(input:CoreCommerceSourceAuthoringInput){state(input);},dispose(input:CoreCommerceSourceAuthoringInput){state(input).disposed=true;}});
 registry.add(owner);return owner;
}
