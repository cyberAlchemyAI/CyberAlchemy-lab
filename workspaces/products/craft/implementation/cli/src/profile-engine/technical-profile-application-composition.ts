/** Application resources are finite joins over original generated owners.
 * Metadata grants no runtime custody or actor authority.
 * Open Questions: goals/plans/craft-connected-applications-2026-11-02/DESIGN.md. */
import {dataDigest,reject} from './contracts.js';
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
export const APPLICATION_COMPOSITION_CONSUMER='craft.application-inputs/v1';
const port=(direction:'requires'|'provides',contract:string,input:string)=>({direction,contract,effect:'read',input_codec:input,result_codec:contract});
const ingestion='craft.generated-ingestion-reference/v1',answer='craft.rag-answer-binding/v1',query='craft.generated-query-source/v1',run='craft.application-run/v1';
export const APPLICATION_COMPOSITION_PORTS=coreFreeze({
 'crm-contact-enrichment/domain-v1':{preferences:port('provides',query,'craft.grouped-preference-inputs/v1')},
 'knowledge-ingestion/domain-v1':{active:port('provides',ingestion,run)},
 'permissioned-rag/domain-v1':{ingestion:port('requires',ingestion,run),answer:port('provides',answer,run)},
 'customer-support/domain-v1':{rag:port('requires',answer,run)},
 'invoice-draft/domain-v1':{},
 'marketing-campaign/domain-v1':{preferences:port('requires',query,'craft.grouped-preference-inputs/v1')},
} as const);
const fail=(message:string):never=>reject('TECHNICAL_PROFILE_APPLICATION_COMPOSITION','application-composition',message);
export function applicationCompositionPorts(family:string):Readonly<Record<string,any>>{
 if(!Object.hasOwn(APPLICATION_COMPOSITION_PORTS,family))fail('unsupported application resource family');return (APPLICATION_COMPOSITION_PORTS as Record<string,any>)[family];
}
export function validateApplicationCompositionExports(envelope:any,topology:any){
 const exports=envelope.exports??[],binding=envelope.bindings?.application;
 // Legacy input profiles without resource exports remain valid standalone inputs.
 if(!binding&&!exports.length)return;
 const expected=applicationCompositionPorts(topology.family);
 if(!binding||binding.kind!=='owner'||binding.capability!=='craft.profile-application-inputs'||binding.source!==envelope.contracts||binding.contract!==APPLICATION_COMPOSITION_CONSUMER||binding.descriptor_ref!==APPLICATION_COMPOSITION_CONSUMER||binding.recipe_ref!==APPLICATION_COMPOSITION_CONSUMER||binding.consumer_status!=='implemented-original-source-profile-join')fail('original application-input owner binding required');
 if(dataDigest(binding.ports)!==dataDigest(expected))fail('exact original family resource ports required');
 if(exports.length!==Object.keys(expected).length||new Set(exports.map((row:any)=>row.id)).size!==exports.length)fail('complete unique application resource exports required');
 for(const row of exports)if(row.node!=='application'||row.port!==row.id||!expected[row.id]||row.contract!==expected[row.id].contract)fail('export must resolve its original application resource');
}
export function resolveApplicationCompositionPort(source:any,id:string,declared:any){
 const expected=applicationCompositionPorts(source.topology.family)[id],binding=source.bindings?.application;
 if(!expected||!binding||binding.kind!=='owner'||binding.capability!=='craft.profile-application-inputs'||binding.contract!==APPLICATION_COMPOSITION_CONSUMER||binding.descriptor_ref!==APPLICATION_COMPOSITION_CONSUMER||binding.recipe_ref!==APPLICATION_COMPOSITION_CONSUMER||dataDigest(expected)!==dataDigest(declared))fail('actual declared original application resource port required');
 if(!source.source_files.some((file:any)=>file.path===binding.source))fail('actual captured application input contract required');return expected;
}
