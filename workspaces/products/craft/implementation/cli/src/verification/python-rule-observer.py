"""Shared independent complete Rule observer, extracted from State Machine tests."""
import pathlib
import hashlib
import importlib.util

if "helper" not in globals():
    spec = importlib.util.spec_from_file_location("operation_observer", pathlib.Path(__file__).with_name("python-operation-observer.py"))
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)

require = helper.require
DATA_SUPPORT = "def _to_set(items, element):\n    keyed = {}\n    for item in items:\n        keyed.setdefault(element.key(item), item)\n    return tuple(keyed[key] for key in sorted(keyed, key=lambda key: key.encode(\"utf-16-be\", \"surrogatepass\")))\n"

def observe_rule(data, m, provider_override=None):
    """Inspect the complete transitive Rule program, including unreachable code."""
    for name, digest in helper.SUPPORT.items():
        require(hashlib.sha256((pathlib.Path(data['root']) / data['module_root'] / 'runtime' / name).read_bytes()).hexdigest() == digest, 'Rule support perimeter')
    c = data["nodes"][m["selector"]]["body"]["typed_contract"]
    ctx = helper.Context(data["rule_model"], m["relative_path"], data["module_root"])
    protocols = [ctx.protocol(p["type"]) for p in c["parameters"]]
    scope = {p["name"]: (p["type"], "p" + str(i)) for i, p in enumerate(c["parameters"])}
    serial = 0
    def fresh():
        nonlocal serial
        name = "q" + str(serial)
        serial += 1
        return name
    def value(e, bindings):
        if e["op"] == "literal":
            t, v = {"kind": "scalar", "name": e["type"]}, int(e["value"]) if e["type"] == "UInt64" else e["value"]
            return t, "_v.STRING.normalize(" + repr(v) + ")" if e["type"] == "String" else repr(v)
        if e["op"] == "variant":
            for d in ctx.declarations.values():
                if d["kind"] == "Enum":
                    for v in d["contract"]["variants"]:
                        if v["ontology_variant"] == e["selector"] and v["payload"] is None:
                            t = {"kind": "named", "selector": d["selector"]}
                            return t, ctx.protocol(t) + ".normalize({'variant': " + repr(v["name"]) + "})"
            require(False, "Rule variant")
        if e["op"] == "to_set":
            t, code = value(e["value"], bindings)
            require(t["kind"] == "list", "Rule set input")
            return {"kind": "set", "element": t["element"]}, "_to_set(" + code + ", " + ctx.protocol(t["element"]) + ")"
        require(e["op"] == "path", "Rule value expression")
        t, code = bindings[e["root"]]
        for prop in e["properties"]:
            collection = t["kind"] in ("list", "set")
            owner = t["element"] if collection else t
            field = next(f for f in ctx.declarations[owner["selector"]]["contract"]["properties"] if f["ontology_property"] == prop)
            if collection:
                item = fresh()
                code = "tuple(" + item + "[" + repr(field["name"]) + "] for " + item + " in " + code + ")"
                if t["kind"] == "set":
                    code = "_to_set(" + code + ", " + ctx.protocol(field["type"]) + ")"
                t = {"kind": t["kind"], "element": field["type"]}
            else:
                t, code = field["type"], code + "[" + repr(field["name"]) + "]"
        return t, code
    def predicate(e, bindings):
        op = e["op"]
        if op in ("all", "any"):
            return "(" + (" and " if op == "all" else " or ").join(predicate(t, bindings) for t in e["terms"]) + ")"
        if op == "not":
            return "(not " + predicate(e["term"], bindings) + ")"
        if op == "rule_ref":
            dependency = next(r for r in m["imports"] if r["selector"] == e["selector"])
            return dependency["local"] + "({" + ", ".join(repr(a["parameter"]) + ": " + value(a["value"], bindings)[1] for a in sorted(e["arguments"], key=lambda a: a["parameter"])) + "})"
        if op in ("eq", "lt", "contains", "set_equal"):
            lt, left = value(e["left"], bindings)
            rt, right = value(e["right"], bindings)
            if op == "contains":
                item, protocol = fresh(), ctx.protocol(rt)
                return "any(" + protocol + ".key(" + item + ") == " + protocol + ".key(" + right + ") for " + item + " in " + left + ")"
            if op == "lt":
                if lt == {"kind": "scalar", "name": "String"}:
                    left += '.encode("utf-16-be", "surrogatepass")'
                    right += '.encode("utf-16-be", "surrogatepass")'
                return "(" + left + " < " + right + ")"
            protocol = ctx.protocol(lt)
            return "(" + protocol + ".key(" + left + ") == " + protocol + ".key(" + right + "))"
        require(op in ("exists", "exactly_one", "unique"), "Rule predicate")
        collection_type, collection = value(e["collection"], bindings)
        item = fresh()
        nested = {**bindings, e["binding"]: (collection_type["element"], item)}
        if op == "unique":
            require(e["where"]["op"] == "eq" and e["where"]["left"] == e["where"]["right"], "unique key")
            t, code = value(e["where"]["left"], nested)
            return "(len({" + ctx.protocol(t) + ".key(" + code + ") for " + item + " in " + collection + "}) == len(" + collection + "))"
        condition = predicate(e["where"], nested)
        return "any(" + condition + " for " + item + " in " + collection + ")" if op == "exists" else "(sum(1 for " + item + " in " + collection + " if " + condition + ") == 1)"
    result = predicate(c["expression"], scope)
    runtime = helper.relative(m["relative_path"], data["module_root"] + "/runtime")
    expected = "from __future__ import annotations\nfrom " + runtime + " import values as _v\nfrom " + runtime + " import facts as _facts\n"
    for i in m["imports"]:
        target = next(r for r in data["rule_modules"] if r["selector"] == i["selector"])
        require(i["module"] == helper.relative(m["relative_path"], target["relative_path"][:-3]) and i["symbol"] == target["callable"], "Rule dependency import")
        expected += "from " + i["module"] + " import " + i["symbol"] + " as " + i["local"] + "\n"
    expected += "RULE_ID = " + repr(m["selector"]) + "\nCLOSURE_SHA256 = " + repr(m["closure_sha256"]) + "\n" + "".join(ctx.facts)
    expected += DATA_SUPPORT[DATA_SUPPORT.index("def _to_set"):]
    expected += "def " + m["callable"] + "(parameters: dict[str, object]) -> bool:\n    if type(parameters) is not dict or any(type(key) is not str for key in parameters):\n        raise TypeError('RULE_INPUT')\n"
    expected += "    if set(parameters) != {" + ", ".join(repr(p["name"]) for p in c["parameters"]) + "}:\n        raise TypeError('RULE_INPUT')\n"
    expected += "".join("    p" + str(i) + " = " + protocols[i] + ".normalize(parameters[" + repr(p["name"]) + "])\n" for i, p in enumerate(c["parameters"]))
    expected += "    return " + result + "\n"
    actual = (pathlib.Path(data["root"]) / m["relative_path"]).read_bytes() if provider_override is None else provider_override
    helper.equivalent(actual, expected, "Rule semantics/effects")

