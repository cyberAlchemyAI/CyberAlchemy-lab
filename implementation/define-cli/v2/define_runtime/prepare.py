"""Pure Pack construction from exact captured input; no model or formula execution."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator
from .contracts import NAMED_USES, check, value_schema
from .exact import binding, bound, decode, encode, pointer, read, require, sha

CEILING = "Candidate preparation and exact binding checks only; no semantic acceptance, domain execution, permission or admission."


def local_ref(pack_id, revision, kind, index, entry):
    names = {"working-meaning": ("working_meanings", "meaning_id"), "application": ("applications", "application_id"), "assessment": ("assessments", "assessment_id")}
    collection, identity = names[kind]
    return {"kind": "embedded", "pack_id": pack_id, "pack_revision": revision,
            "entry_kind": kind, "entry_id": entry[identity], "revision": entry["revision"],
            "selector": f"/{collection}/{index}", "sha256": sha(encode(entry))}


def unique(rows, field):
    values = [r[field] for r in rows]
    require(len(values) == len(set(values)), "duplicate-identity", "Duplicate " + field)


def gap(identity, reason, use="inspect-preparation", continuation="Resolve through the selected owner/source route."):
    return {"gap_id": identity, "reason": reason, "affected_use": use, "continuation": continuation}


def validate_capture(capture, root):
    check(capture, "capture")
    require(capture["mode"] == "historical-snapshot", "live-capture-requires-host", "Live capture must be obtained and verified by the selected host adapter", 3)
    require(capture["permission_observation_binding"] is None and "live_observation_binding" not in capture,
            "snapshot-live-claim", "Historical snapshot cannot manufacture a live lease")
    unique(capture["input_rows"], "input_id")
    raw_by_path = {}
    for row in capture["input_rows"]:
        require(capture["intended_use"] in row["permitted_uses"], "source-use-not-permitted", exit_code=3)
        for b in [row["binding"], row["encoding_contract_binding"], *row["standing_observation"]["basis_bindings"], *row["provenance_bindings"]]:
            raw = bound(root, b)
            previous = raw_by_path.setdefault(b["path"], raw)
            require(previous == raw, "mixed-source-epochs")
    for b in [capture["source_cut"]["binding"], capture["source_profile_binding"], *capture["context_bindings"], *capture["ontology_view_bindings"]]:
        raw_by_path[b["path"]] = bound(root, b)
    total = sum(map(len, raw_by_path.values()))
    require(total <= min(capture["capture_limits"]["max_bytes"], 64 * 1024 * 1024), "snapshot-budget")
    require(len(capture["input_rows"]) <= min(256, capture["capture_limits"]["max_items"]), "snapshot-budget")
    return raw_by_path


def resolve_reference(ref, capture, raw_by_path, pack):
    if ref["kind"] == "embedded":
        require(ref["pack_id"] == pack["pack_id"] and ref["pack_revision"] == pack["revision"], "wrong-owning-pack")
        entry = pointer(pack, ref["selector"])
        key = {"working-meaning": "meaning_id", "application": "application_id", "assessment": "assessment_id"}[ref["entry_kind"]]
        collection = {"working-meaning": "working_meanings", "application": "applications", "assessment": "assessments"}[ref["entry_kind"]]
        require(ref["selector"].startswith("/" + collection + "/") and entry.get(key) == ref["entry_id"] and entry["revision"] == ref["revision"] and sha(encode(entry)) == ref["sha256"], "embedded-reference-mismatch")
        return entry, "local-proposed"
    rows = [r for r in capture["input_rows"] if r["input_id"] == ref["input_id"]]
    require(len(rows) == 1, "unresolved-reference")
    row = rows[0]
    entry = pointer(decode(raw_by_path[row["binding"]["path"]], source=True), ref["selector"])
    # External selector digest uses the selected canonical-entry encoding; original file digest remains separate.
    require(sha(encode(entry)) == ref["sha256"], "selected-entry-mismatch")
    identity = entry.get("definition_id", entry.get("node_id"))
    revision = entry.get("version")
    require(identity == ref["identity"] and revision == ref["revision"], "external-identity-mismatch")
    status = row["standing_observation"]["status"]
    if status == "admitted-current":
        require(row["population"] == "host-member", "standing-laundering")
        require(capture["source_cut"]["kind"] == "repository-registry", "unsupported-standing-basis", exit_code=4)
        registry = decode(raw_by_path[capture["source_cut"]["binding"]["path"]], source=True)
        version = ref["identity"] + "@" + ref["revision"]
        require(registry["current_lookup"].get(ref["identity"]) == version, "historical-meaning")
        matches = [e for e in registry["entries"] if e["definition_id"] == ref["identity"] and e["version"] == ref["revision"]]
        require(len(matches) == 1 and matches[0]["sha256"] == row["binding"]["sha256"] and matches[0]["path"] == row["binding"]["path"] and matches[0].get("admission_decision_ref"), "standing-basis-mismatch")
        require(ref["carrier_ref"] == registry["definition_artifact_type_ref"] and ref["selector"] == "", "carrier-mismatch")
    else:
        require(row["population"] != "host-member" or status != "admitted-current", "standing-laundering")
    return entry, status


def prepare(request_raw, capture_raw, root):
    require(len(request_raw) <= 1024 * 1024 and len(capture_raw) <= 1024 * 1024, "request-budget")
    request, capture = decode(request_raw), decode(capture_raw)
    check(request, "request")
    raw_by_path = validate_capture(capture, root)
    require(request["adapter_selection_binding"] == capture["adapter_selection_binding"], "adapter-selection-mismatch")
    require(request["intended_use"] == capture["intended_use"], "captured-use-mismatch")
    for b in [*request["source_bindings"], *request["evidence_bindings"]]:
        require(raw_by_path.get(b["path"]) == bound(root, b), "uncaptured-input", "Request input is not in the captured closure")
    for k in ["field_supplement_binding", "language_evidence_binding"]:
        if k in request:
            require(raw_by_path.get(request[k]["path"]) == bound(root, request[k]), "uncaptured-input")
    from .capture import bindings_in
    for b in bindings_in(request):
        require(raw_by_path.get(b["path"]) == bound(root, b), "uncaptured-input", "Every selected lineage/evidence binding must be captured exactly")
    unique(request["required_concepts"], "concept_id"); unique(request["handling"], "concept_id")
    require({r["concept_id"] for r in request["required_concepts"]} == {r["concept_id"] for r in request["handling"]}, "incomplete-handling")
    pack = {"schema_version": "cal.define.pack/v2", "pack_id": request["request_id"], "revision": request["request_revision"],
            "status": "candidate", "authority_effect": "none", "scope": {k: request[k] for k in ["goal", "originating_intent", "context", "consumer", "intended_use"]},
            "capture_binding": binding(capture_raw, "capture.json"), "required_concepts": copy.deepcopy(request["required_concepts"]),
            "handling": copy.deepcopy(request["handling"]), "working_meanings": [], "parameter_contracts": [],
            "applications": copy.deepcopy(request["applications"]), "assessments": copy.deepcopy(request["assessments"]),
            "source_bindings": copy.deepcopy(request["source_bindings"]), "evidence_bindings": copy.deepcopy(request["evidence_bindings"]),
            "relationship_records": [], "owner_routes": [], "gaps": copy.deepcopy(capture["gaps"]),
            "materialization_selection": copy.deepcopy(request["materialization_selection"]), "validation_scope": copy.deepcopy(request["validation_scope"]),
            "lineage": {"request_binding": binding(request_raw, "request.json"), "predecessor_package_binding": request.get("predecessor_package_binding")}, "claim_ceiling": CEILING}
    pack["scope"]["authority_boundary"] = "Local candidate preparation; actual effects require their independent native routes."
    for h in request["handling"]:
        if h["disposition"] == "propose" or (h["disposition"] == "specialize" and h["payload"]["mode"] == "meaning-change"):
            pack["working_meanings"].append(copy.deepcopy(h["payload"]["working_meaning"]))
        if h["disposition"] == "open":
            p = h["payload"];pack["gaps"].append(gap("concept:" + h["concept_id"], p["reason"], p["affected_use"], p["continuation"]))
    unique(pack["working_meanings"], "meaning_id")
    for index, meaning in enumerate(pack["working_meanings"]):
        unique(meaning["parameters"], "name")
        for parameter in meaning["parameters"]:
            value_schema(parameter["value_schema"])
        pack["parameter_contracts"].append({"contract_id": "parameters:" + meaning["meaning_id"] + "@" + str(meaning["revision"]),
            "meaning_ref": local_ref(pack["pack_id"], pack["revision"], "working-meaning", index, meaning),
            "parameters": copy.deepcopy(meaning["parameters"]), "lineage": copy.deepcopy(meaning["lineage"]), "authority_effect": "none"})
    for h in request["handling"]:
        if h["disposition"] == "reuse":
            _, status = resolve_reference(h["payload"]["meaning_ref"], capture, raw_by_path, pack)
            require(status == "admitted-current", "reuse-not-admitted-current")
        elif h["disposition"] == "specialize":
            resolve_reference(h["payload"]["parent_ref"], capture, raw_by_path, pack)
            if h["payload"]["mode"] == "application":
                matches = [a for a in pack["applications"] if a["application_id"] == h["payload"]["application_id"]]
                require(len(matches) == 1 and matches[0]["meaning_ref"] == h["payload"]["parent_ref"], "specialization-application-mismatch")
    unique(pack["applications"], "application_id");unique(pack["assessments"], "assessment_id")
    app_results = []
    for application in pack["applications"]:
        meaning, standing = resolve_reference(application["meaning_ref"], capture, raw_by_path, pack)
        require("parameters" in meaning, "missing-parameter-declarations", "Selected meaning has no supported explicit parameter declaration", 4)
        contracts = [c for c in pack["parameter_contracts"] if c["contract_id"] == application["parameter_contract_ref"] and c["meaning_ref"] == application["meaning_ref"]]
        require(len(contracts) == 1, "parameter-contract-mismatch")
        params = {p["name"]: p for p in contracts[0]["parameters"]}
        require(application["bindings"].keys() <= params.keys(), "undeclared-parameter")
        missing = {name for name, p in params.items() if p["required"]} - application["bindings"].keys()
        gap_names = {g["gap_id"] for g in application["binding_gaps"]}
        require(all("parameter:" + name in gap_names for name in missing), "unreported-binding-gap")
        origins = application["value_provenance"];unique(origins, "parameter")
        require({o["parameter"] for o in origins} == application["bindings"].keys(), "missing-value-provenance")
        for name, value in application["bindings"].items():
            require(Draft202012Validator(params[name]["value_schema"]).is_valid(value), "parameter-value-invalid", "Value does not satisfy declared parameter " + name)
            origin = next(o for o in origins if o["parameter"] == name)
            rows = [r for r in capture["input_rows"] if r["input_id"] == origin["input_id"]]
            require(len(rows) == 1, "unresolved-value-source")
            source_value = pointer(decode(raw_by_path[rows[0]["binding"]["path"]], source=True), origin["selector"])
            require(source_value == value and sha(encode(source_value)) == origin["sha256"], "value-provenance-mismatch")
        fully_bound = not missing and not application["binding_gaps"] and application["applicability"] == "established-for-candidate-examination"
        app_results.append({"application_id": application["application_id"], "fully_bound": fully_bound, "meaning_standing": standing,
                            "domain_assessment_executed": False})
    for assessment in pack["assessments"]:
        require(assessment["application_ref"]["entry_kind"] == "application", "assessment-subject-kind")
        resolve_reference(assessment["application_ref"], capture, raw_by_path, pack)
        for b in [*assessment["input_bindings"], *assessment["evidence_bindings"]]:
            require(raw_by_path.get(b["path"]) == bound(root, b), "uncaptured-assessment-input")
        for ref in assessment["method_profile_refs"]:
            resolve_reference(ref, capture, raw_by_path, pack)
        producer = assessment["producer"]
        if producer["execution_receipt"] is not None:
            b = producer["execution_receipt"]
            require(raw_by_path.get(b["path"]) == bound(root, b), "uncaptured-execution-receipt")
        # A byte-matching receipt alone cannot qualify a Method/producer. A native qualification adapter is required.
        require(producer["execution_posture"] != "verified-external", "execution-qualification-unavailable", exit_code=3)
        require(assessment["validation_posture"] in ("unverified-reported", "not-evaluable"), "assessment-standing-promotion")
        if assessment["reported_result"] == "NOT_EVALUABLE":
            require(bool(assessment["unevaluable_reason"]), "missing-unevaluable-reason")
    predecessor = request.get("predecessor_package_binding")
    if predecessor:
        old = decode(bound(root, predecessor));check(old, "pack")
        require(old["pack_id"] == pack["pack_id"] and old["revision"] < pack["revision"], "invalid-successor-lineage")
    elif pack["revision"] != 1:
        require(False, "missing-predecessor", "A later revision requires its exact predecessor binding")
    if capture["mode"] == "historical-snapshot":
        pack["gaps"].append(gap("current-host", "Historical capture does not establish current host permission or freshness.", "prepare-owner-review"))
    if pack["assessments"]:
        pack["gaps"].append(gap("assessment-qualification", "Imported reported results lack qualified actual execution/producer evidence.", "consume-assessment"))
    pack["gaps"].append(gap("actual-governing-route", "Only the host may establish current permission, owner outcomes and applied effects.", "governing-application"))
    statuses = {"inspect-preparation": "ready", "apply-parameters": "ready" if app_results and all(a["fully_bound"] for a in app_results) else "not-evaluable",
                "consume-assessment": "blocked" if pack["assessments"] else "not-evaluable",
                "materialize-definition": "blocked" if pack["materialization_selection"] else "not-evaluable",
                "prepare-owner-review": "blocked", "governing-application": "blocked"}
    if pack["applications"] and (not all(a["fully_bound"] for a in app_results) or any(g["affected_use"] == "apply-parameters" for g in pack["gaps"])):
        statuses["apply-parameters"] = "blocked"
    pack["readiness"] = {u: {"outcome": statuses[u], "obligations": [g["gap_id"] for g in pack["gaps"] if g["affected_use"] == u], "claim_ceiling": CEILING} for u in NAMED_USES}
    check(pack, "pack")
    report = {"schema_version": "cal.define.preparation-report/v2", "authority_effect": "none", "structural_validity": "valid",
              "capture_mode": capture["mode"], "application_checks": app_results, "readiness": pack["readiness"],
              "assessment_execution_count": 0, "actual_owner_outcome": None, "claim_ceiling": CEILING}
    members = {"pack.json": encode(pack), "capture.json": capture_raw, "request.json": request_raw, "report.json": encode(report)}
    for path, raw in raw_by_path.items():
        require(path not in members, "reserved-member-path")
        members["inputs/" + path] = raw
    return pack, report, members
