import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {decodeTypedQueryContract, queryReturnsOptional, type BackendPredicate, type BackendValue, type TypedQueryContract} from '../typed-backend/contracts.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {queryCardinalityExtension} from './query-cardinality-extension.js';
import type {TypedType} from '../typed-operation/contracts.js';
import type {PlannedArtifact} from './contracts.js';
import {renderRustExternalPropertyTypes, rustPascal, rustSelectorModule, rustSelectorType, rustSnake, rustString} from './configured-rust-values.js';

export const RUST_QUERY_SELECTION_VERSION = 'domainspec.configured-rust-queries-selection/v1-candidate';
export const RUST_QUERY_PROTOCOL = 'rust.bound-query/v1-candidate';
export const RUST_QUERY_CONTRACT_SHA256 = '22341e2cb01b1da88402612a858be41239482f9a25cea8e80d5ef1ef187dca80';

export interface RustQuerySelection {readonly schema_version: typeof RUST_QUERY_SELECTION_VERSION; readonly language: 'rust'; readonly module_root: string; readonly roots: readonly string[]; readonly boundary_sha256: string; readonly field_compilation_sha256: string;}
type Value = {type: TypedType; reference: string; string: string | null};
function fail(reason: string): never {throw new TypeError('DS_RUST_QUERY:' + reason);}
function artifact(relative_path: string, content: string): PlannedArtifact {return {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)};}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
const same = (left: TypedType, right: TypedType) => canonicalJson(left) === canonicalJson(right);
const scalarType = (type: TypedType): string => type.kind === 'scalar' ? type.name === 'String' ? 'String' : type.name === 'Bool' ? 'bool' : 'u64' : fail('Query inputs must be scalar');

export function rustQueryPath(moduleRoot: string, selector: string): string {return `${moduleRoot}/src/application/queries/${rustSelectorModule(selector)}.rs`;}

export function planConfiguredRustQueries(boundary: CompiledCompositionBoundary, fields: CompiledProjectFields, selection: RustQuerySelection, contractSource: string) {
  assertCompiledCompositionBoundary(boundary); assertCompiledProjectFields(fields); assertInterfaceData(selection); assertInterfaceData(contractSource);
  if (sha256(contractSource) !== RUST_QUERY_CONTRACT_SHA256) fail('contract drift');
  if (selection.schema_version !== RUST_QUERY_SELECTION_VERSION || selection.language !== 'rust') fail('unsupported selection');
  if (selection.boundary_sha256 !== boundary.boundary_sha256 || selection.field_compilation_sha256 !== fields.compilation_sha256 || fields.certificate.graph_sha256 !== boundary.certificate.graph_sha256 || fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION) fail('stale or cross-graph inputs');
  if (selection.module_root.split('/').some(part => {try {rustSnake(part); return false;} catch {return true;}})) fail('portable module root required');
  if (!Array.isArray(selection.roots) || !selection.roots.length || selection.roots.length > 256 || new Set(selection.roots).size !== selection.roots.length) fail('bounded unique roots required');
  const roots = [...selection.roots].sort(), declarations = new Map(fields.model.declarations.map(row => [row.selector, row]));
  const modules = roots.map(selector => {
    const row = boundary.value_bindings.core_contracts.find(candidate => candidate.owner.selector === selector); if (row?.kind !== 'Query') return fail('selected root is not a bound Query:' + selector);
    const contract = decodeTypedQueryContract(row.contract), declaration = declarations.get(contract.source); if (declaration?.kind !== 'Entity') return fail('Query source must be a checked Entity:' + contract.source);
    const properties = declaration.contract.properties, property = (name: string) => properties.find(item => item.name === name) ?? fail('unknown source field:' + name);
    const externalTypes = renderRustExternalPropertyTypes(declaration.selector, properties), queryName = rustPascal(selector.split(':')[1]!), symbol = rustSnake(selector.split(':')[1]!);
    const value = (candidate: BackendValue): Value => {
      if (candidate.kind === 'field') {const field = property(candidate.name); return {type: field.type, reference: `row.${rustSnake(field.name)}()`, string: field.type.kind === 'scalar' && field.type.name === 'String' ? `row.${rustSnake(field.name)}().as_str()` : null};}
      if (candidate.kind === 'parameter') {const parameter = contract.inputs.find(item => item.name === candidate.name) ?? fail('unknown parameter:' + candidate.name); return {type: parameter.type, reference: rustSnake(parameter.name), string: parameter.type.kind === 'scalar' && parameter.type.name === 'String' ? `${rustSnake(parameter.name)}.as_str()` : null};}
      const type: TypedType = {kind: 'scalar', name: candidate.type};
      if (candidate.type === 'String') return {type, reference: `&String::from(${rustString(String(candidate.value))})`, string: rustString(String(candidate.value))};
      if (candidate.type === 'Bool') return {type, reference: candidate.value ? '&true' : '&false', string: null};
      const integer = BigInt(candidate.value); if (integer < 0n || integer > 18446744073709551615n) return fail('UInt64 literal out of range');
      return {type, reference: `&${integer}u64`, string: null};
    };
    const predicate = (expression: BackendPredicate): string => {
      if (expression.op === 'all' || expression.op === 'any') return '(' + expression.terms.map(predicate).join(expression.op === 'all' ? ' && ' : ' || ') + ')';
      if (expression.op === 'not') return `!(${predicate(expression.term)})`;
      if (!('left' in expression)) return fail('unsupported predicate');
      const left = value(expression.left), right = value(expression.right); if (!same(left.type, right.type)) return fail('comparison type mismatch');
      if (expression.op === 'eq') return `${left.reference} == ${right.reference}`;
      if (left.type.kind !== 'scalar') return fail('ordering requires scalar operands');
      const ordering = left.type.name === 'String' ? `compare_string(${left.string!}, ${right.string!})` : `${left.reference}.cmp(${right.reference})`;
      return expression.op === 'lt' ? `${ordering}.is_lt()` : expression.op === 'lte' ? `!${ordering}.is_gt()` : expression.op === 'gt' ? `${ordering}.is_gt()` : `!${ordering}.is_lt()`;
    };
    const projection = contract.projection.map(name => {const field = property(name); return {name, type: field.type, native_type: externalTypes.get(name)!};});
    const projectedValue = (field: typeof projection[number]) => field.type.kind === 'scalar' && field.type.name !== 'String'
      ? `*row.${rustSnake(field.name)}()`
      : `row.${rustSnake(field.name)}().clone()`;
    if (contract.order_by && property(contract.order_by.field).type.kind !== 'scalar') fail('ordering requires scalar field');
    const parameters = contract.inputs.map(input => `${rustSnake(input.name)}: &${scalarType(input.type)}`), callArguments = contract.inputs.map(input => rustSnake(input.name));
    const filter = contract.filter === null ? 'true' : predicate(contract.filter), filterBinding = contract.filter === null ? '_row' : 'row', sourceType = rustSelectorType(contract.source), reader = `${queryName}Reader`, result = `${queryName}Projection`;
    const orderType = contract.order_by ? property(contract.order_by.field).type : null;
    const stringOrdering = (orderType?.kind === 'scalar' && orderType.name === 'String') || canonicalJson(contract.filter).includes('"String"');
    let ordering = '';
    if (contract.order_by) {
      const field = property(contract.order_by.field), getter = `${rustSnake(field.name)}()`;
      const compare = field.type.kind === 'scalar' && field.type.name === 'String' ? `compare_string(left.${getter}.as_str(), right.${getter}.as_str())` : `left.${getter}.cmp(right.${getter})`;
      ordering = `\n    selected.sort_by(|left, right| ${contract.order_by.direction === 'asc' ? compare : `${compare}.reverse()`});`;
    }
    const limit = contract.limit === null ? '' : `\n    selected.truncate(${contract.limit});`;
    const helper = stringOrdering ? `\nfn compare_string(left: &str, right: &str) -> std::cmp::Ordering {\n    left.encode_utf16().cmp(right.encode_utf16())\n}\n` : '';
    const mutable = contract.order_by !== null || contract.limit !== null;
    const optional = queryReturnsOptional(contract);
    const extension = queryCardinalityExtension(contract, 'rust');
    const cardinalityCheck = optional ? '\n    if selected.len() > 1 { return Err(QueryError { code: "QUERY_CARDINALITY" }); }' : '';
    const content = `// Generated DomainSpec Rust Query.\n\npub const DOMAINSPEC_SELECTOR: &str = ${rustString(selector)};\npub const DOMAINSPEC_CONTRACT_SHA256: &str = ${rustString(sha256(canonicalJson(contract)))};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(extension.protocol_id ?? RUST_QUERY_PROTOCOL)};\n\n#[derive(Clone, Debug, PartialEq, Eq)]\npub struct QueryError { pub code: &'static str }\n\nimpl QueryError { pub const READ: Self = Self { code: \"DOMAINSPEC_QUERY_READ\" }; }\n\n#[derive(Clone, Debug, PartialEq, Eq)]\npub struct ${result} {\n${projection.map(field => `    pub ${rustSnake(field.name)}: ${field.native_type},`).join('\n')}\n}\n\n#[allow(async_fn_in_trait)]\npub trait ${reader} {\n    async fn read_${symbol}(&self${parameters.length ? ', ' + parameters.join(', ') : ''}) -> Result<Vec<${sourceType}>, QueryError>;\n}\n${helper}\npub async fn ${symbol}<R: ${reader}>(reader: &R${parameters.length ? ', ' + parameters.join(', ') : ''}) -> Result<${optional ? 'Option' : 'Vec'}<${result}>, QueryError> {\n    let rows = reader.read_${symbol}(${callArguments.join(', ')}).await?;\n    let ${mutable ? 'mut ' : ''}selected: Vec<${sourceType}> = rows.into_iter().filter(|${filterBinding}| ${filter}).collect();${ordering}${limit}${cardinalityCheck}\n    Ok(selected.into_iter().map(|row| ${result} {\n${projection.map(field => `        ${rustSnake(field.name)}: ${projectedValue(field)},`).join('\n')}\n    }).${optional ? 'next' : 'collect'}())\n}\n`;
    const relative_path = rustQueryPath(selection.module_root, selector);
    return {selector, symbol, reader, result, relative_path, source: contract.source, inputs: contract.inputs, projection, filter: contract.filter, order_by: contract.order_by, limit: contract.limit, ...extension, contract_sha256: sha256(canonicalJson(contract)), artifact: artifact(relative_path, content)};
  });
  const body = {schema_version: 'domainspec.configured-rust-queries-plan/v1-candidate' as const, selection: {...selection, roots}, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256, contract_sha256: RUST_QUERY_CONTRACT_SHA256, protocol_id: RUST_QUERY_PROTOCOL, modules: modules.map(({artifact: _artifact, ...module}) => module), artifacts: modules.map(module => module.artifact).sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
