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
    return {'generated_build_sha256': hashlib.sha256(raw).hexdigest(),
            'guard_calls': 2, 'seal_calls': 2, 'cold_read_calls': 2,
            'sealed_write_or_temp_sites': 5,
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


def expected_package_files(event_count: int) -> frozenset[str]:
    require(type(event_count) is int and 25 <= event_count <= 256,
            'bounded signed event count required')
    events = {f'{family}/{cursor:08d}.json'
              for family in ('semantic', 'governance')
              for cursor in range(1, event_count + 1)}
    return frozenset(events | {'request.json', 'native-output.json',
                               'mapping.json', 'build-result.json', 'manifest.json'})


def validate_package_paths(paths: object, event_count: int) -> None:
    require(type(paths) in (list, tuple, set, frozenset) and
            all(type(name) is str for name in paths) and
            len(paths) == len(set(paths)) and
            set(paths) == expected_package_files(event_count),
            'Mapper package leaf closure differs')


def require_effect_unavailable() -> None:
    """No effect entrypoint exists until the independently reviewed repair."""
    raise ContractError('Mapper package effect capability is not installed')
