"""Read-only successor cut after volatile /tmp loss.

This selects a new persistent host namespace and verifies the public Source
rebuild recipe. It never copies inputs, opens a branch.snapshot body, imports
Source/Reader/Mapper/Context, or creates a Docker object.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
import stat
from pathlib import Path

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
LOCAL = REPO / 'implementation/lab-runtime/local-host'
RECIPE = Path(__file__).resolve().parent
PUBLIC_CUT = RECIPE / 'public-cut.json'
PREPARE = RECIPE / 'prepare_successor.py'
SOURCE_ROLE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
OLD_ATTEMPTS = (
    Path('/tmp/cal-source-only-dev-20261020-0001-exact1'),
    Path('/tmp/cal-reader-only-dev-20261020-0001-unified6'),
    Path('/tmp/cal-mapper-only-dev-20261020-0001-release3'),
    Path('/tmp/cal-context-family-20261020-0001'),
)
PERSISTENT_PARENT = Path('/home/vlad_/.local/state')
PERSISTENT_FAMILY = PERSISTENT_PARENT / 'cyberalchemy-lab/context-successor-20261020-0001'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'


class Refused(RuntimeError):
    pass


def need(ok, why):
    if not ok:
        raise Refused(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected_period(plan, now):
    need(type(now) is dt.datetime and now.tzinfo is not None and
         now.utcoffset() == dt.timedelta(), 'UTC time required')
    start = dt.datetime.fromisoformat(plan['not_before'])
    end = dt.datetime.fromisoformat(plan['expires_at'])
    need(start <= now < end and end - start == dt.timedelta(hours=24),
         'old public Source recipe is no longer current')
    return end


def public_recipe():
    """Run only the recipe's in-memory public cut; private bodies are excluded."""
    need(PREPARE.is_file() and PUBLIC_CUT.is_file(), 'public recipe missing')
    spec = importlib.util.spec_from_file_location('_cal_successor_public_recipe', PREPARE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    plan, generated, constructed_raw = module.construct()
    raw = PUBLIC_CUT.read_bytes()
    need(raw == constructed_raw and plan == json.loads(raw),
         'public cut differs from read-only reconstruction')
    need(len(plan['public_inputs']) == 933 and len(plan['generated_bindings']) == 8 and
         len(generated) == 8 and len(plan['public_inputs']) + len(generated) == 941,
         'Source public stage count differs')
    need(plan['effect'] == 'NOT_RUN' and
         all(not row['path'].endswith('/branch.snapshot') for row in
             plan['public_inputs'] + plan['generated_bindings']),
         'private body selected by public recipe')
    for row in plan['generated_bindings']:
        need(sha(generated[row['path']]) == row['sha256'],
             'generated public binding changed')
        need((RECIPE / 'generated' / row['path']).read_bytes() == generated[row['path']],
             'materialized public generated file changed')
    return plan, sha(raw)


def persistent_destination():
    """Check the persistent ancestor and freshness without creating anything."""
    parent = PERSISTENT_PARENT
    info = os.lstat(parent)
    need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() == os.geteuid() and
         info.st_gid == os.getgid() == os.getegid(), 'persistent parent custody')
    need(not PERSISTENT_FAMILY.exists() and not PERSISTENT_FAMILY.is_symlink(),
         'successor family name is occupied')
    need(not PERSISTENT_FAMILY.is_relative_to(REPO) and
         not PERSISTENT_FAMILY.is_relative_to(Path('/tmp')),
         'persistent family must be outside repository and volatile tmpfs')
    return str(PERSISTENT_FAMILY)


def probe(now=None):
    plan, cut_sha = public_recipe()
    end = selected_period(plan, now or dt.datetime.now(dt.timezone.utc))
    destination = persistent_destination()
    states = {str(p): 'PRESENT' if p.exists() or p.is_symlink() else 'ABSENT'
              for p in OLD_ATTEMPTS}
    need(all(v == 'ABSENT' for v in states.values()),
         'historical attempt unexpectedly present; inspect, do not overwrite')
    return {
        'schema': 'context-successor-recovery-probe/v1',
        'status': 'PUBLIC_SOURCE_REBUILD_PREPARED_ONLY',
        'persistent_destination': destination,
        'old_attempts': states,
        'public_cut_sha256': cut_sha,
        'public_stage_files': 941,
        'source_role': SOURCE_ROLE,
        'source_period_expires_at': end.isoformat(),
        'selected_image': IMAGE,
        'private_archive_recovered': False,
        'source_effect': 'NOT_RUN',
        'reader_mapper_context_effect': 'NOT_RUN',
        'old_package_pins_reusable': False,
        'claim_ceiling': 'Read-only public Source rebuild preflight; no live successor family.',
    }


if __name__ == '__main__':
    print(json.dumps(probe(), sort_keys=True))
