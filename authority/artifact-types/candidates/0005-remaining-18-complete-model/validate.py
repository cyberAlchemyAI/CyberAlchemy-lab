#!/usr/bin/env python3
"""Validate the complete remaining-18 Artifact Type review model."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
DEFINITION_REGISTRY = LAB / "authority/definitions/registry.json"
ADMISSIONS = LAB / "authority/artifact-types/admissions/migration-26/v1"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    model = load(ROOT / "model.json")
    examples = load(ROOT / "examples.json")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, result: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if result else "BLOCK", "detail": detail})

    ids = [entry["target_id"] for entry in model["entries"]]
    check("exact-18-unique-targets", len(ids) == 18 and len(set(ids)) == 18 and set(examples) == {entry["slug"] for entry in model["entries"]}, {"target_count": len(ids), "example_count": len(examples)})
    check("candidate-no-authority-effect", model["authority_effect"] == "none" and model["status"] == "candidate-complete-awaiting-one-admission-decision", {"status": model["status"], "authority_effect": model["authority_effect"]})

    live_defs = {
        f"{item['definition_id']}@{item['version']}": item
        for item in load(DEFINITION_REGISTRY)["entries"]
        if item["lifecycle_state"] == "admitted"
    }
    package_results = []
    for entry in model["entries"]:
        paths = {
            "artifact": LAB / entry["artifact_path"], "schema": LAB / entry["schema_path"],
            "example": LAB / entry["example_path"], "materialization": LAB / entry["materialization_path"],
            "receipt": LAB / entry["validation_receipt_path"],
        }
        digests = {
            "artifact": entry["artifact_sha256"], "schema": entry["schema_sha256"],
            "example": entry["example_sha256"], "materialization": entry["materialization_sha256"],
            "receipt": entry["validation_receipt_sha256"],
        }
        present = all(path.is_file() for path in paths.values())
        current = present and all(sha(paths[key]) == digests[key] for key in paths)
        receipt_pass = present and load(paths["receipt"])["result"] == "PASS"
        definitions_admitted = all(ref in live_defs and sha(LAB / live_defs[ref]["path"]) == live_defs[ref]["sha256"] for ref in entry["semantic_definition_refs"])
        example_exact = present and load(paths["example"]) == examples[entry["slug"]]
        refined = entry["artifact_version"] == "1.0.0-candidate.2" and entry["refinement"]["review_state"] == "revision-authorized-before-admission"
        no_prior_overlay = not (ADMISSIONS / f"{entry['slug']}.json").exists()
        package_results.append({
            "target_id": entry["target_id"], "files_present": present, "digests_current": current,
            "package_validation": "PASS" if receipt_pass else "BLOCK", "definitions_admitted": definitions_admitted,
            "example_exact": example_exact, "refined_version": refined, "no_prior_admission_overlay": no_prior_overlay,
            "ok": present and current and receipt_pass and definitions_admitted and example_exact and refined and no_prior_overlay,
        })
    check("all-18-packages-review-ready", len(package_results) == 18 and all(item["ok"] for item in package_results), package_results)

    overlaps = model["overlap_dispositions"]
    allowed_dispositions = {"distinct", "specialized-policy-carrier"}
    check("overlaps-explicit-and-nonduplicate", model["counts"]["exact_duplicates"] == 0 and len(overlaps) == 5 and all(item["disposition"] in allowed_dispositions and item["boundary"] for item in overlaps), overlaps)

    experiment_relations = model["experiment_relations"]
    research_trace = [item for item in experiment_relations if item["relation"] in {"tests-question-from", "preserves-research-trace"}]
    design_example = examples["experiment-design"]
    run_example = examples["experiment-run"]
    check("experiment-research-trace-explicit", len(research_trace) == 2 and bool(design_example["research_refs"]) and design_example["research_refs"] == run_example["research_refs"], {"relations": research_trace, "design_research_refs": design_example["research_refs"], "run_research_refs": run_example["research_refs"]})

    product_relations = [item for item in experiment_relations if "product" in item["relation"]]
    design_product = design_example["product_evaluation_context"]
    run_product = run_example["product_evaluation_context"]
    stable_product_anchors = ["product_ref", "product_thesis_ref", "thesis_hypothesis_refs", "thesis_outcome_refs", "product_capability_refs", "realization_binding_refs"]
    check("experiment-product-context-explicit", len(product_relations) == 2 and design_product is not None and all(design_product[key] == run_product[key] for key in stable_product_anchors), {"relations": product_relations, "design_product_context": design_product, "run_product_context": run_product})

    relation_audit = model["relation_audit"]
    missing_relations = relation_audit["missing_exact_relations"]
    endpoint_gaps = relation_audit["endpoint_gaps"]
    check(
        "relation-gap-audit-complete",
        relation_audit["existing_contract_count"] == 25
        and relation_audit["contract_state"] == "admitted-migration-contract-only"
        and len(missing_relations) == 27
        and len({(item["relation"], item["source"], item["target"]) for item in missing_relations}) == 27
        and len(endpoint_gaps) == 5
        and len(relation_audit["normalization_plan"]) == 17
        and len(relation_audit["reused_existing_relations"]) == 8
        and all(item["missing_sources"] and item["reason"] for item in endpoint_gaps),
        {"existing_contracts": relation_audit["existing_contract_count"], "unmodeled_semantics": len(missing_relations), "endpoint_gaps": len(endpoint_gaps), "normalized_new_relations": len(relation_audit["normalization_plan"]), "reused_existing_relations": len(relation_audit["reused_existing_relations"])},
    )
    check(
        "relation-reference-ambiguities-corrected",
        examples["measurement-result"]["subject_ref"] == examples["experiment-run"]["node_id"]
        and examples["experiment-run"]["design_version_ref"].endswith("@1.0.0-candidate.1")
        and examples["model-instance-binding"]["parent_model_version_ref"].endswith("@1.0.0-candidate.1")
        and "person_reference_ref" in examples["identity-claim"] and "person_ref" not in examples["identity-claim"]
        and "person_reference_ref" in examples["team-membership"] and "person_ref" not in examples["team-membership"],
        {
            "measurement_subject": examples["measurement-result"]["subject_ref"],
            "design_version": examples["experiment-run"]["design_version_ref"],
            "parent_version": examples["model-instance-binding"]["parent_model_version_ref"],
            "identity_claim_endpoint": examples["identity-claim"].get("person_reference_ref"),
            "membership_endpoint": examples["team-membership"].get("person_reference_ref"),
        },
    )

    axis_successor = relation_audit["axis_orthogonal_successor"]
    axis_model_path = LAB / axis_successor["path"]
    axis_receipt_path = LAB / axis_successor["validation_receipt_path"]
    axis_model = load(axis_model_path) if axis_model_path.is_file() else {}
    axis_receipt = load(axis_receipt_path) if axis_receipt_path.is_file() else {}
    check(
        "axis-orthogonal-relation-successor-bound",
        relation_audit["recommendation_state"] == "superseded-by-axis-orthogonal-successor"
        and sha(axis_model_path) == axis_successor["sha256"]
        and sha(axis_receipt_path) == axis_successor["validation_receipt_sha256"]
        and axis_model.get("counts", {}).get("axis_relation_kinds") == 23
        and axis_model.get("counts", {}).get("collapsed_duplicate_kinds") == 19
        and axis_receipt.get("result") == "PASS",
        axis_successor,
    )

    markdown = (ROOT / "MODEL.md").read_text(encoding="utf-8")
    check("human-review-surface-complete", all(entry["artifact_type_ref"] in markdown and json.dumps(examples[entry["slug"]], indent=2, sort_keys=True) in markdown for entry in model["entries"]), {"entries": len(model["entries"]), "full_examples": len(examples)})

    manifest = load(ROOT / "manifest.json")
    results = []
    for item in manifest["files"] + manifest["bound_package_files"]:
        path = LAB / item["path"]
        actual = sha(path) if path.is_file() else "missing"
        results.append({"path": item["path"], "ok": actual == item["sha256"]})
    check("exact-manifest-current", bool(results) and all(item["ok"] for item in results), results)

    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-complete-artifact-type-review-validation/v1",
        "subject": model["model_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "materials": {"model_sha256": sha(ROOT / "model.json"), "examples_sha256": sha(ROOT / "examples.json"), "model_markdown_sha256": sha(ROOT / "MODEL.md"), "manifest_sha256": sha(ROOT / "manifest.json")},
        "claim_ceiling": "PASS establishes one complete, digest-bound, duplicate-audited review surface for the 18 candidate Artifact Type packages and their examples. It does not admit any Artifact Type or instance and does not activate consumers.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"REMAINING_18_COMPLETE_MODEL={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
