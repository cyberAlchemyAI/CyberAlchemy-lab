/** Exact source-selected cited review over the original RAG, pure Mapping,
 * protected command/Query and source-release owners. No inference/storage engine,
 * identity issuer or distributed transaction is introduced.
 * Open Questions: goals/plans/craft-connected-applications-2026-11-02/DESIGN.md.
 */
import path from 'node:path';
import {types} from 'node:util';
import {readFileSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
import {createGenericCompositionOwner,createGenericQueryObservationOwner,assertGenericApplicationRuntime,inspectGenericNativeProfileArtifact,assertGenericNativeProfileArtifact} from '@domainspec-v2/cli/generic';
import {assert,capture,canonical,sha256,freeze,closed,text,u64} from '../shared.mjs';
const originalSources=new WeakMap(),loadedSourceSha256=sha256(readFileSync(new URL(import.meta.url)));
const implementationCurrent=()=>assert(sha256(readFileSync(new URL(import.meta.url)))===loadedSourceSha256,'StaleOwner','loaded cited review implementation changed');
// Opaque original resources never pass through the inert JSON copier.
function references(value,keys){
 assert(value&&typeof value==='object'&&!types.isProxy(value)&&[Object.prototype,null].includes(Object.getPrototypeOf(value)),'InvalidContract','plain original resource container');
 const descriptors=Object.getOwnPropertyDescriptors(value),actual=Reflect.ownKeys(descriptors);
 assert(actual.length===keys.length&&actual.every(key=>typeof key==='string'&&keys.includes(key)&&descriptors[key].enumerable&&Object.hasOwn(descriptors[key],'value')),'InvalidContract','exact own-data resource fields');
 return Object.freeze(Object.fromEntries(keys.map(key=>[key,descriptors[key].value])));
}
/** Internal bootstrap registration; not exported by the public package. */
export function registerOriginalCitedReviewSource(application,{readAnswer,assertCurrent,release,artifact}){
 assert(application&&typeof application==='object'&&!originalSources.has(application)&&typeof readAnswer==='function'&&typeof assertCurrent==='function'&&release?.abi==='source-release-port/v1','ForeignOwner','original generated RAG/source-release review source');
 const selected=inspectGenericNativeProfileArtifact(artifact);assert(selected.name==='@craft/ai-profiles'&&selected.files.some(file=>file.path==='native/application/cited-review.mjs'&&file.sha256===loadedSourceSha256),'ForeignOwner','loaded cited review implementation matches original selected native artifact');
 originalSources.set(application,{readAnswer,release,assertCurrent(){implementationCurrent();assertGenericNativeProfileArtifact(artifact);assertCurrent();}});
}
const bytes=value=>new TextEncoder().encode(canonical(value));
const identity=answer=>freeze({manifestId:answer.manifestId,payloadSha256:answer.payloadSha256,dependencies:capture(answer.dependencies),evidenceContext:capture(answer.evidenceContext)});
const same=(expected,actual)=>assert(canonical(expected)===canonical(actual),'StaleOwner','same complete released RAG context and answer required');
const expectedContext=answer=>({answer:answer.decision.answer,citationIds:answer.decision.citations,evidence:answer.evidenceContext});
function disclosureSelection(raw){
 const value=closed(raw,['retention','storage','read']);assert(value.retention==='source-bound-gated','UnsupportedCapability','retained source-derived reviews require source-bound gated reads');
 const storage=closed(value.storage,['policyId','action','sink']),read=closed(value.read,['policyId','action','sink']);
 for(const row of [storage,read])for(const key of ['policyId','action','sink'])text(row[key],key,256);
 assert(storage.action==='domain-review.store'&&read.action==='domain-review.read','UnsupportedCapability','finite domain-review storage/read actions');return freeze({retention:value.retention,storage,read});
}
/** Technical source config selects exact Mapping/Entries/release policies. The
 * host injects original resources and actors; serialized truth flags or supplied
 * source manifests cannot grant read, retention or execution permission. */
export async function createCitedDomainReview(options){
 const input=references(options,['rag','source','mapping','target','disclosure']),{rag}=input,original=originalSources.get(rag);assert(original,'ForeignOwner','original generated RAG application required');
 const source=references(input.source,['id','run','actor']),mapping=freeze(closed(input.mapping,['sourcePath','profilePath','selector','readSelector','acceptanceDirectory','owner'])),target=references(input.target,['composition','handle','runtime','entry','actor','readEntry','readActor']),disclosure=disclosureSelection(input.disclosure);
 u64(source.id);u64(source.run);for(const key of ['sourcePath','profilePath','acceptanceDirectory'])assert(typeof mapping[key]==='string'&&path.isAbsolute(mapping[key])&&path.normalize(mapping[key])===mapping[key],'InvalidContract','absolute original Mapping path');
 for(const key of ['selector','readSelector','owner'])text(mapping[key],key,256);for(const key of ['entry','readEntry'])text(target[key],key,256);assertGenericApplicationRuntime(target.runtime);
 const runtime=target.runtime,entry=runtime.entry(target.entry),owner=createGenericCompositionOwner();let handle,queries,disposed=false;
 try{
  handle=await owner.prepare({sourcePath:mapping.sourcePath,profilePath:mapping.profilePath});const review=owner.review(handle,mapping.owner);owner.accept(handle,{decision_id:'cited-review-'+randomUUID(),owner:mapping.owner,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(mapping.acceptanceDirectory,'cited-review-'+randomUUID()+'.json'));
  queries=createGenericQueryObservationOwner(target.composition,target.handle,runtime);
  const current=()=>{assert(!disposed,'StaleOwner','cited review binding closed');original.assertCurrent();owner.assertCurrent(handle);assertGenericApplicationRuntime(runtime);};
  const storage=()=>{current();const state=runtime.inspect();assert(typeof state.store_id==='string'&&typeof state.store_epoch_sha256==='string'&&typeof state.storage?.service==='string','ForeignOwner','actual original domain store identity');assert(disclosure.storage.sink==='local:'+state.storage.service&&disclosure.read.sink==='app:'+state.storage.service+'/reviews','ForeignOwner','selected release destinations must identify the actual original generated service');return {storeId:state.store_id,storeEpoch:state.store_epoch_sha256,service:state.storage.service};};
  const readAnswer=async()=>{current();const answer=await original.readAnswer(source);current();assert(answer?.decision?.released===true&&Array.isArray(answer.evidenceContext)&&answer.evidenceContext.length>0&&answer.evidenceContext.length<=8,'InvalidContract','actual released answer with original bounded source editions');return answer;};
  const project=(selector,input,answer)=>{const result=owner.evaluateReference(handle,{mapping:selector},bytes(input));assert(result.ok,'InvalidContract','actual checked source Mapping must project the original cited context');const context=JSON.parse(new TextDecoder('utf8',{fatal:true}).decode(result.wire));assert(canonical(context)===canonical(expectedContext(answer)),'InvalidContract','source Mapping must preserve the exact released answer, citations and every selected source edition');return context;};
  const release=(answer,selection,{recipient,payload,resourceId,attemptId})=>{current();const context=original.release.describeManifest(answer.manifest).context,exact={policyId:selection.policyId,attemptId,fence:0,resourceId,action:selection.action,sink:selection.sink,recipient,payload,expiresAt:Date.now()+30000,tenant:context.tenant,principal:context.principal},ticket=original.release.issueRelease({manifest:answer.manifest,...exact});current();return freeze(original.release.consumeRelease(ticket,exact));};
  const selected=owner.inspect(handle),mappingIdentity=freeze({selector:mapping.selector,readSelector:mapping.readSelector,profile:selected.profile});
  return Object.freeze({
   inspect(){current();return freeze({schema:'craft.cited-domain-review/v1',source:{id:source.id,run:source.run},mapping:mappingIdentity,target:{entry:target.entry,readEntry:target.readEntry},disclosure,authority_effect:'none',atomicity:'original-domain-store-only;source-currentness-checked-before-and-after'});},
   async invoke(raw){
    const {request,commandKey}=closed(raw,['request','commandKey']);current();text(commandKey,'original review command key',128);const input=capture(request,{maxBytes:65536,maxNodes:4096,maxDepth:32});assert(input&&typeof input==='object'&&!Array.isArray(input)&&!Object.hasOwn(input,'citedContext'),'InvalidContract','business review request excludes caller-supplied cited context');
    const answer=await readAnswer(),expected=identity(answer),context=project(mapping.selector,{answer:answer.decision,evidence:answer.evidenceContext},answer),payload=bytes({request:{...input,citedContext:context}});let prepared;
    try{
     current();prepared=runtime.prepareCommand(entry,payload,{client_key:commandKey});const authorization=await runtime.authorize(target.actor,prepared);current();if(!authorization.ok)return freeze({kind:'not-invoked',stage:'authorization',result:authorization});
     const transferred=await runtime.consume(authorization.value,prepared);current();if(!transferred.ok)return freeze({kind:'not-invoked',stage:'authorization-consumption',result:transferred});
     const command=runtime.inspectTransferredCommandIdentity(transferred.value),store=storage();same(expected,identity(await readAnswer()));
     // This exact processing destination authorizes retention in the selected
     // original store. It is distinct from RAG's human answer-release policy.
     const storageRelease=release(answer,disclosure.storage,{recipient:store.service,payload,resourceId:'domain-review:'+sha256(bytes({...store,entry:target.entry,input:command.canonical_input_sha256})),attemptId:'review-store:'+command.command_tuple_sha256});same(store,storage());
     const result=await runtime.executeCommand(transferred.value);
     try{same(expected,identity(await readAnswer()));same(store,storage());current();}
     catch(error){return freeze({kind:'result-withheld',observation:capture(result.observation??null),commandResultSha256:sha256(bytes(result)),storageReleaseSha256:sha256(bytes(storageRelease)),cause:{code:typeof error?.code==='string'?error.code:'SourceUnavailable'}});}
     // A write result is not itself a new disclosure grant. Only the composed
     // read below releases source-derived content to its actual Query principal.
     return freeze({kind:'completed',observation:capture(result.observation??null),commandResultSha256:sha256(bytes(result)),outcome:result.ok?{kind:result.outcome.kind,...(result.outcome.kind==='Returned'?{}:{code:result.outcome.code})}:{kind:'Fault',code:result.error.code},storageReleaseSha256:sha256(bytes(storageRelease))});
    }finally{if(prepared)runtime.disposePrepared(prepared);}
   },
   async read(raw){
    const {reviewId}=closed(raw,['reviewId']);u64(reviewId);const answer=await readAnswer(),expected=identity(answer);let lease;
    try{
     lease=await queries.read(target.readActor,target.readEntry,bytes({reviewId}),{deadline_ms:Date.now()+300000});const observed=queries.inspect(lease),store=storage();same(expected,identity(await readAnswer()));queries.assertCurrent(lease);
     if(observed.value!==null){
      const projected=project(mapping.readSelector,{review:observed.value},answer);
      // This finite adapter supports the typed saved-review shape used by these
      // examples: discussion, citations and evidence. The source Mapping cannot
      // replace those stored source-bearing fields with current-answer constants.
      // This is not an arbitrary-model taint or provenance proof.
      assert(['discussion','citations','evidence'].every(field=>Object.hasOwn(observed.value,field)),'InvalidContract','finite actual saved review source fields required');
      const retained={answer:observed.value.discussion,citationIds:observed.value.citations,evidence:observed.value.evidence};
      assert(canonical(projected)===canonical(retained),'InvalidContract','inverse Mapping must preserve the actual saved review source fields');
     }
     const envelope={kind:'read',result:observed.result,source:expected,mapping:mappingIdentity},payload=bytes(envelope),readRelease=release(answer,disclosure.read,{recipient:observed.principal.actor,payload,resourceId:'domain-review:'+sha256(bytes({...store,entry:target.readEntry,input:observed.input_sha256,content:observed.content_sha256})),attemptId:'review-read:'+randomUUID()});
     queries.assertCurrent(lease);same(store,storage());current();return freeze({...envelope,readReleaseSha256:sha256(bytes(readRelease))});
    }finally{if(lease)queries.retire(lease);}
   },
   close(){if(disposed)return;disposed=true;queries.close();owner.dispose(handle);},
  });
 }catch(error){queries?.close();if(handle)try{owner.dispose(handle);}catch{}throw error;}
}
