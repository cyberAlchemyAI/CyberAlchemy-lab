/** Focused imported-role lookup over original document/release owners. The Auth
 * access facade is a fixture; connected runtime tests own actual protected jobs.
 * Open Questions: goals/plans/craft-connected-applications-2026-11-02/DESIGN.md. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {createApplicationSourceGateway} from './gateway.mjs';
import {createSourceReleaseService} from '../source-release/index.mjs';
import {createDocumentAuthority} from '../documents/source-access/index.mjs';
import {APPLICATION_SYSTEM_BINDINGS,applicationSystemRoleSubjects} from './application-system-bindings.mjs';
import {canonical,sha256} from '../shared.mjs';
const roles=[{role:'facts',prefix:'support-facts-',format:'json',disclose:true},{role:'approval',prefix:'support-approval-',format:'json',disclose:false},{role:'review',prefix:'support-review-',format:'json',disclose:false},{role:'ragFacts',prefix:'rag-facts-',format:'json',disclose:true},{role:'documentA',prefix:'knowledge-a-',format:'binary',disclose:true},{role:'documentB',prefix:'knowledge-b-',format:'binary',disclose:true}];
function fixture(t,{id='2',roleSubjects}={}){
 const directory=mkdtempSync(path.join(tmpdir(),'gateway-subjects-')),release=createSourceReleaseService({path:path.join(directory,'release.sqlite')}),documents=createDocumentAuthority({path:path.join(directory,'documents.sqlite'),releaseAuthority:release.authority});t.after(()=>{documents.close();release.close();rmSync(directory,{recursive:true,force:true});});
 const profile={id:'source-subject-fixture',scope:'tenant',stages:[{}]},access={profile,assertCurrent(){},async refresh(){},async principal(){return {tenant:'tenant',actor:'operator'};},async job(){return {id,configurationDigest:sha256(canonical(profile))};}};
 for(const role of roles){const subject=roleSubjects?.[role.role]??id;documents.authority.put({id:role.prefix+subject,tenant:'tenant',version:'1',aclRevision:'1',readers:['operator'],classifications:['internal'],mediaType:'text/plain',bytes:new TextEncoder().encode(role.format==='binary'?'Original '+role.role:canonical({objectVersion:'1',role:role.role}))});}
 const configuration={access,documents:documents.port,release,roles,policyId:'review',target:{sink:'zendesk',recipient:'operator',recipientId:'5'},projections:{modelInput:{subjectId:{from:'id'}},review:{}}};
 return {documents,release,configuration,load:gateway=>gateway.load('operator',{id,run:'301'},{deferCapture:true})};
}
test('support consumer2 reads local roles2 and genuine declared producer1 sources without copying documents',async t=>{
 const binding=APPLICATION_SYSTEM_BINDINGS.find(row=>row.slot==='rag'),roleSubjects=applicationSystemRoleSubjects(binding,{run:{id:'1',run:'201'}}),f=fixture(t,{roleSubjects}),gateway=createApplicationSourceGateway({...f.configuration,roleSubjects}),snapshot=await f.load(gateway),source=gateway.inspect(snapshot);
 assert.equal(source.id,'2');assert.deepEqual(Object.fromEntries(Object.entries(source.sources).map(([role,row])=>[role,row.id])),{facts:'support-facts-2',approval:'support-approval-2',review:'support-review-2',ragFacts:'rag-facts-1',documentA:'knowledge-a-1',documentB:'knowledge-b-1'});
 assert.deepEqual(f.release.port.describeManifest(gateway.manifest(snapshot)).entries.map(row=>row.id).sort(),['support-facts-2','rag-facts-1','knowledge-a-1','knowledge-b-1'].sort());
 assert.throws(()=>f.documents.port.read({id:'knowledge-a-2',tenant:'tenant',principal:'operator'}),{code:'SourceUnavailable'},'no synthetic alias or duplicate source was created');
 f.documents.authority.setAccess({id:'knowledge-b-1',tenant:'tenant',aclRevision:'2',readers:[],classifications:['internal']});assert.throws(()=>gateway.inspect(snapshot),{code:'PermissionDenied'},'original imported document ACL still gates currentness');
});
test('source subject selection defaults to same-ID and rejects undeclared/non-UInt64 overrides',async t=>{
 const f=fixture(t,{id:'1'}),gateway=createApplicationSourceGateway(f.configuration),source=gateway.inspect(await f.load(gateway));assert.equal(source.sources.facts.id,'support-facts-1');assert.equal(source.sources.ragFacts.id,'rag-facts-1');
 for(const roleSubjects of [{unknown:'1'},{documentA:'-1'},{documentA:1},{documentA:'01'},{documentA:'18446744073709551616'}])assert.throws(()=>createApplicationSourceGateway({...f.configuration,roleSubjects}),{code:'InvalidContract'});
});

test('runtime subject rebinding changes input identity even for equal-content nondisclosed sources; empty map preserves default',async t=>{
 const f=fixture(t),sameReview={objectVersion:'1',role:'review'};f.documents.authority.put({id:'support-review-1',tenant:'tenant',version:'1',aclRevision:'1',readers:['operator'],classifications:['internal'],mediaType:'text/plain',bytes:new TextEncoder().encode(canonical(sameReview))});
 const original=createApplicationSourceGateway(f.configuration),empty=createApplicationSourceGateway({...f.configuration,roleSubjects:{}}),rebound=createApplicationSourceGateway({...f.configuration,roleSubjects:{review:'1'}}),first=await f.load(original),second=await f.load(empty),third=await f.load(rebound);
 assert.equal(original.inspect(first).sources.review.sha256,rebound.inspect(third).sources.review.sha256,'two genuine records deliberately have equal content');assert.equal(original.manifest(first).id,rebound.manifest(third).id,'private review is not disclosed');assert.equal(original.binding(first).inputDigest,empty.binding(second).inputDigest,'omitted and empty bindings retain original identity');assert.notEqual(original.binding(first).inputDigest,rebound.binding(third).inputDigest,'actual runtime source binding belongs to selection identity');
});
