import type {TypedType} from '../typed-operation/contracts.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {canonicalJson} from '../input/source-manifest.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';
import {pythonRelativeModule, pythonSnake, pythonSymbol} from './configured-python-owned-values.js';

/** Validate raw facts with the selected factories. The returned owned values
 * are construction intermediates, not the Operation's external write format. */
export function createPythonOperationOwned(model: FieldReferenceModel | null, owner: string, target: (selector: string) => string) {
  const cache = new Map<string, string>(), imports: string[] = [], rows: string[] = [];
  const ensure = (type: TypedType): string => {
    const key = canonicalJson(type), prior = cache.get(key); if (prior) return prior;
    const name = '_own' + cache.size; cache.set(key, name);
    let expression: string;
    if (type.kind === 'scalar') expression = 'v';
    else if (type.kind === 'optional') expression = `None if v is None else ${ensure(type.element)}(v)`;
    else if (type.kind === 'list' || type.kind === 'set') expression = `tuple(${ensure(type.element)}(item) for item in v)`;
    else if (type.kind === 'sum') {
      rows.push(`def ${name}(v):\n` + type.variants.map(c => `    if v["variant"] == ${q(c.name)}:\n        return {"variant": ${q(c.name)}${c.payload ? ', "payload": ' + ensure(c.payload) + '(v["payload"])' : ''}}\n`).join('') + '    raise TypeError("OPERATION_VALUE")\n');
      return name;
    } else {
      const d = model?.declarations.find(d => d.selector === type.selector);
      if (!d) throw Error('DS_PYTHON_OPERATION:missing owned declaration');
      const module = pythonRelativeModule(owner, target(type.selector)), node = type.selector.split(':')[1]!, local = name + '_provider';
      if (d.kind === 'Enum') {
        if (d.contract.variants.every(v => v.payload === null)) {
          imports.push(`from ${module} import parse_${pythonSnake(node)} as ${local}\n`);
          expression = `${local}(v["variant"])`;
        } else {
          imports.push(`from ${module} import ${pythonSymbol(node)}ValueComponent as ${local}\n`);
          expression = `${local}.normalize(${ensure({kind: 'sum', variants: d.contract.variants})}(v))`;
        }
      } else {
        imports.push(`from ${module} import create_${pythonSnake(node)}_factory as ${local}\n`);
        const fields = d.contract.properties.map(p => q(p.name) + ': ' + ensure(p.type) + '(v[' + q(p.name) + '])');
        rows.push(`${name}_factory = ${local}()\ndef ${name}(v):\n    result = ${name}_factory.create({${fields.join(', ')}})\n    if not result.ok:\n        raise TypeError("OPERATION_VALUE:" + ",".join(result.failure_codes))\n    return result.value\n`);
        return name;
      }
    }
    rows.push(`def ${name}(v):\n    return ${expression}\n`); return name;
  };
  return {ensure, imports: () => imports.join(''), source: () => rows.join('\n')};
}
