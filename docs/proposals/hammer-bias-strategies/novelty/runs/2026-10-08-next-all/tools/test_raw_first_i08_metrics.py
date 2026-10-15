"""Reporting safeguards, unscored fixtures; no model-outcome evidence."""
import unittest
from copy import deepcopy
from itertools import combinations
import raw_first_i08_metrics as i


def fixture():
    arms = {}
    for n in sorted(i.CONCERNS | i.TREATMENTS):
        arms[n] = {'job_id': n, 'candidate_count': 1,
                   'qualified_family_bounds': [1, 1],
                   'potentially_qualified_family_bounds': [1, 1],
                   'cards': [{'card_id': n, 'qualification': {'status': 'eligible'},
                              'locked_values': {'intelligible': True}}]}
    case = {'study_id': 'I08', 'arms': arms, 'raw_comparison_evaluable': True,
            'denominators': {'raw_cards': 5, 'actual_native_starts': 11},
            'fully_retained_rows': 2}
    pairs = {frozenset([a, b]): {'values': {'relation': 'distinct'},
                               'field_status': {'relation': 'agreed'}}
             for a, b in combinations(arms, 2)}
    return case, pairs


class ReportingSafeguards(unittest.TestCase):
    def test_shared_cards_preserved_without_creation_credit(self):
        c, p = fixture()
        r = i.convergence_from_case(c, p)
        self.assertEqual(set(r['arms']), i.TREATMENTS)
        self.assertEqual(set(r['shared_concerns']), i.CONCERNS)
        self.assertEqual(r['denominators']['convergence_raw_cards'], 2)
        self.assertEqual(r['denominators']['shared_concern_cards'], 3)
        self.assertEqual(r['denominators']['actual_native_starts'], 11)
        self.assertEqual(r['convergence_comparison']['shared_concern_creation_credit'], 0)

    def test_all_intelligible_rivals_block_exclusivity_even_if_ineligible(self):
        c, p = fixture()
        c['arms']['I08-consensus']['cards'][0]['qualification']['status'] = 'ineligible'
        p[frozenset(i.TREATMENTS)]['values']['relation'] = 'equivalent'
        r = i.convergence_from_case(c, p)
        self.assertEqual(r['arms']['I08-deferred']['primary_exclusivity']['I08-deferred']['status'], 'not_exclusive')

    def test_uncertain_direct_pair_stays_unresolved(self):
        c, p = fixture()
        p[frozenset(i.TREATMENTS)]['field_status']['relation'] = 'unresolved'
        r = i.convergence_from_case(c, p)
        self.assertEqual(r['arms']['I08-deferred']['primary_exclusivity']['I08-deferred']['status'], 'unresolved')

    def test_shared_overlap_reported_separately(self):
        c, p = fixture()
        p[frozenset(['I08-deferred', 'concern-evidence'])]['values']['relation'] = 'parameter'
        r = i.convergence_from_case(c, p)['arms']['I08-deferred']
        self.assertEqual(r['primary_exclusivity']['I08-deferred']['status'], 'exclusive')
        self.assertEqual(r['distinct_from_shared_concerns']['I08-deferred']['status'], 'not_exclusive')

    def test_incomplete_case_not_reported_as_zero(self):
        c, p = fixture()
        c['raw_comparison_evaluable'] = False
        r = i.convergence_from_case(c, p)
        self.assertIsNone(r['arms']['I08-deferred']['primary_exclusivity'])
        self.assertIsNone(r['convergence_comparison']['deferred_minus_consensus_family_bounds']['qualified_family_bounds'])

    def test_signed_intervals_preserve_uncertainty(self):
        c, p = fixture()
        c['arms']['I08-deferred']['potentially_qualified_family_bounds'] = [0, 2]
        c['arms']['I08-consensus']['potentially_qualified_family_bounds'] = [1, 2]
        r = i.convergence_from_case(c, p)
        self.assertEqual(r['convergence_comparison']['deferred_minus_consensus_family_bounds']['potentially_qualified_family_bounds'], [-2, 1])

    def test_original_judgments_not_mutated(self):
        c, p = fixture()
        before = deepcopy((c, p))
        i.convergence_from_case(c, p)
        self.assertEqual((c, p), before)

    def test_missing_arm_rejected(self):
        c, p = fixture()
        del c['arms']['concern-evidence']
        with self.assertRaises(ValueError):
            i.convergence_from_case(c, p)


if __name__ == '__main__':
    unittest.main()
