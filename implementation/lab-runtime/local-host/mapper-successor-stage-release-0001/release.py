"""Exact one-shot wrapper for independently PASS-reviewed Mapper stage 0002.

Construction and preflight have no private archive-copy effect. The selected
--execute-reviewed-one-shot route is reserved for a separate static review and
externally observed single dispatch; it is not called by this release's tests.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = HERE.parents[3]
STAGE = LOCAL / 'mapper-successor-stage-0002'
STAGE_FREEZE_SHA = 'c214e06c122186124a11f16e456257a1f800cfea8b05361da9d18247ece60311'
STAGE_REVIEW = LOCAL / 'MAPPER-SUCCESSOR-STAGE-INDEPENDENT-STATIC-REVIEW-0002.md'
STAGE_REVIEW_SHA = 'fad287769926dafe0a662ce9007d28b4bd90ba4523364b51a3ecd6a30974633f'
PLAN_SHA = '9041aeedc8b349f6d7315e7ac2544aabda85afdb748663010e00af25e0b9ca2e'
COPY_SHA = '76bfc24841d652cbae039d666bcde80d7899b3b978ebd0291443705543d3dd95'
VERIFIER_SHA = 'e45ba0c5ba2797b2e7ed564caa4528fbf8d79c8b1f42d95f36783ec59cf94416'
EFFECT_ENABLED = True  # candidate wrapper; separate static review before dispatch


class Refused(ValueError):
    pass


def need(ok: bool, code: str) -> None:
    if not ok:
        raise Refused(code)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _exact_module(name: str, raw: bytes, path: Path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def basis():
    freeze_raw = (STAGE / 'freeze.json').read_bytes()
    review_raw = STAGE_REVIEW.read_bytes()
    need(sha(freeze_raw) == STAGE_FREEZE_SHA and
         sha(review_raw) == STAGE_REVIEW_SHA and
         b'Verdict: **PASS' in review_raw,
         'STAGE_FREEZE_OR_PASS_REVIEW_DRIFT')
    freeze = json.loads(freeze_raw)
    need(freeze['effect_enabled'] is False and freeze['stage_effect'] == 'NOT_RUN' and
         freeze['stage_plan_sha256'] == PLAN_SHA and
         freeze['copy_plan_sha256'] == COPY_SHA and
         freeze['verifier_plan_sha256'] == VERIFIER_SHA and
         freeze['input_files'] == 991 and freeze['source_directories'] == 931 and
         freeze['target_directories'] == 933 and
         freeze['private_inventory_metadata_only_rows'] == 37 and
         len(freeze['file_bindings']) == 14,
         'STAGE_FREEZE_CONTRACT_DRIFT')
    checked = {}
    for row in freeze['file_bindings']:
        rel = Path(row['path'])
        need(not rel.is_absolute() and '..' not in rel.parts and
             rel.parts[:4] == ('implementation', 'lab-runtime', 'local-host',
                               'mapper-successor-stage-0002'),
             'STAGE_MEMBER_PATH_DRIFT')
        path = REPO / rel
        need(path.is_file() and not path.is_symlink(), 'STAGE_MEMBER_TYPE_DRIFT')
        raw = path.read_bytes()
        need(len(raw) == row['size'] and sha(raw) == row['sha256'] and
             path.stat().st_size == row['size'], 'STAGE_MEMBER_BYTES_DRIFT')
        checked[str(rel.relative_to(STAGE.relative_to(REPO)))] = raw
    need(all(name in checked for name in ('anchored_copy.py', 'held_stage.py',
                                         'stage.py')), 'STAGE_MODULE_BINDING_DRIFT')
    # Compile exact verified bytes, never a second path read or existing pyc.
    names = ('anchored_copy', 'held_stage', 'stage')
    prior = {name: sys.modules.get(name) for name in names}
    try:
        for name in names:
            module = _exact_module(name, checked[name + '.py'], STAGE / (name + '.py'))
        need(module.STAGE_EFFECT_ENABLED is False, 'STAGE_PREDECESSOR_EFFECT_DRIFT')
        return module
    finally:
        for name in names:
            sys.modules.pop(name, None)
            if prior[name] is not None:
                sys.modules[name] = prior[name]


def preflight() -> dict:
    return basis().preflight()


def execute_reviewed_one_shot() -> dict:
    stage = basis()
    stage.preflight()
    stage.STAGE_EFFECT_ENABLED = True
    try:
        return stage.execute()
    finally:
        stage.STAGE_EFFECT_ENABLED = False


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(), sort_keys=True))
    elif sys.argv[1:] == ['--execute-reviewed-one-shot']:
        print(json.dumps(execute_reviewed_one_shot(), sort_keys=True))
    else:
        raise SystemExit('expected --preflight or --execute-reviewed-one-shot')
