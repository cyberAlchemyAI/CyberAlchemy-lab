"""Native State Machine oracle derived from source, including complete pair replay."""
import copy
import dataclasses
import enum
import importlib
import inspect
import json
import sys
import typing
from types import MappingProxyType

data = json.load(sys.stdin)
sys.path.insert(0, data["root"])
declarations = {d["selector"]: d for d in (data["model"] or {}).get("declarations", [])}


def sample(t, amount):
    kind = t["kind"]
    if kind == "scalar":
        return {"String": "source-id", "UInt64": amount, "Bool": False}[t["name"]]
    if kind == "named":
        d = declarations[t["selector"]]
        if d["kind"] == "Enum":
            return sample({"kind": "sum", "variants": d["contract"]["variants"]}, amount)
        return {p["name"]: sample(p["type"], amount) for p in d["contract"]["properties"]}
    if kind == "optional":
        return None
    if kind in ("list", "set"):
        return [sample(t["element"], amount)]
    case = t["variants"][0]
    return {"variant": case["name"], **({"payload": sample(case["payload"], amount)} if case["payload"] else {})}


def normalize(t, v):
    kind = t["kind"]
    if kind == "scalar":
        return int(v) if t["name"] == "UInt64" else v
    if kind == "named":
        d = declarations[t["selector"]]
        if d["kind"] == "Enum":
            return normalize({"kind": "sum", "variants": d["contract"]["variants"]}, v)
        return {p["name"]: normalize(p["type"], v[p["name"]]) for p in d["contract"]["properties"]}
    if kind == "optional":
        return None if v is None else normalize(t["element"], v)
    if kind in ("list", "set"):
        return [normalize(t["element"], item) for item in v]
    case = next(c for c in t["variants"] if c["name"] == v["variant"])
    return {"variant": case["name"], **({"payload": normalize(case["payload"], v["payload"])} if case["payload"] else {})}


def value(e, parameters, scope):
    if e["op"] == "literal":
        return int(e["value"]) if e["type"] == "UInt64" else e["value"]
    assert e["op"] == "path", "UNSUPPORTED_ORACLE_EXPRESSION"
    t, v = next(p["type"] for p in parameters if p["name"] == e["root"]), scope[e["root"]]
    for property in e["properties"]:
        f = next(f for f in declarations[t["selector"]]["contract"]["properties"] if f["ontology_property"] == property)
        t, v = f["type"], v[f["name"]]
    return v


def rule(selector, scope):
    c = data["nodes"][selector]["body"]["typed_contract"]
    def evaluate(e):
        if e["op"] == "rule_ref":
            return rule(e["selector"], {a["parameter"]: value(a["value"], c["parameters"], scope) for a in e["arguments"]})
        if e["op"] in ("all", "any"):
            return (all if e["op"] == "all" else any)(evaluate(x) for x in e["terms"])
        if e["op"] == "not":
            return not evaluate(e["term"])
        left, right = value(e["left"], c["parameters"], scope), value(e["right"], c["parameters"], scope)
        if e["op"] == "lt":
            return left < right
        assert e["op"] == "eq", "UNSUPPORTED_ORACLE_PREDICATE"
        return left == right
    return evaluate(c["expression"])


def thaw(v):
    if isinstance(v, enum.Enum):
        return v.value
    if dataclasses.is_dataclass(v):
        assert v.__dataclass_params__.frozen and not hasattr(v, "__dict__"), "MUTABLE_RESULT"
        return {f.name: thaw(getattr(v, f.name)) for f in dataclasses.fields(v)}
    if type(v) is tuple:
        return [thaw(x) for x in v]
    if type(v) is MappingProxyType:
        return {k: thaw(x) for k, x in v.items()}
    assert type(v) in (str, bool, int, type(None)), ("MUTABLE_OR_ACTIVE_VALUE", type(v))
    return v


def reject(call):
    try:
        call()
    except TypeError as e:
        assert str(e) == "STATE_MACHINE_INPUT", str(e)
    else:
        raise AssertionError("MISSING_INPUT_REJECTION")


calls = 0
for m in data["modules"]:
    module = importlib.import_module(m["import_name"])
    reduce = getattr(module, m["callable"])
    State, Trigger = module.State, module.Trigger
    c = data["contracts"][m["selector"]]
    for spoof in (False, True):
        effects = []
        class ActiveMeta(type):
            def __eq__(cls, other):
                effects.append("metaclass equality")
                return spoof
        class Hostile(metaclass=ActiveMeta):
            pass
        reject(lambda: reduce(module.initial_state, next(iter(Trigger)), {"undeclared": Hostile()}))
        assert not effects, "ACTIVE_METACLASS_EXECUTED"
    assert issubclass(State, enum.Enum) and issubclass(Trigger, enum.Enum) and State is not Trigger
    assert [s.value for s in State] == sorted(c["states"])
    assert [t.value for t in Trigger] == sorted(set(t["trigger_event_ref"] for t in c["transitions"]))
    assert module.initial_state is State(c["initial"])
    assert list(inspect.signature(reduce).parameters) == ["state", "trigger", "parameters"]
    assert not inspect.iscoroutinefunction(type(reduce).__call__)
    assert thaw(reduce.descriptor) == m["descriptor"]
    assert set(typing.get_type_hints(module.Parameters)) == set(p["name"] for p in c["inputs"])
    outcomes = typing.get_args(module.Outcome)
    assert len(outcomes) == len(c["transitions"]) + 1
    for outcome, transition in zip(outcomes, c["transitions"]):
        hints = typing.get_type_hints(outcome)
        assert typing.get_args(hints["state"]) == (State(transition["target_state"]),)
        assert typing.get_args(hints["transition_id"]) == (transition["transition_id"],)
        assert len(typing.get_args(hints["output_intents"])) == len(transition["output_intents"])

    for state in State:
        for trigger in Trigger:
            for amount in [0, 9, 10, 9007199254740993, "18446744073709551615"]:
                original = {p["name"]: sample(p["type"], amount) for p in c["inputs"]}
                before = copy.deepcopy(original)
                normalized = {p["name"]: normalize(p["type"], original[p["name"]]) for p in c["inputs"]}
                transition = next((t for t in c["transitions"] if t["source_state"] == state.value and t["trigger_event_ref"] == trigger.value), None)
                accepted = transition is not None
                if transition and transition["guard"]:
                    g = transition["guard"]
                    accepted = rule(g["selector"], {a["parameter"]: value(a["value"], c["inputs"], normalized) for a in g["arguments"]})
                expected = dict(status="transitioned", state=transition["target_state"], transition_id=transition["transition_id"], output_intents=transition["output_intents"]) if accepted else dict(status="rejected", state=state.value, reason="guard" if transition else "no-transition", output_intents=[])
                observed, armed = [], True
                def audit(event, args):
                    if armed and (event in ("open", "import", "exec", "compile") or event.startswith(("os.", "socket.", "subprocess.", "ctypes."))):
                        observed.append(event)
                # One hook per module is enough; register only for first call.
                if calls == 0:
                    sys.addaudithook(audit)
                result = reduce(state, trigger, original)
                assert thaw(result) == expected
                assert thaw(reduce(state, trigger, original)) == expected
                armed = False
                assert not observed, observed
                assert original == before
                calls += 1
                try:
                    result.state = state
                except (AttributeError, TypeError):
                    pass
                else:
                    raise AssertionError("MUTABLE_RESULT")
                if result.output_intents:
                    try:
                        result.output_intents[0]["slot"] = "changed"
                    except TypeError:
                        pass
                    else:
                        raise AssertionError("MUTABLE_INTENT")

    params = {p["name"]: sample(p["type"], 10) for p in c["inputs"]}
    first_state, first_trigger = next(iter(State)), next(iter(Trigger))
    for invalid in [True, 0, None, first_state.value, first_trigger]:
        reject(lambda: reduce(invalid, first_trigger, params))
    for invalid in [True, 0, None, first_trigger.value, first_state]:
        reject(lambda: reduce(first_state, invalid, params))
    class Active(dict):
        def __getitem__(self, k):
            raise AssertionError("ACTIVE_INPUT")
    for invalid in [None, [], Active(params), dict(params, extra=True)]:
        reject(lambda: reduce(first_state, first_trigger, invalid))
    cycle = {}; cycle["cycle"] = cycle
    reject(lambda: reduce(first_state, first_trigger, cycle))
    if c["inputs"]:
        for amount in [True, -1, 1.0, "01", "18446744073709551616", " 1", "١"]:
            malformed = {p["name"]: sample(p["type"], amount) for p in c["inputs"]}
            reject(lambda: reduce(first_state, first_trigger, malformed))
    for p in c["inputs"]:
        if p["type"] == {"kind": "scalar", "name": "Bool"}:
            reject(lambda: reduce(first_state, first_trigger, dict(params, **{p["name"]: 0})))
    try:
        reduce.extra = True
    except (TypeError, AttributeError):
        pass
    else:
        raise AssertionError("MUTABLE_CALLABLE")

print(json.dumps({"native": len(data["modules"]), "cases": calls}))
