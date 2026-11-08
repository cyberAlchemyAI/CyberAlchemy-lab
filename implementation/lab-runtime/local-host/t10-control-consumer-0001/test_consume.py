import copy
import json
import unittest

from consume import CONTROL, ROOT, RUN, T31_RESULT, T31_RESULT_SHA256, read_pinned, selected_validator, validate_run, verify_lineage


class ControlConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control = json.loads((ROOT / CONTROL).read_bytes())
        cls.sample_run = json.loads((ROOT / RUN).read_bytes())

    def test_actual_candidate_run_passes(self):
        validate_run(selected_validator(self.control), self.sample_run)

    def test_changed_bound_schema_is_refused(self):
        control = copy.deepcopy(self.control)
        control["control_bindings"][1]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "exact two ordered schemas"):
            selected_validator(control)

    def test_omitted_status_axis_is_refused(self):
        run = copy.deepcopy(self.sample_run)
        del run["status_axes"]["admission"]
        with self.assertRaisesRegex(ValueError, "workflow run invalid"):
            validate_run(selected_validator(self.control), run)

    def test_invented_research_state_is_refused(self):
        run = copy.deepcopy(self.sample_run)
        run["state"] = "released"
        with self.assertRaisesRegex(ValueError, "workflow run invalid"):
            validate_run(selected_validator(self.control), run)

    def test_changed_source_clause_is_refused(self):
        control = copy.deepcopy(self.control)
        control["source_facts"][-1]["exact_value"]["required"].pop()
        with self.assertRaisesRegex(ValueError, "changed selected clause"):
            selected_validator(control)

    def test_common_schema_cannot_replace_workflow_schema(self):
        control = copy.deepcopy(self.control)
        control["control_bindings"][1] = control["control_bindings"][0]
        with self.assertRaisesRegex(ValueError, "exact two ordered schemas"):
            selected_validator(control)

    def test_runtime_permission_cannot_be_inferred(self):
        control = copy.deepcopy(self.control)
        control["native_or_runtime_use_allowed"] = True
        with self.assertRaisesRegex(ValueError, "wrong selected control"):
            selected_validator(control)

    def test_wrong_option_is_refused(self):
        control = copy.deepcopy(self.control)
        control["option_id"] = "T10:control-option:99"
        with self.assertRaisesRegex(ValueError, "wrong selected control"):
            selected_validator(control)

    def test_selected_run_matches_t31_producer_receipt(self):
        result = read_pinned({"path": T31_RESULT, "sha256": T31_RESULT_SHA256})
        selected = [row for row in result["new_output_transitions"] if row["transition_ref"] == "transition:research:executed"]
        self.assertEqual(len(selected), 1)
        verify_lineage(result, __import__("hashlib").sha256((ROOT / RUN).read_bytes()).hexdigest())
        selected[0]["workflow_run_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "lineage mismatch"):
            verify_lineage(result, __import__("hashlib").sha256((ROOT / RUN).read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
