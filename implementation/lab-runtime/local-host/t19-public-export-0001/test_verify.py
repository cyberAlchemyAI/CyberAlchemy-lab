"""Fast mutations against the durable T19 cold verifier."""
import copy
import json
import unittest
from run import HERE
from verify import verify

class ColdVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((HERE / 'RESULT.json').read_bytes())

    def test_current_physical_result(self):
        verify(copy.deepcopy(self.result))

    def refused(self, mutate):
        altered = copy.deepcopy(self.result)
        mutate(altered)
        with self.assertRaises(ValueError):
            verify(altered)

    def test_empty_cases_refused(self):
        self.refused(lambda x: x.update(cases=[]))

    def test_missing_negative_refused(self):
        self.refused(lambda x: x['cases'].pop())

    def test_duplicate_case_refused(self):
        self.refused(lambda x: x['cases'].__setitem__(4, copy.deepcopy(x['cases'][3])))

    def test_false_original_claim_refused(self):
        self.refused(lambda x: x.update(historical_custody_fixture_replayed=True))

    def test_changed_fixture_binding_refused(self):
        self.refused(lambda x: x['selected_public_fixture_bindings'][0].update(sha256='0'*64))

    def test_false_negative_reason_refused(self):
        self.refused(lambda x: x['cases'][2].update(error='unrelated exception'))

if __name__ == '__main__':
    unittest.main()
