"""Run the retained native T02 constructor into a new engineering fixture.

The old recipe's approval dispatcher is not used. This runner calls its
construction functions against a disjoint output root and records each phase.
It does not modify API30 or enroll any issuer.
"""

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import secrets
import stat
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RECIPE = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/fresh-legacy-current-runtime-preparation-0009"
OLD_PACKET = RECIPE / "Root-packet-INACTIVE.json"
PHASES = ("stage", "source", "cold", "reader", "mapped", "context")
ENGINE_PROFILE = HERE / "engine-v3/runtime/profile.json"
CLEAN_INSTALL = Path("/tmp/cal-native-install-20261022/0001")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_new(path, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    raw = json.dumps(value, sort_keys=True, indent=2).encode() + b"\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(raw)}


def load_helper(name):
    path = RECIPE / (name + ".py")
    require(path.is_file() and not path.is_symlink(), "CONSTRUCTOR_ORIGIN_REFUSED")
    spec = importlib.util.spec_from_file_location("cal_native_successor_" + name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def technical_preflight():
    """Check the retained constructor's current authority input before writes."""
    profile = json.loads(ENGINE_PROFILE.read_bytes())
    selected = profile["current_selection"]["lookup"]
    actual = ROOT / selected["path"]
    require(actual.is_file() and not actual.is_symlink(), "ENGINE_LOOKUP_ORIGIN_REFUSED")
    observed = sha(actual.read_bytes())
    require(observed == selected["sha256"],
            "PINNED_ENGINE_PROFILE_STALE expected=" + selected["sha256"] +
            " observed=" + observed + " path=" + selected["path"])
    return {"engine_profile": ENGINE_PROFILE.relative_to(ROOT).as_posix(),
            "lookup": selected}


def current_engine_bindings():
    manifest_path = HERE / "engine-v3/engine-manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    paths = [HERE / "engine-v3/loader.py", HERE / "engine-v3/pins.json",
             manifest_path, ENGINE_PROFILE, HERE / "private_archive_hardening.py",
             HERE / "installed_context_role.py", HERE / "prepare_installed_runtime.py"]
    paths.extend(ROOT / row["path"] for row in manifest["files"])
    rows = {}
    for path in paths:
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT),
                "ENGINE_INPUT_ORIGIN_REFUSED")
        relative = path.relative_to(ROOT).as_posix()
        row = {"path": relative, "sha256": sha(path.read_bytes())}
        require(rows.get(relative, row) == row, "ENGINE_INPUT_DUPLICATE_REFUSED")
        rows[relative] = row
    return [rows[key] for key in sorted(rows)]


def stage(instance, private_home):
    require(re.fullmatch(r"legacy-local-[0-9a-f]{16}", instance), "INSTANCE_NAME_REFUSED")
    family = HERE / "instances" / instance
    require(not family.exists() and not family.is_symlink(), "CONSUMED_INSTANCE_REFUSED")
    private_home = Path(private_home)
    require(private_home.is_dir() and not private_home.is_symlink() and
            not private_home.resolve().is_relative_to(ROOT), "PRIVATE_HOME_ORIGIN_REFUSED")
    metadata = private_home.stat()
    require(metadata.st_uid == os.getuid() and stat.S_IMODE(metadata.st_mode) == 0o700,
            "PRIVATE_HOME_OWNER_MODE_REFUSED")
    private_instance = private_home / instance
    require(not private_instance.exists() and not private_instance.is_symlink(),
            "PRIVATE_INSTANCE_CONSUMED_REFUSED")
    private_instance.mkdir(mode=0o700)
    current = dt.datetime.now(dt.timezone.utc)
    source = json.loads(OLD_PACKET.read_bytes())
    require(source["instance"] != instance, "OLD_INSTANCE_REFUSED")
    role = dict(source["context_role_selection"])
    role["role_code_binding"] = {
        "path": (HERE / "installed_context_role.py").relative_to(ROOT).as_posix(),
        "sha256": sha((HERE / "installed_context_role.py").read_bytes())}
    require(CLEAN_INSTALL.is_dir() and not CLEAN_INSTALL.is_symlink() and
            not CLEAN_INSTALL.resolve().is_relative_to(ROOT.resolve()),
            "CLEAN_INSTALL_ORIGIN_REFUSED")
    installed = CLEAN_INSTALL.stat()
    require(installed.st_uid == os.getuid() and stat.S_IMODE(installed.st_mode) == 0o700,
            "CLEAN_INSTALL_OWNER_MODE_REFUSED")
    receipt = CLEAN_INSTALL / "installation.json"
    require(receipt.is_file() and not receipt.is_symlink(), "CLEAN_INSTALL_RECEIPT_REFUSED")
    role["installation"] = {"path": str(CLEAN_INSTALL),
                            "identity": [installed.st_dev, installed.st_ino,
                                         installed.st_uid, stat.S_IMODE(installed.st_mode)]}
    role["installation_receipt_binding"] = {"path": str(receipt),
                                               "sha256": sha(receipt.read_bytes())}
    engine_inputs = {row["path"]: row for row in source["current_runtime_input_bindings"]}
    for row in current_engine_bindings():
        require(engine_inputs.get(row["path"], row) == row, "ENGINE_INPUT_CONFLICT_REFUSED")
        engine_inputs[row["path"]] = row
    packet = {"schema": "cal-native-local-successor-selection/v1", "instance": instance,
              "not_before": current.isoformat(),
              "expires_at": (current + dt.timedelta(hours=24)).isoformat(),
              "context_role_selection": role,
              "current_runtime_input_bindings": [engine_inputs[key] for key in sorted(engine_inputs)],
              "constructor_ref": RECIPE.relative_to(ROOT).as_posix(),
              "private_archive_path": str(private_instance / "branch.snapshot"),
              "authority_effect": "none"}
    packet["packet_binding"] = write_new(HERE / "selections" / (instance + ".json"), packet)
    builder = load_helper("build_legacy_family_v2")
    builder.HERE = HERE
    builder._ROOT_PACKET = packet
    builder._ROLE_VALUE = packet["context_role_selection"]
    retained = load_helper("hardening")
    selected = importlib.util.spec_from_file_location("cal_private_archive_hardening", HERE / "private_archive_hardening.py")
    hardening = importlib.util.module_from_spec(selected)
    selected.loader.exec_module(hardening)
    builder._HARDENER = hardening.Hardener(retained, private_instance / "branch.snapshot")
    built = builder.stage(instance)
    require(built["instance"] == instance and built["public_source_name"] == "completion-legacy:" + instance,
            "STAGED_SELECTION_REFUSED")
    return {"instance": instance, "family": str(family), "source_name": built["public_source_name"],
            "not_before": packet["not_before"], "expires_at": packet["expires_at"]}


def protected_output_preflight(family):
    """Permit only a selected package whose archive write is outside Git."""
    selection_path = family / "construction-selection.json"
    require(selection_path.is_file() and not selection_path.is_symlink(),
            "PRIVATE_SELECTION_ORIGIN_REFUSED")
    selection = json.loads(selection_path.read_bytes())
    packet_row = selection["Root_packet_binding"]
    packet_path = ROOT / packet_row["path"]
    require(packet_path.is_file() and sha(packet_path.read_bytes()) == packet_row["sha256"],
            "PRIVATE_PACKET_BINDING_REFUSED")
    packet = json.loads(packet_path.read_bytes())
    archive = Path(packet["private_archive_path"])
    require(archive.is_absolute() and archive.name == "branch.snapshot" and
            archive.parent.is_dir() and not archive.parent.is_symlink() and
            not archive.parent.resolve().is_relative_to(ROOT.resolve()),
            "PRIVATE_ARCHIVE_ORIGIN_REFUSED")
    metadata = archive.parent.stat()
    require(metadata.st_uid == os.getuid() and stat.S_IMODE(metadata.st_mode) == 0o700,
            "PRIVATE_ARCHIVE_OWNER_MODE_REFUSED")
    rows = {row["new"]["path"]: row["new"] for row in selection["template_rows"]}
    for filename in ("base.py", "build.py", "cold.py"):
        path = family / "source" / filename
        row = rows.get(path.relative_to(ROOT).as_posix())
        require(row is not None and sha(path.read_bytes()) == row["sha256"],
                "PROTECTED_GENERATOR_SELECTION_REFUSED")
    base = (family / "source/base.py").read_text()
    build = (family / "source/build.py").read_text()
    cold = (family / "source/cold.py").read_text()
    selected_path = "PRIVATE_ARCHIVE=Path(" + repr(str(archive)) + ")"
    require(selected_path in base and selected_path in build and
            "finally:emit_private(archive(store,pins))" in build and
            "'archive_binding':binding(out/'archive-handle.json')" in build and
            "archive=parse(external_archive(manifest['archive_binding']))" in cold and
            "emit(out/'branch.snapshot'" not in build and
            not (family / "source/packages/0001/branch.snapshot").exists(),
            "PROTECTED_OUTPUT_INSIDE_REPOSITORY_REFUSED")
    return archive


def phase(instance, name):
    require(name in PHASES and name != "stage", "PHASE_REFUSED")
    require(re.fullmatch(r"legacy-local-[0-9a-f]{16}", instance), "INSTANCE_NAME_REFUSED")
    family = HERE / "instances" / instance
    require(family.is_dir() and not family.is_symlink(), "INSTANCE_ORIGIN_REFUSED")
    protected_output_preflight(family)
    technical_preflight()
    constructor = load_helper("construct_legacy_v3")
    constructor.HERE = HERE
    result = getattr(constructor, name)(family)
    write_new(family / (name + "-result.json"), result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=PHASES)
    parser.add_argument("--instance")
    parser.add_argument("--private-home", type=Path)
    args = parser.parse_args()
    instance = args.instance or "legacy-local-" + secrets.token_hex(8)
    require(args.phase == "stage" or args.instance is not None, "INSTANCE_REQUIRED")
    require(args.phase != "stage" or args.private_home is not None, "PRIVATE_HOME_REQUIRED")
    value = stage(instance, args.private_home) if args.phase == "stage" else phase(instance, args.phase)
    print(json.dumps({"phase": args.phase, "instance": instance, "result": value}, sort_keys=True))


if __name__ == "__main__":
    main()
