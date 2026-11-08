"""Exact future Reader stage selection; no private read, copy, or Docker effect."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
SELECTOR = LOCAL / 'reader-successor-recovery-0001'
SELECTOR_FREEZE_SHA = '8cff5cfca3b9488846f7c120fdfc1195560e0d262c5d8e7674cc34572da399ab'
SELECTOR_REVIEW = LOCAL / 'READER-SUCCESSOR-RECOVERY-INDEPENDENT-STATIC-REVIEW-0001.md'
SELECTOR_REVIEW_SHA = '473ac7499fef0f6ddd627bd02b52be5313d4a25a93602c7e792a94144a661390'
STATE = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
SOURCE_ROOT = STATE / 'source-attempt/root'
STAGE_ATTEMPT = STATE / 'reader-stage-attempt'
STAGE_ROOT = STAGE_ATTEMPT / 'root'
READER_ATTEMPT = STATE / 'reader-attempt'
READER_OUTPUT = READER_ATTEMPT / 'reader-output'
CONTAINER_NAME = 'cal-reader-only-20261020-0002-successor-0001'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'


class Refused(ValueError):
    pass


def need(ok: bool, code: str) -> None:
    if not ok:
        raise Refused(code)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def frozen_selector():
    """Verify every selected predecessor byte before loading its pure selector."""
    need(sha((SELECTOR / 'freeze.json').read_bytes()) == SELECTOR_FREEZE_SHA,
         'READER_SELECTOR_FREEZE_DRIFT')
    need(sha(SELECTOR_REVIEW.read_bytes()) == SELECTOR_REVIEW_SHA,
         'READER_SELECTOR_REVIEW_DRIFT')
    freeze = json.loads((SELECTOR / 'freeze.json').read_bytes())
    need(freeze['effect_enabled'] is False and freeze['reader_effect'] == 'NOT_RUN' and
         freeze['source_effect'] == 'NOT_RUN', 'READER_SELECTOR_EFFECT_DRIFT')
    for row in freeze['file_bindings']:
        item = SELECTOR / Path(row['path']).name
        need(item.is_file() and not item.is_symlink() and
             item.stat().st_size == row['size'] and sha(item.read_bytes()) == row['sha256'],
             'READER_SELECTOR_MEMBER_DRIFT')
    spec = importlib.util.spec_from_file_location('cal_frozen_reader_successor_selector',
                                                   SELECTOR / 'adapter.py')
    need(spec is not None and spec.loader is not None, 'READER_SELECTOR_IMPORT')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select_stage(source_raw: bytes, package_raw: bytes, terminal_raw: bytes,
                 period_raw: bytes, review_raw: bytes, outside_review_sha: str,
                 now) -> dict:
    """Build exact 986-row future copy plan solely from reviewed public metadata.

    The caller must pin the independently produced Source effect review SHA
    outside this function before reading Source package bytes. This method
    neither opens nor hashes any selected file, including branch.snapshot.
    """
    a = frozen_selector()
    selected = a.select(source_raw, package_raw, terminal_raw, period_raw,
                        review_raw, outside_review_sha, now)
    source = a.parse(source_raw)
    package = a.parse(package_raw)
    reader_raw = a.encoded(selected['reader_manifest'])
    generated = {a.READER + '/' + name: raw
                 for name, raw in selected['projected_roles'].items()}
    generated[a.READER + '/source-manifest.json'] = reader_raw
    source_rows = source['files'] + package['files'] + [
        {'path': a.SOURCE + '/source-manifest.json',
         'sha256': selected['source_manifest_sha256']},
        {'path': a.SOURCE + '/packages/0001/manifest.json',
         'sha256': selected['source_package_manifest_sha256']}]
    need(len(source_rows) == len({r['path'] for r in source_rows}) == 978,
         'SOURCE_STAGE_CLOSURE')
    need(len(generated) == 8 and len(set(generated)) == 8 and
         sha(reader_raw) == selected['reader_manifest_sha256'],
         'READER_STAGE_CLOSURE')
    rows = []
    for row in source_rows:
        name = row['path']
        need(type(name) is str and not name.startswith('/') and
             all(p not in ('', '.', '..') for p in name.split('/')) and
             type(row['sha256']) is str and len(row['sha256']) == 64 and
             all(c in '0123456789abcdef' for c in row['sha256']),
             'UNSAFE_SOURCE_STAGE_ROW')
        mode = '0600' if name.startswith(a.SOURCE + '/packages/0001/') else '0444'
        rows.append({'path': name, 'sha256': row['sha256'],
                     'source_path': str(SOURCE_ROOT / name),
                     'source_mode': mode, 'target_mode': mode,
                     'source_kind': 'source-attempt'})
    for name, raw in generated.items():
        rows.append({'path': name, 'sha256': sha(raw),
                     'source_path': None, 'source_mode': None,
                     'target_mode': '0444', 'source_kind': 'generated-reader'})
    rows.sort(key=lambda r: r['path'])
    need(len(rows) == len({r['path'] for r in rows}) == 986,
         'STAGE_986_CLOSURE')
    archive = a.SOURCE + '/packages/0001/branch.snapshot'
    need(next(r for r in rows if r['path'] == archive)['sha256'] ==
         selected['source_archive_sha256'], 'ARCHIVE_STAGE_BINDING')
    plan = {'schema': 'lab-reader-successor-stage-plan/v1',
            'status': 'SELECTION_ONLY_EFFECT_DISABLED', 'effect': 'NOT_RUN',
            'archive_body_opened': False, 'no_retry': True,
            'source_attempt': selected['source_attempt'],
            'source_root': str(SOURCE_ROOT),
            'stage_attempt': str(STAGE_ATTEMPT), 'stage_root': str(STAGE_ROOT),
            'reader_attempt': str(READER_ATTEMPT),
            'reader_output': str(READER_OUTPUT),
            'container_name': CONTAINER_NAME,
            'source_manifest_sha256': selected['source_manifest_sha256'],
            'source_package_manifest_sha256': selected['source_package_manifest_sha256'],
            'source_terminal_sha256': selected['source_terminal_sha256'],
            'source_effect_review_sha256': selected['source_effect_review_sha256'],
            'source_archive_sha256': selected['source_archive_sha256'],
            'reader_manifest_sha256': selected['reader_manifest_sha256'],
            'selector_freeze_sha256': SELECTOR_FREEZE_SHA,
            'selector_review_sha256': SELECTOR_REVIEW_SHA,
            'files': rows}
    return {'status': plan['status'], 'plan': plan,
            'plan_sha256': sha(encoded(plan)),
            'generated_reader_bytes': generated, 'effect_enabled': False}


def docker_envelope(stage_dev: int, stage_ino: int, attempt_label: str) -> dict:
    """Selected sandbox envelope, intentionally lacking a runnable entrypoint."""
    need(type(stage_dev) is int and stage_dev > 0 and
         type(stage_ino) is int and stage_ino > 0 and
         type(attempt_label) is str and len(attempt_label) == 64 and
         all(c in '0123456789abcdef' for c in attempt_label),
         'UNREVIEWED_STAGE_IDENTITY')
    return {'effect': 'NOT_RUN', 'create_argv_available': False,
            'entrypoint': 'UNBOUND_NEW_READER_RELEASE_REQUIRED',
            'docker_binary': '/usr/bin/docker', 'container_name': CONTAINER_NAME,
            'attempt_label': attempt_label, 'network': 'none',
            'rootfs': 'read-only', 'capabilities': 'drop-all', 'ipc': 'private',
            'security': 'no-new-privileges', 'pids_limit': 1,
            'memory': '1g', 'cpus': 1, 'user': '1000:1000',
            'image': IMAGE, 'stage_id': f'{stage_dev}:{stage_ino}',
            'stage_bind': {'source': str(STAGE_ROOT), 'target': '/attempt/root',
                           'read_only': True},
            'output_bind': {'source': str(READER_OUTPUT),
                            'target': '/attempt/reader-output', 'read_only': False},
            'scratch_tmpfs': {'target': '/attempt/tmp', 'size': '512m',
                              'mode': '0700', 'uid': 1000, 'gid': 1000}}


def execute_stage(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_STAGE_RELEASE_REQUIRED')


def execute_reader(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_READER_RELEASE_REQUIRED')
