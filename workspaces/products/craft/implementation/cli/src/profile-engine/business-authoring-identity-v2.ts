import {captureJson,dataDigest,reject} from './contracts.js';
import {validateBusinessAuthoringContractV2} from './business-authoring-schema-v2.js';
import {BUSINESS_AUTHORING_CONTRACT_V2,type BusinessSpecDataV2,type DirectExecutableProjectionV2,type OptionalAssuranceProjectionV2} from './business-authoring-protocol-v2.js';
import {BUSINESS_EXECUTABLE_CANONICALIZATION_V2,BUSINESS_ASSURANCE_CANONICALIZATION_V2,BUSINESS_REVIEW_CANONICALIZATION_V2,type BusinessCaptureIdentityV2,type BusinessReviewSubjectV2} from './business-authoring-identity-protocol-v2.js';
/** Pure canonical projections only. Never manufactures a registered original handle.
 * Open Questions: docs/BUSINESS-IDENTITIES-V2.md. */
const compare=(a:string,b:string)=>a<b?-1:a>b?1:0;
const sorted=<T extends {readonly id:string}>(rows:readonly T[])=>[...rows].sort((a,b)=>compare(a.id,b.id));
const named=<T extends {readonly name:string}>(rows:readonly T[])=>[...rows].sort((a,b)=>compare(a.name,b.name));
const frozen=<T>(value:unknown):T=>captureJson(value) as unknown as T;
export function projectDirectExecutableV2(input:BusinessSpecDataV2):DirectExecutableProjectionV2 {
 const spec=validateBusinessAuthoringContractV2('spec',input);
 return frozen({schema_version:'craft.business-executable/v2-candidate',normalization_contract:BUSINESS_AUTHORING_CONTRACT_V2,
  identity:spec.identity,requirements:sorted(spec.requirements),entities:sorted(spec.entities).map(entity=>({...entity,fields:named(entity.fields)})),
  rules:sorted(spec.rules).map(({id,requirement_ref,input,condition})=>({id,requirement_ref,input,condition})),
  operations:sorted(spec.operations),entries:sorted(spec.entries),authority_effect:'none'});
}
export function projectOptionalAssuranceV2(input:BusinessSpecDataV2):OptionalAssuranceProjectionV2 {
 const spec=validateBusinessAuthoringContractV2('spec',input);
 return frozen({schema_version:'craft.business-assurance/v2-candidate',definitions:sorted(spec.definitions),
  claims:sorted(spec.claims).map(claim=>({...claim,sorts:named(claim.sorts),predicates:named(claim.predicates),constants:named(claim.constants),subject_refs:[...claim.subject_refs].sort(compare)})),authority_effect:'none'});
}
export function directExecutableIdentityV2(spec:BusinessSpecDataV2){return frozen<{algorithm:'sha256';canonicalization:typeof BUSINESS_EXECUTABLE_CANONICALIZATION_V2;sha256:string}>({algorithm:'sha256',canonicalization:BUSINESS_EXECUTABLE_CANONICALIZATION_V2,sha256:dataDigest(projectDirectExecutableV2(spec))});}
export function optionalAssuranceIdentityV2(spec:BusinessSpecDataV2){return frozen<{algorithm:'sha256';canonicalization:typeof BUSINESS_ASSURANCE_CANONICALIZATION_V2;sha256:string}>({algorithm:'sha256',canonicalization:BUSINESS_ASSURANCE_CANONICALIZATION_V2,sha256:dataDigest(projectOptionalAssuranceV2(spec))});}
export function captureBusinessIdentityV2(input:unknown):BusinessCaptureIdentityV2 {
 const manifest=validateBusinessAuthoringContractV2('capture',input);
 for(const [kind,rows] of [['profiles',manifest.profiles],['tools',manifest.tools]] as const)if(new Set(rows.map(row=>row.id)).size!==rows.length)reject('BUSINESS_V2_CAPTURE_DUPLICATE','/'+kind,'one exact artifact per identity');
 const body={...manifest,profiles:sorted(manifest.profiles),tools:sorted(manifest.tools)};
 return frozen({...body,capture_sha256:dataDigest(body)});
}
/** Subject is inspectable data. K01 independently reconstructs it and owns original review custody. */
export function projectBusinessReviewSubjectV2(input:BusinessSpecDataV2):BusinessReviewSubjectV2 {
 const spec=validateBusinessAuthoringContractV2('spec',input);
 return validateBusinessAuthoringContractV2('review',{schema_version:'craft.business-review/v2-candidate',normalization_contract:BUSINESS_AUTHORING_CONTRACT_V2,
  model_id:spec.identity.namespace,owner:spec.identity.owner,version:spec.identity.version,authored_rules:sorted(spec.rules),
  executable:projectDirectExecutableV2(spec),executable_sha256:directExecutableIdentityV2(spec).sha256,
  assurance:projectOptionalAssuranceV2(spec),assurance_sha256:optionalAssuranceIdentityV2(spec).sha256,authority_effect:'none'});
}
export function businessReviewIdentityV2(spec:BusinessSpecDataV2){return frozen<{algorithm:'sha256';canonicalization:typeof BUSINESS_REVIEW_CANONICALIZATION_V2;sha256:string}>({algorithm:'sha256',canonicalization:BUSINESS_REVIEW_CANONICALIZATION_V2,sha256:dataDigest(projectBusinessReviewSubjectV2(spec))});}
