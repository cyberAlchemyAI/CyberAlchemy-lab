/** Checked DemoPay-v1 wire projection for original Commerce source sites.
 * Capture is encoding only: a future protected command owner must supply an
 * opaque one-shot dispatch permit before any Capture send can be added.
 * Open Questions: docs/COMMERCE-NATIVE-V1.md#open-questions. */
import {types as host} from 'node:util';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {parseCoreCommerceJson,assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCommerceDemoPaySourceSiteOwnerV1,type CommerceDemoPaySourceSiteOwnerV1,type CommerceDemoPaySourceSiteV1} from './commerce-demopay-source-site-v1.js';
import {assertCommerceDemoPayIntentWitnessOwnerV1,type CommerceDemoPayIntentWitnessOwnerV1,type CommerceDemoPayIntentWitnessV1} from './commerce-demopay-intent-witness-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-core-physical'+ext,'commerce-core-source-owner'+ext,'commerce-demopay-source-site-v1'+ext,'commerce-demopay-intent-witness-v1'+ext]);
const decoder=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true});
const headers=Object.freeze({'content-type':'application/json; charset=utf-8','demopay-protocol':'1'});
const maxUint=18446744073709551615n;
const decimal=/^(0|[1-9][0-9]{0,19})$/;
export class CommerceDemoPayWireErrorV1 extends Error {constructor(readonly code:string){super(code);this.name='CommerceDemoPayWireErrorV1';}}
const bad=(code:string):never=>{throw new CommerceDemoPayWireErrorV1(code);};
export interface DemoPayCommerceRequestV1 {readonly attemptKey:string;readonly orderId:string;readonly amountMinor:string;readonly currency:'USD'}
export interface DemoPayCommerceResultV1 extends DemoPayCommerceRequestV1 {readonly status:'Captured'|'DefinitivelyDeclined'|'Pending'|'Unknown'|'UnknownKey';readonly providerReference:string|null}
export interface DemoPayCommerceWireRequestV1 {readonly origin:'https://demopay.invalid';readonly method:'POST';readonly path:'/v1/capture'|'/v1/capture/inspect';readonly headers:Readonly<Record<string,string>>;readonly body:Uint8Array;readonly signal:AbortSignal}
export interface DemoPayCommerceWireResponseV1 {readonly status:number;readonly headers:Readonly<Record<string,string>>;readonly body:Uint8Array}
export interface DemoPayCommerceRawBytePortV1 {exchange(request:DemoPayCommerceWireRequestV1):Promise<DemoPayCommerceWireResponseV1>}
export type DemoPayCommerceObservationV1=Readonly<
 |{kind:'observed';result:DemoPayCommerceResultV1;matches_request:boolean}
 |{kind:'unresolved';reason:'timeout'|'transport'|'malformed'|'provider-unavailable'|'invalid-request'|'attempt-key-conflict'|'unknown-key'}>;
const keys=(value:unknown,expected:readonly string[]):value is Record<string,unknown>=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))return false;
 const actual=Reflect.ownKeys(value);if(actual.length!==expected.length||actual.some(k=>typeof k!=='string'||!expected.includes(k)))return false;
 const descriptors=Object.getOwnPropertyDescriptors(value);return expected.every(k=>descriptors[k]?.enumerable&&Object.hasOwn(descriptors[k]!,'value'));
};
const identifier=(value:unknown):value is string=>typeof value==='string'&&value.length>0&&Buffer.byteLength(value,'utf8')<=128&&Buffer.from(value).toString('utf8')===value;
const uint64=(value:unknown):value is string=>typeof value==='string'&&decimal.test(value)&&BigInt(value)<=maxUint;
function requestOf(value:unknown):DemoPayCommerceRequestV1 {
 if(!keys(value,['attemptKey','orderId','amountMinor','currency']))bad('InvalidRequest');
 const row=value as Record<string,unknown>;
 if(!identifier(row.attemptKey)||!identifier(row.orderId)||!uint64(row.amountMinor)||row.currency!=='USD')bad('InvalidRequest');
 return Object.freeze({attemptKey:row.attemptKey as string,orderId:row.orderId as string,amountMinor:row.amountMinor as string,currency:'USD' as const});
}
function resultOf(value:unknown):DemoPayCommerceResultV1 {
 if(!keys(value,['attemptKey','orderId','amountMinor','currency','status','providerReference']))bad('MalformedResponse');
 const {attemptKey,orderId,amountMinor,currency,status,providerReference}=value as Record<string,unknown>;
 if(!identifier(attemptKey)||!identifier(orderId)||!uint64(amountMinor)||currency!=='USD'||!['Captured','DefinitivelyDeclined','Pending','Unknown','UnknownKey'].includes(String(status))||
  (status==='Captured'||status==='DefinitivelyDeclined'? !identifier(providerReference):providerReference!==null))bad('MalformedResponse');
 return Object.freeze({attemptKey,orderId,amountMinor,currency:'USD',status,providerReference}) as DemoPayCommerceResultV1;
}
function profileOf(value:unknown):void {
 if(!value||typeof value!=='object'||Array.isArray(value))bad('UnsupportedProfile');const p=value as Record<string,any>;
 if(p.schema_version!=='craft.demopay-wire/v1-candidate'||p.protocol!=='DemoPay-v1'||p.source_module!=='Shop.DemoPay@1'||p.formal_claims_required!==false||p.authority_effect!=='none')bad('UnsupportedProfile');
 const d=p.$defs,t=p.transport,o=p.operations,r=p.result_binding;
 if(d?.Identifier?.type!=='string'||d.Identifier.minLength!==1||d.Identifier.maxLength!==128||d.Identifier['x-utf8-bytes-max']!==128||d.Identifier['x-unicode']!=='well-formed-scalars'||
  d.UInt64?.type!=='string'||d.UInt64.pattern!==decimal.source||d.UInt64['x-exact-max']!==String(maxUint)||d.UInt64['x-native-range-check-required']!==true||
  d.CaptureRequest?.additionalProperties!==false||d.CaptureResult?.additionalProperties!==false||d.ProviderError?.additionalProperties!==false||
  JSON.stringify(d.CaptureRequest.required)!==JSON.stringify(['attemptKey','orderId','amountMinor','currency'])||
  d.CaptureRequest.properties?.attemptKey?.$ref!=='#/$defs/Identifier'||d.CaptureRequest.properties?.orderId?.$ref!=='#/$defs/Identifier'||d.CaptureRequest.properties?.amountMinor?.$ref!=='#/$defs/UInt64'||d.CaptureRequest.properties?.currency?.const!=='USD'||
  JSON.stringify(d.CaptureResult.required)!==JSON.stringify(['attemptKey','orderId','amountMinor','currency','status','providerReference'])||
  JSON.stringify(d.CaptureResult.properties?.status?.enum)!==JSON.stringify(['Captured','DefinitivelyDeclined','Pending','Unknown','UnknownKey'])||
  JSON.stringify(d.ProviderError.required)!==JSON.stringify(['kind','code'])||d.ProviderError.properties?.kind?.const!=='error'||
  JSON.stringify(d.ProviderError.properties?.code?.enum)!==JSON.stringify(['invalid-request','attempt-key-conflict','provider-unavailable'])||
  t?.mode!=='injected-http-bytes'||t.origin!=='https://demopay.invalid'||t.network_fetch_fallback!==false||t.listener!==false||t.request_bytes!==4096||t.response_bytes!==8192||
  t.request_headers?.['content-type']!==headers['content-type']||t.request_headers?.['demopay-protocol']!==headers['demopay-protocol']||
  t.response_headers?.['content-type']!==headers['content-type']||t.response_headers?.['demopay-protocol']!==headers['demopay-protocol']||
  t.json_encoding?.charset!=='UTF-8'||t.json_encoding?.malformed_utf8!=='reject'||t.json_encoding?.duplicate_object_keys!=='reject at every depth before schema validation'||t.json_encoding?.non_json_numeric_constants!=='reject'||t.json_encoding?.trailing_data!=='reject'||t.json_encoding?.top_level!=='one closed object'||
  o?.Capture?.method!=='POST'||o.Capture.path!=='/v1/capture'||o.Capture.request_ref!=='#/$defs/CaptureRequest'||
  o?.InspectCapture?.method!=='POST'||o.InspectCapture.path!=='/v1/capture/inspect'||o.InspectCapture.request_ref!=='#/$defs/CaptureRequest'||o.InspectCapture.effects!=='none; absent lookup creates no intent/record/effect'||
  JSON.stringify(o.InspectCapture.responses?.map((x:any)=>[x.http_status,x.result_statuses??null,x.provider_error??null]))!==JSON.stringify([[200,['Captured','DefinitivelyDeclined','Pending','Unknown'],null],[404,['UnknownKey'],null],[409,null,'attempt-key-conflict'],[400,null,'invalid-request'],[503,null,'provider-unavailable']])||
  JSON.stringify(o.Capture.responses?.map((x:any)=>[x.http_status,x.result_statuses??null,x.provider_error??null]))!==JSON.stringify([[200,['Captured','DefinitivelyDeclined','Pending','Unknown'],null],[400,null,'invalid-request'],[409,null,'attempt-key-conflict'],[503,null,'provider-unavailable']])||
  JSON.stringify(r?.must_equal_request)!==JSON.stringify(['attemptKey','orderId','amountMinor','currency']))bad('UnsupportedProfile');
}
function responseOf(operation:'Capture'|'InspectCapture',original:DemoPayCommerceRequestV1,response:DemoPayCommerceWireResponseV1):DemoPayCommerceObservationV1 {
 if(!response||!Number.isInteger(response.status)||!response.headers||typeof response.headers!=='object'||host.isProxy(response.headers)||
  response.headers['content-type']!==headers['content-type']||response.headers['demopay-protocol']!==headers['demopay-protocol']||!(response.body instanceof Uint8Array)||response.body.byteLength>8192)return Object.freeze({kind:'unresolved',reason:'malformed'});
 let data:unknown;try{data=parseCoreCommerceJson(decoder.decode(response.body),'DemoPay-v1 response');}catch{return Object.freeze({kind:'unresolved',reason:'malformed'});}
 if(response.status===400||response.status===409||response.status===503){
  const code=response.status===400?'invalid-request':response.status===409?'attempt-key-conflict':'provider-unavailable';
  return Object.freeze({kind:'unresolved',reason:keys(data,['kind','code'])&&data.kind==='error'&&data.code===code?code:'malformed'});
 }
 if(response.status!==200&&!(operation==='InspectCapture'&&response.status===404))return Object.freeze({kind:'unresolved',reason:'malformed'});
 let result:DemoPayCommerceResultV1;try{result=resultOf(data);}catch{return Object.freeze({kind:'unresolved',reason:'malformed'});}
 const matches=result.attemptKey===original.attemptKey&&result.orderId===original.orderId&&result.amountMinor===original.amountMinor&&result.currency===original.currency;
 if(response.status===404){if(result.status!=='UnknownKey'||!matches)return Object.freeze({kind:'unresolved',reason:'malformed'});return Object.freeze({kind:'unresolved',reason:'unknown-key'});}
 if(result.status==='UnknownKey')return Object.freeze({kind:'unresolved',reason:'malformed'});
 return Object.freeze({kind:'observed',result,matches_request:matches});
}
export interface CommerceDemoPayWireOwnerV1 {
 encodeCapture(request:DemoPayCommerceRequestV1):Uint8Array;
 parseCapture(request:DemoPayCommerceRequestV1,response:DemoPayCommerceWireResponseV1):DemoPayCommerceObservationV1;
 parseInspect(request:DemoPayCommerceRequestV1,response:DemoPayCommerceWireResponseV1):DemoPayCommerceObservationV1;
 inspect(witnesses:CommerceDemoPayIntentWitnessOwnerV1,witness:CommerceDemoPayIntentWitnessV1,deadlineMs?:number):Promise<DemoPayCommerceObservationV1>;
 assertCurrent():void;dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceDemoPayWireOwnerV1(owner:CommerceDemoPayWireOwnerV1):void {if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();}
export function createCommerceDemoPayWireOwnerV1(sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,sites:CommerceDemoPaySourceSiteOwnerV1,captureSite:CommerceDemoPaySourceSiteV1,inspectSite:CommerceDemoPaySourceSiteV1,port:DemoPayCommerceRawBytePortV1):CommerceDemoPayWireOwnerV1 {
 assertCoreCommerceSourceOwner(sources);assertCommerceDemoPaySourceSiteOwnerV1(sites);pin.assertCurrent();
 const original=sources.inspect(capture),a=sites.inspect(captureSite),b=sites.inspect(inspectSite);
 const file=original.files.find(f=>f.path==='profiles/demopay-wire.json')??bad('MissingProfile');
 if(a.method!=='Capture'||b.method!=='InspectCapture'||a.binding_path!==file.path||b.binding_path!==file.path||a.binding_sha256!==file.sha256||b.binding_sha256!==file.sha256||a.source_capture_sha256!==original.capture_sha256||b.source_capture_sha256!==original.capture_sha256||a.selected_family_sha256!==b.selected_family_sha256||a.protocol_id!=='DemoPay-v1'||b.protocol_id!=='DemoPay-v1')bad('ForeignSite');
 profileOf(parseCoreCommerceJson(file.text,file.path));
 if(!port||typeof port!=='object'||host.isProxy(port)||typeof port.exchange!=='function')bad('MissingPort');
 let disposed=false;
 const current=()=>{if(disposed)bad('DisposedOwner');pin.assertCurrent();sources.assertCurrent(capture);sites.assertCurrent();const nowA=sites.inspect(captureSite),nowB=sites.inspect(inspectSite);if(nowA.binding_sha256!==file.sha256||nowB.binding_sha256!==file.sha256||nowA.selected_family_sha256!==a.selected_family_sha256||nowB.selected_family_sha256!==b.selected_family_sha256)bad('StaleSite');};
 const encode=(request:DemoPayCommerceRequestV1)=>{current();const r=requestOf(request);const body=Buffer.from(JSON.stringify(r),'utf8');if(body.byteLength>4096)bad('RequestBound');return body;};
 const implementation:CommerceDemoPayWireOwnerV1={
  encodeCapture:encode,
  parseCapture(request,response){current();return responseOf('Capture',requestOf(request),response);},
  parseInspect(request,response){current();return responseOf('InspectCapture',requestOf(request),response);},
  async inspect(witnesses,witness,deadlineMs=5000){current();assertCommerceDemoPayIntentWitnessOwnerV1(witnesses);const seen=witnesses.inspect(witness);
   // Reconciliation also inspects Prepared attempts. UnknownKey from either
   // state remains an observation; it grants no Capture dispatch authority.
   if(seen.target!=='Shop.DemoPay.InspectCapture'||seen.site!==b.source_path||!['Prepared','Dispatched'].includes(seen.dispatch_state)||seen.source_capture_sha256!==original.capture_sha256||seen.selected_family_sha256!==b.selected_family_sha256)bad('ForeignIntent');
   if(!Number.isSafeInteger(deadlineMs)||deadlineMs<1||deadlineMs>30000)bad('InvalidDeadline');
   const request=requestOf({attemptKey:seen.request.attemptKey,orderId:seen.request.orderId,amountMinor:seen.request.amountMinor.toString(),currency:seen.request.currency});
   const controller=new AbortController(),body=encode(request);let timer:ReturnType<typeof setTimeout>|undefined,response:DemoPayCommerceWireResponseV1;
   try{response=await Promise.race([port.exchange(Object.freeze({origin:'https://demopay.invalid',method:'POST',path:'/v1/capture/inspect',headers,body,signal:controller.signal})),new Promise<never>((_,reject)=>{timer=setTimeout(()=>{controller.abort();reject(new CommerceDemoPayWireErrorV1('Timeout'));},deadlineMs);})]);}
   catch(error){current();witnesses.inspect(witness);return Object.freeze({kind:'unresolved',reason:error instanceof CommerceDemoPayWireErrorV1&&error.code==='Timeout'?'timeout':'transport'});}
   finally{if(timer)clearTimeout(timer);}
   current();witnesses.inspect(witness);return responseOf('InspectCapture',request,response);
  },assertCurrent:current,dispose(){disposed=true;},
 };const owner=Object.freeze(implementation);owners.add(owner);current();return owner;
}
