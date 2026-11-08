/** Materializes finite identity primitives and original native callsite data.
 * Open Questions: docs/COMMERCE-NATIVE-IDENTITY.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {types as host} from 'node:util';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {pinCoreImplementation,readCorePhysicalFile} from './commerce-core-physical.js';
import {generateCommerceValueCodecBundle} from './commerce-value-codec-generation.js';
import {assertCommerceIdentityCallOwner,type CommerceIdentityCallOwner,type CommerceIdentityCallHandle} from './commerce-identity-call-owner.js';
import type {CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),asset='../../profiles/commerce-local-v1-candidate/runtime/context.ts',pin=pinCoreImplementation(import.meta.url,['commerce-identity-call-owner'+ext,'commerce-value-codec-generation'+ext,asset]),where={path:'application.alch',start:0,end:0},sha=(s:string)=>createHash('sha256').update(s).digest('hex');
// This finite native ABI is implemented by context.ts. Source profiles may
// select it; changing a descriptor does not implement a new primitive.
const supported:Readonly<Record<string,{domain:string|null;parameters:string;result:string}>>={
 checkoutFingerprint:{domain:'craft.checkout-request/v1-candidate',parameters:'logicalEntryId:Identifier,customerId:Identifier,quoteId:Identifier',result:'RequestFingerprint'},
 newOrderId:{domain:'craft.order-id/v1-candidate',parameters:'logicalEntryId:Identifier,customerId:Identifier,checkoutKey:Identifier',result:'Identifier'},
 commandId:{domain:'craft.command-id/v1-candidate',parameters:'namespace:CommandNamespace,orderId:Identifier',result:'Identifier'},
 eventMetadata:{domain:'craft.event-occurrence/v1-candidate',parameters:'producer:ServiceId,aggregateId:Identifier,aggregateVersion:UInt64,ordinal:UInt64,correlationId:Identifier,commandId:Identifier',result:'schema:Shop.Events.EventMetadata@1'},
 stockLinesFingerprint:{domain:'craft.stock-lines/v1-candidate',parameters:'lines:List<StockLine,100>',result:'RequestFingerprint'},
 stockCommandFingerprint:{domain:'craft.stock-command/v1-candidate',parameters:'kind:StockCommandKindName,orderId:Identifier,lines:List<StockLine,100>,expectedReservationVersion:optional<UInt64>',result:'RequestFingerprint'},
 captureFingerprint:{domain:'craft.capture-request/v1-candidate',parameters:'attemptKey:Identifier,orderId:Identifier,amountMinor:UInt64,currency:Currency',result:'RequestFingerprint'},
 eventFingerprint:{domain:'craft.event-content/v1-candidate',parameters:'event:selected-schema:Shop.Events.Event@1',result:'RequestFingerprint'},
 confirmedOrderFingerprint:{domain:'craft.confirmed-order/v1-candidate',parameters:'orderId:Identifier,customerId:Identifier,lines:List<StockLine,100>,payableMinor:UInt64,currency:Currency,reservationId:Identifier,reservationVersion:UInt64,paymentAttemptKey:Identifier,providerReference:Identifier',result:'RequestFingerprint'},
 orderActionFingerprint:{domain:'craft.order-action/v1-candidate',parameters:'action:OrderActionName,orderId:Identifier,reason:optional<Shop.Events.CancellationReason>',result:'RequestFingerprint'},
 clockEpochMs:{domain:null,parameters:'',result:'UInt64'},
};
/** A captured slot policy must partition the complete original tagged enum.
 * The slot names are source data; no application variant is compiled into JS. */
export function checkCommerceTaggedIdentitySlotGroupsV1(raw:unknown,variants:readonly string[]):Readonly<Record<string,string>>{
 if(!raw||typeof raw!=='object'||host.isProxy(raw)||Array.isArray(raw)||![Object.prototype,null].includes(Object.getPrototypeOf(raw)))
  fail('InvalidContract',where,'closed source-declared tagged slots required');
 const slots=Reflect.ownKeys(raw);if(!slots.length||slots.length>128||slots.some(s=>typeof s!=='string'||! /^[a-z][a-z0-9-]{0,63}$/.test(s)))
  fail('InvalidContract',where,'bounded named tagged slots required');
 const expected=new Set(variants),assigned:Record<string,string>=Object.create(null);
 if(expected.size!==variants.length||!expected.size||expected.size>128)fail('InvalidContract',where,'checked enum variants required');
 for(const slot of slots as string[]){
  const descriptor=Object.getOwnPropertyDescriptor(raw,slot),members=descriptor&&Object.hasOwn(descriptor,'value')?descriptor.value:undefined;
  if(!Array.isArray(members)||host.isProxy(members)||Object.getPrototypeOf(members)!==Array.prototype||!members.length||
   members.length>128||Reflect.ownKeys(members).length!==members.length+1)fail('InvalidContract',where,'dense tagged slot members required');
  for(let i=0;i<members.length;i++){
   const member=Object.getOwnPropertyDescriptor(members,String(i));if(!member||!Object.hasOwn(member,'value')||typeof member.value!=='string'||
    !expected.has(member.value)||Object.hasOwn(assigned,member.value))fail('InvalidContract',where,'each original enum variant needs exactly one tagged slot');
   assigned[member.value]=slot;
  }
 }
 if(Object.keys(assigned).length!==expected.size)fail('InvalidContract',where,'tagged slot table must cover every original enum variant');
 return coreFreeze(assigned);
}
function checkTaggedIdentityBinding(b:ReturnType<CommerceIdentityCallOwner['inspect']>,values:ReturnType<CommerceComputationDomainOwner['inspect']>['contract']['values']):void{
 const s=b.signature as any,parameters=s.parameters;
 if(s.abi!=='craft.commerce-identity/v1-candidate'||s.encoding!=='ordered-utf8-field-tuple/v1-candidate'||
  s.domain!=='craft.tagged-observation/v1-candidate'||!Array.isArray(parameters)||parameters.length!==2||
  parameters[0]?.name!=='scopeId'||parameters[0]?.type!=='Identifier'||parameters[1]?.name!=='taggedValue'||
  b.parameters.length!==2||b.parameters[0]?.type.kind!=='refinement'||b.parameters[0].type.name!=='Shop.Values.Identifier'||
  b.parameters[1]?.type.kind!=='enum'||parameters[1]?.type!==b.parameters[1].type.name||b.observation.result.kind!=='record')
  fail('UnsupportedCapability',b.span,'tagged identity requires an exact original enum and shared identity types');
 const enumName=b.parameters[1].type.name,resultName=b.observation.result.name;
 const enumeration=values.enums.find(e=>e.name===enumName),record=values.records.find(r=>r.name===resultName);
 if(!enumeration||!record||record.role!=='ValueObject'||s.result!==resultName.split('.').at(-1)||
  Object.keys(record.fields).length!==2||record.fields.commandId?.kind!=='refinement'||record.fields.commandId.name!=='Shop.Values.Identifier'||
  record.fields.requestFingerprint?.kind!=='refinement'||record.fields.requestFingerprint.name!=='Shop.Values.RequestFingerprint')
  fail('UnsupportedCapability',b.span,'tagged identity result must be the checked command/fingerprint ValueObject');
 checkCommerceTaggedIdentitySlotGroupsV1(s.slot_groups,enumeration.variants.map(v=>v.name));
}
export function generateCommerceIdentityBundle(calls:CommerceIdentityCallOwner,handles:readonly CommerceIdentityCallHandle[],stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle){
 assertCommerceIdentityCallOwner(calls);pin.assertCurrent();if(host.isProxy(handles)||!Array.isArray(handles)||Object.getPrototypeOf(handles)!==Array.prototype)fail('InvalidContract',where,'bounded inert native source-call collection required');const length=Object.getOwnPropertyDescriptor(handles,'length')!.value;if(!length||length>256||Reflect.ownKeys(handles).length!==length+1)fail('InvalidContract',where,'bounded original native source-call collection required');const originals:CommerceIdentityCallHandle[]=[];for(let i=0;i<length;i++){const d=Object.getOwnPropertyDescriptor(handles,String(i));if(!d||!d.enumerable||!Object.hasOwn(d,'value'))fail('InvalidContract',where,'inert original source-call array required');originals.push(d.value);}
 const parent=calls.sourceDomain(),actual=domain.inspect(baseline);if(parent.contract_sha256!==actual.contract_sha256||parent.source_capture_sha256!==actual.source_capture_sha256)fail('ForeignOwner',where,'codec and identity parents must share the original source/domain');
 const bindings=calls.inspectMany(originals);if(new Set(bindings.map(b=>b.key)).size!==bindings.length)fail('InvalidContract',where,'duplicate source native callsites');
 for(const b of bindings){
  if(b.observation.method==='taggedCommandIdentity'){checkTaggedIdentityBinding(b,actual.contract.values);continue;}
  const s=b.signature as any,known=supported[b.observation.method];if(!known||s.abi!=='craft.commerce-identity/v1-candidate'||s.result!==known.result||!Array.isArray(s.parameters)||s.parameters.map((p:any)=>p.name+':'+p.type).join(',')!==known.parameters||(s.domain??null)!==known.domain||known.domain&&s.encoding!=='ordered-utf8-field-tuple/v1-candidate'||b.observation.method==='clockEpochMs'&&s.kind!=='trusted-wall-clock')fail('UnsupportedCapability',b.span,'source signature is not the implemented finite identity primitive ABI');
 }
 const codecs=generateCommerceValueCodecBundle(stage,source,domain,baseline),model={schema_version:'craft.commerce-identity-components/v1-candidate',abi:'craft.commerce-identity/v1-candidate',source_capture_sha256:actual.source_capture_sha256,domain_contract_sha256:actual.contract_sha256,source_schema:actual.contract.values,bindings,maximum_tuple_bytes:524288,qualification:'source-bound identity data primitives;original invocation/context/commit/delivery owners required separately',authority_effect:'none'};
 const data=`// Generated original source-call identity model; data only.\n// Open Questions: docs/COMMERCE-NATIVE-IDENTITY.md#open-questions.\nfunction freezeIdentity(value:any):any{if(value&&typeof value==='object'){for(const child of Object.values(value))freezeIdentity(child);Object.freeze(value);}return value;}\nexport const commerceIdentityModel=freezeIdentity(JSON.parse(${JSON.stringify(JSON.stringify(model))}));\n`;
 const runtime=readCorePhysicalFile(fileURLToPath(new URL(asset,import.meta.url))).text,files=coreFreeze([...codecs.files,{path:'commerce-identity-model.ts',text:data},{path:'context.ts',text:runtime}]);
 const manifest=coreFreeze({kind:'commerce-native-identity-component/v1-candidate',source_capture_sha256:actual.source_capture_sha256,domain_contract_sha256:actual.contract_sha256,code_epoch_sha256:pin.sha256,codec_manifest:codecs.manifest,source_bindings:bindings.map(b=>({key:b.key,caller:b.caller,service:b.service,path:b.expression_path,method:b.observation.method,event_schema:b.event_schema,event_targets:b.event_targets})),model_sha256:dataDigest(model),members:files.map(f=>({path:f.path,sha256:sha(f.text),bytes:Buffer.byteLength(f.text)})),runtime_dependencies:['node:util','node:crypto'],qualification:'original-source/native identity data component only;not-selected-basis-or-original-operation-invocation-context',authority_effect:'none',open_questions_ref:'docs/COMMERCE-NATIVE-IDENTITY.md#open-questions'});
 calls.assertCurrentSet(originals);pin.assertCurrent();return Object.freeze({files,manifest});
}
