import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t31_design_gap", HERE / "check.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CausalityTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="t31-design-gap-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for relative, _ in module.FILES.values():
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(module.ROOT / relative, target)

    def selected(self, key):
        return self.root / module.FILES[key][0]

    def test_original_causal_non_count(self):
        result = module.diagnose(self.root)
        self.assertEqual((result["result"], result["cumulative_observed_count"], result["remaining_count"]),
                         ("NO_NEW_OUTPUT_TRANSITIONS", 4, 24))

    def test_research_design_is_required_as_selected_input(self):
        selection = json.loads(self.selected("research_selection").read_bytes())
        selection["records"] = [row for row in selection["records"] if row["kind"] != "experiment-design"]
        self.selected("research_selection").write_bytes(module.canonical(selection))
        with self.assertRaisesRegex(ValueError, "research_selection: changed bytes"):
            module.diagnose(self.root)

    def test_retroactive_engineering_output_field_refuses(self):
        events = json.loads(self.selected("engineering_events").read_bytes())
        events[0]["detail"]["actual_output_sha256"] = events[0]["detail"]["proposed_output_sha256"]
        self.selected("engineering_events").write_bytes(module.canonical(events))
        workflow = json.loads(self.selected("engineering_workflow").read_bytes())
        workflow["event_bindings"][0]["sha256"] = module.sha(module.canonical(events[0]))
        self.selected("engineering_workflow").write_bytes(module.canonical(workflow))
        with self.assertRaisesRegex(ValueError, "proposal-only"):
            module.diagnose(self.root, exact_phase=False)

    def test_research_design_event_cannot_claim_new_output(self):
        events = json.loads(self.selected("research_events").read_bytes())
        events[0]["detail"]["created_experiment_design"] = True
        self.selected("research_events").write_bytes(module.canonical(events))
        workflow = json.loads(self.selected("research_workflow").read_bytes())
        workflow["event_bindings"][0]["sha256"] = module.sha(module.canonical(events[0]))
        self.selected("research_workflow").write_bytes(module.canonical(workflow))
        with self.assertRaisesRegex(ValueError, "research first event output claim"):
            module.diagnose(self.root, exact_phase=False)

    def test_coherently_changed_selected_phase_refuses_cold_pin(self):
        events = json.loads(self.selected("engineering_events").read_bytes())
        events[0]["detail"]["proposed_output_sha256"] = "0" * 64
        self.selected("engineering_events").write_bytes(module.canonical(events))
        workflow = json.loads(self.selected("engineering_workflow").read_bytes())
        workflow["event_bindings"][0]["sha256"] = module.sha(module.canonical(events[0]))
        self.selected("engineering_workflow").write_bytes(module.canonical(workflow))
        with self.assertRaisesRegex(ValueError, "engineering_events: changed bytes"):
            module.diagnose(self.root)

    def test_changed_producer_refuses(self):
        with self.selected("engineering_source").open("ab") as file:
            file.write(b"\n")
        with self.assertRaisesRegex(ValueError, "engineering_source: changed bytes"):
            module.diagnose(self.root)

    def test_symlinked_ancestor_refuses(self):
        selected = self.selected("research_selection")
        parent = selected.parent
        sibling = parent.with_name("0007-external")
        parent.rename(sibling)
        parent.symlink_to(sibling, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlinked ancestor"):
            module.diagnose(self.root)


if __name__ == "__main__":
    unittest.main()
