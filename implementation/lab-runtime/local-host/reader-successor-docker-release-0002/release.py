"""One-shot external Reader Docker release from exact reviewed controller 0003."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = HERE.parents[3]
CONTROLLER = LOCAL / 'reader-successor-controller-0003'
CONTROLLER_FREEZE_SHA = 'cc8a24271b58551b82a295a3cd8faaddd068e4bc6f50e6430388c5dc69f51b11'
CONTROLLER_REVIEW = LOCAL / 'READER-SUCCESSOR-CONTROLLER-INDEPENDENT-STATIC-REVIEW-0003.md'
CONTROLLER_REVIEW_SHA = 'b5dc21c8f52d420203ee41a9c6898a9a5a198e94d97ef59ec5cb5916918b1351'
DOCKER = '/usr/bin/docker'
DOCKER_SHA = '999189864fcf5cbda492d1fcb790044a6f152e2d0a7e49308d1c21ff4146bd00'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
NAME = 'cal-reader-only-20261020-0002-successor-0001'


class Refused(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(ok: bool, code: str) -> None:
    if not ok:
        raise Refused(code)


def basis():
    raw = (CONTROLLER / 'freeze.json').read_bytes()
    need(sha(raw) == CONTROLLER_FREEZE_SHA and
         sha(CONTROLLER_REVIEW.read_bytes()) == CONTROLLER_REVIEW_SHA,
         'CONTROLLER_FREEZE_OR_REVIEW_DRIFT')
    freeze = json.loads(raw)
    need(freeze['schema'] == 'lab-reader-successor-controller-freeze/v3' and
         freeze['effect_enabled'] is False and freeze['effect'] == 'NOT_RUN' and
         freeze['entrypoint_release_freeze_sha256'] ==
         'a19e831559804d397cc9131b0594f1385fad55f41381139196e5490bf4af52fc' and
         len(freeze['file_bindings']) == 3, 'CONTROLLER_CONTRACT_DRIFT')
    for row in freeze['file_bindings']:
        path = REPO / row['path']
        need(path.is_file() and not path.is_symlink() and
             path.stat().st_size == row['size'] and sha(path.read_bytes()) == row['sha256'],
             'CONTROLLER_MEMBER_DRIFT')
    spec = importlib.util.spec_from_file_location('cal_reviewed_reader_controller',
                                                   CONTROLLER / 'controller.py')
    need(spec is not None and spec.loader is not None, 'CONTROLLER_IMPORT')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(module.EFFECT_ENABLED is False and module.NAME == NAME and
         module.IMAGE == IMAGE and module.DOCKER == DOCKER,
         'CONTROLLER_EFFECT_OR_SELECTION_DRIFT')
    return module


def _command(argv: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=10, check=False)


def host_observation(runner=_command) -> dict:
    need(Path(DOCKER).is_file() and not Path(DOCKER).is_symlink() and
         sha(Path(DOCKER).read_bytes()) == DOCKER_SHA, 'DOCKER_BINARY_DRIFT')
    image = runner([DOCKER, 'image', 'inspect', IMAGE,
                    '--format', '{{.Id}} {{.Architecture}} {{.Config.User}}'])
    need(len(image.stdout) <= 4096 and len(image.stderr) <= 4096 and
         image.returncode == 0 and image.stderr == b'' and
         image.stdout == f'{IMAGE} amd64 20001:20001\n'.encode(),
         'DOCKER_IMAGE_OBSERVATION')
    absence = runner([DOCKER, 'container', 'inspect', NAME,
                      '--format', '{{.Id}}'])
    expected_error = ('Error response from daemon: No such container: ' + NAME + '\n').encode()
    need(len(absence.stdout) <= 4096 and len(absence.stderr) <= 4096 and
         absence.returncode == 1 and absence.stdout == b'\n' and
         absence.stderr == expected_error, 'DOCKER_NAME_NOT_EXCLUSIVELY_ABSENT')
    return {'schema': 'lab-reader-successor-docker-host-observation/v1',
            'image_id': IMAGE, 'image_architecture': 'amd64',
            'container_name': NAME, 'container_absent': True,
            'image_observation_sha256': sha(image.stdout),
            'name_observation_sha256': sha(absence.stderr),
            'effect': 'NOT_RUN'}


def preflight() -> dict:
    controller = basis()
    host = host_observation()
    selected = controller.preflight()
    need(selected['selected_files'] == 986 and selected['attempt_fresh'] is True and
         selected['effect'] == 'NOT_RUN' and selected['status'] == 'PASS_INERT',
         'READER_PREDISPATCH_DRIFT')
    return {'schema': 'lab-reader-successor-docker-predispatch/v1',
            'status': 'READY_FOR_INDEPENDENT_DISPATCH_REVIEW',
            'effect': 'NOT_RUN', 'controller_freeze_sha256': CONTROLLER_FREEZE_SHA,
            'controller_review_sha256': CONTROLLER_REVIEW_SHA,
            'selected_files': 986, 'attempt': str(controller.ATTEMPT),
            'image_id': IMAGE, 'container_name': NAME, 'host': host}


def _record_attempt_unknown(controller, error: BaseException) -> None:
    """Retain explicit UNKNOWN if a one-shot attempt was claimed before failure."""
    # A competing creator can win the exclusive root mkdir after preflight.
    # In that case this process owns no claim and must not write into it.
    if isinstance(error, FileExistsError) and error.filename == str(controller.ATTEMPT):
        return
    try:
        owned = controller.ATTEMPT.lstat()
        if (stat.S_ISDIR(owned.st_mode) and owned.st_uid == os.getuid() and
                owned.st_gid == os.getgid() and stat.S_IMODE(owned.st_mode) == 0o700):
            unknown = {'schema': 'lab-reader-successor-release-unknown/v1',
                       'overall': 'UNKNOWN', 'no_retry': True,
                       'attempt': str(controller.ATTEMPT),
                       'container_name': NAME,
                       'controller_freeze_sha256': CONTROLLER_FREEZE_SHA,
                       'error_class': type(error).__name__,
                       'stop_requested': controller.STOP_REQUESTED is True}
            controller.exclusive(controller.ATTEMPT / 'reader-release-unknown.json',
                                 controller.json_bytes(unknown))
    except FileNotFoundError:
        pass
    except BaseException as secondary:
        error.add_note('UNKNOWN receipt write failed: ' + repr(secondary))


def execute() -> dict:
    controller = basis()
    preflight()
    previous = {}
    def stop(_signum, _frame):
        controller.STOP_REQUESTED = True
    for code in (signal.SIGINT, signal.SIGTERM):
        previous[code] = signal.signal(code, stop)
    controller.EFFECT_ENABLED = True
    try:
        try:
            controller.prepare_attempt()
            if controller.STOP_REQUESTED:
                raise Refused('STOP_AFTER_READER_ATTEMPT_PREPARE')
            return controller.run()
        except BaseException as error:
            # Includes a signal between the post-prepare check and the
            # controller's consumed marker. An occupied attempt is never
            # retried, and the retained UNKNOWN takes precedence over PASS.
            _record_attempt_unknown(controller, error)
            raise
    finally:
        controller.EFFECT_ENABLED = False
        for code, prior in previous.items():
            signal.signal(code, prior)


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(), sort_keys=True))
    elif sys.argv[1:] == ['--execute-reviewed-one-shot']:
        result = execute()
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result.get('overall') == 'PASS' else 2)
    else:
        raise SystemExit('expected --preflight or --execute-reviewed-one-shot')
