"""Synthetic one-shot filesystem tests; no real Reader or private body."""
import datetime as dt
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import controller as C

NOW = dt.datetime(2026,10,20,18,30,tzinfo=dt.timezone.utc)
END = dt.datetime(2026,10,21,15,tzinfo=dt.timezone.utc)


class ControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selection = C.preflight(NOW)['selected']

    def fixture(self):
        return tempfile.TemporaryDirectory(prefix='fixture-signed-scope-',dir='/tmp')

    def test_public_selection_pins_stage_reader_and_separate_attempt(self):
        value = C.preflight(NOW)
        self.assertEqual(value['status'],'EFFECT_DISABLED_DOCKER_SIGNED_SCOPE_RELEASE_PENDING')
        self.assertEqual(value['stage_review_sha256'],C.STAGE_REVIEW_SHA)
        self.assertEqual(value['selected']['reader']['sha256'],
                         C.checked_adapter().READER_CODE_SHA)
        self.assertEqual(value['selected']['reader']['method'],'SelectedReader.open_signed')
        self.assertFalse(os.path.lexists(C.ATTEMPT))
        self.assertEqual(value['auth'],'UNMINTED_UNSELECTED')

    def test_fixture_success_is_sanitized_provisional_and_no_retry(self):
        with self.fixture() as root:
            reader = C.SyntheticSelectedReader(self.selection)
            value = C.run_fixture_once(root,self.selection,reader=reader)
            self.assertEqual(value['status'],
                'PROVISIONAL_FIXTURE_SIGNED_SCOPE_EXTERNAL_OS_REVIEW_REQUIRED')
            self.assertEqual(value['real_effect'],'NOT_RUN')
            self.assertEqual(reader.calls[0],'open_signed')
            self.assertEqual(reader.calls[-1],'close')
            attempt = Path(root)/'attempt.claim'
            self.assertTrue(attempt.is_file())
            raw = (Path(root)/'signed-scope.attestation.json').read_bytes()
            self.assertEqual(C.sha(raw),value['attestation_sha256'])
            record = json.loads(raw)
            self.assertEqual(record['scope_ref'],self.selection['scope_expected'])
            self.assertEqual(record['reader_code_sha256'],C.checked_adapter().READER_CODE_SHA)
            self.assertEqual(record['stage_effect_review_sha256'],C.STAGE_REVIEW_SHA)
            self.assertEqual(record['authority_effect'],'none')
            self.assertIsNone(record['actual_owner_outcome'])
            self.assertFalse(record['retry_allowed'])
            self.assertNotIn('raw_signed_view',record)
            self.assertEqual(os.stat(attempt).st_mode & 0o777,0o600)
            self.assertEqual(os.stat(Path(root)/'signed-scope.attestation.json').st_mode & 0o777,0o600)
            self.assertEqual(C.sha(attempt.read_bytes()),value['marker_sha256'])
            with self.assertRaisesRegex(C.Refused,'ATTEMPT_CONSUMED_NO_RETRY'):
                C.run_fixture_once(root,self.selection)

    def test_postclaim_premarker_is_unknown_and_consumed(self):
        with self.fixture() as root:
            with self.assertRaises(C.Unknown) as caught:
                C.run_fixture_once(root,self.selection,fault='after_claim')
            self.assertFalse(caught.exception.retry_allowed)
            self.assertEqual((Path(root)/'attempt.claim').read_bytes(),b'')
            with self.assertRaises(C.Refused):C.run_fixture_once(root,self.selection)

    def test_marker_before_open_and_later_failure_retains_it(self):
        for fault in ('after_marker','inside_signed','after_close',
                      'attestation_publication'):
            with self.subTest(fault=fault),self.fixture() as root:
                reader=C.SyntheticSelectedReader(self.selection)
                with self.assertRaises(C.Unknown):
                    C.run_fixture_once(root,self.selection,reader=reader,fault=fault)
                self.assertTrue((Path(root)/'attempt.claim').is_file())
                self.assertFalse((Path(root)/'signed-scope.attestation.json').exists())
                if fault=='after_marker':self.assertEqual(reader.calls,[])
                with self.assertRaises(C.Refused):C.run_fixture_once(root,self.selection)

    def test_bad_signed_scope_basis_final_guard_or_close_are_unknown(self):
        for change in ({'bad_scope':True},{'wrong_basis':True},
                       {'fail_final':True},{'fail_close':True}):
            with self.subTest(change=change),self.fixture() as root:
                reader=C.SyntheticSelectedReader(self.selection,**change)
                with self.assertRaises(C.Unknown):
                    C.run_fixture_once(root,self.selection,reader=reader)
                self.assertTrue((Path(root)/'attempt.claim').is_file())
                self.assertFalse((Path(root)/'signed-scope.attestation.json').exists())
                if change.get('fail_final'):
                    self.assertEqual(reader.calls.count('signed_guard'),3)
                    self.assertEqual(reader.calls[-1],'close')

    def test_expired_period_poisoned_before_private_open(self):
        with self.fixture() as root:
            reader=C.SyntheticSelectedReader(self.selection)
            with self.assertRaises(C.Unknown):
                C.run_fixture_once(root,self.selection,reader=reader,at_close=END)
            self.assertEqual(reader.calls,[])
            self.assertTrue((Path(root)/'attempt.claim').is_file())

    def test_replaced_claim_before_first_postcreate_check_refuses(self):
        with self.fixture() as root:
            reader=C.SyntheticSelectedReader(self.selection)
            original=os.open
            def swap(path,flags,*args,**kwargs):
                fd=original(path,flags,*args,**kwargs)
                if path=='attempt.claim' and flags & os.O_EXCL:
                    os.rename(Path(root)/'attempt.claim',Path(root)/'detached-original.claim')
                    replacement=original(Path(root)/'attempt.claim',
                                         os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
                    os.close(replacement)
                return fd
            with mock.patch.object(C.os,'open',side_effect=swap):
                with self.assertRaises(C.Unknown):
                    C.run_fixture_once(root,self.selection,reader=reader)
            self.assertEqual(reader.calls,[])
            self.assertEqual((Path(root)/'detached-original.claim').read_bytes(),b'')
            self.assertEqual((Path(root)/'attempt.claim').read_bytes(),b'')
            self.assertFalse((Path(root)/'signed-scope.attestation.json').exists())

    def test_replaced_claim_after_marker_refuses_before_signed(self):
        with self.fixture() as root:
            reader=C.SyntheticSelectedReader(self.selection)
            original=C._write_claim_held
            def swap(parentfd,claimfd,name,raw):
                digest=original(parentfd,claimfd,name,raw)
                os.rename(Path(root)/'attempt.claim',Path(root)/'detached-original.claim')
                replacement=os.open(Path(root)/'attempt.claim',
                                    os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
                os.close(replacement)
                return digest
            with mock.patch.object(C,'_write_claim_held',side_effect=swap):
                with self.assertRaises(C.Unknown):
                    C.run_fixture_once(root,self.selection,reader=reader)
            self.assertEqual(reader.calls,[])
            self.assertTrue((Path(root)/'detached-original.claim').is_file())
            self.assertFalse((Path(root)/'signed-scope.attestation.json').exists())

    def test_held_claim_marker_tamper_refuses_before_signed(self):
        with self.fixture() as root:
            reader=C.SyntheticSelectedReader(self.selection)
            original=C._write_claim_held
            def tamper(parentfd,claimfd,name,raw):
                digest=original(parentfd,claimfd,name,raw)
                os.pwrite(claimfd,b'X',0)
                return digest
            with mock.patch.object(C,'_write_claim_held',side_effect=tamper):
                with self.assertRaises(C.Unknown):
                    C.run_fixture_once(root,self.selection,reader=reader)
            self.assertEqual(reader.calls,[])
            self.assertFalse((Path(root)/'signed-scope.attestation.json').exists())

    def test_wrong_reader_type_rejected_before_claim(self):
        with self.fixture() as root:
            with self.assertRaisesRegex(C.Refused,'SYNTHETIC_READER_ONLY'):
                C.run_fixture_once(root,self.selection,reader=object())
            self.assertFalse((Path(root)/'attempt.claim').exists())

    def test_review_or_reader_pin_drift_refuses_preflight(self):
        with mock.patch.object(C,'STAGE_REVIEW_SHA','0'*64):
            with self.assertRaisesRegex(C.Refused,'STAGE_EFFECT_REVIEW_DRIFT'):
                C.preflight(NOW)
        with mock.patch.object(C,'ADAPTER_CODE_SHA','0'*64):
            with self.assertRaises(C.Refused):C.preflight(NOW)

    def test_real_signed_reopen_authority_policy_docker_all_refuse(self):
        for fn in (C.run_real_once,C.issue_auth_or_grant,
                   C.create_private_policy,C.launch_docker):
            with self.assertRaisesRegex(C.Refused,'DISABLED'):
                fn()


if __name__ == '__main__':unittest.main(verbosity=2)
