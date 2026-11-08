"""Two bounded Source→Reader attempts over one frozen disposable input vector.

The repository input bytes and fixture episode/control bytes are captured once.
Each attempt has its own scratch family and a sanitized phase outcome. Fresh
fixture signer output may differ, but the selected input vector may not.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import tempfile
import time

from .. import evidence_guard, role_stage, scratch_reader_probe as reader, scratch_source_probe as source
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
CHILD_SECONDS = 180
PAIR_WALL_SECONDS = 900
EPISODE_MARGIN_SECONDS = 60
SELECTION_KEYS = frozenset(('plan_leaf', 'stage_control', 'source_manifest'))
ATTEMPT_NAMES = ('phase-pair-attempt-0001.json', 'phase-pair-attempt-0002.json')
SUMMARY_NAME = 'phase-pair-summary-0001.json'
HEX_SHA = re.compile(r'[0-9a-f]{64}\Z')


def _json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       allow_nan=False) + '\n').encode()


def _sha(value: object) -> str:
    require(type(value) is str and HEX_SHA.fullmatch(value) is not None,
            'closed digest required')
    return value


def _episode_window(vector: 'FrozenVector', now: datetime | None = None) -> dict:
    episode = _parse_closed(vector.episode_raw)
    require(type(episode) is dict and type(episode.get('not_before')) is str and
            type(episode.get('expires_at')) is str, 'closed fixture episode period required')
    try:
        start = datetime.fromisoformat(episode['not_before'])
        end = datetime.fromisoformat(episode['expires_at'])
    except ValueError as exc:
        raise ContractError('fixture episode timestamps invalid') from exc
    now = now or datetime.now(timezone.utc)
    require(start.tzinfo is not None and end.tzinfo is not None and
            start <= now and end >= now + timedelta(seconds=PAIR_WALL_SECONDS + EPISODE_MARGIN_SECONDS),
            'fixture episode cannot cover registered pair window')
    return {'not_before_sha256': source._sha(episode['not_before'].encode()),
            'expires_at_sha256': source._sha(episode['expires_at'].encode()),
            'effect_capture_watchdog_seconds': PAIR_WALL_SECONDS,
            'expiration_margin_seconds': EPISODE_MARGIN_SECONDS}


@contextmanager
def _wall_watchdog():
    """Bound the complete capture and two-child experiment in this process."""
    inherited_mask = signal.pthread_sigmask(signal.SIG_BLOCK, set())
    require(signal.SIGALRM not in inherited_mask,
            'inherited SIGALRM mask disables pair watchdog')
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    require(previous_timer == (0.0, 0.0), 'existing process alarm prevents pair watchdog')
    previous_handler = signal.getsignal(signal.SIGALRM)
    def expired(_signum, _frame):
        raise TimeoutError('registered pair wall time exhausted')
    signal.signal(signal.SIGALRM, expired)
    deadline = time.monotonic() + PAIR_WALL_SECONDS
    signal.setitimer(signal.ITIMER_REAL, PAIR_WALL_SECONDS)
    try:
        yield deadline
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)


def _remaining_child_seconds(deadline: float | None) -> int:
    if deadline is None:
        return CHILD_SECONDS
    remaining = deadline - time.monotonic()
    require(remaining > 1, 'registered pair wall time exhausted before child')
    return min(CHILD_SECONDS, max(1, int(remaining)))


@contextmanager
def _receipt_write_window():
    """Suspend our watchdog across an O_EXCL write/fsync/held-parent check.

    An I/O failure can still strand a partial numbered leaf. Such a leaf is
    preserved and blocks another numbered attempt; it is never removed here.
    """
    prior_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
    try:
        remaining, interval = signal.getitimer(signal.ITIMER_REAL)
        if remaining <= 0:
            yield
            return
        signal.setitimer(signal.ITIMER_REAL, 0)
        started = time.monotonic()
        try:
            yield
        finally:
            left = remaining - (time.monotonic() - started)
            signal.setitimer(signal.ITIMER_REAL, max(0.000001, left), interval)
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, prior_mask)


@dataclass(frozen=True)
class FrozenVector:
    selected: tuple[tuple[str, str, bytes], ...]
    episode_raw: bytes
    role_raw: bytes
    sha256: str

    @classmethod
    def from_selected(cls, rows: dict[str, dict], captured: dict[str, bytes],
                      episode_raw: bytes, role_raw: bytes) -> 'FrozenVector':
        require(type(rows) is dict and type(captured) is dict and len(rows) == 1703 and
                set(rows) == set(captured) and type(episode_raw) is bytes and
                type(role_raw) is bytes and episode_raw and role_raw,
                'exact captured repository and episode/control vector required')
        selected = []
        for name in sorted(rows):
            row, raw = rows[name], captured[name]
            source.check_binding(row, kind='source_api')
            require(row['path'] == name and type(raw) is bytes and
                    source._sha(raw) == row['sha256'],
                    'frozen repository input bytes differ from selected row')
            selected.append((name, row['sha256'], raw))
        digest_input = {
            'repository_rows': [{'path': name, 'sha256': digest}
                                for name, digest, _ in selected],
            'episode_sha256': source._sha(episode_raw),
            'role_sha256': source._sha(role_raw),
        }
        digest = source._sha((json.dumps(digest_input, sort_keys=True,
                                        separators=(',', ':'), allow_nan=False) + '\n').encode())
        return cls(tuple(selected), bytes(episode_raw), bytes(role_raw), digest)

    def rows(self) -> dict[str, dict]:
        return {name: {'path': name, 'sha256': digest}
                for name, digest, _ in self.selected}

    def captured(self) -> dict[str, bytes]:
        return {name: raw for name, _, raw in self.selected}


class DiagnosticState:
    def __init__(self):
        self.stage = 'preflight'
        self.scratch_root: Path | None = None
        self.children: dict[str, dict] = {}
        self.selection: dict[str, str] = {}

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
    elif isinstance(error, TimeoutError):
        code = 'PAIR_WALL_TIMEOUT'
    elif isinstance(error, ContractError):
        code = 'CONTRACT_REFUSAL'
    else:
        code = 'UNEXPECTED_EXCEPTION'
    return {
        'status': 'FAIL-disposable-prefix-diagnostic',
        'failure_stage': state.stage,
        'failure_code': code,
        'child_results': dict(state.children),
        'selection_sha256': dict(state.selection),
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


def probe(state: DiagnosticState, vector: FrozenVector,
          deadline: float | None = None) -> dict:
    require(type(state) is DiagnosticState and type(vector) is FrozenVector,
            'diagnostic state and frozen input vector required')
    state.step('preflight')
    require(source.BWRAP.is_file() and source._sha(source.BWRAP.read_bytes()) == source.BWRAP_SHA,
            'exact selected bubblewrap executable differs')
    version = subprocess.check_output([str(source.BWRAP), '--version'], text=True).strip()
    require(version == 'bubblewrap 0.11.1', 'selected bubblewrap version differs')
    with diagnostic_scratch(state) as root:
        snapshot, output = root / 'snapshot', root / 'output'
        snapshot.mkdir(); output.mkdir()
        state.step('snapshot_capture')
        rows, captured = vector.rows(), vector.captured()
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
        episode_raw = vector.episode_raw
        role_raw = vector.role_raw
        planned = plan(layout, staged, episode_raw=episode_raw, role_raw=role_raw)
        state.selection['plan_leaf'] = source._sha(planned.plan_leaf_bytes)
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
        state.selection['stage_control'] = source._sha(stage_control)
        state.selection['source_manifest'] = source._sha(source_manifest)
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
        source_rc, source_stdout, source_stderr = source._run_bounded(
            source_argv, timeout=_remaining_child_seconds(deadline))
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
        reader_rc, reader_stdout, reader_stderr = source._run_bounded(
            reader_argv, timeout=_remaining_child_seconds(deadline))
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


def diagnose(vector: FrozenVector, deadline: float | None = None) -> dict:
    state = DiagnosticState()
    try:
        result = probe(state, vector, deadline)
        require(state.stage == 'completed' and state.scratch_root is not None and
                not state.scratch_root.exists(), 'successful diagnostic cleanup differs')
    except Exception as error:
        failure = sanitized_failure(state, error)
        failure['input_vector_sha256'] = vector.sha256
        return failure
    return {
        'status': 'PASS-disposable-prefix-diagnostic',
        'input_vector_sha256': vector.sha256,
        'result': result,
        'child_results': dict(state.children),
        'selection_sha256': dict(state.selection),
        'scratch_cleanup_observed': True,
        'raw_stdout_stderr_or_exception_published': False,
        'actual_host_qualification': False,
        'activation_allowed': False,
    }


SAFE_RESULT_COUNTS = frozenset((
    'selected_repository_input_count', 'prospective_template_count',
    'initial_materialized_leaf_count', 'deferred_template_count',
    'source_post_leaf_count', 'reader_pre_leaf_count', 'reader_post_leaf_count',
    'reader_selected_record_count', 'reader_accounted_subject_count',
    'reader_wrong_pin_refusals', 'source_stdout_bytes', 'source_stderr_bytes',
    'reader_stdout_bytes', 'reader_stderr_bytes',
))
SAFE_RESULT_HASHES = frozenset((
    'selected_repository_input_selection_sha256', 'plan_leaf_sha256',
    'stage_selection_sha256', 'source_manifest_sha256',
    'source_package_manifest_sha256', 'reader_manifest_sha256',
    'source_bridge_sha256', 'reader_bridge_sha256', 'source_runner_sha256',
    'reader_runner_sha256', 'bwrap_sha256', 'reader_closure_report_sha256',
    'source_stdout_sha256', 'source_stderr_sha256', 'reader_stdout_sha256',
    'reader_stderr_sha256',
))
SAFE_RESULT_TRUE = frozenset((
    'future_role_directories_absent_before_and_after',
    'source_bridge_unchanged_for_reader', 'reader_family_tree_unchanged',
    'scratch_cleaned_after_return',
))
SAFE_RESULT_EXACT = {
    'status': 'PASS-fixture-prefix-only', 'bwrap_version': 'bubblewrap 0.11.1',
    'protected_source_used': False,
    'claim_ceiling': 'disposable-15-leaf-Source-Reader-prefix-only',
}
RAW_RESULT_FIELDS = (SAFE_RESULT_COUNTS | SAFE_RESULT_HASHES | SAFE_RESULT_TRUE |
                     frozenset(SAFE_RESULT_EXACT) |
                     frozenset(('source_argv_shape', 'reader_argv_shape')))
CHILD_FIELDS = frozenset(('return_code', 'stdout_bytes', 'stdout_sha256',
                          'stderr_bytes', 'stderr_sha256'))


def _safe_children(value: object) -> dict:
    require(type(value) is dict and set(value) <= {'source', 'reader'},
            'closed child result names required')
    safe = {}
    for name, row in value.items():
        require(type(row) is dict and set(row) == CHILD_FIELDS and
                type(row['return_code']) is int and -255 <= row['return_code'] <= 255 and
                all(type(row[key]) is int and 0 <= row[key] <= 128 * 1024
                    for key in ('stdout_bytes', 'stderr_bytes')),
                'closed bounded child metadata required')
        for key in ('stdout_sha256', 'stderr_sha256'):
            _sha(row[key])
        safe[name] = dict(row)
    return safe


def _safe_selection(value: object) -> dict:
    require(type(value) is dict and set(value) <= SELECTION_KEYS,
            'closed derived selection required')
    return {key: _sha(digest) for key, digest in value.items()}


def _safe_attempt(number: int, outcome: dict, vector: FrozenVector) -> dict:
    """Project every recursive field to a closed public metadata schema."""
    require(number in (1, 2) and type(outcome) is dict and
            outcome.get('input_vector_sha256') == vector.sha256,
            'attempt and frozen vector differ')
    status = outcome.get('status')
    if status == 'SKIPPED-unclean-prior-attempt':
        require(set(outcome) == {'status', 'input_vector_sha256'},
                'closed skipped attempt required')
        return {'attempt': number, 'status': status,
                'input_vector_sha256': vector.sha256,
                'scratch_cleanup_observed': None}
    common = {'status', 'input_vector_sha256', 'child_results',
              'selection_sha256', 'scratch_cleanup_observed',
              'raw_stdout_stderr_or_exception_published',
              'actual_host_qualification', 'activation_allowed'}
    require(type(outcome.get('scratch_cleanup_observed')) in (bool, type(None)) and
            outcome.get('raw_stdout_stderr_or_exception_published') is False and
            outcome.get('actual_host_qualification') is False and
            outcome.get('activation_allowed') is False,
            'diagnostic authority or cleanup claim differs')
    safe = {
        'attempt': number, 'status': status,
        'input_vector_sha256': vector.sha256,
        'child_results': _safe_children(outcome.get('child_results')),
        'selection_sha256': _safe_selection(outcome.get('selection_sha256')),
        'scratch_cleanup_observed': outcome['scratch_cleanup_observed'],
        'raw_stdout_stderr_or_exception_published': False,
        'actual_host_qualification': False, 'activation_allowed': False,
    }
    if status == 'FAIL-disposable-prefix-diagnostic':
        require(set(outcome) == common | {'failure_stage', 'failure_code'} and
                outcome.get('failure_stage') in STAGES and
                outcome.get('failure_code') in {'CHILD_TIMEOUT', 'CHILD_OUTPUT_LIMIT',
                    'CHILD_NONZERO', 'CONTRACT_REFUSAL', 'UNEXPECTED_EXCEPTION',
                    'PAIR_WALL_TIMEOUT'},
                'closed failure metadata required')
        safe['failure_stage'] = outcome['failure_stage']
        safe['failure_code'] = outcome['failure_code']
        return safe
    require(status == 'PASS-disposable-prefix-diagnostic' and
            set(outcome) == common | {'result'} and
            outcome['scratch_cleanup_observed'] is True and
            set(safe['child_results']) == {'source', 'reader'} and
            all(row['return_code'] == 0 for row in safe['child_results'].values()) and
            set(safe['selection_sha256']) == SELECTION_KEYS,
            'closed successful attempt required')
    result = outcome['result']
    require(type(result) is dict and set(result) == RAW_RESULT_FIELDS and
            all(type(result[key]) is int and 0 <= result[key] <= 1000000
                for key in SAFE_RESULT_COUNTS) and
            all(result[key] is True for key in SAFE_RESULT_TRUE) and
            all(result[key] == expected for key, expected in SAFE_RESULT_EXACT.items()),
            'closed successful prefix result required')
    for key in SAFE_RESULT_HASHES:
        _sha(result[key])
    require(type(result['source_argv_shape']) is list and
            type(result['reader_argv_shape']) is list and
            all(type(item) is str and len(item) <= 512
                for argv in (result['source_argv_shape'], result['reader_argv_shape'])
                for item in argv) and
            all(len(argv) <= 128 for argv in
                (result['source_argv_shape'], result['reader_argv_shape'])),
            'bounded private argv-shape input required')
    safe['result'] = {key: result[key] for key in sorted(
        SAFE_RESULT_COUNTS | SAFE_RESULT_HASHES | SAFE_RESULT_TRUE |
        frozenset(SAFE_RESULT_EXACT))}
    require(safe['selection_sha256']['plan_leaf'] == result['plan_leaf_sha256'] and
            safe['selection_sha256']['stage_control'] == result['stage_selection_sha256'] and
            safe['selection_sha256']['source_manifest'] == result['source_manifest_sha256'],
            'derived selected inputs differ from result')
    return safe


def _selection_equal(attempts: list[dict]) -> bool | None:
    if len(attempts) != 2 or any(row['status'] != 'PASS-disposable-prefix-diagnostic'
                                 for row in attempts):
        return None
    first, second = (row['selection_sha256'] for row in attempts)
    return (set(first) == set(second) == SELECTION_KEYS and first == second)


def pair(vector: FrozenVector, *, deadline: float | None = None,
         publish_attempt=None) -> dict:
    require(type(vector) is FrozenVector and len(vector.selected) == 1703 and
            FrozenVector.from_selected(vector.rows(), vector.captured(),
                                       vector.episode_raw, vector.role_raw).sha256 == vector.sha256,
            'frozen two-attempt selection changed')
    attempts = []
    bindings = []
    for number in (1, 2):
        if attempts and attempts[-1]['scratch_cleanup_observed'] is not True:
            outcome = {
                'status': 'SKIPPED-unclean-prior-attempt',
                'input_vector_sha256': vector.sha256,
            }
            safe = _safe_attempt(number, outcome, vector)
            attempts.append(safe)
            if publish_attempt is not None:
                bindings.append(publish_attempt(number, safe))
            break
        outcome = diagnose(vector, deadline)
        try:
            safe = _safe_attempt(number, outcome, vector)
        except Exception:
            safe = {
                'attempt': number, 'status': 'FAIL-attempt-result-schema',
                'input_vector_sha256': vector.sha256,
                'failure_code': 'CONTRACT_REFUSAL',
                'scratch_cleanup_observed': None,
                'raw_stdout_stderr_or_exception_published': False,
                'actual_host_qualification': False, 'activation_allowed': False,
            }
        attempts.append(safe)
        if publish_attempt is not None:
            bindings.append(publish_attempt(number, safe))
    consistent = _selection_equal(attempts)
    status = ('PASS-two-disposable-attempts' if consistent is True else
              'INCOMPLETE-or-mixed-disposable-attempts')
    return {
        'schema_version': 'lab-T35-frozen-vector-pair-diagnostic/v1-inactive',
        'status': status,
        'input_vector_sha256': vector.sha256,
        'selected_repository_input_count': len(vector.selected),
        'episode_sha256': source._sha(vector.episode_raw),
        'role_sha256': source._sha(vector.role_raw),
        'same_captured_input_vector': True,
        'derived_selection_equal_when_both_observed': consistent,
        'attempts': attempts,
        'attempt_receipt_bindings': bindings,
        'attempt_limit': 2,
        'effect_capture_watchdog_seconds': PAIR_WALL_SECONDS,
        'receipt_io_excluded_from_watchdog': True,
        'full_execution_inputs_identical': False,
        'historical_contract_error_explained': False,
        'fresh_fixture_signer_per_attempt': True,
        'previous_unexplained_refusal_retained': True,
        'actual_host_qualification': False,
        'activation_allowed': False,
    }


def _publish_attempt(number: int, safe: dict) -> dict:
    require(number in (1, 2) and safe['attempt'] == number,
            'numbered sanitized attempt required')
    payload = {
        'schema_version': 'lab-T35-phase-prefix-pair-attempt/v1-inactive',
        'selected_application_inputs_only': True,
        'full_execution_inputs_identical': False,
        'historical_contract_error_explained': False,
        'effect_capture_watchdog_seconds': PAIR_WALL_SECONDS,
        'receipt_io_excluded_from_watchdog': True,
        'attempt': safe,
    }
    return evidence_guard.publish_numbered(ATTEMPT_NAMES[number - 1], _json(payload))


def _preflight_evidence_names() -> None:
    require(all(not os.path.lexists(evidence_guard.EVIDENCE / name)
                for name in (*ATTEMPT_NAMES, SUMMARY_NAME)),
            'numbered pair evidence already exists')


def run_pair(*, publish: bool = False) -> dict:
    began = time.monotonic()
    if publish:
        _preflight_evidence_names()
    published_bindings: list[dict] = []
    def publish_one(number: int, safe: dict) -> dict:
        with _receipt_write_window():
            binding = _publish_attempt(number, safe)
            published_bindings.append(binding)
        return binding
    try:
        with _wall_watchdog() as deadline:
            rows, captured = source._source_rows()
            episode = _fixture_episode(captured)
            role = b'{"schema_version":"lab-T35-disposable-native-role/v1","authority_effect":"none"}\n'
            vector = FrozenVector.from_selected(rows, captured, episode, role)
            window = _episode_window(vector)
            result = pair(vector, deadline=deadline,
                          publish_attempt=publish_one if publish else None)
            result['episode_window_preflight'] = window
    except Exception as error:
        code = 'CONTRACT_REFUSAL' if isinstance(error, ContractError) else 'UNEXPECTED_EXCEPTION'
        result = {
            'schema_version': 'lab-T35-frozen-vector-pair-diagnostic/v1-inactive',
            'status': 'FAIL-pair-controller',
            'failure_code': code,
            'attempt_receipt_bindings': published_bindings,
            'attempt_limit': 2,
            'effect_capture_watchdog_seconds': PAIR_WALL_SECONDS,
            'receipt_io_excluded_from_watchdog': True,
            'raw_stdout_stderr_or_exception_published': False,
            'actual_host_qualification': False,
            'activation_allowed': False,
        }
    result['observed_elapsed_wall_seconds'] = round(time.monotonic() - began, 6)
    if publish:
        result['pair_summary_binding'] = None
        with _receipt_write_window():
            binding = evidence_guard.publish_numbered(SUMMARY_NAME, _json(result))
        result['pair_summary_binding'] = binding
    return result


if __name__ == '__main__':
    import sys
    try:
        result = run_pair(publish=True)
    except Exception:
        result = {'status': 'FAIL-disposable-prefix-pair',
                  'failure_stage': 'preflight',
                  'failure_code': 'UNEXPECTED_EXCEPTION',
                  'attempts': [], 'attempt_limit': 2,
                  'raw_stdout_stderr_or_exception_published': False,
                  'actual_host_qualification': False,
                  'activation_allowed': False}
    print(json.dumps(result, sort_keys=True, indent=2))
    if result['status'] != 'PASS-two-disposable-attempts':
        sys.exit(1)
