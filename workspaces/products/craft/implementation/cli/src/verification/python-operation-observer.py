"""Compiler-owned independent checked-action/whole-Python-source observer.

No generated module or TypeScript renderer is imported/executed. This recognizes
the selected finite generated grammar, not arbitrary equivalent Python or a
malicious-code sandbox. Dependency bytes are bound to separately tested plans.
"""
import ast
import hashlib
import json
import pathlib
import sys

SUPPORT = {"values.py": "01e2b483f8ab8d56499557430763ff351c08aac6c5a579a7c3d97a30922daa5d", "facts.py": "1d20d280ed71456e1f4cb57afa339df0b1c56c81b74772c0c3a08a2b4b828c8b"}


def require(ok, reason):
    if not ok:
        raise ValueError("PYTHON_OPERATION_OBSERVER:" + reason)


def key(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def dump(node):
    return ast.dump(node, include_attributes=False)


def equivalent(actual, expected, label):
    left, right = ast.parse(actual), ast.parse(expected)
    for i, (a, b) in enumerate(zip(left.body, right.body)):
        require(dump(a) == dump(b), label + ":statement:" + str(i) + ":" + ast.unparse(b).splitlines()[0][:100])
    require(len(left.body) == len(right.body), label + ":statement count")


def frozen(n):
    if isinstance(n, ast.Constant) and type(n.value) in (str, int, bool, type(None)):
        return n.value
    if isinstance(n, ast.Tuple):
        return [frozen(x) for x in n.elts]
    require(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_MappingProxyType" and len(n.args) == 1 and not n.keywords and isinstance(n.args[0], ast.Dict), "frozen descriptor")
    keys = [frozen(k) for k in n.args[0].keys]
    require(all(type(k) is str for k in keys) and len(keys) == len(set(keys)), "descriptor keys")
    return dict(zip(keys, [frozen(v) for v in n.args[0].values]))


def relative(source, target):
    a, b = pathlib.PurePosixPath(source).parent.parts, pathlib.PurePosixPath(target).parts
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return "." * (len(a) - n + 1) + ".".join(b[n:])


def tuple_code(items):
    return "(" + ", ".join(items) + ("," if items else "") + ")"


class Context:
    """Derive native read shapes, fact identity and owned conversions from types."""
    def __init__(self, model, provider, root):
        self.declarations = {d["selector"]: d for d in (model or {}).get("declarations", [])}
        self.provider, self.root = provider, root
        self.types, self.protocols, self.owners = {}, {}, {}
        self.shapes, self.facts, self.owned, self.imports = [], [], [], []
        self.sequence = 0

    def shape(self, name, fields):
        body = name + "Input = _TypedDict(" + repr(name + "Input") + ", {" + ", ".join(repr(n) + ": " + ("_NotRequired[" + i + "]" if o else i) for n, i, _, o in fields) + "})\n"
        body += "class " + name + "(_Protocol):\n"
        for n, _, native, _ in fields:
            if len(fields) > 1:
                body += "    @_overload\n"
            body += "    def __getitem__(self, key: _Literal[" + repr(n) + "]) -> " + native + ": ...\n"
        if len(fields) > 1:
            body += "    def __getitem__(self, key: str) -> object: ...\n"
        if not fields:
            body += "    pass\n"
        self.shapes.append(body)
        return name + "Input", name

    def type(self, t):
        k = key(t)
        if k in self.types:
            return self.types[k]
        kind = t["kind"]
        if kind == "scalar":
            value = {"String": ("str", "str"), "UInt64": ("int | str", "int"), "Bool": ("bool", "bool")}[t["name"]]
        elif kind == "named":
            d = self.declarations[t["selector"]]
            if d["kind"] == "Enum":
                value = self.type({"kind": "sum", "variants": d["contract"]["variants"]})
            else:
                name = "_Shape" + str(self.sequence)
                self.sequence += 1
                value = self.shape(name, [(p["name"], *self.type(p["type"]), p["type"]["kind"] == "optional") for p in d["contract"]["properties"]])
        elif kind == "sum":
            name = "_Shape" + str(self.sequence)
            self.sequence += 1
            cases = []
            for i, v in enumerate(t["variants"]):
                literal = "_Literal[" + repr(v["name"]) + "]"
                fields = [("variant", literal, literal, False)]
                if v["payload"] is not None:
                    fields.append(("payload", *self.type(v["payload"]), False))
                cases.append(self.shape(name + "Case" + str(i), fields))
            value = tuple(" | ".join(c[j] for c in cases) for j in (0, 1))
        else:
            i, n = self.type(t["element"])
            require(kind in ("optional", "list", "set"), "field kind")
            value = ("(" + i + ") | None", "(" + n + ") | None") if kind == "optional" else ("list[" + i + "] | tuple[" + i + ", ...]", "tuple[" + n + ", ...]")
        self.types[k] = value
        return value

    def protocol(self, t):
        k = key(t)
        if k in self.protocols:
            return self.protocols[k]
        kind = t["kind"]
        if kind == "scalar":
            body = "_v." + {"String": "STRING", "UInt64": "UINT64", "Bool": "BOOL"}[t["name"]]
        elif kind == "named":
            d = self.declarations[t["selector"]]
            if d["kind"] == "Enum":
                body = "_facts.named_sum_fact(" + repr(t["selector"]) + ", " + self.protocol({"kind": "sum", "variants": d["contract"]["variants"]}) + ")"
            else:
                fields = sorted(d["contract"]["properties"], key=lambda p: p["name"])
                rows = ["(" + repr(p["name"]) + ", " + self.protocol(p["type"]) + ", " + repr(p["type"]["kind"] == "optional") + ")" for p in fields]
                ids = tuple(p["name"] for p in fields if d["kind"] != "Entity" or p["identity"])
                body = "_facts.record_fact(" + repr(d["kind"]) + ", " + repr(t["selector"]) + ", " + tuple_code(rows) + ", " + repr(ids) + ")"
        elif kind == "sum":
            body = "_facts.sum_fact({" + ", ".join(repr(v["name"]) + ": " + (self.protocol(v["payload"]) if v["payload"] else "None") for v in sorted(t["variants"], key=lambda v: v["name"])) + "})"
        elif kind == "optional":
            body = "_facts.optional_fact(" + self.protocol(t["element"]) + ")"
        else:
            require(kind in ("list", "set"), "protocol kind")
            body = "_facts.sequence_fact(" + self.protocol(t["element"]) + ", " + repr(kind == "set") + ")"
        name = "_fact_type" + str(len(self.protocols))
        self.protocols[k] = name
        self.facts.append(name + " = " + body + "\n")
        return name

    def target(self, selector):
        d = self.declarations[selector]
        feature, node = selector.split(":")
        role = {"Entity": "entities", "Value Object": "value_objects", "Enum": "enums"}[d["kind"]]
        suffix = "_sum" if d["kind"] == "Enum" and any(v["payload"] is not None for v in d["contract"]["variants"]) else ""
        return self.root + "/features/" + feature.replace("-", "_") + "/src/domain/" + role + "/" + node.replace("-", "_") + suffix

    def own(self, t):
        k = key(t)
        if k in self.owners:
            return self.owners[k]
        name = "_own" + str(len(self.owners))
        self.owners[k] = name
        kind = t["kind"]
        if kind == "scalar":
            expression = "v"
        elif kind == "optional":
            expression = "None if v is None else " + self.own(t["element"]) + "(v)"
        elif kind in ("list", "set"):
            expression = "tuple(" + self.own(t["element"]) + "(item) for item in v)"
        elif kind == "sum":
            lines = []
            for v in t["variants"]:
                lines.append("    if v['variant'] == " + repr(v["name"]) + ":\n        return {'variant': " + repr(v["name"]) + (", 'payload': " + self.own(v["payload"]) + "(v['payload'])" if v["payload"] else "") + "}\n")
            self.owned.append("def " + name + "(v):\n" + "".join(lines) + "    raise TypeError('OPERATION_VALUE')\n")
            return name
        else:
            require(kind == "named", "owned kind")
            d = self.declarations[t["selector"]]
            node = t["selector"].split(":")[1]
            module, local = relative(self.provider, self.target(t["selector"])), name + "_provider"
            if d["kind"] == "Enum":
                plain = all(v["payload"] is None for v in d["contract"]["variants"])
                symbol = "parse_" + node.replace("-", "_") if plain else "".join(s[0].upper() + s[1:] for s in node.split("-")) + "ValueComponent"
                self.imports.append("from " + module + " import " + symbol + " as " + local + "\n")
                expression = local + "(v['variant'])" if plain else local + ".normalize(" + self.own({"kind": "sum", "variants": d["contract"]["variants"]}) + "(v))"
            else:
                self.imports.append("from " + module + " import create_" + node.replace("-", "_") + "_factory as " + local + "\n")
                fields = [repr(p["name"]) + ": " + self.own(p["type"]) + "(v[" + repr(p["name"]) + "])" for p in d["contract"]["properties"]]
                self.owned.append(name + "_factory = " + local + "()\ndef " + name + "(v):\n    result = " + name + "_factory.create({" + ", ".join(fields) + "})\n    if not result.ok:\n        raise TypeError('OPERATION_VALUE:' + ','.join(result.failure_codes))\n    return result.value\n")
                return name
        self.owned.append("def " + name + "(v):\n    return " + expression + "\n")
        return name

    def expressions(self, inputs):
        counter = 0
        def value(e):
            nonlocal counter
            op = e["op"]
            if op == "literal":
                t, v = {"kind": "scalar", "name": e["type"]}, int(e["value"]) if e["type"] == "UInt64" else e["value"]
                return t, "_v.STRING.normalize(" + repr(v) + ")" if e["type"] == "String" else repr(v)
            if op == "variant":
                for d in self.declarations.values():
                    if d["kind"] == "Enum":
                        for v in d["contract"]["variants"]:
                            if v["ontology_variant"] == e["selector"] and v["payload"] is None:
                                t = {"kind": "named", "selector": d["selector"]}
                                return t, self.protocol(t) + ".normalize({'variant': " + repr(v["name"]) + "})"
                require(False, "variant selector")
            if op == "to_set":
                t, code = value(e["value"])
                require(t["kind"] == "list", "to_set input")
                return {"kind": "set", "element": t["element"]}, "_to_set(" + code + ", " + self.protocol(t["element"]) + ")"
            require(op == "path", "expression kind")
            i = next(i for i, p in enumerate(inputs) if p["name"] == e["root"])
            t, code = inputs[i]["type"], "p" + str(i)
            for prop in e["properties"]:
                collection = t["kind"] in ("list", "set")
                owner = t["element"] if collection else t
                field = next(f for f in self.declarations[owner["selector"]]["contract"]["properties"] if f["ontology_property"] == prop)
                if collection:
                    item = "q" + str(counter)
                    counter += 1
                    code = "tuple(" + item + "[" + repr(field["name"]) + "] for " + item + " in " + code + ")"
                    if t["kind"] == "set":
                        code = "_to_set(" + code + ", " + self.protocol(field["type"]) + ")"
                    t = {"kind": t["kind"], "element": field["type"]}
                else:
                    t, code = field["type"], code + "[" + repr(field["name"]) + "]"
            return t, code
        return value



# Contract-fixed mechanics are inspected as AST, never executed as target code.
CAPTURE = '''
def _capture(value):
    count = 0
    def copy(v, depth):
        nonlocal count
        count += 1
        if count > 20000 or depth > 64:
            raise TypeError("OPERATION_INPUT")
        kind = type(v)
        if v is None or kind is str or kind is bool or kind is int or kind is float and _isfinite(v):
            return v
        if kind is list or kind is tuple:
            if len(v) > 1024:
                raise TypeError("OPERATION_INPUT")
            return tuple(copy(item, depth + 1) for item in v)
        if kind is not dict or len(v) > 2048 or any(type(k) is not str for k in v):
            raise TypeError("OPERATION_INPUT")
        return {k: copy(item, depth + 1) for k, item in v.items()}
    return copy(value, 0)
def _to_set(items, element):
    keyed = {}
    for item in items:
        keyed.setdefault(element.key(item), item)
    return tuple(keyed[key] for key in sorted(keyed, key=lambda key: key.encode("utf-16-be", "surrogatepass")))
'''

PORTS = '''
CommitReceipt = _TypedDict("CommitReceipt", {"status": _Literal["committed", "rejected", "indeterminate"]})
@_dataclass(frozen=True, slots=True)
class OperationBatch:
    writes: tuple[WriteIntent, ...]
    events: tuple[EventIntent, ...]
class Transaction(_Protocol):
    async def read(self, request: ReadRequest) -> object: ...
    async def commit(self, batch: OperationBatch) -> CommitReceipt: ...
    async def rollback(self) -> None: ...
class _Store(_Protocol):
    async def begin(self) -> Transaction: ...
'''


def observe(data, m):
    root = pathlib.Path(data["root"])
    action = data["actions"][m["selector"]]
    b, d = action["bindings"], m["descriptor"]
    source = data["nodes"][b["selector"]]["body"]
    require(d["bindings"] == b and d["source"] == action["source"] and d["action_sha256"] == action["action_sha256"], "checked action binding")
    require(d["execution_obligations"] == action["execution_obligations"], "execution obligations")
    require(d["field_model_sha256"] == (data["model"]["model_sha256"] if data["model"] else None), "field model binding")
    require(d["protocol_id"] == "python.bound-operation/v1" and d["source_compatibility"] == "explicit-action-bindings-not-legacy-typed-v1", "selected Operation profile")
    for field, rows in [("reads", b["reads"]), ("writes", b["writes"]), ("effects", b["events"])]:
        require(sorted(source[field]) == sorted(r["slot"] for r in rows), "source slots:" + field)
    require(source["failure_continuation"] == action["failure_continuation"], "failure continuation")
    require(d["effect_contract"] == "state-and-outbox" and d["continuation"] == "awaited-settlement" and d["return_semantics"] == "awaited-explicit-outcome", "effect contract")
    require(d["primary_callable_count"] == 1 and d["provider_durability_claim"] is False and d["publication"] is False and d["authority_effect"] == "none", "claim boundary")
    provider = (root / m["provider_path"]).read_bytes()
    require(hashlib.sha256(provider).hexdigest() == d["provider"]["sha256"], "provider digest")
    c = Context(data["model"], m["provider_path"], data["module_root"])
    rules, events = [], []
    for i, g in enumerate(action["guards"]):
        require(g["contract"] == data["nodes"][g["selector"]]["body"]["typed_contract"], "declared Rule source")
        target = next(r for r in data["rule_modules"] if r["selector"] == g["selector"])
        rules.append({"selector": g["selector"], "module": relative(m["provider_path"], target["relative_path"][:-3]), "symbol": target["callable"], "local": "_guard" + str(i)})
    event_targets = sorted(set(e["target"] for e in action["events"]))
    for i, selector in enumerate(event_targets):
        target = next(e for e in data["event_modules"] if e["selector"] == selector)
        events.append({"selector": selector, "module": relative(m["provider_path"], target["relative_path"][:-3]), "symbol": target["callable"], "local": "_make_event" + str(i)})
    require(rules == m["rule_imports"] and events == m["event_imports"], "selected dependency imports")
    inputs = [(c.protocol(p["type"]), *c.type(p["type"])) for p in b["inputs"]]
    initial = c.expressions(b["inputs"])
    value = c.expressions(b["inputs"] + [{"name": r["parameter"], "type": {"kind": "named", "selector": r["target"]}} for r in action["reads"]])
    result_type = c.type(b["result"]["type"])[1]
    result_protocol = c.protocol(b["result"]["type"])
    result = value(b["result"]["value"])[1]
    result_owner = c.own(b["result"]["type"])
    read_shapes, write_shapes, event_shapes = [], [], []
    def literal_field(name, v):
        return name, "_Literal[" + repr(v) + "]", "_Literal[" + repr(v) + "]", False
    reads = ""
    for i, r in enumerate(action["reads"]):
        n, p = str(i), "p" + str(len(inputs) + i)
        identity = next(f for f in c.declarations[r["target"]]["contract"]["properties"] if f["identity"])
        require(r["identity"] == {"property": identity["ontology_property"], "name": identity["name"], "type": identity["type"]}, "read identity source")
        kt = c.type(identity["type"])
        kp, rp = c.protocol(identity["type"]), c.protocol({"kind": "named", "selector": r["target"]})
        read_shapes.append(c.shape("_Read" + n, [literal_field("slot", r["slot"]), literal_field("target", r["target"]), ("key", *kt, False)])[1])
        reads += "        key" + n + " = " + kp + ".normalize(" + initial(r["key"])[1] + ")\n"
        reads += "        raw" + n + " = await transaction.read(_MappingProxyType({'slot': " + repr(r["slot"]) + ", 'target': " + repr(r["target"]) + ", 'key': key" + n + "}))\n"
        reads += "        if raw" + n + " is None:\n            return await abort('failed', 'READ_NOT_FOUND')\n"
        reads += "        " + p + " = " + rp + ".normalize(raw" + n + ")\n"
        reads += "        if " + kp + ".key(" + p + "[" + repr(identity["name"]) + "]) != " + kp + ".key(key" + n + "):\n            return await abort('failed', 'READ_IDENTITY_MISMATCH')\n"
    guards = ""
    for g, r in zip(action["guards"], rules):
        args = ", ".join(repr(a["parameter"]) + ": " + value(a["value"])[1] for a in g["arguments"])
        guards += "        if not " + r["local"] + "({" + args + "}):\n            return await abort('rejected', " + repr("RULE_REJECTED:" + g["selector"]) + ")\n"
    writes = ""
    for i, w in enumerate(action["writes"]):
        t = {"kind": "named", "selector": w["target"]}
        write_shapes.append(c.shape("_Write" + str(i), [literal_field("slot", w["slot"]), literal_field("target", w["target"]), literal_field("mode", w["mode"]), ("value", *c.type(t), False)])[1])
        writes += "        write" + str(i) + " = " + c.protocol(t) + ".normalize(" + value(w["value"])[1] + ")\n        " + c.own(t) + "(write" + str(i) + ")\n"
    event_calls, clocks = "", []
    for i, e in enumerate(action["events"]):
        j = event_targets.index(e["target"])
        require(e["contract"] == data["nodes"][e["target"]]["body"], "Event source")
        generated = e["contract"]["occurred_at_policy"] == "generated"
        if generated:
            clocks.append(e["slot"])
        native = "_Event" + str(j) + "Value"
        event_shapes.append(c.shape("_Event" + str(i), [literal_field("slot", e["slot"]), literal_field("target", e["target"]), ("value", native, native, False)])[1])
        event_calls += "        event" + str(i) + " = " + events[j]["local"] + "(captured[" + repr(e["parameter"]) + "]" + (", clocks[" + repr(e["slot"]) + "]" if generated else "") + ")\n"
    runtime = relative(m["provider_path"], data["module_root"] + "/runtime")
    expected = '''from __future__ import annotations
from asyncio import CancelledError as _CancelledError
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, Never as _Never, Callable as _Callable
from math import isfinite as _isfinite
from codecs import lookup as _lookup_codec
from RUNTIME import values as _v, facts as _facts
_lookup_codec("utf-16-le")
_lookup_codec("utf-16-be")
'''.replace("RUNTIME", runtime)
    expected += "".join("from " + r["module"] + " import " + r["symbol"] + " as " + r["local"] + "\n" for r in rules)
    expected += "".join("from " + e["module"] + " import " + e["symbol"] + " as " + e["local"] + ", EventInput as _Event" + str(i) + "Input, EventValue as _Event" + str(i) + "Value\n" for i, e in enumerate(events))
    expected += "".join(c.imports + c.shapes + c.facts + c.owned) + CAPTURE
    parameters = [repr(p["name"]) + ": " + inputs[i][1] for i, p in enumerate(b["inputs"])]
    parameters += [repr(e["parameter"]) + ": _Event" + str(event_targets.index(e["target"])) + "Input" for e in b["events"]]
    expected += 'OperationInput = _TypedDict("OperationInput", {' + ", ".join(parameters) + "})\nOperationValue = " + result_type + "\n"
    for name, shapes in [("ReadRequest", read_shapes), ("WriteIntent", write_shapes), ("EventIntent", event_shapes)]:
        expected += name + " = " + (" | ".join(shapes) or "_Never") + "\n"
    expected += PORTS
    if clocks:
        expected += '_Clocks = _TypedDict("_Clocks", {' + ", ".join(repr(s) + ": _Callable[[], str]" for s in clocks) + "})\n"
    expected += 'OperationDependencies = _TypedDict("OperationDependencies", {"store": _Store' + (', "clocks": _Clocks' if clocks else "") + "})\n"
    expected += '''@_dataclass(frozen=True, slots=True)
class OperationFailure:
    status: _Literal["rejected", "failed", "indeterminate"]
    stage: str
    code: str
    continuation: _Literal[FAILURE_CONTINUATION]
    cleanupFailed: bool
@_dataclass(frozen=True, slots=True)
class OperationSuccess:
    status: _Literal["committed"]
    value: OperationValue
OperationOutcome = OperationSuccess | OperationFailure
async def execute(parameters: OperationInput, dependencies: OperationDependencies) -> OperationOutcome:
    stage = "input"
    def failure(status, code, cleanup_failed=False):
        return OperationFailure(status, stage, code, FAILURE_CONTINUATION, cleanup_failed)
    try:
        captured = _capture(parameters)
        if type(captured) is not dict or set(captured) != set(INPUT_FIELDS):
            raise TypeError("OPERATION_INPUT")
'''.replace("FAILURE_CONTINUATION", repr(source["failure_continuation"])).replace("INPUT_FIELDS", repr(tuple(p["name"] for p in b["inputs"]) + tuple(e["parameter"] for e in b["events"])))
    expected += "".join("        p" + str(i) + " = " + inputs[i][0] + ".normalize(captured[" + repr(p["name"]) + "])\n" for i, p in enumerate(b["inputs"]))
    expected += '''    except (Exception, _CancelledError):
        return failure("failed", "OPERATION_INPUT")
    stage = "begin"
    try:
'''
    if clocks:
        expected += "        clocks = {" + ", ".join(repr(s) + ": dependencies['clocks'][" + repr(s) + "]" for s in clocks) + "}\n        if any(not callable(clock) for clock in clocks.values()):\n            raise TypeError('CLOCK_DEPENDENCY')\n"
    expected += '''        transaction = await dependencies["store"].begin()
    except (Exception, _CancelledError):
        return failure("failed", "BEGIN_FAILED")
    async def abort(status, code):
        try:
            await transaction.rollback()
            return failure(status, code)
        except (Exception, _CancelledError):
            return failure(status, code, True)
    commit_attempted = False
    try:
        stage = "read"
'''
    expected += reads + '        stage = "guard"\n' + guards + '        stage = "write-validation"\n' + writes + '        stage = "event"\n' + event_calls + '        stage = "result"\n'
    expected += "        result = " + result_protocol + ".normalize(" + result + ")\n        " + result_owner + "(result)\n"
    write_batch = ["_MappingProxyType({'slot': " + repr(w["slot"]) + ", 'target': " + repr(w["target"]) + ", 'mode': " + repr(w["mode"]) + ", 'value': write" + str(i) + "})" for i, w in enumerate(action["writes"])]
    event_batch = ["_MappingProxyType({'slot': " + repr(e["slot"]) + ", 'target': " + repr(e["target"]) + ", 'value': event" + str(i) + "})" for i, e in enumerate(action["events"])]
    expected += "        batch = OperationBatch(" + tuple_code(write_batch) + ", " + tuple_code(event_batch) + ")\n"
    expected += '''        stage = "commit"
        commit_attempted = True
        receipt = await transaction.commit(batch)
        if type(receipt) is not dict or len(receipt) != 1 or any(type(k) is not str for k in receipt) or "status" not in receipt or type(receipt["status"]) is not str:
            return failure("indeterminate", "INVALID_COMMIT_RECEIPT")
        if receipt["status"] == "committed":
            return OperationSuccess("committed", result)
        if receipt["status"] == "rejected":
            return failure("rejected", "COMMIT_REJECTED")
        return failure("indeterminate", "COMMIT_INDETERMINATE" if receipt["status"] == "indeterminate" else "INVALID_COMMIT_RECEIPT")
    except (Exception, _CancelledError):
        if commit_attempted:
            return failure("indeterminate", "COMMIT_UNCERTAIN")
        return await abort("failed", "OPERATION_FAILED")
'''
    equivalent(provider, expected, "Operation semantics/types/effects")
    wrapper = ast.parse((root / m["relative_path"]).read_bytes())
    require(len(wrapper.body) == 8 and isinstance(wrapper.body[4], ast.Assign) and frozen(wrapper.body[4].value) == d, "descriptor binding")
    wrapper.body[4].value = ast.Constant(None)
    provider_import = relative(m["relative_path"], m["provider_path"][:-3])
    require(provider_import == m["provider_import"], "provider import binding")
    expected = '''from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from PROVIDER import execute as _execute, OperationInput, OperationValue, OperationOutcome, OperationDependencies, OperationBatch, Transaction, CommitReceipt, ReadRequest, WriteIntent, EventIntent
_DESCRIPTOR = None
@_dataclass(frozen=True, slots=True)
class _BoundOperation:
    @property
    def descriptor(self): return _DESCRIPTOR
    async def __call__(self, parameters: OperationInput, dependencies: OperationDependencies) -> OperationOutcome:
        return await _execute(parameters, dependencies)
CALLABLE = _BoundOperation()
__all__ = ["CALLABLE", "OperationInput", "OperationValue", "OperationOutcome", "OperationDependencies", "OperationBatch", "Transaction", "CommitReceipt", "ReadRequest", "WriteIntent", "EventIntent"]
'''.replace("PROVIDER", provider_import).replace("CALLABLE", m["callable"])
    require(dump(wrapper) == dump(ast.parse(expected)), "frozen callable/export boundary")


if __name__ == "__main__":
    data = json.load(sys.stdin)
    root = pathlib.Path(data["root"])
    for name, digest in SUPPORT.items():
        require(hashlib.sha256((root / data["module_root"] / "runtime" / name).read_bytes()).hexdigest() == digest, "reviewed fact support")
    for entry in data["dependencies"]:
        require(hashlib.sha256((root / entry["relative_path"]).read_bytes()).hexdigest() == entry["sha256"], "dependency artifact binding:" + entry["relative_path"])
    for module in data["modules"]:
        observe(data, module)
    print(json.dumps({"observed": len(data["modules"]), "target_execution": False}))
