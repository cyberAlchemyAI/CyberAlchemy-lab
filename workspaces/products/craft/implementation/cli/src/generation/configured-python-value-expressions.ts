import type {TypedType, TypedParameter, ValueExpression} from '../typed-operation/contracts.js';
import {createPythonRuleValues} from './configured-python-rule-values.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';

/** Lower checked explicit value expressions without invoking domain behavior. */
export function createPythonValueExpressions(values: ReturnType<typeof createPythonRuleValues>, inputs: readonly TypedParameter[], fail: (reason: string) => never) {
  type Bound = {type: TypedType; code: string};
  const scope = new Map(inputs.map((p, i) => [p.name, {type: p.type, code: 'p' + i}])); let next = 0;
  const literal = (type: string, value: unknown): string => type === 'UInt64' ? String(value) : type === 'Bool' ? value ? 'True' : 'False' : `_v.STRING.normalize(${q(value as string)})`;
  const value = (node: ValueExpression): Bound => {
    if (node.op === 'literal') return {type: {kind: 'scalar', name: node.type}, code: literal(node.type, node.value)};
    if (node.op === 'variant') {
      for (const d of values.declarations.values()) if (d.kind === 'Enum') {
        const variant = d.contract.variants.find(v => v.ontology_variant === node.selector && v.payload === null);
        if (variant) {const type: TypedType = {kind: 'named', selector: d.selector}; return {type, code: `${values.ensure(type)}.normalize({"variant": ${q(variant.name)}})`};}
      }
      return fail('unknown payload-free variant:' + node.selector);
    }
    if (node.op === 'to_set') {
      const source = value(node.value); if (source.type.kind !== 'list') return fail('to_set requires a list');
      return {type: {kind: 'set', element: source.type.element}, code: `_to_set(${source.code}, ${values.ensure(source.type.element)})`};
    }
    let current: Bound = scope.get(node.root) ?? fail('unknown input:' + node.root);
    for (const property of node.properties) {
      const collection = current.type.kind === 'list' || current.type.kind === 'set';
      const owner = current.type.kind === 'list' || current.type.kind === 'set' ? current.type.element : current.type;
      if (owner.kind === 'reference') {
        const declaration = values.get(owner.selector); if (declaration.kind !== 'Entity') return fail('reference target must be an Entity');
        const field = declaration.contract.properties.find(f => f.name === owner.projection[0] && f.identity) ?? fail('invalid reference identity projection');
        if (field.ontology_property !== property) return fail('reference exposes only its identity projection');
        current = {type: collection ? {kind: current.type.kind as 'list' | 'set', element: field.type} : field.type, code: current.code};
        continue;
      }
      if (owner.kind !== 'named') return fail('property requires a named value');
      const declaration = values.get(owner.selector); if (declaration.kind === 'Enum') return fail('Enum has no record properties');
      const field = declaration.contract.properties.find(f => f.ontology_property === property) ?? fail('unknown ontology property:' + property);
      if (collection) {
        const item = 'q' + next++, mapped = `tuple(${item}[${q(field.name)}] for ${item} in ${current.code})`;
        current = {type: {kind: current.type.kind as 'list' | 'set', element: field.type}, code: current.type.kind === 'set' ? `_to_set(${mapped}, ${values.ensure(field.type)})` : mapped};
      } else current = {type: field.type, code: current.code + '[' + q(field.name) + ']'};
    }
    return current;
  };
  return {value, literal};
}
