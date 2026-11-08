import type {RuleExpression, TypedRuleContract, TypedType, ValueExpression} from '../typed-operation/contracts.js';
import {canonicalJson} from '../input/source-manifest.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {createPythonRuleValues} from './configured-python-rule-values.js';

type Bound = Readonly<{type: TypedType; code: string}>;
export interface PythonRuleImport {readonly selector: string; readonly module: string; readonly symbol: string; readonly local: string}
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_RULE:' + reason);};

/** Static lowering of checked Rules. Structured facts are available only in
 * the explicit successor selection, never as an untyped fallback for v1. */
export function renderPythonRule(rule: TypedRuleContract, selector: string, callable: string, closure: string, runtime: string, imports: readonly PythonRuleImport[], model?: FieldReferenceModel | null): string {
  let next = 0;
  const fresh = () => 'q' + next++;
  const protocols = new Map<string, {name: string; source: string}>();
  const structured = model === undefined ? null : createPythonRuleValues(model, fail);
  const protocol = (type: TypedType): string => {
    if (structured) return structured.ensure(type);
    const key = canonicalJson(type), found = protocols.get(key);
    if (found) return found.name;
    let source: string;
    if (type.kind === 'scalar') source = '_v.' + ({String: 'STRING', Bool: 'BOOL', UInt64: 'UINT64'}[type.name]);
    else if (type.kind === 'optional' || type.kind === 'list' || type.kind === 'set') source = `_v.${type.kind}_value(${protocol(type.element)})`;
    else return fail('structured values require a Python fact adapter:' + selector);
    const name = '_type' + protocols.size; protocols.set(key, {name, source}); return name;
  };
  const same = (a: TypedType, b: TypedType) => canonicalJson(a) === canonicalJson(b);
  const value = (node: ValueExpression, scope: ReadonlyMap<string, Bound>): Bound => {
    if (node.op === 'literal') return {type: {kind: 'scalar', name: node.type}, code: node.type === 'Bool' ? (node.value ? 'True' : 'False') : node.type === 'UInt64' ? String(node.value) : `_v.STRING.normalize(${q(node.value as string)})`};
    if (node.op === 'variant') {
      for (const d of structured?.declarations.values() ?? []) if (d.kind === 'Enum') {
        const variant = d.contract.variants.find(v => v.ontology_variant === node.selector && v.payload === null);
        if (variant) {const type: TypedType = {kind: 'named', selector: d.selector}; return {type, code: `${protocol(type)}.normalize({"variant": ${q(variant.name)}})`};}
      }
      return fail('variant requires a checked payload-free Enum case:' + node.selector);
    }
    if (node.op === 'to_set') {
      const source = value(node.value, scope);
      if (source.type.kind !== 'list') return fail('to_set requires a list');
      return {type: {kind: 'set', element: source.type.element}, code: `_to_set(${source.code}, ${protocol(source.type.element)})`};
    }
    let current = scope.get(node.root) ?? fail('unknown Rule parameter:' + node.root);
    for (const property of node.properties) {
      if (!structured) return fail('record path requires a Python fact adapter:' + selector);
      const collection = current.type.kind === 'list' || current.type.kind === 'set';
      const owner = current.type.kind === 'list' || current.type.kind === 'set' ? current.type.element : current.type;
      if (owner.kind !== 'named') return fail('property requires a named value');
      const d = structured.get(owner.selector); if (d.kind === 'Enum') return fail('Enum has no record properties');
      const field = d.contract.properties.find(f => f.ontology_property === property) ?? fail('unknown ontology property:' + property);
      if (collection) {
        const item = fresh(), mapped = `tuple(${item}[${q(field.name)}] for ${item} in ${current.code})`;
        current = {type: {kind: current.type.kind as 'list' | 'set', element: field.type}, code: current.type.kind === 'set' ? `_to_set(${mapped}, ${protocol(field.type)})` : mapped};
      } else current = {type: field.type, code: current.code + '[' + q(field.name) + ']'};
    }
    return current;
  };
  const expression = (node: RuleExpression, scope: ReadonlyMap<string, Bound>): string => {
    if (node.op === 'all' || node.op === 'any') return '(' + node.terms.map(t => expression(t, scope)).join(node.op === 'all' ? ' and ' : ' or ') + ')';
    if (node.op === 'not') return '(not ' + expression(node.term, scope) + ')';
    if (node.op === 'rule_ref') {
      const target = imports.find(i => i.selector === node.selector) ?? fail('unplanned Rule dependency');
      return target.local + '({' + [...node.arguments].sort((a, b) => a.parameter < b.parameter ? -1 : 1).map(a => q(a.parameter) + ': ' + value(a.value, scope).code).join(', ') + '})';
    }
    if (node.op === 'eq' || node.op === 'lt' || node.op === 'contains' || node.op === 'set_equal') {
      const left = value(node.left, scope), right = value(node.right, scope);
      if (node.op === 'contains') {
        if ((left.type.kind !== 'list' && left.type.kind !== 'set') || !same(left.type.element, right.type)) return fail('contains type mismatch');
        const item = fresh(), p = protocol(right.type);
        return `any(${p}.key(${item}) == ${p}.key(${right.code}) for ${item} in ${left.code})`;
      }
      if (!same(left.type, right.type)) return fail('comparison type mismatch');
      if (node.op === 'lt') {
        if (left.type.kind !== 'scalar' || left.type.name === 'Bool') return fail('lt requires String or UInt64');
        // Python code-point ordering differs from the selected UTF-16 ordering.
        const ordered = (code: string) => left.type.kind === 'scalar' && left.type.name === 'String' ? `${code}.encode("utf-16-be", "surrogatepass")` : code;
        return `(${ordered(left.code)} < ${ordered(right.code)})`;
      }
      if (node.op === 'set_equal' && left.type.kind !== 'set') return fail('set_equal requires a set');
      const p = protocol(left.type); return `(${p}.key(${left.code}) == ${p}.key(${right.code}))`;
    }
    if (node.op !== 'exists' && node.op !== 'exactly_one' && node.op !== 'unique') return fail('unsupported Rule expression');
    const source = value(node.collection, scope);
    if (source.type.kind !== 'list' && source.type.kind !== 'set') return fail('quantifier requires a collection');
    const item = fresh(), nested = new Map(scope); nested.set(node.binding, {type: source.type.element, code: item});
    if (node.op === 'unique') {
      if (node.where.op !== 'eq' || node.where.left.op !== 'path' || canonicalJson(node.where.left) !== canonicalJson(node.where.right)) return fail('unique requires an identical path key');
      const key = value(node.where.left, nested);
      return `(len({${protocol(key.type)}.key(${key.code}) for ${item} in ${source.code}}) == len(${source.code}))`;
    }
    const predicate = expression(node.where, nested);
    return node.op === 'exists' ? `any(${predicate} for ${item} in ${source.code})` : `(sum(1 for ${item} in ${source.code} if ${predicate}) == 1)`;
  };
  const parameters = rule.parameters.map(p => protocol(p.type));
  const result = expression(rule.expression, new Map(rule.parameters.map((p, i) => [p.name, {type: p.type, code: 'p' + i}])));
  return `from __future__ import annotations
from ${runtime} import values as _v
${structured ? `from ${runtime} import facts as _facts\n` : ''}\
${imports.map(i => `from ${i.module} import ${i.symbol} as ${i.local}\n`).join('')}
RULE_ID = ${q(selector)}
CLOSURE_SHA256 = ${q(closure)}
${[...protocols.values()].map(p => `${p.name} = ${p.source}\n`).join('')}
${structured?.source() ?? ''}\
def _to_set(items, element):
    # Explicit list-to-set projection deduplicates; set INPUT still rejects duplicates.
    keyed = {}
    for item in items:
        keyed.setdefault(element.key(item), item)
    return tuple(keyed[key] for key in sorted(keyed, key=lambda key: key.encode("utf-16-be", "surrogatepass")))


def ${callable}(parameters: dict[str, object]) -> bool:
    if type(parameters) is not dict or any(type(key) is not str for key in parameters):
        raise TypeError("RULE_INPUT")
    if set(parameters) != {${rule.parameters.map(p => q(p.name)).join(', ')}}:
        raise TypeError("RULE_INPUT")
${rule.parameters.map((p, i) => `    p${i} = ${parameters[i]}.normalize(parameters[${q(p.name)}])\n`).join('')}    return ${result}
`;
}
