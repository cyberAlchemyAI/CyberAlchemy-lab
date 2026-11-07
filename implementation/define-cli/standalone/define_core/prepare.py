"""Pure Pack construction from exact captured input; no model or formula execution."""
from __future__ import annotations

from collections.abc import Mapping
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
    require(capture["mode"] == "local-snapshot", "unsupported-capture-mode", "Portable preparation accepts exact local snapshots only", 4)
    require(capture["permission_observation_binding"] is None and "live_observation_binding" not in capture,
            "snapshot-live-claim", "Historical snapshot cannot manufacture a live lease")
    unique(capture["input_rows"], "input_id")
    paths = [r["binding"]["path"] for r in capture["input_rows"]]
    require(len(paths) == len(set(paths)), "duplicate-source-path")
    raw_by_path = {}
    for row in capture["input_rows"]:
        require(row["selector"] == "", "unsupported-input-selector", "Catalog rows bind whole files; meaning references carry selectors", 4)
        require(capture["intended_use"] in row["permitted_uses"], "source-use-not-permitted", exit_code=3)
        require(row["retention_posture"] != "forbidden", "retention-forbidden", exit_code=3)
        for b in [row["binding"], row["encoding_contract_binding"], *row["standing_observation"]["basis_bindings"], *row["provenance_bindings"]]:
            raw = bound(root, b)
            previous = raw_by_path.setdefault(b["path"], raw)
            require(previous == raw, "mixed-source-epochs")
    for b in [capture["source_cut"]["binding"], capture["source_profile_binding"], *capture["context_bindings"], *capture["ontology_view_bindings"]]:
        raw = bound(root, b)
        require(raw_by_path.setdefault(b["path"], raw) == raw, "mixed-source-epochs")
    total = sum(map(len, raw_by_path.values()))
    require(total <= min(capture["capture_limits"]["max_bytes"], 64 * 1024 * 1024), "snapshot-budget")
    require(len(capture["input_rows"]) <= min(256, capture["capture_limits"]["max_items"]), "snapshot-budget")
    from .capture import CATALOG_PATH, ENCODING_PATH, ENCODING
    require(capture["source_cut"]["binding"] == capture["source_profile_binding"]
            and capture["source_profile_binding"]["path"] == CATALOG_PATH, "invalid-local-source-profile")
    catalog = decode(raw_by_path[CATALOG_PATH]);check(catalog, "catalog")
    unique(catalog["entries"], "input_id")
    require(len(catalog["entries"]) == len(capture["input_rows"]), "catalog-capture-mismatch")
    by_id = {r["input_id"]: r for r in capture["input_rows"]}
    for entry in catalog["entries"]:
        row = by_id.get(entry["input_id"])
        require(row is not None and row["binding"] == entry["binding"], "catalog-capture-mismatch")
        require(row["standing_observation"]["basis_bindings"] == [capture["source_profile_binding"]], "standing-basis-mismatch")
        require(row["encoding_contract_binding"]["path"] == ENCODING_PATH and raw_by_path[ENCODING_PATH] == ENCODING, "unsupported-encoding-contract", exit_code=4)
    # Rc1 empty snapshots supplied an unreferenced standard encoding record.
    # Preserve that exact control member rather than silently dropping caller bytes.
    if ENCODING_PATH in root:
        require(root[ENCODING_PATH] == ENCODING, "unsupported-encoding-contract", exit_code=4)
        raw_by_path[ENCODING_PATH] = root[ENCODING_PATH]
    require(set(root) == set(raw_by_path), "unselected-captured-input", "Every supplied member must belong to the capture closure")
    return raw_by_path


def resolve_reference(ref, capture, raw_by_path, pack):
    if ref["kind"] == "embedded":
        require(ref["pack_id"] == pack["pack_id"] and ref["pack_revision"] == pack["revision"], "wrong-owning-pack")
        entry = pointer(pack, ref["selector"])
        key = {"working-meaning": "meaning_id", "application": "application_id", "assessment": "assessment_id"}[ref["entry_kind"]]
        collection = {"working-meaning": "working_meanings", "application": "applications", "assessment": "assessments"}[ref["entry_kind"]]
        require(isinstance(entry, dict), "invalid-embedded-entry")
        require(len(ref["selector"].split("/")) == 3 and ref["selector"].startswith("/" + collection + "/") and entry.get(key) == ref["entry_id"] and entry["revision"] == ref["revision"] and sha(encode(entry)) == ref["sha256"], "embedded-reference-mismatch")
        return entry, "local-proposed"
    rows = [r for r in capture["input_rows"] if r["input_id"] == ref["input_id"]]
    require(len(rows) == 1, "unresolved-reference")
    row = rows[0]
    entry = pointer(decode(raw_by_path[row["binding"]["path"]], source=True), ref["selector"])
    require(isinstance(entry, dict), "invalid-meaning-carrier", "Selected meaning must be a JSON object")
    # External selector digest uses the selected canonical-entry encoding; original file digest remains separate.
    require(sha(encode(entry)) == ref["sha256"], "selected-entry-mismatch")
    identity = entry.get("definition_id", entry.get("node_id", entry.get("id")))
    revision = entry.get("version", entry.get("revision"))
    require(identity == ref["identity"] and revision == ref["revision"], "external-identity-mismatch")
    status = row["standing_observation"]["status"]
    require(status == "local-reference" and row["population"] != "host-member", "standing-promotion", exit_code=3)
    return entry, status


def prepare(request_raw, capture_raw, root):
    require(isinstance(root, Mapping) and all(isinstance(v, bytes) for v in root.values()), "logical-byte-members-required")
    require(len(request_raw) <= 1024 * 1024 and len(capture_raw) <= 1024 * 1024, "request-budget")
    request, capture = decode(request_raw), decode(capture_raw)
    require(isinstance(request, dict), "invalid-request-document")
    require(request.get("schema_version") == "cal.define.prepare-request/v3", "unsupported-request-version", exit_code=4)
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
    pack = {"schema_version": "cal.define.pack/v3", "pack_id": request["request_id"], "revision": request["request_revision"],
            "status": "candidate", "authority_effect": "none", "scope": {k: request[k] for k in ["goal", "originating_intent", "context", "consumer", "intended_use"]},
            "capture_binding": binding(capture_raw, "capture.json"), "required_concepts": copy.deepcopy(request["required_concepts"]),
            "handling": copy.deepcopy(request["handling"]), "working_meanings": [], "parameter_contracts": [],
            "applications": copy.deepcopy(request["applications"]), "assessments": copy.deepcopy(request["assessments"]),
            "source_bindings": copy.deepcopy(request["source_bindings"]), "evidence_bindings": copy.deepcopy(request["evidence_bindings"]),
            "relationship_records": [], "owner_routes": [], "gaps": copy.deepcopy(capture["gaps"]),
            "materialization_selection": copy.deepcopy(request["materialization_selection"]), "validation_scope": copy.deepcopy(request["validation_scope"]),
            "lineage": {"request_binding": binding(request_raw, "request.json"), "predecessor_package_binding": request.get("predecessor_package_binding")}, "claim_ceiling": CEILING}
    for row in capture["input_rows"]:
        if row["retention_posture"] == "unresolved":
            pack["gaps"].append(gap("retention:" + row["input_id"], "Retention rights are unresolved for this exact source; local preparation does not establish external export permission.", "prepare-owner-review"))
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
            require(status == "local-reference", "unsupported-source-standing")
            pack["gaps"].append(gap("source-standing:" + h["concept_id"], "Exact source identity and bytes are checked; reported standing is not authenticated or admitted by Define.", "governing-application"))
        elif h["disposition"] == "specialize":
            resolve_reference(h["payload"]["parent_ref"], capture, raw_by_path, pack)
            if h["payload"]["mode"] == "application":
                matches = [a for a in pack["applications"] if a["application_id"] == h["payload"]["application_id"]]
                require(len(matches) == 1 and matches[0]["meaning_ref"] == h["payload"]["parent_ref"], "specialization-application-mismatch")
    unique(pack["applications"], "application_id");unique(pack["assessments"], "assessment_id")
    # Explicit external parameter declarations produce mechanical contracts only.
    # No schema or parameter semantics is inferred from prose or a carrier label.
    from .contracts import PARAMETER
    for application in pack["applications"]:
        ref = application["meaning_ref"]
        require(application["consumer"] == request["consumer"] and application["intended_use"] == request["intended_use"], "application-use-mismatch")
        if ref["kind"] != "external":
            continue
        meaning, _ = resolve_reference(ref, capture, raw_by_path, pack)
        require("parameters" in meaning and isinstance(meaning["parameters"], list) and len(meaning["parameters"]) <= 24,
                "missing-parameter-declarations", exit_code=4)
        for parameter in meaning["parameters"]:
            require(Draft202012Validator(PARAMETER).is_valid(parameter), "invalid-parameter-declaration")
            value_schema(parameter["value_schema"])
        unique(meaning["parameters"], "name")
        contract_id = "parameters:" + ref["identity"] + "@" + ref["revision"]
        row = next(r for r in capture["input_rows"] if r["input_id"] == ref["input_id"])
        contract = {"contract_id": contract_id, "meaning_ref": copy.deepcopy(ref), "parameters": copy.deepcopy(meaning["parameters"]),
                    "lineage": [row["binding"]], "authority_effect": "none"}
        existing = [c for c in pack["parameter_contracts"] if c["contract_id"] == contract_id]
        require(not existing or existing == [contract], "ambiguous-parameter-contract")
        if not existing:pack["parameter_contracts"].append(contract)
    unique(pack["parameter_contracts"], "contract_id")
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
        else:
            require(assessment["unevaluable_reason"] is None, "contradictory-assessment-reason")
    for selection in pack["materialization_selection"]:
        require(selection["meaning_ref"]["entry_kind"] == "working-meaning", "materialization-subject-kind")
        resolve_reference(selection["meaning_ref"], capture, raw_by_path, pack)
        if selection["parent_ref"] is not None:
            resolve_reference(selection["parent_ref"], capture, raw_by_path, pack)
    predecessor = request.get("predecessor_package_binding")
    if predecessor:
        old = decode(bound(root, predecessor));check(old, "pack")
        require(old["pack_id"] == pack["pack_id"] and old["revision"] < pack["revision"], "invalid-successor-lineage")
    elif pack["revision"] != 1:
        require(False, "missing-predecessor", "A later revision requires its exact predecessor binding")
    if capture["mode"] == "local-snapshot":
        pack["gaps"].append(gap("current-authority", "Local snapshot does not establish current external permission or freshness.", "prepare-owner-review"))
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
    report = {"schema_version": "cal.define.preparation-report/v3", "authority_effect": "none", "structural_validity": "valid",
              "capture_mode": capture["mode"], "application_checks": app_results, "readiness": pack["readiness"],
              "assessment_execution_count": 0, "actual_owner_outcome": None, "claim_ceiling": CEILING}
    check(report, "report")
    members = {"pack.json": encode(pack), "capture.json": capture_raw, "request.json": request_raw, "report.json": encode(report)}
    for path, raw in raw_by_path.items():
        require(path not in members, "reserved-member-path")
        members["inputs/" + path] = raw
    return pack, report, members
