"""Explicit historical capture of selected original repository/local files."""
from datetime import datetime, timezone
from .exact import binding, bound, decode, encode, require
from .prepare import gap
from .contracts import check

ENCODING = encode({"schema_version": "cal.define.encoding/v1", "new_records": "UTF-8 sorted compact JSON plus LF",
                   "source_bytes": "Original bounded bytes; no duplicate keys; explicit original-file digest", "authority_effect": "none"})
ENCODING_PATH = "define-v2-encoding.json"


def bindings_in(value):
    if isinstance(value, dict):
        if set(value) == {"path", "sha256", "bytes", "digest_kind"}:
            yield value
        else:
            for child in value.values():
                yield from bindings_in(child)
    elif isinstance(value, list):
        for child in value:
            yield from bindings_in(child)


def snapshot(request, root, *, permit_retention=False):
    check(request, "request")
    require(request["adapter_selection_binding"] is None, "snapshot-adapter-claim", "Historical repository capture has no live adapter selection")
    registry_path = "authority/definitions/registry.json"
    from pathlib import Path
    from .exact import read
    registry_raw = read(Path(root) / registry_path)
    registry = decode(registry_raw, source=True)
    registry_binding = binding(registry_raw, registry_path)
    buffers = {registry_path: registry_raw, ENCODING_PATH: ENCODING}
    by_path = {registry_path: registry_binding}
    for b in bindings_in(request):
        raw = bound(root, b)
        require(b["path"] != ENCODING_PATH, "reserved-source-path")
        require(b["path"] not in buffers or buffers[b["path"]] == raw, "mixed-source-epochs")
        buffers[b["path"]], by_path[b["path"]] = raw, b
    refs = []
    def references(value):
        if isinstance(value, dict):
            if value.get("kind") == "external":
                refs.append(value)
            for child in value.values(): references(child)
        elif isinstance(value, list):
            for child in value: references(child)
    references(request)
    rows = []
    for path, b in sorted(by_path.items()):
        entry = next((e for e in registry["entries"] if e["path"] == path and e["sha256"] == b["sha256"] and
                      registry["current_lookup"].get(e["definition_id"]) == e["definition_id"] + "@" + e["version"] and e.get("admission_decision_ref")), None)
        reference_ids = {r["input_id"] for r in refs if entry and r["identity"] == entry["definition_id"] and r["revision"] == entry["version"]}
        require(len(reference_ids) <= 1, "ambiguous-input-id")
        input_id = next(iter(reference_ids)) if reference_ids else path
        is_evidence = any(e["path"] == path for e in request["evidence_bindings"])
        rows.append({"input_id": input_id, "population": "host-member" if entry else "external-evidence" if is_evidence else "local-supplement",
                     "binding": b, "encoding_contract_binding": binding(ENCODING, ENCODING_PATH), "selector": "",
                     "standing_observation": {"status": "admitted-current" if entry else "unverified-candidate", "basis_bindings": [registry_binding] if entry else [],
                                              "limitations": ["Repository registry observation only; no live runtime permission or current-use lease."]},
                     "provenance_bindings": [], "permitted_uses": [request["intended_use"]],
                     "retention_posture": "permitted" if permit_retention else "unresolved"})
    capture = {"schema_version": "cal.define.capture-bundle/v1", "capture_id": "capture:" + request["request_id"], "revision": request["request_revision"],
               "mode": "historical-snapshot", "adapter_selection_binding": None, "intended_use": request["intended_use"],
               "source_cut": {"kind": "repository-registry", "binding": registry_binding}, "source_profile_binding": registry_binding,
               "context_bindings": [], "ontology_view_bindings": [], "captured_at": datetime.now(timezone.utc).isoformat(),
               "permission_observation_binding": None, "input_rows": rows, "capture_limits": {"max_bytes": 67108864, "max_items": 256},
               "gaps": [gap("historical-capture", "Selected repository capture, not an authenticated host delivery.", "prepare-owner-review")], "authority_effect": "none"}
    check(capture, "capture")
    require(sum(map(len, buffers.values())) <= 64 * 1024 * 1024 and len(rows) <= 256, "capture-budget")
    return capture, buffers
