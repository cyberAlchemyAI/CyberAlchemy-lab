/** Exhaustive formal observation table for one canonical bounded Bool list.
 * Only the source-bound wrapper may claim checked-reference/formal parity.
 * Invalid wire encodings, generated native code and effects are outside scope.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import {createHash} from 'node:crypto';
import {canonicalJson,dataDigest} from '../profile-engine/contracts.js';
import {evaluateGenericComputation} from '../commerce/commerce-computation-evaluate.js';
import {assertGenericComputationDomainOwner,type GenericComputationDomainOwner,
 type GenericComputationDomainHandle} from './computation-domain.js';
import {exportCheckedGenericPureExpressionFormalFromWireV1,
 type GenericPureExpressionFormalWitnessV1} from './formal-pure-expression-v1.js';

export class GenericFiniteBoolListFormalErrorV1 extends Error {
 constructor(readonly code:'UnsupportedTranslation'|'InvalidSource'|'ReferenceParityMismatch'){
  super(code);this.name='GenericFiniteBoolListFormalErrorV1';
 }
}
const reject=(code:GenericFiniteBoolListFormalErrorV1['code']):never=>{throw new GenericFiniteBoolListFormalErrorV1(code);};
const sha=(value:string|Uint8Array)=>createHash('sha256').update(value).digest('hex');
const smtString=(value:string)=>`"${value.replaceAll('"','""')}"`;
export type GenericFiniteBoolListResultV1=GenericPureExpressionFormalWitnessV1['result'];
export interface GenericFiniteBoolListObservationV1 {
 readonly values:readonly boolean[];
 readonly input_wire_sha256:string;
 readonly result:GenericFiniteBoolListResultV1;
}
export interface GenericFiniteBoolListFormalModelV1 {
 readonly schema_version:'craft.generic-finite-bool-list-formal-model/v1-candidate';
 readonly language:'smtlib2';
 readonly source_node:string;
 readonly source_capture_sha256:string;
 readonly contract_sha256:string;
 readonly executable_semantics_sha256:string;
 readonly code_epoch_sha256:string;
 readonly input_name:string;
 readonly max_items:0|1|2;
 readonly observations:readonly GenericFiniteBoolListObservationV1[];
 readonly smtlib2:string;
 readonly smtlib2_sha256:string;
 readonly source_binding:'original-owner-checked-reference-and-formal-parity'|'caller-observations-unverified';
 readonly claim_ceiling:'all-canonical-well-typed-bool-list-values-up-to-selected-bound-only';
 readonly unsupported_semantics:readonly ['noncanonical-or-invalid-wire-inputs','generated-native-parity',
  'entry-auth-operation-effects-and-temporal-recovery','solver-proof'];
}
type Metadata=Pick<GenericFiniteBoolListFormalModelV1,
 'source_node'|'source_capture_sha256'|'contract_sha256'|'executable_semantics_sha256'|'code_epoch_sha256'|'input_name'|'max_items'>;
const originalBinding=Symbol('checked-bool-list-reference-formal-parity');

/** Canonical finite domain order: length ascending, then bit-mask ascending. */
export function enumerateGenericFiniteBoolListValuesV1(maxItems:0|1|2):readonly (readonly boolean[])[]{
 if(!Number.isInteger(maxItems)||maxItems<0||maxItems>2)reject('UnsupportedTranslation');
 const rows:boolean[][]=[];
 for(let length=0;length<=maxItems;length++)for(let mask=0;mask<1<<length;mask++)
  rows.push(Object.freeze(Array.from({length},(_,i)=>Boolean(mask&(1<<i)))) as boolean[]);
 return Object.freeze(rows);
}

/** Builds the exhaustive table. Direct callers receive an explicitly
 * unverified observation claim; the checked wrapper alone supplies custody. */
export function buildGenericFiniteBoolListFormalModelV1(metadata:Metadata,
 observations:readonly GenericFiniteBoolListObservationV1[],binding?:symbol):GenericFiniteBoolListFormalModelV1{
 if(!metadata||!metadata.input_name||!metadata.source_node||
  [metadata.source_capture_sha256,metadata.contract_sha256,metadata.executable_semantics_sha256,
   metadata.code_epoch_sha256].some(value=>!/^([a-f0-9]{64})$/.test(value)))reject('InvalidSource');
 const domain=enumerateGenericFiniteBoolListValuesV1(metadata.max_items);
 if(observations.length!==domain.length)reject('UnsupportedTranslation');
 const rows=observations.map((row,index)=>{
  const values=domain[index]!;
  if(JSON.stringify(row.values)!==JSON.stringify(values)||
   row.input_wire_sha256!==sha(canonicalJson({[metadata.input_name]:values}))||
   !Number.isSafeInteger(row.result.fuel_used)||row.result.fuel_used<0)reject('UnsupportedTranslation');
  const result=row.result;
  if(result.ok){if(!/^(?:[a-f0-9]{2})*$/.test(result.wire_hex))reject('UnsupportedTranslation');}
  else if(!result.code||!result.expression_path||!Array.isArray(result.index_path)||
   !Array.isArray(result.call_path))reject('UnsupportedTranslation');
  return Object.freeze({values,input_wire_sha256:row.input_wire_sha256,result:Object.freeze({...result})});
 });
 const payload=(result:GenericFiniteBoolListResultV1)=>result.ok?result.wire_hex:
  Buffer.from(canonicalJson({code:result.code,expression_path:result.expression_path,
   index_path:result.index_path,call_path:result.call_path})).toString('hex');
 const term=(row:GenericFiniteBoolListObservationV1)=>
  `(observed ${row.result.ok} ${smtString(payload(row.result))} ${row.result.fuel_used})`;
 let body=term(rows[rows.length-1]!);
 for(let i=rows.length-2;i>=0;i--){
  const row=rows[i]!,condition=row.values.length===0?'(= Length 0)':
   `(and (= Length ${row.values.length}) ${row.values.map((value,j)=>`(= B${j} ${value})`).join(' ')})`;
  body=`(ite ${condition} ${term(row)} ${body})`;
 }
 const smtlib2=[
  '(set-logic ALL)',
  `; source_capture_sha256 ${metadata.source_capture_sha256}`,
  `; contract_sha256 ${metadata.contract_sha256}`,
  `; executable_semantics_sha256 ${metadata.executable_semantics_sha256}`,
  '; Domain: canonical typed Bool lists only; unused tail bits are irrelevant.',
  '(declare-datatypes () ((EvalResult (observed (ok Bool) (payload String) (fuel Int)))))',
  `(define-fun Evaluate ((Length Int) (B0 Bool) (B1 Bool)) EvalResult ${body})`,
  `(define-fun Admitted ((Length Int)) Bool (and (>= Length 0) (<= Length ${metadata.max_items})))`,
 ].join('\n')+'\n';
 return Object.freeze({schema_version:'craft.generic-finite-bool-list-formal-model/v1-candidate' as const,
  language:'smtlib2' as const,...metadata,observations:Object.freeze(rows),smtlib2,
  smtlib2_sha256:sha(smtlib2),
  source_binding:binding===originalBinding?'original-owner-checked-reference-and-formal-parity' as const:
   'caller-observations-unverified' as const,
  claim_ceiling:'all-canonical-well-typed-bool-list-values-up-to-selected-bound-only' as const,
  unsupported_semantics:Object.freeze(['noncanonical-or-invalid-wire-inputs','generated-native-parity',
   'entry-auth-operation-effects-and-temporal-recovery','solver-proof'] as const)});
}

/** Exhaustively compares the same checked source in reference execution and
 * the independent formal expression dispatcher before emitting a bound table. */
export function exportCheckedGenericFiniteBoolListFormalModelV1(
 owner:GenericComputationDomainOwner,handle:GenericComputationDomainHandle,
):GenericFiniteBoolListFormalModelV1{
 assertGenericComputationDomainOwner(owner);owner.assertCurrent(handle);
 const inspection=owner.inspect(handle),c=inspection.contract;
 if(c.inputs.length!==1)reject('UnsupportedTranslation');
 const input=c.inputs[0]??reject('UnsupportedTranslation');
 const type=input.type;
 if(type.kind!=='list')reject('UnsupportedTranslation');
 const listType=type as Extract<typeof type,{readonly kind:'list'}>;
 if(listType.element.kind!=='scalar'||listType.element.name!=='Bool'||listType.min_items!==0||
  listType.max_items>2||listType.max_items>c.limits.max_items||c.values.collection_predicates.length)
  reject('UnsupportedTranslation');
 const rawExecutable=inspection.derivation.executable_semantics_sha256;
 const executable=typeof rawExecutable==='string'?rawExecutable:reject('InvalidSource');
 const maxItems=listType.max_items as 0|1|2;
 const observations:GenericFiniteBoolListObservationV1[]=[];
 for(const values of enumerateGenericFiniteBoolListValuesV1(maxItems)){
  owner.assertCurrent(handle);
  const wire=new Uint8Array(Buffer.from(canonicalJson({[input.name]:values})));
  const observed=evaluateGenericComputation(owner,handle,wire);
  const formal=exportCheckedGenericPureExpressionFormalFromWireV1(owner,handle,wire);
  const actual:GenericFiniteBoolListResultV1=observed.ok?
   {ok:true,wire_hex:Buffer.from(observed.wire).toString('hex'),fuel_used:observed.fuel_used}:
   {ok:false,code:observed.error.code,expression_path:observed.error.expression_path,
    index_path:observed.error.index_path,call_path:observed.error.call_path,fuel_used:observed.fuel_used};
  if(dataDigest(actual)!==dataDigest(formal.result))reject('ReferenceParityMismatch');
  observations.push(Object.freeze({values,input_wire_sha256:sha(wire),result:Object.freeze(actual)}));
 }
 owner.assertCurrent(handle);
 return buildGenericFiniteBoolListFormalModelV1({source_node:c.source_node,
  source_capture_sha256:inspection.source_capture_sha256,contract_sha256:inspection.contract_sha256,
  executable_semantics_sha256:executable,code_epoch_sha256:inspection.code_epoch_sha256,
  input_name:input.name,max_items:maxItems},observations,originalBinding);
}
