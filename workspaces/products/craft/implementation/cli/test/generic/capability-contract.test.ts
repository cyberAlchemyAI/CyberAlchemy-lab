import test from 'node:test';
import assert from 'node:assert/strict';
import {dataDigest} from '../../src/profile-engine/contracts.js';
import {validateGenericCapabilitySelection,validateGenericContextManifest,validateGenericReleaseTicketData,validateGenericTrustedSearchContextData,validateGenericContinuation} from '../../src/generic/capability-contract.js';
import {capabilityFixture} from './capability-fixtures.js';

test('P01 direct inference reuses kernel and rejects unsupported or ambiguous selections',()=>{
 const {selection,kernel}=capabilityFixture();const v=validateGenericCapabilitySelection(selection,kernel);
 assert.equal(v.bindings[0]!.contract.kind,'inference/v1');assert.ok(Object.isFrozen(v.bindings));
 for(const mutate of [
  (s:any)=>s.bindings.push({...s.bindings[0]}),
  (s:any)=>s.bindings[0].realization_ref='Missing',
  (s:any)=>s.bindings[0].interface='Example.Other',
  (s:any)=>s.realizations[0].capabilities=[],
  (s:any)=>s.bindings[0].bounds={...s.bindings[0].bounds,max_tool_calls:1},
  (s:any)=>s.realizations[0].lifecycle.fallback='automatic',
  (s:any)=>s.realizations[0].implementation.version='latest',
  (s:any)=>s.realizations[0].implementation.package='../../unowned',
  (s:any)=>s.realizations[0].implementation.export='./../../unowned',
  (s:any)=>s.realizations[0].contract='agent-run/v1',
  (s:any)=>s.realizations[0].operations.push('agent.run'),
  (s:any)=>s.bindings[0].contract.operation='vector.embed',
  (s:any)=>s.bindings[0].contract.raw_sql='select *',
  (s:any)=>s.realizations[0].mode='provider',
  (s:any)=>s.bindings[0].bounds={...s.bindings[0].bounds,max_input_bytes:100000},
  (s:any)=>s.realizations[0].target.destination='https://user:secret@example.com',
 ]){const copy=structuredClone(selection);mutate(copy);assert.throws(()=>validateGenericCapabilitySelection(copy,kernel));}
 const stale=structuredClone(kernel);stale.provider_profiles[0].capability_set=['inference/v1'];assert.throws(()=>validateGenericCapabilitySelection(selection,stale),/DIGEST/);
});
test('P01 source manifest, release data and continuation are closed data, not authority',()=>{
 const manifest={schema_version:'craft.source-context-manifest/v1',tenant:'review-desk',dependencies:[{source:'Example.Source',revision:'1',content_sha256:'a'.repeat(64),acl_revision:'1',policy_revision:'2',role:'input'}],context_sha256:'b'.repeat(64),authority_effect:'none'};
 assert.equal(validateGenericContextManifest(manifest).dependencies.length,1);
 assert.throws(()=>validateGenericContextManifest({...manifest,dependencies:[...manifest.dependencies,...manifest.dependencies]}));
 const ticket={schema_version:'craft.source-release-ticket/v1',manifest_sha256:dataDigest(manifest),tenant:'review-desk',attempt:'attempt-123',fence:1,output_sha256:'c'.repeat(64),destination:'fixture://model',recipient:'fixture-reviewer-a',expires_at_ms:1000,use:'single-use',authority_effect:'none'};
 assert.equal(validateGenericReleaseTicketData(ticket).use,'single-use');assert.throws(()=>validateGenericReleaseTicketData({...ticket,secret:'bad'}));
 const context={schema_version:'craft.trusted-search-context/v1',tenant:'review-desk',actor:'fixture-reviewer-a',source_scope:['Example.Source'],grants_revision:'1',source_policy_revision:'1',fence:1,deadline_ms:1000,origin:'original-server-owner',authority_effect:'none'};
 assert.equal(validateGenericTrustedSearchContextData(context).origin,'original-server-owner');assert.throws(()=>validateGenericTrustedSearchContextData({...context,sql:'SELECT 1'}));
 assert.equal(validateGenericContinuation({kind:'retry',attempt:1,maximum:2,not_before_ms:1000,dispatch_evidence:'proven-not-dispatched'}).kind,'retry');
 assert.throws(()=>validateGenericContinuation({kind:'retry',attempt:3,maximum:2,not_before_ms:1000,dispatch_evidence:'proven-not-dispatched'}));
 assert.throws(()=>validateGenericContinuation({kind:'retry',attempt:1,maximum:2,not_before_ms:1000,dispatch_evidence:'unknown'}));
});
test('P01 optional agent, embedding, document and bounded search remain finite distinct variants',()=>{
 for(const kind of ['agent-run/v1','document/v1','search/v1','inference/v1']){
  const {selection:s,kernel:k}=capabilityFixture();const c=s.bindings[0].contract,r=s.realizations[0];
  const table:any={'agent-run/v1':['agent.run','local-inspect'],'document/v1':['document.parse','document-parse'],'search/v1':['search.query','bounded-search'],'inference/v1':['vector.embed','embeddings']};
  const [operation,cap]=table[kind];const common={kind,operation,input_type:c.input_type,result_type:c.result_type,required_capabilities:[cap]};
  s.bindings[0].contract=kind==='agent-run/v1'?{...common,loop_owner:'selected-harness',tools:[{name:'Example.Read',entry:'Example.ReadEntry',query:'Example.ReadQuery',argument_codec:{kind:'scalar',name:'UInt64'},result_codec:{kind:'optional',element:{kind:'record',name:'Example.Item'}},effect:'read-only'}],checkpoint_version:'1'}:kind==='search/v1'?{...common,search:{technique:'keyword',collection:'Example.Documents',top_k:10,max_candidates:50,filter_fields:['category'],filter_operators:['eq'],tenant_scope:'original-owner-required',source_access:'original-owner-required',embedding_space:null}}:kind==='inference/v1'?{...common,tools:'disabled',embedding:{dimensions:16,preprocessing_ref:'Example.Preprocess',space_generation:'Example.Embedding1'}}:common;
  r.contract=kind;r.operations=[operation];r.capabilities=[cap];if(kind==='inference/v1'){r.schema.subset='finite-vector/v1';s.bindings[0].contract.result_type='Craft.Native.FiniteVector';}
  k.provider_profiles[0].capability_set=[kind,cap];if(kind==='agent-run/v1'){r.capabilities.push('readonly-tools');k.provider_profiles[0].capability_set.push('readonly-tools');}k.integration_bindings[0].contract_ref=kind;s.kernel.sha256=dataDigest(k);
  assert.equal(validateGenericCapabilitySelection(s,k).bindings[0]!.contract.kind,kind);
 }
});
