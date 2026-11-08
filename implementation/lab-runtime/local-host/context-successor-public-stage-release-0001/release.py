"""One-shot Context stage-only wrapper; frozen static review required before use.

The production effect entrypoint is deliberately absent from tests. It executes
only the checked stage-writer source bytes after a current read-only preflight.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
STAGE = LOCAL / 'context-successor-public-stage-writer-0002'
STAGE_FREEZE_SHA = '8a49c612931a277485ce3a17fc5c89ac81020c2aa9e556ca46ba65e21c73c742'
STAGE_CODE_SHA = '9228b7aa394a661c1c43513bd754fe4f2bf7e37c8f2dbd834d0c85b5805805bb'
REVIEW = LOCAL / 'context-successor-stage-writer-independent-review-0002/review.json'
REVIEW_SHA = '321ee97a01d0c87539717dc48b8a514bbf9fe440bb96caa6e4c7daabaf492759'
REVIEW_MD = LOCAL / 'CONTEXT-SUCCESSOR-STAGE-WRITER-INDEPENDENT-STATIC-REVIEW-0002.md'
REVIEW_MD_SHA = 'bfbff86e55ceaef84721834d54816a4e8ac7b92970e2a090a5ecbe07e8be2e00'
ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/context-attempt')
SOURCE_PERIOD_SHA = '3ff862090a38b346a384001c2d87da7cf648f18726fb056653a0fb4df40473ba'
EFFECT_ENABLED = True  # candidate route, independently review before one dispatch
# The pinned JIT selector imports the distribution-owned cryptography package.
DIST_PACKAGES = '/usr/lib/python3/dist-packages'
READ_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


class Refused(RuntimeError):
    pass


def need(condition, code):
    if not condition:
        raise Refused(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _close_all(fds, primary=None):
    errors = []
    for fd in reversed(fds):
        try:
            os.close(fd)
        except BaseException as exc:
            errors.append(exc)
    if errors and primary is None:
        raise BaseExceptionGroup('owned close failure', errors)
    if errors:
        primary.add_note('secondary owned descriptor close failure')


def pinned(path, expected, maximum=2*1024*1024):
    """One bounded nofollow read; never import a second pathname buffer."""
    path = Path(path)
    need(path.is_absolute() and path.is_relative_to(LOCAL), 'PUBLIC_PIN_PATH')
    fds = []
    primary = None
    try:
        fds.append(os.open('/', DIR_FLAGS))
        for part in path.parts[1:-1]:
            fds.append(os.open(part, DIR_FLAGS, dir_fd=fds[-1]))
        parents = tuple((os.fstat(fd).st_dev, os.fstat(fd).st_ino) for fd in fds)
        fds.append(os.open(path.name, READ_FLAGS, dir_fd=fds[-1]))
        fd = fds[-1]
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             0 < before.st_size <= maximum, 'PIN_SHAPE')
        raw = bytearray()
        while len(raw) <= before.st_size:
            block = os.read(fd, min(65536, before.st_size+1-len(raw)))
            if not block:
                break
            raw.extend(block)
        after = os.fstat(fd)
        named = os.stat(path.name, dir_fd=fds[-2], follow_symlinks=False)
        def leaf(st):
            return (st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid,
                    st.st_nlink, st.st_size)
        need(len(raw) == before.st_size and leaf(before) == leaf(after) == leaf(named) and
             sha(raw) == expected, 'PIN_BYTES_OR_ID')
        for index, part in enumerate(path.parts[1:-1], 1):
            named_parent = os.stat(part, dir_fd=fds[index-1], follow_symlinks=False)
            need((named_parent.st_dev, named_parent.st_ino) == parents[index],
                 'PIN_PARENT_DETACHED')
        return bytes(raw)
    except BaseException as exc:
        primary = exc
        raise
    finally:
        _close_all(fds, primary)


def _module(raw):
    module = types.ModuleType('checked_context_stage_writer_0002')
    module.__file__ = str(STAGE/'stage_writer.py')
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def basis():
    need(Path(DIST_PACKAGES).is_dir(), 'DISTRIBUTION_DEPENDENCY_ABSENT')
    if DIST_PACKAGES not in sys.path:
        sys.path.insert(0, DIST_PACKAGES)
    freeze = json.loads(pinned(STAGE/'freeze.json', STAGE_FREEZE_SHA))
    review = json.loads(pinned(REVIEW, REVIEW_SHA))
    pinned(REVIEW_MD, REVIEW_MD_SHA)
    need(freeze['schema'] == 'context-successor-public-stage-writer-freeze/v1' and
         freeze['effect_enabled'] is False and freeze['stage_effect'] == 'UNRUN' and
         freeze['bound_rows'] == 1570 and freeze['directories'] == 1021 and
         freeze['auth'] == 'UNMINTED_UNSELECTED' and
         freeze['members']['stage_writer.py'] == STAGE_CODE_SHA and
         review['schema'] == 'context-successor-stage-writer-independent-static-review/v1' and
         review['verdict'] == 'PASS_BOUNDED_STATIC_STAGE_WRITER_ONLY' and
         review['candidate_freeze_sha256'] == STAGE_FREEZE_SHA and
         review['candidate_effect_enabled'] is False and
         review['real_stage_effect'] == 'UNRUN' and
         review['production_attempt_absent'] is True and
         review['protected_archive_body'] == 'UNOPENED' and
         review['mapped_package_buffers_opened'] == 55 and
         review['selected_rows'] == 1570 and review['selected_directories'] == 1021 and
         review['review_md_sha256'] == REVIEW_MD_SHA,
         'REVIEWED_STAGE_CONTRACT')
    checked = {name:pinned(STAGE/name, digest)
               for name,digest in freeze['members'].items()}
    stage = _module(checked['stage_writer.py'])
    need(stage.EFFECT_ENABLED is False and stage.ATTEMPT == ATTEMPT and
         stage.SELECTOR_FREEZE_SHA == freeze['selector_freeze_sha256'] and
         stage.SELECTOR_REVIEW_SHA == freeze['selector_review_sha256'],
         'CHECKED_STAGE_BINDING')
    return stage


def _strict_preflight(stage):
    result = stage.preflight()
    need(type(result) is dict and
         result['status'] == 'EFFECT_DISABLED_READY_FOR_INDEPENDENT_STATIC_REVIEW' and
         result['effect'] == 'NOT_RUN' and result['attempt'] == str(ATTEMPT) and
         result['stage_root'] == str(ATTEMPT/'root') and
         type(result['rows']) is int and result['rows'] == 1570 and
         type(result['directories']) is int and result['directories'] == 1021 and
         result['auth'] == 'UNMINTED_UNSELECTED' and
         result['source_period_sha256'] == SOURCE_PERIOD_SHA and
         result['selector_freeze_sha256'] == stage.SELECTOR_FREEZE_SHA and
         result['selector_review_sha256'] == stage.SELECTOR_REVIEW_SHA and
         result['selection_reads']['mapped_package_buffers'] == 55 and
         result['selection_reads']['protected_source_archive_body'] == 'UNOPENED' and
         not os.path.lexists(ATTEMPT), 'CURRENT_STAGE_PREFLIGHT')
    return result


def preflight():
    return _strict_preflight(basis())


def execute_reviewed_one_shot():
    need(EFFECT_ENABLED is True, 'RELEASE_EFFECT_DISABLED')
    stage = basis()
    selected = _strict_preflight(stage)
    need(stage.EFFECT_ENABLED is False, 'STAGE_PREDECESSOR_EFFECT_DRIFT')
    stage.EFFECT_ENABLED = True
    try:
        result = stage.run_effect()
        need(type(result) is dict and
             result['status'] == 'PROVISIONAL_STAGE_ONLY_EXTERNAL_OS_REVIEW_REQUIRED' and
             type(result['files']) is int and result['files'] == 1570 and
             type(result['directories']) is int and result['directories'] == 1021 and
             result['attempt'] == selected['attempt'] and
             result['retry_allowed'] is False,
             'PROVISIONAL_STAGE_RESULT')
        return result
    finally:
        stage.EFFECT_ENABLED = False


def issue_authority(*_args, **_kwargs):
    raise Refused('AUTH_AND_GRANTS_DISABLED')


def jit_or_docker(*_args, **_kwargs):
    raise Refused('JIT_AND_DOCKER_DISABLED')


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(), sort_keys=True, separators=(',', ':')))
    elif sys.argv[1:] == ['--execute-reviewed-one-shot']:
        print(json.dumps(execute_reviewed_one_shot(), sort_keys=True, separators=(',', ':')))
    else:
        raise SystemExit('expected --preflight or --execute-reviewed-one-shot')
