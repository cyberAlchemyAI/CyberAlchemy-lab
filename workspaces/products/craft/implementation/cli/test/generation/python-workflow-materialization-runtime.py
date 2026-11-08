"""Independent native occurrence/value oracle; never imports a TypeScript renderer."""
import copy
import asyncio
import dataclasses
import gc
import importlib
import json
import sys
import typing
import weakref
from types import MappingProxyType

data = json.load(sys.stdin)
sys.path.insert(0, data["root"])
m = importlib.import_module(data["plan"]["import_name"])
w = data["workflow"]
declarations = {d["selector"]: d for d in (data["model"] or {}).get("declarations", [])}


def thaw(v):
    if dataclasses.is_dataclass(v):
        assert v.__dataclass_params__.frozen and not hasattr(v, "__dict__"), "MUTABLE_CARRIER"
        if hasattr(v, "entries"):
            return {k: thaw(value) for k, value in v.entries}
        if hasattr(v, "data"):
            return thaw(v.data)
        return {f.name: thaw(getattr(v, f.name)) for f in dataclasses.fields(v)}
    if type(v) in (dict, MappingProxyType):
        return {k: thaw(value) for k, value in v.items()}
    if type(v) in (tuple, list):
        return [thaw(value) for value in v]
    return v


def part(v):
    return str(len(v.encode("utf-16-le", "surrogatepass")) // 2) + ":" + v


def key(t, value):
    kind = t["kind"]
    if kind == "scalar":
        return part(t["name"]) + part(("1" if value else "0") if t["name"] == "Bool" else str(value))
    if kind == "named":
        d = declarations[t["selector"]]
        if d["kind"] == "Enum":
            return part(d["selector"]) + key({"kind": "sum", "variants": d["contract"]["variants"]}, value)
        fields = sorted(d["contract"]["properties"], key=lambda p: p["name"])
        fields = [p for p in fields if p["identity"]] if d["kind"] == "Entity" else fields
        return part(d["kind"]) + part(d["selector"]) + "".join(part(p["name"]) + part(key(p["type"], value[p["name"]])) for p in fields)
    if kind == "optional":
        return part("absent") if value is None else part("present") + part(key(t["element"], value))
    if kind in ("list", "set"):
        return part(kind) + part(str(len(value))) + "".join(part(key(t["element"], v)) for v in value)
    case = next(c for c in t["variants"] if c["name"] == value["variant"])
    return part("sum") + part(case["name"]) + (part("no-payload") if case["payload"] is None else part(key(case["payload"], value["payload"])))


def unique(t, values):
    keyed = {}
    for v in values:
        keyed.setdefault(key(t, v), v)
    return [keyed[k] for k in sorted(keyed, key=lambda k: k.encode("utf-16-be", "surrogatepass"))]


def normalize(t, v):
    kind = t["kind"]
    if kind == "scalar":
        if t["name"] == "UInt64":
            return int(v)
        return v.encode("utf-16-le", "surrogatepass").decode("utf-16-le", "surrogatepass") if t["name"] == "String" else v
    if kind == "named":
        d = declarations[t["selector"]]
        if d["kind"] == "Enum":
            return normalize({"kind": "sum", "variants": d["contract"]["variants"]}, v)
        return {p["name"]: normalize(p["type"], v.get(p["name"])) for p in d["contract"]["properties"]}
    if kind == "optional":
        return None if v is None else normalize(t["element"], v)
    if kind in ("list", "set"):
        result = [normalize(t["element"], item) for item in v]
        return unique(t["element"], result) if kind == "set" else result
    case = next(c for c in t["variants"] if c["name"] == v["variant"])
    return {"variant": case["name"], **({"payload": normalize(case["payload"], v["payload"])} if case["payload"] is not None else {})}


def expression(e, captured, returned):
    if e["op"] == "literal":
        t = {"kind": "scalar", "name": e["type"]}
        return t, normalize(t, e["value"])
    if e["op"] == "variant":
        for d in declarations.values():
            if d["kind"] == "Enum":
                for v in d["contract"]["variants"]:
                    if v["ontology_variant"] == e["selector"]:
                        return {"kind": "named", "selector": d["selector"]}, {"variant": v["name"]}
        raise AssertionError("unknown variant")
    if e["op"] == "to_set":
        t, value = expression(e["value"], captured, returned)
        return {"kind": "set", "element": t["element"]}, unique(t["element"], value)
    if e["op"] == "input":
        t = next(p["type"] for p in w["bindings"]["inputs"] if p["name"] == e["name"])
        value = captured[e["name"]]
    else:
        assert e["op"] == "step-result"
        t = next(s["signature"]["result"] for s in w["steps"] if s["step_id"] == e["step_id"])
        value = returned[e["step_id"]]
    for prop in e["properties"]:
        collection = t["kind"] in ("list", "set")
        owner = t["element"] if collection else t
        field = next(p for p in declarations[owner["selector"]]["contract"]["properties"] if p["ontology_property"] == prop)
        if collection:
            value = [v[field["name"]] for v in value]
            if t["kind"] == "set":
                value = unique(field["type"], value)
            t = {"kind": t["kind"], "element": field["type"]}
        else:
            t, value = field["type"], value[field["name"]]
    return t, value


def rejects(call):
    try:
        call()
    except TypeError as e:
        assert str(e) == "WORKFLOW_VALUE", str(e)
    except Exception as e:
        raise AssertionError("INCORRECT_BOUNDARY_REJECTION") from e
    else:
        raise AssertionError("MISSING_BOUNDARY_REJECTION")


raw = copy.deepcopy(data["parameters"])
snapshot = copy.deepcopy(raw)
observed = []
armed = True


def audit(event, args):
    if armed and (event in ("open", "import", "exec", "compile") or event.startswith(("os.", "socket.", "subprocess.", "ctypes."))):
        observed.append(event)


sys.addaudithook(audit)
cap = m.capture(raw)
rows = [m.capture_result(cap, step["step_id"], value) for step, value in zip(w["steps"], data["returns"])]
expected = {p["name"]: normalize(p["type"], raw[p["name"]]) for p in w["bindings"]["inputs"]}
for e in w["event_inputs"]:
    value = copy.deepcopy(raw[e["name"]])
    for field in e["contract"]["payload"]:
        if field["field_id"] in value["payload"] and field["type_ref"] == {"kind": "primitive", "name": "integer"}:
            value["payload"][field["field_id"]] = int(value["payload"][field["field_id"]])
    expected[e["name"]] = value
assert thaw(cap) == expected
returned = {s["step_id"]: normalize(s["signature"]["result"], v) for s, v in zip(w["steps"], data["returns"])}
for group, calls in ((m.steps, w["steps"]), (m.compensations, w["compensations"])):
    for i, call in enumerate(calls):
        compensation = "compensation_id" in call
        name = call["compensation_id"] if compensation else call["step_id"]
        count = next(j for j, s in enumerate(w["steps"]) if s["step_id"] == call["for_step"]) + 1 if compensation else i
        current = group[name]
        assert current.operation_ref == call["operation_ref"] and current.action_sha256 == call["action_sha256"]
        args = current.arguments(cap, rows[:count])
        wanted = {a["parameter"]: expression(a["value"], expected, returned)[1] for a in call["arguments"]}
        wanted.update({e["parameter"]: expected[e["input"]] for e in call["events"]})
        assert type(args) is MappingProxyType and thaw(args) == wanted, ("ARGUMENT_BINDING", name)
        wire = current.operation_input(cap, rows[:count])
        assert type(wire) is dict and thaw(wire) == wanted
        wire.clear()
        assert thaw(current.arguments(cap, rows[:count])) == wanted
        if compensation:
            assert thaw(current.arguments(cap, rows)) == wanted
        else:
            if count:
                rejects(lambda: current.arguments(cap, rows[:count - 1]))
            rejects(lambda: current.arguments(cap, rows[:count + 1]))
assert thaw(m.result(cap, rows)) == normalize(w["bindings"]["result"]["type"], expression(w["bindings"]["result"]["value"], expected, returned)[1]), "RESULT_BINDING"
assert raw == snapshot and not observed, observed
armed = False
assert thaw(m.descriptor) == data["plan"]["descriptor"]

# Same-shape returned native facts from an Operation cross the explicit copy
# adapter, not a new business factory or a widened Operation input contract.
for s, row in zip(w["steps"], rows):
    assert thaw(m.capture_result(cap, s["step_id"], row.value).value) == thaw(row.value)

other = m.capture(snapshot)
for index, s in enumerate(w["steps"]):
    if index:
        bad = [m.capture_result(other, w["steps"][j]["step_id"], data["returns"][j]) for j in range(index)]
        rejects(lambda: m.steps[s["step_id"]].arguments(cap, bad))
        clones = [copy.copy(row) for row in rows[:index]]
        rejects(lambda: m.steps[s["step_id"]].arguments(cap, clones))
        rejects(lambda: m.steps[s["step_id"]].arguments(cap, [rows[index]] * index))
if len(rows) > 1:
    rejects(lambda: m.result(cap, list(reversed(rows))))
rejects(lambda: m.result(cap, rows[:-1]))
rejects(lambda: m.capture_result(cap, "unknown-step", {}))
rejects(lambda: m.steps[w["steps"][0]["step_id"]].arguments(copy.copy(cap), []))


active_type_comparisons = []


class ActiveMeta(type):
    def __eq__(cls, other):
        active_type_comparisons.append("equality")
        return False


class ActiveType(metaclass=ActiveMeta):
    pass


rejects(lambda: m.capture(ActiveType()))
rejects(lambda: m.capture_result(cap, w["steps"][0]["step_id"], ActiveType()))
rejects(lambda: m.result(cap, ActiveType()))
assert not active_type_comparisons, "ACTIVE_METACLASS_EXECUTED"


class Active(dict):
    def __getitem__(self, key):
        raise AssertionError("ACTIVE_INPUT_EXECUTED")


class ActiveList(list):
    def __iter__(self):
        raise AssertionError("ACTIVE_RESULT_EXECUTED")


rejects(lambda: m.capture(Active(snapshot)))
rejects(lambda: m.capture_result(cap, w["steps"][0]["step_id"], MappingProxyType(Active({}))))
rejects(lambda: m.result(cap, ActiveList(rows)))
rejects(lambda: m.capture(dict(snapshot, extra=True)))
cycle = {}; cycle["cycle"] = cycle
rejects(lambda: m.capture(cycle))
for p in w["bindings"]["inputs"]:
    missing = copy.deepcopy(snapshot); del missing[p["name"]]
    rejects(lambda: m.capture(missing))
    if p["type"] == {"kind": "scalar", "name": "UInt64"}:
        for bad in [True, -1, 1.5, "01", "18446744073709551616"]:
            rejects(lambda: m.capture(dict(snapshot, **{p["name"]: bad})))
    if p["type"]["kind"] == "named":
        changed = copy.deepcopy(snapshot)
        changed[p["name"]] = Active(changed[p["name"]])
        rejects(lambda: m.capture(changed))
for e in w["event_inputs"]:
    name, c = e["name"], e["contract"]
    bad = copy.deepcopy(snapshot)
    if c["occurred_at_policy"] == "required":
        del bad[name]["occurredAt"]
    else:
        bad[name]["occurredAt"] = "unexpected"
    rejects(lambda: m.capture(bad))
    integer_fields = [f for f in c["payload"] if f["type_ref"] == {"kind": "primitive", "name": "integer"}]
    for field in integer_fields:
        if not field["required"]:
            absent = copy.deepcopy(snapshot); absent[name]["payload"].pop(field["field_id"], None)
            assert field["field_id"] not in m.capture(absent)[name]["payload"]
        for bad_value in [None, True, "9223372036854775808", "-9223372036854775809"]:
            bad = copy.deepcopy(snapshot); bad[name]["payload"][field["field_id"]] = bad_value
            rejects(lambda: m.capture(bad))
        for good in ["-9223372036854775808", "9223372036854775807"]:
            valid = copy.deepcopy(snapshot); valid[name]["payload"][field["field_id"]] = good
            assert m.capture(valid)[name]["payload"][field["field_id"]] == int(good)

raw.clear()
assert thaw(cap) == expected
for value in [cap, *rows, *m.steps.values(), *m.compensations.values()]:
    try:
        value.extra = 1
    except (AttributeError, TypeError):
        pass
    else:
        raise AssertionError("MUTABLE_CARRIER")
assert set(typing.get_type_hints(m.WorkflowInput)) == set(snapshot)
for s in w["steps"]:
    call = m.steps[s["step_id"]]
    wire_type = typing.get_type_hints(type(call).operation_input)["return"]
    assert set(typing.get_type_hints(wire_type)) == {a["parameter"] for a in s["arguments"]} | {e["parameter"] for e in s["events"]}

def transient():
    cap = m.capture(snapshot)
    row = m.capture_result(cap, w["steps"][0]["step_id"], data["returns"][0])
    return weakref.ref(cap), weakref.ref(row)

first, second = transient()
gc.collect()
assert first() is None and second() is None, "OWNERSHIP_REGISTRY_LEAK"

operation_calls = 0
if data.get("operations"):
    imports = {entry["selector"]: (importlib.import_module(entry["relative_path"][:-3].replace("/", ".")), entry) for entry in data["operations"]}
    commits = []
    class Transaction:
        async def read(self, request):
            raise AssertionError("undeclared read")
        async def commit(self, batch):
            commits.append(batch)
            await asyncio.sleep(0)
            return {"status": "committed"}
        async def rollback(self):
            raise AssertionError("unexpected rollback")
    class Store:
        async def begin(self):
            await asyncio.sleep(0)
            return Transaction()
    async def integrated():
        input = m.capture(snapshot)
        completed = []
        for step in w["steps"]:
            module, entry = imports[step["operation_ref"]]
            call = m.steps[step["step_id"]]
            args = call.operation_input(input, completed)
            outcome = await getattr(module, entry["callable"])(args, {"store": Store()})
            assert outcome.status == "committed", thaw(outcome)
            completed.append(m.capture_result(input, step["step_id"], outcome.value))
        assert thaw(m.result(input, completed)) == snapshot["order"]
        return len(completed)
    operation_calls = asyncio.run(integrated())
    assert len(commits) == len(w["steps"])
    assert [batch.events[0]["value"].occurrence["event-id"] for batch in commits] == [snapshot[next(e["input"] for e in s["events"] if e["parameter"] == "notice_input")]["occurrence"]["event-id"] for s in w["steps"]]
    for reference in data["plan"]["references"]:
        shared = importlib.import_module(reference["relative_path"][:-3].replace("/", ".")).EventRef
        assert shared.__name__ == reference["selector"]
        assert any(value is shared for name, value in vars(m).items() if name.startswith("_Ref"))
print(json.dumps({"steps": len(w["steps"]), "compensations": len(w["compensations"]), "effects": observed, "operation_calls": operation_calls}))
