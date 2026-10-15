import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


def module(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


gates, ranking = module('failure_gates'), module('ranking')


class GateTests(unittest.TestCase):
    def test_missing_review_preserves_candidate_and_per_unit_ranking_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'outputs').mkdir()
            original = {'id': 'A1', 'kind': 'mechanism', 'claim': 'Unassessed original relation'}
            (root / 'outputs/a.json').write_text(json.dumps({'openings': [original]}))
            (root / 'outputs/d.json').write_text(json.dumps({'openings': []}))
            schedule = {'units': [{'unit_id': 'u', 'case_id': 'X', 'condition': 'P01',
                                  'repetition': 1, 'raw_jobs': ['a'], 'post_job': 'd'}]}
            data = gates.gate_main(root, 'X', schedule, {'a': {'status': 'valid'}, 'd': {'status': 'valid'}},
                                   {'unresolved': ['missing second review']})
            ranking.parse_document(data)
            unit = dict(data['units'][0], judgments_locked=False, equivalence_review_locked=False)
            result = ranking.compare_set(unit, {})
            self.assertEqual(result['status'], 'not_evaluable')
            self.assertIsNone(result['ordinary'])
            self.assertEqual(result['candidates'][0]['source_opening'], original)
            self.assertIsNone(result['candidates'][0]['intelligible'])

    def test_missing_preservation_review_keeps_all_raw_id_obligations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'raw.json').write_text(json.dumps({'openings': [{'id': 'X1'}, {'id': 'X2'}]}))
            schedule = {'p09_pairs': [{'pair_id': 'pair', 'case_id': 'X', 'stratum': 'untouched_authored',
                                      'raw_sources': ['raw.json'], 'arms': {'ordinary': 'a', 'P09': 'b'}}]}
            data = gates.gate_pairs(root, 'p09', schedule,
                                    {'a': {'status': 'valid'}, 'b': {'status': 'valid'}}, {'unresolved': []})
            self.assertEqual(len(data['pairs']), 1)
            self.assertEqual(len(data['pairs'][0]['arms']), 2)
            for arm in data['pairs'][0]['arms']:
                self.assertEqual([r['source_id'] for r in arm['raw']], ['X1', 'X2'])
                self.assertTrue(all(r['causal_relation'] is None for r in arm['raw']))
                self.assertFalse(arm['assessment_complete'])


if __name__ == '__main__':
    unittest.main()
