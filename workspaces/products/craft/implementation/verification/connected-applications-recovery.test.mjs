/** Actual source-selected system joins, original runtime owners and recovery.
 * Inference/provider/reviewer responses are fixtures, never live qualification.
 * Open Questions: goals/plans/craft-connected-applications-2026-11-02/DESIGN.md. */
import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import {generateConnectedSystem,connectedHost,seedKnowledge,seedCrm,supportCandidate,invoiceCandidate,marketingContent,stage,pair,submit,finish,approve,invokePreference,effectJournal,hash,canonical,phase} from './connected-application-fixtures.mjs';

async function rejectedAdvance(f,claim,expected){
 await assert.rejects(()=>f.app.advance({claim}),error=>{
  const actualCode=error.code??error.diagnostics?.[0]?.code;
  const actualMessage=error.diagnostics?.[0]?.message??error.message;
  if(actualCode!==expected.code)process.stderr.write('Unexpected original rejection: '+String(error)+'\n'+JSON.stringify(error.diagnostics??null)+'\n'+String(error.stack??'')+'\n');
  assert.equal(actualCode,expected.code,'exact original rejection code');assert.ok(actualMessage.includes(expected.message),'exact original rejection cause: '+String(error));return true;
 });
}
const mutations=(h,alias)=>h.requests[alias].filter(row=>row.method!=='GET');
async function completeMarketing(h){const campaign=await marketingContent(h);await approve(campaign.f,campaign.run,campaign.candidate,{prefix:'campaign-',seconds:true,readers:campaign.readers,extra:{approvedAudienceDigest:campaign.audienceDigest,contentDigest:hash(h.controls.campaignHtml),account:'marketing-account'}});await finish(campaign.f,campaign.scheduled,{claim:campaign.tick.claim});assert.equal(h.requests.marketing.filter(row=>row.url.endsWith('/actions/schedule')).length,1);assert.equal((await stage(campaign.f,campaign.run,5)).receipt.metrics.partial,true);return campaign;}


test('generated connected six-application system preserves genuine joins and recovery boundaries',{timeout:14400000},async t=>{
 const only=process.env.CRAFT_CONNECTED_CASE;
 assert.ok(!process.env.CRAFT_CONNECTED_BRANCH||['permission','preference'].includes(process.env.CRAFT_CONNECTED_BRANCH),'known focused Query branch required');
 const generated=await generateConnectedSystem(t);
 const run=async(name,fn)=>{if(!only||only.split(',').includes(name))await t.test(name,{timeout:3600000},fn);};
 if(only==='marketing-only'){await t.test('marketing-only',{timeout:3600000},async t=>{const h=await connectedHost(t,generated);await seedCrm(h,{complete:false});await completeMarketing(h);assert.deepEqual([...h.system.inspect().opened].sort(),['crm','marketing']);phase('focused marketing completed using original protected CRM Query and four separate provider stages');});return;}

 await run('happy',async t=>{
  const h=await connectedHost(t,generated);assert.equal(h.system.get('support'),undefined,'no implicit child runs or opens');await seedKnowledge(h);await seedCrm(h);
  const support=await supportCandidate(h,{id:'2'});assert.equal(JSON.parse(support.candidate.candidateOrigin).subjectId,'2','consumer identity remains its own');const bindings=h.system.inspect().bindings;assert.ok(bindings.some(row=>row.producerRun?.id==='1'&&row.producerRun?.run==='201'),'typed support join fixes genuine producer subject1 while consumer subject2');const imported={ragFacts:'1',documentA:'1',documentB:'1'};assert.deepEqual({...bindings.find(row=>row.consumer==='support'&&row.port==='rag').roleSubjects},imported,'declared original binding records imported role subjects');assert.deepEqual({...support.f.app.inspectGeneration().roleSubjects},imported,'original service bootstrap uses the same source-role binding');
  await approve(support.f,support.run,support.candidate,{prefix:'support-',review:true,id:'2'});await finish(support.f,support.scheduled,{claim:support.tick.claim});assert.equal(mutations(h,'support').length,1);
  const invoice=await invoiceCandidate(h);await finish(invoice.f,invoice.scheduled,{claim:invoice.tick.claim});assert.equal((await stage(invoice.f,invoice.run,2)).receipt.amountMinor,'250');assert.equal(mutations(h,'invoice').length,1);
  await completeMarketing(h);
  assert.deepEqual([...h.system.inspect().opened].sort(),['crm','ingestion','invoice','marketing','rag','support']);assert.equal(mutations(h,'crm').length,1);assert.equal(mutations(h,'invoice').some(row=>row.url.includes('Payments')),false);phase('all six actual generated applications completed through declared source joins');
 });
 await run('restart',async t=>{
  const h=await connectedHost(t,generated);await seedKnowledge(h);await seedCrm(h,{complete:false});const campaign=await marketingContent(h);await approve(campaign.f,campaign.run,campaign.candidate,{prefix:'campaign-',seconds:true,readers:campaign.readers,extra:{approvedAudienceDigest:campaign.audienceDigest,contentDigest:hash(h.controls.campaignHtml),account:'marketing-account'}});const support=await supportCandidate(h),paid=h.paid(),saved=support.candidate.candidateOrigin;await h.reopen();assert.deepEqual(h.storeReopens.map(row=>row.alias).sort(),['crm','ingestion','invoice','marketing','rag','support'],'all six original store connections closed and reopened');const f=await h.open('support');assert.equal((await stage(f,support.run,1)).candidateOrigin,saved);assert.deepEqual(h.paid(),paid,'reacquiring genuine A2/RAG joins must not repeat embeddings/model');await approve(f,support.run,support.candidate,{prefix:'support-',review:true});await finish(f,support.scheduled,{claim:support.tick.claim});assert.equal(mutations(h,'support').length,1);assert.deepEqual(h.paid(),paid,'resume original candidate, not a new paid inference');assert.ok(h.system.inspect().bindings.some(row=>row.producerRun?.run==='201'));const marketing=await h.open('marketing');let marketingClaim;try{marketingClaim=marketing.app.driver.renewClaim(campaign.tick.claim,300000);}catch(error){assert.equal(error.message,'C13_WORKFLOW_STALE_CLAIM','only an expired original claim permits reacquisition');marketingClaim=marketing.app.driver.claimNext(300000);}assert.equal(marketingClaim?.instance_sha256,campaign.tick.claim.instance_sha256,'recovered original marketing instance');await finish(marketing,campaign.scheduled,{claim:marketingClaim});assert.equal(h.requests.marketing.filter(row=>row.url.endsWith('/actions/schedule')).length,1,'reacquired original grouped CRM Query authorizes current scheduling');assert.deepEqual(h.paid(),paid,'restored candidate and grouped Query never repay model');assert.ok(h.system.inspect().bindings.some(row=>row.port==='preferences'&&row.groupedInputsSha256));
 });
 await run('source-revoked-independent-branch',async t=>{
  const h=await connectedHost(t,generated);await seedKnowledge(h);const support=await supportCandidate(h);await approve(support.f,support.run,support.candidate,{prefix:'support-',review:true});const paid=h.paid();h.corpora.knowledge.documents.authority.setAccess({id:'knowledge-b-1',tenant:h.corpora.knowledge.tenant,aclRevision:'5',readers:['5'],classifications:['internal']});await rejectedAdvance(support.f,support.tick.claim,{code:'PermissionDenied',message:'document authority denied'});assert.equal(mutations(h,'support').length,0);assert.equal(h.paid().knowledge,paid.knowledge,'uncited-source denial never regenerates a paid answer');
  const invoice=await invoiceCandidate(h);await finish(invoice.f,invoice.scheduled,{claim:invoice.tick.claim});assert.equal(mutations(h,'invoice').length,1,'blocked support does not block independent original invoice runtime');assert.equal(h.paid().knowledge,paid.knowledge);
 });
 await run('query-permission-and-preference',async t=>{
  // Independent fresh continuations prove each changed input causes its own
  // denial. A terminal/rejected old claim cannot stand in for the second case.
  for(const branch of ['permission','preference']){
   if(process.env.CRAFT_CONNECTED_BRANCH&&process.env.CRAFT_CONNECTED_BRANCH!==branch)continue;
   await t.test(branch,async t=>{
    const h=await connectedHost(t,generated),crm=await seedCrm(h,{complete:false}),campaign=await marketingContent(h);await approve(campaign.f,campaign.run,campaign.candidate,{prefix:'campaign-',seconds:true,readers:campaign.readers,extra:{approvedAudienceDigest:campaign.audienceDigest,contentDigest:hash(h.controls.campaignHtml),account:'marketing-account'}});const paid=h.paid(),beforeMutations=mutations(h,'marketing').length;
    if(branch==='permission'){crm.auth.setPermission('alice',crm.metadata.query.entry,false);await rejectedAdvance(campaign.f,campaign.tick.claim,{code:'ForeignOwner',message:'current original Query grant required'});}
    else{await invokePreference(crm,'ChangeContactPreference',{...h.preference,version:'8',allowed:false},'revoke-connected-preference');
     // The protected CRM command can outlive the marketing lease; resume the original instance.
     let preferenceClaim;try{preferenceClaim=campaign.f.app.driver.renewClaim(campaign.tick.claim,300000);}catch(error){assert.equal(error.message,'C13_WORKFLOW_STALE_CLAIM','only an expired original claim permits reacquisition');preferenceClaim=campaign.f.app.driver.claimNext(300000);}
     assert.equal(preferenceClaim?.instance_sha256,campaign.tick.claim.instance_sha256,'preference mutation must resume the original workflow instance');
     await finish(campaign.f,campaign.scheduled,{claim:preferenceClaim,expectRejected:true});const denied=await stage(campaign.f,campaign.run,4);assert.equal(denied.accepted,false);assert.equal(denied.reason,'audience-preference-changed','original private current grouped Query changes invalidate audience approval');}
    assert.equal(h.requests.marketing.filter(row=>row.url.endsWith('/actions/schedule')).length,0);assert.equal(mutations(h,'marketing').length,beforeMutations,'changed original Query state causes no new provider effect');assert.deepEqual(h.paid(),paid,'changed original Query state never regenerates a paid proposal');
   });
  }
 });
 await run('stale-downstream-approval',async t=>{
  const h=await connectedHost(t,generated);await seedKnowledge(h);const support=await supportCandidate(h);await approve(support.f,support.run,support.candidate,{prefix:'support-',review:true});const paid=h.paid();h.corpora.knowledge.put('support-review-1',{contentPolicyApproved:true,outputDigest:'0'.repeat(64),manifestDigest:JSON.parse(support.candidate.candidateOrigin).manifestDigest},{version:'3'});await finish(support.f,support.scheduled,{claim:support.tick.claim,expectRejected:true});const rejected=await stage(support.f,support.run,2);assert.equal(rejected.accepted,false);assert.equal(rejected.reason,'content-review-required');assert.equal(mutations(h,'support').length,0);assert.deepEqual(h.paid(),paid);
 });
 await run('unknown-original-intent',async t=>{
  const h=await connectedHost(t,generated),invoice=await invoiceCandidate(h);h.controls.loseInvoiceAck=true;let tick={claim:invoice.tick.claim};for(let i=0;i<8;i++){tick=await invoice.f.app.advance({claim:tick.claim});if(tick.result.kind==='suspended-unknown')break;assert.equal(tick.result.kind,'advanced',canonical(tick));}assert.equal(tick.result.kind,'suspended-unknown');const ledgerFile=path.join(invoice.f.state,'xero.sqlite'),before=effectJournal(ledgerFile),paid=h.paid();assert.equal(before.intents.length,1);assert.equal(before.attempts.length,1);assert.equal(before.observations.at(-1).kind,'unknown');assert.equal(mutations(h,'invoice').length,1);
  await h.reopen();assert.equal(h.storeReopens.length,6,'unknown recovery also retires and reopens original stores');const f=await h.open('invoice');await finish(f,invoice.scheduled,{claim:tick.claim});const after=effectJournal(ledgerFile);assert.equal(after.intents[0].id,before.intents[0].id);assert.equal(after.attempts[0].id,before.attempts[0].id);assert.equal(after.attempts.length,1);assert.equal(mutations(h,'invoice').length,1,'unknown write inspected, never replaced');assert.deepEqual(h.paid(),paid,'provider inspection never repays the model');assert.equal(after.observations.at(-1).kind,'confirmed');
 });
});
