import type {TypedMappingContract} from '../typed-backend/contracts.js';
import {assignableMappingType, checkTypedInputMapping, type TypedInputMappingContract} from '../typed-backend/mapping-inputs.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import type {TypedType, TypedParameter} from '../typed-operation/contracts.js';
import {createPythonRuleValues} from './configured-python-rule-values.js';
import {createPythonValueExpressions} from './configured-python-value-expressions.js';
import {createPythonReadTypes} from './configured-python-read-types.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';
import {pythonFrozenLiteral} from './configured-python-calculation-source.js';

export function renderPythonMapping(contract: TypedMappingContract | TypedInputMappingContract, model: FieldReferenceModel, runtimeModule: string) {
  const fail = (message: string): never => {throw new TypeError('DS_PYTHON_MAPPING:' + message);};
  const values = createPythonRuleValues(model, fail), types = createPythonReadTypes(model, fail), target = values.get(contract.target);
  if (target.kind === 'Enum') return fail('Mapping target requires record fields');
  const inputs: readonly TypedParameter[] = contract.schema_version === 'domainspec.typed-mapping/v2' ? contract.inputs : [{name: 'source', type: {kind: 'named', selector: contract.source}}];
  const protocols = inputs.map(p => values.ensure(p.type)), nativeInputs = inputs.map(p => types.ensure(p.type));
  const {value, literal} = createPythonValueExpressions(values, inputs, fail);
  const lines: string[] = [], parts: string[] = [], result_fields: {name: string; type: TypedType; optional: boolean; ontology_property: string}[] = [];
  const add = (name: string, type: TypedType, ontology_property: string, code: string, fallback: string | null = null, optional = false, present = '') => {
    const variable = 'v' + result_fields.length; values.ensure(type);
    lines.push(`    ${variable} = ${code}\n`);
    if (fallback !== null) lines.push(`    if ${variable} is None:\n        ${variable} = ${fallback}\n`);
    result_fields.push({name, type, optional, ontology_property});
    parts.push(optional ? `*(((${q(name)}, ${variable}),) if ${present} else ())` : `(${q(name)}, ${variable})`);
  };
  let rawSource = '';
  if (contract.schema_version === 'domainspec.typed-mapping/v2') {
    for (const binding of checkTypedInputMapping(contract, model.declarations).bindings)
      add(binding.field.name, binding.field.type, binding.field.ontology_property, value(binding.value).code, binding.default ? value(binding.default).code : null);
  } else {
    const source = values.get(contract.source); if (source.kind === 'Enum') return fail('Mapping source requires record fields');
    rawSource = '        s = _facts._data(parameters["source"])\n';
    for (const binding of contract.fields) {
      const field = target.contract.properties.find(f => f.name === binding.target) ?? fail('unknown target field:' + binding.target);
      const from = binding.source === null ? null : source.contract.properties.find(f => f.name === binding.source) ?? fail('unknown source field:' + binding.source);
      if (from && !assignableMappingType(from.type, field.type)) fail('source/target type mismatch:' + field.name);
      if (binding.default && !assignableMappingType({kind: 'scalar', name: binding.default.type}, field.type)) fail('default type mismatch:' + field.name);
      const fallback = binding.default ? literal(binding.default.type, binding.default.value) : null, present = from ? `${q(from.name)} in s` : 'False';
      if (from && fallback === null && contract.total) lines.push(`    if not (${present}):\n        raise TypeError("MAPPING_REQUIRED_VALUE")\n`);
      const code = from ? fallback === null ? `p0[${q(from.name)}]` : `(p0[${q(from.name)}] if ${present} else ${fallback})` : fallback ?? fail('field requires source or default');
      add(field.name, field.type, field.ontology_property, code, null, !!from && fallback === null && !contract.total && from.type.kind === 'optional', present);
    }
    if (contract.total && contract.fields.length !== target.contract.properties.length) fail('total Mapping must cover every target field');
  }
  types.record('_ReadModel', result_fields.map(f => ({name: f.name, ...types.ensure(f.type), optional: f.optional})));
  const content = `from __future__ import annotations\nfrom typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast\nfrom ${runtimeModule} import values as _v, facts as _facts\nfrom codecs import lookup as _lookup_codec\n_lookup_codec("utf-16-le")\n_lookup_codec("utf-16-be")\n\n` +
    types.source() + `\n_Parameters = _TypedDict("_Parameters", {${inputs.map((p, i) => q(p.name) + ': ' + nativeInputs[i]!.input).join(', ')}})\n\n` + values.source() + `
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
` + inputs.map((p, i) => `        p${i} = ${protocols[i]}.normalize(parameters[${q(p.name)}])\n`).join('') + rawSource +
    `    except (TypeError, ValueError, KeyError):\n        raise TypeError("MAPPING_INPUT") from None\n` + lines.join('') +
    `    return _cast(_ReadModel, _facts._Fact((${parts.map(p => p + ',').join(' ')})))\n`;
  return {content, inputs, result_fields, target_kind: target.kind};
}

export function renderPythonMappingBinding(providerImport: string, callable: string, descriptor: unknown): string {
  return `from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from ${providerImport} import map_values as _map_values, _Parameters, _ReadModel

_DESCRIPTOR = ${pythonFrozenLiteral(descriptor)}

@_dataclass(frozen=True, slots=True)
class _BoundMapping:
    @property
    def descriptor(self):
        return _DESCRIPTOR

    def __call__(self, parameters: _Parameters) -> _ReadModel:
        return _map_values(parameters)

${callable} = _BoundMapping()
__all__ = [${q(callable)}]
`;
}
