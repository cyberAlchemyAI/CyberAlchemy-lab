"""Future single Reader cold-open entrypoint. Never run before independent review."""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path('/attempt/root')
TOOL = Path('/tool')
OUT = Path('/attempt/reader-output')
PRODUCER = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001'
READER = 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0001'
SELECTION_SHA = '073bc2938e30d6d108ed8b22205eed551d3879c1eab4379d0200c4e9f2d90b22'
READER_SHA = '4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251'
MODULE = '_cal_docker_reader_20261020_0001'
PRODUCER_MODULE = '_cal_docker_reader_producer_20261020_0001'
EFFECT_ENABLED = False  # A separately reviewed successor must select a release.


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                       allow_nan=False) + '\n').encode()


def parse(raw: bytes) -> dict:
    def pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs)


def period_current(value: dict, now: dt.datetime | None = None) -> None:
    now = dt.datetime.now(dt.timezone.utc) if now is None else now
    require(now.tzinfo is not None, 'Reader wall clock lacks timezone')
    start = dt.datetime.fromisoformat(value['not_before'])
    end = dt.datetime.fromisoformat(value['expires_at'])
    require(start.tzinfo is not None and end.tzinfo is not None and
            start <= now < end and end - start == dt.timedelta(hours=24),
            'Source participation period is not current')


def regular(path: Path) -> bytes:
    require(path.is_file() and not path.is_symlink(), 'unsafe Reader input')
    return path.read_bytes()


def selected() -> tuple[dict, dict, dict]:
    require(EFFECT_ENABLED, 'Reader effect disabled pending independent review and release')
    require(ROOT.is_dir() and not ROOT.is_symlink() and OUT.is_dir() and
            not OUT.is_symlink() and not list(OUT.iterdir()), 'Reader stage/output state differs')
    raw = regular(TOOL / 'selection.json')
    require(sha(raw) == SELECTION_SHA, 'Reader selection pin differs')
    selection = parse(raw)
    require(selection['effect'] == 'NOT_RUN' and
            selection['reader_manifest_binding'] == {'path': READER + '/source-manifest.json', 'sha256': READER_SHA},
            'Reader selection shape differs')
    source_raw = regular(ROOT / PRODUCER / 'source-manifest.json')
    package_raw = regular(ROOT / PRODUCER / 'packages/0001/manifest.json')
    reader_raw = regular(ROOT / READER / 'source-manifest.json')
    require(sha(source_raw) == selection['source_manifest_binding']['sha256'] and
            sha(package_raw) == selection['source_package_binding']['sha256'] and
            sha(reader_raw) == READER_SHA, 'selected Source/Reader manifest differs')
    source, package, reader = map(parse, (source_raw, package_raw, reader_raw))
    require(package['source_manifest_binding'] == selection['source_manifest_binding'] and
            reader['producer_source_binding'] == selection['source_manifest_binding'] and
            reader['producer_package_binding'] == selection['source_package_binding'] and
            reader['authority_effect'] == 'none' and reader['actual_owner_outcome'] is None,
            'Source/Reader producer join differs')
    period_raw = regular(ROOT / PRODUCER / 'packages/0001/period.json')
    period = parse(period_raw)
    period_current(period)
    require(period['expires_at'] == selection['episode_expires_at'] and
            package['period_binding']['sha256'] == sha(period_raw),
            'selected Source period differs')
    expected_raw = regular(ROOT / PRODUCER / 'packages/0001/expected-replay.json')
    expected = parse(expected_raw)
    require(expected['expected_head'] == selection['expected_head'] and
            package['expected_replay_binding']['sha256'] == sha(expected_raw),
            'Source signed cut selection differs')
    expected_rows = reader['files'] + package['files'] + [
        {'path': READER + '/source-manifest.json', 'sha256': READER_SHA},
        {'path': PRODUCER + '/packages/0001/manifest.json',
         'sha256': selection['source_package_binding']['sha256']},
    ]
    names = [row['path'] for row in expected_rows]
    require(len(names) == 986 and len(set(names)) == 986, 'Reader staged file count differs')
    files, dirs = set(), set()
    for path in ROOT.rglob('*'):
        mode = path.lstat().st_mode
        require(stat.S_ISREG(mode) or stat.S_ISDIR(mode), 'Reader stage has nonregular entry')
        (files if stat.S_ISREG(mode) else dirs).add(path.relative_to(ROOT).as_posix())
    expected_dirs = {parent.as_posix() for name in names for parent in Path(name).parents
                     if parent.as_posix() != '.'} | {PRODUCER + '/receipts'}
    require(files == set(names) and dirs == expected_dirs, 'Reader stage inventory differs')
    for row in expected_rows:
        require(sha(regular(ROOT / row['path'])) == row['sha256'],
                'Reader selected input differs: ' + row['path'])
    return selection, period, expected


def fresh_module_namespace() -> None:
    require(not any(k == MODULE or k.startswith(MODULE + '.') or
                    k == PRODUCER_MODULE or k.startswith(PRODUCER_MODULE + '.')
                    for k in sys.modules), 'stale Reader/Source module namespace present')


def run() -> dict:
    require(EFFECT_ENABLED, 'Reader effect disabled pending independent review and release')
    selection, _, expected = selected()
    fresh_module_namespace()
    role = ROOT / READER
    spec = importlib.util.spec_from_file_location(MODULE, role / '__init__.py',
                                                   submodule_search_locations=[str(role)])
    require(spec is not None and spec.loader is not None, 'Reader module spec unavailable')
    package = importlib.util.module_from_spec(spec)
    sys.modules[MODULE] = package
    spec.loader.exec_module(package)
    loaded = __import__(MODULE + '.reader', fromlist=['SelectedReader'])
    require(Path(loaded.__file__).resolve() == role / 'reader.py', 'actual Reader origin differs')
    reader = loaded.SelectedReader(READER_SHA,
                                   selection['source_manifest_binding']['sha256'],
                                   selection['source_package_binding']['sha256'])
    with reader.open_signed(reader.source_pin, reader.package_pin) as signed:
        require(type(signed) is loaded.adapter.SignedSources and
                type(signed.view) is loaded.Inspection, 'actual Reader type differs')
        period_current(parse(regular(ROOT / PRODUCER / 'packages/0001/period.json')))
        signed.guard()
        report = signed.closure_report()
        result = {
            'schema_version': 'lab-disposable-reader-receipt/v1-private',
            'reader_manifest_sha256': READER_SHA,
            'source_manifest_sha256': reader.source_pin,
            'source_package_manifest_sha256': reader.package_pin,
            'expected_head': expected['expected_head'],
            'source_cut': signed.source_cut,
            'accounted_subjects': len(signed.dispositions),
            'current_records': len(signed.records),
            'schemas': len(signed.schemas),
            'missing_current_carriers': report['missing_current_carriers'],
            'private_closure_report_sha256': sha(encoded(report)),
            'authority_effect': 'none', 'actual_owner_outcome': None,
            'claim_ceiling': 'Disposable exact-pinned Source cold-open and fresh Reader diagnostic only.',
        }
    period_current(parse(regular(ROOT / PRODUCER / 'packages/0001/period.json')))
    selected()  # Recheck every input, including private archive, after close.
    period_current(parse(regular(ROOT / PRODUCER / 'packages/0001/period.json')))
    raw = encoded(result)
    fd = os.open(OUT / 'receipt.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    output_fd = os.open(OUT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(output_fd)
    finally:
        os.close(output_fd)
    require((OUT / 'receipt.json').read_bytes() == raw and
            {p.name for p in OUT.iterdir()} == {'receipt.json'}, 'Reader receipt differs')
    period_current(parse(regular(ROOT / PRODUCER / 'packages/0001/period.json')))
    return {'result': 'PASS_READER_PRIVATE', 'receipt_sha256': sha(raw),
            'reader_manifest_sha256': READER_SHA, 'source_package_manifest_sha256': reader.package_pin}


if __name__ == '__main__':
    require(sys.argv[1:] == ['--execute-reviewed-one-shot'], 'reviewed one-shot flag required')
    require(EFFECT_ENABLED, 'Reader effect disabled pending independent review and release')
    print(json.dumps(run(), sort_keys=True))
