"""Future separate Reader stage using held nofollow dirfds; effect disabled."""
from __future__ import annotations

import json
import os
from pathlib import Path

from anchored_copy import copy_exact, mkdir_exact, write_exact
from audit_stage import audit
from prepare_reader import HERE, SOURCE_ROOT, PRODUCER, NEW, parse, require

ATTEMPT = Path('/tmp/cal-reader-only-dev-20261020-0001-exact1')
STAGE_ENABLED = False  # A reviewed successor must select a release.


def source_modes(name: str) -> tuple[int, int]:
    """Selected Source mode policy, including the two distinct manifests."""
    if name == PRODUCER + '/source-manifest.json':
        return 0o444, 0o444
    if name.startswith(PRODUCER + '/packages/0001/'):
        return 0o600, 0o600
    return 0o444, 0o444


def stage() -> dict:
    require(STAGE_ENABLED, 'Reader separate stage disabled pending independent review')
    require(not ATTEMPT.exists(), 'Reader attempt already exists; no replacement')
    audit()  # Inert retained-stage check before copying.
    selection = parse((HERE / 'selection.json').read_bytes())
    source = parse((SOURCE_ROOT / PRODUCER / 'source-manifest.json').read_bytes())
    package = parse((SOURCE_ROOT / PRODUCER / 'packages/0001/manifest.json').read_bytes())
    expected = {r['path']: r['sha256'] for r in source['files'] + package['files']}
    expected[PRODUCER + '/source-manifest.json'] = selection['source_manifest_binding']['sha256']
    expected[PRODUCER + '/packages/0001/manifest.json'] = selection['source_package_binding']['sha256']
    require(len(expected) == 978, 'Source copy selection differs')
    role_dir = HERE / 'generated' / NEW
    role = parse((role_dir / 'source-manifest.json').read_bytes())
    selected_role = {r['path']: r['sha256'] for r in selection['projected_reader_bindings']}
    selected_role[NEW + '/source-manifest.json'] = selection['reader_manifest_binding']['sha256']
    require(len(selected_role) == 8 and role['producer_package_binding'] == selection['source_package_binding'],
            'Reader staged role differs')
    mkdir_exact(ATTEMPT, 0o700)
    root = ATTEMPT / 'root'
    mkdir_exact(root, 0o755)
    all_names = set(expected) | set(selected_role)
    dirs = {str(parent) for name in all_names for parent in Path(name).parents
            if str(parent) != '.'}
    dirs.add(PRODUCER + '/receipts')
    for name in sorted(dirs, key=lambda value: (len(Path(value).parts), value)):
        private = name == PRODUCER + '/receipts' or name.startswith(PRODUCER + '/packages')
        mkdir_exact(root / name, 0o700 if private else 0o755)
    for name in sorted(expected):
        source_mode, target_mode = source_modes(name)
        copy_exact(SOURCE_ROOT / name, root / name, expected[name],
                   target_mode, source_mode)
    for name in sorted(selected_role):
        copy_exact(HERE / 'generated' / name, root / name, selected_role[name],
                   0o444, 0o644)
    output = ATTEMPT / 'reader-output'
    mkdir_exact(output, 0o700)
    evidence = ATTEMPT / 'evidence'
    mkdir_exact(evidence, 0o700)
    result = {'schema_version': 'lab-fresh-reader-separate-stage/v2-inactive',
              'effect': 'NOT_RUN', 'source_root_unchanged_by_construction': True,
              'root': str(root), 'input_files': 986,
              'reader_output': str(output), 'private_archive_copied_opaquely': True,
              'source_manifest_sha256': selection['source_manifest_binding']['sha256'],
              'source_package_manifest_sha256': selection['source_package_binding']['sha256'],
              'reader_manifest_sha256': selection['reader_manifest_binding']['sha256']}
    out = evidence / 'stage-result.json'
    write_exact(out, (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    return result


if __name__ == '__main__':
    raise SystemExit('Reader separate stage disabled pending independent review')
