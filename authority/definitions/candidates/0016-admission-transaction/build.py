#!/usr/bin/env python3
"""Build the Admission Transaction Definition candidate and synchronized postimages."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
DEF_ROOT = ROOT / "definitions/admission-transaction/v1"
SCHEMA = LAB / "authority/artifact-types/definition/v1/schema.json"
GENERATOR = LAB / "authority/artifact-types/definition/v1/generator.py"
REGISTRY = LAB / "authority/definitions/registry.json"
AUDIT = LAB / "authority/governance/candidates/0002-approval-admission-boundary-audit/audit.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    definition = {
        "schema_version": "cyberalchemy-lab-definition/v1",
        "definition_id": "cal.definition.admission-transaction",
        "version": "1.0.0-candidate.1",
        "term": "Admission Transaction",
        "aliases": ["atomic admission application"],
        "classification": {
            "artifact_type_ref": "cal.artifact-type.definition/v1",
            "semantic_kind": "definition",
            "authority_kind": "semantic-authority",
            "lifecycle_posture_ref": "candidate:approval-admission-boundary-repair/v1",
        },
        "semantic_owner_ref": "role:definition-owner",
        "scope": {
            "authority_scope_ref": "scope:cyberalchemy-lab-governance-application",
            "applicability": "Atomic application of one exact, already authorized Decision Bundle and the deterministic repository consequences declared by its member Decisions.",
            "exclusions": [
                "Selecting a Decision outcome or granting authority.",
                "Adding a target, effect, or runtime action absent from the authorized Decision Bundle.",
                "Treating validation success as admission or semantic correctness.",
            ],
        },
        "voices": {
            "scientific_formal": {
                "normative_statement": "An Admission Transaction is a closed, all-or-nothing application record for one exact authorized Decision Bundle. It verifies the bundle digest, each Decision core digest, authorization evidence, input Project State, and every exact admission target before mutation; then it applies all declared effects and their deterministic receipts, event appends, indexes, projections, and Project State successor as one recoverable unit. It creates no authority beyond the selected outcomes of its member Decisions.",
                "formal_expression": "AdmissionTransaction(t) = (bundle, decision_cores, authorization, input_state, targets, consequences, atomicity, receipt, rollback). Apply(t) succeeds iff Authorized(bundle) and PreconditionDigestsMatch(t) and every target/effect is closed in bundle; success commits all targets and consequences, otherwise commits none.",
                "notation": [
                    {"symbol": "t", "meaning": "One exact Admission Transaction."},
                    {"symbol": "bundle", "meaning": "The exact closed Decision Bundle authorized at one checkpoint."},
                    {"symbol": "decision_cores", "meaning": "Acyclic hashes of stable Decision content bound before generated consequences."},
                ],
                "boundary_conditions": [
                    "The transaction applies authority; it does not originate authority.",
                    "A target or effect absent from the reviewed bundle requires a new Decision Checkpoint.",
                    "Runtime, deployment, publication, migration cutover, destructive, or external effects require an explicit Decision member.",
                    "Generated outputs must not create a digest cycle with final Decision records.",
                ],
                "testable_conditions": [
                    "Every applied target has an exact digest and a corresponding selected Decision outcome.",
                    "Every deterministic consequence is declared before application and bound in the application receipt after creation.",
                    "Failure before commit leaves no partially admitted target or advanced Project State.",
                    "The final receipt proves atomic application and records rollback or recovery state.",
                ],
            },
            "plain_language": {
                "normative": False,
                "explanation": "The one atomic operation that turns an already approved bundle into admitted repository state. It checks exactly what was approved, applies all of it together, records the resulting events and state, and adds no new approval of its own.",
            },
            "domain_context": {
                "normative": False,
                "workspace_ref": "/home/vlad_/projects/CyberAlchemy-lab",
                "explanation": "In the Lab, one owner response can resolve several independent Decisions at one checkpoint. The Admission Transaction applies those exact outcomes and creates their deterministic event, registry, projection, receipt, and Project State consequences without asking the owner to approve those consequences again.",
                "examples": [
                    "A single transaction admits six reviewed Artifact Types, appends one semantic event and one governance event, refreshes registries and indexes, and advances Project State.",
                    "If one carrier digest changed after review, the transaction blocks before mutation and a new checkpoint is required.",
                ],
            },
        },
        "boundaries": [
            "Admission Transaction is not Decision, Decision Bundle, Decision Checkpoint, approval evidence, or Agent Action.",
            "Atomic application is not proof of truth, correctness, deployment success, or external effect.",
            "Deterministic Project State advancement is part of the authorized transaction, not a new Decision.",
        ],
        "source_refs": [{
            "source_ref": "CAL-GOVERNANCE-AUDIT-APPROVAL-ADMISSION-BOUNDARIES-0002",
            "selector": "revised_model",
            "content_sha256": sha(AUDIT),
            "admission_posture": "candidate-unadmitted",
            "source_admission_ref": None,
        }],
        "primary_consumer_refs": ["authority/admissions", "authority/decisions", "authority/project-state-transitions"],
        "index_entry": {"index_ref": "candidate:authority/definitions/registry.json", "entry_id": "cal.definition.admission-transaction"},
        "drift_route": {"owner_ref": "role:definition-owner", "audit_ref": "drift-audit-postimage.json", "challenge_ref": "route:definition-governance-challenge"},
        "source_direction": {
            "canonical": "definition.json",
            "human_projection": "DEFINITION.md",
            "projection_policy": "generated-only",
            "generator_ref": "cal.generator.definition-markdown/v1",
            "generator_sha256": sha(GENERATOR),
        },
        "schema_ref": "cal.schema.definition/v1",
        "schema_digest": sha(SCHEMA),
        "evidence_refs": ["authority/governance/candidates/0002-approval-admission-boundary-audit/receipts/validation.json"],
        "residue_refs": ["residue:owner-admission-required", "residue:runtime-implementation-not-created"],
        "typed_relations": [],
        "claim_ceiling": "This candidate defines Admission Transaction semantics. It does not admit the Definition or carrier, authorize a bundle, mutate Project State, or activate a runtime.",
    }
    dump(DEF_ROOT / "definition.json", definition)
    spec = importlib.util.spec_from_file_location("definition_generator", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    (DEF_ROOT / "DEFINITION.md").write_text(module.render(definition), encoding="utf-8")

    live = load(REGISTRY)
    ref = f"{definition['definition_id']}@{definition['version']}"
    entry = {
        "definition_id": definition["definition_id"],
        "version": definition["version"],
        "term": definition["term"],
        "path": str((DEF_ROOT / "definition.json").relative_to(LAB)),
        "sha256": sha(DEF_ROOT / "definition.json"),
        "lifecycle_state": "candidate-unadmitted",
    }
    entries = sorted([*live["entries"], entry], key=lambda item: (item["definition_id"], item["version"]))
    lookup = dict(live["current_lookup"])
    lookup[definition["definition_id"]] = ref
    postimage = {
        "schema_version": "cyberalchemy-lab-definition-registry-postimage/v1",
        "record_id": "cal.registry.definitions/v1-admission-transaction-candidate.1",
        "status": "candidate-postimage",
        "authority_effect": "none",
        "owner_ref": "role:definition-owner",
        "predecessor": {"path": str(REGISTRY.relative_to(LAB)), "sha256": sha(REGISTRY), "entry_count": len(live["entries"]), "current_count": len(live["current_lookup"]), "admission_decision_ref": live["admission_decision_ref"]},
        "entries": entries,
        "proposed_current_lookup": dict(sorted(lookup.items())),
        "source_direction": {"canonical": "registry-postimage.json", "human_projection": "DEFINITIONS-INDEX.md", "projection_policy": "generated-only", "generator_ref": "candidate:cal.generator.admission-transaction-definition-pack/v1"},
        "claim_ceiling": f"This candidate postimage adds {ref} to the proposed Definition registry without changing the live registry.",
    }
    dump(ROOT / "registry-postimage.json", postimage)
    lines = [
        "<!-- GENERATED FILE: canonical data is registry-postimage.json. -->", "", "# Proposed Definition index", "",
        "> Candidate projection; the live canonical registry remains unchanged.", "",
        f"- Proposed definitions: `{len(entries)}`", "- Authority effect: `none`", "",
        "| ID | Version | Term | Lifecycle | Path | Digest |", "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in entries:
        lines.append(f"| `{item['definition_id']}` | `{item['version']}` | {item['term']} | `{item['lifecycle_state']}` | `{item['path']}` | `{item['sha256']}` |")
    lines += ["", "## Claim ceiling", "", postimage["claim_ceiling"], ""]
    (ROOT / "DEFINITIONS-INDEX.md").write_text("\n".join(lines), encoding="utf-8")

    drift = {
        "schema_version": "cyberalchemy-lab-definition-drift-audit-postimage/v1",
        "status": "candidate",
        "authority_effect": "none",
        "subject_ref": ref,
        "registry_postimage_ref": "registry-postimage.json",
        "checks": [
            {"check_id": "decision-non-collapse", "result": "PASS", "detail": "Admission Transaction applies selected outcomes and cannot select them."},
            {"check_id": "bundle-non-collapse", "result": "PASS", "detail": "Decision Bundle is the closed authorization input; Admission Transaction is its atomic application."},
            {"check_id": "checkpoint-non-collapse", "result": "PASS", "detail": "Decision Checkpoint is the human interaction position and has no application authority."},
            {"check_id": "agent-action-non-collapse", "result": "PASS", "detail": "Agent Action records attributable work; Admission Transaction has a specific governance application contract."},
            {"check_id": "project-state-boundary", "result": "PASS", "detail": "Project State is a deterministic consequence and remains a separate artifact identity."},
        ],
        "claim_ceiling": "This audit checks candidate semantic distinctions only and changes no admitted Definition or consumer.",
    }
    dump(ROOT / "drift-audit-postimage.json", drift)


if __name__ == "__main__":
    main()
