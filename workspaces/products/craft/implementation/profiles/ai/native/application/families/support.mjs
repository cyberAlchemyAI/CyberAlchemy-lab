/** Finite recipe over original support/RAG/Zendesk owners; no business predicates.
 * Open Questions: goals/plans/craft-service-profile-extensions-2026-11-02/DESIGN.md. */
import {freeze} from '../../shared.mjs';

export const serviceFamilyDescriptor=freeze({
 family:'customer-support/domain-v1',
 configuration:{recipe:'SupportReply',effectOperation:'AuthorizeReplySend',continuationRule:'CanSendReply'},
 stages:[
  {name:'proposal',kind:'model'},
  {name:'review',kind:'document',operation:'support.review',decision_acceptance_rule:'CanSendReply'},
  {name:'reply',kind:'provider',operation:'ticket.reply'}
 ],
 approvalStages:['review','reply'],
 resourceRequirements:['model','rag','provider']
});
