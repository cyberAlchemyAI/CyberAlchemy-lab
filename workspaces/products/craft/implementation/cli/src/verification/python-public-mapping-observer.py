"""Checked Mapping v3 -> complete Python package observation without importing it.

Accepts the selected finite generated grammar, not arbitrary Python equivalence.
Checked contracts are supplied separately from the candidate plan. Shared runtime
pins retain their separate native tests; hashes alone are not semantic evidence.
"""
import hashlib
import json
import pathlib
import sys

# The enclosing verifier injects the independent, pinned Interface observer.
base = api.base


def require(ok, reason):
    if not ok:
        raise ValueError("PYTHON_PUBLIC_MAPPING_OBSERVER:" + reason)


def public(t):
    if t["kind"] == "contract":
        return True
    if t["kind"] == "sum":
        return any(v["payload"] is not None and public(v["payload"]) for v in t["variants"])
    return t["kind"] not in ("scalar", "named") and public(t["element"])


def qualified(t, selector):
    if t["kind"] == "contract":
        return dict(t, interface_selector=selector)
    if t["kind"] == "sum":
        return dict(t, variants=[dict(v, payload=qualified(v["payload"], selector) if v["payload"] else None) for v in t["variants"]])
    return t if t["kind"] in ("scalar", "named") else dict(t, element=qualified(t["element"], selector))


SET = '''
def _to_set(items, element):
    keyed = {}
    for item in items:
        keyed.setdefault(element.key(item), item)
    return tuple(keyed[key] for key in sorted(keyed, key=lambda key: key.encode("utf-16-be", "surrogatepass")))
'''


def provider(mapping, model, path, root, imports):
    context = base.Context(model, path, root)
    contract = mapping["contract"]
    aliases = {i["selector"]: "_api" + str(n) for n, i in enumerate(imports)}
    interfaces = {i["source"]["selector"]: i["contract"] for i in mapping["interfaces"]}
    cache, statements = {}, []
    sequence = 0

    def shape(t):
        nonlocal sequence
        if not public(t):
            return (*context.type(t), context.protocol(t))
        identity = base.key(t)
        if identity in cache:
            return cache[identity]
        tag = t["kind"]
        if tag == "contract":
            alias = aliases[t["interface_selector"]]
            native = alias + ".Contract_" + t["contract_id"].replace("-", "_")
            result = (native, native, alias + ".public_contracts[" + repr(t["contract_id"]) + "]")
        else:
            name = "_Mapping" + str(sequence)
            sequence += 1
            if tag == "sum":
                variants = sorted(t["variants"], key=lambda v: v["name"])
                children = [shape(v["payload"]) if v["payload"] else None for v in variants]
                cases = []
                for n, (v, child) in enumerate(zip(variants, children)):
                    literal = "_Literal[" + repr(v["name"]) + "]"
                    cases.append(context.shape(name + "Case" + str(n), [("variant", literal, literal, False)] + ([("payload", *child[:2], False)] if child else [])))
                types = tuple(" | ".join(c[n] for c in cases) for n in (0, 1))
                expression = "_facts.sum_fact({" + ", ".join(repr(v["name"]) + ": " + (child[2] if child else "None") for v, child in zip(variants, children)) + "})"
            else:
                require(tag in ("optional", "list", "set"), "public composite")
                child = shape(t["element"])
                types = ("(" + child[0] + ") | None", "(" + child[1] + ") | None") if tag == "optional" else ("list[" + child[0] + "] | tuple[" + child[0] + ", ...]", "tuple[" + child[1] + ", ...]")
                expression = "_facts.optional_fact(" + child[2] + ")" if tag == "optional" else "_facts.sequence_fact(" + child[2] + ", " + repr(tag == "set") + ")"
            result = (*types, name + "Value")
            statements.append(result[2] + " = " + expression + "\n")
        cache[identity] = result
        return result

    def expression(e):
        nonlocal sequence
        if e["op"] in ("literal", "variant"):
            return context.expressions([])(e)
        if e["op"] == "to_set":
            t, code = expression(e["value"])
            require(t["kind"] == "list", "explicit set input")
            return {"kind": "set", "element": t["element"]}, "_to_set(" + code + ", " + shape(t["element"])[2] + ")"
        require(e["op"] == "path", "expression")
        n = next(n for n, p in enumerate(contract["inputs"]) if p["name"] == e["root"])
        t, code = contract["inputs"][n]["type"], "p" + str(n)
        for prop in e["properties"]:
            collection = t["kind"] in ("list", "set")
            owner = t["element"] if collection else t
            if owner["kind"] == "contract":
                c = next(c for c in interfaces[owner["interface_selector"]]["contracts"] if c["contract_id"] == owner["contract_id"])
                f = next(f for f in c["fields"] if f["ontology_field"] == prop)
                field_type = qualified(f["type"], owner["interface_selector"])
            else:
                require(owner["kind"] == "named", "declared path owner")
                f = next(f for f in context.declarations[owner["selector"]]["contract"]["properties"] if f["ontology_property"] == prop)
                field_type = f["type"]
            if collection:
                item = "_item" + str(sequence)
                sequence += 1
                code = "tuple(" + item + "[" + repr(f["name"]) + "] for " + item + " in " + code + ")"
                if t["kind"] == "set":
                    code = "_to_set(" + code + ", " + shape(field_type)[2] + ")"
                t = {"kind": t["kind"], "element": field_type}
            else:
                t, code = field_type, code + "[" + repr(f["name"]) + "]"
        return t, code

    inputs = [(p["name"], shape(p["type"])) for p in contract["inputs"]]
    fields = []
    for f in mapping["bindings"]["fields"]:
        types = shape(f["target"]["type"])
        value = expression(f["value"])[1]
        fallback = expression(f["default"])[1] if f["default"] is not None else None
        fields.append((f["target"]["name"], types, value, fallback))
    result = ""
    if contract["total"] and contract["target"]["kind"] == "contract":
        result = "_ReadModel = " + shape(contract["target"])[1] + "\n"
    else:
        context.shape("_ReadModel", [(name, *s[:2], False) for name, s, _, _ in fields])
    source = "from __future__ import annotations\nfrom typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast\n"
    source += "from " + base.relative(path, root + "/runtime") + " import values as _v, facts as _facts\nfrom codecs import lookup as _lookup_codec\n_lookup_codec('utf-16-le')\n_lookup_codec('utf-16-be')\n"
    for i in imports:
        parent, member = i["path"].rsplit(".", 1)
        source += "from " + parent + " import " + member + " as " + aliases[i["selector"]] + "\n"
    for i in imports:
        source += "if " + " or ".join(aliases[i["selector"]] + ".descriptor[" + repr(k) + "] != " + repr(i["descriptor"][k]) for k in ("selector", "contract_sha256", "graph_sha256", "field_compilation_sha256")) + ":\n    raise TypeError('MAPPING_INTERFACE_BINDING')\n"
    source += "".join(context.shapes + context.facts + statements) + result
    source += '_Parameters = _TypedDict("_Parameters", {' + ", ".join(repr(name) + ": " + s[0] for name, s in inputs) + "})\n" + SET
    source += "def map_values(parameters: _Parameters) -> _ReadModel:\n    try:\n"
    source += "        if type(parameters) is not dict or len(parameters) != " + str(len(inputs)) + " or any(type(key) is not str for key in parameters):\n            raise TypeError('MAPPING_INPUT')\n"
    source += "        if any(key not in " + repr(tuple(name for name, _ in inputs)) + " for key in parameters):\n            raise TypeError('MAPPING_INPUT')\n"
    for n, (name, s) in enumerate(inputs):
        source += "        p" + str(n) + " = " + s[2] + ".normalize(parameters[" + repr(name) + "])\n"
    for n, (_, s, value, fallback) in enumerate(fields):
        v = "v" + str(n)
        source += "        " + v + " = " + value + "\n"
        if fallback is not None:
            source += "        if " + v + " is None:\n            " + v + " = " + fallback + "\n"
        source += "        " + v + " = " + s[2] + ".normalize(" + v + ")\n"
    source += "    except (TypeError, ValueError, KeyError):\n        raise TypeError('MAPPING_INPUT') from None\n"
    source += "    return _cast(_ReadModel, _facts._Fact(" + base.tuple_code(["(" + repr(name) + ", v" + str(n) + ")" for n, (name, _, _, _) in enumerate(fields)]) + "))\n"
    return source


def binding(module, descriptor):
    source = "from __future__ import annotations\nfrom dataclasses import dataclass as _dataclass\nfrom types import MappingProxyType as _MappingProxyType\n"
    source += "from " + base.relative(module["relative_path"], module["provider_path"][:-3]) + " import map_values as _map_values, _Parameters, _ReadModel\n"
    source += "_DESCRIPTOR = " + api.freeze(descriptor) + "\n"
    source += '''@_dataclass(frozen=True, slots=True)
class _BoundMapping:
    @property
    def descriptor(self):
        return _DESCRIPTOR
    def __call__(self, parameters: _Parameters) -> _ReadModel:
        return _map_values(parameters)
'''
    return source + module["callable"] + " = _BoundMapping()\n__all__ = " + repr([module["callable"]]) + "\n"


def observe(data, module):
    mapping, interfaces = data["mapping"], {i["selector"]: i for i in data["interfaces"]}
    selector, root = mapping["selector"], data["module_root"]
    feature, node = selector.split(":")
    path = root + "/features/" + feature.replace("-", "_") + "/src/application/mappings/" + node.replace("-", "_") + ".py"
    provider_path = str(pathlib.PurePosixPath(path).parent) + "/_providers/" + pathlib.PurePosixPath(path).name
    require(module["selector"] == selector and module["relative_path"] == path and module["provider_path"] == provider_path and module["import_name"] == path[:-3].replace("/", ".") and module["callable"] == "mapping_" + node.replace("-", "_"), "Mapping layout")
    require(sorted(interfaces) == sorted(mapping["bindings"]["interface_selectors"]), "Interface closure")
    for authored in mapping["interfaces"]:
        i = interfaces[authored["source"]["selector"]]
        api.observe({**data, "interfaces": {i["selector"]: {"contract": authored["contract"], "source": {k: authored["source"][k] for k in ("relative_path", "sha256")}}}}, i)
    imports = [dict(selector=s, path=base.relative(provider_path, interfaces[s]["relative_path"][:-3]), descriptor=interfaces[s]["descriptor"], artifact_sha256=interfaces[s]["artifact_sha256"]) for s in mapping["bindings"]["interface_selectors"]]
    provider_content = pathlib.Path(data["root"], provider_path).read_bytes()
    sources = {provider_path: provider(mapping, data["model"], provider_path, root, imports)}
    descriptor = dict(schema_version="domainspec.generated-python-public-mapping-descriptor/v1-candidate", protocol_id="python.bound-mapping/v1", selector=selector,
        mapping_sha256=mapping["mapping_sha256"], definition_sha256="686852a3615345f8ae2f66957d0b6c0ce825007b0e7c5d41492644b880aac0b9", contract=mapping["contract"], bindings=mapping["bindings"],
        imports=[dict(selector=i["selector"], path=i["path"], artifact_sha256=i["artifact_sha256"], contract_sha256=i["descriptor"]["contract_sha256"]) for i in imports],
        provider_sha256=hashlib.sha256(provider_content).hexdigest(), field_compilation_sha256=data["field_compilation_sha256"], graph_sha256=data["graph_sha256"],
        result_fields=[f["target"]["name"] for f in mapping["bindings"]["fields"]],
        return_semantics="field-projection-not-construction", effect_contract="pure-explicit-field-projection", invariant_execution="not-performed", authority_effect="none")
    descriptor["descriptor_sha256"] = api.digest(descriptor)
    require(module["descriptor"] == descriptor, "Mapping descriptor")
    sources[path] = binding(module, descriptor)
    paths = set(sources) | {root + "/runtime/" + name for name in base.SUPPORT}
    for file in list(paths):
        parts = file.split("/")
        paths.update("/".join(parts[:n]) + "/__init__.py" for n in range(1, len(parts)))
    # The enclosing verifier owns whole-workspace closure/custody. This observer
    # checks the entire selected grammar and exact direct Interface dependencies.
    for file in sorted(paths):
        content = pathlib.Path(data["root"], file).read_bytes()
        if file in sources:
            try:
                base.equivalent(content, sources[file], file)
            except (ValueError, SyntaxError) as error:
                raise ValueError("PYTHON_PUBLIC_MAPPING_OBSERVER:AST:" + str(error)) from None
        elif file.endswith("/__init__.py"):
            require(not content, "nonempty initializer:" + file)
        else:
            require(hashlib.sha256(content).hexdigest() == base.SUPPORT[file.split("/")[-1]], "support bytes:" + file)
    return {"whole_source": True, "mappings": 1, "interfaces": len(interfaces), "artifacts": len(paths)}
