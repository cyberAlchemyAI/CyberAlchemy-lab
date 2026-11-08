"""Actual native-origin fixture successor and hostile input checks."""
import copy
from datetime import datetime, timedelta, timezone
import unittest
from cryptography.exceptions import InvalidSignature
import fixture_resolution_source as S
from build_fixture_resolution_source import selected_inputs

class ResolutionSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sub,cls.obs,cls.raw,cls.req=selected_inputs()
        cls.now=datetime.now(timezone.utc)
        cls.source=S.build(submission=cls.sub,observation=cls.obs,candidate_raw=cls.raw,
            request=cls.req,now=cls.now,period_end='2026-10-24T17:54:44.262511+00:00')
    def verify(self,source,**updates):
        inputs=dict(selected_public_hex=self.source['issuer_public_hex'],
            selected_submission_sha256=S.sha(S.canon(self.sub)),
            selected_source_cut=self.sub['source_cut'],now=self.now)
        inputs.update(updates)
        return S.verify(source,**inputs)
    def test_signed_actual_origin_schema_valid_candidate_only(self):
        self.assertTrue(self.verify(self.source))
        self.assertEqual(len(self.source['members']),7)
        self.assertEqual(self.source['envelope']['payload']['actual_owner_outcome'],None)
        self.assertEqual(self.source['members']['challenge-event']['payload']['challenger_ref'],self.sub['agent_instance_ref'])
    def test_changed_native_receipt_refuses(self):
        changed=copy.deepcopy(self.sub);changed['challenge_proposal_ref']+=':changed'
        with self.assertRaises(ValueError):
            S.build(submission=changed,observation=self.obs,candidate_raw=self.raw,
                request=self.req,now=self.now,period_end='2026-10-24T17:54:44.262511+00:00')
    def test_changed_original_candidate_refuses(self):
        with self.assertRaises(ValueError):
            S.build(submission=self.sub,observation=self.obs,candidate_raw=self.raw+b' ',
                request=self.req,now=self.now,period_end='2026-10-24T17:54:44.262511+00:00')
    def test_changed_decision_or_response_refuses(self):
        for field in ['decision','challenge-event']:
            changed=copy.deepcopy(self.source);changed['members'][field]['name']+=' changed'
            with self.assertRaises(ValueError):self.verify(changed)
        changed=copy.deepcopy(self.source);changed['response']['challenger_ref']='agent-instance:foreign'
        with self.assertRaises(ValueError):self.verify(changed)
    def test_changed_signed_outcome_refuses(self):
        changed=copy.deepcopy(self.source);changed['envelope']['payload']['selected_fixture_outcome']='accept'
        with self.assertRaises(InvalidSignature):self.verify(changed)
    def test_wrong_signer_cut_or_submission_refuses(self):
        for extra in [dict(selected_public_hex='00'*32),dict(selected_submission_sha256='00'*32),dict(selected_source_cut={})]:
            with self.assertRaises((ValueError,InvalidSignature)):self.verify(self.source,**extra)
    def test_expired_and_future_source_refuse(self):
        for offset in [-1,3601]:
            with self.assertRaises(ValueError):self.verify(self.source,now=self.now+timedelta(seconds=offset))

if __name__=='__main__':unittest.main()
