"""Exact one-shot release for independently reviewed Reader stage 0001."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = HERE.parents[3]
STAGE = LOCAL / 'reader-successor-stage-0001'
STAGE_FREEZE_SHA = '1487f1b37d1ce05b45acd9692b4878d5b3f5d78f8046e958942ae62dba9eaf20'
STAGE_REVIEW = LOCAL / 'READER-SUCCESSOR-STAGE-INDEPENDENT-STATIC-REVIEW-0001.md'
STAGE_REVIEW_SHA = '5824eb5ffe42da97a28cd364a26e7f58e1a87e313a7206d27c3a60fd2e4667e1'
PLAN_SHA = 'a5ee5e9812c4ab5d0e37b7fe99aec4f334dcb583668ad0489f267f7e2258478b'
SELECTION_SHA = '0891c30ec2af6017233d0ec17ce8b4ae167f9f588eb333a91c0f37a268b7c582'


class Refused(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(ok: bool, code: str) -> None:
    if not ok:
        raise Refused(code)


def basis():
    raw = (STAGE / 'freeze.json').read_bytes()
    need(sha(raw) == STAGE_FREEZE_SHA and sha(STAGE_REVIEW.read_bytes()) == STAGE_REVIEW_SHA,
         'STAGE_REVIEW_OR_FREEZE_DRIFT')
    freeze = json.loads(raw)
    need(freeze['effect_enabled'] is False and freeze['stage_effect'] == 'NOT_RUN' and
         freeze['stage_plan_sha256'] == PLAN_SHA and
         freeze['selection_sha256'] == SELECTION_SHA and
         len(freeze['file_bindings']) == 14,
         'STAGE_FREEZE_CONTRACT')
    for row in freeze['file_bindings']:
        item = REPO / row['path']
        need(item.is_file() and not item.is_symlink() and
             item.stat().st_size == row['size'] and sha(item.read_bytes()) == row['sha256'],
             'STAGE_FROZEN_MEMBER_DRIFT')
    sys.path.insert(0, str(STAGE))
    spec = importlib.util.spec_from_file_location('cal_reviewed_reader_stage', STAGE / 'stage.py')
    need(spec is not None and spec.loader is not None, 'STAGE_IMPORT')
    module = importlib.util.module_from_spec(spec)
    # The wrapper itself is named release when imported by unittest. Let the
    # reviewed stage import its own pinned predecessor named release.
    prior = {name: sys.modules.pop(name, None) for name in ('release', 'anchored_copy')}
    try:
        spec.loader.exec_module(module)
    finally:
        for name, previous in prior.items():
            sys.modules.pop(name, None)
            if previous is not None:
                sys.modules[name] = previous
    need(module.STAGE_RELEASE_ENABLED is False, 'STAGE_PREDECESSOR_EFFECT_DRIFT')
    return module


def preflight() -> dict:
    s = basis()
    return s.preflight()


def execute() -> dict:
    s = basis()
    s.preflight()
    s.STAGE_RELEASE_ENABLED = True
    try:
        return s.execute()
    finally:
        s.STAGE_RELEASE_ENABLED = False


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(), sort_keys=True))
    elif sys.argv[1:] == ['--execute-reviewed-one-shot']:
        print(json.dumps(execute(), sort_keys=True))
    else:
        raise SystemExit('expected --preflight or --execute-reviewed-one-shot')
