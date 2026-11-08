"""Native generated Workflow/Operation execution versus precomputed DomainSpec R01/R02 evidence."""
import asyncio
import copy
import dataclasses
import importlib
import inspect
import json
import sys
import typing
from types import MappingProxyType

data = json.load(sys.stdin)
sys.path.insert(0, data["root"])
entry = data["plan"]["modules"][0]
module = importlib.import_module(entry["import_name"])
provider = importlib.import_module(entry["provider_path"][:-3].replace("/", "."))
material = importlib.import_module(entry["material_path"][:-3].replace("/", "."))
run = getattr(module, entry["callable"])
operations = {m["selector"]: importlib.import_module(m["import_name"]) for m in data["plan"]["operation_plan"]["modules"]}
workflow = data["workflow"]


def thaw(v):
    if dataclasses.is_dataclass(v):
        assert v.__dataclass_params__.frozen and not hasattr(v, "__dict__"), "MUTABLE_OUTCOME"
        if hasattr(v, "entries"):
            return {k: thaw(x) for k, x in v.entries}
        return {f.name: thaw(getattr(v, f.name)) for f in dataclasses.fields(v)}
    if type(v) in (dict, MappingProxyType):
        return {k: thaw(x) for k, x in v.items()}
    if type(v) in (list, tuple):
        return [thaw(x) for x in v]
    return v


for vector in data["vectors"]:
    assert provider._digest(vector["value"]) == vector["digest"], "CANONICAL_METADATA"
assert inspect.iscoroutinefunction(type(run).__call__)
assert set(typing.get_type_hints(module.WorkflowIdentity)) == {"workflow_execution_id", "failure_occurrence_id"}
assert set(typing.get_type_hints(module.WorkflowDependencies)) == {s["operation_ref"] for s in workflow["steps"]}
assert thaw(run.descriptor) == entry["descriptor"]
outcome_types = typing.get_args(provider._Outcome0)
for vector in data["metadata"]:
    value = vector["value"]
    continuation = workflow["steps"][0]["failure_continuation"]
    assert thaw(provider._settlement(value, continuation, outcome_types)) == vector["expected"], "SETTLEMENT_METADATA"
    failure_type = next(t for t in outcome_types if "cleanupFailed" in t.__slots__)
    assert thaw(provider._settlement(failure_type(**value), continuation, outcome_types)) == vector["expected"], "NATIVE_SETTLEMENT_METADATA"


active_evaluations = []


class Active:
    def __eq__(self, other):
        active_evaluations.append("equality")
        raise AssertionError("ACTIVE_VALUE_EXECUTED")
    @property
    def status(self):
        active_evaluations.append("status")
        raise AssertionError("ACTIVE_VALUE_EXECUTED")


class ActiveMeta(type):
    def __eq__(cls, other):
        active_evaluations.append("metaclass equality")
        return False


class ActiveOutcome(metaclass=ActiveMeta):
    pass


assert provider._settlement(ActiveOutcome(), workflow["steps"][0]["failure_continuation"], outcome_types)["commit_status"] == "indeterminate"
assert not active_evaluations, "ACTIVE_METACLASS_EXECUTED"


async def one(case):
    mode, index = case["mode"], case["index"]
    calls, starts, commits, trace = [], [], [], []
    original = {s: m._execute for s, m in operations.items()}
    original_capture_result, original_result = material.capture_result, material.result
    first_call = material.steps["first"]
    call_types = {type(c): type(c).operation_input for c in material.steps.values()}
    comp_types = {type(c): type(c).arguments for c in material.compensations.values()}
    raw, identity = copy.deepcopy(data["parameters"]), dict(data["ids"])

    class Transaction:
        def __init__(self, n):
            self.n = n
        async def read(self, request):
            raise AssertionError("UNDECLARED_READ")
        async def rollback(self):
            trace.append("rollback")
        async def commit(self, batch):
            trace.append("commit:" + str(self.n))
            await asyncio.sleep(0)
            if self.n == index:
                if mode in ("reject", "binding-bad"):
                    return {"status": "rejected"}
                if mode == "indeterminate":
                    return {"status": "indeterminate"}
                if mode == "invalid-receipt":
                    return {"status": "unknown"}
                if mode == "throw-before":
                    raise RuntimeError("unknown commit")
            commits.append(batch)
            if self.n == index and mode == "throw-after":
                raise RuntimeError("acknowledgement lost")
            return {"status": "committed"}

    class Store:
        async def begin(self):
            n = len(starts); starts.append(n); trace.append("begin:" + str(n))
            if n == 0:
                # The Workflow must have captured both values and dependency
                # references before the first suspension.
                raw["order"]["id"] = "caller-mutated"
                raw["post_second"]["occurrence"]["event-id"] = "caller-mutated"
                identity["workflow_execution_id"] = "caller-mutated"
                deps.clear()
            await asyncio.sleep(0)
            if n == index and mode == "begin-throw":
                raise RuntimeError("begin failed")
            return Transaction(n)

    def shim(selector):
        async def execute(args, dependencies):
            n = len(calls); calls.append(selector)
            assert selector == workflow["steps"][n]["operation_ref"], "FORWARD_ORDER"
            assert args["order"]["id"] == "o", "CAPTURE_ALIAS"
            if n == index:
                if mode == "threw":
                    raise RuntimeError("call threw")
                if mode == "cancelled":
                    raise asyncio.CancelledError()
                if mode == "malformed":
                    return {"status": "committed", "value": {}, "extra": True}
                if mode == "active":
                    return {"status": Active(), "value": {}}
                if mode == "committed-bad":
                    return {"status": "committed", "value": {"id": 1}}
            return await original[selector](args, dependencies)
        return execute

    def argument_failure(self, input, results):
        if len(results) == index:
            raise TypeError("test argument failure")
        return call_types[type(self)](self, input, results)

    def final_failure(*args):
        raise TypeError("test result failure")

    def binding_failure(*args):
        raise TypeError("test binding failure")

    for selector, operation in operations.items():
        operation._execute = shim(selector)
    if mode == "not-started":
        for cls in call_types:
            cls.operation_input = argument_failure
    if mode == "final-bad":
        material.result = final_failure
    if mode == "binding-bad":
        for cls in comp_types:
            cls.arguments = binding_failure
    def clock():
        trace.append("clock")
        return "explicit-clock-time"
    deps = {}
    for step in workflow["steps"]:
        action = next(a for a in data["plan"]["operation_plan"]["selection"]["actions"] if a["bindings"]["selector"] == step["operation_ref"])
        clocks = {e["slot"]: clock for e in action["events"] if e["contract"]["occurred_at_policy"] == "generated"}
        deps[step["operation_ref"]] = {"store": Store(), **({"clocks": clocks} if clocks else {})}
    try:
        result = await run(raw, identity, deps)
        observed = thaw(result)
        expected_status = "succeeded" if mode == "success" else "orchestration-error" if mode in ("committed-bad", "final-bad") else "forward-stopped"
        assert result.status == expected_status, ("WORKFLOW_STATUS", mode, index, observed)
        assert observed["evaluation"] == case["expected"], ("WORKFLOW_EVALUATION", mode, index, observed["evaluation"], case["expected"])
        assert len(calls) == (len(workflow["steps"]) if index < 0 else index if mode == "not-started" else index + 1), "NO_CALL_AFTER_FAILURE"
        assert all(s not in calls for s in set(c["operation_ref"] for c in workflow["compensations"]) - set(s["operation_ref"] for s in workflow["steps"])), "IMPLICIT_COMPENSATION"
        recovery = case["expected"]["recovery"]
        intent = recovery["recovery_intent"] if recovery else None
        if result.status == "succeeded":
            assert thaw(result.value) == {"id": "o"}
            assert result.recovery_bindings is None
        elif intent:
            if mode == "binding-bad":
                assert result.bindings_status == "failed" and result.recovery_bindings is None, "BINDINGS_STATUS"
            else:
                assert result.bindings_status == "ready", "BINDINGS_STATUS"
                actual = result.recovery_bindings
                assert actual["intent_id"] == intent["intent_id"] and actual["plan_digest"] == intent["plan_digest"]
                assert [b["compensation_id"] for b in actual["bindings"]] == [b["compensation_id"] for b in intent["plan"]]
                for bound, planned in zip(actual["bindings"], intent["plan"]):
                    for key in ("invocation_identity", "compensation_id", "operation_ref", "action_sha256"):
                        assert bound[key] == planned[key]
                    expected_event = "u1" if bound["compensation_id"] == "first" else "u2"
                    assert bound["arguments"]["notice_input"]["occurrence"]["event-id"] == expected_event, "RECOVERY_ARGUMENT"
                    assert bound["arguments"]["order"]["id"] == "o"
        elif result.status != "succeeded":
            expected_bindings = "not-required" if recovery and recovery["workflow_evaluation_result"] == "not-required" else "not-evaluable"
            assert result.bindings_status == expected_bindings and result.recovery_bindings is None, "BINDINGS_STATUS"
        if mode == "success":
            assert len(commits) == len(workflow["steps"])
            assert [batch.events[0]["value"].occurrence["event-id"] for batch in commits] == [data["parameters"][s["events"][0]["input"]]["occurrence"]["event-id"] for s in workflow["steps"]]
            generated = sum(1 for step in workflow["steps"] for event in step["signature"]["events"] if event["contract"]["occurred_at_policy"] == "generated")
            assert trace.count("clock") == generated, "EXPLICIT_CLOCK_ONLY"
        try:
            result.status = "changed"
        except (AttributeError, TypeError):
            pass
        else:
            raise AssertionError("MUTABLE_OUTCOME")
    finally:
        for selector, operation in operations.items():
            operation._execute = original[selector]
        for cls, method in call_types.items():
            cls.operation_input = method
        for cls, method in comp_types.items():
            cls.arguments = method
        material.capture_result, material.result = original_capture_result, original_result


async def hostile_entry():
    class Store:
        async def begin(self):
            raise AssertionError("INVALID_ENTRY_EFFECT")
    class ActiveDict(dict):
        def __getitem__(self, key):
            raise AssertionError("ACTIVE_ENTRY_EXECUTED")
    valid_deps = {s["operation_ref"]: {"store": Store()} for s in workflow["steps"]}
    for identity, args, deps in [(dict(data["ids"], extra="x"), data["parameters"], valid_deps), (dict(data["ids"], workflow_execution_id="invalid id"), data["parameters"], valid_deps), (ActiveDict(data["ids"]), data["parameters"], valid_deps), (data["ids"], ActiveDict(data["parameters"]), valid_deps), (data["ids"], data["parameters"], {}), (data["ids"], data["parameters"], ActiveDict(valid_deps))]:
        try:
            await run(args, identity, deps)
        except TypeError:
            pass
        else:
            raise AssertionError("INVALID_ENTRY_ACCEPTED")
    original = provider._forward0
    provider._forward0 = lambda *args: None
    try:
        try:
            await run(data["parameters"], data["ids"], valid_deps)
        except TypeError as e:
            assert "Operation callable" in str(e)
        else:
            raise AssertionError("UNPINNED_IMPORT")
    finally:
        provider._forward0 = original


async def main():
    for case in data["cases"]:
        await one(case)
    await hostile_entry()


asyncio.run(main())
assert not active_evaluations, "ACTIVE_VALUE_EXECUTED_AND_CAUGHT"
print(json.dumps({"cases": len(data["cases"]), "metadata_vectors": len(data["metadata"]), "compensation_execution": False}))
