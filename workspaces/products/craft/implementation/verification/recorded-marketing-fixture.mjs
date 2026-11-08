/** Recorded Mailchimp fixture state, never a real-provider qualification.
 * Its response reflects the actual create request rather than a fixed business
 * correlation ID. Open Questions: connected applications DESIGN.md. */
import assert from 'node:assert/strict';
const reply=(value,status=200)=>({status,headers:{},body:status===204?new Uint8Array():new TextEncoder().encode(JSON.stringify(value))});
export function createRecordedMarketingConnector({controls,requests,preference,assertSuppressionCurrent}){
 assert.equal(typeof assertSuppressionCurrent,'function');
 const campaign=()=>{assert.ok(controls.campaign,'a recorded provider campaign must first be created');return {...controls.campaign,status:controls.campaignState,send_time:controls.scheduleTime};};
 return {account:'marketing-account',serverPrefix:'us1',listId:'list1',segmentId:'9',replyTo:'sender@example.test',fromName:'Fixture sender',credentials:{current:()=>({token:'synthetic-marketing',account:'marketing-account',scopes:[],revision:'1',status:'active',expiresAt:Date.now()+3600000})},suppressionPort:{checkCurrent(){assert.equal(assertSuppressionCurrent(),true);return true;}},http:async request=>{
  requests.push(request);const p=new URL(request.url).pathname;
  if(p==='/3.0/')return reply({account_id:'marketing-account'});
  if(p.includes('/segments/'))return reply({members:[{email_address:preference.email,status:'subscribed',list_id:'list1'}],total_items:1});
  if(p.includes('/lists/'))return reply({id:'list1'});
  if(p.includes('/verified-domains/'))return reply({domain:'example.test',verified:true,authenticated:true});
  if(p.includes('/reports/'))return reply({id:'campaign-101',list_id:'list1',emails_sent:1,opens:{opens_total:1}});
  if(p.endsWith('/send-checklist'))return reply({is_ready:true});
  if(p.endsWith('/content')){if(request.method==='PUT')controls.campaignHtml=JSON.parse(new TextDecoder().decode(request.body)).html;return reply({html:controls.campaignHtml});}
  if(p.endsWith('/actions/schedule')){controls.scheduleTime=JSON.parse(new TextDecoder().decode(request.body)).schedule_time;controls.campaignState='schedule';return reply(null,204);}
  if(p==='/3.0/campaigns'&&request.method==='POST'){const actual=JSON.parse(new TextDecoder().decode(request.body));assert.deepEqual(Object.keys(actual).sort(),['recipients','settings','type']);controls.campaign={...actual,id:'campaign-101'};controls.campaignState='save';return reply(campaign());}
  if(p==='/3.0/campaigns'&&request.method==='GET')return reply({campaigns:controls.campaign?[campaign()]:[],total_items:controls.campaign?1:0});
  return reply(campaign());
 }};
}
