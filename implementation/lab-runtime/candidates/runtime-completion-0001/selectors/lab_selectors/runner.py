"""Immutable selected-case execution. Local execution is inert authoring only."""
import argparse
import json
import os
from pathlib import Path
import signal
import selectors
import stat
import subprocess
import time
from lab_contracts.codec import Refusal, canonical, need, parse, sha
from lab_contracts.validation import validate
from .anchors import relative
from .dispatch import verify_endorsement, prepare
from .authority import authorized_execute, load_provider


def exclusive(parent, name, value):
    need('/' not in name and name not in ('.', '..'), 'EVIDENCE_NAME')
    raw = canonical(value) + b'\n'
    exclusive_bytes(parent, name, raw)


def exclusive_bytes(parent, name, raw):
    need('/' not in name and name not in ('.', '..'), 'EVIDENCE_NAME')
    need(type(raw) is bytes and len(raw) <= 64 * 1024 * 1024, 'EVIDENCE_BYTES')
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o600, dir_fd=parent)
    try:
        offset = 0
        while offset < len(raw):
            offset += os.write(fd, raw[offset:])
        os.fsync(fd)
    finally:
        os.close(fd)
    os.fsync(parent)


def read_dispatch(path, expected):
    need(Path(path).is_absolute(), 'ENDORSEMENT_ABSOLUTE_PATH')
    parts = relative(path[1:])
    fds = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)]
    fd = None
    try:
        for name in parts[:-1]:
            fds.append(os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                               dir_fd=fds[-1]))
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                     dir_fd=fds[-1])
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size <= 64 * 1024 * 1024, 'ENDORSEMENT_TYPE_SIZE')
        pieces = []
        size = 0
        while chunk := os.read(fd, 1024 * 1024):
            size += len(chunk)
            need(size <= 64 * 1024 * 1024, 'ENDORSEMENT_LIMIT')
            pieces.append(chunk)
        raw = b''.join(pieces)
        need(sha(raw) == expected, 'DISPATCH_ANCHOR_MISMATCH')
        return raw
    except OSError:
        raise Refusal('ENDORSEMENT_UNREADABLE') from None
    finally:
        if fd is not None:
            os.close(fd)
        for directory in reversed(fds):
            os.close(directory)


def reserve_run(endorsement, reader):
    root = reader.roots.get('repository')
    need(root is not None and root.path == endorsement['repository'], 'REPOSITORY_ANCHOR')
    handles, _ = root.open()
    try:
        parts = relative(endorsement['run_root'])
        for name in parts[:-1]:
            handles.append(os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                   dir_fd=handles[-1]))
        os.mkdir(parts[-1], mode=0o700, dir_fd=handles[-1])
        os.fsync(handles[-1])
        fd = os.open(parts[-1], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=handles[-1])
        return fd
    except OSError:
        raise Refusal('RUN_ROOT_NOT_EXCLUSIVE') from None
    finally:
        for fd in reversed(handles):
            os.close(fd)


def local_command(command, endorsement, run_fd, serial):
    """Bound output/time and kill/reap our own process group on interruption.

This is not hostile same-UID confinement. Independently reviewed inert tests
must stay in the declared owned authoring envelope. Actual stages use provider.
"""
    argv = command['argv']
    need(Path(argv[0]).is_absolute(), 'EXECUTABLE_ABSOLUTE_PATH')
    env = {v['name']: v['value'] for v in command['environment']}
    need(len(env) == len(command['environment']), 'DUPLICATE_ENV')
    need(not any(k in env for k in ('PYTHONSTARTUP', 'PYTHONINSPECT', 'LD_PRELOAD', 'LD_AUDIT')),
         'UNSELECTED_INJECTION_ENV')
    cwd = str(Path(endorsement['repository']) / command['cwd'])
    relative(command['cwd'])
    output_fds = []
    proc = None
    limited = False
    reason = None
    started = time.monotonic_ns()
    try:
        for suffix in ('stdout', 'stderr'):
            output_fds.append(os.open(f'command-{serial:04d}.{suffix}',
                os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                0o600, dir_fd=run_fd))
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                close_fds=True, start_new_session=True)
        deadline = started + command['timeout_ms'] * 1000000
        retained = 0
        with selectors.DefaultSelector() as streams:
            for stream, destination in zip((proc.stdout, proc.stderr), output_fds):
                os.set_blocking(stream.fileno(), False)
                streams.register(stream, selectors.EVENT_READ, destination)
            while streams.get_map():
                if time.monotonic_ns() >= deadline:
                    limited, reason = True, 'TIMEOUT'
                    break
                for key, _ in streams.select(timeout=min(0.05, max(0, (deadline-time.monotonic_ns())/1e9))):
                    chunk = os.read(key.fileobj.fileno(), min(65536, command['max_output_bytes']-retained+1))
                    if not chunk:
                        streams.unregister(key.fileobj)
                        continue
                    remaining = command['max_output_bytes'] - retained
                    kept = chunk[:remaining]
                    offset = 0
                    while offset < len(kept):
                        offset += os.write(key.data, kept[offset:])
                    retained += len(kept)
                    if len(chunk) > remaining:
                        limited, reason = True, 'OUTPUT_LIMIT'
                        break
                if limited:
                    break
        if limited:
            os.killpg(proc.pid, signal.SIGKILL)
        try:
            proc.wait(timeout=max(0.001, (deadline-time.monotonic_ns())/1e9) if not limited else 5)
        except subprocess.TimeoutExpired:
            limited, reason = True, 'TIMEOUT'
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)
        proc.stdout.close()
        proc.stderr.close()
        # A successful leader may not leave children behind in its group.
        try:
            os.killpg(proc.pid, 0)
        except ProcessLookupError:
            pass
        else:
            os.killpg(proc.pid, signal.SIGKILL)
            limited, reason = True, 'DESCENDANT_RESIDUE'
        outputs = []
        for fd in output_fds:
            os.fsync(fd)
            size = os.fstat(fd).st_size
            need(size <= command['max_output_bytes'], 'OUTPUT_LIMIT')
            os.lseek(fd, 0, os.SEEK_SET)
            outputs.append(os.read(fd, size + 1))
        if limited:
            result = {'schema_version': 'lab-case-command-result/v1', 'result': 'UNKNOWN',
                      'checks': 0, 'effect_state': 'unknown', 'cleanup': 'unknown'}
        elif proc.returncode != 0:
            result = {'schema_version': 'lab-case-command-result/v1', 'result': 'FAIL',
                      'checks': 0, 'effect_state': 'unknown', 'cleanup': 'unknown'}
            reason = 'CHILD_NONZERO'
        else:
            result = validate('CommandResult', parse(outputs[0]))
            need(result['result'] != 'PASS' or result['checks'] > 0, 'EMPTY_PASS')
            need(result['result'] != 'PASS' or (result['cleanup'] != 'unknown'
                 and result['effect_state'] in ('none', 'owned-inert')), 'UNKNOWN_EFFECT_OR_CLEANUP_PASS')
            need(result['effect_state'] in ('none', 'owned-inert'), 'INERT_EFFECT_REPORT')
        return result, {'returncode': proc.returncode, 'elapsed_ns': time.monotonic_ns() - started,
                        'reason': reason, 'retained_output_bytes': retained,
                        'output_truncated': reason == 'OUTPUT_LIMIT',
                        'stdout_sha256': sha(outputs[0]), 'stderr_sha256': sha(outputs[1])}
    except BaseException:
        if proc is not None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait(timeout=5)
            if proc.stdout is not None:
                proc.stdout.close()
            if proc.stderr is not None:
                proc.stderr.close()
        raise
    finally:
        for fd in output_fds:
            os.close(fd)


def run(raw, expected_sha, *, requested_unit, requested_kind, selection_path,
        case_path, run_path, provider_factory=None):
    endorsement, reader = verify_endorsement(raw, expected_sha)
    need(requested_unit == endorsement['unit'] and requested_kind == endorsement['selection_kind'], 'DISPATCH_REQUEST')
    root = Path(endorsement['repository'])
    for actual, key in ((selection_path, 'selection_binding'), (case_path, 'case_manifest_binding')):
        binding = endorsement[key]
        selected_root = reader.roots[binding['root_id']]
        need(Path(actual).absolute() == Path(selected_root.path) / binding['relative_path'], 'CLI_SELECTION_DRIFT')
    need(Path(run_path).absolute() == root / endorsement['run_root'], 'CLI_RUN_ROOT_DRIFT')
    run_fd = reserve_run(endorsement, reader)
    provider = None
    results = []
    status = 'ERROR'
    primary = None
    secondary = []
    cleanup = 'unknown'
    command_count = 0
    fenced = False
    actual_dispatch_count = 0
    actual_effect_state = 'none'
    actual_states = []
    try:
        exclusive(run_fd, 'command.json', {'schema_version': 'lab-dispatch-command/v1',
            'unit': requested_unit, 'selection_kind': requested_kind,
            'selection_path': str(selection_path), 'case_manifest_path': str(case_path),
            'run_root': str(run_path), 'endorsement_sha256': expected_sha,
            'external_anchor_channel': 'LAB_DISPATCH_ENDORSEMENT_SHA256',
            'authority_effect': 'none'})
        exclusive(run_fd, 'prepost-pre.json', {'source_bindings': endorsement['source_bindings'],
            'selection_binding': endorsement['selection_binding'], 'verified': True})
        manifest, commands, cases = prepare(endorsement, reader)
        if manifest['stage'] == 'actual':
            need(provider_factory is None, 'TEST_PROVIDER_CANNOT_ACTIVATE_ACTUAL')
            provider = load_provider(endorsement, reader)
        for expanded in cases:
            case = expanded['case']
            failed = False
            case_results = []
            for phase in ('setup', 'commands', 'cleanup'):
                for step in case[phase]:
                    command = commands[step['command_id']]
                    command_count += 1
                    if (failed or fenced) and phase != 'cleanup':
                        result = {'schema_version': 'lab-case-command-result/v1', 'result': 'NOT_RUN',
                                  'checks': 0, 'effect_state': 'none', 'cleanup': 'unknown'}
                        detail = {'reason': 'PRECEDING_CASE_FAILURE'}
                    else:
                        try:
                            for binding in endorsement['source_bindings']:
                                reader.read(binding)
                            reader.read(endorsement['selection_binding'])
                            request = {'schema_version': 'lab-completion-gate-request/v1',
                                'unit': requested_unit, 'case_id': case['id'], 'phase': phase,
                                'command_id': command['id'], 'command_sha256': sha(canonical(command)),
                                'selection_binding': endorsement['selection_binding'],
                                'required_gates': sorted(set(expanded['required_gates']) | set(command['required_gates'])),
                                'gate_checks': expanded['gate_checks'], 'produced_terminal_checks': command['produced_terminal_checks'],
                                'effects': command['effects'],
                                'gate_input_bindings': endorsement['gate_input_bindings']}
                            if manifest['stage'] == 'actual':
                                def dispatched():
                                    nonlocal actual_dispatch_count, actual_effect_state
                                    actual_dispatch_count += 1
                                    actual_effect_state = 'unknown'
                                    actual_states.append('unknown')
                                def retain_original(number, original):
                                    name = f'command-{command_count:04d}-receipt-{number:02d}.json'
                                    exclusive_bytes(run_fd, name, original)
                                    return {'kind': 'evidence', 'root_id': 'repository',
                                        'relative_path': endorsement['run_root'] + '/' + name,
                                        'sha256': sha(original), 'size_bytes': len(original)}
                                result, detail = authorized_execute(provider, request, command, endorsement,
                                                                    dispatched, retain_original)
                                actual_states[-1] = result['effect_state']
                                actual_effect_state = ('unknown' if 'unknown' in actual_states else
                                                       'observed' if 'observed' in actual_states else 'none')
                                need(result['result'] != 'PASS' or (result['effect_state'] != 'unknown'
                                     and result['cleanup'] != 'unknown'), 'UNKNOWN_EFFECT_OR_CLEANUP_PASS')
                            else:
                                result, detail = local_command(command, endorsement, run_fd, command_count)
                        except Exception as exc:
                            from .effect_evidence import EffectEvidenceRefusal
                            known_effect = exc.effect_state if type(exc) is EffectEvidenceRefusal else 'unknown'
                            if type(exc) is EffectEvidenceRefusal and actual_states:
                                actual_states[-1] = known_effect
                                actual_effect_state = ('unknown' if 'unknown' in actual_states else
                                                       'observed' if 'observed' in actual_states else 'none')
                            result = {'schema_version': 'lab-case-command-result/v1', 'result': 'UNKNOWN',
                                      'checks': 0, 'effect_state': known_effect, 'cleanup': 'unknown'}
                            detail = {**(exc.detail if type(exc) is EffectEvidenceRefusal else {}),
                                      'reason': str(exc) if isinstance(exc, Refusal) else 'COMMAND_EXCEPTION'}
                    failed = failed or result['result'] != 'PASS' or result['cleanup'] == 'unknown'
                    fenced = fenced or result['result'] == 'UNKNOWN' or result['effect_state'] == 'unknown'
                    item = {'case_id': case['id'], 'phase': phase, 'command_id': command['id'],
                            'selected_command': command, 'result': result, 'detail': detail}
                    command_record = f'command-{command_count:04d}.json'
                    exclusive(run_fd, command_record, item)
                    if primary is None and result['result'] != 'PASS':
                        primary = {'command_record': command_record, 'case_id': case['id'],
                                   'phase': phase, 'command_id': command['id'],
                                   'result': result['result'], 'reason': detail.get('reason', result['result'])}
                    case_results.append(item)
            results.extend(case_results)
        expected_terminal = {(g['gate'], requirement) for c in cases for g in c['gate_checks']
                             for requirement in g['terminal_outputs']}
        produced_terminal = [(row['gate'], row['requirement']) for r in results
                             for row in r['detail'].get('terminal_checks', [])]
        if all(r['result']['result'] == 'PASS' for r in results):
            need(len(produced_terminal) == len(set(produced_terminal)) and
                 set(produced_terminal) == expected_terminal, 'AGGREGATE_TERMINAL_COVERAGE')
        status = 'PASS' if results and all(r['result']['result'] == 'PASS' for r in results) else 'FAIL'
        if any(r['result']['result'] == 'UNKNOWN' for r in results):
            status = 'UNKNOWN'
        cleanup_states = [r['result']['cleanup'] for r in results]
        cleanup = ('unknown' if 'unknown' in cleanup_states else
                   'retained-owned' if 'retained-owned' in cleanup_states else 'clean')
        for binding in endorsement['source_bindings']:
            reader.read(binding)
        reader.read(endorsement['selection_binding'])
        exclusive(run_fd, 'prepost-post.json', {'source_bindings': endorsement['source_bindings'],
                                               'verified': True})
    except Exception as exc:
        failure = {'command_record': None, 'reason': str(exc) if isinstance(exc, Refusal) else 'RUNNER_EXCEPTION'}
        if primary is None:
            primary = failure
        else:
            secondary.append(failure)
        status = 'ERROR' if command_count == 0 else 'UNKNOWN'
    finally:
        if provider is not None:
            try:
                close_result = provider.close()
                need(type(close_result) is bytes and parse(close_result) ==
                     {'schema_version': 'lab-provider-cleanup/v1', 'result': 'clean'}, 'PROVIDER_CLEANUP')
            except Exception:
                failure = {'command_record': None, 'reason': 'PROVIDER_CLEANUP'}
                if primary is None:
                    primary = failure
                else:
                    secondary.append(failure)
                status, cleanup = 'UNKNOWN', 'unknown'
        terminal = {'schema_version': 'lab-case-attempt-terminal/v1', 'unit': requested_unit,
                    'result': status, 'primary_failure': primary, 'secondary_failures': secondary, 'command_count': command_count,
                    'cleanup': cleanup, 'endorsement_sha256': expected_sha,
                    'actual_dispatch_count': actual_dispatch_count, 'actual_effect_state': actual_effect_state,
                    'authority_effect': 'none'}
        exclusive(run_fd, 'cleanup.json', {'schema_version': 'lab-case-cleanup/v1',
            'state': cleanup, 'foreign_cleanup': False, 'persistent_evidence_retained': True})
        exclusive(run_fd, 'terminal.json', terminal)
        os.close(run_fd)
    return terminal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--unit', required=True)
    parser.add_argument('--selection-kind', required=True)
    parser.add_argument('--selection', required=True)
    parser.add_argument('--case-manifest', required=True)
    parser.add_argument('--run-root', required=True)
    args = parser.parse_args()
    try:
        path = os.environ.get('LAB_DISPATCH_ENDORSEMENT')
        expected = os.environ.get('LAB_DISPATCH_ENDORSEMENT_SHA256')
        need(type(path) is str and type(expected) is str, 'MISSING_EXTERNAL_DISPATCH_ANCHOR')
        raw = read_dispatch(path, expected)
        result = run(raw, expected, requested_unit=args.unit, requested_kind=args.selection_kind,
                     selection_path=args.selection, case_path=args.case_manifest, run_path=args.run_root)
        print(json.dumps(result, sort_keys=True))
        return 0 if result['result'] == 'PASS' else 1
    except Exception as exc:
        print(json.dumps({'result': 'REFUSED', 'reason': str(exc) if type(exc) is Refusal else 'DISPATCH_EXCEPTION',
                          'authority_effect': 'none'}, sort_keys=True))
        return 1
