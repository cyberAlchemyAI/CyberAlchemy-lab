"""Cold provenance and non-mutation checks for the API40 T17 inventory."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import build_inventory as inventory


class Inventory(unittest.TestCase):
    def test_01_frozen_inputs_and_exact_34(self):
        inventory.verify_expected()
        value = inventory.build()
        self.assertEqual(value["operation_count"], 34)
        self.assertEqual(len({row["operation"] for row in value["operations"]}), 34)

    def test_02_changed_input_refuses_without_writing(self):
        selected = inventory.API / "source-manifest.json"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            changed = root / selected
            changed.parent.mkdir(parents=True)
            changed.write_bytes((inventory.ROOT / selected).read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "frozen T17 input differs"):
                inventory.verify_expected({selected: inventory.EXPECTED_BINDINGS[selected]}, root)
        self.assertEqual(inventory.EXPECTED_BINDINGS[selected],
                         hashlib.sha256((inventory.ROOT / selected).read_bytes()).hexdigest())

    def test_03_existing_inventory_comparison_is_read_only(self):
        data = inventory.encoded(inventory.build())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inventory.json"
            path.write_bytes(data)
            inventory.verify_inventory(path, data)
            changed = data.replace(b'"operation_count": 34', b'"operation_count": 33')
            path.write_bytes(changed)
            with self.assertRaisesRegex(ValueError, "retained T17 inventory differs"):
                inventory.verify_inventory(path, data)
            self.assertEqual(path.read_bytes(), changed)

    def test_04_overwrite_and_unversioned_output_refused(self):
        data = inventory.encoded(inventory.build())
        old = inventory.HERE / "INVENTORY-0001.json"
        original = old.read_bytes()
        with self.assertRaises(FileExistsError):
            inventory.write_new(old, data)
        self.assertEqual(old.read_bytes(), original)
        with tempfile.TemporaryDirectory(dir=inventory.HERE) as directory:
            outside = Path(directory) / "INVENTORY-9999.json"
            with self.assertRaisesRegex(ValueError, "new versioned inventory"):
                inventory.write_new(outside, data)

    def test_05_identical_bytes_behind_linked_ancestor_refused(self):
        selected = inventory.API / "source-manifest.json"
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "root"
            real = base / "real" / selected.relative_to("product")
            real.parent.mkdir(parents=True)
            real.write_bytes((inventory.ROOT / selected).read_bytes())
            root.mkdir()
            (root / "product").symlink_to(base / "real", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "linked or nonregular T17 input"):
                inventory.verify_expected({selected: inventory.EXPECTED_BINDINGS[selected]}, root)


if __name__ == "__main__":
    unittest.main()
