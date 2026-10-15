"""Pinned uncached legacy replay bridge; performs no write or trust promotion."""
from __future__ import annotations
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from .common import RuntimeFault, byte_digest, digest, load, require, under, verify_seal


@dataclass(frozen=True)
class ReplayPins:
    """Trusted adapter inputs; never obtain these from the store's own envelope."""
    runtime_version: str
    manifest_path: str
    manifest_sha256: str
    config_sha256: str
    baseline_snapshot_digest: str
    expected_head: str | None = None


def legacy_runtime(executable_repo, pins):
    root = Path(executable_repo).resolve()
    manifest_file = under(root, pins.manifest_path)
    require(byte_digest(manifest_file.read_bytes()) == pins.manifest_sha256, 'legacy executable manifest changed')
    manifest = load(manifest_file)
    require(manifest.get('authority_effect') == 'none', 'legacy binding manifest grants no authority')
    rows = [r for r in manifest['runtimes'] if r['version'] == pins.runtime_version]
    require(len(rows) == 1 and pins.runtime_version in ['v1', 'v2'], 'unknown pinned legacy runtime')
    row = rows[0]
    package = under(root, row['package_path'])
    expected = {b['path'] for b in row['files']}
    actual = {p.relative_to(root).as_posix() for p in (package / 'lab_runtime').glob('*.py')} | {row['package_path'] + '/profile.json'}
    require(actual == expected, 'legacy executable closure changed')
    captured = {}
    for b in row['files']:
        file = under(root, b['path'])
        raw = file.read_bytes()
        require(not file.is_symlink() and byte_digest(raw) == b['sha256'], 'legacy executable bytes changed: ' + b['path'])
        captured[Path(b['path']).relative_to(Path(row['package_path']))] = raw
    stage = TemporaryDirectory(prefix='lab-pinned-full-verifier-')
    package = Path(stage.name)
    for relative, raw in captured.items():
        output = package / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(raw)
    # A fresh package namespace each call prevents mutable module state reuse.
    name = '_lab_full_verifier_' + pins.runtime_version + '_' + str(id(row))
    spec = importlib.util.spec_from_file_location(name, package / 'lab_runtime/__init__.py', submodule_search_locations=[str(package / 'lab_runtime')])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        store_spec = importlib.util.spec_from_file_location(name + '.store', package / 'lab_runtime/store.py')
        store_module = importlib.util.module_from_spec(store_spec)
        sys.modules[name + '.store'] = store_module
        store_spec.loader.exec_module(store_module)
        return name, store_module, stage
    except BaseException:
        stage.cleanup()
        for key in list(sys.modules):
            if key == name or key.startswith(name + '.'):
                sys.modules.pop(key, None)
        raise


def full_replay(path, repository, executable_repo, pins, *, require_current=False):
    """Verify every committed transaction from pinned genesis; never use a cache."""
    store_path = Path(path).resolve()
    require(not any('checkpoint' in f.name.lower() for f in store_path.iterdir()), 'persistent checkpoint input has no trust path; unsupported by full verifier')
    for relative in ['config.json', 'baseline.json', 'HEAD.json']:
        require(not (store_path / relative).is_symlink(), 'store root symlink forbidden')
    config = load(store_path / 'config.json')
    verify_seal(config)
    require(byte_digest((store_path / 'config.json').read_bytes()) == pins.config_sha256, 'independent store configuration pin mismatch')
    baseline = load(store_path / 'baseline.json')
    require(baseline.get('snapshot_digest') == pins.baseline_snapshot_digest, 'independent baseline pin mismatch')
    require(digest({k:v for k,v in baseline.items() if k != 'snapshot_digest'}) == pins.baseline_snapshot_digest, 'baseline bytes changed under external pin')
    head = load(store_path / 'HEAD.json')
    verify_seal(head)
    if pins.expected_head is not None:
        require(head.get('transaction_digest') == pins.expected_head, 'independent HEAD pin mismatch')
    require(type(head.get('sequence')) is int and 0 <= head['sequence'] <= 100000, 'invalid replay sequence')
    transaction_bindings = {}
    for sequence in range(head['sequence'] + 1):
        transaction = store_path / 'transactions' / f'{sequence:010d}.json'
        require(not transaction.is_symlink(), 'committed transaction symlink forbidden')
        # Strict original-byte JSON parsing supplements the preserved legacy reader.
        load(transaction)
        transaction_bindings[transaction] = byte_digest(transaction.read_bytes())
    name, adapter, stage = legacy_runtime(executable_repo, pins)
    try:
        result = adapter.Store(store_path, repository).replay(require_current=require_current)
        require(result['baseline']['snapshot_digest'] == pins.baseline_snapshot_digest, 'baseline changed during replay')
        require(byte_digest((store_path / 'config.json').read_bytes()) == pins.config_sha256, 'configuration changed during replay')
        require(load(store_path / 'HEAD.json') == head, 'HEAD changed during replay; inspect current state')
        legacy_runtime_manifest = under(Path(executable_repo).resolve(), pins.manifest_path)
        require(byte_digest(legacy_runtime_manifest.read_bytes()) == pins.manifest_sha256, 'executable manifest changed during replay')
        # Recheck code bytes and closure after execution as well as before it.
        for file, sha in transaction_bindings.items():
            require(byte_digest(file.read_bytes()) == sha, 'transaction bytes changed during replay')
        later_name, _, later_stage = legacy_runtime(executable_repo, pins)
        for key in list(sys.modules):
            if key == later_name or key.startswith(later_name + '.'):
                sys.modules.pop(key, None)
        later_stage.cleanup()
        return result
    except RuntimeFault:
        raise
    except Exception as exc:
        raise RuntimeFault('full replay rejected: ' + str(exc)) from exc
    finally:
        stage.cleanup()
        for key in list(sys.modules):
            if key == name or key.startswith(name + '.'):
                sys.modules.pop(key, None)


def replay(path, repository, executable_repo, pins, *, require_current=False):
    """Measured no-op: this path is the independent full verifier, every time."""
    return full_replay(path, repository, executable_repo, pins, require_current=require_current)
