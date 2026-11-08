/** Source-bound arbitrary-byte strict UTF-8 admission, before general JSON.
 * The byte sequence is symbolic; only UTF-8 validity and a retained leading
 * BOM's immediate parser fault are translated. JSON grammar remains unsupported.
 * UTF-8 byte ranges follow https://encoding.spec.whatwg.org/#utf-8-decoder.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import type {CommerceApplicationAssemblyV1} from './commerce-application-assembly-v1.js';
import {exportCoreCommerceFormalInputAdmissionV1} from './commerce-core-formal-input-admission-v1.js';

export class CoreCommerceFormalUtf8ErrorV1 extends Error {
 constructor(readonly code:'InvalidModel') {super(code);this.name='CoreCommerceFormalUtf8ErrorV1';}
}
const invalid=():never=>{throw new CoreCommerceFormalUtf8ErrorV1('InvalidModel');};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-computation-kernel'+ext,'commerce-core-formal-input-admission-v1'+ext,
]);
const range=(value:number|undefined,lo:number,hi:number):boolean=>
 value!==undefined&&value>=lo&&value<=hi;

/** Independent concrete evaluator of the symbolic UTF-8 predicate for focused
 * parity with the platform's fatal TextDecoder. It does not parse JSON. */
export function classifyCoreCommerceStrictUtf8BytesV1(bytes:Uint8Array):Readonly<{
 valid_utf8:boolean;leading_bom:boolean;
}> {
 let i=0;
 const bom=bytes.length>=3&&bytes[0]===0xef&&bytes[1]===0xbb&&bytes[2]===0xbf;
 while(i<bytes.length){
  const b=bytes[i]!;
  if(b<=0x7f){i++;continue;}
  if(range(b,0xc2,0xdf)&&range(bytes[i+1],0x80,0xbf)){i+=2;continue;}
  const third=range(bytes[i+2],0x80,0xbf);
  if(third&&(
   b===0xe0&&range(bytes[i+1],0xa0,0xbf)||
   range(b,0xe1,0xec)&&range(bytes[i+1],0x80,0xbf)||
   b===0xed&&range(bytes[i+1],0x80,0x9f)||
   range(b,0xee,0xef)&&range(bytes[i+1],0x80,0xbf)
  )){i+=3;continue;}
  const fourth=range(bytes[i+3],0x80,0xbf);
  if(third&&fourth&&(
   b===0xf0&&range(bytes[i+1],0x90,0xbf)||
   range(b,0xf1,0xf3)&&range(bytes[i+1],0x80,0xbf)||
   b===0xf4&&range(bytes[i+1],0x80,0x8f)
  )){i+=4;continue;}
  return coreFreeze({valid_utf8:false,leading_bom:bom});
 }
 return coreFreeze({valid_utf8:true,leading_bom:bom});
}

export interface CoreCommerceFormalUtf8V1 {
 readonly schema_version:'craft.core-commerce-formal-utf8/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'symbolic-arbitrary-byte-strict-utf8-and-leading-bom-stage';
 readonly application:string;readonly selector:string;readonly service:string;
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly admission_model_sha256:string;readonly exporter_code_sha256:string;
 readonly max_input_bytes:number;readonly fuel:number;readonly byte_work_unit:32;
 readonly assumed_input:'ordinary-attached-unshared-uint8array-with-standard-textdecoder';
 readonly stage_codes:Readonly<{ready_for_json:0;InputBound:1;ResourceLimit:2;InvalidUnicode:3;InputTypeFromRetainedBom:4}>;
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly [
  'input-object-and-shared-buffer-validation','general-json-syntax-escapes-duplicates-depth-and-value',
  'typed-root-and-field-validation','expression-and-output',
  'operation-failure-action-execution','generated-native-parity','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'arbitrary-byte-fatal-utf8-validity-and-retained-leading-bom-priority-only';
}

/** Concrete interpretation of this model's pre-JSON status codes. A zero
 * status deliberately says only that the custom JSON parser must run next. */
export function evaluateCoreCommerceFormalUtf8StageV1(
 model:CoreCommerceFormalUtf8V1,bytes:Uint8Array,
):Readonly<{status:0|1|2|3|4;fuel_used:number;fault_path:''|'$.inputs'}> {
 const length=bytes.byteLength;
 if(length>model.max_input_bytes)return coreFreeze({status:1 as const,fuel_used:0,fault_path:'$.inputs' as const});
 const work=Math.ceil(length/model.byte_work_unit);
 if(work>model.fuel)return coreFreeze({status:2 as const,fuel_used:model.fuel,fault_path:'$.inputs' as const});
 const utf8=classifyCoreCommerceStrictUtf8BytesV1(bytes);
 if(!utf8.valid_utf8)return coreFreeze({status:3 as const,fuel_used:work,fault_path:'$.inputs' as const});
 if(utf8.leading_bom)return coreFreeze({status:4 as const,fuel_used:work,fault_path:'$.inputs' as const});
 return coreFreeze({status:0 as const,fuel_used:work,fault_path:'' as const});
}

export function exportCoreCommerceFormalUtf8V1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommerceFormalUtf8V1 {
 pin.assertCurrent();
 const admission=exportCoreCommerceFormalInputAdmissionV1(
  sources,capture,semantics,semantic,assembly,selector);
 const c=(i:string,lo:number,hi:number)=>`(ByteRange ${i} ${lo} ${hi})`;
 const branch=(lead:string,second:string,more:readonly string[],width:number)=>
  `(and ${lead} ${second} ${more.join(' ')} (StrictUtf8From (+ i ${width})))`;
 const b=c('i',0,127),next='(+ i 1)',third='(+ i 2)',fourth='(+ i 3)';
 const branches=[
  `(and ${b} (StrictUtf8From (+ i 1)))`,
  branch(c('i',194,223),c(next,128,191),[],2),
  branch(c('i',224,224),c(next,160,191),[c(third,128,191)],3),
  branch(c('i',225,236),c(next,128,191),[c(third,128,191)],3),
  branch(c('i',237,237),c(next,128,159),[c(third,128,191)],3),
  branch(c('i',238,239),c(next,128,191),[c(third,128,191)],3),
  branch(c('i',240,240),c(next,144,191),[c(third,128,191),c(fourth,128,191)],4),
  branch(c('i',241,243),c(next,128,191),[c(third,128,191),c(fourth,128,191)],4),
  branch(c('i',244,244),c(next,128,143),[c(third,128,191),c(fourth,128,191)],4),
 ];
 const smtlib2=[
  '(set-logic ALL)',
  `; source_capture_sha256: ${admission.source_capture_sha256}`,
  `; executable_sha256: ${admission.executable_sha256}`,
  `; family_sha256: ${admission.family_sha256}`,
  `; admission_model_sha256: ${admission.smtlib2_sha256}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  '; Symbolic bytes cover every admitted byte sequence; no JSON parser relation is asserted.',
  '; The kernel copies ordinary bytes, charges byte work, then uses fatal UTF-8 with ignoreBOM:true.',
  '; A leading UTF-8 BOM is retained and the selected JSON parser rejects it before a value.',
  '(declare-fun InputBytes () (Array Int Int))',
  '(declare-fun InputByteCount () Int)',
  '(assert (>= InputByteCount 0))',
  '(assert (forall ((i Int)) (=> (and (<= 0 i) (< i InputByteCount)) (and (<= 0 (select InputBytes i)) (<= (select InputBytes i) 255)))))',
  `(define-fun MaxInputBytes () Int ${admission.max_input_bytes})`,
  `(define-fun InitialFuel () Int ${admission.fuel})`,
  '(define-fun ByteRange ((i Int) (lo Int) (hi Int)) Bool (and (>= i 0) (< i InputByteCount) (<= lo (select InputBytes i)) (<= (select InputBytes i) hi)))',
  '(define-fun-rec StrictUtf8From ((i Int)) Bool',
  ` (ite (= i InputByteCount) true (and (< i InputByteCount) (or ${branches.join(' ')}))))`,
  '(define-fun StrictUtf8Valid () Bool (StrictUtf8From 0))',
  '(define-fun LeadingBomRetained () Bool (and (ByteRange 0 239 239) (ByteRange 1 187 187) (ByteRange 2 191 191)))',
  '(define-fun InputBound () Bool (> InputByteCount MaxInputBytes))',
  '(define-fun InitialByteWork () Int (div (+ InputByteCount 31) 32))',
  '(define-fun InitialByteWorkExhausted () Bool (> InitialByteWork InitialFuel))',
  '(define-fun Utf8StageStatus () Int (ite InputBound 1 (ite InitialByteWorkExhausted 2 (ite (not StrictUtf8Valid) 3 (ite LeadingBomRetained 4 0)))))',
  '(define-fun Utf8StageFuelUsed () Int (ite InputBound 0 (ite InitialByteWorkExhausted InitialFuel InitialByteWork)))',
  '(define-fun Utf8StageFaultPath () String (ite (= Utf8StageStatus 0) "" "$.inputs"))',
  '',
 ].join('\n');
 const result:CoreCommerceFormalUtf8V1=coreFreeze({
  schema_version:'craft.core-commerce-formal-utf8/v1-candidate' as const,
  language:'smtlib2' as const,
  scope:'symbolic-arbitrary-byte-strict-utf8-and-leading-bom-stage' as const,
  application:admission.application,selector:admission.selector,service:admission.service,
  source_capture_sha256:admission.source_capture_sha256,executable_sha256:admission.executable_sha256,
  family_sha256:admission.family_sha256,admission_model_sha256:admission.smtlib2_sha256,
  exporter_code_sha256:pin.sha256,max_input_bytes:admission.max_input_bytes,
  fuel:admission.fuel,byte_work_unit:32 as const,
  assumed_input:'ordinary-attached-unshared-uint8array-with-standard-textdecoder' as const,
  stage_codes:{ready_for_json:0 as const,InputBound:1 as const,ResourceLimit:2 as const,
   InvalidUnicode:3 as const,InputTypeFromRetainedBom:4 as const},
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['input-object-and-shared-buffer-validation',
   'general-json-syntax-escapes-duplicates-depth-and-value','typed-root-and-field-validation',
   'expression-and-output','operation-failure-action-execution','generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'arbitrary-byte-fatal-utf8-validity-and-retained-leading-bom-priority-only' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function assertCoreCommerceFormalUtf8CurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,model:CoreCommerceFormalUtf8V1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||
  model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalUtf8V1(
   sources,capture,semantics,semantic,assembly,selector)))invalid();
}
