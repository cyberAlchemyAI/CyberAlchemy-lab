"""Canonical, size-bounded, protected-value-scanned evidence packaging."""

from __future__ import annotations

import re
from typing import Any

from .body_war_canary_canonical_json import canonical_bytes, canonical_sha256

MAX_EVIDENCE_BYTES = 32 * 1024 * 1024
PROTECTED_PATTERNS = (
    re.compile(r"(?i)bearer\s+[a-z0-9._-]+"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:password|secret|token|api[_-]?key)\s*[:=]\s*[^\s,}]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
)


def scan_protected_values(value: Any) -> tuple[str, ...]:
    findings: list[str] = []
    def visit(item: Any, path: str) -> None:
        if isinstance(item, str):
            if any(pattern.search(item) for pattern in PROTECTED_PATTERNS): findings.append(path)
        elif isinstance(item, list):
            for index, child in enumerate(item): visit(child, f"{path}/{index}")
        elif isinstance(item, dict):
            for key, child in item.items(): visit(child, f"{path}/{key}")
    visit(value, "")
    return tuple(sorted(findings))


def build_evidence_pack(run_id: str, receipts: dict[str, Any], declared_preparation_residue: list[str] | None = None) -> dict[str, Any]:
    required = {"decision", "observer", "teardown"}
    missing = sorted(required - receipts.keys())
    if missing: raise ValueError(f"EVIDENCE_REQUIRED_RECEIPT_MISSING:{','.join(missing)}")
    findings = scan_protected_values(receipts)
    if findings: raise ValueError(f"EVIDENCE_PROTECTED_VALUE_FOUND:{','.join(findings)}")
    raw = canonical_bytes(receipts)
    if len(raw) > MAX_EVIDENCE_BYTES: raise ValueError("EVIDENCE_SIZE_CEILING_EXCEEDED")
    teardown = receipts["teardown"]
    if teardown.get("runtime_project_residue") != []: raise ValueError("EVIDENCE_RUNTIME_PROJECT_RESIDUE")
    return {
        "schema_version": "domainspec.orodi.body-war-canary-evidence-pack/v1",
        "run_id": run_id,
        "raw_pack_sha256": canonical_sha256(receipts),
        "size_bytes": len(raw),
        "complete": True,
        "protected_value_scan": "pass",
        "decision_present": True,
        "observer_present": True,
        "teardown_present": True,
        "runtime_project_residue": [],
        "declared_preparation_residue": declared_preparation_residue or [],
        "evidence_residue": ["frozen-receipts", "raw-manifest"],
        "source_mode": "runtime-receipt-derived-offline-snapshot",
        "runtime_admission": "denied",
        "authority_effect": "none",
    }


def derive_snapshot_boundary(pack: dict[str, Any]) -> dict[str, Any]:
    if pack.get("complete") is not True or pack.get("runtime_admission") != "denied" or pack.get("authority_effect") != "none":
        raise ValueError("EVIDENCE_PACK_NOT_PROJECTABLE")
    return {
        "snapshot_id": f"body-war-{pack['run_id']}",
        "raw_evidence_pack_sha256": pack["raw_pack_sha256"],
        "source_mode": "runtime-receipt-derived-offline-snapshot",
        "runtime_admission": "denied",
        "runtime_admitted_observation_ids": [],
        "eligible_control_ids": [],
        "authority_effect": "none",
    }
