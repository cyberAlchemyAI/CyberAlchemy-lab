import {captureJson,dataDigest,reject,validateCoverageShape,type Origin,type CoverageData,type CoverageItem} from './contracts.js';
import {assertCheckedCompositionCurrent,assertProfileSelectionCurrent,type CheckedComposition} from './compose.js';

/** Complete independent source/intent/config/role denominator. No proof/admission.
 * Open questions: PE12 finite observed evidence and PE14 additional application roles. */
interface Obligation {id:string;origin:Origin;kind:CoverageItem['kind'];artifact_refs:readonly string[];reason:string}
function obligations(composition:CheckedComposition):readonly Obligation[] {
 assertCheckedCompositionCurrent(composition);const input=composition.selection.input,out:Obligation[]=[];
 const functionPaths=(source:string)=>composition.data.components.filter(c=>c.role==='domain-function'&&c.origins.some(o=>o.kind==='business'&&o.source===source)).flatMap(c=>c.artifact_paths);
 for(const selector of input.selectors){const artifacts=functionPaths(selector.source);if(!artifacts.length)reject('PROFILE_COVERAGE_SOURCE_UNSUPPORTED',selector.selector,'required source has no checked generated behavior owner');out.push({id:'business:'+selector.source+'#'+selector.selector,origin:{kind:'business',source:selector.source,selector:selector.selector,sha256:selector.sha256},kind:'business-obligation',artifact_refs:artifacts,reason:'Exact authored declaration/clause retained in registered checked source and compiled business artifact plan; native/runtime qualification remains separately gated.'});}
 for(const intent of input.project.public_intents){const paths=composition.data.components.filter(c=>c.role==='http-entry'&&c.origins.some(o=>o.selector==='public-intent:'+intent.id)).flatMap(c=>c.artifact_paths);const source=composition.data.components.find(c=>c.role==='domain-function'&&c.origins.some(o=>o.selector==='public-intent:'+intent.id))!.origins.find(o=>o.kind==='business')!;
  out.push({id:'intent:'+intent.id,origin:{...source,selector:'public-intent:'+intent.id},kind:'public-intent',artifact_refs:paths,reason:'Authored public intent reaches checked callable and uniquely owned planned entry.'});
  out.push({id:'access:'+intent.id,origin:{...source,selector:'access-policy:'+intent.id},kind:'access-policy',artifact_refs:paths,reason:'Explicit business access policy retained; authentication defaults cannot grant permissions.'});
  for(const outcome of intent.outcomes)out.push({id:'outcome:'+intent.id+'#'+outcome.code,origin:{...source,selector:'public-intent:'+intent.id+'#outcome:'+outcome.code},kind:'business-obligation',artifact_refs:paths,reason:'Authored business outcome class retained separately from selected HTTP serialization convention.'});
 }
 for(const wire of input.wire){const paths=functionPaths(wire.source);const sourceOrigin:Origin={kind:'integration-configuration',source:input.project.integration_configuration!,selector:'binding:'+wire.intent_id,sha256:dataDigest(wire)};
  out.push({id:'integration:'+wire.source+'#'+wire.intent_id,origin:sourceOrigin,kind:'integration-binding',artifact_refs:paths,reason:'Exact read-only schema/version/digest and missing/extra policy bound to authored external dependency.'});
  for(const [target,remote] of Object.entries(wire.correspondence))out.push({id:'integration-field:'+wire.source+'#'+wire.intent_id+'#'+target,origin:{...sourceOrigin,selector:sourceOrigin.selector+'#'+remote+'->'+target},kind:'integration-binding',artifact_refs:paths,reason:'Registered compatible field projection/rename; no computations or failure reinterpretation.'});
 }
 for(const component of composition.data.components)out.push({id:'role:'+component.id,origin:component.origins.find(o=>o.kind==='profile-rule')!,kind:'generated-role',artifact_refs:component.artifact_paths,reason:'Unique planned component owner, checked role contract and explicit dependency directions; rendering/native evidence is separate.'});
 for(const application of composition.applications){const paths=composition.data.components.find(c=>c.id==='application_operation_'+application.intent.id)!.artifact_paths,origin:Origin={kind:'business',source:application.intent.source,selector:application.intent.operation_ref,sha256:application.source_sha256};
  for(const node of application.graph.nodes)out.push({id:'application:'+application.intent.id+'#'+node.selector,origin:{...origin,selector:node.selector},kind:'business-obligation',artifact_refs:paths,reason:'Checked domain node retained in the owning registered application plan; no new proof/admission.'});
  out.push({id:'application-intent:'+application.intent.id,origin,kind:'public-intent',artifact_refs:paths,reason:'Explicit authored public Operation intent joined through exact checked Mapping request handler.'});
  out.push({id:'application-access:'+application.intent.id,origin:{...origin,selector:'access-policy:'+application.intent.id},kind:'access-policy',artifact_refs:paths,reason:'Explicit public access; neither provider selection nor profile defaults grant access.'});
  for(const mapping of application.binding.application_graph.runtime_bindings)out.push({id:'application-mapping:'+application.intent.id+'#'+mapping.binding_id,origin:{...origin,selector:mapping.mapping_ref},kind:'integration-binding',artifact_refs:paths,reason:'Actual checked application Mapping binding retained; Operation failures/ports remain explicit.'});
  const original=application.kind==='request-application'?composition.selection.business_applications?.applications.find(a=>a.model.id===application.lineage.application_id):undefined;
  if(application.kind==='request-application'&&!original)reject('PROFILE_COVERAGE_SOURCE_UNSUPPORTED',application.intent.id,'exact captured original application model required');
  if(original){
   for(const selector of original.selectors)out.push({id:'application-source:'+application.intent.id+'#'+selector.selector,origin:{kind:'business',source:original.model.source,selector:original.model.id+'#'+selector.selector,sha256:original.source_sha256},kind:selector.selector.startsWith('formal-claim:')?'formal-claim':'business-obligation',artifact_refs:paths,reason:'Exact authored declaration/clause linked through original/derived line map and registered compiler formation; formal claims remain unproved.'});
   const walk=(value:unknown,pointer:string):void=>{
    if(value!==null&&typeof value==='object'){const entries=Object.entries(value);if(entries.length){for(const [key,child]of entries)walk(child,pointer+'/'+key.replaceAll('~','~0').replaceAll('/','~1'));return;}}
    out.push({id:'application-meaning:'+application.intent.id+'#'+pointer,origin:{kind:'business',source:original.model.semantics,selector:original.model.id+'#'+pointer,sha256:original.semantics_sha256},kind:pointer.startsWith('/claim_meanings/')?'formal-claim':'business-obligation',artifact_refs:paths,reason:'Explicit captured business meaning/guard/result/invariant/guarantee field retained by checked normalization; acceptance is not proof.'});
   };walk(original.semantics,'');
   if(application.kind==='request-application')for(const parameter of Object.keys(application.authored_intent.mapping_arguments))out.push({id:'application-argument:'+application.intent.id+'#'+parameter,origin:{...origin,selector:'application-intent:'+application.intent.id+'#mapping-argument:'+parameter},kind:'integration-binding',artifact_refs:paths,reason:'Authored request body path reaches the checked Mapping parameter with exact type and source identity.'});
  }
  const source=original?.source??composition.selection.input.sources[application.intent.source];
  // Compatibility source is captured separately from the business-only function envelope.
  const snapshot=assertProfileSelectionCurrent(composition.selection),captured=source??snapshot.sources['application:'+application.intent.id+':source']?.text??'';
  for(const claim of captured.matchAll(/^formal-claim\s+([A-Za-z][A-Za-z0-9_]*)\s*:/gm))out.push({id:'application-claim:'+application.intent.id+'#'+claim[1],origin:{...origin,selector:'formal-claim:'+claim[1]},kind:'formal-claim',artifact_refs:paths,reason:'Authored compatibility-carrier formal claim retained as unproved residue; static generation is not proof/admission.'});
 }
 for(const claim of input.project.formal_claims)out.push({id:'claim:'+claim.id,origin:{kind:'business',source:claim.source,selector:claim.selector,sha256:dataDigest(claim)},kind:'formal-claim',artifact_refs:functionPaths(claim.source),reason:'Authored formal claim remains unproved residue; compilation and finite examples do not establish its truth.'});
 return Object.freeze(out);
}
export function createProfileCoverage(composition:CheckedComposition):CoverageData {
 const items=obligations(composition).map((o):CoverageItem=>({id:o.id,origin:o.origin,kind:o.kind,state:o.kind==='formal-claim'?'claim-residue':'retained',reason:o.reason,artifact_refs:o.artifact_refs,evidence_states:o.kind==='business-obligation'&&!o.id.startsWith('outcome:')?['linked','generated']:['linked']}));
 return validateCoverageShape({schema_version:'craft.profile-coverage/v1',source_sha256:composition.data.source_sha256,lock_sha256:composition.data.lock_sha256,items,authority_effect:'none'});
}
export function assertProfileCoverageComplete(composition:CheckedComposition,input:unknown):CoverageData {
 const expected=obligations(composition),coverage=validateCoverageShape(input);
 if(coverage.source_sha256!==composition.data.source_sha256||coverage.lock_sha256!==composition.data.lock_sha256)reject('PROFILE_COVERAGE_STALE','/','coverage must bind exact checked source/profile closure');
 const map=new Map(coverage.items.map(i=>[i.id,i]));if(map.size!==expected.length)reject('PROFILE_COVERAGE_DENOMINATOR','/','missing or invented required obligation');
 const owned=new Set(composition.data.components.flatMap(c=>c.artifact_paths));
 for(const obligation of expected){const item=map.get(obligation.id);if(!item||item.kind!==obligation.kind||dataDigest(item.origin)!==dataDigest(obligation.origin)||dataDigest(item.artifact_refs)!==dataDigest(obligation.artifact_refs))reject('PROFILE_COVERAGE_DENOMINATOR',obligation.id,'obligation origin/owner/artifact link differs');
  if(item.artifact_refs.some(ref=>!owned.has(ref)))reject('PROFILE_COVERAGE_ARTIFACT',item.id,'unowned artifact ref');if(item.kind==='formal-claim'?item.state!=='claim-residue':item.state!=='retained')reject('PROFILE_COVERAGE_REQUIRED_UNSUPPORTED',item.id,'required behavior cannot disappear or become claim residue');
  if(item.evidence_states.some(s=>!['linked','generated'].includes(s)))reject('PROFILE_COVERAGE_EVIDENCE',item.id,'stronger states require independent qualification receipts');
 }
 return coverage;
}

/** The generic source composer uses the same finite coverage vocabulary for its
 * selected native slots. This is a subgraph denominator, not full-app proof. */
export function createCapabilityProfileCoverage(input:Readonly<{source_sha256:string;profile_sha256:string;selection_sha256:string;kernel_sha256:string;bindings:readonly Readonly<{id:string;interface:string;source_path:string;artifact_refs:readonly string[];tools:readonly Readonly<{name:string;entry:string;artifact_refs:readonly string[]}>[]}>[]}>):CoverageData {
 const items:CoverageItem[]=[];
 const add=(id:string,selector:string,source:string,kind:CoverageItem['kind'],refs:readonly string[],reason:string)=>items.push({id,origin:{kind:'business',source,selector,sha256:input.source_sha256},kind,state:'retained',reason,artifact_refs:refs,evidence_states:['linked','generated']});
 for(const b of input.bindings){
  add('capability:'+b.id,b.interface,b.source_path,'integration-binding',b.artifact_refs,'Exact checked business/profile/kernel/resource selection and generated dispatch/codecs; runtime qualification is separate.');
  for(const t of b.tools)add('capability-tool:'+b.id+':'+t.name,t.entry,b.source_path,'generated-role',t.artifact_refs,'Exact original read-only Query Entry argument/result codecs and mediated tool binding.');
 }
 if(new Set(items.map(i=>i.id)).size!==items.length||input.bindings.some(b=>!b.artifact_refs.length))reject('PROFILE_COVERAGE_DENOMINATOR','capabilities','unique complete selected native slots required');
 return validateCoverageShape({schema_version:'craft.profile-coverage/v1',source_sha256:input.source_sha256,lock_sha256:dataDigest({profile:input.profile_sha256,selection:input.selection_sha256,kernel:input.kernel_sha256}),items,authority_effect:'none'});
}
