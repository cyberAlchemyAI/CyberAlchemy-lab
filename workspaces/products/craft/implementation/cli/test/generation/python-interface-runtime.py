"""Native Interface behavior checked against authored contracts, not source hashes."""
import ast
import collections.abc
import copy
import dataclasses
import importlib
import json
import pathlib
import sys
import typing

data = json.load(sys.stdin)
sys.path.insert(0, data["root"])


def thaw(value):
    if dataclasses.is_dataclass(value) and hasattr(value, "entries"):
        return {key: thaw(item) for key, item in value.entries}
    if isinstance(value, collections.abc.Mapping):
        return {key: thaw(item) for key, item in value.items()}
    if type(value) is tuple:
        return [thaw(item) for item in value]
    return value


def part(value):
    return str(len(value.encode("utf-16-le", "surrogatepass")) // 2) + ":" + value


def expected_key(kind, value, selector, contract):
    tag = kind["kind"]
    if tag == "scalar":
        name = kind["name"]
        return part(name) + part(("1" if value else "0") if name == "Bool" else str(value))
    if tag == "optional":
        return part("absent") if value is None else part("present") + part(expected_key(kind["element"], value, selector, contract))
    if tag in ("list", "set"):
        return part(tag) + part(str(len(value))) + "".join(part(expected_key(kind["element"], item, selector, contract)) for item in value)
    if tag == "sum":
        variant = next(v for v in kind["variants"] if v["name"] == value["variant"])
        return part("sum") + part(variant["name"]) + (part("no-payload") if variant["payload"] is None else part(expected_key(variant["payload"], value["payload"], selector, contract)))
    if tag == "contract":
        row = next(c for c in contract["contracts"] if c["contract_id"] == kind["contract_id"])
        return part(selector) + part(row["contract_id"]) + "".join(part(f["name"]) + part(expected_key(f["type"], value[f["name"]], selector, contract)) for f in sorted(row["fields"], key=lambda f: f["name"]))
    row = next(d for d in data["model"]["declarations"] if d["selector"] == kind["selector"])
    if row["kind"] == "Enum":
        return part(row["selector"]) + part(expected_key({"kind": "sum", "variants": row["contract"]["variants"]}, value, selector, contract))
    assert row["kind"] == "Value Object", "ENTITY_LEAK"
    return part("Value Object") + part(row["selector"]) + "".join(part(f["name"]) + part(expected_key(f["type"], value[f["name"]], selector, contract)) for f in sorted(row["contract"]["properties"], key=lambda f: f["name"]))


def fields_of(shape):
    if "__getitem__" not in shape.__dict__:
        return {}
    methods = typing.get_overloads(shape.__getitem__) or [shape.__getitem__]
    return {typing.get_args(typing.get_type_hints(method)["key"])[0]: typing.get_type_hints(method)["return"] for method in methods}


def rejects(call):
    try:
        call()
    except TypeError as error:
        assert str(error) == "INTERFACE_VALUE", str(error)
    else:
        raise AssertionError("INVALID_INTERFACE_INPUT_ACCEPTED")


def immutable(call):
    try:
        call()
    except (TypeError, AttributeError):
        pass
    else:
        raise AssertionError("MUTABLE_PUBLIC_BOUNDARY")


events = []
armed = False


def audit(event, args):
    if armed and (event in ("open", "exec", "compile", "import") or event.startswith(("os.", "socket.", "subprocess."))):
        events.append(event)


sys.addaudithook(audit)
for module in data["modules"]:
    api = importlib.import_module(module["import_name"])
    contract = module["descriptor"]["contract"]
    assert thaw(api.descriptor) == module["descriptor"]
    assert thaw(api.version_policy) == contract["version_policy"]
    tree = ast.parse(pathlib.Path(data["root"], module["relative_path"]).read_text())
    interface_class = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Interface")
    assert len(interface_class.bases) == 1 and isinstance(interface_class.bases[0], ast.Name) and interface_class.bases[0].id == "_Protocol"
    assert all(isinstance(n, ast.FunctionDef) and len(n.body) == 1 and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant) and n.body[0].value.value is Ellipsis for n in interface_class.body)
    assert api.Interface._is_protocol is True
    public_types, members = fields_of(api.PublicContracts), fields_of(api.Interface)
    assert list(public_types) == sorted(c["contract_id"] for c in contract["contracts"])
    assert list(members) == sorted(o["operation_id"] for o in contract["operations"])
    submit = typing.get_args(members["submit-order"])
    assert typing.get_origin(members["submit-order"]) is collections.abc.Callable
    assert submit[0] == [public_types["request"]]
    assert typing.get_origin(submit[1]) is collections.abc.Awaitable, "WRONG_ASYNC_SIGNATURE"
    assert typing.get_args(submit[1]) == (public_types["response"],)
    response_types = fields_of(public_types["response"])
    assert response_types["total"] is int and response_types["enabled"] is bool
    assert response_types["lines"] == tuple[int, ...]
    assert type(None) in typing.get_args(response_types["memo"])
    assert fields_of(public_types["empty"]) == {}
    assert public_types["shadow-response"] is not public_types["response"]
    for name, shape in public_types.items():
        alias = "Contract_" + name.replace("-", "_")
        assert getattr(api, alias) is shape and alias in api.__all__
        assert alias + "Input" in api.__all__
    assert api.endpoint_values["submit-order"]["result"] is api.public_contracts["response"]
    assert api.endpoint_values["submit-order"]["request"] is api.public_contracts["request"]
    assert api.public_contracts["shadow-response"] is not api.public_contracts["response"]
    before = copy.deepcopy(data["response"])
    request = copy.deepcopy(before)
    armed = True
    value = api.public_contracts["response"].normalize(request)
    assert request == before
    assert value["total"] == 18446744073709551615
    assert value["choice"]["payload"]["amount"] == 9007199254740993
    assert value["lines"] == (2, 2, 1) and value["tags"] == ("a", "z")
    assert value["memo"] is None and value["enabled"] is True
    request["choice"]["payload"]["amount"] = 0
    assert value["choice"]["payload"]["amount"] == 9007199254740993
    assert thaw(api.public_contracts["empty"].normalize({})) == {}
    assert api.endpoint_values["find"]["result"].normalize(None) is None
    assert thaw(api.endpoint_values["find"]["result"].normalize(before)) == thaw(value)
    for name in ("response", "shadow-response"):
        normalized = api.public_contracts[name].normalize(before)
        expected = expected_key({"kind": "contract", "contract_id": name}, thaw(normalized), module["selector"], contract)
        assert api.public_contracts[name].key(normalized) == expected, "PUBLIC_IDENTITY_KEY"
    assert api.public_contracts["response"].key(value) != api.public_contracts["shadow-response"].key(value), "PUBLIC_IDENTITY_COLLAPSE"
    if data["model"]:
        assert value["choice"]["payload"]["money"]["amount"] == 9007199254740993
        assert value["choice"]["payload"]["status"]["payload"]["currency"] == "USD"
        # The declared Rule is always false: pure public normalization must not
        # silently become a validating Value Object factory.
    immutable(lambda: setattr(value, "entries", ()))
    immutable(lambda: setattr(value["choice"]["payload"], "entries", ()))
    immutable(lambda: setattr(api.public_contracts["response"], "_protocol", None))
    immutable(lambda: api.public_contracts.__setitem__("response", None))
    immutable(lambda: api.endpoint_values["submit-order"].__setitem__("result", None))
    immutable(lambda: api.descriptor["contract"].__setitem__("contracts", ()))
    for bad in (None, [], {}, {**before, "unknown": 1}, {**before, "tags": ["a", "a"]}, {**before, "enabled": 1}, {**before, "choice": {"variant": "None", "payload": None}}):
        rejects(lambda: api.public_contracts["response"].normalize(bad))
        rejects(lambda: api.public_contracts["response"].key(bad))
    for bad in (True, -1, 1.0, "01", "+1", "1\n", "18446744073709551616", None):
        rejects(lambda: api.public_contracts["response"].normalize({**before, "total": bad}))
    for row in data["versions"]:
        assert api.accepts_consumer_version(row["value"]) is row["accepted"], ("VERSION_POLICY", row)
    assert api.accepts_consumer_version(contract["version_policy"]["provider_version"]) is True
    effects = []
    for spoof in (False, True):
        class Meta(type):
            def __eq__(self, other):
                effects.append("metaclass-equality")
                return spoof

        class Active(metaclass=Meta):
            def __iter__(self):
                effects.append("iteration")
                return iter(())

            def __str__(self):
                effects.append("conversion")
                return "1.2.0"

        for bad in (Active(), {**before, "total": Active()}, {**before, "lines": Active()}, {**before, "choice": Active()}):
            rejects(lambda: api.public_contracts["response"].normalize(bad))
            rejects(lambda: api.public_contracts["response"].key(bad))
        assert api.accepts_consumer_version(Active()) is False

    class ActiveDict(dict):
        def __getitem__(self, key):
            effects.append("get")
            return super().__getitem__(key)

    class ActiveString(str):
        def split(self, *args):
            effects.append("split")
            return super().split(*args)

    rejects(lambda: api.public_contracts["response"].normalize(ActiveDict(before)))
    rejects(lambda: api.public_contracts["response"].normalize({**before, "id": ActiveString("id")}))
    assert api.accepts_consumer_version(ActiveString("1.2.0")) is False
    assert effects == [], ("ACTIVE_INPUT_EXECUTED", effects)
    unicode_value = api.public_contracts["request"].normalize({"id": "\ud83d\ude00"})
    assert unicode_value["id"] == "😀"
    assert api.public_contracts["request"].key({"id": "e\u0301"}) != api.public_contracts["request"].key({"id": "é"})
    armed = False
    assert events == [], ("IMPLICIT_EFFECT", events)
print("native-interface-ok")
