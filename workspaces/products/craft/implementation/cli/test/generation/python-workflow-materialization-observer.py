"""Checked bindings -> complete native materialization AST, without target imports.

Recognizes the selected finite Python grammar, not arbitrary equivalent programs.
Types and expressions reuse the independent Operation observer, not a renderer.
Fixed capture mechanics below are reviewed contract expectations; shared runtime
bytes remain pinned to separately qualified support, not re-proved here.
"""
import ast
import hashlib
import importlib.util
import json
import pathlib
import sys

spec = importlib.util.spec_from_file_location("operation_observer", pathlib.Path(__file__).resolve().parents[2] / "src/verification/python-operation-observer.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def require(ok, why):
    if not ok:
        raise ValueError("PYTHON_WORKFLOW_MATERIALIZATION_OBSERVER:" + why)


def freeze(v):
    if type(v) is dict:
        return "_MappingProxyType({" + ", ".join(repr(k) + ": " + freeze(x) for k, x in v.items()) + "})"
    if type(v) is list:
        return base.tuple_code([freeze(x) for x in v])
    return repr(v)


# Exact bounded inert-copy and capture provenance contract. This text is never
# imported from the generated program or executed by the source observer.
CAPTURE = '''
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
'''


def expected(w, model, provider, root, references, descriptor):
    c = base.Context(model, provider, root)
    inputs, results = w["bindings"]["inputs"], w["steps"]
    input_types, result_types = [], []
    for p in inputs:
        input_types.append((c.protocol(p["type"]), *c.type(p["type"])))
    for s in results:
        result_types.append((c.protocol(s["signature"]["result"]), *c.type(s["signature"]["result"])))
    output = w["bindings"]["result"]
    output_protocol = c.protocol(output["type"])
    _, output_type = c.type(output["type"])
    ref_ids = {r["selector"]: i for i, r in enumerate(references)}
    events, event_code = {}, []
    for i, e in enumerate(w["event_inputs"]):
        contract = e["contract"]
        def field_type(f, wire):
            t = f["type_ref"]
            if t["kind"] == "reference":
                return "str" if wire else "_Ref" + str(ref_ids[t["selector"]])
            return {"string": "str", "boolean": "bool", "integer": "int | str" if wire else "int", "decimal": "int | float" if wire else "float", "timestamp": "str", "uuid": "str"}[t["name"]]
        def normal(f, v):
            t = f["type_ref"]
            if t["kind"] == "reference":
                return "_Ref" + str(ref_ids[t["selector"]]) + "(_e.text(" + v + "))"
            return "_e." + {"string": "string", "boolean": "boolean", "integer": "integer", "decimal": "decimal", "timestamp": "text", "uuid": "text"}[t["name"]] + "(" + v + ")"
        def shape(name, fields):
            return c.shape(name, [(f["field_id"], field_type(f, True), field_type(f, False), not f["required"]) for f in fields])
        name = "_Event" + str(i)
        fields = sorted(contract["payload"], key=lambda f: f["field_id"])
        occurrence = contract["occurrence_id"]
        oi, on = shape(name + "Occurrence", [occurrence])
        pi, pn = shape(name + "Payload", fields)
        generated = contract["occurred_at_policy"] == "generated"
        event_fields = [("occurrence", oi, on, False)]
        if not generated:
            event_fields.append(("occurredAt", "str", "str", False))
        event_fields.append(("payload", pi, pn, False))
        ei, en = c.shape(name, event_fields)
        capture = "_capture_event" + str(i)
        events[e["name"]] = (ei, en, capture)
        keys, oid = tuple(f[0] for f in event_fields), repr(occurrence["field_id"])
        entries = []
        for f in fields:
            key = repr(f["field_id"])
            entry = key + ": " + normal(f, "p[" + key + "]")
            entries.append(entry if f["required"] else "**({" + entry + "} if " + key + " in p else {})")
        event_code.append(f'''def {capture}(raw) -> {en}:
    d = _e.data(raw, {keys!r}, {keys!r})
    o = _e.data(d["occurrence"], ({oid},), ({oid},))
    p = _e.data(d["payload"], {tuple(f["field_id"] for f in fields)!r}, {tuple(f["field_id"] for f in fields if f["required"])!r})
    return _cast({en}, _MappingProxyType({{"occurrence": _MappingProxyType({{{oid}: {normal(occurrence, 'o[' + oid + ']')}}}), ''' + ('' if generated else '"occurredAt": _e.text(d["occurredAt"]), ') + '"payload": _MappingProxyType({' + ', '.join(entries) + '})}))\n')
    ci, cn = c.shape("_CapturedFields", [(p["name"], t[1], t[2], False) for p, t in zip(inputs, input_types)] + [(name, t[0], t[1], False) for name, t in events.items()])

    def convert(e):
        if e["op"] == "input":
            return {"op": "path", "root": "input:" + e["name"], "properties": e["properties"]}
        if e["op"] == "step-result":
            return {"op": "path", "root": "result:" + e["step_id"], "properties": e["properties"]}
        return {"op": "to_set", "value": convert(e["value"])} if e["op"] == "to_set" else e

    def scope(count, indent):
        params = [{"name": "input:" + p["name"], "type": p["type"]} for p in inputs]
        params += [{"name": "result:" + s["step_id"], "type": s["signature"]["result"]} for s in results[:count]]
        reads = ["input[" + repr(p["name"]) + "]" for p in inputs] + ["r[" + repr(s["step_id"]) + "]" for s in results[:count]]
        prelude = ''.join(' ' * indent + f'p{i} = {v}\n' for i, v in enumerate(reads))
        return prelude, c.expressions(params)

    calls = []
    for i, call in enumerate(results + w["compensations"]):
        comp = i >= len(results)
        count = next(j + 1 for j, s in enumerate(results) if s["step_id"] == call["for_step"]) if comp else i
        prelude, value = scope(count, 8)
        args = [(a["parameter"], *value(convert(a["value"]))) for a in call["arguments"]]
        fields = [(name, *c.type(t), False) for name, t, _ in args]
        fields += [(e["parameter"], *events[e["input"]][:2], False) for e in call["events"]]
        ai, an = c.shape("_Arguments" + str(i), fields)
        entries = [repr(name) + ": " + code for name, _, code in args]
        entries += [repr(e["parameter"]) + ": input[" + repr(e["input"]) + "]" for e in call["events"]]
        calls.append(f'''@_dataclass(frozen=True, slots=True)
class _Call{i}:
    operation_ref: _Literal[{call["operation_ref"]!r}] = {call["operation_ref"]!r}
    action_sha256: _Literal[{call["action_sha256"]!r}] = {call["action_sha256"]!r}
    def arguments(self, input: CapturedInput, results: list[CapturedResult] | tuple[CapturedResult, ...]) -> {an}:
        r = _prefix(input, results, {count}, {len(results) if comp else count})
{prelude}        return _cast({an}, _MappingProxyType({{{', '.join(entries)}}}))
    def operation_input(self, input: CapturedInput, results: list[CapturedResult] | tuple[CapturedResult, ...]) -> {ai}:
        return _cast({ai}, _capture_data(self.arguments(input, results), True, True))
''')
    def carriers(rows, offset, key, name):
        return c.shape(name, [(s[key], repr("_Call" + str(i + offset)), "_Call" + str(i + offset), False) for i, s in enumerate(rows)])[1]
    sn = carriers(results, 0, "step_id", "_Steps")
    cnames = carriers(w["compensations"], len(results), "compensation_id", "_Compensations")
    prelude, expression = scope(len(results), 4)
    _, result_code = expression(convert(output["value"]))
    runtime = base.relative(provider, root + "/runtime")
    source = f'''from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast
from weakref import WeakSet as _WeakSet, WeakKeyDictionary as _WeakKeyDictionary
from math import isfinite as _isfinite
from codecs import lookup as _lookup_codec
from {runtime} import values as _v, facts as _facts
'''
    if events:
        source += f'from {runtime} import event_values as _e\n'
    source += ''.join(f'from {r["module"]} import EventRef as _Ref{i}\n' for i, r in enumerate(references))
    source += '_lookup_codec("utf-16-le")\n_lookup_codec("utf-16-be")\n'
    source += '\n'.join(c.shapes + c.facts + event_code)
    for i, (s, t) in enumerate(zip(results, result_types)):
        source += f'''\n@_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class _Result{i}:
    step_id: _Literal[{s["step_id"]!r}]
    action_sha256: _Literal[{s["action_sha256"]!r}]
    value: {t[2]}
'''
    source += f'''
WorkflowInput = {ci}
WorkflowValue = {output_type}
CapturedInput = {cn}
CapturedResult = {' | '.join('_Result' + str(i) for i in range(len(results)))}
StepId = _Literal[{', '.join(repr(s['step_id']) for s in results)}]
@_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class _Input:
    data: _CapturedFields
    def __getitem__(self, key: str):
        return self.data[key]
_inputs = _WeakSet()
_result_inputs = _WeakKeyDictionary()
''' + CAPTURE
    normalized = [repr(p["name"]) + ': ' + t[0] + '.normalize(d[' + repr(p["name"]) + '])' for p, t in zip(inputs, input_types)]
    normalized += [repr(n) + ': ' + t[2] + '(d[' + repr(n) + '])' for n, t in events.items()]
    source += f'''
def capture(raw: WorkflowInput) -> CapturedInput:
    try:
        d = _capture_data(raw)
        if type(d) is not dict or set(d) != set({tuple(p['name'] for p in inputs) + tuple(events)!r}):
            _fail()
        data = _MappingProxyType({{{', '.join(normalized)}}})
    except (TypeError, ValueError, KeyError):
        raise TypeError("WORKFLOW_VALUE") from None
    input = _Input(_cast(_CapturedFields, data))
    _inputs.add(input)
    return _cast(CapturedInput, input)
'''
    if len(results) > 1:
        source += ''.join(f'@_overload\ndef capture_result(input: CapturedInput, step_id: _Literal[{s["step_id"]!r}], raw: object) -> _Result{i}: ...\n' for i, s in enumerate(results))
    source += '''def capture_result(input: CapturedInput, step_id: StepId, raw: object) -> CapturedResult:
    _assert_input(input)
    if type(step_id) is not str:
        _fail()
    try:
        data = _capture_data(raw, True)
'''
    for i, (s, t) in enumerate(zip(results, result_types)):
        source += f'''        if step_id == {s["step_id"]!r}:
            row = _Result{i}({s["step_id"]!r}, {s["action_sha256"]!r}, {t[0]}.normalize(data))
            _result_inputs[row] = input
            return row
'''
    source += f'''    except (TypeError, ValueError, KeyError):
        raise TypeError("WORKFLOW_VALUE") from None
    return _fail()
def _prefix(input, results, minimum, maximum):
    _assert_input(input)
    if (type(results) is not list and type(results) is not tuple) or not minimum <= len(results) <= maximum:
        _fail()
    ids = {tuple(s['step_id'] for s in results)!r}
    classes = {base.tuple_code(['_Result' + str(i) for i in range(len(results))])}
    r = {{}}
    for i, row in enumerate(results):
        if type(row) is not classes[i] or _result_inputs.get(row) is not input or row.step_id != ids[i]:
            _fail()
        r[row.step_id] = row.value
    return r
''' + '\n'.join(calls)
    step_entries = ', '.join(repr(s['step_id']) + ': _Call' + str(i) + '()' for i, s in enumerate(results))
    comp_entries = ', '.join(repr(s['compensation_id']) + ': _Call' + str(i + len(results)) + '()' for i, s in enumerate(w['compensations']))
    source += f'''
steps = _cast({sn}, _MappingProxyType({{{step_entries}}}))
compensations = _cast({cnames}, _MappingProxyType({{{comp_entries}}}))
def result(input: CapturedInput, results: list[CapturedResult] | tuple[CapturedResult, ...]) -> {output_type}:
    r = _prefix(input, results, {len(results)}, {len(results)})
{prelude}    return {output_protocol}.normalize({result_code})
descriptor = {freeze(descriptor)}
__all__ = ["WorkflowInput", "WorkflowValue", "CapturedInput", "CapturedResult", "StepId", "capture", "capture_result", "steps", "compensations", "result", "descriptor"]
'''
    return source


def observe(data):
    p, w = data['plan'], data['workflow']
    root, provider = p['module_root'], p['relative_path']
    feature, node = w['bindings']['selector'].split(':')
    require(provider == root + '/features/' + feature.replace('-', '_') + '/src/application/workflows/_material/' + node.replace('-', '_') + '.py', 'provider path')
    selectors = sorted({f['type_ref']['selector'] for e in w['event_inputs'] for f in [e['contract']['occurrence_id'], *e['contract']['payload']] if f['type_ref']['kind'] == 'reference'})
    references = []
    sources = {}
    for selector in selectors:
        feature, node = selector.split(':')
        path = root + '/runtime/event_references/' + feature.replace('-', '_') + '/' + node.replace('-', '_') + '.py'
        references.append({'selector': selector, 'module': base.relative(provider, path[:-3])})
        sources[path] = 'from typing import NewType as _NewType\nEventRef = _NewType(' + repr(selector) + ', str)\n'
    descriptor = dict(schema_version='domainspec.python-workflow-materialization-descriptor/v1-candidate', workflow_sha256=w['workflow_sha256'], field_compilation_sha256=w['field_compilation_sha256'], contract_sha256='88d7a46aa61a28b371de4e468163a2c36c1da1d8ca83c14c77584fb2061a54a4', selector=w['bindings']['selector'], steps=[{k: s[k] for k in ('step_id', 'operation_ref', 'action_sha256')} for s in w['steps']], compensations=[{k: s[k] for k in ('compensation_id', 'for_step', 'operation_ref', 'action_sha256')} for s in w['compensations']], effect_contract='pure-typed-materialization', invariant_execution='not-performed', commit_evidence='not-established', event_construction='not-performed', authority_effect='none')
    require(p['descriptor'] == descriptor, 'descriptor meaning')
    sources[provider] = expected(w, data['model'], provider, root, references, descriptor)
    support = dict(base.SUPPORT)
    if w['event_inputs']:
        support['event_values.py'] = '607cfb79ac50f4929834afbfd206174d912122541534755688aa703e1d53a4b0'
    paths = set(sources) | {root + '/runtime/' + name for name in support}
    for path in list(paths):
        parts = path.split('/')
        for i in range(1, len(parts)):
            paths.add('/'.join(parts[:i]) + '/__init__.py')
    actual = {a['relative_path']: a for a in p['artifacts']}
    require(len(actual) == len(p['artifacts']) and set(actual) == paths, 'artifact closure')
    for path in sorted(paths):
        content = (pathlib.Path(data['root']) / path).read_bytes()
        if path in sources:
            try:
                base.equivalent(content, sources[path], path)
            except ValueError as error:
                raise ValueError('PYTHON_WORKFLOW_MATERIALIZATION_OBSERVER:AST:' + str(error)) from None
        elif path.endswith('/__init__.py'):
            require(not content, 'nonempty package initializer:' + path)
        else:
            require(hashlib.sha256(content).hexdigest() == support[path.split('/')[-1]], 'support bytes:' + path)
        require(content == actual[path]['content'].encode('utf8'), 'disk/artifact disagreement:' + path)
        require(hashlib.sha256(content).hexdigest() == actual[path]['sha256'], 'artifact digest:' + path)
        require(len(content) == actual[path]['size_bytes'], 'artifact size:' + path)
    return {'whole_source': True, 'modules': len(paths)}


if __name__ == '__main__':
    print(json.dumps(observe(json.load(sys.stdin))))
