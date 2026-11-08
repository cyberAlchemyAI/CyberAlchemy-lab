import {captureJson,dataDigest,reject,sha256} from './contracts.js';
import {validateBusinessAuthoringContractV2} from './business-authoring-schema-v2.js';
import {directExecutableIdentityV2} from './business-authoring-identity-v2.js';
import type {BusinessSourceCapture} from './business-authoring-protocol.js';
import type {BusinessSpecDataV2} from './business-authoring-protocol-v2.js';
/** Finite coverage/output contracts. Plain inventories/plans are not original owner handles.
 * Open Questions: docs/BUSINESS-COVERAGE-V2.md. */
export const BUSINESS_OUTPUT_KINDS_V2=Object.freeze(['code','api-contracts','business-graph','system-graph','business-system-bridge','base-model','conjecture-problems'] as const);
export type BusinessOutputKindV2=typeof BUSINESS_OUTPUT_KINDS_V2[number];
export type BusinessCoverageOwnerV2='source'|'direct-condition'|'pure-operation'|'entry-intent'|'native-realization'|'checked-views';
export interface BusinessCoverageOriginV2 {readonly source:string;readonly selector:string;readonly sha256:string}
export interface BusinessCoverageObligationV2 {
 readonly id:string;readonly kind:'authored-fact'|'entity-shape'|'condition'|'guard'|'result'|'rejection'|'effects'|'entry'|'permission';
 readonly owner_required:BusinessCoverageOwnerV2;readonly origins:readonly BusinessCoverageOriginV2[];
 readonly state:'producer-required';
}
export interface BusinessCoverageInventoryV2 {
 readonly schema_version:'craft.business-coverage/v2-candidate';readonly model_id:string;readonly source_sha256:string;
 readonly executable_sha256:string;readonly obligations:readonly BusinessCoverageObligationV2[];
 readonly inventory_sha256:string;readonly authority_effect:'none';
}
export interface BusinessOutputRequestV2 {readonly kind:BusinessOutputKindV2;readonly requiredness:'required'|'optional'}
export interface BusinessOutputPlanV2 {
 readonly schema_version:'craft.business-output/v2-candidate';readonly mode:'code-only';
 readonly outputs:readonly Readonly<BusinessOutputRequestV2&{state:'pending-producer'|'unsupported-optional'}>[];readonly authority_effect:'none';
}
export type BusinessOutputStateV2='not-requested'|'pending-producer'|'produced'|'unsupported-required'|'unsupported-optional'|'failed-required'|'failed-optional'|'stale';
export interface BusinessProducedArtifactV2 {readonly path:string;readonly sha256:string;readonly bytes:number;readonly checked_owner_sha256:string;readonly producer_sha256:string}
export type BusinessOutputResultRowV2=
 |Readonly<BusinessOutputRequestV2&{state:'produced';artifact:BusinessProducedArtifactV2}>
 |Readonly<{kind:BusinessOutputKindV2;requiredness:'required';state:'pending-producer'|'unsupported-required'|'failed-required'|'stale';artifact:null}>
 |Readonly<{kind:BusinessOutputKindV2;requiredness:'optional';state:'not-requested'|'pending-producer'|'unsupported-optional'|'failed-optional'|'stale';artifact:null}>;
export interface BusinessOutputResultV2 {readonly schema_version:'craft.business-output-result/v2-candidate';readonly rows:readonly BusinessOutputResultRowV2[];readonly authority_effect:'none'}
export type BusinessSupportEvidenceV2=
 |Readonly<{stage:'declared';contract_ref:string}>
 |Readonly<{stage:'generated';artifact_sha256:string;producer_sha256:string}>
 |Readonly<{stage:'native-observed';subject_sha256:string;producer_sha256:string;receipt_sha256:string}>
 |Readonly<{stage:'installed-tested';candidate_sha256:string;runner_sha256:string;receipt_sha256:string}>;
export interface BusinessSupportCellV2 {
 readonly schema_version:'craft.business-support-cell/v2-candidate';readonly cell_id:string;
 readonly source_contract:'alchlang.business-spec/v2-candidate';readonly recipe:'direct-entity-bool-operation/v2-candidate';
 readonly descriptor:'node-http-entry-u0-v4';readonly abi:'craft.u0.pure-submission/v1-candidate';
 readonly entry_access:'public';readonly effects:'none';readonly evidence:readonly BusinessSupportEvidenceV2[];readonly authority_effect:'none';
}
const frozen=<T>(value:unknown):T=>captureJson(value) as unknown as T;
/** Establish the source denominator before semantic lowering; S01 later owns genuine registry/graph joins. */
export function inventoryBusinessSourceContractV2(input:BusinessSpecDataV2,sourceInput:BusinessSourceCapture):BusinessCoverageInventoryV2 {
 const spec=validateBusinessAuthoringContractV2('spec',input),source=frozen<BusinessSourceCapture>(sourceInput);
 if(typeof source.text!=='string'||source.bytes!==Buffer.byteLength(source.text)||source.bytes>1048576||sha256(source.text)!==source.sha256||/[\uD800-\uDFFF]/u.test(source.text))reject('BUSINESS_V2_COVERAGE_SOURCE','/source','exact bounded source capture required');
 const rows=source.text.split(/\r?\n/).map((text,i)=>({text,line:i+1})).filter(row=>row.text.trim()&&!row.text.trimStart().startsWith('#'));
 if(rows.length!==spec.source_spans.length||rows.length!==spec.obligations.length)reject('BUSINESS_V2_COVERAGE_DENOMINATOR','/source_spans','all original noncomment facts required');
 const spans=new Map(spec.source_spans.map(span=>[span.selector,span]));
 if(spans.size!==rows.length||new Set(spec.source_spans.map(span=>span.line)).size!==rows.length||new Set(spec.obligations.map(row=>row.selector)).size!==rows.length||new Set(spec.obligations.map(row=>row.span_selector)).size!==rows.length)reject('BUSINESS_V2_COVERAGE_DENOMINATOR','/obligations','one original obligation and source selector per physical fact');
 const physical=new Map(rows.map(row=>[row.line,row]));
 for(const span of spec.source_spans){const row=physical.get(span.line);if(!row||span.text!==row.text||span.source!==source.path||span.source_sha256!==source.sha256||span.column!==row.text.length-row.text.trimStart().length+1)reject('BUSINESS_V2_COVERAGE_ORIGIN','/source_spans','exact physical source origin required');}
 const obligations:BusinessCoverageObligationV2[]=spec.obligations.map(row=>{
  const span=spans.get(row.span_selector);if(!span)reject('BUSINESS_V2_COVERAGE_ORIGIN','/obligations','original span required');
  return {id:'source:'+row.selector,kind:'authored-fact',owner_required:'source',origins:[{source:span!.source,selector:span!.selector,sha256:source.sha256}],state:'producer-required'};
 });
 const required:readonly [BusinessCoverageObligationV2['kind'],BusinessCoverageOwnerV2,string][]=[['entity-shape','direct-condition','entity '],['condition','direct-condition','condition '],['guard','pure-operation','requires '],['result','pure-operation','returns '],['rejection','pure-operation','on-rejection '],['effects','pure-operation','effects '],['entry','entry-intent','entry '],['permission','entry-intent','permission ']];
 for(const [kind,owner,prefix] of required){const origins=spec.source_spans.filter(span=>span.text.trimStart().startsWith(prefix)).map(span=>({source:span.source,selector:span.selector,sha256:source.sha256}));if(!origins.length)reject('BUSINESS_V2_COVERAGE_REQUIRED','/'+kind,'original executable clause required');obligations.push({id:'executable:'+kind,kind,owner_required:owner,origins,state:'producer-required'});}
 const body={schema_version:'craft.business-coverage/v2-candidate',model_id:spec.identity.namespace,source_sha256:source.sha256,executable_sha256:directExecutableIdentityV2(spec).sha256,obligations,authority_effect:'none'};
 return frozen({...body,inventory_sha256:dataDigest(body)});
}
/** Explicit requested-output planning only. U11 checks actual artifacts/current owners before completion. */
export function planBusinessOutputsV2(input:readonly BusinessOutputRequestV2[]):BusinessOutputPlanV2 {
 const requests=frozen<readonly BusinessOutputRequestV2[]>(input);
 if(!Array.isArray(requests)||requests.length<1||requests.length>BUSINESS_OUTPUT_KINDS_V2.length)reject('BUSINESS_V2_OUTPUT_REQUEST','/outputs','finite explicit output list required');
 const seen=new Set<string>();
 const outputs=requests.map(row=>{
  if(!row||typeof row!=='object'||Object.keys(row).sort().join(',')!=='kind,requiredness'||!BUSINESS_OUTPUT_KINDS_V2.includes(row.kind)||!['required','optional'].includes(row.requiredness)||seen.has(row.kind))reject('BUSINESS_V2_OUTPUT_REQUEST','/outputs','one closed registered output request per kind');seen.add(row.kind);
  const formal=row.kind==='base-model'||row.kind==='conjecture-problems';
  if(formal&&row.requiredness==='required')reject('BUSINESS_V2_OUTPUT_UNSUPPORTED_REQUIRED','/'+row.kind,'U1 exporter is not selected/qualified in U0');
  return {...row,state:formal?'unsupported-optional' as const:'pending-producer' as const};
 });
 if(!requests.some(row=>row.kind==='code'&&row.requiredness==='required'))reject('BUSINESS_V2_OUTPUT_CODE_REQUIRED','/outputs','explicit required code output selects this unit');
 return frozen({schema_version:'craft.business-output/v2-candidate',mode:'code-only',outputs,authority_effect:'none'});
}
