/** Exact recorded fixture response exercised through the original adapter.
 * Open Questions: connected applications DESIGN.md. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createRecordedMarketingConnector} from './recorded-marketing-fixture.mjs';
import {createMailchimpConnector,MAILCHIMP_IDENTITY} from '../profiles/ai/native/connectors/mailchimp/index.mjs';
test('recorded campaign fixture preserves campaign601 POST identity and original adapter inspects without repeating create',async()=>{
 const controls={campaignState:'save',campaignHtml:'',scheduleTime:null},requests=[],resource=createRecordedMarketingConnector({controls,requests,preference:{email:'member@example.test'},assertSuppressionCurrent:()=>true}),connector=createMailchimpConnector({...resource,assertCurrent:()=>true}),h='a'.repeat(64),command={contract:MAILCHIMP_IDENTITY.contract,semanticVersion:'1',operation:'draft.create',approvalDigest:h,manifestDigest:h,correlationId:'campaign-601',subject:'A distinct supplied subject',audienceDigest:h},slot=connector.createSlot({id:'draft',operation:'draft.create',resourceId:'campaign',action:'draft.create'}),context={attemptId:'original',intentId:'original',binding:{tenant:'fixture'},payload:connector.encodeCommand(command),deadlineAt:Date.now()+30000};
 const before=await resource.http({method:'GET',url:'https://us1.api.mailchimp.com/3.0/campaigns'});assert.deepEqual(JSON.parse(new TextDecoder().decode(before.body)),{campaigns:[],total_items:0});
 const created=await slot.execute(context);assert.equal(created.kind,'confirmed');assert.equal(created.state,'draft-created');assert.equal(controls.campaign.settings.title,'campaign-601');assert.equal(controls.campaign.settings.subject_line,command.subject);assert.deepEqual(controls.campaign.recipients,{list_id:'list1',segment_opts:{saved_segment_id:9}});
 assert.equal((await slot.inspect(context)).kind,'confirmed');assert.equal(requests.filter(row=>row.method==='POST').length,1,'inspection must never repeat the create');
 controls.campaign.settings.title='campaign-1';const changed=await slot.inspect(context);assert.equal(changed.kind,'unknown');assert.equal(changed.reason,'draft-correlation-not-provable-review');assert.equal(requests.filter(row=>row.method==='POST').length,1,'wrong identity stays unknown without fallback');
});
