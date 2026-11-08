/** Generated application diagnostics: constant presentation data, no recovery authority.
 * Open Questions: docs/error-mapping source consumer contract and deferred migrations. */
import {randomBytes} from 'node:crypto';
import {assert,capture,canonical,freeze,text,sha256} from '../shared.mjs';
const statuses=Object.freeze({Conflict:409,Forbidden:403,InvalidInput:422});
export function validateApplicationErrorPresentation(raw){
 const table=capture(raw);
 if(table?.schema_version==='craft.error-presentation-set/v1'){
  assert(Object.keys(table).sort().join(',')==='presentation_version,schema_version,tables','InvalidContract','closed presentation set');
  assert(Array.isArray(table.tables)&&table.tables.length===2,'InvalidContract','two producer-bound presentation tables');
  const tables=table.tables.map(t=>{assert(t?.schema_version==='craft.error-presentation-table/v1','InvalidContract','nested presentation sets forbidden');return validateApplicationErrorPresentation(t);});
  assert(new Set(tables.map(t=>t.producer)).size===2&&tables.reduce((n,t)=>n+t.rows.length,0)<=64,'InvalidContract','distinct finite producer tables');
  assert(table.presentation_version===sha256(canonical({schema_version:table.schema_version,tables})),'InvalidContract','aggregate presentation identity');
  return freeze({...table,tables});
 }
 assert(table&&table.schema_version==='craft.error-presentation-table/v1','InvalidContract','checked error table version');
 for(const k of ['producer','reason_type'])assert(typeof table[k]==='string'&&/^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$/.test(table[k]),'InvalidContract','qualified source error identity');
 assert(typeof table.presentation_version==='string'&&/^[a-f0-9]{64}$/.test(table.presentation_version),'InvalidContract','captured presentation version');
 assert(Array.isArray(table.rows)&&table.rows.length>0&&table.rows.length<=64,'ResourceLimit','finite error table');const seen=new Set();
 for(const row of table.rows){assert(row&&Object.keys(row).sort().join(',')==='category,httpStatus,internalCode,message,publicCode','InvalidContract','closed source-selected error row');for(const k of ['internalCode','publicCode']){text(row[k],k,128);assert(/^[A-Za-z_][A-Za-z0-9_-]*$/.test(row[k]),'InvalidContract','finite error code');}text(row.message,'public message',512);assert([...row.message].length<=256&&statuses[row.category]===row.httpStatus&&!seen.has(row.internalCode),'InvalidContract','unique category/status-bound error row');seen.add(row.internalCode);}
 return freeze(table);
}
/** Exact member identities include their source pins and generated kernel identity.
 * This composition adds no diagnostic authority and never aliases producers. */
export function composeApplicationErrorPresentations(business,technical){
 const tables=[business,technical].map(validateApplicationErrorPresentation);
 assert(tables.every(t=>t.schema_version==='craft.error-presentation-table/v1'),'InvalidContract','original leaf tables required');
 const schema_version='craft.error-presentation-set/v1';
 return validateApplicationErrorPresentation({schema_version,tables,presentation_version:sha256(canonical({schema_version,tables}))});
}
const issuedDiagnostics=new WeakSet();
export const isApplicationDiagnostic=value=>!!value&&issuedDiagnostics.has(value);
export const newDiagnosticCorrelation=()=>randomBytes(16).toString('hex');
export function applicationDiagnostic({profile,kind,producer,code,providerKind=null,sourceIdentity=null}){
 assert(profile.errorPresentation,'UnsupportedCapability','selected error presentation required');
 assert(['Rejected','Failed','Fault','ProviderNoEffect','ProviderUnknown'].includes(kind),'InvalidContract','original outcome kind');
 text(producer,'actual outcome producer',256);text(code,'actual original code',128);
 const diagnostic=freeze({kind,producer,code,presentationVersion:profile.errorPresentation.presentation_version,correlationId:newDiagnosticCorrelation(),providerKind,sourceIdentity});issuedDiagnostics.add(diagnostic);return diagnostic;
}
/** Normalize only host-native stage output; a copied/user-shaped diagnostic
 * never inherits the original invocation's provenance. */
export function prepareApplicationDiagnosticOutput(profile,value){
 const diagnostic=isApplicationDiagnostic(value.diagnostic)?value.diagnostic:!value.accepted?applicationDiagnostic({profile,kind:'Fault',producer:profile.module+'.NativeBoundary',code:'operation-unavailable'}):null;
 return {...value,diagnostic};
}
export function publicApplicationStatusResult(profile,result){
 if(profile.errorPresentation&&result.ok&&result.outcome.kind==='Returned'&&result.outcome.value?.error?.correlationId==='0000000000000000')return freeze({...result,outcome:{...result.outcome,value:{...result.outcome.value,error:{...result.outcome.value.error,correlationId:newDiagnosticCorrelation()}}}});
 return result;
}
/** Called only by the provider stage after the original dispatcher returned its
 * validated observation. The function does not change/return retry instructions. */
export function diagnosticForProviderObservation({profile,observation,producer,sourceIdentity}){
 if(!profile.errorPresentation||observation.kind==='confirmed')return null;
 assert(observation&&['no-effect','unknown'].includes(observation.kind),'InvalidContract','original validated provider observation kind');
 const reason=typeof observation.reason==='string'&&/^[A-Za-z0-9_-]{1,128}$/.test(observation.reason)?observation.reason:'provider-unavailable';
 return applicationDiagnostic({profile,kind:observation.kind==='unknown'?'ProviderUnknown':'ProviderNoEffect',producer,code:reason,providerKind:observation.kind,sourceIdentity});
}
/** Generate the projection in ordinary Alch. The original Core compiles it;
 * there is no parallel JS business predicate interpreter. */
export function applicationErrorProjectionSource(table,{providerBindings=[]}={}){
 table=validateApplicationErrorPresentation(table);const quote=JSON.stringify,version=quote(table.presentation_version),rows=(table.schema_version==='craft.error-presentation-set/v1'?table.tables:[table]).flatMap(member=>member.rows.map(row=>({...row,producer:member.producer})));
 const record=`value-object ProfileErrorCode:
  carrier String
  utf8-bytes 1..128
  unicode-scalars 1..128

value-object ProfileErrorMessage:
  carrier String
  utf8-bytes 1..512
  unicode-scalars 1..256

value-object ProfileErrorToken:
  carrier String
  utf8-bytes 16..64
  unicode-scalars 16..64

value-object ProfileErrorVersion:
  carrier String
  utf8-bytes 64..64
  unicode-scalars 64..64
  pattern "^[a-f0-9]{64}$"

value-object ProfileDiagnosticProducer:
  carrier String
  utf8-bytes 1..256
  unicode-scalars 1..256

value-object ProfileDiagnosticKind:
  carrier String
  utf8-bytes 1..32
  unicode-scalars 1..32

value-object ProfileDiagnostic:
  kind ProfileDiagnosticKind
  producer ProfileDiagnosticProducer
  code ProfileErrorCode
  presentationVersion ProfileErrorVersion
  correlationId ProfileErrorToken
  providerKind optional<ProfileDiagnosticKind>
  sourceIdentity optional<ProfileErrorVersion>

value-object ProfilePublicError:
  code ProfileErrorCode
  message ProfileErrorMessage
  category ProfileDiagnosticKind
  correlationId ProfileErrorToken
  presentationVersion ProfileErrorVersion

`;
 let source=record;
 for(const [index,row]of rows.entries())source+=`calculation ProfileError${index}:\n  pure\n  input result ProfileStageOutput\n  result optional<ProfilePublicError>\n  expression some(ProfilePublicError(code=${quote(row.publicCode)},message=${quote(row.message)},category=${quote(row.category)},correlationId=require-some(result.diagnostic).correlationId,presentationVersion=${version}))\n\n`;
 source+=`calculation ProfileNoPublicError:\n  pure\n  result optional<ProfilePublicError>\n  expression none\n\ncalculation ProfileUnknownProviderError:\n  pure\n  input result ProfileStageOutput\n  result optional<ProfilePublicError>\n  expression some(ProfilePublicError(code="reconciliation-required",message="The provider outcome requires reconciliation.",category="Unavailable",correlationId=require-some(result.diagnostic).correlationId,presentationVersion=${version}))\n\ncalculation ProfileUnavailableProviderError:\n  pure\n  input result ProfileStageOutput\n  result optional<ProfilePublicError>\n  expression some(ProfilePublicError(code="provider-unavailable",message="The external service could not complete this operation.",category="Unavailable",correlationId=require-some(result.diagnostic).correlationId,presentationVersion=${version}))\n\ncalculation ProfileGenericPublicError:\n  pure\n  result optional<ProfilePublicError>\n  expression some(ProfilePublicError(code="operation-unavailable",message="The operation could not be completed.",category="Internal",correlationId="0000000000000000",presentationVersion=${version}))\n\ncalculation ProfileGenericDiagnosticError:\n  pure\n  input result ProfileStageOutput\n  result optional<ProfilePublicError>\n  expression some(ProfilePublicError(code="operation-unavailable",message="The operation could not be completed.",category="Internal",correlationId=require-some(result.diagnostic).correlationId,presentationVersion=${version}))\n\npolicy ProfileSelectPublicError:\n  input result ProfileStageOutput\n  result optional<ProfilePublicError>\n  ordered-cases:\n    accepted when result.accepted -> ProfileNoPublicError()\n`;
 const providerKnown=providerBindings.map(binding=>`(require-some(result.diagnostic).producer == ${quote(binding.capability_binding)} and require-some(result.diagnostic).sourceIdentity == some(${quote(binding.capability_sha256)}))`).join(' or ')||'false';
 const known=`present(result.diagnostic) and require-some(result.diagnostic).presentationVersion == ${version}`;
 for(const [index,row]of rows.entries())source+=`    error${index} when ${known} and require-some(result.diagnostic).kind == "Rejected" and require-some(result.diagnostic).producer == ${quote(row.producer)} and require-some(result.diagnostic).code == ${quote(row.internalCode)} -> ProfileError${index}(result=result)\n`;
 source+=`    providerUnknown when ${known} and (${providerKnown}) and require-some(result.diagnostic).kind == "ProviderUnknown" and require-some(result.diagnostic).providerKind == some("unknown") -> ProfileUnknownProviderError(result=result)\n    providerNoEffect when ${known} and (${providerKnown}) and require-some(result.diagnostic).kind == "ProviderNoEffect" and require-some(result.diagnostic).providerKind == some("no-effect") -> ProfileUnavailableProviderError(result=result)\n    genericDiagnostic when present(result.diagnostic) -> ProfileGenericDiagnosticError(result=result)\n    otherwise -> ProfileGenericPublicError()\n\n`;
 return source;
}
