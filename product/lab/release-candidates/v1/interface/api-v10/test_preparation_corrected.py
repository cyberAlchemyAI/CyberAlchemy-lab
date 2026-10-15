"""Preserve original guards; correct only the below-schema response ceiling expectation."""
import test_preparation as original
from unittest.mock import patch
from example_fixture import candidate_call
from protocol import compact

class CorrectedPreparation(original.Preparation):
    def test_small_receipt_budget_refused_before_effect(self):
        # The exact wire contract requires >=4096. A ceiling of 1 is malformed
        # before dispatch; the domain budget gate is never reached.
        c=candidate_call(self.service,self.target);c['max_response_bytes']=1
        with patch.object(self.service.candidates,'prepare',side_effect=AssertionError('must not dispatch')):
            r=self.service.call(compact(c))
        self.assertEqual(r['schema_version'],'lab-api-transport-error/v1-candidate')
        self.assertEqual(r['code'],'invalid-envelope')
        self.assertFalse(list((self.root/'workspace/journal').iterdir()))

    def test_root_dotdot_cannot_select_outside_owned_tmp(self):
        import copy
        from workspace import validate_scope
        policy=copy.deepcopy(self.channel.policy)
        policy['workspace']['root']='/tmp/../home/vlad_/projects/CyberAlchemy-lab'
        with self.assertRaises(Exception):validate_scope(policy)

    def test_all_private_pem_key_families_refused(self):
        from workspace import privacy
        for kind in ('RSA','EC','ENCRYPTED','OPENSSH',''):
            text='-----BEGIN '+(kind+' ' if kind else '')+'PRIVATE KEY-----'
            with self.assertRaises(Exception):privacy({'candidate_text':text})

if __name__=='__main__':original.unittest.main(verbosity=2)
