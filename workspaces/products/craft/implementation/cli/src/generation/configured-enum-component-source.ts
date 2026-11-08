import type {ConfiguredEnumModule} from './configured-enums.js';

// PCR-06 candidate adapter; scope/open questions: ENUM-FIELD-FACTORY-GENERATION.md.
export interface ConfiguredEnumComponentModule {
  readonly selector: string;
  readonly relative_path: string;
  readonly definition_path: string;
  readonly definition_sha256: string;
  readonly unannotated_definition_sha256: string;
  readonly definition_import: string;
  readonly name: string;
  readonly members: ConfiguredEnumModule['members'];
  readonly contract_sha256: string;
}
/** Preserve the v1 definition's runtime expression, but name its inferred private
 * provider type through a public generic function so declaration emission works. */
export function annotateEnumDefinition(m: ConfiguredEnumModule, source: string): string {
  const original = 'export const ' + m.symbol + ' =';
  if (source.split(original).length !== 2) throw new Error('DS_CONFIGURED_FACTORY:Enum definition annotation drift');
  const members = m.members.map(v => 'readonly ' + JSON.stringify(v.name) + ':' + JSON.stringify(v.wire_value)).join(';');
  return source.replace(original, 'export const ' + m.symbol + ':ReturnType<typeof defineEnum<{' + members + '}>> =');
}
export function renderEnumValueSupport(): string {
  return `const enumValue = <T>(provider:Readonly<{isOwned:(input:unknown)=>input is T;key:(input:unknown)=>string}>):ValueProtocol<T> => Object.freeze({
  normalize:(input:unknown):T=>{if(!provider.isOwned(input)) throw new TypeError('UNOWNED_ENUM_CASE');return input;},
  key:(value:T):string=>part('Enum') + part(provider.key(value)),
});
`;
}
export function renderEnumComponent(m: ConfiguredEnumComponentModule): string {
  const q = JSON.stringify;
  return `import {${m.name} as EnumDefinition} from ${q(m.definition_import)};
const brand:unique symbol = Symbol(${q(m.selector)});
export type ${m.name}Case = Readonly<{[brand]:true;variant:EnumDefinition}>;
const cases = Object.freeze({${m.members.map(v => `[${q(v.name)}]:Object.freeze({[brand]:true as const,variant:EnumDefinition[${q(v.name)}]})`).join(',')}});
const ownership = new WeakSet<object>(Object.values(cases));
const owned = (value:unknown):value is ${m.name}Case => value !== null && typeof value === 'object' && ownership.has(value);
const part = (value:string):string => value.length + ':' + value;
export const ${m.name}ValueComponent = Object.freeze({
  protocol_id:'typescript.owned-enum-case/v1-candidate' as const,
  concept:${q(m.selector)},contract_sha256:${q(m.contract_sha256)},
  definition_sha256:${q(m.definition_sha256)},
  values:cases,
  fromVariant:(value:unknown):${m.name}Case=>{
    if(typeof value !== 'string' || !Object.hasOwn(cases,value)) throw new TypeError('INVALID_ENUM_VARIANT');
    return cases[value as keyof typeof cases];
  },
  isOwned:owned,
  key:(value:unknown):string=>{if(!owned(value)) throw new TypeError('UNOWNED_ENUM_CASE');return part(${q(m.selector)}) + part(${q(m.contract_sha256)}) + part(value.variant);},
  equals:(left:unknown,right:unknown):boolean=>owned(left) && owned(right) && left.variant === right.variant,
});
`;
}
