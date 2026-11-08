#!/usr/bin/env python3
"""Hostile mutations that the Define runtime evidence harness must reject."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = PACKAGE_ROOT / "scripts/validate.py"
SPEC = importlib.util.spec_from_file_location("define_runtime_evidence_validator", VALIDATOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def load(relative: str) -> dict:
    return json.loads((PACKAGE_ROOT / relative).read_text(encoding="utf-8"))


CASES: list[tuple[str, dict[str, dict]]] = []


def case(name: str, relative: str, mutate) -> None:
    value = load(relative)
    mutate(value)
    CASES.append((name, {relative: value}))


case("unknown-profile-field", "profile.json", lambda value: value.__setitem__("invented", True))
case("source-digest-drift", "profile.json", lambda value: value["subject"]["exact_inputs"][0].__setitem__("sha256", "0" * 64))
case("obligation-row-omitted", "coverage-matrix.json", lambda value: value["rows"].pop())
case("coverage-count-inflation", "coverage-matrix.json", lambda value: value["counts"].__setitem__("addressed", 23))
case("dangling-node-reference", "coverage-matrix.json", lambda value: value["rows"][0]["ontology_node_refs"].append("define-session-runtime.Invented"))
case("runtime-evidence-inflation", "coverage-matrix.json", lambda value: value.__setitem__("runtime_evidence_state", "conformant"))
case("obligation-status-upgrade", "coverage-matrix.json", lambda value: value["rows"][10].__setitem__("current_status_preserved", "not-assessed"))
case("experiment-live-inflation", "experiments/cli-chat-continuity.experiment.json", lambda value: value.__setitem__("execution_mode", "live"))
case("positive-open-work-loss", "fixtures/pass/cli-chat-continuity.json", lambda value: value["scenarios"][0]["after_restart"].__setitem__("current_question_id", None))
case("negative-error-masking", "fixtures/fail/session-mismatch.json", lambda value: value.__setitem__("expected_error_code", "EVIDENCE_OPEN_WORK_LOST"))
case("summary-status-effect", "dry-run-summary.json", lambda value: value["obligation_status_changes"].append("CAP-OBL-DEFINE-011-CLI-CHAT-CONTINUITY:satisfied"))


failures: list[str] = []
for name, overrides in CASES:
    receipt = MODULE.validate_package(overrides=copy.deepcopy(overrides))
    if receipt["status"] != "BLOCK":
        failures.append(name)
    else:
        print(f"PASS {name}")

if failures:
    print("FAILED hostile cases: " + ", ".join(failures))
    raise SystemExit(1)

print(f"PASS {len(CASES)}/{len(CASES)} hostile mutations rejected")
