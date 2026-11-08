import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t15_relation_closure", HERE / "closure.py")
closure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(closure)


class RelationClosure(unittest.TestCase):
    def test_selected_mapping_has_exact_ten(self):
        result = closure.verify()
        self.assertEqual(result["count"], len(result["relation_versions"]))

    def test_extra_same_family_relation_refuses(self):
        rows = json.loads(closure.MAPPING.read_bytes())["rows"]
        expected = closure.selected_versions(closure.SELECTION.read_bytes())
        extra = json.loads(json.dumps(next(r for r in rows if r["artifact"]["version_ref"] in expected)))
        extra["artifact"]["version_ref"] = closure.PREFIX + "unexpected@1.0.0-candidate.1"
        rows.append(extra)
        with self.assertRaisesRegex(ValueError, "current relation closure differs"):
            closure.check_rows(rows, expected)

    def test_missing_selected_relation_refuses(self):
        rows = json.loads(closure.MAPPING.read_bytes())["rows"]
        expected = closure.selected_versions(closure.SELECTION.read_bytes())
        rows = [r for r in rows if r["artifact"]["version_ref"] != next(iter(expected))]
        with self.assertRaisesRegex(ValueError, "current relation closure differs"):
            closure.check_rows(rows, expected)

    def test_wrong_selected_relation_carrier_refuses(self):
        rows = json.loads(closure.MAPPING.read_bytes())["rows"]
        expected = closure.selected_versions(closure.SELECTION.read_bytes())
        selected = next(r for r in rows if r["artifact"]["version_ref"] in expected)
        selected["artifact"]["carrier_ref"] = "cal.artifact-type.work/v1"
        with self.assertRaisesRegex(ValueError, "current relation carrier differs"):
            closure.check_rows(rows, expected)


if __name__ == "__main__":
    unittest.main()
