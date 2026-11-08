"""Fixed synthetic original-AST child; never imports original Context roles."""
import ast
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
import types


def selected(path, digest):
    if type(digest) is not str or len(digest) != 64:
        raise RuntimeError('CHILD_BINDING')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        info = os.fstat(fd)
        import stat
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= 1024 * 1024:
            raise RuntimeError('CHILD_INPUT_BOUND')
        raw = b''
        while len(raw) <= info.st_size:
            part = os.read(fd, info.st_size + 1 - len(raw))
            if not part:
                break
            raw += part
        after = os.fstat(fd)
        fields = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if fields(info) != fields(after) or len(raw) != info.st_size or hashlib.sha256(raw).hexdigest() != digest:
            raise RuntimeError('CHILD_INPUT_DRIFT')
        return raw
    finally:
        os.close(fd)


def main(config):
    if not (os.getpid() == 1 and sys.flags.isolated and sys.flags.no_site and
            sys.dont_write_bytecode and sys.pycache_prefix == '/cache-disabled' and
            Path('/cache-disabled').is_file() and not Path('/cache-disabled').is_symlink()):
        raise RuntimeError('CHILD_RUNTIME')
    if type(config) is not dict or set(config) != {
        'fixture_only', 'token', 'deadline', 'wire_sha', 'hooks_sha', 'build_sha', 'encoder_sha'
    } or config['fixture_only'] is not True:
        raise RuntimeError('CHILD_SCOPE')
    # All bytes are retained before any selected module executes.
    names = [('layout_bridge', 'wire_bridge.py', 'wire_sha'),
             ('hooks', 'hooks.py', 'hooks_sha')]
    retained = {name: selected('/runner/' + file, config[key]) for name, file, key in names}
    build = selected('/runner/projected-build-inert.py', config['build_sha'])
    encoder = selected('/runner/encoder-source.py', config['encoder_sha'])
    for name, file, _ in names:
        if name in sys.modules:
            raise RuntimeError('CHILD_PRELOADED')
        module = types.ModuleType(name)
        module.__file__ = '/runner/' + file
        sys.modules[name] = module
        exec(compile(retained[name], module.__file__, 'exec'), module.__dict__)
    B, H = sys.modules['layout_bridge'], sys.modules['hooks']
    here = Path('/workspace/product/lab/release-candidates/v1/interface/docker-context-20261020-0001')
    private = Path('/unmounted-context-private-fixture')
    B.need(not private.exists(), 'PRIVATE_FIXTURE_ABSENCE')
    source_path = here / 'source-manifest.json'
    source_raw = source_path.read_bytes()
    B.need(source_raw == b'{"synthetic_public_only":true}\n', 'SYNTHETIC_SOURCE_ONLY')
    source = {'path': str(source_path), 'sha256': B.sha(source_raw)}
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    sock.settimeout(max(0.001, config['deadline'] - time.monotonic()))
    sock.connect('/control/ipc')
    hooks = H.Hooks(sock, (0, os.getuid(), os.getgid()), here, private, source,
                    config['token'], config['deadline'], namespace_child=True)
    tree = ast.parse(build)
    function = lambda t, name: next(n for n in t.body if isinstance(n, ast.FunctionDef) and n.name == name)
    body = function(tree, 'build')
    span = lambda nodes: ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    binding = lambda p: {'path': str(p), 'sha256': B.sha(p.read_bytes())}
    namespace = {'HERE': here, 'require': B.need, 'json': json, 'time': time,
                 'started': time.monotonic(), 'root': private,
                 'source_pin': source['sha256'], 'mapped_pin': 'b' * 64,
                 'binding': binding, '_ctx_emit': hooks.emit,
                 '_ctx_output_ready': hooks.output_ready,
                 '_ctx_release_private': hooks.release_private,
                 '_ctx_print': hooks.provisional_print}
    try:
        exec(compile(span([function(ast.parse(encoder), 'encoded'), function(tree, 'emit')]),
                     'selected-original-functions', 'exec'), namespace)
        exec(compile(span(body.body[1:4]), 'selected-original-output-guard', 'exec'), namespace)
        for index, leaf in enumerate(B.LEAVES[:38]):
            raw = B.encode({'synthetic_public_body': index})
            namespace['emit'](namespace['out'] / leaf, None, raw=raw)
            B.need((namespace['out'] / leaf).read_bytes() == raw, 'POST_ACK_VISIBLE')
        exec(compile(span(body.body[-7:]), 'selected-original-tail', 'exec'), namespace)
        B.need(hooks.state == 'PROVISIONAL' and hooks.client.closed, 'CHILD_FINAL_CLOSE')
        # Parent captures this bounded provisional original print. It is never
        # forwarded as authoritative stdout before the aggregate closes.
        sys.stdout.buffer.write(hooks.output._raw)
        sys.stdout.buffer.flush()
    finally:
        hooks.client.close_once()


if __name__ == '__main__':
    try:
        main(json.loads(sys.argv[1]))
    except BaseException:
        sys.stderr.write('CONTEXT_SYNTHETIC_CHILD_UNKNOWN\n')
        raise SystemExit(1) from None
