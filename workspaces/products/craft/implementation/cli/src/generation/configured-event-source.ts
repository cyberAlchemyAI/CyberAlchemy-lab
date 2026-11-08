import type {FieldSpec} from '../input/project-model.js';
import type {EventReferenceIdentity} from './event-reference-identity.js';

export interface EventSource {
  readonly description:string;
  readonly event_type:string;
  readonly version:string;
  readonly occurrence_id:FieldSpec;
  readonly occurred_at_policy:'required'|'generated';
  readonly payload:readonly FieldSpec[];
}

// Independent observation pins this perimeter. No schema interpreter is emitted.
export const EVENT_VALUE_SUPPORT = `const eventFail = ():never => {throw new TypeError("EVENT_INPUT");};
const eventData = (value:unknown,allowed:readonly string[],required:readonly string[]):Record<string,PropertyDescriptor> => {
  if(!value||typeof value!=="object"||Array.isArray(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))return eventFail();
  const d=Object.getOwnPropertyDescriptors(value);
  if(Reflect.ownKeys(d).some(k=>typeof k!=="string"||!allowed.includes(k))||Object.values(d).some(p=>!Object.hasOwn(p,"value")||!p.enumerable)||required.some(k=>!Object.hasOwn(d,k)))return eventFail();
  return d;
};
const eventString = (v:unknown):string => typeof v==="string"?v:eventFail();
const eventText = (v:unknown):string => typeof v==="string"&&v.length>0?v:eventFail();
const eventBoolean = (v:unknown):boolean => typeof v==="boolean"?v:eventFail();
const eventDecimal = (v:unknown):number => typeof v==="number"&&Number.isFinite(v)?(Object.is(v,-0)?0:v):eventFail();
const eventInteger = (v:unknown):bigint => {
  let n:bigint;
  if(typeof v==="bigint")n=v;
  else if(typeof v==="number"&&Number.isSafeInteger(v))n=BigInt(v);
  else if(typeof v==="string"&&v.length<=20&&/^(0|-?[1-9][0-9]*)$/.exec(v)?.[0]===v)n=BigInt(v);
  else return eventFail();
  return n>=-9223372036854775808n&&n<=9223372036854775807n?n:eventFail();
};
type EventRef<S extends string> = string & {readonly __domainspecRef?:S};
`;

export function renderEventValueSupport(fields: readonly FieldSpec[], referenceIdentities:ReadonlyMap<string,EventReferenceIdentity>=new Map()): string {
  const scalarNames = new Set(fields.flatMap(field => field.type_ref.kind === 'reference' ? [] : [field.type_ref.name]));
  const references = fields.some(field => field.type_ref.kind === 'reference');
  return `const eventFail = ():never => {throw new TypeError("EVENT_INPUT");};
const eventData = (value:unknown,allowed:readonly string[],required:readonly string[]):Record<string,PropertyDescriptor> => {
  if(!value||typeof value!=="object"||Array.isArray(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))return eventFail();
  const d=Object.getOwnPropertyDescriptors(value);
  if(Reflect.ownKeys(d).some(k=>typeof k!=="string"||!allowed.includes(k))||Object.values(d).some(p=>!Object.hasOwn(p,"value")||!p.enumerable)||required.some(k=>!Object.hasOwn(d,k)))return eventFail();
  return d;
};
${scalarNames.has('string') ? 'const eventString = (v:unknown):string => typeof v==="string"?v:eventFail();\n' : ''}const eventText = (v:unknown):string => typeof v==="string"&&v.length>0?v:eventFail();
${scalarNames.has('boolean') ? 'const eventBoolean = (v:unknown):boolean => typeof v==="boolean"?v:eventFail();\n' : ''}${scalarNames.has('decimal') ? 'const eventDecimal = (v:unknown):number => typeof v==="number"&&Number.isFinite(v)?(Object.is(v,-0)?0:v):eventFail();\n' : ''}${scalarNames.has('integer') ? `const eventInteger = (v:unknown):bigint => {
  let n:bigint;
  if(typeof v==="bigint")n=v;
  else if(typeof v==="number"&&Number.isSafeInteger(v))n=BigInt(v);
  else if(typeof v==="string"&&v.length<=20&&/^(0|-?[1-9][0-9]*)$/.exec(v)?.[0]===v)n=BigInt(v);
  else return eventFail();
  return n>=-9223372036854775808n&&n<=9223372036854775807n?n:eventFail();
};
` : ''}${[...referenceIdentities.values()].some(identity=>identity.scalar==='UInt64') ? `const eventUInt64 = (v:unknown):bigint => {
  let n:bigint;
  if(typeof v==="bigint")n=v;
  else if(typeof v==="number"&&Number.isSafeInteger(v))n=BigInt(v);
  else if(typeof v==="string"&&v.length<=20&&/^(0|[1-9][0-9]*)$/.exec(v)?.[0]===v)n=BigInt(v);
  else return eventFail();
  return n>=0n&&n<=18446744073709551615n?n:eventFail();
};
` : ''}${references ? ([...referenceIdentities.values()].some(identity=>identity.scalar==='UInt64')?'type EventRef<S extends string,V> = V & {readonly __domainspecRef?:S};\n':'type EventRef<S extends string> = string & {readonly __domainspecRef?:S};\n') : ''}`;
}

export function renderConfiguredEvent(source:EventSource,referenceIdentities:ReadonlyMap<string,EventReferenceIdentity>):string {
  const q=JSON.stringify;
  const typedReferences=[...referenceIdentities.values()].some(identity=>identity.scalar==='UInt64');
  const native=(field:FieldSpec,input=false):string=>field.type_ref.kind==='reference'
    ? (identity=>input&&identity.scalar==='UInt64'?'bigint|number|string':'EventRef<'+q(field.type_ref.selector)+(typedReferences?','+(identity.scalar==='UInt64'?'bigint':'string'):'')+'>')(referenceIdentities.get(field.type_ref.selector)!)
    : ({string:'string',boolean:'boolean',integer:input?'bigint|number|string':'bigint',decimal:'number',timestamp:'string',uuid:'string'} as const)[field.type_ref.name];
  const normalize=(field:FieldSpec,expr:string):string=>{
    if(field.type_ref.kind==='reference')return (referenceIdentities.get(field.type_ref.selector)?.scalar==='UInt64'?'eventUInt64':'eventText')+'('+expr+')';
    const fn={string:'eventString',boolean:'eventBoolean',integer:'eventInteger',decimal:'eventDecimal',timestamp:'eventText',uuid:'eventText'}[field.type_ref.name];
    return fn+'('+expr+')';
  };
  const fields=[...source.payload].sort((a,b)=>a.field_id<b.field_id?-1:a.field_id>b.field_id?1:0);
  const shape=(input:boolean)=>fields.map(f=>'readonly '+q(f.field_id)+(f.required?'':'?')+':'+native(f,input)).join(';');
  const occurrence=q(source.occurrence_id.field_id),generated=source.occurred_at_policy==='generated';
  const clock=generated?',clock:()=>string':'';
  const payload=fields.map(f=>{
    const value='['+q(f.field_id)+']:'+normalize(f,'p['+q(f.field_id)+']!.value');
    return f.required?value:'...(Object.hasOwn(p,'+q(f.field_id)+')?{'+value+'}:{})';
  }).join(',');
  return renderEventValueSupport([source.occurrence_id, ...fields],referenceIdentities)+
    'export type EventInput = Readonly<{occurrence:Readonly<{'+occurrence+':'+native(source.occurrence_id,true)+'}>;'+(generated?'':'occurredAt:string;')+'payload:Readonly<{'+shape(true)+'}>}>;\n'+
    'export type EventValue = Readonly<{type:'+q(source.event_type)+';version:'+q(source.version)+';occurrence:Readonly<{'+occurrence+':'+native(source.occurrence_id)+'}>;occurredAt:string;payload:Readonly<{'+shape(false)+'}>}>;\n'+
    'export const make = (input:EventInput'+clock+'):EventValue => {\n'+
    '  const d=eventData(input,'+q(generated?['occurrence','payload']:['occurrence','occurredAt','payload'])+','+q(generated?['occurrence','payload']:['occurrence','occurredAt','payload'])+');\n'+
    '  const o=eventData(d["occurrence"]!.value,['+occurrence+'],['+occurrence+']);\n'+
    '  const p=eventData(d["payload"]!.value,'+q(fields.map(f=>f.field_id))+','+q(fields.filter(f=>f.required).map(f=>f.field_id))+');\n'+
    '  const occurrence=Object.freeze({['+occurrence+']:'+normalize(source.occurrence_id,'o['+occurrence+']!.value')+'});\n'+
    '  const payload=Object.freeze({'+payload+'});\n'+
    (generated?'  if(typeof clock!=="function")return eventFail();\n  const occurredAt=eventText(clock());\n':'  const occurredAt=eventText(d["occurredAt"]!.value);\n')+
    '  return Object.freeze({type:'+q(source.event_type)+',version:'+q(source.version)+',occurrence,occurredAt,payload});\n};\n';
}
