"""Read-only Source/Reader evidence joins; no archive, Mapper, or Context effect."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import stat
from pathlib import Path

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
ENV = {'python': '3.14.4', 'jsonschema': '4.23.0', 'cryptography': '46.0.5'}
SELECTION_SHA = '16b46adf47f2f5c1482de4bd23597b32f49185d9c02d9e8d6a5dbdcaba78ae65'
LIMIT = 2 * 1024 * 1024

# The selector is a local, frozen admission input. These path names are the
# complete metadata allowlist, checked before opening any selected target.
EXPECTED_PATHS = {
    'context_constructor': {
        'freeze_path': 'implementation/lab-runtime/local-host/context-construction-0003/freeze.json',
        'review_path': 'implementation/lab-runtime/local-host/CONTEXT-CONSTRUCTION-INDEPENDENT-STATIC-REVIEW-0003.md',
        'rendered_build_path': 'implementation/lab-runtime/local-host/context-construction-0003/rendered/build.py',
    },
    'source': {
        'source_manifest_path': '/tmp/cal-source-only-dev-20261020-0001-exact1/root/product/lab/release-candidates/v1/interface/docker-source-20261020-0001/source-manifest.json',
        'package_manifest_path': '/tmp/cal-source-only-dev-20261020-0001-exact1/root/product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/manifest.json',
        'period_path': '/tmp/cal-source-only-dev-20261020-0001-exact1/root/product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/period.json',
        'effect_review_path': 'implementation/lab-runtime/local-host/SOURCE-ONLY-DOCKER-INDEPENDENT-EFFECT-REVIEW-0006.md',
    },
    'reader': {
        'source_manifest_path': '/tmp/cal-reader-stage-20261020-0001-0008/root/product/lab/release-candidates/v1/interface/docker-reader-20261020-0001/source-manifest.json',
        'reader_code_path': '/tmp/cal-reader-stage-20261020-0001-0008/root/product/lab/release-candidates/v1/interface/docker-reader-20261020-0001/reader.py',
        'receipt_path': '/tmp/cal-reader-only-dev-20261020-0001-unified6/reader-output/receipt.json',
        'effect_review_path': 'implementation/lab-runtime/local-host/READER-ONLY-UNIFIED-INDEPENDENT-EFFECT-REVIEW-0006.md',
    },
}
EXPECTED_TOP_KEYS = frozenset({
    'schema_version', 'status', 'authority_effect', 'actual_owner_outcome',
    'context_constructor', 'source', 'reader', 'mapper_package',
    'context_source_manifest', 'context_launch_enabled', 'protected_archive_body_read',
})


class Refused(ValueError):
    pass


def require(value, reason):
    if not value:
        raise Refused(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_exact(path: Path, pin: str) -> bytes:
    require(type(pin) is str and len(pin) == 64 and all(c in '0123456789abcdef' for c in pin),
            'exact SHA-256 pin required')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and 0 <= info.st_size <= LIMIT,
                'selected metadata must be a bounded regular file')
        parts = []
        total = 0
        while True:
            # At most one byte beyond the opening size can be read. Growth is
            # rejected before a chunk is retained, including for a zero-size
            # file that grows while the descriptor is held.
            chunk = os.read(fd, min(1024 * 1024, info.st_size + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            require(total <= info.st_size, 'selected metadata grew during bounded read')
            parts.append(chunk)
        final = os.fstat(fd)
        require((final.st_dev, final.st_ino, final.st_mode, final.st_nlink, final.st_size) ==
                (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size),
                'selected metadata identity or size changed')
        raw = b''.join(parts)
        require(total == info.st_size and sha(raw) == pin, 'selected metadata bytes changed')
        return raw
    finally:
        os.close(fd)


def selection():
    selected = json.loads(read_exact(HERE / 'selection.json', SELECTION_SHA))
    require(type(selected) is dict and set(selected) == EXPECTED_TOP_KEYS,
            'closed selection schema differs')
    require(selected['schema_version'] == 'lab-context-inert-integration-selection/v2' and
            selected['status'] == 'CONSTRUCTION_ONLY' and
            selected['authority_effect'] == 'none' and
            selected['actual_owner_outcome'] is None and
            selected['mapper_package'] is None and
            selected['context_source_manifest'] is None and
            selected['context_launch_enabled'] is False and
            selected['protected_archive_body_read'] is False,
            'effect-disabled selection differs')
    for role, paths in EXPECTED_PATHS.items():
        group = selected[role]
        require(type(group) is dict, 'selected role shape differs')
        expected_keys = set(paths) | {name.removesuffix('_path') + '_sha256' for name in paths}
        if role == 'reader':
            expected_keys.add('entrypoint')
        require(set(group) == expected_keys, 'closed selected role schema differs')
        for name, expected in paths.items():
            require(type(group[name]) is str and group[name] == expected and
                    Path(expected).name in {'freeze.json', 'build.py', 'source-manifest.json',
                                            'manifest.json', 'period.json', 'reader.py', 'receipt.json',
                                            'CONTEXT-CONSTRUCTION-INDEPENDENT-STATIC-REVIEW-0003.md',
                                            'SOURCE-ONLY-DOCKER-INDEPENDENT-EFFECT-REVIEW-0006.md',
                                            'READER-ONLY-UNIFIED-INDEPENDENT-EFFECT-REVIEW-0006.md'},
                    'selected metadata path differs from allowlist')
            pin = group[name.removesuffix('_path') + '_sha256']
            require(type(pin) is str and len(pin) == 64 and
                    all(c in '0123456789abcdef' for c in pin), 'selected digest shape differs')
    require(selected['reader']['entrypoint'] == 'SelectedReader.open_signed',
            'selected Reader entrypoint differs')
    return selected


def _repo_path(value):
    path = Path(value)
    require(not path.is_absolute() and '..' not in path.parts, 'repository evidence path differs')
    return REPO / path


def verify(now: dt.datetime | None = None):
    selected = selection()
    require(selected['schema_version'] == 'lab-context-inert-integration-selection/v2' and
            selected['status'] == 'CONSTRUCTION_ONLY' and
            selected['authority_effect'] == 'none' and selected['actual_owner_outcome'] is None and
            selected['mapper_package'] is None and selected['context_source_manifest'] is None and
            selected['context_launch_enabled'] is False and
            selected['protected_archive_body_read'] is False,
            'effect-disabled selection differs')
    context = selected['context_constructor']
    freeze = json.loads(read_exact(_repo_path(context['freeze_path']), context['freeze_sha256']))
    require(freeze['status'] == 'FROZEN_PROVISIONAL_EFFECT_DISABLED' and
            freeze['source_manifest_status'] == 'REFUSED' and freeze['effect'] == 'NOT_RUN',
            'reviewed constructor ceiling differs')
    root = _repo_path(context['freeze_path']).parent
    for row in freeze['files']:
        raw = read_exact(root / row['path'], row['sha256'])
        require(len(raw) == row['size'], 'constructor frozen member size changed')
    read_exact(_repo_path(context['review_path']), context['review_sha256'])
    read_exact(_repo_path(context['rendered_build_path']), context['rendered_build_sha256'])
    source, reader = selected['source'], selected['reader']
    for group, names in [(source, ('source_manifest', 'package_manifest', 'period')),
                         (reader, ('source_manifest', 'reader_code', 'receipt'))]:
        for name in names:
            read_exact(Path(group[name + '_path']), group[name + '_sha256'])
        read_exact(_repo_path(group['effect_review_path']), group['effect_review_sha256'])
    sm = json.loads(read_exact(Path(source['source_manifest_path']), source['source_manifest_sha256']))
    sp = json.loads(read_exact(Path(source['package_manifest_path']), source['package_manifest_sha256']))
    period = json.loads(read_exact(Path(source['period_path']), source['period_sha256']))
    rm = json.loads(read_exact(Path(reader['source_manifest_path']), reader['source_manifest_sha256']))
    rr = json.loads(read_exact(Path(reader['receipt_path']), reader['receipt_sha256']))
    require(all(v['authority_effect'] == 'none' and v['actual_owner_outcome'] is None
                for v in (sm, sp, period, rm, rr)), 'selected development posture differs')
    require(sm['environment'] == ENV and rm['environment'] == ENV and
            sp['source_manifest_binding']['sha256'] == source['source_manifest_sha256'] and
            rm['producer_source_binding']['sha256'] == source['source_manifest_sha256'] and
            rm['producer_package_binding']['sha256'] == source['package_manifest_sha256'] and
            rr['source_manifest_sha256'] == source['source_manifest_sha256'] and
            rr['source_package_manifest_sha256'] == source['package_manifest_sha256'] and
            rr['reader_manifest_sha256'] == reader['source_manifest_sha256'] and
            rr['schema_version'] == 'lab-disposable-reader-receipt/v1-private',
            'Source/Reader joins differ')
    if now is None:
        now = dt.datetime.now(dt.timezone.utc)
    require(type(now) is dt.datetime and now.tzinfo is not None, 'aware UTC observation required')
    start = dt.datetime.fromisoformat(period['not_before'])
    end = dt.datetime.fromisoformat(period['expires_at'])
    require(start <= now < end, 'selected Source period is not current')
    return {
        'status': 'SOURCE_READER_METADATA_JOIN_PASS', 'observed_at': now.isoformat(),
        'period_expires_at': end.isoformat(), 'source_manifest_sha256': source['source_manifest_sha256'],
        'source_package_sha256': source['package_manifest_sha256'],
        'reader_manifest_sha256': reader['source_manifest_sha256'],
        'reader_receipt_sha256': reader['receipt_sha256'],
        'reader_entrypoint_candidate': {'code_sha256': reader['reader_code_sha256'],
                                        'entrypoint': reader['entrypoint'],
                                        'status': 'REQUIRES_SAME_FAMILY_PROJECTION'},
        'development_authorization': 'UNSELECTED', 'control_AUTH_projection': 'UNSELECTED',
        'mapper_package': 'UNSELECTED', 'context_source_manifest': 'REFUSED',
        'context_launch': 'REFUSED', 'archive_body_read': False,
    }


def final_context_source_manifest(*_args, **_kwargs):
    raise Refused('fresh reviewed same-family Mapper package and complete Context closure required')


def launch_context(*_args, **_kwargs):
    raise Refused('effect-disabled construction; no final Context source manifest or launch')
