#!/usr/bin/env python3
"""Validate the exact Decision 0071 proposal and bundle postimage."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
HERE = ROOT.parent
LAB = HERE.parents[2]
CANDIDATE = LAB / "authority/operational-foundations/candidates/0001-cyberalchemy-lab-foundation"
POSTIMAGE = ROOT / "bundle-postimage"
RECEIPT = ROOT / "validation.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot() -> dict[str, str]:
    paths = [ROOT / "proposal.json", ROOT / "PROPOSAL.md"]
    paths.extend(sorted(item for item in POSTIMAGE.rglob("*") if item.is_file()))
    return {str(path.relative_to(ROOT)): sha(path) for path in paths}


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    candidate_run = subprocess.run([sys.executable, str(CANDIDATE / "validate.py")], cwd=LAB, text=True, capture_output=True, check=False)
    candidate_receipt = load(CANDIDATE / "receipts/validation.json")
    check("candidate-current-and-pass", candidate_run.returncode == 0 and candidate_receipt["result"] == "PASS", {"returncode": candidate_run.returncode, "stdout": candidate_run.stdout.strip(), "result": candidate_receipt["result"]})

    before = snapshot() if (ROOT / "proposal.json").is_file() else {}
    build_run = subprocess.run([sys.executable, str(ROOT / "build.py")], cwd=LAB, text=True, capture_output=True, check=False)
    after = snapshot()
    check("deterministic-proposal-build", build_run.returncode == 0 and before == after, {"returncode": build_run.returncode, "stdout": build_run.stdout.strip(), "stderr": build_run.stderr.strip(), "changed": sorted(set(before) | set(after)) if before != after else []})

    proposal = load(ROOT / "proposal.json")
    candidate_binding = proposal["inputs"]["foundation_candidate"]
    validation_binding = proposal["inputs"]["candidate_validation"]
    bindings_ok = sha(LAB / candidate_binding["path"]) == candidate_binding["sha256"] and sha(LAB / validation_binding["path"]) == validation_binding["sha256"] and load(LAB / validation_binding["path"])["result"] == "PASS"
    check("input-bindings", bindings_ok, proposal["inputs"])

    bundle = load(POSTIMAGE / "bundle.json")
    file_results = []
    for item in bundle["files"]:
        current = sha(POSTIMAGE / item["path"])
        file_results.append({"path": item["path"], "declared": item["sha256"], "current": current, "match": current == item["sha256"]})
    check("bundle-file-closure", bool(file_results) and all(item["match"] for item in file_results), file_results)

    artifact_admission = load(POSTIMAGE / "artifact-instance-admission.json")
    relation_admission = load(POSTIMAGE / "typed-relation-admission.json")
    foundation_admission = load(POSTIMAGE / "foundation-admission.json")
    exact_counts = artifact_admission["count"] == len(artifact_admission["entries"]) == 9 and relation_admission["count"] == len(relation_admission["entries"]) == 13 and bundle["counts"] == {"artifact_instances_admitted": 9, "typed_relation_instances_admitted": 13, "history_streams_declared": 2, "runtime_activations": 0} and foundation_admission["counts"] == bundle["counts"]
    check("exact-postimage-counts", exact_counts, {"artifact_count": artifact_admission["count"], "relation_count": relation_admission["count"], "bundle_counts": bundle["counts"]})

    source_bindings = []
    for item in artifact_admission["entries"] + relation_admission["entries"]:
        admitted_relative = Path(item["admitted_instance_path"]).relative_to("authority/admissions/cyberalchemy-lab-operational-foundation/v1")
        copied = POSTIMAGE / admitted_relative
        source_bindings.append({"identity": item.get("identity_ref") or item.get("relation_id"), "source_current": sha(LAB / item["source_path"]) == item["source_sha256"], "copy_matches": sha(copied) == item["admitted_instance_sha256"] == item["source_sha256"]})
    check("exact-instance-bindings", all(item["source_current"] and item["copy_matches"] for item in source_bindings), source_bindings)

    effects_ok = proposal["authority_effect"] == "none" and proposal["authorization_present"] is False and proposal["proposed_effects"] == bundle["counts"] and proposal["postimage"]["sha256"] == sha(POSTIMAGE / "bundle.json") and proposal["proposed_effects"]["runtime_activations"] == 0
    check("proposal-authority-boundary", effects_ok, {"authority_effect": proposal["authority_effect"], "authorization_present": proposal["authorization_present"], "effects": proposal["proposed_effects"], "bundle_sha256": sha(POSTIMAGE / "bundle.json")})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-operational-foundation-proposal-validation/v1",
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {"proposal_sha256": sha(ROOT / "proposal.json"), "bundle_sha256": sha(POSTIMAGE / "bundle.json"), "candidate_validation_sha256": sha(CANDIDATE / "receipts/validation.json")},
        "claim_ceiling": "PASS proves the exact proposal and postimage are closed and reproducible. It does not apply the admission.",
    }
    dump(RECEIPT, receipt)
    print(json.dumps({"result": result, "checks": len(checks), **receipt["materials"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
