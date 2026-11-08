"""Exact proposed Reader Docker launch envelope; dispatch is hard-disabled.

The Source 0006 controller is a lifecycle reference, not a release inherited by
this Reader candidate. A reviewed successor must add durable one-shot daemon
control and postclose checks before enabling any command below.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ATTEMPT = Path('/tmp/cal-reader-only-dev-20261020-0001-exact1')
ROOT = ATTEMPT / 'root'
OUTPUT = ATTEMPT / 'reader-output'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
DOCKER = '/usr/bin/docker'
NAME = 'cal-reader-only-20261020-0001-0001'
LABEL = 'cal.reader.attempt=20261020-0001-0001'


def create_argv() -> list[str]:
    return [DOCKER, 'create', '--name', NAME, '--label', LABEL,
            '--network', 'none', '--read-only', '--cap-drop', 'ALL',
            '--security-opt', 'no-new-privileges:true', '--pids-limit', '64',
            '--memory', '1g', '--cpus', '1', '--user', '1000:1000',
            '--mount', f'type=bind,src={ROOT},dst=/attempt/root,readonly',
            '--mount', f'type=bind,src={OUTPUT},dst=/attempt/reader-output',
            '--mount', f'type=bind,src={HERE},dst=/tool,readonly',
            '--tmpfs', '/attempt/tmp:rw,nosuid,nodev,size=512m,mode=1777',
            '--tmpfs', '/tmp:rw,nosuid,nodev,size=256m,mode=1777',
            IMAGE, 'python', '-B', '/tool/reader_once.py', '--execute-reviewed-one-shot']


def contract() -> dict:
    return {'schema_version': 'lab-fresh-reader-controller-contract/v1-inactive',
            'effect': 'NOT_RUN', 'create_argv': create_argv(),
            'source_attempt': '/tmp/cal-source-only-dev-20261020-0001-exact1',
            'reader_attempt': str(ATTEMPT), 'selected_container_name': NAME,
            'must_have_before_create': ['independent static review PASS',
                'separate Reader stage and exact 986-file inventory',
                'current Source episode before create',
                'fresh output/evidence/consumed marker/container name',
                'selected Docker and image IDs, UID/GID, read-only input mount',
                'owned tmpfs capacity and output mount'],
            'required_one_shot_lifecycle': ['durable consumed marker before create',
                'unique container CID/name/label', 'bounded full stdout/stderr',
                'daemon exit plus pre-removal inspect persisted',
                'stop/kill only verified owned CID on timeout or signal',
                'daemon-side absence after cleanup',
                'postclose 986-file input and one-receipt output inventory',
                'source period checked again immediately before PASS terminal',
                'UNKNOWN on ambiguity; no retry'],
            'effect_enabled': False,
            'claim_ceiling': 'Controller contract only; no Reader cold-open or Docker effect.'}


if __name__ == '__main__':
    if sys.argv[1:] == ['--show-contract']:
        print(json.dumps(contract(), sort_keys=True))
    else:
        raise SystemExit('Reader Docker dispatch disabled pending independent review')
