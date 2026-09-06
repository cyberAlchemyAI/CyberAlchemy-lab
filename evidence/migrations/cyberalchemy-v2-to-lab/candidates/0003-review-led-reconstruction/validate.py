#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import author
import followups


ROOT = Path(__file__).resolve().parent


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_validation(receipt: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is validation.json. -->",
        "",
        "# Normalized Reconstruction Validation",
        "",
        f'- Result: `{receipt["result"]}`',
        f'- Checks: `{sum(item["result"] == "PASS" for item in receipt["checks"])}/{len(receipt["checks"])}`',
        f'- Authority effect: `{receipt["authority_effect"]}`',
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    for item in receipt["checks"]:
        lines.append(
            f'| `{item["check_id"]}` | `{item["result"]}` | {item["detail"]} |'
        )
    lines.extend(["", "## Claim ceiling", "", receipt["claim_ceiling"], ""])
    return "\n".join(lines)


def main() -> None:
    checks = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append(
            {
                "check_id": check_id,
                "result": "PASS" if condition else "BLOCK",
                "detail": detail,
            }
        )

    candidate = load(ROOT / "candidate.json")
    definitions = load(ROOT / "definition-inventory.json")
    ledger = load(ROOT / "realization-ledger.json")
    pack = load(ROOT / "definition-pack.json")
    ontologies = load(ROOT / "ontology-inventory.json")
    queue = load(ROOT / "review-queue.json")
    review = load(ROOT / "reviews/0001-definition/review.json")
    target_index = load(ROOT / "target-candidate-index.json")
    ontology_review_index = load(ROOT / "ontology-review-index.json")
    d65_successor = load(ROOT / "d65-successor.json")
    decision_request = load(ROOT / "decision-request.json")
    manifest = load(ROOT / "manifest.json")

    check(
        "no-authority-effect",
        candidate.get("authority_effect") == "none",
        "Candidate has no authority effect.",
    )
    check(
        "no-bulk-copy-artifacts",
        not any(
            (ROOT / name).exists()
            for name in ("copy-allowlist.json", "execute.py", "migration.json")
        ),
        "No copy allowlist, executor, or migration transport exists.",
    )
    check(
        "accepted-normalization-bound",
        definitions["normalization_binding"]["sha256"]
        == digest(author.NORMALIZATION_PATH)
        == definitions["owner_decision_binding"]["accepted_normalization_sha256"],
        "The selected normalization bytes are exact and current.",
    )
    check(
        "owner-decision-bound",
        definitions["owner_decision_binding"]["decision_id"]
        == "CAL-DECISION-0012-NORMALIZE-01-DEFAULTS"
        and definitions["owner_decision_binding"]["selected_option"]
        == "NORMALIZE-01-ACCEPT-DEFAULTS"
        and definitions["owner_decision_binding"]["sha256"]
        == digest(author.NORMALIZATION_DECISION_PATH),
        "The owner-selected planning baseline is exact.",
    )
    baseline_digest = hashlib.sha256(
        author.git_blob(
            author.NORMALIZATION_SOURCE_COMMIT,
            "authority/definitions/DEFINITIONS.md",
        )
    ).hexdigest()
    check(
        "baseline-source-bound",
        definitions["source_baseline"]["sha256"]
        == author.NORMALIZATION_SOURCE_SHA256
        == baseline_digest,
        "The source bytes reviewed by NORMALIZE-01 remain retrievable at the exact Git commit.",
    )
    check(
        "current-source-bound",
        definitions["source_current"]["sha256"] == digest(author.DEFINITIONS_PATH),
        "The current CAV2 definition source is exact.",
    )
    check(
        "accepted-decision-closure",
        definitions["accepted_decision_count"] == len(definitions["decisions"]) == 69,
        "All 69 accepted source-definition decisions are preserved.",
    )
    changed = definitions["drift"]["changed_definition_ids"]
    check(
        "focused-source-drift",
        changed == author.EXPECTED_CHANGED_DEFINITION_IDS
        and definitions["drift"]["unchanged_count"] == 68,
        "Only CAV2-D65 changed after normalization; 68 decisions remain closed.",
    )
    check(
        "d65-only-reopened",
        review["source_definition_id"] == "CAV2-D65"
        and review["normalization_successor_required"] is True
        and review["status"] == "open-source-drift",
        "The sole semantic reconsideration is D65 source drift.",
    )
    check(
        "withdrawal-preserved",
        [item["legacy_id"] for item in definitions["withdrawn_definitions"]]
        == [f"CAV2-D{i}" for i in range(70, 82)],
        "CAV2-D70 through CAV2-D81 remain withdrawal records.",
    )

    family_expected = {
        "semantic": 77,
        "artifact-type": 59,
        "profile": 27,
        "relation-kind": 25,
        "derived-surface": 7,
    }
    check(
        "normalized-target-family-closure",
        ledger["family_counts"] == family_expected
        and ledger["target_count"] == sum(family_expected.values()) == 195,
        "All five normalized target families and all 195 targets are present.",
    )
    target_ids = [item["target_id"] for item in ledger["targets"]]
    check(
        "normalized-target-identity-unique",
        len(target_ids) == len(set(target_ids)),
        "Each normalized target identity occurs once in the realization ledger.",
    )
    state_counts = Counter(item["realization_state"] for item in ledger["targets"])
    check(
        "realization-state-counts",
        state_counts == Counter(ledger["state_counts"])
        and sum(state_counts.values()) == 195,
        "Realization states close over every normalized target.",
    )
    check(
        "admission-not-inferred",
        ledger["matching_policy"]["other"].startswith("no admission inferred")
        and all(
            item["realization_refs"]
            for item in ledger["targets"]
            if item["realization_state"] == "realized-admitted-current"
        ),
        "Only exact registry evidence yields a realized state.",
    )
    check(
        "lab-definition-digests-current",
        all(
            item["sha256"] == item["actual_sha256"]
            for item in author.current_lab_definitions()[1]
        ),
        "All current admitted Definition entries used for matching resolve to exact bytes.",
    )
    check(
        "lab-artifact-type-digests-current",
        all(
            item["sha256"] == item["actual_sha256"]
            for item in author.current_lab_artifact_types()[1]
        ),
        "All current admitted Artifact Type entries used for matching resolve to exact bytes.",
    )

    check(
        "define-pack-target-closure",
        pack["required_concept_ids"] == target_ids and len(pack["concepts"]) == 195,
        "The migration Definition Pack handles every normalized target exactly once.",
    )
    check(
        "define-dispositions-valid",
        all(
            item["current_disposition"] in {"reuse", "specialize", "propose", "open"}
            for item in pack["concepts"]
        ),
        "Every target uses one CAV2 Define disposition.",
    )
    check(
        "define-axis-orthogonal",
        "does not replace" in pack["define_method_binding"]["orthogonality_rule"],
        "Define dispositions do not replace accepted migration dispositions.",
    )
    define_registry_binding = next(
        item
        for item in manifest["source_bindings"]
        if item["repository_id"] == "cyberalchemy-v2-source"
        and item["path"] == "define/handled-definitions.json"
    )
    check(
        "define-registry-not-mutated",
        pack["define_method_binding"]["registry_effect"].startswith("none")
        and digest(author.DEFINE_HANDLED_PATH) == define_registry_binding["sha256"],
        "The CAV2 Define handled registry is an exact read-only dependency.",
    )
    open_targets = {
        item["concept_id"]
        for item in pack["concepts"]
        if item["current_disposition"] == "open"
    }
    affected_targets = set(pack["open_questions"][0]["affected_target_ids"])
    check(
        "d65-open-scope",
        open_targets == affected_targets and len(open_targets) == 6,
        "Only the six D65-derived targets are open.",
    )

    expected_authored_ids = {
        item["target_id"]
        for item in ledger["targets"]
        if item["realization_state"] == "unresolved-no-canonical-match"
    }
    indexed_target_ids = {item["target_id"] for item in target_index["entries"]}
    expected_authored_families = {
        "semantic": 69,
        "artifact-type": 50,
        "profile": 25,
        "relation-kind": 25,
        "derived-surface": 7,
    }
    check(
        "target-prototype-index-closure",
        target_index["entry_count"] == len(target_index["entries"]) == 176
        and indexed_target_ids == expected_authored_ids
        and Counter(item["family"] for item in target_index["entries"])
        == Counter(expected_authored_families),
        "All 176 unresolved non-D65 targets have one indexed prototype scaffold across the five normalized families.",
    )
    target_artifacts = [load(ROOT / item["machine_path"]) for item in target_index["entries"]]
    check(
        "target-prototype-digest-closure",
        all(
            digest(ROOT / item["machine_path"]) == item["machine_sha256"]
            and digest(ROOT / item["human_path"]) == item["human_sha256"]
            for item in target_index["entries"]
        ),
        "Every target prototype machine artifact and generated human projection matches its index digest.",
    )
    check(
        "target-prototype-four-facet-closure",
        all(
            artifact["status"] == "prototype-scaffold"
            and artifact["authority_effect"] == "none"
            and set(artifact["four_facets"])
            == {"classification", "schema", "projection", "machine_checkable"}
            for artifact in target_artifacts
        ),
        "Every authored target is explicitly non-authoritative and carries all four artifact facets.",
    )
    semantic_artifacts = [
        artifact for artifact in target_artifacts if artifact["family"] == "semantic"
    ]
    check(
        "semantic-definition-voice-closure",
        len(semantic_artifacts) == 69
        and all(
            set(artifact["definition_voices"])
            == {
                "normative_voice",
                "formal_voice",
                "plain_language_voice",
                "domain_context_voice",
                "boundary",
            }
            for artifact in semantic_artifacts
        ),
        "All 69 semantic prototypes carry distinct normative, formal, plain-language, domain-context, and boundary voices.",
    )
    check(
        "target-human-projections",
        all(
            (ROOT / entry["human_path"]).read_text(encoding="utf-8")
            == followups.render_target(artifact)
            for entry, artifact in zip(target_index["entries"], target_artifacts)
        ),
        "Every target human file is an exact projection of its canonical machine artifact.",
    )

    check(
        "queue-excludes-settled-decisions",
        queue["settled_definition_decisions"]
        == {
            "count": 68,
            "posture": "preserved-not-queued",
            "source_ref": "CAL-NORMALIZE-01",
        },
        "Settled source-definition decisions are not queued again.",
    )
    unresolved_ids = {
        item["target_id"]
        for item in ledger["targets"]
        if item["realization_state"] != "realized-admitted-current"
    }
    check(
        "realization-queue-closure",
        {item["target_id"] for item in queue["realization_units"]} == unresolved_ids,
        "Every unresolved normalized target has one realization unit.",
    )
    check(
        "one-approval-boundary",
        queue["decision_boundary"]["approval_requests_before_checkpoint"] == 0
        and queue["decision_boundary"]["final_request_shape"]
        == "one-request-set-with-distinct-decisions",
        "The chain accumulates distinct decisions for one final approval boundary.",
    )
    check(
        "followup-queue-state",
        queue["ready_count"] == 0
        and queue["authored_count"] == 176
        and queue["blocked_count"] == 6
        and queue["authored_ontology_review_count"] == 10
        and queue["decision_boundary"]["approval_token"]
        == "APPROVE-CAV2-LAB-RECONSTRUCTION-0003",
        "The queue records 176 authored prototypes, six D65 units pending successor selection, ten authored reviews, and one final token.",
    )

    check(
        "ontology-package-closure",
        ontologies["package_count"] == len(ontologies["packages"])
        and ontologies["review_group_count"]
        == len(ontologies["review_groups"])
        == len(queue["ontology_units"]),
        "Every ontology package belongs to a downstream review group.",
    )
    define_business = next(
        item
        for item in ontologies["packages"]
        if item["profile_path"] == "define/business-ontology/PROFILE.json"
    )
    define_materials = {item["path"] for item in define_business["materials"]}
    required_define_materials = {
        "define/business-ontology/SCHEMA-BINDINGS.json",
        "define/business-ontology/TYPE-SELECTION.json",
        "define/business-ontology/MATERIALIZATION-DECISION.json",
        "define/business-ontology/RESIDUE.jsonl",
    }
    check(
        "ontology-control-surfaces-included",
        required_define_materials <= define_materials,
        "Schema bindings, type selection, materialization decision, and residue are inventoried.",
    )
    domainspec_group = next(
        item
        for item in ontologies["review_groups"]
        if item["group_id"] == "domainspec-v2-lineage"
    )
    check(
        "domainspec-routes-to-craft",
        domainspec_group["successor_route"]["product_id"] == "craft"
        and domainspec_group["successor_route"]["legacy_identity_posture"]
        == "preserve-domainspec-identifiers-as-lineage-aliases",
        "DomainSpec-v2 lineage routes to Craft under NORM-OQ-5.",
    )
    check(
        "ontology-after-realization",
        ontologies["sequencing_rule"]
        == "source-ontology-review-may-follow-target-prototype-authorship;ontology-reconstruction-remains-after-target-realization-closure"
        and all(
            item["status"] == "review-authored-awaiting-final-decision"
            for item in queue["ontology_units"]
        ),
        "Ontology reviews are authored after the non-D65 target prototype pass and remain non-authoritative pending the final planning decision.",
    )

    ontology_reviews = [
        load(ROOT / item["machine_path"]) for item in ontology_review_index["entries"]
    ]
    check(
        "ontology-review-index-closure",
        ontology_review_index["entry_count"]
        == len(ontology_review_index["entries"])
        == len(ontologies["review_groups"])
        == 10
        and {
            item["group_id"] for item in ontology_review_index["entries"]
        }
        == {item["group_id"] for item in ontologies["review_groups"]},
        "Each of the ten ontology inventory groups has one indexed review.",
    )
    check(
        "ontology-review-digest-and-projection-closure",
        all(
            digest(ROOT / entry["machine_path"]) == entry["machine_sha256"]
            and digest(ROOT / entry["human_path"]) == entry["human_sha256"]
            and (ROOT / entry["human_path"]).read_text(encoding="utf-8")
            == followups.render_ontology_review(review_artifact)
            for entry, review_artifact in zip(
                ontology_review_index["entries"], ontology_reviews
            )
        ),
        "Every ontology review and generated human view matches its index and renderer.",
    )
    packages_by_profile = {
        item["profile_path"]: item for item in ontologies["packages"]
    }
    groups_by_id = {
        item["group_id"]: item for item in ontologies["review_groups"]
    }
    type_checks = []
    for review_artifact in ontology_reviews:
        expected_type, viable_types, expected_source, selection_required = (
            followups.ontology_type_for(
                groups_by_id[review_artifact["group_id"]], packages_by_profile
            )
        )
        type_checks.append(
            review_artifact["ontology_type"] == expected_type
            and review_artifact["ontology_type_selection"]["viable_types"]
            == viable_types
            and review_artifact["ontology_type_selection"]["source"]
            == expected_source
            and review_artifact["ontology_type_selection"]["user_selection_required"]
            is selection_required
        )
    check(
        "ontology-type-selection-explicit",
        all(type_checks)
        and sum(
            review_artifact["ontology_type_selection"]["user_selection_required"]
            for review_artifact in ontology_reviews
        )
        == 2,
        "Eight ontology group types come directly from source profiles; two dual-ref governance profiles carry explicit business-system-bridge proposals for the final checkpoint.",
    )
    domainspec_review = next(
        item for item in ontology_reviews if item["group_id"] == "domainspec-v2-lineage"
    )
    check(
        "domainspec-review-preserves-lineage-conflict",
        domainspec_review["recommended_disposition"]
        == "route-lineage-to-craft-and-preserve-legacy-aliases"
        and domainspec_review["successor_route"]["product_id"] == "craft"
        and {item["blocker_id"] for item in domainspec_review["blockers"]}
        >= {
            "NORMALIZED-TARGET-REALIZATION-INCOMPLETE",
            "MULTIPLE-CANONICAL-LINEAGE-CLAIMS",
        },
        "The DomainSpec lineage review routes to Craft without hiding its competing canonical claims.",
    )

    expected_d65_targets = [
        "semantic.prototype-first-domainspec-construction-invariant",
        "type.construction-profile",
        "type.construction-binding",
        "type.implementation-binding",
        "profile.prototype-construction-evaluation",
        "profile.product-candidate-evaluation",
    ]
    check(
        "d65-successor-proposal-closure",
        d65_successor["status"] == "candidate-awaiting-final-checkpoint"
        and d65_successor["authority_effect"] == "none"
        and [item["target_id"] for item in d65_successor["recommended_targets"]]
        == expected_d65_targets
        and len(d65_successor["new_axis_rejections"]) == 3
        and (ROOT / "D65-SUCCESSOR.md").read_text(encoding="utf-8")
        == followups.render_d65(d65_successor),
        "The D65 successor retains only independently useful carriers and profiles, rejects redundant axes, and remains a proposal.",
    )
    exact_subjects_ok = all(
        digest(ROOT / subject["path"]) == subject["sha256"]
        for subject in decision_request["exact_subjects"]
    )
    check(
        "single-composite-decision-boundary-ready",
        decision_request["status"] == "ready-for-owner-review"
        and decision_request["approval_token"]
        == "APPROVE-CAV2-LAB-RECONSTRUCTION-0003"
        and len(decision_request["distinct_decisions"]) == 3
        and exact_subjects_ok
        and decision_request["authority_effect"]
        == "planning-selection-only-if-owner-approves"
        and (ROOT / "DECISION-REQUEST.md").read_text(encoding="utf-8")
        == followups.render_decision_request(decision_request),
        "One exact token binds three distinct planning decisions without granting admission or operational authority.",
    )
    check(
        "candidate-followup-summary-current",
        candidate["followup_construction"]
        == {
            "target_candidate_count": 176,
            "target_family_counts": expected_authored_families,
            "ontology_review_count": 10,
            "d65_successor_status": "candidate-awaiting-final-checkpoint",
            "decision_request_status": "ready-for-owner-review",
            "approval_token": "APPROVE-CAV2-LAB-RECONSTRUCTION-0003",
        },
        "The candidate summarizes the complete authored follow-up chain and final checkpoint exactly.",
    )

    expected_projections = {
        "CANDIDATE.md": author.render_candidate(candidate),
        "DEFINITION-INVENTORY.md": author.render_definition_inventory(definitions),
        "REALIZATION-LEDGER.md": author.render_realization_ledger(ledger),
        "DEFINITION-PACK.md": author.render_definition_pack(pack),
        "ONTOLOGY-INVENTORY.md": author.render_ontology_inventory(ontologies),
        "REVIEW-QUEUE.md": author.render_queue(queue),
        "reviews/0001-definition/REVIEW.md": author.render_review(review),
        "TARGET-CANDIDATE-INDEX.md": followups.render_index(
            "Normalized Target Prototype Index",
            "target-candidate-index.json",
            target_index["entries"],
        ),
        "ONTOLOGY-REVIEW-INDEX.md": followups.render_index(
            "Ontology Group Review Index",
            "ontology-review-index.json",
            ontology_review_index["entries"],
        ),
        "MANIFEST.md": author.render_manifest(manifest),
    }
    check(
        "generated-projections",
        all(
            (ROOT / path).read_text(encoding="utf-8") == content
            for path, content in expected_projections.items()
        ),
        "Every declared human view is an exact generated projection.",
    )
    material_ok = all(
        (ROOT / item["path"]).is_file()
        and digest(ROOT / item["path"]) == item["sha256"]
        for item in manifest["materials"]
    )
    check(
        "manifest-material-closure",
        material_ok,
        "Every candidate material matches its manifest digest.",
    )
    roots = {
        "cyberalchemy-lab": author.LAB,
        "cyberalchemy-v2-source": author.SOURCE,
    }
    file_sources_ok = all(
        (roots[item["repository_id"]] / item["path"]).is_file()
        and digest(roots[item["repository_id"]] / item["path"])
        == item["sha256"]
        for item in manifest["source_bindings"]
        if item["kind"] == "file"
    )
    git_sources_ok = all(
        hashlib.sha256(
            author.git_blob(
                item["git_commit"], item["path"].removeprefix("cyberAlchemy-v2/")
            )
        ).hexdigest()
        == item["sha256"]
        for item in manifest["source_bindings"]
        if item["kind"] == "git-blob"
    )
    check(
        "manifest-source-closure",
        file_sources_ok and git_sources_ok,
        "Every repository-relative file and Git-blob source binding is current.",
    )
    check(
        "claim-ceiling",
        "does not select the D65 successor" in candidate["claim_ceiling"]
        and "refine or admit the target artifacts" in candidate["claim_ceiling"],
        "Validation cannot inflate authored prototype scaffolds into refined canonical artifacts, migration completion, or authority.",
    )

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    receipt = {
        "schema_version": "cyberalchemy-lab-normalized-reconstruction-validation/v2",
        "result": result,
        "checks": checks,
        "summary": {
            "passed": sum(item["result"] == "PASS" for item in checks),
            "total": len(checks),
            "normalized_targets": ledger["target_count"],
            "target_prototype_scaffolds": target_index["entry_count"],
            "ontology_group_reviews": ontology_review_index["entry_count"],
            "final_decision_request": decision_request["status"],
            "settled_definition_decisions_preserved": 68,
            "definition_drift_units": 1,
        },
        "authority_effect": "none",
        "claim_ceiling": "PASS proves only that the accepted normalization, focused D65 drift, 195-target realization ledger, 176 non-authoritative prototype scaffolds, ten source-ontology reviews, the D65 successor proposal, the one-token planning request, generated projections, and exact source bindings are internally closed and current. It does not select the proposals, refine or admit artifacts, approve or execute migration, activate runtimes, commit, push, publish, release, or deploy.",
    }
    receipt_path = ROOT / "receipts/validation.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (ROOT / "receipts/VALIDATION.md").write_text(
        render_validation(receipt), encoding="utf-8"
    )
    print(f"NORMALIZED_RECONSTRUCTION={result}")
    print(
        f"CHECKS={sum(item['result'] == 'PASS' for item in checks)}/{len(checks)}"
    )
    if result != "PASS":
        for item in checks:
            if item["result"] != "PASS":
                print(f"BLOCK {item['check_id']}: {item['detail']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
