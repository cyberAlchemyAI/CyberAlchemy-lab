import { assertCompiledProjectSnapshot, type CompiledProjectGraph } from '../input/project-model.js';
import { assertCompiledProjectFields, type CompiledProjectFields } from '../input/compiled-field-model.js';
import { createCompiledProjectCertificate } from '../compilation/certificate.js';
import { canonicalJson, sha256 } from '../input/source-manifest.js';
import { queryReturnsOptional, type BackendPredicate, type BackendValue } from '../typed-backend/contracts.js';
import { checkTypedInputMapping } from '../typed-backend/mapping-inputs.js';
import { checkPublicMapping, qualifyPublicType, type MappingValueType } from '../typed-backend/mapping-public.js';
import { decodeNamedInterface, checkInterfacePublicClosure } from '../typed-backend/interface.js';
import { createTypedValueChecker } from './value-bindings.js';
import { assertReferencedOperationValueComposition, type ReferencedOperationValueComposition } from './value-composition-references.js';
import type { ScalarName, ValueExpression } from './contracts.js';

type RecordOwner = Extract<MappingValueType, { kind: 'named' | 'contract' }>;
export type CompositionValueType =
  | Readonly<{ kind: 'scalar'; name: ScalarName }>
  | RecordOwner
  | Readonly<{ kind: 'reference'; selector: string; projection: readonly string[] }>
  | Readonly<{ kind: 'optional' | 'list' | 'set'; element: CompositionValueType }>
  | Readonly<{ kind: 'sum'; variants: readonly Readonly<{ name: string; ontology_variant: string; payload: CompositionValueType | null }>[] }>
  | Readonly<{ kind: 'projection'; owner: RecordOwner; fields: readonly string[] }>;
const fail = (reason: string): never => { throw new TypeError('OPERATION_VALUE_TYPES:' + reason); };
const same = (a: CompositionValueType, b: CompositionValueType): boolean => canonicalJson(a) === canonicalJson(b);
const freeze = <T>(value: T): T => { if (value && typeof value === 'object' && !Object.isFrozen(value)) { Object.values(value).forEach(freeze); Object.freeze(value); } return value; };
const snapshots = new WeakSet<object>();
export type TypedOperationValueComposition = ReturnType<typeof compileOperationValueTypes>;
export function assertTypedOperationValueComposition(value: unknown): asserts value is TypedOperationValueComposition {
  if (!value || typeof value !== 'object' || !snapshots.has(value)) fail('unvalidated typed composition');
}

/** Check value preparation, not full action/effect coverage or executable custody. */
export function compileOperationValueTypes(graph: CompiledProjectGraph, fields: CompiledProjectFields, references: ReferencedOperationValueComposition) {
  assertCompiledProjectSnapshot(graph); assertCompiledProjectFields(fields); assertReferencedOperationValueComposition(references);
  const certificate = createCompiledProjectCertificate(graph);
  if (certificate.graph_sha256 !== references.certificate.graph_sha256 || fields.compilation_sha256 !== references.field_compilation_sha256 || fields.certificate.graph_sha256 !== certificate.graph_sha256) fail('cross-graph or field evidence');
  const declarations = fields.model.declarations, domain = createTypedValueChecker(declarations, fail);
  const interfaces = graph.nodes.flatMap(n => n.kind === 'Interface' && (n.body.typed_contract as { schema_version?: string } | undefined)?.schema_version === 'domainspec.typed-interface/v1'
    ? [{ selector: n.selector, contract: decodeNamedInterface(n.body.typed_contract) }] : []);
  const checkedInterfaces = new Set<string>();
  const publicContract = (owner: Extract<RecordOwner, { kind: 'contract' }>) => {
    const api = interfaces.find(i => i.selector === owner.interface_selector) ?? fail('missing Interface');
    if (!checkedInterfaces.has(api.selector)) { checkInterfacePublicClosure(api.contract, declarations); checkedInterfaces.add(api.selector); }
    return api.contract.contracts.find(c => c.contract_id === owner.contract_id) ?? fail('missing qualified public contract');
  };
  const properties = (type: CompositionValueType): readonly { name: string; ontology_property: string; type: CompositionValueType }[] => {
    if (type.kind === 'projection') return properties(type.owner).filter(p => type.fields.includes(p.name));
    if (type.kind === 'contract') return publicContract(type).fields.map(f => ({ name: f.name, ontology_property: f.ontology_field, type: qualifyPublicType(f.type, type.interface_selector) }));
    if (type.kind === 'reference') return [domain.referenceField(type)];
    if (type.kind === 'named') { const d = domain.get(type.selector); if (d.kind !== 'Enum') return d.contract.properties; }
    return fail('field requires a record value; no implicit optional traversal');
  };
  const checkType = (type: CompositionValueType): void => {
    if (type.kind === 'contract') { publicContract(type); return; }
    if (type.kind === 'projection') { properties(type); return; }
    if (type.kind === 'named' || type.kind === 'reference') { domain.checkType(type); return; }
    if (type.kind === 'sum') type.variants.forEach(v => { if (v.payload) checkType(v.payload); });
    else if (type.kind !== 'scalar') checkType(type.element);
  };
  const projected = (owner: RecordOwner, selected: readonly string[]): CompositionValueType => {
    const available = properties(owner);
    if (new Set(selected).size !== selected.length || selected.some(name => !available.some(p => p.name === name))) fail('invalid projected field');
    return available.length === selected.length ? owner : { kind: 'projection', owner, fields: [...selected].sort() };
  };
  const infer = (value: ValueExpression, scope: ReadonlyMap<string, CompositionValueType>): CompositionValueType => {
    if (value.op === 'literal' || value.op === 'variant') return domain.infer(value, new Map());
    if (value.op === 'to_set') { const type = infer(value.value, scope); if (type.kind !== 'list') return fail('to_set requires list'); return { kind: 'set', element: type.element }; }
    let current = scope.get(value.root) ?? fail('unknown value root:' + value.root);
    for (const property of value.properties) {
      if (current.kind === 'list' || current.kind === 'set') {
        const field = properties(current.element).find(p => p.ontology_property === property) ?? fail('unknown or unprojected field:' + property);
        current = { kind: current.kind, element: field.type };
      } else current = (properties(current).find(p => p.ontology_property === property) ?? fail('unknown or unprojected field:' + property)).type;
    }
    return current;
  };
  const initial = new Map<string, CompositionValueType>(references.action.inputs.map(p => [p.name, p.type]));
  initial.forEach(checkType);
  const scope = new Map(initial);
  const reads = references.action.reads.map(read => {
    const declaration = domain.get(read.target);
    if (declaration.kind !== 'Entity') return fail('read requires Entity');
    const identities = declaration.contract.properties.filter(p => p.identity);
    if (identities.length !== 1) return fail('read requires single identity');
    const key_type = infer(read.key, initial);
    if (!same(key_type, identities[0]!.type)) fail('read key type mismatch:' + read.slot);
    const output: CompositionValueType = { kind: 'named', selector: read.target }; scope.set(read.parameter, output);
    return { name: read.parameter, key_type, output };
  });
  const byName = new Map(references.connections.map(c => [c.binding.name, c]));
  const active = new Set<string>(), done = new Set<string>();
  const values: { name: string; selector: string; contract_sha256: string; arguments: readonly { parameter: string; type: CompositionValueType }[]; output: CompositionValueType }[] = [];
  const roots = (value: ValueExpression): readonly string[] => value.op === 'path' ? [value.root] : value.op === 'to_set' ? roots(value.value) : [];
  const visit = (name: string): void => {
    if (done.has(name)) return;
    if (active.has(name)) fail('cyclic values');
    active.add(name);
    const row = byName.get(name) ?? fail('missing value binding'), { binding, contract } = row;
    for (const arg of binding.arguments) for (const dependency of roots(arg.value)) if (byName.has(dependency)) visit(dependency);
    const args = binding.arguments.map(arg => {
      const expected = contract.inputs.find(p => p.name === arg.parameter) ?? fail('missing declared argument');
      checkType(expected.type);
      const type = infer(arg.value, scope);
      if (!same(type, expected.type)) fail('argument type mismatch:' + name + '/' + arg.parameter);
      return { parameter: arg.parameter, type };
    });
    let output: CompositionValueType;
    if (contract.schema_version === 'domainspec.typed-query/v1' || contract.schema_version === 'domainspec.typed-query/v2') {
      if (binding.kind !== 'query') return fail('Query binding mismatch');
      const sourceFields = properties({ kind: 'named', selector: contract.source });
      const field = (name: string) => sourceFields.find(p => p.name === name) ?? fail('unknown Query field');
      const operand = (value: BackendValue): CompositionValueType => value.kind === 'literal' ? { kind: 'scalar', name: value.type }
        : value.kind === 'field' ? field(value.name).type : (contract.inputs.find(p => p.name === value.name) ?? fail('unknown Query parameter')).type;
      const predicate = (value: BackendPredicate): void => {
        if (value.op === 'all' || value.op === 'any') { value.terms.forEach(predicate); return; }
        if (value.op === 'not') { predicate(value.term); return; }
        if (!('left' in value)) return fail('unsupported Query predicate');
        const left = operand(value.left), right = operand(value.right);
        if (!same(left, right)) fail('Query comparison type mismatch');
        if (value.op !== 'eq' && left.kind !== 'scalar') fail('Query ordering needs required scalar');
      };
      if (contract.filter) predicate(contract.filter);
      if (contract.order_by && field(contract.order_by.field).type.kind !== 'scalar') fail('Query ordering needs required scalar');
      const element = projected({ kind: 'named', selector: contract.source }, contract.projection);
      output = queryReturnsOptional(contract) ? binding.absence === 'require-present' ? element : { kind: 'optional', element } : { kind: 'list', element };
    } else if (contract.schema_version === 'domainspec.typed-mapping/v2') {
      checkTypedInputMapping(contract, declarations);
      output = projected({ kind: 'named', selector: contract.target }, contract.fields.map(f => f.target));
    } else {
      checkPublicMapping(contract, declarations, interfaces, true);
      output = projected(contract.target, contract.fields.map(f => f.target));
    }
    scope.set(name, output); values.push({ name, selector: binding.selector, contract_sha256: row.contract_sha256, arguments: args, output });
    active.delete(name); done.add(name);
  };
  [...byName.keys()].sort().forEach(visit);
  // Infer the actual downstream values without reclassifying computed roots as
  // caller inputs. Full action validation owns the expected consumer contracts.
  const expressions = [
    ...references.action.guards.flatMap(g => g.arguments.map(a => a.value)),
    ...references.action.writes.map(w => w.value), references.action.result.value,
  ];
  const consumers = [...new Map(expressions.map(value => [canonicalJson(value), value])).entries()]
    .sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0).map(([, value]) => ({ value, type: infer(value, scope) }));
  const body = {
    schema_version: 'domainspec.operation-value-types/v1-candidate' as const,
    references, reads, values, consumers, field_model_sha256: fields.model.model_sha256,
    public_contracts: interfaces.filter(i => checkedInterfaces.has(i.selector)).sort((a, b) => a.selector < b.selector ? -1 : a.selector > b.selector ? 1 : 0),
    roots: [...scope.entries()].sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0).map(([name, type]) => ({ name, type })),
    validation_stage: 'value-preparation-types' as const, execution: 'not-performed' as const, authority_effect: 'none' as const,
  };
  const result = freeze({ ...body, types_sha256: sha256(canonicalJson(body)) }); snapshots.add(result); return result;
}
