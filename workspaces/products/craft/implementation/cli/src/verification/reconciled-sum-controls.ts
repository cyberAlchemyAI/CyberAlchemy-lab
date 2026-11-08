import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import type {TypedType} from '../typed-operation/contracts.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {createOwnedValueContext,isWitnessUnavailable,WitnessUnavailable,type Dependency,type SumRecipe} from './reconciled-value-context.js';
export type {SumRecipe} from './reconciled-value-context.js';
export const SEMANTIC_SUM_DEFINITION_SHA256='41897da228c7d53f2fbb86535328ee6ddfcb381c832060268437f12fc9e697db';
export interface SumControls {
 readonly selector:string;readonly kind:'Enum';readonly state:'ready';readonly adapter:'sum';
 readonly contract_sha256:string;readonly relative_path:string;readonly callable:string;
 readonly names:readonly string[];readonly module_paths:readonly string[];readonly cases:readonly SemanticCase[];
 readonly value_contract_sha256:string;readonly shape:TypedType;readonly dependencies:Readonly<Record<string,Dependency>>;
 readonly baseline:SumRecipe;
}
const part=(s:string)=>s.length+':'+s;
/** Shared source cases; native wrappers add only representation obligations. */
export function createSumSemanticCases(context:ReturnType<typeof createOwnedValueContext>){
 const {root,rootShape,ref,samples,negative}=context;
 if(root.kind!=='Enum'||root.plain)throw new TypeError('DS_RECONCILED_SUM_CONTROLS:payload-bearing sum required');
 const positives=samples(rootShape),baseline=positives[0]!,baselineKey=ref(rootShape,baseline).key,cases:SemanticCase[]=[],seen=new Set<string>();
 const push=(recipe:SumRecipe,expected:SemanticCase['expected'])=>{
  const encoded=canonicalJson(recipe);if(seen.has(encoded))return;seen.add(encoded);
  if(cases.length>=4096)throw new WitnessUnavailable('bounded sum case capacity exceeded');
  cases.push({id:'case-'+cases.length,mode:'sum',format:'string',values:[encoded],expected});
 };
 for(const r of positives){const expected=ref(rootShape,r);push(r,{kind:'value',value:canonicalJson({view:expected.view,key:expected.key,equals_baseline:expected.key===baselineKey})});}
 for(const r of positives)for(const n of negative(rootShape,r))push(n.recipe,{kind:'error',name:'TypeError',message:n.error});
 return {baseline,cases};
}
export function createSumControls(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan):SumControls|Readonly<{selector:string;kind:'Enum';state:'not_evaluable';reason:string}>{
 try{
  const context=createOwnedValueContext(node,graph,plan),{root,rootShape,valueContract,dependencies,module_paths}=context;
  if(root.kind!=='Enum'||root.plain)throw new TypeError('DS_RECONCILED_SUM_CONTROLS:payload-bearing sum required');
  const {baseline,cases:shared}=createSumSemanticCases(context);
  const cases=shared.map(c=>{
   if(c.expected.kind==='error')return c;
   const expected=JSON.parse(c.expected.value);
   return {...c,expected:{kind:'value' as const,value:canonicalJson({view:expected.view,key:part(node.selector)+part(valueContract)+part(expected.key),owned:true,frozen:true,fresh:true,equal_copy:true,equals_baseline:expected.equals_baseline,clone_rejected:true,foreign_rejected:true,metadata:{protocol_id:'typescript.owned-sum-case/v1-candidate',concept:node.selector,contract_sha256:valueContract,frozen:true}})}};
  });
  return {selector:node.selector,kind:'Enum',state:'ready',adapter:'sum',contract_sha256:sha256(canonicalJson(root.contract)),relative_path:root.relative_path,callable:root.symbol,names:root.contract.variants.map(v=>v.name),module_paths,cases,value_contract_sha256:valueContract,shape:rootShape,dependencies,baseline};
 }catch(error){if(isWitnessUnavailable(error))return {selector:node.selector,kind:'Enum',state:'not_evaluable',reason:error.message};throw error;}
}
