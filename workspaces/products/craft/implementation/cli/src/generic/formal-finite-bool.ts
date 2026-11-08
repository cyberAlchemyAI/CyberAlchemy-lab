/** Finite SMT-LIB2 projection of an original, checked pure computation.
 * This covers canonical well-typed Bool leaves, including flat records. It is an extensional
 * reference-evaluator model, not a model of Entry/Auth/storage/effects.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import {createHash} from 'node:crypto';
import {canonicalJson,dataDigest} from '../profile-engine/contracts.js';
import {assertGenericComputationDomainOwner,type GenericComputationDomainOwner,type GenericComputationDomainHandle} from './computation-domain.js';
import {evaluateGenericComputation} from '../commerce/commerce-computation-evaluate.js';

export interface GenericFormalProfileMetadataV1{
 readonly id:string;readonly path:string;readonly sha256:string;
}
export interface GenericFiniteBoolObservationV1{
 readonly input:Readonly<Record<string,boolean|Readonly<Record<string,boolean>>>>;
 readonly input_wire_sha256:string;
 readonly result:Readonly<{ok:true;wire:'true'|'false';fuel_used:number}|{ok:false;error_json:string;fuel_used:number}>;
}
export interface GenericFiniteBoolFormalModelV1{
 readonly schema_version:'craft.generic-finite-bool-formal-model/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'one-pure-computation-canonical-bool-leaves';
 readonly qualification:'complete-finite-reference-evaluator-observations-only';
 readonly source_node:string;
 readonly source_capture_sha256:string;
 readonly contract_sha256:string;
 readonly executable_semantics_sha256:string;
 readonly code_epoch_sha256:string;
 readonly limits_sha256:string;
 readonly profile_metadata:GenericFormalProfileMetadataV1;
 readonly profile_binding:'caller-supplied-unverified-pending-original-sdk-join';
 readonly input_names:readonly string[];
 readonly input_symbols:readonly string[];
 readonly input_paths:readonly Readonly<{argument:string;field:string|null;symbol:string}>[];
 readonly observations:readonly GenericFiniteBoolObservationV1[];
 readonly smtlib2:string;
 readonly smtlib2_sha256:string;
 readonly authority_effect:'none';
 readonly claim_ceiling:'reference-behavior-on-canonical-bool-leaves-only-no-generated-code-parity-or-application-semantics-or-solver-proof';
}
export class GenericFormalUnsupportedError extends Error{
 constructor(readonly code:'UnsupportedDomain'|'UnsupportedInput'|'UnsupportedResult'|'InputSpaceBound'|'InvalidProfileMetadata'|'NonAsciiObservation'|'ReferenceObservationInvalid'){
  super(code);this.name='GenericFormalUnsupportedError';
 }
}
const reject=(code:GenericFormalUnsupportedError['code']):never=>{throw new GenericFormalUnsupportedError(code);};
const sha=(bytes:string|Uint8Array)=>createHash('sha256').update(bytes).digest('hex');
const smtString=(value:string):string=>{if(/[^\x20-\x7e]/.test(value))return reject('NonAsciiObservation');return '"'+value.replaceAll('"','""')+'"';};
const isBool=(type:{kind:string;name?:string})=>type.kind==='scalar'&&type.name==='Bool';

/** The profile argument is inert metadata here. Only a later original SDK join
 * can bind it to the selected physical profile; this function never claims it
 * has done so. */
export function exportGenericFiniteBoolSmtModel(domain:GenericComputationDomainOwner,handle:GenericComputationDomainHandle,profile:GenericFormalProfileMetadataV1):GenericFiniteBoolFormalModelV1{
 assertGenericComputationDomainOwner(domain);domain.assertCurrent(handle);
 const inspection=domain.inspect(handle),contract=inspection.contract;
 const executable=inspection.derivation.executable_semantics_sha256;
 if(typeof executable!=='string'||!/^[a-f0-9]{64}$/.test(executable)||
   !/^[a-f0-9]{64}$/.test(inspection.source_capture_sha256)||
   !/^[a-f0-9]{64}$/.test(inspection.contract_sha256)||
   !/^[a-f0-9]{64}$/.test(inspection.code_epoch_sha256))return reject('ReferenceObservationInvalid');
 if(inspection.admission_mode!=='bounded-values')return reject('UnsupportedDomain');
 if(!isBool(contract.result))return reject('UnsupportedResult');
 const paths:{argument:string;field:string|null}[]=[];
 for(const binding of contract.inputs){
  if(isBool(binding.type)){paths.push({argument:binding.name,field:null});continue;}
  if(binding.type.kind!=='record')return reject('UnsupportedInput');
  const recordName=binding.type.name,record=contract.values.records.find(candidate=>candidate.name===recordName);
  if(!record||record.invariants.length||!Object.keys(record.fields).length||Object.values(record.fields).some(type=>!isBool(type)))return reject('UnsupportedInput');
  for(const field of Object.keys(record.fields))paths.push({argument:binding.name,field});
 }
 if(paths.length>4)return reject('InputSpaceBound');
 if(!profile||typeof profile.id!=='string'||!profile.id||typeof profile.path!=='string'||!profile.path||typeof profile.sha256!=='string'||!/^[a-f0-9]{64}$/.test(profile.sha256))return reject('InvalidProfileMetadata');
 const names=contract.inputs.map(b=>b.name),symbols=paths.map((_,index)=>`input_${index}`),inputPaths=paths.map((item,index)=>Object.freeze({...item,symbol:symbols[index]!})),observations:GenericFiniteBoolObservationV1[]=[];
 for(let mask=0;mask<1<<paths.length;mask++){
  domain.assertCurrent(handle);
  const input:Record<string,boolean|Record<string,boolean>>=Object.create(null);
  for(const binding of contract.inputs){input[binding.name]=binding.type.kind==='record'?Object.create(null):false;}
  paths.forEach(({argument,field},index)=>{
   if(field===null)input[argument]=Boolean(mask&(1<<index));
   else (input[argument] as Record<string,boolean>)[field]=Boolean(mask&(1<<index));
  });
  const wire=Buffer.from(canonicalJson(input)),observed=evaluateGenericComputation(domain,handle,new Uint8Array(wire));
  const result:GenericFiniteBoolObservationV1['result']=observed.ok
   ?(()=>{const value=new TextDecoder('utf-8',{fatal:true}).decode(observed.wire);if(value!=='true'&&value!=='false')return reject('ReferenceObservationInvalid');return {ok:true as const,wire:value,fuel_used:observed.fuel_used};})()
   :{ok:false,error_json:canonicalJson(observed.error),fuel_used:observed.fuel_used};
  if(!Number.isSafeInteger(result.fuel_used)||result.fuel_used<0)return reject('ReferenceObservationInvalid');
  const immutableInput=Object.freeze(Object.fromEntries(Object.entries(input).map(([name,value])=>[name,typeof value==='boolean'?value:Object.freeze({...value})])));
  observations.push(Object.freeze({input:immutableInput,input_wire_sha256:sha(wire),result:Object.freeze(result)}));
 }
 domain.assertCurrent(handle);
 const term=(row:GenericFiniteBoolObservationV1)=>`(observed ${row.result.ok?'true':'false'} ${smtString(row.result.ok?row.result.wire:row.result.error_json)} ${row.result.fuel_used})`;
 let body=term(observations[observations.length-1]!);
 const bit=(row:GenericFiniteBoolObservationV1,path:typeof inputPaths[number])=>path.field===null?row.input[path.argument]:(row.input[path.argument] as Readonly<Record<string,boolean>>)[path.field];
 for(let i=observations.length-2;i>=0;i--){const row=observations[i]!,condition=symbols.length===1?`(= ${symbols[0]} ${bit(row,inputPaths[0]!)})`:`(and ${inputPaths.map(item=>`(= ${item.symbol} ${bit(row,item)})`).join(' ')})`;body=`(ite ${condition} ${term(row)} ${body})`;}
 const metadata={schema_version:'craft.generic-finite-bool-formal-model/v1-candidate' as const,language:'smtlib2' as const,scope:'one-pure-computation-canonical-bool-leaves' as const,qualification:'complete-finite-reference-evaluator-observations-only' as const,source_node:contract.source_node,source_capture_sha256:inspection.source_capture_sha256,contract_sha256:inspection.contract_sha256,executable_semantics_sha256:executable,code_epoch_sha256:inspection.code_epoch_sha256,limits_sha256:dataDigest(contract.limits),profile_metadata:Object.freeze({...profile}),profile_binding:'caller-supplied-unverified-pending-original-sdk-join' as const,input_names:Object.freeze(names),input_symbols:Object.freeze(symbols),input_paths:Object.freeze(inputPaths),observations:Object.freeze(observations),authority_effect:'none' as const,claim_ceiling:'reference-behavior-on-canonical-bool-leaves-only-no-generated-code-parity-or-application-semantics-or-solver-proof' as const};
 const smtlib2=`(set-logic ALL)\n; Craft source_capture_sha256 ${metadata.source_capture_sha256}\n; Craft contract_sha256 ${metadata.contract_sha256}\n; Craft executable_semantics_sha256 ${metadata.executable_semantics_sha256}\n; Craft limits_sha256 ${metadata.limits_sha256}\n; profile metadata ${metadata.profile_metadata.sha256} is unverified until an original SDK join\n(declare-datatypes () ((EvalResult (observed (ok Bool) (payload String) (fuel Int)))))\n(define-fun Evaluate (${symbols.map(symbol=>`(${symbol} Bool)`).join(' ')}) EvalResult ${body})\n`;
 domain.assertCurrent(handle);
 return Object.freeze({...metadata,smtlib2,smtlib2_sha256:sha(smtlib2)});
}
