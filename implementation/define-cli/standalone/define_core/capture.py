"""Capture explicit logical members without a repository, host, or filesystem."""
from collections.abc import Mapping
from datetime import datetime, timezone
from .exact import binding, bound, decode, encode, logical, member_paths, require
from .contracts import check

ENCODING_PATH = "define-encoding.json"
CATALOG_PATH = "define-source-catalog.json"
ENCODING = encode({"schema_version": "cal.define.encoding/v1", "new_records": "UTF-8 sorted compact JSON plus LF",
                   "source_bytes": "Original bounded bytes and original-file SHA-256", "authority_effect": "none"})


def bindings_in(value):
    if isinstance(value, dict):
        if set(value) == {"path", "sha256", "bytes", "digest_kind"}:
            yield value
        else:
            for key, child in value.items():
                # Task values and JSON Schema literals are data, not source links.
                if key not in ("bindings", "value_schema"):
                    yield from bindings_in(child)
    elif isinstance(value, list):
        for child in value:
            yield from bindings_in(child)


def capture(request_raw, inputs, *, catalog_raw=None, permit_retention=False, captured_at=None):
    """Return capture record and required exact input members; no IO or authority effects."""
    require(isinstance(inputs, Mapping) and all(isinstance(v, bytes) for v in inputs.values()), "logical-byte-members-required")
    require(type(permit_retention) is bool, "invalid-retention-assertion")
    require(isinstance(request_raw, bytes) and len(request_raw) <= 1048576, "request-budget")
    request = decode(request_raw)
    require(isinstance(request, dict), "invalid-request-document")
    require(request.get("schema_version") == "cal.define.prepare-request/v3", "unsupported-request-version", exit_code=4)
    check(request, "request")
    from .prepare import gap, unique
    selected = {}
    for b in bindings_in(request):
        require(b["path"] not in (ENCODING_PATH, CATALOG_PATH), "reserved-source-path")
        raw = bound(inputs, b)
        require(selected.setdefault(b["path"], raw) == raw, "mixed-source-epochs")
    if catalog_raw is None:
        catalog = {"schema_version": "define.source-catalog/v1", "entries": [
            {"input_id": path, "binding": binding(raw, path), "reported_standing": None}
            for path, raw in sorted(selected.items())], "authority_effect": "none"}
        catalog_raw = encode(catalog)
    else:
        require(isinstance(catalog_raw, bytes) and len(catalog_raw) <= 1048576, "catalog-budget")
        catalog = decode(catalog_raw)
    check(catalog, "catalog")
    unique(catalog["entries"], "input_id")
    paths = set()
    for entry in catalog["entries"]:
        b = entry["binding"];logical(b["path"])
        require(b["path"] not in paths and b["path"] not in (ENCODING_PATH, CATALOG_PATH), "duplicate-or-reserved-source-path")
        require(entry["input_id"] not in (ENCODING_PATH, CATALOG_PATH), "reserved-input-id")
        paths.add(b["path"])
        raw = bound(inputs, b)
        require(selected.setdefault(b["path"], raw) == raw, "mixed-source-epochs")
    require(paths == set(selected), "catalog-incomplete", "Catalog must identify every selected source exactly once")
    # Unselected supplied bytes are not silently retained.
    require(set(inputs) == set(selected), "unselected-input-member")
    member_paths({*selected, ENCODING_PATH, CATALOG_PATH})
    catalog_binding = binding(catalog_raw, CATALOG_PATH)
    rows = []
    for entry in catalog["entries"]:
        b = entry["binding"]
        rows.append({"input_id": entry["input_id"], "population": "external-evidence" if b in request["evidence_bindings"] else "local-supplement",
                     "binding": b, "encoding_contract_binding": binding(ENCODING, ENCODING_PATH), "selector": "",
                     "standing_observation": {"status": "local-reference", "basis_bindings": [catalog_binding],
                         "limitations": ["Exact file binding only. Catalog standing is source-reported and not authenticated."]},
                     "provenance_bindings": [], "permitted_uses": [request["intended_use"]],
                     "retention_posture": "permitted" if permit_retention else "unresolved"})
    require(len(rows) <= 240 and sum(map(len, selected.values())) <= 12 * 1024 * 1024, "capture-budget")
    result = {"schema_version": "cal.define.capture-bundle/v2", "capture_id": "capture:" + request["request_id"],
              "revision": request["request_revision"], "mode": "local-snapshot", "adapter_selection_binding": None,
              "intended_use": request["intended_use"], "source_cut": {"kind": "local-files", "binding": catalog_binding},
              "source_profile_binding": catalog_binding, "context_bindings": [], "ontology_view_bindings": [],
              "captured_at": captured_at if captured_at is not None else datetime.now(timezone.utc).isoformat(),
              "permission_observation_binding": None, "input_rows": rows,
              "capture_limits": {"max_bytes": 16 * 1024 * 1024, "max_items": 240},
              "gaps": [gap("local-snapshot", "Selected source snapshot; no authenticated standing, live permission or domain execution.", "prepare-owner-review")],
              "authority_effect": "none"}
    check(result, "capture")
    return result, {**selected, **({ENCODING_PATH: ENCODING} if rows else {}), CATALOG_PATH: catalog_raw}
