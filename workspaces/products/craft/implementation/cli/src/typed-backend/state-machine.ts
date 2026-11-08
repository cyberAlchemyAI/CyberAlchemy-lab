import {decodeTypedType,decodeValueExpression,type TypedParameter,type TypedRuleContract,type ValueExpression} from '../typed-operation/contracts.js';
import {createTypedValueChecker,type TypedValueDeclaration} from '../typed-operation/value-bindings.js';
import {canonicalJson} from '../input/source-manifest.js';

export const TYPED_STATE_MACHINE_VERSION='domainspec.typed-state-machine/v1' as const;
export const STATE_MACHINE_CONTRACT_SHA256='024cddb7ebf6c61e569053ef48a059b675fe89cbe484bebe93c40fd4b9ef63a8';
export interface StateMachineGuard {
  readonly selector:string;
  readonly arguments:readonly Readonly<{parameter:string;value:ValueExpression}>[];
}
export interface StateMachineTransition {
  readonly transition_id:string;
  readonly source_state:string;
  readonly target_state:string;
  readonly trigger_event_ref:string;
  readonly guard:StateMachineGuard|null;
  readonly output_intents:readonly Readonly<{slot:string;event_ref:string}>[];
}
export interface TypedStateMachineContract {
  readonly schema_version:typeof TYPED_STATE_MACHINE_VERSION;
  readonly ontology_state_machine:string;
  readonly inputs:readonly TypedParameter[];
  readonly states:readonly string[];
  readonly initial:string;
  readonly transitions:readonly StateMachineTransition[];
}
export const stateMachineFail=(message:string):never=>{throw Error('MTCLI_STATE_MACHINE:'+message);};
export const freezeStateMachine=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freezeStateMachine);Object.freeze(v);}return v;};
const local=/^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/,id=/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/,selector=/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/,ontology=/^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$/;
const identifier=(v:unknown,p:RegExp):string=>typeof v==='string'&&v.length<=256&&p.exec(v)?.[0]===v?v:stateMachineFail('invalid identifier');

/** Bounded JSON preflight; ordinary getters/coercion are never evaluated.
 * This is not an isolation boundary against arbitrary Proxy traps. */
export function assertStateMachineData(root:unknown):void {
  let count=0;
  const visit=(v:unknown,depth:number):void=>{
    if(++count>20000||depth>64)stateMachineFail('data limits');
    if(v===null||typeof v==='string'||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return;
    if(!v||typeof v!=='object')stateMachineFail('JSON data required');
    const array=Array.isArray(v),proto=Object.getPrototypeOf(v);
    if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)stateMachineFail('plain data required');
    const d=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(d);
    if(keys.length>2048)stateMachineFail('data limits');
    if(array){const length=d.length!.value;if(length>1024||keys.length!==length+1)stateMachineFail('dense bounded array required');for(let i=0;i<length;i++)if(!Object.hasOwn(d,String(i)))stateMachineFail('dense array required');}
    for(const k of keys){if(array&&k==='length')continue;const p=d[k as string];if(typeof k!=='string'||!p||!Object.hasOwn(p,'value')||!p.enumerable)stateMachineFail('data properties required');visit(p!.value,depth+1);}
  };visit(root,0);
}
export function stateMachineObject(v:unknown,keys:readonly string[]):Record<string,unknown>{
  if(!v||typeof v!=='object'||Array.isArray(v)||canonicalJson(Object.keys(v).sort())!==canonicalJson([...keys].sort()))stateMachineFail('closed contract fields required');
  return v as Record<string,unknown>;
}
function list(v:unknown,min=0):readonly unknown[]{if(!Array.isArray(v)||v.length<min||v.length>128)stateMachineFail('array limits');return v as readonly unknown[];}
function unique(values:readonly string[],label:string):void{if(new Set(values).size!==values.length)stateMachineFail('duplicate '+label);}
export function decodeTypedStateMachineContract(value:unknown):TypedStateMachineContract {
  assertStateMachineData(value);
  const c=stateMachineObject(value,['schema_version','ontology_state_machine','inputs','states','initial','transitions']);
  if(c.schema_version!==TYPED_STATE_MACHINE_VERSION)stateMachineFail('unsupported schema');
  const states=list(c.states,1).map(s=>identifier(s,id)),initial=identifier(c.initial,id);unique(states,'state');
  if(!states.includes(initial))stateMachineFail('initial state is not declared');
  const inputs=list(c.inputs).map(v=>{const p=stateMachineObject(v,['name','type']);return {name:identifier(p.name,local),type:decodeTypedType(p.type)};});unique(inputs.map(p=>p.name),'input');
  const transitions=list(c.transitions,1).map(v=>{
    const t=stateMachineObject(v,['transition_id','source_state','target_state','trigger_event_ref','guard','output_intents']);
    const source_state=identifier(t.source_state,id),target_state=identifier(t.target_state,id);
    if(!states.includes(source_state)||!states.includes(target_state))stateMachineFail('transition state is not declared');
    let guard:StateMachineGuard|null=null;
    if(t.guard!==null){
      const g=stateMachineObject(t.guard,['selector','arguments']);
      const args=list(g.arguments).map(v=>{const a=stateMachineObject(v,['parameter','value']);return {parameter:identifier(a.parameter,local),value:decodeValueExpression(a.value,'/guard/arguments',true)};});
      unique(args.map(a=>a.parameter),'guard argument');guard={selector:identifier(g.selector,selector),arguments:args};
    }
    const output_intents=list(t.output_intents).map(v=>{const o=stateMachineObject(v,['slot','event_ref']);return {slot:identifier(o.slot,id),event_ref:identifier(o.event_ref,selector)};});unique(output_intents.map(o=>o.slot),'output slot');
    return {transition_id:identifier(t.transition_id,id),source_state,target_state,trigger_event_ref:identifier(t.trigger_event_ref,selector),guard,output_intents};
  });
  unique(transitions.map(t=>t.transition_id),'transition');
  unique(transitions.map(t=>canonicalJson([t.source_state,t.trigger_event_ref])),'state/trigger pair');
  return freezeStateMachine({schema_version:TYPED_STATE_MACHINE_VERSION,ontology_state_machine:identifier(c.ontology_state_machine,ontology),inputs,states,initial,transitions});
}

export function checkTypedStateMachine(contract:TypedStateMachineContract,declarations:readonly TypedValueDeclaration[],nodes:readonly Readonly<{selector:string;kind:string;rule:TypedRuleContract|null}>[]):void {
  const checker=createTypedValueChecker(declarations,stateMachineFail),scope=new Map(contract.inputs.map(p=>[p.name,p.type])),available=new Map(nodes.map(n=>[n.selector,n]));
  contract.inputs.forEach(p=>checker.checkType(p.type));
  for(const t of contract.transitions){
    for(const ref of [t.trigger_event_ref,...t.output_intents.map(o=>o.event_ref)])if(available.get(ref)?.kind!=='Event')stateMachineFail('Event reference must resolve:'+ref);
    if(t.guard){
      const node=available.get(t.guard.selector),rule=node?.rule;
      if(node?.kind!=='Rule'||!rule||!['domainspec.typed-rule/v1','domainspec.typed-rule/v2'].includes(rule.schema_version))stateMachineFail('declared typed Rule required:'+t.guard.selector);
      const parameters=rule!.parameters,args=new Map(t.guard.arguments.map(a=>[a.parameter,a.value]));
      if(args.size!==parameters.length||parameters.some(p=>!args.has(p.name)))stateMachineFail('exact Rule arguments required');
      for(const p of parameters)if(canonicalJson(checker.infer(args.get(p.name)!,scope))!==canonicalJson(p.type))stateMachineFail('Rule argument type mismatch:'+p.name);
    }
  }
}
