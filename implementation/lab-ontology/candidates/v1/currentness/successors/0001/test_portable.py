"""Focused negative checks for the declared locator equivalence boundary."""
import copy
import unittest
import portable as P


class Guards(unittest.TestCase):
    def test_exact_ref(self):
        P.equivalent_ref((P.COMMIT + '\n').encode('ascii'))

    def test_moved_commit(self):
        with self.assertRaises(ValueError):
            P.equivalent_ref(('0' * 40 + '\n').encode('ascii'))

    def test_alternate_ref_encoding(self):
        with self.assertRaises(ValueError):
            P.equivalent_ref(P.COMMIT.encode('ascii'))

    def sample(self):
        original = {'files': [{'path': P.REF, 'sha256': P.REF_SHA}, {'path': 'retained', 'sha256': 'a' * 64}],
                    'result': 'PASS', 'task_complete': True, 'source_bindings': [{'path': 'contract', 'sha256': 'b' * 64}],
                    'claim_ceiling': 'candidate only'}
        successor = copy.deepcopy(original)
        replacement = {'path': 'witness/main', 'sha256': P.REF_SHA}
        successor['files'][0] = replacement
        successor['portable_locator_routes'] = [{'historical_binding': original['files'][0], 'portable_binding': replacement}]
        return original, successor

    def test_complete_partition(self):
        P.check_partition(*self.sample())

    def test_retained_file_dropped(self):
        a, b = self.sample(); b['files'].pop()
        with self.assertRaises(ValueError): P.check_partition(a, b)

    def test_digest_substitution(self):
        a, b = self.sample(); b['files'][0]['sha256'] = '0' * 64
        with self.assertRaises(ValueError): P.check_partition(a, b)

    def test_undeclared_route(self):
        a, b = self.sample(); b['portable_locator_routes'] = []
        with self.assertRaises(ValueError): P.check_partition(a, b)

    def test_source_obligation_drop(self):
        a, b = self.sample(); b['source_bindings'] = []
        with self.assertRaises(ValueError): P.check_partition(a, b)

    def test_claim_inflation(self):
        a, b = self.sample(); b['claim_ceiling'] = 'admitted'
        with self.assertRaises(ValueError): P.check_partition(a, b)


if __name__ == '__main__': unittest.main(verbosity=2)
