from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("t10_aggregate", HERE / "aggregate.py")
AGGREGATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AGGREGATE)


class All29AggregateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((HERE / "CATALOG.json").read_bytes())

    def test_exact_catalog(self):
        AGGREGATE.validate_catalog(self.catalog)

    def test_duplicate_and_missing_member_refuse(self):
        duplicated = deepcopy(self.catalog)
        duplicated["packages"][-1]["members"] = duplicated["packages"][0]["members"]
        with self.assertRaisesRegex(ValueError, "29-member local coverage"):
            AGGREGATE.validate_catalog(duplicated)
        missing = deepcopy(self.catalog)
        missing["packages"][-1]["members"] = missing["packages"][-1]["members"][:-1]
        with self.assertRaisesRegex(ValueError, "29-member local coverage|catalog package"):
            AGGREGATE.validate_catalog(missing)

    def test_false_original_admission_and_wrong_kind_refuse(self):
        sample = json.loads(AGGREGATE.read_selected(self.catalog["packages"][0]["result"]))
        self.assertEqual(AGGREGATE.members_of(sample), self.catalog["packages"][0]["members"])
        admitted = deepcopy(sample)
        admitted["original_member_admitted"] = True
        with self.assertRaisesRegex(ValueError, "local representation or original admission"):
            AGGREGATE.members_of(admitted)
        admitted_total = deepcopy(sample)
        admitted_total["original_members_admitted"] = 29
        with self.assertRaisesRegex(ValueError, "local result count or authority ceiling"):
            AGGREGATE.members_of(admitted_total)
        wrong_kind = deepcopy(sample)
        wrong_kind["documents"]["typed_relation"]["kind"] = "governed-model"
        with self.assertRaisesRegex(ValueError, "local representation or original admission"):
            AGGREGATE.members_of(wrong_kind)

    def test_full_byte_backed_replay(self):
        fresh = AGGREGATE.build()
        self.assertEqual(fresh["covered_member_indices"], list(range(29)))
        self.assertEqual(fresh["fresh_exact_matches"], 14)
        self.assertEqual(fresh["original_members_admitted"], 0)
        self.assertTrue(fresh["local_mapping_complete"])
        self.assertEqual(fresh, json.loads((HERE / "RESULT.json").read_bytes()))


if __name__ == "__main__":
    unittest.main()
