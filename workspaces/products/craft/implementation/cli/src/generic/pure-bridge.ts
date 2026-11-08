import {coreGenericAdmissionMode,type CoreGenericAdmissionMode} from '../commerce/commerce-core-types.js';
/** Typed custody dispatch; no caller AST-to-execution entry point.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createCoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from '../commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceReviewOwner,type CoreCommerceReviewCapture,type CoreCommerceDecisionCapture,type CoreCommerceAcceptedReview} from '../commerce/commerce-core-review-owner.js';
import {createGenericSemanticOwner,type GenericSemanticCapture} from './semantic-reconstruction.js';
import {createGenericSourceReviewOwner,type GenericReviewCapture,type GenericDecisionCapture,type GenericAcceptedReview} from './source-review-owner.js';
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from '../commerce/commerce-core-source-owner.js';
import type {CoreCommerceDecisionRequest} from '../commerce/commerce-core-review-owner.js';
export type SemanticCapture=CoreCommerceSemanticCapture|GenericSemanticCapture;
export type ReviewCapture=CoreCommerceReviewCapture|GenericReviewCapture;
export type AcceptedReview=CoreCommerceAcceptedReview|GenericAcceptedReview;
export type DecisionCapture=CoreCommerceDecisionCapture|GenericDecisionCapture;
export function createSourceSemanticBridge(sources:CoreCommerceSourceOwner,generic:boolean,mode:CoreGenericAdmissionMode='bounded-values'){
 coreGenericAdmissionMode(mode);
 const legacy=generic?null:createCoreCommerceSemanticOwner(sources),successor=generic?createGenericSemanticOwner(sources,mode):null;
 const oldReview=legacy?createCoreCommerceReviewOwner(legacy):null,newReview=successor?createGenericSourceReviewOwner(successor):null;
 return Object.freeze({legacy,successor,
 check(s:CoreCommerceSourceCapture):SemanticCapture{return successor?successor.check(s):legacy!.check(s);},
 inspect(h:SemanticCapture){return successor?successor.inspect(h as GenericSemanticCapture):legacy!.inspect(h as CoreCommerceSemanticCapture);},
 assertSource(h:SemanticCapture,s:CoreCommerceSourceCapture){if(successor)successor.assertSource(h as GenericSemanticCapture,s);else legacy!.assertSource(h as CoreCommerceSemanticCapture,s);},
 dispose(h:SemanticCapture){if(successor)successor.dispose(h as GenericSemanticCapture);else legacy!.dispose(h as CoreCommerceSemanticCapture);},
 reviews:Object.freeze({prepare(h:SemanticCapture,label:string):ReviewCapture{return newReview?newReview.prepare(h as GenericSemanticCapture,label):oldReview!.prepare(h as CoreCommerceSemanticCapture,label);},inspect(h:ReviewCapture){return newReview?newReview.inspect(h as GenericReviewCapture):oldReview!.inspect(h as CoreCommerceReviewCapture);},recordDecision(h:ReviewCapture,r:CoreCommerceDecisionRequest,file:string):DecisionCapture{return newReview?newReview.recordDecision(h as GenericReviewCapture,r,file):oldReview!.recordDecision(h as CoreCommerceReviewCapture,r,file);},requireAccepted(h:ReviewCapture,d:DecisionCapture):AcceptedReview{return newReview?newReview.requireAccepted(h as GenericReviewCapture,d as GenericDecisionCapture):oldReview!.requireAccepted(h as CoreCommerceReviewCapture,d as CoreCommerceDecisionCapture);},inspectDecision(h:DecisionCapture){return newReview?newReview.inspectDecision(h as GenericDecisionCapture):oldReview!.inspectDecision(h as CoreCommerceDecisionCapture);},assertAcceptedCurrent(h:AcceptedReview){if(newReview)newReview.assertAcceptedCurrent(h as GenericAcceptedReview);else oldReview!.assertAcceptedCurrent(h as CoreCommerceAcceptedReview);}}),
 });
}
