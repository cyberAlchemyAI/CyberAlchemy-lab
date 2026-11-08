import type {FieldReferenceModel} from '../input/field-reference-model.js';
import type {TypedRulePolicyContract} from '../typed-backend/policy-rules.js';
import {createStructuredValueRenderer} from './configured-value-types.js';
import {createStructuredValueExpressionRenderer} from './configured-value-expressions.js';
export interface PolicyRuleImport {readonly selector:string;readonly path:string;readonly symbol:string;readonly local:string;}
const q=JSON.stringify,fail=(m:string):never=>{throw Error('DS_CONFIGURED_POLICY:'+m);};
/** Static selection over explicitly generated Rule dependencies. No strategy imports. */
export function renderConfiguredPolicy(contract:TypedRulePolicyContract,model:FieldReferenceModel|null,imports:readonly PolicyRuleImport[]){
 const values=createStructuredValueRenderer(model,fail);let next=0;
 const value=createStructuredValueExpressionRenderer(values,model,()=> 'q'+next++,fail);
 const native=contract.inputs.map(p=>values.ensure(p.type)),scope=new Map(contract.inputs.map((p,i)=>[p.name,{type:p.type,code:'p'+i}]));
 const cases=contract.cases.map(c=>{
  const dependency=imports.find(i=>i.selector===c.rule.selector)??fail('missing Rule import');
  const args=[...c.rule.arguments].sort((a,b)=>a.parameter<b.parameter?-1:1).map(a=>'['+q(a.parameter)+']:'+value(a.value,scope).code);
  return '  if('+dependency.local+'({'+args.join(',')+'}))return '+q(c.target)+';\n';
 }).join('');
 const strategies=[...new Set([...contract.cases.map(c=>c.target),contract.default_target])].sort();
 const body=
  'export const select = (parameters:Readonly<{'+contract.inputs.map((p,i)=>'readonly '+q(p.name)+':'+native[i]!.input).join(';')+'}>):'+strategies.map(s=>q(s)).join('|')+' => {\n'+
  '  const d=ruleData(parameters,'+q(contract.inputs.map(p=>p.name))+');\n'+
  '  if(Object.keys(d).length!=='+contract.inputs.length+')throw new TypeError("POLICY_INPUT");\n'+
  contract.inputs.map((p,i)=>'  const p'+i+' = '+native[i]!.protocol+'.normalize(d['+q(p.name)+']!.value);\n').join('')+
  cases+'  return '+q(contract.default_target)+';\n};\n';
 return imports.map(i=>'import {'+i.symbol+' as '+i.local+'} from '+q(i.path)+';\n').join('')+values.source(body).replaceAll('RULE_INPUT','POLICY_INPUT');
}
