"""Inert contract for a future disposable Mapper package effect.

This module only checks selected code and renders/validates proposed native
arguments and output names. It has no process, write, or authority API.
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

from .. import role_stage

REPO = Path(__file__).resolve().parents[6]
LEGACY_BUILD = REPO / ('product/lab/release-candidates/v1/interface/'
                       'legacy-session-fixture-mapped-v2-action-0148/build.py')
RUNTIME_BRIDGE = REPO / ('implementation/lab-runtime/candidates/'
                         'runtime-completion-0001/t35_external_v1/runtime_bridge.py')
NATIVE_CLI = REPO / 'implementation/lab-context/candidates/v1/native/src/main.rs'
SELECTED_SHA = {
    LEGACY_BUILD: 'dced09f9432318ef286475081ea5f4f7e6fa633c7cefbd9db76c0ec3c47ecbbb',
    RUNTIME_BRIDGE: '9e3c8aebcb735a2302fe911d149f1bde275bbbc4f1e3898dc8d7684349533699',
    NATIVE_CLI: 'ef16890fbfd33b78e4e618b30f1a2df12d1526d12560bae62f625dece34c5594',
}
FAMILY = '/work/out/legacy-fixture-source'
PACKAGE = FAMILY + '/mapped/packages/0001'
CONTEXT = FAMILY + '/context'
NATIVE_INPUTS = ('/work/native-input/semantic.json',
                 '/work/native-input/governance.json')
REPLAY_ARGS = (PACKAGE + '/semantic', PACKAGE + '/governance',
               PACKAGE + '/request.json')
ABI_NAMES = ('ld-linux-x86-64.so.2', 'libgcc_s.so.1', 'libc.so.6')


class ContractError(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ContractError(reason)


def selected_sources() -> dict[str, str]:
    """Bind the reviewed historical algorithm, bridge refusal and CLI source."""
    result = {}
    for path, expected in SELECTED_SHA.items():
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected,
                'selected source changed')
        result[str(path.relative_to(REPO))] = expected
    return result


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    found = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name == name]
    require(len(found) == 1, 'selected function shape differs')
    return found[0]


def _calls(node: ast.AST, name: str) -> int:
    return sum(isinstance(item, ast.Call) and
               isinstance(item.func, ast.Name) and item.func.id == name
               for item in ast.walk(node))


def selected_event_count() -> int:
    """Extract the fixed node/relation closure from the pinned selected build."""
    selected_sources()
    build = _function(ast.parse(LEGACY_BUILD.read_bytes()), 'build')

    def required_count(name: str) -> int:
        values = []
        for node in ast.walk(build):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == 'require' and node.args):
                continue
            comparison = node.args[0]
            if (isinstance(comparison, ast.Compare) and len(comparison.ops) == 1
                    and isinstance(comparison.ops[0], ast.Eq)
                    and isinstance(comparison.left, ast.Call)
                    and isinstance(comparison.left.func, ast.Name)
                    and comparison.left.func.id == 'len'
                    and len(comparison.left.args) == 1
                    and isinstance(comparison.left.args[0], ast.Name)
                    and comparison.left.args[0].id == name
                    and len(comparison.comparators) == 1
                    and isinstance(comparison.comparators[0], ast.Constant)
                    and type(comparison.comparators[0].value) is int):
                values.append(comparison.comparators[0].value)
        require(len(values) == 1, 'selected event count predicate differs')
        return values[0]

    nodes = required_count('current')
    declared_relations = required_count('selected_relation_refs')
    relations = required_count('relations')
    require(nodes == 15 and declared_relations == relations == 10,
            'selected source cut count differs')
    request = [node.value for node in ast.walk(build)
               if isinstance(node, ast.Assign) and len(node.targets) == 1
               and isinstance(node.targets[0], ast.Name)
               and node.targets[0].id == 'request']
    require(len(request) == 1 and isinstance(request[0], ast.Dict),
            'selected native request differs')
    cursors = {}
    for node in ast.walk(request[0]):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if (isinstance(key, ast.Constant) and
                        key.value in ('semantic_cursor', 'governance_cursor')):
                    require(isinstance(value, ast.Constant) and
                            type(value.value) is int and key.value not in cursors,
                            'selected native cursor differs')
                    cursors[key.value] = value.value
    count = nodes + relations
    require(cursors == {'semantic_cursor': count, 'governance_cursor': count},
            'selected request cursor differs from signed cut')
    return count


def inspect_generated_builder() -> dict[str, object]:
    """Show the exact sealed call sites, not approval to bypass the seals."""
    selected_sources()
    layout = role_stage.DisposableLayout(Path(FAMILY), Path('/work/snapshot'),
                                         'legacy-fixture-source')
    raw = role_stage.render_python(LEGACY_BUILD.read_bytes(), layout=layout,
                                   role='mapped', name='build.py')
    tree = ast.parse(raw)
    build, emit, seal, call = (_function(tree, name)
                               for name in ('build', 'emit', 'seal', 'call'))
    require([ast.unparse(item) for item in build.body[:5]] == [
        'guard(pin)', 'started = time.monotonic()',
        "out = HERE / 'packages/0001'",
        "require(not out.exists(), 'mapped package already exists')",
        '_t35_effect_refused()'],
        'package precreate conflict topology differs')
    require(_calls(build, 'guard') == 2 and _calls(build, 'seal') == 2 and
            _calls(build, 'call') == 2 and _calls(build, 'emit') == 6,
            'generated Mapper build call topology differs')
    require(_calls(build, '_t35_effect_refused') == 1 and
            _calls(emit, '_t35_effect_refused') == 2 and
            _calls(seal, '_t35_effect_refused') == 2 and
            _calls(call, 'run_native') == 1,
            'generated Mapper effect seal topology differs')
    bridge = RUNTIME_BRIDGE.read_text()
    require("raise RuntimeError('No selected native executor or phase effect capability is installed')"
            in bridge, 'native bridge is no longer refused')
    cli = NATIVE_CLI.read_text()
    require('args.len() == 3 && args[1] == "seal-fixture"' in cli and
            'if args.len() != 4' in cli,
            'selected native CLI topology differs')
    count = selected_event_count()
    return {'generated_build_sha256': hashlib.sha256(raw).hexdigest(),
            'guard_calls': 2, 'seal_calls': 2, 'cold_read_calls': 2,
            'sealed_write_or_temp_sites': 5,
            'selected_event_count': count,
            'expected_package_leaf_count': 2 * count + 5,
            'precreated_package_conflicts_with_builder': True,
            'bridge_native_refused': True,
            'package_effect_ready': False}


def native_args(step: int) -> tuple[str, ...]:
    """Exact in-sandbox CLI arguments for two seals then two cold reads."""
    require(type(step) is int and 0 <= step < 4, 'native step outside closed sequence')
    if step < 2:
        return ('seal-fixture', NATIVE_INPUTS[step])
    return REPLAY_ARGS


def validate_native_args(step: int, args: object) -> None:
    require(type(args) in (tuple, list) and all(type(x) is str for x in args)
            and tuple(args) == native_args(step),
            'native invocation outside exact four-call contract')


def native_sandbox_argv(scratch: Path, step: int) -> tuple[str, ...]:
    """Pure proposed read-only Bubblewrap command; no file is touched."""
    require(isinstance(scratch, Path) and scratch.is_absolute() and
            scratch.parent == Path('/tmp') and
            scratch.name.startswith('lc-u02-05-mapper-package-') and
            '..' not in scratch.parts,
            'task-owned absolute scratch path required')
    args = native_args(step)
    selected = scratch / 'selected'
    mounts = [
        '--ro-bind', str(selected / 'native'), '/work/native',
    ]
    for name in ABI_NAMES:
        mounts += ['--ro-bind', str(selected / 'abi' / name),
                   '/work/abi/' + name]
    if step < 2:
        mounts += ['--ro-bind', str(scratch / 'native-input' /
                                    ('semantic.json' if step == 0 else 'governance.json')),
                   NATIVE_INPUTS[step]]
    else:
        mounts += ['--ro-bind', str(scratch / 'output/legacy-fixture-source/'
                                    'mapped/packages/0001'), PACKAGE]
    return tuple([
        str(selected / 'bwrap'), '--die-with-parent', '--unshare-all',
        '--clearenv', '--setenv', 'LC_ALL', 'C',
        '--dir', '/work', '--dir', '/work/abi',
        '--dir', '/work/native-input', '--dir', '/work/out',
        '--dir', FAMILY, '--dir', FAMILY + '/mapped',
        '--dir', FAMILY + '/mapped/packages',
        *mounts, '--chdir', '/work', '--',
        '/work/abi/ld-linux-x86-64.so.2', '--inhibit-cache',
        '--library-path', '/work/abi', '/work/native', *args])


def validate_native_sandbox_argv(scratch: Path, step: int,
                                 argv: object) -> None:
    require(type(argv) in (tuple, list) and all(type(x) is str for x in argv)
            and tuple(argv) == native_sandbox_argv(scratch, step),
            'native sandbox command differs')


def builder_sandbox_argv(scratch: Path) -> tuple[str, ...]:
    """Pure proposed builder argv: family is read-only; IPC fd is inherited."""
    require(isinstance(scratch, Path) and scratch.is_absolute() and
            scratch.parent == Path('/tmp') and
            scratch.name.startswith('lc-u02-05-mapper-package-') and
            '..' not in scratch.parts,
            'task-owned absolute scratch path required')
    snapshot = scratch / 'snapshot'
    family_host = scratch / 'output/legacy-fixture-source'
    return tuple([
        str(scratch / 'selected/bwrap'), '--die-with-parent', '--unshare-all',
        '--clearenv', '--setenv', 'PATH', '/usr/bin:/bin',
        '--setenv', 'HOME', '/nonexistent', '--setenv', 'TMPDIR', '/nonexistent',
        '--setenv', 'LC_ALL', 'C.UTF-8',
        '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib',
        '--ro-bind', '/lib64', '/lib64',
        '--dir', '/work', '--dir', '/work/out',
        '--ro-bind', str(snapshot), '/work/snapshot',
        '--ro-bind', str(family_host), FAMILY,
        '--ro-bind', str(snapshot / '_t35_mapper_package_bridge.py'),
        '/work/snapshot/_t35_external_runtime_capture.py',
        '--chdir', '/work', '--', '/usr/bin/python3', '-I', '-B',
        '/work/snapshot/_t35_mapper_package_runner.py'])


def validate_builder_sandbox_argv(scratch: Path, argv: object) -> None:
    require(type(argv) in (tuple, list) and all(type(x) is str for x in argv)
            and tuple(argv) == builder_sandbox_argv(scratch),
            'builder sandbox command differs')


def expected_package_files(event_count: int) -> frozenset[str]:
    require(type(event_count) is int and
            event_count == selected_event_count(),
            'selected signed event count required')
    events = {f'{family}/{cursor:08d}.json'
              for family in ('semantic', 'governance')
              for cursor in range(1, event_count + 1)}
    return frozenset(events | {'request.json', 'native-output.json',
                               'mapping.json', 'build-result.json', 'manifest.json'})


def validate_package_paths(paths: object, event_count: int) -> None:
    """Names only; a future held nofollow inventory must verify custody."""
    require(type(paths) in (list, tuple, set, frozenset) and
            all(type(name) is str for name in paths) and
            len(paths) == len(set(paths)) and
            set(paths) == expected_package_files(event_count),
            'Mapper package leaf closure differs')


def validate_inventory_model(directories: object, files: object,
                             manifest_hashes: object, *, uid: int,
                             gid: int) -> None:
    """Pure model for future held-nofollow poststate observations.

    The effect controller must gather these rows through held dirfds and
    nofollow stat/open; this model never inspects a live filesystem.
    """
    require(type(uid) is int and uid >= 0 and type(gid) is int and gid >= 0
            and type(directories) is dict and type(files) is dict and
            type(manifest_hashes) is dict,
            'closed inventory model required')
    expected = expected_package_files(selected_event_count())
    require(set(directories) == {'.', 'semantic', 'governance'} and
            set(files) == expected and
            set(manifest_hashes) == expected - {'manifest.json'},
            'package inventory names differ')
    for row in directories.values():
        require(type(row) is dict and row ==
                {'type': 'directory', 'mode': 0o700, 'uid': uid, 'gid': gid},
                'package directory custody differs')
    for name, row in files.items():
        require(type(row) is dict and set(row) ==
                {'type', 'mode', 'uid', 'gid', 'nlink', 'sha256'} and
                row['type'] == 'regular' and row['mode'] == 0o600 and
                row['uid'] == uid and row['gid'] == gid and row['nlink'] == 1 and
                type(row['sha256']) is str and len(row['sha256']) == 64 and
                all(c in '0123456789abcdef' for c in row['sha256']),
                'package leaf custody differs')
        if name != 'manifest.json':
            require(manifest_hashes[name] == row['sha256'],
                    'manifest leaf hash differs')


def require_effect_unavailable() -> None:
    """No effect entrypoint exists until the independently reviewed repair."""
    raise ContractError('Mapper package effect capability is not installed')
