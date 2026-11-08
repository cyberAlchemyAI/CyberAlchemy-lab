import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t10_endpoint_route", HERE / "route.py")
route = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route)


class EndpointControlRoutes(unittest.TestCase):
    def test_selected_receipt(self):
        expected = json.loads((HERE / "RESULT.json").read_bytes())
        actual = route.receipt()
        self.assertEqual(expected, actual)
        self.assertEqual([r["index"] for r in actual["routes"]], [0, 1, 2, 3])
        self.assertEqual(actual["selected_governed_model_representations"], 0)

    def test_wrong_kind_refuses(self):
        matrix = route.body(route.ROOT, {"path": route.MATRIX, "sha256": route.MATRIX_SHA})
        impact = route.body(route.ROOT, matrix["rows"][0]["original_target_bindings"][0])
        row = copy.deepcopy(matrix["rows"][0])
        row["member_ref"] = "protocol:C10:mapping-product"
        with self.assertRaisesRegex(ValueError, "wrong endpoint member"):
            route.endpoint(route.ROOT, row, impact, 0)

    def test_wrong_identity_selector_refuses(self):
        row = route.EXAMPLES[0]
        example = route.body(route.ROOT, {"path": row[0], "sha256": row[1]})
        matrix = route.body(route.ROOT, {"path": route.MATRIX, "sha256": route.MATRIX_SHA})
        schema = route.body(route.ROOT, matrix["rows"][0]["original_target_bindings"][2])
        impact = route.body(route.ROOT, matrix["rows"][0]["original_target_bindings"][0])
        proposal = copy.deepcopy(impact["endpoint_proposals"][0])
        proposal["identity_selector"] = "/product_id"
        with self.assertRaisesRegex(ValueError, "wrong endpoint proposal"):
            route.proposed_identity(example, schema, proposal, expected_field="project_id", expected_kind="project")

    def test_invalid_carrier_refuses(self):
        row = route.EXAMPLES[1]
        example = route.body(route.ROOT, {"path": row[0], "sha256": row[1]})
        matrix = route.body(route.ROOT, {"path": route.MATRIX, "sha256": route.MATRIX_SHA})
        schema = route.body(route.ROOT, matrix["rows"][1]["original_target_bindings"][2])
        impact = route.body(route.ROOT, matrix["rows"][0]["original_target_bindings"][0])
        example["product_id"] = None
        with self.assertRaisesRegex(ValueError, "invalid carrier"):
            route.proposed_identity(example, schema, impact["endpoint_proposals"][1],
                                    expected_field="product_id", expected_kind="product")

    def test_wrong_source_profile_relation_refuses(self):
        matrix = route.body(route.ROOT, {"path": route.MATRIX, "sha256": route.MATRIX_SHA})
        row = copy.deepcopy(matrix["rows"][3])
        row["proposed_model_relation"]["counterpart_ref"] = "implementation:wrong"
        with self.assertRaisesRegex(ValueError, "candidate relation differs"):
            route.source_profile(route.ROOT, row)

    def test_changed_original_body_refuses(self):
        matrix = route.body(route.ROOT, {"path": route.MATRIX, "sha256": route.MATRIX_SHA})
        selected = [{"path": route.MATRIX, "sha256": route.MATRIX_SHA}, route.PROFILES_CODE]
        for row in matrix["rows"][:4]:
            selected += [row[key] for key in ("original_body_binding", "original_disposition_binding", "review_choice_binding")]
            selected += row["original_target_bindings"] + row["original_evidence_bindings"] + row["prepared_postimage_bindings"]
        selected += [{"path": x[0], "sha256": x[1]} for x in route.EXAMPLES]
        with tempfile.TemporaryDirectory(prefix="t10-endpoint-") as name:
            root = Path(name)
            for binding in selected:
                target = root / binding["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(route.ROOT / binding["path"], target)
            original = root / matrix["rows"][0]["original_body_binding"]["path"]
            original.write_bytes(original.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "changed bytes"):
                route.routes(root)


if __name__ == "__main__":
    unittest.main()
