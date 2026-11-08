"""Focused retained native representation and confidence-route checks."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t10_representation_native", HERE / "route.py")
route = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route)


def sample():
    matrix = route.body(route.ROOT, route.MATRIX)
    rows = [matrix["rows"][i] for i in (16, 17, 19, 20)]
    profile_binding = rows[0]["original_target_bindings"][0]
    translation_binding = next(b for b in rows[2]["original_target_bindings"]
                               if b["path"].endswith("/profiles/translation-profile.json"))
    o02_binding = next(b for b in rows[0]["original_evidence_bindings"] if b["path"] == route.O02)
    o02 = route.body(route.ROOT, o02_binding)
    episode_binding = o02["rich_lifecycle_episode"]
    witness_binding = next(b for b in o02["files"] if b["path"] == route.EPISODE + "mapping-witnesses.json")
    view_binding = next(b for b in o02["files"] if b["path"] == route.EPISODE + "initial-native-view.json")
    values = [o02, route.body(route.ROOT, profile_binding), route.body(route.ROOT, translation_binding),
              route.body(route.ROOT, rows[3]["original_target_bindings"][0]),
              route.body(route.ROOT, episode_binding), route.body(route.ROOT, witness_binding),
              route.body(route.ROOT, view_binding)]
    bindings = [profile_binding, translation_binding, episode_binding, witness_binding, view_binding]
    return values, bindings


def link(values, bindings):
    return route.link_native(*values, *bindings)


class RepresentationNative(unittest.TestCase):
    def test_01_exact_four_member_route(self):
        value = route.receipt()
        self.assertEqual(value["routes"]["members"], [16, 17, 19, 20])
        self.assertEqual(value["routes"]["observed"]["rich_nodes"], 3)
        self.assertEqual(value["routes"]["observed"]["typed_relations"], 1)
        self.assertEqual(value["routes"]["observed"]["confidence_level"], "not-assessed")
        self.assertEqual(value["selected_governed_model_representations"], 0)
        self.assertFalse(value["T10_complete"])

    def test_02_changed_bytes_and_symlinked_parent_refuse(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "real").mkdir()
            (root / "real" / "profile.json").write_bytes(b'{}')
            binding = {"path": "real/profile.json", "sha256": hashlib.sha256(b'{}').hexdigest()}
            self.assertEqual(route.exact(root, binding), b'{}')
            (root / "real" / "profile.json").write_bytes(b'{"changed":true}')
            with self.assertRaisesRegex(ValueError, "changed bytes"):
                route.exact(root, binding)
            (root / "alias").symlink_to(root / "real", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "unsafe path"):
                route.exact(root, {**binding, "path": "alias/profile.json"})

    def test_03_missing_o02_source_row_or_wrong_witness_refuse(self):
        values, bindings = sample()
        changed = deepcopy(values)
        changed[0]["files"] = [b for b in changed[0]["files"] if b != bindings[1]]
        with self.assertRaisesRegex(ValueError, "source/output bindings differ"):
            link(changed, bindings)
        changed = deepcopy(values)
        changed[5]["profile_binding"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source/output bindings differ"):
            link(changed, bindings)

    def test_04_changed_native_count_or_checkpoint_refuse(self):
        values, bindings = sample()
        changed = deepcopy(values)
        changed[4]["rich_nodes"] = 2
        with self.assertRaisesRegex(ValueError, "lifecycle result differs"):
            link(changed, bindings)
        changed = deepcopy(values)
        changed[6]["checkpoint_parity"] = "FAIL"
        with self.assertRaisesRegex(ValueError, "lifecycle result differs"):
            link(changed, bindings)

    def test_05_confidence_and_admission_refuse(self):
        values, bindings = sample()
        changed = deepcopy(values)
        changed[3]["evidence_level"] = "supported"
        with self.assertRaisesRegex(ValueError, "confidence projection differs"):
            link(changed, bindings)
        changed = deepcopy(values)
        changed[6]["governed_nodes"][0]["governance_state"]["candidate_or_maturity_status"] = "admitted"
        with self.assertRaisesRegex(ValueError, "admission posture differs"):
            link(changed, bindings)

    def test_06_wrong_native_kind_or_global_edge_refuse(self):
        values, bindings = sample()
        changed = deepcopy(values)
        changed[6]["governed_nodes"][0]["identity"]["type_ref"] = "wrong"
        with self.assertRaisesRegex(ValueError, "type, or admission posture differs"):
            link(changed, bindings)
        changed = deepcopy(values)
        changed[5]["relation"]["confirmed_global_edge_eligible"] = True
        with self.assertRaisesRegex(ValueError, "native relation source or event differs"):
            link(changed, bindings)

    def test_07_wrong_node_witness_or_source_digest_refuse(self):
        values, bindings = sample()
        changed = deepcopy(values)
        changed[5]["capability"]["rich_record"]["node_id"] = changed[5]["work"]["rich_record"]["node_id"]
        with self.assertRaisesRegex(ValueError, "native witness represented source differs"):
            link(changed, bindings)
        changed = deepcopy(values)
        changed[5]["implementation"]["source_view"]["carrier"]["source_binding"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "native witness source or node identity differs"):
            link(changed, bindings)

    def test_08_relation_event_digest_and_endpoint_join_refuse(self):
        values, bindings = sample()
        changed = deepcopy(values)
        changed[5]["relation"]["native_semantic_ref"]["semantic_event_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "native relation event/source/endpoint join differs"):
            link(changed, bindings)
        changed = deepcopy(values)
        changed[6]["semantic_events"][3]["complete_resulting_semantic_state"]["source_node_id"] = "other"
        with self.assertRaisesRegex(ValueError, "native relation event/source/endpoint join differs"):
            link(changed, bindings)
        changed = deepcopy(values)
        changed[5]["relation"]["source_typed_relation"]["record"]["payload"]["target"]["version_ref"] = "other"
        with self.assertRaisesRegex(ValueError, "native relation event/source/endpoint join differs"):
            link(changed, bindings)


if __name__ == "__main__":
    unittest.main()
