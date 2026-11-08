import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {stateMachineFail, type TypedStateMachineContract} from '../typed-backend/state-machine.js';
import {createPythonRuleValues} from './configured-python-rule-values.js';
import {createPythonReadTypes} from './configured-python-read-types.js';
import {createPythonValueExpressions} from './configured-python-value-expressions.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';
import {pythonFrozenLiteral} from './configured-python-calculation-source.js';

export interface PythonStateRuleImport {readonly selector: string; readonly module: string; readonly symbol: string; readonly local: string;}
export const pythonStateMember = (state: string) => state.replaceAll('-', '_').toUpperCase();
export const pythonTriggerMember = (selector: string) => selector.split(':').map(pythonStateMember).join('__');

/** Synchronous enum reducer. Event references remain symbols and intent rows. */
export function renderPythonStateMachine(c: TypedStateMachineContract, model: FieldReferenceModel | null, imports: readonly PythonStateRuleImport[], runtime: string): string {
  const values = createPythonRuleValues(model, stateMachineFail), types = createPythonReadTypes(model, stateMachineFail);
  const inputs = c.inputs.map(p => ({protocol: values.ensure(p.type), ...types.ensure(p.type)}));
  const {value} = createPythonValueExpressions(values, c.inputs, stateMachineFail);
  const states = [...c.states].sort(), triggers = [...new Set(c.transitions.map(t => t.trigger_event_ref))].sort();
  const resultTypes = c.transitions.map((t, i) => {
    const intents = t.output_intents.map((o, j) => types.record('_Intent' + i + '_' + j, ['slot', 'event_ref'].map(name => ({name, input: `_Literal[${q(o[name as keyof typeof o])}]`, native: `_Literal[${q(o[name as keyof typeof o])}]`, optional: false}))).native);
    return `@_dataclass(frozen=True, slots=True)\nclass _Transition${i}:\n    status: _Literal["transitioned"]\n    state: _Literal[State.${pythonStateMember(t.target_state)}]\n    transition_id: _Literal[${q(t.transition_id)}]\n    output_intents: tuple[${intents.length ? intents.join(', ') : '()'}]\n`;
  }).join('\n');
  const branches = c.transitions.map((t, i) => {
    let branch = `    if state is State.${pythonStateMember(t.source_state)} and trigger is Trigger.${pythonTriggerMember(t.trigger_event_ref)}:\n`;
    if (t.guard) {
      const dependency = imports.find(r => r.selector === t.guard!.selector) ?? stateMachineFail('missing Python guard');
      const args = [...t.guard.arguments].sort((a, b) => a.parameter < b.parameter ? -1 : 1).map(a => q(a.parameter) + ': ' + value(a.value).code);
      branch += `        if not ${dependency.local}({${args.join(', ')}}):\n            return _Rejected("rejected", state, "guard", ())\n`;
    }
    const intents = t.output_intents.map(o => `_MappingProxyType({"slot": ${q(o.slot)}, "event_ref": ${q(o.event_ref)}})`);
    return branch + `        return _Transition${i}("transitioned", State.${pythonStateMember(t.target_state)}, ${q(t.transition_id)}, (${intents.join(', ')}${intents.length ? ',' : ''}))\n`;
  }).join('');
  return `from __future__ import annotations
import enum as _enum
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload
from math import isfinite as _isfinite
from codecs import lookup as _lookup_codec
from ${runtime} import values as _v, facts as _facts
_lookup_codec("utf-16-le")
_lookup_codec("utf-16-be")
` + imports.map(r => `from ${r.module} import ${r.symbol} as ${r.local}\n`).join('') + `
@_enum.unique
class State(_enum.Enum):
${states.map(s => `    ${pythonStateMember(s)} = ${q(s)}\n`).join('')}
@_enum.unique
class Trigger(_enum.Enum):
${triggers.map(s => `    ${pythonTriggerMember(s)} = ${q(s)}\n`).join('')}
` + types.source() + '\n' + values.source() + '\n' + resultTypes + `
@_dataclass(frozen=True, slots=True)
class _Rejected:
    status: _Literal["rejected"]
    state: State
    reason: _Literal["guard", "no-transition"]
    output_intents: tuple[()]

Parameters = _TypedDict("Parameters", {${c.inputs.map((p, i) => q(p.name) + ': ' + inputs[i]!.input).join(', ')}})
Outcome = ${c.transitions.map((_, i) => '_Transition' + i).concat('_Rejected').join(' | ')}
initial_state: State = State.${pythonStateMember(c.initial)}
` + dataSupport + `
def reduce(state: State, trigger: Trigger, parameters: Parameters) -> Outcome:
    if type(state) is not State or not any(state is member for member in State) or type(trigger) is not Trigger or not any(trigger is member for member in Trigger):
        raise TypeError("STATE_MACHINE_INPUT")
    try:
        _check_data(parameters)
        if type(parameters) is not dict or set(parameters) != set((${c.inputs.map(p => q(p.name) + ',').join(' ')})):
            raise TypeError("STATE_MACHINE_INPUT")
` + c.inputs.map((p, i) => `        p${i} = ${inputs[i]!.protocol}.normalize(parameters[${q(p.name)}])\n`).join('') + `    except (TypeError, ValueError, KeyError):
        raise TypeError("STATE_MACHINE_INPUT") from None
` + branches + `    return _Rejected("rejected", state, "no-transition", ())
`;
}

const dataSupport = `
def _check_data(root):
    count = 0
    def visit(v, depth):
        nonlocal count
        count += 1
        if count > 20000 or depth > 64:
            raise TypeError("STATE_MACHINE_INPUT")
        kind = type(v)
        if v is None or kind is str or kind is bool or kind is int or kind is float and _isfinite(v):
            return
        if kind is list or kind is tuple:
            if len(v) > 1024:
                raise TypeError("STATE_MACHINE_INPUT")
            for item in v:
                visit(item, depth + 1)
            return
        if kind is not dict or len(v) > 2048 or any(type(k) is not str for k in v):
            raise TypeError("STATE_MACHINE_INPUT")
        for item in v.values():
            visit(item, depth + 1)
    visit(root, 0)

def _to_set(items, element):
    keyed = {}
    for item in items:
        keyed.setdefault(element.key(item), item)
    return tuple(keyed[key] for key in sorted(keyed, key=lambda key: key.encode("utf-16-be", "surrogatepass")))
`;

export function renderPythonStateMachineBinding(provider: string, callable: string, descriptor: unknown): string {
  return `from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from ${provider} import reduce as _reduce, initial_state, State, Trigger, Parameters, Outcome

_DESCRIPTOR = ${pythonFrozenLiteral(descriptor)}

@_dataclass(frozen=True, slots=True)
class _BoundStateMachine:
    @property
    def descriptor(self):
        return _DESCRIPTOR

    def __call__(self, state: State, trigger: Trigger, parameters: Parameters) -> Outcome:
        return _reduce(state, trigger, parameters)

${callable} = _BoundStateMachine()
__all__ = [${q(callable)}, "initial_state", "State", "Trigger", "Parameters", "Outcome"]
`;
}
