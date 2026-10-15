"""Memory-only checks of nontrivial interaction and inheritance semantics."""
import unittest
import copy
import raw_i11_metrics_v1 as r


class Arithmetic(unittest.TestCase):
    def example(self):
        cells = {}
        for key in r.CELLS:
            a, b, c = map(int, key)
            value = a + 2*b + 3*c + 4*a*b + 5*b*c + 6*a*c + 7*a*b*c
            cells[key] = [value, value]
        return cells

    def test_full_interactions(self):
        out = r.factorial_contrasts(self.example())
        self.assertEqual({k:v['bounds'][0] for k,v in out['main'].items()},
                         {'inversion':7.75, 'attack':8.25, 'conversion':10.25})
        self.assertEqual({k:v['bounds'][0] for k,v in out['pair'].items()},
                         {'inversion_x_attack':7.5, 'inversion_x_conversion':9.5, 'attack_x_conversion':8.5})
        self.assertEqual(out['three_way']['bounds'], [7,7])

    def test_constant_shift_does_not_create_interaction(self):
        a = self.example()
        b = {k:[v[0]+100,v[1]+100] for k,v in a.items()}
        self.assertEqual(r.factorial_contrasts(a), r.factorial_contrasts(b))

    def test_unknown_corner_is_not_zero(self):
        a = self.example(); a['111'] = None
        out = r.factorial_contrasts(a)
        self.assertIsNone(out['three_way']['bounds'])
        self.assertEqual(out['three_way']['unavailable_corners'], ['111'])
        self.assertTrue(all(x['bounds'] is None for x in out['main'].values()))

    def test_generic_cannot_change_factorial_contrast(self):
        a = self.example(); before = r.factorial_contrasts(a)
        a['G'] = [999,999]
        self.assertEqual(before, r.factorial_contrasts(a))

    def test_interval_uncertainty_is_propagated(self):
        a = {k:[0,1] for k in r.CELLS}
        self.assertEqual(r.interval_contrast(a,[0])['bounds'], [-1,1])
        self.assertEqual(r.interval_contrast(a,[0,1])['bounds'], [-2,2])
        self.assertEqual(r.interval_contrast(a,[0,1,2])['bounds'], [-4,4])

    def test_bad_intervals_are_rejected(self):
        for bad in ([True,1], [3,2], [None,1]):
            a = self.example(); a['111'] = bad
            with self.assertRaises(ValueError): r.factorial_contrasts(a)

    def pair(self,a,b,rel,status='agreed'):
        return {frozenset([a,b]):{'values':{'relation':rel},'field_status':{'relation':status}}}

    def test_direct_inherited_relation_does_not_get_new_credit(self):
        self.assertEqual(r.appearance('new',['old'],self.pair('new','old','parameter'))['status'], 'inherited_family')

    def test_missing_or_disputed_relation_stays_unknown(self):
        self.assertEqual(r.appearance('new',['old'],{})['status'], 'unresolved')
        self.assertEqual(r.appearance('new',['old'],self.pair('new','old','distinct','family_unresolved'))['status'], 'unresolved')

    def test_direct_distinction_and_empty_prior(self):
        self.assertEqual(r.appearance('new',['old'],self.pair('new','old','distinct'))['status'], 'first_introduced')
        self.assertEqual(r.appearance('new',[],{})['status'], 'first_introduced')

    def fixture(self):
        i = r.i
        root = i.R
        fixture = i.read(root/'fixtures/composition-i11-maximal-inputs.v2.json')
        inputs = (fixture['schedule'], fixture['reviews'],
                  i.read(root/'generation-review-contract.v2.json'),
                  i.read(root/'criteria-generation.v2.json'),
                  i.read(root/'archives/case-archives.json'))
        packet, admin = i.build_raw_case('H-P', fixture['artifacts'], fixture['dispositions'], inputs=inputs)
        self.assertEqual(packet, i.read(root/'fixtures/composition-i11-maximal-raw.v2.json'))
        review = i.read(root/'reviews/composition-capacity/I11-maximal-raw-v2.json')
        # Fictional in-memory agreement only; this cannot serve as native evidence.
        lock = i.disputes.compare(packet, review, review)
        lock['independent_review_complete'] = True
        return fixture['schedule']['jobs'], admin['mapping'], lock

    def test_full_fictional_matrix_mapping_is_preserved(self):
        jobs, mapping, lock = self.fixture()
        before = copy.deepcopy(lock)
        result = r.summarize_units(jobs, mapping, lock, {j['job_id']:'valid' for j in jobs})
        self.assertEqual(len(result['units']),27)
        self.assertEqual(sum(x['candidate_count'] for x in result['units'].values()),54)
        self.assertEqual(set(result['final_cells']),set(r.CELLS)|{'G'})
        self.assertEqual(lock,before)

    def test_present_fixture_cards_do_not_turn_missing_execution_into_zero(self):
        jobs, mapping, lock = self.fixture()
        states = {j['job_id']:'valid' for j in jobs}
        target = next(j for j in jobs if j['arm']=='010' and j['stage']==3)
        states[target['job_id']] = 'missing'
        result = r.summarize_units(jobs,mapping,lock,states)
        self.assertIsNone(result['final_cells']['010']['qualified_card_count'])
        self.assertIsNone(result['factorial_qualified_family_contrasts']['three_way']['bounds'])


if __name__ == '__main__':
    unittest.main()
