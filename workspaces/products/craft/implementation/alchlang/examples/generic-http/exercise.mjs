import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '@domainspec-v2/cli/generic/testing';
const generated=path.resolve(process.argv[2]??'generated');
const {createGeneratedApplicationOwner}=await import(pathToFileURL(path.join(generated,'application.mjs')).href);
const state=mkdtempSync(path.join(tmpdir(),'craft-generic-http-example-'));
const owner=createGeneratedApplicationOwner();let handle,auth,runtime;
const subject='example-alice';
try{
 handle=await owner.prepare();
 const review=owner.review(handle,'example-http-open');
 owner.accept(handle,{decision_id:'example-http-open',owner:'example-http-open',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(state,'review.json'));
 auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(state,'auth'),subjects:[{id:subject,evidence:'isolated-example-evidence',session:'isolated-example-session'}],grants:['ReviewDesk.CommitRequestApprovalEntry','ReviewDesk.ReadStoredRequestEntry'].map(entry=>({subject,entry}))});
 const setup=await prepareGenericFixtureRuntime(owner,handle,{service:'ReviewDeskService',ownedDirectory:path.join(state,'store'),nativeAuth:auth.nativeAuth});runtime=setup.runtime;
 loadGenericFixture(setup.fixture,new Uint8Array(readFileSync(new URL('./fixture-rows.json',import.meta.url))));
 const commit=owner.bindHttp(handle,runtime,'ReviewDeskHttp.Commit');
 const request=()=>new Request('https://example.test/api/approvals',{method:'POST',headers:{'content-type':'application/json','x-craft-command-key':Buffer.from('first-approval-23','utf8').toString('base64url')},body:JSON.stringify({id:'23'})});
 const denied=await commit(request());assert.equal(denied.status,401);
 const associated=()=>{const value=request();auth.associateRequest(commit,value,subject);return value;};
 const response=await commit(associated());assert.equal(response.status,200);const committed=await response.json();
 assert.equal(committed.kind,'returned');assert.equal(committed.observation.kind,'committed');assert.deepEqual(committed.value,{approved:true,id:'23',total:'20',state:'Approved'});
 const retry=await commit(associated());assert.equal(retry.status,200);const replayed=await retry.json();assert.equal(replayed.observation.kind,'replayed');assert.deepEqual(replayed.value,committed.value);
 const read=owner.bindHttp(handle,runtime,'ReviewDeskHttp.Read');const readRequest=new Request('https://example.test/api/requests/23');auth.associateRequest(read,readRequest,subject);
 const loaded=await read(readRequest);assert.equal(loaded.status,200);const stored=await loaded.json();assert.equal(stored.value.value.state,'Approved');assert.equal(stored.value.version,'7');
 console.log(JSON.stringify({unauthenticated_status:denied.status,committed,replayed,stored:stored.value,state_directory:state},null,2));
 console.log('Generated protected POST and GET, atomic state change and stable command replay passed. No listener was started.');
}finally{
 const errors=[];for(const close of [()=>runtime?.close(),()=>auth?.close(),()=>handle?owner.dispose(handle):undefined])try{await close();}catch(error){errors.push(error);}
 if(errors.length)throw new AggregateError(errors,'Example cleanup failed');
}
