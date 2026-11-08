"""Current T06 local prerequisite runner; refuses to label API17 as API33."""

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
INTERFACE = ROOT / "product/lab/release-candidates/v1/interface"
API = INTERFACE / "api-integration-v33-current-0001"
SDK = INTERFACE / "composite-operator-v1-completion-0001/revision-0003"
PREPARER = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-0001/revision-0003/prepare_branches.py"
BRIDGE = ROOT / "implementation/lab-runtime/local-host/working/craft-api30-b0-bridge-inactive-0003"
BRIDGE_FREEZE_SHA256 = "79260d72298e33e74eb1da862aeb4eab7478f29f2aa4d1867d00060ca2a50582"


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_json(path, pin):
    need(re.fullmatch(r"[a-f0-9]{64}", pin) is not None, "SHA256_PIN_REQUIRED")
    need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT) and
         not any(parent.is_symlink() for parent in path.parents if parent.is_relative_to(ROOT)),
         "PINNED_ORIGIN_CHANGED:" + str(path))
    raw = path.read_bytes()
    need(sha(raw) == pin, "PIN_CHANGED:" + str(path))
    return json.loads(raw)


def selected_bytes(row, reason):
    need(type(row) is dict and set(row) in ({"path", "sha256"}, {"path", "sha256", "size_bytes"}), reason)
    name = row["path"]
    need(type(name) is str and not Path(name).is_absolute() and ".." not in Path(name).parts and
         type(row["sha256"]) is str and re.fullmatch(r"[a-f0-9]{64}", row["sha256"]) is not None, reason)
    path = ROOT / name
    need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT) and
         not any(parent.is_symlink() for parent in path.parents if parent.is_relative_to(ROOT)), reason)
    need(stat.S_ISREG(path.stat().st_mode), reason)
    raw = path.read_bytes()
    if "size_bytes" in row:
        need(type(row["size_bytes"]) is int and len(raw) == row["size_bytes"], reason)
    need(sha(raw) == row["sha256"], reason)
    return raw


def inspect_current(source_pin, profile_pin):
    source = pinned_json(API / "source-manifest.json", source_pin)
    profile = pinned_json(API / "contract-profile.json", profile_pin)
    need(source["profile_binding"] == {"path": (API / "contract-profile.json").relative_to(ROOT).as_posix(),
                                      "sha256": profile_pin}, "SOURCE_PROFILE_LINK_CHANGED")
    need(source["authority_effect"] == profile["authority_effect"] == "none" and
         len(profile["implemented_operations"]) == 34, "CURRENT_API_SELECTION_CHANGED")
    members_path = API / "integration-members.json"
    historical_member = profile["integration_members_binding"]
    members_raw = selected_bytes({"path": members_path.relative_to(ROOT).as_posix(),
                                  "sha256": historical_member["sha256"]}, "PROFILE_MEMBER_LINK_CHANGED")
    members = json.loads(members_raw)
    need(members["authority_effect"] == "none" and set(members["members"]) == {"actions", "governance"},
         "MEMBER_SELECTION_CHANGED")
    selected_bytes(historical_member, "PROFILE_MEMBER_LINK_CHANGED")
    sdk_manifest = SDK / "source-manifest.json"
    declared = {row["path"]: row["sha256"] for row in profile["files"]}
    sdk_manifest_raw = selected_bytes({"path": sdk_manifest.relative_to(ROOT).as_posix(),
                                       "sha256": declared.get(sdk_manifest.relative_to(ROOT).as_posix())},
                                      "CURRENT_PROFILE_DOES_NOT_SELECT_HISTORICAL_SDK_MANIFEST")
    sdk_pin = sha(sdk_manifest_raw)
    sdk_rows = json.loads(sdk_manifest_raw)["files"]
    need(len(declared) == len(profile["files"]) and
         all(declared.get(row["path"]) == row["sha256"] for row in sdk_rows),
         "CURRENT_PROFILE_DOES_NOT_SELECT_HISTORICAL_SDK_BYTES")
    observed = {row["path"]: selected_bytes(row, "HISTORICAL_SDK_BYTES_CHANGED") for row in sdk_rows}
    sdk_code = observed[(SDK / "composite.py").relative_to(ROOT).as_posix()]
    preparer_row = {"path": PREPARER.relative_to(ROOT).as_posix(),
                    "sha256": declared.get(PREPARER.relative_to(ROOT).as_posix())}
    preparer_code = selected_bytes(preparer_row, "HISTORICAL_PREPARER_BYTES_CHANGED")
    need(b"API=INTERFACE/'api-integration-v17'" in sdk_code and
         b"'api-integration-v17.protocol'" in preparer_code and
         b"'api-integration-v17.guard'" in preparer_code,
         "HISTORICAL_COMPOSITE_ORIGIN_CHANGED")
    return {"api_source_sha256": source_pin, "api_profile_sha256": profile_pin,
            "api_operation_count": 34, "member_count": 2,
            "historical_sdk_manifest_sha256": sdk_pin,
            "historical_sdk_profile_rows": len(sdk_rows),
            "historical_sdk_binds_api17": True,
            "historical_preparer_binds_api17": True}


def craft_build():
    freeze = pinned_json(BRIDGE / "FREEZE.json", BRIDGE_FREEZE_SHA256)
    need(freeze["authority_effect"] == "none" and freeze["native_eligibility"] is False and
         freeze["source8_closure"] is False, "CRAFT_CEILING_CHANGED")
    for name, digest in freeze["local_files_sha256"].items():
        need(sha((BRIDGE / name).read_bytes()) == digest, "CRAFT_BRIDGE_CHANGED:" + name)
    script = ("import {execute} from " + json.dumps((BRIDGE / "bridge.mjs").as_uri()) + ";" +
              "const result=await execute({writeResult:false});process.stdout.write(JSON.stringify(result)+'\\n');")
    completed = subprocess.run(["node", "--input-type=module", "-e", script], cwd=ROOT,
                               capture_output=True, text=True, timeout=180)
    need(completed.returncode == 0, "CRAFT_BUILD_FAILED:" + completed.stderr[-1000:])
    result = json.loads(completed.stdout)
    need(result["status"] == "technical_candidate_validation_passed" and
         result["generated_rule_rows"] == result["generated_query_rows"] == 5 and
         result["generated_manifest_sha256"] == freeze["fresh_generated_manifest_sha256"] and
         result["native_eligibility"] is False and result["source8_closure"] is False,
         "CRAFT_GENERATED_BEHAVIOR_CHANGED")
    return {"status": result["status"], "checked_input_count": result["checked_input_count"],
            "bridge_freeze_sha256": BRIDGE_FREEZE_SHA256,
            "generated_manifest_sha256": result["generated_manifest_sha256"],
            "generated_rule_rows": result["generated_rule_rows"],
            "generated_query_rows": result["generated_query_rows"],
            "generated_operation": result["generated_operation"],
            "native_eligibility": False}


def run(source_pin, profile_pin, with_craft):
    current = inspect_current(source_pin, profile_pin)
    craft = craft_build() if with_craft else {"status": "not_run"}
    return {"schema_version": "lab-T06-current-composite-prerequisite/v1-candidate",
            "status": "BLOCKED_CURRENT_COMPOSITE_INTEGRATION", "authority_effect": "none",
            "entrypoint_sha256": sha(Path(__file__).read_bytes()),
            "current_api": current, "craft": craft,
            "actual_base_action_governance_started": False,
            "actual_full34_ready": False, "dispatch_operations_executed": 0,
            "causal_gap": "Maintained revision-0003 SDK and branch preparer select API17 at true origins; current API33 source/profile do not contain a selected versioned SDK/preparer successor with API33 binding. A frozen API17 startup cannot qualify current API33. Build and pin a successor SDK, preparer and driver in a current API source/profile before branch construction.",
            "claim_ceiling": "Current API33 static selection plus independent Craft fixture execution only; no composite startup or native Craft dispatch."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-source-sha256", required=True)
    parser.add_argument("--api-profile-sha256", required=True)
    parser.add_argument("--craft", action="store_true")
    parser.add_argument("--receipt")
    args = parser.parse_args()
    value = run(args.api_source_sha256, args.api_profile_sha256, args.craft)
    raw = json.dumps(value, sort_keys=True, indent=2).encode() + b"\n"
    if args.receipt:
        path = Path(args.receipt).resolve()
        need(path.parent == HERE and path.name.startswith("RUN-") and path.suffix == ".json",
             "OWNED_VERSIONED_RECEIPT_REQUIRED")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    print(raw.decode(), end="")


if __name__ == "__main__":
    main()
