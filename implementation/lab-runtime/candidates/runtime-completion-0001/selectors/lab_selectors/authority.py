"""Bounded coordinator transport to an independently selected authority adapter.

No provider is imported into the runner or privileged broker. The adapter runs
under the coordinator's existing UID. Its reviewed implementation authenticates
enrollment and current permissions, dispatches through the fixed broker, rechecks
each effect and returns sanitized original evidence. No default actual provider.
"""
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time
from lab_contracts.codec import Refusal, canonical, closed, need, parse, sha
from lab_contracts.validation import validate


def bounded_transport(argv, environment, cwd, request_bytes, timeout_ms, max_output_bytes, on_dispatch=None):
    """Hard aggregate retained-output cap; bounded stdin/write/read/deadline."""
    need(type(request_bytes) is bytes and len(request_bytes) <= 65536, 'PROVIDER_REQUEST_LIMIT')
    need(type(timeout_ms) is int and 0 < timeout_ms <= 3600000, 'PROVIDER_TIMEOUT_LIMIT')
    need(type(max_output_bytes) is int and 0 < max_output_bytes <= 65536, 'PROVIDER_OUTPUT_LIMIT')
    need(Path(argv[0]).is_absolute(), 'PROVIDER_EXECUTABLE')
    proc = subprocess.Popen(argv, cwd=cwd, env=environment, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            close_fds=True, start_new_session=True)
    if on_dispatch is not None:
        on_dispatch()
    deadline = time.monotonic_ns() + timeout_ms * 1000000
    output = [bytearray(), bytearray()]
    offset = 0
    try:
        with selectors.DefaultSelector() as streams:
            for stream in (proc.stdin, proc.stdout, proc.stderr):
                os.set_blocking(stream.fileno(), False)
            streams.register(proc.stdin, selectors.EVENT_WRITE, 'input')
            streams.register(proc.stdout, selectors.EVENT_READ, 0)
            streams.register(proc.stderr, selectors.EVENT_READ, 1)
            while streams.get_map():
                need(time.monotonic_ns() < deadline, 'PROVIDER_TIMEOUT_UNKNOWN')
                for key, _ in streams.select(min(0.05, max(0, (deadline-time.monotonic_ns())/1e9))):
                    if key.data == 'input':
                        try:
                            offset += os.write(proc.stdin.fileno(), request_bytes[offset:offset+4096])
                        except BrokenPipeError:
                            raise Refusal('PROVIDER_INPUT_REFUSED') from None
                        if offset == len(request_bytes):
                            streams.unregister(proc.stdin)
                            proc.stdin.close()
                    else:
                        remaining = max_output_bytes - sum(map(len, output))
                        chunk = os.read(key.fileobj.fileno(), min(4096, remaining+1))
                        if not chunk:
                            streams.unregister(key.fileobj)
                        else:
                            need(len(chunk) <= remaining, 'PROVIDER_OUTPUT_LIMIT_UNKNOWN')
                            output[key.data].extend(chunk)
        proc.wait(timeout=max(0.001, (deadline-time.monotonic_ns())/1e9))
        need(proc.returncode == 0, 'PROVIDER_NONZERO_UNKNOWN')
        try:
            os.killpg(proc.pid, 0)
        except ProcessLookupError:
            pass
        else:
            raise Refusal('PROVIDER_DESCENDANT_UNKNOWN')
        return bytes(output[0])
    except subprocess.TimeoutExpired:
        raise Refusal('PROVIDER_TIMEOUT_UNKNOWN') from None
    finally:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait(timeout=5)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            stream.close()


class BoundedProvider:
    def __init__(self, endorsement, reader, launch):
        self.endorsement, self.reader, self.launch = endorsement, reader, launch

    def execute(self, request, command, on_dispatch):
        e = self.endorsement
        for binding in e['source_bindings']:
            self.reader.read(binding)
        self.reader.read(e['issuer_enrollment_binding'])
        envelope = {'schema_version': 'lab-actual-authority-provider-request/v1',
            'issuer_enrollment_binding': e['issuer_enrollment_binding'],
            'provider_binding': e['provider_binding'], 'request': request, 'command': command}
        env = {r['name']: r['value'] for r in self.launch['environment']}
        need(len(env) == len(self.launch['environment']), 'PROVIDER_DUPLICATE_ENV')
        return bounded_transport(self.launch['argv'], env,
            str(Path(e['repository']) / self.launch['cwd']), canonical(envelope),
            min(command['timeout_ms'], self.launch['timeout_ms']),
            min(command['max_output_bytes'], self.launch['max_output_bytes'], 65536), on_dispatch)

    def close(self):
        # All transport children/FDs are reaped/closed per call. Store/effect
        # cleanup remains original typed evidence, never inferred from reaping.
        return b'{"schema_version":"lab-provider-cleanup/v1","result":"clean"}'


def load_provider(endorsement, reader):
    need(endorsement['stage'] == 'actual' and endorsement['provider_kind'] == 'actual',
         'ACTUAL_PROVIDER_REQUIRED')
    binding = endorsement['provider_binding']
    need(binding is not None and binding in endorsement['source_bindings'], 'PROVIDER_NOT_REVIEWED')
    need(endorsement['issuer_enrollment_binding'] is not None, 'ISSUER_ENROLLMENT_REQUIRED')
    launches = [c for c in endorsement['commands'] if c['id'] == endorsement['provider_command_id']]
    need(len(launches) == 1 and binding in launches[0]['program_bindings'], 'PROVIDER_LAUNCH')
    for selected in launches[0]['program_bindings']:
        need(selected in endorsement['source_bindings'], 'PROVIDER_SOURCE_CLOSURE')
        reader.read(selected)
    reader.read(endorsement['issuer_enrollment_binding'])
    return BoundedProvider(endorsement, reader, launches[0])


def authorized_execute(provider, request, command, endorsement, on_dispatch, retain_original=None):
    from .effect_evidence import validate_and_retain, EffectEvidenceRefusal
    need(type(provider) is BoundedProvider, 'ACTUAL_PROVIDER_REQUIRED')
    raw = provider.execute(request, command, on_dispatch)
    reply = parse(raw)
    closed(reply, ('schema_version', 'gate_verification', 'command_result', 'effect_evidence'))
    need(reply['schema_version'] == 'lab-actual-authority-provider-result/v1', 'PROVIDER_REPLY_VERSION')
    result = validate('CommandResult', reply['command_result'])
    try:
        proof = validate('GateVerification', reply['gate_verification'])
        detail = validate_and_retain(reply['effect_evidence'], proof, result, request, command,
                                     endorsement, retain_original)
    except EffectEvidenceRefusal:
        raise
    except Exception as exc:
        raise EffectEvidenceRefusal(str(exc) if isinstance(exc, Refusal) else 'RECEIPT_VALIDATION_UNKNOWN',
                                    'unknown') from None
    result = {**result, 'result': detail['evidence_result'],
              'effect_state': detail['verified_effect_state'], 'cleanup': detail['verified_cleanup']}
    return result, {'request_sha256': proof['request_sha256'], 'reply_sha256': sha(raw), **detail}
