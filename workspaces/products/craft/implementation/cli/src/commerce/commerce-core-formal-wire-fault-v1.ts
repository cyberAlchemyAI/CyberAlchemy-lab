/** Two constructive parser faults with exact byte-budget/error priority.
 * These are source-bound families, not a translation of all UTF-8 or JSON.
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
import {exportCoreCommerceFormalAsciiWireV1,encodeCoreCommerceFormalAsciiWireV1,type CoreCommerceFormalAsciiWireV1}
 from './commerce-core-formal-ascii-wire-v1.js';
import {exportCoreCommerceFormalInputAdmissionV1} from './commerce-core-formal-input-admission-v1.js';

export type CoreCommerceFormalWireFaultKindV1='invalid-utf8-trailer'|'invalid-json-trailer';
export class CoreCommerceFormalWireFaultErrorV1 extends Error {
 constructor(readonly code:'UnsupportedFault'|'InvalidModel'){super(code);this.name='CoreCommerceFormalWireFaultErrorV1';}
}
const fail=(code:CoreCommerceFormalWireFaultErrorV1['code']):never=>{throw new CoreCommerceFormalWireFaultErrorV1(code);};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const quote=(value:string)=>`"${value.replaceAll('"','""')}"`;
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-computation-kernel'+ext,'commerce-core-formal-ascii-wire-v1'+ext,'commerce-core-formal-input-admission-v1'+ext,
]);

export interface CoreCommerceFormalWireFaultV1 {
 readonly schema_version:'craft.core-commerce-formal-wire-fault/v1-candidate';
 readonly language:'smtlib2';readonly fault:CoreCommerceFormalWireFaultKindV1;
 readonly scope:'source-ordered-ascii-json-with-one-fixed-invalid-trailer';
 readonly application:string;readonly selector:string;readonly service:string;readonly input_fields:readonly string[];
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly calculation_sha256:string;readonly bounds_asset_sha256:string;readonly exporter_code_sha256:string;
 readonly max_input_bytes:number;readonly fuel:number;readonly post_admission_error:'InvalidUnicode'|'InputType';
 readonly assumed_bytes:'exact-ascii-utf8-base-object-followed-by-one-ff-or-bang-byte';
 readonly status_codes:Readonly<{input_bound:1;initial_fuel_limit:2;post_admission_fault:3}>;
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['general-invalid-utf8-and-json','arbitrary-json-escapes-and-key-order','raw-byte-array-theory','expression-and-operation-execution','generated-native-parity','solver-proof'];
 readonly authority_effect:'none';readonly claim_ceiling:'fixed-trailer-family-with-source-ordered-input-bound-fuel-and-parser-fault-priority-only';
}

export function exportCoreCommerceFormalWireFaultV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,fault:CoreCommerceFormalWireFaultKindV1,
):CoreCommerceFormalWireFaultV1 {
 pin.assertCurrent();
 if(fault!=='invalid-utf8-trailer'&&fault!=='invalid-json-trailer')fail('UnsupportedFault');
 const ascii=exportCoreCommerceFormalAsciiWireV1(sources,capture,semantics,semantic,assembly,selector);
 const admission=exportCoreCommerceFormalInputAdmissionV1(sources,capture,semantics,semantic,assembly,selector);
 if(ascii.source_capture_sha256!==admission.source_capture_sha256||
  ascii.calculation_sha256!==admission.calculation_sha256)fail('InvalidModel');
 const pieces:string[]=[];
 for(let i=0;i<ascii.input_fields.length;i++)pieces.push(quote((i===0?'{':',')+JSON.stringify(ascii.input_fields[i])+':"'),`WireValue${i}`);
 pieces.push(quote('"}'));
 const post_admission_error=fault==='invalid-utf8-trailer'?'InvalidUnicode':'InputType';
 const lines=[
  '(set-logic QF_SLIA)',
  `; source_capture_sha256: ${ascii.source_capture_sha256}`,
  `; executable_sha256: ${ascii.executable_sha256}`,
  `; family_sha256: ${ascii.family_sha256}`,
  `; calculation_sha256: ${ascii.calculation_sha256}`,
  `; bounds_asset_sha256: ${ascii.bounds_asset_sha256}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  `; Fault: ${fault}; expected post-admission code: ${post_admission_error}.`,
  '; Assumes exact ASCII UTF-8 of BaseWire plus one 0xFF or 0x21 trailer byte.',
  '; Byte bound precedes initial byte-work fuel; fatal UTF-8 precedes JSON parsing.',
  ...ascii.input_fields.flatMap((field,i)=>[
   `; WireValue${i}: ${field}`,
   `(declare-fun WireValue${i} () String)`,
   `(assert (str.in_re WireValue${i} (re.* (re.union (re.range "a" "z") (re.range "0" "9")))))`,
  ]),
  `(define-fun BaseWire () String (str.++ ${pieces.join(' ')}))`,
  '(define-fun InputByteCount () Int (+ (str.len BaseWire) 1))',
  `(define-fun MaxInputBytes () Int ${admission.max_input_bytes})`,
  '(assert (<= (str.len BaseWire) MaxInputBytes))',
  `(define-fun InitialFuel () Int ${admission.fuel})`,
  '(define-fun InputBound () Bool (> InputByteCount MaxInputBytes))',
  '(define-fun InitialByteWorkExhausted () Bool (> InputByteCount (* 32 InitialFuel)))',
  '(define-fun FaultStatus () Int (ite InputBound 1 (ite InitialByteWorkExhausted 2 3)))',
  '(define-fun FuelUsedAtFault () Int (ite InputBound 0 (ite InitialByteWorkExhausted InitialFuel (div (+ InputByteCount 31) 32))))',
  '',
 ];
 const smtlib2=lines.join('\n');
 const result:CoreCommerceFormalWireFaultV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-wire-fault/v1-candidate' as const,language:'smtlib2' as const,fault,
  scope:'source-ordered-ascii-json-with-one-fixed-invalid-trailer' as const,
  application:ascii.application,selector:ascii.selector,service:ascii.service,input_fields:ascii.input_fields,
  source_capture_sha256:ascii.source_capture_sha256,executable_sha256:ascii.executable_sha256,
  family_sha256:ascii.family_sha256,calculation_sha256:ascii.calculation_sha256,
  bounds_asset_sha256:ascii.bounds_asset_sha256,exporter_code_sha256:pin.sha256,
  max_input_bytes:admission.max_input_bytes,fuel:admission.fuel,post_admission_error,
  assumed_bytes:'exact-ascii-utf8-base-object-followed-by-one-ff-or-bang-byte' as const,
  status_codes:{input_bound:1 as const,initial_fuel_limit:2 as const,post_admission_fault:3 as const},
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['general-invalid-utf8-and-json','arbitrary-json-escapes-and-key-order',
   'raw-byte-array-theory','expression-and-operation-execution','generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'fixed-trailer-family-with-source-ordered-input-bound-fuel-and-parser-fault-priority-only' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function encodeCoreCommerceFormalWireFaultV1(
 ascii:CoreCommerceFormalAsciiWireV1,values:readonly string[],fault:CoreCommerceFormalWireFaultKindV1,
):Uint8Array {
 if(fault!=='invalid-utf8-trailer'&&fault!=='invalid-json-trailer')fail('UnsupportedFault');
 const base=encodeCoreCommerceFormalAsciiWireV1(ascii,values),bytes=new Uint8Array(base.length+1);
 bytes.set(base);bytes[base.length]=fault==='invalid-utf8-trailer'?0xff:0x21;
 return bytes;
}

export function assertCoreCommerceFormalWireFaultCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,fault:CoreCommerceFormalWireFaultKindV1,
 model:CoreCommerceFormalWireFaultV1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalWireFaultV1(sources,capture,semantics,semantic,assembly,selector,fault)))fail('InvalidModel');
}
