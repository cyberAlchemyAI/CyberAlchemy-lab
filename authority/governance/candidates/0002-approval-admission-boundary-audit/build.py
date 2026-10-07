#!/usr/bin/env python3
"""Build the approval and admission boundary audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
REGISTRY = LAB / "authority/definitions/registry.json"
TYPE_REGISTRY = LAB / "authority/admissions/project-state-bootstrap/v1/registries/artifact-type-registry.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    definitions = load(REGISTRY)
    types = load(TYPE_REGISTRY)
    required_definitions = [
        "cal.definition.authority-boundary",
        "cal.definition.decision-bundle",
        "cal.definition.decision-checkpoint",
        "cal.definition.user-decision-preference",
        "cal.definition.workflow-decision-profile",
        "cal.definition.decision",
        "cal.definition.decision-scope",
        "cal.definition.derived-refresh",
    ]
    definition_entries = []
    for definition_id in required_definitions:
        current_ref = definitions["current_lookup"][definition_id]
        entry = next(item for item in definitions["entries"] if f"{item['definition_id']}@{item['version']}" == current_ref)
        definition_entries.append({**entry, "current_ref": current_ref})

    required_carriers = [
        "cal.artifact-type.decision/v1",
        "cal.artifact-type.decision-scope/v1",
        "cal.artifact-type.review/v1",
        "cal.artifact-type.authority-boundary/v1",
        "cal.artifact-type.decision-bundle/v1",
        "cal.artifact-type.decision-checkpoint/v1",
        "cal.artifact-type.user-decision-preference/v1",
        "cal.artifact-type.workflow-decision-profile/v1",
        "cal.artifact-type.admission-transaction/v1",
    ]
    admitted_refs = {item["artifact_type_ref"] for item in types["admitted_contracts"]}
    carrier_findings = [
        {"artifact_type_ref": ref, "status": "admitted-current" if ref in admitted_refs else "missing"}
        for ref in required_carriers
    ]

    decisions = []
    for number, slug in [
        (70, "definition-complete-lab-model-admission"),
        (71, "cyberalchemy-lab-operational-foundation-admission"),
        (72, "project-state-bootstrap-admission"),
        (73, "first-governed-agent-work-episode-admission"),
    ]:
        directory = LAB / f"docs/decisions/{number:04d}-{slug}"
        decision = load(directory / "decision.json")
        authorization = load(directory / "authorization.json")
        decisions.append(
            {
                "number": number,
                "decision_id": decision["decision_id"],
                "title": decision["title"],
                "authority_effect": decision["authority_effect"],
                "decision_path": str((directory / "decision.json").relative_to(LAB)),
                "decision_sha256": sha(directory / "decision.json"),
                "authorization_path": str((directory / "authorization.json").relative_to(LAB)),
                "authorization_sha256": sha(directory / "authorization.json"),
                "verbatim_user_authorization": authorization.get("verbatim_user_authorization"),
            }
        )

    pending = LAB / "authority/project-state-transitions/candidates/0002-decision-0073-successor/transition.json"
    audit = {
        "schema_version": "cyberalchemy-lab-approval-admission-boundary-audit/v1",
        "audit_id": "CAL-GOVERNANCE-AUDIT-APPROVAL-ADMISSION-BOUNDARIES-0002",
        "status": "candidate-awaiting-owner-review",
        "authority_effect": "none",
        "question": "Why did the operational foundation require repeated approvals, and where should future approval and admission boundaries be placed?",
        "finding": "The Lab preserved separate decision identities correctly but exposed each dependent admission as a separate human approval. This conflicts with the admitted single Decision Checkpoint interaction model. The model's Definitions are admitted, but five required interaction carriers and an Admission Transaction carrier are missing, so the rule is not executable.",
        "source_bindings": {
            "definition_registry": {"path": str(REGISTRY.relative_to(LAB)), "sha256": sha(REGISTRY)},
            "artifact_type_registry": {"path": str(TYPE_REGISTRY.relative_to(LAB)), "sha256": sha(TYPE_REGISTRY)},
            "definitions": definition_entries,
            "decisions": decisions,
            "pending_successor": {"path": str(pending.relative_to(LAB)), "sha256": sha(pending)},
        },
        "current_boundary_assessment": [
            {"boundary": "D70 integrated semantic and carrier model", "decision_identity": "necessary", "separate_human_checkpoint": "avoidable-if-packaged-upfront", "reason": "It changes the admitted semantic and carrier surface and therefore retains an independent authority act. It could still have been presented in the same Decision Bundle as exact downstream decisions."},
            {"boundary": "D71 operational foundation", "decision_identity": "necessary", "separate_human_checkpoint": "avoidable-if-packaged-upfront", "reason": "It admits operational instances and relations under a different effect boundary. Separate identity is correct; a separate user interaction was not required once its exact target existed."},
            {"boundary": "D72 history contracts and first state bootstrap", "decision_identity": "necessary-under-materialized-target-rule", "separate_human_checkpoint": "caused-by-late-target-materialization", "reason": "The exact history carriers and successor target were produced only after D71. The admitted Decision Bundle rule excludes future unresolved targets, so the process forced another checkpoint. The work should have prepared this dependency before the prior checkpoint."},
            {"boundary": "D73 first Agent work episode", "decision_identity": "necessary", "separate_human_checkpoint": "reasonable-for-new-reviewed-work", "reason": "It introduces new exact Agent, Context, Ontology, Work, classification, state, and relation instances. It is a new reviewable semantic and lifecycle effect."},
            {"boundary": "Proposed D74 admission of the D73 Project State successor", "decision_identity": "unnecessary", "separate_human_checkpoint": "reject", "reason": "The successor is a deterministic governed consequence of Decision 0073. Requiring another approval creates an endless decision-to-state-to-decision chain."},
        ],
        "revised_model": {
            "human_checkpoint_rule": "One bounded work package resolves at most one human Decision Checkpoint. The checkpoint may present one closed Decision Bundle containing multiple independently scoped Decision members.",
            "decision_identity_rule": "Each semantic, lifecycle, authority, runtime, or external effect retains its own Decision identity, Decision Scope, owner, target, digest, exclusions, and invalidation conditions.",
            "admission_transaction_rule": "One owner response authorizes one atomic Admission Transaction over every exact member of the reviewed Decision Bundle and all deterministic consequences declared by those members.",
            "project_state_rule": "Semantic event, governance event, Project State successor, receipts, indexes, and projections that deterministically materialize an authorized effect execute inside the same Admission Transaction and require no second approval.",
            "digest_acyclicity_rule": "Governance events bind a stable decision-core digest and authorization digest. The final Decision record and application receipt may bind the resulting bundle and Project State digests. Generated state must not hash a final record that hashes the generated state.",
            "runtime_rule": "Runtime activation, deployment, publication, migration cutover, destructive action, or external side effect remains a distinct Decision member and must be explicitly present in the reviewed bundle.",
            "new_checkpoint_triggers": [
                "A new semantic choice or interpretation",
                "A new target absent from the reviewed closed bundle",
                "A material target digest change outside an explicitly allowed representation repair",
                "An authority owner, scope, allowed effect, or exclusion change",
                "A runtime, external, destructive, publication, deployment, migration, or cutover effect not already explicit",
                "A challenge, invalidation condition, or failed precondition that changes the decision set",
            ],
            "no_new_checkpoint_for": [
                "Validation of already reviewed exact targets",
                "Atomic application of already authorized admissions",
                "Application receipts and validation receipts",
                "Inventory, index, and derived projection refreshes",
                "Semantic and governance event append operations declared by the authorized transaction",
                "The deterministic Project State successor declared by the authorized transaction",
            ],
        },
        "carrier_gap": {
            "admitted": [ref for ref in required_carriers if ref in admitted_refs],
            "missing": [ref for ref in required_carriers if ref not in admitted_refs],
            "resolution": "Materialize and admit the missing interaction carriers plus Admission Transaction/v1, then bind the Project State transition workflow to decision_mode single.",
            "authorization_semantics": "Use Decision.selected_outcome as the approval or rejection outcome. Do not create a separate Approval semantic node. An authorization envelope may preserve the user utterance and exact bundle digest as evidence for the Decision.",
        },
        "history_disposition": {
            "decisions_0070_through_0073": "preserve-as-admitted-history",
            "rewrite_or_merge": False,
            "pending_decision_0074": "do-not-admit-under-the-old-boundary-pattern",
            "next_bundle": "One checkpoint should review the boundary-model carriers, workflow profile, and disposition of the already materialized D73 successor as independently scoped members of one Decision Bundle.",
        },
        "claim_ceiling": "This audit identifies approval and admission boundary drift and proposes a corrected interaction and transaction model. It does not alter admitted decisions, admit carriers, authorize the pending successor, activate a runtime, or create an external effect.",
    }
    dump(ROOT / "audit.json", audit)
    rows = "\n".join(
        f"| {item['boundary']} | {item['decision_identity']} | {item['separate_human_checkpoint']} | {item['reason']} |"
        for item in audit["current_boundary_assessment"]
    )
    carriers = "\n".join(f"- `{item['artifact_type_ref']}`: **{item['status']}**" for item in carrier_findings)
    (ROOT / "AUDIT.md").write_text(
        "# Approval and admission boundary audit\n\n"
        "Status: **candidate awaiting owner review**\n\n"
        "## Finding\n\n"
        + audit["finding"]
        + "\n\n## Boundary assessment\n\n"
        "| Boundary | Decision identity | Separate checkpoint | Reason |\n"
        "| --- | --- | --- | --- |\n"
        + rows
        + "\n\n## Corrected rule\n\n"
        "One bounded work package gets one human Decision Checkpoint. It may contain several independent Decision members in one Decision Bundle. One response authorizes one atomic Admission Transaction. Deterministic receipts, events, indexes, projections, and the resulting Project State successor are consequences of that transaction and do not create another approval.\n\n"
        "## Carrier coverage\n\n"
        + carriers
        + "\n\n## Current history\n\n"
        "Decisions 0070 through 0073 remain valid immutable history. The pending Decision 0074 pattern should not be applied. The next review package should contain the missing carriers, a single-checkpoint workflow profile, and the already materialized D73 successor as separately scoped members of one bundle.\n\n"
        "## Claim ceiling\n\n"
        + audit["claim_ceiling"]
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"definitions_checked": len(definition_entries), "decisions_reviewed": len(decisions), "carriers_missing": len(audit["carrier_gap"]["missing"]), "result": "BUILT"}, sort_keys=True))


if __name__ == "__main__":
    main()
