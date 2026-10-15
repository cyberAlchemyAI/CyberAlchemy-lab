"""Unscored P10 conservation and gate fixtures."""
import unittest
from copy import deepcopy
from presentation_v4 import views


def card(name, **kw):
    return dict(id=name, fit='preserves', usefulness=1, observability=2,
                intelligible=True, support='inference', novelty='new',
                contract='met', retention='retained', family_id=name,
                family_confirmed=True, uncertain_links=False, raw_order=0, **kw)


class ViewContracts(unittest.TestCase):
    def test_resolved_nonqualifying_family_allows_ordinary_fallback(self):
        c = card('a');c.update(family_confirmed=False, novelty='equivalent')
        r = views([c])
        self.assertEqual(r['status'], 'evaluable')
        self.assertEqual(r['ordinary'], ['a'])
        self.assertEqual(r['alternative'], ['a'])
        self.assertEqual(r['eligible_ids'], [])

    def test_unresolved_family_field_gates(self):
        c = card('a');c['family_confirmed'] = None
        self.assertEqual(views([c])['status'], 'not_evaluable')

    def test_no_opening_evaluable_when_execution_complete(self):
        self.assertEqual(views([])['ordinary'], [])
        self.assertEqual(views([])['status'], 'evaluable')

    def test_failed_coverage_not_zero(self):
        self.assertIsNone(views([], context_complete=False)['ordinary'])

    def test_partial_operator_contract_does_not_erase_exposure_eligibility(self):
        c = card('a');c['contract'] = 'partial'
        self.assertEqual(views([c])['eligible_ids'], ['a'])

    def test_unresolved_retention_and_pair_gate(self):
        for key, value in [('retention', 'uncertain'), ('uncertain_links', True)]:
            c = card('a');c[key] = value
            self.assertEqual(views([c])['status'], 'not_evaluable')

    def test_two_distinct_source_families_cannot_add_exposure(self):
        a,b = card('a'),card('b')
        a['novelty'] = 'equivalent'
        r = views([a,b])
        self.assertEqual(r['ordinary'], r['alternative'])
        self.assertEqual(r['entering_ids'], [])

    def test_three_card_positive_control_preserves_first_and_inserts_eligible(self):
        a,b,c = card('a'),card('b'),card('c')
        a.update(usefulness=2, novelty='equivalent');b['novelty'] = 'equivalent'
        r = views([a,b,c])
        self.assertEqual(r['ordinary'], ['a','b'])
        self.assertEqual(r['alternative'], ['a','c'])
        self.assertTrue(r['first_unchanged'])
        self.assertEqual(r['entering_ids'], ['c'])
        self.assertEqual(r['displaced_ids'], ['b'])

    def test_no_input_or_assessment_mutation(self):
        cs = [card('a'),card('b')];before = deepcopy(cs)
        views(cs)
        self.assertEqual(cs,before)


    def test_null_contract_is_ordinary_visible_but_ineligible(self):
        c = card('a');c['contract'] = None
        result = views([c])
        self.assertEqual(result['ordinary'], ['a'])
        self.assertEqual(result['alternative'], ['a'])
        self.assertEqual(result['eligible_ids'], [])
        self.assertIsNone(c['contract'])

    def test_resolved_operator_contract_variants_do_not_credit_operator_success(self):
        for value in ['met', 'partial', 'not_met', 'inapplicable']:
            c = card('a');c['contract'] = value
            self.assertEqual(views([c])['eligible_ids'], ['a'])

    def test_order_precedence_fit_then_usefulness_then_observability_then_source_then_id(self):
        variants = [
            ({'fit':'uncertain','usefulness':2}, {'fit':'preserves','usefulness':0}),
            ({'usefulness':0,'observability':2}, {'usefulness':1,'observability':0}),
            ({'observability':1,'raw_order':0}, {'observability':2,'raw_order':1}),
            ({'raw_order':1}, {'raw_order':0}),
        ]
        for low, high in variants:
            x,y = card('a'),card('z');x.update(low);y.update(high)
            self.assertEqual(views([x,y])['ordinary'], ['z','a'])
        self.assertEqual(views([card('z'),card('a')])['ordinary'], ['a','z'])

    def test_raw_order_required_without_silent_zero_fallback(self):
        c = card('a');del c['raw_order']
        self.assertIsNone(views([c])['ordinary'])


if __name__ == '__main__':
    unittest.main()
