/** Bounded operational projection of the checked Core Commerce input parser.
 * It returns the first typed input fault and fuel count for an ordinary byte
 * buffer. This is a per-input interpreter, not a universal SMT JSON relation.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {coreFreeze} from './commerce-core-syntax.js';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {classifyCoreCommerceStrictUtf8BytesV1} from './commerce-core-formal-utf8-v1.js';
import {exportCoreCommerceFormalInputFieldsV1,type CoreCommerceFormalInputFieldsV1}
 from './commerce-core-formal-input-fields-v1.js';
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import type {CommerceApplicationAssemblyV1} from './commerce-application-assembly-v1.js';

export const CORE_COMMERCE_FORMAL_JSON_MAX_BYTES_V1=4096;
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-computation-kernel'+ext,'commerce-core-formal-utf8-v1'+ext,
 'commerce-core-formal-input-fields-v1'+ext,
]);
const sha=(value:Uint8Array|string)=>createHash('sha256').update(value).digest('hex');
export class CoreCommerceFormalJsonInputErrorV1 extends Error {
 constructor(readonly code:'UnsupportedTranslation'){
  super(code);this.name='CoreCommerceFormalJsonInputErrorV1';
 }
}
type FaultCode='InputType'|'InputBound'|'InvalidUnicode'|'ResourceLimit';
class Fault extends Error {
 constructor(readonly code:FaultCode,readonly path:string){super(code);}
}
const fault=(code:FaultCode,path:string):never=>{throw new Fault(code,path);};
const scalar=(value:string):boolean=>{
 for(let i=0;i<value.length;i++){
  const n=value.charCodeAt(i);
  if(n>=0xd800&&n<=0xdbff){
   const next=value.charCodeAt(++i);
   if(!(next>=0xdc00&&next<=0xdfff))return false;
  }else if(n>=0xdc00&&n<=0xdfff)return false;
 }
 return true;
};

/** Mirrors the source parser's order, including duplicate *decoded* keys,
 * invalid scalar escapes, and depth before syntax at the next value. */
export function parseCoreCommerceFormalJsonValueV1(json:string):unknown {
 let at=0;
 const bad=():never=>fault('InputType','$.inputs');
 const ws=()=>{while(/[\x20\t\r\n]/.test(json[at]??'!'))at++;};
 const string=():string=>{
  const start=at++;
  while(at<json.length){
   const ch=json[at++];
   if(ch==='"'){
    let value:string;
    try{value=JSON.parse(json.slice(start,at)) as string;}catch{return bad();}
    if(!scalar(value))fault('InvalidUnicode','$.inputs');
    return value;
   }
   if(ch==='\\')at++;
  }
  return bad();
 };
 const value=(depth:number):unknown=>{
  if(depth>32)fault('InputBound','$.inputs');
  ws();const ch=json[at];
  if(ch==='"')return string();
  if(ch==='{'){
   at++;ws();const out:Record<string,unknown>=Object.create(null);
   if(json[at]==='}'){at++;return out;}
   for(;;){
    ws();if(json[at]!=='"')return bad();
    const name=string();if(Object.hasOwn(out,name))return bad();
    ws();if(json[at++]!==':')return bad();
    out[name]=value(depth+1);ws();
    const next=json[at++];if(next==='}')return out;
    if(next!==',')return bad();
   }
  }
  if(ch==='['){
   at++;ws();const out:unknown[]=[];
   if(json[at]===']'){at++;return out;}
   for(;;){
    out.push(value(depth+1));ws();
    const next=json[at++];if(next===']')return out;
    if(next!==',')return bad();
   }
  }
  const match=/^(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/.exec(json.slice(at));
  if(!match)return bad();
  at+=match[0].length;
  return JSON.parse(match[0]) as unknown;
 };
 const result=value(0);ws();if(at!==json.length)return bad();
 return result;
}

export type CoreCommerceFormalJsonInputResultV1=Readonly<{
 scope:'ordinary-uint8array-at-most-4096-bytes-with-checked-uint64-input-fields';
 status:'ready_for_expression'|FaultCode;
 fault_path:''|string;fuel_used:number;
 values:readonly bigint[]|null;
 claim_ceiling:'bounded-per-input-parser-and-uint64-decode-observation-only';
}>;

/** The model supplies source-checked bounds and input field order. Bytes above
 * 4096 that pass earlier admission fail explicitly instead of being extrapolated. */
export function evaluateCoreCommerceFormalJsonInputV1(
 model:Pick<CoreCommerceFormalInputFieldsV1,'max_input_bytes'|'max_value_bytes'|'fuel'|'input_fields'>,
 bytes:Uint8Array,
):CoreCommerceFormalJsonInputResultV1 {
 if(!(bytes instanceof Uint8Array)||model.input_fields.length<1||
  model.max_value_bytes<22||model.input_fields.some(name=>typeof name!=='string'))
  throw new CoreCommerceFormalJsonInputErrorV1('UnsupportedTranslation');
 const scope='ordinary-uint8array-at-most-4096-bytes-with-checked-uint64-input-fields' as const;
 const claim_ceiling='bounded-per-input-parser-and-uint64-decode-observation-only' as const;
 let used=0;
 const failure=(code:FaultCode,path:string):CoreCommerceFormalJsonInputResultV1=>
  coreFreeze({scope,status:code,fault_path:path,fuel_used:used,values:null,claim_ceiling});
 if(bytes.byteLength>model.max_input_bytes)return failure('InputBound','$.inputs');
 const charge=(count:number,path:string)=>{
  if(count>model.fuel-used){used=model.fuel;fault('ResourceLimit',path);}
  used+=count;
 };
 try{
  charge(Math.ceil(bytes.byteLength/32),'$.inputs');
  if(bytes.byteLength>CORE_COMMERCE_FORMAL_JSON_MAX_BYTES_V1)
   throw new CoreCommerceFormalJsonInputErrorV1('UnsupportedTranslation');
  if(!classifyCoreCommerceStrictUtf8BytesV1(bytes).valid_utf8)fault('InvalidUnicode','$.inputs');
  let json:string;
  try{json=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(bytes);}
  catch{fault('InvalidUnicode','$.inputs');}
  const raw=parseCoreCommerceFormalJsonValueV1(json!);
  if(!raw||typeof raw!=='object'||Array.isArray(raw))fault('InputType','$.inputs');
  const fields=raw as Record<string,unknown>;
  const names=Object.keys(fields);
  if(names.length!==model.input_fields.length||
   model.input_fields.some(name=>!Object.hasOwn(fields,name)))fault('InputType','$.inputs');
  const values:bigint[]=[];
  for(const name of model.input_fields){
   const path='$.inputs.'+name,wire=fields[name];
   charge(1,path);
   if(typeof wire!=='string')fault('InputType',path);
   const textWire=wire as string;
   if(textWire.length>20||!/^(0|[1-9][0-9]*)$/.test(textWire))fault('InputType',path);
   const value=BigInt(textWire);
   if(value>18446744073709551615n)fault('InputBound',path);
   charge(1,path);charge(1,path);
   values.push(value);
  }
  return coreFreeze({scope,status:'ready_for_expression' as const,fault_path:'' as const,
   fuel_used:used,values,claim_ceiling});
 }catch(error){
  if(error instanceof CoreCommerceFormalJsonInputErrorV1)throw error;
  if(error instanceof Fault)return failure(error.code,error.path);
  throw error;
 }
}

export interface CoreCommerceFormalJsonInputWitnessV1 {
 readonly schema_version:'craft.core-commerce-formal-json-input-witness/v1-candidate';
 readonly language:'smtlib2';readonly scope:'one-source-bound-concrete-input-at-most-4096-bytes';
 readonly application:string;readonly selector:string;readonly service:string;
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly fields_model_sha256:string;readonly exporter_code_sha256:string;
 readonly input_bytes_hex:string;readonly input_bytes_sha256:string;
 readonly result:CoreCommerceFormalJsonInputResultV1;
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['universal-byte-to-json-relation','input-object-and-shared-buffer-validation',
  'admitted-buffers-above-4096-bytes','expression-and-output','operation-and-native-effect-equivalence','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'grounded-per-input-parser-and-uint64-decode-witness-only';
}

/** SMT facts bind the *concrete* bytes and observed result. They do not encode
 * the parser algorithm as constraints for arbitrary symbolic byte arrays. */
export function exportCoreCommerceFormalJsonInputWitnessV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,bytes:Uint8Array,
):CoreCommerceFormalJsonInputWitnessV1 {
 pin.assertCurrent();
 const fields=exportCoreCommerceFormalInputFieldsV1(sources,capture,semantics,semantic,assembly,selector);
 const byteCopy=Uint8Array.from(bytes);
 const result=evaluateCoreCommerceFormalJsonInputV1(fields,byteCopy);
 const hex=Buffer.from(byteCopy).toString('hex');
 const code={ready_for_expression:0,InputType:1,InputBound:2,InvalidUnicode:3,ResourceLimit:4}[result.status];
 const lines=[
  '(set-logic ALL)',
  `; source_capture_sha256: ${fields.source_capture_sha256}`,
  `; executable_sha256: ${fields.executable_sha256}`,
  `; family_sha256: ${fields.family_sha256}`,
  `; fields_model_sha256: ${fields.smtlib2_sha256}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  `; concrete_input_bytes_sha256: ${sha(byteCopy)}`,
  '; Ground facts for one checked byte input; no universal parser relation or solver proof.',
  `(define-fun InputByteCount () Int ${byteCopy.length})`,
  '(declare-fun InputBytes () (Array Int Int))',
  ...[...byteCopy].map((byte,i)=>`(assert (= (select InputBytes ${i}) ${byte}))`),
  `(define-fun InputStatus () Int ${code})`,
  `(define-fun InputFuelUsed () Int ${result.fuel_used})`,
  `(define-fun InputFaultPath () String ${JSON.stringify(result.fault_path)})`,
  ...(result.values??[]).map((value,i)=>`(define-fun Input${i}Value () Int ${value})`),
  '',
 ];
 const smtlib2=lines.join('\n');
 const witness=coreFreeze({
  schema_version:'craft.core-commerce-formal-json-input-witness/v1-candidate' as const,
  language:'smtlib2' as const,scope:'one-source-bound-concrete-input-at-most-4096-bytes' as const,
  application:fields.application,selector:fields.selector,service:fields.service,
  source_capture_sha256:fields.source_capture_sha256,executable_sha256:fields.executable_sha256,
  family_sha256:fields.family_sha256,fields_model_sha256:fields.smtlib2_sha256,
  exporter_code_sha256:pin.sha256,input_bytes_hex:hex,input_bytes_sha256:sha(byteCopy),
  result,smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['universal-byte-to-json-relation','input-object-and-shared-buffer-validation',
   'admitted-buffers-above-4096-bytes','expression-and-output','operation-and-native-effect-equivalence',
   'solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'grounded-per-input-parser-and-uint64-decode-witness-only' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return witness;
}
