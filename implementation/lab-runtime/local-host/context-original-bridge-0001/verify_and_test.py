"""Exact-byte, synthetic-only test dispatch. No actual Context launch route."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent
SELECTION_SHA = '98b533c67c31c476f850de7f98e038712f9077c76fc45f0e2811682dc21ca566'
GUARD = '/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-02/python-bytecode-cache-disabled-0002'


def read(path, expected_sha, expected_size):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size != expected_size or expected_size > 128 * 1024 * 1024:
            raise RuntimeError('SELECTED_TYPE_SIZE')
        digest = hashlib.sha256()
        chunks = []
        total = 0
        while total <= expected_size:
            chunk = os.read(fd, min(1024 * 1024, expected_size + 1 - total))
            if not chunk:
                break
            digest.update(chunk)
            chunks.append(chunk)
            total += len(chunk)
        after = os.fstat(fd)
        fields = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if fields(info) != fields(after) or total != expected_size or digest.hexdigest() != expected_sha:
            raise RuntimeError('SELECTED_BYTES_DRIFT')
        return b''.join(chunks)
    finally:
        os.close(fd)


def verify():
    path = HERE / 'selection.json'
    raw = read(path, SELECTION_SHA, path.lstat().st_size)
    selected = json.loads(raw)
    if selected['effect_enabled'] is not False:
        raise RuntimeError('EFFECT_DISABLED_REQUIRED')
    retained = {}
    for row in selected['input_bindings']:
        data = read(row['path'], row['sha256'], row['size'])
        if Path(row['path']).parent == HERE:
            retained[Path(row['path']).name] = data
    return selected, retained


def main():
    if not (sys.flags.no_site and sys.dont_write_bytecode and
            sys.executable == '/usr/bin/python3.14' and
            os.environ.get('PYTHONPYCACHEPREFIX') == GUARD and
            Path(GUARD).is_file() and not Path(GUARD).is_symlink() and
            'adapter' not in sys.modules):
        raise RuntimeError('TEST_RUNTIME_SELECTION')
    selected, retained = verify()
    for name in ('layout_bridge', 'project', 'hooks'):
        if name in sys.modules:
            raise RuntimeError('PRELOADED_CANDIDATE')
        module = types.ModuleType(name)
        module.__file__ = str(HERE / (name + '.py'))
        sys.modules[name] = module
        exec(compile(retained[name + '.py'], module.__file__, 'exec'), module.__dict__)
    tests = types.ModuleType('_selected_original_bridge_tests')
    tests.__file__ = str(HERE / 'test_original.py')
    sys.modules[tests.__name__] = tests
    exec(compile(retained['test_original.py'], tests.__file__, 'exec'), tests.__dict__)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    verify()
    print(json.dumps({'schema_version': 'context-bridge-static-test-result/v1',
                      'selection_sha256': SELECTION_SHA, 'tests_run': result.testsRun,
                      'passed': result.wasSuccessful(), 'optimization': sys.flags.optimize,
                      'selected_inputs_pre_post': len(selected['input_bindings']),
                      'original_Context_effect': 'NOT_RUN',
                      'private_archive_body_read': False,
                      'claim': 'selected_original_AST_and_synthetic_IPC_no_Docker'}, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
