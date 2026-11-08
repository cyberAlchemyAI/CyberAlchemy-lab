/** Original dispatcher/release custody checks, fixture HTTP only; no real provider qualification.
 * Open Questions: ../../../../goals/plans/craft-domain-execution-separation-2026-11-01/DESIGN.md. */
import test from 'node:test';import assert from 'node:assert/strict';import {mkdtempSync,rmSync} from 'node:fs';import {tmpdir} from 'node:os';import path from 'node:path';
import {createEffectDispatcher} from '../effects/index.mjs';import {createSourceReleaseService} from '../source-release/index.mjs';import {createHubspotConnector,HUBSPOT_IDENTITY} from '../connectors/hubspot/index.mjs';
async function fixture(t){const directory=mkdtempSync(path.join(tmpdir(),'de03-custody-'));let clock=1000,posts=0;
 const release=createSourceReleaseService({path:path.join(directory,'release.sqlite'),now:()=>clock}),h='a'.repeat(64);
 const connector=createHubspotConnector({account:'account',now:()=>clock,credentials:{current:()=>({token:'synthetic-only',account:'account',scopes:['crm.objects.contacts.read','crm.objects.contacts.write','crm.schemas.contacts.read'],revision:'1',status:'active',expiresAt:10000})},assertCurrent:()=>true,http:async request=>{if(request.url.includes('/properties/'))return {status:200,headers:{},body:Buffer.from(JSON.stringify({name:'craft_correlation_id',type:'string',hasUniqueValue:true}))};if(request.method==='POST'){posts++;throw Error('fixture effect committed but ACK lost');}throw Error('inspection deliberately unselected');}});
 const slot=connector.createSlot({id:'hubspot',operation:'contact.upsert',resourceId:'crm',action:'sync'}),payload=connector.encodeCommand({contract:HUBSPOT_IDENTITY.contract,semanticVersion:'1',operation:'contact.upsert',correlationId:'lead-1',email:'fixture@example.test',firstName:'Fixture',lastName:'Contact',industry:'manufacturing',ownerId:'1',approvalDigest:h,manifestDigest:h});
 const config={path:path.join(directory,'effects.sqlite'),slots:[slot],releasePort:release.port,assertCurrent:()=>true,now:()=>clock};let effects=createEffectDispatcher(config);t.after(()=>{effects.close();release.close();rmSync(directory,{recursive:true,force:true});});
 release.authority.putInlineSource({id:'fact',tenant:'tenant',revision:'1',aclRevision:'1',classifications:['internal'],readers:['operator'],bytes:Buffer.from('fixture source')});release.authority.defineContext({id:'context',tenant:'tenant',principal:'operator',inputs:[{adapter:'inline',id:'fact'}]});release.authority.setPolicy({id:'release',revision:'1',tenants:['tenant'],actions:['sync'],sinks:['hubspot'],recipients:['account'],classifications:['internal'],requireRecipientRead:false});
 const request={intentId:'original-contact-command',slotId:'hubspot',tenant:'tenant',principal:'operator',resourceId:'crm',action:'sync',approvalRevision:'1',sourceRevision:'1',fence:1,payload,deadlineAt:9000,cause:{subjectId:'1',approvalSnapshot:'approved-at-v1'}};
 const ticket=(attempt,deadline)=>release.port.issueRelease({manifest:release.port.captureContext({contextId:'context',tenant:'tenant',principal:'operator'}),policyId:'release',attemptId:attempt.attemptId,fence:1,resourceId:'crm',action:'sync',sink:'hubspot',recipient:'account',payload,expiresAt:deadline});
 return {request,ticket,get effects(){return effects;},get posts(){return posts;},setClock:value=>clock=value,restart(){effects.close();effects=createEffectDispatcher(config);}};
}
test('DE03 original unknown intent rejects changed approval cause after restart without replacement',async t=>{
 const f=await fixture(t),first=f.effects.prepare(f.request);assert.equal((await f.effects.dispatch({attemptId:first.attemptId,ticket:f.ticket(first,8000)})).kind,'unknown');assert.equal(f.posts,1);f.restart();
 assert.throws(()=>f.effects.prepare({...f.request,cause:{...f.request.cause,approvalSnapshot:'different-approval'}}),/CONFLICT/);
 const original=f.effects.inspectIntent(f.request.intentId);assert.equal(original.attemptId,first.attemptId);assert.equal(original.observation.kind,'unknown');assert.deepEqual({...original.cause},f.request.cause);assert.equal(f.posts,1);assert.throws(()=>f.effects.prepare({...f.request,retryOf:first.attemptId}),/INSPECTION_REQUIRED/);
});
test('DE03 original dispatcher rejects send when approval-bounded attempt expires before dispatch',async t=>{
 const f=await fixture(t),deadline=1100,first=f.effects.prepare({...f.request,deadlineAt:deadline}),ticket=f.ticket(first,deadline);f.setClock(deadline);
 await assert.rejects(f.effects.dispatch({attemptId:first.attemptId,ticket}),/DEADLINE|EXPIRED/);assert.equal(f.posts,0);
});
