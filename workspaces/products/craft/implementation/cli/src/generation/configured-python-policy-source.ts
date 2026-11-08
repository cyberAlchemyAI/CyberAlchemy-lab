import type {FieldReferenceModel} from '../input/field-reference-model.js';
import type {TypedRulePolicyContract} from '../typed-backend/policy-rules.js';
import {createPythonRuleValues} from './configured-python-rule-values.js';
import {createPythonReadTypes} from './configured-python-read-types.js';
import {createPythonValueExpressions} from './configured-python-value-expressions.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';
import {pythonFrozenLiteral} from './configured-python-calculation-source.js';

export interface PythonPolicyRuleImport {readonly selector: string; readonly module: string; readonly symbol: string; readonly local: string;}
/** Direct Rule calls in source order. Strategies are identities, never imports. */
export function renderPythonPolicy(contract: TypedRulePolicyContract, model: FieldReferenceModel | null, imports: readonly PythonPolicyRuleImport[], runtimeModule: string) {
  const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_POLICY:' + reason);};
  const values = createPythonRuleValues(model, fail), types = createPythonReadTypes(model, fail);
  const protocols = contract.inputs.map(p => values.ensure(p.type)), native = contract.inputs.map(p => types.ensure(p.type));
  const {value} = createPythonValueExpressions(values, contract.inputs, fail);
  const cases = contract.cases.map(c => {
    const rule = imports.find(i => i.selector === c.rule.selector) ?? fail('missing Rule import');
    const args = [...c.rule.arguments].sort((a, b) => a.parameter < b.parameter ? -1 : 1).map(a => q(a.parameter) + ': ' + value(a.value).code);
    return `    if ${rule.local}({${args.join(', ')}}):\n        return ${q(c.target)}\n`;
  }).join('');
  const targets = [...new Set([...contract.cases.map(c => c.target), contract.default_target])].sort();
  return `from __future__ import annotations
from typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast
from ${runtimeModule} import values as _v, facts as _facts
from codecs import lookup as _lookup_codec
_lookup_codec("utf-16-le")
_lookup_codec("utf-16-be")
` + imports.map(i => `from ${i.module} import ${i.symbol} as ${i.local}\n`).join('') + '\n' + types.source() +
    `\n_Parameters = _TypedDict("_Parameters", {${contract.inputs.map((p, i) => q(p.name) + ': ' + native[i]!.input).join(', ')}})\n_Strategy = _Literal[${targets.map(q).join(', ')}]\n\n` + values.source() + `
def _to_set(items, element):
    keyed = {}
    for item in items:
        keyed.setdefault(element.key(item), item)
    return tuple(keyed[key] for key in sorted(keyed, key=lambda key: key.encode("utf-16-be", "surrogatepass")))


def select(parameters: _Parameters) -> _Strategy:
    try:
        if type(parameters) is not dict or len(parameters) != ${contract.inputs.length} or any(type(key) is not str for key in parameters):
            raise TypeError("POLICY_INPUT")
        if any(key not in (${contract.inputs.map(p => q(p.name) + ',').join(' ')}) for key in parameters):
            raise TypeError("POLICY_INPUT")
` + contract.inputs.map((p, i) => `        p${i} = ${protocols[i]}.normalize(parameters[${q(p.name)}])\n`).join('') +
    `    except (TypeError, ValueError, KeyError):\n        raise TypeError("POLICY_INPUT") from None\n` + cases + `    return ${q(contract.default_target)}\n`;
}

export function renderPythonPolicyBinding(providerImport: string, callable: string, descriptor: unknown) {
  return `from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from ${providerImport} import select as _select, _Parameters, _Strategy

_DESCRIPTOR = ${pythonFrozenLiteral(descriptor)}

@_dataclass(frozen=True, slots=True)
class _BoundPolicy:
    @property
    def descriptor(self):
        return _DESCRIPTOR

    def __call__(self, parameters: _Parameters) -> _Strategy:
        return _select(parameters)

${callable} = _BoundPolicy()
__all__ = [${q(callable)}]
`;
}
