import type {NamedInterfaceContract, InterfacePublicType} from '../typed-backend/interface.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {canonicalJson} from '../input/source-manifest.js';
import {createPythonReadTypes} from './configured-python-read-types.js';
import {createPythonRuleValues} from './configured-python-rule-values.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';
import {pythonFrozenLiteral} from './configured-python-calculation-source.js';

/** Checked, acyclic public contracts compose static protocols, not an interpreter.
 * Public contract identity is Interface selector + local contract id. No factory,
 * invariant, operation or transport is executed by this structural boundary. */
export function renderPythonInterface(selector: string, contract: NamedInterfaceContract, model: FieldReferenceModel | null, runtimeModule: string, descriptor: unknown) {
  const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_INTERFACE:' + reason);};
  const types = createPythonReadTypes(model, fail), values = createPythonRuleValues(model, fail);
  const contracts = [...contract.contracts].sort((a, b) => a.contract_id < b.contract_id ? -1 : 1);
  const operations = [...contract.operations].sort((a, b) => a.operation_id < b.operation_id ? -1 : 1);
  type Shape = {input: string; native: string; protocol: string};
  const cache = new Map<string, Shape>(), rows: string[] = []; let sequence = 0;
  const tuple = (parts: string[]) => '(' + parts.map(p => p + ',').join(' ') + ')';
  const ensure = (t: InterfacePublicType): Shape => {
    if (t.kind === 'scalar' || t.kind === 'named') return {...types.ensure(t), protocol: values.ensure(t)};
    const key = canonicalJson(t), prior = cache.get(key); if (prior) return prior;
    const name = '_Public' + sequence++, protocol = name + 'Value';
    let shape: {input: string; native: string}, expression: string;
    if (t.kind === 'contract') {
      const c = contracts.find(c => c.contract_id === t.contract_id) ?? fail('missing public contract');
      const fields = [...c.fields].sort((a, b) => a.name < b.name ? -1 : 1), children = fields.map(f => ensure(f.type));
      shape = types.record(name, fields.map((f, i) => ({name: f.name, ...children[i]!, optional: f.type.kind === 'optional'})));
      expression = `_facts.record_fact(${q(selector)}, ${q(c.contract_id)}, ${tuple(fields.map((f, i) => `(${q(f.name)}, ${children[i]!.protocol}, ${f.type.kind === 'optional' ? 'True' : 'False'})`))}, ${tuple(fields.map(f => q(f.name)))})`;
    } else if (t.kind === 'sum') {
      const variants = [...t.variants].sort((a, b) => a.name < b.name ? -1 : 1), children = variants.map(v => v.payload ? ensure(v.payload) : null);
      const cases = variants.map((v, i) => types.record(name + 'Case' + i, [{name: 'variant', input: `_Literal[${q(v.name)}]`, native: `_Literal[${q(v.name)}]`, optional: false}, ...(children[i] ? [{name: 'payload', ...children[i]!, optional: false}] : [])]));
      shape = {input: cases.map(c => c.input).join(' | '), native: cases.map(c => c.native).join(' | ')};
      expression = '_facts.sum_fact({' + variants.map((v, i) => q(v.name) + ': ' + (children[i]?.protocol ?? 'None')).join(', ') + '})';
    } else {
      const child = ensure(t.element);
      shape = t.kind === 'optional' ? {input: `(${child.input}) | None`, native: `(${child.native}) | None`} :
        {input: `list[${child.input}] | tuple[${child.input}, ...]`, native: `tuple[${child.native}, ...]`};
      expression = t.kind === 'optional' ? `_facts.optional_fact(${child.protocol})` : `_facts.sequence_fact(${child.protocol}, ${t.kind === 'set' ? 'True' : 'False'})`;
    }
    rows.push(protocol + ' = ' + expression + '\n');
    const result = {...shape, protocol}; cache.set(key, result); return result;
  };
  const publicTypes = contracts.map(c => ensure({kind: 'contract', contract_id: c.contract_id}));
  const endpoints = operations.map(o => ({request: ensure(o.request), result: ensure(o.result)}));
  types.record('PublicContracts', contracts.map((c, i) => ({name: c.contract_id, ...publicTypes[i]!, optional: false})));
  types.record('Interface', operations.map((o, i) => ({name: o.operation_id, input: `_Callable[[${endpoints[i]!.request.native}], _Awaitable[${endpoints[i]!.result.native}]]`, native: `_Callable[[${endpoints[i]!.request.native}], _Awaitable[${endpoints[i]!.result.native}]]`, optional: false})));
  const exposed = new Map<string, string>();
  const expose = (s: Shape) => {
    let id = exposed.get(s.protocol);
    if (!id) {id = '_boundary' + exposed.size; exposed.set(s.protocol, id); rows.push(`${id}: BoundaryValue[${s.native}] = BoundaryValue(${s.protocol})\n`);}
    return id;
  };
  const publicRows = contracts.map((c, i) => q(c.contract_id) + ': ' + expose(publicTypes[i]!));
  const endpointRows = operations.map((o, i) => q(o.operation_id) + ': _MappingProxyType({"request": ' + expose(endpoints[i]!.request) + ', "result": ' + expose(endpoints[i]!.result) + '})');
  const aliases = contracts.flatMap((c, i) => [{name: 'Contract_' + c.contract_id.replaceAll('-', '_'), type: publicTypes[i]!.native}, {name: 'Contract_' + c.contract_id.replaceAll('-', '_') + 'Input', type: publicTypes[i]!.input}]);
  const content = `from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Awaitable as _Awaitable, Callable as _Callable, Generic as _Generic, TypeVar as _TypeVar, Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast
from ${runtimeModule} import values as _v, facts as _facts
from codecs import lookup as _lookup_codec
_lookup_codec("utf-16-le")
_lookup_codec("utf-16-be")

_T = _TypeVar("_T")

@_dataclass(frozen=True, slots=True)
class BoundaryValue(_Generic[_T]):
    _protocol: _v.ValueProtocol[_T]

    def normalize(self, value: object) -> _T:
        try:
            return self._protocol.normalize(value)
        except (TypeError, ValueError, KeyError):
            raise TypeError("INTERFACE_VALUE") from None

    def key(self, value: object) -> str:
        return self._protocol.key(self.normalize(value))

` + types.source() + '\n' + aliases.map(a => a.name + ' = ' + a.type + '\n').join('') + values.source() + rows.join('') + `
public_contracts = _MappingProxyType({${publicRows.join(', ')}})
endpoint_values = _MappingProxyType({${endpointRows.join(', ')}})
descriptor = ${pythonFrozenLiteral(descriptor)}
version_policy = ${pythonFrozenLiteral(contract.version_policy)}

def accepts_consumer_version(value: object) -> bool:
    if type(value) is not str or len(value) > 194:
        return False
    parts = value.split(".")
    if len(parts) != 3 or any(not (1 <= len(p) <= 64) or not p.isascii() or not p.isdecimal() or (len(p) > 1 and p[0] == "0") for p in parts):
        return False
` + (contract.version_policy.mode === 'exact' ? `    return value == ${q(contract.version_policy.provider_version)}\n` :
      `    provider = ${tuple(contract.version_policy.provider_version.split('.').map(q))}\n    return parts[0] == provider[0] and ((len(parts[1]), parts[1]), (len(parts[2]), parts[2])) <= ((len(provider[1]), provider[1]), (len(provider[2]), provider[2]))\n`) +
    '\n__all__ = ["Interface", "PublicContracts", "BoundaryValue", "public_contracts", "endpoint_values", "descriptor", "version_policy", "accepts_consumer_version", ' + aliases.map(a => q(a.name)).join(', ') + ']\n';
  return {content};
}
