import copy
import base64
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t22_episode_local', HERE / 'episode.py')
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)


class EpisodeTests(unittest.TestCase):
    def fixture_root(self, root):
        names = list(E.PINS) + ['authority/admissions/lab-specialist-owner-bootstrap-v1-0003/bundle.json']
        for name in names:
            dst = root / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(E.ROOT / name, dst)

    def test_actual_inspection_and_cold_verification(self):
        result = E.run()
        self.assertTrue(E.verify(result))
        self.assertEqual([r['code'] for r in result['report']['discrepancies']], [
            'api30-current-project-state-lookup-stale', 'api30-current-project-state-body-unselected'])
        self.assertEqual(result['session']['consumed_view_sha256'], E.sha(E.compact(result['view'])))
        projected = result['view']['current_project_state']['payload']
        self.assertEqual(projected['project_ref'], E.PROJECT)
        self.assertEqual(len(projected['artifact_refs']), 57)
        self.assertEqual(len(projected['decision_refs']), 15)
        self.assertEqual(len(result['report']['observed_state_projection']['role_assignment_refs']), 4)
        self.assertFalse(result['native_lab_session'])

    def test_actual_payload_bytes_consumed_then_zeroed(self):
        selected = E.selection()
        session = E.FreshSession()
        view = E.bounded_view(selected, session.opened)
        receipt = session.consume(view)
        held = session.memory[0]
        self.assertEqual(bytes(held), E.compact(view))
        self.assertIn(b'"artifact_refs"', held)
        self.assertEqual(receipt['view_sha256'], E.sha(bytes(held)))
        close = session.close()
        self.assertTrue(close['memory_zeroed'] and close['nonce_zeroed'])
        self.assertFalse(any(held))

    def test_changed_current_lookup_refuses_before_session(self):
        with tempfile.TemporaryDirectory(prefix='cal-T22-lookup-') as temp:
            root = Path(temp); self.fixture_root(root)
            selected = root / E.LOOKUP
            selected.write_bytes(selected.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'selected source byte differs'):
                E.run(root)

    def test_changed_project_state_body_refuses_before_session(self):
        with tempfile.TemporaryDirectory(prefix='cal-T22-state-') as temp:
            root = Path(temp); self.fixture_root(root)
            selected = root / E.STATE
            selected.write_bytes(selected.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'selected source byte differs'):
                E.run(root)

    def test_changed_api30_manifest_refuses_before_session(self):
        with tempfile.TemporaryDirectory(prefix='cal-T22-api30-') as temp:
            root = Path(temp); self.fixture_root(root)
            selected = root / E.API
            selected.write_bytes(selected.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'selected source byte differs'):
                E.run(root)

    def test_equal_byte_symlinked_ancestor_refuses(self):
        with tempfile.TemporaryDirectory(prefix='cal-T22-link-') as temp:
            root = Path(temp); (root / 'real').mkdir()
            (root / 'real' / 'state.json').write_bytes(b'exact')
            (root / 'link').symlink_to('real', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'unsafe selected source attachment'):
                E.read_exact(root, 'link/state.json', E.sha(b'exact'))

    def test_expired_and_duplicate_consumption_refuse(self):
        tick = [100.0]
        session = E.FreshSession(clock=lambda: tick[0], monotonic=lambda: tick[0], ttl=2)
        view = {'opened_at': E.utc(100), 'expires_at': E.utc(102), 'payload': 'test'}
        tick[0] = 102.0
        with self.assertRaisesRegex(ValueError, 'not fresh/current'):
            session.consume(view)
        other = E.FreshSession(clock=lambda: 200.0, monotonic=lambda: 200.0, ttl=2)
        correct = {'opened_at': E.utc(200), 'expires_at': E.utc(202), 'payload': 'test'}
        other.consume(correct)
        with self.assertRaisesRegex(ValueError, 'already consumed'):
            other.consume(correct)
        close = other.close()
        self.assertTrue(close['memory_zeroed'] and close['nonce_zeroed'])

    def test_changed_view_or_report_refuses_cold_replay(self):
        result = E.run()
        def resign(value):
            key = Ed25519PrivateKey.generate()
            public = key.public_key().public_bytes(encoding=serialization.Encoding.Raw,
                                                    format=serialization.PublicFormat.Raw)
            value['technical_session_public_key_base64'] = base64.b64encode(public).decode()
            body = {k: v for k, v in value.items() if k != 'technical_session_signature_base64'}
            value['technical_session_signature_base64'] = base64.b64encode(key.sign(E.compact(body))).decode()
        changed = copy.deepcopy(result)
        changed['report']['discrepancies'][0]['observed_sha256'] = '0' * 64
        resign(changed)
        with self.assertRaisesRegex(ValueError, 'inspection report or claim ceiling differs'):
            E.verify(changed)
        changed = copy.deepcopy(result)
        changed['view']['project_ref'] = 'project:wrong'
        resign(changed)
        with self.assertRaisesRegex(ValueError, 'technical Session consumption/closure differs'):
            E.verify(changed)
        changed = copy.deepcopy(result)
        projected = changed['view']['current_project_state']['payload']
        projected['cursor'] = 'decision:forged'
        changed['view']['current_project_state']['payload_sha256'] = E.sha(E.compact(projected))
        digest = E.sha(E.compact(changed['view']))
        changed['session']['consumed_view_sha256'] = digest
        changed['session']['consumed_input_bytes'] = len(E.compact(changed['view']))
        changed['report'] = E.expected_report(E.selection(), changed['view'], digest)
        resign(changed)
        with self.assertRaisesRegex(ValueError, 'technical Session consumption/closure differs'):
            E.verify(changed)

    def test_wrong_session_view_binding_refuses(self):
        session = E.FreshSession(ttl=2)
        wrong = {'opened_at': E.utc(session.opened), 'expires_at': E.utc(session.opened + 3)}
        with self.assertRaisesRegex(ValueError, 'not bound'):
            session.consume(wrong)


if __name__ == '__main__': unittest.main()
