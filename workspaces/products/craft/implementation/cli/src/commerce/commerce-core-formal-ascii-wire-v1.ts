/** Exact restricted ASCII JSON envelope for a source-bound UInt64 input model.
 * The emitted SMT binds declared parsed observations to one generated wire
 * family; arbitrary JSON, escapes, key order and non-ASCII remain unsupported.
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
import {exportCoreCommerceFormalInputFieldsV1,type CoreCommerceFormalInputFieldsV1} from './commerce-core-formal-input-fields-v1.js';

export class CoreCommerceFormalAsciiWireErrorV1 extends Error {
 constructor(readonly code:'UnsupportedEnvelope'|'InvalidWireValue'|'InvalidModel'){
  super(code);this.name='CoreCommerceFormalAsciiWireErrorV1';
 }
}
const fail=(code:CoreCommerceFormalAsciiWireErrorV1['code']):never=>{throw new CoreCommerceFormalAsciiWireErrorV1(code);};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-computation-kernel'+ext,'commerce-core-formal-input-fields-v1'+ext]);
const smtString=(value:string)=>`"${value.replaceAll('"','""')}"`;
const names=(fields:readonly string[])=>fields.length>0&&fields.length<=8&&
 fields.every(name=>/^[A-Za-z_][A-Za-z0-9_]*$/.test(name))&&new Set(fields).size===fields.length;

export interface CoreCommerceFormalAsciiWireV1 {
 readonly schema_version:'craft.core-commerce-formal-ascii-wire/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'source-ordered-closed-json-object-with-quoted-lowercase-ascii-alphanumeric-values';
 readonly application:string;readonly selector:string;readonly service:string;readonly input_fields:readonly string[];
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly calculation_sha256:string;readonly bounds_asset_sha256:string;readonly exporter_code_sha256:string;
 readonly input_fields_model_sha256:string;readonly max_input_bytes:number;
 readonly assumed_bytes:'exact-ascii-utf8-encoding-of-the-declared-input-wire';
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['arbitrary-json-syntax-or-key-order','json-string-escapes-and-unicode','raw-byte-array-theory-and-utf8-proof','expression-and-output-validation','operation-failure-action-execution','generated-native-parity','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'fixed-source-ordered-ascii-json-envelope-bound-to-all-uint64-input-observations-only';
}

/** A quote-free lowercase ASCII value can never alter JSON structure. Every
 * generated member is unique, so the checked parser yields the exact object
 * and strings represented by the all-fields model. */
export function exportCoreCommerceFormalAsciiWireV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommerceFormalAsciiWireV1 {
 pin.assertCurrent();
 const fields=exportCoreCommerceFormalInputFieldsV1(sources,capture,semantics,semantic,assembly,selector);
 if(!names(fields.input_fields))fail('UnsupportedEnvelope');
 const inputPieces:string[]=[];
 for(let i=0;i<fields.input_fields.length;i++){
  const before=(i===0?'{':',')+JSON.stringify(fields.input_fields[i])+':"';
  inputPieces.push(smtString(before),`WireValue${i}`);
 }
 inputPieces.push(smtString('"}'));
 const tail=[
  '; Restricted parser bridge: exact ASCII UTF-8 bytes of InputWire are required.',
  '; Values contain only lowercase ASCII letters/digits, so JSON strings need no escapes.',
  '; This construction fixes key order and gives each source-declared key exactly once.',
  ...fields.input_fields.flatMap((field,i)=>[
   `; WireValue${i}: ${field}`,
   `(declare-fun WireValue${i} () String)`,
   `(assert (str.in_re WireValue${i} (re.* (re.union (re.range "a" "z") (re.range "0" "9")))))`,
  ]),
  `(define-fun InputWire () String (str.++ ${inputPieces.join(' ')}))`,
  '(assert (= InputByteCount (str.len InputWire)))',
  '(assert ParsedRootObject)',
  ...fields.input_fields.flatMap((_,i)=>[
   `(assert InputHas${i})`,
   `(assert Field${i}IsString)`,
   `(assert (= Field${i}Wire WireValue${i}))`,
  ]),
  '(assert (= AdditionalKeyCount 0))','',
 ];
 const smtlib2=fields.smtlib2+tail.join('\n');
 const result:CoreCommerceFormalAsciiWireV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-ascii-wire/v1-candidate' as const,language:'smtlib2' as const,
  scope:'source-ordered-closed-json-object-with-quoted-lowercase-ascii-alphanumeric-values' as const,
  application:fields.application,selector:fields.selector,service:fields.service,input_fields:fields.input_fields,
  source_capture_sha256:fields.source_capture_sha256,executable_sha256:fields.executable_sha256,
  family_sha256:fields.family_sha256,calculation_sha256:fields.calculation_sha256,
  bounds_asset_sha256:fields.bounds_asset_sha256,exporter_code_sha256:pin.sha256,
  input_fields_model_sha256:fields.smtlib2_sha256,max_input_bytes:fields.max_input_bytes,
  assumed_bytes:'exact-ascii-utf8-encoding-of-the-declared-input-wire' as const,
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['arbitrary-json-syntax-or-key-order','json-string-escapes-and-unicode',
   'raw-byte-array-theory-and-utf8-proof','expression-and-output-validation','operation-failure-action-execution',
   'generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'fixed-source-ordered-ascii-json-envelope-bound-to-all-uint64-input-observations-only' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function encodeCoreCommerceFormalAsciiWireV1(model:CoreCommerceFormalAsciiWireV1,values:readonly string[]):Uint8Array {
 if(!model||model.schema_version!=='craft.core-commerce-formal-ascii-wire/v1-candidate'||
  !names(model.input_fields)||!Array.isArray(values)||values.length!==model.input_fields.length||
  values.some(value=>typeof value!=='string'||!/^[a-z0-9]*$/.test(value)))fail('InvalidWireValue');
 const object=Object.create(null) as Record<string,string>;
 for(let i=0;i<values.length;i++)object[model.input_fields[i]!]=values[i]!;
 const wire=JSON.stringify(object),bytes=new TextEncoder().encode(wire);
 if(bytes.length>model.max_input_bytes)fail('InvalidWireValue');
 return bytes;
}

export function assertCoreCommerceFormalAsciiWireCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,model:CoreCommerceFormalAsciiWireV1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalAsciiWireV1(sources,capture,semantics,semantic,assembly,selector)))fail('InvalidModel');
}
