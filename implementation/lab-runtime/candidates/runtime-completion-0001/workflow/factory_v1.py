"""Inert selected-code observation, not a producer factory or effect capability.

The caller supplies independently selected bytes and an already loaded callable.
Only compile/code/module/registration joins occur here. No source is imported,
no class is constructed and no callable is invoked. Mutable globals, defaults,
current grants, actual instance custody and invocation lineage remain unproved.
"""
import ast
import hashlib
import json
import types


class BindingRefusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise BindingRefusal(code)


def plain(value):
    remaining = [10000]

    def visit(item, depth):
        remaining[0] -= 1
        if remaining[0] < 0 or depth > 16:
            return False
        if type(item) is dict:
            return len(item) <= 1024 and all(
                type(key) is str and len(key) <= 256 and visit(child, depth + 1)
                for key, child in item.items())
        if type(item) is list:
            return len(item) <= 1024 and all(visit(child, depth + 1) for child in item)
        if type(item) is str:
            return len(item) <= 4096
        if type(item) is int:
            return -(1 << 63) <= item < (1 << 63)
        return type(item) is bool or item is None
    return visit(value, 0)


def text(value):
    return type(value) is str and 0 < len(value) <= 4096 and "\0" not in value


def digest(value):
    return type(value) is str and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def relative(value):
    return (text(value) and not value.startswith("/") and "\\" not in value
            and all(part not in ("", ".", "..") for part in value.split("/")))


def binding(value):
    need(type(value) is dict and set(value) == {"path", "sha256"}, "BINDING")
    need(relative(value["path"]) and digest(value["sha256"]), "BINDING")


def selected(raw, expected, limit):
    need(type(raw) is bytes and 0 < len(raw) <= limit and digest(expected), "SELECTED_BYTES")
    need(hashlib.sha256(raw).hexdigest() == expected, "SELECTED_DRIFT")
    return raw


def document(raw, expected):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "DUPLICATE_KEY")
            result[key] = value
        return result
    selected(raw, expected, 1048576)
    try:
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: need(False, "NONFINITE"))
    except (ValueError, UnicodeError, RecursionError):
        raise BindingRefusal("DOCUMENT_ENCODING") from None
    need(plain(value), "DOCUMENT_DATA")
    return value


def registry_origins(raw, expected):
    """Read three literal tables from selected public source; never execute it."""
    selected(raw, expected, 1048576)
    names = {"REGISTRY", "IMPLEMENTATION_ORIGINS", "STAGED_PRODUCER_ORIGINS"}
    found = {}
    try:
        tree = ast.parse(raw)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in names:
                        need(target.id not in found, "REGISTRY_DUPLICATE")
                        found[target.id] = ast.literal_eval(node.value)
    except (SyntaxError, ValueError, TypeError, RecursionError):
        raise BindingRefusal("REGISTRY_ENCODING") from None
    need(set(found) == names, "REGISTRY_TABLES")
    registry = found["REGISTRY"]
    need(type(registry) is dict and len(registry) == 28, "REGISTRY_COVERAGE")
    return found


def safe_code(code):
    """Code equality must not reach object-controlled constants."""
    pending = [(code, 0)]
    count = 0
    while pending:
        value, depth = pending.pop()
        count += 1
        need(count <= 10000 and depth <= 64, "CODE_BOUND")
        kind = type(value)
        if kind is types.CodeType:
            pending.extend((c, depth + 1) for c in value.co_consts)
        elif kind in (tuple, frozenset):
            pending.extend((c, depth + 1) for c in value)
        else:
            need(kind in (str, bytes, int, float, complex, bool)
                 or value is None or value is Ellipsis, "CODE_CONSTANT")


def verify_callable(selection_raw, *, expected_selection_sha256,
                    source_inventory_raw, expected_inventory_sha256,
                    registry_source_raw, expected_registry_source_sha256,
                    source_raw, expected_source_cut, repository_root,
                    module, callable_object, expected_instance=None):
    """Observe selected code identity only; the result cannot authorize invocation.

    Function, ordinary bound method and classmethod are supported. Properties,
    static methods, custom metaclasses and dynamic closures explicitly refuse.
    The source inventory is a versioned selected subset, not a full Source cut.
    """
    need(text(expected_source_cut) and text(repository_root)
         and repository_root.startswith("/") and not repository_root.endswith("/")
         and "\\" not in repository_root
         and all(p not in ("", ".", "..") for p in repository_root.split("/")[1:]),
         "EXPECTED_CONTEXT")
    row = document(selection_raw, expected_selection_sha256)
    need(type(row) is dict and set(row) == {
        "schema_version", "source_cut", "transition_ref", "producer_binding",
        "entrypoint", "callable_kind", "compile_optimize"}, "SELECTION_SHAPE")
    need(row["schema_version"] == "lab-inert-callable-selection/v1"
         and row["source_cut"] == expected_source_cut, "SELECTION_CONTEXT")
    need(row["callable_kind"] in ("function", "method", "classmethod")
         and type(row["compile_optimize"]) is int and row["compile_optimize"] in (0, 1, 2),
         "CALLABLE_PROFILE")
    binding(row["producer_binding"])
    need(text(row["entrypoint"]) and len(row["entrypoint"].split(".")) <= 8
         and all(p.isidentifier() for p in row["entrypoint"].split(".")), "ENTRYPOINT")
    inventory = document(source_inventory_raw, expected_inventory_sha256)
    need(type(inventory) is dict and set(inventory) == {"schema_version", "source_cut", "files"}
         and inventory["schema_version"] == "lab-inert-producer-source-subset/v1"
         and inventory["source_cut"] == expected_source_cut, "INVENTORY_CONTEXT")
    need(type(inventory["files"]) is list and 0 < len(inventory["files"]) <= 512,
         "INVENTORY_BOUND")
    members = {}
    for item in inventory["files"]:
        binding(item)
        need(item["path"] not in members, "INVENTORY_DUPLICATE")
        members[item["path"]] = item
    b = row["producer_binding"]
    need(members.get(b["path"]) == b, "SOURCE_MEMBERSHIP")
    tables = registry_origins(registry_source_raw, expected_registry_source_sha256)
    need(type(row["transition_ref"]) is str and row["transition_ref"] in tables["REGISTRY"],
         "TRANSITION")
    original = tables["REGISTRY"][row["transition_ref"]]
    allowed = {original["original_producer_path"]}
    allowed.update(tables["IMPLEMENTATION_ORIGINS"].get(original["family"], ()))
    allowed.update(tables["STAGED_PRODUCER_ORIGINS"])
    need(b["path"] in allowed and b["path"].endswith(".py"), "PRODUCER_ORIGIN")
    selected(source_raw, b["sha256"], 1048576)
    filename = repository_root + "/" + b["path"]
    need(type(module) is types.ModuleType, "MODULE_TYPE")
    namespace = types.ModuleType.__getattribute__(module, "__dict__")
    need(all(type(key) is str for key in namespace), "MODULE_KEYS")
    need(type(namespace.get("__name__")) is str
         and type(namespace.get("__file__")) is str and namespace["__file__"] == filename,
         "MODULE_ORIGIN")
    need(type(callable_object) in (types.FunctionType, types.MethodType), "CALLABLE_TYPE")
    fn = callable_object.__func__ if type(callable_object) is types.MethodType else callable_object
    need(fn.__globals__ is namespace and type(fn.__module__) is str
         and fn.__module__ == namespace["__name__"]
         and fn.__code__.co_filename == filename and fn.__qualname__ == row["entrypoint"],
         "CALLABLE_ORIGIN")
    parts = row["entrypoint"].split(".")
    owner = None
    registered = namespace
    for part in parts[:-1]:
        owner = registered.get(part)
        need(type(owner) is type, "OWNER_CLASS")
        registered = type.__getattribute__(owner, "__dict__")
    target = registered.get(parts[-1])
    if row["callable_kind"] == "function":
        need(len(parts) == 1 and type(callable_object) is types.FunctionType
             and target is fn and expected_instance is None, "FUNCTION_REGISTRATION")
    elif row["callable_kind"] == "method":
        need(type(callable_object) is types.MethodType and owner is not None
             and type(target) is types.FunctionType and target is fn
             and type(callable_object.__self__) is owner
             and callable_object.__self__ is expected_instance, "INSTANCE_REGISTRATION")
    else:
        need(type(callable_object) is types.MethodType and owner is not None
             and type(target) is classmethod and target.__func__ is fn
             and callable_object.__self__ is owner and expected_instance is owner,
             "CLASS_REGISTRATION")
    try:
        compiled = compile(source_raw, filename, "exec", dont_inherit=True,
                           optimize=row["compile_optimize"])
    except (SyntaxError, ValueError, TypeError, RecursionError):
        raise BindingRefusal("SOURCE_COMPILE") from None
    safe_code(fn.__code__)
    matches = []
    pending = [compiled]
    count = 0
    while pending:
        code = pending.pop()
        count += 1
        need(count <= 4096, "CODE_BOUND")
        if code.co_qualname == row["entrypoint"]:
            matches.append(code)
        pending.extend(c for c in code.co_consts if type(c) is types.CodeType)
    need(len(matches) == 1 and matches[0] == fn.__code__, "CODE_MISMATCH")
    return {"schema_version": "lab-inert-callable-observation/v1",
            "selection_sha256": expected_selection_sha256,
            "source_inventory_sha256": expected_inventory_sha256,
            "registry_source_sha256": expected_registry_source_sha256,
            "source_cut": expected_source_cut, "transition_ref": row["transition_ref"],
            "producer_binding": dict(b), "entrypoint": row["entrypoint"],
            "observation": "selected-code-match", "producer_invocations": 0,
            "authority_effect": "none", "actual_instance_custody_verified": False}
