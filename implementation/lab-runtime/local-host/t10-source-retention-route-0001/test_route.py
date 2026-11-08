"""Focused O05 source-retention producer and O06 consumer refusals."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t10_source_retention", HERE / "route.py")
route = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route)


def sample():
    matrix = route.body(route.ROOT, route.MATRIX)
    rows = matrix["rows"][24:27]
    core_binding, manifest_binding, archive_binding = rows[2]["original_target_bindings"]
    o05_binding = next(b for b in rows[0]["original_evidence_bindings"] if b["path"] == route.O05)
    values = [route.body(route.ROOT, rows[0]["original_target_bindings"][0]),
              route.body(route.ROOT, rows[1]["original_target_bindings"][0]),
              route.body(route.ROOT, core_binding), route.body(route.ROOT, manifest_binding),
              route.sha(route.exact(route.ROOT, archive_binding)), route.body(route.ROOT, o05_binding)]
    return values, [core_binding, manifest_binding, archive_binding]


def link(values, bindings):
    return route.link_source(*values, *bindings)


class SourceRetention(unittest.TestCase):
    def test_01_exact_140_item_projection_and_archive(self):
        value = route.receipt()
        self.assertEqual(value["routes"]["members"], [24, 25, 26])
        self.assertEqual(value["routes"]["source_projection"]["disposition_counts"],
                         {"adapt": 88, "reference": 43, "block": 9})
        self.assertEqual(value["selected_governed_model_representations"], 0)
        self.assertFalse(value["T10_complete"])

    def test_02_changed_bytes_and_symlinked_parent_refuse(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "real").mkdir()
            (root / "real" / "core.json").write_bytes(b'{}')
            binding = {"path": "real/core.json", "sha256": hashlib.sha256(b'{}').hexdigest()}
            self.assertEqual(route.exact(root, binding), b'{}')
            (root / "real" / "core.json").write_bytes(b'{"changed":true}')
            with self.assertRaisesRegex(ValueError, "changed bytes"):
                route.exact(root, binding)
            (root / "alias").symlink_to(root / "real", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "unsafe path"):
                route.exact(root, {**binding, "path": "alias/core.json"})

    def test_03_changed_item_or_block_count_refuse(self):
        values, bindings = sample()
        changed = deepcopy(values)
        changed[0]["items"][0]["disposition"] = "block"
        with self.assertRaisesRegex(ValueError, "disposition projection differs"):
            link(changed, bindings)
        changed = deepcopy(values)
        changed[2]["dispositions"][0]["disposition"] = "block"
        changed[0]["items"] = deepcopy(changed[2]["dispositions"])
        with self.assertRaisesRegex(ValueError, "disposition projection differs"):
            link(changed, bindings)

    def test_04_missing_o05_producer_or_wrong_archive_refuse(self):
        values, bindings = sample()
        changed = deepcopy(values)
        changed[5]["files"] = [b for b in changed[5]["files"] if b != bindings[2]]
        with self.assertRaisesRegex(ValueError, "archive or producer receipt differs"):
            link(changed, bindings)
        changed = deepcopy(values)
        changed[4] = "0" * 64
        with self.assertRaisesRegex(ValueError, "archive or producer receipt differs"):
            link(changed, bindings)

    def test_05_private_export_or_source_admission_refuse(self):
        values, bindings = sample()
        changed = deepcopy(values)
        changed[1]["public_export"] = True
        with self.assertRaisesRegex(ValueError, "private-use or authority ceiling differs"):
            link(changed, bindings)
        changed = deepcopy(values)
        changed[1]["source_owner_and_access_authority_verified"] = True
        with self.assertRaisesRegex(ValueError, "private-use or authority ceiling differs"):
            link(changed, bindings)

    def test_06_source_selection_and_retirement_refuse(self):
        values, bindings = sample()
        changed = deepcopy(values)
        changed[0]["source_selection_binding"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "disposition projection differs"):
            link(changed, bindings)
        changed = deepcopy(values)
        changed[0]["source_retirements"] = 1
        with self.assertRaisesRegex(ValueError, "private-use or authority ceiling differs"):
            link(changed, bindings)


if __name__ == "__main__":
    unittest.main()
