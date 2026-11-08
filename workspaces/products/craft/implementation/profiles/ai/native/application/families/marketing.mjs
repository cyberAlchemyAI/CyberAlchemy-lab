/** Finite recipe over original Mailchimp effects and protected CRM Query.
 * Open Questions: goals/plans/craft-service-profile-extensions-2026-11-02/DESIGN.md. */
import {freeze} from '../../shared.mjs';
export const serviceFamilyDescriptor=freeze({
 family:'marketing-campaign/domain-v1',
 configuration:{draftOperation:'PrepareDraft',observationOperation:'ObserveMetrics'},
 stages:[
  {name:'proposal',kind:'model'},
  {name:'createDraft',kind:'provider',operation:'draft.create',businessOperation:'PrepareDraft'},
  {name:'setContent',kind:'provider',operation:'draft.content',businessOperation:'PrepareDraft'},
  {name:'schedule',kind:'provider',operation:'campaign.schedule'},
  {name:'metrics',kind:'provider',operation:'campaign.metrics',observationOperation:'ObserveMetrics',readCurrent:true}
 ],
 approvalStages:['schedule'],resourceRequirements:['model','providers','query']
});
