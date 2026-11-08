/** Finite recipe over original PDF/text parser, model and Xero DRAFT owners.
 * No business arithmetic, reconciliation or approval predicate lives here.
 * Open Questions: goals/plans/craft-service-profile-extensions-2026-11-02/DESIGN.md. */
import {freeze} from '../../shared.mjs';
export const serviceFamilyDescriptor=freeze({
 family:'invoice-draft/domain-v1',
 configuration:{recipe:'InvoiceDraft'},
 stages:[
  {name:'extraction',kind:'model'},
  {name:'draftPosting',kind:'provider',operation:'bill.draft'}
 ],
 approvalStages:['draftPosting'],
 resourceRequirements:['model','parser','provider']
});
