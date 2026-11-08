"""Versioned, sanitized diagnostic of the disposable Source→Reader prefix.

This copies the exact reviewed prefix probe and adds allowlisted phase tags and
bounded child metadata. Cleanup receives its own stage before context exit.
Earlier numbered probe and diagnostic sources remain immutable.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile

from .. import role_stage, scratch_reader_probe as reader, scratch_source_probe as source
from ..held_paths import _parse_closed
from ..path_contract import ContractError, require
from .plan import ACTIVE_ROLES, plan


FAMILY = reader.FAMILY
SNAPSHOT = reader.SNAPSHOT
PREFIX_BRIDGE_MARKER = 'len(rows)!=30 or any(_source().get(name)!=digest for name,digest in rows.items())'
STAGES = frozenset((
    'preflight', 'snapshot_capture', 'template_plan', 'prefix_materialization',
    'source_selection', 'source_prestate', 'source_child_running',
    'source_child_postreturn', 'source_poststate', 'reader_selection',
    'reader_prestate', 'reader_child_running', 'reader_child_postreturn',
    'reader_poststate', 'cleanup', 'completed',
))


class DiagnosticState:
    def __init__(self):
        self.stage = 'preflight'
        self.scratch_root: Path | None = None
        self.children: dict[str, dict] = {}

    def step(self, stage: str) -> None:
        require(stage in STAGES, 'closed diagnostic stage required')
        self.stage = stage

    def child(self, name: str, rc: int, stdout: bytes, stderr: bytes) -> None:
        require(name in ('source', 'reader') and name not in self.children and
                type(rc) is int and type(stdout) is bytes and type(stderr) is bytes and
                len(stdout) <= 128 * 1024 and len(stderr) <= 128 * 1024,
                'bounded diagnostic child result required')
        self.children[name] = {
            'return_code': rc,
            'stdout_bytes': len(stdout), 'stdout_sha256': source._sha(stdout),
            'stderr_bytes': len(stderr), 'stderr_sha256': source._sha(stderr),
        }


@contextmanager
def diagnostic_scratch(state: DiagnosticState):
    """Tag cleanup only after a successful body, before context exit."""
    require(type(state) is DiagnosticState, 'diagnostic scratch state required')
    with tempfile.TemporaryDirectory(prefix='lc-u02-05-phase-prefix-') as scratch:
        root = Path(scratch)
        state.scratch_root = root
        yield root
        state.step('cleanup')


def sanitized_failure(state: DiagnosticState, error: Exception) -> dict:
    """Emit only closed codes and counts after disposable context cleanup."""
    require(type(state) is DiagnosticState and state.stage in STAGES,
            'closed diagnostic state required')
    child = ('source' if state.stage.startswith('source_child') else
             'reader' if state.stage.startswith('reader_child') else None)
    rc = state.children.get(child, {}).get('return_code') if child else None
    if rc == 124:
        code = 'CHILD_TIMEOUT'
    elif rc == 125:
        code = 'CHILD_OUTPUT_LIMIT'
    elif rc is not None and rc != 0:
        code = 'CHILD_NONZERO'
    elif isinstance(error, ContractError):
        code = 'CONTRACT_REFUSAL'
    else:
        code = 'UNEXPECTED_EXCEPTION'
    return {
        'status': 'FAIL-disposable-prefix-diagnostic',
        'failure_stage': state.stage,
        'failure_code': code,
        'child_results': dict(state.children),
        'scratch_cleanup_observed': (None if state.scratch_root is None else
                                     not state.scratch_root.exists()),
        'raw_stdout_stderr_or_exception_published': False,
        'actual_host_qualification': False,
        'activation_allowed': False,
    }


def _prefix_bridge(source_sha: str, package_sha: str, reader_sha: str,
                   stage_sha: str) -> bytes:
    """Use the exact reviewed Reader bridge with a 15-leaf early stage bound."""
    text = reader.READER_BRIDGE
    require(text.count(PREFIX_BRIDGE_MARKER) == 1,
            'reviewed Reader stage-count preimage differs')
    text = text.replace(PREFIX_BRIDGE_MARKER,
                        'len(rows)!=15 or any(_source().get(name)!=digest for name,digest in rows.items())')
    for marker, digest in (('__SOURCE_SHA__', source_sha), ('__PACKAGE_SHA__', package_sha),
                           ('__READER_SHA__', reader_sha), ('__STAGE_SHA__', stage_sha)):
        require(text.count(marker) == 1 and len(digest) == 64 and
                all(c in '0123456789abcdef' for c in digest),
                'exact selected prefix bridge pin required')
        text = text.replace(marker, digest)
    compile(text, '<phase-scoped-reader-bridge>', 'exec', optimize=0)
    compile(text, '<phase-scoped-reader-bridge>', 'exec', optimize=2)
    return text.encode()


def _inventory(family_host: Path) -> tuple[dict[str, str], set[str]]:
    files = source._tree_files(family_host)
    dirs = source._tree_dirs(family_host)
    require(all(not name.startswith(('mapped/', 'context/')) for name in files) and
            'mapped' not in dirs and 'context' not in dirs,
            'future Mapper/Context materialized before predecessor selection')
    return files, dirs


def _source_selection(planned, repository_rows: dict[str, dict]) -> tuple[bytes, bytes]:
    """Bind the 15 materialized leaves and selected sparse repository snapshot."""
    stage_rows = list(planned.initial_bindings())
    require(len(stage_rows) == 15 and len(repository_rows) == 1703,
            'exact phase prefix and repository selection required')
    stage_control = (json.dumps(stage_rows, sort_keys=True,
                                separators=(',', ':'), allow_nan=False) + '\n').encode()
    source_manifest = reader._json({
        'schema_version': 'lab-T35-disposable-phase-prefix-source/v2-inactive',
        'files': planned.source_rows(list(repository_rows.values())),
        'environment': {'python': '3.14.4', 'jsonschema': '4.19.2',
                        'cryptography': '46.0.5'},
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'fixture_only': True,
    })
    selected = _parse_closed(source_manifest)
    require(len(selected['files']) == 1718 and
            {row['path'] for row in selected['files'] if row['path'].startswith('/')} ==
            {row['path'] for row in stage_rows},
            'Source selection included future or omitted early materialized role')
    return stage_control, source_manifest


def _reader_argv(snapshot: Path, family_host: Path, bridge: Path) -> list[str]:
    argv = reader._sandbox_argv(snapshot, family_host, '_t35_reader_runner.py')
    target = str(SNAPSHOT / '_t35_external_runtime_capture.py')
    marker = ['--ro-bind', str(family_host), str(FAMILY)]
    index = next((i for i in range(len(argv) - 2) if argv[i:i + 3] == marker), None)
    require(index is not None and bridge.parent == snapshot and bridge.is_file(),
            'exact Reader snapshot overlay target required')
    argv[index + 3:index + 3] = ['--ro-bind', str(bridge), target]
    require(argv.count(target) == 1, 'Reader bridge overlay must be exact and singular')
    return argv


def _fixture_episode(captured: dict[str, bytes]) -> bytes:
    from datetime import datetime, timedelta, timezone
    original = _parse_closed(captured[str(source.EXTRA_INPUTS[0])])
    now = datetime.now(timezone.utc)
    value = {key: item.replace('R03-legacy-session-fixture-0257',
                               'completion-legacy-fixture-source')
             if type(item) is str else item for key, item in original.items()}
    value['not_before'] = (now - timedelta(minutes=1)).isoformat()
    value['expires_at'] = (now + timedelta(hours=23, minutes=59)).isoformat()
    value['purpose'] = 'Phase-scoped disposable Source and Reader fixture only.'
    return reader._json(value)


def probe(state: DiagnosticState) -> dict:
    require(type(state) is DiagnosticState, 'diagnostic state required')
    state.step('preflight')
    require(source.BWRAP.is_file() and source._sha(source.BWRAP.read_bytes()) == source.BWRAP_SHA,
            'exact selected bubblewrap executable differs')
    version = subprocess.check_output([str(source.BWRAP), '--version'], text=True).strip()
    require(version == 'bubblewrap 0.11.1', 'selected bubblewrap version differs')
    with diagnostic_scratch(state) as root:
        snapshot, output = root / 'snapshot', root / 'output'
        snapshot.mkdir(); output.mkdir()
        state.step('snapshot_capture')
        rows, captured = source._source_rows()
        source._copy_snapshot(snapshot, rows, captured)
        (snapshot / '_t35_source_runner.py').write_text(source.SANDBOX_RUNNER)
        (snapshot / '_t35_reader_runner.py').write_text(reader.READER_RUNNER)
        state.step('template_plan')
        layout = role_stage.DisposableLayout(FAMILY, SNAPSHOT, 'legacy-fixture-source')
        staged = role_stage.stage_rows(layout, lambda name: captured[name])
        family_host = output / 'legacy-fixture-source'
        for row in staged:
            name = PurePosixPath(row['output']['path']).name
            raw = row['bytes']
            if row['role'] == 'source' and name.endswith('.py'):
                raw = source._unsealed_source(captured[row['input']['path']], layout, name)
            row['bytes'] = raw
            row['output'] = source._bind(Path(row['output']['path']), raw)
        episode_raw = _fixture_episode(captured)
        role_raw = b'{"schema_version":"lab-T35-disposable-native-role/v1","authority_effect":"none"}\n'
        planned = plan(layout, staged, episode_raw=episode_raw, role_raw=role_raw)
        state.step('prefix_materialization')
        for row in staged:
            if row['role'] not in ACTIVE_ROLES:
                continue
            path = family_host / Path(row['output']['path']).relative_to(str(FAMILY))
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(row['bytes'])
        for suffix, raw in (('source/episode-contract.json', episode_raw),
                            ('source/context-native-role.json', role_raw),
                            ('construction-selection.json', planned.plan_leaf_bytes)):
            path = family_host / suffix
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(raw)
        prefix_files, prefix_dirs = _inventory(family_host)
        planned.check_initial_inventory({str(FAMILY / suffix): digest
                                         for suffix, digest in prefix_files.items()})
        require(prefix_dirs == {'source', 'reader'},
                'initial phase-scoped directories differ')
        state.step('source_selection')
        stage_control, source_manifest = _source_selection(planned, rows)
        (snapshot / '_t35_stage_selection.json').write_bytes(stage_control)
        with (family_host / reader.SOURCE_REL).open('xb') as stream:
            stream.write(source_manifest)
        source_bridge = (source.SCRATCH_BRIDGE.replace('__SOURCE_MANIFEST_SHA__',
                         source._sha(source_manifest)).replace('__STAGE_SELECTION_SHA__',
                         source._sha(stage_control))).encode()
        require(source_bridge.count(b'__SOURCE_MANIFEST_SHA__') == 0 and
                source_bridge.count(b'__STAGE_SELECTION_SHA__') == 0,
                'Source bridge exact pin substitution required')
        with (snapshot / '_t35_external_runtime_capture.py').open('xb') as stream:
            stream.write(source_bridge)
        package_host = family_host / 'source/packages'
        package_host.mkdir()
        state.step('source_prestate')
        pre_files, pre_dirs = _inventory(family_host)
        require(set(pre_files) == set(prefix_files) | {reader.SOURCE_REL} and
                all(pre_files[name] == digest for name, digest in prefix_files.items()) and
                pre_dirs == {'source', 'reader', 'source/packages'},
                'Source/Reader prefix changed before Source child')
        expected_members = source._historical_package_names(
            captured[source.HISTORICAL_SOURCE_PACKAGE['path']])
        source_argv = reader._sandbox_argv(snapshot, family_host,
                                           '_t35_source_runner.py', package_host=package_host)
        state.step('source_child_running')
        source_rc, source_stdout, source_stderr = source._run_bounded(source_argv)
        state.child('source', source_rc, source_stdout, source_stderr)
        state.step('source_child_postreturn')
        require(source_rc == 0 and not source_stderr,
                'phase-scoped Source child failed or emitted diagnostics')
        state.step('source_poststate')
        package_raw, source_post, source_dirs = reader._source_package_verified(
            family_host, pre_files, pre_dirs, expected_members, source_stdout)
        require(len(source_post) == 53 and 'mapped' not in source_dirs and
                'context' not in source_dirs,
                'Source child created a future role or unexpected leaf count')
        package_sha = source._sha(package_raw)
        state.step('reader_selection')
        reader_manifest = reader._reader_manifest(source_manifest, package_raw)
        reader_sha = source._sha(reader_manifest)
        with (family_host / reader.READER_REL).open('xb') as stream:
            stream.write(reader_manifest)
        reader_pre, reader_dirs = _inventory(family_host)
        require(set(reader_pre) == set(source_post) | {reader.READER_REL} and
                all(reader_pre[name] == digest for name, digest in source_post.items()) and
                reader_dirs == source_dirs and len(reader_pre) == 54,
                'Reader manifest changed selected Source/package or future role absence')
        reader_bridge = _prefix_bridge(source._sha(source_manifest), package_sha,
                                       reader_sha, source._sha(stage_control))
        reader_bridge_path = snapshot / '_t35_reader_bridge.py'
        with reader_bridge_path.open('xb') as stream:
            stream.write(reader_bridge)
        source_bridge_unchanged = (
            source._sha((snapshot / '_t35_external_runtime_capture.py').read_bytes()) ==
            source._sha(source_bridge))
        require(source_bridge_unchanged, 'selected Source bridge changed before Reader child')
        state.step('reader_prestate')
        reader_argv = _reader_argv(snapshot, family_host, reader_bridge_path)
        state.step('reader_child_running')
        reader_rc, reader_stdout, reader_stderr = source._run_bounded(reader_argv)
        state.child('reader', reader_rc, reader_stdout, reader_stderr)
        state.step('reader_child_postreturn')
        require(reader_rc == 0 and not reader_stderr,
                'phase-scoped Reader child failed or emitted diagnostics')
        state.step('reader_poststate')
        reader_post, reader_post_dirs = _inventory(family_host)
        unchanged = reader_post == reader_pre and reader_post_dirs == reader_dirs
        require(unchanged, 'phase-scoped Reader changed read-only family')
        selected = reader._reader_output(reader_stdout, reader_sha=reader_sha,
                                         source_sha=source._sha(source_manifest),
                                         package_sha=package_sha)
        summary = {
            'status': 'PASS-fixture-prefix-only',
            'selected_repository_input_count': len(rows),
            'selected_repository_input_selection_sha256': source._sha((json.dumps(
                [rows[name] for name in sorted(rows)], sort_keys=True,
                separators=(',', ':')) + '\n').encode()),
            'prospective_template_count': len(staged),
            'initial_materialized_leaf_count': len(prefix_files),
            'deferred_template_count': len(planned.deferred_bindings()),
            'future_role_directories_absent_before_and_after': True,
            'plan_leaf_sha256': source._sha(planned.plan_leaf_bytes),
            'stage_selection_sha256': source._sha(stage_control),
            'source_manifest_sha256': source._sha(source_manifest),
            'source_package_manifest_sha256': package_sha,
            'reader_manifest_sha256': reader_sha,
            'source_bridge_sha256': source._sha(source_bridge),
            'reader_bridge_sha256': source._sha(reader_bridge),
            'source_bridge_unchanged_for_reader': source_bridge_unchanged,
            'source_runner_sha256': source._sha(source.SANDBOX_RUNNER.encode()),
            'reader_runner_sha256': source._sha(reader.READER_RUNNER.encode()),
            'bwrap_sha256': source.BWRAP_SHA, 'bwrap_version': version,
            'source_argv_shape': ['<sparse-snapshot>' if a == str(snapshot) else
                                  '<disposable-family>' if a == str(family_host) else
                                  '<disposable-package>' if a == str(package_host) else a
                                  for a in source_argv],
            'reader_argv_shape': ['<sparse-snapshot>' if a == str(snapshot) else
                                  '<disposable-family>' if a == str(family_host) else
                                  '<disposable-reader-bridge>' if a == str(reader_bridge_path)
                                  else a
                                  for a in reader_argv],
            'source_post_leaf_count': len(source_post),
            'reader_pre_leaf_count': len(reader_pre),
            'reader_post_leaf_count': len(reader_post),
            'reader_family_tree_unchanged': unchanged,
            'reader_selected_record_count': selected['selected_record_count'],
            'reader_accounted_subject_count': selected['accounted_subject_count'],
            'reader_wrong_pin_refusals': selected['wrong_independent_pin_refusals'],
            'reader_closure_report_sha256': selected['closure_report_sha256'],
            'source_stdout_sha256': source._sha(source_stdout),
            'source_stdout_bytes': len(source_stdout),
            'source_stderr_sha256': source._sha(source_stderr),
            'source_stderr_bytes': len(source_stderr),
            'reader_stdout_sha256': source._sha(reader_stdout),
            'reader_stdout_bytes': len(reader_stdout),
            'reader_stderr_sha256': source._sha(reader_stderr),
            'reader_stderr_bytes': len(reader_stderr),
            'protected_source_used': False,
            'claim_ceiling': 'disposable-15-leaf-Source-Reader-prefix-only',
        }
    require(not root.exists(), 'phase-scoped scratch root remained after cleanup')
    summary['scratch_cleaned_after_return'] = True
    state.step('completed')
    return summary


def diagnose() -> dict:
    state = DiagnosticState()
    try:
        result = probe(state)
        require(state.stage == 'completed' and state.scratch_root is not None and
                not state.scratch_root.exists(), 'successful diagnostic cleanup differs')
    except Exception as error:
        return sanitized_failure(state, error)
    return {
        'status': 'PASS-disposable-prefix-diagnostic',
        'result': result,
        'child_results': dict(state.children),
        'scratch_cleanup_observed': True,
        'raw_stdout_stderr_or_exception_published': False,
        'actual_host_qualification': False,
        'activation_allowed': False,
    }


if __name__ == '__main__':
    import sys
    try:
        result = diagnose()
    except Exception:
        result = {'status': 'FAIL-disposable-prefix-diagnostic',
                  'failure_stage': 'preflight',
                  'failure_code': 'UNEXPECTED_EXCEPTION',
                  'child_results': {},
                  'scratch_cleanup_observed': None,
                  'raw_stdout_stderr_or_exception_published': False,
                  'actual_host_qualification': False,
                  'activation_allowed': False}
    print(json.dumps(result, sort_keys=True, indent=2))
    if result['status'].startswith('FAIL'):
        sys.exit(1)
