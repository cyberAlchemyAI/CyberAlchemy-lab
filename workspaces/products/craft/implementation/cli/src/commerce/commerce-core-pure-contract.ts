/** Fresh independent source -> faithful pure producer data. This is neither
 * an evaluator nor an original semantic/review/native owner.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {coreGenericAdmissionMode,type CoreGenericAdmissionMode} from './commerce-core-types.js';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {checkCoreCommercePureSources,checkCoreGenericPureSources,requireLegacyExpressionData,coreValueAstType} from './commerce-core-pure.js';
import type {GenericComputationContractV1,GenericValueSchemaV1} from '../generic/computation-data-v1.js';
import type {ComputationContractV1,ComputationLimitsV1,ValueSchemaV1} from './commerce-data-v1.js';
const limitNames=['max_input_bytes','max_output_bytes','max_value_bytes','max_items','max_iterations','max_ast_nodes','max_ast_depth','max_call_depth','fuel']as const;
function createComputationContract(sources:readonly {readonly path:string;readonly text:string}[],sourceNode:string,limits:ComputationLimitsV1,generic:boolean,mode:CoreGenericAdmissionMode='bounded-values') {
 const where={path:sources[0]?.path??'application.alch',start:0,end:0};
 try{dataDigest(limits);}catch{return fail('InvalidContract',where,'closed inert computation limits required');}
 if(!limits||typeof limits!=='object'||Array.isArray(limits)||Object.keys(limits).length!==limitNames.length||limitNames.some(k=>!Object.hasOwn(limits,k)||!Number.isSafeInteger(limits[k])||limits[k]<1||limits[k]>2147483647))fail('InvalidContract',where,'exact positive finite computation limits required');
 const pure=generic?checkCoreGenericPureSources(sources,mode):checkCoreCommercePureSources(sources),selected=pure.declarations.find(d=>d.name===sourceNode);if(!selected)fail('UnknownReference',where,'exact source pure declaration required');
 const records=pure.value_declarations.filter(d=>d.role!=='Enum'),enums=pure.value_declarations.filter(d=>d.role==='Enum');
 if(records.length>64||enums.length>64||pure.source_refinements.length>64||pure.declarations.length>128)fail('ResourceLimit',where,'pure producer contract declaration limits');
 const values:Omit<GenericValueSchemaV1,'schema_version'>&{schema_version:ValueSchemaV1['schema_version']|GenericValueSchemaV1['schema_version']}={schema_version:generic?'craft.generic-values/v1-candidate':'craft.commerce-values/v1-candidate',records:records.map(d=>{
  const invariants=pure.record_invariants.find(r=>r.record===d.name);if(!invariants)fail('InvalidContract',where,'source record invariant inventory missing');
  const fields=Object.fromEntries(d.fields.map(f=>[f.name,coreValueAstType(f.type)]));
  return {name:d.name,role:d.role as'Entity'|'ValueObject'|'Event',fields,invariants:invariants.invariants,event_version:d.event_version,entity:d.role==='Entity'?{identity:d.identity,unique:d.unique,immutable:d.immutable==='all'?d.fields.map(f=>f.name):d.immutable,version:generic&&(mode==='atomic-state-entry'||mode==='external-read-entry'||(mode==='external-write-entry'||mode==='event-handoff-entry'))?null:d.fields.some(f=>f.name==='version'&&f.type.kind==='UInt64')?'version':null}:null};
 }),enums:enums.map(d=>({name:d.name,variants:d.variants.map(v=>({name:v.name,wire:v.wire,fields:Object.fromEntries(v.fields.map(f=>[f.name,coreValueAstType(f.type)]))}))})),
 refinements:pure.source_refinements.map(r=>({name:r.name,carrier:{kind:'string',max_bytes:r.max_bytes,max_scalars:r.max_scalars},min_utf8_bytes:r.min_bytes,max_utf8_bytes:r.max_bytes,min_unicode_scalars:r.min_scalars,max_unicode_scalars:r.max_scalars,pattern:r.pattern,normalization:'none',equality:'exact-scalar-sequence'})),
 collection_predicates:pure.collection_predicates.map(p=>({type:coreValueAstType(p.type),rule:p.rule})),root:coreValueAstType(selected.result)};
 return coreFreeze({schema_version:generic?'craft.generic-computation/v1-candidate' as const:'domainspec.iteration-expression/v2-candidate' as const,semantics_revision:generic?'ordered-metered-generic-v1-candidate' as const:'ordered-metered-commerce-v2-candidate' as const,...(generic?{invariant_policy:'reject-inexact/v1' as const,record_layout:'canonical-fields/v1' as const,equality_policy:'typed-structural-metered/v1' as const,append_policy:'list-item-checkpoint-capacity/v1' as const}:{}),source_node:selected.name,values,inputs:selected.parameters.map(p=>({name:p.name,type:coreValueAstType(p.type)})),functions:pure.declarations.map(d=>({name:d.name,kind:d.kind,pure:true,parameters:d.parameters.map(p=>({name:p.name,type:coreValueAstType(p.type)})),result:coreValueAstType(d.result),body:d.body,preconditions:d.preconditions,precondition_mode:'embedded-once-in-body',rounding:d.rounding,on_evaluation_error:d.on_evaluation_error})),result:coreValueAstType(selected.result),rounding:selected.rounding,limits:{...limits},expression:{op:'call',declaration:selected.name,arguments:selected.parameters.map(p=>({op:'var',name:p.name}))}});
}
export function createCoreCommerceComputationContract(sources:readonly {readonly path:string;readonly text:string}[],sourceNode:string,limits:ComputationLimitsV1):ComputationContractV1{return requireLegacyExpressionData<ComputationContractV1>(createComputationContract(sources,sourceNode,limits,false));}
export function createCoreGenericComputationContract(sources:readonly {readonly path:string;readonly text:string}[],sourceNode:string,limits:ComputationLimitsV1,mode:CoreGenericAdmissionMode='bounded-values'):GenericComputationContractV1{coreGenericAdmissionMode(mode);return createComputationContract(sources,sourceNode,limits,true,mode) as GenericComputationContractV1;}
export function checkCoreCommerceComputationProposal(sources:readonly {readonly path:string;readonly text:string}[],sourceNode:string,limits:ComputationLimitsV1,proposal:unknown):ComputationContractV1 {
 const actual=createCoreCommerceComputationContract(sources,sourceNode,limits),where={path:sources[0]?.path??'application.alch',start:0,end:0};let proposed:string;
 try{proposed=dataDigest(proposal);}catch{return fail('InvalidContract',where,'inert bounded computation proposal required');}
 if(proposed!==dataDigest(actual))fail('InvalidContract',where,'computation data differs from fresh independent source reconstruction');return actual;
}
