"""Cold checks for the unselected T16 fixture successor functions."""

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from contextlib import contextmanager

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


F = load('_cal_t16_fixture_recut', HERE / 'fixture_recut.py')
W = load('_cal_t16_worker_for_cold', HERE / 'run_bucket.py')


class Recut(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        code = W.capture()
        if any(name == W.PACKAGE or name.startswith(W.PACKAGE + '.') for name in sys.modules):
            raise ValueError('ambient selected test package')
        cls.finder = W.PinnedAPI(code)
        sys.meta_path.insert(0, cls.finder)
        __import__(W.PACKAGE)
        cls.challenge = __import__(W.PACKAGE + '.test_challenge_api', fromlist=['CurrentChallenge'])
        cls.controls = __import__(W.PACKAGE + '.test_current_controls', fromlist=['CurrentControls'])
        cls.preparation = __import__(W.PACKAGE + '.test_preparation_corrected', fromlist=['CorrectedPreparation'])

    @classmethod
    def tearDownClass(cls):
        sys.meta_path.remove(cls.finder)

    def test_01_closed_selected_test_origins(self):
        for module, name in [(self.challenge, 'test_challenge_api.py'),
                             (self.controls, 'test_current_controls.py'),
                             (self.preparation, 'test_preparation_corrected.py')]:
            F.selected_module(module, name)
        bad = SimpleNamespace(__file__=str(F.API / 'test_preparation.py'))
        with self.assertRaisesRegex(ValueError, 'origin or byte'):
            F.selected_module(bad, 'test_challenge_api.py')

    def test_02_original_method_ids_preserved_by_scoped_successors(self):
        pairs = [(self.challenge.CurrentChallenge,
                  F.current_challenge_setup(self.challenge.CurrentChallenge, self.challenge)),
                 (self.controls.CurrentControls,
                  F.expired_original_control(self.controls.CurrentControls, self.controls)),
                 (self.preparation.CorrectedPreparation,
                  F.current_protected_preparation(self.preparation.CorrectedPreparation,
                                                  self.preparation, self.controls))]
        for original, successor in pairs:
            old = set(unittest.defaultTestLoader.getTestCaseNames(original))
            new = set(unittest.defaultTestLoader.getTestCaseNames(successor))
            self.assertEqual(old, new)
            self.assertEqual(original.__name__, successor.__name__)
            self.assertEqual(original.__module__, successor.__module__)
        self.assertEqual(len(pairs), 3)

    def test_03_current_session_selection_is_closed(self):
        good = {'kind': 'agent-session', 'version_ref': F.PROTECTED_SESSION_REF,
                'record': {'payload': {'session_memory': 'protected'}}}
        view = SimpleNamespace(legacy_signed_sources=SimpleNamespace(source_cut={'store_ref': F.CURRENT_STORE}),
                               subjects={'one': good})
        source = SimpleNamespace(current_legacy_view=lambda selected: selected is view)
        self.assertIs(F.current_protected_session_subject(view, source), good)
        view.subjects['two'] = good
        with self.assertRaisesRegex(ValueError, 'witness unavailable'):
            F.current_protected_session_subject(view, source)
        view.subjects.pop('two')
        good['version_ref'] = 'agent-session:foreign@candidate.1'
        with self.assertRaisesRegex(ValueError, 'witness unavailable'):
            F.current_protected_session_subject(view, source)
        good['version_ref'] = F.PROTECTED_SESSION_REF
        with self.assertRaisesRegex(ValueError, 'view differs'):
            F.current_protected_session_subject(view, SimpleNamespace(current_legacy_view=lambda _: False))
        view.legacy_signed_sources.source_cut['store_ref'] = 'foreign'
        with self.assertRaisesRegex(ValueError, 'view differs'):
            F.current_protected_session_subject(view, source)

    def test_04_historical_period_remains_exact_and_expired(self):
        import hashlib, json
        from datetime import datetime, timezone
        raw = F.EXPIRED_PERIOD.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), F.EXPIRED_PERIOD_SHA)
        self.assertLess(datetime.fromisoformat(json.loads(raw)['expires_at'].replace('Z', '+00:00')),
                        datetime.now(timezone.utc))

    def test_05_challenge_successor_selects_only_current_name_and_cut(self):
        successor = F.current_challenge_setup(self.challenge.CurrentChallenge, self.challenge)
        projection = {'scope': 'fixture'}
        view = SimpleNamespace(data={'projection': projection},
                               legacy_signed_sources=SimpleNamespace(source_cut={'store_ref': F.CURRENT_STORE}))
        names = []
        @contextmanager
        def replay(name):
            names.append(name)
            yield view
        with patch.object(self.challenge, 'verify'), \
             patch.object(self.challenge.P, 'Schemas', return_value=object()), \
             patch.object(self.challenge.P.source, 'replay_source', side_effect=replay), \
             patch.object(self.challenge.P.source, 'current_legacy_view', return_value=True):
            successor.setUpClass()
            self.assertEqual(names, [F.CURRENT_NAME])
            successor.tearDownClass()
        view.legacy_signed_sources.source_cut['store_ref'] = 'foreign'
        with patch.object(self.challenge, 'verify'), \
             patch.object(self.challenge.P, 'Schemas', return_value=object()), \
             patch.object(self.challenge.P.source, 'replay_source', side_effect=replay), \
             patch.object(self.challenge.P.source, 'current_legacy_view', return_value=True):
            with self.assertRaisesRegex(ValueError, 'cut differs'):
                successor.setUpClass()


if __name__ == '__main__':
    unittest.main(verbosity=2)
