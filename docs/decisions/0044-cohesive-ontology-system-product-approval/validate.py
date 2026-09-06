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
RECEIPT = ROOT / "receipts" / "validation.json"
EXPECTED_COMMAND = "CLOSYS-PAPP-1 candidate=0aae6913d90fc836ff88d0714da695629a92cef81881f8569582eff8666dead5 receipt=26baa86798ebdcadf68f4925c9d0ddf66bc9b1e3b6bff4ba1e7cc3d46c523c42"
EXPECTED_CANDIDATE = "0aae6913d90fc836ff88d0714da695629a92cef81881f8569582eff8666dead5"
EXPECTED_SYSTEM = "977ab3235bc52b3feddc2e8c4e7103349d763ab802f5982534ac409fd1e2c8c9"
EXPECTED_PRODUCT_TEST = "26baa86798ebdcadf68f4925c9d0ddf66bc9b1e3b6bff4ba1e7cc3d46c523c42"
EXPECTED_REQUEST = "92f52b35cbb028eb21cd95f3d02b5afcea60ca5f1d700b2e2af9fa18bc48315f"
EXPECTED_ADMISSIBILITY = "aeb8d90326fd645ba28d5003d9ae94434f4fefcddf48c1b6387fb6ad40ecda57"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current(relative: str, expected: str) -> bool:
    path = LAB / relative
    return path.is_file() and sha(path) == expected


def semantic_errors(decision: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version", "decision_id", "gate_id", "status", "decided_at",
        "decision_source", "subject", "selected_option", "product_approval",
        "downstream_authority", "next_frontier", "non_effects",
        "authority_effect", "source_direction", "claim_ceiling",
    }
    if set(decision) != required:
        errors.append("decision-field-set-mismatch")
    source = decision.get("decision_source", {})
    if source.get("kind") != "explicit-user-command" or source.get("verbatim") != EXPECTED_COMMAND or source.get("observed_count") != 1:
        errors.append("decision-source-mismatch")
    subject = decision.get("subject", {})
    expected = {
        "product_candidate_sha256": EXPECTED_CANDIDATE,
        "ontology_system_sha256": EXPECTED_SYSTEM,
        "product_test_sha256": EXPECTED_PRODUCT_TEST,
        "admissibility_request_sha256": EXPECTED_REQUEST,
        "admissibility_receipt_sha256": EXPECTED_ADMISSIBILITY,
    }
    if any(subject.get(key) != value for key, value in expected.items()):
        errors.append("subject-digest-mismatch")
    selected = decision.get("selected_option", {})
    if selected != {"option_id": "CLOSYS-PAPP-1", "effect": "product-approval-only"} or decision.get("authority_effect") != "product-approval-only":
        errors.append("approval-effect-mismatch")
    approval = decision.get("product_approval", {})
    approval_expected = {
        "state": "approved",
        "identity": EXPECTED_CANDIDATE,
        "validation": "PASS",
        "deterministic_runs": 2,
        "test_cases": 9,
        "hostile_probes": 8,
        "source_count": 15,
        "component_count": 14,
        "relation_count": 15,
        "catalog_package_count": 20,
        "review_group_count": 10,
        "typed_residue_count": 5,
    }
    if any(approval.get(key) != value for key, value in approval_expected.items()):
        errors.append("product-approval-claim-mismatch")
    downstream = decision.get("downstream_authority", {})
    false_keys = set(downstream) - {"separate_post_approval_admission_decision_required"}
    if any(downstream.get(key) is not False for key in false_keys):
        errors.append("downstream-authority-escalation")
    if downstream.get("separate_post_approval_admission_decision_required") is not True:
        errors.append("post-approval-boundary-missing")
    frontier = decision.get("next_frontier", {})
    if frontier.get("eligible") is not True or frontier.get("permitted_effect") != "prepare and validate one exact non-effectful admission candidate":
        errors.append("next-frontier-mismatch")
    direction = decision.get("source_direction", {})
    if direction != {"canonical": "decision.json", "human_projection": "DECISION.md", "projection_policy": "generated-only", "generator": "generator.py"}:
        errors.append("source-direction-mismatch")
    if len(decision.get("non_effects", [])) != 9:
        errors.append("non-effect-coverage-mismatch")
    return errors


def main() -> int:
    decision = load(DECISION)
    subject = decision["subject"]
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    refs = {
        "candidate": (subject["product_candidate_path"], subject["product_candidate_sha256"]),
        "ontology_system": (subject["ontology_system_path"], subject["ontology_system_sha256"]),
        "product_test": (subject["product_test_path"], subject["product_test_sha256"]),
        "admissibility_request": (subject["admissibility_request_path"], subject["admissibility_request_sha256"]),
        "admissibility_receipt": (subject["admissibility_receipt_path"], subject["admissibility_receipt_sha256"]),
    }
    failures = [name for name, (path, digest) in refs.items() if not current(path, digest)]
    add("immutable-subject-bindings", not failures, {"failures": failures, "refs": refs})

    candidate = load(LAB / subject["product_candidate_path"])
    product_test = load(LAB / subject["product_test_path"])
    request = load(LAB / subject["admissibility_request_path"])
    admissibility = load(LAB / subject["admissibility_receipt_path"])
    closure = (
        candidate.get("candidate_id") == subject["product_candidate_id"]
        and candidate.get("status") == "ready-for-product-approval"
        and candidate.get("authority_effect") == "none"
        and candidate.get("product_test", {}).get("result") == "PASS"
        and candidate.get("product_test", {}).get("product_approval_eligible") is True
        and candidate.get("product_test", {}).get("product_approval_granted") is False
        and product_test.get("result") == "PASS"
        and product_test.get("product_approval_eligible") is True
        and product_test.get("admission_authorized") is False
    )
    add("tested-product-eligibility", closure, {"candidate_status": candidate.get("status"), "test_result": product_test.get("result")})

    input_failures = []
    for item in product_test.get("inputs", []):
        path = LAB / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            input_failures.append(item.get("path"))
    add("current-frozen-material-set", len(product_test.get("inputs", [])) == 6 and not input_failures, {"count": len(product_test.get("inputs", [])), "failures": input_failures})

    gate = (
        request.get("decisionId") == decision["decision_id"]
        and any(item.get("optionId") == "CLOSYS-PAPP-1" for item in request.get("candidates", []))
        and admissibility.get("decisionId") == decision["decision_id"]
        and admissibility.get("routeOutcome") == "gate"
        and "CLOSYS-PAPP-1" in admissibility.get("admissibleOptionIds", [])
    )
    add("decision-gate-selection", gate, {"route": admissibility.get("routeOutcome"), "selected": "CLOSYS-PAPP-1"})

    semantics = semantic_errors(decision)
    add("owner-command-and-claim-ceiling", not semantics, semantics)

    spec = importlib.util.spec_from_file_location("approval_generator", ROOT / "generator.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    projection = ROOT / "DECISION.md"
    add("generated-projection-parity", projection.is_file() and projection.read_text(encoding="utf-8") == module.render(decision), sha(projection) if projection.is_file() else "missing")

    probes = []
    mutations = {
        "candidate-digest-substitution": ("subject", "product_candidate_sha256", "0" * 64),
        "receipt-digest-substitution": ("subject", "product_test_sha256", "0" * 64),
        "selection-substitution": ("selected_option", "option_id", "CLOSYS-PAPP-2"),
        "root-admission-escalation": ("downstream_authority", "cohesive_root_admitted", True),
        "child-admission-escalation": ("downstream_authority", "child_ontologies_admitted_by_this_decision", True),
        "deployment-escalation": ("downstream_authority", "deployment_authorized", True),
    }
    for probe_id, (section, key, value) in mutations.items():
        mutated = copy.deepcopy(decision)
        mutated[section][key] = value
        caught = bool(semantic_errors(mutated))
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("mutation-probes", all(item["result"] == "PASS" for item in probes), probes)

    failed = [item["check_id"] for item in checks if item["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    inputs = [DECISION, LAB / subject["product_candidate_path"], LAB / subject["ontology_system_path"], LAB / subject["product_test_path"], LAB / subject["admissibility_request_path"], LAB / subject["admissibility_receipt_path"], ROOT / "DECISION.md", ROOT / "generator.py", ROOT / "validate.py"]
    receipt = {
        "schema_version": "cyberalchemy-lab-cohesive-ontology-system-product-approval-validation/v1",
        "decision_id": decision["decision_id"],
        "gate_id": decision["gate_id"],
        "result": result,
        "stage_state": "PRODUCT_APPROVED" if result == "PASS" else "not_evaluable",
        "failed_checks": failed,
        "checks": checks,
        "product_candidate_id": subject["product_candidate_id"],
        "product_candidate_sha256": subject["product_candidate_sha256"],
        "product_test_sha256": subject["product_test_sha256"],
        "product_approval": "approved" if result == "PASS" else "not_evaluable",
        "cohesive_root_admitted": False,
        "authority_effect": "product-approval-only" if result == "PASS" else "none",
        "inputs": [{"path": str(path.relative_to(LAB)), "sha256": sha(path)} for path in inputs],
        "claim_ceiling": "PASS proves only that the explicit user command approved the exact frozen and tested cohesive Lab ontology-system Product candidate. It grants no root or child admission, runtime adoption, activation, migration, cutover, publication, release, deployment, source retirement, or external effect.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decision_id": receipt["decision_id"], "result": result, "stage_state": receipt["stage_state"], "failed_checks": failed, "product_approval": receipt["product_approval"], "cohesive_root_admitted": False, "authority_effect": receipt["authority_effect"]}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
