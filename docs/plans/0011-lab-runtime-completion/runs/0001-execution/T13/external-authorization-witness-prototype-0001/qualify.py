"""Pure retained-fixture qualification; full selected public bytes, no native calls."""
import argparse
import base64
import datetime
import hashlib
import json
import os
import stat
import sys
import types
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).absolute().parent
INSTALL = ROOT / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
DEPS = 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
DEPS_SHA = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'

def capture(path, pin, size=None, mode=None):
    absolute = Path(path)
    assert absolute.is_absolute() and '..' not in absolute.parts
    held = []; fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW); held.append(fd)
    try:
        for name in absolute.parts[1:-1]:
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            held.append(child); fd = child
        leaf = os.open(absolute.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd); held.append(leaf)
        before = os.fstat(leaf); assert stat.S_ISREG(before.st_mode)
        chunks = []
        while True:
            chunk = os.read(leaf, 1024 * 1024)
            if not chunk: break
            chunks.append(chunk)
        raw = b''.join(chunks)
        after = os.fstat(leaf)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_gid, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        assert identity(after) == identity(before) and hashlib.sha256(raw).hexdigest() == pin
        assert size is None or len(raw) == size
        assert mode is None or stat.S_IMODE(before.st_mode) == mode
        for index, name in enumerate(absolute.parts[1:]):
            named = os.stat(name, dir_fd=held[index], follow_symlinks=False)
            current = os.fstat(held[index + 1])
            assert (named.st_dev, named.st_ino, named.st_mode) == (current.st_dev, current.st_ino, current.st_mode)
        return raw, {'path': str(absolute.relative_to(ROOT)), 'sha256': pin, 'size_bytes': len(raw),
            'mode': stat.S_IMODE(before.st_mode), 'device': before.st_dev, 'inode': before.st_ino}
    finally:
        for descriptor in reversed(held): os.close(descriptor)

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--output-name', required=True); args = parser.parse_args()
    assert Path(sys.executable) == INSTALL / 'bin/python'
    assert args.output_name in {'QUALIFICATION.json'}
    fd_start = len(os.listdir('/proc/self/fd'))
    manifest_raw, _ = capture(HERE / 'source-manifest.json', args.manifest_sha256)
    manifest = json.loads(manifest_raw); selected = manifest['files']; bodies = {}; entry = []
    for row in selected:
        raw, record = capture(ROOT / row['path'], row['sha256'], row['size_bytes'])
        bodies[row['path']] = raw; entry.append(record)
    dependency_raw, _ = capture(ROOT / DEPS, DEPS_SHA)
    dependency = json.loads(dependency_raw); installed = []
    for row in dependency['inputs']:
        mode = 0o755 if row['kind'] in {'interpreter', 'native-executable'} or row['destination'] == 'lib/abi/ld-linux-x86-64.so.2' else 0o644
        installed.append({'path': str((INSTALL / row['destination']).relative_to(ROOT)), 'sha256': row['sha256'],
            'size_bytes': row['size_bytes'], 'mode': mode})
    for name, row in dependency['wheel_members'].items():
        installed.append({'path': str((INSTALL / name).relative_to(ROOT)), **row})
    assert len(installed) == 1010 and len({r['path'] for r in installed}) == 1010
    installed_entry = [capture(ROOT / r['path'], r['sha256'], r['size_bytes'], r['mode'])[1] for r in installed]
    sys.path.insert(0, str(INSTALL / 'deps'))
    own = str(HERE.relative_to(ROOT)) + '/'; code = bodies[own + 'witness.py']
    module = types.ModuleType('_cal_T13_retained_external_witness_fixture')
    module.__file__ = str(HERE / 'witness.py')
    exec(compile(code, module.__file__, 'exec', dont_inherit=True), module.__dict__)
    packet = json.loads(bodies[own + 'FIXTURE-PUBLIC-INPUTS.json'])
    assert packet['fixture_only'] is True and packet['private_keys_exported'] is False
    decode = lambda value: base64.b64decode(value, validate=True)
    context_raw = decode(packet['context_raw_base64']); context = module.parse(context_raw)
    plan_raw = decode(packet['plan_raw_base64']); plan = module.parse(plan_raw)
    response_raw = decode(packet['response_raw_base64']); response = module.parse(response_raw)
    at = module.instant(response['payload']['issued_at'])
    artifacts = {name: decode(raw) for name, raw in packet['public_artifacts'].items()}
    for binding_name, source_name in [('materializer_binding', 'materializer'), ('schema_binding', 'native'), ('decision_schema_binding', 'Decision_schema')]:
        selected_ref = packet['public_code_source_refs'][source_name]
        held = bodies[selected_ref['path']]
        assert module.sha(held) == selected_ref['sha256'] == context[binding_name]['sha256']
        artifacts[context[binding_name]['path']] = held
    schema_raw = bodies[own + 'protocol.schema.json']; schema_pin = module.sha(schema_raw)
    heads = [t['expected_head'] for t in plan['targets']]
    prepared = module.prepare(context_raw, module.sha(context_raw), plan_raw, module.sha(plan_raw), artifacts,
        schema_raw, schema_pin, heads, at)
    witness_raw = decode(packet['witness_raw_base64']); decision_raw = decode(packet['Decision_raw_base64'])
    decision_schema = artifacts[context['decision_schema_binding']['path']]
    result = module.verify_witness(witness_raw, module.sha(witness_raw), prepared, response_raw, decision_raw,
        decision_schema, context['decision_schema_binding']['sha256'], heads, at)
    inherited = module.inherited_originals(bodies['docs/plans/0011-lab-runtime-completion/runs/0001-execution/T13/native-event-closure-preparation-0001/ACCOUNTING-88.json'],
        'c783761f5180365cbec59ef8ab654cb3d9bb3376e408eee37f06216ccaf46f1d')
    assert result['technical_fixture_witness_verified'] is True and result['actual_adoption_authorized'] is False
    assert len(prepared['events']) == len(prepared['cores']) == inherited['original_intents'] == 88
    assert all(row['native_event_bytes'] is None and row['actual_owner_Decision_binding'] is None for row in inherited['unchanged_blockers'])
    exit_rows = [capture(ROOT / r['path'], r['sha256'], r['size_bytes'])[1] for r in selected]
    installed_exit = [capture(ROOT / r['path'], r['sha256'], r['size_bytes'], r['mode'])[1] for r in installed]
    assert entry == exit_rows and installed_entry == installed_exit
    capture(HERE / 'source-manifest.json', args.manifest_sha256)
    assert len(os.listdir('/proc/self/fd')) == fd_start
    report = {'schema_version': 'lab-T13-retained-fixture-qualification/v1-candidate', 'result': 'PASS',
        'source_manifest_sha256': args.manifest_sha256, 'source_entry': entry, 'source_exit': exit_rows,
        'installed_entry': installed_entry, 'installed_exit': installed_exit, 'FD_delta': 0,
        'fixture_time_evaluated': response['payload']['issued_at'], 'real_current_authority_evaluated': False,
        'guarded_fixture_targets': 88, 'original_targets_materialized': 0, 'original_intents_blocked': 88,
        'native_or_Lab_or_lease_calls': False, 'private_original_archive_or_keys_read': False,
        'authority_effect': 'none', 'task_complete': False}
    with (HERE / args.output_name).open('x') as stream: stream.write(json.dumps(report, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in {'source_entry', 'source_exit', 'installed_entry', 'installed_exit'}}))

if __name__ == '__main__': main()
