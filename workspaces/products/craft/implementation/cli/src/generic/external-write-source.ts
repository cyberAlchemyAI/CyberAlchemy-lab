/** Original captured declarations -> checked inert write/inspection pairs.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail,coreSourceChildren as children,coreSourceTokens as tokens} from '../commerce/commerce-core-syntax.js';
import {coreValueAstType,type GenericExpressionData} from '../commerce/commerce-core-pure.js';
import {parseCoreCommerceJson,type CoreCommerceSourceInspection} from '../commerce/commerce-core-source-owner.js';
import type {CoreOperationSource} from '../commerce/commerce-core-flow-operation.js';
import type {CoreQuerySemantics} from '../commerce/commerce-core-flow-query.js';
import type {createCoreValueTypes} from '../commerce/commerce-core-types.js';
import type {GenericPureDeclarationV1} from './computation-data-v1.js';
import type * as W from './external-write-data-v1.js';
import {resolveGenericExternalWriteSelection} from './external-write-profile.js';
const at={path:'contracts/external-write-bindings.json',start:0,end:0};
type Operation=GenericExpressionData<CoreOperationSource>;type Query=GenericExpressionData<CoreQuerySemantics>;
export function deriveCheckedExternalWriteBindings(capture:CoreCommerceSourceInspection,types:ReturnType<typeof createCoreValueTypes>,operations:readonly Operation[],queries:readonly Query[],functions:readonly GenericPureDeclarationV1[]){
 if(capture.capture_mode!=='external-write-entry'&&capture.capture_mode!=='event-handoff-entry')fail('InvalidContract',at,'actual original external-write capture required');const asset=capture.files.find(f=>f.path===at.path);if(!asset)fail('MissingMapping',at,'actual physically captured write selection required');
 // The original physical owner has already applied the strict JSON decoder.
 const selected=resolveGenericExternalWriteSelection(parseCoreCommerceJson(asset.text,asset.path)),same=(a:unknown,b:unknown)=>dataDigest(a)===dataDigest(b),fn=(id:string,kind:'Mapping'|'Rule')=>{const f=functions.find(f=>f.name===id);if(!f||f.kind!==kind||!f.pure)fail('TypeMismatch',at,'actual pure '+kind+' required: '+id);return f;};
 const bindings:W.GenericExternalWriteCheckedBindingV1[]=selected.bindings.map(b=>{
  const iface=types.declarations.get(b.interface_ref),write=operations.find(o=>o.name===b.write_operation_ref),inspect=queries.find(q=>q.name===b.inspect_query_ref);
  if(!iface||iface.interface_kind!=='external'||iface.exposes.length!==2||!write||write.protocol?.kind!=='native-capture'||!inspect||inspect.kind!=='native-protocol'||write.protocol.interface!==iface.id||inspect.interface!==iface.id||b.native_family_ref!==iface.id||write.contexts.length||inspect.contexts.length)fail('InvalidContract',at,'actual context-free native capture and paired inspection on one Interface required');
  const clauses=children(iface.syntax,'interface-clause').filter(c=>tokens(c).filter(t=>!t.layout)[0]?.token==='protocol');if(clauses.length!==1)fail('InvalidContract',iface.syntax,'one exact source protocol required');const protocol=tokens(clauses[0]!).filter(t=>!t.layout)[1]?.token;
  if(protocol!==b.protocol_id||inspect.protocol!==b.protocol_id||write.protocol.binding_path!==inspect.binding_path||!write.protocol.binding_path||!write.protocol.intent)fail('InvalidContract',iface.syntax,'exact original protocol and shared native binding path required');
  const native=capture.files.find(f=>f.path===inspect.binding_path);if(!native||!native.path.endsWith('.json'))fail('MissingMapping',iface.syntax,'native JSON profile must be physically captured');const profile=parseCoreCommerceJson(native.text,native.path);
  if(!profile||typeof profile!=='object'||Array.isArray(profile)||!Object.hasOwn(profile,'protocol')||(profile as Record<string,unknown>).protocol!==b.protocol_id)fail('InvalidContract',iface.syntax,'captured native profile protocol differs from exact source token');
  const wire_request_type=coreValueAstType(write.protocol.intent.type),wire_result_type=coreValueAstType(write.result);if(!same(write.parameters.map(p=>({name:p.name,type:coreValueAstType(p.type)})),inspect.parameters.map(p=>({name:p.name,type:coreValueAstType(p.type)})))||!same(wire_result_type,coreValueAstType(inspect.result)))fail('TypeMismatch',iface.syntax,'write and inspect must have identical ordered request/result signatures');
  const request=fn(b.request_mapping_ref,'Mapping'),inspectRequest=fn(b.inspect_request_mapping_ref,'Mapping'),validation=fn(b.response_validation_rule_ref,'Rule'),response=fn(b.response_mapping_ref,'Mapping'),matches=fn(b.matches_rule_ref,'Rule'),unresolved=fn(b.unresolved_rule_ref,'Rule');
  if(request.parameters.length!==1||inspectRequest.parameters.length!==1||!same(request.parameters[0]!.type,inspectRequest.parameters[0]!.type)||!same(request.result,wire_request_type)||!same(inspectRequest.result,wire_request_type)||response.parameters.length!==1||!same(response.parameters[0]!.type,wire_result_type)||validation.parameters.length!==2||!same(validation.parameters.map(p=>p.type),[wire_request_type,wire_result_type])||validation.result.kind!=='scalar'||validation.result.name!=='Bool'||matches.parameters.length!==2||!same(matches.parameters.map(p=>p.type),[request.parameters[0]!.type,response.result])||matches.result.kind!=='scalar'||matches.result.name!=='Bool'||unresolved.parameters.length!==1||!same(unresolved.parameters[0]!.type,response.result)||unresolved.result.kind!=='scalar'||unresolved.result.name!=='Bool')fail('TypeMismatch',iface.syntax,'exact source-bound request/inspect/validation/response/matches/unresolved Mapping and Rule signatures required');
  return coreFreeze({...b,schema_version:'craft.generic-external-write-binding/v1-candidate' as const,request_type:request.parameters[0]!.type,result_type:response.result,wire_request_type,wire_result_type,write_contract_sha256:dataDigest(write),inspect_contract_sha256:dataDigest(inspect),mapping_contracts_sha256:dataDigest([request,inspectRequest,validation,response,matches,unresolved]),selection_source:{path:asset.path,sha256:asset.sha256,bytes:asset.bytes},native_source:{path:native.path,sha256:native.sha256,bytes:native.bytes}});
 });
 const nativeOperations=operations.filter(o=>o.protocol?.kind==='native-capture'),nativeQueries=queries.filter(q=>q.kind==='native-protocol');if(nativeOperations.length!==bindings.length||nativeQueries.length!==bindings.length||nativeOperations.some(o=>!bindings.some(b=>b.write_operation_ref===o.name))||nativeQueries.some(q=>!bindings.some(b=>b.inspect_query_ref===q.name)))fail('InvalidContract',at,'every native declaration requires one checked write/inspect pair before projection');
 return coreFreeze({selection:selected,bindings});
}
/** No meaning projection can erase selected native protocol or Mapping identity. */
export function externalWriteExecutableMeaning(contract:W.GenericExternalWriteTransactionApplicationV1){return contract;}
