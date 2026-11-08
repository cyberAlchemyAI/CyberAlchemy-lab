"""Checked public contracts -> complete Python Interface AST, without target imports.

Recognizes the selected generated grammar, not arbitrary equivalent Python.
Shared runtime pins retain their separate native qualification; they are not
semantic proofs. Read shapes reuse the independent Operation observer.
"""
import ast
import hashlib
import json
import pathlib
import sys

# The enclosing verifier injects the pinned independent Operation grammar.


def require(ok, reason):
    if not ok:
        raise ValueError("PYTHON_INTERFACE_OBSERVER:" + reason)


def digest(value):
    # Selected metadata has ASCII object keys; authored Unicode remains values.
    text = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    text = ''.join(('\\u%04x' % ord(c)) if 0xD800 <= ord(c) <= 0xDFFF else c for c in text)
    return hashlib.sha256(text.encode("utf8")).hexdigest()


def freeze(value):
    if type(value) is dict:
        return "_MappingProxyType({" + ", ".join(repr(k) + ": " + freeze(v) for k, v in value.items()) + "})"
    if type(value) is list:
        return base.tuple_code([freeze(v) for v in value])
    return repr(value)


BOUNDARY = '''
_T = _TypeVar("_T")
@_dataclass(frozen=True, slots=True)
class BoundaryValue(_Generic[_T]):
    _protocol: _v.ValueProtocol[_T]
    def normalize(self, value: object) -> _T:
        try:
            return self._protocol.normalize(value)
        except (TypeError, ValueError, KeyError):
            raise TypeError("INTERFACE_VALUE") from None
    def key(self, value: object) -> str:
        return self._protocol.key(self.normalize(value))
'''
VERSION = '''
def accepts_consumer_version(value: object) -> bool:
    if type(value) is not str or len(value) > 194:
        return False
    parts = value.split(".")
    if len(parts) != 3 or any(not (1 <= len(p) <= 64) or not p.isascii() or not p.isdecimal() or (len(p) > 1 and p[0] == "0") for p in parts):
        return False
'''


def expected(selector, contract, model, path, root, descriptor):
    context = base.Context(model, path, root)
    contracts = sorted(contract["contracts"], key=lambda c: c["contract_id"])
    members = sorted(contract["operations"], key=lambda o: o["operation_id"])
    local = {c["contract_id"]: c for c in contracts}
    cache, statements, exposed = {}, [], {}
    sequence = 0

    def value(t):
        nonlocal sequence
        tag = t["kind"]
        if tag in ("scalar", "named"):
            return (*context.type(t), context.protocol(t))
        identity = base.key(t)
        if identity in cache:
            return cache[identity]
        name = "_Public" + str(sequence)
        sequence += 1
        protocol = name + "Value"
        if tag == "contract":
            c = local[t["contract_id"]]
            fields = sorted(c["fields"], key=lambda f: f["name"])
            children = [value(f["type"]) for f in fields]
            shape = context.shape(name, [(f["name"], *child[:2], f["type"]["kind"] == "optional") for f, child in zip(fields, children)])
            rows = ["(" + repr(f["name"]) + ", " + child[2] + ", " + repr(f["type"]["kind"] == "optional") + ")" for f, child in zip(fields, children)]
            expression = "_facts.record_fact(" + repr(selector) + ", " + repr(c["contract_id"]) + ", " + base.tuple_code(rows) + ", " + repr(tuple(f["name"] for f in fields)) + ")"
        elif tag == "sum":
            variants = sorted(t["variants"], key=lambda v: v["name"])
            children = [value(v["payload"]) if v["payload"] else None for v in variants]
            cases = []
            for index, (v, child) in enumerate(zip(variants, children)):
                literal = "_Literal[" + repr(v["name"]) + "]"
                fields = [("variant", literal, literal, False)] + ([("payload", *child[:2], False)] if child else [])
                cases.append(context.shape(name + "Case" + str(index), fields))
            shape = tuple(" | ".join(c[i] for c in cases) for i in (0, 1))
            expression = "_facts.sum_fact({" + ", ".join(repr(v["name"]) + ": " + (child[2] if child else "None") for v, child in zip(variants, children)) + "})"
        else:
            child = value(t["element"])
            require(tag in ("optional", "list", "set"), "public type")
            if tag == "optional":
                shape = ("(" + child[0] + ") | None", "(" + child[1] + ") | None")
                expression = "_facts.optional_fact(" + child[2] + ")"
            else:
                shape = ("list[" + child[0] + "] | tuple[" + child[0] + ", ...]", "tuple[" + child[1] + ", ...]")
                expression = "_facts.sequence_fact(" + child[2] + ", " + repr(tag == "set") + ")"
        statements.append(protocol + " = " + expression + "\n")
        result = (*shape, protocol)
        cache[identity] = result
        return result

    public = [value({"kind": "contract", "contract_id": c["contract_id"]}) for c in contracts]
    endpoints = [(value(m["request"]), value(m["result"])) for m in members]
    context.shape("PublicContracts", [(c["contract_id"], *shape[:2], False) for c, shape in zip(contracts, public)])
    callables = ["_Callable[[" + request[1] + "], _Awaitable[" + result[1] + "]]" for request, result in endpoints]
    context.shape("Interface", [(m["operation_id"], call, call, False) for m, call in zip(members, callables)])

    def boundary(shape):
        if shape[2] not in exposed:
            name = "_boundary" + str(len(exposed))
            exposed[shape[2]] = name
            statements.append(name + ": BoundaryValue[" + shape[1] + "] = BoundaryValue(" + shape[2] + ")\n")
        return exposed[shape[2]]

    public_rows = [repr(c["contract_id"]) + ": " + boundary(shape) for c, shape in zip(contracts, public)]
    endpoint_rows = [repr(m["operation_id"]) + ": _MappingProxyType({'request': " + boundary(request) + ", 'result': " + boundary(result) + "})" for m, (request, result) in zip(members, endpoints)]
    runtime = base.relative(path, root + "/runtime")
    source = "from __future__ import annotations\nfrom dataclasses import dataclass as _dataclass\nfrom types import MappingProxyType as _MappingProxyType\n"
    source += "from typing import Awaitable as _Awaitable, Callable as _Callable, Generic as _Generic, TypeVar as _TypeVar, Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast\n"
    source += "from " + runtime + " import values as _v, facts as _facts\nfrom codecs import lookup as _lookup_codec\n_lookup_codec('utf-16-le')\n_lookup_codec('utf-16-be')\n"
    aliases = [("Contract_" + c["contract_id"].replace("-", "_") + suffix, shape[index]) for c, shape in zip(contracts, public) for suffix, index in (("", 1), ("Input", 0))]
    source += BOUNDARY + "".join(context.shapes) + "".join(name + " = " + native + "\n" for name, native in aliases) + "".join(context.facts + statements)
    source += "public_contracts = _MappingProxyType({" + ", ".join(public_rows) + "})\nendpoint_values = _MappingProxyType({" + ", ".join(endpoint_rows) + "})\n"
    source += "descriptor = " + freeze(descriptor) + "\nversion_policy = " + freeze(contract["version_policy"]) + "\n" + VERSION
    policy = contract["version_policy"]
    if policy["mode"] == "exact":
        source += "    return value == " + repr(policy["provider_version"]) + "\n"
    else:
        require(policy["mode"] == "backward", "version policy mode")
        source += "    provider = " + repr(tuple(policy["provider_version"].split("."))) + "\n"
        source += "    return parts[0] == provider[0] and ((len(parts[1]), parts[1]), (len(parts[2]), parts[2])) <= ((len(provider[1]), provider[1]), (len(provider[2]), provider[2]))\n"
    source += "__all__ = " + repr(['Interface', 'PublicContracts', 'BoundaryValue', 'public_contracts', 'endpoint_values', 'descriptor', 'version_policy', 'accepts_consumer_version'] + [name for name, _ in aliases]) + "\n"
    return source


def expected_descriptor(selector, authored, data):
    descriptor = dict(schema_version="domainspec.generated-python-interface-descriptor/v1-candidate", protocol_id="python.bound-interface/v1", selector=selector,
        definition_sha256="cfaaff5a40d3c84b128ffc572fa74652863241a8513bac8b63342fc1148fb4b5",
        version_definition_sha256="15f8132055336ba19d64fb0bee59d8f8bc711600ab1aa159116d5a03d65d6526",
        graph_sha256=data["graph_sha256"], source=authored["source"], field_compilation_sha256=data["field_compilation_sha256"], contract_sha256=digest(authored["contract"]), contract=authored["contract"],
        effect_contract="structural-interface-and-pure-shape-normalizers", invariant_execution="not-performed", transport_execution="not-performed", member_execution="not-performed",
        runtime=[dict(id=name, sha256=sha) for name, sha in base.SUPPORT.items()], authority_effect="none")
    descriptor["descriptor_sha256"] = digest(descriptor)
    return descriptor


def observe(data, module):
    root = data["module_root"]
    selector = module["selector"]
    feature, node = selector.split(":")
    path = root + "/features/" + feature.replace("-", "_") + "/src/application/interfaces/" + node.replace("-", "_") + ".py"
    require(module["relative_path"] == path and module["import_name"] == path[:-3].replace("/", "."), "module layout")
    authored = data["interfaces"][selector]
    descriptor = expected_descriptor(selector, authored, data)
    require(module["descriptor"] == descriptor, "descriptor meaning")
    source = expected(selector, authored["contract"], data["model"], path, root, descriptor)
    paths = {path} | {root + "/runtime/" + name for name in base.SUPPORT}
    for file in list(paths):
        parts = file.split("/")
        for i in range(1, len(parts)):
            paths.add("/".join(parts[:i]) + "/__init__.py")
    # Exact workspace closure/custody belongs to the enclosing verifier. This
    # observer owns the complete Interface grammar and its only runtime imports.
    for file in sorted(paths):
        content = pathlib.Path(data["root"], file).read_bytes()
        if file == path:
            try:
                base.equivalent(content, source, path)
            except ValueError as error:
                raise ValueError("PYTHON_INTERFACE_OBSERVER:AST:" + str(error)) from None
        elif file.endswith("/__init__.py"):
            require(not content, "nonempty package initializer:" + file)
        else:
            require(hashlib.sha256(content).hexdigest() == base.SUPPORT[file.split("/")[-1]], "support bytes:" + file)
    require(hashlib.sha256(pathlib.Path(data["root"], path).read_bytes()).hexdigest() == module["artifact_sha256"], "module artifact identity")
    return {"whole_source": True, "interfaces": 1, "artifacts": len(paths)}
