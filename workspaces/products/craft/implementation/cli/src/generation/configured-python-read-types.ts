import type {TypedType} from '../typed-operation/contracts.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {canonicalJson} from '../input/source-manifest.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';

/** Structural read typing only. These Protocols do not construct domain values
 * or replace declared concepts with classes; normalized facts implement indexing. */
export function createPythonReadTypes(model: FieldReferenceModel | null, fail: (reason: string) => never) {
  const declarations = new Map(model?.declarations.map(d => [d.selector, d]) ?? []);
  const cache = new Map<string, {input: string; native: string}>(), lines: string[] = []; let sequence = 0;
  const record = (name: string, fields: readonly {name: string; input: string; native: string; optional: boolean}[]) => {
    lines.push(`${name}Input = _TypedDict(${q(name + 'Input')}, {${fields.map(f => q(f.name) + ': ' + (f.optional ? `_NotRequired[${f.input}]` : f.input)).join(', ')}})\n`);
    lines.push(`class ${name}(_Protocol):\n` + fields.map(f => (fields.length > 1 ? '    @_overload\n' : '') + `    def __getitem__(self, key: _Literal[${q(f.name)}]) -> ${f.native}: ...\n`).join('') + (fields.length > 1 ? '    def __getitem__(self, key: str) -> object: ...\n' : fields.length ? '' : '    pass\n'));
    return {input: name + 'Input', native: name};
  };
  const ensure = (type: TypedType): {input: string; native: string} => {
    const key = canonicalJson(type), cached = cache.get(key); if (cached) return cached;
    let value: {input: string; native: string};
    if (type.kind === 'scalar') value = {input: type.name === 'UInt64' ? 'int | str' : type.name === 'Bool' ? 'bool' : 'str', native: type.name === 'UInt64' ? 'int' : type.name === 'Bool' ? 'bool' : 'str'};
    else if (type.kind === 'reference') {
      const d = declarations.get(type.selector) ?? fail('missing checked declaration:' + type.selector);
      if (d.kind !== 'Entity') return fail('reference target must be an Entity:' + type.selector);
      const field = d.contract.properties.find(f => f.name === type.projection[0] && f.identity);
      if (!field) return fail('reference projection must select the Entity identity:' + type.selector + '#' + type.projection[0]);
      value = ensure(field.type);
    } else if (type.kind === 'named') {
      const d = declarations.get(type.selector) ?? fail('missing checked declaration:' + type.selector);
      if (d.kind === 'Enum') value = ensure({kind: 'sum', variants: d.contract.variants});
      else {
        const name = '_Shape' + sequence++;
        value = record(name, d.contract.properties.map(f => ({name: f.name, ...ensure(f.type), optional: f.type.kind === 'optional'})));
      }
    } else if (type.kind === 'sum') {
      const name = '_Shape' + sequence++;
      const cases = type.variants.map((v, i) => record(name + 'Case' + i, [{name: 'variant', input: `_Literal[${q(v.name)}]`, native: `_Literal[${q(v.name)}]`, optional: false},
        ...(v.payload ? [{name: 'payload', ...ensure(v.payload), optional: false}] : [])]));
      value = {input: cases.map(c => c.input).join(' | '), native: cases.map(c => c.native).join(' | ')};
    } else {
      const child = ensure(type.element);
      value = type.kind === 'optional' ? {input: `(${child.input}) | None`, native: `(${child.native}) | None`} :
        {input: `list[${child.input}] | tuple[${child.input}, ...]`, native: `tuple[${child.native}, ...]`};
    }
    cache.set(key, value); return value;
  };
  return {ensure, record, source: () => lines.join('\n')};
}
