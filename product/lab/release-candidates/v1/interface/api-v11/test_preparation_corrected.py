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

    def test_historical_source_session_memory_never_returns_as_body(self):
        from artifact_model import artifact_ref
        from fixtures import call
        from handlers import cut
        subjects=[s for s in self.view.subjects.values() if s['kind']=='agent-session' and s['record'].get('payload',{}).get('session_memory')]
        self.assertTrue(subjects,'independent R02 audit source Session memory input remains explicit')
        c=call(self.channel.context,'artifact.inspect',cut(self.view),artifact=artifact_ref(self.view,subjects[0]),include=['body'])
        r=self.service.call(compact(c));self.assertEqual(r['message']['code'],'private-material-excluded')
        self.assertNotIn('envelope',r['message'])

    def test_protected_source_session_exact_metadata_remains_inspectable(self):
        from artifact_model import artifact_ref
        from fixtures import call
        from handlers import cut
        s=next(s for s in self.view.subjects.values() if s['kind']=='agent-session')
        c=call(self.channel.context,'artifact.inspect',cut(self.view),artifact=artifact_ref(self.view,s),include=['contract','lifecycle','gaps'])
        r=self.service.call(compact(c));self.assertEqual(r['kind'],'result');self.assertIsNone(r['message']['envelope'])

if __name__=='__main__':original.unittest.main(verbosity=2)
