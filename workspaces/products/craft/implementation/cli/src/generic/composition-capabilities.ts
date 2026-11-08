/** Phase-specific admission; broader legacy parser support is not admission.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {coreSourceFail as fail,coreSourceChildren as children} from '../commerce/commerce-core-syntax.js';
import type {CoreCommerceSourceInspection} from '../commerce/commerce-core-source-owner.js';
import type {CorePureSemantics} from '../commerce/commerce-core-pure.js';
const at={path:'source.alch',start:0,end:0};
export const GENERIC_COMPOSITION_CAPABILITIES=Object.freeze(['Rule','record-bool'] as const);
export const GENERIC_OPERATION_CAPABILITIES=Object.freeze(['Rule','record-bool','Operation'] as const);
export const GENERIC_MAPPING_CAPABILITIES=Object.freeze(['Rule','record-bool','Operation','Mapping','record-uint64'] as const);
export const GENERIC_CALCULATION_CAPABILITIES=Object.freeze([...GENERIC_MAPPING_CAPABILITIES,'Calculation','Policy'] as const);
export const GENERIC_SCALAR_OPERATORS=Object.freeze(['and','or','eq','lt','lte','gt','gte','add','subtract','multiply','divide']);
export function admitGenericComposition(source:Pick<CoreCommerceSourceInspection,'reconstruction'>,pure:CorePureSemantics,capabilities:readonly string[]=GENERIC_COMPOSITION_CAPABILITIES):void {
 const calculations=capabilities.includes('Calculation')&&capabilities.includes('Policy'),mapping=capabilities.includes('Mapping'),scalars=mapping?['Bool','UInt64']:['Bool'];
 const declarations=source.reconstruction.modules.flatMap(m=>m.declarations);
 for(const d of declarations){
  if(d.surface==='Interface'&&d.interface_kind==='application-composition')continue;
  if(!['Rule','ValueObject',...(capabilities.includes('Operation')?['Operation']:[]),...(mapping?['Mapping']:[]),...(calculations?['Calculation','Policy']:[])].includes(d.surface))fail('UnsupportedCapability',d.syntax,'declaration enters a later composition phase');
  if(d.surface==='ValueObject'&&(d.refinement||d.fields.some(f=>!scalars.includes(f.type.kind))))fail('UnsupportedCapability',d.syntax,'this phase admits only flat Bool/selected UInt64 records');
  if(d.surface==='Mapping'){
   const body=children(d.syntax,'mapping-body')[0];
   if(children(d.syntax,'expression').length||!body||children(body,'ordered-case').length)fail('UnsupportedCapability',d.syntax,'Mapping preconditions and ordered cases require a later phase');
  }
 }
 if(!pure.declarations.some(d=>d.kind==='Rule'))fail('MissingMapping',at,'at least one Rule required');
 if(pure.source_refinements.length||pure.collection_predicates.length||pure.record_invariants.some(r=>r.invariants.length))fail('UnsupportedCapability',at,'invariants and collections enter a later composition phase');
 for(const d of pure.declarations){
  if(capabilities.includes('Operation')&&d.on_evaluation_error!==null)fail('UnsupportedCapability',at,'this phase does not execute callee evaluation-error handlers');
  if(!['Rule',...(mapping?['Mapping']:[]),...(calculations?['Calculation','Policy']:[])].includes(d.kind)||(d.kind==='Rule'&&d.result.kind!=='Bool')||!['record',...scalars].includes(d.result.kind)||d.parameters.some(p=>!['record',...scalars].includes(p.type.kind)))fail('UnsupportedCapability',at,'pure signature requires an admitted scalar or flat record');
  if((d.kind==='Calculation'||d.kind==='Policy')&&d.result.kind!=='UInt64')fail('UnsupportedCapability',at,'C04 Calculation and Policy results require UInt64');
  const declared=declarations.find(x=>x.id===d.name)!;
  const fieldMapping=d.kind==='Mapping'&&!children(children(declared.syntax,'mapping-body')[0]!,'expression-value').length;
  // Policy cases/actions are containers, not expressions. Visit every nested
  // container so unreachable branches cannot conceal unsupported operators.
  const stack:any[]=[d.body];let visited=0;
  while(stack.length){if(++visited>131072)fail('ResourceLimit',at,'bounded generic admission traversal');const e=stack.pop();if(!e||typeof e!=='object')continue;
   if(typeof e.op==='string'){
    if(!['var','field','literal','unary','binary','call','let',...(fieldMapping?['record']:[]),...(calculations?['policy']:[])].includes(e.op))fail('UnsupportedCapability',at,'expression operator enters a later phase: '+e.op);
    if(e.op==='literal'&&(e.type.kind!=='scalar'||!scalars.includes(e.type.name)))fail('UnsupportedCapability',at,'literal requires an admitted scalar');
    if(e.op==='binary'&&!(calculations?GENERIC_SCALAR_OPERATORS:['and','or','eq']).includes(e.operator))fail('UnsupportedCapability',at,'scalar arithmetic and ordering enter a later phase');
   }
   for(const value of Object.values(e))if(value&&typeof value==='object')stack.push(value);
  }
 }
}

export const GENERIC_VALUE_CAPABILITIES=Object.freeze([...GENERIC_CALCULATION_CAPABILITIES,'bounded-values','bounded-collections'] as const);

export const GENERIC_TECHNICAL_PROFILE_CAPABILITIES=Object.freeze([...GENERIC_VALUE_CAPABILITIES,'technical-profile-family','Mapping-preconditions'] as const);

export const GENERIC_STATE_CAPABILITIES=Object.freeze([...GENERIC_VALUE_CAPABILITIES,'StateMachine'] as const);

/** Exact C07 selected application cell; predecessor vectors remain unchanged. */
export const GENERIC_KEYED_CAPABILITIES=Object.freeze([...GENERIC_STATE_CAPABILITIES,'Entity','Query','Entry','keyed-sqlite-read','auth-foundation-ready'] as const);

/** Closed C08 source selection; no runtime grant. */
export const GENERIC_TRANSACTION_CAPABILITIES=Object.freeze([...GENERIC_KEYED_CAPABILITIES,'stateful-operation','atomic-sqlite-transaction','hidden-revision','command-replay'] as const);

/** Closed external read extension of the atomic application mode. */
export const GENERIC_EXTERNAL_READ_CAPABILITIES=Object.freeze([...GENERIC_TRANSACTION_CAPABILITIES,'Interface','external-read-preflight','http-safe-get','checked-provider-mappings'] as const);

/** Selected first C11 protocol: identical write/inspect signatures; no runtime grant. */
export const GENERIC_EXTERNAL_WRITE_CAPABILITIES=Object.freeze([...GENERIC_EXTERNAL_READ_CAPABILITIES,'external-write-preflight','paired-native-inspection','durable-intent-identity'] as const);

/** Closed C12 Event handoff selection over the cumulative transaction cell. */
export const GENERIC_EVENT_CAPABILITIES=Object.freeze([...GENERIC_TRANSACTION_CAPABILITIES,'Event','event-handoff'] as const);
/** C12 can also select Event handoff after the cumulative external-write cell. */
export const GENERIC_EVENT_EXTERNAL_READ_CAPABILITIES=Object.freeze([...GENERIC_EXTERNAL_READ_CAPABILITIES,'Event','event-handoff'] as const);
export const GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES=Object.freeze([...GENERIC_EXTERNAL_WRITE_CAPABILITIES,'Event','event-handoff'] as const);
