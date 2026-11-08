import type {TypedRuleContract, TypedType, RuleExpression} from '../typed-operation/contracts.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import type {ConfiguredRuleModule} from './configured-rules.js';
import {canonicalJson} from '../input/source-manifest.js';
import {createStructuredValueExpressionRenderer} from './configured-value-expressions.js';
import {createStructuredValueRenderer} from './configured-value-types.js';

// Static source specialization for the checked type algebra. No runtime graph,
// declaration table, invariant execution or reference lookup is emitted.
// Scope/open questions: STRUCTURED-RULE-VALUES.md.
type Bound = Readonly<{type:TypedType;code:string}>;
const fail=(message:string):never=>{throw new Error('DS_CONFIGURED_RULE:'+message);};
const q=JSON.stringify;
export function renderStructuredRule(rule:TypedRuleContract,module:ConfiguredRuleModule,model:FieldReferenceModel|null):string {
  const values=createStructuredValueRenderer(model,fail),{ensure}=values;
  let next=0;const fresh=()=> 'q'+next++;
  const same=(a:TypedType,b:TypedType)=>canonicalJson(a)===canonicalJson(b);
  const value=createStructuredValueExpressionRenderer(values,model,fresh,fail);
  const expression=(node:RuleExpression,scope:ReadonlyMap<string,Bound>):string=>{
    if(node.op==='all'||node.op==='any')return '('+node.terms.map(t=>expression(t,scope)).join(node.op==='all'?' && ':' || ')+')';
    if(node.op==='not')return '!('+expression(node.term,scope)+')';
    if(node.op==='rule_ref'){
      const target=module.imports.find(i=>i.selector===node.selector)??fail('unplanned Rule dependency');
      return target.local+'({'+[...node.arguments].sort((a,b)=>a.parameter<b.parameter?-1:1).map(a=>'['+q(a.parameter)+']:'+value(a.value,scope).code).join(',')+'})';
    }
    if(node.op==='eq'||node.op==='lt'||node.op==='contains'||node.op==='set_equal'){
      const left=value(node.left,scope),right=value(node.right,scope);
      if(node.op==='contains'){
        if((left.type.kind!=='list'&&left.type.kind!=='set')||!same(left.type.element,right.type))return fail('contains type mismatch');
        const key=ensure(right.type).protocol,item=fresh();return left.code+'.some('+item+'=>'+key+'.key('+item+')==='+key+'.key('+right.code+'))';
      }
      if(!same(left.type,right.type))return fail('comparison type mismatch');
      if(node.op==='lt'){
        if(left.type.kind!=='scalar'||left.type.name==='Bool')return fail('lt requires numeric or String operands');return '('+left.code+' < '+right.code+')';
      }
      if(node.op==='set_equal'&&left.type.kind!=='set')return fail('set_equal requires a set');
      const key=ensure(left.type).protocol;return '('+key+'.key('+left.code+') === '+key+'.key('+right.code+'))';
    }
    if(node.op!=='unique'&&node.op!=='exists'&&node.op!=='exactly_one')return fail('unsupported Rule expression');
    const source=value(node.collection,scope);if(source.type.kind!=='list'&&source.type.kind!=='set')return fail('quantifier requires a collection');
    const item=fresh(),nested=new Map(scope);nested.set(node.binding,{type:source.type.element,code:item});
    if(node.op==='unique'){
      if(node.where.op!=='eq'||canonicalJson(node.where.left)!==canonicalJson(node.where.right)||node.where.left.op!=='path')return fail('unique requires an identical path key');
      const key=value(node.where.left,nested);return '(new Set('+source.code+'.map('+item+'=>'+ensure(key.type).protocol+'.key('+key.code+'))).size === '+source.code+'.length)';
    }
    const predicate=expression(node.where,nested);return node.op==='exists'?source.code+'.some('+item+'=>'+predicate+')':'('+source.code+'.filter('+item+'=>'+predicate+').length === 1)';
  };
  const parameters=rule.parameters.map(p=>ensure(p.type));
  const result=expression(rule.expression,new Map(rule.parameters.map((p,i)=>[p.name,{type:p.type,code:'p'+i}])));
  const body=
    '// domainspec-rule: '+q(module.selector)+'; closure: '+module.closure_sha256+'\nexport const '+module.callable+' = (parameters:Readonly<{'+rule.parameters.map((p,i)=>'readonly '+q(p.name)+':'+parameters[i]!.input).join(';')+'}>):boolean => {\n'+
    '  const d=ruleData(parameters,'+q(rule.parameters.map(p=>p.name))+');\n  if(Object.keys(d).length!=='+rule.parameters.length+')throw new TypeError(\'RULE_INPUT\');\n'+
    rule.parameters.map((p,i)=>'  const p'+i+' = '+parameters[i]!.protocol+'.normalize(d['+q(p.name)+']!.value);\n').join('')+'  return '+result+';\n};\n';
  return module.imports.map(i=>'import { '+i.symbol+' as '+i.local+' } from '+q(i.path)+';\n').join('')+values.source(body);
}
