"""Current signed-source API reviews, real permissions and durable idempotency."""
import base64
import copy
import unittest
from . import protocol as P, handlers as H, fixtures as F, workspace as W
from . import review_fixture as RF
from .guard import verify

PROFILE = None
SOURCE = None

class CurrentReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify(SOURCE)
        cls.schemas = P.Schemas(PROFILE)
        cls.manager = P.source.replay_source('custody-participation')
        cls.view = cls.manager.__enter__()
        cls.projection = P.compact(cls.view.data['projection'])
        cls.witnesses = []

    @classmethod
    def tearDownClass(cls):
        assert P.compact(cls.view.data['projection']) == cls.projection
        cls.manager.__exit__(None, None, None)
        verify(SOURCE)

    def example(self, **kwargs):
        return self.enterContext(RF.example(self.view, self.schemas, **kwargs))

    def invoke(self, service, value):
        raw = P.compact(value)
        reply = service.call(raw)
        W.privacy(reply)
        if 'kind' in reply:
            self.assertTrue(self.schemas.valid('api-reply', reply))
            self.assertEqual(reply['request_binding']['sha256'], P.source.sha(raw))
        self.witnesses.append({'call': copy.deepcopy(value), 'reply': copy.deepcopy(reply)})
        return reply

    def journal(self, service):
        return {path.relative_to(service.vault.root).as_posix(): path.read_bytes()
                for path in service.vault.root.rglob('*') if path.is_file()}

    def inspect(self, service):
        call = F.call(service.channel.context, 'operation.inspect', H.cut(self.view))
        call['message']['lookup'] = {'operation': 'proposal.review', 'idempotency_key': 'fixture:review'}
        return self.invoke(service, call)

    def manifest(self, service, reply):
        return P.frame_parse(service.vault.object_read(reply['message']['manifest_binding']))

    def test_00_actual_two_target_review_one_checkpoint(self):
        service, request, witness = self.example()
        reply = self.invoke(service, request())
        self.assertEqual(reply['kind'], 'result')
        result = reply['message']
        manifest = self.manifest(service, reply)
        self.assertEqual(result['human_checkpoint_count'], 1)
        self.assertEqual(result['atomicity_requirement'], 'all-or-nothing')
        self.assertEqual(len(result['ordered_core_bindings']), 2)
        self.assertEqual(len(manifest['targets']), 2)
        self.assertEqual(len(manifest['ordered_required_owner_responses']), 2)
        self.assertEqual(result['base_cut'], H.cut(self.view))
        self.assertTrue(result['all_targets_materialized'])
        self.assertFalse(manifest['current_owner_authority_verified'])
        self.assertIsNone(manifest['actual_owner_outcome'])
        self.assertEqual(manifest['repository_admissions_applied'], 0)
        self.assertEqual(manifest['runtime_activations'], 0)
        self.assertEqual(manifest['external_effect_refs'], [])
        for row in manifest['targets']:
            body = service.vault.material(row['original_content_binding'])
            self.assertEqual(P.source.sha(body), row['target']['artifact']['byte_sha256'])
            self.assertNotEqual(body, self.view.handle.common.encoded(P.frame_parse(body)))

    def test_01_actual_retry_reads_saved_outcome_without_redispatch(self):
        service, request, _ = self.example()
        call = request()
        first = self.invoke(service, call)
        self.assertEqual(first['kind'], 'result')
        before = self.journal(service)
        retry = copy.deepcopy(call)
        retry['call_id'] += ':retry'
        second = self.invoke(service, retry)
        self.assertEqual(second['kind'], 'result')
        self.assertEqual(second['message'], first['message'])
        self.assertEqual(self.journal(service), before)
        inspection = self.inspect(service)
        self.assertEqual(inspection['kind'], 'result')
        self.assertFalse(inspection['message']['retry_allowed'])
        self.assertFalse(inspection['message']['reconciliation_required'])

    def test_02_actual_pending_claim_never_redispatches(self):
        service, request, _ = self.example()
        call = request()
        service.vault.claim(call, P.compact(call), service.channel.context)
        before = self.journal(service)
        reply = self.invoke(service, call)
        self.assertEqual(reply['kind'], 'error')
        self.assertEqual(reply['message']['code'], 'recovery-required')
        self.assertEqual(self.journal(service), before)
        inspection = self.inspect(service)
        self.assertTrue(inspection['message']['reconciliation_required'])
        self.assertFalse(inspection['message']['retry_allowed'])

    def test_03_reordered_cores_refused_before_claim(self):
        service, request, _ = self.example()
        call = request()
        call['message']['stable_core_bindings'].reverse()
        before = self.journal(service)
        reply = self.invoke(service, call)
        self.assertEqual(reply['kind'], 'error')
        self.assertEqual(reply['message']['code'], 'invalid-contract')
        self.assertEqual(self.journal(service), before)

    def test_04_changed_example_preserves_uncertainty(self):
        service, request, _ = self.example()
        call = request()
        call['message']['example_bindings'][0]['sha256'] = '0' * 64
        reply = self.invoke(service, call)
        self.assertEqual(reply['kind'], 'error')
        self.assertEqual(reply['message']['code'], 'indeterminate')
        inspection = self.inspect(service)
        self.assertTrue(inspection['message']['reconciliation_required'])
        self.assertFalse(inspection['message']['retry_allowed'])

    def test_05_public_owner_claim_cannot_supply_authority(self):
        service, request, _ = self.example()
        call = request()
        call['message']['owner_authorized'] = True
        before = self.journal(service)
        reply = self.invoke(service, call)
        self.assertEqual(reply.get('code'), 'invalid-envelope')
        self.assertEqual(self.journal(service), before)

    def test_06_routing_material_revocation_refused(self):
        service, request, _ = self.example()
        call = request()
        selected = service.vault.inputs['candidate:review-routing']
        path = service.vault.root / selected['path']
        original = path.read_bytes()
        path.write_bytes(original + b' ')
        try:
            reply = self.invoke(service, call)
            self.assertEqual(reply.get('code'), 'unauthenticated-channel')
        finally:
            path.write_bytes(original)

    def test_07_existing_metadata_grant_cannot_review(self):
        service, request, _ = self.example(grant_review=False)
        before = self.journal(service)
        reply = self.invoke(service, request())
        self.assertEqual(reply.get('code'), 'unsupported-operation')
        self.assertEqual(self.journal(service), before)

    def test_08_actual_nonce_and_operator_context(self):
        service, _, witness = self.example()
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        proof = witness['signed_nonce_proof']
        Ed25519PublicKey.from_public_bytes(base64.b64decode(witness['public_policy']['reader_public_key'])).verify(
            base64.b64decode(proof['signature']), P.compact(proof['challenge']))
        context = service.channel.context
        self.assertEqual(context['role_assignment_bindings'], [])
        self.assertEqual(context['authority_scope'], 'operator-local')
        for key in ['agent_instance_ref', 'session_ref', 'assignment_ref']:
            self.assertIsNone(context[key])
        self.assertFalse(context['accept_client_supplied_authority_context'])
        self.assertNotIn('session.open', service.channel.policy['allowed_operations'])
        self.assertNotIn('admission.apply', service.channel.policy['allowed_operations'])
        self.assertEqual(len(service.channel.policy['allowed_operations']), 9)

    def test_09_semantic_and_operational_gaps_remain_in_package(self):
        service, request, witness = self.example()
        reply = self.invoke(service, request())
        self.assertEqual(reply['kind'], 'result')
        manifest = self.manifest(service, reply)
        self.assertEqual(manifest['original_semantic_and_operational_gaps'],
                         witness['prepare_reply']['message']['gaps'])
        self.assertGreater(len(manifest['original_semantic_and_operational_gaps']), 0)
        self.assertFalse(manifest['current_owner_authority_verified'])
        self.assertIsNone(manifest['actual_owner_outcome'])

    def test_10_multiple_owner_voices_are_independent(self):
        service, request, _ = self.example(multiple_voices=True)
        reply = self.invoke(service, request())
        self.assertEqual(reply['kind'], 'result')
        manifest = self.manifest(service, reply)
        voices = manifest['ordered_required_owner_responses']
        self.assertEqual(len(voices), 4)
        self.assertEqual({row['owner_role_ref'] for row in voices}, {'role:repository-owner', 'role:definition-owner'})
        self.assertEqual(len({row['core_index'] for row in voices}), 2)
        self.assertEqual(reply['message']['human_checkpoint_count'], 1)
        self.assertFalse(manifest['current_owner_authority_verified'])
