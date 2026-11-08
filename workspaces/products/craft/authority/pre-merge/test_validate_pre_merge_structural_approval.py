#!/usr/bin/env python3
"""Regression tests for the DomainSpec v2 C12 pre-merge validator."""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).with_name("validate_pre_merge_structural_approval.py")
DECISION_REF = (
    "projects/domainspec-v2/authority/decisions/"
    "2026-08-24-victor-pre-merge-structural-approval.md"
)


def git(repo: pathlib.Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return digest(data)


class PreMergeApprovalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.temp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "branch", "-M", "main")
        git(self.repo, "config", "user.email", "fixture@example.invalid")
        git(self.repo, "config", "user.name", "Fixture")

        project = self.repo / "projects/domainspec-v2"
        project.mkdir(parents=True)
        (project / "model.txt").write_text("before\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "checkout", "-qb", "feature")

        (project / "model.txt").write_text("after\n", encoding="utf-8")
        (project / "validation.json").write_text('{"status":"pass"}\n', encoding="utf-8")
        (self.repo / "other.txt").write_text("bundled\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "head")
        self.head = git(self.repo, "rev-parse", "HEAD")

        acceptance = self.repo / "acceptance.json"
        acceptance.write_text('{"status":"accepted"}\n', encoding="utf-8")
        self.acceptance_sha = digest(acceptance.read_bytes())

        before = b"before\n"
        after = b"after\n"
        validation = b'{"status":"pass"}\n'
        bundled = b"bundled\n"
        inventory = [
            {
                "path": "other.txt",
                "delta_class": "create",
                "before": None,
                "after": {"sha256": digest(bundled), "size_bytes": len(bundled)},
            },
            {
                "path": "projects/domainspec-v2/model.txt",
                "delta_class": "modify",
                "before": {"sha256": digest(before), "size_bytes": len(before)},
                "after": {"sha256": digest(after), "size_bytes": len(after)},
            },
            {
                "path": "projects/domainspec-v2/validation.json",
                "delta_class": "create",
                "before": None,
                "after": {"sha256": digest(validation), "size_bytes": len(validation)},
            },
        ]
        self.receipt = {
            "schema_version": "domainspec-v2.pre-merge-structural-approval/v1",
            "receipt_id": "DSV2-PREMERGE-FIXTURE-001",
            "decision_ref": DECISION_REF,
            "constitution_rule": "domainspec-v2-C12",
            "project_scope": "projects/domainspec-v2",
            "target_branch": "main",
            "base_commit": self.base,
            "head_commit": self.head,
            "semantic_owner": {
                "principal_id": "rondelli",
                "display_name": "Rondelli",
                "acceptance_ref": "acceptance.json",
                "acceptance_sha256": self.acceptance_sha,
            },
            "verification_assignment": {
                "assigned_by": "rondelli",
                "level": "V2",
                "assigned_at": "2026-08-24T17:00:00Z",
            },
            "structural_verifier": {
                "principal_id": "victor-boscaro",
                "display_name": "Victor Boscaro",
                "role": "independent-pre-merge-structural-verifier",
                "authentication_evidence_ref": "direct-response:fixture",
                "authentication_evidence_sha256": "1" * 64,
            },
            "candidate": {
                "inventory_digest_algorithm": "sha256(rfc8785-compatible-canonical-json(sorted-inventory))",
                "inventory_digest": canonical_digest(inventory),
                "inventory": inventory,
            },
            "validation_evidence": [
                {
                    "validator_id": "fixture-validation",
                    "status": "pass",
                    "path": "projects/domainspec-v2/validation.json",
                    "sha256": digest(validation),
                }
            ],
            "decision": "approve",
            "approved_at": "2026-08-24T17:01:00Z",
            "authority_effect": "merge-eligibility-only",
            "claim_ceiling": "structural-merge-eligibility-only-no-semantic-proof-promotion-release-deployment-or-production-effect",
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_validator(self, receipt: dict[str, object]) -> tuple[int, dict[str, object]]:
        receipt_path = pathlib.Path(self.temp.name) / "approval.json"
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--repo-root",
                str(self.repo),
                "--receipt",
                str(receipt_path),
                "--expected-target-branch",
                "main",
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.returncode, json.loads(result.stdout)

    def test_exact_candidate_passes(self) -> None:
        code, result = self.run_validator(self.receipt)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["code"], "PRE_MERGE_STRUCTURAL_APPROVAL_VALID")

    def test_candidate_byte_mismatch_blocks(self) -> None:
        changed = json.loads(json.dumps(self.receipt))
        changed["candidate"]["inventory"][0]["after"]["sha256"] = "2" * 64
        changed["candidate"]["inventory_digest"] = canonical_digest(changed["candidate"]["inventory"])
        code, result = self.run_validator(changed)
        self.assertEqual(code, 1)
        self.assertEqual(result["code"], "CANDIDATE_INVENTORY_MISMATCH")

    def test_wrong_verifier_blocks(self) -> None:
        changed = json.loads(json.dumps(self.receipt))
        changed["structural_verifier"]["principal_id"] = "rondelli"
        code, result = self.run_validator(changed)
        self.assertEqual(code, 1)
        self.assertEqual(result["code"], "VERIFIER_IDENTITY_INVALID")

    def test_stale_validation_evidence_blocks(self) -> None:
        changed = json.loads(json.dumps(self.receipt))
        changed["validation_evidence"][0]["sha256"] = "3" * 64
        code, result = self.run_validator(changed)
        self.assertEqual(code, 1)
        self.assertEqual(result["code"], "VALIDATION_EVIDENCE_STALE")

    def test_advanced_target_branch_blocks(self) -> None:
        git(self.repo, "checkout", "-q", "main")
        (self.repo / "target-advanced.txt").write_text("advanced\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "advance target")
        code, result = self.run_validator(self.receipt)
        self.assertEqual(code, 1)
        self.assertEqual(result["code"], "TARGET_BRANCH_ADVANCED")


if __name__ == "__main__":
    unittest.main()
