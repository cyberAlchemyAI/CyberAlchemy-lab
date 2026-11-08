/** Generic Mapping order lowers to existing typed lets, never a new evaluator.
 * Legacy source normalization and ExprV1 remain unchanged.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {coreFreeze,coreSha256,coreSourceFail as fail,coreSourceChildren as children,coreSourceChild as child,coreSourceText as text,coreSourceTokens as tokens} from '../commerce/commerce-core-syntax.js';
import {checkCoreCommercePureSources,requireLegacyExpressionData} from '../commerce/commerce-core-pure.js';
import {reconstructCoreCommerceSources} from '../commerce/commerce-core-reconstruction.js';
import {createCoreCommerceComputationContract} from '../commerce/commerce-core-pure-contract.js';
import {admitGenericComposition,GENERIC_MAPPING_CAPABILITIES,GENERIC_CALCULATION_CAPABILITIES} from './composition-capabilities.js';
import type {GenericComputationContractV1,GenericExprV1} from './computation-data-v1.js';
import type {ComputationContractV1,ComputationLimitsV1,ExprV1} from '../commerce/commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url));
export const pureMappingPin=pinCoreImplementation(import.meta.url,['composition-capabilities'+ext,'../commerce/commerce-core-pure-contract'+ext,'../commerce/commerce-core-pure'+ext]);
export const GENERIC_MAPPING_REVISION='craft.generic-ordered-mapping/typed-lets-v1-candidate';
const at={path:'mapping',start:0,end:0};
const canonicalFields=<T>(fields:Readonly<Record<string,T>>):Record<string,T>=>Object.fromEntries(Object.keys(fields).sort().map(k=>[k,fields[k]!]));
export function createOrderedMappingComputation(sources:readonly {path:string;text:string}[],selected:string,limits:ComputationLimitsV1,calculations=false){
 pureMappingPin.assertCurrent();const reconstruction=reconstructCoreCommerceSources(sources),pure=checkCoreCommercePureSources(sources);
 admitGenericComposition({reconstruction},pure,calculations?GENERIC_CALCULATION_CAPABILITIES:GENERIC_MAPPING_CAPABILITIES);
 const base=createCoreCommerceComputationContract(sources,selected,limits);
 return requireLegacyExpressionData<ReturnType<typeof orderMappingContract>&{contract:ComputationContractV1}>(orderMappingContract(base,reconstruction,sources));
}
/** Compiler-only structural lowering shared by versioned original-source producers. */
export function orderMappingContract(base:ComputationContractV1|GenericComputationContractV1,reconstruction:ReturnType<typeof reconstructCoreCommerceSources>,sources:readonly {path:string;text:string}[]){
 const limits=base.limits,sequences:any[]=[];
 const functions=base.functions.map(f=>{
  if(f.kind!=='Mapping')return f;
  const declaration=reconstruction.modules.flatMap(m=>m.declarations).find(d=>d.id===f.name)!,body=child(declaration.syntax,'mapping-body');
  const source={path:declaration.syntax.path,start:declaration.syntax.start,end:declaration.syntax.end};
  if(children(body,'expression-value').length){sequences.push({mapping:f.name,form:'whole-expression',source,assignments:[]});return f;}
  let fieldBody=f.body;const guards:GenericExprV1[]=[];
  while(fieldBody.op==='require_some'&&fieldBody.value.op==='if'&&fieldBody.value.then.op==='some'&&fieldBody.value.else.op==='none'){guards.push(fieldBody.value.condition as GenericExprV1);fieldBody=fieldBody.value.then.value as typeof fieldBody;}
  if(fieldBody.op!=='record')fail('InvalidContract',source,'checked field Mapping must construct its original target record');
  const original=fieldBody,record=base.values.records.find(r=>r.name===original.type_name)!;
  const preserved=children(body,'name-list').flatMap(list=>children(list,'qualified-name').map(node=>({name:text(node),kind:'preserve',source:{path:node.path,start:node.start,end:node.end}})));
  const assigned=children(body,'field-binding').map(node=>({name:tokens(node).filter(t=>!t.layout)[1]!.token,kind:'assignment',source:{path:node.path,start:node.start,end:node.end}}));
  const ordered=[...preserved,...assigned];if(ordered.length!==Object.keys(original.fields).length||new Set(ordered.map(x=>x.name)).size!==ordered.length||ordered.some(x=>!Object.hasOwn(original.fields,x.name)))fail('InvalidContract',source,'exact desugared source assignment coverage required');
  // Every authored or checker-generated binding is reserved before selecting
  // deterministic fresh locals; a profile cannot capture a business variable.
  const used=new Set(f.parameters.map(p=>p.name)),pending:any[]=[f.body];let visited=0;
  while(pending.length){if(++visited>65536)fail('ResourceLimit',source,'bounded Mapping construction');const v=pending.pop();if(!v||typeof v!=='object')continue;if(v.op==='var')used.add(v.name);if(v.binding?.name)used.add(v.binding.name);for(const x of Object.values(v))if(x&&typeof x==='object')pending.push(...(Array.isArray(x)?x:[x]));}
  let ordinal=0;const bindings=ordered.map(row=>{let name:string;do{name='__craft_mapping_'+ordinal++;}while(used.has(name));used.add(name);return {...row,binding:{name,type:record.fields[row.name]!}};});
  let expression:GenericExprV1={op:'record',type_name:original.type_name,fields:canonicalFields(Object.fromEntries(bindings.map(x=>[x.name,{op:'var' as const,name:x.binding.name}])))};
  for(let i=bindings.length-1;i>=0;i--){const b=bindings[i]!;expression={op:'let',binding:b.binding,value:original.fields[b.name]!,body:expression};}
  for(let i=guards.length-1;i>=0;i--)expression={op:'require_some',value:{op:'if',condition:guards[i]!,then:{op:'some',value:expression},else:{op:'none',element_type:f.result}}};
  sequences.push({mapping:f.name,form:'ordered-fields',source,assignments:bindings});return {...f,body:expression};
 });
 const contract={...base,functions,values:{...base.values,records:base.values.records.map(r=>({...r,fields:canonicalFields(r.fields)})),enums:base.schema_version==='craft.generic-computation/v1-candidate'?base.values.enums.map(e=>({...e,variants:e.variants.map(v=>({...v,fields:canonicalFields(v.fields)}))})):base.values.enums}};
 // The extra lets are actual AST work. Bound construction before recursive
 // freezing/digesting and retain all authored runtime limits unchanged.
 const pending:{value:unknown;depth:number}[]=[{value:contract,depth:1}];let nodes=0;
 while(pending.length){const {value,depth}=pending.pop()!;if(!value||typeof value!=='object')continue;const expr='op'in value;if(expr&&(++nodes>limits.max_ast_nodes||depth>limits.max_ast_depth||nodes>65536||depth>128))fail('ResourceLimit',at,'ordered Mapping exceeds AST construction bound');for(const v of Object.values(value))if(v&&typeof v==='object')pending.push({value:v,depth:depth+(expr?1:0)});}
 const derivation={revision:GENERIC_MAPPING_REVISION,assignments:sequences,source_limits_sha256:dataDigest(limits),layout:'canonical-record-layout;preserve-listed-before-authored-fields',metering:'existing-typed-let-and-var-charges;preserve-equals-explicit-copy;single-shared-budget',validation:'each-assignment-before-next;cached-same-destination-on-let-unwind',authority_effect:'none'};
 const {root:_selectedResult,...valueTypes}=contract.values;
 const mapping_semantics_sha256=dataDigest({revision:GENERIC_MAPPING_REVISION,functions:contract.functions,values:valueTypes,limits});
 const projection_sha256=dataDigest({mapping_semantics_sha256,assignments:sequences,sources:sources.map(s=>({path:s.path,sha256:coreSha256(s.text)}))});
 pureMappingPin.assertCurrent();return coreFreeze({contract,derivation:{...derivation,mapping_semantics_sha256,projection_sha256}});
}
