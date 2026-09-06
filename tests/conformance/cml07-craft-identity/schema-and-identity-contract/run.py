#!/usr/bin/env python3
"""Collect CML-07 S3 validation and S4 scoped conformance evidence."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SOURCE_REPO = LAB.parent / "domainspec-core"
SUITE_PATH = ROOT / "suite.json"
VALIDATION_ROOT = LAB / "evidence/validation/cml07-craft-identity/receipts"
CONFORMANCE_ROOT = LAB / "evidence/conformance/cml07-craft-identity/schema-and-identity-contract"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module(
    "cml07_identity_carrier_validator",
    LAB / "tooling/validators/cml07_identity_carrier.py",
)
GENERATOR = load_module(
    "cml07_identity_carrier_generator",
    LAB / "tooling/generators/cml07_identity_carrier.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def result(ok: bool) -> str:
    return "PASS" if ok else "BLOCK"


def render_suite(suite: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical source is suite.json. -->",
        "",
        "# CML-07 Craft Identity Schema and Contract Suite",
        "",
        f"- Suite: `{suite['suite_id']}`",
        f"- Status: `{suite['status']}`",
        f"- Carrier subjects: `{len(suite['subjects'])}`",
        f"- Hostile cases: `{len(suite['hostile_cases'])}`",
        f"- Approval checkpoints before final bundle: `{suite['decision_boundary']['intermediate_approvals']}`",
        f"- Final approval checkpoints: `{suite['decision_boundary']['final_approvals']}`",
        "",
        "## Carrier subjects",
        "",
    ]
    for subject in suite["subjects"]:
        lines.append(
            f"- `{subject['artifact_type_ref']}` → `{subject['machine_path']}` "
            f"(identity field `{subject['identity_field']}`)"
        )
    lines.extend(["", "## Hostile cases", ""])
    for case in suite["hostile_cases"]:
        lines.append(f"- `{case['case_id']}` must reject `{case['expected_rejection']}`")
    lines.extend(
        [
            "",
            "## Single approval boundary",
            "",
            suite["decision_boundary"]["rule"],
            "",
            "## Claim ceiling",
            "",
            suite["claim_ceiling"],
            "",
        ]
    )
    return "\n".join(lines)


def render_receipt(receipt: dict[str, Any], title: str) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical source is the adjacent JSON receipt. -->",
        "",
        f"# {title}",
        "",
        f"- Subject: `{receipt['subject']}`",
        f"- Result: **{receipt['result']}**",
        f"- Checks: `{receipt['summary']['passed']}/{receipt['summary']['total']}`",
        f"- Authority effect: `{receipt['authority_effect']}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{item['check_id']}`: **{item['result']}**" for item in receipt["checks"])
    lines.extend(["", "## Claim ceiling", "", receipt["claim_ceiling"], ""])
    return "\n".join(lines)


def render_assessment(assessment: dict[str, Any]) -> str:
    scopes = assessment["assessment"]
    lines = [
        "<!-- GENERATED FILE: canonical source is assessment.json. -->",
        "",
        "# CML-07 Craft Identity Conformance Assessment",
        "",
        f"- Subject: `{assessment['subject']}`",
        f"- Result: **{assessment['result']}**",
        f"- Validation: `{scopes['validation_result']}`",
        f"- Schema conformance: `{scopes['schema_conformance']}`",
        f"- Identity-contract conformance: `{scopes['identity_contract_conformance']}`",
        f"- Carrier admission: `{scopes['carrier_admission']}`",
        f"- Implementation conformance: `{scopes['implementation_conformance']}`",
        f"- Runtime conformance: `{scopes['runtime_conformance']}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{item['check_id']}`: **{item['result']}**" for item in assessment["checks"])
    lines.extend(["", "## Claim ceiling", "", assessment["claim_ceiling"], ""])
    return "\n".join(lines)


def selected_source_sha(admission: dict[str, Any]) -> tuple[str, str]:
    path = SOURCE_REPO / admission["source_path"]
    file_sha = sha(path) if path.is_file() else "missing"
    if admission["selector_kind"] == "whole-file-v1":
        return file_sha, file_sha
    if admission["selector_kind"] == "line-range-v1" and path.is_file():
        lines = path.read_bytes().splitlines(keepends=True)
        selected = b"".join(lines[admission["start_line"] - 1 : admission["end_line"]])
        return hashlib.sha256(selected).hexdigest(), file_sha
    return "unsupported-selector", file_sha


def set_path(subject: dict[str, Any], path: list[Any], value: Any) -> None:
    cursor: Any = subject
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = value


def main() -> int:
    suite = load(SUITE_PATH)
    (ROOT / "SUITE.md").write_text(render_suite(suite), encoding="utf-8")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": result(ok), "detail": detail})

    dependency_results = {}
    for item in suite["dependencies"]:
        path = LAB / item["path"]
        observed = sha(path) if path.is_file() else "missing"
        dependency_results[item["path"]] = observed
    check(
        "all-selected-dependencies-current",
        all(dependency_results[item["path"]] == item["sha256"] for item in suite["dependencies"]),
        dependency_results,
    )

    decision29 = load(LAB / "docs/decisions/0029-cml07-semantic-foundation-v1/decision.json")
    decision30 = load(LAB / "docs/decisions/0030-cml07-s2-artifact-types-v1/decision.json")
    decision30_receipt = load(
        LAB / "docs/decisions/0030-cml07-s2-artifact-types-v1/receipts/admission-validation.json"
    )
    check(
        "semantic-and-artifact-type-predecessors-admitted",
        decision29.get("status") == "owner-admitted"
        and decision29.get("admission_result", {}).get("definitions_admitted") == 14
        and decision30.get("status") == "owner-admitted"
        and decision30.get("admission_result", {}).get("artifact_types_admitted") == 6
        and decision30_receipt.get("result") == "PASS",
        {
            "semantic_decision": decision29.get("status"),
            "definitions_admitted": decision29.get("admission_result", {}).get("definitions_admitted"),
            "artifact_type_decision": decision30.get("status"),
            "artifact_types_admitted": decision30.get("admission_result", {}).get("artifact_types_admitted"),
            "artifact_type_admission_validation": decision30_receipt.get("result"),
        },
    )

    admissions = load(
        LAB / "authority/decisions/source-admission/craft-identity-v1/v1/admissions.json"
    )
    source_results = []
    for admission in admissions["admissions"]:
        selected_sha, file_sha = selected_source_sha(admission)
        source_results.append(
            {
                "admission_id": admission["admission_id"],
                "selected_sha256": selected_sha,
                "expected_selected_sha256": admission["selected_sha256"],
                "source_file_sha256": file_sha,
                "expected_source_file_sha256": admission["source_file_sha256_at_authoring"],
                "current": selected_sha == admission["selected_sha256"]
                and file_sha == admission["source_file_sha256_at_authoring"],
            }
        )
    check(
        "all-eight-admitted-source-selections-current",
        len(source_results) == 8 and all(item["current"] for item in source_results),
        source_results,
    )

    owners = load(
        LAB / "authority/owners/foundation-01/v1/candidates/0004-craft-identity/owners.json"
    )
    available_roles = {item["role_id"] for item in owners["role_assignments"]}
    required_roles = {subject["owner_ref"].removeprefix("role:") for subject in suite["subjects"]}
    required_roles.add("evidence-conformance-owner")
    check(
        "all-accountable-owner-roles-resolve",
        required_roles <= available_roles,
        {"required": sorted(required_roles), "available_count": len(available_roles)},
    )

    admitted_types = {
        item["artifact_type_ref"]: item for item in decision30["admitted_artifact_types"]
    }
    carriers: dict[str, dict[str, Any]] = {}
    subject_results = []
    individual_receipts = []
    for subject in suite["subjects"]:
        machine_path = LAB / subject["machine_path"]
        projection_path = LAB / subject["projection_path"]
        schema_path = LAB / subject["schema_path"]
        carrier = load(machine_path)
        schema = load(schema_path)
        carriers[subject["subject_id"]] = carrier
        schema_failures = VALIDATOR.schema_errors(carrier, schema)
        semantic_failures = VALIDATOR.semantic_errors(carrier)
        projection_ok = (
            projection_path.is_file()
            and projection_path.read_text(encoding="utf-8") == GENERATOR.render(carrier)
        )
        admitted_type = admitted_types.get(subject["artifact_type_ref"], {})
        type_binding_ok = (
            admitted_type.get("decision_overlay_status") == "admitted-current"
            and admitted_type.get("schema_path") == subject["schema_path"]
            and admitted_type.get("schema_sha256") == sha(schema_path)
        )
        owner_fields = [
            carrier.get("semantic_owner_ref"),
            carrier.get("accountable_owner_ref"),
            carrier.get("binding_owner_ref"),
            carrier.get("lineage_owner_ref"),
            carrier.get("graph_owner_ref"),
        ]
        owner_ok = subject["owner_ref"] in owner_fields
        identity = carrier.get(subject["identity_field"])
        receipt_checks = [
            {"check_id": "closed-schema-validation", "result": result(not schema_failures), "detail": schema_failures or "no schema errors"},
            {"check_id": "carrier-semantic-validation", "result": result(not semantic_failures), "detail": semantic_failures or "no semantic errors"},
            {"check_id": "generated-projection-parity", "result": result(projection_ok), "detail": sha(projection_path) if projection_path.is_file() else "missing"},
            {"check_id": "admitted-artifact-type-binding", "result": result(type_binding_ok), "detail": admitted_type},
            {"check_id": "accountable-owner-binding", "result": result(owner_ok), "detail": subject["owner_ref"]},
        ]
        receipt_failed = [item for item in receipt_checks if item["result"] != "PASS"]
        receipt = {
            "schema_version": "cyberalchemy-lab-cml07-carrier-validation-receipt/v1",
            "subject": identity,
            "artifact_type_ref": subject["artifact_type_ref"],
            "result": "BLOCK" if receipt_failed else "PASS",
            "authority_effect": "none",
            "assessment": {
                "validation_result": "BLOCK" if receipt_failed else "PASS",
                "schema_conformance": "NOT_ESTABLISHED" if schema_failures else "PASS",
                "identity_contract_conformance": "not_evaluable-at-individual-carrier-scope",
                "carrier_admission": "candidate-unadmitted",
                "implementation_conformance": "not_evaluable",
                "runtime_conformance": "not_evaluable",
            },
            "checks": receipt_checks,
            "summary": {"total": len(receipt_checks), "passed": len(receipt_checks) - len(receipt_failed), "blocked": len(receipt_failed)},
            "materials": {
                "machine_path": subject["machine_path"],
                "machine_sha256": sha(machine_path),
                "projection_path": subject["projection_path"],
                "projection_sha256": sha(projection_path) if projection_path.is_file() else "missing",
                "schema_path": subject["schema_path"],
                "schema_sha256": sha(schema_path),
            },
            "source_direction": {
                "canonical": f"{subject['subject_id']}.json",
                "human_projection": f"{subject['subject_id'].upper()}-VALIDATION.md",
                "projection_policy": "generated-only",
                "generator": "tests/conformance/cml07-craft-identity/schema-and-identity-contract/run.py",
            },
            "claim_ceiling": "PASS establishes validation and schema conformance for this exact candidate carrier only. It does not establish cohort identity-contract conformance, admission, implementation conformance, runtime conformance, publication, or deployment.",
        }
        receipt_path = VALIDATION_ROOT / f"{subject['subject_id']}.json"
        receipt_md = VALIDATION_ROOT / f"{subject['subject_id'].upper()}-VALIDATION.md"
        write_json(receipt_path, receipt)
        receipt_md.write_text(render_receipt(receipt, f"{subject['subject_id'].replace('-', ' ').title()} Validation"), encoding="utf-8")
        individual_receipts.append({"subject": identity, "path": str(receipt_path.relative_to(LAB)), "sha256": sha(receipt_path), "result": receipt["result"]})
        subject_results.append(
            {
                "subject_id": subject["subject_id"],
                "identity": identity,
                "schema": result(not schema_failures),
                "semantics": result(not semantic_failures),
                "projection": result(projection_ok),
                "artifact_type_binding": result(type_binding_ok),
                "owner_binding": result(owner_ok),
                "receipt": receipt["result"],
            }
        )
    check(
        "six-carriers-validate-individually",
        len(subject_results) == 6 and all(item["receipt"] == "PASS" for item in subject_results),
        subject_results,
    )

    cohort_failures = VALIDATOR.cohort_errors(carriers)
    check(
        "cohort-identity-contract-closes",
        not cohort_failures,
        cohort_failures or "all carrier identities and required relations resolve without collapse",
    )
    check(
        "no-craft-root-bounded-context-inferred",
        not (LAB / "contexts/craft").exists(),
        "contexts/craft is absent",
    )

    hostile_results = []
    for case in suite["hostile_cases"]:
        mutated = copy.deepcopy(carriers)
        target = mutated[case["target"]]
        if case["operation"] == "set":
            set_path(target, case["path"], case["value"])
        elif case["operation"] == "append-copy":
            cursor: Any = target
            for part in case["path"]:
                cursor = cursor[part]
            cursor.append(copy.deepcopy(cursor[case["source_index"]]))
        else:
            raise ValueError(f"unsupported hostile operation: {case['operation']}")
        subject = next(item for item in suite["subjects"] if item["subject_id"] == case["target"])
        failures = (
            VALIDATOR.schema_errors(target, load(LAB / subject["schema_path"]))
            + VALIDATOR.semantic_errors(target)
            + VALIDATOR.cohort_errors(mutated)
        )
        hostile_results.append(
            {
                "case_id": case["case_id"],
                "expected_rejection": case["expected_rejection"],
                "result": "PASS" if failures else "BLOCK",
                "observed_failures": failures,
            }
        )
    check(
        "all-ten-hostile-collapse-and-inference-cases-rejected",
        len(hostile_results) == 10 and all(item["result"] == "PASS" for item in hostile_results),
        hostile_results,
    )

    all_ids = []
    for subject in suite["subjects"]:
        all_ids.append(carriers[subject["subject_id"]][subject["identity_field"]])
    all_ids.append(carriers["method-binding"]["method_ref"])
    check(
        "all-seven-primary-identities-distinct",
        len(all_ids) == len(set(all_ids)) == 7,
        all_ids,
    )
    check(
        "machine-canonical-human-generated",
        all(item["projection"] == "PASS" for item in subject_results)
        and suite["source_direction"]["projection_policy"] == "generated-only",
        {"carrier_projections": 6, "suite_projection": str((ROOT / 'SUITE.md').relative_to(LAB))},
    )
    check(
        "single-final-approval-boundary",
        suite["decision_boundary"] == {
            "mode": "single-checkpoint",
            "placement": "end-of-complete-cml07-workflow",
            "intermediate_approvals": 0,
            "final_approvals": 1,
            "rule": "All S3 carrier construction and S4 evidence collection complete before one immutable digest-bound owner decision is requested.",
        },
        suite["decision_boundary"],
    )

    failed = [item for item in checks if item["result"] != "PASS"]
    validation_receipt = {
        "schema_version": "cyberalchemy-lab-cml07-craft-identity-validation-receipt/v1",
        "subject": suite["suite_id"],
        "result": "BLOCK" if failed else "PASS",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"total": len(checks), "passed": len(checks) - len(failed), "blocked": len(failed)},
        "individual_receipts": individual_receipts,
        "materials": {
            "suite_path": str(SUITE_PATH.relative_to(LAB)),
            "suite_sha256": sha(SUITE_PATH),
            "suite_projection_sha256": sha(ROOT / "SUITE.md"),
        },
        "source_direction": {
            "canonical": "validation.json",
            "human_projection": "VALIDATION.md",
            "projection_policy": "generated-only",
            "generator": "tests/conformance/cml07-craft-identity/schema-and-identity-contract/run.py",
        },
        "claim_ceiling": suite["claim_ceiling"],
    }
    aggregate_path = VALIDATION_ROOT / "validation.json"
    write_json(aggregate_path, validation_receipt)
    (VALIDATION_ROOT / "VALIDATION.md").write_text(
        render_receipt(validation_receipt, "CML-07 Craft Identity Validation"),
        encoding="utf-8",
    )

    conformance_checks = [
        {"check_id": "aggregate-validation-pass", "result": result(validation_receipt["result"] == "PASS"), "detail": sha(aggregate_path)},
        {"check_id": "six-closed-schema-assessments-pass", "result": result(all(item["schema"] == "PASS" for item in subject_results)), "detail": subject_results},
        {"check_id": "identity-contract-cohort-pass", "result": result(not cohort_failures), "detail": cohort_failures or "closed"},
        {"check_id": "negative-non-collapse-profile-pass", "result": result(all(item["result"] == "PASS" for item in hostile_results)), "detail": hostile_results},
        {"check_id": "carrier-state-remains-candidate", "result": result(all(item["status"] == "candidate-unadmitted" and item["authority_effect"] == "none" for item in carriers.values())), "detail": "six carriers remain non-effectful candidates"},
        {"check_id": "implementation-and-runtime-scopes-not-inferred", "result": "PASS", "detail": {"implementation_conformance": "not_evaluable", "runtime_conformance": "not_evaluable"}},
    ]
    conformance_failed = [item for item in conformance_checks if item["result"] != "PASS"]
    assessment = {
        "schema_version": "cyberalchemy-lab-cml07-schema-and-identity-contract-conformance/v1",
        "assessment_id": "CAL-CML07-CRAFT-IDENTITY-CONFORMANCE-0001",
        "subject": "exact-cml07-craft-identity-carrier-cohort-v1",
        "result": "BLOCK" if conformance_failed else "PASS",
        "authority_effect": "evidence-only",
        "assessment_owner_ref": "role:evidence-conformance-owner",
        "assessment": {
            "validation_result": "BLOCK" if failed else "PASS",
            "schema_conformance": "NOT_ESTABLISHED" if failed else "PASS",
            "identity_contract_conformance": "NOT_ESTABLISHED" if conformance_failed else "PASS",
            "carrier_admission": "candidate-unadmitted",
            "implementation_conformance": "not_evaluable",
            "runtime_conformance": "not_evaluable",
        },
        "checks": conformance_checks,
        "summary": {"total": len(conformance_checks), "passed": len(conformance_checks) - len(conformance_failed), "blocked": len(conformance_failed)},
        "validation_receipt": {"path": str(aggregate_path.relative_to(LAB)), "sha256": sha(aggregate_path)},
        "source_direction": {
            "canonical": "assessment.json",
            "human_projection": "ASSESSMENT.md",
            "projection_policy": "generated-only",
            "generator": "tests/conformance/cml07-craft-identity/schema-and-identity-contract/run.py",
        },
        "claim_ceiling": suite["claim_ceiling"],
    }
    assessment_path = CONFORMANCE_ROOT / "assessment.json"
    write_json(assessment_path, assessment)
    (CONFORMANCE_ROOT / "ASSESSMENT.md").write_text(render_assessment(assessment), encoding="utf-8")

    print(f"CML07_CRAFT_IDENTITY_VALIDATION={validation_receipt['result']}")
    print(f"VALIDATION_CHECKS={validation_receipt['summary']['passed']}/{validation_receipt['summary']['total']}")
    print(f"SCHEMA_AND_IDENTITY_CONFORMANCE={assessment['result']}")
    print(f"CONFORMANCE_CHECKS={assessment['summary']['passed']}/{assessment['summary']['total']}")
    for item in failed:
        print(f"BLOCK {item['check_id']}: {item['detail']}")
    for item in conformance_failed:
        print(f"BLOCK {item['check_id']}: {item['detail']}")
    return 1 if failed or conformance_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
