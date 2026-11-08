import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {PolicyControls} from './reconciled-policy-controls.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import {decodeTypedStateMachineContract} from '../typed-backend/state-machine.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {createStructuralFacts,RuleFactsCapacity,type FactRecipe} from './reconciled-rule-facts.js';
import {createStructuralCases} from './reconciled-structural-cases.js';
import {RuleWitnessCapacity} from './reconciled-rule-reference.js';
export const SEMANTIC_STATE_MACHINE_DEFINITION_SHA256='da9a3a504fded187bdd6b6956b6695736598f48564c6d85aba396fa9b7688ffb';
export interface StateMachineControls extends Omit<PolicyControls,'kind'|'adapter'|'source_predicted_targets'|'source_predicted_branches'>{
 readonly kind:'State Machine';readonly adapter:'state-machine';readonly declared_pair_count:number;
 readonly source_predicted_transitions:readonly string[];
}
export function createStateMachineSemanticCases(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph){
 const unmet=(reason:string)=>({selector:node.selector,kind:'State Machine' as const,state:'not_evaluable' as const,reason});
 try{
  const contract=decodeTypedStateMachineContract(node.body.typed_contract),guards=contract.transitions.flatMap(t=>t.guard?[t.guard]:[]);
  const states=[...contract.states].sort(),triggers=[...new Set(contract.transitions.map(t=>t.trigger_event_ref))].sort();
  const pairs=states.flatMap(state=>triggers.map(trigger=>({state,trigger,transition:contract.transitions.find(t=>t.source_state===state&&t.trigger_event_ref===trigger)})));
  const capacity=()=>{throw new RuleFactsCapacity('bounded State Machine case capacity exceeded');};
  if(pairs.length>4096)capacity();
  const facts=createStructuralFacts(graph,guards.map(g=>g.selector),guards.flatMap(g=>g.arguments.map(a=>a.value)));
  const transitions=new Set<string>();let predictions=0;
  const structural=createStructuralCases(contract.inputs,facts,args=>{
   predictions+=pairs.length;if(predictions>4096)capacity();
   return canonicalJson(pairs.map(({state,transition:t})=>{
    if(!t)return {status:'rejected',state,reason:'no-transition',output_intents:[]};
    if(t.guard&&!facts.reference.guard(t.guard,args))return {status:'rejected',state,reason:'guard',output_intents:[]};
    transitions.add(t.transition_id);return {status:'transitioned',state:t.target_state,transition_id:t.transition_id,output_intents:t.output_intents};
   }));
  },'state-machine','STATE_MACHINE_INPUT');
  if(structural.cases.length*pairs.length+1>4096)capacity();
  const cases:SemanticCase[]=[{id:'case-0',mode:'initial-state',format:'string',values:[],expected:{kind:'value',value:contract.initial}}];
  const symbol=(value:string):FactRecipe=>({tag:'scalar',format:'string',value});
  const push=(recipe:string,state:FactRecipe,trigger:FactRecipe,expected:SemanticCase['expected'])=>{
   if(cases.length>=4096)capacity();
   cases.push({id:'case-'+cases.length,mode:'state-machine',format:'string',values:[recipe,canonicalJson(state),canonicalJson(trigger)],expected});
  };
  for(const c of structural.cases){
   const expected=c.expected.kind==='value'?JSON.parse(c.expected.value):null;
   for(const [i,pair]of pairs.entries())push(c.values[0]!,symbol(pair.state),symbol(pair.trigger),expected?{kind:'value',value:canonicalJson(expected[i])}:c.expected);
  }
  const baseline=structural.cases.find(c=>c.expected.kind==='value')!;
  const inputError={kind:'error' as const,name:'TypeError' as const,message:'STATE_MACHINE_INPUT'};
  for(const side of ['state','trigger']){
   const valid=symbol(side==='state'?states[0]!:triggers[0]!);
   const invalid:FactRecipe[]=[symbol('__semantic_unknown__'),...['null','undefined','number','boolean','array','object','coercion'].map(mode=>({tag:'bad' as const,base:valid,mode}))];
   for(const value of invalid)push(baseline.values[0]!,side==='state'?value:symbol(states[0]!),side==='trigger'?value:symbol(triggers[0]!),inputError);
  }
  return {selector:node.selector,kind:'State Machine' as const,state:'ready' as const,contract,contract_sha256:sha256(canonicalJson(contract)),names:contract.inputs.map(p=>p.name),cases,recipes:structural.recipes,declared_pair_count:pairs.length,source_predicted_transitions:[...transitions].sort()};
 }catch(error){if(error instanceof RuleFactsCapacity||error instanceof RuleWitnessCapacity)return unmet(error.message.replace('bounded Rule','bounded State Machine').replace('bounded record witness Rule','bounded State Machine'));throw error;}
}

export function createStateMachineControls(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan):StateMachineControls|Readonly<{selector:string;kind:'State Machine';state:'not_evaluable';reason:string}>{
 const shared=createStateMachineSemanticCases(node,graph);
 if(shared.state!=='ready')return shared;
 const {contract,...cases}=shared;
  const callable='transition'+node.selector.split(':')[1]!.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
  const modules=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(node.selector)&&m.exports.some(e=>e.name===callable&&e.kind==='value'));
  if(modules.length!==1)throw new TypeError('DS_STATE_MACHINE_CONTROLS:unique native reducer required');
  const paths=new Set<string>(),visit=(p:string)=>{
   if(paths.has(p))return;paths.add(p);
   const m=plan.resolved.modules.find(m=>m.relative_path===p);
   if(!m)throw new TypeError('DS_STATE_MACHINE_CONTROLS:missing native closure');
   if(m.qualified_selectors.some(s=>!['Rule','State Machine'].includes(graph.nodes.find(n=>n.selector===s)!.kind)))throw new TypeError('DS_STATE_MACHINE_CONTROLS:Event, Operation or factory dependency forbidden');
   for(const i of m.imports){if(!i.target_path)throw new TypeError('DS_STATE_MACHINE_CONTROLS:external dependency');visit(i.target_path);}
  };visit(modules[0]!.relative_path);
  const native_imports=[...paths].sort().map(relative_path=>({relative_path,imports:plan.resolved.modules.find(m=>m.relative_path===relative_path)!.imports.map(i=>({specifier:i.specifier,target_path:i.target_path!}))}));
 return {...cases,adapter:'state-machine',relative_path:modules[0]!.relative_path,callable,module_paths:[...paths].sort(),native_imports};
}
