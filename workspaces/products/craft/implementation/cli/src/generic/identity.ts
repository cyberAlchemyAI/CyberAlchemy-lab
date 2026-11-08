/** Inert reachable semantics projection; callers retain original checked owner custody.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import type {GenericEffectPlanV1,GenericPureDeclarationV1,GenericValueSchemaV1} from './computation-data-v1.js';import type {ComputationLimitsV1} from '../commerce/commerce-data-v1.js';
export function deriveGenericReachableOperationSemantics(operation:GenericEffectPlanV1,functions:readonly GenericPureDeclarationV1[],values:GenericValueSchemaV1,limits:ComputationLimitsV1){
 const selectedFunctions=new Set<string>(),selectedRecords=new Set<string>(),selectedEnums=new Set<string>(),selectedRefinements=new Set<string>(),selectedPredicates=new Set<number>(),queue:unknown[]=[operation],typeKeys=new Set<string>();let visited=0;
 const addFunction=(name:string)=>{if(selectedFunctions.has(name))return;const f=functions.find(f=>f.name===name);if(!f)fail('UnknownReference',{path:'reachable-operation',start:0,end:0},'reachable function absent');selectedFunctions.add(name);queue.push(f);};
 const addType=(kind:string,name:string)=>{const set=kind==='record'?selectedRecords:kind==='refinement'?selectedRefinements:selectedEnums;if(set.has(name))return;const row=kind==='record'?values.records.find(r=>r.name===name):kind==='refinement'?values.refinements.find(r=>r.name===name):values.enums.find(r=>r.name===name);if(!row)fail('UnknownReference',{path:'reachable-operation',start:0,end:0},'reachable type absent');set.add(name);queue.push(row);};
 while(queue.length){if(++visited>1000000)fail('ResourceLimit',{path:'reachable-operation',start:0,end:0},'reachable projection bound');const item=queue.pop();if(!item||typeof item!=='object')continue;if(Array.isArray(item)){queue.push(...item);continue;}const v=item as Record<string,unknown>;
  if(typeof v.kind==='string'&&['record','enum','refinement','variant'].includes(v.kind)){const name=v.kind==='variant'?v.enum_name:v.name;if(typeof name==='string')addType(v.kind==='variant'?'enum':v.kind,name);}
  if(v.op==='record'||v.op==='enum_value'){if(typeof v.type_name==='string')addType(v.op==='record'?'record':'enum',v.type_name);}
  if(v.op==='validate_refinement'&&typeof v.refinement==='string')addType('refinement',v.refinement);
  if(v.op==='require_variant'&&typeof v.enum_name==='string')addType('enum',v.enum_name);
  if(v.op==='call'&&typeof v.declaration==='string')addFunction(v.declaration);if(typeof v.calculation==='string')addFunction(v.calculation);
  if(typeof v.kind==='string'&&['list','optional','record','enum','variant','refinement','scalar','string','literal','outcome'].includes(v.kind)){const digest=dataDigest(v);if(!typeKeys.has(digest)){typeKeys.add(digest);values.collection_predicates.forEach((p,i)=>{if(dataDigest(p.type)===digest&&!selectedPredicates.has(i)){selectedPredicates.add(i);queue.push(p);addFunction(p.rule);}});}}
  queue.push(...Object.values(v));
 }
 const projection=coreFreeze({schema_version:'craft.generic-reachable-operation-semantics/v1-candidate',operation,functions:functions.filter(f=>selectedFunctions.has(f.name)).sort((a,b)=>a.name.localeCompare(b.name)),values:{records:values.records.filter(r=>selectedRecords.has(r.name)).sort((a,b)=>a.name.localeCompare(b.name)),enums:values.enums.filter(r=>selectedEnums.has(r.name)).sort((a,b)=>a.name.localeCompare(b.name)),refinements:values.refinements.filter(r=>selectedRefinements.has(r.name)).sort((a,b)=>a.name.localeCompare(b.name)),collection_predicates:values.collection_predicates.filter((_,i)=>selectedPredicates.has(i))},limits,semantics_revision:'ordered-metered-generic-v1-candidate',invariant_policy:'reject-inexact/v1',record_layout:'canonical-fields/v1',equality_policy:'typed-structural-metered/v1',append_policy:'list-item-checkpoint-capacity/v1'});
 return coreFreeze({operation:operation.operation.module+'.'+operation.operation.name,semantic_sha256:dataDigest(projection),projection,authority_effect:'none'});
}

/** Stable original AST path identity. Physical locations remain separate provenance. */
export function genericTransactionSourceSite(operation:string,segments:readonly (readonly [string,string|number])[]):string{
 const kinds=['enforce','read','call','transaction','create','update','guard','conditional','then','else','loop','return','emit'];
 if(!/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(operation)||!segments.length||segments.some(([kind,value])=>!kinds.includes(kind)||(typeof value==='number'?(!Number.isSafeInteger(value)||value<0):typeof value!=='string'||!/^[A-Za-z_][A-Za-z0-9_]*$/.test(value))))fail('InvalidContract',{path:'transaction-site',start:0,end:0},'invalid original transaction source site');
 const value='c08-site/v1:'+JSON.stringify([operation,segments]);if(Buffer.byteLength(value,'utf8')>2048)fail('ResourceLimit',{path:'transaction-site',start:0,end:0},'transaction source site exceeds 2048 bytes');return value;
}

/** Pre-expansion executable meaning excludes physical provenance and generated IDs. */
export function deriveGenericAuthoredLogicalMeaning(modules:readonly import('../commerce/commerce-core-reconstruction.js').CoreCommerceModule[]){
 const projection=modules.map(m=>({module:m.module,imports:m.imports.map(i=>({target:i.target,alias:i.alias})),declarations:m.declarations.filter(d=>d.surface!=='FormalClaim').map(d=>({id:d.id,surface:d.surface,tokens:semanticTokens(d.syntax)}))})).sort((a,b)=>a.module<b.module?-1:a.module>b.module?1:0);
 return coreFreeze({schema_version:'craft.generic-authored-logical-semantics/v1-candidate',modules:projection,authority_effect:'none'});
}
function semanticTokens(node:import('../commerce/commerce-core-syntax.js').CoreSourceNode):readonly string[]{
 const out:string[]=[];const walk=(n:import('../commerce/commerce-core-syntax.js').CoreSourceNode)=>{for(const child of n.children)if('rule'in child)walk(child);else if(!child.layout)out.push(child.token);};walk(node);return out;
}
