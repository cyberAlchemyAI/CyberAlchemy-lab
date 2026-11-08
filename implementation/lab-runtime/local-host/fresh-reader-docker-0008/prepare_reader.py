"""Construct only a fresh Reader role; never open the private Source archive."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
SOURCE_ROOT = Path('/tmp/cal-source-only-dev-20261020-0001-exact1/root')
INTERFACE = 'product/lab/release-candidates/v1/interface'
OLD = f'{INTERFACE}/legacy-session-fixture-reader-v1-action-0148'
NEW = f'{INTERFACE}/docker-reader-20261020-0001'
PRODUCER = f'{INTERFACE}/docker-source-20261020-0001'
SOURCE_SHA = '7e0938e70ac00b5308851b5a5a7c7bdb92041efab3be17296998acb4160395c1'
PACKAGE_SHA = 'f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b'
TERMINAL_SHA = '4b39cf98a4b9964becac7aa90086e0e77fe41c68addd6b67262544a0db47abdd'
ROLE = {
    '__init__.py': '1b88f99e5c0621338bf462d41cb54effcf2ec08cba8884fdf8dedc6179709529',
    'base.py': 'd677d3ab9ff523c07404ab95e3a77509b0a016323d4b8a0cd8c2c1f42e8c7d39',
    'reader.py': 'f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9',
    'adapter.py': '85646307fa07c768105258ef0d49226b2d06fc70af3e5993fb2f58ca2124c399',
    'inspection.py': '49770bd3c1f3c873840545a09f4ac207371b510b29e38f11a0523e0acb81cc11',
    'model.py': '687f42b643cfadaa2c9782cd1630c3ae26fff03c37d5f10ab2e9e0da4c8e70c7',
    'eligibility.py': '5d16158070ddfcdc026a59390041b11db39556435754f67623390c0bc6d4c2ba',
}
OLD_PRODUCER = 'legacy-session-fixture-source-v1-action-0148'
NEW_PRODUCER = 'docker-source-20261020-0001'
OLD_MODULE = '_cal_legacy_session_fixture_producer_0257'
NEW_MODULE = '_cal_docker_reader_producer_20261020_0001'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode()


def parse(raw: bytes) -> dict:
    def pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs)


def read_regular(path: Path) -> bytes:
    require(path.is_file() and not path.is_symlink(), 'missing or unsafe regular input: ' + str(path))
    return path.read_bytes()


def projection(name: str, raw: bytes) -> bytes:
    require(name in ROLE and sha(raw) == ROLE[name], 'Reader preimage differs: ' + name)
    if name != 'base.py':
        return raw
    text = raw.decode('utf-8')
    for old, new in ((OLD_PRODUCER, NEW_PRODUCER), (OLD_MODULE, NEW_MODULE)):
        require(text.count(old) == 1, 'Reader projection span differs: ' + old)
        text = text.replace(old, new, 1)
    projected = text.encode('utf-8')
    inverse = projected.decode('utf-8')
    for old, new in ((OLD_PRODUCER, NEW_PRODUCER), (OLD_MODULE, NEW_MODULE)):
        require(inverse.count(new) == 1, 'Reader inverse span differs: ' + new)
        inverse = inverse.replace(new, old, 1)
    require(inverse.encode('utf-8') == raw, 'Reader inverse did not recover exact preimage')
    return projected


def build() -> dict:
    source_path = SOURCE_ROOT / PRODUCER / 'source-manifest.json'
    package_path = SOURCE_ROOT / PRODUCER / 'packages/0001/manifest.json'
    terminal_path = SOURCE_ROOT.parent / 'evidence/source-once.terminal.json'
    source_raw, package_raw, terminal_raw = map(read_regular, (source_path, package_path, terminal_path))
    require(sha(source_raw) == SOURCE_SHA and sha(package_raw) == PACKAGE_SHA and
            sha(terminal_raw) == TERMINAL_SHA, 'completed Source predecessor pin differs')
    source, package, terminal = map(parse, (source_raw, package_raw, terminal_raw))
    require(terminal['overall'] == terminal['operation'] == 'PASS' and
            terminal['package_manifest_sha256'] == PACKAGE_SHA and terminal['no_retry'] is True,
            'Source terminal is not selected PASS')
    require(len(source['files']) == 940 and len({r['path'] for r in source['files']}) == 940,
            'Source public closure differs')
    require(package['source_manifest_binding'] == {'path': PRODUCER + '/source-manifest.json', 'sha256': SOURCE_SHA} and
            len(package['files']) == 36, 'selected Source package differs')
    role_dir = HERE / 'generated' / NEW
    require(not role_dir.exists(), 'Reader projection already exists; no overwrite')
    role_dir.mkdir(parents=True)
    original_rows, projected_rows = [], []
    for name, expected in sorted(ROLE.items()):
        original = read_regular(REPO / OLD / name)
        require(sha(original) == expected, 'Reader source changed')
        result = projection(name, original)
        target = role_dir / name
        target.write_bytes(result)
        original_rows.append({'path': OLD + '/' + name, 'sha256': expected})
        projected_rows.append({'path': NEW + '/' + name, 'sha256': sha(result)})
    input_rows = source['files'] + [{'path': PRODUCER + '/source-manifest.json', 'sha256': SOURCE_SHA}] + projected_rows
    names = [r['path'] for r in input_rows]
    require(len(names) == 948 and len(set(names)) == 948 and all(not n.endswith('/branch.snapshot') for n in names),
            'Reader selected static closure differs')
    reader_manifest = {
        'schema_version': 'lab-docker-distinct-reader-source/v1-candidate',
        'files': sorted(input_rows, key=lambda row: row['path']),
        'environment': {'python': '3.14.4', 'jsonschema': '4.23.0', 'cryptography': '46.0.5'},
        'fixture_only': True, 'qualification': False, 'authority_effect': 'none',
        'actual_owner_outcome': None,
        'producer_source_binding': {'path': PRODUCER + '/source-manifest.json', 'sha256': SOURCE_SHA},
        'producer_package_binding': {'path': PRODUCER + '/packages/0001/manifest.json', 'sha256': PACKAGE_SHA},
    }
    manifest_raw = encoded(reader_manifest)
    (role_dir / 'source-manifest.json').write_bytes(manifest_raw)
    selection = {
        'schema_version': 'lab-fresh-reader-docker-selection/v1-inactive',
        'effect': 'NOT_RUN', 'source_attempt': str(SOURCE_ROOT.parent),
        'source_terminal_binding': {'path': str(terminal_path), 'sha256': TERMINAL_SHA},
        'source_manifest_binding': {'path': PRODUCER + '/source-manifest.json', 'sha256': SOURCE_SHA},
        'source_package_binding': {'path': PRODUCER + '/packages/0001/manifest.json', 'sha256': PACKAGE_SHA},
        'reader_manifest_binding': {'path': NEW + '/source-manifest.json', 'sha256': sha(manifest_raw)},
        'original_reader_preimages': original_rows, 'projected_reader_bindings': projected_rows,
        'episode_expires_at': '2026-10-21T08:20:00+00:00',
        'expected_head': 'b4d3b5288e8b3140bb0dd06c04e660379a3179ca75b56f2f98de2ba2888e43b1',
        'archive_declared_sha256': package['archive_binding']['sha256'],
        'package_member_count': 36, 'reader_static_input_count': 948,
        'claim_ceiling': 'Effect-disabled fresh Reader construction and inert Source-stage audit only; no archive cold-open, Reader/Mapper/Context effect, protected Source8 or original-plan acceptance.',
    }
    (HERE / 'selection.json').write_bytes(encoded(selection))
    return {'result': 'PASS_CONSTRUCTED_INACTIVE', 'reader_manifest_sha256': sha(manifest_raw),
            'selection_sha256': sha(encoded(selection)), 'projected_role_files': len(projected_rows)}


if __name__ == '__main__':
    print(json.dumps(build(), sort_keys=True))
