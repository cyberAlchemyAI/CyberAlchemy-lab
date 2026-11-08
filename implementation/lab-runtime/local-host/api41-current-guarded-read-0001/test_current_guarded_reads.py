"""Bounded current-native guarded-read successor tests; no historical Source5 replay."""
from contextlib import ExitStack
import copy
import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v41-current-source8-0001'
API_SOURCE = '69c872681c53ff02ba5d38ef0f80d866d75f0b9e8c6b6d5d214b9adc2ba70961'
API_PROFILE = '18ed4a8a577679211ee5f530ea8148fc18cb0dd0a29ef16de73d6ea761eb9860'
FAMILY = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8'
FAMILY_SOURCE = '501e59318f2e0f504c4bd9cbf2c364e9901712cef33d785d67dd0a7107fa6a27'
FAMILY_CONTEXT = '9a7baaf2453bed90a67b7145dd02c21f6e72150759885358e18f643f34899ddd'
MODULE = '_cal_api40_current_guarded_read_successor_0001'


def exact(path, expected):
    if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('selected current guarded-read input differs')


def selected_api():
    exact(API / 'source-manifest.json', API_SOURCE)
    exact(API / 'contract-profile.json', API_PROFILE)
    exact(FAMILY / 'source/source-manifest.json', FAMILY_SOURCE)
    exact(FAMILY / 'context/source-manifest.json', FAMILY_CONTEXT)
    if MODULE not in sys.modules:
        spec = importlib.util.spec_from_file_location(MODULE, API / '__init__.py', submodule_search_locations=[str(API)])
        package = importlib.util.module_from_spec(spec)
        sys.modules[MODULE] = package
        spec.loader.exec_module(package)
    guard = __import__(MODULE + '.guard', fromlist=['verify'])
    guard.verify(API_SOURCE)
    return __import__(MODULE + '.protocol', fromlist=['source'])


class CurrentGuardedReads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        package = selected_api()
        cls.source = package.source
        cls.model = __import__(MODULE + '.artifact_model', fromlist=['artifact_ref'])
        cls.guards = __import__(MODULE + '.guarded_reads', fromlist=['model_read_batch'])
        cls.inherited = __import__(MODULE + '.test_guarded_reads', fromlist=['GuardedReads']).GuardedReads
        cls.api_guard = __import__(MODULE + '.guard', fromlist=['verify'])
        cls.stack = ExitStack()
        cls.addClassCleanup(lambda: cls.api_guard.verify(API_SOURCE))
        cls.addClassCleanup(cls.stack.close)
        cls.view = cls.stack.enter_context(cls.source.replay_source(cls.source.CURRENT_SOURCE8_NAME))
        if not cls.source.current_source8_view(cls.view):
            raise ValueError('actual current Source8 view required')
        cls.parent = cls.view.custody_signed_sources
        cls.delivery = cls.view.source8_context_producer

    def test_snapshot_header_mutation_rejected(self):
        # Run the inherited assertion body over a fresh current signed source.
        with self.guards.participation_snapshot(self.parent, self.delivery) as snapshot:
            snapshot.guard()
        self.inherited.test_snapshot_header_mutation_rejected(self)
        with self.guards.participation_snapshot(self.parent, self.delivery) as snapshot:
            snapshot.guard()

    def test_current_signed_model_batch_positive(self):
        selected = self.view.source8_context_producer
        subject = next(s for s in self.view.subjects.values() if s['identity'] == selected.records.WORK)
        with self.guards.model_read_batch(self.view):
            ref = self.model.artifact_ref(self.view, subject)
            self.assertEqual(ref, selected.reader.adapter.model.artifact_ref(self.view, subject))

    def test_current_subject_header_mutation_rejected(self):
        selected = self.view.source8_context_producer
        subject = next(s for s in self.view.subjects.values() if s['identity'] == selected.records.WORK)
        original = copy.deepcopy(subject)
        with self.guards.model_read_batch(self.view):
            self.model.artifact_ref(self.view, subject)
        try:
            with self.assertRaises(ValueError):
                with self.guards.model_read_batch(self.view):
                    self.model.artifact_ref(self.view, subject)
                    subject['identity'] = 'work:unselected-mutated-header'
        finally:
            subject.clear()
            subject.update(original)
        self.assertTrue(self.source.current_source8_view(self.view))

    def test_current_original_byte_mutation_rejected(self):
        key = next(iter(self.view.originals))
        original = self.view.originals[key]
        with self.guards.model_read_batch(self.view):
            self.assertTrue(original)
        try:
            with self.assertRaises(ValueError):
                with self.guards.model_read_batch(self.view):
                    self.view.originals[key] = original + b' '
        finally:
            self.view.originals[key] = original
        self.assertTrue(self.source.current_source8_view(self.view))

    def test_foreign_view_refused(self):
        with self.assertRaises(ValueError):
            with self.guards.model_read_batch(copy.copy(self.view)):
                self.fail('foreign current view must not be accepted')

    def test_changed_native_reader_class_refused(self):
        reader = self.view.source8_context_producer.reader
        module = sys.modules[type(reader).__module__]
        self.assertIs(self.source.reader_factory(self.view)(), reader)
        with patch.object(module, 'SelectedReader', object):
            with self.assertRaises(ValueError):
                self.source.reader_factory(self.view)
        self.assertIs(self.source.reader_factory(self.view)(), reader)

    def test_changed_native_reader_origin_refused(self):
        reader = self.view.source8_context_producer.reader
        module = sys.modules[type(reader).__module__]
        self.assertIs(self.source.reader_factory(self.view)(), reader)
        with patch.object(module, '__file__', '/tmp/unselected-reader.py'):
            with self.assertRaises(ValueError):
                self.source.reader_factory(self.view)
        self.assertIs(self.source.reader_factory(self.view)(), reader)


if __name__ == '__main__':
    unittest.main(verbosity=2)
