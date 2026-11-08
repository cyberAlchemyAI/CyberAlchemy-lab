"""Exact-byte, one-shot original Mapper Docker release wrapper.

The wrapper is an effect-capable candidate for separate static review. Tests
call only preflight and inert fakes. A human-owned external observer dispatches
the selected command once after independent release review.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = HERE.parents[3]
CONTROLLER = LOCAL / 'mapper-successor-docker-controller-0002'
CONTROLLER_FREEZE_SHA = '4cac02ffa93511633ccdd45f2b0562069225f0e6e7530399ef88f5d2e692da2b'
CONTROLLER_REVIEW = LOCAL / 'MAPPER-SUCCESSOR-DOCKER-CONTROLLER-INDEPENDENT-STATIC-REVIEW-0002.md'
CONTROLLER_REVIEW_SHA = '253503d80afaf0d6af0caa2411f38acc96d50fc8b54e70b85dc7efebd84c7bd9'
STAGE_EFFECT_REVIEW_SHA = 'bae85fada28780b6bcc88082d2436082402d8acfc25b420328c79df6d2f07406'
ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/mapper-attempt/docker-attempt')
CONTAINER_NAME = 'cal-mapper-only-20261020-0002-successor-0001'
MODULE_NAMES = ('anchored_copy', 'held_stage', 'docker_protocol',
                'output_verifier', 'root_guard', 'controller')
BOUND_NAMES = ('anchored_copy.py', 'controller.py', 'docker_protocol.py',
               'held_stage.py', 'mapper_once.py', 'output_verifier.py',
               'root_guard.py', 'tests.py', 'HANDOFF.md')
EFFECT_ENABLED = True  # separate static review and external one-shot dispatch still required


class Refused(ValueError):
    pass


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise Refused(reason)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _identity(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _close_owned(fds: list[int], primary: BaseException | None) -> None:
    errors = []
    for fd in reversed(fds):
        try:
            os.close(fd)
        except BaseException as error:
            errors.append(error)
    if errors:
        if primary is not None:
            primary.secondary_close_errors = tuple(errors)
            primary.add_note('Secondary release FD close failures retained: ' +
                             ', '.join(repr(error) for error in errors))
        else:
            raise BaseExceptionGroup('release FD close failed', errors)


def pinned(path: Path, expected: str, limit: int) -> bytes:
    """Read one exact nofollow inode and execute only its captured bytes."""
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts and
         path.name not in ('', '.', '..'), 'PINNED_PATH_DRIFT')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    leaf_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
    opened = []
    try:
        opened.append(os.open('/', flags))
        for part in path.parent.parts[1:]:
            opened.append(os.open(part, flags, dir_fd=opened[-1]))
        parent = opened[-1]
        before = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             before.st_uid == os.getuid() and
             stat.S_IMODE(before.st_mode) & 0o022 == 0 and
             0 <= before.st_size <= limit, 'PINNED_FILE_METADATA')
        opened.append(os.open(path.name, leaf_flags, dir_fd=parent))
        fd = opened[-1]
        need(_identity(os.fstat(fd)) == _identity(before), 'PINNED_OPEN_DRIFT')
        chunks, size = [], 0
        while True:
            block = os.read(fd, 1024 * 1024)
            if not block:
                break
            size += len(block)
            need(size <= limit, 'PINNED_OVERSIZE')
            chunks.append(block)
        raw = b''.join(chunks)
        need(size == before.st_size and sha(raw) == expected and
             _identity(os.fstat(fd)) == _identity(before) and
             _identity(os.stat(path.name, dir_fd=parent,
                               follow_symlinks=False)) == _identity(before),
             'PINNED_BYTES_OR_ATTACHMENT_DRIFT')
        return raw
    finally:
        _close_owned(opened, sys.exception())


def _parse(raw: bytes) -> dict:
    def pairs(rows):
        value = {}
        for key, item in rows:
            need(key not in value, 'DUPLICATE_JSON_KEY')
            value[key] = item
        return value
    try:
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(
                               Refused('NONFINITE_JSON')))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise Refused('INVALID_FREEZE_JSON') from error
    need(type(value) is dict, 'FREEZE_OBJECT_REQUIRED')
    return value


def checked_bytes() -> dict[str, bytes]:
    freeze = _parse(pinned(CONTROLLER / 'freeze.json', CONTROLLER_FREEZE_SHA,
                           64 * 1024))
    review = pinned(CONTROLLER_REVIEW, CONTROLLER_REVIEW_SHA, 256 * 1024)
    need(b'**Verdict: PASS for the frozen, effect-disabled controller;' in review and
         CONTROLLER_FREEZE_SHA.encode() in review,
         'CONTROLLER_INDEPENDENT_PASS_REVIEW_DRIFT')
    need(freeze.get('schema') == 'lab-mapper-successor-docker-controller-freeze/v1' and
         freeze.get('effect_enabled') is False and
         freeze.get('status') == 'READY_FOR_INDEPENDENT_STATIC_REVIEW_NO_EFFECT_YET' and
         freeze.get('stage_effect_review_sha256') == STAGE_EFFECT_REVIEW_SHA and
         freeze.get('one_shot_attempt') == str(ATTEMPT) and
         freeze.get('container_name') == CONTAINER_NAME and
         freeze.get('input_files') == 991 and
         freeze.get('input_directories') == 933 and
         freeze.get('private_rows') == 37 and
         freeze.get('expected_output_leaves') == 55 and
         freeze.get('external_exit_and_independent_effect_review_required') is True and
         freeze.get('no_retry') is True and
         freeze.get('normal_tests') == freeze.get('optimized_tests') == 13,
         'CONTROLLER_FREEZE_CONTRACT_DRIFT')
    rows = freeze.get('file_bindings')
    need(type(rows) is list and len(rows) == len(BOUND_NAMES),
         'CONTROLLER_FILE_BINDING_COUNT')
    checked = {}
    for index, name in enumerate(BOUND_NAMES):
        row = rows[index]
        path = CONTROLLER / name
        need(type(row) is dict and row.get('path') == str(path.relative_to(REPO)) and
             type(row.get('size')) is int and 0 <= row['size'] <= 2 * 1024 * 1024 and
             type(row.get('sha256')) is str and len(row['sha256']) == 64,
             'CONTROLLER_FILE_BINDING_DRIFT')
        data = pinned(path, row['sha256'], row['size'])
        need(len(data) == row['size'], 'CONTROLLER_FILE_SIZE_DRIFT')
        checked[name] = data
    return checked


@contextmanager
def reviewed_controller():
    checked = checked_bytes()
    previous = {name: sys.modules.get(name) for name in MODULE_NAMES}
    try:
        for name in MODULE_NAMES:
            path = CONTROLLER / (name + '.py')
            # Compile the same captured bytes that were verified above.
            code = compile(checked[name + '.py'], str(path), 'exec')
            module = types.ModuleType(name)
            module.__file__ = str(path)
            sys.modules[name] = module
            exec(code, module.__dict__)
        controller = sys.modules['controller']
        need(controller.EFFECT_ENABLED is False and
             controller.HERE == CONTROLLER and
             controller.DOCKER_ATTEMPT == ATTEMPT and
             controller.NAME == CONTAINER_NAME and
             controller.ENTRYPOINT_SHA == sha(checked['mapper_once.py']) and
             controller.STAGE_EFFECT_REVIEW_SHA == STAGE_EFFECT_REVIEW_SHA,
             'CHECKED_CONTROLLER_MODULE_DRIFT')
        # The child entrypoint is copied by hash under the held claim. Compile
        # its captured bytes here without running its host-incompatible body.
        compile(checked['mapper_once.py'], str(CONTROLLER / 'mapper_once.py'), 'exec')
        yield controller
    finally:
        for name in reversed(MODULE_NAMES):
            sys.modules.pop(name, None)
            if previous[name] is not None:
                sys.modules[name] = previous[name]


def preflight() -> dict:
    with reviewed_controller() as controller:
        result = controller.preflight()
    need(result['effect'] == 'NOT_RUN' and
         result['status'] == 'READY_FOR_INDEPENDENT_DISPATCH_REVIEW' and
         result['attempt'] == str(ATTEMPT) and
         result['container_name'] == CONTAINER_NAME and
         result['stage_effect_review_sha256'] == STAGE_EFFECT_REVIEW_SHA and
         result['input_files'] == 991 and
         result['private_inventory_rows_metadata_only'] == 37 and
         result['output_expected_leaves'] == 55 and
         result['no_retry'] is True,
         'RELEASE_PREFLIGHT_RESULT_DRIFT')
    return {'schema': 'lab-mapper-successor-docker-release-predispatch/v1',
            'status': 'READY_FOR_INDEPENDENT_RELEASE_REVIEW_NO_EFFECT_YET',
            'effect': 'NOT_RUN', 'controller_freeze_sha256': CONTROLLER_FREEZE_SHA,
            'controller_review_sha256': CONTROLLER_REVIEW_SHA,
            'stage_effect_review_sha256': STAGE_EFFECT_REVIEW_SHA,
            'attempt': str(ATTEMPT), 'container_name': CONTAINER_NAME,
            'no_retry': True, 'controller_preflight': result}


def execute_reviewed_one_shot() -> dict:
    need(EFFECT_ENABLED, 'MAPPER_RELEASE_EFFECT_DISABLED')
    with reviewed_controller() as controller:
        ready = controller.preflight()
        need(ready['effect'] == 'NOT_RUN' and ready['attempt'] == str(ATTEMPT) and
             ready['no_retry'] is True, 'RELEASE_PREFLIGHT_DRIFT')
        controller.EFFECT_ENABLED = True
        try:
            return controller.execute()
        finally:
            controller.EFFECT_ENABLED = False


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(), sort_keys=True))
    elif sys.argv[1:] == ['--execute-reviewed-one-shot']:
        print(json.dumps(execute_reviewed_one_shot(), sort_keys=True))
    else:
        raise SystemExit('expected --preflight or --execute-reviewed-one-shot')
