import {createGenericTransactionSourceContract,createGenericExternalWriteTransactionSourceContract,createGenericEventTransactionSourceContract} from './transaction-source.js';
import {createKeyedSourceContract} from './readonly-control.js';
import {genericSourceBounds as keyedSourceBounds} from './semantic-reconstruction.js';
import {coreGenericAdmissionMode,type CoreGenericAdmissionMode} from '../commerce/commerce-core-types.js';
import {GENERIC_TECHNICAL_PROFILE_CAPABILITIES,GENERIC_EXTERNAL_WRITE_CAPABILITIES,GENERIC_EXTERNAL_READ_CAPABILITIES,GENERIC_TRANSACTION_CAPABILITIES,GENERIC_VALUE_CAPABILITIES,GENERIC_STATE_CAPABILITIES,GENERIC_KEYED_CAPABILITIES,GENERIC_EVENT_CAPABILITIES} from './composition-capabilities.js';
/** Inert generic source projection. Only original registered owners can execute it.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail,coreSourceChildren as children,coreSourceChild as child} from '../commerce/commerce-core-syntax.js';
import {reconstructCoreCommerceSources} from '../commerce/commerce-core-reconstruction.js';
import {checkCoreGenericPureSources} from '../commerce/commerce-core-pure.js';
import {createCoreGenericComputationContract} from '../commerce/commerce-core-pure-contract.js';
import {createCoreGenericEffectContracts} from '../commerce/commerce-core-role-contracts.js';
import {orderMappingContract} from './pure-mapping.js';
import {lowerOperationContract} from './pure-operation.js';
import type {ComputationLimitsV1} from '../commerce/commerce-data-v1.js';
import type {GenericComputationContractV1} from './computation-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url));
export const genericSourcePin=pinCoreImplementation(import.meta.url,['../commerce/commerce-policy-enforcement'+ext,'external-write-source'+ext,'external-write-profile'+ext,'external-write-data-v1'+ext,'external-write-identity'+ext,'composition-capabilities'+ext,'computation-data-v1'+ext,'pure-mapping'+ext,'pure-operation'+ext,'../commerce/commerce-core-pure-contract'+ext,'../commerce/commerce-core-pure'+ext,'../commerce/commerce-core-types'+ext,'../commerce/commerce-core-role-contracts'+ext,'../commerce/commerce-core-flow-operation'+ext,'../commerce/commerce-core-flow-expression'+ext,'readonly-control'+ext,'query-data-v1'+ext,'../commerce/commerce-core-flow-query'+ext,'../commerce/commerce-core-flow-entry'+ext,'transaction-source'+ext,'transaction-data-v1'+ext,'event-data-v1'+ext,'event-handoff-source'+ext,'assurance-source'+ext,'identity'+ext,'../../contracts/generic-transaction-v1.schema.json','../../contracts/generic-computation-v1.schema.json']);
export function genericAdmissionIdentity(mode:CoreGenericAdmissionMode='bounded-values'){coreGenericAdmissionMode(mode);return {admission_mode:mode,admission_capabilities_sha256:dataDigest(mode==='technical-profile'?GENERIC_TECHNICAL_PROFILE_CAPABILITIES:mode==='event-handoff-entry'?GENERIC_EVENT_CAPABILITIES:mode==='external-write-entry'?GENERIC_EXTERNAL_WRITE_CAPABILITIES:mode==='external-read-entry'?GENERIC_EXTERNAL_READ_CAPABILITIES:mode==='atomic-state-entry'?GENERIC_TRANSACTION_CAPABILITIES:mode==='keyed-query-entry'?GENERIC_KEYED_CAPABILITIES:mode==='state-proposals'?GENERIC_STATE_CAPABILITIES:GENERIC_VALUE_CAPABILITIES)};}
export function checkGenericSource(sources:readonly {path:string;text:string}[],mode:CoreGenericAdmissionMode='bounded-values'){
 coreGenericAdmissionMode(mode);if(mode==='keyed-query-entry'||mode==='atomic-state-entry'||mode==='external-read-entry'||mode==='external-write-entry'||mode==='event-handoff-entry')fail('InvalidContract',{path:'generic-source',start:0,end:0},'service application requires original physical capture');
 genericSourcePin.assertCurrent();const reconstruction=reconstructCoreCommerceSources(sources);
 for(const d of reconstruction.modules.flatMap(m=>m.declarations)){
  if(!['ValueObject','Enum','Rule','Calculation','Policy','Mapping','Operation',...(mode==='state-proposals'?['StateMachine']:[])].includes(d.surface)&&!(d.surface==='Interface'&&['application-composition','bounded-schema',...(mode==='technical-profile'?['technical-profile-family']:[])].includes(d.interface_kind??'')))fail('UnsupportedCapability',d.syntax,'outside generic value/pure/zero-effect source scope');
  if(d.contexts.length)fail('UnsupportedCapability',d.syntax,'native/private contexts require later ownership');
  if(d.surface==='Mapping'){const body=child(d.syntax,'mapping-body');if(children(body,'ordered-case').length||(mode!=='technical-profile'&&children(d.syntax,'expression').length))fail('UnsupportedCapability',d.syntax,'ordered Mapping cases/preconditions require separate admission');}
 }
 const pure=checkCoreGenericPureSources(sources,mode);if(pure.declarations.some(d=>d.on_evaluation_error!==null))fail('UnsupportedCapability',{path:sources[0]?.path??'source',start:0,end:0},'evaluation-error handlers require explicit future control semantics');
 const effects=createCoreGenericEffectContracts(sources,[],mode);genericSourcePin.assertCurrent();return {reconstruction,pure,effects};
}
export function createGenericSourceComputation(sources:readonly {path:string;text:string}[],selected:string,limits:ComputationLimitsV1,mode:CoreGenericAdmissionMode='bounded-values'){
 coreGenericAdmissionMode(mode);
 const checked=checkGenericSource(sources,mode),at={path:sources[0]?.path??'source',start:0,end:0},first=checked.pure.declarations[0];if(!first)fail('MissingMapping',at,'generic computation needs an original pure declaration');
 const operation=checked.effects.find(e=>e.operation.module+'.'+e.operation.name===selected),pure=checked.pure.declarations.find(d=>d.name===selected);if(!operation&&!pure)fail('UnknownReference',at,'exact generic pure or Operation selector required');
 const base=createCoreGenericComputationContract(sources,operation?first.name:selected,limits,mode),mapped=orderMappingContract(base,checked.reconstruction,sources);
 const lowered=operation?lowerOperationContract(mapped.contract as GenericComputationContractV1,operation,checked.effects.map(e=>e.operation.module+'.'+e.operation.name)):null;
 const contract=(lowered?.contract??mapped.contract) as GenericComputationContractV1;
 const pending:{value:unknown;depth:number}[]=[{value:contract,depth:1}];let count=0;
 while(pending.length){const {value,depth}=pending.pop()!;if(!value||typeof value!=='object')continue;const expr='op'in value;if(expr&&(++count>Math.min(limits.max_ast_nodes,65536)||depth>Math.min(limits.max_ast_depth,128)))fail('ResourceLimit',at,'complete generic lowered AST construction bound');for(const v of Object.values(value))if(v&&typeof v==='object')pending.push({value:v,depth:depth+(expr?1:0)});}
 const {root:_root,...values}=mapped.contract.values;
 const executable_semantics_sha256=dataDigest({...(mode==='state-proposals'?genericAdmissionIdentity(mode):{}),schema:contract.schema_version,revision:contract.semantics_revision,policies:{invariant:contract.invariant_policy,layout:contract.record_layout,equality:contract.equality_policy,append:contract.append_policy},functions:mapped.contract.functions,values,limits,effects:checked.effects});
 const derivation={...genericAdmissionIdentity(mode),...mapped.derivation,...(lowered?{operation:lowered.derivation}:{}),executable_semantics_sha256,semantic_revision:contract.semantics_revision,metering:'single-shared-budget;generic-typed-let-target-checkpoint-before-body;ordered-structural-comparison'};
 genericSourcePin.assertCurrent();return coreFreeze({contract,derivation});
}

export function createGenericKeyedSourceContract(capture:import('../commerce/commerce-core-source-owner.js').CoreCommerceSourceInspection){genericSourcePin.assertCurrent();const limits=keyedSourceBounds(capture),result=createKeyedSourceContract(capture,limits);genericSourcePin.assertCurrent();return result;}
export function createGenericKeyedPureComputation(capture:import('../commerce/commerce-core-source-owner.js').CoreCommerceSourceInspection,selected:string){
 const mode=capture.capture_mode;if(mode!=='keyed-query-entry'&&mode!=='atomic-state-entry'&&mode!=='external-read-entry'&&mode!=='external-write-entry'&&mode!=='event-handoff-entry')fail('InvalidContract',{path:'generic-source',start:0,end:0},'actual service capture required');
 const actual=mode==='event-handoff-entry'?createGenericEventTransactionSourceContract(capture):mode==='external-write-entry'?createGenericExternalWriteTransactionSourceContract(capture):mode==='atomic-state-entry'||mode==='external-read-entry'?createGenericTransactionSourceContract(capture):createGenericKeyedSourceContract(capture),app=actual.contract,paths=new Set(capture.reconstruction.modules.map(m=>m.path)),sources=capture.files.filter(f=>paths.has(f.path)),op=app.pure_operations.find(o=>o.operation.module+'.'+o.operation.name===selected),pure=app.functions.find(f=>f.name===selected);
 if(!op&&!pure)fail('UnsupportedCapability',{path:'keyed-source',start:0,end:0},'selected role must be actual pure callable or zero-effect Operation');
 const base=createCoreGenericComputationContract(sources,op?app.functions[0]!.name:selected,app.limits,mode),mapped=orderMappingContract(base,capture.reconstruction,sources),lowered=op?lowerOperationContract(mapped.contract as GenericComputationContractV1,op,app.pure_operations.map(p=>p.operation.module+'.'+p.operation.name)):null;
 return coreFreeze({contract:(lowered?.contract??mapped.contract) as GenericComputationContractV1,derivation:{...genericAdmissionIdentity(mode),...mapped.derivation,...(lowered?{operation:lowered.derivation}:{}),executable_semantics_sha256:actual.derivation.executable_semantics_sha256,semantic_revision:'ordered-metered-generic-v1-candidate'}});
}

export {createGenericTransactionSourceContract,createGenericExternalWriteTransactionSourceContract,createGenericEventTransactionSourceContract};
