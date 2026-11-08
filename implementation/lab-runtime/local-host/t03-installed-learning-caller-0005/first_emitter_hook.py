"""Emit exact native first Session bodies privately before Session close."""
from datetime import timedelta
import importlib.util
from pathlib import Path
import stat
import sys


def emit(runtime, host, selected, opened, resource, code_path, code_sha256):
    common_path = Path(__file__).with_name('runtime_common.py')
    spec = importlib.util.spec_from_file_location('_t03_first_emitter_common', common_path)
    C = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = C
    spec.loader.exec_module(C)
    P, A = runtime.P, runtime.A
    code = Path(code_path)
    C.need(code.is_absolute() and code.is_file() and not code.is_symlink()
           and C.sha(code.read_bytes()) == code_sha256,
           'selected native first-emitter adapter bytes differ')
    module = C.load_file(code)
    output = runtime.evidence / 'native-first-emission'
    C.need(not output.exists(), 'first emission output root already exists')
    output.mkdir(mode=0o700)
    now = A.now()
    expiry = min(resource.expires, now + timedelta(minutes=20))
    C.need(now < expiry, 'live first Session lacks emission time')
    grant = {'schema_version': 'lab-private-native-first-emitter-grant/v1-fixture',
             'principal_ref': host.channel.context['principal_ref'],
             'scope_ref': selected.sources.scope_ref,
             'source_cut': selected.source_cut,
             'session_ref': opened['session_ref'],
             'opening_result_sha256': C.sha(P.compact(opened)),
             'producer_policy_sha256': host.channel.expected_sha,
             'output_root': str(output),
             'not_before': (now - timedelta(seconds=1)).isoformat(),
             'expires_at': expiry.isoformat(),
             'revoked': False,
             'permitted_effects': ['emit-formal-lifecycle-output'],
             'authority_effect': 'none',
             'actual_owner_outcome': None}
    grant_binding = C.write(runtime.evidence / 'native-first-emitter-grant.json', grant)
    emitter = module.NativeFirstEmitter(
        api_directory=runtime.api,
        source_sha256=runtime.api_binding['sha256'],
        profile_sha256=runtime.profile_binding['sha256'],
        control_path=grant_binding['path'],
        control_sha256=grant_binding['sha256'],
        adapter_sha256=code_sha256)
    emitted = emitter.emit(host, opened)
    C.need(emitted['posture'] == 'produced-uncommitted'
           and emitted['output_root'] == str(output)
           and len(emitted['receipt']['outputs']) == 3
           and emitted['receipt']['actual_RAM_memory_accessed'] is False,
           'exact three private native formal outputs absent')
    receipt_path = output / 'emission.json'
    C.need(receipt_path.is_file() and not receipt_path.is_symlink()
           and stat.S_IMODE(receipt_path.stat().st_mode) == 0o600
           and C.sha(receipt_path.read_bytes()) == emitted['receipt_sha256'],
           'private first-emitter original receipt differs')
    C.need(C.sha(code.read_bytes()) == code_sha256,
           'first-emitter adapter changed during live use')
    result = {'posture': 'produced-uncommitted',
              'output_root': str(output),
              'receipt_path': str(receipt_path),
              'receipt_sha256': emitted['receipt_sha256'],
              'formal_output_count': 3,
              'adapter_sha256': code_sha256,
              'grant_sha256': grant_binding['sha256'],
              'actual_RAM_memory_accessed': False,
              'authority_effect': 'none'}
    C.write(runtime.evidence / 'FIRST-EMISSION.json', result)
    return result
