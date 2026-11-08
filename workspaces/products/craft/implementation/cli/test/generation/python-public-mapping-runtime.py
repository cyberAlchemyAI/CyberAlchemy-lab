"""Execute generated public Mapping packages against independent domain examples."""
import copy
import dataclasses
import importlib
import json
import sys
import typing

data = json.load(sys.stdin)
sys.path.insert(0, data["root"])


def thaw(value):
    if dataclasses.is_dataclass(value) and hasattr(value, "entries"):
        return {key: thaw(item) for key, item in value.entries}
    if hasattr(value, "items"):
        return {key: thaw(item) for key, item in value.items()}
    if type(value) is tuple:
        return [thaw(item) for item in value]
    return value


def response():
    detail = {"amount": "9007199254740993", "label": "first"}
    return {"id": "response-id", "lines": [detail, detail.copy(), {"amount": 2, "label": "last"}],
            "unique": [{"amount": 2, "label": "first"}, {"amount": 2, "label": "second"}, {"amount": 1, "label": "third"}],
            "choice": {"variant": "Detail", "payload": {"amount": 0, "label": "selected"}}}


def arguments():
    return {"response": response(), "order_total": "18446744073709551615", "memo": None,
            "fallback": "fallback", "order": {"id": "entity-id", "amount": 5},
            "foreign": {**response(), "id": "foreign-id"}, "choice": {"variant": "Detail", "payload": {"amount": 0, "label": "selected"}}}


def rejects(call):
    try:
        call()
    except TypeError as error:
        assert str(error) == "MAPPING_INPUT", str(error)
    else:
        raise AssertionError("INVALID_INPUT_ACCEPTED")


def immutable(call):
    try:
        call()
    except (TypeError, AttributeError):
        pass
    else:
        raise AssertionError("MUTABLE_PROJECTION")


events = []
armed = False


def audit(event, args):
    if armed and (event in ("open", "exec", "compile", "import") or event.startswith(("os.", "socket.", "subprocess."))):
        events.append(event)


sys.addaudithook(audit)
for plan in data["plans"]:
    apis = {m["selector"]: importlib.import_module(m["import_name"]) for m in plan["interfaces"]}
    functions = {}
    for module in plan["modules"]:
        fn = getattr(importlib.import_module(module["import_name"]), module["callable"])
        name = module["selector"].split(":map-", 1)[1]
        functions[name] = fn
        assert thaw(fn.descriptor) == module["descriptor"]
        hints = typing.get_type_hints(fn.__call__)
        inputs = typing.get_type_hints(hints["parameters"])
        if "response" in inputs:
            assert inputs["response"] is apis["commerce:api"].Contract_response
        if "foreign" in inputs:
            assert inputs["foreign"] is apis["commerce:other-api"].Contract_response
            assert inputs["foreign"] is not apis["commerce:api"].Contract_response
        if name == "full":
            assert hints["return"] is apis["commerce:api"].Contract_summary
            assert inputs["order_total"] == int | str
        if name == "empty":
            assert hints["return"] is apis["commerce:api"].Contract_empty
        args = {p["name"]: arguments()[p["name"]] for p in module["descriptor"]["contract"]["inputs"]}
        before = copy.deepcopy(args)
        armed = True
        out = fn(args)
        assert args == before
        if name == "full":
            assert [key for key, _ in out.entries] == ["id", "total", "memo", "details", "dedup", "amounts", "unique_amounts", "amounts_from_set", "choice"]
            assert out["id"] == ("entity-id" if data["domain"] else "response-id"), "WRONG_SOURCE_PATH"
            assert out["total"] == 18446744073709551615, "LOST_EXPLICIT_TOTAL"
            assert out["memo"] == "fallback"
            assert out["amounts"] == (9007199254740993, 9007199254740993, 2)
            assert out["unique_amounts"] == (9007199254740993, 2)
            assert out["amounts_from_set"] == (1, 2)
            assert len(out["details"]) == 3 and len(out["dedup"]) == 2
            assert thaw(out["choice"]) == {"variant": "Detail", "payload": {"amount": 0, "label": "selected"}}
            assert fn({**args, "memo": ""})["memo"] == "", "WRONG_NULLISH_FALLBACK"
            assert fn({**args, "memo": "supplied"})["memo"] == "supplied"
            assert fn({**args, "order_total": 0})["total"] == 0
            owned = apis["commerce:api"].public_contracts["response"].normalize(response())
            assert thaw(fn({**args, "response": owned})) == thaw(out)
            assert thaw(apis["commerce:api"].public_contracts["summary"].normalize(out)) == thaw(out)
            immutable(lambda: setattr(out["details"][0], "entries", ()))
            immutable(lambda: setattr(out["choice"]["payload"], "entries", ()))
            for patch in [{"lines": [{"amount": True, "label": "bad"}]}, {"unique": [{"amount": 1, "label": "same"}] * 2}, {"choice": {"variant": "None", "payload": None}}]:
                rejects(lambda: fn({**args, "response": {**response(), **patch}}))
            assert fn({**args, "response": {**response(), "choice": {"variant": "None"}}})["choice"]["variant"] == "None"
        elif name == "partial":
            assert thaw(out) == {"id": "response-id"}
        elif name == "foreign":
            assert thaw(out) == {"id": "foreign-id"}
        elif name == "sum":
            assert thaw(out) == {"choice": {"variant": "Detail", "payload": {"amount": 0, "label": "selected"}}}
            assert thaw(fn({"choice": {"variant": "None"}})) == {"choice": {"variant": "None"}}
        elif name in ("empty", "domain-empty"):
            assert thaw(out) == {}
        elif name in ("domain", "domain-only"):
            assert thaw(out) == {"id": "response-id" if name == "domain" else "entity-id", "amount": 18446744073709551615}
        else:
            raise AssertionError("UNTESTED_MAPPING")
        immutable(lambda: setattr(out, "entries", ()))
        immutable(lambda: setattr(fn, "descriptor", {}))
        immutable(lambda: fn.descriptor.__setitem__("contract", {}))
        for bad in (None, [], {**args, "hidden": 1}):
            rejects(lambda: fn(bad))
        if args:
            rejects(lambda: fn({k: v for k, v in args.items() if k != next(iter(args))}))
        if "order_total" in args:
            for bad in (True, -1, 1.0, "01", "+1", "18446744073709551616", None):
                rejects(lambda: fn({**args, "order_total": bad}))
        if "order" in args:
            # Even a field never used by the projection is normalized.
            rejects(lambda: fn({**args, "order": {"id": "entity-id", "amount": True}}))
        effects = []
        for spoof in (False, True):
            class Meta(type):
                def __eq__(self, other):
                    effects.append("metaclass-equality")
                    return spoof

            class Active(metaclass=Meta):
                def __getitem__(self, key):
                    effects.append("get")
                    return None

                def __iter__(self):
                    effects.append("iterate")
                    return iter(())

            rejects(lambda: fn(Active()))
            if "response" in args:
                rejects(lambda: fn({**args, "response": Active()}))
                rejects(lambda: fn({**args, "response": {**response(), "lines": Active()}}))
            if "order_total" in args:
                rejects(lambda: fn({**args, "order_total": Active()}))
        assert effects == [], ("ACTIVE_INPUT_EXECUTED", effects)
        if "response" in args:
            args["response"]["id"] = "changed"
            if name in ("full", "partial", "domain"):
                assert out["id"] != "changed"
        armed = False
        assert events == [], ("IMPLICIT_EFFECT", events)
print("native-public-mapping-ok")
