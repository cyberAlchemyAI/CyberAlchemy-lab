/** Focused CG02 checks through the original generated Auth/SQLite Query owner.
 * Open Questions: ../../../../goals/plans/craft-crm-business-only-generation-2026-11-01/DESIGN.md. */
import test from 'node:test';
import {DatabaseSync} from 'node:sqlite';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createGenericCompositionOwner} from '@domainspec-v2/cli/generic';
import {createGenericAuthFixture,prepareGenericFixtureRuntime} from '@domainspec-v2/cli/generic/testing';
import {compileApplicationProfile,createApplicationAccess,createApplicationQuerySource,sha256} from '@craft/ai-profiles/application';
import {createSourceReleaseService} from '@craft/ai-profiles/source-release';
const repo=fileURLToPath(new URL('../../../../',import.meta.url));
const appDirectory=path.join(repo,'implementation/craft-ai-reference-apps/crm');
const decode=value=>JSON.parse(new TextDecoder().decode(value.bytes));

async function genuinePreferenceRuntime(t){
 const directory=mkdtempSync(path.join(tmpdir(),'cg02-query-inputs-'));
 const component=path.join(appDirectory,'preferences.alch');
 const profile={schema:'craft.ai-application-profile/v1',id:'crm-query-inputs',module:'CrmOperations',service:'CrmProfileService',scope:'reference-operations',entryAccess:{sourcePath:path.join(appDirectory,'entries.alch'),entry:'CrmOperationsAccess.PrepareContactUpdateEntry'},operation:'PrepareContactUpdate',types:{request:'ReviewRequest',modelInput:'ModelRequest',proposal:'Proposal',decision:'Decision'},stages:[{name:'evaluation',kind:'model',capability_binding:'Crm.QueryInputFixture',capability_sha256:'1'.repeat(64),deadline_ms:30000}],additionalSources:[{sourcePath:component,sha256:sha256(readFileSync(component))}]};
 const compiled=compileApplicationProfile({businessSourcePath:path.join(appDirectory,'journey.alch'),profile,baseProfile:JSON.parse(readFileSync(path.join(appDirectory,'contracts/eligibility-profile.json'),'utf8')),outputDirectory:path.join(directory,'source')});
 const accept=(owner,handle,name)=>{const review=owner.review(handle,name);owner.accept(handle,{decision_id:name,owner:name,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,name+'.json'));};
 const build=createGenericCompositionOwner(),built=await build.prepare({sourcePath:compiled.sourcePath,profilePath:compiled.profilePath});
 let owner,handle,auth,runtime,release;
 t.after(async()=>{try{if(runtime)await runtime.close();if(auth)await auth.close();if(handle)owner.dispose(handle);build.dispose(built);if(release)release.close();}finally{rmSync(directory,{recursive:true,force:true});}});
 accept(build,built,'query-source-generate');const generated=path.join(directory,'generated');build.generate(built,{entry:compiled.selectors.start,outputDirectory:generated});
 const {createGeneratedApplicationOwner}=await import(pathToFileURL(path.join(generated,'application.mjs')).href);owner=createGeneratedApplicationOwner();handle=await owner.prepare();accept(owner,handle,'query-source-runtime');
 const entry='CrmOperations.ReadContactPreferenceEntry',record='CrmOperations.RecordContactPreferenceEntry',change='CrmOperations.ChangeContactPreferenceEntry';
 auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth'),sessionTtlSeconds:7200,subjects:[{id:'operator',evidence:'operator-evidence',session:'operator-session'}],grants:[entry,record,change].map(entry=>({subject:'operator',entry}))});
 const fixture=await prepareGenericFixtureRuntime(owner,handle,{service:profile.service,ownedDirectory:path.join(directory,'store'),nativeAuth:auth.nativeAuth});runtime=fixture.runtime;
 release=createSourceReleaseService({path:path.join(directory,'source-release.sqlite')});
 const access=createApplicationAccess({composition:owner,handle,runtime,profile});
 const actor=id=>auth.actor(runtime,'operator',id);
 const command=async(id,preference,key)=>{const result=await access.command(actor(id),id,{preference},key);assert.equal(result.outcome.kind,'Returned',JSON.stringify(result));};
 return {directory,owner,handle,runtime,auth,release,entry,record,change,actor,command,base:{composition:owner,handle,runtime,actor:actor(entry),entry,releaseAuthority:release.authority}};
}

test('CG02 descriptors reject ambiguous, executable and unbounded source selections before owner formation',async()=>{
 const invalid=[
  {inputs:new Map([['x',[{contactId:'1'}]]]),subjectInputs:{prefix:'preferences-',inputField:'contactId'}},
  {subjectInputs:{prefix:'preferences-',inputField:'contactId',execute(){}}},
  {subjectInputs:{prefix:'preferences-',inputField:'contact.id'}},
  {subjectInputs:{prefix:'preferences-',inputField:'__proto__'}},
  {subjectInputs:{prefix:'',inputField:'contactId'}},
  {subjectInputs:{prefix:'preferences-',inputField:'contactId'},resultView:{kind:'single-record',identityField:'contactId',coerce:true}},
  {subjectInputs:{prefix:'preferences-',inputField:'contactId'},resultView:{kind:'single-record',identityField:'contactId'},collectionField:'renamed'},
  {inputs:new Map(Array.from({length:101},(_,i)=>[String(i),[{contactId:String(i)}]]))}
 ];
 for(const selection of invalid)await assert.rejects(createApplicationQuerySource({entry:'Entry',adapterId:'descriptor-check',...selection}),{code:'InvalidContract'});
});

test('CG02 dynamic subjects use genuine Query leases; record identity, versions, revocation and legacy mode remain distinct',{timeout:900000},async t=>{
 const f=await genuinePreferenceRuntime(t);
 let rejectedPort;
 await assert.rejects(createApplicationQuerySource({...f.base,adapterId:'failed-registration',inputs:new Map([['selected-8',[{contactId:'8'}]]]),releaseAuthority:{registerAdapter(id,port){rejectedPort=port;throw Error('fixture registration failure');}}}),/fixture registration failure/);
 assert.throws(()=>rejectedPort.readCurrent({id:'selected-8',tenant:'reference-operations',principal:'operator'}),{code:'StaleOwner'},'failed registration closes its actual Query owner');
 const preference=id=>({contactId:id,email:'person-'+id+'@example.test',version:'2',allowed:true,identityVerified:true});
 await f.command(f.record,preference('8'),'preference-8-v2');
 const source=await createApplicationQuerySource({...f.base,adapterId:'dynamic-preferences',subjectInputs:{prefix:'preferences-',inputField:'contactId'},resultView:{kind:'single-record',identityField:'contactId'}});t.after(()=>source.close());
 const request=id=>({id:'preferences-'+id,tenant:'reference-operations',principal:'operator'});
 const first=await source.read(request('8'));assert.deepEqual(decode(first),{record:preference('8')});assert.match(first.revision,/^[a-f0-9]{64}$/);assert.equal(decode(first).record.version,'2');assert.equal(first.sha256,sha256(first.bytes));
 await assert.rejects(source.read({...request('8'),principal:'forged'}),{code:'PermissionDenied'});
 assert.deepEqual(decode(source.readCurrent(request('8'))),decode(first),'failed principal read preserves the last valid head');
 await assert.rejects(source.read({...request('8'),tenant:'another-tenant'}),{code:'PermissionDenied'});
 await assert.rejects(source.read(request('08')),{code:'InvalidContract'});
 await assert.rejects(source.read(request('18446744073709551616')),{code:'InvalidContract'});
 await assert.rejects(source.read({...request('8'),id:'wrong-8'}),{code:'SourceUnavailable'});
 await assert.rejects(source.read(request('9')));assert.deepEqual(decode(source.readCurrent(request('8'))),decode(first),'missing subject does not replace another head');
 // A new subject is discovered after opening; no authored/static Map is rebuilt.
 await f.command(f.record,preference('9'),'preference-9-v2');
 const second=await source.read(request('9'));assert.equal(decode(second).record.contactId,'9');assert.equal(decode(second).record.version,'2');
 assert.notEqual(second.revision,first.revision,'same business version can have a different opaque observation revision');
 const beforeChange=await source.read(request('8'));
 assert.equal(decode(beforeChange).record.version,'2');
 assert.equal(beforeChange.revision,first.revision,'an unrelated contact cannot change the exact keyed Query observation revision');
 await f.command(f.change,{...preference('8'),version:'3',allowed:false},'preference-8-v3');
 assert.throws(()=>source.readCurrent(request('8')),'original storage currentness rejects the old lease');
 const updated=await source.read(request('8'));assert.equal(decode(updated).record.allowed,false);assert.equal(decode(updated).record.version,'3');assert.notEqual(updated.revision,beforeChange.revision);
 // Fault injection changes only the original hidden revision, not the
 // business payload/version. The exact original Query lease must still stale.
 const table=JSON.parse(readFileSync(path.join(f.directory,'generated/storage/schema.json'),'utf8')).tables.find(t=>t.entity==='CrmOperations.StoredContactPreference');
 assert.match(table.physical_name,/^craft_[a-f0-9_]+$/);assert.equal(table.revision_column,'_craft_revision');const identity=table.columns.find(c=>c.name==='contactId').sql_name;assert.match(identity,/^f_[a-f0-9]+$/);
 const database=new DatabaseSync(path.join(f.directory,'store/store.sqlite'));
 try{const previous=database.prepare(`SELECT "_craft_revision" AS value FROM "${table.physical_name}" WHERE "${identity}"=?`).get('8'),next=Buffer.from(previous.value);next.writeBigUInt64BE(next.readBigUInt64BE()+1n);database.prepare(`UPDATE "${table.physical_name}" SET "_craft_revision"=? WHERE "${identity}"=?`).run(next,'8');}finally{database.close();}
 assert.throws(()=>source.readCurrent(request('8')),'selected hidden revision participates in original Query custody');
 const sameBusiness=await source.read(request('8'));assert.equal(decode(sameBusiness).record.version,'3');assert.notEqual(sameBusiness.revision,updated.revision,'business version is not the opaque observation revision');
 const badIdentity=await createApplicationQuerySource({...f.base,adapterId:'wrong-record-identity',subjectInputs:{prefix:'preferences-',inputField:'contactId'},resultView:{kind:'single-record',identityField:'version'}});t.after(()=>badIdentity.close());
 await assert.rejects(badIdentity.read(request('8')),{code:'ForeignOwner'});assert.throws(()=>badIdentity.readCurrent(request('8')),{code:'PermissionDenied'});
 const legacy=await createApplicationQuerySource({...f.base,adapterId:'legacy-preferences',inputs:new Map([['legacy-8',[{contactId:'8'}]]])});t.after(()=>legacy.close());
 const legacyRequest={...request('8'),id:'legacy-8'},oldFormat=await legacy.read(legacyRequest);assert.deepEqual(decode(oldFormat),{records:[{...preference('8'),version:'3',allowed:false}]});
 f.auth.setPermission('operator',f.entry,false);assert.throws(()=>source.readCurrent(request('8')));await assert.rejects(source.read(request('8')));
 f.auth.setPermission('operator',f.entry,true);await source.read(request('8'));
 source.close();source.close();assert.throws(()=>source.readCurrent(request('8')),{code:'StaleOwner'});await assert.rejects(source.read(request('8')),{code:'StaleOwner'});
 const reopened=await createApplicationQuerySource({...f.base,adapterId:'dynamic-preferences',subjectInputs:{prefix:'preferences-',inputField:'contactId'},resultView:{kind:'single-record',identityField:'contactId'}});t.after(()=>reopened.close());
 assert.equal(decode(await reopened.read(request('9'))).record.contactId,'9','fresh source owner reuses its retired adapter ID and discovers subject without a prebuilt Map');
});
