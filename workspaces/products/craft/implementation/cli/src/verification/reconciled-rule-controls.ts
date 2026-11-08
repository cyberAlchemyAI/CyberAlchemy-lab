import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {createRuleFacts,RuleFactsCapacity,type FactRecipe} from './reconciled-rule-facts.js';
import {RuleWitnessCapacity} from './reconciled-rule-reference.js';
import {createStructuralCases} from './reconciled-structural-cases.js';
export const SEMANTIC_RULE_DEFINITION_SHA256='5a92d59563038bc72989be9b75bf18b87de51d203f9e75b3efc6cfedc44610e9';
export interface RuleControls {
 readonly selector:string;readonly kind:'Rule';readonly state:'ready';readonly adapter:'rule';
 readonly contract_sha256:string;readonly relative_path:string;readonly callable:string;readonly names:readonly string[];
 readonly module_paths:readonly string[];readonly cases:readonly SemanticCase[];readonly recipes:readonly FactRecipe[];
}
export function createRuleSemanticCases(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph){
 const facts=createRuleFacts(graph,node.selector),{reference,rule}=facts,parameters=rule.parameters;
 const {cases,recipes}=createStructuralCases(parameters,facts,args=>String(reference.evaluate(node.selector,args)));
 return {rule,parameters,cases,recipes};
}
export function createRuleControls(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan):RuleControls|Readonly<{selector:string;kind:'Rule';state:'not_evaluable';reason:string}>{
 try{
  const {rule,parameters,cases,recipes}=createRuleSemanticCases(node,graph);
  const callable='rule'+node.selector.split(':')[1]!.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
  const modules=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(node.selector)&&m.exports.some(e=>e.name===callable&&e.kind==='value'));
  if(modules.length!==1)throw new TypeError('DS_RULE_CONTROLS:unique native Rule module required');
  const paths=new Set<string>(),visit=(p:string)=>{if(paths.has(p))return;paths.add(p);const m=plan.resolved.modules.find(m=>m.relative_path===p);if(!m)throw new TypeError('DS_RULE_CONTROLS:missing native closure');for(const i of m.imports){if(!i.target_path)throw new TypeError('DS_RULE_CONTROLS:external Rule dependency');visit(i.target_path);}};visit(modules[0]!.relative_path);
  return {selector:node.selector,kind:'Rule',state:'ready',adapter:'rule',contract_sha256:sha256(canonicalJson(rule)),relative_path:modules[0]!.relative_path,callable,names:parameters.map(p=>p.name),module_paths:[...paths].sort(),cases,recipes};
 }catch(error){if(error instanceof RuleFactsCapacity||error instanceof RuleWitnessCapacity)return {selector:node.selector,kind:'Rule',state:'not_evaluable',reason:error.message};throw error;}
}
