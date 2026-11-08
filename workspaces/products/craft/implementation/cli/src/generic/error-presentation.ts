/** Checked error presentation over original application outcomes; no execution/retry authority.
 * Open Questions: docs/ERROR-PRESENTATION.md#open-questions. */
import {randomBytes} from 'node:crypto';
import type {ErrorPresentationTable} from '../profile-engine/technical-profile-error-contracts.js';
import {dataDigest} from '../profile-engine/contracts.js';
import {assertTechnicalProfileSourceOwner,type CheckedTechnicalProfileSource,type createTechnicalProfileSourceOwner} from '../profile-engine/technical-profile-source.js';
import {requireGenericCompositionRuntime,type GenericCompositionHandle} from './public-sdk.js';
import {assertGenericErrorRuntimeBinding} from './execution-session.js';
import type {GenericApplicationRuntime,GenericTransactionApplicationRuntime} from './invocation-owner.js';

export interface GenericErrorPresentationBinding {readonly kind:'original-error-presentation-binding/v1'}
type Table=ErrorPresentationTable;
type Bound={current:()=>void;original:ReturnType<typeof requireGenericCompositionRuntime>;table:Table;entries:ReadonlySet<string>};
const bindings=new WeakMap<object,Bound>();
const fixed:Record<string,{status:number;message:string;category:string}>={
 AuthenticationRequired:{status:401,message:'Authentication is required.',category:'Forbidden'},PermissionDenied:{status:403,message:'Access is denied.',category:'Forbidden'},
 AuthorizationUnavailable:{status:503,message:'Authorization is unavailable.',category:'Unavailable'},
 CommitIndeterminate:{status:503,message:'The command outcome requires reconciliation.',category:'Unavailable'},ExternalOutcomeUnknown:{status:503,message:'The external outcome requires reconciliation.',category:'Unavailable'},
 InvalidCommandKey:{status:400,message:'The command key is invalid.',category:'InvalidInput'},
 MalformedRequest:{status:400,message:'The request is invalid.',category:'InvalidInput'},InvalidInput:{status:400,message:'The request is invalid.',category:'InvalidInput'},PayloadTooLarge:{status:413,message:'The request exceeds the permitted size.',category:'InvalidInput'},
 UnsupportedMediaType:{status:415,message:'The request media type is unsupported.',category:'InvalidInput'},RouteNotFound:{status:404,message:'The requested route was not found.',category:'InvalidInput'},MethodNotAllowed:{status:405,message:'The request method is unsupported.',category:'InvalidInput'},BodyTimeout:{status:408,message:'The request body timed out.',category:'InvalidInput'},
 StorageUnavailable:{status:503,message:'Storage is unavailable.',category:'Unavailable'},ReadConflict:{status:409,message:'The stored data changed.',category:'Conflict'},CommandPayloadConflict:{status:409,message:'The command key conflicts with a previous request.',category:'Conflict'},CommandIdentityCollision:{status:409,message:'The command identity conflicts.',category:'Conflict'},
 ExecutionFault:{status:422,message:'The operation could not be evaluated.',category:'InvalidInput'},CommandCapacity:{status:503,message:'Command capacity is unavailable.',category:'Unavailable'},RevisionExhausted:{status:503,message:'Storage revision capacity is unavailable.',category:'Unavailable'},
};
const aliases:Record<string,string>={'invalid-request':'MalformedRequest','request-aborted':'MalformedRequest','body-read-failed':'MalformedRequest','request-too-large':'PayloadTooLarge','unsupported-media-type':'UnsupportedMediaType','route-not-found':'RouteNotFound','method-not-allowed':'MethodNotAllowed','command-key-required':'InvalidInput','invalid-command-key':'InvalidInput'};
function response(status:number,code:string,message:string,category:string,version:string):Response{
 const correlationId=randomBytes(16).toString('hex');const error={code,message,category,correlationId,presentationVersion:version};const body=JSON.stringify({kind:'error',error});
 if(Buffer.byteLength(body)>4096)return new Response(JSON.stringify({kind:'error',error:{code:'internal-error',message:'The request could not be completed.',category:'Internal',correlationId,presentationVersion:'fixed-v1'}}),{status:500,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
 return new Response(body,{status,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
}
/** Platform semantics remain fixed here; unknown codes never echo caller/error content. */
export function renderGenericPlatformError(code:string,status=500,presentationVersion='fixed-v1'):Response{
 const selected=fixed[aliases[code]??code];
 if(selected&&selected.status===status)return response(status,aliases[code]??code,selected.message,selected.category,/^[a-f0-9]{64}$/.test(presentationVersion)?presentationVersion:'fixed-v1');
 return response(500,'internal-error','The request could not be completed.','Internal','fixed-v1');
}
export function createGenericErrorPresentationBinding({sourceOwner,sourceHandle,businessOwner,businessHandle,entries}:{sourceOwner:ReturnType<typeof createTechnicalProfileSourceOwner>;sourceHandle:CheckedTechnicalProfileSource;businessOwner:unknown;businessHandle:GenericCompositionHandle;entries?:readonly string[]}):GenericErrorPresentationBinding{
 assertTechnicalProfileSourceOwner(sourceOwner);const original=requireGenericCompositionRuntime(businessOwner,businessHandle);original.assertCurrent();
 const table=sourceOwner.inspectErrorPresentation(sourceHandle) as Table;const contract=original.plans.inspectSourceApplication(original.application).contract;
 const actualEnum=contract.values.enums.find(e=>e.name===table.reason_type);if(!actualEnum||dataDigest(actualEnum)!==table.reason_type_sha256)throw Error('ERROR_PRESENTATION_ENUM_MISMATCH');
 const selected=entries??contract.entries.filter(e=>e.target===table.producer).map(e=>e.entry);if(!selected.length||new Set(selected).size!==selected.length)throw Error('ERROR_PRESENTATION_ENTRIES_REQUIRED');
 for(const name of selected){const entry=original.plans.inspectEntry(original.plans.bindEntry(original.application,name));if(entry.target!==table.producer)throw Error('ERROR_PRESENTATION_PRODUCER_MISMATCH');}
 const digest=dataDigest(table),current=()=>{original.assertCurrent();sourceOwner.assertCurrent(sourceHandle);if(dataDigest(sourceOwner.inspectErrorPresentation(sourceHandle))!==digest)throw Error('ERROR_PRESENTATION_STALE');};current();
 const binding=Object.freeze({kind:'original-error-presentation-binding/v1' as const});bindings.set(binding,{original,table,entries:new Set(selected),current});return binding;
}
export function assertGenericErrorPresentationRuntime(binding:GenericErrorPresentationBinding,runtime:GenericApplicationRuntime|GenericTransactionApplicationRuntime):void{const row=bindings.get(binding);if(!row)throw Error('ERROR_PRESENTATION_FOREIGN_BINDING');row.current();assertGenericErrorRuntimeBinding(runtime as GenericTransactionApplicationRuntime,row.original.plans,row.original.application);}
export function inspectGenericErrorPresentation(binding:GenericErrorPresentationBinding){const row=bindings.get(binding);if(!row)throw Error('ERROR_PRESENTATION_FOREIGN_BINDING');row.current();return Object.freeze({presentation_version:row.table.presentation_version,producer:row.table.producer,reason_type:row.table.reason_type,entries:Object.freeze([...row.entries])});}
export function renderGenericErrorPresentation(binding:GenericErrorPresentationBinding,input:{entry:string;outcomeKind:string;code?:string;platformCode?:string;status?:number}):Response{
 const row=bindings.get(binding);try{if(!row)throw Error('FOREIGN');row.current();if(input.platformCode)return renderGenericPlatformError(input.platformCode,input.status??500,row.table.presentation_version);
 if(input.outcomeKind!=='Rejected'||!row.entries.has(input.entry))return renderGenericPlatformError('InternalError',500);
 const selected=row.table.rows.find(r=>r.internalCode===input.code);if(!selected)return renderGenericPlatformError('InternalError',500);
 return response(selected.httpStatus,selected.publicCode,selected.message,selected.category,row.table.presentation_version);
 }catch{return renderGenericPlatformError('InternalError',500);}
}
