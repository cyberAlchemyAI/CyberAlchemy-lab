/** Source-bound post-parse projection through the first UInt64 wire decode.
 * Parsed-object and first-value observations are inputs to this model: it does
 * not translate UTF-8 decoding or JSON parsing into SMT strings.
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
import {exportCoreCommercePureUint64SmtV1} from './commerce-core-formal-uint64-v1.js';
import {exportCoreCommerceFormalInputAdmissionV1} from './commerce-core-formal-input-admission-v1.js';

const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-computation-kernel'+ext,'commerce-core-formal-uint64-v1'+ext,'commerce-core-formal-input-admission-v1'+ext,
]);
const reject=():never=>{throw new Error('InvalidModel: exact source-bound first-field projection required');};

export interface CoreCommerceFormalFirstFieldV1 {
 readonly schema_version:'craft.core-commerce-formal-first-field/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'parsed-root-closed-fields-and-first-uint64-wire-decode-before-checkpoint';
 readonly application:string;readonly selector:string;readonly service:string;
 readonly first_field:string;readonly input_fields:readonly string[];
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly calculation_sha256:string;readonly bounds_asset_sha256:string;readonly exporter_code_sha256:string;
 readonly max_input_bytes:number;readonly fuel:number;
 readonly assumed_input:'admitted-ordinary-uint8array-with-successful-utf8-json-parse-and-honest-parsed-observations';
 readonly status_codes:Readonly<{ready_for_checkpoint:0;closed_input_type:1;first_decode_fuel_limit:2;first_wire_input_type:3;first_uint64_input_bound:4}>;
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['utf8-and-json-parser-translation','parsed-observation-extraction','first-checkpoint-and-remaining-fields','later-value-and-output-budgets','calculation-and-operation-execution','generated-native-parity','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'checked-parsed-root-key-closure-and-first-uint64-pre-checkpoint-priority-only';
}

/** The checked kernel closes the parsed root before any scalar decode. Each
 * scalar decode charges one fuel unit before its wire-type and UInt64 checks. */
export function exportCoreCommerceFormalFirstFieldV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommerceFormalFirstFieldV1 {
 pin.assertCurrent();
 const pure=exportCoreCommercePureUint64SmtV1(sources,capture,semantics,semantic,assembly,selector);
 const admission=exportCoreCommerceFormalInputAdmissionV1(sources,capture,semantics,semantic,assembly,selector);
 if(pure.inputs.length<1||pure.inputs.length>8||
  admission.source_capture_sha256!==pure.source_capture_sha256||admission.calculation_sha256!==pure.calculation_sha256)reject();
 const first_field=pure.inputs[0]!.name,input_fields=pure.inputs.map(row=>row.name);
 const present=input_fields.map((_,i)=>`InputHas${i}`),declarations=present.map(name=>`(declare-fun ${name} () Bool)`);
 const closed=`(and ParsedRootObject ${present.join(' ')} (= AdditionalKeyCount 0))`;
 const smtlib2=[
  '(set-logic QF_SLIA)',
  `; source_capture_sha256: ${pure.source_capture_sha256}`,
  `; executable_sha256: ${pure.executable_sha256}`,
  `; family_sha256: ${pure.family_sha256}`,
  `; calculation_sha256: ${pure.calculation_sha256}`,
  `; bounds_asset_sha256: ${admission.bounds_asset_sha256}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  `; First field: ${first_field}; parser observations must describe the actual parsed JSON value.`,
  '; Precondition: admitted ordinary bytes, successful fatal UTF-8 decode and JSON parse.',
  '; Status 0 means ready for the first checkpoint, not a successful calculation.',
  '(declare-fun InputByteCount () Int)',
  `(define-fun MaxInputBytes () Int ${admission.max_input_bytes})`,
  `(define-fun InitialFuel () Int ${admission.fuel})`,
  '(assert (and (>= InputByteCount 0) (<= InputByteCount MaxInputBytes) (<= InputByteCount (* 32 InitialFuel))))',
  '(define-fun InitialByteWork () Int (div (+ InputByteCount 31) 32))',
  '(declare-fun ParsedRootObject () Bool)',
  ...declarations,
  '(declare-fun AdditionalKeyCount () Int)',
  '(assert (>= AdditionalKeyCount 0))',
  `(define-fun ClosedInput () Bool ${closed})`,
  '(declare-fun FirstIsString () Bool)',
  '(declare-fun FirstWire () String)',
  '(define-fun CanonicalDecimal () Bool (and FirstIsString (<= (str.len FirstWire) 20) (str.in_re FirstWire (re.union (str.to_re "0") (re.++ (re.range "1" "9") (re.* (re.range "0" "9")))))))',
  '(define-fun FirstUInt64Value () Int (str.to_int FirstWire))',
  '(define-fun FirstFieldStatus () Int (ite (not ClosedInput) 1 (ite (>= InitialByteWork InitialFuel) 2 (ite (not CanonicalDecimal) 3 (ite (> FirstUInt64Value 18446744073709551615) 4 0)))))',
  '(define-fun FuelUsedAtFirstFieldBoundary () Int (ite (not ClosedInput) InitialByteWork (ite (>= InitialByteWork InitialFuel) InitialFuel (+ InitialByteWork 1))))',
  '',
 ].join('\n');
 const result:CoreCommerceFormalFirstFieldV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-first-field/v1-candidate' as const,language:'smtlib2' as const,
  scope:'parsed-root-closed-fields-and-first-uint64-wire-decode-before-checkpoint' as const,
  application:pure.application,selector:pure.selector,service:pure.service,first_field,input_fields,
  source_capture_sha256:pure.source_capture_sha256,executable_sha256:pure.executable_sha256,
  family_sha256:pure.family_sha256,calculation_sha256:pure.calculation_sha256,
  bounds_asset_sha256:admission.bounds_asset_sha256,exporter_code_sha256:pin.sha256,
  max_input_bytes:admission.max_input_bytes,fuel:admission.fuel,
  assumed_input:'admitted-ordinary-uint8array-with-successful-utf8-json-parse-and-honest-parsed-observations' as const,
  status_codes:{ready_for_checkpoint:0 as const,closed_input_type:1 as const,first_decode_fuel_limit:2 as const,first_wire_input_type:3 as const,first_uint64_input_bound:4 as const},
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['utf8-and-json-parser-translation','parsed-observation-extraction','first-checkpoint-and-remaining-fields',
   'later-value-and-output-budgets','calculation-and-operation-execution','generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'checked-parsed-root-key-closure-and-first-uint64-pre-checkpoint-priority-only' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function assertCoreCommerceFormalFirstFieldCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,model:CoreCommerceFormalFirstFieldV1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalFirstFieldV1(sources,capture,semantics,semantic,assembly,selector)))reject();
}
