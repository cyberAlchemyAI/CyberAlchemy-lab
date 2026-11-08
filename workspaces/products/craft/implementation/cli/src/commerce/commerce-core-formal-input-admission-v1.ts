/** Source-bound input byte/fuel admission slice for a checked pure Calculation.
 * This models the ordered threshold checks on an ordinary attached, unshared
 * Uint8Array before UTF-8 decoding. It makes no claim about the later parser,
 * value checks, expression, output, or enclosing Operation.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {parseCoreCommerceJson,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import type {CommerceApplicationAssemblyV1} from './commerce-application-assembly-v1.js';
import {exportCoreCommercePureUint64SmtV1} from './commerce-core-formal-uint64-v1.js';

export class CoreCommerceFormalInputAdmissionErrorV1 extends Error {
 constructor(readonly code:'UnsupportedAdmission'|'InvalidModel') {super(code);this.name='CoreCommerceFormalInputAdmissionErrorV1';}
}
const reject=(code:CoreCommerceFormalInputAdmissionErrorV1['code']):never=>{throw new CoreCommerceFormalInputAdmissionErrorV1(code);};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-computation-kernel'+ext,'commerce-core-formal-uint64-v1'+ext]);
const bounded=(value:unknown)=>typeof value==='number'&&Number.isSafeInteger(value)&&value>0&&value<=2147483647;

export interface CoreCommerceFormalInputAdmissionV1 {
 readonly schema_version:'craft.core-commerce-formal-input-admission/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'input-byte-length-and-initial-byte-work-fuel-threshold-before-decoding';
 readonly application:string;readonly selector:string;readonly service:string;
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly calculation_sha256:string;readonly bounds_asset_sha256:string;readonly exporter_code_sha256:string;
 readonly max_input_bytes:number;readonly fuel:number;readonly byte_work_unit:32;
 readonly assumed_input:'native-attached-nonproxy-unshared-uint8array-with-standard-builtins';
 readonly admission_codes:Readonly<{ready_for_decode:0;InputBound:1;ResourceLimit:2}>;
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['input-object-and-shared-buffer-validation','utf8-and-json-decoding','typed-input-validation','later-fuel-and-value-budgets','calculation-and-output','failure-action-dispatch','generated-native-parity','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'source-bound-byte-length-and-initial-byte-work-fuel-priority-only';
}

/** `input` checks length before the first byte-work charge. For a fresh account,
 * ceil(byteLength/32) exceeds fuel exactly when byteLength > 32*fuel. */
export function exportCoreCommerceFormalInputAdmissionV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommerceFormalInputAdmissionV1 {
 pin.assertCurrent();
 const pure=exportCoreCommercePureUint64SmtV1(sources,capture,semantics,semantic,assembly,selector);
 const captured=sources.inspect(capture),asset=captured.files.find(row=>row.path==='contracts/compute-bounds.json');
 if(!asset)throw new CoreCommerceFormalInputAdmissionErrorV1('UnsupportedAdmission');
 const parsed=parseCoreCommerceJson(asset.text,asset.path) as {computation?:{limits?:{max_input_bytes?:unknown;fuel?:unknown}}};
 const maxInput=parsed.computation?.limits?.max_input_bytes,fuel=parsed.computation?.limits?.fuel;
 if(!bounded(maxInput)||!bounded(fuel))reject('UnsupportedAdmission');
 const max_input_bytes=maxInput as number,configured_fuel=fuel as number;
 const smtlib2=[
  '(set-logic QF_LIA)',
  `; source_capture_sha256: ${pure.source_capture_sha256}`,
  `; executable_sha256: ${pure.executable_sha256}`,
  `; family_sha256: ${pure.family_sha256}`,
  `; calculation_sha256: ${pure.calculation_sha256}`,
  `; bounds_asset_sha256: ${asset.sha256}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  '; Assumes an ordinary attached, non-proxy, unshared Uint8Array and standard built-ins.',
  '; Status 1 InputBound precedes byte-work; status 2 ResourceLimit is the first byte-work charge.',
  '; Status 0 only means ready for UTF-8 decoding, not valid input or successful calculation.',
  '(declare-fun InputByteCount () Int)',
  '(assert (>= InputByteCount 0))',
  `(define-fun MaxInputBytes () Int ${max_input_bytes})`,
  `(define-fun InitialFuel () Int ${configured_fuel})`,
  '(define-fun InputBound () Bool (> InputByteCount MaxInputBytes))',
  '(define-fun InitialByteWorkExhausted () Bool (> InputByteCount (* 32 InitialFuel)))',
  '(define-fun AdmissionStatus () Int (ite InputBound 1 (ite InitialByteWorkExhausted 2 0)))',
  '',
 ].join('\n');
 const result:CoreCommerceFormalInputAdmissionV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-input-admission/v1-candidate' as const,language:'smtlib2' as const,
  scope:'input-byte-length-and-initial-byte-work-fuel-threshold-before-decoding' as const,
  application:pure.application,selector:pure.selector,service:pure.service,
  source_capture_sha256:pure.source_capture_sha256,executable_sha256:pure.executable_sha256,
  family_sha256:pure.family_sha256,calculation_sha256:pure.calculation_sha256,
  bounds_asset_sha256:asset.sha256,exporter_code_sha256:pin.sha256,
  max_input_bytes, fuel:configured_fuel,byte_work_unit:32 as const,
  assumed_input:'native-attached-nonproxy-unshared-uint8array-with-standard-builtins' as const,
  admission_codes:{ready_for_decode:0 as const,InputBound:1 as const,ResourceLimit:2 as const},
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['input-object-and-shared-buffer-validation','utf8-and-json-decoding','typed-input-validation',
   'later-fuel-and-value-budgets','calculation-and-output','failure-action-dispatch','generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'source-bound-byte-length-and-initial-byte-work-fuel-priority-only' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function assertCoreCommerceFormalInputAdmissionCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,model:CoreCommerceFormalInputAdmissionV1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalInputAdmissionV1(sources,capture,semantics,semantic,assembly,selector)))
  reject('InvalidModel');
}
