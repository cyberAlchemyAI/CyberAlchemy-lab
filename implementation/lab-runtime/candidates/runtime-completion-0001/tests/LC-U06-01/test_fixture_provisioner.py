"""Provisional fixture oracles for the T34 successor; not unit acceptance."""

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[6]
SOURCE = ROOT / 'implementation/lab-runtime/candidates/runtime-completion-0001/provisioner/fixture.py'
spec = importlib.util.spec_from_file_location('provisional_u0601_fixture', SOURCE)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
FixturePlan = module.FixturePlan
FixtureProvisioner = module.FixtureProvisioner
ProvisioningRefusal = module.ProvisioningRefusal

RUNTIME = ROOT / 'implementation/lab-runtime/candidates/repeatable-operation'
sys.path.insert(0, str(RUNTIME))
from lab_runtime.common import byte_digest, load
from lab_runtime.replay import ReplayPins, full_replay, legacy_runtime

MANIFEST_REL = 'implementation/lab-runtime/candidates/repeatable-operation/design/legacy-runtime-bindings.json'
MANIFEST = ROOT / MANIFEST_REL


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class SelectedLegacyFixtureEngine:
    """Exercise the original selected C11 v2 store in private fixture scratch."""

    def __init__(self):
        pins = ReplayPins('v2', MANIFEST_REL, byte_digest(MANIFEST.read_bytes()), '', '')
        self.name, self.engine, self.stage = legacy_runtime(ROOT, pins)
        self.profile = load(Path(self.stage.name) / 'profile.json')
        self.manifest_sha = pins.manifest_sha256
        self.source_sha256 = sha(MANIFEST.read_bytes())
        self.profile_sha256 = sha((ROOT / 'implementation/lab-runtime/v2/profile.json').read_bytes())
        self.engine_sha256 = sha((ROOT / 'implementation/lab-runtime/v2/lab_runtime/store.py').read_bytes())

    def close(self):
        self.stage.cleanup()
        for key in list(sys.modules):
            if key == self.name or key.startswith(self.name + '.'):
                sys.modules.pop(key, None)

    def keygen(self, private, public):
        self.engine.keygen(private, public)

    def initialize(self, path, plan, public):
        self.engine.Store(path, ROOT).initialize(
            self.profile, plan.store_id, plan.operator_ref, public,
            ['artifact-instance'], ['admit'])

    def inspect(self, path, plan):
        config = load(path / 'config.json')
        baseline = load(path / 'baseline.json')
        head = load(path / 'HEAD.json')
        pins = ReplayPins('v2', MANIFEST_REL, self.manifest_sha,
                          byte_digest((path / 'config.json').read_bytes()),
                          baseline['snapshot_digest'], head['transaction_digest'])
        replay = full_replay(path, ROOT, ROOT, pins, require_current=True)
        if replay['config']['store_id'] != plan.store_id:
            raise ValueError('store identity changed')
        return {'store_id': plan.store_id,
                'head_sha256': byte_digest((path / 'HEAD.json').read_bytes())}


def fixture_policy(public, plan):
    # Closed at the provisioner boundary; original ReaderChannel validation is
    # a later U05-03 actual-oracle obligation, not inferred from this record.
    value = {'schema_version': 'lab-fixture-reader-policy/v1',
             'reader_public_key': public, 'principal_ref': plan.operator_ref,
             'scope_refs': ['scope:lab-runtime-local:' + plan.store_id],
             'expires_at': plan.expires_at, 'revoked': False,
             'authority_effect': 'none', 'actual_owner_outcome': None}
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


class ProvisionerCase(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix='lab-U06-01-fixture-', dir='/tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        os.chmod(self.root, 0o700)
        for name in ('inputs', 'store', 'keys', 'channels', 'rollback', 'journal'):
            path = self.root / name
            path.mkdir(mode=0o700)
        originals = (
            ROOT / 'implementation/lab-runtime/candidates/repeatable-operation/design/legacy-runtime-bindings.json',
            ROOT / 'implementation/lab-runtime/v2/profile.json',
            ROOT / 'implementation/lab-runtime/v2/lab_runtime/store.py',
        )
        self.input_paths = []
        for source in originals:
            target = self.root / 'inputs' / source.name
            target.write_bytes(source.read_bytes())
            os.chmod(target, 0o600)
            self.input_paths.append(target)
        self.engine = SelectedLegacyFixtureEngine()
        self.addCleanup(self.engine.close)

    def plan(self, run_id, store_id='owned-fixture', base_head_sha256=None):
        refs = self.input_paths
        return FixturePlan(
            owned_root=str(self.root), store_id=store_id,
            operator_ref='role:candidate-U06-01',
            scope_ref='scope:lab-runtime-local:' + store_id,
            source_ref=str(refs[0]), source_sha256=sha(refs[0].read_bytes()),
            profile_ref=str(refs[1]), profile_sha256=sha(refs[1].read_bytes()),
            engine_ref=str(refs[2]), engine_sha256=sha(refs[2].read_bytes()),
            base_head_sha256=base_head_sha256 or sha(b'ABSENT'), run_id=run_id,
            expires_at=(datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat())

    def test_two_independent_scoped_rehearsals_and_rollback_retention(self):
        first = FixtureProvisioner(self.plan('run_one', 'first-store'), self.engine)
        second = FixtureProvisioner(self.plan('run_two', 'second-store'), self.engine)
        one = first.provision(fixture_policy)
        two = second.provision(fixture_policy)
        self.assertEqual(first.inspect()['state'], 'COMPLETE')
        self.assertEqual(second.inspect()['state'], 'COMPLETE')
        self.assertNotEqual(one['head_sha256'], two['head_sha256'])
        self.assertTrue(first.store.exists() and second.store.exists())
        self.assertEqual(list((self.root / 'rollback').iterdir()), [])
        self.assertEqual(stat.S_IMODE(first.key.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(first.policy.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(first.public.stat().st_mode) & 0o022, 0)
        self.assertTrue(first.key.is_relative_to(self.root / 'keys'))
        self.assertFalse(first.key.is_relative_to(first.store))
        self.assertEqual(json.loads(first.intent.read_bytes())['authority_effect'], 'none')

    def test_restart_rotates_key_and_challenge_and_revokes_prior(self):
        first = FixtureProvisioner(self.plan('run_one'), self.engine)
        first.provision(fixture_policy)
        nonce = first.challenge_nonce()
        second = FixtureProvisioner(self.plan('run_two', base_head_sha256=first.inspect()['head_sha256']), self.engine)
        second.restart_channel(first, fixture_policy)
        self.assertEqual(second.inspect()['state'], 'COMPLETE')
        self.assertNotEqual(first.public.read_bytes(), second.public.read_bytes())
        self.assertNotEqual(nonce, second.challenge_nonce())
        self.assertNotEqual(second.challenge_nonce(), second.challenge_nonce())
        with self.assertRaisesRegex(ProvisioningRefusal, 'CHANNEL_REVOKED'):
            first.challenge_nonce()
        self.assertEqual(first.inspect()['state'], 'COMPLETE_REVOKED')
        self.assertTrue(first.store.exists() and first.key.exists())
        self.assertFalse(first.policy.exists())
        self.assertTrue(first.archived_policy.exists())
        self.assertFalse((self.root / 'store' / 'run_two').exists())

    def test_lost_response_is_inspectable_without_redispatch(self):
        selected = FixtureProvisioner(self.plan('lost_reply'), self.engine)
        with self.assertRaisesRegex(RuntimeError, 'lost response'):
            selected.provision(fixture_policy,
                               after_engine=lambda: (_ for _ in ()).throw(RuntimeError('lost response')))
        self.assertEqual(selected.inspect()['state'], 'EFFECT_OBSERVED_RESPONSE_UNKNOWN')
        with self.assertRaisesRegex(ProvisioningRefusal, 'PREIMAGE_EXISTS'):
            selected.provision(fixture_policy)
        self.assertTrue(selected.intent.exists() and selected.store.exists())
        self.assertFalse(selected.result.exists())

    def test_input_drift_and_symlink_refuse_before_intent(self):
        selected = FixtureProvisioner(self.plan('drift'), self.engine)
        self.input_paths[0].write_bytes(b'changed')
        with self.assertRaisesRegex(ProvisioningRefusal, 'INPUT_DRIFT'):
            selected.provision(fixture_policy)
        self.assertFalse(selected.intent.exists())
        self.input_paths[0].unlink()
        self.input_paths[0].symlink_to(MANIFEST)
        with self.assertRaisesRegex(ProvisioningRefusal, 'FILE_CUSTODY'):
            selected.provision(fixture_policy)
        self.assertFalse(selected.intent.exists())

    def test_wrong_policy_and_existing_path_do_not_reuse_or_overwrite(self):
        selected = FixtureProvisioner(self.plan('wrong'), self.engine)
        def wrong(public, plan):
            return fixture_policy(public, plan).replace(b'"revoked":false', b'"revoked":true')
        with self.assertRaisesRegex(ProvisioningRefusal, 'POLICY_SELECTION'):
            selected.provision(wrong)
        self.assertEqual(selected.inspect()['state'], 'INTENT_ONLY')
        self.assertFalse(selected.store.exists())
        self.assertFalse(selected.policy.exists())
        self.assertTrue(selected.key.exists())
        self.assertFalse(selected.store.exists())
        with self.assertRaisesRegex(ProvisioningRefusal, 'PREIMAGE_EXISTS'):
            selected.provision(fixture_policy)

    def test_foreign_scope_and_extra_authority_field_refuse(self):
        selected = FixtureProvisioner(self.plan('foreign-scope'), self.engine)
        def wrong_scope(public, plan):
            value = json.loads(fixture_policy(public, plan))
            value['scope_refs'] = ['scope:lab-runtime-local:other-store']
            return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
        with self.assertRaisesRegex(ProvisioningRefusal, 'POLICY_SELECTION'):
            selected.provision(wrong_scope)
        self.assertEqual(selected.inspect()['state'], 'INTENT_ONLY')
        self.assertFalse(selected.store.exists())
        self.assertFalse(selected.policy.exists())
        extra = FixtureProvisioner(self.plan('extra-authority', 'second-store'), self.engine)
        def extra_field(public, plan):
            value = json.loads(fixture_policy(public, plan))
            value['effect_authorization'] = 'fixture-must-not-grant'
            return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
        with self.assertRaisesRegex(ProvisioningRefusal, 'POLICY_SELECTION'):
            extra.provision(extra_field)
        self.assertFalse(extra.policy.exists())
        self.assertFalse(extra.store.exists())

    def test_key_fsync_failure_preserves_intent_before_store_effect(self):
        selected = FixtureProvisioner(self.plan('fsync-fault'), self.engine)
        original_fsync = os.fsync
        def fail_private_key(fd):
            path = os.readlink('/proc/self/fd/' + str(fd))
            if path == str(selected.key):
                raise OSError('fixture key fsync fault')
            return original_fsync(fd)
        with patch.object(module.os, 'fsync', side_effect=fail_private_key):
            with self.assertRaisesRegex(OSError, 'fixture key fsync fault'):
                selected.provision(fixture_policy)
        self.assertTrue(selected.intent.exists() and selected.key.exists())
        self.assertFalse(selected.store.exists() or selected.result.exists())
        self.assertEqual(selected.inspect()['state'], 'INTENT_ONLY')

    def test_result_extra_field_and_nonfinite_refuse(self):
        selected = FixtureProvisioner(self.plan('tampered-result'), self.engine)
        selected.provision(fixture_policy)
        result = json.loads(selected.result.read_bytes())
        result['undeclared'] = 'extra'
        selected.result.write_bytes(json.dumps(result).encode())
        with self.assertRaisesRegex(ProvisioningRefusal, 'RESULT_CHANGED'):
            selected.inspect()
        with self.assertRaisesRegex(ProvisioningRefusal, 'NONFINITE_RECORD'):
            module._parse(b'{"n":NaN}')

    def test_revocation_archive_interposition_keeps_foreign_bytes(self):
        selected = FixtureProvisioner(self.plan('archive-race'), self.engine)
        selected.provision(fixture_policy)
        original_rename = module._rename_no_replace
        def interpose(source, target):
            Path(target).write_bytes(b'foreign owned archive')
            os.chmod(target, 0o600)
            return original_rename(source, target)
        with patch.object(module, '_rename_no_replace', side_effect=interpose):
            with self.assertRaises(FileExistsError):
                selected.revoke()
        self.assertEqual(selected.archived_policy.read_bytes(), b'foreign owned archive')
        self.assertTrue(selected.policy.exists())
        self.assertEqual(selected.inspect()['state'], 'REVOKE_UNKNOWN')
        with self.assertRaisesRegex(ProvisioningRefusal, 'CHANNEL_REVOKED'):
            selected.challenge_nonce()

    def test_revoked_policy_name_dangling_symlink_refuses_complete(self):
        selected = FixtureProvisioner(self.plan('revoked-link'), self.engine)
        selected.provision(fixture_policy)
        selected.revoke()
        self.assertEqual(selected.inspect()['state'], 'COMPLETE_REVOKED')
        selected.policy.symlink_to(self.root / 'missing-foreign-policy')
        with self.assertRaisesRegex(ProvisioningRefusal, 'REVOKE_CHANGED'):
            selected.inspect()

    def test_actual_posture_and_external_root_refuse(self):
        plan = self.plan('scope')
        with self.assertRaisesRegex(ProvisioningRefusal, 'PLAN_SCOPE'):
            FixtureProvisioner(FixturePlan(**{**plan.__dict__, 'posture': 'actual'}), self.engine)
        with self.assertRaisesRegex(ProvisioningRefusal, 'FIXTURE_ROOT_ONLY'):
            FixtureProvisioner(FixturePlan(**{**plan.__dict__, 'owned_root': str(ROOT)}), self.engine)

    def test_orphan_store_without_intent_is_unknown(self):
        selected = FixtureProvisioner(self.plan('orphan'), self.engine)
        self.assertEqual(selected.inspect(), {'state': 'ABSENT', 'effect': 'none'})
        selected.store.mkdir(mode=0o700)
        self.assertEqual(selected.inspect(), {'state': 'UNKNOWN', 'effect': 'unknown'})
        with self.assertRaisesRegex(ProvisioningRefusal, 'PREIMAGE_EXISTS'):
            selected.provision(fixture_policy)

    def test_dangling_state_names_never_prove_absence_or_completion(self):
        selected = FixtureProvisioner(self.plan('dangling'), self.engine)
        missing = self.root / 'missing-target'
        selected.intent.symlink_to(missing)
        with self.assertRaisesRegex(ProvisioningRefusal, 'FILE_CUSTODY'):
            selected.inspect()
        selected.intent.unlink()
        selected.provision(fixture_policy)
        selected.revocation_intent.symlink_to(missing)
        with self.assertRaisesRegex(ProvisioningRefusal, 'FILE_CUSTODY'):
            selected.inspect()
        with self.assertRaisesRegex(ProvisioningRefusal, 'CHANNEL_REVOKED'):
            selected.challenge_nonce()
        selected.revocation_intent.unlink()
        selected.revocation.symlink_to(missing)
        with self.assertRaisesRegex(ProvisioningRefusal, 'REVOKE_INCOMPLETE'):
            selected.inspect()
        selected.revocation.unlink()
        selected.archived_policy.symlink_to(missing)
        with self.assertRaisesRegex(ProvisioningRefusal, 'REVOKE_INCOMPLETE'):
            selected.inspect()
        with self.assertRaisesRegex(ProvisioningRefusal, 'REVOKE_INCOMPLETE'):
            selected.revoke()
        selected.archived_policy.unlink()
        saved = self.root / 'journal' / 'saved-result.json'
        selected.result.rename(saved)
        selected.result.symlink_to(missing)
        with self.assertRaisesRegex(ProvisioningRefusal, 'FILE_CUSTODY'):
            selected.inspect()
        selected.result.unlink()
        saved.rename(selected.result)
        self.assertEqual(selected.inspect()['state'], 'COMPLETE')

    def test_input_ancestor_symlink_and_wrong_owner_refuse(self):
        plan = self.plan('unsafe')
        nested = self.root / 'inputs' / 'nested'
        nested.symlink_to(self.root / 'inputs', target_is_directory=True)
        linked = FixturePlan(**{**plan.__dict__, 'source_ref': str(nested / self.input_paths[0].name)})
        with self.assertRaisesRegex(ProvisioningRefusal, 'DIRECTORY_CUSTODY'):
            FixtureProvisioner(linked, self.engine)
        with patch.object(module.os, 'geteuid', return_value=os.geteuid() + 1):
            with self.assertRaisesRegex(ProvisioningRefusal, 'FIXTURE_ROOT_MODE'):
                FixtureProvisioner(plan, self.engine)

    def test_restart_wrong_operator_refuses_without_revoking_prior(self):
        first = FixtureProvisioner(self.plan('run_one'), self.engine)
        first.provision(fixture_policy)
        next_plan = self.plan('run_two', base_head_sha256=first.inspect()['head_sha256'])
        changed = FixturePlan(**{**next_plan.__dict__,
                                 'operator_ref': 'role:candidate-other'})
        second = FixtureProvisioner(changed, self.engine)
        with self.assertRaisesRegex(ProvisioningRefusal, 'RESTART_CONTINUITY'):
            second.restart_channel(first, fixture_policy)
        self.assertEqual(first.inspect()['state'], 'COMPLETE')
        self.assertFalse(first.revocation_intent.exists())

    def test_root_replacement_and_policy_tamper_refuse(self):
        selected = FixtureProvisioner(self.plan('root_guard'), self.engine)
        selected.provision(fixture_policy)
        public_mode = stat.S_IMODE(selected.public.stat().st_mode)
        os.chmod(selected.public, 0o666)
        with self.assertRaisesRegex(ProvisioningRefusal, 'FILE_CUSTODY'):
            selected.inspect()
        os.chmod(selected.public, public_mode)
        os.chmod(selected.policy, 0o644)
        with self.assertRaisesRegex(ProvisioningRefusal, 'FILE_CUSTODY'):
            selected.inspect()
        os.chmod(selected.policy, 0o600)
        old = self.root / 'channels-old'
        (self.root / 'channels').rename(old)
        (self.root / 'channels').mkdir(mode=0o700)
        with self.assertRaisesRegex(ProvisioningRefusal, 'DIRECTORY_CHANGED'):
            selected.challenge_nonce()

    def test_expired_selection_still_allows_read_only_inspection(self):
        selected = FixtureProvisioner(self.plan('expiry'), self.engine)
        selected.provision(fixture_policy)
        actual_datetime = module.datetime
        class ExpiredClock(datetime):
            @classmethod
            def now(cls, tz=None):
                return actual_datetime.now(tz) + timedelta(days=1)
        module.datetime = ExpiredClock
        try:
            self.assertEqual(selected.inspect()['state'], 'COMPLETE')
            with self.assertRaisesRegex(ProvisioningRefusal, 'PLAN_PERIOD'):
                selected.challenge_nonce()
            # Cleanup/revocation is permitted after positive expiry.
            selected.revoke()
            self.assertEqual(selected.inspect()['state'], 'COMPLETE_REVOKED')
        finally:
            module.datetime = actual_datetime


if __name__ == '__main__':
    unittest.main()
