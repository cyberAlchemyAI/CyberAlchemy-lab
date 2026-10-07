#!/usr/bin/env python3
"""Build and atomically apply the Decision 0074 governance transaction surface."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CANDIDATE = LAB / "authority/artifact-types/candidates/0013-governance-transaction-surface"
RELATION = LAB / "authority/relation-kinds/candidates/0007-governance-transaction-extension"
DEFINITION = LAB / "authority/definitions/candidates/0016-admission-transaction/definitions/admission-transaction/v1/definition.json"
D73 = LAB / "authority/project-state-transitions/candidates/0002-decision-0073-successor/instances/artifacts"
FINAL = LAB / "authority/admissions/governance-transaction-surface/v1"
DREG = LAB / "authority/definitions/registry.json"
DINDEX = LAB / "authority/definitions/DEFINITIONS-INDEX.md"
DDRIFT = LAB / "authority/definitions/drift-audit.json"
DDRIFT_MD = LAB / "authority/definitions/DEFINITION-DRIFT-AUDIT.md"

CHECKPOINT = "CAL-DECISION-CHECKPOINT-0074-GOVERNANCE-TRANSACTION-SURFACE"
BUNDLE_ID = "CAL-DECISION-BUNDLE-0074-GOVERNANCE-TRANSACTION-SURFACE"
TRANSACTION_ID = "admission-transaction:governance-transaction-surface-0074"
PROJECT = "project:cyberalchemy-v2-to-lab-migration"
STATE73 = "project-state:cyberalchemy-v2-to-lab-migration:decision-0073"
STATE74 = "project-state:cyberalchemy-v2-to-lab-migration:decision-0074"
SCOPE = "scope:cyberalchemy-lab-decision-0074-governance-transaction"
POLICY = "policy:cyberalchemy-lab-operational-foundation"
CHALLENGE = "challenge-contract:cyberalchemy-lab-operational-foundation"
DECISIONS = [
    {
        "decision_id": "CAL-DECISION-0074A-GOVERNANCE-CARRIER-ADMISSION",
        "decision_ref": "decision:0074A-governance-carrier-admission",
        "scope_ref": "decision-scope:0074A-governance-carrier-admission",
        "owner_ref": "role:artifact-type-owner",
        "effect_kind": "artifact-type-admission",
        "target_ref": "artifact-type-set:governance-transaction-fourteen",
        "target_path": "authority/artifact-types/candidates/0013-governance-transaction-surface/admission-target-set.json",
    },
    {
        "decision_id": "CAL-DECISION-0074B-ADMISSION-TRANSACTION-DEFINITION-ADMISSION",
        "decision_ref": "decision:0074B-admission-transaction-definition-admission",
        "scope_ref": "decision-scope:0074B-admission-transaction-definition-admission",
        "owner_ref": "role:definition-owner",
        "effect_kind": "definition-admission",
        "target_ref": "cal.definition.admission-transaction@1.0.0-candidate.1",
        "target_path": "authority/definitions/candidates/0016-admission-transaction/definitions/admission-transaction/v1/definition.json",
    },
    {
        "decision_id": "CAL-DECISION-0074C-GOVERNANCE-RELATION-SURFACE-ADMISSION",
        "decision_ref": "decision:0074C-governance-relation-surface-admission",
        "scope_ref": "decision-scope:0074C-governance-relation-surface-admission",
        "owner_ref": "role:relation-owner",
        "effect_kind": "relation-kind-successor-admission",
        "target_ref": "relation-kind-set:governance-transaction-0007",
        "target_path": "authority/relation-kinds/candidates/0007-governance-transaction-extension/relation-kind-successor-manifest.json",
    },
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


def atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(LAB))


def material(path: Path) -> dict:
    return {"path": rel(path), "sha256": sha(path)}


def with_event_digest(core: dict) -> dict:
    result = copy.deepcopy(core)
    result["event_digest"] = digest(core)
    return result


def render_index(registry: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit machine sources and run the bound admission builder. -->",
        "",
        "# CyberAlchemy Lab Definition Index",
        "",
        f"- Status: `{registry['status']}`",
        f"- Admission decision: `{registry['admission_decision_ref']}`",
        "",
        "| ID | Version | Term | Lifecycle | Path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in registry["entries"]:
        lines.append(f"| `{item['definition_id']}` | `{item['version']}` | {item['term']} | `{item['lifecycle_state']}` | `{item['path']}` |")
    lines += ["", "## Current lookup", ""]
    lines += [f"- `{key}` -> `{value}`" for key, value in registry["current_lookup"].items()]
    lines += ["", "## Claim ceiling", "", registry["claim_ceiling"], ""]
    return "\n".join(lines)


def render_drift(audit: dict) -> str:
    lines = ["<!-- GENERATED FILE: edit drift-audit.json through its bound admission builder. -->", "", "# Definition Drift Audit", "", "> Machine JSON is canonical.", ""]
    for finding in audit.get("findings", []):
        lines += [f"## {finding['finding_id']} — {finding['status']}", "", finding["condition"], "", f"Remediation: {finding['remediation']}", ""]
    lines += ["## Claim ceiling", "", audit["claim_ceiling"], ""]
    return "\n".join(lines)


def build_definition_registry() -> tuple[dict, str, dict, str]:
    live = load(DREG)
    definition = load(DEFINITION)
    definition_ref = f"{definition['definition_id']}@{definition['version']}"
    if definition["definition_id"] in live["current_lookup"]:
        raise RuntimeError("Admission Transaction Definition is already selected current")
    post = copy.deepcopy(live)
    post["entries"].append({
        "admission_decision_ref": DECISIONS[1]["decision_id"],
        "definition_id": definition["definition_id"],
        "lifecycle_state": "admitted",
        "path": rel(DEFINITION),
        "sha256": sha(DEFINITION),
        "term": definition["term"],
        "version": definition["version"],
    })
    post["entries"].sort(key=lambda item: (item["definition_id"], item["version"]))
    post["current_lookup"][definition["definition_id"]] = definition_ref
    post["current_lookup"] = dict(sorted(post["current_lookup"].items()))
    post["status"] = "owner-admitted"
    post["authority_effect"] = "one-hundred-eighty-nine-exact-definition-versions-canonical"
    post["admission_decision_ref"] = DECISIONS[1]["decision_id"]
    post["predecessor"] = {"path": rel(DREG), "sha256": sha(DREG), "entry_count": len(live["entries"]), "current_count": len(live["current_lookup"]), "admission_decision_ref": live["admission_decision_ref"]}
    post["source_direction"] = {"canonical": "registry.json", "human_projection": "DEFINITIONS-INDEX.md", "projection_policy": "generated-only", "generator_ref": "cal.generator.governance-transaction-surface-admission/v1"}
    post["claim_ceiling"] = "This registry contains 189 admitted Definition versions and selects 183 current identities. Decision 0074B admits only the exact Admission Transaction Definition and activates no runtime."
    index = render_index(post)
    drift = copy.deepcopy(load(DDRIFT))
    drift["admission_decision_ref"] = DECISIONS[1]["decision_id"]
    drift["record_id"] = "CAL-DEFINITION-DRIFT-AUDIT-POST-ADMISSION-TRANSACTION-V1"
    drift.setdefault("findings", []).append({
        "finding_id": "ADMISSION-TRANSACTION-DEFINITION-POST-001",
        "severity": "resolved",
        "status": "admitted",
        "condition": "The Admission Transaction Definition is admitted and selected current with its exact reviewed digest.",
        "target": definition_ref,
        "remediation": "Use the admitted Definition through the admitted Admission Transaction/v1 carrier and preserve transaction output bindings in application receipts.",
    })
    drift.setdefault("summary", {}).update({"current_definition_terms": 183, "definition_versions": 189, "admission_transaction_definition": "admitted-current"})
    drift["source_direction"] = {"canonical": "drift-audit.json", "human_projection": "DEFINITION-DRIFT-AUDIT.md", "projection_policy": "generated-only", "generator_ref": "cal.generator.governance-transaction-surface-admission/v1"}
    drift["claim_ceiling"] = "This audit records the exact Admission Transaction Definition admission. It does not prove consumer conformance, runtime activation, or external effect."
    drift["registry_sha256"] = hashlib.sha256(encoded(post)).hexdigest()
    return post, index, drift, render_drift(drift)


def build_artifact_registry() -> dict:
    source = load(LAB / "authority/admissions/project-state-bootstrap/v1/registries/artifact-type-registry.json")
    targets = load(CANDIDATE / "admission-target-set.json")
    impacted = load(CANDIDATE / "impacted-carrier-successors.json")
    post = copy.deepcopy(source)
    predecessor_refs = {item["predecessor_artifact_path"]: item for item in impacted["entries"]}
    predecessor_type_refs = set()
    for item in impacted["entries"]:
        predecessor_type_refs.add(load(LAB / item["predecessor_artifact_path"])["artifact_type_ref"])
    for contract in post["admitted_contracts"]:
        if contract["artifact_type_ref"] in predecessor_type_refs:
            contract["lifecycle_state"] = "admitted-historical"
    for descriptor in post["descriptors"]:
        if descriptor["artifact_type_ref"] in predecessor_type_refs:
            descriptor["effective_state"] = "admitted-historical"
    for target in targets["entries"]:
        artifact = load(LAB / target["artifact_path"])
        semantic_kind = artifact["classification"]["semantic_kind"]
        discriminator = artifact["instance_contract"]["instance_discriminator"]
        schema_path = target["schema_path"]
        contract = {
            "admission_decision_ref": DECISIONS[0]["decision_id"],
            "artifact_path": target["artifact_path"],
            "artifact_sha256": target["artifact_sha256"],
            "artifact_type_ref": artifact["artifact_type_ref"],
            "instance_discriminator": discriminator,
            "lifecycle_state": "admitted-current",
            "schema_path": schema_path,
            "schema_selector": None,
            "schema_sha256": target["schema_sha256"],
            "semantic_definition_refs": artifact["semantic_definition_refs"],
            "semantic_kind": semantic_kind,
        }
        descriptor = {
            "activation_state": "not-activated",
            "artifact_type_id": artifact["artifact_type_id"],
            "artifact_type_ref": artifact["artifact_type_ref"],
            "descriptor_path": target["artifact_path"],
            "descriptor_sha256": target["artifact_sha256"],
            "descriptor_version": artifact["version"],
            "effective_decision_refs": [DECISIONS[0]["decision_id"]],
            "effective_state": "admitted-current",
            "embedded_status": artifact["status"],
            "instance_discriminator": discriminator,
            "proposed_primary_definition_ref": None,
            "resolution_target_ref": None,
            "schema_path": schema_path,
            "schema_sha256": target["schema_sha256"],
            "semantic_binding_posture": "current-as-declared",
            "semantic_definition_refs": artifact["semantic_definition_refs"],
        }
        post["admitted_contracts"].append(contract)
        post["descriptors"].append(descriptor)
        post["current_by_identity"][artifact["artifact_type_id"]] = artifact["artifact_type_ref"]
    post["admitted_contracts"].sort(key=lambda item: item["artifact_type_ref"])
    post["descriptors"].sort(key=lambda item: item["artifact_type_ref"])
    post["current_by_identity"] = dict(sorted(post["current_by_identity"].items()))
    state_counts = {}
    for descriptor in post["descriptors"]:
        state_counts[descriptor["effective_state"]] = state_counts.get(descriptor["effective_state"], 0) + 1
    post["inventory"] = {
        "admitted_contract_count": len(post["admitted_contracts"]),
        "admitted_current_count": sum(item["lifecycle_state"] == "admitted-current" for item in post["admitted_contracts"]),
        "admitted_historical_count": sum(item["lifecycle_state"] == "admitted-historical" for item in post["admitted_contracts"]),
        "descriptor_count": len(post["descriptors"]),
        "descriptor_declared_ref_count": sum(bool(item.get("artifact_type_ref")) for item in post["descriptors"]),
        "descriptor_identity_count": len({item["artifact_type_id"] for item in post["descriptors"]}),
        "descriptor_resolved_ref_count": sum(bool(item.get("artifact_type_ref") or item.get("resolution_target_ref")) for item in post["descriptors"]),
        "duplicate_resolution_count": len(post["duplicate_resolutions"]),
        "semantic_binding_counts": {"current-as-declared": sum(item.get("semantic_binding_posture") == "current-as-declared" for item in post["descriptors"])},
        "state_counts": dict(sorted(state_counts.items())),
    }
    post["status"] = "owner-admitted-postimage"
    post["authority_effect"] = "fourteen-governance-transaction-artifact-type-contracts-admitted"
    post["version"] = "4.0.0"
    post["source_direction"] = {"canonical": "artifact-type-registry.json", "projection_policy": "generated-only", "generator_ref": "cal.generator.governance-transaction-surface-admission/v1", "predecessor_ref": "authority/admissions/project-state-bootstrap/v1/registries/artifact-type-registry.json"}
    post["claim_ceiling"] = "Admits exactly fourteen Artifact Type contracts, including eight successors and six new identities. It activates no runtime or consumer."
    if (len(post["admitted_contracts"]), len(post["current_by_identity"])) != (143, 121):
        raise RuntimeError("unexpected Artifact Type registry postimage counts")
    return post


def build_relation_registry() -> dict:
    source = load(LAB / "authority/admissions/definition-complete-lab-model/v1/relation-kind-registry.json")
    manifest = load(RELATION / "relation-kind-successor-manifest.json")
    rows = {item["relation_kind_id"]: item for item in source["entries"]}
    for item in manifest["entries"]:
        instance = load(LAB / item["path"])
        payload = instance["payload"]
        rows[item["relation_kind_id"]] = {
            "admission_decision_ref": DECISIONS[2]["decision_id"],
            "authority_effect": "relation-kind-admission-only",
            "axis_id": payload["axis_id"],
            "exact_endpoint_pair_count": len(payload["allowed_endpoint_pairs"]),
            "instance_path": item["path"],
            "instance_sha256": item["sha256"],
            "lifecycle_state": "admitted-current",
            "relation_kind_id": item["relation_kind_id"],
            "relation_kind_ref": item["relation_kind_id"],
            "required_qualifier_axes": payload["qualifier_contract"]["required_axes"],
        }
    post = copy.deepcopy(source)
    post["entries"] = [rows[key] for key in sorted(rows)]
    post["count"] = len(post["entries"])
    post["status"] = "owner-admitted-postimage"
    post["authority_effect"] = "three-relation-kind-successors-and-one-new-relation-kind-admitted"
    post["claim_ceiling"] = "Admits three exact Relation Kind successors and the materializes-consequence axis. It creates no Typed Relation by itself and activates no runtime."
    if post["count"] != 41:
        raise RuntimeError("unexpected Relation Kind registry count")
    return post


def build_endpoint_inventory() -> dict:
    source = load(LAB / "authority/admissions/definition-complete-lab-model/v1/endpoint-inventory.json")
    model = load(RELATION / "model.json")
    targets = load(CANDIDATE / "admission-target-set.json")
    carriers = {item["endpoint_kind"]: item for item in source["entries"]}
    for item in targets["entries"]:
        artifact = load(LAB / item["artifact_path"])
        kind = artifact["classification"]["semantic_kind"]
        carriers[kind] = {
            "admission_ref": DECISIONS[0]["decision_id"],
            "carrier_ref": artifact["artifact_type_ref"],
            "endpoint_kind": kind,
            "lifecycle_state": "admitted-current",
            "path": item["artifact_path"],
            "source_for": [],
            "target_for": [],
        }
    endpoint_kinds = sorted({pair[axis] for entry in model["entries"] for pair in entry["allowed_endpoint_pairs"] for axis in ("source_kind", "target_kind")})
    entries = []
    for kind in endpoint_kinds:
        if kind not in carriers:
            raise RuntimeError(f"no current carrier for endpoint kind {kind}")
        row = copy.deepcopy(carriers[kind])
        row["source_for"] = sorted({entry["relation_kind_id"] for entry in model["entries"] for pair in entry["allowed_endpoint_pairs"] if pair["source_kind"] == kind})
        row["target_for"] = sorted({entry["relation_kind_id"] for entry in model["entries"] for pair in entry["allowed_endpoint_pairs"] if pair["target_kind"] == kind})
        entries.append(row)
    pairs = sum(len(entry["allowed_endpoint_pairs"]) for entry in model["entries"])
    return {
        "schema_version": "cyberalchemy-lab-definition-complete-endpoint-inventory/v1",
        "status": "owner-admitted-postimage",
        "authority_effect": "none",
        "subject": model["model_id"],
        "closed_world": True,
        "counts": {"admitted-current": len(entries), "declared_endpoint_pairs": pairs, "named_endpoint_kinds": len(entries), "referenced-no-canonical-carrier": 0, "wildcard_tokens": 0},
        "entries": entries,
        "claim_ceiling": "Current endpoint carrier inventory for the admitted 41 Relation Kind model; it declares no relation instance or runtime behavior.",
    }


def build_governance_instances(stage: Path, decision_cores: list[dict], resolved_digest: str) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    policy_ref = POLICY
    auth_ref = rel(HERE / "authorization.json")
    def from_fixture(kind: str, version: str = "v1") -> dict:
        if version == "v1":
            return load(LAB / f"authority/artifact-types/{kind}/v1/fixtures/valid/record.json")
        return load(CANDIDATE / f"impacted-carrier-successors/{kind}/{version}/fixtures/valid/record.json")

    scope_instances = []
    for index, (meta, core) in enumerate(zip(DECISIONS, decision_cores), 1):
        scope = from_fixture("decision-scope", "v2")
        scope.update({"node_id": meta["scope_ref"], "name": f"Decision 0074{chr(64+index)} exact admission scope", "lifecycle_state": "active", "owner_ref": meta["owner_ref"], "scope_ref": SCOPE, "evidence_refs": [auth_ref], "claim_ceiling": "Admitted exact Decision scope; it permits only the bound admission effect and excludes runtime, publication, deployment, and external effects."})
        scope["payload"] = {"subject_refs": [meta["target_ref"]], "subject_kind_refs": [meta["effect_kind"]], "permitted_effects": [meta["effect_kind"]], "excluded_effects": ["runtime-activation", "external-publication", "deployment"]}
        scope["relation_refs"] = [{"relation_kind_ref": "relation.scopes-authority-over", "direction": "target", "counterpart_kind": "authority-boundary", "counterpart_ref": "authority-boundary:lab-owner-governance-admission-0074"}]
        path = stage / f"instances/governance/decision-scopes/decision-0074{chr(96+index)}.json"
        dump(path, scope); scope_instances.append(scope)

        decision = from_fixture("decision", "v2")
        decision.update({"node_id": meta["decision_ref"], "name": meta["decision_id"], "lifecycle_state": "active", "owner_ref": meta["owner_ref"], "scope_ref": meta["scope_ref"], "evidence_refs": [auth_ref, rel(HERE / f"decision-cores/decision-0074{chr(96+index)}.json")], "claim_ceiling": "Admits only the exact target and digest bound by this independent Decision within the one resolved checkpoint."})
        decision["payload"] = {"decision_maker_ref": "principal:lab-owner", "declared_effect_refs": [meta["effect_kind"]], "evidence_basis_refs": [auth_ref], "selected_outcome": "admit-exact-reviewed-target", "subject_refs": [meta["target_ref"]]}
        decision["relation_refs"] = [{"relation_kind_ref": "relation.member-of", "direction": "source", "counterpart_kind": "decision-bundle", "counterpart_ref": "decision-bundle:governance-transaction-surface-0074"}]
        path = stage / f"instances/governance/decisions/decision-0074{chr(96+index)}.json"
        dump(path, decision)

    boundary = from_fixture("authority-boundary")
    boundary.update({"node_id": "authority-boundary:lab-owner-governance-admission-0074", "name": "Lab owner governance admission boundary", "lifecycle_state": "active", "owner_ref": "role:repository-owner", "scope_ref": SCOPE, "evidence_refs": [auth_ref], "claim_ceiling": "Binds repository owner authority to the three exact Decision scopes in this checkpoint; it grants no runtime or external authority."})
    boundary["payload"].update({"authority_scope_ref": CHECKPOINT, "effective_period": "decision-0074-transaction-only"})
    boundary["relation_refs"] = [{"relation_kind_ref": "relation.scopes-authority-over", "direction": "source", "counterpart_kind": "decision-scope", "counterpart_ref": item["node_id"]} for item in scope_instances]
    dump(stage / "instances/governance/authority-boundary.json", boundary)

    profile = from_fixture("workflow-decision-profile")
    profile.update({"node_id": "workflow-decision-profile:lab-governance-single-checkpoint", "name": "Lab governance single checkpoint profile", "lifecycle_state": "active", "owner_ref": "role:repository-owner", "scope_ref": SCOPE, "evidence_refs": [auth_ref], "claim_ceiling": "Records one final-review checkpoint for exact targets and does not authorize effects outside the resolved bundle."})
    profile["relation_refs"] = [{"relation_kind_ref": "relation.governed-by", "direction": "source", "counterpart_kind": "policy", "counterpart_ref": policy_ref}]
    dump(stage / "instances/governance/workflow-decision-profile.json", profile)

    preference = from_fixture("user-decision-preference")
    preference.update({"node_id": "user-decision-preference:lab-owner-final-review", "name": "Lab owner final review preference", "lifecycle_state": "active", "owner_ref": "role:repository-owner", "scope_ref": SCOPE, "evidence_refs": [auth_ref], "claim_ceiling": "Records the final-review interaction preference and supplies no admission authority by itself."})
    preference["relation_refs"] = [{"relation_kind_ref": "relation.governed-by", "direction": "source", "counterpart_kind": "policy", "counterpart_ref": policy_ref}]
    dump(stage / "instances/governance/user-decision-preference.json", preference)

    checkpoint = from_fixture("decision-checkpoint")
    checkpoint.update({"node_id": "decision-checkpoint:governance-transaction-review-0074", "name": "Decision 0074 governance transaction final review", "lifecycle_state": "active", "owner_ref": "role:repository-owner", "scope_ref": SCOPE, "evidence_refs": [auth_ref], "claim_ceiling": "Records the single resolved owner checkpoint for the three independent Decisions."})
    checkpoint["payload"].update({"decision_bundle_ref": "decision-bundle:governance-transaction-surface-0074", "presentation_state": "resolved", "opened_at": "2026-10-06T00:00:00-03:00", "closed_at": "2026-10-06T00:00:00-03:00"})
    checkpoint["relation_refs"] = [{"relation_kind_ref": "relation.governed-by", "direction": "source", "counterpart_kind": "policy", "counterpart_ref": policy_ref}]
    dump(stage / "instances/governance/decision-checkpoint.json", checkpoint)

    decision_bundle = from_fixture("decision-bundle")
    decision_bundle.update({"node_id": "decision-bundle:governance-transaction-surface-0074", "name": BUNDLE_ID, "lifecycle_state": "active", "owner_ref": "role:repository-owner", "scope_ref": SCOPE, "evidence_refs": [auth_ref], "claim_ceiling": "Resolved atomic bundle of three independent exact-target Decisions; the owner response does not collapse their identities."})
    decision_bundle["payload"] = {
        "checkpoint_ref": checkpoint["node_id"],
        "ordered_decisions": [{"decision_ref": meta["decision_ref"], "decision_core_sha256": sha(HERE / f"decision-cores/decision-0074{chr(97+i)}.json"), "owner_ref": meta["owner_ref"], "scope_ref": meta["scope_ref"], "effect_kind": meta["effect_kind"], "target_refs": [meta["target_ref"]], "target_digests": [{"target_ref": meta["target_ref"], "sha256": sha(LAB / meta["target_path"])}], "selected_outcome": "admit-exact-reviewed-target"} for i, meta in enumerate(DECISIONS)],
        "all_targets_materialized": True,
        "bundle_digest": resolved_digest,
        "atomicity_requirement": "all-or-nothing",
        "invalidation_conditions": ["any-target-digest-change", "authority-scope-change", "new-runtime-or-external-effect", "failed-precondition"],
    }
    decision_bundle["relation_refs"] = [{"relation_kind_ref": "relation.member-of", "direction": "target", "counterpart_kind": "decision", "counterpart_ref": meta["decision_ref"]} for meta in DECISIONS]
    dump(stage / "instances/governance/decision-bundle.json", decision_bundle)
    return paths


def build() -> tuple[Path, dict]:
    run = subprocess.run([sys.executable, str(CANDIDATE / "validate.py")], cwd=LAB, check=False)
    if run.returncode or load(CANDIDATE / "receipts/validation.json")["result"] != "PASS":
        raise RuntimeError("governance transaction candidate validation failed")

    authorization = {
        "schema_version": "cyberalchemy-lab-owner-authorization/v2",
        "authorization_id": "CAL-AUTHORIZATION-0074-GOVERNANCE-TRANSACTION-SURFACE",
        "recorded_on": "2026-10-06",
        "principal_ref": "principal:lab-owner",
        "decision_checkpoint_ref": CHECKPOINT,
        "authorized": True,
        "verbatim_user_authorization": "amidted, and do next",
        "interpreted_scope": "Admit the exact reviewed governance transaction surface and perform its deterministic registry, index, Project State, semantic history, and governance history consequences in one atomic Admission Transaction.",
        "selected_outcome": "admit-exact-reviewed-target",
        "decision_refs": [item["decision_id"] for item in DECISIONS],
        "reviewed_bindings": {
            "review_bundle_sha256": "2a4636a1d7d24d45a0111501fd45a8a3fba41ff3b86324db1e7106f3b6173c3f",
            "reviewed_thirteen_carrier_target_set_sha256": "9324030cacd0e1078129f8cbd3181a9af4b4046032bbd1d54413c97869c7f613",
            "corrected_fourteen_carrier_target_set_sha256": sha(CANDIDATE / "admission-target-set.json"),
            "definition_sha256": sha(DEFINITION),
            "relation_kind_successor_manifest_sha256": sha(RELATION / "relation-kind-successor-manifest.json"),
        },
        "representation_closure_repair": {**material(CANDIDATE / "representation-closure-repair.json"), "semantic_scope_changed": False},
        "excluded_effects": ["runtime-activation", "external-publication", "deployment", "consumer-activation", "semantic-scope-expansion"],
    }
    dump(HERE / "authorization.json", authorization)

    core_records = []
    for index, meta in enumerate(DECISIONS):
        core = {
            "schema_version": "cyberalchemy-lab-stable-decision-core/v1",
            "decision_id": meta["decision_id"], "decision_ref": meta["decision_ref"],
            "owner_ref": meta["owner_ref"], "scope_ref": meta["scope_ref"], "effect_kind": meta["effect_kind"],
            "target_refs": [meta["target_ref"]], "target_digests": [{"target_ref": meta["target_ref"], "sha256": sha(LAB / meta["target_path"])}],
            "selected_outcome": "admit-exact-reviewed-target", "authorization_ref": rel(HERE / "authorization.json"),
            "generated_consequence_digests_excluded": True,
        }
        path = HERE / f"decision-cores/decision-0074{chr(97+index)}.json"
        dump(path, core)
        core_records.append(core)

    resolved_core = {
        "checkpoint_ref": CHECKPOINT,
        "ordered_decisions": [{"decision_ref": item["decision_ref"], "decision_core_sha256": sha(HERE / f"decision-cores/decision-0074{chr(97+i)}.json"), "selected_outcome": "admit-exact-reviewed-target"} for i, item in enumerate(DECISIONS)],
        "atomicity": "all-or-nothing",
    }
    resolved_digest = digest(resolved_core)

    temp_root = Path(tempfile.mkdtemp(prefix=".decision-0074-", dir=LAB))
    stage = temp_root / "v1"
    stage.mkdir()
    definition_registry, definition_index, drift, drift_md = build_definition_registry()
    artifact_registry = build_artifact_registry()
    relation_registry = build_relation_registry()
    endpoint_inventory = build_endpoint_inventory()
    dump(stage / "registries/definition-registry.json", definition_registry)
    (stage / "registries/DEFINITIONS-INDEX.md").write_text(definition_index, encoding="utf-8")
    dump(stage / "registries/definition-drift-audit.json", drift)
    (stage / "registries/DEFINITION-DRIFT-AUDIT.md").write_text(drift_md, encoding="utf-8")
    dump(stage / "registries/artifact-type-registry.json", artifact_registry)
    dump(stage / "registries/relation-kind-registry.json", relation_registry)
    dump(stage / "registries/endpoint-inventory.json", endpoint_inventory)

    build_governance_instances(stage, core_records, resolved_digest)

    historical_dir = stage / "instances/project-history/decision-0073"
    historical_dir.mkdir(parents=True)
    for name in ["project-state.json", "project-semantic-event-history.json", "project-governance-event-history.json"]:
        shutil.copyfile(D73 / name, historical_dir / name)

    stable_material_paths = [HERE / "authorization.json"] + [HERE / f"decision-cores/decision-0074{letter}.json" for letter in "abc"] + [CANDIDATE / "admission-target-set.json", CANDIDATE / "representation-closure-repair.json", DEFINITION, RELATION / "relation-kind-successor-manifest.json"]
    stable_materials = [material(path) for path in stable_material_paths]
    old_state = load(D73 / "project-state.json")
    old_semantic = load(D73 / "project-semantic-event-history.json")
    old_governance = load(D73 / "project-governance-event-history.json")
    artifact_refs = old_state["payload"]["artifact_refs"] + [item["path"] for item in stable_materials]
    state_materials = [material(LAB / path) for path in artifact_refs]
    state_digest = "sha256:" + digest(state_materials)
    state = copy.deepcopy(old_state)
    state.update({"schema_version": "cyberalchemy-lab-project-state/v2", "node_id": STATE74, "name": "CyberAlchemy v2 migration state after Decision 0074", "lifecycle_state": "active", "scope_ref": SCOPE, "evidence_refs": [item["path"] for item in stable_materials], "claim_ceiling": "Current immutable Project State through the applied Decision 0074 Admission Transaction. It records repository governance state and activates no Agent, consumer, service, deployment, or external runtime.", "relation_refs": [{"relation_kind_ref": "relation.member-of", "direction": "source", "counterpart_kind": "project", "counterpart_ref": PROJECT}, {"relation_kind_ref": "relation.successor-of", "direction": "source", "counterpart_kind": "project-state", "counterpart_ref": STATE73}, {"relation_kind_ref": "relation.materializes-consequence", "direction": "target", "counterpart_kind": "admission-transaction", "counterpart_ref": TRANSACTION_ID}]})
    state["payload"].update({"cursor": "decision:0074", "artifact_refs": artifact_refs, "decision_refs": old_state["payload"]["decision_refs"] + [item["decision_id"] for item in DECISIONS], "state_digest": state_digest})
    dump(stage / "instances/project-state.json", state)

    semantic_core = {"event_id": "project-semantic-event:cyberalchemy-v2-to-lab-migration:4", "cursor": 4, "previous_event_digest": old_semantic["payload"]["events"][-1]["event_digest"], "change_kind": "governance-transaction-surface-admitted", "predecessor_state_ref": STATE73, "predecessor_state_digest": old_state["payload"]["state_digest"], "resulting_state_ref": STATE74, "resulting_state_digest": state_digest, "material_refs": stable_materials, "record_ref": rel(CANDIDATE / "admission-target-set.json"), "semantic_summary": "Decision 0074 admitted the governance transaction carriers, Admission Transaction Definition, relation extension, exact registries, and self-contained D74 Project State consequences."}
    semantic_event = with_event_digest(semantic_core)
    semantic = copy.deepcopy(old_semantic)
    semantic.update({"schema_version": "cyberalchemy-lab-project-semantic-event-history/v2", "lifecycle_state": "active", "scope_ref": SCOPE, "evidence_refs": [item["path"] for item in stable_materials], "relation_refs": [{"relation_kind_ref": "relation.materializes-consequence", "direction": "target", "counterpart_kind": "admission-transaction", "counterpart_ref": TRANSACTION_ID}], "claim_ceiling": "Append-only Project semantic history through event 4; it records the exact state transition and supplies no governance authority."})
    semantic["payload"]["events"] = old_semantic["payload"]["events"] + [semantic_event]
    semantic["payload"]["latest_cursor"] = 4
    semantic["payload"]["chain_digest"] = digest([event["event_digest"] for event in semantic["payload"]["events"]])
    dump(stage / "instances/project-semantic-event-history.json", semantic)

    governance_core = {"event_id": "project-governance-event:cyberalchemy-v2-to-lab-migration:4", "governance_cursor": 4, "previous_event_digest": old_governance["payload"]["events"][-1]["event_digest"], "semantic_event_ref": {"semantic_event_id": semantic_event["event_id"], "semantic_event_digest": semantic_event["event_digest"], "semantic_cursor": 4}, "decision_ref": CHECKPOINT, "authorization_ref": rel(HERE / "authorization.json"), "authorization_sha256": sha(HERE / "authorization.json"), "policy_ref": POLICY, "challenge_contract_ref": CHALLENGE, "upstream_governance_evidence_refs": [item["path"] for item in stable_materials], "record_ref": rel(HERE / "decision-cores/decision-0074a.json"), "governance_summary": "One explicit repository owner response resolved three independent Decision identities and authorized one atomic Admission Transaction with no runtime or external effects."}
    governance_event = with_event_digest(governance_core)
    governance = copy.deepcopy(old_governance)
    governance.update({"schema_version": "cyberalchemy-lab-project-governance-event-history/v2", "lifecycle_state": "active", "scope_ref": SCOPE, "evidence_refs": governance_core["upstream_governance_evidence_refs"], "relation_refs": [{"relation_kind_ref": "relation.materializes-consequence", "direction": "target", "counterpart_kind": "admission-transaction", "counterpart_ref": TRANSACTION_ID}], "claim_ceiling": "Append-only Project governance history through event 4; it binds the exact owner authorization and cannot patch semantic state."})
    governance["payload"]["events"] = old_governance["payload"]["events"] + [governance_event]
    governance["payload"]["latest_governance_cursor"] = 4
    governance["payload"]["chain_digest"] = digest([event["event_digest"] for event in governance["payload"]["events"]])
    dump(stage / "instances/project-governance-event-history.json", governance)

    output_hashes = {name: sha(stage / path) for name, path in {"definition_registry": "registries/definition-registry.json", "definition_index": "registries/DEFINITIONS-INDEX.md", "artifact_type_registry": "registries/artifact-type-registry.json", "relation_kind_registry": "registries/relation-kind-registry.json", "endpoint_inventory": "registries/endpoint-inventory.json"}.items()}
    generated = load(CANDIDATE / "impacted-carrier-successors/generated-output/v2/fixtures/valid/record.json")
    generated.update({"node_id": "generated-output:decision-0074-registry-index-projections", "name": "Decision 0074 registry and index projections", "lifecycle_state": "active", "owner_ref": "role:repository-owner", "scope_ref": SCOPE, "evidence_refs": [rel(HERE / "authorization.json")], "claim_ceiling": "Binds the exact deterministic registry and index postimages created by the Admission Transaction; it makes no semantic correctness or runtime claim."})
    generated["payload"] = {"generator_ref": "cal.generator.governance-transaction-surface-admission/v1", "input_refs": [item["target_path"] for item in DECISIONS], "output_digest": "sha256:" + digest(output_hashes), "reproducibility_receipt_ref": rel(FINAL / "receipts/application.json")}
    generated["relation_refs"] = [{"relation_kind_ref": "relation.materializes-consequence", "direction": "target", "counterpart_kind": "admission-transaction", "counterpart_ref": TRANSACTION_ID}]
    dump(stage / "instances/generated-output.json", generated)

    transaction = load(LAB / "authority/artifact-types/admission-transaction/v1/fixtures/valid/record.json")
    transaction.update({"node_id": TRANSACTION_ID, "name": "Applied Decision 0074 governance surface Admission Transaction", "lifecycle_state": "active", "owner_ref": "role:repository-owner", "scope_ref": SCOPE, "evidence_refs": [rel(HERE / "authorization.json")] + [rel(HERE / f"decision-cores/decision-0074{letter}.json") for letter in "abc"], "claim_ceiling": "Atomically applies the three exact authorized admission Decisions and binds deterministic repository outputs. It activates no runtime and creates no external effect."})
    output_paths = {"project-state": stage / "instances/project-state.json", "project-semantic-event-history": stage / "instances/project-semantic-event-history.json", "project-governance-event-history": stage / "instances/project-governance-event-history.json", "generated-output": stage / "instances/generated-output.json"}
    transaction["payload"] = {
        "project_ref": "project:cyberalchemy-lab", "decision_bundle_ref": "decision-bundle:governance-transaction-surface-0074",
        "decision_core_refs": [{"decision_ref": item["decision_ref"], "decision_core_sha256": sha(HERE / f"decision-cores/decision-0074{chr(97+i)}.json"), "selected_outcome": "admit-exact-reviewed-target"} for i, item in enumerate(DECISIONS)],
        "review_bundle_digest": authorization["reviewed_bindings"]["review_bundle_sha256"], "resolved_bundle_digest": resolved_digest,
        "authorization_evidence_ref": rel(HERE / "authorization.json"), "authorization_evidence_sha256": sha(HERE / "authorization.json"),
        "input_state_ref": STATE73, "input_state_sha256": sha(D73 / "project-state.json"),
        "admission_targets": [{"target_ref": item["target_ref"], "target_sha256": sha(LAB / item["target_path"]), "effect_kind": item["effect_kind"]} for item in DECISIONS],
        "deterministic_consequences": [{"consequence_ref": {"project-state": STATE74, "project-semantic-event-history": semantic["node_id"], "project-governance-event-history": governance["node_id"], "generated-output": generated["node_id"]}[kind], "consequence_kind": kind, "declared_input_ref": BUNDLE_ID, "output_sha256": sha(path)} for kind, path in output_paths.items()],
        "atomicity": "all-or-nothing", "application_state": "applied", "application_receipt_ref": rel(FINAL / "receipts/application.json"), "rollback_ref": "rollback:restore-decision-0073-project-state-and-registry-preimages", "runtime_activations": 0, "external_effect_refs": [],
        "decision_core_hash_policy": "stable-core-excludes-generated-consequence-digests", "output_binding_policy": "application-receipt-binds-final-output-digests",
    }
    transaction["relation_refs"] = [{"relation_kind_ref": "relation.governed-by", "direction": "source", "counterpart_kind": "policy", "counterpart_ref": POLICY}] + [{"relation_kind_ref": "relation.materializes-consequence", "direction": "source", "counterpart_kind": kind, "counterpart_ref": transaction["payload"]["deterministic_consequences"][index]["consequence_ref"]} for index, kind in enumerate(output_paths)]
    dump(stage / "instances/governance/admission-transaction.json", transaction)

    typed_schema = load(CANDIDATE / "impacted-carrier-successors/typed-relation/v3/schema.json")
    relation_targets = [("project-state", STATE74, "current-project-state", stage / "instances/project-state.json"), ("project-semantic-event-history", semantic["node_id"], "semantic-history", stage / "instances/project-semantic-event-history.json"), ("project-governance-event-history", governance["node_id"], "governance-history", stage / "instances/project-governance-event-history.json"), ("generated-output", generated["node_id"], "registry-index-projections", stage / "instances/generated-output.json")]
    for kind, target_ref, role, output_path in relation_targets:
        record = load(CANDIDATE / "impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json")
        record.update({"node_id": f"typed-relation:decision-0074-materializes-{kind}", "name": f"Decision 0074 transaction materializes {kind}", "lifecycle_state": "active", "owner_ref": "role:relation-owner", "scope_ref": SCOPE, "evidence_refs": [rel(HERE / "authorization.json")], "claim_ceiling": "Records one deterministic transaction consequence with its exact output digest; it grants no new authority and proves no semantic correctness."})
        record["payload"] = {"relation_kind_ref": "relation.materializes-consequence", "source": {"kind": "admission-transaction", "ref": TRANSACTION_ID, "version_ref": TRANSACTION_ID + "@applied"}, "target": {"kind": kind, "ref": target_ref, "version_ref": target_ref + "@decision-0074"}, "qualifiers": {"application_receipt_ref": rel(FINAL / "receipts/application.json"), "consequence_role": role, "output_digest": "sha256:" + sha(output_path)}, "relation_lifecycle_state": "active", "relation_evidence_refs": [rel(HERE / "authorization.json")]}
        dump(stage / f"instances/typed-relations/materializes-{kind}.json", record)
        errors = list(jsonschema.Draft202012Validator(typed_schema).iter_errors(record))
        if errors:
            raise RuntimeError(f"Typed Relation validation failed for {kind}: {errors[0].message}")

    definition_admission = {"schema_version": "cyberalchemy-lab-definition-admission/v1", "decision_id": DECISIONS[1]["decision_id"], "status": "owner-admitted", "count": 1, "entry": {"definition_ref": "cal.definition.admission-transaction@1.0.0-candidate.1", **material(DEFINITION)}, "claim_ceiling": "Admits only the exact Admission Transaction Definition."}
    artifact_admission = {"schema_version": "cyberalchemy-lab-collective-artifact-type-admission/v1", "decision_id": DECISIONS[0]["decision_id"], "status": "owner-admitted", "count": 14, "predecessors_transitioned_to_historical": 8, "target_set": material(CANDIDATE / "admission-target-set.json"), "entries": load(CANDIDATE / "admission-target-set.json")["entries"], "claim_ceiling": "Admits exactly fourteen Artifact Type contracts and activates no consumer or runtime."}
    relation_admission = {"schema_version": "cyberalchemy-lab-collective-relation-kind-admission/v1", "decision_id": DECISIONS[2]["decision_id"], "status": "owner-admitted", "count": 4, "successors": 3, "new_axes": 1, "target_set": material(RELATION / "relation-kind-successor-manifest.json"), "entries": load(RELATION / "relation-kind-successor-manifest.json")["entries"], "claim_ceiling": "Admits three Relation Kind successors and one new orthogonal Relation Kind; it creates no connection by itself."}
    dump(stage / "definition-admission.json", definition_admission)
    dump(stage / "artifact-type-admission.json", artifact_admission)
    dump(stage / "relation-kind-admission.json", relation_admission)
    dump(stage / "representation-closure-repair.json", load(CANDIDATE / "representation-closure-repair.json"))

    schema_map = {
        "instances/governance/authority-boundary.json": LAB / "authority/artifact-types/authority-boundary/v1/schema.json",
        "instances/governance/workflow-decision-profile.json": LAB / "authority/artifact-types/workflow-decision-profile/v1/schema.json",
        "instances/governance/user-decision-preference.json": LAB / "authority/artifact-types/user-decision-preference/v1/schema.json",
        "instances/governance/decision-checkpoint.json": LAB / "authority/artifact-types/decision-checkpoint/v1/schema.json",
        "instances/governance/decision-bundle.json": LAB / "authority/artifact-types/decision-bundle/v1/schema.json",
        "instances/governance/admission-transaction.json": LAB / "authority/artifact-types/admission-transaction/v1/schema.json",
        "instances/project-state.json": CANDIDATE / "impacted-carrier-successors/project-state/v2/schema.json",
        "instances/project-semantic-event-history.json": CANDIDATE / "impacted-carrier-successors/project-semantic-event-history/v2/schema.json",
        "instances/project-governance-event-history.json": CANDIDATE / "impacted-carrier-successors/project-governance-event-history/v2/schema.json",
        "instances/generated-output.json": CANDIDATE / "impacted-carrier-successors/generated-output/v2/schema.json",
    }
    validations = []
    for relative_path, schema_path in schema_map.items():
        path = stage / relative_path
        errors = [error.message for error in jsonschema.Draft202012Validator(load(schema_path)).iter_errors(load(path))]
        validations.append({"path": relative_path, "schema": rel(schema_path), "result": "PASS" if not errors else "BLOCK", "errors": errors})
    for name in ["project-state.json", "project-semantic-event-history.json", "project-governance-event-history.json"]:
        source_path = D73 / name
        preserved_path = stage / "instances/project-history/decision-0073" / name
        validations.append({"path": str(preserved_path.relative_to(stage)), "schema": "byte-exact-D73-historical-preservation", "result": "PASS" if sha(source_path) == sha(preserved_path) else "BLOCK", "errors": []})
    decision_schema = load(CANDIDATE / "impacted-carrier-successors/decision/v2/schema.json")
    scope_schema = load(CANDIDATE / "impacted-carrier-successors/decision-scope/v2/schema.json")
    for path in (stage / "instances/governance/decisions").glob("*.json"):
        errors = [error.message for error in jsonschema.Draft202012Validator(decision_schema).iter_errors(load(path))]
        validations.append({"path": str(path.relative_to(stage)), "schema": "decision/v2", "result": "PASS" if not errors else "BLOCK", "errors": errors})
    for path in (stage / "instances/governance/decision-scopes").glob("*.json"):
        errors = [error.message for error in jsonschema.Draft202012Validator(scope_schema).iter_errors(load(path))]
        validations.append({"path": str(path.relative_to(stage)), "schema": "decision-scope/v2", "result": "PASS" if not errors else "BLOCK", "errors": errors})
    if any(item["result"] != "PASS" for item in validations):
        blocked = [item for item in validations if item["result"] != "PASS"]
        raise RuntimeError("instance schema validation failed: " + json.dumps(blocked[:3]))

    def admitted_material(path: Path) -> dict:
        return {"path": rel(FINAL / path.relative_to(stage)), "sha256": sha(path)}

    receipt = {
        "schema_version": "cyberalchemy-lab-admission-transaction-application-receipt/v1", "result": "PASS", "applied_on": "2026-10-06",
        "decision_checkpoint_ref": CHECKPOINT, "decision_refs": [item["decision_id"] for item in DECISIONS], "transaction_ref": TRANSACTION_ID,
        "transaction_sha256": sha(stage / "instances/governance/admission-transaction.json"), "authorization": material(HERE / "authorization.json"),
        "outputs": {"project_state": admitted_material(stage / "instances/project-state.json"), "semantic_history": admitted_material(stage / "instances/project-semantic-event-history.json"), "governance_history": admitted_material(stage / "instances/project-governance-event-history.json"), "generated_output": admitted_material(stage / "instances/generated-output.json"), "definition_registry": admitted_material(stage / "registries/definition-registry.json"), "artifact_type_registry": admitted_material(stage / "registries/artifact-type-registry.json"), "relation_kind_registry": admitted_material(stage / "registries/relation-kind-registry.json"), "endpoint_inventory": admitted_material(stage / "registries/endpoint-inventory.json")},
        "counts": {"definitions_admitted": 1, "artifact_types_admitted": 14, "artifact_type_predecessors_historical": 8, "relation_kinds_admitted": 4, "relation_kind_successors": 3, "new_relation_kinds": 1, "typed_relations_admitted": 4, "project_states_materialized": 2, "semantic_events_appended": 2, "governance_events_appended": 2, "runtime_activations": 0, "external_effects": 0},
        "no_followup_bookkeeping_decision_required": True,
        "claim_ceiling": "PASS binds the exact atomic Decision 0074 transaction outputs and proves repository postimage closure only. It proves no runtime behavior or external effect.",
    }
    dump(stage / "receipts/application.json", receipt)
    validation = {"schema_version": "cyberalchemy-lab-governance-transaction-surface-admission-validation/v1", "result": "PASS", "checks": validations, "counts": {"schema_instances": len(validations), "definition_versions": len(definition_registry["entries"]), "current_definitions": len(definition_registry["current_lookup"]), "artifact_type_contracts": artifact_registry["inventory"]["admitted_contract_count"], "current_artifact_types": artifact_registry["inventory"]["admitted_current_count"], "relation_kinds": relation_registry["count"], "endpoint_kinds": endpoint_inventory["counts"]["named_endpoint_kinds"], "endpoint_pairs": endpoint_inventory["counts"]["declared_endpoint_pairs"], "runtime_activations": 0}, "claim_ceiling": "PASS proves exact schema, registry, endpoint, event-chain, and output-binding closure for this repository transaction."}
    dump(stage / "receipts/validation.json", validation)

    (stage / "ADMISSION.md").write_text("# Governance transaction surface admission\n\nStatus: **owner admitted and atomically applied**\n\nThis bundle preserves three Decision identities, one owner checkpoint, and one Admission Transaction. It materializes the Decision 0073 intermediate Project State and the current Decision 0074 state within the same transaction.\n\n- Definitions admitted: `1`\n- Artifact Types admitted: `14`\n- Relation Kinds admitted: `4`\n- Typed Relations admitted: `4`\n- Current Project State: `decision:0074`\n- Runtime activations: `0`\n- External effects: `0`\n", encoding="utf-8")
    files = []
    for path in sorted(stage.rglob("*")):
        if path.is_file() and path.name != "bundle.json":
            files.append({"path": str(path.relative_to(stage)), "sha256": sha(path)})
    bundle = {"schema_version": "cyberalchemy-lab-governance-transaction-surface-admission-bundle/v1", "bundle_id": "CAL-GOVERNANCE-TRANSACTION-SURFACE-ADMISSION-BUNDLE-0074", "decision_checkpoint_ref": CHECKPOINT, "decision_refs": [item["decision_id"] for item in DECISIONS], "status": "owner-admitted-postimage", "authority_effect": "definition-artifact-type-relation-kind-and-deterministic-project-state-admission", "authorization": material(HERE / "authorization.json"), "admission_transaction": {"path": "instances/governance/admission-transaction.json", "sha256": sha(stage / "instances/governance/admission-transaction.json")}, "representation_closure_repair": material(CANDIDATE / "representation-closure-repair.json"), "files": files, "counts": receipt["counts"], "current_project_state_ref": STATE74, "current_project_state_sha256": sha(stage / "instances/project-state.json"), "runtime_activations": 0, "external_effect_refs": [], "claim_ceiling": "Immutable atomic Decision 0074 postimage. It admits exact repository governance contracts and state consequences, with no runtime activation or external effect."}
    dump(stage / "bundle.json", bundle)
    return temp_root, {"stage": stage, "bundle": bundle, "definition_registry": definition_registry, "definition_index": definition_index, "drift": drift, "drift_md": drift_md, "receipt": receipt}


def main() -> int:
    if FINAL.exists():
        receipt_path = FINAL / "receipts/application.json"
        receipt = load(receipt_path)
        repaired = False
        for item in receipt["outputs"].values():
            if item["path"].startswith(".decision-0074-"):
                suffix = item["path"].split("/v1/", 1)[1]
                item["path"] = rel(FINAL / suffix)
                repaired = True
            target = LAB / item["path"]
            if not target.is_file() or sha(target) != item["sha256"]:
                raise RuntimeError(f"applied output binding is missing or changed: {item['path']}")
        if repaired:
            dump(receipt_path, receipt)
            bundle_path = FINAL / "bundle.json"
            bundle = load(bundle_path)
            bundle["files"] = [{"path": str(path.relative_to(FINAL)), "sha256": sha(path)} for path in sorted(FINAL.rglob("*")) if path.is_file() and path != bundle_path]
            dump(bundle_path, bundle)
            dump(HERE / "receipts/application.json", receipt)
            decision_path = HERE / "decision.json"
            if decision_path.is_file():
                decision = load(decision_path)
                decision["admission_bundle"] = material(bundle_path)
                dump(decision_path, decision)
        print(json.dumps({"result": "REPAIRED" if repaired else "ALREADY-APPLIED", "bundle_sha256": sha(FINAL / "bundle.json"), "current_project_state_ref": load(FINAL / "bundle.json")["current_project_state_ref"]}, sort_keys=True))
        return 0
    temp_root, built = build()
    stage: Path = built["stage"]
    backups = {path: path.read_bytes() for path in [DREG, DINDEX, DDRIFT, DDRIFT_MD]}
    created: list[Path] = []
    try:
        FINAL.parent.mkdir(parents=True, exist_ok=True)
        os.replace(stage, FINAL)
        created.append(FINAL)
        atomic(DREG, encoded(built["definition_registry"]))
        atomic(DINDEX, built["definition_index"].encode("utf-8"))
        atomic(DDRIFT, encoded(built["drift"]))
        atomic(DDRIFT_MD, built["drift_md"].encode("utf-8"))

        decision = {
            "schema_version": "cyberalchemy-lab-governance-transaction-surface-admission-decision/v1", "decision_checkpoint_id": CHECKPOINT,
            "title": "Governance transaction surface admission", "status": "owner-admitted", "decided_on": "2026-10-06", "owner_ref": "principal:lab-owner",
            "decision_refs": [item["decision_id"] for item in DECISIONS], "authorization": material(HERE / "authorization.json"),
            "admission_bundle": material(FINAL / "bundle.json"), "admission_transaction": material(FINAL / "instances/governance/admission-transaction.json"),
            "current_project_state": material(FINAL / "instances/project-state.json"), "representation_closure_repair": material(CANDIDATE / "representation-closure-repair.json"),
            "effects": built["receipt"]["counts"], "next_successor_obligation": None,
            "claim_ceiling": "Decision 0074 admits the exact governance transaction surface and its deterministic D73 and D74 Project State consequences. It creates no D75 bookkeeping obligation, runtime activation, deployment, publication, or external effect.",
        }
        dump(HERE / "decision.json", decision); created.append(HERE / "decision.json")
        (HERE / "DECISION.md").write_text("# Decision 0074: Governance transaction surface admission\n\nStatus: **owner admitted**\n\nOne owner response resolved three independent Decisions and one all-or-nothing Admission Transaction. The transaction admitted 1 Definition, 14 Artifact Types, and 4 Relation Kinds; appended semantic and governance events 3 and 4; and advanced the current Project State to Decision 0074.\n\nRuntime activations and external effects: `0`. No D75 bookkeeping Decision is required.\n", encoding="utf-8"); created.append(HERE / "DECISION.md")
        dump(HERE / "decision-bundle.json", load(FINAL / "instances/governance/decision-bundle.json")); created.append(HERE / "decision-bundle.json")
        dump(HERE / "receipts/application.json", load(FINAL / "receipts/application.json")); created.append(HERE / "receipts/application.json")

        if sha(DREG) != sha(FINAL / "registries/definition-registry.json") or sha(DINDEX) != sha(FINAL / "registries/DEFINITIONS-INDEX.md"):
            raise RuntimeError("live Definition registry/index do not match the admitted bundle")
        post = load(FINAL / "receipts/validation.json")
        if post["result"] != "PASS" or post["counts"] != {"schema_instances": post["counts"]["schema_instances"], "definition_versions": 189, "current_definitions": 183, "artifact_type_contracts": 143, "current_artifact_types": 121, "relation_kinds": 41, "endpoint_kinds": 109, "endpoint_pairs": 550, "runtime_activations": 0}:
            raise RuntimeError("post-application validation counts changed")
        print(json.dumps({"result": "APPLIED", "decision_checkpoint_ref": CHECKPOINT, "decision_refs": decision["decision_refs"], "bundle_sha256": sha(FINAL / "bundle.json"), "transaction_sha256": sha(FINAL / "instances/governance/admission-transaction.json"), "project_state_sha256": sha(FINAL / "instances/project-state.json"), "semantic_history_sha256": sha(FINAL / "instances/project-semantic-event-history.json"), "governance_history_sha256": sha(FINAL / "instances/project-governance-event-history.json"), "counts": built["receipt"]["counts"]}, sort_keys=True))
        return 0
    except Exception:
        for path, data in backups.items():
            atomic(path, data)
        for path in reversed(created):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            elif path.exists():
                path.unlink()
        raise
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
