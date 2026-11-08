import {createHash} from 'node:crypto';
import {lowerApplicationDomain} from './application-domain-lowering.js';
import {lowerApplicationRuleProjections} from './application-rule-projection.js';
import {json,digest} from './domainspec-profile.js';
import type {BusinessApplicationInput} from './business-application-protocol.js';
import {lowerDirectApplicationDomainV2,assertDirectBusinessFormationV2Current,type DirectBusinessFormationV2} from './application-domain-lowering.js';
import {projectDirectBusinessRuleV2,assertDirectRuleSourceProjectionV2Current,type DirectRuleSourceProjectionV2} from './application-rule-projection.js';
import type {LoweredDirectBusinessV2} from './business-authoring-stages-v2.js';
import {assertLoweredDirectBusinessV2Current} from './business-authoring-carriers.js';
import {businessCanonical,businessHash,businessReject,freezeBusinessData} from './business-authoring-model.js';

export interface DerivedDirectBusinessBindingsV2 {
 readonly kind:'derived-direct-business-bindings-v2';readonly lowered:LoweredDirectBusinessV2;
 readonly formation:DirectBusinessFormationV2;readonly rule:DirectRuleSourceProjectionV2;
 readonly selected_rule_refs:readonly [string];readonly bindings_sha256:string;readonly authority_effect:'none';
}
const directBindings=new WeakMap<object,{lowered:LoweredDirectBusinessV2;formation:DirectBusinessFormationV2;rule:DirectRuleSourceProjectionV2;fingerprint:string}>();
/** Derive technical source data without legacy formal resources or Core acceptance.
 * Open Questions: independent Core owner correspondence at U03/L02/G01. */
export function deriveDirectBusinessApplicationBindingsV2(lowered:LoweredDirectBusinessV2):DerivedDirectBusinessBindingsV2 {
 assertLoweredDirectBusinessV2Current(lowered);
 const formation=lowerDirectApplicationDomainV2(lowered),rule=projectDirectBusinessRuleV2(formation);
 const selected_rule_refs:readonly [string]=[rule.selector];
 const bindings_sha256=businessHash(businessCanonical({source:lowered.business.source.sha256,executable:lowered.business.executable_sha256,formation:formation.formation_sha256,rule:rule.projection_sha256,selected_rule_refs}));
 const result=Object.freeze({kind:'derived-direct-business-bindings-v2' as const,lowered,formation,rule,selected_rule_refs:Object.freeze(selected_rule_refs),bindings_sha256,authority_effect:'none' as const});
 directBindings.set(result,{lowered,formation,rule,fingerprint:bindings_sha256});assertDerivedDirectBusinessBindingsV2Current(result);return result;
}
export function assertDerivedDirectBusinessBindingsV2Current(value:DerivedDirectBusinessBindingsV2):void {
 const state=value&&typeof value==='object'?directBindings.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'original direct bindings required');
 assertLoweredDirectBusinessV2Current(state.lowered);assertDirectBusinessFormationV2Current(state.formation);assertDirectRuleSourceProjectionV2Current(state.rule);
 if(value.lowered!==state.lowered||value.formation!==state.formation||value.rule!==state.rule||value.selected_rule_refs.length!==1||value.selected_rule_refs[0]!==state.rule.selector||value.bindings_sha256!==state.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',state.lowered.business.source.path,1,1,'direct bindings changed');
}
// Open questions: operation/action/request/native joins BA03–BA18. No owner acceptance is synthesized.
interface Engine {assertBusinessInputV2Current(input:BusinessApplicationInput):void;dataDigest(input:unknown):string;captureJson(input:unknown):any}
export interface DerivedBusinessApplicationBindings {
 readonly application_id:string;readonly source:string;readonly original_source_sha256:string;readonly original_semantics_sha256:string;
 readonly source_sha256:string;readonly bindings:any;readonly sources:ReadonlyMap<string,Buffer>;readonly files:Readonly<Record<string,string>>;
 readonly formation:ReturnType<typeof lowerApplicationDomain>;readonly interpretation:any;readonly projection:ReturnType<typeof lowerApplicationRuleProjections>;
 readonly line_map:readonly Readonly<{derived_line:number;original_line:number|null;origin:'business'|'adapter'}>[];readonly derivation_sha256:string;
}
const current=new WeakMap<object,{input:BusinessApplicationInput;engine:Engine;digest:string}>();
const sha=(body:string|Buffer)=>createHash('sha256').update(body).digest('hex');
export function deriveBusinessApplicationBindings(input:BusinessApplicationInput,applicationId:string,engine:Engine):DerivedBusinessApplicationBindings {
 engine.assertBusinessInputV2Current(input);const application=input.applications.find(a=>a.model.id===applicationId);if(!application)throw Error('BUSINESS_APPLICATION_MODEL_UNKNOWN');
 const original=application.source.split('\n'),domain=original.findIndex(line=>/^domain\s/.test(line));if(domain<0)throw Error('BUSINESS_APPLICATION_DOMAIN_REQUIRED');
 const lines=[...original];lines.splice(domain+1,0,'profile application-v1');const source=lines.join('\n'),sourceHash=sha(source);
 const line_map=lines.map((_line,index)=>({derived_line:index+1,original_line:index===domain+1?null:index>domain+1?index:index+1,origin:index===domain+1?'adapter' as const:'business' as const}));
 const files:Record<string,string>={},prefix='business/'+application.model.id+'/',sources=new Map<string,Buffer>();
 const write=(name:string,value:unknown,raw=false)=>{const relative=prefix+name,body=raw?String(value):json(value);if(Object.hasOwn(files,relative))throw Error('BUSINESS_APPLICATION_RESOURCE_COLLISION');files[relative]=body;const bytes=Buffer.from(body);sources.set(relative,bytes);return {path:relative,sha256:sha(bytes),size_bytes:bytes.length,current:true};};
 const runtime=input.runtime.data.application_runtime;
 const formalProfile=write('formal-profile.json',input.runtime.assets[runtime.formal_profile_asset]!.text!,true);
 const algorithm=write('identity-algorithm.json',input.runtime.assets[runtime.identity_algorithm_asset]!.text!,true);
 const formal_claims:Record<string,unknown>={};
 for(const [name,claim]of Object.entries(application.semantics.claim_meanings)){
  // Decision and definition bodies are copied from exact explicit accepted business input.
  const acceptance=write(name+'/owner-acceptance.json',claim.owner_acceptance);
  const meaning=write(name+'/business-meaning.json',{...claim.business_meaning,acceptance:{status:claim.owner_acceptance.outcome,owner_ref:claim.owner_acceptance.owner,acceptance_ref:acceptance.path,acceptance_digest:acceptance.sha256}});
  const definitions=write(name+'/definitions.json',{definitions:claim.definitions});
  const selected=claim.definition_refs.map(id=>{const index=claim.definitions.findIndex(d=>d.definition_id===id);if(index<0)throw Error('BUSINESS_APPLICATION_DEFINITION_UNKNOWN');return {id,index,body:claim.definitions[index]!};}).sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
  const definitionBinding=write(name+'/definition-binding.json',{schema_version:'domainspec-v2.formal-claim-definition-binding/v1-candidate',binding_id:application.model.id+':'+name,claim_identity:{claim_id:claim.claim_id,claim_version:claim.version},definition_authority_ref:definitions,definition_nodes:selected.map(d=>({definition_id:d.id,definition_pointer:'#/definitions/'+d.index,status:d.body.status,definition_digest:engine.dataDigest(d.body)})),relations:selected.map(d=>({relation_id:application.model.id+':'+name+':'+d.id,relation_type:'uses_definition',source_claim_id:claim.claim_id,target_definition_id:d.id,definition_pointer:'#/definitions/'+d.index,binding_effect:'semantic-dependency',inference:'explicit'})),definition_closure:{definition_ids:selected.map(d=>d.id),canonicalization:'domainspec-json-keysort-v1',digest_algorithm:'sha256',digest:engine.dataDigest(selected.map(d=>d.body))},resolution_policy:{edge_source:'explicit-author-declaration',name_inference:'forbidden',missing_definition:'block',transitive_dependencies:'required',definition_body_authority:'definition_authority_ref'},authority_effect:'none',claim_ceiling:claim.business_meaning.claim_ceiling});
  formal_claims[name]={claim_id:claim.claim_id,claim_version:claim.version,supersedes:claim.supersedes,business_meaning_ref:meaning,business_acceptance_ref:acceptance,definition_binding_ref:definitionBinding,formal_language_profile_ref:formalProfile,identity_algorithm_ref:algorithm};
 }
 const bindings=engine.captureJson({schema_version:'alchlang.application-bindings/v1',source_sha256:sourceHash,owner:application.semantics.owner,formal:{schema_version:'alchlang.formal-claim-bindings/v1',source_sha256:sourceHash,owner:application.semantics.owner,formal_claims},declarations:application.semantics.declarations});
 const formation=lowerApplicationDomain(source,bindings,sources);
 const ruleNames=formation.model.rules.map(r=>r.id).sort();if(JSON.stringify(Object.keys(application.semantics.rule_meanings).sort())!==JSON.stringify(ruleNames))throw Error('BUSINESS_APPLICATION_RULE_COVERAGE');
 const rules:Record<string,unknown>={};for(const rule of formation.model.rules){const claim=formation.model.formal_claims.find(c=>c.id===rule.claim_ref)!;const trace=formation.trace.declarations.find(t=>t.source_id===claim.id)!;
  rules[rule.id]={claim_identity_inputs_digest:trace.identity_inputs_digest,context_id:application.model.id+':'+rule.id,ceiling:claim.ceiling,...application.semantics.rule_meanings[rule.id]};
 }
 const interpretation=engine.captureJson({schema_version:'alchlang.ground-rule-interpretation/v1-candidate',formation_sha256:digest(json(formation)),rules});
 const projection=lowerApplicationRuleProjections(source,bindings,sources,interpretation);
 const stable={application_id:application.model.id,source,original_source_sha256:application.source_sha256,original_semantics_sha256:application.semantics_sha256,source_sha256:sourceHash,bindings,files,formation,interpretation,projection,line_map};
 const result=Object.freeze({...stable,sources:new Map([...sources].map(([key,body])=>[key,Buffer.from(body)])),files:Object.freeze(files),line_map:Object.freeze(line_map),derivation_sha256:engine.dataDigest(stable)});current.set(result,{input,engine,digest:result.derivation_sha256});assertDerivedBusinessApplicationCurrent(result);return result;
}
export function assertDerivedBusinessApplicationCurrent(value:DerivedBusinessApplicationBindings):void {
 const state=current.get(value);if(!state)throw Error('BUSINESS_APPLICATION_DERIVATION_UNREGISTERED');state.engine.assertBusinessInputV2Current(state.input);
 const {sources,derivation_sha256:_digest,...rest}=value;
 if(state.engine.dataDigest(rest)!==state.digest)throw Error('BUSINESS_APPLICATION_DERIVATION_CHANGED');
 for(const [name,body]of Object.entries(value.files)){const bytes=sources.get(name);if(!bytes||sha(bytes)!==sha(body))throw Error('BUSINESS_APPLICATION_DERIVATION_RESOURCE_CHANGED');}
 if(sources.size!==Object.keys(value.files).length)throw Error('BUSINESS_APPLICATION_DERIVATION_RESOURCE_CHANGED');
}
