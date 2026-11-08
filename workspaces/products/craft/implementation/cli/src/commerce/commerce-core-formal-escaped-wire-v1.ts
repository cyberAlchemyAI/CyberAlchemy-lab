/** Source-bound fixed JSON envelope with every lowercase ASCII value character
 * encoded as a JSON \u00XX escape. It does not claim general JSON equivalence.
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
import {exportCoreCommerceFormalInputFieldsV1} from './commerce-core-formal-input-fields-v1.js';

export class CoreCommerceFormalEscapedWireErrorV1 extends Error {
 constructor(readonly code:'UnsupportedEnvelope'|'InvalidWireValue'|'InvalidModel'){
  super(code);this.name='CoreCommerceFormalEscapedWireErrorV1';
 }
}
const fail=(code:CoreCommerceFormalEscapedWireErrorV1['code']):never=>{throw new CoreCommerceFormalEscapedWireErrorV1(code);};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const smtString=(value:string)=>`"${value.replaceAll('"','""')}"`;
const alphabet='abcdefghijklmnopqrstuvwxyz0123456789';
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-computation-kernel'+ext,'commerce-core-formal-input-fields-v1'+ext]);

export interface CoreCommerceFormalEscapedWireV1 {
 readonly schema_version:'craft.core-commerce-formal-escaped-wire/v1-candidate';
 readonly language:'smtlib2';readonly scope:'source-ordered-json-with-all-lowercase-ascii-value-characters-escaped';
 readonly application:string;readonly selector:string;readonly service:string;readonly input_fields:readonly string[];
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly calculation_sha256:string;readonly bounds_asset_sha256:string;readonly exporter_code_sha256:string;
 readonly input_fields_model_sha256:string;readonly max_input_bytes:number;
 readonly assumed_bytes:'exact-ascii-utf8-encoding-of-source-ordered-all-escaped-input-wire';
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['mixed-direct-and-escaped-characters','escaped-or-reordered-keys','non-ascii-and-surrogate-escapes','arbitrary-json-and-invalid-escape-error-priority','raw-byte-array-theory','expression-and-operation-execution','generated-native-parity','solver-proof'];
 readonly authority_effect:'none';readonly claim_ceiling:'fixed-source-ordered-all-escaped-ascii-value-envelope-only';
}

export function exportCoreCommerceFormalEscapedWireV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommerceFormalEscapedWireV1 {
 pin.assertCurrent();
 const fields=exportCoreCommerceFormalInputFieldsV1(sources,capture,semantics,semantic,assembly,selector);
 if(!fields.input_fields.length||fields.input_fields.some(name=>!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)))fail('UnsupportedEnvelope');
 let mapping='""';
 for(const char of [...alphabet].reverse()){
  const escape='u00'+char.charCodeAt(0).toString(16).padStart(2,'0');
  mapping=`(ite (= c ${smtString(char)}) (str.++ (str.from_code 92) ${smtString(escape)}) ${mapping})`;
 }
 const parts:string[]=[];
 for(let i=0;i<fields.input_fields.length;i++){
  parts.push(smtString((i===0?'{':',')+JSON.stringify(fields.input_fields[i])+':"'),`(EscapeAscii Field${i}Wire)`);
 }
 parts.push(smtString('"}'));
 const tail=[
  '; Values are lowercase ASCII letters/digits. Each character is encoded as six ASCII bytes: \\u00XX.',
  '; Escaped keys, mixed encodings, surrogates, arbitrary JSON and parser failures remain unsupported.',
  `(define-fun EscapeChar ((c String)) String ${mapping})`,
  '(define-fun-rec EscapeAscii ((s String)) String (ite (= s "") "" (str.++ (EscapeChar (str.at s 0)) (EscapeAscii (str.substr s 1 (- (str.len s) 1))))))',
  ...fields.input_fields.flatMap((_,i)=>[
   `(assert (str.in_re Field${i}Wire (re.* (re.union (re.range "a" "z") (re.range "0" "9")))))`,
   `(assert InputHas${i})`,`(assert Field${i}IsString)`,
  ]),
  `(define-fun InputWire () String (str.++ ${parts.join(' ')}))`,
  '(assert (= InputByteCount (str.len InputWire)))',
  '(assert ParsedRootObject)',
  '(assert (= AdditionalKeyCount 0))','',
 ];
 const smtlib2=fields.smtlib2.replace('(set-logic QF_SLIA)','(set-logic ALL)')+tail.join('\n');
 const result:CoreCommerceFormalEscapedWireV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-escaped-wire/v1-candidate' as const,language:'smtlib2' as const,
  scope:'source-ordered-json-with-all-lowercase-ascii-value-characters-escaped' as const,
  application:fields.application,selector:fields.selector,service:fields.service,input_fields:fields.input_fields,
  source_capture_sha256:fields.source_capture_sha256,executable_sha256:fields.executable_sha256,
  family_sha256:fields.family_sha256,calculation_sha256:fields.calculation_sha256,
  bounds_asset_sha256:fields.bounds_asset_sha256,exporter_code_sha256:pin.sha256,
  input_fields_model_sha256:fields.smtlib2_sha256,max_input_bytes:fields.max_input_bytes,
  assumed_bytes:'exact-ascii-utf8-encoding-of-source-ordered-all-escaped-input-wire' as const,
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['mixed-direct-and-escaped-characters','escaped-or-reordered-keys',
   'non-ascii-and-surrogate-escapes','arbitrary-json-and-invalid-escape-error-priority','raw-byte-array-theory',
   'expression-and-operation-execution','generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'fixed-source-ordered-all-escaped-ascii-value-envelope-only' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function encodeCoreCommerceFormalEscapedWireV1(model:CoreCommerceFormalEscapedWireV1,values:readonly string[]):Uint8Array {
 if(!model||model.schema_version!=='craft.core-commerce-formal-escaped-wire/v1-candidate'||
  !Array.isArray(values)||values.length!==model.input_fields.length||
  values.some(value=>typeof value!=='string'||!/^[a-z0-9]*$/.test(value)))fail('InvalidWireValue');
 const encoded=values.map(value=>[...value].map(char=>'\\u00'+char.charCodeAt(0).toString(16).padStart(2,'0')).join(''));
 const wire='{'+model.input_fields.map((name,i)=>JSON.stringify(name)+':"'+encoded[i]+'"').join(',')+'}';
 const bytes=new TextEncoder().encode(wire);
 if(bytes.length>model.max_input_bytes)fail('InvalidWireValue');
 return bytes;
}

export function assertCoreCommerceFormalEscapedWireCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,model:CoreCommerceFormalEscapedWireV1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalEscapedWireV1(sources,capture,semantics,semantic,assembly,selector)))fail('InvalidModel');
}
