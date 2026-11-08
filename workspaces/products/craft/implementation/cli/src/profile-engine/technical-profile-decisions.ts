/** Checked decision-source adapter over original Core owners; never dispatches,
 * grants authority or refreshes credentials. Caller metadata is pure input only.
 * Open Questions: goals/plans/craft-technical-profiles-2026-10-31/UNIFIED-DESIGN.md#open-questions.
 */
import {createCoreCommerceSourceOwner} from '../commerce/commerce-core-source-owner.js';
import {createGenericSemanticOwner,genericSourceBounds} from '../generic/semantic-reconstruction.js';
import {createGenericComputationDomainOwner} from '../generic/computation-domain.js';
import {createGenericSourceComputation} from '../generic/pure-source-stage.js';
import {evaluateGenericComputationObserved} from '../commerce/commerce-computation-evaluate.js';
import {compileGenericComputationTypeScript} from '../commerce/commerce-computation-native.js';
import {dataDigest} from './contracts.js';
import type {GenericComputationContractV1} from '../generic/computation-data-v1.js';

export const TECHNICAL_DECISION_ACTIONS=Object.freeze(['Dispatch','Renew','WaitForRefresh','RecoverRefresh','InspectOriginal','Backoff','Reauthorize','Finish','Halt'] as const);
export type TechnicalDecisionAction=typeof TECHNICAL_DECISION_ACTIONS[number];
export interface TechnicalProfileDecision {readonly action:TechnicalDecisionAction;readonly delayMs:string}
/** This only validates a pure proposal. Consuming it still requires original
 * action/context, authorization, source disclosure and fence checks. */
export function validateTechnicalProfileDecision(value:unknown):TechnicalProfileDecision {
 if(!value||typeof value!=='object'||Array.isArray(value))throw new Error('Decision record required');
 const r=value as Record<string,unknown>;
 if(Object.keys(r).length!==2||!TECHNICAL_DECISION_ACTIONS.includes(r.action as TechnicalDecisionAction)||typeof r.delayMs!=='string'||!/^(0|[1-9][0-9]*)$/.test(r.delayMs)||r.delayMs.length>20||BigInt(r.delayMs)>18446744073709551615n)throw new Error('Exact decision action and UInt64 delay required');
 if(r.action==='Backoff'?r.delayMs==='0':r.delayMs!=='0')throw new Error('Only Backoff carries a positive delay');
 return Object.freeze({action:r.action as TechnicalDecisionAction,delayMs:r.delayMs});
}
/** Validate the exact inert result ABI after original source/domain checking.
 * This is type admission only, never an authority grant or source evaluator. */
export function validateTechnicalProfileDecisionContract(proposal:GenericComputationContractV1) {
 const operationOutcome=proposal.result.kind==='enum'&&proposal.result.name===proposal.source_node+'.GeneratedOutcome';
 const result=operationOutcome&&proposal.result.kind==='enum'?proposal.values.enums.find(e=>e.name===(proposal.result as {name:string}).name)?.variants.find(v=>v.name==='Returned')?.fields.value:proposal.result;
 if(!result||result.kind!=='record')throw new Error('Decision source must return a declared record');
 const record=proposal.values.records.find(row=>row.name===result.name),fields=record?.fields;
 if(!fields||Object.keys(fields).length!==2||fields.action?.kind!=='enum'||fields.delayMs?.kind!=='scalar'||fields.delayMs.name!=='UInt64')throw new Error('Decision source requires exact action/delayMs record');
 const actionType=fields.action;
 const variants=proposal.values.enums.find(row=>row.name===actionType.name)?.variants;
 if(!variants?.length||variants.some(v=>Object.keys(v.fields).length!==0||!TECHNICAL_DECISION_ACTIONS.includes(v.wire as TechnicalDecisionAction)))throw new Error('Decision source requires admitted nullary action variants');
 return Object.freeze({operationOutcome,record:record!.name,actions:Object.freeze(variants.map(v=>v.wire as TechnicalDecisionAction))});
}
/** Capture, check and execute/emit one finite pure decision source through the
 * original generic computation domain. No callback/effect evaluation is added. */
export function prepareTechnicalProfileDecisionSource(options:{readonly sourceRoot:string;readonly selector:string;readonly applicationFile?:string}) {
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(options.sourceRoot,options.applicationFile??'application.alch');
 const semantics=createGenericSemanticOwner(sources),semantic=semantics.check(capture),inspection=sources.inspect(capture);
 const texts=inspection.files.filter(row=>row.path.endsWith('.alch')).map(row=>({path:row.path,text:row.text}));
 const actual=createGenericSourceComputation(texts,options.selector,genericSourceBounds(inspection)),proposal=actual.contract;
 const {operationOutcome}=validateTechnicalProfileDecisionContract(proposal);
 const domain=createGenericComputationDomainOwner(sources,capture,semantics,semantic),handle=domain.check(proposal);
 let disposed=false;
 const current=()=>{if(disposed)throw new Error('Decision source disposed');domain.assertCurrent(handle);};
 return Object.freeze({
  inspect(){current();const checked=domain.inspect(handle);return Object.freeze({selector:options.selector,source_capture_sha256:checked.source_capture_sha256,contract_sha256:checked.contract_sha256,result_encoding:operationOutcome?'original-operation-outcome':'decision-record',policy_calculations:checked.contract.functions.filter(f=>f.kind==='Policy').map(f=>({policy:f.name,result:f.result})),authority_effect:'none' as const});},
  evaluate(wire:Uint8Array){current();const observed=evaluateGenericComputationObserved(domain,handle,wire);if(observed.result.ok){const decoded=JSON.parse(new TextDecoder().decode(observed.result.wire));if(!operationOutcome)validateTechnicalProfileDecision(decoded);else if(decoded.tag==='Returned')validateTechnicalProfileDecision(decoded.fields.value);}return observed;},
  compile(){current();const compiled=compileGenericComputationTypeScript(domain,handle);return Object.freeze({...compiled,decision_contract_sha256:dataDigest({result:proposal.result,values:proposal.values})});},
  dispose(){current();domain.dispose(handle);semantics.dispose(semantic);sources.dispose(capture);disposed=true;},
 });
}
