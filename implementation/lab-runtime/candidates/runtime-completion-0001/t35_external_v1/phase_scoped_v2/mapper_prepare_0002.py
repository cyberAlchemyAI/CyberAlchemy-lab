"""Fixture-only, delayed Mapper and native selection after Source/Reader.

This module can prepare and exclusively create four mapped role leaves and a
Mapper source manifest in disposable scratch. It never runs Mapper build or a
native executable, and its output is not a production phase receipt.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import stat

from .. import phase_rebind, role_stage, scratch_reader_probe as reader
from .. import scratch_source_probe as source
from ..held_paths import HeldCanonicalDirectory, _parse_closed
from ..path_contract import check_binding, require
from . import prefix_probe
from .plan import StagePlan

MAPPER_SCHEMA = 'lab-T35-disposable-mapper-source/v2-inactive'
MAPPER_NAMES = frozenset(role_stage.ROLE_FILES['mapped'])
MAPPER_LEAVES = frozenset('mapped/' + name for name in MAPPER_NAMES)
MAPPER_MANIFEST = 'mapped/source-manifest.json'
ENVIRONMENT = {'python': '3.14.4', 'jsonschema': '4.19.2', 'cryptography': '46.0.5'}


def _binding(path: PurePosixPath, raw: bytes) -> dict:
    return {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest()}


def _closed_rows(rows: object, *, family: PurePosixPath) -> dict[str, dict]:
    require(type(rows) is list, 'Mapper selected rows must be a list')
    selected: dict[str, dict] = {}
    for row in rows:
        require(type(row) is dict and set(row) == {'path', 'sha256'},
                'closed Mapper selected row required')
        check_binding(row, kind='output' if row['path'].startswith('/') else 'source_api',
                      family=family if row['path'].startswith('/') else None)
        require(row['path'] not in selected, 'duplicate Mapper selected row')
        selected[row['path']] = dict(row)
    return selected


def project(planned: StagePlan, repository_rows: dict[str, dict],
            source_raw: bytes, package_raw: bytes, reader_raw: bytes,
            native_raw: bytes, *, expected_package_members: set[str]
            ) -> tuple[dict[str, bytes], bytes, dict]:
    """Derive exact Mapper bytes from selected, fresh predecessor manifest bytes.

    The caller must additionally hold-read these three predecessor leaves and
    verify the Source package poststate; receipts alone are never inputs here.
    """
    require(type(planned) is StagePlan and
            type(planned.layout) is role_stage.DisposableLayout and
            type(repository_rows) is dict and
            all(type(raw) is bytes for raw in
                (source_raw, package_raw, reader_raw, native_raw)) and
            type(expected_package_members) is set,
            'typed disposable Mapper predecessor selection required')
    layout = planned.layout
    source_value = _parse_closed(source_raw)
    require(type(source_value) is dict and set(source_value) ==
            {'schema_version', 'files', 'environment', 'authority_effect',
             'actual_owner_outcome', 'fixture_only'} and
            source_value['schema_version'] ==
            'lab-T35-disposable-phase-prefix-source/v2-inactive' and
            source_value['environment'] == ENVIRONMENT and
            source_value['fixture_only'] is True and
            source_value['authority_effect'] == 'none' and
            source_value['actual_owner_outcome'] is None,
            'Source prefix manifest schema or authority differs')
    _, expected_source_raw = prefix_probe._source_selection(planned, repository_rows)
    require(source_raw == expected_source_raw,
            'Source manifest differs from exact initial plan and repository rows')
    package_value = _parse_closed(package_raw)
    require(type(package_value) is dict and set(package_value) ==
            {'schema_version', 'files', 'source_manifest_binding', 'archive_binding',
             'expected_replay_binding', 'period_binding', 'episode_contract_binding',
             'visibility', 'public_package_export_allowed', 'authority_effect',
             'actual_owner_outcome'} and
            package_value['schema_version'] ==
            'lab-owned-current-participation-package/v1-candidate' and
            package_value['source_manifest_binding'] ==
            _binding(layout.family / prefix_probe.reader.SOURCE_REL, source_raw) and
            package_value['visibility'] == 'private-candidate-original-custody' and
            package_value['public_package_export_allowed'] is False and
            package_value['authority_effect'] == 'none' and
            package_value['actual_owner_outcome'] is None,
            'Source package schema, source binding, or authority differs')
    package_rows = _closed_rows(package_value['files'], family=layout.family)
    prefix = layout.family / 'source/packages/0001'
    require(len(package_rows) == 36 and
            {str(PurePosixPath(name).relative_to(prefix)) for name in package_rows} ==
            expected_package_members,
            'Source package exact member set differs')
    require(all(package_value[key] == package_rows.get(str(prefix / name))
                for key, name in (
                    ('archive_binding', 'branch.snapshot'),
                    ('expected_replay_binding', 'expected-replay.json'),
                    ('period_binding', 'period.json'))) and
            package_value['episode_contract_binding'] ==
            _binding(layout.family / 'source/episode-contract.json', planned.episode_raw),
            'Source package core or episode binding differs')
    require(reader_raw == reader._reader_manifest(source_raw, package_raw),
            'Reader manifest differs from exact Source/package selection')
    reader_value = _parse_closed(reader_raw)
    reader_rows = _closed_rows(reader_value['files'], family=layout.family)
    require(reader_value['environment'] == ENVIRONMENT and
            reader_value['authority_effect'] == 'none' and
            reader_value['actual_owner_outcome'] is None and
            reader_value['fixture_only'] is True,
            'Reader environment or authority differs')
    native_name = str(role_stage.NATIVE_REL)
    native_row = {'path': native_name, 'sha256': role_stage.NATIVE_SHA}
    require(native_name not in repository_rows and native_name not in reader_rows and
            hashlib.sha256(native_raw).hexdigest() == role_stage.NATIVE_SHA,
            'Mapper native must be a new exact late selection')
    predecessor = {
        'source': _binding(layout.family / prefix_probe.reader.SOURCE_REL, source_raw),
        'source_package': _binding(layout.family / prefix_probe.reader.PACKAGE_REL,
                                   package_raw),
        'reader': _binding(layout.family / prefix_probe.reader.READER_REL, reader_raw),
    }
    template = {Path(path).name: bytes(raw) for role, path, raw in planned.templates
                if role == 'mapped'}
    require(set(template) == MAPPER_NAMES, 'four selected Mapper templates required')
    changed = phase_rebind.rebind(layout, 'mapped',
                                  {name: template[name] for name in ('base.py', 'build.py')},
                                  predecessor)
    template.update(changed)
    require(all(hashlib.sha256(template[name]).hexdigest() ==
                planned.mapper_bindings(predecessor)[str(layout.family / 'mapped' / name)]['sha256']
                for name in MAPPER_NAMES),
            'Mapper rendered bytes differ from immutable template plan')
    mapped_rows = [_binding(layout.family / 'mapped' / name, template[name])
                   for name in sorted(MAPPER_NAMES)]
    selected = dict(reader_rows)
    for row in [native_row,
                _binding(layout.family / prefix_probe.reader.READER_REL, reader_raw),
                *mapped_rows]:
        require(row['path'] not in selected, 'Mapper output aliases predecessor selection')
        selected[row['path']] = row
    require(set(selected).isdisjoint(str(layout.family / 'context' / name)
                                     for name in role_stage.ROLE_FILES['context']),
            'future Context role entered Mapper selection')
    manifest = {
        'schema_version': MAPPER_SCHEMA,
        'files': [selected[name] for name in sorted(selected)],
        'environment': ENVIRONMENT,
        'original_source_binding': predecessor['source'],
        'original_package_binding': predecessor['source_package'],
        'adapter_source_binding': predecessor['reader'],
        'selected_native_executable': {
            'path': str(layout.snapshot / role_stage.NATIVE_REL),
            'sha256': role_stage.NATIVE_SHA},
        'fixture_only': True,
        'qualification': False,
        'authority_effect': 'none',
        'actual_owner_outcome': None,
    }
    raw = reader._json(manifest)
    require(_parse_closed(raw) == manifest and len(selected) == len(reader_rows) + 6,
            'closed Mapper manifest derivation differs')
    return template, raw, predecessor


def _exclusive_leaf(parent: HeldCanonicalDirectory, name: str, raw: bytes) -> None:
    require(type(name) is str and name in MAPPER_NAMES | {'source-manifest.json'} and
            type(raw) is bytes and 0 < len(raw) <= 2 * 1024 * 1024 and parent.attached(),
            'bounded attached Mapper output required')
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW |
                 os.O_CLOEXEC, 0o600, dir_fd=parent.fd)
    try:
        view = memoryview(raw)
        while view:
            written = os.write(fd, view)
            require(written > 0, 'Mapper output write stalled')
            view = view[written:]
        os.fsync(fd)
        held = os.fstat(fd)
        attached = os.stat(name, dir_fd=parent.fd, follow_symlinks=False)
        require(stat.S_ISREG(held.st_mode) and held.st_nlink == 1 and
                (held.st_dev, held.st_ino, held.st_size) ==
                (attached.st_dev, attached.st_ino, attached.st_size) and
                held.st_size == len(raw) and parent.attached(),
                'Mapper leaf detached or aliased after exclusive write')
    finally:
        os.close(fd)


def materialize(family_host: Path, planned: StagePlan,
                repository_rows: dict[str, dict], source_raw: bytes,
                package_raw: bytes, reader_raw: bytes, native_raw: bytes, *,
                expected_package_members: set[str], pre_files: dict[str, str],
                pre_dirs: set[str]) -> tuple[dict[str, str], set[str], bytes, dict]:
    """Create only five delayed Mapper leaves in an owned disposable family.

    Any partial write is a refusal and the enclosing TemporaryDirectory must
    be cleaned. This function cannot authorize a later build or host install.
    """
    require(isinstance(family_host, Path) and type(pre_files) is dict and
            type(pre_dirs) is set and
            family_host.name == 'legacy-fixture-source',
            'closed disposable Mapper materialization required')
    template, manifest_raw, predecessor = project(
        planned, repository_rows, source_raw, package_raw, reader_raw, native_raw,
        expected_package_members=expected_package_members)
    require(source._tree_files(family_host) == pre_files and
            source._tree_dirs(family_host) == pre_dirs and
            'mapped' not in pre_dirs and 'context' not in pre_dirs and
            all(not name.startswith(('mapped/', 'context/')) for name in pre_files),
            'Source/Reader prestate changed or future role already materialized')
    with HeldCanonicalDirectory(str(family_host)) as family:
        os.mkdir('mapped', mode=0o700, dir_fd=family.fd)
        require(family.attached(), 'family detached during Mapper directory creation')
        with HeldCanonicalDirectory(str(family_host / 'mapped')) as mapped:
            for name in sorted(MAPPER_NAMES):
                _exclusive_leaf(mapped, name, template[name])
            _exclusive_leaf(mapped, 'source-manifest.json', manifest_raw)
            os.fsync(mapped.fd)
            require(mapped.attached() and family.attached(),
                    'Mapper directory or family detached after materialization')
        os.fsync(family.fd)
        require(family.attached(), 'family detached after Mapper directory fsync')
    post_files, post_dirs = source._tree_files(family_host), source._tree_dirs(family_host)
    expected = dict(pre_files)
    expected.update({'mapped/' + name: hashlib.sha256(raw).hexdigest()
                     for name, raw in template.items()})
    expected[MAPPER_MANIFEST] = hashlib.sha256(manifest_raw).hexdigest()
    require(post_files == expected and post_dirs == pre_dirs | {'mapped'},
            'Mapper materialization changed Source/Reader or created extra output')
    return post_files, post_dirs, manifest_raw, predecessor
