"""Real submitted challenge outputs consumed by the original generic validator."""
import copy
import unittest
from . import protocol as P,fixtures as F,handlers as H,jcs
from . import test_challenge_api as C
SOURCE=None;PROFILE=None
class GeneratedWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        C.SOURCE=SOURCE;C.PROFILE=PROFILE;C.CurrentChallenge.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls):C.CurrentChallenge.tearDownClass.__func__(cls)
    example=C.CurrentChallenge.example
    invoke=C.CurrentChallenge.invoke
    journal=C.CurrentChallenge.journal
    def submitted(self):
        service,request,witness=self.example();reply=self.invoke(service,request())
        self.assertEqual(reply['kind'],'result',reply)
        return service,reply['message'],witness
    def validation(self,service,proposal,key='fixture:challenge-validation'):
        call=F.call(service.channel.context,'lab.status',H.cut(self.view))
        call.update(operation='change.validate',idempotency_key=key,deadline=service.channel.context['expires_at'],message=copy.deepcopy(proposal))
        return call
    def test_01_actual_generated_proposal_reaches_original_four_target_validation(self):
        service,proposal,witness=self.submitted();manifest=copy.deepcopy(service.vault.manifest);inputs=copy.deepcopy(service.vault.inputs)
        reply=self.invoke(service,self.validation(service,proposal));self.assertEqual(reply['kind'],'result',reply)
        report=reply['message'];self.assertTrue(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:validation-report:v1-candidate',report))
        self.assertEqual(report['result'],'not-evaluable');self.assertEqual(report['authority_effect'],'none')
        checks={c['check_ref']:c for c in report['checks']}
        for name in ('exact-source-target-schema-core','declared-typed-connection-closure','private-boundary'):
            self.assertEqual(checks['check:'+name]['result'],'pass')
        core_check=P.frame_parse(service.vault.object_read(checks['check:exact-source-target-schema-core']['evidence_bindings'][0]))
        self.assertEqual(core_check['details']['target_count'],4)
        self.assertEqual(service.vault.manifest,manifest);self.assertEqual(service.vault.inputs,inputs)
        self.assertEqual(P.compact(self.view.data['projection']),self.projection)
        self.assertTrue(report['gaps'])
        unresolved=[c for c in report['checks'] if c['check_ref'].startswith('check:remaining-domain-reference-')]
        self.assertEqual(len(unresolved),2)
        for check in unresolved:
            self.assertEqual(check['result'],'not-evaluable')
            detail=P.frame_parse(service.vault.object_read(check['evidence_bindings'][0]))
            self.assertIn('full domain reference resolver',detail['details']['reason'])
            self.assertIn(detail['details']['carrier_ref'],[t['artifact']['carrier_ref'] for t in proposal['targets']])
        call=self.validation(service,proposal);before=self.journal(service);call['call_id']+=':retry'
        retry=self.invoke(service,call);self.assertEqual(retry['message'],report);self.assertEqual(self.journal(service),before)
    def test_02_modified_generated_target_refused_before_new_claim(self):
        service,proposal,_=self.submitted();call=self.validation(service,proposal)
        call['message']['targets'][0]['requested_effect']+=' edited';before=self.journal(service)
        reply=self.invoke(service,call);self.assertEqual(reply['kind'],'error');self.assertEqual(reply['message']['code'],'invalid-contract')
        self.assertEqual(self.journal(service),before)
    def test_03_unknown_producer_key_cannot_select_output_metadata(self):
        service,proposal,_=self.submitted();proposal['idempotency_key']='not-a-completed-producer'
        call=self.validation(service,proposal);before=self.journal(service);reply=self.invoke(service,call)
        self.assertEqual(reply['kind'],'error');self.assertEqual(reply['message']['code'],'invalid-contract');self.assertEqual(self.journal(service),before)
    def test_04_pending_producer_cannot_supply_completed_output(self):
        service,proposal,_=self.submitted()
        namespace=jcs.namespace('challenge.submit',proposal['idempotency_key'],service.channel.context)
        (service.vault.root/'journal'/(namespace+'.result.json')).unlink()
        before=self.journal(service);reply=self.invoke(service,self.validation(service,proposal))
        self.assertEqual(reply['kind'],'error');self.assertEqual(reply['message']['code'],'invalid-contract');self.assertEqual(self.journal(service),before)
    def test_05_missing_original_output_refused_without_reconstruction_writes(self):
        service,proposal,_=self.submitted();content=proposal['targets'][0]['content']
        (service.vault.root/'objects'/(content['byte_sha256']+'.json')).unlink()
        before=self.journal(service);reply=self.invoke(service,self.validation(service,proposal))
        self.assertEqual(reply['kind'],'error');self.assertEqual(reply['message']['code'],'invalid-contract');self.assertEqual(self.journal(service),before)
