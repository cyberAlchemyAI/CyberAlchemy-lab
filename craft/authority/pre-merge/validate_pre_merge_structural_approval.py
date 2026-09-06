#!/usr/bin/env python3
"""Fail-closed validator for DomainSpec v2 C12 pre-merge receipts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from typing import Any


PROJECT_PREFIX = "projects/domainspec-v2/"
SCHEMA_VERSION = "domainspec-v2.pre-merge-structural-approval/v1"
DECISION_REF = (
    "projects/domainspec-v2/authority/decisions/"
    "2026-08-24-victor-pre-merge-structural-approval.md"
)
DIGEST_ALGORITHM = "sha256(rfc8785-compatible-canonical-json(sorted-inventory))"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_ID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


class ValidationFailure(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def fail(code: str, message: str) -> None:
    raise ValidationFailure(code, message)


def run_git(repo_root: pathlib.Path, *args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        fail("GIT_COMMAND_FAILED", f"git {' '.join(args)} failed: {detail}")
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def require_exact_keys(value: Any, keys: set[str], location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail("SHAPE_INVALID", f"{location} must be an object")
    actual = set(value)
    if actual != keys:
        fail(
            "KEY_SET_INVALID",
            f"{location} keys differ; missing={sorted(keys - actual)} extra={sorted(actual - keys)}",
        )
    return value


def require_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value:
        fail("VALUE_INVALID", f"{location} must be a nonempty string")
    return value


def require_sha256(value: Any, location: str) -> str:
    text = require_string(value, location)
    if not SHA256_RE.fullmatch(text):
        fail("DIGEST_INVALID", f"{location} must be lowercase SHA-256")
    return text


def require_repo_path(value: Any, location: str, domainspec_only: bool = False) -> str:
    text = require_string(value, location)
    candidate = pathlib.PurePosixPath(text)
    if candidate.is_absolute() or ".." in candidate.parts or "." in candidate.parts:
        fail("PATH_INVALID", f"{location} is not a normalized repository-relative path")
    if str(candidate) != text:
        fail("PATH_INVALID", f"{location} is not normalized")
    if domainspec_only and not text.startswith(PROJECT_PREFIX):
        fail("PATH_OUT_OF_SCOPE", f"{location} must be inside {PROJECT_PREFIX}")
    return text


def require_timestamp(value: Any, location: str) -> str:
    text = require_string(value, location)
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        fail("TIMESTAMP_INVALID", f"{location} must be an ISO-8601 timestamp")
    if parsed.tzinfo is None:
        fail("TIMESTAMP_INVALID", f"{location} must include a timezone")
    return text


def git_blob(repo_root: pathlib.Path, commit: str, path: str) -> bytes:
    return run_git(repo_root, "show", f"{commit}:{path}", binary=True)  # type: ignore[return-value]


def image_for(repo_root: pathlib.Path, commit: str, path: str) -> dict[str, Any]:
    data = git_blob(repo_root, commit, path)
    return {"sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)}


def derive_inventory(repo_root: pathlib.Path, base: str, head: str) -> list[dict[str, Any]]:
    raw = run_git(
        repo_root,
        "diff",
        "--name-status",
        "-z",
        "--no-renames",
        base,
        head,
        binary=True,
    )
    tokens = raw.split(b"\0")  # type: ignore[union-attr]
    entries: list[dict[str, Any]] = []
    cursor = 0
    while cursor < len(tokens) and tokens[cursor]:
        status = tokens[cursor].decode("ascii", errors="strict")
        cursor += 1
        if cursor >= len(tokens) or not tokens[cursor]:
            fail("GIT_DIFF_INVALID", "name-status output ended before a path")
        path = tokens[cursor].decode("utf-8", errors="strict")
        cursor += 1
        require_repo_path(path, "derived inventory path")
        kind = status[:1]
        if kind == "A":
            entry = {
                "path": path,
                "delta_class": "create",
                "before": None,
                "after": image_for(repo_root, head, path),
            }
        elif kind == "D":
            entry = {
                "path": path,
                "delta_class": "delete",
                "before": image_for(repo_root, base, path),
                "after": None,
            }
        elif kind in {"M", "T"}:
            entry = {
                "path": path,
                "delta_class": "modify",
                "before": image_for(repo_root, base, path),
                "after": image_for(repo_root, head, path),
            }
        else:
            fail("GIT_DIFF_STATUS_UNSUPPORTED", f"unsupported git status {status!r} for {path}")
        entries.append(entry)
    entries.sort(key=lambda item: item["path"])
    if not entries:
        fail("EMPTY_CANDIDATE", "the merge candidate changes no paths")
    if not any(entry["path"].startswith(PROJECT_PREFIX) for entry in entries):
        fail("PROJECT_SCOPE_NOT_TOUCHED", "the candidate does not change DomainSpec v2")
    return entries


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_inventory_shape(inventory: Any) -> list[dict[str, Any]]:
    if not isinstance(inventory, list) or not inventory:
        fail("INVENTORY_INVALID", "candidate.inventory must be a nonempty array")
    checked: list[dict[str, Any]] = []
    prior_path = ""
    for index, raw_entry in enumerate(inventory):
        entry = require_exact_keys(
            raw_entry,
            {"path", "delta_class", "before", "after"},
            f"candidate.inventory[{index}]",
        )
        path = require_repo_path(entry["path"], f"candidate.inventory[{index}].path")
        if path <= prior_path:
            fail("INVENTORY_ORDER_INVALID", "candidate inventory paths must be unique and sorted")
        prior_path = path
        delta_class = entry["delta_class"]
        if delta_class not in {"create", "modify", "delete"}:
            fail("DELTA_CLASS_INVALID", f"unsupported delta class at {path}")
        for side in ("before", "after"):
            image = entry[side]
            if image is not None:
                image = require_exact_keys(image, {"sha256", "size_bytes"}, f"{path}.{side}")
                require_sha256(image["sha256"], f"{path}.{side}.sha256")
                if not isinstance(image["size_bytes"], int) or image["size_bytes"] < 0:
                    fail("SIZE_INVALID", f"{path}.{side}.size_bytes must be a nonnegative integer")
        if delta_class == "create" and not (entry["before"] is None and entry["after"] is not None):
            fail("DELTA_IMAGE_INVALID", f"create images invalid for {path}")
        if delta_class == "modify" and not (entry["before"] is not None and entry["after"] is not None):
            fail("DELTA_IMAGE_INVALID", f"modify images invalid for {path}")
        if delta_class == "delete" and not (entry["before"] is not None and entry["after"] is None):
            fail("DELTA_IMAGE_INVALID", f"delete images invalid for {path}")
        checked.append(entry)
    return checked


def validate_receipt(
    repo_root: pathlib.Path,
    receipt_path: pathlib.Path,
    expected_target_branch: str | None,
) -> dict[str, Any]:
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail("RECEIPT_PARSE_FAILED", str(exc))

    top = require_exact_keys(
        receipt,
        {
            "schema_version",
            "receipt_id",
            "decision_ref",
            "constitution_rule",
            "project_scope",
            "target_branch",
            "base_commit",
            "head_commit",
            "semantic_owner",
            "verification_assignment",
            "structural_verifier",
            "candidate",
            "validation_evidence",
            "decision",
            "approved_at",
            "authority_effect",
            "claim_ceiling",
        },
        "receipt",
    )
    if top["schema_version"] != SCHEMA_VERSION:
        fail("SCHEMA_VERSION_INVALID", "unexpected receipt schema version")
    if not re.fullmatch(r"DSV2-PREMERGE-[A-Z0-9][A-Z0-9._-]*", require_string(top["receipt_id"], "receipt_id")):
        fail("RECEIPT_ID_INVALID", "receipt_id does not match the governed format")
    if top["decision_ref"] != DECISION_REF or top["constitution_rule"] != "domainspec-v2-C12":
        fail("GOVERNANCE_BINDING_INVALID", "decision or constitution binding differs")
    if top["project_scope"] != "projects/domainspec-v2":
        fail("PROJECT_SCOPE_INVALID", "project scope differs")
    target_branch = require_string(top["target_branch"], "target_branch")
    if expected_target_branch is None:
        fail("TARGET_BRANCH_EXPECTATION_MISSING", "caller must provide --expected-target-branch")
    if target_branch != expected_target_branch:
        fail("TARGET_BRANCH_MISMATCH", "target branch differs from the caller expectation")

    base = require_string(top["base_commit"], "base_commit")
    head = require_string(top["head_commit"], "head_commit")
    if not GIT_ID_RE.fullmatch(base) or not GIT_ID_RE.fullmatch(head) or base == head:
        fail("COMMIT_ID_INVALID", "base/head must be distinct full Git object IDs")
    resolved_base = run_git(repo_root, "rev-parse", f"{base}^{{commit}}")
    resolved_head = run_git(repo_root, "rev-parse", f"{head}^{{commit}}")
    if resolved_base != base or resolved_head != head:
        fail("COMMIT_ID_NONCANONICAL", "base/head must equal their full resolved commit IDs")
    target_tip = run_git(repo_root, "rev-parse", f"{expected_target_branch}^{{commit}}")
    if target_tip != base:
        fail("TARGET_BRANCH_ADVANCED", "the target branch no longer points at the approved base")
    ancestor = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", base, head],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if ancestor.returncode != 0:
        fail("BASE_NOT_ANCESTOR", "the approved base is not an ancestor of the candidate head")

    owner = require_exact_keys(
        top["semantic_owner"],
        {"principal_id", "display_name", "acceptance_ref", "acceptance_sha256"},
        "semantic_owner",
    )
    if owner["principal_id"] != "rondelli" or owner["display_name"] != "Rondelli":
        fail("SEMANTIC_OWNER_INVALID", "semantic owner must be Rondelli")
    acceptance_ref = require_repo_path(owner["acceptance_ref"], "semantic_owner.acceptance_ref")
    acceptance_digest = require_sha256(owner["acceptance_sha256"], "semantic_owner.acceptance_sha256")
    acceptance_path = repo_root / acceptance_ref
    if not acceptance_path.is_file() or acceptance_path.is_symlink():
        fail("OWNER_ACCEPTANCE_MISSING", "owner acceptance ref is missing or a symlink")
    if hashlib.sha256(acceptance_path.read_bytes()).hexdigest() != acceptance_digest:
        fail("OWNER_ACCEPTANCE_STALE", "owner acceptance digest differs")

    assignment = require_exact_keys(
        top["verification_assignment"],
        {"assigned_by", "level", "assigned_at"},
        "verification_assignment",
    )
    if assignment["assigned_by"] != "rondelli" or assignment["level"] not in {"V1", "V2", "V3"}:
        fail("VERIFICATION_ASSIGNMENT_INVALID", "Rondelli must assign V1, V2, or V3")
    require_timestamp(assignment["assigned_at"], "verification_assignment.assigned_at")

    verifier = require_exact_keys(
        top["structural_verifier"],
        {
            "principal_id",
            "display_name",
            "role",
            "authentication_evidence_ref",
            "authentication_evidence_sha256",
        },
        "structural_verifier",
    )
    if (
        verifier["principal_id"] != "victor-boscaro"
        or verifier["display_name"] != "Victor Boscaro"
        or verifier["role"] != "independent-pre-merge-structural-verifier"
    ):
        fail("VERIFIER_IDENTITY_INVALID", "Victor Boscaro verifier identity or role differs")
    require_string(verifier["authentication_evidence_ref"], "authentication_evidence_ref")
    require_sha256(verifier["authentication_evidence_sha256"], "authentication_evidence_sha256")

    candidate = require_exact_keys(
        top["candidate"],
        {"inventory_digest_algorithm", "inventory_digest", "inventory"},
        "candidate",
    )
    if candidate["inventory_digest_algorithm"] != DIGEST_ALGORITHM:
        fail("DIGEST_ALGORITHM_INVALID", "candidate inventory digest algorithm differs")
    recorded_inventory = validate_inventory_shape(candidate["inventory"])
    recorded_digest = require_sha256(candidate["inventory_digest"], "candidate.inventory_digest")
    if canonical_digest(recorded_inventory) != recorded_digest:
        fail("INVENTORY_SELF_DIGEST_MISMATCH", "recorded inventory does not match its digest")
    derived_inventory = derive_inventory(repo_root, base, head)
    if recorded_inventory != derived_inventory:
        fail("CANDIDATE_INVENTORY_MISMATCH", "recorded inventory differs from the exact Git candidate")

    evidence = top["validation_evidence"]
    if not isinstance(evidence, list) or not evidence:
        fail("VALIDATION_EVIDENCE_MISSING", "validation_evidence must be nonempty")
    seen_evidence: set[str] = set()
    for index, raw_item in enumerate(evidence):
        item = require_exact_keys(
            raw_item,
            {"validator_id", "status", "path", "sha256"},
            f"validation_evidence[{index}]",
        )
        require_string(item["validator_id"], f"validation_evidence[{index}].validator_id")
        if item["status"] != "pass":
            fail("VALIDATION_STATUS_INVALID", f"validation evidence {index} is not pass")
        path = require_repo_path(item["path"], f"validation_evidence[{index}].path", True)
        if path in seen_evidence:
            fail("VALIDATION_EVIDENCE_DUPLICATE", f"duplicate validation evidence path {path}")
        seen_evidence.add(path)
        expected = require_sha256(item["sha256"], f"validation_evidence[{index}].sha256")
        actual = hashlib.sha256(git_blob(repo_root, head, path)).hexdigest()
        if actual != expected:
            fail("VALIDATION_EVIDENCE_STALE", f"validation evidence digest differs for {path}")

    if top["decision"] != "approve":
        fail("DECISION_INVALID", "receipt decision must be approve")
    require_timestamp(top["approved_at"], "approved_at")
    if top["authority_effect"] != "merge-eligibility-only":
        fail("AUTHORITY_EFFECT_INVALID", "authority effect exceeds merge eligibility")
    if top["claim_ceiling"] != (
        "structural-merge-eligibility-only-no-semantic-proof-promotion-release-"
        "deployment-or-production-effect"
    ):
        fail("CLAIM_CEILING_INVALID", "claim ceiling differs from the governed structural ceiling")

    try:
        relative_receipt = receipt_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        relative_receipt = None
    if relative_receipt is not None:
        present = subprocess.run(
            ["git", "-C", str(repo_root), "cat-file", "-e", f"{head}:{relative_receipt}"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode == 0
        if present:
            fail("SELF_REFERENTIAL_RECEIPT", "approval receipt must not be part of the candidate head")

    return {
        "status": "pass",
        "code": "PRE_MERGE_STRUCTURAL_APPROVAL_VALID",
        "receipt_id": top["receipt_id"],
        "target_branch": target_branch,
        "base_commit": base,
        "head_commit": head,
        "verification_level": assignment["level"],
        "changed_path_count": len(derived_inventory),
        "candidate_inventory_digest": recorded_digest,
        "authority_effect": "merge-eligibility-only",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=pathlib.Path)
    parser.add_argument("--receipt", required=True, type=pathlib.Path)
    parser.add_argument("--expected-target-branch")
    args = parser.parse_args()
    try:
        result = validate_receipt(args.repo_root, args.receipt, args.expected_target_branch)
    except ValidationFailure as exc:
        print(json.dumps({"status": "block", "code": exc.code, "message": exc.message}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
