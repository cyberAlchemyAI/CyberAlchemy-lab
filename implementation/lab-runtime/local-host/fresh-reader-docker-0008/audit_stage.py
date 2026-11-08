"""Read-only audit of the retained Source stage and constructed Reader role.

The private branch.snapshot is never opened here. Its current bytes remain an
explicit pre-dispatch check for the later reviewed Reader effect.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import stat
from pathlib import Path

from prepare_reader import (HERE, SOURCE_ROOT, PRODUCER, NEW, ROLE, OLD,
                            SOURCE_SHA, PACKAGE_SHA, TERMINAL_SHA,
                            projection, parse, require, sha)

SELECTION_SHA = '073bc2938e30d6d108ed8b22205eed551d3879c1eab4379d0200c4e9f2d90b22'
READER_SHA = '4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251'


def entries(root: Path) -> tuple[set[str], set[str]]:
    files, directories = set(), set()
    require(root.is_dir() and not root.is_symlink(), 'stage root changed')
    for path in root.rglob('*'):
        mode = path.lstat().st_mode
        require(stat.S_ISREG(mode) or stat.S_ISDIR(mode), 'nonregular or symlink stage entry')
        name = path.relative_to(root).as_posix()
        (files if stat.S_ISREG(mode) else directories).add(name)
    return files, directories


def expected_dirs(files: set[str]) -> set[str]:
    names = {parent.as_posix() for name in files for parent in Path(name).parents
             if parent.as_posix() != '.'}
    names.add(PRODUCER + '/receipts')
    return names


def audit(root: Path = SOURCE_ROOT, *, now: dt.datetime | None = None,
          selection_path: Path | None = None, role_root: Path | None = None,
          strict_inventory: bool = True) -> dict:
    selection_path = HERE / 'selection.json' if selection_path is None else selection_path
    role_root = HERE / 'generated' / NEW if role_root is None else role_root
    selection_raw = selection_path.read_bytes()
    require(sha(selection_raw) == SELECTION_SHA, 'trusted Reader selection changed')
    selected = parse(selection_raw)
    require(selected['effect'] == 'NOT_RUN' and selected['source_attempt'] == str(root.parent) and
            selected['source_terminal_binding']['sha256'] == TERMINAL_SHA and
            selected['source_manifest_binding']['sha256'] == SOURCE_SHA and
            selected['source_package_binding']['sha256'] == PACKAGE_SHA and
            selected['reader_manifest_binding']['sha256'] == READER_SHA and
            selected['reader_static_input_count'] == 948,
            'Reader selection shape differs')
    current = dt.datetime.now(dt.timezone.utc) if now is None else now
    require(current.tzinfo is not None and current < dt.datetime.fromisoformat(selected['episode_expires_at']),
            'selected Source episode expired')
    terminal_path = root.parent / 'evidence/source-once.terminal.json'
    terminal_raw = terminal_path.read_bytes()
    require(sha(terminal_raw) == TERMINAL_SHA, 'selected Source terminal differs')
    terminal = parse(terminal_raw)
    require(terminal['overall'] == terminal['operation'] == 'PASS' and
            terminal['package_manifest_sha256'] == PACKAGE_SHA and terminal['no_retry'] is True,
            'selected Source effect differs')
    source_path = root / PRODUCER / 'source-manifest.json'
    package_path = root / PRODUCER / 'packages/0001/manifest.json'
    source_raw, package_raw = source_path.read_bytes(), package_path.read_bytes()
    require(sha(source_raw) == SOURCE_SHA and sha(package_raw) == PACKAGE_SHA,
            'Source manifest or package differs')
    source, package = parse(source_raw), parse(package_raw)
    require(package['source_manifest_binding'] == selected['source_manifest_binding'] and
            len(package['files']) == selected['package_member_count'],
            'Source package closure differs')
    expected_source = {r['path']: r['sha256'] for r in source['files']}
    require(len(source['files']) == 940 and len(expected_source) == 940,
            'Source static closure duplicate or incomplete')
    expected_source[PRODUCER + '/source-manifest.json'] = SOURCE_SHA
    for path, digest in expected_source.items():
        item = root / path
        require(item.is_file() and not item.is_symlink() and sha(item.read_bytes()) == digest,
                'selected public input differs: ' + path)
    expected_package = {r['path']: r['sha256'] for r in package['files']}
    require(len(expected_package) == 36 and len(package['files']) == 36 and
            package['archive_binding']['path'] in expected_package,
            'Source package member inventory differs')
    output_rows = {PRODUCER + '/' + r['path']: r for r in terminal['output_inventory']['files']}
    require(len(output_rows) == 37 and
            set(output_rows) == set(expected_package) | {PRODUCER + '/packages/0001/manifest.json'},
            'Source output receipt inventory differs')
    archive_path = package['archive_binding']['path']
    for path, digest in expected_package.items():
        item = root / path
        require(item.is_file() and not item.is_symlink() and item.stat().st_size == output_rows[path]['size'] and
                digest == output_rows[path]['sha256'], 'package member attachment differs: ' + path)
        if path != archive_path:
            require(sha(item.read_bytes()) == digest, 'package member bytes differ: ' + path)
    require(output_rows[PRODUCER + '/packages/0001/manifest.json']['sha256'] == PACKAGE_SHA,
            'Source output manifest receipt differs')
    role_manifest_path = role_root / 'source-manifest.json'
    role_raw = role_manifest_path.read_bytes()
    require(sha(role_raw) == READER_SHA, 'fresh Reader manifest differs')
    role = parse(role_raw)
    require(role['producer_source_binding'] == selected['source_manifest_binding'] and
            role['producer_package_binding'] == selected['source_package_binding'] and
            role['environment'] == {'python': '3.14.4', 'jsonschema': '4.23.0', 'cryptography': '46.0.5'} and
            role['authority_effect'] == 'none' and role['actual_owner_outcome'] is None and
            role['fixture_only'] is True and role['qualification'] is False,
            'Reader manifest contract differs')
    role_rows = {r['path']: r['sha256'] for r in role['files']}
    require(len(role['files']) == 948 and len(role_rows) == 948 and
            role_rows == {**expected_source, **{r['path']: r['sha256'] for r in selected['projected_reader_bindings']}},
            'Reader role/code closure differs')
    for name, old_digest in ROLE.items():
        projected_path = NEW + '/' + name
        actual = (role_root / name).read_bytes()
        original = (HERE.parents[3] / OLD / name).read_bytes()
        require(sha(original) == old_digest and actual == projection(name, original) and
                sha(actual) == role_rows[projected_path],
                'Reader projection differs: ' + name)
    if strict_inventory:
        files, directories = entries(root)
        intended = set(expected_source) | set(expected_package) | {PRODUCER + '/packages/0001/manifest.json'}
        require(files == intended and directories == expected_dirs(intended),
                'Source stage contains unexpected file or directory')
    return {
        'schema_version': 'lab-fresh-reader-stage-audit/v1-inert',
        'result': 'PASS_INERT', 'effect': 'NOT_RUN', 'reader_manifest_sha256': READER_SHA,
        'source_manifest_sha256': SOURCE_SHA, 'source_package_manifest_sha256': PACKAGE_SHA,
        'selected_source_static_files': len(expected_source), 'selected_package_files': 37,
        'projected_reader_modules': 7, 'archive_current_bytes_checked': False,
        'claim_ceiling': selected['claim_ceiling'],
    }


if __name__ == '__main__':
    print(json.dumps(audit(), sort_keys=True))
