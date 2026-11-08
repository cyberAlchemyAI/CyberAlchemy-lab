"""Read-only W03 Source target preflight against the actual selected engine."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[4]
INSTANCES = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances'
OLD = INSTANCES / 'legacy-local-ce4d53a6479188a5/source'
NEW = INSTANCES / 'legacy-local-8d0312c813444f57/source'


def selected(name, directory):
    spec = importlib.util.spec_from_file_location(
        name, directory / '__init__.py', submodule_search_locations=[str(directory)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return (importlib.import_module(name + '.base'),
            importlib.import_module(name + '.cold'),
            importlib.import_module(name + '.records'))


class W03SourcePreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_base, cls.old_cold, _ = selected('_cal_t31_ce4_w03_preflight', OLD)
        cls.new_base, cls.new_cold, cls.new_records = selected('_cal_t31_w03_preflight', NEW)
        cls.manifest_pin = hashlib.sha256((NEW / 'source-manifest.json').read_bytes()).hexdigest()
        cls.new_manifest = cls.new_base.verify_source(cls.manifest_pin)
        old_pin = hashlib.sha256((OLD / 'source-manifest.json').read_bytes()).hexdigest()
        old_package = hashlib.sha256((OLD / 'packages/0001/manifest.json').read_bytes()).hexdigest()
        cls.source_context = cls.old_cold.open_source(old_pin, old_package)
        cls.source = cls.source_context.__enter__()
        cls.data = cls.source.data
        cls.original_targets = json.loads((OLD / 'packages/0001/proposal.json').read_text())['targets']
        cls.originals = cls.new_records.w03_original_rows()
        cls.targets = cls.new_records.engineering_targets(cls.data['projection'],
            cls.data['config']['scope_ref'], cls.data['config'], cls.original_targets)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'source_context'):
            cls.source_context.__exit__(None, None, None)

    def test_actual_engine_accepts_exact_additions(self):
        proposal = {'schema_version': 'lab-runtime-proposal/v1',
            'proposal_id': 'T31-W03-STATIC-PREFLIGHT-0001',
            'expected_head': self.data['head']['transaction_digest'],
            'source_snapshot_digest': self.data['config']['source_snapshot_digest'],
            'scope_ref': self.data['config']['scope_ref'],
            'policy_ref': self.data['config']['policy_ref'],
            'challenge_route': self.data['config']['challenge_route'],
            'schemas': {}, 'targets': self.targets}
        post, cores = self.source.handle.operations.prepare(self.data['projection'], proposal,
            self.data['head']['transaction_digest'], self.data['config'])
        self.assertEqual(len(cores), 15)
        self.assertNotEqual(post, self.data['projection'])
        self.assertEqual(len(self.targets), 15)
        for kind, (row, body, raw) in self.originals.items():
            self.assertEqual(self.new_records.original_bytes_for(row['version_ref']), raw)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            self.assertEqual(next(t for t in self.targets if t['version_ref'] == row['version_ref'])['record'], body)
        self.assertNotIn(self.new_records.W03_RESOLUTION + '@candidate.1',
                         {t['version_ref'] for t in self.targets})
        self.assertNotEqual(self.new_records.W03_PRINCIPAL, self.new_records.PRINCIPAL)

    def test_changed_public_original_is_refused(self):
        wrong = copy.deepcopy(self.targets)
        work = next(t for t in wrong if t['version_ref'] == self.originals['work'][0]['version_ref'])
        work['record']['name'] += ' changed'
        with self.assertRaisesRegex(ValueError, 'original record substitution'):
            self.new_records.verify_engineering_targets(wrong, self.originals)

    def test_wrong_work_or_effect_join_is_refused(self):
        for target_ref, field, wrong_value in (
            (self.new_records.W03_RESOLUTION + '@' + self.new_records.W03_LOCAL_VERSION,
             'selected_subject_refs', ['work:foreign@candidate.1']),
            (self.new_records.W03_DECISION + '@' + self.new_records.W03_LOCAL_VERSION,
             'declared_effect_refs', ['effect:foreign']),
            (self.new_records.W03_EFFECT + '@' + self.new_records.W03_LOCAL_VERSION,
             'subject_ref', 'intent-resolution:foreign@candidate.1'),
        ):
            with self.subTest(field=field):
                wrong = copy.deepcopy(self.targets)
                target = next(t for t in wrong if t['version_ref'] == target_ref)
                target['record']['payload'][field] = wrong_value
                with self.assertRaisesRegex(ValueError, 'evidence join differs'):
                    self.new_records.verify_engineering_targets(wrong, self.originals)

    def test_wrong_typed_relation_or_recycled_owner_is_refused(self):
        wrong = copy.deepcopy(self.targets)
        relation = next(t for t in wrong if t['version_ref'].startswith(
            'typed-relation:' + self.new_records.PREFIX + ':w03:decision-resolution@'))
        relation['record']['payload']['qualifiers']['exact_target_version_ref'] = 'intent-resolution:foreign@candidate.1'
        with self.assertRaisesRegex(ValueError, 'typed Decision/Resolution join differs'):
            self.new_records.verify_engineering_targets(wrong, self.originals)
        wrong = copy.deepcopy(self.targets)
        principal = next(t for t in wrong if t['version_ref'] ==
                         self.new_records.W03_PRINCIPAL + '@' + self.new_records.W03_LOCAL_VERSION)
        principal['record']['payload']['stable_subject_ref'] = 'principal:repository-owner@candidate.1'
        with self.assertRaisesRegex(ValueError, 'cannot borrow Agent or owner identity'):
            self.new_records.verify_engineering_targets(wrong, self.originals)

    def test_changed_manifest_digest_is_refused(self):
        rows = copy.deepcopy(self.new_manifest['files'])
        path = self.new_records.W03_DIRECTORY + 'work.json'
        row = next(item for item in rows if item['path'] == path)
        row['sha256'] = '0' * 64
        with self.assertRaises(Exception):
            self.new_base.verify_inputs(rows)


if __name__ == '__main__':
    unittest.main()
