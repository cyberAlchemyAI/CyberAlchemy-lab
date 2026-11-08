import {decodeTypedType,decodeValueExpression,type TypedParameter,type TypedRuleContract,type ValueExpression} from '../typed-operation/contracts.js';
import {createTypedValueChecker,type TypedValueDeclaration} from '../typed-operation/value-bindings.js';
import {canonicalJson} from '../input/source-manifest.js';
export const TYPED_POLICY_RULES_VERSION='domainspec.typed-policy/v2' as const;
export interface PolicyRuleReference {
 readonly selector:string;
 readonly arguments:readonly Readonly<{parameter:string;value:ValueExpression}>[];
}
export interface TypedRulePolicyContract {
 readonly schema_version:typeof TYPED_POLICY_RULES_VERSION;
 readonly ontology_policy:string;
 readonly inputs:readonly TypedParameter[];
 readonly cases:readonly Readonly<{target:string;rule:PolicyRuleReference}>[];
 readonly default_target:string;
}
const fail=(message:string):never=>{throw Error('MTCLI_TYPED_POLICY:'+message);};
const local=/^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/,selector=/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/,ontology=/^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$/;
export function assertPolicyData(value:unknown,depth=0):void{
 if(depth>64)fail('contract depth');
 if(value===null||typeof value==='string'||typeof value==='boolean'||typeof value==='number'&&Number.isFinite(value))return;
 if(!value||typeof value!=='object')fail('JSON data required');
 const v=value as object,array=Array.isArray(v),proto=Object.getPrototypeOf(v);
 if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)fail('plain data required');
 const d=Object.getOwnPropertyDescriptors(v);
 if(array&&(Reflect.ownKeys(d).length!==(v as unknown[]).length+1||Array.from({length:(v as unknown[]).length},(_,i)=>d[String(i)]).some(x=>!x)))fail('dense array required');
 for(const key of Reflect.ownKeys(d)){if(array&&key==='length')continue;const p=d[key as string];if(typeof key!=='string'||!p||!Object.hasOwn(p,'value')||!p.enumerable)fail('data properties required');assertPolicyData(p!.value,depth+1);}
}
const keys=(value:unknown,names:readonly string[]):Record<string,unknown>=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).length!==names.length||names.some(k=>!Object.hasOwn(value,k)))fail('closed contract fields required');
 return value as Record<string,unknown>;
};
const id=(v:unknown,pattern:RegExp):string=>typeof v==='string'&&pattern.test(v)?v:fail('invalid identifier');
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};
export function decodeTypedRulePolicyContract(value:unknown):TypedRulePolicyContract{
 assertPolicyData(value);const c=keys(value,['schema_version','ontology_policy','inputs','cases','default_target']);
 if(c.schema_version!==TYPED_POLICY_RULES_VERSION)fail('unsupported Policy schema');
 if(!Array.isArray(c.inputs)||c.inputs.length>128||!Array.isArray(c.cases)||!c.cases.length||c.cases.length>256)fail('input/case limits');
 const inputs=(c.inputs as unknown[]).map(v=>{const p=keys(v,['name','type']);return {name:id(p.name,local),type:decodeTypedType(p.type)};});
 if(new Set(inputs.map(p=>p.name)).size!==inputs.length)fail('duplicate inputs');
 const cases=(c.cases as unknown[]).map(v=>{
  const row=keys(v,['target','rule']),r=keys(row.rule,['selector','arguments']);
  if(!Array.isArray(r.arguments)||r.arguments.length>128)fail('argument limits');
  const args=(r.arguments as unknown[]).map(v=>{const a=keys(v,['parameter','value']);return {parameter:id(a.parameter,local),value:decodeValueExpression(a.value,'/typed_contract/cases/rule/arguments',true)};});
  if(new Set(args.map(a=>a.parameter)).size!==args.length)fail('duplicate Rule arguments');
  return {target:id(row.target,selector),rule:{selector:id(r.selector,selector),arguments:args}};
 });
 return freeze({schema_version:TYPED_POLICY_RULES_VERSION,ontology_policy:id(c.ontology_policy,ontology),inputs,cases,default_target:id(c.default_target,selector)});
}
export function checkTypedRulePolicy(contract:TypedRulePolicyContract,declarations:readonly TypedValueDeclaration[],rules:readonly Readonly<{selector:string;contract:TypedRuleContract}>[]){
 const checker=createTypedValueChecker(declarations,fail),scope=new Map(contract.inputs.map(p=>[p.name,p.type])),available=new Map(rules.map(r=>[r.selector,r.contract]));
 contract.inputs.forEach(p=>checker.checkType(p.type));
 for(const c of contract.cases){
  const rule=available.get(c.rule.selector)??fail('unresolved declared Rule:'+c.rule.selector);
  const args=new Map(c.rule.arguments.map(a=>[a.parameter,a.value]));
  if(args.size!==rule.parameters.length||rule.parameters.some(p=>!args.has(p.name)))fail('Rule arguments must bind exactly:'+c.rule.selector);
  for(const p of rule.parameters)if(canonicalJson(checker.infer(args.get(p.name)!,scope))!==canonicalJson(p.type))fail('Rule argument type mismatch:'+c.rule.selector+':'+p.name);
 }
 return contract;
}
