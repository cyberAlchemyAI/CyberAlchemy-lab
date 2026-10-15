"""Disposable technical issuers only; no actual owner response is produced."""
import copy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import owner_ingress as O


def stamp(value):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')


class IngressTests(unittest.TestCase):
    def setUp(self):
        self.host = Ed25519PrivateKey.generate()
        self.registry = Ed25519PrivateKey.generate()
        pub = lambda key: key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
        self.trust = O.TrustContext('fixture:host', pub(self.host), 'fixture:registry', pub(self.registry),
                                    'fixture:explicit-human-review', 'fixture:governing-registry',
                                    'technical-fixture')
        self.now = datetime.now(timezone.utc).replace(microsecond=0)
        self.authority = {'principal_ref': 'fixture:owner', 'scope_ref': 'fixture:repository',
                          'expires_at': stamp(self.now + timedelta(hours=1)),
                          'owner_roles': {'artifact-instance': 'fixture:role-owner'}}
        core = {'owner_ref': 'fixture:role-owner', 'target_ref': 'fixture:target/v1',
                'target_sha256': 'a' * 64, 'decision_ref': 'fixture:decision'}
        self.review = {'authority': self.authority, 'authority_sha256': O.digest(self.authority),
                       'targets': [{'category': 'artifact-instance', 'version_ref': 'fixture:target/v1'}],
                       'independent_cores': [core], 'core_sha256s': [O.legacy_core_digest(core)],
                       'bundle_id': 'fixture-bundle', 'bundle_path': 'fixture/admissions/v1',
                       'authority_effect': 'none', 'fixture_only': True}
        role = {'schema_version': 'lab-governing-owner-evidence/v1-candidate',
                'registry_ref': self.trust.governing_registry_ref, 'registry_cursor': 'fixture:cursor/1',
                'principal_ref': 'fixture:owner', 'scope_ref': 'fixture:repository',
                'governing_roles': self.authority['owner_roles'], 'authority_sha256': O.digest(self.authority),
                'source_evidence': [{'ref': 'fixture:resolved-authority', 'sha256': 'b' * 64}],
                'valid_from': stamp(self.now - timedelta(minutes=5)),
                'valid_until': stamp(self.now + timedelta(hours=1)),
                'resolution': 'independently-resolved-current-governing-authority',
                'permitted_effect': 'one-exact-immutable-repository-bundle'}
        self.response = {'schema_version': O.VERSION, 'authority_proof': self.sign(role, 'role')}
        presentation = {'schema_version': 'lab-host-review-presentation/v1-candidate',
                        'mechanism_ref': self.trust.mechanism_ref, 'presentation_id': 'fixture:presentation/1',
                        'conversation_id': 'fixture:conversation/1', 'principal_ref': 'fixture:owner',
                        'review_sha256': O.digest(self.review), 'authority_sha256': O.digest(self.authority),
                        'bundle_id': self.review['bundle_id'], 'bundle_path': self.review['bundle_path'],
                        'decision_core_sha256s': self.review['core_sha256s'],
                        'displayed_material_sha256': 'c' * 64,
                        'presented_at': stamp(self.now - timedelta(minutes=2))}
        self.response['presentation'] = self.sign(presentation, 'host')
        content = 'Technical fixture only: admit this exact fixture review.'
        message = {'schema_version': 'lab-host-owner-message/v1-candidate',
                   'mechanism_ref': self.trust.mechanism_ref, 'message_id': 'fixture:message/1',
                   'conversation_id': 'fixture:conversation/1', 'principal_ref': 'fixture:owner',
                   'interaction_kind': 'human-explicit-review-disposition', 'content': content,
                   'content_sha256': sha256(content.encode()).hexdigest(),
                   'presentation_sha256': O.digest(self.response['presentation']),
                   'review_sha256': O.digest(self.review),
                   'authority_proof_sha256': O.digest(self.response['authority_proof']),
                   'selected_outcome': O.ADMIT, 'recorded_at': stamp(self.now - timedelta(minutes=1))}
        self.response['message'] = self.sign(message, 'host')
        self.selection = self.selected()

    def sign(self, payload, kind):
        issuer = self.trust.role_issuer if kind == 'role' else self.trust.host_issuer
        key = self.registry if kind == 'role' else self.host
        core = {'issuer_ref': issuer, 'payload': copy.deepcopy(payload)}
        return dict(core, signature=key.sign(O.encoded(core)).hex())

    def selected(self):
        return O.Selection(O.digest(self.review), O.digest(self.response['authority_proof']),
                           O.digest(self.response['presentation']), O.digest(self.response['message']),
                           'fixture:cursor/1', 'fixture:owner', 'fixture:repository')

    def change(self, field, changes):
        payload = copy.deepcopy(self.response[field]['payload']); payload.update(changes)
        self.response[field] = self.sign(payload, 'role' if field == 'authority_proof' else 'host')
        if field != 'message':
            message = copy.deepcopy(self.response['message']['payload'])
            message[field + '_sha256'] = O.digest(self.response[field])
            self.response['message'] = self.sign(message, 'host')
        self.selection = self.selected()

    def deny(self, reason=None):
        with self.assertRaises(O.Refusal) as caught:
            O.verify(self.response, self.review, self.selection, self.trust)
        if reason:
            self.assertIn(reason, str(caught.exception))

    def test_01_technical_positive_exact_signed_evidence(self):
        result = O.ingest(O.encoded(self.response), self.review, self.selection, self.trust)
        self.assertEqual(result['usage'], 'technical-fixture')
        self.assertEqual(result['authority_effect'], 'none')

    def test_02_fixture_positive_never_authorizes_actual_publication(self):
        with self.assertRaisesRegex(O.Refusal, 'technical fixtures'):
            O.verify_for_publication(self.response, self.review, self.selection, self.trust)

    def test_03_unsigned_caller_human_flag_denied(self):
        self.response['human'] = True; self.deny('closed fields')

    def test_04_forged_host_signature_even_if_evidence_selected(self):
        self.response['message']['signature'] = '00' * 64
        self.selection = self.selected(); self.deny('signature')

    def test_05_absent_host_proof(self):
        self.response['message'] = None; self.selection = self.selected(); self.deny('closed fields')

    def test_06_signed_wrong_owner(self):
        self.change('message', {'principal_ref': 'fixture:other'}); self.deny('disposition absent')

    def test_07_signed_wrong_scope(self):
        self.change('authority_proof', {'scope_ref': 'fixture:other'}); self.deny('governing authority')

    def test_08_signed_missing_governing_role(self):
        self.change('authority_proof', {'governing_roles': {}}); self.deny('governing authority')

    def test_09_expired_signed_role(self):
        self.change('authority_proof', {'valid_until': stamp(self.now - timedelta(seconds=1))})
        self.deny('expired')

    def test_10_future_authority(self):
        self.change('authority_proof', {'valid_from': stamp(self.now + timedelta(seconds=30))})
        self.deny('expired/current')

    def test_11_changed_review_without_selection_rejected(self):
        self.review['bundle_path'] = 'fixture/other/v1'; self.deny('review changed')

    def test_12_changed_target_core_even_with_new_selection(self):
        self.review['independent_cores'][0]['target_ref'] = 'fixture:other/v1'
        self.selection = self.selected(); self.deny('member cores')

    def test_13_signed_stale_registry_cursor(self):
        self.change('authority_proof', {'registry_cursor': 'fixture:cursor/0'})
        self.deny('governing authority')

    def test_14_signed_unselected_issuer(self):
        self.response['message']['issuer_ref'] = 'fixture:other-host'
        self.selection = self.selected(); self.deny('unselected issuer')

    def test_15_key_custody_does_not_replace_independent_registry(self):
        self.trust = replace(self.trust, role_issuer=self.trust.host_issuer,
                             role_public_key=self.trust.host_public_key)
        self.deny('independent role issuer')

    def test_16_copied_goal_request_not_explicit_admission(self):
        content = 'complete this plan'
        self.change('message', {'content': content, 'content_sha256': sha256(content.encode()).hexdigest(),
                               'interaction_kind': 'human-goal-request', 'selected_outcome': None})
        self.deny('disposition absent')

    def test_17_changed_actual_message_content(self):
        self.change('message', {'content': 'different text'}); self.deny('content digest')

    def test_18_reject_is_verified_but_never_positive(self):
        self.change('message', {'selected_outcome': 'reject-exact-review'})
        self.assertEqual(O.verify(self.response, self.review, self.selection, self.trust)['selected_outcome'],
                         'reject-exact-review')
        with self.assertRaisesRegex(O.Refusal, 'positive owner'):
            O.verify_for_publication(self.response, self.review, self.selection, self.trust)

    def test_19_original_key_adapter_shape_cannot_enter(self):
        fixture = {'schema_version': 'lab-repository-owner-response/v1-candidate',
                   'authorization_mechanism': 'independent-repository-key-adapter',
                   'human_conversation_outcome': None, 'selected_outcome': O.ADMIT}
        with self.assertRaises(O.Refusal):
            O.verify_for_publication(fixture, self.review, self.selection, self.trust)

    def test_20_persistent_replay_refusal_across_journal_instances(self):
        with tempfile.TemporaryDirectory(prefix='cal-T33-technical-replay-') as tmp:
            root = Path(tmp); root.chmod(0o700)
            O.ReplayJournal(root).reserve(self.response, self.review, self.selection, self.trust, rehearsal=True)
            with self.assertRaisesRegex(O.Refusal, 'replay'):
                O.ReplayJournal(root).reserve(self.response, self.review, self.selection, self.trust, rehearsal=True)
            self.assertEqual(len(list(root.iterdir())), 1)

    def test_21_expired_repository_authority(self):
        self.authority['expires_at'] = stamp(self.now - timedelta(seconds=1))
        self.review['authority_sha256'] = O.digest(self.authority)
        self.change('authority_proof', {'authority_sha256': O.digest(self.authority)})
        self.deny('expired')

    def test_22_message_before_review_presentation(self):
        self.change('message', {'recorded_at': stamp(self.now - timedelta(minutes=3))})
        self.deny('outside authority period')

    def test_23_unpinned_changed_envelope(self):
        self.response['message']['payload']['content'] = 'tampered'; self.deny('evidence changed')

    def test_24_duplicate_keys_nonfinite_and_oversize(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'x' * (1024 * 1024 + 1)):
            with self.assertRaises(O.Refusal):
                O.parse(raw)


if __name__ == '__main__':
    unittest.main(verbosity=2)
