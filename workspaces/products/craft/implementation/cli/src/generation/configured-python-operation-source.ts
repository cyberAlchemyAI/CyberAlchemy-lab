import type {CheckedOperationAction} from '../typed-operation/action-bindings.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {createPythonRuleValues} from './configured-python-rule-values.js';
import {createPythonReadTypes} from './configured-python-read-types.js';
import {createPythonValueExpressions} from './configured-python-value-expressions.js';
import {createPythonOperationOwned} from './configured-python-operation-owned.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';
import {pythonFrozenLiteral} from './configured-python-calculation-source.js';

export interface PythonOperationImport {readonly selector: string; readonly module: string; readonly symbol: string; readonly local: string;}
export function renderPythonOperation(action: CheckedOperationAction, model: FieldReferenceModel | null, owner: string, target: (selector: string) => string, rules: readonly PythonOperationImport[], events: readonly PythonOperationImport[], runtime: string) {
  const fail = (reason: string): never => {throw Error('DS_PYTHON_OPERATION:' + reason);};
  const b = action.bindings, values = createPythonRuleValues(model, fail), types = createPythonReadTypes(model, fail), owned = createPythonOperationOwned(model, owner, target);
  const inputs = b.inputs.map(p => ({protocol: values.ensure(p.type), ...types.ensure(p.type)}));
  const scope = [...b.inputs, ...action.reads.map(r => ({name: r.parameter, type: {kind: 'named' as const, selector: r.target}}))];
  const initial = createPythonValueExpressions(values, b.inputs, fail), {value} = createPythonValueExpressions(values, scope, fail);
  const resultType = types.ensure(b.result.type), resultProtocol = values.ensure(b.result.type), result = value(b.result.value).code, resultOwner = owned.ensure(b.result.type);
  const literalField = (name: string, value: string) => ({name, input: `_Literal[${q(value)}]`, native: `_Literal[${q(value)}]`, optional: false});
  const readShapes: string[] = [], writeShapes: string[] = [], eventShapes: string[] = [];
  const reads = action.reads.map((r, i) => {
    const keyType = types.ensure(r.identity.type), keyProtocol = values.ensure(r.identity.type), protocol = values.ensure({kind: 'named', selector: r.target});
    readShapes.push(types.record('_Read' + i, [literalField('slot', r.slot), literalField('target', r.target), {name: 'key', ...keyType, optional: false}]).native);
    const variable = 'p' + (b.inputs.length + i);
    return `        key${i} = ${keyProtocol}.normalize(${initial.value(r.key).code})\n        raw${i} = await transaction.read(_MappingProxyType({"slot": ${q(r.slot)}, "target": ${q(r.target)}, "key": key${i}}))\n        if raw${i} is None:\n            return await abort("failed", "READ_NOT_FOUND")\n        ${variable} = ${protocol}.normalize(raw${i})\n        if ${keyProtocol}.key(${variable}[${q(r.identity.name)}]) != ${keyProtocol}.key(key${i}):\n            return await abort("failed", "READ_IDENTITY_MISMATCH")\n`;
  }).join('');
  const guards = action.guards.map(g => {
    const rule = rules.find(r => r.selector === g.selector) ?? fail('missing Rule import');
    return `        if not ${rule.local}({${g.arguments.map(a => q(a.parameter) + ': ' + value(a.value).code).join(', ')}}):\n            return await abort("rejected", ${q('RULE_REJECTED:' + g.selector)})\n`;
  }).join('');
  const writes = action.writes.map((w, i) => {
    const type = {kind: 'named' as const, selector: w.target};
    writeShapes.push(types.record('_Write' + i, [literalField('slot', w.slot), literalField('target', w.target), literalField('mode', w.mode), {name: 'value', ...types.ensure(type), optional: false}]).native);
    return `        write${i} = ${values.ensure(type)}.normalize(${value(w.value).code})\n        ${owned.ensure(type)}(write${i})\n`;
  }).join('');
  const eventIndex = (selector: string) => {const index = events.findIndex(e => e.selector === selector); if (index < 0) fail('missing Event import'); return index;};
  const eventCalls = action.events.map((e, i) => {
    const index = eventIndex(e.target);
    eventShapes.push(types.record('_Event' + i, [literalField('slot', e.slot), literalField('target', e.target), {name: 'value', input: `_Event${index}Value`, native: `_Event${index}Value`, optional: false}]).native);
    return `        event${i} = ${events[index]!.local}(captured[${q(e.parameter)}]${e.contract.occurred_at_policy === 'generated' ? ', clocks[' + q(e.slot) + ']' : ''})\n`;
  }).join('');
  const clockSlots = action.events.filter(e => e.contract.occurred_at_policy === 'generated').map(e => e.slot), fields = [...b.inputs.map(p => p.name), ...b.events.map(e => e.parameter)];
  const tuple = (items: string[]) => '(' + items.join(', ') + (items.length ? ',' : '') + ')';
  return `from __future__ import annotations
from asyncio import CancelledError as _CancelledError
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, Never as _Never, Callable as _Callable
from math import isfinite as _isfinite
from codecs import lookup as _lookup_codec
from ${runtime} import values as _v, facts as _facts
_lookup_codec("utf-16-le")
_lookup_codec("utf-16-be")
` + rules.map(r => `from ${r.module} import ${r.symbol} as ${r.local}\n`).join('') + events.map((e, i) => `from ${e.module} import ${e.symbol} as ${e.local}, EventInput as _Event${i}Input, EventValue as _Event${i}Value\n`).join('') + owned.imports() + '\n' + types.source() + '\n' + values.source() + '\n' + owned.source() + captureSupport + `
OperationInput = _TypedDict("OperationInput", {${b.inputs.map((p, i) => q(p.name) + ': ' + inputs[i]!.input).concat(action.events.map(e => q(e.parameter) + ': _Event' + eventIndex(e.target) + 'Input')).join(', ')}})
OperationValue = ${resultType.native}
ReadRequest = ${readShapes.join(' | ') || '_Never'}
WriteIntent = ${writeShapes.join(' | ') || '_Never'}
EventIntent = ${eventShapes.join(' | ') || '_Never'}
CommitReceipt = _TypedDict("CommitReceipt", {"status": _Literal["committed", "rejected", "indeterminate"]})

@_dataclass(frozen=True, slots=True)
class OperationBatch:
    writes: tuple[WriteIntent, ...]
    events: tuple[EventIntent, ...]

class Transaction(_Protocol):
    async def read(self, request: ReadRequest) -> object: ...
    async def commit(self, batch: OperationBatch) -> CommitReceipt: ...
    async def rollback(self) -> None: ...

class _Store(_Protocol):
    async def begin(self) -> Transaction: ...

${clockSlots.length ? '_Clocks = _TypedDict("_Clocks", {' + clockSlots.map(s => q(s) + ': _Callable[[], str]').join(', ') + '})\n' : ''}OperationDependencies = _TypedDict("OperationDependencies", {"store": _Store${clockSlots.length ? ', "clocks": _Clocks' : ''}})

@_dataclass(frozen=True, slots=True)
class OperationFailure:
    status: _Literal["rejected", "failed", "indeterminate"]
    stage: str
    code: str
    continuation: _Literal[${q(action.failure_continuation)}]
    cleanupFailed: bool

@_dataclass(frozen=True, slots=True)
class OperationSuccess:
    status: _Literal["committed"]
    value: OperationValue

OperationOutcome = OperationSuccess | OperationFailure

async def execute(parameters: OperationInput, dependencies: OperationDependencies) -> OperationOutcome:
    stage = "input"
    def failure(status, code, cleanup_failed=False):
        return OperationFailure(status, stage, code, ${q(action.failure_continuation)}, cleanup_failed)
    try:
        captured = _capture(parameters)
        if type(captured) is not dict or set(captured) != set(${tuple(fields.map(q))}):
            raise TypeError("OPERATION_INPUT")
` + b.inputs.map((p, i) => `        p${i} = ${inputs[i]!.protocol}.normalize(captured[${q(p.name)}])\n`).join('') + `    except (Exception, _CancelledError):
        return failure("failed", "OPERATION_INPUT")
    stage = "begin"
    try:
` + (clockSlots.length ? `        clocks = {${clockSlots.map(s => q(s) + ': dependencies["clocks"][' + q(s) + ']').join(', ')}}\n        if any(not callable(clock) for clock in clocks.values()):\n            raise TypeError("CLOCK_DEPENDENCY")\n` : '') + `        transaction = await dependencies["store"].begin()
    except (Exception, _CancelledError):
        return failure("failed", "BEGIN_FAILED")
    async def abort(status, code):
        try:
            await transaction.rollback()
            return failure(status, code)
        except (Exception, _CancelledError):
            return failure(status, code, True)
    commit_attempted = False
    try:
        stage = "read"
` + reads + `        stage = "guard"
` + guards + `        stage = "write-validation"
` + writes + `        stage = "event"
` + eventCalls + `        stage = "result"
        result = ${resultProtocol}.normalize(${result})
        ${resultOwner}(result)
        batch = OperationBatch(${tuple(action.writes.map((w, i) => `_MappingProxyType({"slot": ${q(w.slot)}, "target": ${q(w.target)}, "mode": ${q(w.mode)}, "value": write${i}})`))}, ${tuple(action.events.map((e, i) => `_MappingProxyType({"slot": ${q(e.slot)}, "target": ${q(e.target)}, "value": event${i}})`))})
        stage = "commit"
        commit_attempted = True
        receipt = await transaction.commit(batch)
        if type(receipt) is not dict or len(receipt) != 1 or any(type(k) is not str for k in receipt) or "status" not in receipt or type(receipt["status"]) is not str:
            return failure("indeterminate", "INVALID_COMMIT_RECEIPT")
        if receipt["status"] == "committed":
            return OperationSuccess("committed", result)
        if receipt["status"] == "rejected":
            return failure("rejected", "COMMIT_REJECTED")
        return failure("indeterminate", "COMMIT_INDETERMINATE" if receipt["status"] == "indeterminate" else "INVALID_COMMIT_RECEIPT")
    except (Exception, _CancelledError):
        if commit_attempted:
            return failure("indeterminate", "COMMIT_UNCERTAIN")
        return await abort("failed", "OPERATION_FAILED")
`;
}

const captureSupport = `
def _capture(value):
    count = 0
    def copy(v, depth):
        nonlocal count
        count += 1
        if count > 20000 or depth > 64:
            raise TypeError("OPERATION_INPUT")
        kind = type(v)
        if v is None or kind is str or kind is bool or kind is int or kind is float and _isfinite(v):
            return v
        if kind is list or kind is tuple:
            if len(v) > 1024:
                raise TypeError("OPERATION_INPUT")
            return tuple(copy(item, depth + 1) for item in v)
        if kind is not dict or len(v) > 2048 or any(type(k) is not str for k in v):
            raise TypeError("OPERATION_INPUT")
        return {k: copy(item, depth + 1) for k, item in v.items()}
    return copy(value, 0)

def _to_set(items, element):
    keyed = {}
    for item in items:
        keyed.setdefault(element.key(item), item)
    return tuple(keyed[key] for key in sorted(keyed, key=lambda key: key.encode("utf-16-be", "surrogatepass")))
`;

export function renderPythonOperationBinding(provider: string, callable: string, descriptor: unknown) {
  return `from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from ${provider} import execute as _execute, OperationInput, OperationValue, OperationOutcome, OperationDependencies, OperationBatch, Transaction, CommitReceipt, ReadRequest, WriteIntent, EventIntent

_DESCRIPTOR = ${pythonFrozenLiteral(descriptor)}

@_dataclass(frozen=True, slots=True)
class _BoundOperation:
    @property
    def descriptor(self):
        return _DESCRIPTOR

    async def __call__(self, parameters: OperationInput, dependencies: OperationDependencies) -> OperationOutcome:
        return await _execute(parameters, dependencies)

${callable} = _BoundOperation()
__all__ = [${q(callable)}, "OperationInput", "OperationValue", "OperationOutcome", "OperationDependencies", "OperationBatch", "Transaction", "CommitReceipt", "ReadRequest", "WriteIntent", "EventIntent"]
`;
}
