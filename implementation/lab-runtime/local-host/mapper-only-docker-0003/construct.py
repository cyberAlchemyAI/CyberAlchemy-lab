"""Inert Mapper projection. Never reads a private archive or runs a role."""
from __future__ import annotations

import ast
import datetime as dt
import hashlib
import json
from pathlib import Path
import os
import resource
import subprocess
import stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
LOCAL = HERE.parent
OLD = "product/lab/release-candidates/v1/interface/legacy-session-fixture-mapped-v2-action-0148"
NEW = "product/lab/release-candidates/v1/interface/docker-mapped-20261020-0001"
READER = "product/lab/release-candidates/v1/interface/docker-reader-20261020-0001"
SOURCE = "product/lab/release-candidates/v1/interface/docker-source-20261020-0001"
STAGE = Path("/tmp/cal-reader-stage-20261020-0001-0008")
ATTEMPT = Path("/tmp/cal-mapper-only-dev-20261020-0001-inert3")
NATIVE = "product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/bin/lab-context-native-reader"
NATIVE_SHA = "fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c"
PROBE = Path('/tmp/cal-mapper-permission-probe-20261020-0003/receipt.json')
PROBE_SHA = 'a52b9a9a054479b381330f92ff1a5e7db242486b5355721c27923b5e3641bf9b'
OLD_PINS = {
    "source": "f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2",
    "package": "8e7b675666308e0e73fb23962b310ea3a89baa48ad6bf2c9cf1c5c9ce9e96964",
    "reader": "0ad1c974a5725d7bf0c23cc08b27c9e4e6c2b4fba512ddc0009aef337e81c0a5",
}
NEW_PINS = {
    "source": "7e0938e70ac00b5308851b5a5a7c7bdb92041efab3be17296998acb4160395c1",
    "package": "f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b",
    "reader": "4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251",
}
PREIMAGES = {
    "__init__.py": "a88e78979e6f4ddfaf89055996e294a92987e42ca63526252a56defb8bc05362",
    "base.py": "02f0481cb20dd81c5e4b6228ce4657987d8960ea9930893434b364a48f5b12ad",
    "build.py": "dced09f9432318ef286475081ea5f4f7e6fa633c7cefbd9db76c0ec3c47ecbbb",
    "policy.json": "1c2ddd360e56666fec0f4ff2095f32369705cff7b96edecbc5ba0720136457ab",
}
COUNTS = {
    "__init__.py": (0, 0, 0), "base.py": (1, 1, 1),
    "build.py": (1, 1, 0), "policy.json": (0, 0, 0),
}
DESIGN_SHA = "49ebe73ec35d0f1d223765626cc215c55f084713bc4f26090a7a3ecb047021c7"
DESIGN_REVIEW_SHA = "e2e06887d9594e4d3bcb8654be4415df02dd42e67922c14695cb620066b4bc3b"
READER_MANIFEST = LOCAL / "fresh-reader-docker-0008/generated" / READER / "source-manifest.json"
STAGE_PLAN = LOCAL / "fresh-reader-docker-0008/stage-plan.json"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def role_projection(name: str, original: bytes, pins: dict[str, str] = NEW_PINS) -> tuple[bytes, dict]:
    require(name in PREIMAGES and digest(original) == PREIMAGES[name], "Mapper preimage differs")
    require(set(pins) == set(OLD_PINS), "three predecessor pins required")
    text = original.decode("utf-8")
    old_source = "legacy-session-fixture-source-v1-action-0148"
    old_reader = "legacy-session-fixture-reader-v1-action-0148"
    old_native = "/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader"
    replacements = {old_source: SOURCE.rsplit("/", 1)[1],
                    old_reader: READER.rsplit("/", 1)[1],
                    old_native: "/attempt/input/lab-context-native-reader"}
    if name == "build.py":
        replacements["p.is_relative_to(HERE/'packages') or p.is_relative_to(HERE/'receipts')"] = (
            "p.is_relative_to(HERE/'packages')")
        replacements["prefix='cal-legacy-session-fixture-0257-seal-')"] = (
            "prefix='cal-legacy-session-fixture-0257-seal-',dir='/attempt/scratch')")
    for key, new in pins.items():
        require(len(new) == 64 and all(c in "0123456789abcdef" for c in new), "invalid new pin")
        replacements[OLD_PINS[key]] = new
    expected = dict(zip(OLD_PINS, COUNTS[name]))
    for key, count in expected.items():
        require(text.count(OLD_PINS[key]) == count, "predecessor occurrence vector differs")
    route_counts = {old: text.count(old) for old in (old_source, old_reader, old_native)}
    require(route_counts == ({old_source: 1, old_reader: 1, old_native: 0} if name == "base.py" else
                             {old_source: 0, old_reader: 0, old_native: 1} if name == "build.py" else
                             {old_source: 0, old_reader: 0, old_native: 0}), "role path vector differs")
    projected = text
    for old, new in replacements.items():
        projected = projected.replace(old, new)
    reverse = projected
    for old, new in reversed(list(replacements.items())):
        reverse = reverse.replace(new, old)
    require(reverse == text, "inverse literal projection differs")
    if name.endswith(".py"):
        for level in (0, 2):
            compile(projected, NEW + "/" + name, "exec", optimize=level)
        require(type(ast.parse(projected)) is ast.Module, "projected AST differs")
    else:
        require(json.loads(projected) == json.loads(text), "policy changed")
    row = {"role": name, "preimage_sha256": digest(original),
           "projection_sha256": digest(projected.encode()),
           "inverse_recovered_sha256": digest(reverse.encode()),
           "predecessor_occurrences": expected,
           "path_occurrences": route_counts,
           "allowed_literals": list(replacements)}
    return projected.encode(), row


def reader_gate(terminal: dict, receipt: dict, external_exit: int,
                reviewed_terminal_sha256: str, terminal_bytes: bytes,
                period: dict, now: dt.datetime) -> None:
    """Pure predecessor gate. Actual call also needs fresh no-follow attachment checks."""
    require(external_exit == 0 and terminal.get("overall") == "PASS" and
            terminal.get("operation") == "PASS" and terminal.get("cleanup") == "PASS" and
            terminal.get("reader_effect") == "DISPOSABLE_READER_DIAGNOSTIC" and
            terminal.get("client_exit") == 0 and terminal.get("daemon_exit") == 0 and
            terminal.get("daemon_exit_consistent") is True and
            terminal.get("absent") is True and terminal.get("forced_cleanup") is False and
            terminal.get("postclose_inputs") == "PASS" and
            terminal.get("output_attachment") == "PASS" and
            terminal.get("stream_or_deadline_failure") is False,
            "Reader terminal or external exit not PASS")
    require(digest(terminal_bytes) == reviewed_terminal_sha256,
            "independent Reader terminal binding differs")
    require(receipt.get("schema_version") == "lab-disposable-reader-receipt/v1-private" and
            receipt.get("reader_manifest_sha256") == NEW_PINS["reader"] and
            receipt.get("source_manifest_sha256") == NEW_PINS["source"] and
            receipt.get("source_package_manifest_sha256") == NEW_PINS["package"] and
            receipt.get("authority_effect") == "none" and
            receipt.get("actual_owner_outcome") is None,
            "Reader receipt predecessor pins differ")
    require(terminal.get("receipt_sha256") == digest(canonical(receipt)),
            "Reader receipt attachment differs")
    require(now.tzinfo is not None and
            dt.datetime.fromisoformat(period["not_before"]) <= now <
            dt.datetime.fromisoformat(period["expires_at"]),
            "selected Source period absent or expired")


def native_abi_gate(raw: bytes, mode: int, program_headers: str,
                    dynamic_headers: str) -> None:
    require(digest(raw) == NATIVE_SHA and mode == 0o755 and raw[:4] == b"\x7fELF" and
            raw[4] == 2 and raw[5] == 1 and int.from_bytes(raw[18:20], "little") == 62,
            "native hash, mode or ELF machine differs")
    require("[Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]" in program_headers,
            "native interpreter differs")
    for needed in ("libgcc_s.so.1", "libc.so.6", "ld-linux-x86-64.so.2"):
        require("Shared library: [" + needed + "]" in dynamic_headers,
                "native required library differs: " + needed)


def resource_gate(fd_soft_limit: int, available_bytes: int, available_inodes: int,
                  attempt_exists: bool) -> None:
    require(not attempt_exists and ATTEMPT.parent == Path("/tmp") and
            STAGE != ATTEMPT and not STAGE.is_relative_to(ATTEMPT) and
            not ATTEMPT.is_relative_to(STAGE), "Mapper attempt occupied or unsafe")
    require(fd_soft_limit >= 1024 and available_bytes >= 512 * 1024 * 1024 and
            available_inodes >= 2200, "insufficient Mapper FD, scratch or inode budget")


def path_graph_gate(plan: dict, projected_build: bytes, *, packages_empty: bool) -> None:
    mounts = plan['container_mounts']
    root = '/workspace'
    mapper = root + '/' + NEW
    packages = mapper + '/packages'
    require(mounts == [
        {'type': 'bind', 'source': str(ATTEMPT / 'root'), 'target': root, 'mode': 'ro'},
        {'type': 'bind', 'source': str(ATTEMPT / 'root' / NEW / 'packages'),
         'target': packages, 'mode': 'rw'},
        {'type': 'bind', 'source': str(ATTEMPT / 'input'),
         'target': '/attempt/input', 'mode': 'ro'},
        {'type': 'tmpfs', 'target': '/attempt/scratch',
         'size_bytes': 536870912, 'mode': '0700', 'uid': 1000, 'gid': 1000},
    ], 'Mapper mount graph differs')
    require(plan['container_env'] == {'TMPDIR': '/attempt/scratch'} and
            plan['output_package_container'] == packages + '/0001' and
            plan['output_package_host'] == str(ATTEMPT / 'root' / NEW / 'packages/0001') and
            plan['source_stage_read_only'] is True and packages_empty,
            'Mapper output/scratch or package freshness differs')
    expected_output = [f'{family}/{cursor:08d}.json'
                       for family in ('semantic', 'governance')
                       for cursor in range(1, 26)] + [
        'request.json', 'native-output.json', 'mapping.json',
        'build-result.json', 'manifest.json']
    require(plan['expected_package_members'] == expected_output and
            len(expected_output) == len(set(expected_output)) == 55 and
            all((packages + '/0001/' + name).startswith(packages + '/0001/') and
                '..' not in name.split('/') for name in expected_output),
            'Mapper 55-leaf output path closure differs')
    source = projected_build.decode()
    require("out=HERE/'packages/0001'" in source and
            "p.is_relative_to(HERE/'packages')" in source and
            "p.is_relative_to(HERE/'packages') or p.is_relative_to(HERE/'receipts')" not in source and
            "dir='/attempt/scratch'" in source and
            "tempfile.TemporaryDirectory(" in source and
            source.count('emit(out/') == 6 and
            all("emit(out/'" + name + "'" in source for name in (
                'request.json', 'native-output.json', 'mapping.json',
                'build-result.json', 'manifest.json')),
            'projected Mapper write/tempfile route differs')
    require(packages.startswith(mapper + '/') and
            not packages.startswith(root + '/' + SOURCE + '/') and
            not packages.startswith(root + '/' + READER + '/') and
            not str(ATTEMPT / 'root').startswith(str(STAGE) + '/'),
            'Mapper output overlaps Source, Reader or consumed stage')


def permission_gate(identity: dict, *, archive_owner: tuple[int, int, int],
                    package_owner: tuple[int, int, int],
                    scratch_owner: tuple[int, int, int],
                    traversed: list[tuple[int, int, int]]) -> None:
    require(identity == {'image_default_user': '20001:20001',
                         'runtime_user': '1000:1000',
                         'runtime_userns': 'host',
                         'host_to_container_uid_gid': 'identity',
                         'launch_flags': ['--user', '1000:1000', '--userns', 'host']},
            'effective container identity is not selected')
    uid, gid = 1000, 1000
    require(archive_owner == (uid, gid, 0o600),
            'private Source archive owner/mode unreadable for selected UID')
    require(package_owner == (uid, gid, 0o700),
            'Mapper package mountpoint owner/mode unwritable for selected UID')
    require(scratch_owner == (uid, gid, 0o700),
            'native scratch owner/mode unwritable for selected UID')
    require(traversed and all(owner == uid and group == gid and mode & 0o100
                             for owner, group, mode in traversed),
            'Source/Reader path traversal unavailable to selected UID')


def selected_stage_permissions() -> tuple[tuple[int, int, int], list[tuple[int, int, int]]]:
    archive = STAGE / 'root' / SOURCE / 'packages/0001/branch.snapshot'
    require(archive.is_relative_to(STAGE / 'root'), 'selected archive path escaped')
    lineage = []
    current = STAGE / 'root'
    for part in archive.relative_to(current).parts[:-1]:
        info = current.lstat()
        require(stat.S_ISDIR(info.st_mode) and not current.is_symlink(),
                'staged traversal path type differs')
        lineage.append((info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)))
        current = current / part
    info = current.lstat()
    require(stat.S_ISDIR(info.st_mode) and not current.is_symlink(),
            'staged archive parent type differs')
    lineage.append((info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)))
    leaf = archive.lstat()
    require(stat.S_ISREG(leaf.st_mode) and not archive.is_symlink(),
            'staged private archive type differs')
    return (leaf.st_uid, leaf.st_gid, stat.S_IMODE(leaf.st_mode)), lineage


def synthetic_probe_gate(receipt: dict) -> None:
    require(receipt.get('schema_version') == 'lab-mapper-synthetic-permission-probe/v1' and
            receipt.get('overall') == 'PASS_SYNTHETIC_ACCESS' and
            receipt.get('image') == 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874' and
            receipt.get('effective_user') == '1000:1000' and
            receipt.get('userns') == 'host' and
            receipt.get('docker_exit') == 0 and
            receipt.get('container_absent') is True and
            receipt.get('timeout') is False and
            receipt.get('synthetic_only') is True and
            receipt.get('no_private_archive_body') is True and
            receipt.get('no_mapper_or_reader_effect') is True and
            receipt.get('observed') == {'uid': 1000, 'gid': 1000,
                                        'archive_read': True, 'reader_read': True,
                                        'package_write': True, 'scratch_write': True,
                                        'tmpdir': '/attempt/scratch'},
            'selected harmless Docker access probe differs')


def build() -> tuple[dict, dict[str, bytes]]:
    require(digest((LOCAL / "MAPPER-DOCKER-NEXT-UNIT-DESIGN-0002.md").read_bytes()) == DESIGN_SHA,
            "reviewed design changed")
    require(digest((LOCAL / "MAPPER-DOCKER-NEXT-UNIT-INDEPENDENT-DESIGN-REVIEW-0002.md").read_bytes()) == DESIGN_REVIEW_SHA,
            "design review changed")
    require(digest(READER_MANIFEST.read_bytes()) == NEW_PINS["reader"], "Reader adapter manifest changed")
    plan_raw = STAGE_PLAN.read_bytes()
    require(digest(plan_raw) == "82ddcf898953881d49cfb1b99ba0b91f4f9c7393cfde5ae3bb9549b5a769e524",
            "stage plan changed")
    plan = json.loads(plan_raw)
    stage_rows = {row["path"]: row["sha256"] for row in plan["files"]}
    require(len(stage_rows) == len(plan["files"]) == 986, "stage plan cardinality differs")
    require(stage_rows.get(SOURCE + "/source-manifest.json") == NEW_PINS["source"] and
            stage_rows.get(SOURCE + "/packages/0001/manifest.json") == NEW_PINS["package"] and
            stage_rows.get(READER + "/source-manifest.json") == NEW_PINS["reader"],
            "three predecessor pins not selected by stage plan")
    reader = json.loads(READER_MANIFEST.read_bytes())
    rows = reader["files"] + [{"path": READER + "/source-manifest.json", "sha256": NEW_PINS["reader"]}]
    require(len(rows) == 949 and all(stage_rows.get(row["path"]) == row["sha256"] for row in rows),
            "Reader public closure not selected by stage")
    require(all(not row["path"].endswith("/branch.snapshot") and
                "legacy-session-fixture-" not in row["path"] for row in rows),
            "historical protected input entered closure")
    source_manifest_bytes = (STAGE / "root" / SOURCE / "source-manifest.json").read_bytes()
    source_package_manifest_bytes = (STAGE / "root" / SOURCE / "packages/0001/manifest.json").read_bytes()
    require(digest(source_manifest_bytes) == NEW_PINS["source"] and
            digest(source_package_manifest_bytes) == NEW_PINS["package"],
            "staged Source predecessor manifest bytes changed")
    source_manifest = json.loads(source_manifest_bytes)
    source_rows = source_manifest["files"]
    reader_rows = {row["path"]: row["sha256"] for row in reader["files"]}
    require(len(source_rows) == 940 and len(reader_rows) == 948 and
            all(reader_rows.get(row["path"]) == row["sha256"] for row in source_rows),
            "public Source closure not preserved by Reader closure")
    generated = {}
    ledger = []
    for name in PREIMAGES:
        raw = (REPO / OLD / name).read_bytes()
        projected, item = role_projection(name, raw)
        generated[name] = projected
        ledger.append(item)
        rows.append({"path": NEW + "/" + name, "sha256": digest(projected)})
    require(len(rows) == 953 and len({r["path"] for r in rows}) == 953, "Mapper static closure differs")
    native = REPO / NATIVE
    require(native.is_file() and not native.is_symlink() and
            digest(native.read_bytes()) == NATIVE_SHA and native.stat().st_mode & 0o777 == 0o755,
            "selected native bytes or mode differ")
    native_raw = native.read_bytes()
    headers = subprocess.run(["readelf", "-l", str(native)], capture_output=True,
                             text=True, check=True)
    dynamic = subprocess.run(["readelf", "-d", str(native)], capture_output=True,
                             text=True, check=True)
    native_abi_gate(native_raw, native.stat().st_mode & 0o777,
                    headers.stdout, dynamic.stdout)
    manifest = {
        "schema_version": "lab-docker-distinct-mapper-source/v1-candidate",
        "authority_effect": "none", "actual_owner_outcome": None,
        "fixture_only": True, "qualification": False,
        "environment": {"python": "3.14.4", "jsonschema": "4.23.0", "cryptography": "46.0.5"},
        "original_source_binding": {"path": SOURCE + "/source-manifest.json", "sha256": NEW_PINS["source"]},
        "original_package_binding": {"path": SOURCE + "/packages/0001/manifest.json", "sha256": NEW_PINS["package"]},
        "adapter_source_binding": {"path": READER + "/source-manifest.json", "sha256": NEW_PINS["reader"]},
        "selected_native_executable": {"path": "/attempt/input/lab-context-native-reader", "sha256": NATIVE_SHA},
        "files": sorted(rows, key=lambda r: r["path"]),
    }
    require(all(not row["path"].endswith("/branch.snapshot") for row in manifest["files"]),
            "private archive entered static manifest")
    identity = {'image_default_user': '20001:20001',
                'runtime_user': '1000:1000',
                'runtime_userns': 'host',
                'host_to_container_uid_gid': 'identity',
                'launch_flags': ['--user', '1000:1000', '--userns', 'host']}
    archive_permission, traversed = selected_stage_permissions()
    permission_gate(identity, archive_owner=archive_permission,
                    package_owner=(1000, 1000, 0o700),
                    scratch_owner=(1000, 1000, 0o700), traversed=traversed)
    probe_raw = PROBE.read_bytes()
    require(digest(probe_raw) == PROBE_SHA, 'synthetic access probe receipt changed')
    synthetic_probe_gate(json.loads(probe_raw))
    mount_plan = {
                "source_stage_read_only": True,
                "destination_exclusive_0700": True,
                "copy_no_follow_no_replace_with_postreadback": True,
                "source_copy_inventory_files": 986,
                "source_copy_inventory_directories": 931,
                "mapper_sibling": NEW,
                "packages_mountpoint_empty_0700": True,
                "package_0001_must_be_absent": True,
                "output_package_host": str(ATTEMPT / "root" / NEW / "packages/0001"),
                "output_package_container": "/workspace/" + NEW + "/packages/0001",
                "expected_package_members": [f'{family}/{cursor:08d}.json'
                                             for family in ('semantic', 'governance')
                                             for cursor in range(1, 26)] + [
                    'request.json', 'native-output.json', 'mapping.json',
                    'build-result.json', 'manifest.json'],
                "container_env": {"TMPDIR": "/attempt/scratch"},
                "container_mounts": [
                    {"type": "bind", "source": str(ATTEMPT / "root"), "target": "/workspace", "mode": "ro"},
                    {"type": "bind", "source": str(ATTEMPT / "root" / NEW / "packages"),
                     "target": "/workspace/" + NEW + "/packages", "mode": "rw"},
                    {"type": "bind", "source": str(ATTEMPT / "input"),
                     "target": "/attempt/input", "mode": "ro"},
                    {"type": "tmpfs", "target": "/attempt/scratch", "size_bytes": 536870912,
                     "mode": "0700", "uid": 1000, "gid": 1000},
                ],
                "excluded": ["checkout", "Docker socket", "historical private family", "consumed Reader stage writable"],
            }
    path_graph_gate(mount_plan, generated['build.py'], packages_empty=True)
    return {"manifest": manifest, "ledger": ledger,
            "container_identity": identity,
            "synthetic_permission_probe": {'path': str(PROBE), 'sha256': PROBE_SHA,
                                            'result': 'PASS_SYNTHETIC_ACCESS',
                                            'proves_private_archive_access': False,
                                            'proves_mapper_effect': False},
            "staged_archive_metadata": {'uid': archive_permission[0],
                                        'gid': archive_permission[1],
                                        'mode': format(archive_permission[2], '04o'),
                                        'body_opened': False},
            "staged_traversal_components": len(traversed),
            "stage_plan_sha256": digest(plan_raw), "stage_files": 986,
            "stage_directories": 931, "fresh_attempt": str(ATTEMPT),
            "copy_from": str(STAGE / "root"), "copy_to": str(ATTEMPT / "root"),
            "reader_requirement": "independently reviewed PASS cold-open receipt, terminal and external OS exit",
            "reader_status_at_freeze": "UNKNOWN on consumed unified3 attempt; no PASS selected",
            "reader_predecessor": {
                "stage_freeze_sha256": "7baa002724d031a1225e73518dee282caf3f9d26a914bdc306788c3873917606",
                "stage_terminal_sha256": "bd45626107f1754b9d108e138fdf3a85dc3b4ed0ffa00cfb1fc304f7974093cd",
                "reader_unified3_terminal_sha256": "77aa45c9776629c213c8ce940b7637d9710a17bc1c41388d7a7df65f2a42f6b1",
                "reader_unified3_external_exit_sha256": "9d90959791638c5def91b38999b6c1a7fbed053827722475156568514bab8046",
                "reader_unified3_external_exit": 2,
                "reader_unified3_overall": "UNKNOWN",
                "reader_cold_open_pass_receipt": None,
            },
            "copy_and_mount_plan": mount_plan,
            "selected_image": {"id": "sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874",
                               "architecture": "amd64", "os": "linux",
                               "python": "3.14.4", "jsonschema": "4.23.0", "cryptography": "46.0.5"},
            "limits_for_later_effect": {"deadline_seconds": 180, "fd_limit": 1024,
                                        "memory_bytes": 1073741824, "scratch_bytes": 536870912,
                                        "output_bytes": 268435456,
                                        "capacity_preflight_proved": False},
            "native": {"original_path": NATIVE, "sha256": NATIVE_SHA,
                       "container_path": "/attempt/input/lab-context-native-reader",
                       "abi": "ELF64 little-endian x86-64 GNU/Linux glibc",
                       "interpreter": "/lib64/ld-linux-x86-64.so.2",
                       "needed": ["libgcc_s.so.1", "libc.so.6"],
                       "container_load_proved": False},
            "effect": "NOT_RUN"}, generated


def main() -> None:
    state, generated = build()
    target = HERE / "generated" / NEW
    require(not target.exists(), "generated Mapper projection exists; no overwrite")
    target.mkdir(parents=True)
    for name, raw in generated.items():
        (target / name).write_bytes(raw)
    (target / "source-manifest.json").write_bytes(canonical(state["manifest"]))
    state["mapper_manifest_sha256"] = digest((target / "source-manifest.json").read_bytes())
    (HERE / "selection.json").write_bytes(canonical(state))
    print(json.dumps({"result": "INERT_CONSTRUCTION_COMPLETE", "effect": "NOT_RUN",
                      "mapper_manifest_sha256": state["mapper_manifest_sha256"],
                      "static_rows": len(state["manifest"]["files"]),
                      "reader_dispatch": "HOLD_UNKNOWN"}, sort_keys=True))


if __name__ == "__main__":
    main()
