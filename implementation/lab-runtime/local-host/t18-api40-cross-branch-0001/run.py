"""Exercise a real API40 Base challenge with the distinct Action credential."""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PREDECESSOR = ROOT / "implementation/lab-runtime/local-host/t06-api40-rebind-0001/run_product.py"
DRIVER = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api40-0001/revision-0001/drive_operator.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def verify_boundary_cut(parent):
    """Pin executable inputs without claiming the whole host profile is current."""
    for path in (parent.API / "source-manifest.json", parent.API / "contract-profile.json",
                 parent.API / "integration-members.json", parent.SDK / "source-manifest.json",
                 parent.BRANCH / "driver-selection.json", parent.PROVISION):
        parent.exact(path, parent.PINS[path])
    source = json.loads((parent.API / "source-manifest.json").read_bytes())
    profile = json.loads((parent.API / "contract-profile.json").read_bytes())
    if (source["profile_binding"] != {"path": (parent.API / "contract-profile.json").relative_to(ROOT).as_posix(),
                                     "sha256": parent.PINS[parent.API / "contract-profile.json"]}
            or len(source["files"]) != 207 or len(profile["files"]) != 33424
            or len({row["path"] for row in source["files"]}) != 207
            or len({row["path"] for row in profile["files"]}) != 33424):
        raise ValueError("selected API40 boundary closure differs")
    for row in source["files"]:
        parent.exact(ROOT / row["path"], row["sha256"])
    return source, profile


def run():
    parent = load(PREDECESSOR, "_t18_api40_product_selection")
    source, profile = verify_boundary_cut(parent)
    selected_driver = {row["path"]: row["sha256"] for row in profile["files"]}
    relative_driver = DRIVER.relative_to(ROOT).as_posix()
    if selected_driver.get(relative_driver) != sha(DRIVER.read_bytes()):
        raise ValueError("actual API40 profile does not select driver bytes")
    control = Path(tempfile.mkdtemp(prefix="cal-T18-cross-proof-", dir="/tmp"))
    private_root = None
    private_root_identity = None
    started = time.monotonic()
    try:
        if stat.S_IMODE(control.stat().st_mode) != 0o700:
            raise ValueError("private control root mode differs")
        installation = parent.INSTALL
        selected = [str(installation / "lib/abi/ld-linux-x86-64.so.2"), "--inhibit-cache",
                    "--library-path", str(installation / "lib/abi"),
                    str(installation / "bin/python"), "-X", "utf8", "-B", "-S"]
        env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "PYTHONNOUSERSITE": "1",
               "PYTHONDONTWRITEBYTECODE": "1",
               "PYTHONPATH": str(ROOT / "implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay")
               + ":" + str(installation / "deps")}
        selection = parent.BRANCH / "driver-selection.json"
        stage, _ = parent.child([*selected, str(parent.BRANCH / "prepare_branches.py"), "stage-keys",
                                 "--selection", str(selection), "--selection-sha256", parent.PINS[selection]],
                                control, "stage", 120, env)
        if stage.returncode:
            raise ValueError("fresh branch key staging refused")
        private_root = Path(stage.stdout.decode().strip())
        state = private_root.lstat()
        if (private_root.parent != Path("/tmp") or not private_root.name.startswith("cal-T06-branch-fixtures-")
                or not stat.S_ISDIR(state.st_mode) or state.st_uid != os.getuid()
                or stat.S_IMODE(state.st_mode) != 0o700):
            raise ValueError("fresh private branch root differs")
        private_root_identity = (state.st_dev, state.st_ino, state.st_uid)
        lock = control / "lease.lock"
        prepared, _ = parent.child([*selected, str(parent.BRANCH / "prepare_branches.py"), "prepare",
                                    "--selection", str(selection), "--selection-sha256", parent.PINS[selection],
                                    "--root", str(private_root), "--source-sha256",
                                    parent.PINS[parent.API / "source-manifest.json"], "--profile-sha256",
                                    parent.PINS[parent.API / "contract-profile.json"], "--lease-lock", str(lock)],
                                   control, "prepare", 900, env)
        if prepared.returncode:
            raise ValueError("fresh three-branch preparation refused")
        driver = load(DRIVER, "_t18_api40_selected_driver")
        private_selection = private_root / "private-branch-selection.json"
        selection_sha = sha(private_selection.read_bytes())
        record = driver.read_record(str(private_selection), selection_sha)
        base_key_row = record["reader_keys"]["base"]
        action_key_row = record["reader_keys"]["actions"]
        original_load_key = driver.load_key
        substituted = []
        key_material = {}
        def wrong_base_key(row, selected_record):
            if row == base_key_row:
                base_key = original_load_key(base_key_row, selected_record)
                action_key = original_load_key(action_key_row, selected_record)
                from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
                base_public = base_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
                action_public = action_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
                if base_public == action_public:
                    raise ValueError("branch credentials are not independent")
                key_material.update(base_public=base_public, action_public=action_public)
                substituted.append({"base_public_sha256": sha(base_public),
                                    "action_public_sha256": sha(action_public)})
                return action_key
            return original_load_key(row, selected_record)
        driver.load_key = wrong_base_key
        frames = []
        original_receive = driver.Frames.receive
        def observed_receive(self, deadline):
            frame = original_receive(self, deadline)
            frames.append({"schema_version": frame.get("schema_version"), "code": frame.get("code")})
            if frame.get("schema_version") == "lab-composite-challenges/v1-candidate":
                key_material["base_challenge"] = frame["challenges"]["base"]
            return frame
        driver.Frames.receive = observed_receive
        original_send = driver.send
        proof_observations = []
        def observed_send(stream, value):
            if (value.get("schema_version") == "lab-composite-branch-proof/v1-candidate"
                    and value.get("branch") == "base"):
                from cryptography.exceptions import InvalidSignature
                from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
                proof_raw = base64.b64decode(value["proof_base64"], validate=True)
                proof = driver.parse(proof_raw)
                if (proof["schema_version"] != "lab-local-reader-proof/v1-candidate"
                        or proof["challenge"] != key_material["base_challenge"]):
                    raise ValueError("wrong-key proof did not bind actual Base challenge")
                signature = base64.b64decode(proof["signature"], validate=True)
                encoded = driver.compact(proof["challenge"])
                Ed25519PublicKey.from_public_bytes(key_material["action_public"]).verify(signature, encoded)
                try:
                    Ed25519PublicKey.from_public_bytes(key_material["base_public"]).verify(signature, encoded)
                except InvalidSignature:
                    pass
                else:
                    raise ValueError("Action signature also verified under Base key")
                proof_observations.append({"base_challenge_sha256": sha(encoded),
                                           "wrong_proof_sha256": sha(proof_raw),
                                           "action_key_verified": True, "base_key_verified": False})
            return original_send(stream, value)
        driver.send = observed_send
        args = argparse.Namespace(sdk_directory=str(parent.SDK),
            sdk_source_sha256=parent.PINS[parent.SDK / "source-manifest.json"],
            provisioning_path=parent.PROVISION.relative_to(ROOT).as_posix(),
            provisioning_sha256=parent.PINS[parent.PROVISION], lease_lock=str(lock))
        refusal = None
        try:
            driver.run(record, args)
        except Exception as error:
            refusal = {"class": type(error).__name__, "message_sha256": sha(str(error).encode())}
        expected_frames = ["lab-composite-fresh-session-request/v1-candidate",
                           "lab-composite-challenges/v1-candidate",
                           "lab-composite-startup-error/v1-candidate"]
        if ([row["schema_version"] for row in frames] != expected_frames or
                frames[-1]["code"] != "startup-or-channel-refused" or refusal is None or
                len(substituted) != 1 or len(proof_observations) != 1 or
                any(row["schema_version"] == "lab-composite-ready/v1-candidate" for row in frames)):
            raise ValueError("cryptographic wrong-branch Base proof did not refuse before readiness")
        verify_boundary_cut(parent)
        return {"schema_version": "lab-T18-api40-cross-branch-proof/v1-candidate",
                "status": "PASS", "source_manifest_sha256": parent.PINS[parent.API / "source-manifest.json"],
                "profile_sha256": parent.PINS[parent.API / "contract-profile.json"],
                "sdk_manifest_sha256": parent.PINS[parent.SDK / "source-manifest.json"],
                "selected_driver_sha256": selected_driver[relative_driver],
                "private_selection_sha256": selection_sha,
                "case": "Base challenge signed by independent Action private key",
                "public_key_digests": substituted[0],
                "proof_observation": proof_observations[0],
                "frames": frames, "refusal": refusal,
                "composite_ready": False, "dispatch_executed": False,
                "whole_host_profile_verified": False,
                "authority_effect": "none", "elapsed_seconds": round(time.monotonic() - started, 3)}
    finally:
        try:
            if private_root_identity is not None:
                state = private_root.lstat()
                if ((state.st_dev, state.st_ino, state.st_uid) != private_root_identity
                        or not stat.S_ISDIR(state.st_mode)):
                    raise ValueError("owned private root changed before cleanup")
                shutil.rmtree(private_root)
        finally:
            shutil.rmtree(control)


def main():
    os.umask(0o077)
    output = HERE / "RESULT-0001.json"
    if output.exists():
        raise ValueError("new exact result path required")
    try:
        result = run()
        result["private_fixture_roots_removed"] = True
    except Exception as error:
        result = {"schema_version": "lab-T18-api40-cross-branch-proof/v1-candidate",
                  "status": "REFUSED", "error_class": type(error).__name__,
                  "error_message_sha256": sha(str(error).encode()),
                  "composite_ready": False, "dispatch_executed": False,
                  "authority_effect": "none"}
    raw = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({"status": result["status"], "result_sha256": sha(raw),
                      "elapsed_seconds": result.get("elapsed_seconds")}, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
