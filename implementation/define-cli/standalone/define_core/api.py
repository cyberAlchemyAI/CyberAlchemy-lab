"""Versioned stateless public API; caller-provided bytes only, no path IO."""
import base64
import binascii
from . import VERSION
from .contracts import SCHEMAS, check
from .exact import Refusal, decode, encode, logical, member_paths, require, sha, shape, tree

API_VERSION = "define.api/v1"
MAX_FRAME = 32 * 1024 * 1024
MAX_TOTAL = 16 * 1024 * 1024
MAX_MEMBER = 16 * 1024 * 1024
OPERATIONS = ("capabilities", "schema", "capture", "prepare", "inspect", "reconstruct", "materialize", "observe-use")


def byte_members(value):
    require(isinstance(value, dict) and len(value) <= 256, "member-budget")
    require(all(isinstance(s, str) for s in value.values()), "invalid-base64-member")
    require(sum(len(s) for s in value.values()) <= 4 * ((MAX_TOTAL + 2) // 3) + 1024, "encoded-members-budget")
    member_paths(value)
    output, total = {}, 0
    for path, text in value.items():
        logical(path)
        require(len(text) <= 4 * ((MAX_MEMBER + 2) // 3), "member-budget")
        try:
            raw = base64.b64decode(text, validate=True)
        except (ValueError, binascii.Error):
            raise Refusal("invalid-base64-member", "Expected canonical standard base64") from None
        require(base64.b64encode(raw).decode("ascii") == text, "noncanonical-base64")
        total += len(raw)
        require(len(raw) <= MAX_MEMBER and total <= MAX_TOTAL, "members-budget")
        output[path] = raw
    return output


def encoded_members(value):
    require(len(value) <= 256 and sum(map(len, value.values())) <= MAX_TOTAL, "members-budget")
    return {path: base64.b64encode(raw).decode("ascii") for path, raw in sorted(value.items())}


def utf8(params, key, maximum=1048576):
    require(isinstance(params.get(key), str), "invalid-utf8-field")
    try:raw = params[key].encode("utf-8", errors="strict")
    except UnicodeError:raise Refusal("invalid-unicode", "Expected exact UTF-8 text") from None
    require(len(raw) <= maximum, "input-budget")
    return raw


def verified_package(params):
    from .package import verify_package
    members = byte_members(params["package_members"])
    require("manifest.json" in members, "missing-manifest")
    manifest_raw = members["manifest.json"]
    m, required, buffers = verify_package(manifest_raw, lambda _, row: members[row["path"]], all_members=True)
    require(set(members) == {"manifest.json", *(row["path"] for row in m["members"].values())}, "unselected-package-member")
    return manifest_raw, m, required, buffers


def dispatch(operation, params):
    require(operation in OPERATIONS, "unsupported-operation", exit_code=4)
    if operation == "capabilities":
        shape(params, ())
        return {"version": VERSION, "api_version": API_VERSION, "operations": list(OPERATIONS), "schemas": [*SCHEMAS, "definition-carrier"],
                "limits": {"frame_bytes": MAX_FRAME, "total_member_bytes": MAX_TOTAL, "member_count": 256},
                "source_standing": "local-reference; reported standing is not authenticated", "domain_execution": False,
                "lab_required": False, "network_access": False, "caller_filesystem_access": False, "bundled_resource_reads": True,
                "input_authorship": "Caller supplies authored meanings and evidence; no built-in model inference.",
                "compatibility": "V3 Packs require an explicit qualified mapping before native Lab review.",
                "authority_effect": "none"}
    if operation == "schema":
        shape(params, ("kind",))
        require(isinstance(params["kind"], str) and params["kind"] in [*SCHEMAS, "definition-carrier"], "unsupported-schema", exit_code=4)
        if params["kind"] == "definition-carrier":
            from .exact import binding
            from .integrity import resource_bytes
            schema_raw = resource_bytes("schema.json");generator_raw = resource_bytes("generator.py")
            return {"schema": decode(schema_raw), "schema_binding": binding(schema_raw, "resources/schema.json"),
                    "generator_binding": binding(generator_raw, "resources/generator.py"), "posture": "candidate-carrier-only"}
        return {"schema": {"$schema": "https://json-schema.org/draft/2020-12/schema", **SCHEMAS[params["kind"]]}}
    if operation == "capture":
        shape(params, ("request_utf8", "inputs"), ("catalog_utf8", "permit_retention", "captured_at"))
        from .capture import capture
        record, members = capture(utf8(params, "request_utf8"), byte_members(params["inputs"]),
            catalog_raw=utf8(params, "catalog_utf8") if "catalog_utf8" in params else None,
            permit_retention=params.get("permit_retention", False), captured_at=params.get("captured_at"))
        return {"capture": record, "capture_utf8": encode(record).decode("utf-8"), "inputs": encoded_members(members)}
    if operation == "prepare":
        shape(params, ("request_utf8", "capture_utf8", "inputs"))
        from .prepare import prepare
        from .package import manifest_for, verify_package
        pack, report, members = prepare(utf8(params, "request_utf8"), utf8(params, "capture_utf8"), byte_members(params["inputs"]))
        manifest = manifest_for(pack, members);manifest_raw = encode(manifest)
        verify_package(manifest_raw, lambda _, row: members[row["path"]], all_members=True)
        return {"pack": pack, "report": report, "root_sha256": sha(manifest_raw), "pack_sha256": sha(members["pack.json"]),
                "package_members": encoded_members({**members, "manifest.json": manifest_raw}), "readiness": report["readiness"]}
    if operation in ("inspect", "reconstruct", "materialize", "observe-use"):
        shape(params, ("package_members", "requested_use", "consumer") if operation == "observe-use" else ("package_members",),
              ("current_source_base64",) if operation == "observe-use" else ())
        raw, manifest, required, buffers = verified_package(params)
        if operation == "inspect":
            return {"root_sha256": sha(raw), "pack_sha256": manifest["pack_binding"]["sha256"],
                    "required_members_verified": len(required), "frozen_integrity": "verified", "current_permission": "not-established"}
        if operation == "reconstruct":
            return {"root_sha256": sha(raw), "package_members": encoded_members({**buffers, "manifest.json": raw}),
                    "posture": "exact-frozen-reconstruction"}
        if operation == "materialize":
            from .materialize import materialize_members
            report, output = materialize_members(buffers)
            return {"report": report, "members": encoded_members(output)}
        from .observe import observe
        require(all(isinstance(params[k], str) and 0 < len(params[k]) <= 4096 for k in ("requested_use", "consumer")), "invalid-use-observation")
        current = byte_members({"source.json": params["current_source_base64"]})["source.json"] if "current_source_base64" in params else None
        return observe(buffers, params["requested_use"], params["consumer"], current)
    raise Refusal("unsupported-operation", "Unsupported operation", 4)


def invoke(document):
    """Public shared dispatcher. All failures have a stable, non-sensitive envelope."""
    identity, operation = None, None
    try:
        from .integrity import verify
        verify()
        tree(document)
        shape(document, ("api_version", "id", "operation", "params"))
        require(isinstance(document["id"], str) and 0 < len(document["id"]) <= 128, "invalid-correlation-id")
        # Correlation IDs are caller-supplied; never echo unvalidated source objects.
        identity = document["id"]
        require(document["api_version"] == API_VERSION, "unsupported-api-version", exit_code=4)
        require(isinstance(document["operation"], str) and document["operation"] in OPERATIONS, "unsupported-operation", exit_code=4)
        operation = document["operation"]
        require(isinstance(document["params"], dict), "invalid-params")
        require(len(encode(document)) <= MAX_FRAME, "frame-budget")
        check(document, "api-request")
        data = dispatch(operation, document["params"])
        outcome = data.get("outcome", "prepared-with-gaps" if operation == "prepare" and data["pack"]["gaps"] else "prepared")
        return {"api_version": API_VERSION, "id": identity, "operation": operation, "outcome": outcome,
                "diagnostics": [], "data": data, "authority_effect": "none"}
    except Exception as exc:
        known = isinstance(exc, Refusal)
        code = exc.code if known else "invalid-input-or-unavailable-source"
        outcome = "unsupported" if known and exc.exit_code == 4 else "blocked" if known and exc.exit_code == 3 else "invalid-input"
        return {"api_version": API_VERSION, "id": identity, "operation": operation, "outcome": outcome,
                "diagnostics": [{"code": code, "message": "Operation refused; input values withheld."}], "data": None, "authority_effect": "none"}
