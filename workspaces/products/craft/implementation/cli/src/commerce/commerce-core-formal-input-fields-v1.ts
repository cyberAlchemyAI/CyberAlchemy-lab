/** Exact source-bound scalar wire/checkpoint slice after successful JSON parse.
 * The parser-to-observation relation remains outside this projection.
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
import {exportCoreCommerceFormalInputAdmissionV1} from './commerce-core-formal-input-admission-v1.js';

export class CoreCommerceFormalInputFieldsErrorV1 extends Error {
 constructor(readonly code:'UnsupportedBudget'|'InvalidModel'){super(code);this.name='CoreCommerceFormalInputFieldsErrorV1';}
}
const reject=(code:CoreCommerceFormalInputFieldsErrorV1['code']):never=>{throw new CoreCommerceFormalInputFieldsErrorV1(code);};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-computation-kernel'+ext,'commerce-core-formal-uint64-v1'+ext,'commerce-core-formal-input-admission-v1'+ext,
]);
const MAX='18446744073709551615';
const bounded=(value:unknown)=>typeof value==='number'&&Number.isSafeInteger(value)&&value>0&&value<=2147483647;

export interface CoreCommerceFormalInputFieldsV1 {
 readonly schema_version:'craft.core-commerce-formal-input-fields/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'closed-parsed-root-and-all-uint64-input-wire-decodes-through-scalar-checkpoints';
 readonly application:string;readonly selector:string;readonly service:string;readonly input_fields:readonly string[];
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly calculation_sha256:string;readonly bounds_asset_sha256:string;readonly exporter_code_sha256:string;
 readonly max_input_bytes:number;readonly max_value_bytes:number;readonly fuel:number;
 readonly worst_admitted_input_byte_work:number;readonly scalar_checkpoint_fuel_per_field:3;
 readonly remaining_fuel_after_all_input_checkpoints_at_max_wire_size:number;
 readonly assumed_input:'admitted-ordinary-uint8array-with-successful-utf8-json-parse-and-honest-parsed-observations';
 readonly status_codes:Readonly<{ready_for_expression:0;closed_input_type:1;field_wire_input_type:2;field_uint64_input_bound:3}>;
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['utf8-and-json-parser-translation','parsed-observation-extraction','expression-and-output-validation','operation-failure-action-execution','generated-native-parity','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'checked-all-uint64-input-wire-and-scalar-checkpoint-priority-with-source-bounded-fuel-margin-only';
}

/** A checked UInt64 scalar checkpoint costs one decode charge, one validate
 * charge, and one byte-work charge for its 3..22 byte quoted decimal. The
 * model rejects bounds that cannot guarantee these charges for every field. */
export function exportCoreCommerceFormalInputFieldsV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommerceFormalInputFieldsV1 {
 pin.assertCurrent();
 const pure=exportCoreCommercePureUint64SmtV1(sources,capture,semantics,semantic,assembly,selector);
 const admission=exportCoreCommerceFormalInputAdmissionV1(sources,capture,semantics,semantic,assembly,selector);
 const source=sources.inspect(capture),asset=source.files.find(row=>row.path==='contracts/compute-bounds.json');
 if(!asset)throw new CoreCommerceFormalInputFieldsErrorV1('InvalidModel');
 if(asset.sha256!==admission.bounds_asset_sha256||
  pure.source_capture_sha256!==admission.source_capture_sha256||
  pure.calculation_sha256!==admission.calculation_sha256)reject('InvalidModel');
 const parsed=parseCoreCommerceJson(asset.text,asset.path) as {computation?:{limits?:{max_value_bytes?:unknown}}};
 const valueMax=parsed.computation?.limits?.max_value_bytes;
 if(!bounded(valueMax))reject('UnsupportedBudget');
 const max_value_bytes=valueMax as number,fields=pure.inputs.map(row=>row.name),worst=Math.ceil(admission.max_input_bytes/32);
 if(fields.length<1||fields.length>8||max_value_bytes<22||worst+3*fields.length>admission.fuel)reject('UnsupportedBudget');
 const lines=[
  '(set-logic QF_SLIA)',
  `; source_capture_sha256: ${pure.source_capture_sha256}`,
  `; executable_sha256: ${pure.executable_sha256}`,
  `; family_sha256: ${pure.family_sha256}`,
  `; calculation_sha256: ${pure.calculation_sha256}`,
  `; bounds_asset_sha256: ${asset.sha256}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  '; Precondition: ordinary admitted bytes, successful strict UTF-8 and JSON parse.',
  '; ParsedRootObject, InputHas, AdditionalKeyCount, IsString and Wire are unproven parsed-value observations.',
  '; Source bounds guarantee all scalar checkpoint fuel charges and quoted decimal value sizes.',
  '; Status 0 means ready for expression only; it says nothing about expression or output success.',
  '(declare-fun InputByteCount () Int)',
  `(define-fun MaxInputBytes () Int ${admission.max_input_bytes})`,
  `(define-fun InitialFuel () Int ${admission.fuel})`,
  `(define-fun MaxValueBytes () Int ${max_value_bytes})`,
  '(assert (and (>= InputByteCount 0) (<= InputByteCount MaxInputBytes) (<= InputByteCount (* 32 InitialFuel))))',
  '(define-fun InitialByteWork () Int (div (+ InputByteCount 31) 32))',
  '(declare-fun ParsedRootObject () Bool)',
  ...fields.map((_,i)=>`(declare-fun InputHas${i} () Bool)`),
  '(declare-fun AdditionalKeyCount () Int)',
  '(assert (>= AdditionalKeyCount 0))',
  `(define-fun ClosedInput () Bool (and ParsedRootObject ${fields.map((_,i)=>`InputHas${i}`).join(' ')} (= AdditionalKeyCount 0)))`,
 ];
 for(let i=0;i<fields.length;i++)lines.push(
  `; Field ${i}: ${fields[i]}`,
  `(declare-fun Field${i}IsString () Bool)`,
  `(declare-fun Field${i}Wire () String)`,
  `(define-fun Field${i}Canonical () Bool (and Field${i}IsString (<= (str.len Field${i}Wire) 20) (str.in_re Field${i}Wire (re.union (str.to_re "0") (re.++ (re.range "1" "9") (re.* (re.range "0" "9")))))))`,
  `(define-fun Field${i}Value () Int (str.to_int Field${i}Wire))`,
  `(define-fun Field${i}Status () Int (ite (not Field${i}Canonical) 2 (ite (> Field${i}Value ${MAX}) 3 0)))`,
 );
 let status='0',used=`(+ InitialByteWork ${3*fields.length})`;
 for(let i=fields.length-1;i>=0;i--){
  status=`(ite (not (= Field${i}Status 0)) Field${i}Status ${status})`;
  used=`(ite (not (= Field${i}Status 0)) (+ InitialByteWork ${3*i+1}) ${used})`;
 }
 lines.push(
  `(define-fun InputStatus () Int (ite (not ClosedInput) 1 ${status}))`,
  `(define-fun FuelUsedAtInputBoundary () Int (ite (not ClosedInput) InitialByteWork ${used}))`,
  `(assert (<= (+ (div (+ MaxInputBytes 31) 32) ${3*fields.length}) InitialFuel))`,
  '(assert (>= MaxValueBytes 22))','',
 );
 const smtlib2=lines.join('\n');
 const result:CoreCommerceFormalInputFieldsV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-input-fields/v1-candidate' as const,language:'smtlib2' as const,
  scope:'closed-parsed-root-and-all-uint64-input-wire-decodes-through-scalar-checkpoints' as const,
  application:pure.application,selector:pure.selector,service:pure.service,input_fields:fields,
  source_capture_sha256:pure.source_capture_sha256,executable_sha256:pure.executable_sha256,
  family_sha256:pure.family_sha256,calculation_sha256:pure.calculation_sha256,
  bounds_asset_sha256:asset.sha256,exporter_code_sha256:pin.sha256,
  max_input_bytes:admission.max_input_bytes,max_value_bytes,fuel:admission.fuel,
  worst_admitted_input_byte_work:worst,scalar_checkpoint_fuel_per_field:3 as const,
  remaining_fuel_after_all_input_checkpoints_at_max_wire_size:admission.fuel-worst-3*fields.length,
  assumed_input:'admitted-ordinary-uint8array-with-successful-utf8-json-parse-and-honest-parsed-observations' as const,
  status_codes:{ready_for_expression:0 as const,closed_input_type:1 as const,field_wire_input_type:2 as const,field_uint64_input_bound:3 as const},
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['utf8-and-json-parser-translation','parsed-observation-extraction','expression-and-output-validation',
   'operation-failure-action-execution','generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'checked-all-uint64-input-wire-and-scalar-checkpoint-priority-with-source-bounded-fuel-margin-only' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function assertCoreCommerceFormalInputFieldsCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,model:CoreCommerceFormalInputFieldsV1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalInputFieldsV1(sources,capture,semantics,semantic,assembly,selector)))reject('InvalidModel');
}

/** The kernel's ordered input pipeline after ordinary-byte admission. UTF-8
 * validity and the parser's first outcome are observations, not byte-level
 * translations. The parser outcome is 0 success, 1 malformed/duplicate JSON,
 * 2 invalid scalar string, or 3 nesting beyond its checked depth bound. */
export interface CoreCommerceFormalInputPipelineV1 {
 readonly schema_version:'craft.core-commerce-formal-input-pipeline/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'post-admission-utf8-parser-closed-root-and-uint64-field-failure-priority';
 readonly application:string;readonly selector:string;readonly service:string;
 readonly source_capture_sha256:string;readonly input_fields_model_sha256:string;
 readonly exporter_code_sha256:string;readonly input_fields:readonly string[];
 readonly assumed_input:'ordinary-admitted-byte-buffer-with-honest-utf8-and-parser-outcome-observations';
 readonly parser_observation_codes:Readonly<{parsed:0;InputType:1;InvalidUnicode:2;InputBound:3}>;
 readonly pipeline_status_codes:Readonly<{ready_for_expression:0;InvalidUnicode:1;InputType:2;InputBound:3}>;
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['byte-to-utf8-and-json-parser-relation','input-object-and-shared-buffer-validation','expression-and-output','operation-failure-action-execution','generated-native-parity','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'conditional-checked-post-admission-parser-outcome-and-field-failure-priority-only';
}

export function exportCoreCommerceFormalInputPipelineV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommerceFormalInputPipelineV1 {
 pin.assertCurrent();
 const fields=exportCoreCommerceFormalInputFieldsV1(sources,capture,semantics,semantic,assembly,selector);
 let fieldPath='""';
 for(let i=fields.input_fields.length-1;i>=0;i--)
  fieldPath=`(ite (not (= Field${i}Status 0)) ${JSON.stringify('$.inputs.'+fields.input_fields[i])} ${fieldPath})`;
 const smtlib2=fields.smtlib2+[
  '; The following stage order is checked against the pinned computation kernel.',
  '; Utf8Valid and ParserOutcome are honest observations, not computed from InputByteCount.',
  '; ParserOutcome is the first actual parser fault; syntax/duplicate keys, invalid scalar, and depth may interleave.',
  '; PipelineStatus 0 means ready for expression only. The input object and native execution are not represented.',
  '(declare-fun Utf8Valid () Bool)',
  '(declare-fun ParserOutcome () Int)',
  '(assert (and (>= ParserOutcome 0) (<= ParserOutcome 3)))',
  '(define-fun PipelineStatus () Int (ite (not Utf8Valid) 1 (ite (= ParserOutcome 2) 1 (ite (= ParserOutcome 1) 2 (ite (= ParserOutcome 3) 3 (ite (= InputStatus 3) 3 (ite (= InputStatus 0) 0 2)))))))',
  '(define-fun PipelineFuelUsed () Int (ite (or (not Utf8Valid) (not (= ParserOutcome 0))) InitialByteWork FuelUsedAtInputBoundary))',
  `(define-fun FieldFaultPath () String (ite (not ClosedInput) "$.inputs" ${fieldPath}))`,
  '(define-fun PipelineFaultPath () String (ite (or (not Utf8Valid) (not (= ParserOutcome 0))) "$.inputs" (ite (= InputStatus 0) "" FieldFaultPath)))',
  '',
 ].join('\n');
 const result:CoreCommerceFormalInputPipelineV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-input-pipeline/v1-candidate' as const,
  language:'smtlib2' as const,
  scope:'post-admission-utf8-parser-closed-root-and-uint64-field-failure-priority' as const,
  application:fields.application,selector:fields.selector,service:fields.service,
  source_capture_sha256:fields.source_capture_sha256,input_fields_model_sha256:fields.smtlib2_sha256,
  exporter_code_sha256:pin.sha256,input_fields:fields.input_fields,
  assumed_input:'ordinary-admitted-byte-buffer-with-honest-utf8-and-parser-outcome-observations' as const,
  parser_observation_codes:{parsed:0 as const,InputType:1 as const,InvalidUnicode:2 as const,InputBound:3 as const},
  pipeline_status_codes:{ready_for_expression:0 as const,InvalidUnicode:1 as const,InputType:2 as const,InputBound:3 as const},
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['byte-to-utf8-and-json-parser-relation','input-object-and-shared-buffer-validation',
   'expression-and-output','operation-failure-action-execution','generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'conditional-checked-post-admission-parser-outcome-and-field-failure-priority-only' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function assertCoreCommerceFormalInputPipelineCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,model:CoreCommerceFormalInputPipelineV1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||
  model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalInputPipelineV1(
   sources,capture,semantics,semantic,assembly,selector)))reject('InvalidModel');
}
