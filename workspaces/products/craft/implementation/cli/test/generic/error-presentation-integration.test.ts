/** Real source/profile/Auth/SQLite integration. No listener or live provider.
 * Open Questions: docs/ERROR-PRESENTATION.md#open-questions. */
import test from 'node:test';import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,rmSync,cpSync} from 'node:fs';import path from 'node:path';import {tmpdir} from 'node:os';import {fileURLToPath,pathToFileURL} from 'node:url';
import {createGenericCompositionOwner,createGenericHttpCompositionOwner,createGenericBundledApplicationOwner} from '../../src/generic/public-sdk.js';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.js';
import {createTechnicalProfileSourceOwner} from '../../src/profile-engine/technical-profile-source.js';
import {createGenericHttpHandler,associateGenericHttpFixtureRequest} from '../../src/generic/http-adapter.js';
import {createTechnicalErrorPresentationApplicationOwner,createErrorPresentedBundledApplicationOwner} from '../../src/profile-engine/technical-profile-error-application.js';
import {createGenericEntryHttpHandler} from '../../src/generic/http-entry.js';
import {createGenericErrorPresentationBinding,assertGenericErrorPresentationRuntime,renderGenericErrorPresentation,inspectGenericErrorPresentation} from '../../src/generic/error-presentation.js';
const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url)),core=path.join(repo,'craft/projects/domainspec-v2/impl/cli');
const fixture=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C08/fixtures-candidate-002/approval');
const entry='ReviewDesk.CommitRequestApprovalEntry',read='ReviewDesk.ReadStoredRequestEntry',subject='error-reviewer';
const enumSource='enum EligibilityRejection:\n  value Unverified wire "eligibility-unverified"\n';
const extra=`\n${enumSource}enum EligibilityResult:
  variant Allow
  variant Reject reason EligibilityRejection
calculation Eligible:
  pure
  result EligibilityResult
  expression EligibilityResult.Allow()
calculation Ineligible:
  pure
  result EligibilityResult
  expression EligibilityResult.Reject(reason=EligibilityRejection.Unverified)
policy BeforeApproval:
  input verified Bool
  result EligibilityResult
  ordered-cases:
    denied when not verified -> Ineligible()
    otherwise -> Eligible()
`;
function accept(owner:any,handle:any,dir:string,name:string){const review=owner.review(handle,name);owner.accept(handle,{decision_id:name,owner:name,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(dir,name+'.json'));}
function sourceProfile(directory:string,message:string){mkdirSync(directory,{recursive:true});const samples=path.join(core,'examples/technical-profile-source');for(const f of ['error-family.json','error-obligations.json'])cpSync(path.join(samples,f),path.join(directory,f));
 writeFileSync(path.join(directory,'types.alch'),'module ReviewDesk version 1\n'+enumSource);
 writeFileSync(path.join(directory,'presentation.alch'),`module Profiles.TestError version 1
use ReviewDesk.EligibilityRejection
value-object Text:
  carrier String
  utf8-bytes 1..512
  unicode-scalars 1..256
value-object Presentation:
  coverage Text
  code Text
  message Text
  category Text
  httpStatus UInt64
value-object ErrorCase:
  reason EligibilityRejection
  presentation Presentation
value-object Plan:
  cases List<ErrorCase,1>
mapping Build:
  target Plan
  total true
  field cases <- [ErrorCase(reason=EligibilityRejection.Unverified,presentation=Presentation(coverage="Mapped",code="review-required",message=${JSON.stringify(message)},category="Conflict",httpStatus=409))]
interface Family:
  kind technical-profile-family
  family-contract error-family.json
  obligations error-obligations.json
  input checked technical Craft model with original owner
  output derived candidate package with actual resolved native basis
  callbacks forbidden
  unknown-primitive reject
  missing-producer reject
`);
 const config=JSON.parse(readFileSync(path.join(samples,'error-crm.profile.json'),'utf8'));config.id='Profiles.TestError';config.sources=['types.alch','presentation.alch'];config.boundary='Profiles.TestError.Family';config.selection.mapping='Profiles.TestError.Build';writeFileSync(path.join(directory,'profile.json'),JSON.stringify(config));writeFileSync(path.join(directory,'error-contract.json'),JSON.stringify({schema_version:'craft.error-presentation-contract/v1',producer:'ReviewDesk.CommitRequestApproval',reason_type:'ReviewDesk.EligibilityRejection'}));
 const owner=createTechnicalProfileSourceOwner(),handle=owner.prepare({sourceRoot:directory,manifestPath:path.join(directory,'profile.json')});return {owner,handle};
}
function request(key:string){return new Request('https://fixture.invalid/approve',{method:'POST',headers:{'content-type':'application/json','idempotency-key':key},body:'{"id":"24"}'});}
test('EM04 generated protected API maps409, retains422 defaults and journaled rejection across presentation versions',{timeout:600000},async()=>{
 const dir=mkdtempSync(path.join(tmpdir(),'craft-error-integration-'));let auth:any,runtime:any,setup:any,generated:any,handle:any,original:any,originalHandle:any,p1:any,p2:any;
 try{mkdirSync(path.join(dir,'contracts'));const text=(readFileSync(path.join(fixture,'business.alch'),'utf8')+extra).replace('  call decision ApproveRequest(request=stored.value)','  enforce BeforeApproval(verified=stored.value.verified)\n  call decision ApproveRequest(request=stored.value)');writeFileSync(path.join(dir,'business.alch'),text);const profile=JSON.parse(readFileSync(path.join(fixture,'profile.json'),'utf8'));profile.capabilities.push('operation-policy-enforcement');writeFileSync(path.join(dir,'profile.json'),JSON.stringify(profile));writeFileSync(path.join(dir,'contracts/selected-profile.json'),JSON.stringify(profile));const hp=JSON.parse(readFileSync(path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C14/three-app-authoring-contract-001/casedesk/http-profile.json'),'utf8'));hp.id='ReviewHttp';hp.routes=[{id:'ReviewHttp.Approve',service:'ReviewDeskService',entry,method:'POST',path:'/approve',query:[],response_mapping:'ReviewDesk.HttpDecision'}];hp.route_prefix='';hp.limits.request_bytes=profile.limits.max_input_bytes;writeFileSync(path.join(dir,'contracts/http-profile.json'),JSON.stringify(hp));writeFileSync(path.join(dir,'business.alch'),text+'\nmapping HttpDecision:\n  input decision Decision\n  target Decision\n  total true\n  expression decision\n');for(const name of ['bounds.json','transactions.json'])cpSync(path.join(fixture,'contracts',name),path.join(dir,'contracts',name));
 original=createGenericHttpCompositionOwner();originalHandle=await original.prepare({sourcePath:path.join(dir,'business.alch'),profilePath:path.join(dir,'contracts/selected-profile.json'),httpProfilePath:path.join(dir,'contracts/http-profile.json')});accept(original,originalHandle,dir,'source');const output=path.join(dir,'generated');original.generate(originalHandle,{entry,outputDirectory:output});const module=path.join(output,'application.mjs'),bundle=JSON.parse(readFileSync(module,'utf8').split('const bundle=')[1].split(';\nexport function')[0]);generated=createGenericBundledApplicationOwner(pathToFileURL(module).href,bundle);handle=await generated.prepare();accept(generated,handle,dir,'generated');
 auth=await createGenericAuthFixture(generated,handle,{ownedDirectory:path.join(dir,'auth'),subjects:[{id:subject,evidence:'error-evidence',session:'error-session'}],grants:[{subject,entry},{subject,entry:read}]});setup=await prepareGenericFixtureRuntime(generated,handle,{service:'ReviewDeskService',ownedDirectory:path.join(dir,'store'),nativeAuth:auth.nativeAuth});runtime=setup.runtime;loadGenericFixture(setup.fixture,Buffer.from(readFileSync(path.join(fixture,'fixture-rows.json'))));
 p1=sourceProfile(path.join(dir,'presentation-one'),'Review is required.');p2=sourceProfile(path.join(dir,'presentation-two'),'Please review this request.');
 const b1=createGenericErrorPresentationBinding({sourceOwner:p1.owner,sourceHandle:p1.handle,businessOwner:generated,businessHandle:handle,entries:[entry]}),b2=createGenericErrorPresentationBinding({sourceOwner:p2.owner,sourceHandle:p2.handle,businessOwner:generated,businessHandle:handle,entries:[entry]});
 assert.throws(()=>createGenericErrorPresentationBinding({sourceOwner:p1.owner,sourceHandle:p1.handle,businessOwner:generated,businessHandle:handle,entries:[read]}),/PRODUCER_MISMATCH/);assert.throws(()=>assertGenericErrorPresentationRuntime(b1,{}as any));
 const options={entry,route:'/approve',kind:'command' as const,max_request_bytes:4096},legacy=createGenericEntryHttpHandler(runtime,options),first=createGenericEntryHttpHandler(runtime,{...options,errorPresentation:b1}),second=createGenericEntryHttpHandler(runtime,{...options,errorPresentation:b2});const actor=()=>auth.actor(runtime,subject,entry);
 assert.equal((await legacy(request('same-rejected-command'),actor())).status,422);const a=await first(request('same-rejected-command'),actor());assert.equal(a.status,409);const av=await a.json();assert.equal(av.error.code,'review-required');assert.equal(av.error.message,'Review is required.');assert.equal((await second(request('same-rejected-command'),actor())).status,409);const bv=await (await second(request('same-rejected-command'),actor())).json();assert.equal(bv.error.message,'Please review this request.');assert.notEqual(av.error.presentationVersion,bv.error.presentationVersion);assert.equal((await (await first(request('same-rejected-command'),actor())).json()).error.message,'Review is required.');
 const originalResult=await (await legacy(request('same-rejected-command'),actor())).json();assert.deepEqual(originalResult.outcome,{kind:'Rejected',code:'eligibility-unverified'});assert.equal((await first(request('anonymous'))).status,401);const malformed=new Request('https://fixture.invalid/approve',{method:'POST',headers:{'content-type':'application/json','idempotency-key':'invalid-input'},body:'{"id":"bad"}'});assert.equal((await first(malformed,actor())).status,400);assert.equal(renderGenericErrorPresentation(b1,{entry,outcomeKind:'Failed',code:'eligibility-unverified'}).status,500);assert.notEqual(inspectGenericErrorPresentation(b1).presentation_version,inspectGenericErrorPresentation(b2).presentation_version);
 const rich=createGenericHttpHandler(generated,handle,runtime,'ReviewHttp.Approve',{errorPresentation:b1}),richLegacy=createGenericHttpHandler(generated,handle,runtime,'ReviewHttp.Approve');
 const richRequest=(handler:any,key:string)=>{const r=new Request('https://fixture.invalid/approve',{method:'POST',headers:{'content-type':'application/json','x-craft-command-key':Buffer.from(key).toString('base64url')},body:'{"id":"24"}'});associateGenericHttpFixtureRequest(auth,handler,r,subject);return r;};
 assert.equal((await richLegacy(richRequest(richLegacy,'rich-replay'))).status,422);const richResponse=await rich(richRequest(rich,'rich-replay'));assert.equal(richResponse.status,409);assert.equal((await richResponse.json()).error.code,'review-required');assert.equal((await rich(new Request('https://fixture.invalid/approve',{method:'POST',headers:{'content-type':'application/json','x-craft-command-key':Buffer.from('anonymous-rich').toString('base64url')},body:'{"id":"24"}'}))).status,401);
 const overlayDir=path.join(dir,'overlay');createTechnicalErrorPresentationApplicationOwner({sourceOwner:p1.owner,sourceHandle:p1.handle,sdk:original,application:originalHandle}).emit({entry,outputDirectory:overlayDir});
 const overlay=createErrorPresentedBundledApplicationOwner(pathToFileURL(path.join(overlayDir,'application.mjs')).href);let oh:any,oa:any,or:any;try{oh=await overlay.prepare();assert.throws(()=>overlay.bindEntryHttp(oh,runtime,options),/ACCEPTANCE_REQUIRED/);accept(overlay,oh,dir,'overlay-decision');const actual=overlay.originalBinding(oh);oa=await createGenericAuthFixture(actual.sdk,actual.handle,{ownedDirectory:path.join(dir,'overlay-auth'),subjects:[{id:subject,evidence:'overlay-evidence',session:'overlay-session'}],grants:[{subject,entry},{subject,entry:read}]});const os=await prepareGenericFixtureRuntime(actual.sdk,actual.handle,{service:'ReviewDeskService',ownedDirectory:path.join(dir,'overlay-store'),nativeAuth:oa.nativeAuth});or=os.runtime;loadGenericFixture(os.fixture,Buffer.from(readFileSync(path.join(fixture,'fixture-rows.json'))));const handler=overlay.bindEntryHttp(oh,or,options);assert.equal((await handler(request('overlay-rejected'),oa.actor(or,subject,entry))).status,409);const service=overlay.bindServiceHttp(oh,or,{service:'ReviewDeskService'}),serviceRequest=new Request('https://fixture.invalid/approve',{method:'POST',headers:{'content-type':'application/json','x-craft-command-key':Buffer.from('service-rejected').toString('base64url')},body:'{"id":"24"}'});associateGenericHttpFixtureRequest(oa,service.handlerForRoute('ReviewHttp.Approve'),serviceRequest,subject);const serviceResult=await service(serviceRequest);assert.equal(serviceResult.status,409);assert.equal((await serviceResult.json()).error.code,'review-required');const missingRoute=await service(new Request('https://fixture.invalid/no-such-route'));assert.equal(missingRoute.status,404);assert.equal((await missingRoute.json()).kind,'error');const wrongMethod=await service(new Request('https://fixture.invalid/approve',{method:'GET'}));assert.equal(wrongMethod.status,405);assert.equal(wrongMethod.headers.get('allow'),'POST');assert.equal((await wrongMethod.json()).kind,'error');assert.throws(()=>overlay.bindServiceHttp(oh,or,{service:'ReviewDeskService',entryOverrides:{}}as any),/SERVICE_OPTIONS/);assert.throws(()=>service.handlerForRoute('Unknown.Route'),/ROUTE_REQUIRED/);assert.throws(()=>assertGenericErrorPresentationRuntime(b1,or));}finally{if(or)await or.close();if(oa)await oa.close();if(oh)overlay.dispose(oh);}
 const tableFile=path.join(overlayDir,'error-table.json'),saved=readFileSync(tableFile);writeFileSync(tableFile,'{}');assert.throws(()=>createErrorPresentedBundledApplicationOwner(pathToFileURL(path.join(overlayDir,'application.mjs')).href),/OUTPUT_CHANGED/);writeFileSync(tableFile,saved);

 }finally{if(runtime)await runtime.close();if(auth)await auth.close();if(p1)p1.owner.dispose(p1.handle);if(p2)p2.owner.dispose(p2.handle);if(handle)generated.dispose(handle);if(originalHandle)original.dispose(originalHandle);rmSync(dir,{recursive:true,force:true});}
});
