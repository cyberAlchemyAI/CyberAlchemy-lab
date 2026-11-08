import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {deriveBusinessApplicationBindings,assertDerivedBusinessApplicationCurrent} from '../src/business-application-bindings.js';
import {json,digest} from '../src/domainspec-profile.js';
// Open questions: full executable/request/native/installed gates BA03–BA18.
const repo=path.resolve(import.meta.dirname,'../../../../../../..'),cli=path.join(repo,'craft/projects/domainspec-v2/impl/cli');
async function fixture(t:any){const engine=await import(pathToFileURL(path.join(cli,'src/profile-engine/index.ts')).href);const root=mkdtempSync(path.join(os.tmpdir(),'business-bindings-'));t.after(()=>rmSync(root,{recursive:true,force:true}));cpSync(path.join(cli,'test/profile-engine/fixtures/business-notice'),root,{recursive:true});const file=path.join(root,'project.json'),p=JSON.parse(readFileSync(file,'utf8'));p.profiles[0].path=path.join(cli,'profiles/node-http-entry-local-v2');writeFileSync(file,JSON.stringify(p));const snapshot=engine.loadProfileProjectV2(file,{engine:[{key:'contracts',path:path.join(cli,'src/profile-engine/contracts-v2.ts')}],tools:[{key:'node',path:process.execPath}]});return {root,engine,input:engine.prepareBusinessInputV2(snapshot)};}

test('explicit accepted business records produce current formal/declaration/ground Rule carriers without technical authored files',async t=>{
 const f=await fixture(t),d=deriveBusinessApplicationBindings(f.input,'commerce',f.engine);assert.equal(d.formation.model.declarations.length,3);assert.equal(d.projection.trace.projections.length,1);assert.equal(Object.keys(d.files).length,6);
 const claim=d.bindings.formal.formal_claims.IdentityClaim,accepted=JSON.parse(d.files[claim.business_acceptance_ref.path]!),meaning=JSON.parse(d.files[claim.business_meaning_ref.path]!);
 assert.equal(f.engine.dataDigest(accepted),f.engine.dataDigest(f.input.applications[0].semantics.claim_meanings.IdentityClaim.owner_acceptance));assert.equal(meaning.status,'accepted');assert.equal(d.interpretation.formation_sha256,digest(json(d.formation)));assert.equal(d.projection.trace.projections[0]!.proof,false);
 assert.equal(d.source.split('\n').filter(line=>line==='profile application-v1').length,1);assert.equal(d.line_map.filter(l=>l.origin==='adapter').length,1);assert.ok(d.line_map.filter(l=>l.origin==='business').every(l=>l.original_line!==null));
 assertDerivedBusinessApplicationCurrent(d);assert.equal(deriveBusinessApplicationBindings(f.input,'commerce',f.engine).derivation_sha256,d.derivation_sha256);
});
test('derived resource/formation changes and stale original inputs cannot masquerade as current',async t=>{
 const f=await fixture(t),d=deriveBusinessApplicationBindings(f.input,'commerce',f.engine);assert.throws(()=>assertDerivedBusinessApplicationCurrent(JSON.parse(JSON.stringify(d))),/UNREGISTERED/);
 const name=[...d.sources.keys()][0]!;d.sources.get(name)![0]=0;assert.throws(()=>assertDerivedBusinessApplicationCurrent(d),/RESOURCE_CHANGED/);
 const clean=deriveBusinessApplicationBindings(f.input,'commerce',f.engine);writeFileSync(path.join(f.root,'domain.alch'),readFileSync(path.join(f.root,'domain.alch'),'utf8')+'\n');assert.throws(()=>assertDerivedBusinessApplicationCurrent(clean),/STALE/);
});
