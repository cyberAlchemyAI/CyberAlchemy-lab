"""Fixed synthetic child. No Context import, archive, signer, grant or native operation."""
import errno
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
import types

BRIDGE_SHA = '5bf35088d43f781453ee8f4e9397a033bd2acdd671142a5a7c05adad709bb52a'
PHASES = {'bootstrap', 'runtime', 'connect', 'guard', 'go', 'emit', 'readback',
          'deny_output', 'deny_sentinel', 'mountinfo', 'release', 'result',
          'manifest', 'finish_readback', 'summary'}
phase = 'bootstrap'


def diagnostic(error, phase_name):
    kind = type(error)
    classes = ((OSError, 'OS'), (PermissionError, 'PERMISSION'),
               (TimeoutError, 'TIMEOUT'), (BrokenPipeError, 'PIPE'),
               (ConnectionResetError, 'RESET'), (RuntimeError, 'RUNTIME'),
               (ValueError, 'VALUE'))
    label = next((name for cls, name in classes if kind is cls), 'OTHER')
    number = None
    if any(kind is cls for cls in (OSError, PermissionError, TimeoutError,
                                  BrokenPipeError, ConnectionResetError)):
        value = object.__getattribute__(error, 'errno')
        if type(value) is int and value in (errno.EACCES, errno.EROFS, errno.EPIPE,
                                           errno.ETIMEDOUT, errno.ECONNRESET):
            number = value
    return {'schema': 'context-child-diagnostic/v1',
            'phase': phase_name if type(phase_name) is str and phase_name in PHASES else 'bootstrap',
            'class': label, 'errno': number}


def denied_write(path):
    """Open only; never write even if confinement is absent."""
    try:
        fd = os.open(path, os.O_WRONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError as error:
        if error.errno in (errno.EACCES, errno.EROFS):
            return error.errno
        raise
    else:
        os.close(fd)
        raise RuntimeError('WRITE_OPEN_ALLOWED')


def mount_observation(raw, selected_path):
    if type(raw) is not bytes or not 0 < len(raw) <= 1024 * 1024:
        raise RuntimeError('MOUNTINFO_BOUND')
    matched = []
    for row in raw.splitlines():
        if len(row) > 8192:
            raise RuntimeError('MOUNTINFO_ROW_BOUND')
        fields = row.split()
        if len(fields) < 10 or len(fields) > 128 or b'-' not in fields:
            raise RuntimeError('MOUNTINFO_SHAPE')
        if fields[4] == os.fsencode(selected_path):
            matched.append(row)
            options = fields[5].split(b',')
            if b'ro' not in options or b'rw' in options:
                raise RuntimeError('MOUNT_NOT_READONLY')
    if len(matched) != 1:
        raise RuntimeError('MOUNT_IDENTITY')
    return {'selected_path': str(selected_path), 'selected_line': matched[0].decode('ascii'),
            'mountinfo_sha256': hashlib.sha256(raw).hexdigest(), 'mountinfo_size': len(raw)}


def main(config):
    global phase
    phase = 'runtime'
    if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode and
            type(sys.pycache_prefix) is str and Path(sys.pycache_prefix).is_file()):
        raise RuntimeError('CHILD_COLD_RUNTIME')
    bridge_path = Path(config['bridge'])
    raw = bridge_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BRIDGE_SHA:
        raise RuntimeError('BRIDGE_DRIFT')
    B = types.ModuleType('_selected_context_bridge')
    B.__file__ = str(bridge_path)
    exec(compile(raw, str(bridge_path), 'exec'), B.__dict__)
    if config['fault'] == 'crash':
        os._exit(23)
    if config['fault'] == 'timeout':
        time.sleep(60)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    phase = 'connect'
    sock.settimeout(max(0.001, config['deadline'] - time.monotonic()))
    sock.connect(config['socket'])
    peer = tuple(config['parent_peer'])
    B.configure(sock)
    out = Path(config['out'])
    phase = 'guard'
    guard = Path(__file__).with_name('output_guard.py').read_bytes()
    B.need(B.sha(guard) == config['guard_sha256'], 'ORIGINAL_GUARD_PREIMAGE')
    # Exact selected original build expression. No source verification/body is run.
    exec(compile(guard, 'selected-original-output-guard', 'exec'), {'out': out, 'require': B.need})
    ready = {'schema': 'context-child-ready/v1', 'attempt': config['token'],
             'out': str(out), 'original_guard_sha256': B.sha(guard), 'output_absent': True}
    B.send(sock, B.encode(ready), config['deadline'])
    phase = 'go'
    B.need(B.receive(sock, peer, config['deadline']) ==
           B.encode({'schema': 'context-child-go/v1', 'ready_sha256': B.sha(B.encode(ready))}),
           'GO_BINDING')
    # Docker translates an ancestor PID outside the child PID namespace to zero.
    # This is a selected coordinate, never an assertion of host process identity.
    if config['docker']:
        B.need(peer == (0, os.getuid(), os.getgid()), 'CHILD_PARENT_COORDINATE')
        client = B.Client.__new__(B.Client)
        B.configure(sock)
        client.sock, client.peer, client.token = sock, peer, config['token']
        client.out, client.source = Path(config['out']), config['source']
        client.deadline, client.seq, client.rows = config['deadline'], 0, []
        client.state, client.released, client.closed, client.trace = 'OPEN', False, False, []
    else:
        client = B.Client(sock, peer, config['token'], config['out'],
                          config['source'], config['deadline'])
    if config['fault'] == 'wrong_token':
        client.token = '0' * 32
    out = client.out
    observed = []
    readonly = []
    ro_mount = None
    sentinel = None
    for index, leaf in enumerate(B.LEAVES[:38]):
        phase = 'emit'
        payload = B.encode({'synthetic_public_fixture': True, 'ordinal': index + 1})
        client.emit(out / leaf, payload)
        phase = 'readback'
        B.need((out / leaf).read_bytes() == payload, 'POST_ACK_READBACK')
        observed.append(leaf)
        if config['docker'] and index == 0:
            phase = 'deny_output'
            readonly.append(denied_write(out / leaf))
            # Unlike a 0444 output leaf, this selected sentinel is writable by
            # this same UID on the host. EROFS is a discriminating mount check.
            path = Path(config['sentinel']['path'])
            info = path.stat(follow_symlinks=False)
            identity = [info.st_dev, info.st_ino, info.st_uid, info.st_gid,
                        info.st_mode & 0o777, info.st_size]
            B.need(identity == config['sentinel']['identity'] and
                   B.sha(path.read_bytes()) == config['sentinel']['sha256'] and
                   identity[2:5] == [os.getuid(), os.getgid(), 0o644], 'SENTINEL_IDENTITY')
            phase = 'deny_sentinel'
            number = denied_write(path)
            B.need(number == errno.EROFS, 'SENTINEL_NOT_EROFS')
            readonly.append(number)
            phase = 'mountinfo'
            with open('/proc/self/mountinfo', 'rb') as stream:
                mountinfo = stream.read(1024 * 1024 + 1)
            ro_mount = mount_observation(mountinfo, config['public_root'])
            sentinel = dict(config['sentinel'])
    phase = 'release'
    client.release_private()
    phase = 'result'
    result = B.encode({'synthetic_public_fixture': True, 'private_empty_fixture_removed': True})
    client.emit(out / B.LEAVES[38], result)
    observed.append(B.LEAVES[38])
    binding = lambda p: {'path': str(p), 'sha256': B.sha(p.read_bytes())}
    manifest = {
        'schema_version': 'lab-actual-context-delivery-package/v1-candidate',
        'files': [binding(out / name) for name in sorted(B.LEAVES[:39])],
        'source_manifest_binding': config['source'], 'authority_effect': 'none',
        'actual_owner_outcome': None, 'delivery_binding': binding(out / 'delivery.json'),
        'provenance_binding': binding(out / 'delivery-provenance.json'),
        'claim_ceiling': B.CLAIM,
    }
    phase = 'manifest'
    client.emit(out / 'manifest.json', B.encode(manifest))
    observed.append('manifest.json')
    B.need(client.closed and client.state == 'SUMMARY_PERMITTED', 'CHILD_CLOSE')
    phase = 'finish_readback'
    B.need(B.sha((out / 'manifest.json').read_bytes()) == B.sha(B.encode(manifest)),
           'FINISH_POST_ACK_READ')
    summary = {'result': 'PASS', 'package_binding': binding(out / 'manifest.json'),
               'generated_carriers': 30, 'posture': 'ready', 'public_API_operations_added': 0}
    report = {'schema': 'context-synthetic-child/v1', 'summary': summary,
              'pid': os.getpid(), 'uid': os.getuid(), 'gid': os.getgid(),
              'closed': client.closed, 'state': client.state, 'read_leaves': observed,
              'readonly_errno': readonly, 'parent_peer': list(peer),
              'readonly_mount': ro_mount, 'sentinel': sentinel,
              'original_output_guard': ready,
              'runtime': {'version': list(sys.version_info[:3]), 'isolated': sys.flags.isolated,
                          'no_site': sys.flags.no_site, 'bytecode_disabled': sys.dont_write_bytecode,
                          'cache_prefix_regular_file': True}}
    if config['fault'] == 'bad_summary':
        report['summary']['generated_carriers'] = 31
    phase = 'summary'
    print(json.dumps(report, sort_keys=True), flush=True)
    if config['fault'] == 'exit_after_summary':
        os._exit(19)
    if config['fault'] == 'stdout_overflow':
        print('x' * 40000, flush=True)


if __name__ == '__main__':
    try:
        main(json.loads(sys.argv[1]))
    except BaseException as error:
        sys.stderr.write(json.dumps(diagnostic(error, phase), sort_keys=True) + '\n')
        raise SystemExit(1)
