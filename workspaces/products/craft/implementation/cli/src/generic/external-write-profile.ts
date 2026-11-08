/** Closed, inert write selection. No producer, attempt or dispatch authority.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {captureJson} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import type * as W from './external-write-data-v1.js';
const at={path:'contracts/external-write-bindings.json',start:0,end:0};
const keys=['id','interface_ref','write_operation_ref','inspect_query_ref','native_family_ref','protocol_id','request_mapping_ref','inspect_request_mapping_ref','response_validation_rule_ref','response_mapping_ref','matches_rule_ref','unresolved_rule_ref'] as const;
function closed(v:unknown,required:readonly string[],optional:readonly string[]=[]):Record<string,unknown>{if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).some(k=>![...required,...optional].includes(k))||required.some(k=>!Object.hasOwn(v,k)))return fail('InvalidContract',at,'closed inert write selection object required');return v as Record<string,unknown>;}
function source(v:unknown):v is string{return typeof v==='string'&&v.length>=1&&v.length<=256&&/^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$/.exec(v)?.[0]===v;}
/** Full-string match: a final newline is never admitted by a dollar anchor. */
export function isGenericExternalProtocolId(v:unknown):v is string{return typeof v==='string'&&v.length>=1&&Buffer.byteLength(v)<=256&&/^[A-Za-z_][A-Za-z0-9_.-]*$/.exec(v)?.[0]===v;}
export function resolveGenericExternalWriteSelection(raw:unknown):W.GenericExternalWriteSelectionV1{
 const v=closed(captureJson(raw),['schema_version','identity_limits','bindings'],['open_questions_ref']);if(v.schema_version!=='craft.generic-external-write-selection/v1-candidate'||!Array.isArray(v.bindings)||v.bindings.length<1||v.bindings.length>16)fail('InvalidContract',at,'exact bounded write selection required');
 const limits=closed(v.identity_limits,['schema_version','max_child_depth','max_local_call_frames','max_site_occurrences','max_total_occurrences','max_tuple_bytes','wrapper_depth']);if(limits.schema_version!=='craft.generic-causal-identity-limits/v1-candidate')fail('InvalidContract',at,'explicit causal limits required');
 for(const [k,min,max]of [['max_child_depth',1,60],['max_local_call_frames',1,64],['max_site_occurrences',1,2147483647],['max_total_occurrences',1,2147483647],['max_tuple_bytes',1,1048576],['wrapper_depth',0,60]]as const){const x=limits[k];if(typeof x!=='number'||!Number.isSafeInteger(x)||Object.is(x,-0)||x<min||x>max)fail('InvalidContract',at,'explicit selected causal bound required: '+k);}
 const ids=new Set<string>(),interfaces=new Set<string>(),members=new Set<string>();for(const rawBinding of v.bindings){const b=closed(rawBinding,keys);for(const k of keys)if(k==='protocol_id'?!isGenericExternalProtocolId(b[k]):!source(b[k]))fail('InvalidContract',at,'exact write binding reference required: '+k);
  if(b.native_family_ref!==b.interface_ref||ids.has(b.id as string)||interfaces.has(b.interface_ref as string)||members.has(b.write_operation_ref as string)||members.has(b.inspect_query_ref as string)||b.write_operation_ref===b.inspect_query_ref)fail('InvalidContract',at,'unique exact source Interface family/pair required');ids.add(b.id as string);interfaces.add(b.interface_ref as string);members.add(b.write_operation_ref as string);members.add(b.inspect_query_ref as string);
 }
 if(v.open_questions_ref!==undefined&&(typeof v.open_questions_ref!=='string'||v.open_questions_ref.length<1||v.open_questions_ref.length>4096))fail('InvalidContract',at,'bounded inert documentation reference required');return coreFreeze(v) as unknown as W.GenericExternalWriteSelectionV1;
}
