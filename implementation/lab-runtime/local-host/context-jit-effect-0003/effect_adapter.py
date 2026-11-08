"""Effect-disabled Context JIT adapter with no-replace fixture detachment.

No actual Source body is opened, no Ed25519 private key is generated, and no
real authorization, host policy, HostChannel or Context role is created here.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
import stat
import types
from pathlib import Path

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
LOCAL = REPO / 'implementation/lab-runtime/local-host'
HERE = Path(__file__).resolve().parent
PROVISION_FREEZE = 'fab03502c79f807eb33c1617cae3480d9a1e3fe2d6e26d2ef6dcb9a0a7b1d522'
PROVISION_REVIEW = '63f681dece788484bb0d090ecd48a628b54b8079244d6961c393555caaa5fa92'
PROVISION_CODE = '8428eac94f5416e22b499108218a2d39ee9fa17d6c54cf6896ceab844b108a69'
AUTH_GUARD = 'f7054b285f8eacfbd4c31e097aa1f0fb7a77bb7fe9d0810b733ef00df11a4976'
POLICY_GUARD = '0565b4a1a559404cf773198bf52e62f444b656084157557319ff0c3b44253a6f'
STAGE_FREEZE = '8e7194585a4a98ce4a6ed906ef349449457335aba2060229c1d105eac36021b8'
STAGE_SELECTION = '6721210d076da6462f904b2836a9e3ff5853be92f395a05ee2b141b517e078bf'
PROJECTED_BUILD = '30149a0388f3eb32fb30dd5b07bc11a8309ed7ab3fafa56ef8b5d714d39f93f0'
PROJECTED_CONTROL = 'ebd63979ce378070e6d5647c240234548a9fb38d141b6ed0d57885925f66c7e1'
TOPOLOGY_SHA = '6e37cdc5cc0ff1b10b81c109409d766e812148b7fbda9607ec016e2278a92733'
READER_CODE_PATH = Path('/tmp/cal-mapper-only-dev-20261020-0001-release3/root/product/lab/release-candidates/v1/interface/docker-reader-20261020-0001/reader.py')
READER_ADAPTER_PATH = READER_CODE_PATH.with_name('adapter.py')
READER_CODE_SHA = 'f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9'
READER_ADAPTER_SHA = '85646307fa07c768105258ef0d49226b2d06fc70af3e5993fb2f58ca2124c399'
STAGE_TOPOLOGY_FREEZE_SHA = '5db0269e8a47ed267cc39a6b0ee09cf5b8169ef87e92bf1c80032d9f3c230e70'
STAGE_TOPOLOGY_COMPAT_SHA = 'f5ccf9395c97f4b22532f713c161e370c0adcbc66eeab5939ef5526a8d11b6b4'
PREDECESSOR_FREEZE_SHA = '911bacb0101223886f71b259fe64881e3725f506a2aeac5e26a544dc1aa5afce'
PREDECESSOR_REVIEW_SHA = '6ff7522893705f36c3973b78c5e8e51a039b0504add449a67027e4a722086cd8'
PREDECESSOR_0002_FREEZE_SHA = '5cad973e8045d85fc899954e6b3009779551c06a52379106b1659a1c523ba2a7'
PREDECESSOR_0002_REVIEW_SHA = 'b8844c906bfafe9d4b5473ab8ae7edc48a99e41f7ea9d6b08f26ad45265d8a7c'
PINS = {
    LOCAL / 'context-jit-provision-0001/freeze.json': PROVISION_FREEZE,
    LOCAL / 'CONTEXT-JIT-PROVISION-INDEPENDENT-STATIC-REVIEW-0001.md': PROVISION_REVIEW,
    LOCAL / 'context-jit-provision-0001/jit_provision.py': PROVISION_CODE,
    LOCAL / 'context-auth-guard-0004/held_auth.py': AUTH_GUARD,
    LOCAL / 'context-policy-0002/held_policy.py': POLICY_GUARD,
    LOCAL / 'context-stage-0001/freeze.json': STAGE_FREEZE,
    LOCAL / 'context-stage-0001/selection.json': STAGE_SELECTION,
    LOCAL / 'context-jit-provision-0001/projected-build.py': PROJECTED_BUILD,
    LOCAL / 'context-jit-provision-0001/projected-control.py': PROJECTED_CONTROL,
    READER_CODE_PATH: READER_CODE_SHA,
    READER_ADAPTER_PATH: READER_ADAPTER_SHA,
    HERE / 'required-topology.json': TOPOLOGY_SHA,
    LOCAL / 'context-stage-topology-0001/freeze.json': STAGE_TOPOLOGY_FREEZE_SHA,
    LOCAL / 'context-stage-topology-0001/compatibility.json': STAGE_TOPOLOGY_COMPAT_SHA,
    LOCAL / 'context-jit-effect-0001/freeze.json': PREDECESSOR_FREEZE_SHA,
    LOCAL / 'CONTEXT-JIT-EFFECT-INDEPENDENT-STATIC-REVIEW-0001.md': PREDECESSOR_REVIEW_SHA,
    LOCAL / 'context-jit-effect-0002/freeze.json': PREDECESSOR_0002_FREEZE_SHA,
    LOCAL / 'CONTEXT-JIT-EFFECT-INDEPENDENT-STATIC-REVIEW-0002.md': PREDECESSOR_0002_REVIEW_SHA,
}
FIXTURE_AUTH = b'fixture-only invalid authorization bytes; no grant\n'
FIXTURE_POLICY = b'fixture-only invalid host policy bytes; no key\n'
EFFECT_ENABLED = False
REQUIRED_SEQUENCE = (
    'VERIFY_VERSIONED_STAGE_SELECTION_AND_EXACT_PREIMAGES',
    'DURABLY_RECORD_FRESH_ATTEMPT_INTENT',
    'OPEN_EXACT_READER_SIGNED_SOURCE_AND_GUARD',
    'COMPARE_SIGNED_SCOPE_TO_PUBLIC_APPROVAL_AND_CURRENT_PERIOD',
    'VERIFY_SOURCE_ROLE_OWNER_0700_AND_EXCLUSIVE_AUTH_NAMESPACE',
    'OBTAIN_APPROVED_ISSUER_AUTHORIZATION_FOR_EXACT_CONTEXT_FAMILY',
    'WRITE_AUTH_EXCLUSIVE_0600_NOFOLLOW_FSYNC_AND_HELD_READBACK',
    'CREATE_EXACT_PRIVATE_ROOT_EXCLUSIVE_OWNER_0700',
    'GENERATE_ONE_USE_IN_MEMORY_ED25519_PRIVATE_KEY',
    'CONSTRUCT_POLICY_WITH_REVIEWED_BYTE_BOUND_VALIDATOR',
    'WRITE_POLICY_EXCLUSIVE_0600_NOFOLLOW_FSYNC_AND_HELD_READBACK',
    'OPEN_HOSTCHANNEL_AND_AUTHENTICATE_EXACT_CHALLENGE_ONCE',
    'CLOSE_CHANNEL_AND_DROP_KEY_REFERENCE',
    'PROVE_RACE_SAFE_CLEANUP_OR_EXPLICIT_TRUSTED_UID_EXCLUSIVITY',
    'REMOVE_ONLY_VERIFIED_OWNED_AUTH_AND_PRIVATE_POLICY_OBJECTS',
    'VERIFY_ABSENCE_AND_DURABLY_RECORD_ATTEMPT_CONSUMED',
)


class Refused(ValueError):
    pass


class Unknown(Refused):
    pass


def require(ok, reason):
    if not ok:
        raise Refused(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_public(path, pin):
    require(path in PINS and PINS[path] == pin, 'unselected public preimage')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                0 < before.st_size <= 2 * 1024 * 1024, 'bounded public preimage required')
        raw = os.read(fd, before.st_size + 1)
        after = os.fstat(fd)
        require(len(raw) == before.st_size and
                (before.st_dev, before.st_ino, before.st_mode, before.st_size) ==
                (after.st_dev, after.st_ino, after.st_mode, after.st_size) and
                digest(raw) == pin, 'public preimage changed')
        return raw
    finally:
        os.close(fd)


def reviewed_preimages():
    for path, pin in PINS.items():
        pinned_public(path, pin)
    build = pinned_public(LOCAL / 'context-jit-provision-0001/projected-build.py', PROJECTED_BUILD)
    control = pinned_public(LOCAL / 'context-jit-provision-0001/projected-control.py', PROJECTED_CONTROL)
    reader = pinned_public(READER_CODE_PATH, READER_CODE_SHA)
    adapter = pinned_public(READER_ADAPTER_PATH, READER_ADAPTER_SHA)
    require(build.count(b'def provision(path, source):\n    _t35_effect_refused()') == 1 and
            build.count(b'_jit_private_root() as tmp:') == 1 and
            build.count(b'HostChannel(policy_path, policy_pin, source_pin, source, schemas)') == 1 and
            build.count(b'channel.authenticate(proof_raw)') == 1 and
            control.count(b'def read_auth_bytes(') == 1 and
            control.count(b'def read_policy_bytes(') == 1 and
            control.count(b'def authenticate(self, proof_raw):') == 1 and
            control.count(b'self.used = True') == 2 and
            reader.count(b'def open_signed(self, source_pin, package_pin):') == 1 and
            reader.count(b'with C.open_source(source_pin,package_pin) as cold:') == 1 and
            adapter.count(b"view.data['config']['scope_ref']") >= 2,
            'projected held guards or one-use HostChannel shape differs')
    return {'status': 'EXACT_PUBLIC_PREIMAGES', 'count': len(PINS),
            'effect': 'NOT_RUN', 'source_signed_view': 'NOT_OPENED'}


def load_guard(name, path, pin):
    raw = pinned_public(path, pin)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def signed_scope_contract(scope_ref, source_guarded, package_guarded):
    """Pure shape check; booleans cannot attest an actual Reader.open_signed view."""
    require(source_guarded is True and package_guarded is True and
            scope_ref == 'scope:cyberalchemy-lab-first-agent-episode',
            'current signed Source scope or package guard differs')
    return {'scope_ref': scope_ref, 'claim': 'SYNTHETIC_ONLY'}


def effect_plan():
    """Exact ordered contract only; no step invokes an effect here."""
    reviewed_preimages()
    topology = topology_contract()
    require(topology['authorization_leaf']['sha256'] == 'UNMINTED_UNSELECTED' and
            topology['selection_effect'] == 'NOT_RUN',
            'no effect-qualified versioned selection exists')
    return {'steps': list(REQUIRED_SEQUENCE), 'effect': 'NOT_RUN',
            'stage_successor': 'UNSELECTED', 'issuer': 'UNSELECTED',
            'unknown_rule': 'PRESERVE_EVIDENCE_AND_NEVER_REUSE_ATTEMPT'}


def topology_contract():
    """Required successor selection; stage0001 has no AUTH subtree and stays frozen."""
    raw = pinned_public(HERE / 'required-topology.json', TOPOLOGY_SHA)
    compatible = json.loads(pinned_public(
        LOCAL / 'context-stage-topology-0001/compatibility.json',
        STAGE_TOPOLOGY_COMPAT_SHA))
    require(compatible['jit_required_topology_draft_sha256'] == TOPOLOGY_SHA and
            compatible['stage_root_file_count_after_auth'] == 1571 and
            compatible['selected_new_stage_selection_sha256'] ==
            'UNSELECTED_PENDING_AUTH_AND_ROLE_PROJECTION',
            'stage topology compatibility does not bind required amendment')
    return json.loads(raw)


def actual_one_shot(*_args, **_kwargs):
    raise Refused('effect disabled: no reviewed versioned stage, issuer, key or Context effect')


def create_actual_authorization(*_args, **_kwargs):
    raise Refused('effect disabled: no Source issuer grant or real authorization write')


def generate_actual_key(*_args, **_kwargs):
    raise Refused('effect disabled: no one-use Ed25519 private key creation')


# The following fixture writes only schema-invalid public dummy strings under an
# isolated /tmp prefix. Its custody mechanics are not an issuer or JIT release.
def _fixed_fixture_base(base):
    path = Path(base)
    require(path.is_absolute() and path.parent == Path('/tmp') and
            path.name.startswith('cal-jit-effect-fixture-') and
            str(path) == path.as_posix(), 'isolated fixture base required')
    info = os.lstat(path)
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid() == os.getuid() and
            info.st_gid == os.getegid() == os.getgid() and
            stat.S_IMODE(info.st_mode) == 0o700,
            'owned 0700 fixture base required')
    return path


def _owned(path, kind, mode):
    info = os.lstat(path)
    require((stat.S_ISDIR(info.st_mode) if kind == 'directory' else stat.S_ISREG(info.st_mode)) and
            info.st_uid == os.geteuid() == os.getuid() and
            info.st_gid == os.getegid() == os.getgid() and
            stat.S_IMODE(info.st_mode) == mode and
            (kind == 'directory' or info.st_nlink == 1),
            'exact owned fixture object required')
    stable = (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid)
    return stable if kind == 'directory' else stable + (info.st_nlink, info.st_size)


def _same(path, identity, kind, mode):
    require(_owned(path, kind, mode) == identity, 'owned fixture identity changed')


def _fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _exclusive_dir(path):
    os.mkdir(path, 0o700)
    identity = _owned(path, 'directory', 0o700)
    _fsync_dir(path.parent)
    return identity


def _exclusive_file(path, raw):
    require(raw in (FIXTURE_AUTH, FIXTURE_POLICY), 'only invalid fixture bytes allowed')
    parent = path.parent
    _owned(parent, 'directory', 0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    primary = None
    try:
        require(os.write(fd, raw) == len(raw), 'short fixture write')
        os.fsync(fd)
        identity = _owned(path, 'file', 0o600)
    except BaseException as error:
        primary = error
    try:
        os.close(fd)
    except BaseException as close_error:
        raise Unknown('fixture leaf close uncertain; preserve attempt') from close_error
    if primary is not None:
        raise Unknown('fixture leaf write uncertain; preserve attempt') from primary
    _fsync_dir(parent)
    return identity


def _journal(base, ordinal, event):
    require(type(event) is str and 1 <= len(event) <= 100 and '\n' not in event,
            'bounded event required')
    directory = base / 'journal'
    _owned(directory, 'directory', 0o700)
    path = directory / f'{ordinal:04d}.json'
    raw = (json.dumps({'event': event, 'ordinal': ordinal}, sort_keys=True) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        require(os.write(fd, raw) == len(raw), 'short journal write')
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_dir(directory)


def _fixture_detach_no_replace(source, target, base):
    """Atomically refuse an occupied detached name; fixture-only mutation."""
    require(source.is_relative_to(base) and target.parent == base and
            target.name in ('detached-owned-policy', 'detached-owned-private') and
            source != target, 'exact fixture detach paths required')
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        renameat2 = libc.renameat2
    except AttributeError as error:
        raise Refused('atomic RENAME_NOREPLACE unavailable; preserve attempt') from error
    renameat2.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                          ctypes.c_char_p, ctypes.c_uint)
    renameat2.restype = ctypes.c_int
    at_fdcwd = -100
    rename_noreplace = 1
    result = renameat2(at_fdcwd, os.fsencode(source), at_fdcwd,
                       os.fsencode(target), rename_noreplace)
    if result != 0:
        number = ctypes.get_errno()
        raise OSError(number, os.strerror(number), str(target))
    _fsync_dir(source.parent)
    _fsync_dir(target.parent)


def _fixture_one_shot_body(base, inject=None):
    """Exercise no-replace and held reads without deleting any name.

    All outcomes preserve the fixture objects and consume the attempt. The
    caller owns the isolated base and may dispose of it after examining the
    evidence. This function supplies no real-effect cleanup primitive.
    """
    base = _fixed_fixture_base(base)
    require(inject in (None, 'fail_after_policy', 'unknown_after_policy',
                       'replace_policy_name', 'replace_private_dir_name'),
            'selected fixture injection required')
    reviewed_preimages()
    source = base / 'source-role'
    auth_dir = source / 'authorization'
    auth_leaf = auth_dir / 'context-development.json'
    private = base / 'private-root'
    policy_leaf = private / 'permission.json'
    require(not any(path.exists() or path.is_symlink() for path in
                    (base / 'journal', source, auth_dir, auth_leaf, private, policy_leaf)),
            'fixture attempt name consumed or occupied')
    os.mkdir(base / 'journal', 0o700)
    _fsync_dir(base)
    ordinal = 0
    def record(event):
        nonlocal ordinal
        ordinal += 1
        _journal(base, ordinal, event)
    record('ATTEMPT_INTENT')
    source_id = _exclusive_dir(source)
    record('SOURCE_ROLE_0700_CREATED')
    auth_dir_id = _exclusive_dir(auth_dir)
    record('AUTH_DIRECTORY_0700_CREATED')
    auth_id = _exclusive_file(auth_leaf, FIXTURE_AUTH)
    record('INVALID_AUTH_FIXTURE_0600_CREATED')
    private_id = _exclusive_dir(private)
    record('PRIVATE_ROOT_0700_CREATED')
    policy_id = _exclusive_file(policy_leaf, FIXTURE_POLICY)
    record('INVALID_POLICY_FIXTURE_0600_CREATED')
    auth_guard = load_guard('_fixture_held_auth', LOCAL / 'context-auth-guard-0004/held_auth.py', AUTH_GUARD)
    policy_guard = load_guard('_fixture_held_policy', LOCAL / 'context-policy-0002/held_policy.py', POLICY_GUARD)
    require(auth_guard.read_auth_bytes(auth_leaf, source, digest(FIXTURE_AUTH), os.geteuid()) == FIXTURE_AUTH,
            'fixture held AUTH readback differs')
    require(policy_guard.read_policy_bytes(policy_leaf, private, source,
                                           digest(FIXTURE_POLICY), os.geteuid(), os.getegid()) == FIXTURE_POLICY,
            'fixture held policy readback differs')
    record('HELD_DUMMY_READBACK_CONFIRMED')
    if inject == 'replace_policy_name':
        record('INJECT_POLICY_RENAME_REPLACEMENT_INTENT')
        detached = base / 'detached-owned-policy'
        _fixture_detach_no_replace(policy_leaf, detached, base)
        _same(detached, policy_id, 'file', 0o600)
        fd = os.open(policy_leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        try:
            os.write(fd, b'foreign replacement; preserve\n')
            os.fsync(fd)
        finally:
            os.close(fd)
        _fsync_dir(private)
        record('INJECT_POLICY_RENAME_REPLACEMENT_DONE')
    if inject == 'replace_private_dir_name':
        record('INJECT_PRIVATE_DIRECTORY_RENAME_REPLACEMENT_INTENT')
        detached = base / 'detached-owned-private'
        _fixture_detach_no_replace(private, detached, base)
        _same(detached, private_id, 'directory', 0o700)
        os.mkdir(private, 0o700)
        _fsync_dir(base)
        record('INJECT_PRIVATE_DIRECTORY_RENAME_REPLACEMENT_DONE')
    if inject == 'unknown_after_policy':
        record('UNKNOWN_PRESERVE_OBJECTS_REFUSE_REUSE')
        return {'status': 'UNKNOWN_PRESERVED', 'attempt_reusable': False,
                'auth_sha256': digest(FIXTURE_AUTH), 'policy_sha256': digest(FIXTURE_POLICY),
                'private_root_present': True, 'journal': str(base / 'journal')}
    if inject == 'fail_after_policy':
        record('SYNTHETIC_FAILURE_PRESERVE_FOR_MANUAL_DISPOSITION')
    # These observations may detect an injected replacement. No subsequent
    # unlink/rmdir uses the observed name, so a later replacement cannot be
    # deleted by this adapter. Ambiguity becomes UNKNOWN in the wrapper.
    _same(policy_leaf, policy_id, 'file', 0o600)
    _same(private, private_id, 'directory', 0o700)
    _same(auth_leaf, auth_id, 'file', 0o600)
    _same(auth_dir, auth_dir_id, 'directory', 0o700)
    _same(source, source_id, 'directory', 0o700)
    record('OBJECTS_PRESERVED_FOR_MANUAL_DISPOSITION')
    record('ATTEMPT_CONSUMED_CUSTODY_PRESERVED')
    return {'status': 'FAILED_PRESERVED' if inject else 'CUSTODY_PRESERVED',
            'attempt_reusable': False, 'auth_sha256': digest(FIXTURE_AUTH),
            'policy_sha256': digest(FIXTURE_POLICY),
            'private_root_present': True, 'journal': str(base / 'journal')}


def fixture_one_shot(base, inject=None):
    """Never retry an attempt after any fixture effect or uncertain cleanup."""
    try:
        return _fixture_one_shot_body(base, inject)
    except BaseException as error:
        path = Path(base)
        journal = path / 'journal'
        if (path.parent == Path('/tmp') and
                path.name.startswith('cal-jit-effect-fixture-') and
                journal.is_dir() and not journal.is_symlink()):
            active = False
            terminal = False
            try:
                _fixed_fixture_base(path)
                members = tuple(journal.iterdir())
                ordinals = [int(item.stem) for item in members
                            if item.suffix == '.json' and item.stem.isdecimal()]
                if len(ordinals) == len(members) and ordinals:
                    ordered = sorted(members)
                    first = json.loads(ordered[0].read_bytes())['event']
                    last = json.loads(ordered[-1].read_bytes())['event']
                    active = first == 'ATTEMPT_INTENT'
                    terminal = last in (
                            'ATTEMPT_CONSUMED_CUSTODY_PRESERVED',
                            'UNKNOWN_PRESERVE_OBJECTS_REFUSE_REUSE',
                            'UNKNOWN_PRESERVE_EVIDENCE_REFUSE_REUSE')
                    if active and not terminal:
                        _journal(path, max(ordinals) + 1,
                                 'UNKNOWN_PRESERVE_EVIDENCE_REFUSE_REUSE')
            except BaseException:
                # Existing intent journal still consumes the attempt. The
                # caller must reconcile it out of band; never retry here.
                pass
            if active and not terminal:
                raise Unknown('fixture effect uncertain; inspect journal and preserve attempt') from error
            raise
        raise
