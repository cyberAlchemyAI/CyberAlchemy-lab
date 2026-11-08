"""Inert, pinned public authority worksheet; no role or effect execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
SOURCES = {
    "original": ("product/lab/release-candidates/v1/release-validation/0001/final-materializer-selection-0276.json", "c5f290c5f5bebbbf3b8572a9b3457d265e9ab632a35e6b4cc5a4a78dd2f99465"),
    "composed": ("product/lab/release-candidates/v1/release-validation/0001/final-materializer-selection-0276-composed-v3.json", "a9da357abf6a70b7db456e599f119cd0fef271881cad6a7f5c9966b8fc325da6"),
    "prior_matrix": ("docs/plans/0011-lab-runtime-completion/runs/0001-execution/T12/owner-prerequisites-0001/candidate-owner-effect-matrix.json", "24bd05bee504f53806638bd8d443d36135cf0d7319a289fd912b1513c150c94b"),
    "public_readpoint": ("docs/plans/0011-lab-runtime-completion/runs/0001-execution/T12/current-native-owner-authority-readpoint-0001/REPORT.json", "e507fcada0259774b60d15bae8d2318d130bd06dbfc4f9a5abddf145db348ff5"),
    "public_review": ("docs/plans/0011-lab-runtime-completion/runs/0001-execution/T12/current-native-owner-authority-independent-review-0001/review.json", "15c1a5efbe58dbbf850605fb2e0f3a93ce15da8a1cc1ccab8c6bc9371383ad4a"),
}
OUTPUT = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U10-03/owner-matrix-worksheet-0001.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_sources(root: Path = ROOT) -> dict:
    result = {}
    for name, (relative, expected) in SOURCES.items():
        path = root / relative
        data = path.read_bytes()
        if expected:
            require(digest(data) == expected, f"source drift: {name}")
        result[name] = json.loads(data)
    readpoint = result["public_readpoint"]
    for binding in readpoint["source_bindings"] + [item["binding"] for item in readpoint["admitted_instance_ledgers"]]:
        relative = binding["path"]
        require(not Path(relative).is_absolute() and ".." not in Path(relative).parts, "unsafe source locator")
        require(digest((root / relative).read_bytes()) == binding["sha256"], f"public source drift: {relative}")
    selected_ledgers = {item["binding"]["path"] for item in readpoint["admitted_instance_ledgers"]}
    discovered_ledgers = {str(path.relative_to(root)) for path in (root / "authority/admissions").rglob("artifact-instance-admission.json")}
    require(selected_ledgers == discovered_ledgers, "public admitted ledger set drift")
    return result


def construct(inputs: dict) -> dict:
    original = inputs["original"]
    composed = inputs["composed"]
    prior = inputs["prior_matrix"]
    readpoint = inputs["public_readpoint"]
    review = inputs["public_review"]
    require(review.get("result") == "PASS" and review.get("accepted_observations", {}).get("current_exact_owner_authority_established") is False, "public review cannot establish current authority")
    require(readpoint.get("authority_effect") == "none" and readpoint.get("public_admitted_role_instance_count") == 0 and readpoint.get("public_admitted_role_assignment_instance_count") == 0, "public authority readpoint changed")
    require(len(original["members"]) == 363 and len(composed["members"]) == 365 and len(prior["members"]) == 363, "member count changed")
    originals = {m["member_ref"]: m for m in original["members"]}
    priors = {m["member_ref"]: m for m in prior["members"]}
    composed_rows = {m["member_ref"]: m for m in composed["members"]}
    require(len(originals) == 363 and len(priors) == 363 and len(composed_rows) == 365, "duplicate member")
    require(set(originals) == set(priors) and set(originals) < set(composed_rows), "member selection mismatch")
    require(composed.get("original_selection_binding") == {"path": SOURCES["original"][0], "sha256": SOURCES["original"][1]}, "composed predecessor mismatch")
    require(composed.get("additional_member_count") == 2 and composed.get("original_member_count") == 363 and composed.get("total_member_count") == 365, "composed count declaration mismatch")
    expected_new = {
        "protocol:S02:final-common-operator:api-integration-v16",
        "protocol:S02:method-v1-native-namespace-revision-candidate-0254",
    }
    require(set(composed_rows) - set(originals) == expected_new, "additional members changed")
    rows = []
    for ref in sorted(composed_rows):
        member = composed_rows[ref]
        old = originals.get(ref)
        prior_row = priors.get(ref)
        roles = member["proposed_owner_roles"]
        require(roles and all(isinstance(role, str) and role.startswith("role:") for role in roles), f"invalid role declaration: {ref}")
        if old is not None:
            require(old["proposed_owner_roles"] == roles and prior_row["required_roles"] == roles, f"role drift: {ref}")
            require(prior_row["current_owner_authority_verified"] is False and prior_row["actual_owner_outcome"] is None, f"forged prior owner outcome: {ref}")
        axes = member["axes"]
        require(axes.get("operation") in {"admit", "append-owner-governance-event-after-R08-only", None}, f"unexpected effect operation: {ref}")
        locator = {key: axes.get(key) for key in ("category", "operation", "carrier_ref", "identity_ref", "version_ref", "decision_ref", "body_binding", "metadata_record_binding", "archive_binding") if key in axes}
        rows.append({
            "member_ref": ref,
            "member_class": member["member_class"],
            "selection_membership": "original363-and-composed365" if old else "composed365-addition-only",
            "original_effect_axes_sha256": digest(canonical(old["axes"])) if old else None,
            "composed_effect_axes_sha256": digest(canonical(axes)),
            "effect_locator": locator,
            "operation_status": "declared-in-candidate" if axes.get("operation") is not None else "not-declared-in-candidate",
            "declared_target_bindings": member["original_target_bindings"],
            "proposed_roles": roles,
            "declared_candidate_scope_ref": axes.get("original_body_scope_ref"),
            "governing_current_authority": {
                "status": "unverified-public-absence-private-unknown",
                "trusted_role_issuer_root": None,
                "actual_role_instance": None,
                "actual_assignment_instance": None,
                "assignee_ref": None,
                "authenticated_operator_to_owner_link": None,
                "effect_scope_ref": None,
                "period_start": None,
                "period_end": None,
                "revocation_and_successor_status": "unverified",
                "authorized_for_this_effect": False,
                "actual_owner_outcome": None,
            },
        })
    return {
        "schema_version": "LC-U10-03-inert-public-owner-matrix-worksheet/v1",
        "status": "INERT-PUBLIC-WORKSHEET-NOT-CURRENT-AUTHORITY",
        "authority_effect": "none",
        "source_bindings": [{"path": path, "sha256": (expected or digest(canonical(inputs[name])))} for name, (path, expected) in SOURCES.items()],
        "public_readpoint_scope": "Four selected public admitted instance ledgers; private/native stores not inspected; historical role routes are not current grants.",
        "original_member_count": 363,
        "composed_member_count": 365,
        "additional_member_count": 2,
        "public_admitted_role_instance_count": 0,
        "public_admitted_role_assignment_instance_count": 0,
        "current_verified_owner_count": 0,
        "members": rows,
    }


def check_worksheet(worksheet: dict, inputs: dict) -> None:
    require(worksheet == construct(inputs), "worksheet drift or forged authority")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("write", "check"))
    args = parser.parse_args()
    inputs = load_sources()
    worksheet = construct(inputs)
    if args.mode == "write":
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(OUTPUT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o644)
        with os.fdopen(fd, "wb") as stream:
            stream.write(json.dumps(worksheet, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
    else:
        check_worksheet(json.loads(OUTPUT.read_bytes()), inputs)
    print("PASS: pinned public worksheet; 363 original, 365 composed, 0 current verified owners")


if __name__ == "__main__":
    main()
