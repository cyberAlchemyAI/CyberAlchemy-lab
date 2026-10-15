"""Actual authentication, signed source, durable result and refused challenges."""
import copy
import unittest
from . import protocol as P,handlers as H,workspace as W,fixtures as F
from . import challenge_fixture as CF
from .guard import verify
SOURCE=None;PROFILE=None
class CurrentChallenge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify(SOURCE);cls.schemas=P.Schemas(PROFILE)
        cls.manager=P.source.replay_source('custody-participation');cls.view=cls.manager.__enter__()
        cls.projection=P.compact(cls.view.data['projection']);cls.witnesses=[]
    @classmethod
    def tearDownClass(cls):
        assert P.compact(cls.view.data['projection'])==cls.projection
        cls.manager.__exit__(None,None,None);verify(SOURCE)
    def example(self,**kwargs):return self.enterContext(CF.example(self.view,self.schemas,**kwargs))
    def invoke(self,service,call):
        raw=P.compact(call);reply=service.call(raw);W.privacy(reply)
        if 'kind' in reply:
            self.assertTrue(self.schemas.valid('api-reply',reply));self.assertEqual(reply['request_binding']['sha256'],P.source.sha(raw))
        self.witnesses.append({'call':copy.deepcopy(call),'reply':copy.deepcopy(reply)})
        return reply
    def journal(self,service):return {p.relative_to(service.vault.root).as_posix():p.read_bytes() for p in service.vault.root.rglob('*') if p.is_file()}
    def inspect(self,service):
        call=F.call(service.channel.context,'operation.inspect',H.cut(self.view))
        call['deadline']=service.channel.context['expires_at'];call['message']['lookup']={'operation':'challenge.submit','idempotency_key':'fixture:challenge-submit'}
        return self.invoke(service,call)
    def test_01_actual_challenge_proposal_preserves_exact_revision_and_original_bytes(self):
        service,request,witness=self.example();reply=self.invoke(service,request());self.assertEqual(reply['kind'],'result',reply)
        proposal=reply['message'];self.assertEqual(len(proposal['targets']),1)
        target=proposal['targets'][0];raw=service.vault.material({'ref':target['content']['content_ref'],'sha256':target['content']['byte_sha256']})
        self.assertEqual(raw,witness['candidate_original']);self.assertNotEqual(raw,self.view.handle.common.encoded(P.frame_parse(raw)))
        body=P.frame_parse(raw);self.assertEqual(body['payload']['subject_version_ref'],witness['subject']['version_ref'])
        self.assertEqual(body['payload']['response_state'],'open');self.assertEqual(body['payload']['resolution_decision_ref'],'none')
        self.assertEqual(proposal['connection_proposals'],[]);self.assertEqual(P.compact(self.view.data['projection']),self.projection)
        self.assertEqual(self.inspect(service)['kind'],'result')
    def test_02_actual_exact_retry_is_read_only(self):
        service,request,_=self.example();call=request();first=self.invoke(service,call);self.assertEqual(first['kind'],'result',first)
        before=self.journal(service);retry=copy.deepcopy(call);retry['call_id']+=':retry'
        second=self.invoke(service,retry);self.assertEqual(second['kind'],'result',second)
        self.assertEqual(second['message'],first['message']);self.assertEqual(self.journal(service),before)
    def test_03_undeclared_ground_refused_before_claim_without_file_changes(self):
        service,request,_=self.example();call=request();call['message']['ground']='invented-ground';before=self.journal(service)
        reply=self.invoke(service,call);self.assertEqual(reply['kind'],'error');self.assertEqual(reply['message']['code'],'invalid-contract')
        self.assertEqual(self.journal(service),before)
    def test_04_required_evidence_omission_refused_before_claim(self):
        service,request,_=self.example();call=request();call['message']['evidence_bindings']=call['message']['evidence_bindings'][:-1]
        before=self.journal(service);reply=self.invoke(service,call);self.assertEqual(reply['kind'],'error')
        self.assertEqual(reply['message']['code'],'invalid-contract');self.assertEqual(self.journal(service),before)
    def test_05_exact_subject_byte_substitution_refused(self):
        service,request,_=self.example();call=request();call['message']['subject']['byte_sha256']='0'*64
        before=self.journal(service);reply=self.invoke(service,call);self.assertEqual(reply['kind'],'error')
        self.assertEqual(reply['message']['code'],'invalid-contract');self.assertEqual(self.journal(service),before)
    def test_06_pending_claim_is_never_redispatched(self):
        service,request,_=self.example();call=request();service.vault.claim(call,P.compact(call),service.channel.context)
        before=self.journal(service);reply=self.invoke(service,call);self.assertEqual(reply['kind'],'error')
        self.assertEqual(reply['message']['code'],'recovery-required');self.assertEqual(self.journal(service),before)
    def test_07_actual_transport_requires_independent_challenge_grant(self):
        service,request,_=self.example(grant_challenge=False);before=self.journal(service)
        reply=self.invoke(service,request());self.assertEqual(reply['code'],'unsupported-operation');self.assertEqual(self.journal(service),before)
