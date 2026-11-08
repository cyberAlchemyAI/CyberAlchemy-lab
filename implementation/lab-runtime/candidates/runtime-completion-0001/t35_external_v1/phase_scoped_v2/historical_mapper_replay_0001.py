"""Inactive, pure contract for two historical Mapper cold native reads.

There is deliberately no process launcher, scratch writer, or publication API.
The selected historical package is evidence of one past run, not a fresh
Source/Reader/Mapper result or a protected Source8 authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat

REPO = Path(__file__).resolve().parents[6]
PACKAGE = REPO / ('product/lab/release-candidates/v1/interface/'
                  'legacy-session-fixture-mapped-v2-action-0148/packages/0001')
INSTALL = REPO / ('product/lab/release-candidates/v1/interface/'
                  'runtime-dependencies-v2-completion-0001/installations/0004')
BWRAP = Path('/usr/bin/bwrap')
SELECTED_RUNTIME = {
    BWRAP: (80424, 0o755, '523da3e7399044be5163aee6f57a77a6bef7454376e28f0a0627920bae1b76b6'),
    INSTALL / 'bin/lab-context-native-reader':
        (20243600, 0o755, 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'),
    INSTALL / 'lib/abi/ld-linux-x86-64.so.2':
        (254864, 0o755, 'bda779ea9e9ad234f60315477d7cfd0bdde861cd8ddd9df8cdaf62f18c4cec14'),
    INSTALL / 'lib/abi/libgcc_s.so.1':
        (187120, 0o644, '9d339ecb409578d6a5d587e6c537a8f9589b8a13fefba30d167433a4b5758bee'),
    INSTALL / 'lib/abi/libc.so.6':
        (2190608, 0o644, '85e64f97e348786a8fb4d9f3d52fec289e2fb86bba20f0731dfe61990525e0f7'),
}
PACKAGE_INVENTORY_SHA256 = 'e38101f67689dc56ba23815a6d6017125bbb391e64757dff643c52876095b4d6'
PACKAGE_FILE_COUNT = 55
PACKAGE_TOTAL_BYTES = 781575
REQUEST_SHA256 = '7c7e658aa0cf9f6eb259cec423a886f6183774fd4236cdfcd2309f1b9e80e3b8'
EXPECTED_STDOUT_SHA256 = '669b5eced4988dbe4fdf562ab82ad605ce671cd37490ec75251e94f06c680177'
EXPECTED_STDOUT_BYTES = 221942
STDOUT_CAP_BYTES = 262144
STDERR_CAP_BYTES = 256
CHILD_TIMEOUT_SECONDS = 30
AGGREGATE_CAP_SECONDS = 90
EXPECTED_BWRAP_VERSION = b'bubblewrap 0.11.1\n'
ATTEMPT_NAME = 'historical-mapper-replay-attempt-0001.json'
RESULT_NAME = 'historical-mapper-replay-result-0001.json'


class ContractError(ValueError):
    pass


def require(ok: bool, code: str) -> None:
    if not ok:
        raise ContractError(code)


def expected_names() -> frozenset[str]:
    return frozenset(
        {f'{family}/{index:08d}.json'
         for family in ('semantic', 'governance')
         for index in range(1, 26)} |
        {'request.json', 'native-output.json', 'mapping.json',
         'build-result.json', 'manifest.json'})


def _regular_bytes(path: Path, size: int, mode: int, digest: str) -> bytes:
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
            info.st_size == size and stat.S_IMODE(info.st_mode) == mode,
            'selected_leaf_metadata')
    raw = path.read_bytes()
    require(len(raw) == size and hashlib.sha256(raw).hexdigest() == digest,
            'selected_leaf_digest')
    require(path.lstat() == info, 'selected_leaf_changed')
    return raw


def static_preflight() -> dict[str, object]:
    """Read only selected checkout/package/runtime; never run native code."""
    runtime = {}
    for path, (size, mode, digest) in SELECTED_RUNTIME.items():
        _regular_bytes(path, size, mode, digest)
        runtime[str(path)] = digest
    for directory in (PACKAGE, PACKAGE / 'semantic', PACKAGE / 'governance'):
        info = directory.lstat()
        require(stat.S_ISDIR(info.st_mode) and
                stat.S_IMODE(info.st_mode) == 0o700,
                'package_directory_metadata')
    actual = set()
    rows = []
    total = 0
    for directory in (PACKAGE, PACKAGE / 'semantic', PACKAGE / 'governance'):
        for leaf in directory.iterdir():
            if leaf.is_dir() and leaf in (PACKAGE / 'semantic',
                                          PACKAGE / 'governance'):
                continue
            name = leaf.relative_to(PACKAGE).as_posix()
            require(name in expected_names() and name not in actual,
                    'package_path_closure')
            info = leaf.lstat()
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                    stat.S_IMODE(info.st_mode) == 0o600,
                    'package_leaf_metadata')
            raw = leaf.read_bytes()
            require(len(raw) == info.st_size and leaf.lstat() == info,
                    'package_leaf_changed')
            digest = hashlib.sha256(raw).hexdigest()
            rows.append([name, len(raw), digest])
            total += len(raw)
            actual.add(name)
    require(actual == expected_names() and len(rows) == PACKAGE_FILE_COUNT and
            total == PACKAGE_TOTAL_BYTES, 'package_inventory_closure')
    rows.sort(key=lambda row: row[0])
    inventory = (json.dumps(rows, separators=(',', ':'), ensure_ascii=True) +
                 '\n').encode()
    require(hashlib.sha256(inventory).hexdigest() == PACKAGE_INVENTORY_SHA256,
            'package_inventory_digest')
    by_name = {row[0]: row for row in rows}
    require(by_name['request.json'][2] == REQUEST_SHA256 and
            by_name['native-output.json'][1:] ==
            [EXPECTED_STDOUT_BYTES, EXPECTED_STDOUT_SHA256],
            'package_replay_selection')
    request = json.loads((PACKAGE / 'request.json').read_bytes())
    output = json.loads((PACKAGE / 'native-output.json').read_bytes())
    require(request['selector']['semantic_cursor'] == 25 and
            request['governance_cursor'] == 25 and
            output['cut']['semantic_cursor'] == 25 and
            output['governance_cursor'] == 25 and
            output['authority_effect'] == 'none' and
            len(output['governed_nodes']) == 15,
            'historical_cut_selection')
    return {'package_inventory_sha256': PACKAGE_INVENTORY_SHA256,
            'package_file_count': PACKAGE_FILE_COUNT,
            'package_total_bytes': PACKAGE_TOTAL_BYTES,
            'runtime_sha256': runtime,
            'expected_stdout_sha256': EXPECTED_STDOUT_SHA256,
            'expected_stdout_bytes': EXPECTED_STDOUT_BYTES,
            'effect_performed': False, 'authority_effect': 'none'}


def _scratch(scratch: Path) -> None:
    require(isinstance(scratch, Path) and scratch.is_absolute() and
            scratch.parent == Path('/tmp') and
            scratch.name.startswith('lc-u02-05-historical-mapper-replay-') and
            '..' not in scratch.parts,
            'task_owned_scratch_path')


def replay_argv(scratch: Path) -> tuple[str, ...]:
    """Exact argv for EACH of two fresh, identical read-only native children."""
    _scratch(scratch)
    selected = scratch / 'selected'
    package = scratch / 'package'
    return tuple([
        str(selected / 'bwrap'), '--die-with-parent', '--unshare-all',
        '--clearenv', '--setenv', 'LC_ALL', 'C',
        '--dir', '/work', '--dir', '/work/abi',
        '--ro-bind', str(selected / 'native'), '/work/native',
        '--ro-bind', str(selected / 'abi/ld-linux-x86-64.so.2'),
        '/work/abi/ld-linux-x86-64.so.2',
        '--ro-bind', str(selected / 'abi/libgcc_s.so.1'),
        '/work/abi/libgcc_s.so.1',
        '--ro-bind', str(selected / 'abi/libc.so.6'),
        '/work/abi/libc.so.6',
        '--ro-bind', str(package), '/work/package',
        '--chdir', '/work', '--',
        '/work/abi/ld-linux-x86-64.so.2', '--inhibit-cache',
        '--library-path', '/work/abi', '/work/native',
        '/work/package/semantic', '/work/package/governance',
        '/work/package/request.json',
    ])


def validate_replay_argv(scratch: Path, argv: object) -> None:
    require(type(argv) in (list, tuple) and
            all(type(item) is str for item in argv) and
            tuple(argv) == replay_argv(scratch), 'replay_argv')


def validate_replays(first: object, second: object,
                     first_stderr: object, second_stderr: object,
                     first_rc: object, second_rc: object,
                     *, first_closed: bool, second_closed: bool,
                     first_forced: bool, second_forced: bool) -> None:
    """Pure observation predicate; process custody is external to this plan."""
    require(type(first) is bytes and type(second) is bytes and
            len(first) <= STDOUT_CAP_BYTES and len(second) <= STDOUT_CAP_BYTES and
            len(first) == len(second) == EXPECTED_STDOUT_BYTES and
            hashlib.sha256(first).hexdigest() == EXPECTED_STDOUT_SHA256 and
            first == second and
            type(first_stderr) is bytes and type(second_stderr) is bytes and
            first_stderr == second_stderr == b'' and
            type(first_rc) is int and type(second_rc) is int and
            first_rc == second_rc == 0 and
            first_closed is True and second_closed is True and
            first_forced is False and second_forced is False,
            'historical_native_replay_observation')
