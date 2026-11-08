import sys,types,importlib,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'))
DELTA=HERE/'integrated-resolver-delta-0001'
meta=json.loads((DELTA/'DELTA-PINS.json').read_bytes())
for row in meta['postimages']:
 assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
pkg=types.ModuleType('_t22_actual71_fixture_source');pkg.__path__=[str(DELTA)];sys.modules[pkg.__name__]=pkg
bridge=types.ModuleType(pkg.__name__+'.source_bridge');bridge.ROOT=ROOT;sys.modules[bridge.__name__]=bridge
S=importlib.import_module(pkg.__name__+'.fixture_resolution_source')
def selected_inputs():
 private=Path.home()/'.local/share/cyberalchemy-lab/t22-native-agent-diagnostics/91755e756e7543e6a42e664fafa744b2'
 return (json.loads((HERE/'LIVE-NATIVE-AGENT-COLD-API71-0001.json').read_bytes()),json.loads((HERE/'NATIVE-AGENT-COLD-CALL-API71-0002.json').read_bytes()),(private/'candidate.json').read_bytes(),json.loads((private/'request.json').read_bytes()))

"""Actual native-origin fixture successor and hostile input checks."""
import copy
from datetime import datetime, timedelta, timezone
import unittest
from cryptography.exceptions import InvalidSignature

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import base64


class ResolutionSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sub,cls.obs,cls.raw,cls.req=selected_inputs()
        cls.now=datetime.now(timezone.utc)
        cls.key=Ed25519PrivateKey.generate()
        cls.source=S.build(submission=cls.sub,observation=cls.obs,candidate_raw=cls.raw,
            request=cls.req,now=cls.now,period_end='2026-10-25T05:08:32.938122+00:00',signing_key=cls.key)
    def verify(self,source,**updates):
        inputs=dict(selected_public_hex=self.source['issuer_public_hex'],
            selected_submission_sha256=S.sha(S.canon(self.sub)),
            selected_source_cut=self.sub['source_cut'],now=self.now)
        inputs.update(updates)
        return S.verify(source,**inputs)
    def test_signed_actual_origin_schema_valid_candidate_only(self):
        self.assertTrue(self.verify(self.source))
        self.assertEqual(len(self.source['members']),7)
        self.assertEqual(self.source['members']['challenge-event']['payload']['response_state'],'deferred')
        self.assertEqual(self.source['envelope']['payload']['actual_owner_outcome'],None)
        self.assertEqual(self.source['members']['challenge-event']['payload']['challenger_ref'],self.sub['agent_instance_ref'])
    def test_changed_native_receipt_refuses(self):
        changed=copy.deepcopy(self.sub);changed['challenge_proposal_ref']+=':changed'
        with self.assertRaises(ValueError):
            S.build(submission=changed,observation=self.obs,candidate_raw=self.raw,
                request=self.req,now=self.now,period_end='2026-10-25T05:08:32.938122+00:00')
    def test_changed_original_candidate_refuses(self):
        with self.assertRaises(ValueError):
            S.build(submission=self.sub,observation=self.obs,candidate_raw=self.raw+b' ',
                request=self.req,now=self.now,period_end='2026-10-25T05:08:32.938122+00:00')
    def test_changed_decision_or_response_refuses(self):
        for field in ['decision','challenge-event']:
            changed=copy.deepcopy(self.source);changed['members'][field]['name']+=' changed'
            with self.assertRaises(ValueError):self.verify(changed)
        changed=copy.deepcopy(self.source);changed['response']['challenger_ref']='agent-instance:foreign'
        with self.assertRaises(ValueError):self.verify(changed)
    def test_resigned_original_evidence_omission_refuses(self):
        changed=copy.deepcopy(self.source)
        changed['response']['evidence_bindings'].pop()
        changed['envelope']['payload']['response_sha256']=S.sha(S.canon(changed['response']))
        changed['envelope']['signature']=base64.b64encode(self.key.sign(S.canon(changed['envelope']['payload']))).decode()
        with self.assertRaisesRegex(ValueError,'original native challenge evidence omitted'):
            self.verify(changed)
    def test_resigned_original_request_substitution_refuses(self):
        changed=copy.deepcopy(self.source)
        changed['original_request']['ground']='invented-ground'
        changed['envelope']['payload']['original_request_sha256']=S.sha(S.canon(changed['original_request']))
        changed['envelope']['signature']=base64.b64encode(self.key.sign(S.canon(changed['envelope']['payload']))).decode()
        with self.assertRaisesRegex(ValueError,'original native request bytes changed'):
            self.verify(changed)
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
