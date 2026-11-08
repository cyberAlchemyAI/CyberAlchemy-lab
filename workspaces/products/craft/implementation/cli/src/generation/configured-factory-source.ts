import type {BoundFactoryValidator, ConfiguredFactoryModule} from './configured-factories.js';
import {renderCollectionSupportFor} from './configured-collection-source.js';
import {renderEnumValueSupport} from './configured-enum-component-source.js';
import {renderSumSupportFor, renderValueImports, renderValueType, renderValueProtocol} from './configured-sum-source.js';
import {renderUInt64Support} from './configured-uint64-source.js';
import {renderExactUInt64Support} from './configured-exact-uint64-source.js';
import {renderReferenceType,renderReferenceImports,renderReferenceDescriptors} from './configured-reference-source.js';
import {renderEntitySupport} from './configured-entity-source.js';

// Source emitter only. The planner owns validation. Scope: FACTORY-GENERATION.md.
export function renderConfiguredFactory(m: ConfiguredFactoryModule): string {
  const q = JSON.stringify, name = m.name, entity = m.kind === 'Entity';
  const identity = m.fields.find(f => f.identity);
  const keyFields = entity ? [identity!] : m.fields;
  const scalarType = (tag: string) => tag === 'Bool' ? 'boolean' : 'string';
  const fieldType = (f: ConfiguredFactoryModule['fields'][number]) => {
    const reference=m.reference_bindings?.find(r=>r.field===f.name);
    return reference ? renderReferenceType(reference) : f.value_shape ? renderValueType(f.value_shape, m.exact_uint64) : (f.wrappers ?? []).reduceRight((type, wrapper) => wrapper === 'optional' ? `(${type})|null` : `ReadonlyArray<${type}>`, f.component?.type_local ?? scalarType(f.tag));
  };
  const tag = (f: ConfiguredFactoryModule['fields'][number]) => f.wrappers?.length ? f.wrappers[0]![0]!.toUpperCase() + f.wrappers[0]!.slice(1) : f.tag;
  const fieldProtocol = (f: ConfiguredFactoryModule['fields'][number]) => f.value_shape ? renderValueProtocol(f.value_shape) : (f.wrappers ?? []).reduceRight((expression, wrapper) => `${wrapper}Value(${expression})`, f.component ? `${f.tag === 'Enum' ? 'enumValue' : 'ownedValue'}(${f.component.local})` : f.tag === 'Bool' ? 'boolValue' : 'stringValue');
  const fieldProtocols = m.fields.map(fieldProtocol);
  const protocolSource = fieldProtocols.join('\n');
  const validator = (v: BoundFactoryValidator) => `Object.freeze({rule:${q(v.rule)},closure_sha256:${q(v.closure_sha256)},artifact_sha256:${q(v.artifact_sha256)},validate:(fields:${name}Fields):boolean=>${v.local}({${v.arguments.map(a => `[${q(a.parameter)}]:${v.fact_views?.[a.parameter] ?? `fields${(a.path ?? [a.field!]).map((p, i) => `${i ? '.fields' : ''}[${q(p)}]`).join('')}`}`).join(',')}})})`;
  const component = (f: ConfiguredFactoryModule['fields'][number]) => `Object.freeze({field:${q(f.name)},tag:${q(tag(f))} as const,value:fields[${q(f.name)}],protocol_id:"typescript.owned-value-component/v1" as const,protocol_sha256:${q(m.component_protocol_sha256)}})`;
  const normalization = m.collections ? `    let fields:${name}Fields;
    try {
      if (input === null || typeof input !== 'object' || Array.isArray(input) || ![Object.prototype,null].includes(Object.getPrototypeOf(input))) return failure('INVALID_FIELDS');
      const descriptors = Object.getOwnPropertyDescriptors(input);
      if (Reflect.ownKeys(descriptors).some(key=>typeof key !== 'string' || !${q(m.fields.map(f => f.name))}.includes(key)) || Object.values(descriptors).some(d=>!Object.hasOwn(d,'value') || !d.enumerable)) return failure('INVALID_FIELDS');
      fields = Object.freeze({${m.fields.map((f, i) => `[${q(f.name)}]:field${i}Value.normalize(Object.hasOwn(descriptors,${q(f.name)}) ? descriptors[${q(f.name)}]!.value : ${f.wrappers?.[0] === 'optional' ? 'null' : 'undefined'})`).join(',')}});
    } catch {return failure('INVALID_FIELDS');}
` : `    if (input === null || typeof input !== 'object' || Array.isArray(input) || ![Object.prototype,null].includes(Object.getPrototypeOf(input))) return failure('INVALID_FIELDS');
    const descriptors = Object.getOwnPropertyDescriptors(input);
    if (Reflect.ownKeys(input).length !== ${m.fields.length} || Object.values(descriptors).some(d=>!Object.hasOwn(d,'value') || !d.enumerable)${m.fields.map(f => f.component ? ` || !${f.component.local}.isOwned(descriptors[${q(f.name)}]?.value)` : ` || typeof descriptors[${q(f.name)}]?.value !== ${q(scalarType(f.tag))}`).join('')}) return failure('INVALID_FIELDS');
    const fields:${name}Fields = Object.freeze({${m.fields.map(f => `[${q(f.name)}]:descriptors[${q(f.name)}]!.value as ${fieldType(f)}`).join(',')}});
`;
  return m.imports.map(i => `import {${i.symbol} as ${i.local}} from ${q(i.path)};\n`).join('') +
    m.fields.flatMap(f => f.value_shape ? [renderValueImports(f.value_shape)] : f.component ? [`import {${f.component.symbol} as ${f.component.local}} from ${q(f.component.path)};\nimport type {${f.component.type_symbol} as ${f.component.type_local}} from ${q(f.component.path)};\n`] : []).join('') +
    (m.reference_bindings ? renderReferenceImports(m.reference_bindings) : '') +
`export interface ${name}Fields {
${m.fields.map(f => `  readonly ${q(f.name)}:${fieldType(f)};`).join('\n')}
}
const brand:unique symbol = Symbol(${q(m.selector)});
${entity ? `const identityBrand:unique symbol = Symbol(${q(m.selector + ':identity')});\n` : ''}type Component = Readonly<{field:string;tag:'String'|'Bool'${m.composed ? "|'ValueObject'" : ''}${m.collections ? "|'Optional'|'List'|'Set'" : ''}${m.enum_fields ? "|'Enum'" : ''}${m.sum_fields ? "|'Sum'" : ''}${m.uint64_fields ? "|'UInt64'" : ''}${m.entity_fields ? "|'Entity'" : ''};value:${m.composed ? 'unknown' : 'string|boolean'};protocol_id:'typescript.owned-value-component/v1';protocol_sha256:string}>;
export interface ${name}Snapshot {
  readonly [brand]:true;
  readonly fields:${name}Fields;
  readonly components:readonly Component[];
  readonly hash:()=>string;
  readonly ${entity ? 'sameIdentity' : 'equals'}:(other:unknown)=>boolean;
${entity ? `  readonly identity:Readonly<{[identityBrand]:true;component:Component}>;\n` : ''}}
type ValidatorTrace = Readonly<{rule:string;closure_sha256:string;artifact_sha256:string;outcome:'pass'|'fail'|'exception'}>;
type Trace = Readonly<{route:string;phases:readonly string[];validators:readonly ValidatorTrace[]}>;
type Result = Readonly<{ok:true;value:${name}Snapshot;failure_codes:readonly string[];trace:Trace}> | Readonly<{ok:false;value:null;failure_codes:readonly string[];trace:Trace}>;
type BoundValidator = Readonly<{rule:string;closure_sha256:string;artifact_sha256:string;validate:(fields:${name}Fields)=>boolean}>;
interface Factory {
  readonly create:(input:unknown)=>Result;
  readonly reconstruct:(input:unknown)=>Result;
${entity ? `  readonly transition:(previous:${name}Snapshot,input:unknown)=>Result;\n` : ''}  readonly extend:(id:string)=>Factory;
  readonly extensions:readonly string[];
}
const snapshots = new WeakMap<object,Readonly<{fields:${name}Fields;key:string}>>();
const owned = (value:unknown):value is ${name}Snapshot => value !== null && typeof value === 'object' && snapshots.has(value);
const part = (value:string):string => value.length + ':' + value;
${m.collections ? renderCollectionSupportFor(fieldProtocols) + (protocolSource.includes('enumValue') ? renderEnumValueSupport() : '') + renderSumSupportFor(fieldProtocols) + (protocolSource.includes('uint64Value') ? (m.exact_uint64 ? renderExactUInt64Support() : renderUInt64Support()) : '') + (protocolSource.includes('ownedEntityValue') ? renderEntitySupport() : '') + fieldProtocols.map((protocol, i) => `const field${i}Value = ${protocol};\n`).join('') : ''}const valueKey = (fields:${name}Fields):string => part(${q(m.selector)}) + part(${q(m.component_protocol_sha256)})${keyFields.map(f => ` + part(${q(f.name)}) + part(${q(tag(f))}) + part(${m.collections ? `field${m.fields.indexOf(f)}Value.key(fields[${q(f.name)}])` : f.component ? `${f.component.local}.key(fields[${q(f.name)}])` : f.tag === 'Bool' ? `fields[${q(f.name)}] ? '1' : '0'` : `fields[${q(f.name)}]`})`).join('')};
const baseValidators:readonly BoundValidator[] = Object.freeze([${m.base_validators.map(validator).join(',')}]);
const extensionValidators:Readonly<Record<string,readonly BoundValidator[]>> = Object.freeze({${m.extensions.map(e => `[${q(e.id)}]:Object.freeze([${e.validators.map(validator).join(',')}])`).join(',')}});
const makeFactory = (extensions:readonly string[],validators:readonly BoundValidator[]):Factory => {
  const construct = (route:string,input:unknown${entity ? `,previous?:${name}Snapshot` : ''}):Result => {
    const phases:string[] = ['normalize'];
    const trace:ValidatorTrace[] = [];
    const evidence = ():Trace => Object.freeze({route,phases:Object.freeze([...phases]),validators:Object.freeze([...trace])});
    const failure = (code:string):Result => Object.freeze({ok:false,value:null,failure_codes:Object.freeze([code]),trace:evidence()});
${normalization}    for (const validator of validators) {
      let outcome:'pass'|'fail'|'exception';
      try {outcome = validator.validate(fields) === true ? 'pass' : 'fail';} catch {outcome = 'exception';}
      trace.push(Object.freeze({rule:validator.rule,closure_sha256:validator.closure_sha256,artifact_sha256:validator.artifact_sha256,outcome}));
      if (outcome !== 'pass') return failure('RULE_' + outcome.toUpperCase() + ':' + validator.rule);
    }
${entity ? `    phases.push('resolve-identity');\n` : ''}    const key = valueKey(fields);
${entity ? `    if (previous !== undefined && (!owned(previous) || snapshots.get(previous)!.key !== key)) return failure('IDENTITY_CHANGED');\n` : ''}    const components:readonly Component[] = Object.freeze([${m.fields.map(component).join(',')}]);
    phases.push('form');
    const value:${name}Snapshot = Object.freeze({[brand]:true as const,fields,components,
      hash:():string=>key,
      ${entity ? 'sameIdentity' : 'equals'}:(other:unknown):boolean=>owned(other) && ${entity ? 'snapshots.get(other)!.key === key' : m.fields.map((f, i) => m.collections ? `field${i}Value.key(snapshots.get(other)!.fields[${q(f.name)}]) === field${i}Value.key(fields[${q(f.name)}])` : f.component ? `${f.component.local}.equals(snapshots.get(other)!.fields[${q(f.name)}],fields[${q(f.name)}])` : `snapshots.get(other)!.fields[${q(f.name)}] === fields[${q(f.name)}]`).join(' && ')},
${entity ? `      identity:Object.freeze({[identityBrand]:true as const,component:components[${m.fields.findIndex(f => f.identity)}]!}),\n` : ''}    });
    snapshots.set(value,Object.freeze({fields,key}));
    phases.push('freeze');
    return Object.freeze({ok:true,value,failure_codes:Object.freeze([]),trace:evidence()});
  };
  return Object.freeze({
    create:(input:unknown):Result=>construct('create',input),
    reconstruct:(input:unknown):Result=>construct('reconstruct',input),
${entity ? `    transition:(previous:${name}Snapshot,input:unknown):Result=>owned(previous) ? construct('transition',input,previous) : Object.freeze({ok:false,value:null,failure_codes:Object.freeze(['INVALID_PREVIOUS']),trace:Object.freeze({route:'transition',phases:Object.freeze([]),validators:Object.freeze([])})}),\n` : ''}    extensions,
    extend:(id:string):Factory=>{
      if (typeof id !== 'string' || !Object.hasOwn(extensionValidators,id) || extensions.includes(id)) throw new TypeError('INVALID_EXTENSION');
      return makeFactory(Object.freeze([...extensions,id]),Object.freeze([...validators,...extensionValidators[id]!]));
    },
  });
};
export const ${m.callable} = ():Factory => makeFactory(Object.freeze([]),baseValidators);
${m.composed && (!entity || m.entity_fields) ? `// Only this provider's validated snapshots can cross an owned-component boundary.
export const ${name}ValueComponent = Object.freeze({
  protocol_id:${entity ? "'typescript.owned-entity-component/v1-candidate'" : "'typescript.owned-value-component/v1'"} as const,
  concept:${q(m.selector)},contract_sha256:${q(m.component_protocol_sha256)},
  isOwned:owned,
  key:(value:unknown):string=>{if (!owned(value)) throw new TypeError('UNOWNED_COMPONENT');return snapshots.get(value)!.key;},
  equals:(left:unknown,right:unknown):boolean=>owned(left) && owned(right) && snapshots.get(left)!.key === snapshots.get(right)!.key,
});
` : ''}${m.reference_bindings ? renderReferenceDescriptors(name,m.reference_bindings) : ''}`;
}
