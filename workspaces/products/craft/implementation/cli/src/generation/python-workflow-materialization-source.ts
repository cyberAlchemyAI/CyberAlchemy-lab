import type {FieldReferenceModel} from '../input/field-reference-model.js';
import type {FieldSpec} from '../input/project-model.js';
import type {ValueExpression} from '../typed-operation/contracts.js';
import type {CheckedWorkflowBindings, WorkflowValueExpression} from '../typed-operation/workflow-bindings.js';
import {createPythonRuleValues} from './configured-python-rule-values.js';
import {createPythonReadTypes} from './configured-python-read-types.js';
import {createPythonValueExpressions} from './configured-python-value-expressions.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';
import {pythonFrozenLiteral} from './configured-python-calculation-source.js';

const fail = (why: string): never => {throw new TypeError('PYTHON_WORKFLOW_MATERIALIZATION:' + why);};
const tuple = (items: readonly string[]) => '(' + items.map(i => i + ',').join(' ') + ')';

/** Static occurrence functions; no Operation imports, clocks, or source interpreter. */
export function renderPythonWorkflowMaterialization(w: CheckedWorkflowBindings, model: FieldReferenceModel | null, runtime: string,
  references: readonly {selector: string; module: string;scalar?:'String'|'UInt64'}[], descriptor: unknown): string {
  const values = createPythonRuleValues(model, fail), types = createPythonReadTypes(model, fail), b = w.bindings;
  const inputs = b.inputs.map(p => ({...p, protocol: values.ensure(p.type), ...types.ensure(p.type)}));
  const results = w.steps.map((s, i) => ({...s, protocol: values.ensure(s.signature.result), ...types.ensure(s.signature.result), className: '_Result' + i}));
  const output = {protocol: values.ensure(b.result.type), ...types.ensure(b.result.type)};
  const referenceIndex = (selector: string) => references.findIndex(r => r.selector === selector);
  const eventSources: string[] = [];
  const eventTypes = w.event_inputs.map((e, i) => {
    const name = '_Event' + i, c = e.contract, generated = c.occurred_at_policy === 'generated';
    const native = (f: FieldSpec, input: boolean) => f.type_ref.kind === 'reference' ? input ? (references[referenceIndex(f.type_ref.selector)]?.scalar==='UInt64'?'int | str':'str') : '_Ref' + referenceIndex(f.type_ref.selector) :
      ({string: 'str', boolean: 'bool', integer: input ? 'int | str' : 'int', decimal: input ? 'int | float' : 'float', timestamp: 'str', uuid: 'str'})[f.type_ref.name];
    const normalize = (f: FieldSpec, expr: string) => f.type_ref.kind === 'reference' ? `_Ref${referenceIndex(f.type_ref.selector)}(${references[referenceIndex(f.type_ref.selector)]?.scalar==='UInt64'?'_event_ref_uint64':'_e.text'}(${expr}))` :
      `_e.${{string: 'string', boolean: 'boolean', integer: 'integer', decimal: 'decimal', timestamp: 'text', uuid: 'text'}[f.type_ref.name]}(${expr})`;
    const fields = [...c.payload].sort((a, b) => a.field_id < b.field_id ? -1 : 1);
    const shape = (name: string, fields: readonly FieldSpec[]) => types.record(name, fields.map(f => ({name: f.field_id, input: native(f, true), native: native(f, false), optional: !f.required})));
    const occurrence = shape(name + 'Occurrence', [c.occurrence_id]), payload = shape(name + 'Payload', fields);
    const shapeType = types.record(name, [{name: 'occurrence', ...occurrence, optional: false}, ...(generated ? [] : [{name: 'occurredAt', input: 'str', native: 'str', optional: false}]), {name: 'payload', ...payload, optional: false}]);
    const keys = generated ? ['occurrence', 'payload'] : ['occurrence', 'occurredAt', 'payload'], id = q(c.occurrence_id.field_id);
    const items = fields.map(f => {const item = q(f.field_id) + ': ' + normalize(f, 'p[' + q(f.field_id) + ']'); return f.required ? item : `**({${item}} if ${q(f.field_id)} in p else {})`;});
    eventSources.push(`def _capture_event${i}(raw) -> ${shapeType.native}:\n    d = _e.data(raw, ${tuple(keys.map(q))}, ${tuple(keys.map(q))})\n    o = _e.data(d["occurrence"], (${id},), (${id},))\n    p = _e.data(d["payload"], ${tuple(fields.map(f => q(f.field_id)))}, ${tuple(fields.filter(f => f.required).map(f => q(f.field_id)))})\n    return _cast(${shapeType.native}, _MappingProxyType({"occurrence": _MappingProxyType({${id}: ${normalize(c.occurrence_id, 'o[' + id + ']')}}), ${generated ? '' : '"occurredAt": _e.text(d["occurredAt"]), '}"payload": _MappingProxyType({${items.join(', ')}})}))\n`);
    return {...e, ...shapeType, capture: '_capture_event' + i};
  });
  const captured = types.record('_CapturedFields', [...inputs.map(p => ({name: p.name, input: p.input, native: p.native, optional: false})), ...eventTypes.map(e => ({name: e.name, input: e.input, native: e.native, optional: false}))]);
  const convert = (e: WorkflowValueExpression): ValueExpression => e.op === 'input' ? {op: 'path', root: 'input:' + e.name, properties: e.properties} : e.op === 'step-result' ? {op: 'path', root: 'result:' + e.step_id, properties: e.properties} : e.op === 'to_set' ? {op: 'to_set', value: convert(e.value)} : e;
  const lower = (count: number) => {
    const params = [...inputs.map(p => ({name: 'input:' + p.name, type: p.type})), ...results.slice(0, count).map(r => ({name: 'result:' + r.step_id, type: r.signature.result}))];
    const expressions = createPythonValueExpressions(values, params, fail);
    const prelude = inputs.map((p, i) => `        p${i} = input[${q(p.name)}]\n`).join('') + results.slice(0, count).map((r, i) => `        p${inputs.length + i} = r[${q(r.step_id)}]\n`).join('');
    return {prelude, value: (e: WorkflowValueExpression) => expressions.value(convert(e))};
  };
  const calls: string[] = [];
  const emitCall = (c: CheckedWorkflowBindings['steps'][number], count: number, compensation: boolean, index: number) => {
    const name = '_Call' + index, env = lower(count), args = c.arguments.map(a => ({name: a.parameter, ...env.value(a.value)}));
    const shape = types.record('_Arguments' + index, [...args.map(a => ({name: a.name, ...types.ensure(a.type), optional: false})), ...c.events.map(e => {const t = eventTypes.find(t => t.name === e.input)!; return {name: e.parameter, input: t.input, native: t.native, optional: false};})]);
    calls.push(`@_dataclass(frozen=True, slots=True)\nclass ${name}:\n    operation_ref: _Literal[${q(c.operation_ref)}] = ${q(c.operation_ref)}\n    action_sha256: _Literal[${q(c.action_sha256)}] = ${q(c.action_sha256)}\n\n    def arguments(self, input: CapturedInput, results: list[CapturedResult] | tuple[CapturedResult, ...]) -> ${shape.native}:\n        r = _prefix(input, results, ${count}, ${compensation ? w.steps.length : count})\n${env.prelude}        return _cast(${shape.native}, _MappingProxyType({${[...args.map(a => q(a.name) + ': ' + a.code), ...c.events.map(e => q(e.parameter) + ': input[' + q(e.input) + ']')].join(', ')}}))\n\n    def operation_input(self, input: CapturedInput, results: list[CapturedResult] | tuple[CapturedResult, ...]) -> ${shape.input}:\n        return _cast(${shape.input}, _capture_data(self.arguments(input, results), True, True))\n`);
    return name;
  };
  const stepCalls = w.steps.map((s, i) => emitCall(s, i, false, i));
  const compCalls = w.compensations.map((c, i) => emitCall({...c, step_id: c.for_step}, w.steps.findIndex(s => s.step_id === c.for_step) + 1, true, stepCalls.length + i));
  const stepsType = types.record('_Steps', w.steps.map((s, i) => ({name: s.step_id, input: q(stepCalls[i]!), native: stepCalls[i]!, optional: false})));
  const compType = types.record('_Compensations', w.compensations.map((c, i) => ({name: c.compensation_id, input: q(compCalls[i]!), native: compCalls[i]!, optional: false})));
  const env = lower(w.steps.length), resultExpr = env.value(b.result.value);
  const names = [...inputs, ...eventTypes].map(p => p.name);
  const resultClasses = results.map(r => `@_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)\nclass ${r.className}:\n    step_id: _Literal[${q(r.step_id)}]\n    action_sha256: _Literal[${q(r.action_sha256)}]\n    value: ${r.native}\n`).join('\n');
  return `from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast
from weakref import WeakSet as _WeakSet, WeakKeyDictionary as _WeakKeyDictionary
from math import isfinite as _isfinite
from codecs import lookup as _lookup_codec
from ${runtime} import values as _v, facts as _facts
${eventTypes.length ? 'from ' + runtime + ' import event_values as _e\n' : ''}${references.map((r, i) => 'from ' + r.module + ' import EventRef as _Ref' + i + '\n').join('')}
_lookup_codec("utf-16-le")
_lookup_codec("utf-16-be")
` + (references.some(r=>r.scalar==='UInt64')?`def _event_ref_uint64(value):
    if type(value) is int:
        number = value
    elif type(value) is str and 1 <= len(value) <= 20 and (value == "0" or value[0] != "0" and value.isascii() and value.isdecimal()):
        number = int(value)
    else:
        return _e.fail()
    if number < 0 or number > 18446744073709551615:
        return _e.fail()
    return number

`: '') + types.source() + '\n' + values.source() + '\n' + eventSources.join('\n') + '\n' + resultClasses + `
WorkflowInput = ${captured.input}
WorkflowValue = ${output.native}
CapturedInput = ${captured.native}
CapturedResult = ${results.map(r => r.className).join(' | ')}
StepId = _Literal[${w.steps.map(s => q(s.step_id)).join(', ')}]

@_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class _Input:
    data: _CapturedFields
    def __getitem__(self, key: str):
        return self.data[key]

_inputs = _WeakSet()
_result_inputs = _WeakKeyDictionary()
` + support + `
def capture(raw: WorkflowInput) -> CapturedInput:
    try:
        d = _capture_data(raw)
        if type(d) is not dict or set(d) != set(${tuple(names.map(q))}):
            _fail()
        data = _MappingProxyType({${[...inputs.map(p => q(p.name) + ': ' + p.protocol + '.normalize(d[' + q(p.name) + '])'), ...eventTypes.map(e => q(e.name) + ': ' + e.capture + '(d[' + q(e.name) + '])')].join(', ')}})
    except (TypeError, ValueError, KeyError):
        raise TypeError("WORKFLOW_VALUE") from None
    input = _Input(_cast(_CapturedFields, data))
    _inputs.add(input)
    return _cast(CapturedInput, input)

` + (results.length > 1 ? results.map(r => `@_overload\ndef capture_result(input: CapturedInput, step_id: _Literal[${q(r.step_id)}], raw: object) -> ${r.className}: ...\n`).join('') : '') + `def capture_result(input: CapturedInput, step_id: StepId, raw: object) -> CapturedResult:
    _assert_input(input)
    if type(step_id) is not str:
        _fail()
    try:
        data = _capture_data(raw, True)
` + results.map(r => `        if step_id == ${q(r.step_id)}:\n            row = ${r.className}(${q(r.step_id)}, ${q(r.action_sha256)}, ${r.protocol}.normalize(data))\n            _result_inputs[row] = input\n            return row\n`).join('') + `    except (TypeError, ValueError, KeyError):
        raise TypeError("WORKFLOW_VALUE") from None
    return _fail()

def _prefix(input, results, minimum, maximum):
    _assert_input(input)
    if (type(results) is not list and type(results) is not tuple) or not minimum <= len(results) <= maximum:
        _fail()
    ids = ${tuple(results.map(r => q(r.step_id)))}
    classes = ${tuple(results.map(r => r.className))}
    r = {}
    for i, row in enumerate(results):
        if type(row) is not classes[i] or _result_inputs.get(row) is not input or row.step_id != ids[i]:
            _fail()
        r[row.step_id] = row.value
    return r

` + calls.join('\n') + `
steps = _cast(${stepsType.native}, _MappingProxyType({${w.steps.map((s, i) => q(s.step_id) + ': ' + stepCalls[i] + '()').join(', ')}}))
compensations = _cast(${compType.native}, _MappingProxyType({${w.compensations.map((c, i) => q(c.compensation_id) + ': ' + compCalls[i] + '()').join(', ')}}))

def result(input: CapturedInput, results: list[CapturedResult] | tuple[CapturedResult, ...]) -> ${output.native}:
    r = _prefix(input, results, ${w.steps.length}, ${w.steps.length})
` + env.prelude.replaceAll('        ', '    ') + `    return ${output.protocol}.normalize(${resultExpr.code})

descriptor = ${pythonFrozenLiteral(descriptor)}
__all__ = ["WorkflowInput", "WorkflowValue", "CapturedInput", "CapturedResult", "StepId", "capture", "capture_result", "steps", "compensations", "result", "descriptor"]
`;
}

const support = `
def _fail():
    raise TypeError("WORKFLOW_VALUE")

def _assert_input(input):
    if type(input) is not _Input or input not in _inputs:
        _fail()

def _capture_data(value, native=False, internal_mapping=False):
    count = 0
    def copy(v, depth):
        nonlocal count
        count += 1
        if count > 20000 or depth > 64:
            _fail()
        kind = type(v)
        if v is None or kind is str or kind is bool or kind is int or kind is float and _isfinite(v):
            return v
        if kind is list or kind is tuple:
            if len(v) > 1024:
                _fail()
            return tuple(copy(item, depth + 1) for item in v)
        if native and kind is _facts._Fact:
            v = _facts._data(v)
        elif internal_mapping and kind is _MappingProxyType:
            v = dict(v)
        elif kind is not dict:
            _fail()
        if len(v) > 2048 or any(type(k) is not str for k in v):
            _fail()
        return {k: copy(item, depth + 1) for k, item in v.items()}
    return copy(value, 0)

def _to_set(items, element):
    keyed = {}
    for item in items:
        keyed.setdefault(element.key(item), item)
    return tuple(keyed[key] for key in sorted(keyed, key=lambda key: key.encode("utf-16-be", "surrogatepass")))
`;
