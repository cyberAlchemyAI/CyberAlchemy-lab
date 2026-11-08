/** Finite error-presentation source consumer. No interpreter or effect authority.
 * Open Questions: docs/ERROR-PRESENTATION.md#open-questions. */
import {captureJson,dataDigest,reject} from './contracts.js';
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
import type {GenericComputationContractV1} from '../generic/computation-data-v1.js';
export const ERROR_PRESENTATION_CONSUMER='craft.error-presentation/v1' as const;
export type ErrorPresentationCategory='Conflict'|'Forbidden'|'InvalidInput';
export interface ErrorPresentationRow {readonly internalCode:string;readonly publicCode:string;readonly message:string;readonly category:ErrorPresentationCategory;readonly httpStatus:number}
export interface ErrorPresentationTable {readonly schema_version:'craft.error-presentation-table/v1';readonly producer:string;readonly reason_type:string;readonly reason_type_sha256:string;readonly rows:readonly ErrorPresentationRow[];readonly presentation_version:string;readonly source:Readonly<{profile_id:string;version:string;mapping:string;source_closure_sha256:string;contract_sha256:string;reason_projection?:Readonly<{path:string;sha256:string;start:number;end:number;projection_sha256:string}>}>}
export interface ErrorPresentationContract {readonly schema_version:'craft.error-presentation-contract/v1';readonly producer:string;readonly reason_type:string}
function fail(message:string):never{return reject('TECHNICAL_PROFILE_ERROR_PRESENTATION','error-presentation',message);}
const record=(v:unknown):v is Record<string,any>=>!!v&&typeof v==='object'&&!Array.isArray(v);
function closed(v:unknown,keys:readonly string[]):asserts v is Record<string,any>{if(!record(v)||Object.keys(v).sort().join(',')!==[...keys].sort().join(','))fail('exact closed error-presentation shape required');}
const qualified=(v:unknown):v is string=>typeof v==='string'&&v.length<=192&&/^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$/.test(v);
const digest=(v:unknown)=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
export function validateErrorPresentationContract(raw:unknown):ErrorPresentationContract {
 const value:unknown=captureJson(raw);closed(value,['schema_version','producer','reason_type']);if(value.schema_version!=='craft.error-presentation-contract/v1'||!qualified(value.producer)||!qualified(value.reason_type))fail('exact producer and reason enum contract required');return coreFreeze(value) as ErrorPresentationContract;
}
export function deriveErrorPresentationRows(raw:unknown,contract:GenericComputationContractV1,selection:ErrorPresentationContract):readonly ErrorPresentationRow[]{
 closed(raw,['cases']);if(!Array.isArray(raw.cases)||raw.cases.length<1||raw.cases.length>64)fail('bounded nonempty cases required');
 const reason=contract.values.enums.find(v=>v.name===selection.reason_type);if(!reason||reason.variants.length<1||reason.variants.length>64||reason.variants.some(v=>Object.keys(v.fields).length))fail('actual finite nullary reason enum required');
 const rootName=contract.result.kind==='record'?contract.result.name:null;const root=rootName?contract.values.records.find(r=>r.name===rootName):undefined;
 const cases=root?.fields.cases,elementName=cases?.kind==='list'&&cases.element.kind==='record'?cases.element.name:null,element=elementName?contract.values.records.find(r=>r.name===elementName):undefined;
 if(!element||element.fields.reason?.kind!=='enum'||element.fields.reason.name!==reason.name)fail('table reason field must use the exact selected nominal reason enum');
 const wires=new Set(reason.variants.map(v=>v.wire));if(wires.size!==reason.variants.length||[...wires].some(w=>!w.length||w.length>128||!/^[A-Za-z_][A-Za-z0-9_-]*$/.test(w)))fail('unique finite reason wire codes required');
 const rows:ErrorPresentationRow[]=[],seen=new Set<string>();const statusByCategory={Conflict:409,Forbidden:403,InvalidInput:422} as const;
 for(const row of raw.cases){closed(row,['reason','presentation']);closed(row.presentation,['coverage','code','message','category','httpStatus']);const p=row.presentation;
  if(typeof row.reason!=='string'||!wires.has(row.reason)||seen.has(row.reason))fail('each declared reason must occur exactly once');seen.add(row.reason);
  if(p.coverage!=='Mapped'||typeof p.code!=='string'||p.code.length<1||p.code.length>128||!/^[a-z][a-z0-9-]*$/.test(p.code))fail('mapped bounded public error code required');
  if(typeof p.message!=='string'||!p.message.isWellFormed()||!p.message.length||Buffer.byteLength(p.message)>512||[...p.message].length>256||/[\u0000-\u001f\u007f]/.test(p.message))fail('bounded public literal message without controls required');
  if(!Object.hasOwn(statusByCategory,p.category)||typeof p.httpStatus!=='string'||! /^(403|409|422)$/.test(p.httpStatus)||statusByCategory[p.category as ErrorPresentationCategory]!==Number(p.httpStatus))fail('canonical finite category/status pair required');
  rows.push({internalCode:row.reason,publicCode:p.code,message:p.message,category:p.category,httpStatus:Number(p.httpStatus)});
 }
 if(seen.size!==wires.size)fail('table must cover the complete actual reason enum');
 return coreFreeze(rows.sort((a,b)=>a.internalCode.localeCompare(b.internalCode)));
}
export function createErrorPresentationTable(rows:readonly ErrorPresentationRow[],selection:ErrorPresentationContract,contract:GenericComputationContractV1,source:ErrorPresentationTable['source']):ErrorPresentationTable {
 if(!digest(source.source_closure_sha256)||!digest(source.contract_sha256)||!qualified(source.mapping)||!qualified(source.profile_id))fail('actual captured error-profile source identity required');
 const reason=contract.values.enums.find(v=>v.name===selection.reason_type);if(!reason)fail('captured reason enum required');
 const value={schema_version:'craft.error-presentation-table/v1' as const,producer:selection.producer,reason_type:selection.reason_type,reason_type_sha256:dataDigest(reason),rows,source};return coreFreeze({...value,presentation_version:dataDigest(value)});
}
