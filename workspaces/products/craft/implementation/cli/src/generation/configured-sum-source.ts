import type {TypedType} from '../typed-operation/contracts.js';
import {renderCollectionSupportFor} from './configured-collection-source.js';
import {renderEnumValueSupport} from './configured-enum-component-source.js';
import {renderUInt64Support} from './configured-uint64-source.js';
import {renderExactUInt64Support} from './configured-exact-uint64-source.js';
import {renderEntitySupport} from './configured-entity-source.js';

// PCR-06 candidate static composition; scope/open questions: SUM-FIELD-FACTORY-GENERATION.md.
export interface ValueImport {
  readonly selector: string; readonly path: string; readonly symbol: string;
  readonly local: string; readonly type_symbol: string; readonly type_local: string;
}
export type ValueShape =
  | Readonly<{kind:'String'|'Bool'|'UInt64'}>
  | Readonly<{kind:'ValueObject'|'Entity'|'Enum'|'Sum'; component:ValueImport}>
  | Readonly<{kind:'optional'|'list'|'set'; element:ValueShape}>
  | Readonly<{kind:'sum'; variants:readonly Readonly<{name:string; ontology_variant:string; payload:ValueShape|null}>[]}>;
export interface ConfiguredSumModule {
  readonly selector:string; readonly relative_path:string; readonly name:string;
  readonly shape:ValueShape; readonly contract_sha256:string;
  readonly uint64_fields?:true;
  readonly exact_uint64?:true;
  readonly entity_fields?:true;
}
export function composeValueShape(type:TypedType, prefix:string,
  resolve:(selector:string,local:string)=>Readonly<{kind:'ValueObject'|'Entity'|'Enum'|'Sum';component:ValueImport}>, allowUInt64=false):ValueShape {
  if(type.kind==='scalar') {
    if(type.name!=='String'&&type.name!=='Bool'&&!(allowUInt64&&type.name==='UInt64'))throw new Error('DS_CONFIGURED_FACTORY:unsupported sum scalar');
    return {kind:type.name};
  }
  if(type.kind==='named')return resolve(type.selector,prefix);
  if(type.kind==='reference')throw new Error('DS_CONFIGURED_FACTORY:reference requires identity resolution');
  if(type.kind==='sum')return {kind:'sum',variants:[...type.variants].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0)
    .map((v,i)=>({name:v.name,ontology_variant:v.ontology_variant,payload:v.payload?composeValueShape(v.payload,prefix+'Case'+i,resolve,allowUInt64):null}))};
  return {kind:type.kind,element:composeValueShape(type.element,prefix+'Element',resolve,allowUInt64)};
}
export function valueDependencies(shape:ValueShape, value_path:readonly string[]=[]):Readonly<{component:ValueImport;value_path:readonly string[]}>[] {
  if('component' in shape)return [{component:shape.component,value_path}];
  if('element' in shape)return valueDependencies(shape.element,[...value_path,shape.kind]);
  if(shape.kind==='sum')return shape.variants.flatMap(v=>v.payload?valueDependencies(v.payload,[...value_path,'variant',v.name,'payload']):[]);
  return [];
}
export function renderValueImports(shape:ValueShape):string {
  return valueDependencies(shape).map(({component:c})=>`import {${c.symbol} as ${c.local}} from ${JSON.stringify(c.path)};\nimport type {${c.type_symbol} as ${c.type_local}} from ${JSON.stringify(c.path)};\n`).join('');
}
export function renderValueType(shape:ValueShape, exact=false, input=false):string {
  if('component' in shape)return shape.component.type_local;
  if('element' in shape)return shape.kind==='optional'?`(${renderValueType(shape.element,exact,input)})|null`:`ReadonlyArray<${renderValueType(shape.element,exact,input)}>`;
  if(shape.kind==='sum')return '('+shape.variants.map(v=>`Readonly<{variant:${JSON.stringify(v.name)}${v.payload?';payload:'+renderValueType(v.payload,exact,input):''}}>`).join('|')+')';
  return shape.kind==='UInt64'?(exact?(input?'bigint|number|string':'bigint'):'number'):shape.kind==='Bool'?'boolean':'string';
}
export function renderValueProtocol(shape:ValueShape):string {
  if('component' in shape)return `${shape.kind==='Entity'?'ownedEntityValue':shape.kind==='Sum'?'ownedSumValue':shape.kind==='Enum'?'enumValue':'ownedValue'}(${shape.component.local})`;
  if('element' in shape)return `${shape.kind}Value(${renderValueProtocol(shape.element)})`;
  if(shape.kind==='sum')return 'sumValue(Object.freeze({'+shape.variants.map(v=>`[${JSON.stringify(v.name)}]:${v.payload?renderValueProtocol(v.payload):'null'}`).join(',')+'}))';
  return shape.kind==='UInt64'?'uint64Value':shape.kind==='Bool'?'boolValue':'stringValue';
}
export function renderSumSupport():string {
  return renderSumSupportFor(['sumValue', 'ownedSumValue']);
}
export function renderSumSupportFor(expressions:readonly string[]):string {
  const source=expressions.join('\n');
  const structural=source.includes('sumValue');
  const owned=source.includes('ownedSumValue');
  return `${structural ? `type SumPayloadProtocol = Readonly<{normalize:(input:unknown)=>unknown;key:(value:never)=>string}>;
type SumCaseOf<P> = {[K in keyof P]:P[K] extends null ? Readonly<{variant:K}> : P[K] extends ValueProtocol<infer T> ? Readonly<{variant:K;payload:T}> : never}[keyof P];
const sumValue = <const P extends Readonly<Record<string,SumPayloadProtocol|null>>>(variants:P):ValueProtocol<SumCaseOf<P>> => {
  const cases = new WeakMap<object,string>();
  return Object.freeze({
    normalize:(input:unknown):SumCaseOf<P>=>{
      if(input === null || typeof input !== 'object' || Array.isArray(input) || ![Object.prototype,null].includes(Object.getPrototypeOf(input))) throw new TypeError('INVALID_SUM');
      const descriptors = Object.getOwnPropertyDescriptors(input);
      if(Reflect.ownKeys(descriptors).some(key=>typeof key !== 'string' || !['variant','payload'].includes(key)) || Object.values(descriptors).some(d=>!Object.hasOwn(d,'value') || !d.enumerable)) throw new TypeError('INVALID_SUM');
      const variant = descriptors.variant?.value;
      if(typeof variant !== 'string' || !Object.hasOwn(variants,variant)) throw new TypeError('INVALID_SUM_VARIANT');
      const protocol = variants[variant]!;
      if(Reflect.ownKeys(descriptors).length !== (protocol === null ? 1 : 2) || (protocol !== null && !Object.hasOwn(descriptors,'payload'))) throw new TypeError('INVALID_SUM_PAYLOAD');
      const payload = protocol === null ? null : protocol.normalize(descriptors.payload!.value);
      const result = Object.freeze(protocol === null ? {variant} : {variant,payload}) as SumCaseOf<P>;
      cases.set(result,part('Sum') + part(variant) + (protocol === null ? part('no-payload') : part('payload') + part(protocol.key(payload as never))));
      return result;
    },
    key:(value:SumCaseOf<P>):string=>{
      const key = cases.get(value);
      if(key === undefined) throw new TypeError('UNOWNED_SUM');
      return key;
    },
  });
};
` : ''}${owned ? `const ownedSumValue = <T>(provider:Readonly<{isOwned:(input:unknown)=>input is T;key:(input:unknown)=>string}>):ValueProtocol<T> => Object.freeze({
  normalize:(input:unknown):T=>{if(!provider.isOwned(input)) throw new TypeError('UNOWNED_SUM_CASE');return input;},
  key:(value:T):string=>part('NamedSum') + part(provider.key(value)),
});
` : ''}`;
}
export function renderConfiguredSum(m:ConfiguredSumModule):string {
  const q=JSON.stringify;
  const shapeProtocol=renderValueProtocol(m.shape);
  return renderValueImports(m.shape)+`const brand:unique symbol = Symbol(${q(m.selector)});
export type ${m.name}Input = ${renderValueType(m.shape,m.exact_uint64,true)};
export type ${m.name}Case = ${m.exact_uint64 ? renderValueType(m.shape,true) : m.name+'Input'} & Readonly<{[brand]:true}>;
const part = (value:string):string => value.length + ':' + value;
${renderCollectionSupportFor([shapeProtocol])+(shapeProtocol.includes('enumValue')?renderEnumValueSupport():'')+renderSumSupportFor([shapeProtocol])+(shapeProtocol.includes('uint64Value')?(m.exact_uint64?renderExactUInt64Support():renderUInt64Support()):'')+(shapeProtocol.includes('ownedEntityValue')?renderEntitySupport():'')}const shapeValue = ${shapeProtocol};
const cases = new WeakMap<object,string>();
const owned = (value:unknown):value is ${m.name}Case => value !== null && typeof value === 'object' && cases.has(value);
export const ${m.name}ValueComponent = Object.freeze({
  protocol_id:'typescript.owned-sum-case/v1-candidate' as const,
  concept:${q(m.selector)},contract_sha256:${q(m.contract_sha256)},
  create:(input:${m.name}Input):${m.name}Case=>{
    const normalized = shapeValue.normalize(input);
    const key = part(${q(m.selector)}) + part(${q(m.contract_sha256)}) + part(shapeValue.key(normalized));
    const result = Object.freeze({...normalized,[brand]:true as const});
    cases.set(result,key);
    return result;
  },
  isOwned:owned,
  key:(value:unknown):string=>{if(!owned(value)) throw new TypeError('UNOWNED_SUM_CASE');return cases.get(value)!;},
  equals:(left:unknown,right:unknown):boolean=>owned(left) && owned(right) && cases.get(left) === cases.get(right),
});
`;
}
