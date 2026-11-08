"""Byte-backed isolated execution of the frozen O03 query source cut."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'implementation/lab-runtime/local-host/t10-o03-current-engine-successor-0002'
CONTROL_SHA = '559ca5e90bc1d0e90d1724a2d2b8ecc1427e2694469bfb4d89c6c7a208fc6b6d'
QUERY_SHA = '35669dfc01b3b5eaa7740666c9507a6c5a9511ebd1eb14d662a0315f6570c84f'
PROBE_SHA = 'a4d634c2b3f0ebc29fe30354cad763020bfdd72c3342321b77f4f6032b683f40'
LOADER = ROOT / 'product/lab/release-candidates/v1/interface/coupling/loader.py'
LOADER_SHA = '858620f70be64e23e5f276efe41986fee9ecf5fe6bb1de0c227f6f8751653bd6'
ORDER = ('common', 'contract', 'scope', 'selection', 'model', 'materialize')
NAMES = ('probe', 'query_run', *ORDER, '_O03_T12_successor_engine_loader')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_exact(path, expected):
    path = Path(path)
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('selected executable path has a linked ancestor')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        raw = os.read(fd, os.fstat(fd).st_size + 1)
    finally:
        os.close(fd)
    if sha(raw) != expected or sha(path.read_bytes()) != expected:
        raise ValueError('selected executable bytes changed: ' + str(path))
    return raw


def execute_module(name, path, raw):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__package__ = ''
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


@contextmanager
def selected_modules():
    raw_control = read_exact(OLD / 'query-control-selection.json', CONTROL_SHA)
    control = json.loads(raw_control)
    bindings = {row['path']: row['sha256'] for row in control['files']}
    expected = {p.relative_to(ROOT).as_posix() for p in (OLD / 'query-successor').rglob('*')
                if p.is_file() and '__pycache__' not in p.parts}
    if (control['schema_version'] != 'lab-T10-O03-current-query-control-selection/v1' or
            len(bindings) != len(control['files']) or set(bindings) != expected):
        raise ValueError('selected query control closure differs')
    raws = {}
    for path, digest in bindings.items():
        raws[path] = read_exact(ROOT / path, digest)
    raw_probe = read_exact(OLD / 'probe.py', PROBE_SHA)
    raw_query = read_exact(OLD / 'query_run.py', QUERY_SHA)
    raw_loader = read_exact(LOADER, LOADER_SHA)
    previous = {name: sys.modules.get(name) for name in NAMES}
    previous_path = list(sys.path)
    try:
        probe = execute_module('probe', OLD / 'probe.py', raw_probe)
        modules = {}
        for name in ORDER:
            path = OLD / 'query-successor' / (name + '.py')
            raw = raws[path.relative_to(ROOT).as_posix()]
            if name == 'scope':
                def pinned_loader(loader_name, loader_path):
                    if loader_name != '_O03_T12_successor_engine_loader' or Path(loader_path) != LOADER:
                        raise ValueError('unselected query loader origin')
                    return execute_module(loader_name, LOADER, raw_loader)
                modules['common'].module = pinned_loader
            modules[name] = execute_module(name, path, raw)
        query_run = execute_module('query_run', OLD / 'query_run.py', raw_query)
        query_run.query_modules = lambda manifest: modules
        query_run.verify_controls()
        yield query_run, modules
        query_run.verify_controls()
        if any(sha((ROOT / path).read_bytes()) != digest for path, digest in bindings.items()):
            raise ValueError('selected query controls changed during execution')
        read_exact(OLD / 'probe.py', PROBE_SHA)
        read_exact(OLD / 'query_run.py', QUERY_SHA)
        read_exact(LOADER, LOADER_SHA)
    finally:
        sys.path[:] = previous_path
        for name, previous_module in previous.items():
            if previous_module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous_module


def execute(scope_name):
    if scope_name not in ('current-specialist-owner', 'historical-d73-slice'):
        raise ValueError('unselected secure query scope')
    with selected_modules() as (runner, modules):
        answers = runner.execute(scope_name)
        answer_digests = {name: sha(runner.canonical(answer)) for name, answer in answers.items()}
    return {'scope': scope_name, 'answer_digests': answer_digests,
            'query_control_sha256': CONTROL_SHA, 'query_run_sha256': QUERY_SHA,
            'loader_sha256': LOADER_SHA, 'probe_sha256': PROBE_SHA,
            'module_execution': 'compiled from selected bytes with ambient modules displaced',
            'authority_effect': 'none', 'selected_governed_models': 0}


if __name__ == '__main__':
    print(json.dumps(execute(sys.argv[1]), sort_keys=True, indent=2))
