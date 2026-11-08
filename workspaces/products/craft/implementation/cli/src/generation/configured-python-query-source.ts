import type {TypedQueryContract, BackendPredicate, BackendValue} from '../typed-backend/contracts.js';
import {queryReturnsOptional} from '../typed-backend/contracts.js';
import type {TypedType} from '../typed-operation/contracts.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {canonicalJson} from '../input/source-manifest.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';
import {createPythonRuleValues} from './configured-python-rule-values.js';
import {pythonFrozenLiteral} from './configured-python-calculation-source.js';

import {createPythonReadTypes} from './configured-python-read-types.js';

/** Reuses the existing normalized fact algebra. No query AST is emitted. */
export function renderPythonQuery(contract: TypedQueryContract, model: FieldReferenceModel, runtimeModule: string) {
  const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_QUERY:' + reason);};
  const values = createPythonRuleValues(model, fail), types = createPythonReadTypes(model, fail), source = values.get(contract.source);
  if (source.kind !== 'Entity') return fail('Query read target must be an Entity');
  const fields = source.contract.properties, field = (name: string) => fields.find(f => f.name === name) ?? fail('unknown field:' + name);
  const parameters = contract.inputs.map(p => values.ensure(p.type));
  const rowType = types.ensure({kind: 'named', selector: contract.source});
  const rowsType = values.ensure({kind: 'list', element: {kind: 'named', selector: contract.source}});
  const resultFields = contract.projection.map(name => ({name, type: field(name).type}));
  types.record('_ReadModel', resultFields.map(f => ({name: f.name, ...types.ensure(f.type), optional: false})));
  const operand = (v: BackendValue): {type: TypedType; code: string} => {
    if (v.kind === 'literal') return {type: {kind: 'scalar', name: v.type}, code: v.type === 'UInt64' ? String(v.value) : v.type === 'Bool' ? v.value ? 'True' : 'False' : `_v.STRING.normalize(${q(String(v.value))})`};
    if (v.kind === 'field') return {type: field(v.name).type, code: `row[${q(v.name)}]`};
    const index = contract.inputs.findIndex(p => p.name === v.name); if (index < 0) return fail('unknown parameter:' + v.name);
    return {type: contract.inputs[index]!.type, code: 'p' + index};
  };
  const ordered = (code: string, type: TypedType): string => {
    if (type.kind !== 'scalar') return fail('ordering requires a required scalar');
    return type.name === 'String' ? `${code}.encode("utf-16-be", "surrogatepass")` : code;
  };
  const predicate = (e: BackendPredicate): string => {
    if (e.op === 'all' || e.op === 'any') return '(' + e.terms.map(predicate).join(e.op === 'all' ? ' and ' : ' or ') + ')';
    if (e.op === 'not') return '(not ' + predicate(e.term) + ')';
    if (!('left' in e)) return fail('unknown predicate');
    const left = operand(e.left), right = operand(e.right);
    if (canonicalJson(left.type) !== canonicalJson(right.type)) return fail('comparison type mismatch');
    if (e.op === 'eq') return `(${values.ensure(left.type)}.key(${left.code}) == ${values.ensure(right.type)}.key(${right.code}))`;
    return `(${ordered(left.code, left.type)} ${{lt: '<', lte: '<=', gt: '>', gte: '>='}[e.op]} ${ordered(right.code, right.type)})`;
  };
  const filter = contract.filter ? predicate(contract.filter) : 'True';
  const optional = queryReturnsOptional(contract);
  let ordering = '';
  if (contract.order_by) ordering = `        selected.sort(key=lambda row: ${ordered(`row[${q(contract.order_by.field)}]`, field(contract.order_by.field).type)}, reverse=${contract.order_by.direction === 'desc' ? 'True' : 'False'})\n`;
  const content = `from __future__ import annotations\nfrom typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast\nfrom ${runtimeModule} import values as _v, facts as _facts\nfrom codecs import lookup as _lookup_codec\n\n# Resolve standard codec dependencies at module load, not during a Query.\n_lookup_codec("utf-16-le")\n_lookup_codec("utf-16-be")\n\n` +
    types.source() + '\n' + `_Parameters = _TypedDict("_Parameters", {${contract.inputs.map(p => q(p.name) + ': ' + types.ensure(p.type).input).join(', ')}})\n` +
    `_RowsInput = list[${rowType.input}] | tuple[${rowType.input}, ...]\n\n` + values.source() + '\n' +
    `def query(rows: _RowsInput, parameters: _Parameters) -> ${optional ? '_ReadModel | None' : 'tuple[_ReadModel, ...]'}:\n    try:\n` +
    `        if type(parameters) is not dict or len(parameters) != ${contract.inputs.length} or any(type(key) is not str for key in parameters):\n            raise TypeError("QUERY_INPUT")\n` +
    `        if any(key not in (${contract.inputs.map(p => q(p.name) + ',').join(' ')}) for key in parameters):\n            raise TypeError("QUERY_INPUT")\n` +
    contract.inputs.map((p, i) => `        p${i} = ${parameters[i]}.normalize(parameters[${q(p.name)}])\n`).join('') +
    `        snapshots = ${rowsType}.normalize(rows)\n        selected = [row for row in snapshots if ${filter}]\n` + ordering +
    (contract.limit === null ? '' : `        selected = selected[:${contract.limit}]\n`) +
    (optional ? `        if len(selected) > 1:\n            raise RuntimeError("QUERY_CARDINALITY")\n        if not selected:\n            return None\n        row = selected[0]\n        return _cast(_ReadModel, _facts._Fact((${contract.projection.map(name => `(${q(name)}, row[${q(name)}]),`).join(' ')})))\n` :
    `        return tuple(_cast(_ReadModel, _facts._Fact((${contract.projection.map(name => `(${q(name)}, row[${q(name)}]),`).join(' ')}))) for row in selected)\n`) +
    `    except (TypeError, ValueError, KeyError):\n        raise TypeError("QUERY_INPUT") from None\n`;
  return {content, read_fields: fields.map(f => f.name).sort(), result_fields: resultFields};
}

export function renderPythonQueryBinding(providerImport: string, callable: string, descriptor: unknown, optional = false): string {
  return `from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from ${providerImport} import query as _query, _RowsInput, _Parameters, _ReadModel

_DESCRIPTOR = ${pythonFrozenLiteral(descriptor)}

@_dataclass(frozen=True, slots=True)
class _BoundQuery:
    @property
    def descriptor(self):
        return _DESCRIPTOR

    def __call__(self, rows: _RowsInput, parameters: _Parameters) -> ${optional ? '_ReadModel | None' : 'tuple[_ReadModel, ...]'}:
        return _query(rows, parameters)

${callable} = _BoundQuery()
__all__ = [${q(callable)}]
`;
}
