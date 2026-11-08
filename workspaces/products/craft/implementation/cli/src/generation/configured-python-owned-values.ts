import path from 'node:path';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import type {TypedType} from '../typed-operation/contracts.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {pythonStringLiteral as q, pythonEnumSymbol} from './configured-python-enums.js';

export const pythonSymbol = (node: string) => node.split('-').map(w => w[0]!.toUpperCase() + w.slice(1)).join('');
export const pythonSnake = (node: string) => node.replaceAll('-', '_');
const keywords = new Set('and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield'.split(' '));
// Double underscore cannot occur in the source local-name grammar.
export const pythonField = (name: string) => keywords.has(name) ? 'field__' + name : name;
export function pythonRelativeModule(from: string, to: string): string {
  const parts = path.posix.relative(path.posix.dirname(from), to).replace(/\.py$/, '').split('/');
  let up = 0; while (parts[0] === '..') {parts.shift(); up++;}
  return '.'.repeat(up + 1) + parts.join('.');
}
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_VALUE:' + reason);};

/** Pure static owned-value emission shared by algebraic Enums and factories.
 * Callers validate declaration closure and provider bindings before emitting. */
export function createPythonOwnedValues(selector: string, file: string, contract: string, model: FieldReferenceModel, target: (selector: string) => string) {
  const declarations = new Map(model.declarations.map(d => [d.selector, d]));
  const name = pythonSymbol(selector.split(':')[1]!);
  const imports = new Map<string, {selector: string; path: string; local: string; type: string; code: string; emit?: string}>();
  const classes: string[] = []; let index = 0, factIndex = 0, visits = 0;
  const render = (type: TypedType, rootShape = false): {expression: string; type: string} => {
    if (type.kind === 'scalar') return {expression: {String: 'STRING', Bool: 'BOOL', UInt64: 'UINT64'}[type.name], type: {String: 'str', Bool: 'bool', UInt64: 'int'}[type.name]};
    if(type.kind==='reference'){
      const d=declarations.get(type.selector);if(d?.kind!=='Entity')return fail('reference target must be an Entity');
      const field=d.contract.properties.find(f=>f.name===type.projection[0]&&f.identity)??fail('invalid reference identity projection');
      return render(field.type);
    }
    if (type.kind === 'named') {
      const d = declarations.get(type.selector) ?? fail('missing owned dependency:' + type.selector);
      let dep = imports.get(type.selector);
      if (!dep) {
        const n = imports.size, node = type.selector.split(':')[1]!, plain = d.kind === 'Enum' && d.contract.variants.every(v => v.payload === null);
        const module = pythonRelativeModule(file, target(type.selector));
        dep = {selector: type.selector, path: target(type.selector), type: `_Type${n}`,
          local: plain ? `enum_value(_Type${n}, _emit${n}, ${q(type.selector)}, ${q(sha256(canonicalJson(d.contract)))})` : `owned_value(_Component${n})`,
          ...(plain ? {emit: `_emit${n}`} : {}),
          code: plain ? `from ${module} import ${pythonEnumSymbol(node)} as _Type${n}, emit_${pythonSnake(node)} as _emit${n}\n` : `from ${module} import ${pythonSymbol(node)}${d.kind === 'Enum' ? 'Case' : 'Snapshot'} as _Type${n}, ${pythonSymbol(node)}ValueComponent as _Component${n}\n`};
        imports.set(type.selector, dep);
      }
      return {expression: dep.local, type: dep.type};
    }
    if (type.kind !== 'sum') {
      const element = render(type.element); return {expression: `${type.kind}_value(${element.expression})`, type: type.kind === 'optional' ? `(${element.type} | None)` : `tuple[${element.type}, ...]`};
    }
    const ordinal = index++, prefix = rootShape ? name : `_${name}Inner${ordinal}`;
    const variants = [...type.variants].sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0).map(v => {
      const payload = v.payload === null ? null : render(v.payload), caseName = `${prefix}Variant${v.name}`;
      classes.push(`@_dataclass(frozen=True, slots=True, eq=False, init=False, weakref_slot=True)\nclass ${caseName}(_OwnedCase):\n    variant: _Literal[${q(v.name)}]\n${payload ? '    payload: ' + payload.type + '\n' : ''}\n    def __init__(self, *args, **kwargs):\n        raise TypeError("SUM_CONSTRUCTION_REQUIRES_COMPONENT")\n`);
      return {name: v.name, caseName, payload};
    });
    return {expression: `sum_value({${variants.map(v => `${q(v.name)}: (${v.caseName}, ${v.payload?.expression ?? 'None'})`).join(', ')}}, ${q(rootShape ? selector : selector + '/inline/' + ordinal)}, ${q(contract)})`, type: variants.map(v => v.caseName).join(' | ')};
  };
  const fact = (type: TypedType, code: string): string => {
    if (++visits > 10000) return fail('fact view source limit');
    if (type.kind === 'scalar') return code;
    if(type.kind==='reference')return code;
    if (type.kind === 'optional') return `(None if ${code} is None else ${fact(type.element, code)})`;
    if (type.kind === 'list' || type.kind === 'set') {const item = 'fact' + factIndex++; return `tuple(${fact(type.element, item)} for ${item} in ${code})`;}
    if (type.kind === 'named') {
      const d = declarations.get(type.selector) ?? fail('missing fact declaration');
      if (d.kind === 'Enum') {
        if (d.contract.variants.every(v => v.payload === null)) {render(type); return `{"variant": ${imports.get(type.selector)!.emit}(${code})}`;}
        return fact({kind: 'sum', variants: d.contract.variants}, code);
      }
      return '{' + d.contract.properties.map(p => q(p.name) + ': ' + fact(p.type, code + '.fields.' + pythonField(p.name))).join(', ') + '}';
    }
    return '(' + type.variants.map(v => `({"variant": ${q(v.name)}${v.payload ? ', "payload": ' + fact(v.payload, code + '.payload') : ''}} if ${code}.variant == ${q(v.name)} else `).join('') + '_invalid_fact()' + ')'.repeat(type.variants.length) + ')';
  };
  const prelude = (support: string) => `from __future__ import annotations\n\nfrom dataclasses import dataclass as _dataclass\nfrom typing import Literal as _Literal\nfrom ${pythonRelativeModule(file, support)} import OwnedCase as _OwnedCase, STRING, BOOL, UINT64, optional_value, list_value, set_value, sum_value, owned_value, enum_value\n` + [...imports.values()].map(i => i.code).join('') + '\n\n' + classes.join('\n\n');
  return {render, fact, prelude, imports};
}
