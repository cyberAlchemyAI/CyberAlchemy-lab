"""Unscored source conservation and stage-gate fixtures."""
import unittest
from copy import deepcopy
from unittest.mock import patch
import i10_source_pool_v4 as a


def retained():
    values = dict(relation='retained', discriminator='retained', uncertainty='retained',
                  lineage_consistent=True, fit_preserved=True, complete_protected_fields=True)
    return {'identity': {'source_card_id': 'opaque'}, 'values': values,
            'field_status': {k: 'agreed' for k in values}}


def fixture():
    values = dict(fit='preserves', usefulness=1, observability=2, intelligible=True,
                  support='inference', novelty='equivalent', contract='met', family_confirmed=False)
    card = {'card_id': 'opaque', 'local_id': 'R1', 'locked_values': values,
            'field_status': {k: 'agreed' for k in values}}
    metric = dict(arms={'I06-ordinary': {'job_id': 'RAW', 'cards': [card]}},
                  raw_execution_valid=True, raw_independent_review_complete=True,
                  post_independent_review_complete=True,
                  denominators={'invalid_terminal_outputs': 0, 'planned_generation_roles': 6, 'planned_review_roles': 4, 'actual_native_starts': 10, 'actual_terminal_joins': 10, 'structurally_valid_terminal_outputs': 10, 'skipped_roles': 0}, saved_words_proxy=123, source_bindings=[])
    raw = {'rows': []}
    post = {'rows': [dict(table='retention_rows', **retained())]}
    source = {'openings': [{'id': 'R1', 'claim': 'Exact hypothetical source payload.'}]}
    return metric, raw, post, source


def run_fixture(metric, raw, post, source):
    verified = {'stage_coverage': {'complete': True}, 'source_orders': {'RAW': [{'local_id': c['id'], 'frozen_source_order': i} for i, c in enumerate(source['openings'])]}, 'source_bindings': [], 'ordinary_generic_full_source_context_verified': True}
    with patch.object(a.context, 'source_context', return_value=verified), \
         patch.object(a.m, 'case_metrics', return_value=metric), \
         patch.object(a.f, 'bound_lock', side_effect=[(raw, {}), (post, {})]), \
         patch.object(a.g, 'jobs', return_value={'RAW': {'output_ref': 'fixture.json'}}), \
         patch.object(a.f, 'read', return_value=source), \
         patch.object(a.g, 'sha', return_value='fixture-sha'):
        return a.pool('H-C1', 'I06-ordinary')


class SourceContracts(unittest.TestCase):
    def test_exact_payload_and_nonqualifying_pool_preserved(self):
        data = fixture();before = deepcopy(data)
        r = run_fixture(*data)
        self.assertEqual(r['views']['ordinary'], ['RAW:R1'])
        self.assertEqual(r['views']['eligible_ids'], [])
        self.assertEqual(r['source_evidence'][0]['raw_payload'], data[3]['openings'][0])
        self.assertEqual(data, before)
        self.assertEqual(r['new_generation_or_review_call_credit'], 0)

    def test_failed_post_does_not_erase_raw_payload_or_invent_zero_view(self):
        data = fixture();data[0]['post_independent_review_complete'] = False
        r = run_fixture(*data)
        self.assertIsNone(r['views']['ordinary'])
        self.assertEqual(len(r['source_evidence']), 1)

    def test_unresolved_scalar_kept_null(self):
        data = fixture()
        data[0]['arms']['I06-ordinary']['cards'][0]['field_status']['fit'] = 'scalar_unresolved'
        r = run_fixture(*data)
        self.assertIsNone(r['candidates'][0]['fit'])
        self.assertEqual(r['views']['status'], 'not_evaluable')

    def test_missing_source_card_rejected(self):
        data = fixture();data[3]['openings'] = []
        with self.assertRaises(AssertionError):
            run_fixture(*data)

    def test_generic_and_old_pilot_not_display_pools(self):
        for case, arm in [('H-P', 'I06-ordinary'), ('H-C1', 'I06-generic')]:
            with self.assertRaises(ValueError):
                a.pool(case, arm)

    def test_retention_needs_every_protected_field(self):
        row = retained();row['values']['complete_protected_fields'] = False
        self.assertEqual(a.retention_status(row), 'lost')

    def test_unknown_retention_never_receives_preservation_credit(self):
        row = retained();row['field_status']['discriminator'] = 'scalar_unresolved'
        self.assertEqual(a.retention_status(row), 'uncertain')
        self.assertEqual(a.retention_status(None), 'unobservable')

    def test_boolean_zero_does_not_receive_preservation_credit(self):
        row = retained();row['values']['complete_protected_fields'] = 0
        self.assertEqual(a.retention_status(row), 'uncertain')


    def test_invalid_raw_and_compression_gates_preserving_candidates(self):
        for raw_valid, invalid in [(False, 1), (True, 1)]:
            data = fixture();data[0]['raw_execution_valid'] = raw_valid
            data[0]['denominators']['invalid_terminal_outputs'] = invalid
            data[0]['denominators']['structurally_valid_terminal_outputs'] = 9
            result = run_fixture(*data)
            self.assertIsNone(result['views']['ordinary'])
            self.assertEqual(len(result['source_evidence']), 1)

    def test_missing_or_skipped_compression_gates_even_empty_raw(self):
        for empty in [False, True]:
            for skipped in [False, True]:
                data = fixture()
                if empty:
                    data[0]['arms']['I06-ordinary']['cards'] = []
                    data[3]['openings'] = []
                data[0]['denominators']['actual_native_starts'] = 9
                data[0]['denominators']['actual_terminal_joins'] = 9
                data[0]['denominators']['structurally_valid_terminal_outputs'] = 9
                data[0]['denominators']['skipped_roles'] = int(skipped)
                result = run_fixture(*data)
                self.assertIsNone(result['views']['ordinary'])
                self.assertIsNone(result['full_text_burden']['ordinary'])
                self.assertEqual(len(result['source_evidence']), 0 if empty else 1)

    def test_null_contract_keeps_payload_ordinary_and_null_score(self):
        data = fixture()
        c = data[0]['arms']['I06-ordinary']['cards'][0]
        c['locked_values']['contract'] = None;c['field_status']['contract'] = 'scalar_unresolved'
        result = run_fixture(*data)
        self.assertEqual(result['views']['ordinary'], ['RAW:R1'])
        self.assertEqual(result['views']['eligible_ids'], [])
        self.assertIsNone(result['full_text_burden']['ordinary']['selected_scores_and_contracts'][0]['contract'])


if __name__ == '__main__':
    unittest.main()
