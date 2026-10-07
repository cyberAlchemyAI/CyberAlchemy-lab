#!/usr/bin/env python3
"""Validate the candidate reference slice against the owner-admitted Lab model."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
PACK = ROOT / "pack.json"
RECEIPT = ROOT / "receipts" / "validation.json"
REGISTRY_PATH = LAB / "authority/admissions/definition-complete-lab-model/v1/artifact-type-registry.json"
RELATION_REGISTRY_PATH = LAB / "authority/admissions/definition-complete-lab-model/v1/relation-kind-registry.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def generated_snapshot() -> dict[str, str]:
    paths = [ROOT / "pack.json", ROOT / "REFERENCE-SLICE.md", ROOT / "REVIEW.md"]
    for folder in (ROOT / "instances", ROOT / "ontology"):
        paths.extend(sorted(x for x in folder.rglob("*") if x.is_file()))
    return {str(x.relative_to(ROOT)): sha(x) for x in paths if x.exists()}


def schema_errors(record: dict[str, Any], schema_path: Path) -> list[str]:
    schema = load(schema_path)
    validator_class = jsonschema.validators.validator_for(schema)
    validator_class.check_schema(schema)
    validator = validator_class(schema)
    errors = []
    for error in sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path)):
        location = "/".join(str(x) for x in error.absolute_path) or "$"
        errors.append(f"{location}: {error.message}")
    return errors


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    before = generated_snapshot()
    build = subprocess.run(
        [sys.executable, str(ROOT / "build.py")],
        cwd=LAB,
        text=True,
        capture_output=True,
        check=False,
    )
    after = generated_snapshot()
    check(
        "deterministic-build",
        build.returncode == 0 and before == after,
        {"returncode": build.returncode, "stdout": build.stdout.strip(), "stderr": build.stderr.strip(), "changed_paths": sorted(set(before) | set(after)) if before != after else []},
    )

    pack = load(PACK)
    registry = load(REGISTRY_PATH)
    relation_registry = load(RELATION_REGISTRY_PATH)
    contracts = {x["artifact_type_ref"]: x for x in registry["admitted_contracts"] if x["lifecycle_state"] == "admitted-current"}
    relation_entries = {x["relation_kind_id"]: x for x in relation_registry["entries"]}
    artifact_entries = pack["artifacts"]
    typed_relations = pack["typed_relations"]

    inputs_current = all(sha(LAB / item["path"]) == item["sha256"] for item in pack["inputs"].values())
    check("admitted-inputs-current", inputs_current, pack["inputs"])

    artifact_validation = []
    artifact_by_ref: dict[str, dict[str, Any]] = {}
    artifact_manifest_by_ref = {x["identity_ref"]: x for x in artifact_entries}
    for entry in artifact_entries:
        path = LAB / entry["path"]
        contract = contracts.get(entry["carrier_type_ref"])
        record = load(path)
        errors = []
        if contract is None:
            errors.append("carrier is not admitted-current")
        else:
            errors.extend(schema_errors(record, LAB / contract["schema_path"]))
        if sha(path) != entry["sha256"]:
            errors.append("manifest digest mismatch")
        if record.get("authority_effect") != "none":
            errors.append("authority_effect must be none")
        identity = record.get("node_id") or record.get("product_id") or record.get("project_id") or record.get("goal_id")
        if identity != entry["identity_ref"]:
            errors.append("identity field does not match manifest")
        artifact_validation.append({"identity_ref": entry["identity_ref"], "carrier_type_ref": entry["carrier_type_ref"], "errors": errors})
        artifact_by_ref[entry["identity_ref"]] = record
    check(
        "all-artifacts-use-admitted-current-schemas",
        bool(artifact_validation) and all(not x["errors"] for x in artifact_validation),
        artifact_validation,
    )

    unique_artifacts = len(artifact_manifest_by_ref) == len(artifact_entries)
    counts_exact = pack["counts"] == {
        "artifact_instances": len(artifact_entries),
        "typed_relation_instances": len(typed_relations),
        "ontology_nodes": len(load(LAB / pack["ontology_projection"]["manifest_path"])["node_entries"]),
        "ontology_edges": len(load(LAB / pack["ontology_projection"]["manifest_path"])["edge_entries"]),
        "artifact_kinds": len({x["semantic_kind"] for x in artifact_entries}),
    }
    check("manifest-counts-and-identities", unique_artifacts and counts_exact, {"counts": pack["counts"], "unique_artifacts": unique_artifacts})

    typed_schema_path = LAB / contracts["cal.artifact-type.typed-relation/v2"]["schema_path"]
    relation_validation = []
    relation_by_ref: dict[str, dict[str, Any]] = {}
    for entry in typed_relations:
        path = LAB / entry["path"]
        record = load(path)
        payload = record["payload"]
        kind_id = payload["relation_kind_ref"]
        kind_entry = relation_entries.get(kind_id)
        kind_record = load(LAB / kind_entry["instance_path"]) if kind_entry else None
        errors = schema_errors(record, typed_schema_path)
        if sha(path) != entry["sha256"]:
            errors.append("manifest digest mismatch")
        if record.get("authority_effect") != "none":
            errors.append("authority_effect must be none")
        if kind_entry is None or kind_entry.get("lifecycle_state") != "admitted-current":
            errors.append("Relation Kind is not admitted-current")
        else:
            if sha(LAB / kind_entry["instance_path"]) != kind_entry["instance_sha256"]:
                errors.append("Relation Kind registry digest mismatch")
            pair = {"source_kind": payload["source"]["kind"], "target_kind": payload["target"]["kind"]}
            if pair not in kind_record["payload"]["allowed_endpoint_pairs"]:
                errors.append(f"undeclared endpoint pair {pair}")
            contract = kind_record["payload"]["qualifier_contract"]
            actual = set(payload["qualifiers"])
            required = set(contract["required_axes"])
            allowed = set(contract["properties"])
            if actual != required or actual - allowed:
                errors.append(f"qualifier axes {sorted(actual)} do not equal required {sorted(required)}")
        for side in ("source", "target"):
            endpoint = payload[side]
            local = artifact_manifest_by_ref.get(endpoint["ref"])
            if local is None:
                errors.append(f"{side} endpoint does not resolve locally")
            elif local["semantic_kind"] != endpoint["kind"]:
                errors.append(f"{side} endpoint kind mismatch")
            elif local["version_ref"] != endpoint["version_ref"]:
                errors.append(f"{side} endpoint version mismatch")
        if record["node_id"] != entry["relation_id"]:
            errors.append("relation identity mismatch")
        relation_validation.append({"relation_id": entry["relation_id"], "relation_kind_ref": kind_id, "errors": errors})
        relation_by_ref[entry["relation_id"]] = record
    check(
        "all-typed-relations-close-exactly",
        len(relation_by_ref) == len(typed_relations) and all(not x["errors"] for x in relation_validation),
        relation_validation,
    )

    projection = load(LAB / pack["ontology_projection"]["manifest_path"])
    semantic_histories = [artifact_by_ref[x] for x in projection["semantic_event_history_refs"]]
    governance_histories = [artifact_by_ref[x] for x in projection["governance_event_history_refs"]]
    semantic_events = [event for history in semantic_histories for event in history["payload"]["events"]]
    semantic_by_id = {x["event_id"]: x for x in semantic_events}
    governance_events = [event for history in governance_histories for event in history["payload"]["events"]]
    semantic_chain_ok = all(history["payload"]["chain_digest"] == digest_value([x["event_digest"] for x in history["payload"]["events"]]) for history in semantic_histories) and projection["semantic_chain_digest"] == digest_value([x["event_digest"] for x in semantic_events])
    semantic_previous_ok = all(all(x["previous_event_digest"] == (events[i - 1]["event_digest"] if i else None) for i, x in enumerate(events)) for events in [history["payload"]["events"] for history in semantic_histories])
    governance_chain_ok = all(history["payload"]["chain_digest"] == digest_value([x["event_digest"] for x in history["payload"]["events"]]) for history in governance_histories) and projection["governance_chain_digest"] == digest_value([x["event_digest"] for x in governance_events])
    governance_previous_ok = all(all(x["previous_event_digest"] == (events[i - 1]["event_digest"] if i else None) for i, x in enumerate(events)) for events in [history["payload"]["events"] for history in governance_histories])
    governance_tuple_ok = all(x["semantic_event_ref"]["semantic_event_id"] in semantic_by_id and x["semantic_event_ref"]["semantic_event_digest"] == semantic_by_id[x["semantic_event_ref"]["semantic_event_id"]]["event_digest"] for x in governance_events)
    event_paths_ok = all((LAB / x["record_ref"]).is_file() for x in semantic_events + governance_events)
    check("event-histories-and-governance-tuples", semantic_chain_ok and semantic_previous_ok and governance_chain_ok and governance_previous_ok and governance_tuple_ok and event_paths_ok, {"semantic_histories": len(semantic_histories), "semantic_events": len(semantic_events), "governance_histories": len(governance_histories), "governance_events": len(governance_events), "semantic_chain": semantic_chain_ok, "governance_chain": governance_chain_ok, "governance_tuples": governance_tuple_ok, "record_paths": event_paths_ok})

    node_by_ref = {}
    node_validation = []
    governance_event_ids = {x["event_id"] for x in governance_events}
    for entry in projection["node_entries"]:
        record = load(LAB / entry["path"])
        payload = record["payload"]
        subject = artifact_manifest_by_ref.get(entry["represented_subject_ref"])
        errors = []
        if sha(LAB / entry["path"]) != entry["sha256"]:
            errors.append("node digest mismatch")
        if subject is None:
            errors.append("represented subject does not resolve")
        else:
            represented = payload["represented_subject"]
            if represented["ref"] != subject["identity_ref"] or represented["digest"] != subject["sha256"] or represented["kind"] != subject["semantic_kind"]:
                errors.append("represented subject binding mismatch")
        sem = payload["governance_binding"]["semantic_event_ref"]
        if sem["semantic_event_id"] not in semantic_by_id or semantic_by_id[sem["semantic_event_id"]]["event_digest"] != sem["semantic_event_digest"]:
            errors.append("semantic event binding mismatch")
        if not set(payload["governance_binding"]["governance_event_refs"]).issubset(governance_event_ids):
            errors.append("governance event binding mismatch")
        if payload["replay_source"] is not False:
            errors.append("Ontology Node cannot be a replay source")
        node_by_ref[entry["node_ref"]] = record
        node_validation.append({"node_ref": entry["node_ref"], "errors": errors})
    check("ontology-nodes-bind-exact-subjects", all(not x["errors"] for x in node_validation), node_validation)

    edge_validation = []
    for entry in projection["edge_entries"]:
        record = load(LAB / entry["path"])
        payload = record["payload"]
        relation_entry = next((x for x in typed_relations if x["relation_id"] == entry["projected_relation_ref"]), None)
        relation = relation_by_ref.get(entry["projected_relation_ref"])
        errors = []
        if sha(LAB / entry["path"]) != entry["sha256"]:
            errors.append("edge digest mismatch")
        binding = payload["global_typed_relation_binding"]
        if relation is None or relation_entry is None:
            errors.append("projected Typed Relation does not resolve")
        else:
            if binding["typed_relation_ref"] != relation_entry["relation_id"] or binding["typed_relation_digest"] != relation_entry["sha256"]:
                errors.append("Typed Relation binding mismatch")
            source_node = node_by_ref.get(payload["source_node_ref"])
            target_node = node_by_ref.get(payload["target_node_ref"])
            if source_node is None or source_node["payload"]["represented_subject"]["ref"] != relation["payload"]["source"]["ref"]:
                errors.append("source node direction mismatch")
            if target_node is None or target_node["payload"]["represented_subject"]["ref"] != relation["payload"]["target"]["ref"]:
                errors.append("target node direction mismatch")
            if payload["relation_type_ref"] != relation["payload"]["relation_kind_ref"] or payload["closed_qualifiers"] != relation["payload"]["qualifiers"]:
                errors.append("relation semantics mismatch")
        if payload["edge_mode"] != "global-projection" or payload["replay_source"] is not False:
            errors.append("edge mode or replay boundary mismatch")
        edge_validation.append({"edge_ref": entry["edge_ref"], "errors": errors})
    check("ontology-edges-project-global-relations", all(not x["errors"] for x in edge_validation), edge_validation)

    cut = artifact_by_ref[projection["cut_ref"]]
    expected_cut_digest = digest_value({"semantic_chain_digest": projection["semantic_chain_digest"], "governance_chain_digest": projection["governance_chain_digest"], "nodes": [{"ref": x["node_ref"], "sha256": x["sha256"]} for x in projection["node_entries"]], "edges": [{"ref": x["edge_ref"], "sha256": x["sha256"]} for x in projection["edge_entries"]]})
    view = artifact_by_ref[projection["view_ref"]]
    cut_ok = cut["payload"]["calculated_digest"] == projection["cut_digest"] == expected_cut_digest and cut["payload"]["replay_source"] is False
    view_ok = view["payload"]["cut_ref"] == projection["cut_ref"] and view["payload"]["cut_digest"] == expected_cut_digest and view["payload"]["replay_source"] is False
    check("cut-and-view-are-exact-derived-surfaces", cut_ok and view_ok, {"cut_digest": expected_cut_digest, "cut_ok": cut_ok, "view_ok": view_ok})

    context_view = artifact_by_ref["context-view:reference-slice-authoring:2026-10-06"]
    included_ok = all((LAB / x["source_ref"]).is_file() and sha(LAB / x["source_ref"]) == x["sha256"] for x in context_view["included_material"])
    session = artifact_by_ref["agent-session:reference-slice-authoring:2026-10-06"]
    agent = artifact_by_ref["agent-instance:reference-slice-authoring:2026-10-06"]
    project_state = artifact_by_ref["project-state:cyberalchemy-v2-to-lab-migration:decision-0070"]
    consumed_targets = {x["payload"]["target"]["ref"] for x in relation_by_ref.values() if x["payload"]["relation_kind_ref"] == "relation.consumes-view" and x["payload"]["source"]["ref"] == session["node_id"]}
    memory_ok = (
        pack["memory_contract"]["machine_agent_ephemeral"] is True
        and pack["memory_contract"]["standalone_session_memory_artifact_present"] is False
        and not any(x["semantic_kind"] == "session-memory" for x in artifact_entries)
        and agent["payload"]["session_ref"] == session["node_id"]
        and agent["payload"]["terminated_at"] == "when-session-terminates"
        and session["payload"]["session_memory"]["expires_with_session"] is True
        and project_state["payload"]["project_ref"] == "project:cyberalchemy-v2-to-lab-migration"
        and set(pack["memory_contract"]["long_term_selection_refs"]) == consumed_targets
        and included_ok
    )
    check("agent-memory-and-project-state-boundary", memory_ok, {"consumed_views": sorted(consumed_targets), "durable_state": project_state["node_id"], "context_digests_current": included_ok, "standalone_session_memory_instances": sum(1 for x in artifact_entries if x["semantic_kind"] == "session-memory")})

    distinct = [
        "product:cyberalchemy-lab",
        "project:cyberalchemy-v2-to-lab-migration",
        "product-capability:cyberalchemy-lab:governed-knowledge-lifecycle",
        "capability-realization-binding:governed-repository-toolchain",
        "implementation:cyberalchemy-lab-governed-repository-toolchain",
        "research-inquiry:v2-to-lab-semantic-preservation",
        "hypothesis:reference-slice-preserves-orthogonality",
        "experiment-design:reference-slice-contract-validation",
        "experiment-run:reference-slice-contract-validation:2026-10-06",
        "evidence-set:reference-slice-validation",
        "finding:reference-slice-schema-and-relation-closure",
        "agent-instance:reference-slice-authoring:2026-10-06",
        "agent-session:reference-slice-authoring:2026-10-06",
        "project-state:cyberalchemy-v2-to-lab-migration:decision-0070",
        "context-view:reference-slice-authoring:2026-10-06",
        "ontology-view:cyberalchemy-lab-reference-slice:2026-10-06",
    ]
    noncollapse_ok = len(distinct) == len(set(distinct)) and all(x in artifact_manifest_by_ref for x in distinct) and all(x["node_ref"] != x["represented_subject_ref"] for x in projection["node_entries"]) and all(x["edge_ref"] != x["projected_relation_ref"] for x in projection["edge_entries"])
    check("non-collapse-invariants", noncollapse_ok, {"distinct_subjects": len(distinct), "assertions": pack["non_collapse_assertions"]})

    no_effect = pack["authority_effect"] == "none" and all(artifact_by_ref[x]["authority_effect"] == "none" for x in artifact_by_ref) and all(x["authority_effect"] == "none" for x in relation_by_ref.values()) and projection["authority_effect"] == "none"
    check("zero-authority-runtime-and-migration-effects", no_effect and pack["status"] == "candidate-owner-review-open", {"authority_effect": pack["authority_effect"], "excluded_effects": pack["excluded_effects"]})

    failed = [x for x in checks if x["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-reference-instance-pack-validation/v1",
        "subject": pack["pack_id"],
        "result": "PASS" if not failed else "FAIL",
        "authority_effect": "evidence-only",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "counts": pack["counts"],
        "materials": {"pack_sha256": sha(PACK), "artifact_type_registry_sha256": sha(REGISTRY_PATH), "relation_kind_registry_sha256": sha(RELATION_REGISTRY_PATH), "projection_manifest_sha256": sha(LAB / pack["ontology_projection"]["manifest_path"])},
        "claim_ceiling": "PASS proves deterministic schema, exact endpoint, qualifier, local reference, projection, and memory-boundary closure for this candidate slice only. It admits no instance or relation and activates no runtime.",
    }
    dump(RECEIPT, receipt)
    print(json.dumps({"result": receipt["result"], "checks": receipt["summary"], "counts": receipt["counts"], "pack_sha256": receipt["materials"]["pack_sha256"]}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
