#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
DECISION = ROOT / "decision.json"
RECEIPT = ROOT / "receipts/validation.json"
EXPECTED_COMMAND = "APPROVE-ONTOLOGY-PRODUCT-V1 candidate=12e9e07a697702c2644090018205bc88fee34b76aff0796425fe3ae4f630f328 receipt=04303ddb928505cc988fc5ad3f9828cb991a270e48e0bf23cddb37a43907595e"
EXPECTED_CANDIDATE = "12e9e07a697702c2644090018205bc88fee34b76aff0796425fe3ae4f630f328"
EXPECTED_RECEIPT = "04303ddb928505cc988fc5ad3f9828cb991a270e48e0bf23cddb37a43907595e"
EXPECTED_PRODUCT_TEST = "f1d7cbaa3e14c74e4ac77e0cb0180740dc3d48b863576a3af75033ea177bea73"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current(relative: Any, expected: Any) -> bool:
    path = LAB / str(relative or "")
    return path.is_file() and sha(path) == expected


def semantic_errors(decision: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_keys = {
        "schema_version", "decision_id", "gate_id", "status", "decided_at",
        "decision_source", "subject", "selected_option", "product_approval",
        "downstream_authority", "non_effects", "authority_effect",
        "source_direction", "claim_ceiling",
    }
    if set(decision) != required_keys:
        errors.append("decision-field-set-mismatch")
    source = decision.get("decision_source", {})
    if (
        source.get("kind") != "explicit-user-command"
        or source.get("verbatim") != EXPECTED_COMMAND
        or source.get("observed_count") != 1
    ):
        errors.append("decision-source-mismatch")
    subject = decision.get("subject", {})
    if (
        subject.get("product_candidate_sha256") != EXPECTED_CANDIDATE
        or subject.get("candidate_validation_sha256") != EXPECTED_RECEIPT
        or subject.get("product_test_sha256") != EXPECTED_PRODUCT_TEST
    ):
        errors.append("subject-digest-mismatch")
    selected = decision.get("selected_option", {})
    if (
        selected.get("option_id") != "APPROVE-ONTOLOGY-PRODUCT-V1"
        or selected.get("effect") != "product-approval-only"
        or decision.get("authority_effect") != "product-approval-only"
    ):
        errors.append("approval-effect-mismatch")
    approval = decision.get("product_approval", {})
    if (
        approval.get("state") != "approved"
        or approval.get("identity") != EXPECTED_CANDIDATE
        or approval.get("candidate_validation") != "PASS"
        or approval.get("product_tests") != "PASS"
        or approval.get("structural_checks") != 9
        or approval.get("rust_product_tests") != 9
        or approval.get("nodes") != 23
        or approval.get("relations") != 24
        or approval.get("typed_residue") != 5
    ):
        errors.append("product-approval-claim-mismatch")
    downstream = decision.get("downstream_authority", {})
    expected_false = {
        "definitions_admitted", "artifact_types_admitted", "contexts_admitted",
        "runtime_adopted", "sources_admitted", "activated", "cutover_authorized",
        "publication_authorized", "release_authorized", "deployment_authorized",
        "source_retirement_authorized", "stable_release_designated",
    }
    if any(downstream.get(key) is not False for key in expected_false):
        errors.append("downstream-authority-escalation")
    if downstream.get("separate_post_approval_decisions_required") is not True:
        errors.append("post-approval-boundary-missing")
    direction = decision.get("source_direction", {})
    if (
        direction.get("canonical") != "decision.json"
        or direction.get("human_projection") != "DECISION.md"
        or direction.get("projection_policy") != "generated-only"
    ):
        errors.append("source-direction-mismatch")
    if len(decision.get("non_effects", [])) != 9:
        errors.append("non-effect-coverage-mismatch")
    return errors


def main() -> int:
    decision = load(DECISION)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    subject = decision["subject"]
    refs = {
        "candidate": (subject["product_candidate_path"], subject["product_candidate_sha256"]),
        "candidate_validation": (subject["candidate_validation_path"], subject["candidate_validation_sha256"]),
        "product_test": (subject["product_test_path"], subject["product_test_sha256"]),
    }
    ref_failures = [name for name, (path, digest) in refs.items() if not current(path, digest)]
    add("immutable-subject-bindings", not ref_failures, {"failures": ref_failures, "refs": refs})

    candidate = load(LAB / subject["product_candidate_path"])
    candidate_receipt = load(LAB / subject["candidate_validation_path"])
    product_test = load(LAB / subject["product_test_path"])
    candidate_closure = (
        candidate.get("candidate_id") == subject["product_candidate_id"]
        and candidate.get("version") == subject["product_candidate_version"]
        and candidate.get("status") == "ready-for-product-approval"
        and candidate.get("authority_effect") == "none"
        and candidate.get("product_approval", {}).get("eligible") is True
        and candidate.get("product_approval", {}).get("granted") is False
        and candidate_receipt.get("result") == "PASS"
        and candidate_receipt.get("candidate_sha256") == EXPECTED_CANDIDATE
        and candidate_receipt.get("summary", {}).get("passed") == 9
        and all(check.get("result") == "PASS" for check in candidate_receipt.get("checks", []))
        and product_test.get("result") == "PASS"
        and product_test.get("summary", {}).get("rust_product_tests") == 9
        and product_test.get("product_approval_granted") is False
    )
    add(
        "tested-product-eligibility",
        candidate_closure,
        {
            "candidate_status": candidate.get("status"),
            "candidate_validation": candidate_receipt.get("result"),
            "product_test": product_test.get("result"),
        },
    )

    material_failures = []
    for item in candidate_receipt.get("material", []):
        path = LAB / str(item.get("path", ""))
        if not path.is_file() or sha(path) != item.get("sha256"):
            material_failures.append(item.get("path"))
    add(
        "current-frozen-material-set",
        len(candidate_receipt.get("material", [])) == 18 and not material_failures,
        {"count": len(candidate_receipt.get("material", [])), "failures": material_failures},
    )

    semantics = semantic_errors(decision)
    add("owner-command-and-claim-ceiling", not semantics, semantics)

    generator_path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("approval_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    projection = ROOT / "DECISION.md"
    add(
        "generated-projection-parity",
        projection.is_file() and projection.read_text(encoding="utf-8") == module.render(decision),
        sha(projection) if projection.is_file() else "missing",
    )

    probes = []
    mutations = {
        "candidate-digest-substitution": ("subject", "product_candidate_sha256", "0" * 64),
        "receipt-digest-substitution": ("subject", "candidate_validation_sha256", "0" * 64),
        "approval-effect-escalation": ("selected_option", "effect", "external-effect"),
        "activation-escalation": ("downstream_authority", "activated", True),
        "publication-escalation": ("downstream_authority", "publication_authorized", True),
    }
    for probe_id, (section, key, value) in mutations.items():
        mutated = copy.deepcopy(decision)
        mutated[section][key] = value
        caught = bool(semantic_errors(mutated))
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("mutation-probes", all(item["result"] == "PASS" for item in probes), probes)

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    inputs = [
        DECISION,
        LAB / subject["product_candidate_path"],
        LAB / subject["candidate_validation_path"],
        LAB / subject["product_test_path"],
        ROOT / "DECISION.md",
        ROOT / "generator.py",
        ROOT / "validate.py",
    ]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-product-approval-validation/v1",
        "decision_id": decision["decision_id"],
        "gate_id": decision["gate_id"],
        "result": result,
        "stage_state": "PRODUCT_APPROVED" if result == "PASS" else "not_evaluable",
        "failed_checks": failed,
        "checks": checks,
        "product_candidate_id": subject["product_candidate_id"],
        "product_candidate_sha256": subject["product_candidate_sha256"],
        "candidate_validation_sha256": subject["candidate_validation_sha256"],
        "product_test_sha256": subject["product_test_sha256"],
        "product_approval": "approved" if result == "PASS" else "not_evaluable",
        "downstream_authority": decision["downstream_authority"],
        "authority_effect": "product-approval-only" if result == "PASS" else "none",
        "inputs": [
            {"path": str(path.relative_to(LAB)), "sha256": sha(path)} for path in inputs
        ],
        "claim_ceiling": "PASS proves only that the explicit user command approved the exact frozen and tested Ontology Product candidate. It grants no admission, adoption, activation, cutover, publication, release, deployment, stable-release, source-retirement, or external-effect authority.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "decision_id": receipt["decision_id"],
        "result": receipt["result"],
        "stage_state": receipt["stage_state"],
        "failed_checks": receipt["failed_checks"],
        "product_approval": receipt["product_approval"],
        "authority_effect": receipt["authority_effect"],
    }, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
