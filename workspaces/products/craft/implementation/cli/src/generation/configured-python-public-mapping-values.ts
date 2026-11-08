import type {TypedType, ValueExpression} from '../typed-operation/contracts.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {qualifyPublicType, type MappingValueType, type MappingInterfaceDeclaration} from '../typed-backend/mapping-public.js';
import {canonicalJson} from '../input/source-manifest.js';
import {createPythonRuleValues} from './configured-python-rule-values.js';
import {createPythonReadTypes} from './configured-python-read-types.js';
import {createPythonValueExpressions} from './configured-python-value-expressions.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';

/** Public paths extend static domain lowering without synthetic record declarations. */
export function createPythonPublicMappingValues(model: FieldReferenceModel | null, interfaces: readonly MappingInterfaceDeclaration[], aliases: ReadonlyMap<string, string>, fail: (reason: string) => never) {
  const domain = createPythonRuleValues(model, fail), types = createPythonReadTypes(model, fail);
  const literals = createPythonValueExpressions(domain, [], fail);
  type Shape = {input: string; native: string; protocol: string};
  type Bound = {type: MappingValueType; code: string};
  const cache = new Map<string, Shape>(), rows: string[] = []; let next = 0;
  const hasPublic = (t: MappingValueType): boolean => t.kind === 'contract' || (t.kind === 'sum' ? t.variants.some(v => v.payload !== null && hasPublic(v.payload)) : t.kind === 'scalar' || t.kind === 'named' || t.kind === 'reference' ? false : hasPublic(t.element));
  const ensure = (t: MappingValueType): Shape => {
    if (!hasPublic(t)) return {...types.ensure(t as TypedType), protocol: domain.ensure(t as TypedType)};
    const id = canonicalJson(t), cached = cache.get(id); if (cached) return cached;
    if (t.kind === 'contract') {
      const alias = aliases.get(t.interface_selector) ?? fail('missing Interface import');
      const native = alias + '.Contract_' + t.contract_id.replaceAll('-', '_');
      const value = {native, input: native, protocol: alias + '.public_contracts[' + q(t.contract_id) + ']'}; cache.set(id, value); return value;
    }
    const name = '_Mapping' + next++, protocol = name + 'Value'; let shape: {input: string; native: string}, expression: string;
    if (t.kind === 'sum') {
      const variants = [...t.variants].sort((a, b) => a.name < b.name ? -1 : 1), children = variants.map(v => v.payload ? ensure(v.payload) : null);
      const cases = variants.map((v, i) => types.record(name + 'Case' + i, [{name: 'variant', input: `_Literal[${q(v.name)}]`, native: `_Literal[${q(v.name)}]`, optional: false}, ...(children[i] ? [{name: 'payload', ...children[i]!, optional: false}] : [])]));
      shape = {input: cases.map(c => c.input).join(' | '), native: cases.map(c => c.native).join(' | ')};
      expression = '_facts.sum_fact({' + variants.map((v, i) => q(v.name) + ': ' + (children[i]?.protocol ?? 'None')).join(', ') + '})';
    } else if (t.kind === 'optional' || t.kind === 'list' || t.kind === 'set') {
      const child = ensure(t.element);
      shape = t.kind === 'optional' ? {input: `(${child.input}) | None`, native: `(${child.native}) | None`} : {input: `list[${child.input}] | tuple[${child.input}, ...]`, native: `tuple[${child.native}, ...]`};
      expression = t.kind === 'optional' ? `_facts.optional_fact(${child.protocol})` : `_facts.sequence_fact(${child.protocol}, ${t.kind === 'set' ? 'True' : 'False'})`;
    } else return fail('public value type');
    const value = {...shape, protocol}; cache.set(id, value); rows.push(protocol + ' = ' + expression + '\n'); return value;
  };
  const properties = (t: MappingValueType) => {
    if (t.kind === 'contract') {
      const api = interfaces.find(i => i.selector === t.interface_selector) ?? fail('missing Interface');
      const contract = api.contract.contracts.find(c => c.contract_id === t.contract_id) ?? fail('missing public contract');
      return contract.fields.map(f => ({name: f.name, ontology_property: f.ontology_field, type: qualifyPublicType(f.type, t.interface_selector)}));
    }
    if (t.kind === 'named') {const d = domain.get(t.selector); if (d.kind !== 'Enum') return d.contract.properties;}
    return fail('path requires a declared record value; no implicit unwrap');
  };
  const expression = (e: ValueExpression, scope: ReadonlyMap<string, Bound>): Bound => {
    if (e.op === 'literal' || e.op === 'variant') return literals.value(e);
    if (e.op === 'to_set') {const source = expression(e.value, scope); if (source.type.kind !== 'list') return fail('to_set requires list'); return {type: {kind: 'set', element: source.type.element}, code: `_to_set(${source.code}, ${ensure(source.type.element).protocol})`};}
    let current = scope.get(e.root) ?? fail('undeclared input');
    for (const property of e.properties) {
      const collection = current.type.kind === 'list' || current.type.kind === 'set', owner = current.type.kind === 'list' || current.type.kind === 'set' ? current.type.element : current.type;
      const field = properties(owner).find(f => f.ontology_property === property) ?? fail('unknown ontology field');
      if (collection) {const item = '_item' + next++, mapped = `tuple(${item}[${q(field.name)}] for ${item} in ${current.code})`; current = {type: {kind: current.type.kind as 'list' | 'set', element: field.type}, code: current.type.kind === 'set' ? `_to_set(${mapped}, ${ensure(field.type).protocol})` : mapped};}
      else current = {type: field.type, code: current.code + '[' + q(field.name) + ']'};
    }
    return current;
  };
  return {ensure, expression, types, source: () => types.source() + domain.source() + rows.join('')};
}
