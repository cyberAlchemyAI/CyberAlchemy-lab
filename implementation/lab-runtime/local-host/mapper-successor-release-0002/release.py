"""Fresh Mapper stage selection. This module has no filesystem or Docker effect."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
SELECTOR = LOCAL / 'mapper-successor-recovery-0001'
SELECTOR_FREEZE_SHA = 'a927eab2573e2474f0bf5450fcfa58d6d7ab82eb220fb776af0037865e1f86a6'
SELECTOR_REVIEW = LOCAL / 'MAPPER-SUCCESSOR-RECOVERY-INDEPENDENT-STATIC-REVIEW-0001.md'
SELECTOR_REVIEW_SHA = 'f694dd458dc457d72b5ae3659a4d207277d6568f62fa8e0e2cea628b5932981e'
READER_RELEASE = LOCAL / 'reader-successor-release-0001'
READER_RELEASE_FREEZE_SHA = '9505c5b890003b087c8c9f7065cf38b4cd7f9b8d43f3f06ecdf61b69829e092c'
READER_RELEASE_REVIEW = LOCAL / 'READER-SUCCESSOR-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md'
READER_RELEASE_REVIEW_SHA = 'a593c8fbedb44c0941d578c2afb5b401f878f7d1990a1a86b4a0a788d3fd8b58'
SOURCE_REVIEW_SHA = '599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440'
STATE = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
READER_STAGE_ROOT = STATE / 'reader-stage-attempt/root'
ATTEMPT = STATE / 'mapper-attempt'
ATTEMPT_ROOT = ATTEMPT / 'root'
CONTAINER_NAME = 'cal-mapper-only-20261020-0002-successor-0001'
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


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, 'SELECTOR_IMPORT')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _frozen(directory: Path, expected_sha: str, review: Path,
            review_sha: str, binding_key: str) -> None:
    freeze_path = directory / 'freeze.json'
    need(freeze_path.is_file() and not freeze_path.is_symlink() and
         sha(freeze_path.read_bytes()) == expected_sha and
         review.is_file() and not review.is_symlink() and
         sha(review.read_bytes()) == review_sha, binding_key + '_FREEZE_OR_REVIEW_DRIFT')
    freeze = json.loads(freeze_path.read_bytes())
    need(freeze['effect_enabled'] is False, binding_key + '_EFFECT_DRIFT')
    rows = freeze.get('bindings', freeze.get('file_bindings'))
    need(type(rows) is list and len(rows) >= 3, binding_key + '_BINDINGS')
    for row in rows:
        member = directory / Path(row['path']).name
        need(member.is_file() and not member.is_symlink() and
             member.stat().st_size == row['size'] and
             sha(member.read_bytes()) == row['sha256'], binding_key + '_MEMBER_DRIFT')


def frozen_selector():
    _frozen(SELECTOR, SELECTOR_FREEZE_SHA, SELECTOR_REVIEW,
            SELECTOR_REVIEW_SHA, 'MAPPER_SELECTOR')
    return _load(SELECTOR / 'adapter.py', 'cal_frozen_mapper_selector')


def frozen_reader_release():
    _frozen(READER_RELEASE, READER_RELEASE_FREEZE_SHA,
            READER_RELEASE_REVIEW, READER_RELEASE_REVIEW_SHA, 'READER_RELEASE')
    return _load(READER_RELEASE / 'release.py', 'cal_frozen_reader_release')


def select_stage(*, source_manifest_raw: bytes, source_package_raw: bytes,
                 source_terminal_raw: bytes, period_raw: bytes,
                 source_review_raw: bytes, outside_source_review_sha: str,
                 reader_manifest_raw: bytes, reader_receipt_raw: bytes,
                 reader_terminal_raw: bytes, reader_external_raw: bytes,
                 reader_review_raw: bytes, outside_reader_review_sha: str,
                 now) -> dict:
    """Select a future exact stage from public metadata and outside review pins.

    All private bytes arrive as caller-supplied metadata. In particular this
    function never opens the protected branch.snapshot or Reader output.
    """
    need(outside_source_review_sha == SOURCE_REVIEW_SHA and
         sha(source_review_raw) == SOURCE_REVIEW_SHA, 'SOURCE_EFFECT_REVIEW_PIN')
    mapper = frozen_selector()
    reader = frozen_reader_release()
    # JSON false and 0.0 compare equal to Python integer 0. The frozen Mapper
    # selector checks equality only; reject those scalar aliases before calling it.
    external = mapper.parse(reader_external_raw)
    need(type(external) is dict and
         type(external.get('exit_code')) is int and
         external['exit_code'] == 0, 'READER_EXTERNAL_OS_INTEGER_ZERO')
    selected = mapper.select(
        source_manifest_raw=source_manifest_raw,
        source_package_raw=source_package_raw,
        source_terminal_raw=source_terminal_raw,
        period_raw=period_raw,
        source_review_raw=source_review_raw,
        outside_source_review_sha=outside_source_review_sha,
        reader_manifest_raw=reader_manifest_raw,
        reader_receipt_raw=reader_receipt_raw,
        reader_terminal_raw=reader_terminal_raw,
        reader_external_raw=reader_external_raw,
        reader_review_raw=reader_review_raw,
        outside_reader_review_sha=outside_reader_review_sha,
        now=now)
    predecessor = reader.select_stage(
        source_manifest_raw, source_package_raw, source_terminal_raw,
        period_raw, source_review_raw, outside_source_review_sha, now)
    reader_plan = predecessor['plan']
    need(reader_plan['reader_manifest_sha256'] == selected['reader_manifest_sha256'] and
         reader_plan['stage_root'] == str(READER_STAGE_ROOT) and
         len(reader_plan['files']) == 986 and
         selected['output_contract']['effect_verifier_adapted'] is False and
         selected['output_contract']['native_sha256'] == mapper.NATIVE_SHA and
         len(selected['expected_package_members']) == 55,
         'READER_STAGE_OR_OUTPUT_JOIN')
    mapper_raw = mapper.encoded(selected['mapper_manifest'])
    generated = {mapper.MAPPER + '/' + name: raw
                 for name, raw in selected['projected_roles'].items()}
    generated[mapper.MAPPER + '/source-manifest.json'] = mapper_raw
    need(len(generated) == 5 and
         sha(mapper_raw) == selected['mapper_manifest_sha256'],
         'MAPPER_PROJECTION_CLOSURE')
    rows = []
    for row in reader_plan['files']:
        name = row['path']
        need(type(name) is str and not name.startswith('/') and
             all(p not in ('', '.', '..') for p in name.split('/')) and
             row['source_kind'] in ('source-attempt', 'generated-reader') and
             row['target_mode'] in ('0444', '0600') and
             type(row['sha256']) is str and len(row['sha256']) == 64,
             'UNSAFE_READER_STAGE_ROW')
        rows.append({'path': name, 'sha256': row['sha256'],
                     'source_path': str(READER_STAGE_ROOT / name),
                     'source_mode': row['target_mode'],
                     'target_mode': row['target_mode'],
                     'source_kind': 'reviewed-reader-stage'})
    for name, raw in generated.items():
        rows.append({'path': name, 'sha256': sha(raw),
                     'source_path': None, 'source_mode': None,
                     'target_mode': '0444', 'source_kind': 'generated-mapper'})
    rows.sort(key=lambda row: row['path'])
    need(len(rows) == len({row['path'] for row in rows}) == 991 and
         all(row['sha256'] == sha(generated[row['path']])
             for row in rows if row['source_kind'] == 'generated-mapper'),
         'MAPPER_STAGE_991_CLOSURE')
    plan = {
        'schema': 'lab-mapper-successor-stage-plan/v1',
        'status': 'SELECTION_ONLY_EFFECT_DISABLED', 'effect': 'NOT_RUN',
        'archive_body_opened': False, 'no_retry': True,
        'reader_stage_root': str(READER_STAGE_ROOT),
        'mapper_attempt': str(ATTEMPT), 'mapper_root': str(ATTEMPT_ROOT),
        'container_name': CONTAINER_NAME, 'image': IMAGE,
        'source_effect_review_sha256': SOURCE_REVIEW_SHA,
        'reader_effect_review_sha256': outside_reader_review_sha,
        'reader_stage_plan_sha256': predecessor['plan_sha256'],
        'source_package_manifest_sha256': selected['source_package_manifest_sha256'],
        'reader_manifest_sha256': selected['reader_manifest_sha256'],
        'mapper_manifest_sha256': selected['mapper_manifest_sha256'],
        'native_sha256': selected['output_contract']['native_sha256'],
        'verifier_template_sha256': selected['output_contract']['template_sha256'],
        'expected_package_members': list(selected['expected_package_members']),
        'output_acceptance_contract': {
            'verifier_rebound': False,
            'leaf_count': 55, 'semantic_leaves': 25, 'governance_leaves': 25,
            'node_count': 15, 'edge_count': 10, 'exact_governance_joins': 25,
            'native_seal_processes': 2, 'actual_cold_native_read_processes': 2,
            'cold_native_replay_byte_parity': True,
            'same_signed_source_cut': True,
            'native_domain_mapping_supplied': True,
            'context_or_ontology_view_carriers_generated': False,
            'authority_effect': 'none', 'actual_owner_outcome': None,
            'task_complete': False},
        'selector_freeze_sha256': SELECTOR_FREEZE_SHA,
        'selector_review_sha256': SELECTOR_REVIEW_SHA,
        'files': rows,
    }
    return {'status': plan['status'], 'plan': plan,
            'plan_sha256': sha(encoded(plan)), 'generated_mapper_bytes': generated,
            'output_contract': selected['output_contract'],
            'effect_enabled': False}


def docker_envelope(stage_dev: int, stage_ino: int, attempt_label: str) -> dict:
    """Describe the selected confinement; emit no executable Docker argv."""
    need(type(stage_dev) is int and stage_dev > 0 and
         type(stage_ino) is int and stage_ino > 0 and
         type(attempt_label) is str and len(attempt_label) == 64 and
         all(c in '0123456789abcdef' for c in attempt_label),
         'UNREVIEWED_STAGE_IDENTITY')
    mapper = frozen_selector()
    return {'effect': 'NOT_RUN', 'create_argv_available': False,
            'entrypoint': 'UNBOUND_NEW_MAPPER_RELEASE_REQUIRED',
            'docker_binary': '/usr/bin/docker', 'container_name': CONTAINER_NAME,
            'attempt_label': attempt_label, 'stage_id': f'{stage_dev}:{stage_ino}',
            'image': IMAGE, 'network': 'none', 'rootfs': 'read-only',
            'capabilities': 'drop-all', 'security': 'no-new-privileges',
            'pids_limit': 16, 'memory': '1g', 'cpus': 1,
            'user': '1000:1000', 'userns': 'host',
            'root_bind': {'source': str(ATTEMPT_ROOT), 'target': '/workspace',
                          'read_only': True},
            'package_bind': {'source': str(ATTEMPT_ROOT / mapper.MAPPER / 'packages'),
                             'target': '/workspace/' + mapper.MAPPER + '/packages',
                             'read_only': False, 'must_be_empty_0700': True},
            'native_bind': {'source': str(ATTEMPT / 'input'),
                            'target': '/attempt/input', 'read_only': True,
                            'executable_sha256': mapper.NATIVE_SHA},
            'scratch_tmpfs': {'target': '/attempt/scratch', 'size': '512m',
                              'mode': '0700', 'uid': 1000, 'gid': 1000}}


def execute_stage(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_MAPPER_STAGE_RELEASE_REQUIRED')


def execute_mapper(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_MAPPER_RELEASE_REQUIRED')
