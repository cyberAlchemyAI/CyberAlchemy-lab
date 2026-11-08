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


def main(config):
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
    sock.settimeout(max(0.001, config['deadline'] - time.monotonic()))
    sock.connect(config['socket'])
    peer = tuple(config['parent_peer'])
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
    for index, leaf in enumerate(B.LEAVES[:38]):
        payload = B.encode({'synthetic_public_fixture': True, 'ordinal': index + 1})
        client.emit(out / leaf, payload)
        B.need((out / leaf).read_bytes() == payload, 'POST_ACK_READBACK')
        observed.append(leaf)
        if config['docker'] and index == 0:
            for target in (out / leaf, out / 'unmediated.json'):
                try:
                    fd = os.open(target, os.O_WRONLY | os.O_CREAT, 0o600)
                except OSError as error:
                    B.need(error.errno == errno.EROFS, 'RO_BIND_NOT_EROFS')
                    readonly.append(error.errno)
                else:
                    os.close(fd)
                    raise RuntimeError('DIRECT_WRITE_ALLOWED')
    client.release_private()
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
    client.emit(out / 'manifest.json', B.encode(manifest))
    observed.append('manifest.json')
    B.need(client.closed and client.state == 'SUMMARY_PERMITTED', 'CHILD_CLOSE')
    B.need(B.sha((out / 'manifest.json').read_bytes()) == B.sha(B.encode(manifest)),
           'FINISH_POST_ACK_READ')
    summary = {'result': 'PASS', 'package_binding': binding(out / 'manifest.json'),
               'generated_carriers': 30, 'posture': 'ready', 'public_API_operations_added': 0}
    report = {'schema': 'context-synthetic-child/v1', 'summary': summary,
              'pid': os.getpid(), 'uid': os.getuid(), 'gid': os.getgid(),
              'closed': client.closed, 'state': client.state, 'read_leaves': observed,
              'readonly_errno': readonly, 'parent_peer': list(peer),
              'runtime': {'version': list(sys.version_info[:3]), 'isolated': sys.flags.isolated,
                          'no_site': sys.flags.no_site, 'bytecode_disabled': sys.dont_write_bytecode,
                          'cache_prefix_regular_file': True}}
    if config['fault'] == 'bad_summary':
        report['summary']['generated_carriers'] = 31
    print(json.dumps(report, sort_keys=True), flush=True)
    if config['fault'] == 'exit_after_summary':
        os._exit(19)
    if config['fault'] == 'stdout_overflow':
        print('x' * 40000, flush=True)


if __name__ == '__main__':
    try:
        main(json.loads(sys.argv[1]))
    except BaseException:
        sys.stderr.write('SYNTHETIC_CHILD_UNKNOWN\n')
        raise SystemExit(1)
