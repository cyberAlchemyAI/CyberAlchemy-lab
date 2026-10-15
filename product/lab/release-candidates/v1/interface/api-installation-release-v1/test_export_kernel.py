import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from . import export_test_base as B
from .export_kernel import *

class Exports(unittest.TestCase):
    observations = []
    @classmethod
    def setUpClass(cls):
        cls.schemas = B.guard()
        cls.cm = P.source.replay_source('custody-participation')
        cls.view = cls.cm.__enter__()
        cls.cut = B.H.cut(cls.view)
        cls.actual = []
        with B.M.model_read_batch(cls.view):
            for _, subject in sorted(cls.view.subjects.items()):
                if subject['carrier_ref'] in ('cal.artifact-type.intent/v1', 'cal.artifact-type.goal/v1') and subject['source'].get('encoding') == 'base64-original-json/v1-candidate':
                    ref = B.M.artifact_ref(cls.view, subject)
                    raw, locator, encoding, _ = B.M.record_bytes(cls.view, subject)
                    cls.actual.append(Material(encoded(ref), raw, locator, encoding))
        require(len(cls.actual) >= 2, 'actual original Intent/Goal body closure unavailable')
        cls.actual = tuple(cls.actual[:2])
    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory(prefix='cal-R03-file-export-')))
        self.root.chmod(0o700)
        self.actor = {'principal_ref': 'principal:candidate-export-fixture', 'agent_instance_ref': None, 'assignment_ref': None, 'session_ref': None, 'role_assignment_refs': []}
        review = {'selection_ref': 'selection:actual-intent-goal-export', 'source_cut': self.cut, 'artifact_refs': [m.artifact for m in self.actual], 'include_session_memory': False, 'authority_effect': 'none'}
        self.selection = Selection(review['selection_ref'], encoded(self.cut), self.actual, encoded(review))
        self.authorized = True
        self.host = ExportHost(self.root, 'owned:candidate-export', self.actor, self.selection, self.schemas, self.view.custody_signed_sources.guard, lambda: self.authorized)
        self.request = {'schema_version': 'lab-file-materialization-request/v1-candidate', 'request_ref': 'request:actual-export', 'actor': self.actor, 'source_cut': self.cut, 'selection_ref': self.selection.ref, 'artifact_refs': review['artifact_refs'], 'output_root_scope_ref': self.host.scope_ref, 'mode': 'byte-exact', 'renderer_binding': None, 'managed_relative_paths': ['intent/body.json', 'goal/body.json'], 'overwrite_unmanaged_files': False, 'include_session_memory': False, 'privacy_review_binding': self.selection.privacy_binding, 'authority_effect': 'none'}
    def refused(self, mutate):
        request = copy.deepcopy(self.request)
        mutate(request)
        with self.assertRaises(ValueError):
            self.host.materialize(request)
        self.assertEqual(list(self.root.iterdir()), [])
    def test_actual_original_byte_export(self):
        result = self.host.materialize(self.request)
        self.assertEqual(result['posture'], 'published')
        generation = self.root / sha(encoded(self.request))
        for path, material in zip(self.request['managed_relative_paths'], self.actual, strict=True):
            self.assertEqual((generation / 'files' / path).read_bytes(), material.original_bytes)
        self.assertFalse(result['canonical_replay_source'])
        self.assertEqual(result['authority_effect'], 'none')
        self.observations.append({'request': copy.deepcopy(self.request), 'result': result, 'manifest': json.loads((generation / 'manifest.json').read_bytes()), 'owned_root': str(self.root), 'fixture_permission_only': True})
    def test_pinned_renderer(self):
        self.request.update(mode='rendered', renderer_binding=renderer_binding())
        result = self.host.materialize(self.request)
        self.assertEqual(result['posture'], 'published')
        generation = self.root / sha(encoded(self.request))
        for path, material in zip(self.request['managed_relative_paths'], self.actual, strict=True):
            raw = (generation / 'files' / path).read_bytes()
            self.assertEqual(json.loads(raw), json.loads(material.original_bytes))
            self.assertTrue(raw.endswith(b'\n'))
    def test_exact_retry_preserves_files_and_receipt(self):
        first = self.host.materialize(self.request)
        before = {str(p): (p.stat().st_ino, p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(self.host.materialize(copy.deepcopy(self.request)), first)
        after = {str(p): (p.stat().st_ino, p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
    def test_retry_requires_current_authorization(self):
        self.host.materialize(self.request)
        self.authorized = False
        with self.assertRaises(ValueError):
            self.host.materialize(self.request)
    def test_unmanaged_file_preserved(self):
        unmanaged = self.root / 'notes.txt'
        unmanaged.write_bytes(b'existing unrelated bytes')
        result = self.host.materialize(self.request)
        self.assertEqual(result['posture'], 'published')
        self.assertEqual(unmanaged.read_bytes(), b'existing unrelated bytes')
    def test_caller_output_scope_cannot_select_path(self):
        self.refused(lambda r: r.update(output_root_scope_ref='/tmp/outside'))
    def test_parent_traversal_refused(self):
        self.refused(lambda r: r.update(managed_relative_paths=['../escape.json', 'product.json']))
    def test_absolute_path_refused(self):
        self.refused(lambda r: r.update(managed_relative_paths=['/tmp/escape.json', 'product.json']))
    def test_duplicate_path_refused(self):
        self.refused(lambda r: r.update(managed_relative_paths=['body.json', 'body.json']))
    def test_file_directory_collision_refused(self):
        self.refused(lambda r: r.update(managed_relative_paths=['body', 'body/item.json']))
    def test_source_cut_change_refused(self):
        self.refused(lambda r: r['source_cut'].update(commit_sha256='0'*64))
    def test_changed_original_digest_refused(self):
        self.refused(lambda r: r['artifact_refs'][0].update(byte_sha256='0'*64))
    def test_missing_selection_member_refused(self):
        self.refused(lambda r: r['artifact_refs'].pop())
    def test_privacy_binding_change_refused(self):
        self.refused(lambda r: r['privacy_review_binding'].update(sha256='0'*64))
    def test_session_memory_flag_refused(self):
        self.refused(lambda r: r.update(include_session_memory=True))
    def test_overwrite_unmanaged_flag_refused(self):
        self.refused(lambda r: r.update(overwrite_unmanaged_files=True))
    def test_wrong_renderer_refused(self):
        self.refused(lambda r: r.update(mode='rendered', renderer_binding={'ref': 'renderer:unknown', 'sha256': '0'*64}))
    def test_output_budget_refused_before_effect(self):
        self.host.max_bytes = 1
        self.refused(lambda r: None)
    def test_root_symlink_refused(self):
        parent = Path(self.enterContext(tempfile.TemporaryDirectory(prefix='cal-R03-file-export-link-')))
        alias = parent / 'alias'
        alias.symlink_to(self.root, target_is_directory=True)
        self.host.root = alias
        with self.assertRaises(ValueError):
            self.host.materialize(self.request)
        self.assertEqual(list(self.root.iterdir()), [])
    def test_pending_generation_never_redispatched(self):
        generation = self.root / sha(encoded(self.request))
        generation.mkdir(mode=0o700)
        (generation / 'unmanaged.txt').write_bytes(b'preserve incomplete generation')
        with self.assertRaises(ValueError):
            self.host.materialize(self.request)
        self.assertEqual({p.name for p in generation.iterdir()}, {'unmanaged.txt'})
    def test_modified_published_output_refused(self):
        self.host.materialize(self.request)
        target = self.root / sha(encoded(self.request)) / 'files' / 'intent/body.json'
        target.write_bytes(b'{}')
        with self.assertRaises(ValueError):
            self.host.materialize(self.request)
        self.assertEqual(target.read_bytes(), b'{}')
    def test_symlink_published_output_refused(self):
        self.host.materialize(self.request)
        target = self.root / sha(encoded(self.request)) / 'files' / 'intent/body.json'
        target.unlink()
        target.symlink_to('/etc/passwd')
        with self.assertRaises(ValueError):
            self.host.materialize(self.request)
        self.assertTrue(target.is_symlink())
    def test_preclaim_expired_authorization_refused(self):
        self.authorized = False
        self.refused(lambda r: None)
    def test_actor_claim_refused(self):
        self.refused(lambda r: r['actor'].update(principal_ref='person:owner'))
