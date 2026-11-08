import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {MappingControls} from './reconciled-mapping-controls.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import {createOperationBinding} from './reconciled-operation-binding.js';
import {createOperationCases,isOperationCapacity} from './reconciled-operation-cases.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';

export const SEMANTIC_OPERATION_DEFINITION_SHA256='154ea235c163bc7d9cf39335904a409147b423be431a0d43b8814f18eb1eae21';
export interface OperationControls extends Omit<MappingControls,'kind'|'adapter'>{readonly kind:'Operation';readonly adapter:'operation';}
export function createOperationEffectAudit(graph:CompiledProjectGraph,plan:ReconciledProjectPlan){
 const nodes=graph.nodes.filter(n=>n.kind==='Operation'),module_paths=[...new Set(nodes.flatMap(n=>createOperationBinding(n,graph,plan).module_paths))].sort();
 const runtime=plan.selection.module_root+'/runtime/enum.ts';
 return {definition_sha256:SEMANTIC_OPERATION_DEFINITION_SHA256,roots:nodes.map(n=>n.selector).sort(),module_paths,
  support_modules:module_paths.filter(p=>p===runtime).map(relative_path=>({relative_path,source_sha256:sha256(getReconciledSource('enum_provider'))}))};
}
export function createOperationControls(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan):OperationControls|Readonly<{selector:string;kind:'Operation';state:'not_evaluable';reason:string}>{
 try{
  const binding=createOperationBinding(node,graph,plan),control=createOperationCases(graph,plan,binding);
  const descriptor:SemanticCase={id:'binding',mode:'operation-descriptor',format:'string',values:[],expected:{kind:'value',value:canonicalJson(binding.descriptor)}};
  return {selector:node.selector,kind:'Operation',state:'ready',adapter:'operation',contract_sha256:sha256(canonicalJson(binding.action.bindings)),
   relative_path:binding.relative_path,callable:binding.callable,module_paths:binding.module_paths,native_imports:binding.native_imports,
   names:[...binding.action.bindings.inputs.map(p=>p.name),...binding.action.events.map(e=>e.parameter)],cases:[descriptor,...control.cases],recipes:control.recipes};
 }catch(e){if(isOperationCapacity(e))return {selector:node.selector,kind:'Operation',state:'not_evaluable',reason:e.message};throw e;}
}
