"""Exact, disposable T25 candidate: original public inputs plus local additions."""

import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import types
import zipfile

ROOT = Path(__file__).resolve().parents[4]
TASK = Path(__file__).resolve().parent
ORIGINAL = ROOT / "implementation/lab-runtime/local-host/t25-original-package-accounting-0001/bundle.py"
ORIGINAL_ACCOUNT = ROOT / "implementation/lab-runtime/local-host/t25-original-package-accounting-0001/account.py"
ORIGINAL_CODE_PINS = {
    ORIGINAL.relative_to(ROOT).as_posix(): "3555d8478361b44d5fa076d24762b1d786f7dd0640f9516839e012e37cd86d14",
    ORIGINAL_ACCOUNT.relative_to(ROOT).as_posix(): "549a5a4cfd93fea86a9247a9b5b21eccf210b10b8c3b569fc2f1511253453837",
}
FIXTURE = "implementation/lab-runtime/local-host/"
FIXTURE_MANIFEST = FIXTURE + "source-manifest.json"
FIXTURE_RELEASE = FIXTURE + "package-release.json"
FIXTURE_BUILDER = FIXTURE + "package_runtime.py"
PUBLIC_REGISTRY = "authority/admissions/governance-transaction-surface/v1/registries/definition-registry.json"
CANONICAL_REGISTRY = "authority/definitions/registry.json"
ORIGINAL_SHA = "c9ea2d54995ba3b80cfc1db1ace9ab395152e090eb1677012d26f317ccb5a573"
FIXTURE_SHA = "1e00e6fd7f1baf7f8cfcd0c0ae7c11ab66649e05cc9575705bee968117ae0346"
RELEASE_SHA = "a8cfacd9e15b65184c1b87a284a699475850b8a783a354102301f50ccbe9cb3e"
API40 = {
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/source-manifest.json": "45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219",
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/contract-profile.json": "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614",
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/integration-members.json": "625ccd27d3a18166dbdaa837c3ec9395491853cb28cef5ff4e05392c99365732",
    "product/lab/release-candidates/v1/interface/composite-operator-v1-current-api40-0001/revision-0001/source-manifest.json": "f123c4e02828c1c3f88dfc4b74adc3bdf1cc2919bc53df8ccf68e00ff677da1e",
    "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api40-0001/revision-0001/driver-selection.json": "2709c559fdfe0ffca7bd684b7454903446367731170df63dd8243ca7076f4480",
    "implementation/lab-runtime/local-host/t06-api40-rebind-0001/run_product.py": "bc8c19774acdbe463546444ea22949f4212ea949c3a2d25a9c53baad5d4f60a6",
    "implementation/lab-runtime/local-host/t06-api40-rebind-0001/RUN-PRODUCT-0001.json": "e4a6be9dac68bcddb06fa54e30bf69deea78f5e46c00258ac9911b9a81a93d64",
    "implementation/lab-runtime/local-host/t06-api40-rebind-0001/drive_effects_0002.py": "ced8b82be6a6ca77562b1d900b7dca122e3e1ecefbd06e428a5e4c0bd50b7cec",
    "implementation/lab-runtime/local-host/t06-api40-rebind-0001/run_craft_same_cut.py": "dfd5f66fc95b21914e0f6de4a32d867c7fb63688e7a8394da88edb945ad5e95e",
    "implementation/lab-runtime/local-host/t06-composite-current-prerequisites-0001/entrypoint.py": "a46ae15046c9b47c92de0ceb285d6ad5dfa319a280a575593a362045619c56b3",
    "implementation/lab-runtime/local-host/t06-api40-rebind-0001/RUN-LIVE-EFFECTS-0002.json": "7bac9d32cad2aa5081ede012ac3d70b0f139b7c166482638954c9a83902f7d5b",
    "implementation/lab-runtime/local-host/t06-api40-rebind-0001/RUN-CRAFT-SAME-CUT-0001.json": "8b46747e098f11016cb92151e3fc550feabc82bd12bc72cf8d2e692d42fbe9a9",
}
CONTROL = "META/candidate-manifest.json"
ORIGINAL_ENTRY = "META/original-public-inputs.zip"
DOCKERIGNORE = ("*\n!Dockerfile\n!requirements.lock\n!compose.yaml\n!run-local-product.sh\n"
                "!package-manifest.json\n!workspace/\n!workspace/**\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def parse(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("duplicate candidate JSON key")
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def safe(name):
    if (not isinstance(name, str) or not name or "\\" in name or name.startswith("/")
            or any(part in ("", ".", "..") for part in name.split("/"))):
        raise ValueError("unsafe candidate path")
    return Path(name)


def read_exact(name, expected):
    path = ROOT / safe(name)
    for parent in (path, *path.parents):
        if parent == ROOT.parent:
            break
        if parent.is_symlink():
            raise ValueError("selected symlink")
    state = path.lstat()
    if not stat.S_ISREG(state.st_mode):
        raise ValueError("selected nonregular file")
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError("selected bytes changed: " + name)
    return raw


def original_module():
    # Execute only the bytes that passed selection. A path-based loader would
    # reopen the source after validation and could run substituted code before
    # a post-import hash check detects it.
    sources = {name: read_exact(name, digest) for name, digest in ORIGINAL_CODE_PINS.items()}
    account = types.ModuleType("t25_selected_original_account")
    account.__file__ = str(ORIGINAL_ACCOUNT)
    exec(compile(sources[ORIGINAL_ACCOUNT.relative_to(ROOT).as_posix()], account.__file__, "exec"),
         account.__dict__)
    module = types.ModuleType("t25_selected_original_bundle")
    module.__file__ = str(ORIGINAL)
    previous = sys.modules.get("account")
    sys.modules["account"] = account
    try:
        exec(compile(sources[ORIGINAL.relative_to(ROOT).as_posix()], module.__file__, "exec"),
             module.__dict__)
    finally:
        if previous is None:
            sys.modules.pop("account", None)
        else:
            sys.modules["account"] = previous
    for name, digest in ORIGINAL_CODE_PINS.items():
        read_exact(name, digest)
    if module.account is not account:
        raise ValueError("original bundle account binding changed")
    return module


def selected_additions():
    fixture_raw = read_exact(FIXTURE_MANIFEST, FIXTURE_SHA)
    fixture = parse(fixture_raw)
    release_raw = read_exact(FIXTURE_RELEASE, RELEASE_SHA)
    release = parse(release_raw)
    if (fixture["schema"] != "lab-local-image-source-manifest/v1" or
            release != {"schema": "lab-local-package-release/v1",
                        "source_manifest_sha256": FIXTURE_SHA,
                        "build_inputs": fixture["build_inputs"]} or
            len(fixture["materials"]) != 698 or len(fixture["runtime_code"]) != 3 or
            len(fixture["build_inputs"]) != 4 or len(fixture["namespace_only"]) != 78 or
            fixture["materials"][CANONICAL_REGISTRY] != fixture["materials"][PUBLIC_REGISTRY]):
        raise ValueError("fixture selection changed")
    rows = {}
    for name, expected in {**fixture["materials"], **fixture["runtime_code"]}.items():
        source = PUBLIC_REGISTRY if name == CANONICAL_REGISTRY else name
        rows["fixture/workspace/" + name] = (read_exact(source, expected),
                                               "public-registry-equivalent" if name == CANONICAL_REGISTRY else "selected-file")
    for name, expected in fixture["build_inputs"].items():
        rows["fixture/" + name] = (read_exact(FIXTURE + name, expected), "selected-build-input")
    for name in fixture["namespace_only"]:
        safe(name)
        archive_name = "fixture/workspace/" + name
        if archive_name in rows:
            raise ValueError("namespace overlaps selected file")
        rows[archive_name] = (b"", "name-only-empty-placeholder")
    rows["fixture/package-manifest.json"] = (fixture_raw, "selected-control")
    rows["fixture/package-release.json"] = (release_raw, "selected-control")
    rows["fixture/package_runtime.py"] = (read_exact(FIXTURE_BUILDER, fixture["builder_sha256"]), "selected-builder")
    rows["fixture/.dockerignore"] = (DOCKERIGNORE, "deterministic-build-context-filter")
    for name, expected in API40.items():
        rows["api40/" + name] = (read_exact(name, expected), "selected-api40-control-or-evidence")
    if len(rows) != 799 or len(rows) != len(set(rows)):
        raise ValueError("addition inventory changed")
    return rows


def entry(name, raw):
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info, raw


def build():
    original = original_module()
    original_blob = original.build()
    if sha(original_blob) != ORIGINAL_SHA or original.replay(original_blob)["original_members"] != 363:
        raise ValueError("original bundle changed")
    additions = selected_additions()
    manifest = {"schema_version": "lab-t25-local-candidate/v1",
                "original_bundle_sha256": ORIGINAL_SHA,
                "original_member_count": 363, "original_public_files": 681,
                "addition_count": len(additions), "original_member_dispositions_complete": False,
                "installed_api40_replay": False, "original_effect_gaps_retained": True,
                "authority_effect": "none",
                "additions": [{"path": name, "sha256": sha(raw), "size": len(raw), "kind": kind}
                              for name, (raw, kind) in sorted(additions.items())]}
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", allowZip64=True) as archive:
        for name, raw in [(CONTROL, encoded(manifest)), (ORIGINAL_ENTRY, original_blob),
                          *((name, raw) for name, (raw, _) in sorted(additions.items()))]:
            archive.writestr(*entry(name, raw))
    return output.getvalue()


def replay(blob):
    with zipfile.ZipFile(io.BytesIO(blob), "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != 801 or len(set(names)) != len(names) or names[:2] != [CONTROL, ORIGINAL_ENTRY]:
            raise ValueError("candidate inventory changed")
        for info in infos:
            safe(info.filename)
            if (info.is_dir() or info.compress_type != zipfile.ZIP_STORED or
                    info.create_system != 3 or info.external_attr >> 16 != 0o100644):
                raise ValueError("unsafe candidate entry")
        canonical = io.BytesIO()
        with zipfile.ZipFile(canonical, "w", allowZip64=True) as rebuilt:
            for info in infos:
                rebuilt.writestr(*entry(info.filename, archive.read(info)))
        if canonical.getvalue() != blob:
            raise ValueError("noncanonical candidate archive")
        manifest = parse(archive.read(CONTROL))
        if (set(manifest) != {"schema_version", "original_bundle_sha256", "original_member_count",
                              "original_public_files", "addition_count", "original_member_dispositions_complete",
                              "installed_api40_replay", "original_effect_gaps_retained", "authority_effect", "additions"}
                or manifest["schema_version"] != "lab-t25-local-candidate/v1"
                or manifest["original_bundle_sha256"] != ORIGINAL_SHA
                or manifest["original_member_count"] != 363 or manifest["original_public_files"] != 681
                or manifest["addition_count"] != 799 or manifest["original_member_dispositions_complete"] is not False
                or manifest["installed_api40_replay"] is not False
                or manifest["original_effect_gaps_retained"] is not True
                or manifest["authority_effect"] != "none"):
            raise ValueError("candidate manifest changed")
        original_blob = archive.read(ORIGINAL_ENTRY)
        if sha(original_blob) != ORIGINAL_SHA:
            raise ValueError("original bundle bytes changed")
        original = original_module()
        original_result = original.replay(original_blob)
        if original_result["original_members"] != 363 or original_result["replayed_public_files"] != 681:
            raise ValueError("original replay changed")
        rows = manifest["additions"]
        if not isinstance(rows, list) or len(rows) != 799 or names[2:] != [row["path"] for row in rows]:
            raise ValueError("candidate addition order changed")
        selected = selected_additions()
        with tempfile.TemporaryDirectory(prefix="cal-t25-candidate-replay-") as directory:
            root = Path(directory)
            for row in rows:
                name = row["path"]
                safe(name)
                if name not in selected:
                    raise ValueError("unselected candidate addition")
                expected_raw, expected_kind = selected[name]
                raw = archive.read(name)
                if (row != {"path": name, "sha256": sha(expected_raw), "size": len(expected_raw),
                            "kind": expected_kind} or raw != expected_raw):
                    raise ValueError("candidate addition bytes changed")
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                if sha(target.read_bytes()) != row["sha256"]:
                    raise ValueError("candidate clean replay changed")
        return {"schema_version": "lab-t25-local-candidate-replay/v1",
                "archive_sha256": sha(blob), "original_members": 363,
                "original_public_files": 681, "replayed_additions": 799,
                "fixture_workspace_files": 779, "api40_selected_controls": len(API40),
                "original_member_dispositions_complete": False,
                "installed_api40_replay": False,
                "original_effect_gaps_retained": True, "authority_effect": "none",
                "task_complete": False}


def extract_verified(blob, root):
    """Materialize the checked fixture context and selected API40 controls in an empty root."""
    result = replay(blob)
    root = Path(root)
    state = root.lstat()
    if not stat.S_ISDIR(state.st_mode) or root.is_symlink() or any(root.iterdir()):
        raise ValueError("nonempty or unsafe extraction root")
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        for info in archive.infolist():
            target = root / safe(info.filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
            fd = os.open(target, flags, 0o644)
            with os.fdopen(fd, "wb") as stream:
                stream.write(archive.read(info))
            target.chmod(0o755 if info.filename == "fixture/run-local-product.sh" else 0o644)
    verifier = root / "fixture/workspace/implementation/lab-runtime/local-host/verify_package.py"
    context = root / "fixture"
    check = subprocess.run([sys.executable, "-B", str(verifier), "--verify-context", str(context)],
                           cwd=root, capture_output=True, timeout=60)
    if check.returncode != 0:
        raise ValueError("extracted fixture package verification refused")
    result["extracted_fixture_context_verified"] = True
    return result


def inventory(blob):
    """Human-reviewable exact rows without persisting the disposable archive."""
    result = replay(blob)
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        additions = parse(archive.read(CONTROL))["additions"]
    original = original_module()
    members = original.account.run()["member_ids"]
    if len(members) != 363 or len(set(members)) != 363:
        raise ValueError("original member inventory changed")
    return {"schema_version": "lab-t25-local-candidate-inventory/v1",
            "archive_sha256": result["archive_sha256"],
            "original_member_ids": members, "additions": additions,
            "original_member_dispositions_complete": False,
            "installed_api40_replay": False, "task_complete": False}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract", type=Path, help="existing empty destination for verified local candidate")
    parser.add_argument("--inventory", action="store_true", help="print exact original and addition inventory")
    args = parser.parse_args()
    if args.extract and args.inventory:
        parser.error("choose extraction or inventory")
    blob = build()
    result = (inventory(blob) if args.inventory else
              extract_verified(blob, args.extract) if args.extract else replay(blob))
    print(json.dumps(result, sort_keys=True, indent=2))
