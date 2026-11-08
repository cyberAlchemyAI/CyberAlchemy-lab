"""Exact, durable fixture provisioning for the LC-U06-01 construction cut.

This module deliberately has no actual-authority entrypoint. An eventual selected
operator adapter must be added only after LC-U05-03 and external custody are
accepted. Fixture callbacks are executable test dependencies, never an issuer.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import stat


class ProvisioningRefusal(ValueError):
    pass


def _need(condition, code):
    if not condition:
        raise ProvisioningRefusal(code)


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _json(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def _parse(raw):
    _need(type(raw) is bytes and 0 < len(raw) <= 65536, 'RECORD_BOUND')
    def pairs(items):
        result = {}
        for key, value in items:
            _need(key not in result, 'DUPLICATE_FIELD')
            result[key] = value
        return result
    def nonfinite(_value):
        raise ProvisioningRefusal('NONFINITE_RECORD')
    def decimal(_value):
        raise ProvisioningRefusal('DECIMAL_RECORD')
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=nonfinite, parse_float=decimal)


def _hex64(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def _component(value):
    return (type(value) is str and 1 <= len(value) <= 80 and
            re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9_-]*', value) is not None)


def _path(value):
    _need(type(value) is str and value.startswith('/') and len(value) <= 4096,
          'PATH_SELECTION')
    path = Path(value)
    _need('..' not in path.parts and str(path) == value, 'PATH_SELECTION')
    return path


def _present(path):
    """Lexical occupancy, including a dangling symlink; errors are not absence."""
    try:
        os.lstat(path)
        return True
    except FileNotFoundError:
        return False


def _directory_pin(path):
    """Pin every directory component. This is an inert selected-path check."""
    path = _path(str(path))
    pins = []
    current = Path('/')
    for name in path.parts[1:]:
        current = current / name
        info = os.lstat(current)
        _need(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode),
              'DIRECTORY_CUSTODY')
        pins.append((str(current), info.st_dev, info.st_ino, info.st_uid,
                     info.st_gid, stat.S_IMODE(info.st_mode)))
    return tuple(pins)


def _guard_pins(pins):
    for path, dev, ino, uid, gid, mode in pins:
        info = os.lstat(path)
        _need(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode)
              and (info.st_dev, info.st_ino, info.st_uid, info.st_gid,
                   stat.S_IMODE(info.st_mode)) == (dev, ino, uid, gid, mode),
              'DIRECTORY_CHANGED')


def _regular(path, *, mode=None, forbid_group_other_write=False, maximum=65536):
    _directory_pin(path.parent)
    before = os.lstat(path)
    _need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
          before.st_uid == os.geteuid() and
          (mode is None or stat.S_IMODE(before.st_mode) == mode) and
          (not forbid_group_other_write or
           stat.S_IMODE(before.st_mode) & 0o022 == 0) and
          0 <= before.st_size <= maximum, 'FILE_CUSTODY')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        opened = os.fstat(fd)
        _need((opened.st_dev, opened.st_ino, opened.st_mode, opened.st_size,
               opened.st_mtime_ns) ==
              (before.st_dev, before.st_ino, before.st_mode, before.st_size,
               before.st_mtime_ns), 'FILE_CHANGED')
        chunks = []
        total = 0
        while True:
            part = os.read(fd, min(65536, maximum - total + 1))
            if not part:
                break
            total += len(part)
            _need(total <= maximum, 'FILE_BOUND')
            chunks.append(part)
        after = os.fstat(fd)
        named = os.lstat(path)
        stamp = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size,
                           s.st_mtime_ns, s.st_ctime_ns)
        _need(stamp(before) == stamp(after) == stamp(named), 'FILE_CHANGED')
        return b''.join(chunks)
    finally:
        os.close(fd)


def _write_new(path, raw, mode):
    _need(type(raw) is bytes and len(raw) <= 65536, 'OUTPUT_BOUND')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW |
                 os.O_CLOEXEC, mode)
    try:
        os.fchmod(fd, mode)
        view = memoryview(raw)
        while view:
            count = os.write(fd, view)
            _need(count > 0, 'WRITE_SHORT')
            view = view[count:]
        os.fsync(fd)
    finally:
        os.close(fd)
    parent_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY |
                        os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)
    _need(_regular(path, mode=mode) == raw, 'OUTPUT_CHANGED')


def _sync_existing(path, *, mode=None, forbid_group_other_write=False):
    """Durably order selected keygen outputs before a store or result effect."""
    original = _regular(path, mode=mode,
                        forbid_group_other_write=forbid_group_other_write,
                        maximum=8192)
    selected = os.lstat(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        held = os.fstat(fd)
        _need((held.st_dev, held.st_ino, held.st_mode, held.st_size,
               held.st_uid, held.st_gid) ==
              (selected.st_dev, selected.st_ino, selected.st_mode,
               selected.st_size, selected.st_uid, selected.st_gid),
              'KEY_CHANGED')
        os.fsync(fd)
    finally:
        os.close(fd)
    parent_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY |
                        os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)
    named = os.lstat(path)
    _need((named.st_dev, named.st_ino, named.st_mode, named.st_size,
           named.st_uid, named.st_gid) ==
          (selected.st_dev, selected.st_ino, selected.st_mode,
           selected.st_size, selected.st_uid, selected.st_gid), 'KEY_CHANGED')
    _need(_regular(path, mode=mode,
                   forbid_group_other_write=forbid_group_other_write,
                   maximum=8192) == original, 'KEY_CHANGED')
    return original


def _rename_no_replace(source, destination):
    """One atomic Linux detach/rename; never leave two live policy links."""
    _need(source.parent == destination.parent, 'REVOKE_ROOT')
    _directory_pin(source.parent)
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, 'renameat2', None)
    _need(renameat2 is not None, 'ATOMIC_RENAME_UNAVAILABLE')
    renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                          ctypes.c_char_p, ctypes.c_uint]
    renameat2.restype = ctypes.c_int
    directory = os.open(source.parent, os.O_RDONLY | os.O_DIRECTORY |
                        os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        outcome = renameat2(directory, os.fsencode(source.name), directory,
                            os.fsencode(destination.name), 1)  # RENAME_NOREPLACE
        if outcome != 0:
            code = ctypes.get_errno()
            if code in (errno.ENOSYS, errno.EINVAL, errno.EOPNOTSUPP):
                raise ProvisioningRefusal('ATOMIC_RENAME_UNAVAILABLE')
            if code == errno.EEXIST:
                raise FileExistsError(code, 'archive already exists', str(destination))
            raise OSError(code, os.strerror(code), str(source), str(destination))
        os.fsync(directory)
    finally:
        os.close(directory)


@dataclass(frozen=True)
class FixturePlan:
    """Exact selected rehearsal; no field can request admitted effects."""

    owned_root: str
    store_id: str
    operator_ref: str
    scope_ref: str
    source_ref: str
    source_sha256: str
    profile_ref: str
    profile_sha256: str
    engine_ref: str
    engine_sha256: str
    base_head_sha256: str
    run_id: str
    expires_at: str
    rollback_retention: str = 'retain-predecessor'
    schema_version: str = 'lab-local-provisioning-plan/v1-fixture'
    posture: str = 'fixture-only'

    def check(self, *, require_current=True):
        _need(self.schema_version == 'lab-local-provisioning-plan/v1-fixture'
              and self.posture == 'fixture-only' and _component(self.store_id)
              and re.fullmatch('[a-zA-Z0-9-]+', self.store_id) is not None
              and _component(self.run_id)
              and type(self.operator_ref) is str
              and self.operator_ref.startswith('role:candidate-')
              and len(self.operator_ref) > len('role:candidate-')
              and self.scope_ref == 'scope:lab-runtime-local:' + self.store_id
              and self.rollback_retention == 'retain-predecessor', 'PLAN_SCOPE')
        for value in (self.source_sha256, self.profile_sha256,
                      self.engine_sha256, self.base_head_sha256):
            _need(_hex64(value), 'PLAN_DIGEST')
        try:
            instant = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            raise ProvisioningRefusal('PLAN_PERIOD') from None
        _need(instant.tzinfo is not None, 'PLAN_PERIOD')
        if require_current:
            _need(instant.astimezone(timezone.utc) > datetime.now(timezone.utc),
                  'PLAN_PERIOD')
        root = _path(self.owned_root)
        _need(str(root).startswith('/tmp/') and root != Path('/tmp'),
              'FIXTURE_ROOT_ONLY')
        root_info = os.lstat(root)
        _need(stat.S_ISDIR(root_info.st_mode) and
              root_info.st_uid == os.geteuid() and
              stat.S_IMODE(root_info.st_mode) == 0o700,
              'FIXTURE_ROOT_MODE')
        _directory_pin(root)
        refs = []
        for ref, digest in ((self.source_ref, self.source_sha256),
                            (self.profile_ref, self.profile_sha256),
                            (self.engine_ref, self.engine_sha256)):
            path = _path(ref)
            _need(path.is_relative_to(root / 'inputs'), 'INPUT_SCOPE')
            refs.append(path)
            _need(_sha(_regular(path)) == digest, 'INPUT_DRIFT')
        _need(len(set(refs)) == 3, 'INPUT_ALIAS')

    def descriptor(self, *, require_current=True):
        self.check(require_current=require_current)
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


class FixtureProvisioner:
    """One exclusive store genesis, then fresh per-run reader channels.

    `engine` is a selected fixture test adapter. It never grants real custody.
    Once intent exists, every failure leaves it for inspection; no automatic
    deletion or same-operation redispatch is offered.
    """

    def __init__(self, plan, engine):
        _need(type(plan) is FixturePlan, 'PLAN_TYPE')
        plan.check()
        _need(getattr(engine, 'source_sha256', None) == plan.source_sha256
              and getattr(engine, 'profile_sha256', None) == plan.profile_sha256
              and getattr(engine, 'engine_sha256', None) == plan.engine_sha256,
              'ENGINE_SELECTION')
        root = _path(plan.owned_root)
        self.plan = plan
        self.root = root
        self.engine = engine
        self.dirs = {name: root / name for name in
                     ('inputs', 'store', 'keys', 'channels', 'rollback', 'journal')}
        for name, path in self.dirs.items():
            info = os.lstat(path)
            _need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
                  and stat.S_IMODE(info.st_mode) == 0o700,
                  'OWNED_DIRECTORY_' + name.upper())
        self.pins = {name: _directory_pin(path) for name, path in self.dirs.items()}
        self.store = self.dirs['store'] / plan.store_id
        self.key = self.dirs['keys'] / (plan.run_id + '.pem')
        self.public = self.dirs['keys'] / (plan.run_id + '.pub')
        self.policy = self.dirs['channels'] / (plan.run_id + '.json')
        self.intent = self.dirs['journal'] / (plan.run_id + '.intent.json')
        self.result = self.dirs['journal'] / (plan.run_id + '.result.json')
        self.revocation_intent = self.dirs['journal'] / (plan.run_id + '.revoke-intent.json')
        self.revocation = self.dirs['journal'] / (plan.run_id + '.revoked.json')
        self.archived_policy = self.dirs['channels'] / (plan.run_id + '.revoked-policy.json')

    def _guard(self, *, require_current=True):
        self.plan.check(require_current=require_current)
        for pins in self.pins.values():
            _guard_pins(pins)

    def _current(self):
        self._guard()
        _need(not _present(self.revocation) and
              not _present(self.revocation_intent),
              'CHANNEL_REVOKED')

    def _intent_record(self):
        return {'schema_version': 'lab-fixture-provisioning-intent/v1',
                'plan_sha256': _sha(_json(self.plan.descriptor(require_current=False))),
                'store_id': self.plan.store_id, 'run_id': self.plan.run_id,
                'operator_ref': self.plan.operator_ref,
                'base_head_sha256': self.plan.base_head_sha256,
                'authority_effect': 'none', 'posture': 'fixture-only'}

    def _check_intent(self):
        _need(_parse(_regular(self.intent, mode=0o600)) == self._intent_record(),
              'INTENT_CHANGED')

    def provision(self, policy_builder, *, after_engine=None):
        """Create one fixture store and its first channel; never retry intent."""
        self._current()
        _need(self.plan.base_head_sha256 == _sha(b'ABSENT'), 'BASE_HEAD_SELECTION')
        _need(not any(_present(p) for p in
                      (self.store, self.key, self.public, self.policy,
                       self.intent, self.result, self.revocation_intent,
                       self.revocation, self.archived_policy)), 'PREIMAGE_EXISTS')
        _write_new(self.intent, _json(self._intent_record()), 0o600)
        try:
            self._check_intent()
            self._guard()
            self.engine.keygen(self.key, self.public)
            _need(_sync_existing(self.key, mode=0o600) != b'',
                  'KEY_CUSTODY')
            public = _sync_existing(self.public,
                                    forbid_group_other_write=True).decode('ascii').strip()
            _need(public and '\n' not in public, 'PUBLIC_KEY')
            self._guard()
            policy_raw = self._policy_bytes(policy_builder, public)
            self.engine.initialize(self.store, self.plan, public)
            self._guard()
            observed = self.engine.inspect(self.store, self.plan)
            _need(type(observed) is dict and observed.get('store_id') == self.plan.store_id
                  and _hex64(observed.get('head_sha256')),
                  'STORE_INSPECTION')
            if after_engine is not None:
                after_engine()  # fixture fault injection; intent remains durable
            self._stage(policy_raw)
            record = {'schema_version': 'lab-fixture-provisioning-result/v1',
                      'plan_sha256': self._intent_record()['plan_sha256'],
                      'store_id': self.plan.store_id,
                      'head_sha256': observed['head_sha256'],
                      'policy_sha256': _sha(_regular(self.policy, mode=0o600)),
                      'public_key_sha256': _sha(_regular(
                          self.public, forbid_group_other_write=True)),
                      'authority_effect': 'none', 'posture': 'fixture-only'}
            _write_new(self.result, _json(record), 0o600)
            self._guard()
            self._check_intent()
            _need(self.inspect()['state'] == 'COMPLETE', 'POSTCHECK')
            return record
        except BaseException:
            # Preserve all partial files, including the original durable intent.
            raise

    def _policy_bytes(self, policy_builder, public):
        _need(callable(policy_builder), 'POLICY_BUILDER')
        self._guard()
        _need(not _present(self.policy),
              'POLICY_PREIMAGE')
        raw = policy_builder(public, self.plan)
        _need(type(raw) is bytes and len(raw) <= 16384, 'POLICY_BOUND')
        policy = _parse(raw)
        _need(type(policy) is dict and set(policy) == {
                  'schema_version', 'reader_public_key', 'principal_ref',
                  'scope_refs', 'expires_at', 'revoked',
                  'authority_effect', 'actual_owner_outcome'} and
              policy.get('schema_version') == 'lab-fixture-reader-policy/v1' and
              policy.get('reader_public_key') == public and
              policy.get('principal_ref') == self.plan.operator_ref and
              policy.get('scope_refs') == [self.plan.scope_ref] and
              policy.get('revoked') is False and
              policy.get('authority_effect') == 'none' and
              policy.get('actual_owner_outcome') is None and
              policy.get('expires_at') == self.plan.expires_at,
              'POLICY_SELECTION')
        return raw

    def _stage(self, raw):
        self._guard()
        _need(not _present(self.policy),
              'POLICY_PREIMAGE')
        _write_new(self.policy, raw, 0o600)
        self._guard()

    def restart_channel(self, prior, policy_builder):
        """Stage a new credential for an existing verified store after revocation.

        `prior` must be the prior selected fixture instance. No in-memory Session,
        nonce, key or old policy is copied. A new run_id is mandatory.
        """
        _need(type(prior) is FixtureProvisioner and
              prior.root == self.root and prior.store == self.store and
              prior.plan.run_id != self.plan.run_id, 'RESTART_SELECTION')
        _need(all(getattr(self.plan, key) == getattr(prior.plan, key) for key in
                  ('store_id', 'operator_ref', 'scope_ref', 'source_ref',
                   'source_sha256', 'profile_ref', 'profile_sha256',
                   'engine_ref', 'engine_sha256', 'rollback_retention')),
              'RESTART_CONTINUITY')
        self._current()
        prior_state = prior.inspect()
        _need(prior_state['state'] == 'COMPLETE', 'PRIOR_UNKNOWN')
        _need(self.plan.base_head_sha256 == prior_state['head_sha256'],
              'BASE_HEAD_SELECTION')
        _need(not any(_present(p) for p in
                      (self.key, self.public, self.policy, self.intent,
                       self.result, self.revocation_intent, self.revocation,
                       self.archived_policy)),
              'RESTART_PREIMAGE')
        _write_new(self.intent, _json(self._intent_record()), 0o600)
        self.engine.keygen(self.key, self.public)
        _need(_sync_existing(self.key, mode=0o600) != b'', 'KEY_CUSTODY')
        public = _sync_existing(self.public,
                                forbid_group_other_write=True).decode('ascii').strip()
        _need(public != _regular(prior.public,
                                 forbid_group_other_write=True).decode('ascii').strip(),
              'KEY_REUSED')
        policy_raw = self._policy_bytes(policy_builder, public)
        observed = self.engine.inspect(self.store, self.plan)
        _need(observed.get('store_id') == self.plan.store_id and
              observed.get('head_sha256') == self.plan.base_head_sha256,
              'STORE_INSPECTION')
        prior.revoke()
        self._stage(policy_raw)
        record = {'schema_version': 'lab-fixture-provisioning-result/v1',
                  'plan_sha256': self._intent_record()['plan_sha256'],
                  'store_id': self.plan.store_id,
                  'head_sha256': observed['head_sha256'],
                  'policy_sha256': _sha(_regular(self.policy, mode=0o600)),
                  'public_key_sha256': _sha(_regular(
                      self.public, forbid_group_other_write=True)),
                  'authority_effect': 'none', 'posture': 'fixture-only'}
        _write_new(self.result, _json(record), 0o600)
        _need(self.inspect()['state'] == 'COMPLETE', 'POSTCHECK')
        return record

    def revoke(self):
        self._guard(require_current=False)
        _need(self.inspect()['state'] == 'COMPLETE', 'REVOKE_UNKNOWN')
        _need(not _present(self.archived_policy) and
              not _present(self.revocation_intent) and
              not _present(self.revocation),
              'REVOKE_PREIMAGE')
        policy_sha = _sha(_regular(self.policy, mode=0o600))
        record = {
            'schema_version': 'lab-fixture-channel-revocation/v1',
            'plan_sha256': self._intent_record()['plan_sha256'],
            'policy_sha256': policy_sha,
            'authority_effect': 'none'}
        _write_new(self.revocation_intent, _json(record), 0o600)
        # One atomic no-replace transition. The original ReaderChannel opens
        # this path on every guard; after rename it cannot authenticate.
        _rename_no_replace(self.policy, self.archived_policy)
        _need(_sha(_regular(self.archived_policy, mode=0o600)) == policy_sha
              and not _present(self.policy),
              'REVOKE_DETACH')
        _write_new(self.revocation, _json(record), 0o600)
        self._guard(require_current=False)

    def challenge_nonce(self):
        """Fresh process-local challenge, intentionally absent from durable state."""
        import secrets
        self._current()
        _need(self.inspect()['state'] == 'COMPLETE', 'CHANNEL_UNKNOWN')
        return secrets.token_hex(32)

    def inspect(self):
        """Read-only, independently recheck intent/store/result after lost reply."""
        self._guard(require_current=False)
        if not _present(self.intent):
            if any(_present(path) for path in
                   (self.store, self.key, self.public, self.policy,
                    self.result, self.revocation_intent, self.revocation,
                    self.archived_policy)):
                return {'state': 'UNKNOWN', 'effect': 'unknown'}
            return {'state': 'ABSENT', 'effect': 'none'}
        self._check_intent()
        if not _present(self.store):
            return {'state': 'INTENT_ONLY', 'effect': 'unknown'}
        try:
            observed = self.engine.inspect(self.store, self.plan)
            _need(type(observed) is dict and observed.get('store_id') == self.plan.store_id
                  and _hex64(observed.get('head_sha256')), 'STORE_INSPECTION')
        except Exception:
            return {'state': 'UNKNOWN', 'effect': 'unknown'}
        if not _present(self.result):
            return {'state': 'EFFECT_OBSERVED_RESPONSE_UNKNOWN',
                    'effect': 'observed', 'head_sha256': observed['head_sha256']}
        record = _parse(_regular(self.result, mode=0o600))
        revoked = _present(self.revocation)
        if _present(self.revocation_intent):
            revocation_record = _parse(_regular(self.revocation_intent, mode=0o600))
            _need(revocation_record == {
                'schema_version': 'lab-fixture-channel-revocation/v1',
                'plan_sha256': self._intent_record()['plan_sha256'],
                'policy_sha256': record.get('policy_sha256'),
                'authority_effect': 'none'}, 'REVOKE_RECORD_CHANGED')
            if not revoked:
                return {'state': 'REVOKE_UNKNOWN', 'effect': 'unknown'}
            _need(_parse(_regular(self.revocation, mode=0o600)) ==
                  revocation_record and not _present(self.policy) and
                  _sha(_regular(self.archived_policy, mode=0o600)) ==
                  record.get('policy_sha256'), 'REVOKE_CHANGED')
        else:
            _need(not revoked and not _present(self.archived_policy),
                  'REVOKE_INCOMPLETE')
        _need(type(record) is dict and record.get('schema_version') ==
              'lab-fixture-provisioning-result/v1' and
              set(record) == {'schema_version', 'plan_sha256', 'store_id',
                              'head_sha256', 'policy_sha256',
                              'public_key_sha256', 'authority_effect',
                              'posture'} and
              record.get('plan_sha256') == self._intent_record()['plan_sha256'] and
              record.get('store_id') == self.plan.store_id and
              record.get('head_sha256') == observed['head_sha256'] and
              (revoked or record.get('policy_sha256') ==
               _sha(_regular(self.policy, mode=0o600))) and
              record.get('public_key_sha256') == _sha(_regular(
                  self.public, forbid_group_other_write=True)) and
              record.get('authority_effect') == 'none' and
              record.get('posture') == 'fixture-only', 'RESULT_CHANGED')
        return {'state': 'COMPLETE_REVOKED' if revoked else 'COMPLETE',
                'effect': 'observed',
                'head_sha256': observed['head_sha256']}
