import {decodeTypedType,decodeValueExpression,type ScalarName,type TypedType,type ValueExpression} from '../typed-operation/contracts.js';
import {createTypedValueChecker,type TypedValueDeclaration} from '../typed-operation/value-bindings.js';
import {assertInterfaceData,checkInterfacePublicClosure,type NamedInterfaceContract,type InterfacePublicType} from './interface.js';
import {canonicalJson} from '../input/source-manifest.js';
export const PUBLIC_MAPPING_VERSION='domainspec.typed-mapping/v3';
export const PUBLIC_MAPPING_CONTRACT_SHA256='5de04e24cbd6a137b3f3120b5fbfbba2775339f26cfb3d56498eaf6ae8e067b3';
export const PUBLIC_MAPPING_VALUE_OBJECT_CONTRACT_SHA256='924538cd28276e3076e06c011ce47cbe73c8d232c230ae9d2407f3abf012caf8';
export const isPublicMappingDefinitionSha256=(digest:string):boolean=>digest===PUBLIC_MAPPING_CONTRACT_SHA256||digest===PUBLIC_MAPPING_VALUE_OBJECT_CONTRACT_SHA256;
export type MappingValueType=
 | Readonly<{kind:'scalar';name:ScalarName}>
 | Readonly<{kind:'named';selector:string}>
 | Readonly<{kind:'reference';selector:string;projection:readonly string[]}>
 | Readonly<{kind:'contract';interface_selector:string;contract_id:string}>
 | Readonly<{kind:'optional'|'list'|'set';element:MappingValueType}>
 | Readonly<{kind:'sum';variants:readonly Readonly<{name:string;ontology_variant:string;payload:MappingValueType|null}>[]}>;
export type PublicMappingTarget=Extract<MappingValueType,{kind:'named'|'contract'}>;
export type PublicMemberUse=Readonly<{interface_selector:string;operation_id:string;side:'request'|'result'}>;
export interface PublicMappingContract {
 readonly schema_version:typeof PUBLIC_MAPPING_VERSION;readonly ontology_mapping:string;
 readonly inputs:readonly Readonly<{name:string;type:MappingValueType;use:PublicMemberUse|null}>[];
 readonly target:PublicMappingTarget;readonly target_use:PublicMemberUse|null;
 readonly fields:readonly Readonly<{target:string;value:ValueExpression;default:ValueExpression|null}>[];
 readonly total:boolean;
}
export type MappingInterfaceDeclaration=Readonly<{selector:string;contract:NamedInterfaceContract}>;
const fail=(reason:string):never=>{throw Object.assign(new TypeError('MTCLI_PUBLIC_MAPPING:'+reason),{code:'MTCLI_PUBLIC_MAPPING',exitCode:22});};
const local=/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/,field=/^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
const selector=/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const ontology=/^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+(?:#[A-Za-z][A-Za-z0-9_]*)?$/;
const id=(v:unknown,re:RegExp):string=>typeof v==='string'&&v.length<=256&&re.exec(v)?.[0]===v?v:fail('identifier');
const keys=(v:unknown,names:readonly string[]):Record<string,unknown>=>{
 if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).length!==names.length||names.some(k=>!Object.hasOwn(v,k)))return fail('closed fields');
 return v as Record<string,unknown>;
};
const list=(v:unknown,max:number,min=0):readonly unknown[]=>Array.isArray(v)&&v.length>=min&&v.length<=max?v:fail('list bounds');
const unique=(values:readonly string[])=>{if(new Set(values).size!==values.length)fail('duplicate identity');};
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};
function decodeType(value:unknown,depth=0):MappingValueType{
 if(depth>16)return fail('type depth');
 const v=value as Record<string,unknown>;if(!v||typeof v!=='object')return fail('type');
 if(v.kind==='scalar'||v.kind==='named'||v.kind==='reference')return decodeTypedType(value) as Extract<MappingValueType,{kind:'scalar'|'named'|'reference'}>;
 if(v.kind==='contract'){keys(v,['kind','interface_selector','contract_id']);return {kind:'contract',interface_selector:id(v.interface_selector,selector),contract_id:id(v.contract_id,local)};}
 if(v.kind==='optional'||v.kind==='list'||v.kind==='set'){
  keys(v,['kind','element']);const element=decodeType(v.element,depth+1);if(element.kind==='optional')return fail('nested optional');
  return {kind:v.kind,element};
 }
 if(v.kind==='sum'){
  keys(v,['kind','variants']);const variants=list(v.variants,128,1).map(x=>{
   const p=keys(x,['name','ontology_variant','payload']);return {name:id(p.name,/^[A-Z][A-Za-z0-9]*$/),ontology_variant:id(p.ontology_variant,ontology),payload:p.payload===null?null:decodeType(p.payload,depth+1)};
  });unique(variants.map(v=>v.name));unique(variants.map(v=>v.ontology_variant));return {kind:'sum',variants};
 }
 return fail('unsupported type');
}
function use(v:unknown):PublicMemberUse|null{
 if(v===null)return null;const u=keys(v,['interface_selector','operation_id','side']);
 if(u.side!=='request'&&u.side!=='result')return fail('member side');
 return {interface_selector:id(u.interface_selector,selector),operation_id:id(u.operation_id,local),side:u.side};
}
export function decodePublicMapping(value:unknown):PublicMappingContract{
 assertInterfaceData(value);const c=keys(value,['schema_version','ontology_mapping','inputs','target','target_use','fields','total']);
 if(c.schema_version!==PUBLIC_MAPPING_VERSION||typeof c.total!=='boolean')return fail('version or totality');
 const target=decodeType(c.target);if(target.kind!=='named'&&target.kind!=='contract')return fail('target requires Entity or public contract');
 const inputs=list(c.inputs,128).map(x=>{const p=keys(x,['name','type','use']);return {name:id(p.name,field),type:decodeType(p.type),use:use(p.use)};});
 const fields=list(c.fields,256).map(x=>{const p=keys(x,['target','value','default']);return {target:id(p.target,field),value:decodeValueExpression(p.value,'/mapping/value',true),default:p.default===null?null:decodeValueExpression(p.default,'/mapping/default',true)};});
 unique(inputs.map(p=>p.name));unique(fields.map(p=>p.target));
 return freeze({schema_version:PUBLIC_MAPPING_VERSION,ontology_mapping:id(c.ontology_mapping,ontology),inputs,target,target_use:use(c.target_use),fields,total:c.total});
}
export const publicMappingTargetSelector=(target:PublicMappingTarget):string=>target.kind==='named'?target.selector:target.interface_selector;
export function qualifyPublicType(type:InterfacePublicType,interface_selector:string):MappingValueType{
 if(type.kind==='contract')return {kind:'contract',interface_selector,contract_id:type.contract_id};
 if(type.kind==='scalar'||type.kind==='named')return type;
 if(type.kind==='sum')return {kind:'sum',variants:type.variants.map(v=>({...v,payload:v.payload?qualifyPublicType(v.payload,interface_selector):null}))};
 return {kind:type.kind,element:qualifyPublicType(type.element,interface_selector)};
}
const same=(a:MappingValueType,b:MappingValueType)=>canonicalJson(a)===canonicalJson(b);
const assignable=(a:MappingValueType,b:MappingValueType)=>same(a,b)||b.kind==='optional'&&same(a,b.element);
/** Public identity remains first class; never synthesize a domain record declaration. */
export function checkPublicMapping(contract:PublicMappingContract,declarations:readonly TypedValueDeclaration[],interfaces:readonly MappingInterfaceDeclaration[],allowValueObjectTarget=false){
 const domain=createTypedValueChecker(declarations,fail),apis=new Map(interfaces.map(i=>[i.selector,i.contract]));
 if(apis.size!==interfaces.length)return fail('duplicate Interface');
 const usedInterfaces=new Set<string>(),usedDomains=new Set<string>();
 const api=(selector:string)=>{
  const value=apis.get(selector)??fail('unresolved Interface:'+selector);
  if(!usedInterfaces.has(selector)){checkInterfacePublicClosure(value,declarations);usedInterfaces.add(selector);}
  return value;
 };
 const publicContract=(t:Extract<MappingValueType,{kind:'contract'}>)=>api(t.interface_selector).contracts.find(c=>c.contract_id===t.contract_id)??fail('unresolved public contract');
 const checkType=(t:MappingValueType):void=>{
  if(t.kind==='contract'){publicContract(t);return;}
  if(t.kind==='named'||t.kind==='reference'){domain.checkType(t as TypedType);usedDomains.add(t.selector);return;}
  if(t.kind==='sum')t.variants.forEach(v=>{if(v.payload)checkType(v.payload);});
  else if(t.kind!=='scalar')checkType(t.element);
 };
 const properties=(t:MappingValueType)=>{
  if(t.kind==='contract')return publicContract(t).fields.map(f=>({name:f.name,ontology_property:f.ontology_field,type:qualifyPublicType(f.type,t.interface_selector)}));
  if(t.kind==='named'){
   const d=domain.get(t.selector);usedDomains.add(t.selector);if(d.kind==='Enum')return fail('Enum has no fields');return d.contract.properties;
  }
  if(t.kind==='reference'){
   const d=domain.get(t.selector);usedDomains.add(t.selector);if(d.kind!=='Entity')return fail('reference target must be an Entity');
   const p=d.contract.properties.find(f=>f.name===t.projection[0]&&f.identity)??fail('invalid reference projection');
   return [p];
  }return fail('field requires domain value or public contract; no implicit unwrap');
 };
 const member=(use:PublicMemberUse|null,type:MappingValueType)=>{
  if(use===null)return null;
  const operation=api(use.interface_selector).operations.find(o=>o.operation_id===use.operation_id)??fail('unknown Interface member');
  const expected=qualifyPublicType(operation[use.side],use.interface_selector);
  if(!same(type,expected))return fail('member position type mismatch');
  return {use,operation_ref:operation.operation_ref,type:expected};
 };
 contract.inputs.forEach(p=>checkType(p.type));checkType(contract.target);
 if(contract.target.kind==='named'){
  const kind=domain.get(contract.target.selector).kind;
  if(kind!=='Entity'&&!(allowValueObjectTarget&&kind==='Value Object'))return fail(allowValueObjectTarget?'canonical maps target must be Entity, Value Object or Interface':'canonical maps target must be Entity or Interface');
 }
 const scope=new Map(contract.inputs.map(p=>[p.name,p.type]));
 const infer=(v:ValueExpression):MappingValueType=>{
  if(v.op==='literal')return domain.infer(v,new Map());
  if(v.op==='variant'){const type=domain.infer(v,new Map());checkType(type);return type;}
  if(v.op==='to_set'){const type=infer(v.value);if(type.kind!=='list')return fail('to_set requires list');return {kind:'set',element:type.element};}
  let current=scope.get(v.root)??fail('undeclared Mapping input');
  for(const property of v.properties){
   const collection=current.kind==='list'||current.kind==='set',owner=collection?(current as Extract<MappingValueType,{element:MappingValueType}>).element:current;
   const p=properties(owner).find(f=>f.ontology_property===property)??fail('unknown ontology field');
   current=collection?{kind:current.kind as 'list'|'set',element:p.type}:p.type;
  }
  return current;
 };
 const targetFields=properties(contract.target),inputs=contract.inputs.map(p=>({...p,member:member(p.use,p.type)}));
 const targetMember=member(contract.target_use,contract.target);
 const fields=contract.fields.map(f=>{
  const target=targetFields.find(p=>p.name===f.target)??fail('unknown target field'),actual=infer(f.value);
  if(f.default===null){if(!assignable(actual,target.type))return fail('field type mismatch:'+f.target);}
  else{
   if(actual.kind!=='optional')return fail('default requires optional');
   if(!assignable(actual.element,target.type)||!assignable(infer(f.default),target.type))return fail('default type mismatch');
  }
  return {target,value:f.value,default:f.default,value_type:actual};
 });
 if(contract.total&&fields.length!==targetFields.length)return fail('total field coverage');
 return freeze({inputs,target:contract.target,target_member:targetMember,target_fields:targetFields,fields,
  interface_selectors:[...usedInterfaces].sort(),domain_selectors:[...usedDomains].sort(),effect_contract:'pure-explicit-projection' as const});
}
