"""Trusted local Lab registry snapshot translation. No runtime or owner effects."""
from pathlib import Path
from ..exact import binding, bound, decode, encode, read, require, sha
from ..capture import bindings_in, capture

REGISTRY = "authority/definitions/registry.json"


def snapshot(request_raw, source_root, *, permit_retention=False):
    """Verify historical registry entries; preserve them as reported evidence only."""
    from ..integrity import verify
    verify()
    root = Path(source_root)
    request = decode(request_raw)
    from ..contracts import check
    check(request, "request")
    registry_raw = read(root / REGISTRY)
    registry = decode(registry_raw, source=True)
    inputs = {REGISTRY: registry_raw}
    for b in bindings_in(request):
        raw = bound(root, b)
        require(inputs.setdefault(b["path"], raw) == raw, "mixed-source-epochs")
    refs = []
    def collect(value):
        if isinstance(value, dict):
            if value.get("kind") == "external":refs.append(value)
            for key, child in value.items():
                if key not in ("bindings", "value_schema"):collect(child)
        elif isinstance(value, list):
            for child in value:collect(child)
    collect(request)
    entries, observations = [], []
    for path, raw in sorted(inputs.items()):
        selected = [e for e in registry["entries"] if e["path"] == path and e["sha256"] == sha(raw) and
                    registry["current_lookup"].get(e["definition_id"]) == e["definition_id"] + "@" + e["version"] and e.get("admission_decision_ref")]
        require(len(selected) <= 1, "ambiguous-registry-entry")
        reported = None;aliases = set()
        if selected:
            entry = selected[0];body = decode(raw, source=True)
            require(body.get("definition_id") == entry["definition_id"] and body.get("version") == entry["version"], "registry-body-identity-mismatch")
            for ref in refs:
                if ref["identity"] == entry["definition_id"] and ref["revision"] == entry["version"]:
                    require(ref["carrier_ref"] == registry["definition_artifact_type_ref"] and ref["selector"] == "" and ref["sha256"] == sha(encode(body)), "registry-reference-mismatch")
                    aliases.add(ref["input_id"])
            reported = "Historical Lab registry reports admitted-current; exact registry/body checked locally. No current host standing or permission."
            observations.append({"definition_id": entry["definition_id"], "version": entry["version"], "registry_binding": binding(registry_raw, REGISTRY),
                                 "definition_binding": binding(raw, path), "admission_decision_ref": entry["admission_decision_ref"], "authority_effect": "none"})
        require(len(aliases) <= 1, "ambiguous-source-alias")
        entries.append({"input_id": next(iter(aliases)) if aliases else path, "binding": binding(raw, path), "reported_standing": reported})
    catalog = {"schema_version": "define.source-catalog/v1", "entries": entries, "authority_effect": "none"}
    result, members = capture(request_raw, inputs, catalog_raw=encode(catalog), permit_retention=permit_retention)
    reference_observations = []
    for ref in refs:
        matched = any(o["definition_id"] == ref["identity"] and o["version"] == ref["revision"] for o in observations)
        reference_observations.append({"input_id": ref["input_id"], "identity": ref["identity"], "revision": ref["revision"],
                                       "registry_match": "historical-match" if matched else "not-established", "authority_effect": "none"})
    report = {"schema_version": "define.lab-snapshot-observation/v1", "registry_binding": binding(registry_raw, REGISTRY),
              "observations": observations, "reference_observations": reference_observations, "translation": "reported-historical-evidence-only", "native_v3_review_route": "not-qualified",
              "actual_owner_outcome": None, "authority_effect": "none"}
    return result, members, report
