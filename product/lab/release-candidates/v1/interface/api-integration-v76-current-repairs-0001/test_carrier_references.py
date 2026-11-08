"""Actual independently selected reference closure and original-byte refusals."""
import copy,unittest
from . import protocol as P,fixtures as F,handlers as H,workspace as W
from . import test_challenge_api as C,workflow_fixture as WF
SOURCE=None;PROFILE=None
class CarrierReferenceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        C.SOURCE=SOURCE;C.PROFILE=PROFILE;C.CurrentChallenge.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls):C.CurrentChallenge.tearDownClass.__func__(cls)
    invoke=C.CurrentChallenge.invoke
    journal=C.CurrentChallenge.journal
    def submitted(self):
        service,submit,compose,witness=self.enterContext(WF.example(self.view,self.schemas,resolve_references=True))
        result=self.invoke(service,submit());self.assertEqual(result['kind'],'result',result)
        return service,compose(result['message']),witness
    def call(self,service,proposal,name='change.validate'):
        value=F.call(service.channel.context,'lab.status',H.cut(self.view))
        value.update(operation=name,message=copy.deepcopy(proposal),
            idempotency_key=proposal['idempotency_key'] if name=='change.prepare' else 'fixture:reference-validation',
            deadline=service.channel.context['expires_at'])
        return value
    def test_01_three_carriers_have_separate_typed_reference_evidence(self):
        service,proposal,_=self.submitted();manifest=copy.deepcopy(service.vault.manifest)
        reply=self.invoke(service,self.call(service,proposal));self.assertEqual(reply['kind'],'result',reply)
        report=reply['message'];self.assertEqual(report['result'],'pass',report)
        self.assertEqual(report['gaps'],[])
        selected=[c for c in report['checks'] if c['check_ref'].startswith('check:selected-carrier-reference-')]
        self.assertEqual(len(selected),3)
        classes=set()
        for check in selected:
            self.assertEqual(check['result'],'pass')
            detail=P.frame_parse(service.vault.object_read(check['evidence_bindings'][0]))['details']
            self.assertTrue(detail['reference_closure_only'])
            self.assertFalse(detail['current_owner_authority_verified'])
            self.assertFalse(detail['canonical_admission_granted'])
            classes.update(row['reference_class'] for row in detail['typed_references'])
        self.assertIn('signed-artifact-revision',classes)
        self.assertIn('operational-validation-receipt',classes)
        self.assertIn('bound-original-document',classes)
        self.assertIn('declared-workflow-type-reference',classes)
        prepared=self.invoke(service,self.call(service,proposal,'change.prepare'))
        self.assertEqual(prepared['kind'],'result',prepared)
        self.assertEqual(len(prepared['message']['stable_core_bindings']),5)
        self.assertEqual(len(prepared['message']['gaps']),1)
        self.assertEqual(prepared['message']['posture'],'blocked')
        self.assertEqual(service.vault.manifest,manifest)
        self.assertEqual(P.compact(self.view.data['projection']),self.projection)
    def test_02_substituted_original_source_refused_before_claim(self):
        service,proposal,_=self.submitted()
        challenge=P.frame_parse(service.vault.object_read(service.channel.policy['challenge_control']['routing_binding']))
        row=next(r for r in challenge['accepted_evidence'] if r['kind']=='source')
        selected=service.vault.inputs[row['binding']['ref']]
        path=service.vault.root/selected['path'];path.write_bytes(path.read_bytes()+b' ')
        before=self.journal(service);reply=self.invoke(service,self.call(service,proposal))
        self.assertEqual(reply['schema_version'],'lab-api-transport-error/v1-candidate')
        self.assertEqual(reply['code'],'unauthenticated-channel')
        self.assertEqual(self.journal(service),before)
    def test_03_missing_original_receipt_refused_before_claim(self):
        service,proposal,_=self.submitted()
        challenge=P.frame_parse(service.vault.object_read(service.channel.policy['challenge_control']['routing_binding']))
        row=next(r for r in challenge['accepted_evidence'] if r['kind']=='validation-receipt')
        (service.vault.root/service.vault.inputs[row['binding']['ref']]['path']).unlink()
        before=self.journal(service);reply=self.invoke(service,self.call(service,proposal))
        self.assertEqual(reply['schema_version'],'lab-api-transport-error/v1-candidate')
        self.assertEqual(reply['code'],'unauthenticated-channel')
        self.assertEqual(self.journal(service),before)
