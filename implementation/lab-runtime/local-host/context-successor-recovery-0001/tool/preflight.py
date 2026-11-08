"""Read-only staged public closure check; does not import or run Source roles."""
from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import sys
from pathlib import Path

ROOT = Path("/attempt/root")
TOOL = Path("/tool")
INTERFACE = ROOT / "product/lab/release-candidates/v1/interface"
FAMILY = INTERFACE / "docker-source-20261020-0002"
ENGINE = INTERFACE / "custody-correction-v4"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def mount_table() -> dict[str, tuple[str, str]]:
    rows = {}
    for line in Path("/proc/self/mountinfo").read_text().splitlines():
        before, after = line.split(" - ", 1)
        left, right = before.split(), after.split()
        rows[left[4]] = (left[5], right[0])
    return rows


def main(*, details: bool = False, require_output_mounts: bool = False) -> dict:
    require(platform.python_version() == "3.14.4" and
            importlib.metadata.version("jsonschema") == "4.23.0" and
            importlib.metadata.version("cryptography") == "46.0.5",
            "selected Docker Source runtime differs")
    plan = json.loads((TOOL / "public-cut.json").read_bytes())
    expected = plan["public_inputs"] + plan["generated_bindings"]
    require(len(expected) == len(plan["public_inputs"]) + 8 and
            len({row["path"] for row in expected}) == len(expected),
            "closed public stage inventory differs")
    names = set()
    require(not ROOT.is_symlink() and all(not path.is_symlink() for path in ROOT.rglob("*")),
            "staged root contains symlink entry")
    for row in expected:
        name = row["path"]
        require(not name.endswith("/branch.snapshot") and
                not any(marker in name.lower() for marker in (".pem", ".key", "private", "secret", "credential")),
                "protected source appeared in public cut")
        path = ROOT / name
        require(path.is_file() and not path.is_symlink() and
                path.resolve().is_relative_to(ROOT) and sha(path.read_bytes()) == row["sha256"],
                "staged input changed: " + name)
        names.add(name)
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()}
    require(actual == names, "extra or missing staged input")
    require((FAMILY / "packages").is_dir() and not list((FAMILY / "packages").iterdir()) and
            (FAMILY / "receipts").is_dir() and not list((FAMILY / "receipts").iterdir()) and
            all(p.stat().st_uid == os.geteuid() and p.stat().st_gid == os.getegid() and
                p.stat().st_mode & 0o777 == 0o700
                for p in (FAMILY / "packages", FAMILY / "receipts")),
            "Source outputs are not fresh")
    mounts = mount_table()
    require("ro" in mounts[str(ROOT)][0].split(",") and
            "ro" in mounts[str(TOOL)][0].split(","),
            "selected input or tool mount is writable")
    scratch = Path("/attempt/tmp")
    if require_output_mounts:
        outputs = {str(FAMILY / "packages"), str(FAMILY / "receipts")}
        nested = {name for name in mounts if name.startswith(str(ROOT) + "/")}
        require(nested == outputs and
                all("rw" in mounts[name][0].split(",") for name in outputs),
                "Source output submounts differ")
    if scratch.is_dir():
        stat = os.statvfs(scratch)
        require(mounts.get(str(scratch), (None, None))[1] == "tmpfs" and
                "rw" in mounts[str(scratch)][0].split(",") and
                os.access(scratch, os.W_OK | os.X_OK) and
                stat.f_bavail * stat.f_frsize >= 128 * 1024 * 1024 and
                stat.f_favail >= 1024,
                "owned Source temporary workspace unavailable")
    else:
        require(not require_output_mounts, "Source temporary workspace absent")
    manifest = FAMILY / "source-manifest.json"
    require(sha(manifest.read_bytes()) == plan["source_manifest"]["sha256"],
            "independent new source pin differs")
    pins = json.loads((ENGINE / "pins.json").read_bytes())
    spec = importlib.util.spec_from_file_location("_cal_source_preflight_loader", ENGINE / "loader.py")
    loader = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = loader
    spec.loader.exec_module(loader)
    loader.verify_engine(loader.EnginePins(**pins))
    # Import the selected public engine source resolver only. This executes no
    # Source builder, signer, store, native binary or protected archive reader.
    sys.path.insert(0, str(ENGINE / "runtime"))
    from lab_runtime import sources
    profile = json.loads((ENGINE / "runtime/profile.json").read_bytes())
    snapshot = sources.capture(ROOT, profile)
    closure_raw = (TOOL / "capture-closure.json").read_bytes()
    require(sha(closure_raw) == plan["capture_closure_sha256"],
            "frozen capture observation changed")
    closure = json.loads(closure_raw)
    require(snapshot["snapshot_digest"] == closure["snapshot_digest"] and
            snapshot["epoch_inventory"] == closure["epoch_inventory"] and
            sorted(({"path": name, "sha256": digest}
                    for name, digest in snapshot["materials"].items()), key=lambda row: row["path"]) ==
            closure["captured_material_bindings"],
            "exact read-only capture closure differs")
    require(set(snapshot["materials"]) <= names and
            not any(name.endswith("/branch.snapshot") for name in snapshot["materials"]),
            "public capture escaped selected input set")
    result = {"schema_version": "lab-source-only-public-preflight/v1-inert",
            "result": "PASS", "source_effect": "NOT_RUN", "selected_input_files": len(expected),
            "captured_materials": len(snapshot["materials"]),
            "snapshot_digest": snapshot["snapshot_digest"],
            "epoch_admission_bundle_names": len(snapshot["epoch_inventory"]["admission_bundles"]),
            "epoch_decision_names": len(snapshot["epoch_inventory"]["recorded_decisions"]),
            "source_manifest_sha256": plan["source_manifest"]["sha256"]}
    if details:
        result["captured_material_bindings"] = [
            {"path": name, "sha256": digest} for name, digest in sorted(snapshot["materials"].items())]
        result["epoch_inventory"] = snapshot["epoch_inventory"]
    return result


if __name__ == "__main__":
    print(json.dumps(main(details=sys.argv[1:] == ["--details"]), sort_keys=True))
