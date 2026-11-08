/** Closed contract admission only. Runtime/source authority requires original checked owners.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import {captureJson,dataDigest,reject,validateShape} from '../profile-engine/contracts.js';
import {validateIntegrationKernelV2} from '../system-integration/kernel-v2.js';
import type * as C from './capability-data-v1.js';
import {GENERIC_NATIVE_VECTOR_TYPE_V1} from './capability-data-v1.js';

export function validateGenericCapabilitySelection(input:unknown,kernelInput:unknown):C.GenericCapabilitySelectionV1 {
 const value=validateShape<C.GenericCapabilitySelectionV1>('capability-selection',input);
 const kernel=validateIntegrationKernelV2(captureJson(kernelInput));
 if(dataDigest(kernelInput)!==value.kernel.sha256)reject('CAPABILITY_KERNEL_DIGEST','/kernel/sha256','exact canonical kernel digest required');
 const unique=(values:readonly string[],p:string)=>{if(new Set(values).size!==values.length)reject('CAPABILITY_AMBIGUOUS',p,'one exact identity required');};
 unique(value.bindings.map(b=>b.id),'/bindings');unique(value.bindings.map(b=>b.interface),'/bindings/interface');unique(value.realizations.map(r=>r.id),'/realizations');
 const used=new Set<string>();
 value.bindings.forEach((binding,i)=>{
  const at='/bindings/'+i,realization=value.realizations.find(r=>r.id===binding.realization_ref);
  if(!realization)reject('CAPABILITY_MISSING',at+'/realization_ref',binding.realization_ref);
  used.add(realization.id);
  if(!/^(?:@[a-z0-9][a-z0-9._-]*\/)?[a-z0-9][a-z0-9._-]*$/.test(realization.implementation.package))reject('CAPABILITY_PACKAGE',at+'/realization_ref','exact package identity, not a path or executable expression, required');
  const exported=realization.implementation.export;
  if(exported!=='.'&&(!exported.startsWith('./')||exported.slice(2).split('/').some(s=>!s||s==='.'||s==='..'||!/^[A-Za-z0-9_.-]+$/.test(s))))reject('CAPABILITY_EXPORT',at+'/realization_ref','owned package export subpath required');
  if(binding.contract.kind!==realization.contract||!realization.operations.includes(binding.contract.operation))reject('CAPABILITY_CONTRACT',at+'/contract','selected realization cannot honor semantic operation');
  const familyOperations:Record<string,readonly string[]>={'inference/v1':['text.generate','text.structured','vector.embed'],'agent-run/v1':['agent.run'],'document/v1':['document.parse'],'search/v1':['search.query']};
  if(realization.operations.some(op=>!familyOperations[realization.contract]!.includes(op)))reject('CAPABILITY_CONTRACT',at+'/realization_ref','mixed inference/harness/business operation families are unsupported');
  const integration=kernel.integration_bindings.find(b=>b.binding_id===realization.integration_binding_ref);
  if(!integration)reject('CAPABILITY_MISSING',at+'/realization_ref','existing integration binding required');
  if(integration.logical_boundary_ref!==binding.interface)reject('CAPABILITY_LINEAGE',at+'/interface','business Interface and integration boundary differ');
  if(integration.contract_ref!==binding.contract.kind)reject('CAPABILITY_CONTRACT',at,'integration binding semantic contract differs');
  const resource=kernel.provider_realizations.find(r=>r.realization_id===integration.provider_realization_ref)!;
  const provider=kernel.provider_profiles.find(p=>p.profile_id===resource.provider_profile_ref)!;
  if(resource.adapter_ref!==realization.id)reject('CAPABILITY_LINEAGE',at+'/realization_ref','native descriptor differs from selected resource adapter');
  if(!provider.capability_set.includes(binding.contract.kind))reject('CAPABILITY_CONTRACT',at,'provider profile semantic family mismatch');
  const required:string[]=[...binding.contract.required_capabilities];
  const intrinsic:Record<string,string>={'text.generate':'text-output','text.structured':'structured-output','vector.embed':'embeddings','agent.run':'local-inspect','document.parse':'document-parse','search.query':'bounded-search'};
  required.push(intrinsic[binding.contract.operation]!);
  if(binding.contract.kind==='agent-run/v1'&&binding.contract.tools.length)required.push('readonly-tools');
  for(const cap of required)if(!realization.capabilities.includes(cap as typeof realization.capabilities[number])||!provider.capability_set.includes(cap))reject('CAPABILITY_UNSUPPORTED',at+'/contract/required_capabilities','missing '+cap);
  if(integration.direction==='inbound')reject('CAPABILITY_DIRECTION',at,'outbound or bidirectional integration required');
  const slot=realization.lifecycle.credential_slot_ref;
  if(slot!==null&&!provider.secret_slot_refs.includes(slot))reject('CAPABILITY_CREDENTIAL',at,'credential slot not declared by original provider profile');
  if(realization.mode==='provider'&&(!slot||!resource.credential_binding_ref))reject('CAPABILITY_CREDENTIAL',at,'operator credential binding required for provider mode');
  for(const [key,limit] of Object.entries(binding.bounds))if(limit>realization.bounds[key as keyof typeof binding.bounds])reject('CAPABILITY_BOUNDS',at+'/bounds/'+key,'required bound exceeds selected realization');
  if(binding.contract.kind==='inference/v1'){
   if((binding.contract.operation==='vector.embed')!==(binding.contract.embedding!==null))reject('CAPABILITY_EMBEDDING',at+'/contract/embedding','only embedding operations carry dimension/space identity');
   if((binding.contract.operation==='vector.embed')!==(binding.contract.result_type===GENERIC_NATIVE_VECTOR_TYPE_V1))reject('CAPABILITY_EMBEDDING',at+'/contract/result_type','embedding results require the declared profile-native finite-vector type; business results keep their declared ValueObject');
   if(binding.bounds.max_tool_calls!==0||binding.bounds.max_model_attempts!==1)reject('CAPABILITY_LOOP',at+'/bounds','direct inference has one logical model attempt and no tools');
   const subset=binding.contract.operation==='vector.embed'?'finite-vector/v1':'checked-business-values/v1';
   if(realization.schema.subset!==subset)reject('CAPABILITY_SCHEMA',at,'schema subset differs from semantic operation');
  }
  if(binding.contract.kind==='agent-run/v1'){
   unique(binding.contract.tools.map(t=>t.name),at+'/contract/tools');
   if(binding.bounds.max_model_attempts<1)reject('CAPABILITY_BOUNDS',at+'/bounds','bounded harness model attempts required');
  }
  if(binding.contract.kind==='search/v1'){
   const s=binding.contract.search;
   if(s.top_k>s.max_candidates||s.max_candidates>binding.bounds.max_items)reject('CAPABILITY_SEARCH',at+'/contract/search','bounded candidate/top-k relation required');
   if((s.technique!=='keyword')!==(s.embedding_space!==null))reject('CAPABILITY_SEARCH',at+'/contract/search','vector/hybrid needs exact embedding-space identity');
  }
  // Exact destination identity is data, never a route for embedding credentials.
  try{const u=new URL(realization.target.destination);if(u.username||u.password)reject('CAPABILITY_CREDENTIAL',at,'credentials cannot be embedded in target');}catch(e){if(e instanceof Error&&e.name==='ProfileRejected')throw e;}
 });
 if(value.realizations.some(r=>!used.has(r.id)))reject('CAPABILITY_UNUSED','/realizations','unselected realization must not introduce a dependency');
 return value;
}

export function validateGenericContextManifest(input:unknown):C.GenericSourceContextManifestV1 {
 const v=validateShape<C.GenericSourceContextManifestV1>('context-manifest',input);
 if(new Set(v.dependencies.map(d=>d.source)).size!==v.dependencies.length)reject('CAPABILITY_AMBIGUOUS','/dependencies','one revision per source required');
 return v;
}
export const validateGenericReleaseTicketData=(input:unknown)=>validateShape<C.GenericSourceReleaseTicketDataV1>('release-ticket',input);
export const validateGenericTrustedSearchContextData=(input:unknown)=>validateShape<C.GenericTrustedSearchContextDataV1>('trusted-search-context',input);
export function validateGenericContinuation(input:unknown):C.GenericContinuationDecisionV1 {
 const v=validateShape<C.GenericContinuationDecisionV1>('continuation',input);
 if(v.kind==='retry'&&v.attempt>v.maximum)reject('CAPABILITY_RETRY','/attempt','bounded attempts exhausted');
 return v;
}
