/** Actual captured source -> inert HTTP descriptor; no descriptor grants custody.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail,coreSourceChildren as children,coreSourceDescendants as descendants,coreSourceTokens as tokens,coreSourceText as text} from '../commerce/commerce-core-syntax.js';
import {createCoreValueTypes} from '../commerce/commerce-core-types.js';
import {createCoreContextCatalog} from '../commerce/commerce-core-context.js';
import type {CoreCommerceSourceInspection} from '../commerce/commerce-core-source-owner.js';
import type {ValueTypeV1} from '../commerce/commerce-data-v1.js';
import type {GenericHttpApplicationV1,GenericHttpEntryV1} from './http-data-v1.js';
import {createGenericTransactionSourceContract,createGenericExternalWriteTransactionSourceContract,createGenericEventTransactionSourceContract} from './transaction-source.js';
import {resolveGenericHttpProfile} from './http-profile.js';
export const GENERIC_HTTP_REVISION='strict-http-framing-same-account-response/v1-candidate' as const;
export function createGenericHttpSourceContract(capture:CoreCommerceSourceInspection){
 const base=capture.capture_mode==='event-handoff-entry'?createGenericEventTransactionSourceContract(capture):capture.capture_mode==='external-write-entry'?createGenericExternalWriteTransactionSourceContract(capture):createGenericTransactionSourceContract(capture),types=createCoreValueTypes(capture.reconstruction),root=[...types.declarations.values()].find(d=>d.interface_kind==='application-composition');if(!root)fail('MissingMapping',{path:capture.application_path,start:0,end:0},'original application root required');
 const catalog=createCoreContextCatalog(types,capture.files.filter(f=>f.path.endsWith('.json'))),http=catalog.asset(root,['http-bindings']),profileAsset=catalog.asset(root,['parameters']);
 if(!http||!profileAsset)fail('MissingMapping',root.syntax,'actual HTTP and base profile assets required');
 const full=(head:string)=>{const clauses=children(root.syntax,'interface-clause').filter(c=>tokens(c).filter(t=>!t.layout)[0]?.token===head);if(clauses.length!==1)fail('InvalidContract',root.syntax,'one exact profile reference required');const ref=descendants(clauses[0]!,'reference')[0];if(!ref||text(ref).includes('#'))fail('InvalidContract',root.syntax,'full HTTP/base profile files required');};full('http-bindings');full('parameters');
 const file=capture.files.find(f=>f.path===http.path);if(!file)fail('UnknownReference',root.syntax,'actual captured HTTP profile absent');const profile=resolveGenericHttpProfile(file.text,file.path);if(profile.limits.request_bytes!==base.contract.limits.max_input_bytes)fail('InvalidContract',root.syntax,'HTTP request_bytes must equal the original computation max_input_bytes');
 if(new Set(profile.routes.map(route=>route.service)).size!==1)fail('UnsupportedCapability',root.syntax,'one service per generated HTTP application required');
 if(http.path!=='contracts/http-profile.json'||profileAsset.path!=='contracts/selected-profile.json'||!['contracts/selected-profile.json','selected-profile.json'].includes(profile.application_profile)||profileAsset.value!==profileAsset.doc||http.value!==http.doc)fail('InvalidContract',root.syntax,'fixed original physical profile association required');
 const scalar=(t:ValueTypeV1):boolean=>{
  if(t.kind==='scalar')return t.name==='UInt64'||t.name==='Bool';if(t.kind==='string')return true;
  if(t.kind==='refinement'){const r=base.contract.values.refinements.find(r=>r.name===t.name);return !!r&&(r.carrier.kind==='scalar'&&(r.carrier.name==='Bool'||r.carrier.name==='UInt64')||r.carrier.kind==='string');}
  if(t.kind==='enum'){const e=base.contract.values.enums.find(e=>e.name===t.name);return !!e&&e.variants.every(v=>Object.keys(v.fields).length===0);}return false;
 };
 const entries:GenericHttpEntryV1[]=profile.routes.map((route,index)=>{
  const d=types.resolve(root.module,route.entry,root.syntax),md=types.resolve(root.module,route.response_mapping,root.syntax),entry=base.contract.entries.find(e=>e.entry===d.id),mapping=base.contract.functions.find(f=>f.name===md.id&&f.kind==='Mapping');
  if(!entry||d.surface!=='Entry'||!mapping||md.surface!=='Mapping')fail('UnknownReference',root.syntax,'actual Entry and Mapping required');if(entry.service!==route.service)fail('InvalidContract',d.syntax,'HTTP route service differs from Entry');
  if(entry.access.principal_kind==='service')fail('UnsupportedCapability',d.syntax,'service Event receivers require their original relay credential, not a request-response HTTP route');
  const isCommand=entry.schema_version==='craft.generic-transaction-entry/v1-candidate'||entry.schema_version==='craft.generic-operator-entry/v1-candidate';if(route.method==='POST'?!isCommand:isCommand||!(base.contract.queries.some(q=>q.query===entry.target)||base.contract.readonly_operations.some(o=>o.operation===entry.target)))fail('UnsupportedCapability',d.syntax,'HTTP method requires its actual read/stateful Entry');
  if(mapping.parameters.length!==1||dataDigest(mapping.parameters[0]!.type)!==dataDigest(entry.result))fail('TypeMismatch',md.syntax,'response Mapping takes exactly the original Entry result');
  if(route.method==='GET'){
   const names=[...route.path.split('/').filter(s=>s.startsWith('{')).map(s=>s.slice(1,-1)),...route.query.map(q=>q.parameter)];if(names.length!==entry.parameters.length||entry.parameters.some(p=>!names.includes(p.name)))fail('TypeMismatch',d.syntax,'GET carriers must cover each source parameter exactly once');if(entry.parameters.some(p=>!scalar(p.type)))fail('TypeMismatch',d.syntax,'GET requires checked bounded scalar or nullary Enum input');
  }
  // The original all-functions/value closure is already bound by the base digest.
  // This additionally binds the exact selected Mapping; no caller AST is admitted.
  return {schema_version:'craft.generic-http-entry/v1-candidate',route:{...route,entry:d.id,response_mapping:md.id},entry_contract_sha256:dataDigest(entry),response_mapping_sha256:dataDigest({mapping,functions:base.contract.functions,values:base.contract.values,limits:base.contract.limits}),parameters:entry.parameters,result:entry.result,response_result:mapping.result,profile_source:{path:file.path,sha256:file.sha256,pointer:'/routes/'+index},entry_source:{path:d.syntax.path,start:d.syntax.start,end:d.syntax.end},mapping_source:{path:md.syntax.path,start:md.syntax.start,end:md.syntax.end},revision:GENERIC_HTTP_REVISION};
 });
 const semantic={revision:GENERIC_HTTP_REVISION,base_application_sha256:dataDigest(base.contract),base_profile_sha256:base.derivation.profile_sha256,http_profile_sha256:dataDigest(profile),profile,entries:entries.map(({profile_source,entry_source,mapping_source,...entry})=>entry)},transport_semantics_sha256=dataDigest(semantic);
 const contract:GenericHttpApplicationV1={schema_version:'craft.generic-http-application/v1-candidate',base_application_sha256:semantic.base_application_sha256,base_profile_sha256:semantic.base_profile_sha256,http_profile_sha256:semantic.http_profile_sha256,profile,entries,transport_semantics_sha256};
 return coreFreeze({base,contract,transport_semantics_sha256,executable_sha256:dataDigest({revision:GENERIC_HTTP_REVISION,base:base.derivation.executable_semantics_sha256,transport:transport_semantics_sha256})});
}
