#!/usr/bin/env python3
"""Validate the dry-run Define Session Runtime evidence contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
MATERIAL_FILES = (
    "README.md",
    "profile.json",
    "coverage-matrix.json",
    "gaps.json",
    "dry-run-summary.json",
    "schemas/conformance-evidence.schema.json",
    "experiments/cli-chat-continuity.experiment.json",
    "fixtures/pass/cli-chat-continuity.json",
    "fixtures/fail/missing-metadata.json",
    "fixtures/fail/session-mismatch.json",
    "fixtures/fail/revision-digest-mismatch.json",
    "fixtures/fail/question-disappears.json",
    "fixtures/fail/live-run-not-implemented.json",
    "scripts/validate.py",
    "tests/test_negative_mutations.py",
)
FIXTURE_PATHS = (
    "fixtures/pass/cli-chat-continuity.json",
    "fixtures/fail/missing-metadata.json",
    "fixtures/fail/session-mismatch.json",
    "fixtures/fail/revision-digest-mismatch.json",
    "fixtures/fail/question-disappears.json",
    "fixtures/fail/live-run-not-implemented.json",
)
INSTANCE_SPECS = (
    ("profile.json", "profile"),
    ("coverage-matrix.json", "coverageMatrix"),
    ("gaps.json", "gapRegistry"),
    ("dry-run-summary.json", "dryRunSummary"),
    ("experiments/cli-chat-continuity.experiment.json", "experimentSpec"),
    *((path, "runFixture") for path in FIXTURE_PATHS),
)
CLAIM_CEILING = (
    "Closed project-local evidence schemas, exact current source bindings, 23-row "
    "model coverage, synthetic bidirectional fixture discrimination, obligation-status "
    "preservation, runtime_evidence_state not_evaluable, status_effect none, and "
    "authority_effect none only; no implemented runtime, obligation satisfaction, "
    "behavioral conformance, adoption, execution, publication, release, deployment, "
    "or external effect."
)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(
    path: Path,
    label: str,
    errors: list[str],
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    relative = path.relative_to(PACKAGE_ROOT).as_posix() if path.is_relative_to(PACKAGE_ROOT) else None
    if overrides and relative in overrides:
        value = overrides[relative]
    else:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot load {label}: {exc}")
            return {}
    if not isinstance(value, dict):
        errors.append(f"{label} must contain one JSON object")
        return {}
    return value


def validate_instance(
    schema: dict[str, Any],
    definition: str,
    value: dict[str, Any],
    label: str,
    errors: list[str],
) -> None:
    wrapper = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": schema.get("$defs", {}),
        "$ref": f"#/$defs/{definition}",
    }
    for violation in sorted(Draft202012Validator(wrapper).iter_errors(value), key=lambda item: list(item.path)):
        locator = ".".join(str(part) for part in violation.path)
        errors.append(f"{label}{'.' + locator if locator else ''}: {violation.message}")


def material_digest(errors: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(MATERIAL_FILES):
        path = PACKAGE_ROOT / relative
        if not path.is_file():
            errors.append(f"missing material file: {relative}")
            continue
        digest.update(relative.encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


@lru_cache(maxsize=1)
def live_system_validation() -> tuple[int, dict[str, Any] | None, str]:
    script = REPOSITORY_ROOT / "cyberAlchemy-v2/define/system-ontology/scripts/validate.py"
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    run = subprocess.run(
        [sys.executable, str(script)],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(run.stdout)
    except json.JSONDecodeError:
        payload = None
    return run.returncode, payload, run.stderr.strip()


def pointer_parts(pointer: str) -> list[str]:
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer.lstrip("/").split("/")]


def apply_mutation(value: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(value)
    parts = pointer_parts(mutation.get("json_pointer", ""))
    if not parts:
        raise ValueError("mutation pointer must select a child")
    target: Any = result
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    last = parts[-1]
    if mutation.get("operation") == "remove":
        if isinstance(target, list):
            target.pop(int(last))
        else:
            target.pop(last)
    elif mutation.get("operation") == "replace":
        if isinstance(target, list):
            target[int(last)] = copy.deepcopy(mutation.get("value"))
        else:
            target[last] = copy.deepcopy(mutation.get("value"))
    else:
        raise ValueError("unsupported mutation operation")
    return result


def required_snapshot_metadata_present(snapshot: dict[str, Any]) -> bool:
    required = {
        "interface",
        "session_id",
        "schema_version",
        "revision",
        "state_digest",
        "current_question_id",
        "open_question_ids",
        "question_records",
        "non_answer_ids",
        "conflict_ids",
        "open_gap_ids",
        "refresh_route",
        "handoff_ref",
        "inferred_answer_count",
        "authority_effect",
    }
    question_required = {"question_id", "state", "reason", "owner_ref", "blocked_use", "next_action"}
    records = snapshot.get("question_records")
    return required <= set(snapshot) and isinstance(records, list) and bool(records) and all(
        isinstance(record, dict) and question_required <= set(record) for record in records
    )


def semantic_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in snapshot.items() if key != "interface"}


def evaluate_fixture(fixture: dict[str, Any]) -> tuple[str, str | None]:
    if fixture.get("execution_mode") == "live" and fixture.get("subject_implementation_status") == "not-implemented":
        return "rejected", "EVIDENCE_LIVE_SUBJECT_NOT_IMPLEMENTED"
    scenarios = fixture.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 2:
        return "rejected", "EVIDENCE_METADATA_INCOMPLETE"
    if {item.get("direction") for item in scenarios if isinstance(item, dict)} != {"cli-to-chat", "chat-to-cli"}:
        return "rejected", "EVIDENCE_DIRECTION_INCOMPLETE"
    for scenario in scenarios:
        before = scenario.get("before_restart", {})
        persisted = scenario.get("persisted_after_restart", {})
        after = scenario.get("after_restart", {})
        if not all(isinstance(item, dict) and required_snapshot_metadata_present(item) for item in (before, persisted, after)):
            return "rejected", "EVIDENCE_METADATA_INCOMPLETE"
        expected_interfaces = ("cli", "storage", "chat") if scenario.get("direction") == "cli-to-chat" else ("chat", "storage", "cli")
        if (before.get("interface"), persisted.get("interface"), after.get("interface")) != expected_interfaces:
            return "rejected", "EVIDENCE_DIRECTION_INCOMPLETE"
        if len({before.get("session_id"), persisted.get("session_id"), after.get("session_id")}) != 1:
            return "rejected", "EVIDENCE_SESSION_IDENTITY_MISMATCH"
        if len({before.get("schema_version"), persisted.get("schema_version"), after.get("schema_version")}) != 1:
            return "rejected", "EVIDENCE_SESSION_IDENTITY_MISMATCH"
        if len({before.get("revision"), persisted.get("revision"), after.get("revision")}) != 1 or len(
            {before.get("state_digest"), persisted.get("state_digest"), after.get("state_digest")}
        ) != 1:
            return "rejected", "EVIDENCE_REVISION_DIGEST_MISMATCH"
        open_work_fields = (
            "current_question_id",
            "open_question_ids",
            "question_records",
            "non_answer_ids",
            "conflict_ids",
            "open_gap_ids",
            "refresh_route",
            "handoff_ref",
        )
        if any(before.get(field) != persisted.get(field) or before.get(field) != after.get(field) for field in open_work_fields):
            return "rejected", "EVIDENCE_OPEN_WORK_LOST"
        if any(item.get("inferred_answer_count") != 0 or item.get("authority_effect") != "none" for item in (before, persisted, after)):
            return "rejected", "EVIDENCE_AUTHORITY_OR_INFERENCE_DRIFT"
        if semantic_snapshot(before) != semantic_snapshot(persisted) or semantic_snapshot(before) != semantic_snapshot(after):
            return "rejected", "EVIDENCE_STATE_MISMATCH"
    return "dry-run-shape-pass", None


def validate_package(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    schema = load_json(PACKAGE_ROOT / "schemas/conformance-evidence.schema.json", "evidence schema", errors, overrides)
    if schema:
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            errors.append(f"evidence schema invalid: {exc}")

    documents: dict[str, dict[str, Any]] = {}
    for relative, definition in INSTANCE_SPECS:
        value = load_json(PACKAGE_ROOT / relative, relative, errors, overrides)
        documents[relative] = value
        if schema and value:
            validate_instance(schema, definition, value, relative, errors)

    profile = documents["profile.json"]
    matrix = documents["coverage-matrix.json"]
    local_gaps = documents["gaps.json"]
    summary = documents["dry-run-summary.json"]
    experiment = documents["experiments/cli-chat-continuity.experiment.json"]
    pass_fixture = documents["fixtures/pass/cli-chat-continuity.json"]

    expected_inputs = {
        "cyberAlchemy-v2/define/system-ontology/PROFILE.json",
        "cyberAlchemy-v2/define/system-ontology/NODES.json",
        "cyberAlchemy-v2/define/system-ontology/RELATIONS.json",
    }
    declared_inputs = {item.get("path") for item in profile.get("subject", {}).get("exact_inputs", []) if isinstance(item, dict)}
    if declared_inputs != expected_inputs:
        errors.append("profile exact system input inventory changed")
    for item in profile.get("subject", {}).get("exact_inputs", []):
        path = REPOSITORY_ROOT / item.get("path", "")
        if not path.is_file() or item.get("sha256") != sha256(path.read_bytes()):
            errors.append(f"profile source digest mismatch: {item.get('path')}")

    obligation_binding = profile.get("obligation_registry", {})
    obligation_path = REPOSITORY_ROOT / obligation_binding.get("path", "")
    obligation_doc = load_json(obligation_path, "obligation registry", errors)
    if not obligation_path.is_file() or obligation_binding.get("sha256") != sha256(obligation_path.read_bytes()):
        errors.append("obligation registry digest mismatch")
    obligations = obligation_doc.get("obligations", [])
    obligation_status = {
        item.get("obligation_id"): item.get("current_status") for item in obligations if isinstance(item, dict)
    }
    if obligation_doc.get("registry_id") != matrix.get("obligation_registry_ref") or len(obligation_status) != 23:
        errors.append("coverage matrix obligation registry identity or count mismatch")

    system_profile = load_json(REPOSITORY_ROOT / "cyberAlchemy-v2/define/system-ontology/PROFILE.json", "system profile", errors)
    if system_profile.get("implementation_status") != "not-implemented" or profile.get("subject", {}).get("implementation_status") != "not-implemented":
        errors.append("runtime evidence package may only target the declared not-implemented subject")
    system_exit, system_live, system_stderr = live_system_validation()
    if system_live is None:
        errors.append(f"cannot parse live system validation output: exit={system_exit} stderr={system_stderr}")
    else:
        if system_live.get("overall") != "FLAG" or system_exit != 2:
            errors.append("profile expects the current system source validation state FLAG")
        if system_live.get("material_digest") != profile.get("subject", {}).get("source_material_digest"):
            errors.append("profile source_material_digest does not match live system validation")
        warnings.append("current Define system ontology validation is source-current FLAG because DomainSpec compilation is not evaluable; this package evaluates evidence shape only")

    nodes_doc = load_json(REPOSITORY_ROOT / "cyberAlchemy-v2/define/system-ontology/NODES.json", "system nodes", errors)
    relations_doc = load_json(REPOSITORY_ROOT / "cyberAlchemy-v2/define/system-ontology/RELATIONS.json", "system relations", errors)
    source_gaps_doc = load_json(REPOSITORY_ROOT / "cyberAlchemy-v2/define/system-ontology/design/GAPS.json", "system design gaps", errors)
    witnesses_doc = load_json(REPOSITORY_ROOT / "cyberAlchemy-v2/define/system-ontology/design/PLANNED-WITNESSES.json", "planned witnesses", errors)
    node_ids = {item.get("node_id") for item in nodes_doc.get("nodes", []) if isinstance(item, dict)}
    relation_ids = {item.get("relation_id") for item in relations_doc.get("relations", []) if isinstance(item, dict)}
    source_gap_ids = {item.get("gap_id") for item in source_gaps_doc.get("gaps", []) if isinstance(item, dict)}
    witness_ids = {item.get("witness_id") for item in witnesses_doc.get("witnesses", []) if isinstance(item, dict)}
    residue_ids: set[str] = set()
    residue_path = REPOSITORY_ROOT / "cyberAlchemy-v2/define/system-ontology/RESIDUE.jsonl"
    try:
        for line in residue_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                residue_ids.add(json.loads(line).get("residue_id"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load system residue: {exc}")
    local_gap_items = local_gaps.get("gaps", [])
    local_gap_ids = {item.get("gap_id") for item in local_gap_items if isinstance(item, dict)}
    if len(local_gap_ids) != len(local_gap_items):
        errors.append("duplicate local evidence gap IDs")

    rows = matrix.get("rows", [])
    row_ids = [row.get("obligation_id") for row in rows if isinstance(row, dict)]
    if row_ids != list(obligation_status):
        errors.append("coverage matrix must preserve the exact 23-obligation order and identity")
    coverage_counts = {state: sum(row.get("model_coverage") == state for row in rows) for state in ("addressed", "partial", "gap")}
    expected_counts = {"addressed": 4, "partial": 14, "gap": 5}
    if coverage_counts != expected_counts or any(matrix.get("counts", {}).get(key) != value for key, value in expected_counts.items()):
        errors.append(f"coverage counts changed: expected {expected_counts}, found {coverage_counts}")
    for row in rows:
        obligation_id = row.get("obligation_id")
        if row.get("current_status_preserved") != obligation_status.get(obligation_id):
            errors.append(f"obligation status drift in coverage row {obligation_id}")
        if row.get("runtime_evidence_state") != "not_evaluable":
            errors.append(f"runtime evidence inflation in coverage row {obligation_id}")
        if any(ref not in node_ids for ref in row.get("ontology_node_refs", [])):
            errors.append(f"dangling ontology node reference in coverage row {obligation_id}")
        if any(ref not in relation_ids for ref in row.get("ontology_relation_refs", [])):
            errors.append(f"dangling ontology relation reference in coverage row {obligation_id}")
        if any(ref not in witness_ids for ref in row.get("planned_witness_refs", [])):
            errors.append(f"dangling planned witness reference in coverage row {obligation_id}")
        if any(ref not in source_gap_ids for ref in row.get("source_gap_refs", [])):
            errors.append(f"dangling source gap reference in coverage row {obligation_id}")
        if any(ref not in residue_ids for ref in row.get("source_residue_refs", [])):
            errors.append(f"dangling source residue reference in coverage row {obligation_id}")
        if any(ref not in local_gap_ids for ref in row.get("local_gap_refs", [])):
            errors.append(f"dangling local gap reference in coverage row {obligation_id}")
        if row.get("status_effect", "none") != "none":
            errors.append(f"coverage row {obligation_id} attempts a status effect")
    for gap in local_gap_items:
        if any(ref not in obligation_status for ref in gap.get("blocks_obligation_refs", [])):
            errors.append(f"local gap {gap.get('gap_id')} has dangling obligation reference")

    if matrix.get("runtime_evidence_state") != "not_evaluable" or matrix.get("status_effect") != "none":
        errors.append("coverage matrix must preserve not_evaluable runtime evidence and status_effect none")
    if summary.get("runtime_evidence_state") != "not_evaluable" or summary.get("obligation_status_changes") != []:
        errors.append("dry-run summary attempts to change obligation or runtime evidence status")

    expected_directions = {"cli-to-chat", "chat-to-cli"}
    pass_directions = {item.get("direction") for item in pass_fixture.get("scenarios", []) if isinstance(item, dict)}
    if pass_directions != expected_directions or pass_fixture.get("base_fixture_ref") is not None or pass_fixture.get("mutation") is not None:
        errors.append("positive fixture must contain exactly the two inline directional scenarios")
    outcome, error_code = evaluate_fixture(pass_fixture)
    if outcome != pass_fixture.get("expected_outcome") or error_code is not None or pass_fixture.get("expected_error_code") is not None:
        errors.append(f"positive fixture evaluation mismatch: outcome={outcome} error={error_code}")

    fail_paths = list(FIXTURE_PATHS[1:])
    observed_failures: list[str] = []
    for relative in fail_paths:
        fixture = documents[relative]
        if fixture.get("base_fixture_ref") != FIXTURE_PATHS[0] or "scenarios" in fixture:
            errors.append(f"negative fixture {relative} must derive only from the exact positive fixture")
            continue
        try:
            effective = apply_mutation(pass_fixture, fixture.get("mutation", {}))
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            errors.append(f"cannot apply negative fixture {relative}: {exc}")
            continue
        outcome, error_code = evaluate_fixture(effective)
        if outcome != fixture.get("expected_outcome") or error_code != fixture.get("expected_error_code"):
            errors.append(
                f"negative fixture {relative} evaluation mismatch: expected {fixture.get('expected_error_code')} found {error_code}"
            )
        else:
            observed_failures.append(error_code or "")
    if len(set(observed_failures)) != 5:
        errors.append("five negative fixtures must discriminate five distinct rejection codes")

    declared_pass = experiment.get("pass_fixture_ref")
    declared_fail = experiment.get("fail_fixture_refs", [])
    if declared_pass != FIXTURE_PATHS[0] or declared_fail != fail_paths:
        errors.append("experiment fixture inventory differs from the exact evidence corpus")
    if experiment.get("execution_mode") != "synthetic-dry-run" or experiment.get("live_execution_status") != "blocked-not-implemented":
        errors.append("experiment may not claim live execution")
    if experiment.get("primary_obligation_ref") != "CAP-OBL-DEFINE-011-CLI-CHAT-CONTINUITY" or experiment.get("planned_witness_ref") != "WIT-DES-001":
        errors.append("experiment obligation or witness binding changed")

    checks = [
        "closed JSON Schema and instance shapes",
        "exact current obligation and system-source digest bindings",
        "live system validation remains source-current FLAG and implementation not-implemented",
        "exact 23-row obligation identity, status, and coverage-count preservation",
        "ontology node, relation, witness, design-gap, residue, and local-gap closure",
        "runtime_evidence_state not_evaluable and status_effect none",
        "bidirectional complete-open-work synthetic fixture shape",
        "five distinct negative fixture rejection codes",
        "no obligation status mutation or aggregate conformance claim",
    ]
    receipt = {
        "schema_ref": "schemas/conformance-evidence.schema.json#/$defs/validationReceipt",
        "schema_version": "cav2-define-runtime-evidence-validation/v1",
        "validated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "PASS" if not errors else "BLOCK",
        "package_root": "cyberAlchemy-v2/define/capabilities/evidence/define-session-runtime",
        "evidence_mode": "dry-run-only",
        "runtime_evidence_state": "not_evaluable",
        "counts": {
            "obligations": len(rows),
            "model_addressed": coverage_counts["addressed"],
            "model_partial": coverage_counts["partial"],
            "model_gaps": coverage_counts["gap"],
            "pass_fixtures": 1,
            "reject_fixtures": len(fail_paths),
            "checks": len(checks),
        },
        "material_digest": material_digest(errors),
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "authority_effect": "none",
        "claim_ceiling": CLAIM_CEILING,
    }
    if schema:
        receipt_errors: list[str] = []
        validate_instance(schema, "validationReceipt", receipt, "validation receipt", receipt_errors)
        if receipt_errors:
            receipt["errors"].extend(receipt_errors)
            receipt["status"] = "BLOCK"
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = validate_package()
    if args.write_receipt:
        receipts = PACKAGE_ROOT / "receipts"
        receipts.mkdir(parents=True, exist_ok=True)
        stamp = receipt["validated_at"].replace(":", "").replace("-", "").replace(".", "")
        path = receipts / f"validation-{stamp}.json"
        path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        receipt["receipt_path"] = str(path.relative_to(REPOSITORY_ROOT))
    if args.json or args.write_receipt:
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
    else:
        print(
            f"{receipt['status']} Define runtime evidence obligations={receipt['counts']['obligations']} "
            f"coverage={receipt['counts']['model_addressed']}/{receipt['counts']['model_partial']}/"
            f"{receipt['counts']['model_gaps']} errors={len(receipt['errors'])}"
        )
        for error in receipt["errors"]:
            print(f"ERROR {error}")
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
