"""Selected Mapper container entrypoint for one reviewed release attempt."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path('/workspace')
TOOL = Path('/tool')
MAPPER = ROOT / 'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002'
SOURCE = ROOT / 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
READER = ROOT / 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0002'
SCRATCH = Path('/attempt/scratch')
NATIVE = Path('/attempt/input/lab-context-native-reader')
SOURCE_SHA = '2843a67fd28a295f5c175b8d8c2b31f701040bb8d7dedeade8d76bbdf057d1d1'
PACKAGE_SHA = 'bdb5eac92cbb3f96857c4d2ccb00880441d55fb8f1dbbeb5cdaae8d81c720653'
READER_SHA = '048ef6c1f54387fc6e593f38b29723cb06f84649f12e9c75a0340d389b0f5756'
MAPPER_SHA = 'bad889d50a0ba302ae83c9f4d5d9b664417af50cf4a6e4c408dfb50f8680d947'
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
EFFECT_ENABLED = True  # selected container tool; host controller remains disabled


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def selected_topology(uid: int, gid: int, pid: int, env: dict,
                      package_stat: os.stat_result, scratch_stat: os.stat_result,
                      archive_stat: os.stat_result, native_stat: os.stat_result,
                      root_device: int, scratch_mountinfo: bytes) -> None:
    require(uid == gid == 1000 and pid == 1 and
            env.get('TMPDIR') == '/attempt/scratch',
            'selected Mapper process identity or TMPDIR differs')
    require(stat.S_ISDIR(package_stat.st_mode) and
            package_stat.st_uid == package_stat.st_gid == 1000 and
            stat.S_IMODE(package_stat.st_mode) == 0o700,
            'Mapper package mount owner or mode differs')
    require(stat.S_ISDIR(scratch_stat.st_mode) and
            scratch_stat.st_uid == scratch_stat.st_gid == 1000 and
            stat.S_IMODE(scratch_stat.st_mode) == 0o700 and
            scratch_stat.st_dev != root_device,
            'Mapper private scratch tmpfs differs')
    require(stat.S_ISREG(archive_stat.st_mode) and
            archive_stat.st_uid == archive_stat.st_gid == 1000 and
            stat.S_IMODE(archive_stat.st_mode) == 0o600,
            'Mapper selected archive attachment differs')
    require(stat.S_ISREG(native_stat.st_mode) and
            native_stat.st_uid == native_stat.st_gid == 1000 and
            stat.S_IMODE(native_stat.st_mode) == 0o755,
            'Mapper native attachment differs')
    require(b'/attempt/scratch ' in scratch_mountinfo and b' - tmpfs ' in scratch_mountinfo,
            'Mapper scratch mount type differs')


def preflight() -> dict:
    require(not EFFECT_ENABLED, 'inert entrypoint unexpectedly enabled')
    return {'result': 'HOLD_EFFECT_DISABLED', 'effect': 'NOT_RUN',
            'mapper_manifest_sha256': MAPPER_SHA,
            'source_manifest_sha256': SOURCE_SHA,
            'reader_manifest_sha256': READER_SHA,
            'native_sha256': NATIVE_SHA}


def execute(source_pin: str) -> None:
    require(EFFECT_ENABLED, 'Mapper entrypoint effect disabled')
    require(source_pin == SOURCE_SHA, 'selected Mapper source pin differs')
    archive = SOURCE / 'packages/0001/branch.snapshot'
    package_dir = MAPPER / 'packages'
    selected_topology(os.getuid(), os.getgid(), os.getpid(), os.environ,
                      package_dir.lstat(), SCRATCH.lstat(), archive.lstat(),
                      NATIVE.lstat(), ROOT.stat().st_dev,
                      Path('/proc/self/mountinfo').read_bytes())
    require(not (package_dir / '0001').exists() and not package_dir.is_symlink(),
            'Mapper package already occupied')
    require(sha((MAPPER / 'source-manifest.json').read_bytes()) == MAPPER_SHA and
            sha((SOURCE / 'source-manifest.json').read_bytes()) == SOURCE_SHA and
            sha((SOURCE / 'packages/0001/manifest.json').read_bytes()) == PACKAGE_SHA and
            sha((READER / 'source-manifest.json').read_bytes()) == READER_SHA and
            sha(NATIVE.read_bytes()) == NATIVE_SHA,
            'Mapper predecessor manifest or native input differs')
    spec = importlib.util.spec_from_file_location('_cal_mapper_selected', MAPPER / '__init__.py',
                                                  submodule_search_locations=[str(MAPPER)])
    require(spec is not None and spec.loader is not None, 'selected Mapper module unavailable')
    package = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = package
    spec.loader.exec_module(package)
    build = __import__(spec.name + '.build', fromlist=['build'])
    build.build(MAPPER_SHA)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--source-sha256')
    args = parser.parse_args()
    require(args.preflight != bool(args.source_sha256), 'select one Mapper route')
    if args.preflight:
        print(json.dumps(preflight(), sort_keys=True))
    else:
        execute(args.source_sha256)
