import {decodeTypedType,decodeValueExpression,type TypedParameter,type TypedType,type TypedProperty,type TypedRecordContract,type TypedSumContract,type ValueExpression} from '../typed-operation/contracts.js';
import {createTypedValueChecker,type TypedValueDeclaration} from '../typed-operation/value-bindings.js';
import {canonicalJson} from '../input/source-manifest.js';

export const TYPED_MAPPING_INPUTS_VERSION='domainspec.typed-mapping/v2' as const;
export interface TypedInputMappingContract {
  readonly schema_version:typeof TYPED_MAPPING_INPUTS_VERSION;
  readonly ontology_mapping:string;
  readonly inputs:readonly TypedParameter[];
  readonly target:string;
  readonly fields:readonly Readonly<{target:string;value:ValueExpression;default:ValueExpression|null}>[];
  readonly total:boolean;
}
export type MappingDeclaration=TypedValueDeclaration;
const fail=(message:string):never=>{throw new Error('MTCLI_TYPED_MAPPING:'+message);};
const local=/^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/,selector=/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/,ontology=/^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+(?:#[A-Za-z][A-Za-z0-9_]*)?$/;
function data(value:unknown,depth=0):void {
  if(depth>64)fail('contract depth');
  if(value===null||typeof value==='string'||typeof value==='boolean'||typeof value==='number'&&Number.isFinite(value))return;
  if(!value||typeof value!=='object')fail('JSON data required');
  const v=value as object,array=Array.isArray(v),proto=Object.getPrototypeOf(v);
  if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)fail('plain data required');
  const d=Object.getOwnPropertyDescriptors(v);
  if(array&&(Reflect.ownKeys(d).length!==(v as unknown[]).length+1||Array.from({length:(v as unknown[]).length},(_,i)=>d[String(i)]).some(x=>!x)))fail('dense arrays required');
  for(const key of Reflect.ownKeys(d)){if(array&&key==='length')continue;const p=d[key as string];if(typeof key!=='string'||!p||!Object.hasOwn(p,'value')||!p.enumerable)fail('data properties required');data(p!.value,depth+1);}
}
function keys(value:unknown,names:readonly string[]):Record<string,unknown>{
  if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).length!==names.length||names.some(k=>!Object.hasOwn(value,k)))fail('closed contract fields required');
  return value as Record<string,unknown>;
}
const name=(value:unknown,pattern:RegExp):string=>typeof value==='string'&&pattern.test(value)?value:fail('invalid identifier');
const freeze=<T>(value:T):T=>{if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.values(value).forEach(freeze);Object.freeze(value);}return value;};
export function decodeTypedInputMappingContract(value:unknown):TypedInputMappingContract {
  data(value);const c=keys(value,['schema_version','ontology_mapping','inputs','target','fields','total']);
  if(c.schema_version!==TYPED_MAPPING_INPUTS_VERSION||typeof c.total!=='boolean')fail('unsupported Mapping schema or totality');
  if(!Array.isArray(c.inputs)||c.inputs.length>128||!Array.isArray(c.fields)||!c.fields.length||c.fields.length>256)fail('input/field limits');
  const inputs=(c.inputs as unknown[]).map(v=>{const p=keys(v,['name','type']);return {name:name(p.name,local),type:decodeTypedType(p.type)};});
  const fields=(c.fields as unknown[]).map(v=>{const f=keys(v,['target','value','default']);return {target:name(f.target,local),value:decodeValueExpression(f.value,'/typed_contract/fields/value',true),default:f.default===null?null:decodeValueExpression(f.default,'/typed_contract/fields/default',true)};});
  if(new Set(inputs.map(p=>p.name)).size!==inputs.length||new Set(fields.map(f=>f.target)).size!==fields.length)fail('duplicate input or target field');
  return freeze({schema_version:TYPED_MAPPING_INPUTS_VERSION,ontology_mapping:name(c.ontology_mapping,ontology),inputs,target:name(c.target,selector),fields,total:c.total as boolean});
}
export const sameMappingType=(a:TypedType,b:TypedType):boolean=>canonicalJson(a)===canonicalJson(b);
export const assignableMappingType=(actual:TypedType,target:TypedType):boolean=>sameMappingType(actual,target)||target.kind==='optional'&&sameMappingType(actual,target.element);

/** Semantic input/field checking without code generation, factories or graph-edge synthesis. */
export function checkTypedInputMapping(contract:TypedInputMappingContract,declarations:readonly MappingDeclaration[]){
  const checker=createTypedValueChecker(declarations,fail),target=checker.get(contract.target);
  if(target.kind==='Enum')return fail('Mapping target must have record fields');
  contract.inputs.forEach(p=>checker.checkType(p.type));
  const scope=new Map(contract.inputs.map(p=>[p.name,p.type]));
  const infer=(v:ValueExpression)=>checker.infer(v,scope);
  const targetFields=target.contract.properties;
  const bindings=contract.fields.map(f=>{
    const field=targetFields.find(p=>p.name===f.target)??fail('unknown target field:'+f.target);
    const actual=infer(f.value);
    if(f.default===null){if(!assignableMappingType(actual,field.type))fail('field type mismatch:'+f.target);}
    else{
      if(actual.kind!=='optional')return fail('default requires a nullable value:'+f.target);
      if(!assignableMappingType(actual.element,field.type)||!assignableMappingType(infer(f.default),field.type))fail('default type mismatch:'+f.target);
    }
    return {field,value:f.value,default:f.default,value_type:actual};
  });
  if(contract.total&&bindings.length!==targetFields.length)fail('total Mapping must cover every target field');
  return freeze({inputs:contract.inputs,target:target.selector,target_kind:target.kind,bindings});
}
