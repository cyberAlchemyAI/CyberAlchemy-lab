/** Source error tables use original Core semantics and original source custody.
 * Open Questions: docs/ERROR-PRESENTATION.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createTechnicalProfileSourceOwner} from '../../src/profile-engine/technical-profile-source.js';
const examples=fileURLToPath(new URL('../../examples/technical-profile-source/',import.meta.url));
function fixture(t:any){
 const root=mkdtempSync(path.join(os.tmpdir(),'craft-error-source-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 for(const name of ['error-crm.alch','error-crm-domain.alch','error-crm.profile.json','error-contract.json','error-family.json','error-obligations.json'])writeFileSync(path.join(root,name),readFileSync(path.join(examples,name)));
 const owner=createTechnicalProfileSourceOwner(),manifestPath=path.join(root,'error-crm.profile.json');
 return {root,owner,manifestPath,load:()=>owner.prepare({sourceRoot:root,manifestPath}),source(change:(s:string)=>string){const f=path.join(root,'error-crm.alch');writeFileSync(f,change(readFileSync(f,'utf8')));},domain(change:(s:string)=>string){const f=path.join(root,'error-crm-domain.alch');writeFileSync(f,change(readFileSync(f,'utf8')));},manifest(change:(v:any)=>void){const value=JSON.parse(readFileSync(manifestPath,'utf8'));change(value);writeFileSync(manifestPath,JSON.stringify(value));}};
}
test('EM02 complete CRM source Policy then outside Mapping derives twelve checked rows',t=>{
 const f=fixture(t),handle=f.load();try{const a=f.owner.inspectErrorPresentation(handle);assert.equal(a.rows.length,12);assert.equal(a.rows.find(r=>r.internalCode==='preference-changed')?.httpStatus,409);assert.equal(a.rows.find(r=>r.internalCode==='preference-denied')?.httpStatus,403);assert.equal(a.rows.find(r=>r.internalCode==='unsupported-enrichment')?.httpStatus,422);assert.equal(a.producer,'CrmOperations.PrepareContactUpdate');assert.match(a.reason_type_sha256,/^[a-f0-9]{64}$/);assert.match(a.presentation_version,/^[a-f0-9]{64}$/);assert.ok(Object.isFrozen(a));assert.ok(Object.isFrozen(a.rows));assert.equal(f.owner.inspect(handle).target_consumer,'craft.error-presentation/v1');}finally{f.owner.dispose(handle);}
});
test('EM02 source profile compilation reopens exact table and rejects descriptor/source tampering',t=>{
 const f=fixture(t),handle=f.load(),out=path.join(f.root,'compiled');try{f.owner.publishSelection(handle,out);const owner=createTechnicalProfileSourceOwner(),other=owner.prepareCompiled(path.join(out,'selection.json'));try{assert.deepEqual(owner.inspectErrorPresentation(other),f.owner.inspectErrorPresentation(handle));const artifact=path.join(out,'selection.json');writeFileSync(artifact,readFileSync(artifact,'utf8')+'\n');assert.throws(()=>owner.inspectErrorPresentation(other),/STALE/);}finally{owner.dispose(other);}}finally{f.owner.dispose(handle);}
});
test('EM02 missing and duplicate rows reject even when author omits optional record invariants',t=>{
 for(const mutate of [(s:string)=>s.replace('ContactUpdateRejection.SourceStale,ContactUpdateRejection.DisclosureDenied','ContactUpdateRejection.DisclosureDenied'),(s:string)=>s.replace('field cases <- map([ContactUpdateRejection.SourceStale,','field cases <- map([ContactUpdateRejection.DisclosureDenied,')]){
  const f=fixture(t);f.source(s=>mutate(s.replace('  invariant length(cases) == 12\n','').replace('  invariant all-unique-exact(map(cases,item:ErrorCase => item.reason))\n','')));assert.throws(f.load,/ERROR_PRESENTATION/);
 }
});
test('EM02 enum growth and Unmapped are generation errors',t=>{
 const grown=fixture(t);grown.domain(s=>s.replace('enum ContactUpdateRejection:\n','enum ContactUpdateRejection:\n  value NewReason wire "new-reason"\n'));assert.throws(grown.load,/complete actual reason enum/);
 const unmapped=fixture(t);unmapped.source(s=>s.split('\n').filter(line=>!line.includes('    preferenceChanged when ')).join('\n'));assert.throws(unmapped.load,/mapped bounded public error code/);
});
test('EM02 nominal reason type cannot be replaced by same-wire foreign enum',t=>{
 const f=fixture(t),other=readFileSync(path.join(f.root,'error-crm-domain.alch'),'utf8').replace('module CrmOperations version 1','module OtherDomain version 1').replace('enum ContactUpdateRejection:','enum OtherReason:');writeFileSync(path.join(f.root,'error-foreign.alch'),other);f.manifest(v=>v.sources.push('error-foreign.alch'));f.source(s=>s.replace('use CrmOperations.ContactUpdateRejection','use OtherDomain.OtherReason').replaceAll('ContactUpdateRejection','OtherReason'));assert.throws(f.load,/exact selected nominal reason enum/);
});
test('EM02 public code/message/status restrictions reject forged presentation',t=>{
 for(const change of [(s:string)=>s.replace('code="source-stale"','code="bad/code"'),(s:string)=>s.replace('The source changed. Review the latest data.','x'.repeat(513)),(s:string)=>s.replace('The source changed. Review the latest data.','line\\nnext'),(s:string)=>s.replace('category=Conflict,httpStatus=409','category=Conflict,httpStatus=403')]){const f=fixture(t);f.source(change);assert.throws(f.load,/EVALUATION|ERROR_PRESENTATION|TypeMismatch|bound|refinement|literal/i);}
});
test('EM02 profile resources/runtime selection arguments and unknown hooks cannot be smuggled in',t=>{
 for(const change of [(v:any)=>{v.selection.arguments={request:'not-public'};},(v:any)=>{v.execute='javascript';},(v:any)=>{v.target.package_schema='craft.technical-profile-runtime/v1';}]){const f=fixture(t);f.manifest(change);assert.throws(f.load,/ERROR_PRESENTATION|SCHEMA|CONSUMER/);}
});
test('EM02 stale original source and foreign handles cannot reuse checked table',t=>{
 const f=fixture(t),handle=f.load();assert.throws(()=>createTechnicalProfileSourceOwner().inspectErrorPresentation(handle),/OWNER/);assert.throws(()=>f.owner.inspectErrorPresentation({kind:'original-checked-technical-profile-source/v1'}),/OWNER/);f.source(s=>s+'\n');assert.throws(()=>f.owner.inspectErrorPresentation(handle),/STALE/);f.owner.dispose(handle);
});

test('EM02 full original CRM file is captured but only its reason Enum enters technical admission',t=>{
 const f=fixture(t),business=fileURLToPath(new URL('../../../../../../../implementation/craft-ai-reference-apps/crm/journey.alch',import.meta.url));
 f.domain(()=>readFileSync(business,'utf8'));const handle=f.load();
 try{const table=f.owner.inspectErrorPresentation(handle);assert.equal(table.rows.length,12);assert.equal(table.source.reason_projection?.path,'error-crm-domain.alch');assert.match(table.source.reason_projection?.projection_sha256??'',/^[a-f0-9]{64}$/);const out=path.join(f.root,'compiled-full-business');f.owner.publishSelection(handle,out);assert.match(readFileSync(path.join(out,'sources/error-crm-domain.alch'),'utf8'),/enforce ContactUpdateEligibility/,'compiled closure must retain unchanged full original source');const owner=createTechnicalProfileSourceOwner(),compiled=owner.prepareCompiled(path.join(out,'selection.json'));try{assert.deepEqual(owner.inspectErrorPresentation(compiled),table);}finally{owner.dispose(compiled);}}
 finally{f.owner.dispose(handle);}
});
