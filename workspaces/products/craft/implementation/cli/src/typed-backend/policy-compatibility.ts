import {decodeTypedPolicyContract,type BackendPredicate,type BackendValue} from './contracts.js';
import {assertPolicyData,decodeTypedRulePolicyContract} from './policy-rules.js';
import {decodeTypedRuleContract,type RuleExpression,type ValueExpression} from '../typed-operation/contracts.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
const fail=(m:string):never=>{throw Error('MTCLI_POLICY_MIGRATION:'+m);};
/** Explicit, non-writing extraction: callers own new Rule names and graph registration. */
export function migrateTypedPolicyV1(source:unknown,names:readonly Readonly<{selector:string;ontology_rule:string}>[]){
 assertPolicyData(source);assertPolicyData(names);
 const legacy=decodeTypedPolicyContract(source);
 if(names.length!==legacy.cases.length||names.some(n=>Object.keys(n).sort().join('|')!=='ontology_rule|selector')||new Set(names.map(n=>n.selector)).size!==names.length||new Set(names.map(n=>n.ontology_rule)).size!==names.length)fail('one distinct named Rule binding is required per case');
 const parameters=new Map(legacy.inputs.map(p=>[p.name,p.type]));
 const value=(v:BackendValue):ValueExpression=>{
  if(v.kind==='literal')return {op:'literal',type:v.type,value:v.type==='UInt64'?String(v.value):v.value};
  if(v.kind!=='parameter'||!parameters.has(v.name))return fail('legacy value must name a declared Policy input');
  return {op:'path',root:v.name,properties:[]};
 };
 const type=(v:BackendValue)=>v.kind==='literal'?v.type:v.kind==='parameter'?parameters.get(v.name):null;
 const scalarType=(v:BackendValue)=>{const t=type(v);return typeof t==='string'?t:t?.kind==='scalar'?t.name:fail('scalar legacy comparison required');};
 const predicate=(p:BackendPredicate):RuleExpression=>{
  if(p.op==='all'||p.op==='any')return {op:p.op,terms:p.terms.map(predicate)};
  if(p.op==='not')return {op:'not',term:predicate(p.term)};
  if(!('left' in p))return fail('unsupported legacy predicate');
  const l=scalarType(p.left),r=scalarType(p.right);if(l!==r)fail('coercive or mismatched legacy operands require an explicit semantic decision');
  if(p.op!=='eq'&&l==='Bool')fail('legacy ordered Boolean comparison is unsupported');
  const left=value(p.left),right=value(p.right),eq:RuleExpression={op:'eq',left,right};
  const less=(a:ValueExpression,b:ValueExpression):RuleExpression=>({op:'lt',left:a,right:b});
  if(p.op==='eq')return eq;
  if(p.op==='lt')return less(left,right);
  if(p.op==='gt')return less(right,left);
  return {op:'any',terms:[p.op==='lte'?less(left,right):less(right,left),eq]};
 };
 const rules=legacy.cases.map((c,i)=>({selector:names[i]!.selector,typed_contract:decodeTypedRuleContract({schema_version:'domainspec.typed-rule/v2',ontology_rule:names[i]!.ontology_rule,parameters:legacy.inputs,expression:predicate(c.when)})}));
 const policy=decodeTypedRulePolicyContract({schema_version:'domainspec.typed-policy/v2',ontology_policy:legacy.ontology_policy,inputs:legacy.inputs,cases:legacy.cases.map((c,i)=>({target:c.target,rule:{selector:rules[i]!.selector,arguments:legacy.inputs.map(p=>({parameter:p.name,value:{op:'path',root:p.name,properties:[]}}))}})),default_target:legacy.default_target});
 const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};
 return freeze({schema_version:'domainspec.policy-v1-rule-extraction/v1-candidate',legacy_sha256:sha256(canonicalJson(legacy)),policy,rules,authority_effect:'none',graph_effect:'none',input_validation:'explicit-typed-scalar-data-no-coercion'});
}
