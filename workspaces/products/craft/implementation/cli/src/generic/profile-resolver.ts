/** Closed technical profile, actual physical identity and executable recipe.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {POLICY_ENFORCEMENT_CAPABILITY} from '../commerce/commerce-policy-enforcement.js';
import {dataDigest} from '../profile-engine/contracts.js';
import {parseCoreCommerceJson} from '../commerce/commerce-core-source-owner.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {GENERIC_COMPOSITION_CAPABILITIES,GENERIC_OPERATION_CAPABILITIES,GENERIC_MAPPING_CAPABILITIES,GENERIC_CALCULATION_CAPABILITIES,GENERIC_VALUE_CAPABILITIES,GENERIC_STATE_CAPABILITIES,GENERIC_KEYED_CAPABILITIES,GENERIC_EVENT_CAPABILITIES,GENERIC_EVENT_EXTERNAL_READ_CAPABILITIES,GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES} from './composition-capabilities.js';
import type {ComputationLimitsV1} from '../commerce/commerce-data-v1.js';
export interface GenericPureProfile {readonly schema_version:'craft.generic-pure-profile/v1-candidate';readonly id:string;readonly target:'node-esm';readonly capabilities:readonly ('Rule'|'record-bool'|'Operation'|'Mapping'|'record-uint64'|'Calculation'|'Policy'|'bounded-values'|'bounded-collections'|'StateMachine'|'operation-policy-enforcement')[];readonly limits:ComputationLimitsV1}
export const PURE_PROFILE_RECIPE=Object.freeze({version:'craft.generic-pure-recipe/v1-candidate',target:'node-esm',emitter:'compileCommerceComputationTypeScript/v2',module:'rule.mjs',expansion:'generated-application-root;unchanged-business-source;checked-pure-callable',runtime_dependencies:['node:util'],authority_effect:'none'});
const {module:_ruleModule,...sharedRecipe}=PURE_PROFILE_RECIPE;
export const PURE_OPERATION_RECIPE=Object.freeze({...sharedRecipe,version:'craft.generic-pure-operation-recipe/v1-candidate',modules:{Rule:'rule.mjs',Operation:'operation.mjs'},lowering:'craft.generic-zero-effect-operation/v1-candidate'});
export const PURE_MAPPING_RECIPE=Object.freeze({...sharedRecipe,version:'craft.generic-pure-mapping-recipe/v1-candidate',modules:{Rule:'rule.mjs',Operation:'operation.mjs',Mapping:'mapping.mjs'},lowering:'craft.generic-ordered-mapping/typed-lets-v1-candidate'});
export const PURE_CALCULATION_RECIPE=Object.freeze({...PURE_MAPPING_RECIPE,version:'craft.generic-scalar-policy-recipe/v1-candidate',modules:{...PURE_MAPPING_RECIPE.modules,Calculation:'calculation.mjs',Policy:'policy.mjs'},pure_semantics:'original-checked-uint64-arithmetic-and-first-match-policy/v1-candidate'});
export const PURE_VALUE_RECIPE=Object.freeze({...PURE_CALCULATION_RECIPE,version:'craft.generic-bounded-values-recipe/v1-candidate',emitter:'compileGenericComputationTypeScript/v1',pure_semantics:'ordered-metered-generic-v1-candidate'});
export const PURE_STATE_RECIPE=Object.freeze({...PURE_VALUE_RECIPE,version:'craft.generic-state-proposal-recipe/v1-candidate',admission_mode:'state-proposals',machine_semantics:'source-ordered-nullary-zero-intent-proposals/v1-candidate'});
const exactCapabilities=(actual:unknown,base:readonly string[],enforcement=true)=>dataDigest(actual)===dataDigest(base)||enforcement&&dataDigest(actual)===dataDigest([...base,POLICY_ENFORCEMENT_CAPABILITY]);
export function resolveGenericPureProfile(text:string,file:string,sourceLimits:ComputationLimitsV1):GenericPureProfile {
 const p=parseCoreCommerceJson(text,file) as any,at={path:file,start:0,end:0};
 if(!p||typeof p!=='object'||Array.isArray(p)||Object.keys(p).sort().join(',')!=='capabilities,id,limits,schema_version,target'||p.schema_version!=='craft.generic-pure-profile/v1-candidate'||typeof p.id!=='string'||! /^[a-z][a-z0-9-]{0,63}$/.test(p.id)||p.target!=='node-esm'||(dataDigest(p.capabilities)!==dataDigest(GENERIC_COMPOSITION_CAPABILITIES)&&dataDigest(p.capabilities)!==dataDigest(GENERIC_OPERATION_CAPABILITIES)&&dataDigest(p.capabilities)!==dataDigest(GENERIC_MAPPING_CAPABILITIES)&&dataDigest(p.capabilities)!==dataDigest(GENERIC_CALCULATION_CAPABILITIES)&&!exactCapabilities(p.capabilities,GENERIC_VALUE_CAPABILITIES)&&!exactCapabilities(p.capabilities,GENERIC_STATE_CAPABILITIES)))fail('UnsupportedCapability',at,'exact supported pure profile and recipe required');
 if(dataDigest(p.limits)!==dataDigest(sourceLimits))fail('InvalidContract',at,'profile cannot alter source-declared computation limits');
 return coreFreeze(p);
}

export type GenericKeyedProfile=import('./query-data-v1.js').GenericKeyedQueryProfileV1;
export const KEYED_PROFILE_RECIPE=Object.freeze({version:'craft.generic-keyed-query-recipe/v1-candidate',target:'node-esm',module:'application.mjs',runtime_package:'@domainspec-v2/cli',runtime_package_version:'1.3.0',runtime_semantics_revision:'ordered-metered-generic-v1-candidate',runtime_export:'./generic',admission_mode:'keyed-query-entry',storage:'sqlite-keyed-canonical-values/v1-candidate',auth_abi:'craft.commerce-auth-ready-bridge/v1-candidate',auth_route_template:'commerce:{logical_entry_id}',authority_effect:'none'});
export function resolveGenericKeyedProfile(text:string,file:string,sourceLimits:ComputationLimitsV1):GenericKeyedProfile {
 const p=parseCoreCommerceJson(text,file) as any,at={path:file,start:0,end:0};
 if(!p||typeof p!=='object'||Array.isArray(p)||Object.keys(p).sort().join(',')!=='auth_abi,auth_route_template,capabilities,entry_context,id,limits,schema_version,services,storage,target'||p.schema_version!=='craft.generic-keyed-query-profile/v1-candidate'||typeof p.id!=='string'||!/^[a-z][a-z0-9-]{0,63}$/.test(p.id)||p.target!=='node-esm'||dataDigest(p.capabilities)!==dataDigest(GENERIC_KEYED_CAPABILITIES)||p.entry_context!=='customer-ready-scalars/v1-candidate'||p.auth_abi!=='craft.commerce-auth-ready-bridge/v1-candidate'||p.auth_route_template!=='commerce:{logical_entry_id}'||p.storage!=='sqlite-keyed-canonical-values/v1-candidate')fail('InvalidContract',at,'exact keyed Query profile and recipe required');
 if(dataDigest(p.limits)!==dataDigest(sourceLimits))fail('InvalidContract',at,'profile cannot alter source-declared bounds');
 if(!Array.isArray(p.services)||!p.services.length||p.services.length>16||p.services.some((v:any)=>!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).sort().join(',')!=='id,module'||![v.id,v.module].every(x=>typeof x==='string'&&/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(x)))||new Set(p.services.map((x:any)=>x.id)).size!==p.services.length||new Set(p.services.map((x:any)=>x.module)).size!==p.services.length)fail('InvalidContract',at,'exact unique source module/service assignments required');
 return coreFreeze(p);
}

export type GenericTransactionProfile=import('./transaction-data-v1.js').GenericTransactionProfileV1;
export type GenericEventProfile=Omit<GenericTransactionProfile,'schema_version'|'capabilities'|'storage'>&Readonly<{
 readonly schema_version:'craft.generic-event-profile/v1-candidate';
 readonly capabilities:readonly string[];
 readonly storage:'sqlite-fenced-event-handoff/v1-candidate';
 readonly string_policy:Readonly<{max_utf8_bytes:256;max_scalars:256}>;
 readonly event_handoff:Readonly<{transport:'process-local-checked-envelope/v1-candidate';delivery:'durable-at-least-once/v1-candidate'}>;
}>;
export const TRANSACTION_PROFILE_RECIPE=Object.freeze({...KEYED_PROFILE_RECIPE,version:'craft.generic-transaction-recipe/v1-candidate',admission_mode:'atomic-state-entry',storage:'sqlite-atomic-command-values/v1-candidate',command_identity:'original-subject-entry-client-key/v1-candidate'});
export const EVENT_PROFILE_RECIPE=Object.freeze({...TRANSACTION_PROFILE_RECIPE,version:'craft.generic-event-recipe/v1-candidate',admission_mode:'event-handoff-entry',storage:'sqlite-fenced-event-handoff/v1-candidate',event_handoff:'durable-at-least-once/v1-candidate',event_transport:'process-local-checked-envelope/v1-candidate'});
const transactionCeilings=Object.freeze({max_participants:16,max_read_observations:128,max_mutations:128,max_control_depth:64,max_command_key_bytes:128,max_command_key_scalars:128,max_command_tuple_bytes:4096,max_command_records:1024,max_command_journal_bytes:16777216,max_permission_trace_items:128,max_permission_trace_bytes:32768});
export function resolveGenericTransactionBounds(text:string,file:string):import('./transaction-data-v1.js').GenericTransactionBoundsV1{
 const b=parseCoreCommerceJson(text,file) as Record<string,unknown>,at={path:file,start:0,end:0};
 if(!b||typeof b!=='object'||Array.isArray(b)||b.schema_version!=='craft.generic-transaction-bounds/v1-candidate'||Object.keys(b).sort().join(',')!==['schema_version',...Object.keys(transactionCeilings)].sort().join(',')||Object.entries(transactionCeilings).some(([k,max])=>typeof b[k]!=='number'||!Number.isSafeInteger(b[k])||(b[k] as number)<1||(b[k] as number)>max))fail('InvalidContract',at,'exact positive authored transaction bounds required');
 return coreFreeze(b) as unknown as import('./transaction-data-v1.js').GenericTransactionBoundsV1;
}
export function resolveGenericTransactionProfile(text:string,file:string,sourceLimits:ComputationLimitsV1,sourceBounds:import('./transaction-data-v1.js').GenericTransactionBoundsV1):GenericTransactionProfile{
 const p=parseCoreCommerceJson(text,file) as any,at={path:file,start:0,end:0};
 const caps=[...GENERIC_KEYED_CAPABILITIES,'stateful-operation','atomic-sqlite-transaction','hidden-revision','command-replay'];
 if(!p||typeof p!=='object'||Array.isArray(p)||Object.keys(p).sort().join(',')!=='application_namespace,auth_abi,auth_route_template,capabilities,entry_context,id,limits,schema_version,services,storage,target,transaction_bounds'||p.schema_version!=='craft.generic-transaction-profile/v1-candidate'||typeof p.id!=='string'||!/^[a-z][a-z0-9-]{0,63}$/.test(p.id)||p.target!=='node-esm'||!exactCapabilities(p.capabilities,caps)||p.entry_context!=='customer-ready-scalars/v1-candidate'||p.auth_abi!=='craft.commerce-auth-ready-bridge/v1-candidate'||p.auth_route_template!=='commerce:{logical_entry_id}'||p.storage!=='sqlite-atomic-command-values/v1-candidate'||typeof p.application_namespace!=='string'||p.application_namespace.length>192||!/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(p.application_namespace))fail('InvalidContract',at,'exact atomic-state profile and recipe required');
 resolveGenericTransactionBounds(JSON.stringify(sourceBounds),file+':authored-transaction-bounds');
 if(dataDigest(p.limits)!==dataDigest(sourceLimits)||dataDigest(p.transaction_bounds)!==dataDigest(sourceBounds))fail('InvalidContract',at,'profile cannot alter original computation or transaction bounds');
 const names=['max_input_bytes','max_output_bytes','max_value_bytes','max_items','max_iterations','max_ast_nodes','max_ast_depth','max_call_depth','fuel'];
 if(!sourceLimits||Object.keys(sourceLimits).sort().join(',')!==names.sort().join(',')||Object.values(sourceLimits).some(v=>!Number.isSafeInteger(v)||v<1||v>2147483647)||sourceLimits.max_input_bytes>65536||sourceLimits.max_output_bytes>65536)fail('InvalidContract',at,'exact computation bounds within atomic payload/result ceiling required');
 if(!Array.isArray(p.services)||!p.services.length||p.services.length>16||p.services.some((v:any)=>!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).sort().join(',')!=='id,module'||![v.id,v.module].every(x=>typeof x==='string'&&x.length<=192&&/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(x)))||new Set(p.services.map((x:any)=>x.id)).size!==p.services.length||new Set(p.services.map((x:any)=>x.module)).size!==p.services.length)fail('InvalidContract',at,'exact unique source module/service assignments required');
 return coreFreeze(p);
}
/** Distinct C12 selection; V1-V3 selected profile bytes remain unchanged. */
export function resolveGenericEventProfile(text:string,file:string,sourceLimits:ComputationLimitsV1,sourceBounds:import('./transaction-data-v1.js').GenericTransactionBoundsV1):GenericEventProfile{
 const p=parseCoreCommerceJson(text,file) as any,at={path:file,start:0,end:0};
 if(!p||typeof p!=='object'||Array.isArray(p)||Object.keys(p).sort().join(',')!=='application_namespace,auth_abi,auth_route_template,capabilities,entry_context,event_handoff,id,limits,schema_version,services,storage,string_policy,target,transaction_bounds'||p.schema_version!=='craft.generic-event-profile/v1-candidate'||p.storage!=='sqlite-fenced-event-handoff/v1-candidate'||!p.event_handoff||Object.keys(p.event_handoff).sort().join(',')!=='delivery,transport'||p.event_handoff.transport!=='process-local-checked-envelope/v1-candidate'||p.event_handoff.delivery!=='durable-at-least-once/v1-candidate'||!p.string_policy||Object.keys(p.string_policy).sort().join(',')!=='max_scalars,max_utf8_bytes'||p.string_policy.max_utf8_bytes!==256||p.string_policy.max_scalars!==256)fail('InvalidContract',at,'exact selected Event handoff profile required');
 const baseline={...p,schema_version:'craft.generic-transaction-profile/v1-candidate',storage:'sqlite-atomic-command-values/v1-candidate',capabilities:[...GENERIC_EVENT_CAPABILITIES.slice(0,-2),...(p.capabilities?.includes(POLICY_ENFORCEMENT_CAPABILITY)?[POLICY_ENFORCEMENT_CAPABILITY]:[])]};delete baseline.event_handoff;delete baseline.string_policy;
 if(![GENERIC_EVENT_CAPABILITIES,GENERIC_EVENT_EXTERNAL_READ_CAPABILITIES,GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES].some(c=>exactCapabilities(p.capabilities,c)))fail('InvalidContract',at,'Event handoff capability selection required');
 resolveGenericTransactionProfile(JSON.stringify(baseline),file+':base-transaction',sourceLimits,sourceBounds);
 return coreFreeze(p) as GenericEventProfile;
}
