"""Read-only staged public closure check; does not import or run Source roles."""
from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import platform
import sys
from pathlib import Path

ROOT = Path("/attempt/root")
TOOL = Path("/tool")
INTERFACE = ROOT / "product/lab/release-candidates/v1/interface"
FAMILY = INTERFACE / "docker-source-20261020-0001"
ENGINE = INTERFACE / "custody-correction-v4"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def main(*, details: bool = False) -> dict:
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
            (FAMILY / "receipts").is_dir() and not list((FAMILY / "receipts").iterdir()),
            "Source outputs are not fresh")
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
