"""Preparation-only tests: artificial comparisons, actual historical schema only."""

import copy
import hashlib
import json
from pathlib import Path
import random
import tempfile
import unittest

import ranking


def candidate(raw_id, family_id=None, **changes):
    value = dict(raw_id=raw_id, family_id=family_id or raw_id, novelty='equivalent',
                 usefulness=2, fit='preserves', observability=2, retention='retained',
                 support='inference', judgment_resolved=True, intelligible=True)
    value.update(changes)
    return value


def unit(*records, **changes):
    value = dict(unit_id='artificial', execution_valid=True, assessment_complete=True,
                 judgments_locked=True, equivalence_review_locked=True, raw=list(records))
    value.update(changes)
    return value


def families(*records):
    return {record['family_id']: dict(equivalence_status='confirmed', uncertain_equivalence_with=[])
            for record in records}


def document(count):
    return dict(judgments_locked=True, equivalence_review_locked=True, families={},
                units=[unit(unit_id='artificial-' + str(i)) for i in range(count)],
                sources=[{'path': 'artificial-J1.json', 'sha256': '1' * 64},
                         {'path': 'artificial-J2.json', 'sha256': '2' * 64}])


def synthetic_run(root, fresh=True):
    (root / 'inputs/historical-ranking').mkdir(parents=True)
    (root / 'reports').mkdir()
    for name, count in ranking.HISTORICAL_FILES.items():
        (root / 'inputs/historical-ranking' / name).write_text(json.dumps(document(count)))
    if fresh:
        for name in ranking.FRESH_FILES:
            (root / name).write_text(json.dumps(document(28)))


class ComparisonTests(unittest.TestCase):
    def compare(self, *records, **changes):
        return ranking.compare_set(unit(*records, **changes), families(*records))

    def test_first_slot_and_fixed_score_conservation(self):
        records = [candidate('Z1', text='first three words'), candidate('Z2', text='ordinary second'),
                   candidate('A1', novelty='new', usefulness=1, text='qualified alternative')]
        result = self.compare(*records)
        self.assertEqual(result['ordinary']['raw_ids'], ['Z1', 'Z2'])
        self.assertEqual(result['alternative']['raw_ids'], ['Z1', 'A1'])
        self.assertEqual(result['ordinary']['fixed_scores'][0], result['alternative']['fixed_scores'][0])
        self.assertEqual(result['entering']['fixed_scores']['usefulness'], 1)
        self.assertEqual(result['displaced']['fixed_scores']['usefulness'], 2)
        self.assertEqual(result['utility_displacement']['usefulness_delta'], -1)
        self.assertEqual(result['family_exposures'][0]['family_id'], 'A1')
        self.assertEqual(result['family_exposures'][0]['alternative'], 1)
        self.assertEqual(result['text_burden']['ordinary_words'], 5)
        self.assertEqual(result['text_burden']['alternative_words'], 5)

    def test_inputs_are_immutable_and_candidates_preserved(self):
        records = [candidate('Z1', metadata={'nested': ['unchanged']}), candidate('A1', novelty='new')]
        source_unit, source_families = unit(*records), families(*records)
        before = copy.deepcopy((source_unit, source_families))
        result = ranking.compare_set(source_unit, source_families)
        self.assertEqual((source_unit, source_families), before)
        self.assertEqual(result['candidates'], records)
        result['candidates'][0]['metadata']['nested'].append('output mutation')
        self.assertEqual((source_unit, source_families), before)

    def test_stable_raw_order_and_lexical_ties(self):
        records = [candidate(raw_id) for raw_id in ['omega', 'Q2', 'A2', 'Q1', 'A1', 'Z2', 'alpha', 'Z1']]
        expected = ['Z1', 'Z2', 'A1', 'A2', 'Q1', 'Q2', 'alpha', 'omega']
        for seed in range(10):
            random.Random(seed).shuffle(records)
            self.assertEqual([record['raw_id'] for record in sorted(records, key=ranking._rank)], expected)
        result = self.compare(candidate('omega'), candidate('alpha'), candidate('beta'))
        self.assertEqual(result['ordinary']['raw_ids'], ['alpha', 'beta'])

    def test_fit_then_usefulness_then_observability(self):
        result = self.compare(candidate('Z1', fit='conditional'), candidate('Z2', fit='uncertain'),
                              candidate('A1', usefulness=1), candidate('A2', observability=1))
        self.assertEqual(result['ordinary']['raw_ids'], ['A2', 'A1'])

    def test_family_duplication_cannot_take_two_slots(self):
        result = self.compare(candidate('Z1', 'same'), candidate('A1', 'same', novelty='new'),
                              candidate('Z2', 'other'))
        self.assertEqual(result['ordinary']['raw_ids'], ['Z1', 'Z2'])
        self.assertEqual(result['alternative']['raw_ids'], ['Z1', 'Z2'])
        self.assertFalse(result['eligibility']['A1']['eligible_for_second'])

    def test_fallback_with_no_eligible_alternative_is_valid(self):
        result = self.compare(candidate('Z1'), candidate('Z2'))
        self.assertEqual(result['status'], 'evaluable')
        self.assertFalse(result['alternative_found'])
        self.assertEqual(result['ordinary'], result['alternative'])
        self.assertIsNone(result['entering'])
        self.assertIsNone(result['displaced'])
        self.assertEqual(result['utility_displacement']['usefulness_delta'], 0)

    def test_zero_and_one_candidate_complete_exposure(self):
        empty = self.compare()
        self.assertEqual(empty['status'], 'evaluable')
        self.assertEqual(empty['ordinary']['raw_ids'], [])
        self.assertEqual(empty['alternative']['raw_ids'], [])
        self.assertEqual(empty['family_exposures'], [])
        one = self.compare(candidate('A1', novelty='new'))
        self.assertEqual(one['ordinary']['raw_ids'], ['A1'])
        self.assertEqual(one['alternative']['raw_ids'], ['A1'])
        self.assertFalse(one['alternative_found'])

    def test_lost_candidate_is_preserved_but_never_presented(self):
        result = self.compare(candidate('Z1', retention='lost'), candidate('A1', novelty='new'))
        self.assertEqual(len(result['candidates']), 2)
        self.assertEqual(result['ordinary']['raw_ids'], ['A1'])
        self.assertFalse(result['eligibility']['Z1']['qualifies'])

    def test_unsupported_and_unintelligible_do_not_qualify(self):
        result = self.compare(candidate('Z1'), candidate('Z2'),
                              candidate('A1', novelty='new', support='unsupported'),
                              candidate('A2', novelty='new', intelligible=False))
        self.assertFalse(result['eligibility']['A1']['qualifies'])
        self.assertFalse(result['eligibility']['A2']['qualifies'])
        self.assertEqual(result['alternative']['raw_ids'], ['Z1', 'Z2'])

    def test_unresolved_scalars_preserved_and_excluded(self):
        records = [candidate('Z1'), candidate('Z2'), candidate('A1', novelty='new', judgment_resolved=False),
                   candidate('A2', novelty='new', unresolved_judgments=[{'fields': ['fit']}])]
        result = self.compare(*records)
        self.assertEqual(result['candidates'], records)
        self.assertFalse(result['eligibility']['A1']['qualifies'])
        self.assertFalse(result['eligibility']['A2']['qualifies'])
        self.assertEqual(result['alternative']['raw_ids'], ['Z1', 'Z2'])

    def test_unresolved_retained_ranking_keys_gate_without_inventing_scores(self):
        for field in ('fit', 'usefulness', 'observability'):
            result = self.compare(candidate('Z1'), candidate('Z2'),
                                  candidate('A1', novelty='new', judgment_resolved=False, **{field: None}))
            self.assertEqual(result['status'], 'not_evaluable')
            self.assertIn('unresolved-ranking-score:A1:' + field, result['gate_causes'])
            self.assertIsNone(result['ordinary'])
            self.assertIsNone(result['candidates'][2][field])

    def test_null_nonranking_scalars_only_prevent_alternative(self):
        for field in ('novelty', 'support', 'contract'):
            result = self.compare(candidate('Z1'), candidate('Z2'), candidate('A1', novelty='new', **{field: None})
                                  if field != 'novelty' else candidate('A1', novelty=None))
            self.assertEqual(result['status'], 'evaluable')
            self.assertFalse(result['eligibility']['A1']['qualifies'])
            self.assertEqual(result['alternative']['raw_ids'], ['Z1', 'Z2'])

    def test_conditional_fit_ranks_but_is_ineligible(self):
        result = self.compare(candidate('Z1', fit='violates'),
                              candidate('A1', fit='conditional', novelty='new'))
        self.assertEqual(result['ordinary']['raw_ids'], ['A1', 'Z1'])
        self.assertFalse(result['eligibility']['A1']['qualifies'])
        self.assertEqual(result['violations']['ordinary'], ['Z1'])
        self.assertEqual(result['conditional_fit']['ordinary'], ['A1'])

    def test_uncertain_family_status_excluded(self):
        records = [candidate('Z1'), candidate('Z2'), candidate('A1', novelty='new')]
        family_map = families(*records)
        family_map['A1']['equivalence_status'] = 'uncertain'
        result = ranking.compare_set(unit(*records), family_map)
        self.assertFalse(result['eligibility']['A1']['qualifies'])

    def test_uncertain_links_exclude_both_directions_without_merge(self):
        for source, target in [('Z1', 'A1'), ('A1', 'Z1')]:
            records = [candidate('Z1'), candidate('Z2'), candidate('A1', novelty='new')]
            family_map = families(*records)
            family_map[source]['uncertain_equivalence_with'] = [target]
            result = ranking.compare_set(unit(*records), family_map)
            self.assertTrue(result['eligibility']['A1']['qualifies'])
            self.assertFalse(result['eligibility']['A1']['eligible_for_second'])
            self.assertEqual(result['alternative']['raw_ids'], ['Z1', 'Z2'])
            self.assertEqual(len(result['family_exposures']), 3)

    def test_uncertain_links_are_not_transitively_merged(self):
        records = [candidate('Z1'), candidate('Z2'), candidate('A1', novelty='new')]
        family_map = families(*records)
        family_map['Z1']['uncertain_equivalence_with'] = ['Z2']
        family_map['Z2']['uncertain_equivalence_with'] = ['A1']
        result = ranking.compare_set(unit(*records), family_map)
        self.assertEqual(result['alternative']['raw_ids'], ['Z1', 'A1'])

    def test_historical_missing_support_is_unavailable_not_unsupported(self):
        records = [candidate('Z1'), candidate('Z2'), candidate('A1', novelty='new')]
        del records[2]['support']
        result = self.compare(*records, stratum='historical')
        self.assertEqual(result['alternative']['raw_ids'], ['Z1', 'A1'])
        self.assertFalse(result['eligibility']['A1']['support_available'])
        self.assertNotIn('support', result['entering']['fixed_scores'])
        self.assertNotIn('support', result['candidates'][2])

    def test_fresh_missing_support_gates(self):
        record = candidate('A1', novelty='new')
        del record['support']
        result = self.compare(record)
        self.assertEqual(result['status'], 'not_evaluable')
        self.assertIn('support_missing:A1', result['gate_causes'])
        self.assertIsNone(result['ordinary'])
        self.assertIsNone(result['family_exposures'])

    def test_missing_execution_reviews_and_locks_gate(self):
        for flag in ('execution_valid', 'assessment_complete', 'judgments_locked', 'equivalence_review_locked'):
            for value in (False, None):
                source = unit(candidate('Z1'))
                if value is None:
                    del source[flag]
                else:
                    source[flag] = value
                result = ranking.compare_set(source, families(*source['raw']))
                self.assertEqual(result['status'], 'not_evaluable')
                self.assertIsNone(result['ordinary'])
                self.assertIsNone(result['family_exposures'])
                self.assertEqual(result['candidates'], source['raw'])

    def test_missing_neutral_d_and_explicit_missing_review_gate(self):
        for changes in ({'retention_observed': False}, {'missing_output_roles': ['D']},
                        {'skipped_roles': ['D']}, {'review_coverage_complete': False}):
            self.assertEqual(self.compare(candidate('Z1'), **changes)['status'], 'not_evaluable')

    def test_missing_text_is_null_not_output_word_proxy(self):
        result = self.compare(candidate('Z1', claim='three claim words'), candidate('Z2'), output_words=999)
        self.assertEqual(result['text_burden']['candidate_words'], {'Z1': 3, 'Z2': None})
        self.assertIsNone(result['text_burden']['ordinary_words'])


class InputTests(unittest.TestCase):
    def test_exact_actual_historical_schema_and_120_units_without_comparison(self):
        loaded = ranking.load_documents(Path(__file__).resolve().parents[1])
        self.assertEqual(len(loaded), 8)
        self.assertEqual(sum(len(source['data']['units']) for source in loaded), 120)
        self.assertTrue(all(len(source['sha256']) == 64 for source in loaded))

    def test_artificial_all_has_176_dispositions_and_source_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_run(root)
            before = {(root / name): (root / name).read_bytes() for name in ranking.FRESH_FILES}
            output = ranking.run(root, 'all')
            report = json.loads(output.read_text())
            self.assertEqual(report['dispositions'], 176)
            self.assertEqual(len(report['sources']), 10)
            self.assertEqual(sum(item['stratum'] == 'historical' for item in report['comparisons']), 120)
            self.assertEqual(sum(item['stratum'] == 'fresh' for item in report['comparisons']), 56)
            for path, source_bytes in before.items():
                self.assertEqual(path.read_bytes(), source_bytes)
                self.assertEqual(next(source['sha256'] for source in report['sources']
                                      if source['path'] == str(path.relative_to(root))),
                                 hashlib.sha256(source_bytes).hexdigest())
            self.assertEqual(report['sources'][0]['assessment_sources'][0]['sha256'], '1' * 64)

    def test_write_once(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_run(root)
            output = ranking.run(root, 'historical')
            source_bytes = output.read_bytes()
            with self.assertRaises(FileExistsError):
                ranking.run(root, 'historical')
            self.assertEqual(output.read_bytes(), source_bytes)

    def test_exact_file_set_and_counts_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_run(root)
            extra = root / 'inputs/historical-ranking/extra.json'
            extra.write_text('{}')
            with self.assertRaises(ValueError):
                ranking.load_documents(root)
            extra.unlink()
            path = root / 'inputs/historical-ranking/bundle-D1-resolved.json'
            path.write_text(json.dumps(document(7)))
            with self.assertRaises(ValueError):
                ranking.load_documents(root)
            self.assertFalse((root / 'reports/p10-historical.json').exists())

    def test_missing_fresh_source_and_bad_fresh_count_do_not_fake_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_run(root, fresh=False)
            with self.assertRaises(FileNotFoundError):
                ranking.run(root, 'all')
            for name in ranking.FRESH_FILES:
                (root / name).write_text(json.dumps(document(27)))
            with self.assertRaises(ValueError):
                ranking.run(root, 'all')
            self.assertFalse((root / 'reports/p10-all.json').exists())

    def test_container_rejects_duplicate_and_incomplete_records(self):
        for bad in ({}, {'families': {}, 'units': [{'unit_id': 'u', 'raw': [{}]}]},
                    {'families': {}, 'units': [unit(), unit()]}):
            with self.assertRaises(ValueError):
                ranking.parse_document(bad)

    def test_family_list_normalizes_without_mutating_inputs(self):
        record = candidate('A1', 'F1', novelty='new')
        data = document(1)
        data['units'] = [unit(record)]
        data['families'] = [{'family_id': 'F1', 'equivalence_status': 'confirmed',
                             'uncertain_equivalence_with': [], 'signature': 'artificial'}]
        before = copy.deepcopy(data)
        parsed = ranking.parse_document(data)
        self.assertEqual(set(parsed['families']), {'F1'})
        self.assertEqual(parsed['families']['F1'], before['families'][0])
        self.assertEqual(data, before)
        result = ranking.compare_set(parsed['units'][0], parsed['families'])
        self.assertEqual(result['status'], 'evaluable')
        parsed['families']['F1']['uncertain_equivalence_with'].append('output mutation')
        self.assertEqual(data, before)

    def test_family_list_rejects_duplicate_ids(self):
        data = document(1)
        data['families'] = [{'family_id': 'duplicate'}, {'family_id': 'duplicate'}]
        before = copy.deepcopy(data)
        with self.assertRaises(ValueError):
            ranking.parse_document(data)
        self.assertEqual(data, before)

    def test_unintelligible_null_family_is_unit_gate_without_cli_crash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_run(root)
            path = root / ranking.FRESH_FILES[0]
            data = document(28)
            record = candidate('A1', intelligible=False)
            record['family_id'] = None
            data['units'][0]['raw'] = [record]
            data['families'] = []
            before = copy.deepcopy(data)
            ranking.parse_document(data)
            self.assertEqual(data, before)
            path.write_text(json.dumps(data))
            report = json.loads(ranking.run(root, 'all').read_text())
            fresh = [item for item in report['comparisons'] if item['source'] == ranking.FRESH_FILES[0]]
            self.assertEqual(fresh[0]['status'], 'not_evaluable')
            self.assertIn('family_missing:None', fresh[0]['gate_causes'])
            self.assertEqual(fresh[0]['candidates'], [record])
            self.assertIsNone(fresh[0]['family_exposures'])
            self.assertEqual(fresh[1]['status'], 'evaluable')

    def test_false_unit_or_document_lock_cannot_be_overridden(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_run(root)
            path = root / ranking.FRESH_FILES[0]
            data = document(28)
            data['units'][0]['judgments_locked'] = False
            data['equivalence_review_locked'] = False
            path.write_text(json.dumps(data))
            report = json.loads(ranking.run(root, 'all').read_text())
            fresh = [item for item in report['comparisons'] if item['source'] == ranking.FRESH_FILES[0]]
            self.assertTrue(all(item['status'] == 'not_evaluable' for item in fresh))
            self.assertIn('judgments_locked_not_complete', fresh[0]['gate_causes'])


if __name__ == '__main__':
    unittest.main()
