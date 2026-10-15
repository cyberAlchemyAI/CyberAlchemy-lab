"""Pinned candidate sources and bounded, original-byte output construction."""
from dataclasses import asdict
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path, PurePosixPath
import platform
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


def sha(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode()
def load(path): return json.loads(path.read_bytes())


def require(value, reason):
    if not value: raise ValueError(reason)


def binding(path):
    path = Path(path)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def original(row):
    name = row['path'];p = PurePosixPath(name)
    require(not p.is_absolute() and p.as_posix() == name and '..' not in p.parts and '\\' not in name, 'unsafe selected source path')
    file = ROOT / name
    require(file.is_file() and not file.is_symlink() and not any(x.is_symlink() for x in file.parents), 'unsafe original source')
    raw = file.read_bytes();require(sha(raw) == row['sha256'], 'selected source bytes changed: ' + name)
    return raw


def verify_source(pin):
    path = HERE / 'source-manifest.json';require(sha(path.read_bytes()) == pin, 'independent participation source pin differs')
    value = load(path)
    require(value['authority_effect'] == 'none' and value['actual_owner_outcome'] is None, 'candidate source cannot grant authority')
    require(value['environment'] == {'python': platform.python_version(), 'jsonschema': importlib.metadata.version('jsonschema'), 'cryptography': importlib.metadata.version('cryptography')}, 'selected R02 participation environment differs')
    for row in value['files']: original(row)
    return value


def emit(path, value, *, raw=None):
    path = Path(path)
    require(path.is_relative_to(HERE / 'packages') or path.is_relative_to(HERE / 'receipts'), 'outside candidate output boundary')
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    import os
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as stream: stream.write(encoded(value) if raw is None else raw)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path);m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m;spec.loader.exec_module(m);return m


loader = module('_R03_fresh_participation_engine', HERE.parent / 'corrections-v1/loader.py')


def selected_pins():
    # The source manifest independently fixes this file; no discovery-based grant.
    return loader.EnginePins(**load(HERE.parent / 'corrections-v1/pins.json'))
