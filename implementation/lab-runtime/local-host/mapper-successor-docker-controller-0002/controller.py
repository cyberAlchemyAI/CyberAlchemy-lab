"""Effect-disabled successor Mapper Docker role controller on reviewed stage."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
import subprocess
import sys
import time
import types

from anchored_copy import LEAF_FLAGS, close_all, identity, parent_chain, reattached
from held_stage import HeldAttempt
import docker_protocol
import output_verifier
from root_guard import RootGuard

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = HERE.parents[3]
STAGE = LOCAL / 'mapper-successor-stage-0002'
STAGE_FREEZE_SHA = 'c214e06c122186124a11f16e456257a1f800cfea8b05361da9d18247ece60311'
STAGE_STATIC_REVIEW = LOCAL / 'MAPPER-SUCCESSOR-STAGE-INDEPENDENT-STATIC-REVIEW-0002.md'
STAGE_STATIC_REVIEW_SHA = 'fad287769926dafe0a662ce9007d28b4bd90ba4523364b51a3ecd6a30974633f'
STAGE_RELEASE = LOCAL / 'mapper-successor-stage-release-0001'
STAGE_RELEASE_FREEZE_SHA = '543f3f21bc0542a73fbcbc5980c353c3a610ef806d4a7942b6839340fb912443'
STAGE_RELEASE_REVIEW = LOCAL / 'MAPPER-SUCCESSOR-STAGE-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md'
STAGE_RELEASE_REVIEW_SHA = '7cd5411e65b1b0e3d545a83b91120035f0979c3b9177ccdf5da87192be43a9e4'
STAGE_EFFECT_REVIEW = LOCAL / 'context-successor-mapper-stage-independent-effect-review-0001/review.json'
STAGE_EFFECT_REVIEW_SHA = 'bae85fada28780b6bcc88082d2436082402d8acfc25b420328c79df6d2f07406'
STAGE_EFFECT_NARRATIVE = LOCAL / 'context-successor-mapper-stage-independent-effect-review-0001/REVIEW.md'
STAGE_EFFECT_NARRATIVE_SHA = '546325e476e16d8562c7280d50c34df45423fd2c06c8460406491e0fe4237150'
ADAPTER = LOCAL / 'mapper-successor-stage-adapter-0002'
ADAPTER_FREEZE_SHA = 'c4a15d25587623ec4b73408d2e3e51f767d0d33e4943262b491bae435eabef0e'
ADAPTER_REVIEW = LOCAL / 'MAPPER-SUCCESSOR-STAGE-ADAPTER-INDEPENDENT-STATIC-REVIEW-0002.md'
ADAPTER_REVIEW_SHA = '1be51f0fac1d9a2cdf7780dbc7ffd4bd50aef7448d43358712248bba0e8e93be'
PLAN_SHA = '9041aeedc8b349f6d7315e7ac2544aabda85afdb748663010e00af25e0b9ca2e'
COPY_SHA = '76bfc24841d652cbae039d666bcde80d7899b3b978ebd0291443705543d3dd95'
VERIFIER_SHA = 'e45ba0c5ba2797b2e7ed564caa4528fbf8d79c8b1f42d95f36783ec59cf94416'
STAGE_TERMINAL_SHA = 'be474e04f4627575a2e16e61427050e5e486ac19101784170592280348969461'
STAGE_CONSUMED_SHA = '92ffef252e352ce6cc36acfd3f2980308f686e70c60cbe23176ca6256d6f55d3'
STAGE_EXTERNAL_SHA = 'ddac0db744829ec1bd849e1111fe325fb3af9055939334d97373c68eff104e54'
STAGE_INTENT_SHA = '3bd370c6024e4a967dcf98a934cd8feaa91190d6f8e03283912701c46e6574fc'
STAGE_STDOUT_SHA = '6f5e7df111b375ae5e5b1721edd729e5f4b4981259b7a8c3418843db45b4de10'
STAGE_STDERR_SHA = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
STAGE_OBSERVATION_SHA = '26a84c8eda65e5c411f12e5b2656bec9352be1d918106cd4069352166208f6f2'
STAGE_ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/mapper-attempt')
ROOT = STAGE_ATTEMPT / 'root'
DOCKER_ATTEMPT = STAGE_ATTEMPT / 'docker-attempt'
STAGE_EXTERNAL = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/mapper-successor-stage-release-0001')
MAPPER = 'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002'
SOURCE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
READER = 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0002'
SOURCE_SHA = '2843a67fd28a295f5c175b8d8c2b31f701040bb8d7dedeade8d76bbdf057d1d1'
PACKAGE_SHA = 'bdb5eac92cbb3f96857c4d2ccb00880441d55fb8f1dbbeb5cdaae8d81c720653'
READER_SHA = '048ef6c1f54387fc6e593f38b29723cb06f84649f12e9c75a0340d389b0f5756'
MAPPER_SHA = 'bad889d50a0ba302ae83c9f4d5d9b664417af50cf4a6e4c408dfb50f8680d947'
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
ENTRYPOINT_SHA = 'e00b863a91b5084e3ec85c662b38d912ee556fd6b1780704cb0f56d5de83cc2a'
DOCKER = '/usr/bin/docker'
DOCKER_SHA = '999189864fcf5cbda492d1fcb790044a6f152e2d0a7e49308d1c21ff4146bd00'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
NAME = 'cal-mapper-only-20261020-0002-successor-0001'
EFFECT_ENABLED = False


class Refused(ValueError):
    pass


def need(ok: bool, code: str) -> None:
    if not ok:
        raise Refused(code)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def parse(raw: bytes) -> dict:
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
        raise Refused('INVALID_JSON') from error
    need(type(value) is dict, 'JSON_OBJECT_REQUIRED')
    return value


def pinned(path: Path, digest: str, limit: int = 1024 * 1024) -> bytes:
    with parent_chain(path) as (parent, chain):
        before = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             before.st_uid == os.getuid() and 0 <= before.st_size <= limit,
             'PINNED_FILE_METADATA')
        fd = os.open(path.name, LEAF_FLAGS, dir_fd=parent)
        try:
            need(identity(os.fstat(fd)) == identity(before), 'PINNED_OPEN_DRIFT')
            chunks = []
            size = 0
            while True:
                block = os.read(fd, 1024 * 1024)
                if not block:
                    break
                size += len(block)
                need(size <= limit, 'PINNED_FILE_OVERSIZE')
                chunks.append(block)
            raw = b''.join(chunks)
            need(size == before.st_size and sha(raw) == digest and
                 identity(os.fstat(fd)) == identity(before), 'PINNED_BYTES_DRIFT')
            reattached(path, chain, identity(before))
            return raw
        finally:
            close_all([fd], sys.exception())


def _freeze(directory: Path, expected: str, review: Path, review_sha: str,
            enabled: bool, members: int) -> dict:
    raw = pinned(directory / 'freeze.json', expected, 32 * 1024)
    need(sha(pinned(review, review_sha, 256 * 1024)) == review_sha,
         'REVIEW_DRIFT')
    freeze = parse(raw)
    need(freeze['effect_enabled'] is enabled and
         len(freeze['file_bindings']) == members, 'FREEZE_CONTRACT')
    for row in freeze['file_bindings']:
        path = REPO / row['path']
        need(len(pinned(path, row['sha256'], 2 * 1024 * 1024)) == row['size'],
             'FROZEN_MEMBER_DRIFT')
    return freeze


def _actual_adapter(now: datetime) -> dict:
    freeze = _freeze(ADAPTER, ADAPTER_FREEZE_SHA, ADAPTER_REVIEW,
                     ADAPTER_REVIEW_SHA, False, 7)
    row = next(row for row in freeze['file_bindings'] if row['path'].endswith('/adapter.py'))
    raw = pinned(REPO / row['path'], row['sha256'], 128 * 1024)
    module = types.ModuleType('cal_reviewed_mapper_direct_adapter_0002')
    module.__file__ = str(ADAPTER / 'adapter.py')
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module.select_actual(now=now)


def _reviewed_stage(now: datetime) -> tuple[dict, dict, dict]:
    pinned(STAGE_STATIC_REVIEW, STAGE_STATIC_REVIEW_SHA, 256 * 1024)
    stage = _freeze(STAGE, STAGE_FREEZE_SHA, STAGE_STATIC_REVIEW,
                    STAGE_STATIC_REVIEW_SHA, False, 14)
    need(stage['stage_plan_sha256'] == PLAN_SHA and
         stage['copy_plan_sha256'] == COPY_SHA and
         stage['verifier_plan_sha256'] == VERIFIER_SHA,
         'STAGE_FREEZE_PLAN_JOIN')
    release = _freeze(STAGE_RELEASE, STAGE_RELEASE_FREEZE_SHA,
                      STAGE_RELEASE_REVIEW, STAGE_RELEASE_REVIEW_SHA, True, 3)
    need(release['stage_freeze_sha256'] == STAGE_FREEZE_SHA,
         'STAGE_RELEASE_FREEZE_JOIN')
    selected = _actual_adapter(now)
    for name, digest, value in (
        ('stage-plan.json', PLAN_SHA, selected['stage_plan']),
        ('copy-plan.json', COPY_SHA, selected['copy_plan']),
        ('verifier-plan.json', VERIFIER_SHA, selected['verifier_plan'])):
        need(pinned(STAGE / name, digest, 1024 * 1024) == encoded(value),
             'DYNAMIC_STAGE_PLAN_DRIFT')
    return selected['stage_plan'], selected['copy_plan'], selected['verifier_plan']


def _stage_effect(plan: dict, copy: dict) -> dict:
    review_raw = pinned(STAGE_EFFECT_REVIEW, STAGE_EFFECT_REVIEW_SHA, 64 * 1024)
    pinned(STAGE_EFFECT_NARRATIVE, STAGE_EFFECT_NARRATIVE_SHA, 256 * 1024)
    review = parse(review_raw)
    terminal_raw = pinned(STAGE_ATTEMPT / 'evidence/stage-terminal.json',
                          STAGE_TERMINAL_SHA, 16 * 1024)
    consumed_raw = pinned(STAGE_ATTEMPT / 'consumed.json', STAGE_CONSUMED_SHA, 16 * 1024)
    external_raw = pinned(STAGE_EXTERNAL / 'result.json', STAGE_EXTERNAL_SHA, 32 * 1024)
    intent_raw = pinned(STAGE_EXTERNAL / 'intent.json', STAGE_INTENT_SHA, 32 * 1024)
    stdout_raw = pinned(STAGE_EXTERNAL / 'stdout.bin', STAGE_STDOUT_SHA, 16 * 1024)
    stderr_raw = pinned(STAGE_EXTERNAL / 'stderr.bin', STAGE_STDERR_SHA, 16 * 1024)
    pinned(STAGE_EFFECT_REVIEW.parent / 'observation.json', STAGE_OBSERVATION_SHA,
           4 * 1024 * 1024)
    terminal, consumed, external, intent = map(
        parse, (terminal_raw, consumed_raw, external_raw, intent_raw))
    need(review.get('schema') == 'lab-mapper-successor-stage-effect-review/v1' and
         review.get('verdict') == 'PASS_BOUNDED_STAGE_ONLY_EFFECT' and
         review.get('release_freeze_sha256') == STAGE_RELEASE_FREEZE_SHA and
         review.get('release_review_sha256') == STAGE_RELEASE_REVIEW_SHA and
         review.get('stage_plan_sha256') == PLAN_SHA and
         review.get('copy_plan_sha256') == COPY_SHA and
         review.get('terminal_sha256') == STAGE_TERMINAL_SHA and
         review.get('consumed_sha256') == STAGE_CONSUMED_SHA and
         review.get('external_observation_sha256') == STAGE_EXTERNAL_SHA and
         review.get('external_intent_sha256') == STAGE_INTENT_SHA and
         review.get('external_stdout_sha256') == STAGE_STDOUT_SHA and
         review.get('external_stderr_sha256') == STAGE_STDERR_SHA and
         review.get('observation_sha256') == STAGE_OBSERVATION_SHA and
         type(review.get('os_exit_code')) is int and review['os_exit_code'] == 0 and
         review.get('unknown_absent') is True and review.get('output_package_absent') is True and
         review.get('no_retry') is True and review.get('mapper_effect') == 'NOT_RUN' and
         review.get('native_execution') == 'NOT_RUN' and
         review.get('file_count') == 991 and review.get('directory_count') == 933 and
         review.get('private_rows') == 37 and review.get('mapper_manifest_sha256') == MAPPER_SHA and
         review.get('source_continuity_ceiling') ==
         'current snapshot only; creation/pre-effect per-file inode identities were not externally retained',
         'MAPPER_STAGE_REVIEW_JOIN')
    need(terminal.get('schema') == 'lab-mapper-successor-stage-terminal/v1' and
         terminal.get('overall') == 'OBSERVED_STAGE_ONLY' and
         terminal.get('effect') == 'PRIVATE_STAGE_COPY_ONLY' and
         terminal.get('mapper_effect') == 'NOT_RUN' and
         terminal.get('attempt') == str(STAGE_ATTEMPT) and
         terminal.get('input_files') == 991 and terminal.get('target_directories') == 933 and
         terminal.get('stage_plan_sha256') == PLAN_SHA and
         terminal.get('copy_plan_sha256') == COPY_SHA and
         terminal.get('requires_external_exit_zero_and_independent_stage_review') is True and
         consumed.get('attempt') == str(STAGE_ATTEMPT) and
         consumed.get('stage_plan_sha256') == PLAN_SHA and
         consumed.get('copy_plan_sha256') == COPY_SHA and
         consumed.get('no_retry') is True,
         'MAPPER_STAGE_TERMINAL_OR_CONSUMED_JOIN')
    need(type(external.get('os_exit_code')) is int and
         external['os_exit_code'] == 0 and
         external.get('process_error') is None and
         external.get('freeze_sha256') == STAGE_RELEASE_FREEZE_SHA and
         external.get('review_sha256') == STAGE_RELEASE_REVIEW_SHA and
         external.get('stdout_sha256') == STAGE_STDOUT_SHA and
         external.get('stderr_sha256') == STAGE_STDERR_SHA and
         external.get('stdout_size') == len(stdout_raw) and
         external.get('stderr_size') == len(stderr_raw) and
         external.get('retry_allowed') is False and
         intent.get('argv') == ['/usr/bin/python3', '-B',
              str(STAGE_RELEASE / 'release.py'), '--execute-reviewed-one-shot'] and
         intent.get('freeze_sha256') == STAGE_RELEASE_FREEZE_SHA and
         intent.get('review_sha256') == STAGE_RELEASE_REVIEW_SHA and
         intent.get('retry_allowed') is False and
         stderr_raw == b'' and parse(stdout_raw) == terminal and
         STAGE_STDOUT_SHA != STAGE_TERMINAL_SHA and
         not os.path.lexists(STAGE_ATTEMPT / 'stage-unknown.json'),
         'MAPPER_STAGE_EXTERNAL_OR_UNKNOWN_JOIN')
    need(plan['mapper_attempt'] == str(STAGE_ATTEMPT) and
         plan['mapper_root'] == str(ROOT) and
         plan['mapper_manifest_sha256'] == MAPPER_SHA and
         plan['reader_effect_review_sha256'] == review['reader_effect_review_sha256'] and
         copy['target_directories'] == review['directory_count'] and
         plan['native_sha256'] == review['native_sha256'] == NATIVE_SHA,
         'MAPPER_STAGE_PLAN_REVIEW_JOIN')
    return review


def dir_mode(name: str) -> int:
    return (0o700 if name == SOURCE + '/receipts' or
            name.startswith(SOURCE + '/packages') or
            name == MAPPER + '/packages' else 0o755)


def metadata(path: Path, mode: int, *, directory: bool = False) -> os.stat_result:
    with parent_chain(path) as (parent, chain):
        info = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        need((stat.S_ISDIR(info.st_mode) if directory else
              stat.S_ISREG(info.st_mode) and info.st_nlink == 1) and
             info.st_uid == os.getuid() and info.st_gid == os.getgid() and
             stat.S_IMODE(info.st_mode) == mode, 'STAGE_MEMBER_OWNER_MODE_DRIFT')
        reattached(path, chain, identity(info))
        return info


def hash_exact(path: Path, digest: str, mode: int) -> None:
    before = metadata(path, mode)
    with parent_chain(path) as (parent, chain):
        fd = os.open(path.name, LEAF_FLAGS, dir_fd=parent)
        try:
            need(identity(os.fstat(fd)) == identity(before), 'STAGE_HASH_OPEN_DRIFT')
            h = hashlib.sha256()
            while True:
                block = os.read(fd, 1024 * 1024)
                if not block:
                    break
                h.update(block)
            need(h.hexdigest() == digest and identity(os.fstat(fd)) == identity(before),
                 'STAGE_HASH_BYTES_DRIFT')
            reattached(path, chain, identity(before))
        finally:
            close_all([fd], sys.exception())


def entries(root: Path) -> tuple[set[str], set[str]]:
    need(root.is_dir() and not root.is_symlink(), 'STAGE_ROOT_TYPE_DRIFT')
    files, dirs = set(), set()
    for current, children, leaves in os.walk(root, followlinks=False):
        for name in children + leaves:
            item = Path(current) / name
            info = item.lstat()
            need(stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode),
                 'STAGE_NONREGULAR_ENTRY')
            (dirs if stat.S_ISDIR(info.st_mode) else files).add(
                item.relative_to(root).as_posix())
    return files, dirs


def input_inventory(plan: dict, copy: dict, *, hash_private: bool,
                    allow_output: bool = False) -> dict[str, tuple[int, ...]]:
    metadata(STAGE_ATTEMPT, 0o700, directory=True)
    metadata(ROOT, 0o755, directory=True)
    files, dirs = entries(ROOT)
    package = MAPPER + '/packages/0001'
    if allow_output:
        files = {name for name in files if not name.startswith(package + '/')}
        dirs = {name for name in dirs if name != package and
                not name.startswith(package + '/')}
    need(files == {row['path'] for row in plan['files']} and
         dirs == set(copy['target_directory_names']) and
         len(files) == 991 and len(dirs) == 933,
         'STAGE_INPUT_INVENTORY_DRIFT')
    for name in dirs:
        metadata(ROOT / name, dir_mode(name), directory=True)
    result = {}
    for row in plan['files']:
        mode = int(row['target_mode'], 8)
        path = ROOT / row['path']
        result[row['path']] = identity(metadata(path, mode))
        if hash_private or mode != 0o600:
            hash_exact(path, row['sha256'], mode)
    native = STAGE_ATTEMPT / 'input/lab-context-native-reader'
    result['/attempt/input/lab-context-native-reader'] = identity(metadata(native, 0o755))
    hash_exact(native, NATIVE_SHA, 0o755)
    need(not os.path.lexists(ROOT / package) if not allow_output else True,
         'MAPPER_PACKAGE_ALREADY_PRESENT')
    return result


def trusted_selection(*, now: datetime | None = None) -> dict:
    now = datetime.now(timezone.utc) if now is None else now
    plan, copy, verifier = _reviewed_stage(now)
    review = _stage_effect(plan, copy)
    need(verifier['expected_package_members'] == plan['expected_package_members'] and
         len(verifier['expected_package_members']) == 55 and
         verifier['template_sha256'] == plan['verifier_template_sha256'] and
         verifier['effect_verifier_adapted'] is False,
         'MAPPER_VERIFIER_SELECTION_DRIFT')
    return {'plan': plan, 'copy': copy, 'verifier': verifier,
            'stage_effect_review_sha256': STAGE_EFFECT_REVIEW_SHA,
            'stage_terminal_sha256': STAGE_TERMINAL_SHA,
            'stage_external_sha256': STAGE_EXTERNAL_SHA,
            'source_continuity_ceiling': review['source_continuity_ceiling']}


def _command(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    return docker_protocol.SubprocessDocker._run(args,
                                                 deadline=time.monotonic() + 10)


def host_observation(runner=_command) -> dict:
    docker_info = Path(DOCKER).lstat()
    need(stat.S_ISREG(docker_info.st_mode) and docker_info.st_uid == 0 and
         stat.S_IMODE(docker_info.st_mode) == 0o755 and
         docker_info.st_size <= 64 * 1024 * 1024,
         'DOCKER_BINARY_METADATA_DRIFT')
    h = hashlib.sha256()
    with Path(DOCKER).open('rb') as source:
        while block := source.read(1024 * 1024):
            h.update(block)
    need(h.hexdigest() == DOCKER_SHA and
         Path(DOCKER).lstat() == docker_info, 'DOCKER_BINARY_DRIFT')
    image = runner([DOCKER, 'image', 'inspect', IMAGE,
                    '--format', '{{.Id}} {{.Architecture}} {{.Config.User}}'])
    need(image.returncode == 0 and image.stderr == b'' and
         image.stdout == f'{IMAGE} amd64 20001:20001\n'.encode(),
         'MAPPER_DOCKER_IMAGE_OBSERVATION')
    absent = runner([DOCKER, 'container', 'inspect', NAME,
                     '--format', '{{.Id}}'])
    expected = ('Error response from daemon: No such container: ' + NAME + '\n').encode()
    need(absent.returncode == 1 and absent.stdout == b'\n' and
         absent.stderr == expected, 'MAPPER_DOCKER_NAME_NOT_ABSENT')
    return {'image': IMAGE, 'container_name': NAME, 'container_absent': True,
            'docker_binary_sha256': DOCKER_SHA,
            'image_observation_sha256': sha(image.stdout),
            'name_absence_sha256': sha(absent.stderr)}


def docker_create_argv(selection: dict, *, label: str) -> list[str]:
    need(type(label) is str and len(label) == 32 and
         all(char in '0123456789abcdef' for char in label),
         'MAPPER_ATTEMPT_LABEL_DRIFT')
    plan = selection['plan']
    need(plan['container_name'] == NAME and plan['image'] == IMAGE and
         plan['mapper_root'] == str(ROOT) and plan['native_sha256'] == NATIVE_SHA and
         plan['mapper_manifest_sha256'] == MAPPER_SHA,
         'MAPPER_DOCKER_SELECTION_DRIFT')
    return [DOCKER, 'create', '--name', NAME,
            '--label', 'cal.mapper.attempt=' + label,
            '--user', '1000:1000', '--userns', 'host', '--network', 'none',
            '--read-only', '--cap-drop', 'ALL',
            '--security-opt', 'no-new-privileges:true',
            '--pids-limit', '16', '--memory', '1g', '--cpus', '1',
            '-e', 'TMPDIR=/attempt/scratch',
            '--mount', 'type=bind,src=' + str(ROOT) + ',dst=/workspace,readonly',
            '--mount', 'type=bind,src=' + str(ROOT / MAPPER / 'packages') +
            ',dst=/workspace/' + MAPPER + '/packages',
            '--mount', 'type=bind,src=' + str(STAGE_ATTEMPT / 'input') +
            ',dst=/attempt/input,readonly',
            '--mount', 'type=bind,src=' + str(DOCKER_ATTEMPT / 'tool') +
            ',dst=/tool,readonly',
            '--tmpfs', '/attempt/scratch:rw,nosuid,nodev,size=512m,mode=0700,uid=1000,gid=1000',
            '--entrypoint', 'python', IMAGE,
            '/tool/mapper_once.py', '--source-sha256', SOURCE_SHA]


def preflight() -> dict:
    selection = trusted_selection()
    need(not os.path.lexists(DOCKER_ATTEMPT), 'MAPPER_DOCKER_ATTEMPT_CONSUMED')
    input_inventory(selection['plan'], selection['copy'], hash_private=False)
    need(output_verifier.MAPPER_SHA == MAPPER_SHA and
         output_verifier.SOURCE_PACKAGE_SHA == PACKAGE_SHA and
         sha((HERE / 'mapper_once.py').read_bytes()) == ENTRYPOINT_SHA,
         'MAPPER_TOOL_OR_VERIFIER_DRIFT')
    host = host_observation()
    fs = os.statvfs(STAGE_ATTEMPT)
    need(fs.f_bavail * fs.f_frsize >= 512 * 1024 * 1024 and
         fs.f_favail >= 4096, 'MAPPER_DOCKER_HOST_CAPACITY')
    return {'schema': 'lab-mapper-successor-docker-predispatch/v1',
            'status': 'READY_FOR_INDEPENDENT_DISPATCH_REVIEW', 'effect': 'NOT_RUN',
            'stage_effect_review_sha256': STAGE_EFFECT_REVIEW_SHA,
            'stage_plan_sha256': PLAN_SHA, 'input_files': 991,
            'private_inventory_rows_metadata_only': 37,
            'output_expected_leaves': 55, 'native_sha256': NATIVE_SHA,
            'attempt': str(DOCKER_ATTEMPT), 'container_name': NAME,
            'host': host, 'no_retry': True}


def execute() -> dict:
    need(EFFECT_ENABLED, 'MAPPER_DOCKER_EFFECT_DISABLED_PENDING_STATIC_REVIEW')
    selection = trusted_selection()
    preflight()
    before = input_inventory(selection['plan'], selection['copy'], hash_private=True)
    claim = HeldAttempt(DOCKER_ATTEMPT)
    guard = RootGuard(ROOT, MAPPER + '/packages')
    try:
        guard.acquire()
        claim.claim()
        claim.write('consumed.json', encoded({
            'schema': 'lab-mapper-successor-docker-consumed/v1',
            'attempt': str(DOCKER_ATTEMPT), 'stage_effect_review_sha256':
            STAGE_EFFECT_REVIEW_SHA, 'no_retry': True}))
        claim.mkdir('tool', 0o700)
        claim.copy(HERE / 'mapper_once.py', 'tool/mapper_once.py', ENTRYPOINT_SHA,
                   0o444, 0o644)
        claim.mkdir('evidence', 0o700)
        label = secrets.token_hex(16)
        args = docker_create_argv(selection, label=label)
        claim.write('evidence/prepared.json', encoded({
            'schema': 'lab-mapper-successor-docker-prepared/v1',
            'stage_effect_review_sha256': STAGE_EFFECT_REVIEW_SHA,
            'entrypoint_sha256': ENTRYPOINT_SHA, 'container_name': NAME,
            'image': IMAGE, 'label': label,
            'create_argv_sha256': sha(('\0'.join(args)).encode()),
            'no_retry': True, 'effect': 'NOT_STARTED'}))
        claim.attached()
        guard.attached()
        trusted_selection()
        host_observation()
        terminal = docker_protocol.reconcile_once(
            docker_protocol.SubprocessDocker(), args, image=IMAGE, label=label,
            name=NAME, evidence_dir=DOCKER_ATTEMPT / 'evidence',
            expected_args=docker_create_argv(selection, label=label),
            evidence_claim=claim)
        need(terminal['overall'] == 'PASS' and terminal['container_absent'] is True,
             'MAPPER_DOCKER_TERMINAL_NOT_PASS')
        claim.attached()
        guard.attached()
        output = output_verifier.verify(guard.package_fd,
                                        selection['verifier']['expected_package_members'])
        guard.attached()
        need(input_inventory(selection['plan'], selection['copy'], hash_private=True,
                             allow_output=True) == before,
             'MAPPER_DOCKER_INPUT_POSTDRIFT')
        claim.attached()
        guard.attached()
        final = {'schema': 'lab-mapper-successor-docker-final/v1',
                 'overall': 'OBSERVED_DOCKER_ONLY', 'attempt': str(DOCKER_ATTEMPT),
                 'stage_effect_review_sha256': STAGE_EFFECT_REVIEW_SHA,
                 'terminal_sha256': sha(docker_protocol.evidence_json_bytes(terminal)),
                 'output': output, 'no_retry': True,
                 'authority_effect': 'none', 'actual_owner_outcome': None,
                 'original_task_acceptance': False,
                 'requires_external_exit_zero_and_independent_effect_review': True,
                 'claim_ceiling': 'disposable Mapper output only; external exit and independent effect review pending'}
        claim.write('evidence/final.json', encoded(final))
        claim.attached()
        guard.attached()
        return final
    except BaseException as error:
        if claim.claimed and claim.fd is not None:
            unknown = {'schema': 'lab-mapper-successor-docker-final/v1',
                       'overall': 'UNKNOWN', 'attempt': str(DOCKER_ATTEMPT),
                       'stage_effect_review_sha256': STAGE_EFFECT_REVIEW_SHA,
                       'no_retry': True, 'error_class': type(error).__name__}
            try:
                claim.write('docker-unknown.json', encoded(unknown), attached=False)
            except BaseException as secondary:
                error.add_note('Docker UNKNOWN receipt write failed: ' + repr(secondary))
        raise
    finally:
        primary = sys.exception()
        try:
            claim.close(primary)
        finally:
            guard.close(primary if primary is not None else sys.exception())


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(), sort_keys=True))
    elif sys.argv[1:] == ['--execute-reviewed-one-shot']:
        print(json.dumps(execute(), sort_keys=True))
    else:
        raise SystemExit('expected --preflight or --execute-reviewed-one-shot')
