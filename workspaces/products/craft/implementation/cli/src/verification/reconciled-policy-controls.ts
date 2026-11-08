import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {RuleControls} from './reconciled-rule-controls.js';
import {decodeTypedRulePolicyContract} from '../typed-backend/policy-rules.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {createStructuralFacts,RuleFactsCapacity} from './reconciled-rule-facts.js';
import {createStructuralCases} from './reconciled-structural-cases.js';
import {RuleWitnessCapacity} from './reconciled-rule-reference.js';
export const SEMANTIC_POLICY_DEFINITION_SHA256='4da738c2a406c42aa45cf5a45048bef7d1bf0f968b7e18bc0e26d3159acb53a6';
export interface PolicyControls extends Omit<RuleControls,'kind'|'adapter'>{
 readonly kind:'Policy';readonly adapter:'policy';readonly source_predicted_targets:readonly string[];
 readonly source_predicted_branches:readonly number[];
 readonly native_imports:readonly Readonly<{relative_path:string;imports:readonly Readonly<{specifier:string;target_path:string}>[]}>[];
}
export function createPolicySemanticCases(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph){
  const contract=decodeTypedRulePolicyContract(node.body.typed_contract),roots=contract.cases.map(c=>c.rule.selector);
  const facts=createStructuralFacts(graph,roots,contract.cases.flatMap(c=>c.rule.arguments.map(a=>a.value))),targets=new Set<string>(),branches=new Set<number>();
  const {cases,recipes}=createStructuralCases(contract.inputs,facts,args=>{
   const result=facts.reference.select(contract,args);targets.add(result.target);branches.add(result.index);return result.target;
  },'policy','POLICY_INPUT');
  return {contract,cases,recipes,targets,branches};
}
export function createPolicyControls(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan):PolicyControls|Readonly<{selector:string;kind:'Policy';state:'not_evaluable';reason:string}>{
 const unmet=(reason:string)=>({selector:node.selector,kind:'Policy' as const,state:'not_evaluable' as const,reason});
 try{
  const {contract,cases,recipes,targets,branches}=createPolicySemanticCases(node,graph);
  if(targets.size<2)return unmet('bounded Policy cases lack distinct-target input-sensitivity witnesses; no unreachable-branch claim');
  const callable='policy'+node.selector.split(':')[1]!.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
  const modules=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(node.selector)&&m.exports.some(e=>e.name===callable&&e.kind==='value'));
  if(modules.length!==1)throw new TypeError('DS_POLICY_CONTROLS:unique native Policy module required');
  const paths=new Set<string>(),visit=(p:string)=>{
   if(paths.has(p))return;paths.add(p);
   const m=plan.resolved.modules.find(m=>m.relative_path===p);
   if(!m)throw new TypeError('DS_POLICY_CONTROLS:missing native closure');
   if(m.qualified_selectors.some(s=>!['Rule','Policy'].includes(graph.nodes.find(n=>n.selector===s)!.kind)))throw new TypeError('DS_POLICY_CONTROLS:strategy or factory dependency forbidden');
   for(const i of m.imports){if(!i.target_path)throw new TypeError('DS_POLICY_CONTROLS:external dependency');visit(i.target_path);}
  };visit(modules[0]!.relative_path);
  const native_imports=[...paths].sort().map(relative_path=>({relative_path,imports:plan.resolved.modules.find(m=>m.relative_path===relative_path)!.imports.map(i=>({specifier:i.specifier,target_path:i.target_path!}))}));
  return {selector:node.selector,kind:'Policy',state:'ready',adapter:'policy',contract_sha256:sha256(canonicalJson(contract)),relative_path:modules[0]!.relative_path,callable,names:contract.inputs.map(p=>p.name),module_paths:[...paths].sort(),cases,recipes,source_predicted_targets:[...targets].sort(),source_predicted_branches:[...branches].sort((a,b)=>a-b),native_imports};
 }catch(error){if(error instanceof RuleFactsCapacity||error instanceof RuleWitnessCapacity)return unmet(error.message.replace('bounded Rule','bounded Policy').replace('bounded record witness Rule','bounded Policy'));throw error;}
}
