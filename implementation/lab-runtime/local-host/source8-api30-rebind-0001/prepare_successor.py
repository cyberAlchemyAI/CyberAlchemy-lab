"""Build an isolated API30 successor against one completed native Source8 family.

The historical API30 package and its expired fixture are immutable inputs. This
builder refuses partial families and an existing output, then records the exact
files it changed. It does not grant authority or manufacture a passing test.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
OLD = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v30"
FAMILY = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8"
OUTPUT = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v33-current-0001"
OLD_LEGACY = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/fresh-legacy-current-runtime-preparation-0009/instances/legacy-source8-20261018-b"
OLD_OPTIMIZED = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0005/instances/optimized-0005"
OLD_LEGACY_PIN = "888a46401bbe019b03445241829d4ee141f22c6c36e322afa127a942655a35b2"
OLD_OPTIMIZED_PIN = "a7f8ef943ff91b33c9b1a635e9c45f14ccb6c5926eb723d0e99205f55b27f925"
OLD_LEGACY_MAPPING = "b027e768a68fd785128bd8daf9c576250da91717d43774916419776ced09a6ec"
OLD_OPTIMIZED_MAPPING = "b0a12f7e3deab2a660eb92e8242533bdd3f1e58ceda79c7ceb76ff040a0ede45"
OLD_LEGACY_NAME = "completion-legacy:legacy-source8-20261018-b"
OLD_OPTIMIZED_NAME = "completion-current-participation:optimized-0005"
OLD_LEGACY_STORE = "completion-legacy-source8-20261018-b"
OLD_OPTIMIZED_STORE = "completion-optimized-source8-0005-optimized-0005"
OLD_READER_SHA = "5c85be9aef9e0afc6ee3bf49cf7140872c99cf648775fcb5805107f268ac1a53"
OLD_NOT_BEFORE = "2026-10-18T04:28:53.699295+00:00"
OLD_EXPIRES_AT = "2026-10-19T04:28:53.699295+00:00"
MACHINE_HELPERS = (
    "machine-context-scope-v3-api25-completion-0001",
    "machine-context-scope-v4-api33-legacy-0001",
    "machine-context-scope-v5-api33-current-legacy-0001",
)
T06_SDK = ROOT / "product/lab/release-candidates/v1/interface/composite-operator-v1-current-api33-0001/revision-0001"
T06_BRANCH = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api33-0001/revision-0001"
T06_SDK_MANIFEST_SHA = "277209c322c7891fb8c99533ed8280b1343c8f7bbb0ec68f090abbcd0d1b7b4a"
T06_BRANCH_SELECTION_SHA = "1c95d97c9aa505fd576444b1699ca7075ac3f13218e8b3f308d53cb529d10c2d"
INTEGRATION_MEMBERS_SHA = "64931c417e6738d82c1c4cb819bb660237aab038bf6474594d421d8991f6d7d1"
OLD_INTEGRATION_MEMBERS = "product/lab/release-candidates/v1/interface/api-integration-v16/integration-members.json"
OLD_EPHEMERAL_NATIVE_EXE = "/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader"
STABLE_NATIVE_EXE = "product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/bin/lab-context-native-reader"
NATIVE_EXE_SHA = "fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c"
AUTHORITY_CURRENT = "authority/project-state-transitions/current.json"
AUTHORITY_OLD_SHA = "8ba8ee25ccbf12721d800c693120a3452ddf1ec4427c6fdf1e0655beae31bc12"
AUTHORITY_CURRENT_SHA = "12937950af2a00ef329deb1a922275250c61ad199b8f6216eab448e06bf49984"
OLD_SYSTEM_LIBLZMA = "/usr/lib/x86_64-linux-gnu/liblzma.so.5.8.3"
INSTALLED_LIBLZMA = "product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/lib/abi/liblzma.so.5"
SELECTED_LIBLZMA_SHA = "64550dc7a4dc9159d32c00d9e78ce86e0951d02b7b24827df97f090dae101a19"
RUNTIME_SELECTOR_MODULES = (
    "challenge_resolution.py", "classification_preparation.py",
    "current_lesson_application.py", "current_lesson_selection.py",
    "failure_preparation.py", "lesson_application.py", "lesson_assessment.py",
    "lesson_selection.py", "typed_preparation.py",
)
EXPECTED_ROLE_EXCLUSIONS = (
    "role-assignment:lab-repository-owner-bootstrap-0005@sha256.08afbee78d4fc8b3c478001941bfd494de4014384113852cffbf3bb8fedf6c60",
    "role-assignment:lab-specialist-artifact-type-owner-bootstrap-0003@sha256.708e1da320083a0044db32ffe05373f14be6efa74d2cf086074dbb2b3223e911",
    "role-assignment:lab-specialist-definition-owner-bootstrap-0003@sha256.65e6e307b5a451a684831b7317069a98508c62672d036eb224b5cd646dd391ec",
    "role-assignment:lab-specialist-identity-graph-owner-bootstrap-0003@sha256.9e05beddb520ce49fbaba9e47d892f492ad8da99397c767eb889d04225e73c4b",
    "role:artifact-type-owner@sha256.3c6878874484210908e895c3ead966f63c3408dcf8b50f361d82616e27ac1a5b",
    "role:definition-owner@sha256.bbd3a83be40588d8a162f57edb593a4621a5e8b7cf9ed00c8fe8d351632bf6ba",
    "role:identity-graph-owner@sha256.2c6b57c7039ebfc39237cdf32b8ae3419bfaec55831c5e568b5d1a6bf4ee9dce",
    "role:repository-owner@sha256.18c11c56a8ef8ef17079525ae98b55b655f8ffadbfca8c2ed3e5f82f966605cf",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_current_integration_members(profile_path: Path, output: Path) -> dict[str, str]:
    """Make dispatch and operator guard select one exact API33 member origin."""
    current = output / "integration-members.json"
    if not current.is_file() or current.is_symlink() or digest(current) != INTEGRATION_MEMBERS_SHA:
        raise ValueError("current API33 integration members differ")
    profile = json.loads(profile_path.read_text())
    if profile["integration_members_binding"] != {"path": OLD_INTEGRATION_MEMBERS,
                                                   "sha256": INTEGRATION_MEMBERS_SHA}:
        raise ValueError("inherited integration member origin differs")
    current_binding = {"path": current.relative_to(ROOT).as_posix(),
                       "sha256": INTEGRATION_MEMBERS_SHA}
    if any(row["path"] == current_binding["path"] for row in profile["files"]):
        raise ValueError("current integration member profile row already present")
    profile["integration_members_binding"] = current_binding
    profile["files"].append(current_binding)
    profile_path.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n")
    return current_binding


def retire_ephemeral_native_executable_row(profile_path: Path) -> dict[str, str]:
    """Retire only the missing duplicate build-path row; retain installed ELF."""
    stable = ROOT / STABLE_NATIVE_EXE
    if stable.is_symlink() or not stable.is_file() or digest(stable) != NATIVE_EXE_SHA:
        raise ValueError("stable selected native executable differs")
    info = stable.stat()
    raw = stable.read_bytes()
    if (not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o755 or
            info.st_uid != os.getuid() or len(raw) != 20243600 or
            raw[:6] != b"\x7fELF\x02\x01" or raw[18:20] != b"\x3e\x00"):
        raise ValueError("stable selected native executable mode or ABI differs")
    profile = json.loads(profile_path.read_text())
    old = {"path": OLD_EPHEMERAL_NATIVE_EXE, "sha256": NATIVE_EXE_SHA}
    current = {"path": STABLE_NATIVE_EXE, "sha256": NATIVE_EXE_SHA}
    if profile["files"].count(old) != 1 or profile["files"].count(current) != 1:
        raise ValueError("exact duplicate native executable profile rows differ")
    profile["files"].remove(old)
    profile_path.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n")
    return current


def rebind_current_authority_and_retire_system_liblzma(profile_path: Path) -> dict[str, dict[str, str]]:
    """Re-pin one current authority byte and retain the already selected installed ABI byte.

    The old Context disposition still records the historical authority binding;
    this changes only the current API profile. The mutable system liblzma path
    is an obsolete duplicate of the already selected installed shared object.
    """
    authority = ROOT / AUTHORITY_CURRENT
    installed = ROOT / INSTALLED_LIBLZMA
    if (authority.is_symlink() or not authority.is_file() or
            digest(authority) != AUTHORITY_CURRENT_SHA):
        raise ValueError("current authority byte differs")
    if (installed.is_symlink() or not installed.is_file() or
            digest(installed) != SELECTED_LIBLZMA_SHA):
        raise ValueError("selected installed liblzma byte differs")
    info = installed.stat()
    raw = installed.read_bytes()
    if (not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o644 or
            info.st_uid != os.getuid() or len(raw) != 215448 or
            raw[:6] != b"\x7fELF\x02\x01" or raw[18:20] != b"\x3e\x00" or
            b"liblzma.so.5\x00" not in raw):
        raise ValueError("selected installed liblzma ABI or custody differs")
    profile = json.loads(profile_path.read_text())
    old_authority = {"path": AUTHORITY_CURRENT, "sha256": AUTHORITY_OLD_SHA}
    current_authority = {"path": AUTHORITY_CURRENT, "sha256": AUTHORITY_CURRENT_SHA}
    old_system = {"path": OLD_SYSTEM_LIBLZMA, "sha256": SELECTED_LIBLZMA_SHA}
    current_installed = {"path": INSTALLED_LIBLZMA, "sha256": SELECTED_LIBLZMA_SHA}
    rows = profile["files"]
    if (rows.count(old_authority) != 1 or rows.count(old_system) != 1 or
            rows.count(current_installed) != 1 or
            sum(row.get("path") == AUTHORITY_CURRENT for row in rows) != 1 or
            sum(row.get("path") == OLD_SYSTEM_LIBLZMA for row in rows) != 1 or
            sum(row.get("path") == INSTALLED_LIBLZMA for row in rows) != 1):
        raise ValueError("exact current authority or liblzma profile rows differ")
    rows[rows.index(old_authority)] = current_authority
    rows.remove(old_system)
    profile_path.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n")
    return {"current_authority": current_authority, "installed_liblzma": current_installed,
            "retired_system_liblzma": old_system}


def include_t06_operator_rows(profile_path: Path) -> list[dict[str, str]]:
    """Select the independently reviewed current API33 SDK and branch producer bytes."""
    sdk_manifest = T06_SDK / "source-manifest.json"
    branch_selection = T06_BRANCH / "driver-selection.json"
    for path, expected in ((sdk_manifest, T06_SDK_MANIFEST_SHA),
                           (branch_selection, T06_BRANCH_SELECTION_SHA)):
        if not path.is_file() or path.is_symlink() or digest(path) != expected:
            raise ValueError("reviewed T06 operator selection differs")
    sdk = json.loads(sdk_manifest.read_text())
    branch = json.loads(branch_selection.read_text())
    sdk_expected = {"bootstrap.py", "composite.py", "control.py", "framing.py",
                    "launch.py", "composite.config.schema.json"}
    sdk_rows = sdk["files"]
    if (len(sdk_rows) != 6 or {Path(row["path"]).name for row in sdk_rows} != sdk_expected or
            any((ROOT / row["path"]).parent != T06_SDK for row in sdk_rows)):
        raise ValueError("reviewed T06 SDK closure differs")
    branch_rows = [row for row in branch["files"] if (ROOT / row["path"]).parent == T06_BRANCH]
    if len(branch_rows) != 2 or {Path(row["path"]).name for row in branch_rows} != {"prepare_branches.py", "drive_operator.py"}:
        raise ValueError("reviewed T06 branch producer closure differs")
    additions = ([{"path": sdk_manifest.relative_to(ROOT).as_posix(), "sha256": T06_SDK_MANIFEST_SHA},
                  {"path": branch_selection.relative_to(ROOT).as_posix(), "sha256": T06_BRANCH_SELECTION_SHA}] +
                 [{"path": row["path"], "sha256": row["sha256"]} for row in sdk_rows + branch_rows])
    if len(additions) != 10 or len({row["path"] for row in additions}) != 10:
        raise ValueError("reviewed T06 selected rows duplicate")
    profile = json.loads(profile_path.read_text())
    original = {row["path"]: row["sha256"] for row in profile["files"]}
    if len(original) != len(profile["files"]):
        raise ValueError("API profile file rows duplicate")
    for row in branch["files"]:
        if row in branch_rows:
            continue
        if original.get(row["path"]) != row["sha256"]:
            raise ValueError("reviewed T06 historical branch dependency absent")
    for row in additions:
        path = ROOT / row["path"]
        if (row["path"] in original or not path.is_file() or path.is_symlink() or
                digest(path) != row["sha256"]):
            raise ValueError("reviewed T06 operator byte or path differs")
    profile["files"].extend(sorted(additions, key=lambda row: row["path"]))
    profile_path.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n")
    return additions


def required_json(path: Path) -> dict:
    value = json.loads(path.read_bytes())
    if type(value) is not dict:
        raise ValueError(f"object required: {path}")
    return value


def family_values(family: Path, context_path: Path | None = None) -> dict[str, str]:
    family = family.resolve(strict=True)
    if not family.is_relative_to(ROOT) or any(p.is_symlink() for p in (family, *family.parents)):
        raise ValueError("family must be a real directory within this repository")
    for phase in ("source", "cold", "reader", "mapped", "context"):
        result = family / f"{phase}-result.json"
        if not result.is_file():
            raise ValueError(f"native family phase is incomplete: {phase}")
        row = required_json(result)
        if phase == "source":
            for key, selected in (("source_binding", family / "source/source-manifest.json"),
                                  ("package_binding", family / "source/packages/0001/manifest.json")):
                if row.get(key, {}).get("sha256") != digest(selected):
                    raise ValueError("native source result does not bind the source package")
        elif not str(row.get("result", "")).startswith("PASS"):
            raise ValueError(f"native family phase failed: {phase}")
    for selected in (family / "source", family / "reader", family / "mapped", family / "context"):
        if not selected.is_dir():
            raise ValueError(f"native family part missing: {selected}")
    context_path = (family / "context" if context_path is None else context_path).resolve(strict=True)
    if not context_path.is_relative_to(ROOT) or any(p.is_symlink() for p in (context_path, *context_path.parents)):
        raise ValueError("Context successor must be a real directory within this repository")
    if context_path != family / "context":
        result = required_json(context_path / "context-result.json")
        if not str(result.get("result", "")).startswith("PASS"):
            raise ValueError("selected Context successor has no PASS result")
    source = family / "source/packages/0001"
    period = required_json(source / "period.json")
    replay = required_json(source / "expected-replay.json")
    engine_profile = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/engine-v3/runtime/profile.json"
    if digest(engine_profile) != replay["engine_pins"]["profile_sha256"]:
        raise ValueError("native engine profile differs from signed source selection")
    now = datetime.now(timezone.utc)
    if not datetime.fromisoformat(period["not_before"]) <= now < datetime.fromisoformat(period["expires_at"]):
        raise ValueError("native family Assignment is not current")
    source_manifest = family / "source/source-manifest.json"
    source_package = source / "manifest.json"
    reader_manifest = family / "reader/source-manifest.json"
    mapped_package = family / "mapped/packages/0001/manifest.json"
    mapping_path = family / "mapped/packages/0001/mapping.json"
    context_manifest = context_path / "source-manifest.json"
    context_package = context_path / "packages/0001/manifest.json"
    for path in (source_manifest, source_package, reader_manifest, mapped_package, context_manifest, context_package):
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"native family manifest missing or linked: {path}")
    mapping_manifest = required_json(mapped_package)
    matching_mapping_rows = [row for row in mapping_manifest["files"]
                             if row["path"] == mapping_path.relative_to(ROOT).as_posix()]
    if (len(matching_mapping_rows) != 1 or mapping_path.is_symlink()
            or matching_mapping_rows[0]["sha256"] != digest(mapping_path)):
        raise ValueError("native mapping bytes differ from mapped package manifest")
    mapping = required_json(mapping_path)
    dispositions = mapping.get("projection_dispositions")
    if type(dispositions) is not list or len(dispositions) != 604 or len({row["version_ref"] for row in dispositions}) != 604:
        raise ValueError("native disposition closure differs")
    by_ref = {row["version_ref"]: row for row in dispositions}
    if any(by_ref.get(ref) != {"version_ref": ref, "carrier_ref": None,
                               "effective_state": "admitted-current",
                               "disposition": "retained-source-outside-declared-context-selection"}
           for ref in EXPECTED_ROLE_EXCLUSIONS):
        raise ValueError("exact eight unrepresentable role dispositions differ")
    if mapping["source_package_binding"] != {"path": source_package.relative_to(ROOT).as_posix(),
                                              "sha256": digest(source_package)}:
        raise ValueError("native mapping source package binding differs")
    delivery = required_json(context_path / "packages/0001/delivery.json")
    permission = required_json(context_path / "packages/0001/host-permission-public.json")
    for row in (delivery, permission):
        datetime.fromisoformat(row["expires_at"])
    reader_binding = required_json(context_path / "implementation-binding.json")
    new_reader_sha = digest(family / "reader/reader.py")
    if reader_binding["code_binding"]["sha256"] != new_reader_sha:
        raise ValueError("Context implementation does not bind the selected Reader bytes")
    new_path = family.relative_to(ROOT).as_posix()
    store = period["principal_ref"].removeprefix("principal:")
    if not store.startswith("completion-legacy-local-"):
        raise ValueError("unexpected new family identity")
    return {
        "family_path": new_path,
        "context_path": context_path.relative_to(ROOT).as_posix(),
        "historical_context_construction_delivery_expires_at": delivery["expires_at"],
        "historical_context_construction_host_permission_expires_at": permission["expires_at"],
        "legacy_name": "completion-legacy:" + store.removeprefix("completion-"),
        "current_name": "completion-current-participation:" + store.removeprefix("completion-"),
        "store": store,
        "source_sha256": digest(source_manifest),
        "source_package_sha256": digest(source_package),
        "reader_sha256": new_reader_sha,
        "reader_manifest_sha256": digest(reader_manifest),
        "mapped_package_sha256": digest(mapped_package),
        "mapping_sha256": digest(mapping_path),
        "context_sha256": digest(context_manifest),
        "context_package_sha256": digest(context_package),
        "not_before": period["not_before"],
        "expires_at": period["expires_at"],
        "principal": period["principal_ref"],
        "entrypoint": reader_binding["entrypoint_ref"],
        "engine_profile_path": engine_profile.relative_to(ROOT).as_posix(),
        "engine_profile_sha256": digest(engine_profile),
    }


def replacements(values: dict[str, str]) -> list[tuple[str, str]]:
    path = values["family_path"]
    return [
        (OLD_LEGACY + "/context", values["context_path"]),
        (OLD_OPTIMIZED + "/context", values["context_path"]),
        (OLD_LEGACY, path), (OLD_OPTIMIZED, path),
        (OLD_LEGACY_PIN, values["context_sha256"]),
        (OLD_OPTIMIZED_PIN, values["context_sha256"]),
        (OLD_LEGACY_MAPPING, values["mapped_package_sha256"]),
        (OLD_OPTIMIZED_MAPPING, values["mapped_package_sha256"]),
        (OLD_LEGACY_NAME, values["legacy_name"]),
        (OLD_OPTIMIZED_NAME, values["current_name"]),
        (OLD_LEGACY_STORE, values["store"]),
        (OLD_OPTIMIZED_STORE, values["store"]),
        (OLD_READER_SHA, values["reader_sha256"]),
        (OLD_NOT_BEFORE, values["not_before"]),
        (OLD_EXPIRES_AT, values["expires_at"]),
        ("_cal_api23_current_legacy_live_20261015093410_31d1bbb85b71", "_cal_api30_current_legacy_local_20261022_0001"),
        ("_cal_api23_current_source8_optimized_0005", "_cal_api30_current_source8_local_20261022_0001"),
    ]


def route_legacy_machine_scope(path: Path) -> None:
    """Select exact API33 helpers for the two legacy Machine origins."""
    old = "generate=selected.generate\n"
    text = path.read_text()
    if text.count(old) != 1:
        raise ValueError("API30 Machine helper export changed")
    old_origin = 'assert Path(selected.__file__).resolve()==PATH/"generation.py"'
    if text.count(old_origin) != 1:
        raise ValueError("API30 Machine helper origin check changed")
    text = text.replace(old_origin, 'if Path(selected.__file__).resolve()!=PATH/"generation.py":\n    raise ValueError("unselected v3 Machine helper")')
    text = text.replace(old, '''_v3_generate=selected.generate
LEGACY_PATH=HERE.parent/"machine-context-scope-v4-api33-legacy-0001"
LEGACY_NAME="_cal_api33_exact_legacy_machine_scope_0001"
CURRENT_LEGACY_PATH=HERE.parent/"machine-context-scope-v5-api33-current-legacy-0001"
CURRENT_LEGACY_NAME="_cal_api33_exact_current_legacy_machine_scope_0001"

def generate(custodian,message,request_raw,mapped_pin,schemas):
    origin=Path(sys.modules[type(custodian).__module__].__file__).name
    if origin not in ('legacy_context_sessions.py','current_legacy_context_sessions.py'):
        return _v3_generate(custodian,message,request_raw,mapped_pin,schemas)
    path,name=(LEGACY_PATH,LEGACY_NAME) if origin=='legacy_context_sessions.py' else (CURRENT_LEGACY_PATH,CURRENT_LEGACY_NAME)
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/"__init__.py",
            submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    exact=__import__(name+".generation",fromlist=["generate"])
    if Path(exact.__file__).resolve()!=path/"generation.py":
        raise ValueError("unselected exact Machine helper")
    return exact.generate(custodian,message,request_raw,mapped_pin,schemas)
''')
    path.write_text(text)


def harden_runtime_selector(path: Path) -> None:
    """Retain exact origin selection when Python assertions are optimized out."""
    text = path.read_text()
    pattern = r"(?m)^(?P<indent>[ \t]*)assert Path\(selected\.__file__\)\.resolve\(\)\s*==\s*(?P<variable>PATH|path)\s*/\s*(?P<literal>['\"][^'\"]+['\"])"
    def explicit(match):
        literal = match.group('literal')
        variable = match.group('variable')
        indent = match.group('indent')
        return f'{indent}if Path(selected.__file__).resolve()!={variable}/{literal}:\n{indent}    raise ValueError("unselected runtime helper")'
    updated, count = re.subn(pattern, explicit, text)
    if count != 1:
        raise ValueError(f"runtime selector origin assertion changed: {path.name}")
    path.write_text(updated)


def harden_retained_expiry_checks(path: Path) -> None:
    text = path.read_text()
    checks = (
        "old['not_before']=='2026-10-12T01:28:58.791379+00:00' and old['expires_at']==EXPECTED_PREVIOUS_EXPIRES_AT",
        "old['original_expired_period_binding']==EXPECTED_ORIGINAL5_PRIOR",
        "earlier['expires_at']=='2026-10-10T02:45:14.443492+00:00'",
    )
    for index, expression in enumerate(checks, 1):
        original = "assert " + expression
        if text.count(original) != 1:
            raise ValueError("retained expired source predicate changed")
        text = text.replace(original, f'if not ({expression}):\n        raise ValueError("retained expired source predicate {index} differs")')
    path.write_text(text)


def harden_fixture_observation(path: Path) -> None:
    text = path.read_text()
    predicates = (
        "root.is_relative_to(Path('/tmp')) and root.resolve()==root",
        "root.stat().st_uid==os.getuid() and root.stat().st_mode&0o777==0o700",
        "path.is_file() and not path.is_symlink()",
        "len(data)<=1024*1024",
    )
    for index, predicate in enumerate(predicates, 1):
        original = "assert " + predicate
        if text.count(original) != 1:
            raise ValueError("fixture observation custody predicate changed")
        text = text.replace(original, f'if not ({predicate}):\n            raise ValueError("fixture observation custody predicate {index} differs")')
    text = text.replace("data=path.read_bytes();if not", "data=path.read_bytes()\n        if not")
    path.write_text(text)


def correct_current_machine_origin(path: Path) -> None:
    old = "Path(C.__file__).resolve().parent.parent==HERE.parent"
    text = path.read_text()
    if text.count(old) != 1:
        raise ValueError("current Machine origin guard changed")
    path.write_text(text.replace(old, "Path(C.__file__).resolve()==HERE/'current_context_sessions.py' and not Path(C.__file__).is_symlink()"))


def enable_current_source8_test_grant(path: Path) -> None:
    """Let the isolated test provisioner bind the selected current Source8 period."""
    old = "if source_name in ('custody-participation','legacy-session-fixture',source.CURRENT_LEGACY_NAME):\n        d=source.legacy_delivery_for(source_name) if source_name in ('legacy-session-fixture',source.CURRENT_LEGACY_NAME) else source.custody_delivery();period=d.reader.HERE/'packages/0001/period.json';p=d.load(period)"
    new = "if source_name in ('custody-participation','legacy-session-fixture',source.CURRENT_LEGACY_NAME,source.CURRENT_SOURCE8_NAME):\n        d=source.current_session_fixture_delivery() if source_name==source.CURRENT_SOURCE8_NAME else source.legacy_delivery_for(source_name) if source_name in ('legacy-session-fixture',source.CURRENT_LEGACY_NAME) else source.custody_delivery();period=d.reader.HERE/'packages/0001/period.json';p=d.load(period)"
    text = path.read_text()
    if text.count(old) != 1:
        raise ValueError("API30 test grant selector changed")
    path.write_text(text.replace(old, new))


def adapt_protocol_guard(path: Path) -> None:
    """Keep the frozen schema closure at its old paths and verify v33 bytes."""
    text = path.read_text()
    old = """mandatory.update(str((HERE/name).relative_to(ROOT)) for name in ('protocol.py','auth.py','service.py','source_bridge.py','guard.py','authentication.schema.json','schema-inputs.json'))
        mandatory.update(str(file.relative_to(ROOT)) for file in (HERE/'schemas').glob('*.schema.json'))"""
    new = """historical=HERE.parent/'api-integration-v30'
        mandatory.update(str((historical/name).relative_to(ROOT)) for name in ('protocol.py','auth.py','service.py','source_bridge.py','guard.py','authentication.schema.json','schema-inputs.json'))
        mandatory.update(str(file.relative_to(ROOT)) for file in (historical/'schemas').glob('*.schema.json'))"""
    if text.count(old) != 1:
        raise ValueError("API30 schema execution closure layout changed")
    text = text.replace(old, new)
    old_end = "        _verify_files(ROOT,[rows[key] for key in sorted(rows)])\n"
    new_end = """        _verify_files(ROOT,[rows[key] for key in sorted(rows)])
        from .guard import verify as verify_successor
        receipt=source.parse((HERE/'rebind-receipt.json').read_bytes())
        source.require(receipt['successor_package']==str(HERE.relative_to(ROOT)),'local successor receipt differs')
        verify_successor(receipt['successor_manifest_sha256'])
"""
    if text.count(old_end) != 1:
        raise ValueError("API30 schema guard verification layout changed")
    path.write_text(text.replace(old_end, new_end))


def select_native_engine_profile(path: Path, values: dict[str, str]) -> None:
    text = path.read_text()
    old = "path=HERE.parent/'custody-correction-v4/runtime/profile.json'"
    if text.count(old) != 2:
        raise ValueError("API30 native profile selectors changed")
    for name in ("CURRENT_SOURCE8_NAME", "CURRENT_LEGACY_NAME"):
        replacement = f"path=ROOT/'{values['engine_profile_path']}' if name=={name} else HERE.parent/'custody-correction-v4/runtime/profile.json'"
        text = text.replace(old, replacement, 1)
    path.write_text(text)


def select_current_authentication_schema(path: Path, values: dict[str, str]) -> None:
    """Replace only two exact fixture aliases in the copied closed schema."""
    text = path.read_text()
    for before, after in ((OLD_LEGACY_NAME, values["legacy_name"]),
                          (OLD_OPTIMIZED_NAME, values["current_name"])):
        if text.count(before) < 1 or after in text:
            raise ValueError("API30 authentication source-name selection changed")
        text = text.replace(before, after)
    json.loads(text)
    path.write_text(text)


def install_native_role_dispositions(path: Path, values: dict[str, str]) -> None:
    """Bind the eight source-retained T12 roles excluded from native artifacts."""
    family = values["family_path"]
    source_package = family + "/source/packages/0001/manifest.json"
    mapped_package = family + "/mapped/packages/0001/manifest.json"
    mapping = family + "/mapped/packages/0001/mapping.json"
    code = '''"""Exact current-family native artifact representability boundary."""
from pathlib import Path
from .protocol import source, ROOT
from .guarded_reads import _active

SOURCE_PACKAGE = ROOT / {source_package!r}
SOURCE_PACKAGE_SHA = {source_package_sha!r}
MAPPED_PACKAGE = ROOT / {mapped_package!r}
MAPPED_PACKAGE_SHA = {mapped_package_sha!r}
MAPPING = ROOT / {mapping!r}
MAPPING_SHA = {mapping_sha!r}
EXCLUDED = frozenset({excluded!r})
REASON = ('Selected signed source retains this T12 Role or RoleAssignment outside the declared native Context selection; '
          'it has no native artifact carrier, so this bounded API read cannot present an artifact reference. '
          'Mapping SHA-256: ' + MAPPING_SHA + '.')

def _exact(path, expected):
    source.require(path.is_file() and not path.is_symlink(), 'native disposition path missing or linked')
    raw = path.read_bytes()
    source.require(source.sha(raw) == expected, 'native disposition bytes differ')
    return raw

def _current(view):
    legacy = getattr(view, 'legacy_context_producer', None)
    modern = getattr(view, 'source8_context_producer', None)
    return ((legacy is not None and legacy.HERE == ROOT / {legacy_context!r}) or
            (modern is not None and modern.HERE == ROOT / {modern_context!r}))

def selected(view):
    if not _current(view):
        return frozenset()
    active = getattr(_active, 'value', None)
    source.require(active is not None and active['view'] is view,
                   'native disposition outside verified original model read batch')
    cached = active.get('native_role_exclusions')
    if cached is not None:
        return cached
    _exact(SOURCE_PACKAGE, SOURCE_PACKAGE_SHA)
    package = source.parse(_exact(MAPPED_PACKAGE, MAPPED_PACKAGE_SHA))
    source.require(package['schema_version'] == 'lab-mapped-context-package/v1-candidate' and
                   [row for row in package['files'] if row['path'] == str(MAPPING.relative_to(ROOT))] ==
                   [{{'path': str(MAPPING.relative_to(ROOT)), 'sha256': MAPPING_SHA}}],
                   'selected native mapping package does not bind mapping bytes')
    data = source.parse(_exact(MAPPING, MAPPING_SHA))
    from .handlers import cut
    origin = getattr(view, 'legacy_original_view', getattr(view, 'source8_original_view', view))
    source.require(data['source_name'] == 'custody-participation' and
                   data['source_package_binding'] ==
                   {{'path': str(SOURCE_PACKAGE.relative_to(ROOT)), 'sha256': SOURCE_PACKAGE_SHA}} and
                   data['source_cut'] == cut(origin),
                   'native disposition source package or cut differs')
    rows = data['projection_dispositions']
    source.require(type(rows) is list and len(rows) == 604 and
                   len({{row['version_ref'] for row in rows}}) == 604 and
                   data['source_closure']['accounted_subjects'] == 604,
                   'native disposition source closure differs')
    by_ref = {{row['version_ref']: row for row in rows}}
    source.require(set(origin.subjects) == set(by_ref),
                   'native disposition subjects differ from selected signed source')
    for ref in EXCLUDED:
        subject = origin.subjects[ref]
        source.require(subject['category'] == 'artifact-instance' and
                       subject['effective_state'] == 'admitted-current' and
                       subject['carrier_ref'] is None and
                       by_ref[ref] == {{'version_ref': ref, 'carrier_ref': None,
                                        'effective_state': 'admitted-current',
                                        'disposition': 'retained-source-outside-declared-context-selection'}},
                       'exact T12 native-unrepresentable role disposition differs')
    active['native_role_exclusions'] = EXCLUDED
    return EXCLUDED

def unrepresentable(view, subject):
    result = subject['version_ref'] in selected(view)
    if result:
        source.require(subject['category'] == 'artifact-instance' and
                       subject['effective_state'] == 'admitted-current' and
                       subject['carrier_ref'] is None,
                       'role exclusion subject changed in selected prefix')
    return result

def excluded_subjects(view):
    refs = selected(view)
    return [view.subjects[ref] for ref in sorted(refs) if ref in view.subjects]

def verify_end(view):
    active = getattr(_active, 'value', None)
    if active is not None and active.get('view') is view and 'native_role_exclusions' in active:
        _exact(SOURCE_PACKAGE, SOURCE_PACKAGE_SHA)
        _exact(MAPPED_PACKAGE, MAPPED_PACKAGE_SHA)
        _exact(MAPPING, MAPPING_SHA)
'''.format(
        source_package=source_package,
        source_package_sha=values["source_package_sha256"],
        mapped_package=mapped_package,
        mapped_package_sha=values["mapped_package_sha256"],
        mapping=mapping,
        mapping_sha=values["mapping_sha256"],
        excluded=EXPECTED_ROLE_EXCLUSIONS,
        legacy_context=values["context_path"],
        modern_context=values["context_path"],
    )
    path.write_text(code)


def apply_native_role_exclusions(output: Path) -> None:
    """Use the same exact bounded predicate in canonical and SQL reads."""
    changes = {
        "artifact_model.py": (
            ("from .guarded_reads import selected_model,model_read_batch\n",
             "from .guarded_reads import selected_model,model_read_batch\nfrom . import native_dispositions as native\n"),
            ("if s['effective_state'] in ('admitted-current','admitted-historical','local-admitted-current','local-admitted-historical')]",
             "if s['effective_state'] in ('admitted-current','admitted-historical','local-admitted-current','local-admitted-historical') and not native.unrepresentable(view,s)]"),
        ),
        "projection.py": (
            ("from .guarded_reads import model_read_batch\n",
             "from .guarded_reads import model_read_batch\nfrom . import native_dispositions as native\n"),
            ("for subject in sorted(view.subjects.values(),key=lambda s:s['version_ref']):\n                    header=artifact_ref(view,subject);",
             "for subject in sorted(view.subjects.values(),key=lambda s:s['version_ref']):\n                    if native.unrepresentable(view,subject):continue\n                    header=artifact_ref(view,subject);"),
            ("if subject['effective_state'] in ('admitted-current','local-admitted-current'):\n                        candidates.setdefault(artifact_ref(view,subject)",
             "if subject['effective_state'] in ('admitted-current','local-admitted-current') and not native.unrepresentable(view,subject):\n                        candidates.setdefault(artifact_ref(view,subject)"),
            ("self.items=references(view);self.relations,self.gaps=connections(view,schemas)",
             "self.items=references(view);self.relations,self.gaps=connections(view,schemas)\n            self.gaps.extend({'subject_ref':subject['version_ref'],'reason':native.REASON} for subject in native.excluded_subjects(view))"),
            ("db.execute('INSERT INTO projection_gap VALUES(?,?,?,?,?,?,?)',(self.ref,'gap:R03-query:'+str(i),scope,g['subject_ref'],\n                        'unclosed-typed-connection','R03/S02/R08','use-needing-connection-closure'))",
             "db.execute('INSERT INTO projection_gap VALUES(?,?,?,?,?,?,?)',(self.ref,'gap:R03-query:'+str(i),scope,g['subject_ref'],\n                        'native-artifact-representation-unavailable' if g['subject_ref'] in native.selected(view) else 'unclosed-typed-connection',\n                        'R03/S02/R08','artifact-representation-unavailable' if g['subject_ref'] in native.selected(view) else 'use-needing-connection-closure'))"),
        ),
        "handlers.py": (
            ("from .projection import Generation\n", "from .projection import Generation\nfrom . import native_dispositions as native\n"),
            ("if subject['effective_state'] in ('admitted-current','local-admitted-current'):\n                heads.setdefault(model.artifact_ref(view,subject)",
             "if subject['effective_state'] in ('admitted-current','local-admitted-current') and not native.unrepresentable(view,subject):\n                heads.setdefault(model.artifact_ref(view,subject)"),
            ("gaps.extend(gap(r['subject_ref'],r['reason'],'use-needing-connection-closure') for r in missing)\n",
             "gaps.extend(gap(r['subject_ref'],r['reason'],'use-needing-connection-closure') for r in missing)\n        gaps.extend(gap(subject['version_ref'],native.REASON,'artifact-representation-unavailable') for subject in native.excluded_subjects(view))\n"),
        ),
        "projection_refresh.py": (
            ("+ str(len(staged.gaps)) + ' unresolved source semantic joins remain explicitly indexed in projection_gap and reported by artifact.query. '",
             "+ str(len(staged.gaps)) + ' source semantic joins or native representation exclusions remain explicitly indexed in projection_gap and reported by artifact.query. '"),
        ),
    }
    for name, replacements in changes.items():
        path = output / name
        text = path.read_text()
        for before, after in replacements:
            if text.count(before) != 1:
                raise ValueError(f"API30 native role exclusion insertion changed: {name}")
            text = text.replace(before, after)
        path.write_text(text)
    path = output / "guarded_reads.py"
    text = path.read_text()
    for family in ("legacy", "Source8"):
        guard = "legacy_view_guard" if family == "legacy" else "source8_view_guard"
        before = ("        finally:\n            del _active.value\n"
                  f"            after_delivery,after_reader,after={guard}(view)\n"
                  "            source.require(after_delivery is delivery and after_reader is reader\n"
                  "                and after_reader.adapter.model is model and methods==(model.artifact_ref,model.record_bytes)\n"
                  f"                and after==before,'{family} original model or prefix changed during read')")
        after = ("        finally:\n            try:\n"
                 "                from .native_dispositions import verify_end\n"
                 "                verify_end(view)\n"
                 "            finally:\n                del _active.value\n"
                 f"                after_delivery,after_reader,after={guard}(view)\n"
                 "                source.require(after_delivery is delivery and after_reader is reader\n"
                 "                    and after_reader.adapter.model is model and methods==(model.artifact_ref,model.record_bytes)\n"
                 f"                    and after==before,'{family} original model or prefix changed during read')")
        if text.count(before) != 1:
            raise ValueError(f"API30 {family} read-exit guard layout changed")
        text = text.replace(before, after)
    path.write_text(text)


def install_local_guard(path: Path) -> None:
    """Keep anchored current-byte verification; omit historical accounting."""
    text = path.read_text()
    marker = "def _accounting(manifest):"
    if text.count(marker) != 1:
        raise ValueError("API30 guard layout changed")
    prefix = text[:text.index(marker)]
    guard = '''def verify(pin):
    """Exact local successor bytes; historical input accounting is unqualified."""
    path = HERE / 'source-manifest.json'
    selected = {'path': str(path.relative_to(ROOT)), 'sha256': pin}
    raw = _capture_exact(ROOT, selected)
    manifest = json.loads(raw)
    required = {'schema_version','environment','authority_effect','actual_owner_outcome',
                'historical_input_accounting_qualified','claim_ceiling','files',
                'family_source_manifest_binding','family_source_package_binding',
                'family_reader_manifest_binding','family_mapped_package_binding',
                'family_mapping_binding',
                'family_context_manifest_binding','family_context_package_binding',
                'profile_binding','engine_profile_binding','predecessor_source_manifest_binding'}
    if set(manifest) != required or manifest['schema_version'] != 'lab-api30-current-source-successor/v1':
        raise ValueError('selected local API successor manifest differs')
    if manifest['environment'] != {'python': platform.python_version(),
                                  'jsonschema': importlib.metadata.version('jsonschema'),
                                  'cryptography': importlib.metadata.version('cryptography')}:
        raise ValueError('API environment differs')
    if manifest['authority_effect'] != 'none' or manifest['actual_owner_outcome'] is not None or manifest['historical_input_accounting_qualified'] is not False:
        raise ValueError('local successor claim exceeded')
    rows = manifest['files']
    if type(rows) is not list or not rows or len({r['path'] for r in rows}) != len(rows):
        raise ValueError('closed unique successor byte rows required')
    package = HERE.relative_to(ROOT).as_posix() + '/'
    helpers = ('machine-context-scope-v3-api25-completion-0001',
               'machine-context-scope-v4-api33-legacy-0001',
               'machine-context-scope-v5-api33-current-legacy-0001')
    helper_paths = {str((HERE.parent / helper / name).relative_to(ROOT))
                    for helper in helpers for name in ('__init__.py','generation.py')}
    actual_helpers = set()
    for row in rows:
        if type(row) is not dict or set(row) != {'path','sha256'} or type(row['path']) is not str or type(row['sha256']) is not str or not re.fullmatch('[a-f0-9]{64}',row['sha256']):
            raise ValueError('invalid successor byte row')
        if row['path'] in helper_paths:
            actual_helpers.add(row['path'])
        elif not row['path'].startswith(package):
            raise ValueError('foreign successor byte row')
    if actual_helpers != helper_paths:
        raise ValueError('external Machine helper closure differs')
    actual = {p.relative_to(ROOT).as_posix() for p in HERE.rglob('*')
              if p.is_file() and p != path and p.name != 'rebind-receipt.json'
              and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.suffix != '.pyc'}
    listed = {r['path'] for r in rows if r['path'].startswith(package)}
    if actual != listed:
        raise ValueError('local successor file set differs')
    selected_bindings = (manifest['family_source_manifest_binding'],
                         manifest['family_source_package_binding'],
                         manifest['family_reader_manifest_binding'],
                         manifest['family_mapped_package_binding'],
                         manifest['family_mapping_binding'],
                         manifest['family_context_manifest_binding'],
                         manifest['family_context_package_binding'],
                         manifest['profile_binding'],
                         manifest['engine_profile_binding'],
                         manifest['predecessor_source_manifest_binding'])
    for binding in selected_bindings:
        _capture_exact(ROOT,binding)
    _verify_files(ROOT,rows)
    for binding in selected_bindings:
        _capture_exact(ROOT,binding)
    if _capture_exact(ROOT,selected) != raw:
        raise ValueError('local successor manifest changed during verification')
    return manifest
'''
    path.write_text(prefix + guard)


def build(family: Path = FAMILY, output: Path = OUTPUT, context_path: Path | None = None) -> dict:
    family = family.resolve(strict=True)
    values = family_values(family, context_path)
    selected_context = ROOT / values["context_path"]
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"successor already exists: {output}")
    if output.parent != OLD.parent or output.name != OUTPUT.name:
        raise ValueError("only the selected disjoint API30 successor path is allowed")
    if not OLD.is_dir():
        raise ValueError("frozen API30 input absent")
    for path in OLD.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"linked API30 input refused: {path}")
        if path.is_file() and (path.suffix in (".pem", ".key") or path.name == "branch.snapshot"):
            raise ValueError(f"private API30 input refused: {path}")
    shutil.copytree(OLD, output, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "receipts"))
    changed: dict[str, dict] = {}
    try:
        for path in sorted(output.rglob("*.py")):
            original = path.read_text()
            updated = original
            substitutions = {}
            for before, after in replacements(values):
                count = updated.count(before)
                if count:
                    updated = updated.replace(before, after)
                    substitutions[before] = count
            if updated != original:
                path.write_text(updated)
                changed[path.relative_to(output).as_posix()] = substitutions
        for name in ("source_bridge.py", "current_context_sessions.py", "current_legacy_context_sessions.py", "machine_auth_scope.py", "legacy_fixture_selection.py"):
            if name not in changed:
                raise ValueError(f"required successor binding unchanged: {name}")
        route_legacy_machine_scope(output / "machine_context_scope.py")
        changed["machine_context_scope.py"] = {"legacy_machine_helper": 1, "current_legacy_machine_helper": 1}
        for name in RUNTIME_SELECTOR_MODULES:
            harden_runtime_selector(output / name)
            changed[name] = {"explicit_runtime_helper_origin": 1}
        harden_retained_expiry_checks(output / "legacy_fixture_selection.py")
        changed["legacy_fixture_selection.py"]["retained_expiry_fail_closed"] = 3
        harden_fixture_observation(output / "fixture_observation.py")
        changed["fixture_observation.py"] = {"explicit_observation_custody": 4}
        correct_current_machine_origin(output / "current_machine_context_scope.py")
        changed["current_machine_context_scope.py"] = {"same_package_exact_origin": 1}
        enable_current_source8_test_grant(output / "fixtures.py")
        changed["fixtures.py"] = {"current_source8_period_selection": 1}
        adapt_protocol_guard(output / "protocol.py")
        changed["protocol.py"] = {"historical_schema_closure_and_current_byte_guard": 1}
        select_native_engine_profile(output / "source_bridge.py", values)
        changed["source_bridge.py"]["exact_native_engine_profile"] = 2
        select_current_authentication_schema(output / "authentication.schema.json", values)
        changed["authentication.schema.json"] = {"exact_current_source_name_aliases": 2}
        install_native_role_dispositions(output / "native_dispositions.py", values)
        changed["native_dispositions.py"] = {"exact_eight_role_dispositions": 8}
        apply_native_role_exclusions(output)
        for name in ("artifact_model.py", "projection.py", "projection_refresh.py", "handlers.py", "guarded_reads.py"):
            changed[name] = {"same_exact_native_representability_predicate": 1}
        install_local_guard(output / "guard.py")
        changed["guard.py"] = {"local_current_byte_guard": 1}
        integration_members = select_current_integration_members(output / "contract-profile.json", output)
        stable_native_executable = retire_ephemeral_native_executable_row(output / "contract-profile.json")
        t06_rows = include_t06_operator_rows(output / "contract-profile.json")
        current_rows = rebind_current_authority_and_retire_system_liblzma(output / "contract-profile.json")
        changed["contract-profile.json"] = {"exact_current_T06_operator_rows": len(t06_rows),
                                            "current_integration_members_origin": integration_members["path"],
                                            "retired_only_ephemeral_native_executable_row": OLD_EPHEMERAL_NATIVE_EXE,
                                            "current_authority_row": current_rows["current_authority"],
                                            "retired_only_system_liblzma_duplicate": current_rows["retired_system_liblzma"]}
        # The copied historical source manifest names historical bytes. Replace it
        # with a manifest of this actual successor; do not rebrand its old closure.
        manifest = output / "source-manifest.json"
        manifest.unlink()
        files = []
        for path in sorted(output.rglob("*")):
            if path.is_file() and path != manifest:
                files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)})
        external = []
        for helper in MACHINE_HELPERS:
            for name in ("__init__.py", "generation.py"):
                path = output.parent / helper / name
                if not path.is_file() or path.is_symlink():
                    raise ValueError(f"exact Machine helper absent: {path}")
                entry = {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}
                external.append(entry)
                files.append(entry)
        bind = lambda path: {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}
        manifest.write_text(json.dumps({"schema_version": "lab-api30-current-source-successor/v1", "files": files,
            "environment": {"python": platform.python_version(), "jsonschema": importlib.metadata.version("jsonschema"),
                            "cryptography": importlib.metadata.version("cryptography")},
            "authority_effect": "none", "actual_owner_outcome": None, "historical_input_accounting_qualified": False,
            "claim_ceiling": "Local API30 successor current-byte and fixture integration only; historical input accounting unqualified.",
            "family_source_manifest_binding": bind(family / "source/source-manifest.json"),
            "family_source_package_binding": bind(family / "source/packages/0001/manifest.json"),
            "family_reader_manifest_binding": bind(family / "reader/source-manifest.json"),
            "family_mapped_package_binding": bind(family / "mapped/packages/0001/manifest.json"),
            "family_mapping_binding": bind(family / "mapped/packages/0001/mapping.json"),
            "family_context_manifest_binding": bind(selected_context / "source-manifest.json"),
            "family_context_package_binding": bind(selected_context / "packages/0001/manifest.json"),
            "profile_binding": bind(output / "contract-profile.json"),
            "engine_profile_binding": bind(ROOT / values["engine_profile_path"]),
            "predecessor_source_manifest_binding": bind(OLD / "source-manifest.json")}, indent=2, sort_keys=True) + "\n")
        receipt = {"result": "PREPARED", "source_package": OLD.relative_to(ROOT).as_posix(),
            "successor_package": output.relative_to(ROOT).as_posix(), "family": values,
            "changed_files": changed, "successor_manifest_sha256": digest(manifest),
            "external_machine_helpers": external,
            "current_integration_members_binding": integration_members,
            "stable_native_executable_binding": stable_native_executable,
            "selected_t06_operator_rows": sorted(t06_rows, key=lambda row: row["path"]),
            "current_authority_and_liblzma_bindings": current_rows,
            "whole_session_classes_tested": False}
        (output / "rebind-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        return receipt
    except BaseException:
        shutil.rmtree(output)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", type=Path, default=FAMILY)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--context-path", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.family, args.output, args.context_path), sort_keys=True))
