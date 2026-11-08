import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
// Actual public selection -> original early owner only. No accepted input/callable.
// Open Questions: Q02 context; later U04/U08 retain this same live lineage.
const core=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),root=path.resolve(core,'../../../../..'),out=path.join(root,'implementation/craft-alchlang-commerce-2026-10-16/evidence/Q02'),alch=path.join(root,'language/capabilities/alchlang/plans/general-compiler-v1/implementation');
process.env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT=core;
const front=await import(pathToFileURL(path.join(alch,'dist/index.js')).href),sourceRoot=path.join(out,'../J02/selected-project'),choice={profile:'node-http-entry-u0-v4',output:'code'};
const prepare=()=>front.prepareDirectBusinessAuthoringProjectV2(sourceRoot,'business.alch',choice);

test('original early request carries source/entry/Interface/Mapping lineage before any callable or native binding',async()=>{
 const p=await prepare();try{const r=p.runtime.requests,early=p.early,source=r.source(early),model=p.selection.models[0],entry=source.entries[0];r.assertEarlyCurrent(early);assert.equal(early.selection,p.selection);assert.equal(source.source_sha256,model.source.sha256);assert.equal(source.executable_sha256,model.executable_sha256);
  assert.equal(entry.logical_id,'ProcessHttp');assert.equal(entry.operation_ref,'dispatching:process');assert.equal(entry.rule_ref,'dispatching:can-process');assert.equal(entry.interface_ref,'dispatching:process-http');assert.equal(entry.permission.kind,'public');assert.equal(entry.mappings.input,'dispatching:craftrequest-process-http-input');assert.equal(entry.mappings.output,'dispatching:craftrequest-process-http-output');
  assert.deepEqual(entry.mappings.fields.map((f:any)=>[f.name,f.scalar,f.identity]),[['id','UInt64',true],['verified','Bool',false]]);assert.equal(entry.origins.length,5);assert(entry.origins.every((o:any)=>o.source==='business.alch'&&o.sha256===model.source.sha256));
  assert.deepEqual(early.entries[0].unresolved_native_obligations.map((o:any)=>o.producer),['generated-callable','exact-codec','injected-handler','request-graph']);
  const noLate=(value:any)=>{if(value&&typeof value==='object')for(const [key,child]of Object.entries(value)){assert.equal(['callable','invoke','handler','realized_sha256','accepted','route'].includes(key),false,key);noLate(child);}};noLate(early);noLate(source);assert.equal(Object.hasOwn(p,'accepted'),false);assert.equal(Object.hasOwn(p,'callable'),false);
  const j02=JSON.parse(fs.readFileSync(path.join(out,'../J02/selected-source-observation-verified.json'),'utf8'));assert.equal(p.selection.selection_sha256,j02.selection.selection_sha256);assert.equal(p.runtime.basis.basis_sha256,j02.basis_sha256);
  fs.writeFileSync(path.join(out,'early-request-observation.json'),JSON.stringify({schema_version:'craft.u0-early-request-observation/v1-candidate',selection_sha256:p.selection.selection_sha256,early,request_source:source,original_selection_pointer_preserved:true,callable:'not-generated',accepted_input:'not-created',native_obligations:'all-four-pending',authority_effect:'none',open_questions_ref:'CONTEXT.md#open-questions'},null,2)+'\n',{flag:'wx'});
 }finally{front.disposeDirectBusinessAuthoringProjectV2(p);}
});

test('original early producer rejects serialized/foreign/wrong-stage/callback substitutions without executing callbacks',async()=>{
 const p=await prepare(),foreign=await prepare();let calls=0;const callback=()=>{calls++;throw Error('must not execute');};
 try{const r=p.runtime.requests;r.assertEarlyCurrent(p.early);assert.throws(()=>r.assertEarlyCurrent(structuredClone(p.early)));assert.throws(()=>r.source(structuredClone(p.early)));assert.throws(()=>foreign.runtime.requests.assertEarlyCurrent(p.early));assert.throws(()=>r.prepareEarly(foreign.selection));
  for(const wrong of [{selection:p.selection,generate:callback},{kind:'bound-u0-entry-v2',invoke:callback},p.early])assert.throws(()=>r.prepareEarly(wrong));
  await assert.rejects(()=>r.bindLate(p.early,{invoke:callback},p.runtime.basis));assert.throws(()=>r.assertBoundCurrent(p.early));assert.equal(calls,0);
 }finally{front.disposeDirectBusinessAuthoringProjectV2(p);front.disposeDirectBusinessAuthoringProjectV2(foreign);}
});

test('source drift invalidates the original early handle even while its copied data is unchanged',async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'craft-q02-source-'));try{const file=path.join(temp,'business.alch');fs.copyFileSync(path.join(sourceRoot,'business.alch'),file);const p=await front.prepareDirectBusinessAuthoringProjectV2(temp,'business.alch',choice),before=JSON.stringify(p.early);fs.appendFileSync(file,'\n');assert.equal(JSON.stringify(p.early),before);assert.throws(()=>p.runtime.requests.assertEarlyCurrent(p.early));}finally{fs.rmSync(temp,{recursive:true,force:true});}
});
