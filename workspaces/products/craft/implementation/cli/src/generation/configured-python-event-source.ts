import type {FieldSpec} from '../input/project-model.js';
import type {EventSource} from './configured-event-source.js';
import {createPythonReadTypes} from './configured-python-read-types.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';
import {pythonFrozenLiteral} from './configured-python-calculation-source.js';
import type {EventReferenceIdentity} from './event-reference-identity.js';

/** Frozen Event data, not an Entity factory, occurrence registry or publisher. */
export function renderPythonEvent(source: EventSource, runtimeModule: string, referenceImports: readonly Readonly<{selector: string; module: string; identity:EventReferenceIdentity}>[]): string {
  const types = createPythonReadTypes(null, reason => {throw new TypeError('DS_PYTHON_EVENT:' + reason);});
  const fields = [...source.payload].sort((a, b) => a.field_id < b.field_id ? -1 : a.field_id > b.field_id ? 1 : 0);
  const refs = [...new Set([source.occurrence_id, ...fields].flatMap(f => f.type_ref.kind === 'reference' ? [f.type_ref.selector] : []))].sort();
  const native = (f: FieldSpec, input = false): string => {
    if(f.type_ref.kind==='reference'){
      const selector=f.type_ref.selector,identity=referenceImports.find(r=>r.selector===selector)!.identity;
      return input?(identity.scalar==='UInt64'?'int | str':'str'):'_Ref'+refs.indexOf(selector);
    }
    return ({string: 'str', boolean: 'bool', integer: input ? 'int | str' : 'int', decimal: input ? 'int | float' : 'float', timestamp: 'str', uuid: 'str'})[f.type_ref.name];
  };
  const normalize = (f: FieldSpec, expr: string): string => {
    if(f.type_ref.kind==='reference'){
      const selector=f.type_ref.selector,identity=referenceImports.find(r=>r.selector===selector)!.identity;
      return `_Ref${refs.indexOf(selector)}(${identity.scalar==='UInt64'?'_event_ref_uint64':'_e.text'}(${expr}))`;
    }
    return `_e.${{string: 'string', boolean: 'boolean', integer: 'integer', decimal: 'decimal', timestamp: 'text', uuid: 'text'}[f.type_ref.name]}(${expr})`;
  };
  const shape = (name: string, fields: readonly FieldSpec[]) => types.record(name, fields.map(f => ({name: f.field_id, input: native(f, true), native: native(f), optional: !f.required})));
  shape('_Occurrence', [source.occurrence_id]); shape('_Payload', fields);
  const id = q(source.occurrence_id.field_id), generated = source.occurred_at_policy === 'generated';
  const tuple = (items: readonly string[]) => '(' + items.map(v => q(v) + ',').join(' ') + ')';
  const keys = generated ? ['occurrence', 'payload'] : ['occurrence', 'occurredAt', 'payload'];
  const payload = fields.map(f => {
    const item = q(f.field_id) + ': ' + normalize(f, 'p[' + q(f.field_id) + ']');
    return f.required ? item : `**({${item}} if ${q(f.field_id)} in p else {})`;
  }).join(', ');
  return `from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Callable as _Callable, Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast
from ${runtimeModule} import event_values as _e

` + refs.map((selector, i) => {
      const dependency = referenceImports.find(r => r.selector === selector);
      if (!dependency) throw new TypeError('DS_PYTHON_EVENT:missing reference type:' + selector);
      return `from ${dependency.module} import EventRef as _Ref${i}\n`;
    }).join('') + '\n' + (referenceImports.some(r=>r.identity.scalar==='UInt64')?`def _event_ref_uint64(value):
    if type(value) is int:
        number = value
    elif type(value) is str and 1 <= len(value) <= 20 and (value == "0" or value[0] != "0" and value.isascii() and value.isdecimal()):
        number = int(value)
    else:
        return _e.fail()
    if number < 0 or number > 18446744073709551615:
        return _e.fail()
    return number

`: '') + types.source() +
    `\nEventInput = _TypedDict("EventInput", {"occurrence": _OccurrenceInput, ${generated ? '' : '"occurredAt": str, '}"payload": _PayloadInput})

@_dataclass(frozen=True, slots=True)
class EventValue:
    type: _Literal[${q(source.event_type)}]
    version: _Literal[${q(source.version)}]
    occurrence: _Occurrence
    occurredAt: str
    payload: _Payload

def make(input: EventInput${generated ? ', clock: _Callable[[], str]' : ''}) -> EventValue:
    d = _e.data(input, ${tuple(keys)}, ${tuple(keys)})
    o = _e.data(d["occurrence"], (${id},), (${id},))
    p = _e.data(d["payload"], ${tuple(fields.map(f => f.field_id))}, ${tuple(fields.filter(f => f.required).map(f => f.field_id))})
    occurrence = _cast(_Occurrence, _MappingProxyType({${id}: ${normalize(source.occurrence_id, 'o[' + id + ']')}}))
    payload = _cast(_Payload, _MappingProxyType({${payload}}))
` + (generated ? `    if not callable(clock):\n        return _e.fail()\n    occurredAt = _e.text(clock())\n` : `    occurredAt = _e.text(d["occurredAt"])\n`) +
    `    return EventValue(${q(source.event_type)}, ${q(source.version)}, occurrence, occurredAt, payload)\n`;
}

export function renderPythonEventBinding(provider: string, callable: string, descriptor: unknown, generated: boolean): string {
  return `from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Callable as _Callable
from ${provider} import make as _make, EventInput, EventValue

_DESCRIPTOR = ${pythonFrozenLiteral(descriptor)}

@_dataclass(frozen=True, slots=True)
class _BoundEvent:
    @property
    def descriptor(self):
        return _DESCRIPTOR

    def __call__(self, input: EventInput${generated ? ', clock: _Callable[[], str]' : ''}) -> EventValue:
        return _make(input${generated ? ', clock' : ''})

${callable} = _BoundEvent()
__all__ = [${q(callable)}, "EventInput", "EventValue"]
`;
}
