import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import type {PlannedArtifact} from './contracts.js';

/** R10 candidate native adapter. Remaining scope: R10-PYTHON.md in the work pack. */
export const PYTHON_ENUM_SELECTION_VERSION = 'domainspec.configured-python-enums-selection/v1-candidate';
export const PYTHON_ENUM_PROTOCOL = 'python.nominal-enum-explicit-wire/v1';
export const PYTHON_ENUM_SOURCE_DIGESTS = Object.freeze({
  configuration: '9ac018e42080483f373219049b466d8a515cb3e7748181ea8e635b1162af8317',
  base: '48d0ba174105b020bb6b94c79c27b208a67f7d5f92d4c0c9c3a28c7d91a04d9f',
  python: '148cd333265563f6591ad6cd1cd7300b2fe0af3b9ec19de84ab4dab3162fbca4',
});
export interface PythonEnumSelection {
  readonly schema_version: typeof PYTHON_ENUM_SELECTION_VERSION;
  readonly language: 'python';
  readonly module_root: string;
  readonly field_compilation_sha256: string;
}
export type PythonEnumSources = Readonly<Record<keyof typeof PYTHON_ENUM_SOURCE_DIGESTS, string>>;
export interface PythonEnumModule {
  readonly selector: string;
  readonly relative_path: string;
  readonly import_name: string;
  readonly symbol: string;
  readonly callable_stem: string;
  readonly members: readonly Readonly<{name: string; native_name: string; wire_value: string; ontology_variant: string}>[];
}
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_ENUM:' + reason);};
const keywords = new Set('False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield'.split(' '));
const reserved = new Set([...keywords, ...'con prn aux nul'.split(' '), ...Array.from({length: 9}, (_, i) => ['com' + (i + 1), 'lpt' + (i + 1)]).flat()]);
const shadowedStdlib = new Set(['enum', 'typing', 'types', 'builtins', 'dataclasses', 'collections', 'json', 'sys', 'hashlib', 'weakref']);
export function pythonPortableIdentifier(value: unknown): asserts value is string {
  if (typeof value !== 'string' || /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(value)?.[0] !== value || reserved.has(value)) fail('unsafe portable identifier:' + String(value));
}
const portable: typeof pythonPortableIdentifier = pythonPortableIdentifier;
function closed(value: unknown, keys: readonly string[]): void {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('inert object required');
  const descriptors = Object.getOwnPropertyDescriptors(value);
  if (Reflect.ownKeys(descriptors).some(k => typeof k !== 'string') || Object.keys(descriptors).sort().join('|') !== [...keys].sort().join('|') || Object.values(descriptors).some(d => !('value' in d) || !d.enumerable)) fail('closed data fields required');
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);}
  return value;
}
const snake = (name: string) => name.replaceAll('-', '_');
export function pythonEnumSymbol(node: string): string {
  const name = node.split('-').map(w => w[0]!.toUpperCase() + w.slice(1)).join('');
  // Source identifiers cannot produce an underscore, so the escape cannot
  // collide with a normal PascalCase concept such as concept-none.
  return keywords.has(name) ? 'Concept_' + name : name;
}
export const pythonStringLiteral = (value: string) => JSON.stringify(value).replaceAll('\u2028', '\\u2028').replaceAll('\u2029', '\\u2029');
const literal = pythonStringLiteral;
function render(m: PythonEnumModule): string {
  const branch = (result: (member: PythonEnumModule['members'][number]) => string) => m.members.map(v =>
    `    if member is ${m.symbol}.${v.native_name}:\n        return ${result(v)}\n`).join('');
  return `from __future__ import annotations

import enum as _enum

ENUM_ID = ${literal(m.selector)}
PROTOCOL_ID = ${literal(PYTHON_ENUM_PROTOCOL)}


class _EnumWireError(ValueError):
    code = "DOMAINSPEC_ENUM_UNKNOWN_WIRE"

    def __init__(self, wire_value: object):
        self.enum_id = ENUM_ID
        self.wire_value = wire_value
        super().__init__(self.code + ":" + ENUM_ID)

    def as_dict(self) -> dict[str, object]:
        return {"code": self.code, "enum_id": self.enum_id, "wire_value": self.wire_value}


class _EnumMemberError(TypeError):
    code = "DOMAINSPEC_ENUM_MEMBER_INVALID"

    def __init__(self, member: object):
        self.enum_id = ENUM_ID
        self.member = member
        super().__init__(self.code + ":" + ENUM_ID)


@_enum.unique
class ${m.symbol}(_enum.Enum):
${m.members.map(v => `    ${v.native_name} = ${literal(v.wire_value)}\n`).join('')}

def parse_${m.callable_stem}(wire_value: str) -> ${m.symbol}:
    if type(wire_value) is not str:
        raise _EnumWireError(wire_value)
${m.members.map(v => `    if wire_value == ${literal(v.wire_value)}:\n        return ${m.symbol}.${v.native_name}\n`).join('')}    raise _EnumWireError(wire_value)


def emit_${m.callable_stem}(member: ${m.symbol}) -> str:
${branch(v => literal(v.wire_value))}    raise _EnumMemberError(member)


def ${m.callable_stem}_member_id(member: ${m.symbol}) -> str:
${branch(v => literal(v.ontology_variant))}    raise _EnumMemberError(member)
`;
}

/** Every selected declaration must be a plain Enum; never erase a payload or
 * filter out record dependencies. Uses checked snapshots only and writes nothing.
 */
export function resolvePythonEnumContext(fields: CompiledProjectFields, selection: PythonEnumSelection, sources: PythonEnumSources) {
  assertCompiledProjectFields(fields);
  closed(selection, ['schema_version', 'language', 'module_root', 'field_compilation_sha256']);
  closed(sources, Object.keys(PYTHON_ENUM_SOURCE_DIGESTS));
  if (selection.schema_version !== PYTHON_ENUM_SELECTION_VERSION || selection.language !== 'python') fail('unsupported selection');
  if (fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION || fields.compilation_sha256 !== selection.field_compilation_sha256) fail('exact current checked fields required');
  if (typeof selection.module_root !== 'string') fail('module root required');
  const rootParts = selection.module_root.split('/');rootParts.forEach(portable);
  if (shadowedStdlib.has(rootParts[0]!)) fail('module root shadows Python standard library');
  for (const key of Object.keys(PYTHON_ENUM_SOURCE_DIGESTS) as (keyof PythonEnumSources)[])
    if (typeof sources[key] !== 'string' || sha256(sources[key]) !== PYTHON_ENUM_SOURCE_DIGESTS[key]) fail('source drift:' + key);
  // These are frozen candidate representation inputs, not a claim that an old
  // profile's provider-absent status has been activated by generating this plan.
  const configuration = JSON.parse(sources.configuration);
  const cell = configuration.types.find((t: {kind: string}) => t.kind === 'Enum');
  if (cell?.role !== 'domain/enums') fail('Enum location contract');
  const profile = JSON.parse(sources.python);
  const overlay = profile.representation_overlays.find((o: {contract_id: string}) => o.contract_id === 'enum.profile-representation');
  const protocol = overlay?.candidate_protocols.find((p: {protocol_id: string}) => p.protocol_id === PYTHON_ENUM_PROTOCOL);
  if (protocol?.form_id !== 'python.enum-class' || protocol.native_contract?.str_mixin !== 'forbidden' || protocol.native_contract?.aliases !== 'forbidden') fail('nominal Enum representation required');
  const root = rootParts.map(snake).join('/');
  return {root, role: cell.role as string};
}

export function planConfiguredPythonEnums(fields: CompiledProjectFields, selection: PythonEnumSelection, sources: PythonEnumSources) {
  const {root, role} = resolvePythonEnumContext(fields, selection, sources);
  const modules: PythonEnumModule[] = fields.model.declarations.map(d => {
    if (d.kind !== 'Enum') return fail('unsupported declaration kind:' + d.selector);
    if (d.contract.variants.some(v => v.payload !== null)) fail('payload-bearing sum requires algebraic adapter:' + d.selector);
    const [feature, node] = d.selector.split(':') as [string, string];portable(feature);portable(node);
    const relative_path = `${root}/features/${snake(feature)}/src/${role}/${snake(node)}.py`;
    return {selector: d.selector, relative_path, import_name: relative_path.slice(0, -3).replaceAll('/', '.'),
      symbol: pythonEnumSymbol(node), callable_stem: snake(node),
      members: d.contract.variants.map(v => ({name: v.name, native_name: keywords.has(v.name) ? 'Variant_' + v.name : v.name, wire_value: v.name, ontology_variant: v.ontology_variant})).sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0)};
  });
  const files = new Map<string, string>();
  const add = (file: string, content: string) => {if (files.has(file) && files.get(file) !== content) fail('artifact collision:' + file);files.set(file, content);};
  for (const m of modules) {
    add(m.relative_path, render(m));
    const parts = m.relative_path.split('/');
    for (let i = 1; i < parts.length; i++) add(parts.slice(0, i).join('/') + '/__init__.py', '');
  }
  const artifacts: PlannedArtifact[] = [...files].sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0).map(([relative_path, content]) => ({relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)}));
  const body = {schema_version: 'domainspec.configured-python-enums-plan/v1-candidate' as const, selection: {...selection},
    source_digests: PYTHON_ENUM_SOURCE_DIGESTS, certificate: fields.certificate, field_compilation_sha256: fields.compilation_sha256,
    modules, artifacts, protocol_id: PYTHON_ENUM_PROTOCOL, input_envelope: 'plain-enum-variant-name-wire/v1-candidate',
    output_effect: 'none', authority_effect: 'none'};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
