"""Externally pinned cold original-source reader for the owned participation cut."""
from contextlib import contextmanager
import base64
import copy
from dataclasses import asdict
import os
import re
import tempfile
from base import *

adapter = module('_R03_fresh_signed_source_adapter', HERE.parent / 'operator-context-v5/source_adapter.py')


def package(source_pin, package_pin):
    control = verify_source(source_pin)
    path = HERE / 'packages/0001/manifest.json';require(sha(path.read_bytes()) == package_pin, 'independent participation package differs')
    m = load(path)
    require(m['authority_effect'] == 'none' and m['actual_owner_outcome'] is None and m['public_package_export_allowed'] is False
        and m['visibility'] == 'private-candidate-original-custody', 'source package posture cannot grant authority or public export')
    paths = set()
    for b in m['files']:
        require(b['path'].startswith((HERE / 'packages/0001').relative_to(ROOT).as_posix() + '/') and b['path'] not in paths, 'source package file closure escaped')
        original(b);paths.add(b['path'])
    expected = load(ROOT / m['expected_replay_binding']['path'])
    require(sha((ROOT / m['expected_replay_binding']['path']).read_bytes()) == m['expected_replay_binding']['sha256'], 'expected replay binding differs')
    require(expected['engine_pins'] == asdict(selected_pins()), 'independent source engine pins differ')
    require((ROOT / m['archive_binding']['path']).stat().st_size <= 64*1024*1024, 'source archive byte budget exceeded')
    return control, m, expected


def selection(source_pin, package_pin, name):
    require(name == 'fresh-participation', 'owned source nickname is closed')
    _, m, expected = package(source_pin, package_pin)
    return {'name': name, 'archive_binding': m['archive_binding'], 'expected_replay_binding': m['expected_replay_binding'],
        'config_sha256': expected['config_sha256'], 'baseline_snapshot_digest': expected['baseline_snapshot_digest'],
        'expected_head': expected['expected_head'], 'engine_pins': expected['engine_pins'],
        'candidate_selection_basis': {'manifest_sha256': package_pin, 'source_manifest_sha256': source_pin},
        'authority_effect': 'none', 'actual_owner_outcome': None}


@contextmanager
def open_signed(source_pin, package_pin):
    control, m, expected = package(source_pin, package_pin)
    row = selection(source_pin, package_pin, 'fresh-participation');a = json.loads(original(m['archive_binding']))
    require(a['schema_version'] == 'lab-owned-participation-archive/v1-candidate' and a['private_keys_exported'] is False
        and a['Session_memory_rehydrated'] is False and a['authority_effect'] == 'none' and a['actual_owner_outcome'] is None, 'source archive included forbidden key/runtime/authority state')
    require(a['engine_pins'] == expected['engine_pins'], 'archive executable differs')
    for key in ['config_sha256', 'baseline_snapshot_digest', 'expected_head']:
        require(a[key] == expected[key], 'independent archive source cut differs')
    head = json.loads(base64.b64decode(a['files']['HEAD.json']['base64_original_bytes'], validate=True))
    require(type(head['sequence']) is int and 0 <= head['sequence'] <= 100, 'source transaction count budget exceeded')
    names = {'config.json', 'baseline.json', 'HEAD.json'} | {f'transactions/{i:010d}.json' for i in range(head['sequence'] + 1)}
    require(set(a['files']) == names, 'closed original store byte files required')
    pins = selected_pins()
    with tempfile.TemporaryDirectory(prefix='cal-R03-fresh-cold-source-') as tmp, loader.engine(pins) as handle:
        root = Path(tmp);store = root / 'store';store.mkdir(mode=0o700);(store / 'transactions').mkdir(mode=0o700);originals = {}
        for name, b in a['files'].items():
            require(set(b) == {'sha256', 'base64_original_bytes'}, 'closed archived original byte binding required')
            raw = base64.b64decode(b['base64_original_bytes'], validate=True);require(sha(raw) == b['sha256'], 'archived original bytes differ')
            descriptor = os.open(store / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, 'wb') as f: f.write(raw)
            originals[name] = raw
        data = handle.replay_owned(store, expected['config_sha256'], expected['baseline_snapshot_digest'], expected['expected_head'])
        require(handle.common.digest(data['projection']) == expected['projection_sha256']
            and [handle.common.digest(t) for t in data['transactions']] == expected['transaction_sha256s'], 'cold signature/core/consequence/projection replay differs')
        source_view = adapter.source.Inspection(data, row, originals, handle)
        selected = adapter.SignedSources(source_view, control['source_adapter_binding']['sha256'],
            selection_reader=lambda name: selection(source_pin, package_pin, name))
        try:
            yield selected
            selected.guard()
            require(all((store / name).read_bytes() == raw for name, raw in originals.items()), 'cold reader changed original signed store')
            require({p.relative_to(store).as_posix() for p in store.rglob('*') if p.is_file()} == names, 'cold reader created runtime/Session or store files')
        finally: selected.close()
    require(not root.exists(), 'owned cold read store remains')
