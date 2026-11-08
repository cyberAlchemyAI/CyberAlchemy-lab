import {assertCheckedPublicMapping, type CheckedPublicMapping} from '../input/compiled-public-mapping.js';
import {assertCompiledProjectFields, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import type {MappingValueType} from '../typed-backend/mapping-public.js';
import {createPythonPublicMappingValues} from './configured-python-public-mapping-values.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';

export interface PythonPublicMappingImport {readonly selector: string; readonly alias: string; readonly path: string; readonly descriptor: Readonly<{selector: string; contract_sha256: string; graph_sha256: string; field_compilation_sha256: string | null}>;}
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_PUBLIC_MAPPING:' + reason);};
/** One pure projection, statically lowered from the registered checked mapping. */
export function renderPythonPublicMapping(mapping: CheckedPublicMapping, fields: CompiledProjectFields | null, imports: readonly PythonPublicMappingImport[], runtimeModule: string) {
  assertCheckedPublicMapping(mapping); if (fields !== null) assertCompiledProjectFields(fields); assertInterfaceData(imports);
  if (mapping.field_compilation_sha256 !== (fields?.compilation_sha256 ?? null)) fail('field mismatch');
  if (canonicalJson(imports.map(i => i.selector).sort()) !== canonicalJson(mapping.bindings.interface_selectors) || new Set(imports.map(i => i.alias)).size !== imports.length) fail('exact Interface imports required');
  for (const i of imports) {
    if (/^_api[0-9]+$/.exec(i.alias)?.[0] !== i.alias || /^\.+[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$/.exec(i.path)?.[0] !== i.path) fail('invalid native import');
    const source = mapping.interfaces.find(api => api.source.selector === i.selector) ?? fail('missing Interface evidence');
    if (i.descriptor.selector !== i.selector || i.descriptor.contract_sha256 !== sha256(canonicalJson(source.contract)) || i.descriptor.graph_sha256 !== mapping.certificate.graph_sha256 || i.descriptor.field_compilation_sha256 !== (fields?.compilation_sha256 ?? null)) fail('Interface descriptor mismatch');
  }
  const values = createPythonPublicMappingValues(fields?.model ?? null, mapping.interfaces.map(i => ({selector: i.source.selector, contract: i.contract})), new Map(imports.map(i => [i.selector, i.alias])), fail);
  const inputs = mapping.contract.inputs.map(p => ({...p, shape: values.ensure(p.type)}));
  const scope = new Map(inputs.map((p, i) => [p.name, {type: p.type, code: 'p' + i}]));
  const projections = mapping.bindings.fields.map(f => ({name: f.target.name, shape: values.ensure(f.target.type as MappingValueType), value: values.expression(f.value, scope).code, fallback: f.default === null ? null : values.expression(f.default, scope).code}));
  const result = mapping.contract.total && mapping.contract.target.kind === 'contract' ? '_ReadModel = ' + values.ensure(mapping.contract.target).native + '\n' : '';
  if (!result) values.types.record('_ReadModel', projections.map(p => ({name: p.name, ...p.shape, optional: false})));
  const sourceImports = imports.map(i => {const end = i.path.lastIndexOf('.'); return 'from ' + i.path.slice(0, end) + ' import ' + i.path.slice(end + 1) + ' as ' + i.alias + '\n';}).join('');
  const guards = imports.map(i => 'if ' + ['selector', 'contract_sha256', 'graph_sha256', 'field_compilation_sha256'].map(key => `${i.alias}.descriptor[${q(key)}] != ${i.descriptor[key as keyof typeof i.descriptor] === null ? 'None' : q(i.descriptor[key as keyof typeof i.descriptor]!)}`).join(' or ') + ':\n    raise TypeError("MAPPING_INTERFACE_BINDING")\n').join('');
  const content = `from __future__ import annotations
from typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast
from ${runtimeModule} import values as _v, facts as _facts
from codecs import lookup as _lookup_codec
_lookup_codec("utf-16-le")
_lookup_codec("utf-16-be")
` + sourceImports + guards + values.source() + result +
    `_Parameters = _TypedDict("_Parameters", {${inputs.map(p => q(p.name) + ': ' + p.shape.input).join(', ')}})\n` + `
def _to_set(items, element):
    keyed = {}
    for item in items:
        keyed.setdefault(element.key(item), item)
    return tuple(keyed[key] for key in sorted(keyed, key=lambda key: key.encode("utf-16-be", "surrogatepass")))

def map_values(parameters: _Parameters) -> _ReadModel:
    try:
        if type(parameters) is not dict or len(parameters) != ${inputs.length} or any(type(key) is not str for key in parameters):
            raise TypeError("MAPPING_INPUT")
        if any(key not in (${inputs.map(p => q(p.name) + ',').join(' ')}) for key in parameters):
            raise TypeError("MAPPING_INPUT")
` + inputs.map((p, i) => `        p${i} = ${p.shape.protocol}.normalize(parameters[${q(p.name)}])\n`).join('') +
    projections.map((p, i) => `        v${i} = ${p.value}\n` + (p.fallback === null ? '' : `        if v${i} is None:\n            v${i} = ${p.fallback}\n`) + `        v${i} = ${p.shape.protocol}.normalize(v${i})\n`).join('') +
    `    except (TypeError, ValueError, KeyError):\n        raise TypeError("MAPPING_INPUT") from None\n` +
    `    return _cast(_ReadModel, _facts._Fact((${projections.map((p, i) => `(${q(p.name)}, v${i}),`).join(' ')})))\n`;
  return {content, result_fields: projections.map(p => p.name)};
}
