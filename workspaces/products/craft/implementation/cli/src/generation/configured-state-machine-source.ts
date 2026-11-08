import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {stateMachineFail,type TypedStateMachineContract} from '../typed-backend/state-machine.js';
import {createStructuredValueRenderer} from './configured-value-types.js';
import {createStructuredValueExpressionRenderer} from './configured-value-expressions.js';

export interface StateMachineRuleImport {readonly selector:string;readonly path:string;readonly symbol:string;readonly local:string;}
const q=JSON.stringify;
export function renderConfiguredStateMachine(c:TypedStateMachineContract,model:FieldReferenceModel|null,imports:readonly StateMachineRuleImport[]):string {
  const values=createStructuredValueRenderer(model,stateMachineFail);let serial=0;
  const value=createStructuredValueExpressionRenderer(values,model,()=> 'q'+serial++,stateMachineFail);
  const types=c.inputs.map(p=>values.ensure(p.type)),scope=new Map(c.inputs.map((p,i)=>[p.name,{type:p.type,code:'p'+i}]));
  const triggers=[...new Set(c.transitions.map(t=>t.trigger_event_ref))].sort(),states=[...c.states].sort();
  const outputs=(rows:readonly {slot:string;event_ref:string}[])=>'Object.freeze(['+rows.map(o=>'Object.freeze({slot:'+q(o.slot)+',event_ref:'+q(o.event_ref)+'})').join(',')+'] as const)';
  const branches=c.transitions.map(t=>{
    let guard='';
    if(t.guard){const dependency=imports.find(i=>i.selector===t.guard!.selector)??stateMachineFail('missing guard import');
      const args=[...t.guard.arguments].sort((a,b)=>a.parameter<b.parameter?-1:1).map(a=>'['+q(a.parameter)+']:'+value(a.value,scope).code).join(',');
      guard='    if(!'+dependency.local+'({'+args+'}))return Object.freeze({status:"rejected",state,reason:"guard",output_intents:Object.freeze([] as const)});\n';
    }
    return '  if(state==='+q(t.source_state)+'&&trigger==='+q(t.trigger_event_ref)+'){\n'+guard+
      '    return Object.freeze({status:"transitioned",state:'+q(t.target_state)+',transition_id:'+q(t.transition_id)+',output_intents:'+outputs(t.output_intents)+'});\n  }\n';
  }).join('');
  const successes=c.transitions.map(t=>'Readonly<{status:"transitioned";state:'+q(t.target_state)+';transition_id:'+q(t.transition_id)+';output_intents:readonly ['+t.output_intents.map(o=>'Readonly<{slot:'+q(o.slot)+';event_ref:'+q(o.event_ref)+'}>').join(',')+']}>').join('|');
  // Validate a bounded inert tree before generated normalizers traverse inputs.
  const support=`const checkData = (root:unknown):void=>{
  let count=0;
  const visit=(v:unknown,depth:number):void=>{
    if(++count>20000||depth>64)throw new TypeError('STATE_MACHINE_INPUT');
    if(v===null||typeof v==='string'||typeof v==='boolean'||typeof v==='bigint'||typeof v==='number'&&Number.isFinite(v))return;
    if(!v||typeof v!=='object')throw new TypeError('STATE_MACHINE_INPUT');
    const array=Array.isArray(v),proto=Object.getPrototypeOf(v);
    if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)throw new TypeError('STATE_MACHINE_INPUT');
    const d=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(d);
    if(keys.length>2048)throw new TypeError('STATE_MACHINE_INPUT');
    if(array){const length=d.length!.value;if(length>1024||keys.length!==length+1)throw new TypeError('STATE_MACHINE_INPUT');for(let i=0;i<length;i++)if(!Object.hasOwn(d,String(i)))throw new TypeError('STATE_MACHINE_INPUT');}
    for(const k of keys){if(array&&k==='length')continue;const p=d[k as string];if(typeof k!=='string'||!p||!Object.hasOwn(p,'value')||!p.enumerable)throw new TypeError('STATE_MACHINE_INPUT');visit(p.value,depth+1);}
  };visit(root,0);
};
`;
  const body=support+
    'export type State='+states.map(s=>q(s)).join('|')+';\nexport type Trigger='+triggers.map(s=>q(s)).join('|')+';\n'+
    'export type Parameters=Readonly<{'+c.inputs.map((p,i)=>'readonly '+q(p.name)+':'+types[i]!.input).join(';')+'}>;\n'+
    'export type Outcome=('+successes+')|Readonly<{status:"rejected";state:State;reason:"guard"|"no-transition";output_intents:readonly []}>;\n'+
    'export const initialState:State='+q(c.initial)+';\n'+
    'export const reduce=(state:State,trigger:Trigger,parameters:Parameters):Outcome=>{\n'+
    '  if(typeof state!=="string"||!'+q(states)+'.includes(state)||typeof trigger!=="string"||!'+q(triggers)+'.includes(trigger))throw new TypeError("STATE_MACHINE_INPUT");\n'+
    '  checkData(parameters);\n  const d=ruleData(parameters,'+q(c.inputs.map(p=>p.name))+');\n'+
    '  if(Object.keys(d).length!=='+c.inputs.length+')throw new TypeError("STATE_MACHINE_INPUT");\n'+
    c.inputs.map((p,i)=>'  const p'+i+'='+types[i]!.protocol+'.normalize(d['+q(p.name)+']!.value);\n').join('')+
    branches+'  return Object.freeze({status:"rejected",state,reason:"no-transition",output_intents:Object.freeze([] as const)});\n};\n';
  return imports.map(i=>'import {'+i.symbol+' as '+i.local+'} from '+q(i.path)+';\n').join('')+
    values.source(body).replaceAll('RULE_INPUT','STATE_MACHINE_INPUT');
}
