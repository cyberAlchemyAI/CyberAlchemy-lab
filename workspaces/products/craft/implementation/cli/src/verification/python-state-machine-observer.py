"""Independent whole-source Python State Machine observation; no target execution."""
import ast
import hashlib
import json
import pathlib

# The pinned independent checked-type observer is injected as helper.


def require(ok, why):
    if not ok:
        raise ValueError("PYTHON_STATE_MACHINE_OBSERVER:" + why)


def member(s):
    return s.replace("-", "_").upper()


def trigger(s):
    return "__".join(member(p) for p in s.split(":"))


DATA_SUPPORT = '''def _check_data(root):
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
'''


def observe(data, m, overrides=None):
    def read(path):
        return overrides[path] if overrides and path in overrides else (pathlib.Path(data['root']) / path).read_bytes()
    root, c, d = pathlib.Path(data["root"]), data["contracts"][m["selector"]], m["descriptor"]
    require(d["contract"] == c and d["protocol_id"] == "python.bound-state-machine/v1", "source/profile binding")
    require(d["field_model_sha256"] == (data["model"]["model_sha256"] if data["model"] else None), "field model binding")
    require(d["effect_contract"] == "none" and d["trigger_semantics"] == "explicit-event-input-symbol" and d["output_semantics"] == "ordered-unexecuted-intents", "symbol/effect boundaries")
    events = sorted(set(t["trigger_event_ref"] for t in c["transitions"]) | set(o["event_ref"] for t in c["transitions"] for o in t["output_intents"]))
    require([e["selector"] for e in d["event_dependencies"]] == events, "Event selection")
    for event in d["event_dependencies"]:
        node = data["nodes"][event["selector"]]
        require(node["kind"] == "Event" and event["kind"] == "Event", "Event identity")
        content = json.dumps(node["body"], sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        content = "".join("\\u%04x" % ord(ch) if 0xD800 <= ord(ch) <= 0xDFFF else ch for ch in content).encode()
        require(hashlib.sha256(content).hexdigest() == event["body_sha256"], "Event body binding")
    provider = read(m["provider_path"])
    require(hashlib.sha256(provider).hexdigest() == d["provider"]["sha256"], "provider digest")
    ctx = helper.Context(data["model"], m["provider_path"], data["module_root"])
    inputs = [(ctx.protocol(p["type"]), *ctx.type(p["type"])) for p in c["inputs"]]
    value = ctx.expressions(c["inputs"])
    guards = sorted(set(t["guard"]["selector"] for t in c["transitions"] if t["guard"]))
    imports = []
    for i, selector in enumerate(guards):
        r = next(r for r in data["rule_modules"] if r["selector"] == selector)
        imports.append({"selector": selector, "module": helper.relative(m["provider_path"], r["relative_path"][:-3]), "symbol": r["callable"], "local": "_condition" + str(i)})
    require(imports == m["imports"], "only declared Rule imports")
    results = ""
    for i, t in enumerate(c["transitions"]):
        intents = []
        for j, row in enumerate(t["output_intents"]):
            fields = [(n, "_Literal[" + repr(row[n]) + "]", "_Literal[" + repr(row[n]) + "]", False) for n in ("slot", "event_ref")]
            intents.append(ctx.shape("_Intent" + str(i) + "_" + str(j), fields)[1])
        results += "@_dataclass(frozen=True, slots=True)\nclass _Transition" + str(i) + ":\n    status: _Literal['transitioned']\n    state: _Literal[State." + member(t["target_state"]) + "]\n    transition_id: _Literal[" + repr(t["transition_id"]) + "]\n    output_intents: tuple[" + (", ".join(intents) if intents else "()") + "]\n"
    branches = ""
    for i, t in enumerate(c["transitions"]):
        branches += "    if state is State." + member(t["source_state"]) + " and trigger is Trigger." + trigger(t["trigger_event_ref"]) + ":\n"
        if t["guard"]:
            g = t["guard"]
            dependency = next(r for r in imports if r["selector"] == g["selector"])
            args = ", ".join(repr(a["parameter"]) + ": " + value(a["value"])[1] for a in sorted(g["arguments"], key=lambda a: a["parameter"]))
            branches += "        if not " + dependency["local"] + "({" + args + "}):\n            return _Rejected('rejected', state, 'guard', ())\n"
        intents = ["_MappingProxyType({'slot': " + repr(o["slot"]) + ", 'event_ref': " + repr(o["event_ref"]) + "})" for o in t["output_intents"]]
        branches += "        return _Transition" + str(i) + "('transitioned', State." + member(t["target_state"]) + ", " + repr(t["transition_id"]) + ", " + helper.tuple_code(intents) + ")\n"
    runtime = helper.relative(m["provider_path"], data["module_root"] + "/runtime")
    expected = '''from __future__ import annotations
import enum as _enum
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload
from math import isfinite as _isfinite
from codecs import lookup as _lookup_codec
from RUNTIME import values as _v, facts as _facts
_lookup_codec("utf-16-le")
_lookup_codec("utf-16-be")
'''.replace("RUNTIME", runtime)
    expected += "".join("from " + r["module"] + " import " + r["symbol"] + " as " + r["local"] + "\n" for r in imports)
    expected += "@_enum.unique\nclass State(_enum.Enum):\n" + "".join("    " + member(s) + " = " + repr(s) + "\n" for s in sorted(c["states"]))
    expected += "@_enum.unique\nclass Trigger(_enum.Enum):\n" + "".join("    " + trigger(s) + " = " + repr(s) + "\n" for s in sorted(set(t["trigger_event_ref"] for t in c["transitions"])))
    expected += "".join(ctx.shapes + ctx.facts) + results
    expected += '''@_dataclass(frozen=True, slots=True)
class _Rejected:
    status: _Literal["rejected"]
    state: State
    reason: _Literal["guard", "no-transition"]
    output_intents: tuple[()]
'''
    expected += 'Parameters = _TypedDict("Parameters", {' + ", ".join(repr(p["name"]) + ": " + inputs[i][1] for i, p in enumerate(c["inputs"])) + "})\n"
    expected += "Outcome = " + " | ".join(["_Transition" + str(i) for i in range(len(c["transitions"]))] + ["_Rejected"]) + "\ninitial_state: State = State." + member(c["initial"]) + "\n" + DATA_SUPPORT
    expected += '''def reduce(state: State, trigger: Trigger, parameters: Parameters) -> Outcome:
    if type(state) is not State or not any(state is member for member in State) or type(trigger) is not Trigger or not any(trigger is member for member in Trigger):
        raise TypeError("STATE_MACHINE_INPUT")
    try:
        _check_data(parameters)
        if type(parameters) is not dict or set(parameters) != set(INPUT_FIELDS):
            raise TypeError("STATE_MACHINE_INPUT")
'''.replace("INPUT_FIELDS", repr(tuple(p["name"] for p in c["inputs"])))
    expected += "".join("        p" + str(i) + " = " + inputs[i][0] + ".normalize(parameters[" + repr(p["name"]) + "])\n" for i, p in enumerate(c["inputs"]))
    expected += '''    except (TypeError, ValueError, KeyError):
        raise TypeError("STATE_MACHINE_INPUT") from None
''' + branches + '    return _Rejected("rejected", state, "no-transition", ())\n'
    helper.equivalent(provider, expected, "State Machine semantics/types/effects")
    wrapper = ast.parse(read(m["relative_path"]))
    require(len(wrapper.body) == 8 and isinstance(wrapper.body[4], ast.Assign) and helper.frozen(wrapper.body[4].value) == d, "descriptor binding")
    wrapper.body[4].value = ast.Constant(None)
    expected = '''from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from PROVIDER import reduce as _reduce, initial_state, State, Trigger, Parameters, Outcome
_DESCRIPTOR = None
@_dataclass(frozen=True, slots=True)
class _BoundStateMachine:
    @property
    def descriptor(self): return _DESCRIPTOR
    def __call__(self, state: State, trigger: Trigger, parameters: Parameters) -> Outcome:
        return _reduce(state, trigger, parameters)
CALLABLE = _BoundStateMachine()
__all__ = ["CALLABLE", "initial_state", "State", "Trigger", "Parameters", "Outcome"]
'''.replace("PROVIDER", helper.relative(m["relative_path"], m["provider_path"][:-3])).replace("CALLABLE", m["callable"])
    require(helper.dump(wrapper) == helper.dump(ast.parse(expected)), "frozen wrapper/exports")
