import type {FieldReferenceModel} from '../input/field-reference-model.js';
import type {TypedType} from '../typed-operation/contracts.js';
import {canonicalJson} from '../input/source-manifest.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';

/** Checked declarations specialize static fact protocols. Identity references
 * are not looked up, and normalizing a fact never executes an invariant. */
export function createPythonRuleValues(model: FieldReferenceModel | null, fail: (reason: string) => never) {
  const declarations = new Map(model?.declarations.map(d => [d.selector, d]) ?? []);
  const types = new Map<string, string>(), rows: string[] = [];
  const get = (selector: string) => declarations.get(selector) ?? fail('missing checked declaration:' + selector);
  const tuple = (items: string[]) => '(' + items.join(', ') + (items.length ? ',' : '') + ')';
  const ensure = (type: TypedType): string => {
    const id = canonicalJson(type), found = types.get(id); if (found) return found;
    let source: string;
    if (type.kind === 'scalar') source = '_v.' + ({String: 'STRING', Bool: 'BOOL', UInt64: 'UINT64'}[type.name]);
    else if (type.kind === 'reference') {
      const d = get(type.selector); if (d.kind !== 'Entity') return fail('reference target must be an Entity:' + type.selector);
      const field = d.contract.properties.find(f => f.name === type.projection[0] && f.identity);
      if (!field) return fail('reference projection must select the Entity identity:' + type.selector + '#' + type.projection[0]);
      source = ensure(field.type);
    } else if (type.kind === 'named') {
      const d = get(type.selector);
      if (d.kind === 'Enum') source = `_facts.named_sum_fact(${q(d.selector)}, ${ensure({kind: 'sum', variants: d.contract.variants})})`;
      else {
        const fields = [...d.contract.properties].sort((a, b) => a.name < b.name ? -1 : 1);
        const items = fields.map(f => `(${q(f.name)}, ${ensure(f.type)}, ${f.type.kind === 'optional' ? 'True' : 'False'})`);
        const keys = d.kind === 'Entity' ? fields.filter(f => f.identity) : fields;
        source = `_facts.record_fact(${q(d.kind)}, ${q(d.selector)}, ${tuple(items)}, ${tuple(keys.map(f => q(f.name)))})`;
      }
    } else if (type.kind === 'sum') source = '_facts.sum_fact({' + [...type.variants].sort((a, b) => a.name < b.name ? -1 : 1).map(v => q(v.name) + ': ' + (v.payload ? ensure(v.payload) : 'None')).join(', ') + '})';
    else source = type.kind === 'optional' ? `_facts.optional_fact(${ensure(type.element)})` : `_facts.sequence_fact(${ensure(type.element)}, ${type.kind === 'set' ? 'True' : 'False'})`;
    const name = '_fact_type' + types.size; types.set(id, name); rows.push(name + ' = ' + source + '\n'); return name;
  };
  return {ensure, get, declarations, source: () => rows.join('')};
}
