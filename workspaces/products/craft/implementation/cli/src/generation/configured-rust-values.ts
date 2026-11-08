import type {TypedType} from '../typed-operation/contracts.js';

const keywords = new Set('as async await break const continue crate dyn else enum extern false fn for if impl in let loop match mod move mut pub ref return self Self static struct super trait true type unsafe use where while abstract become box do final macro override priv typeof unsized virtual yield try gen'.split(' '));

export function rustSnake(value: string): string {
  const result = value.replaceAll('-', '_');
  if (!/^[a-z][a-z0-9_]*$/.test(result) || result.includes('__')) throw new TypeError('DS_RUST_VALUE:portable snake-case identifier required:' + value);
  return keywords.has(result) ? 'domain_' + result : result;
}

export function rustPascal(value: string): string {
  const result = value.split('-').map(part => part[0]!.toUpperCase() + part.slice(1)).join('');
  if (!/^[A-Z][A-Za-z0-9]*$/.test(result)) throw new TypeError('DS_RUST_VALUE:portable PascalCase identifier required:' + value);
  return keywords.has(result) ? 'Domain' + result : result;
}

export function rustString(value: string): string {
  let output = '"';
  for (let index = 0; index < value.length;) {
    const point = value.codePointAt(index)!; index += point > 0xffff ? 2 : 1;
    if (point >= 0xd800 && point <= 0xdfff) throw new TypeError('DS_RUST_VALUE:unpaired surrogate');
    if (point === 0x22) output += '\\"';
    else if (point === 0x5c) output += '\\\\';
    else if (point === 0x00) output += '\\0';
    else if (point === 0x09) output += '\\t';
    else if (point === 0x0a) output += '\\n';
    else if (point === 0x0d) output += '\\r';
    else if (point < 0x20 || point >= 0x7f && point <= 0x9f) output += `\\u{${point.toString(16)}}`;
    else output += String.fromCodePoint(point);
  }
  return output + '"';
}

export function rustSelectorType(selector: string): string {
  const [feature, node, ...rest] = selector.split(':');
  if (!feature || !node || rest.length) throw new TypeError('DS_RUST_VALUE:qualified selector required:' + selector);
  return `crate::domain::types::${rustSelectorModule(selector)}::${rustPascal(node)}`;
}

export function rustSelectorModule(selector: string): string {
  const [feature, node, ...rest] = selector.split(':');
  if (!feature || !node || rest.length) throw new TypeError('DS_RUST_VALUE:qualified selector required:' + selector);
  const left = rustSnake(feature), right = rustSnake(node);
  return `f${left.length}_${left}_n${right.length}_${right}`;
}

export interface RustRenderedType {
  readonly type: string;
  readonly support: readonly string[];
  readonly definitions: readonly string[];
}

/** Render record property types as they are named from another module. The
 * shared ordinal mirrors owned factory lowering, including nested inline sums. */
export function renderRustExternalPropertyTypes(selector: string, properties: readonly Readonly<{name: string; type: TypedType}>[]): ReadonlyMap<string, string> {
  const owner = rustPascal(selector.split(':')[1]!), ordinal = {value: 0}, module = `crate::domain::types::${rustSelectorModule(selector)}`;
  return new Map(properties.map(property => {
    const rendered = renderRustOwnedType(property.type, owner, ordinal);
    const type = rendered.type
      .replace(new RegExp(`\\b${owner}InlineSum[0-9]+\\b`, 'g'), name => `${module}::${name}`)
      .replace(/\bBTreeSet</g, 'std::collections::BTreeSet<');
    return [property.name, type] as const;
  }));
}

/** Render owned Rust value types. Anonymous sums receive deterministic private
 * enum names; callers own the surrounding module and collision checks. */
export function renderRustOwnedType(type: TypedType, owner: string, ordinal: {value: number}, depth = 0): RustRenderedType {
  if (depth > 32) throw new TypeError('DS_RUST_VALUE:type depth exceeded');
  if (type.kind === 'scalar') return {type: type.name === 'String' ? 'String' : type.name === 'Bool' ? 'bool' : type.name === 'UInt64' ? 'u64' : (() => {throw new TypeError('DS_RUST_VALUE:unsupported scalar');})(), support: [], definitions: []};
  if (type.kind === 'named') return {type: rustSelectorType(type.selector), support: [], definitions: []};
  if (type.kind === 'reference') throw new TypeError('DS_RUST_VALUE:reference requires declaration identity resolution');
  if (type.kind === 'optional' || type.kind === 'list' || type.kind === 'set') {
    const inner = renderRustOwnedType(type.element, owner, ordinal, depth + 1);
    return {type: type.kind === 'optional' ? `Option<${inner.type}>` : type.kind === 'list' ? `Vec<${inner.type}>` : `BTreeSet<${inner.type}>`, support: [...inner.support, ...(type.kind === 'set' ? ['std::collections::BTreeSet'] : [])], definitions: inner.definitions};
  }
  const name = `${owner}InlineSum${ordinal.value++}`;
  const rendered = type.variants.map(variant => ({variant, payload: variant.payload === null ? null : renderRustOwnedType(variant.payload, owner, ordinal, depth + 1)}));
  const members = rendered.map(({variant, payload}) => `    ${rustPascal(variant.name)}${payload ? `(${payload.type})` : ''},`).join('\n');
  return {type: name, support: rendered.flatMap(row => row.payload?.support ?? []), definitions: [...rendered.flatMap(row => row.payload?.definitions ?? []), `#[derive(Clone, Debug, PartialEq, Eq, Hash)]\npub enum ${name} {\n${members}\n}`]};
}
