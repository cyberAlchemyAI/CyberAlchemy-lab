"""Actual complete producer closure, original preparation and one pending review."""
import copy
import unittest
from . import protocol as P, fixtures as F, handlers as H, workspace as W
from . import test_challenge_api as C, workflow_fixture as WF
SOURCE = None
PROFILE = None

class WorkflowComposition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        C.SOURCE=SOURCE; C.PROFILE=PROFILE
        C.CurrentChallenge.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls):
        C.CurrentChallenge.tearDownClass.__func__(cls)
    invoke = C.CurrentChallenge.invoke
    journal = C.CurrentChallenge.journal
    def fixture(self):
        return self.enterContext(WF.example(self.view, self.schemas))
    def operation(self, service, name, message, key):
        if name == 'change.prepare': key = message['idempotency_key']
        call = F.call(service.channel.context, 'lab.status', H.cut(self.view))
        call.update(operation=name, message=copy.deepcopy(message), idempotency_key=key,
                    deadline=service.channel.context['expires_at'])
        return call
    def submitted(self):
        service, submit, compose, witness = self.fixture()
        reply = self.invoke(service, submit())
        self.assertEqual(reply['kind'], 'result', reply)
        return service, compose(reply['message']), witness
    def test_01_actual_submit_prepare_review_retry_inspection(self):
        service, proposal, witness = self.submitted()
        manifest = copy.deepcopy(service.vault.manifest)
        inputs = copy.deepcopy(service.vault.inputs)
        reply = self.invoke(service, self.operation(service, 'change.prepare', proposal, 'fixture:composed-prepare'))
        self.assertEqual(reply['kind'], 'result', reply)
        review = reply['message']
        self.assertEqual(len(review['stable_core_bindings']), 5)
        self.assertTrue(review['gaps'])
        call = self.operation(service, 'proposal.review', review, 'fixture:composed-review')
        reply = self.invoke(service, call)
        self.assertEqual(reply['kind'], 'result', reply)
        package = reply['message']
        self.assertEqual(package['human_checkpoint_count'], 1)
        self.assertEqual(package['ordered_core_bindings'], review['stable_core_bindings'])
        self.assertTrue(package['all_targets_materialized'])
        material = P.frame_parse(service.vault.object_read(package['manifest_binding']))
        self.assertEqual(len(material['targets']), 5)
        self.assertEqual(len(material['ordered_required_owner_responses']), 10)
        self.assertEqual(material['original_semantic_and_operational_gaps'], review['gaps'])
        self.assertIsNone(material['actual_owner_outcome'])
        self.assertFalse(material['current_owner_authority_verified'])
        self.assertEqual(material['repository_admissions_applied'], 0)
        self.assertEqual(material['runtime_activations'], 0)
        W.privacy(material)
        before = self.journal(service)
        call['call_id'] += ':retry'
        retry = self.invoke(service, call)
        self.assertEqual(retry['message'], package)
        self.assertEqual(self.journal(service), before)
        inspect = F.call(service.channel.context, 'operation.inspect', H.cut(self.view))
        inspect['deadline'] = service.channel.context['expires_at']
        inspect['message']['lookup'] = {'operation': 'proposal.review', 'idempotency_key': 'fixture:composed-review'}
        self.assertEqual(self.invoke(service, inspect)['kind'], 'result')
        self.assertEqual(service.vault.manifest, manifest)
        self.assertEqual(service.vault.inputs, inputs)
        self.assertEqual(P.compact(self.view.data['projection']), self.projection)
    def test_02_omitted_producer_member_refused_before_claim(self):
        service, proposal, _ = self.submitted()
        proposal['targets'].pop(0)
        before = self.journal(service)
        reply = self.invoke(service, self.operation(service, 'change.prepare', proposal, 'fixture:omission'))
        self.assertEqual(reply['kind'], 'error')
        self.assertEqual(reply['message']['code'], 'invalid-contract')
        self.assertEqual(self.journal(service), before)
    def test_03_changed_member_effect_refused_before_claim(self):
        service, proposal, _ = self.submitted()
        proposal['targets'][-1]['requested_effect'] += ' edited'
        before = self.journal(service)
        reply = self.invoke(service, self.operation(service, 'change.prepare', proposal, 'fixture:alteration'))
        self.assertEqual(reply['kind'], 'error')
        self.assertEqual(reply['message']['code'], 'invalid-contract')
        self.assertEqual(self.journal(service), before)
