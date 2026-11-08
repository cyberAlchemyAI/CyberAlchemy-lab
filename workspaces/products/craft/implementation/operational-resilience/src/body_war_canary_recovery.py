"""Durable recovery-ledger model. No Docker operation is performed here."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .body_war_canary_canonical_json import canonical_bytes

EFFECT_EPOCHS = {"prepared": 0, "images-prepared": 1, "project-created": 2, "baseline-run": 3, "candidate-exposed": 4, "fault-active": 5, "rollback": 6, "teardown": 7}


def make_recovery_ledger(run_id: str, project_name: str, receipt_root: str, cleanup_sha256: str) -> dict[str, Any]:
    if not run_id or not project_name.startswith("orodi-bw-") or len(cleanup_sha256) != 64:
        raise ValueError("RECOVERY_LEDGER_IDENTITY_INVALID")
    return {
        "schema_version": "domainspec.orodi.body-war-canary-recovery-ledger/v1",
        "run_id": run_id,
        "project_name": project_name,
        "effect_epoch": 0,
        "expected_resources": ["stable", "candidate", "gateway", "prometheus", "experiment"],
        "allowed_labels": {"com.docker.compose.project": project_name},
        "ports": [18080, 18081, 18101, 18102, 19090],
        "receipt_root": receipt_root,
        "cleanup_executable_sha256": cleanup_sha256,
        "written_before_first_effect": True,
        "recovery_status": "prepared",
        "authority_effect": "none",
    }


def advance_effect(ledger: dict[str, Any], epoch_name: str) -> dict[str, Any]:
    if epoch_name not in EFFECT_EPOCHS:
        raise ValueError("RECOVERY_EFFECT_EPOCH_UNKNOWN")
    next_epoch = EFFECT_EPOCHS[epoch_name]
    current = int(ledger["effect_epoch"])
    if next_epoch != current + 1:
        raise ValueError("RECOVERY_EFFECT_EPOCH_NON_SEQUENTIAL")
    return {**ledger, "effect_epoch": next_epoch, "recovery_status": "effect-known" if next_epoch < 7 else "recovered"}


def classify_recovery(ledger: dict[str, Any], observed_exact_resources: set[str], unknown_matching_resources: set[str]) -> str:
    if unknown_matching_resources:
        return "blocked-unknown-effect"
    expected = set(ledger["expected_resources"])
    if not observed_exact_resources.issubset(expected):
        return "blocked-unknown-effect"
    return "cleanup-required" if observed_exact_resources else "recovered"


def write_ledger_before_effect(path: Path, ledger: dict[str, Any]) -> None:
    if ledger.get("effect_epoch") != 0 or ledger.get("written_before_first_effect") is not True:
        raise ValueError("RECOVERY_LEDGER_NOT_PRE_EFFECT")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(canonical_bytes(ledger) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
