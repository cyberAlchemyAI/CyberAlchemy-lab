#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
DECISION = ROOT / "decision.json"
RECEIPT = ROOT / "receipts/decision-validation.json"
EXPECTED_COMMAND = "do it"
EXPECTED_CANDIDATE = "5ebe011a083babcc383ca9ec0ea341be8448e18db65911a1a54d55dcf1e5860c"
EXPECTED_BINDING = "28253f456733f75650cea4f52440c302de575c7c0e4af58a5cedab23afb65e9d"
EXPECTED_PRODUCT_TEST = "a9aba1894ae529e39dd532ff6bd23016f9c9c38381023fa985821061522d8a95"
EXPECTED_REQUEST = "93508d2b37626a28fcd7da8d440d92c7964b2faf755f0f019fe87996056e3769"
EXPECTED_ADMISSIBILITY = "97bf36c7cf5cacdc06342842a880e50b6eb33e5d7bf7eb1d9fdb1523b9862641"


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
        "binding_sha256": EXPECTED_BINDING,
        "product_test_sha256": EXPECTED_PRODUCT_TEST,
        "admissibility_request_sha256": EXPECTED_REQUEST,
        "admissibility_receipt_sha256": EXPECTED_ADMISSIBILITY,
    }
    if any(subject.get(key) != value for key, value in expected.items()):
        errors.append("subject-digest-mismatch")
    selected = decision.get("selected_option", {})
    if selected != {"option_id": "EVRT-PAPP-1", "effect": "product-approval-only"} or decision.get("authority_effect") != "product-approval-only":
        errors.append("approval-effect-mismatch")
    approval = decision.get("product_approval", {})
    approval_expected = {
        "state": "approved",
        "identity": EXPECTED_CANDIDATE,
        "validation": "PASS",
        "deterministic_rust_runs": 2,
        "rust_test_cases": 15,
        "candidate_validator_tests": 5,
        "cli_materializations": 2,
        "node_count": 14,
        "relation_count": 15,
        "semantic_event_count": 29,
        "governance_event_count": 29,
        "latest_snapshot_count": 29,
        "acceptance_material_count": 19,
        "runtime_event_tree_sha256": "b279aa1d9ed049f68dd14f77bc4e7be8f41d3e6483e21564a62907bcc592b1b2",
    }
    if any(approval.get(key) != value for key, value in approval_expected.items()):
        errors.append("product-approval-claim-mismatch")
    downstream = decision.get("downstream_authority", {})
    false_keys = set(downstream) - {"separate_binding_admission_decision_required"}
    if any(downstream.get(key) is not False for key in false_keys):
        errors.append("downstream-authority-escalation")
    if downstream.get("separate_binding_admission_decision_required") is not True:
        errors.append("post-approval-boundary-missing")
    frontier = decision.get("next_frontier", {})
    if frontier.get("eligible") is not True or frontier.get("permitted_effect") != "prepare and validate one exact non-effectful implementation-binding admission candidate":
        errors.append("next-frontier-mismatch")
    direction = decision.get("source_direction", {})
    if direction != {"canonical": "decision.json", "human_projection": "DECISION.md", "projection_policy": "generated-only", "generator": "generator.py"}:
        errors.append("source-direction-mismatch")
    if len(decision.get("non_effects", [])) != 8:
        errors.append("non-effect-coverage-mismatch")
    return errors


def build_receipt() -> dict[str, Any]:
    decision = load(DECISION)
    subject = decision["subject"]
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    refs = {
        "candidate": [subject["product_candidate_path"], subject["product_candidate_sha256"]],
        "binding": [subject["binding_path"], subject["binding_sha256"]],
        "product_test": [subject["product_test_path"], subject["product_test_sha256"]],
        "admissibility_request": [subject["admissibility_request_path"], subject["admissibility_request_sha256"]],
        "admissibility_receipt": [subject["admissibility_receipt_path"], subject["admissibility_receipt_sha256"]],
    }
    failures = [name for name, (path, digest) in refs.items() if not current(path, digest)]
    add("immutable-subject-bindings", not failures, {"failures": failures, "refs": refs})

    candidate = load(LAB / subject["product_candidate_path"])
    binding = load(LAB / subject["binding_path"])
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
        and binding.get("status") == "test-candidate"
        and binding.get("authority_effect") == "none"
        and binding.get("runtime_source", {}).get("adopted") is False
        and product_test.get("result") == "PASS"
        and product_test.get("candidate_sha256") == EXPECTED_CANDIDATE
        and product_test.get("binding_sha256") == EXPECTED_BINDING
        and product_test.get("product_approval_eligible") is True
        and product_test.get("product_approval_granted") is False
        and product_test.get("authority_effect") == "none"
    )
    add("tested-product-eligibility", closure, {"candidate_status": candidate.get("status"), "test_result": product_test.get("result")})

    material_failures = []
    material = candidate.get("acceptance_material", [])
    for item in material:
        path = LAB / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            material_failures.append(item.get("path"))
    add("current-frozen-material-set", len(material) == 19 and not material_failures, {"count": len(material), "failures": material_failures})

    gate = (
        request.get("decisionId") == decision["decision_id"]
        and any(item.get("optionId") == "EVRT-PAPP-1" and item.get("structuralStatus") == "admissible" for item in request.get("candidates", []))
        and admissibility.get("decisionId") == decision["decision_id"]
        and admissibility.get("routeOutcome") == "gate"
        and admissibility.get("decisionGateRequired") is True
        and "EVRT-PAPP-1" in admissibility.get("admissibleOptionIds", [])
        and not admissibility.get("rejectedOptions")
    )
    add("decision-gate-selection", gate, {"route": admissibility.get("routeOutcome"), "selected": "EVRT-PAPP-1"})

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
        "binding-digest-substitution": ("subject", "binding_sha256", "0" * 64),
        "receipt-digest-substitution": ("subject", "product_test_sha256", "0" * 64),
        "selection-substitution": ("selected_option", "option_id", "EVRT-PAPP-2"),
        "binding-admission-escalation": ("downstream_authority", "implementation_binding_admitted", True),
        "runtime-adoption-escalation": ("downstream_authority", "rust_runtime_adopted", True),
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
    inputs = [
        DECISION,
        LAB / subject["product_candidate_path"],
        LAB / subject["binding_path"],
        LAB / subject["product_test_path"],
        LAB / subject["admissibility_request_path"],
        LAB / subject["admissibility_receipt_path"],
        ROOT / "DECISION.md",
        ROOT / "generator.py",
        ROOT / "validate.py",
    ]
    return {
        "schema_version": "cyberalchemy-lab-ontology-event-runtime-product-approval-validation/v1",
        "decision_id": decision["decision_id"],
        "gate_id": decision["gate_id"],
        "result": result,
        "stage_state": "PRODUCT_APPROVED" if result == "PASS" else "not_evaluable",
        "failed_checks": failed,
        "checks": checks,
        "product_candidate_id": subject["product_candidate_id"],
        "product_candidate_sha256": subject["product_candidate_sha256"],
        "binding_sha256": subject["binding_sha256"],
        "product_test_sha256": subject["product_test_sha256"],
        "product_approval": "approved" if result == "PASS" else "not_evaluable",
        "implementation_binding_admitted": False,
        "runtime_adopted": False,
        "runtime_activated": False,
        "authority_effect": "product-approval-only" if result == "PASS" else "none",
        "inputs": [{"path": str(path.relative_to(LAB)), "sha256": sha(path)} for path in inputs],
        "claim_ceiling": "PASS proves only that the explicit user command approved the exact frozen and tested event-runtime realization Product candidate. It grants no implementation-binding admission, runtime adoption or activation, child admission, migration, cutover, publication, release, deployment, source retirement, or external effect.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = build_receipt()
    rendered = json.dumps(receipt, indent=2) + "\n"
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(rendered, encoding="utf-8")
    print(json.dumps({
        "decision_id": receipt["decision_id"],
        "result": receipt["result"],
        "stage_state": receipt["stage_state"],
        "failed_checks": receipt["failed_checks"],
        "product_approval": receipt["product_approval"],
        "implementation_binding_admitted": False,
        "runtime_adopted": False,
        "runtime_activated": False,
        "authority_effect": receipt["authority_effect"],
    }, indent=2))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
