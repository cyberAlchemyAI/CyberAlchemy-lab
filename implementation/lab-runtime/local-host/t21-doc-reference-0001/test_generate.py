"""Causal checks for the exact public operation-reference generator."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE = Path(__file__).with_name("generate.py")
SPEC = importlib.util.spec_from_file_location("t21_reference_generator", MODULE)
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


class Reference(unittest.TestCase):
    def test_all_34_pages_and_bound_schemas(self):
        generated = G.build()
        self.assertEqual(len(generated), 35)
        self.assertIn(b"Current runtime qualification: **pending**", generated["action-dispatch.md"])
        self.assertIn(b"| Pending |", generated["README.md"])
        G.verify()

    def test_changed_catalog_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / G.CATALOG
            path.parent.mkdir(parents=True)
            path.write_bytes((G.ROOT / G.CATALOG).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "changed reference file"):
                G.build(root)

    def test_changed_bound_schema_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = json.loads((G.ROOT / G.CATALOG).read_bytes())
            paths = {G.CATALOG}
            for operation in catalog["operations"]:
                paths.update(operation[key]["ref"] for key in G.SCHEMA_KEYS)
            for name in paths:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((G.ROOT / name).read_bytes())
            target = root / catalog["operations"][0]["request_schema"]["ref"]
            target.write_bytes(target.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "changed reference file"):
                G.build(root)

    def test_schema_resource_uri_mismatch_refuses(self):
        catalog = json.loads((G.ROOT / G.CATALOG).read_bytes())
        binding = dict(catalog["operations"][0]["request_schema"])
        binding["resource_uri"] = "urn:synthetic:wrong"
        with self.assertRaisesRegex(ValueError, "schema resource URI differs"):
            G.schema_line(G.ROOT, Path(G.DESTINATION), "Request", binding)

    def test_generated_page_mutation_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = json.loads((G.ROOT / G.CATALOG).read_bytes())
            paths = {G.CATALOG}
            for operation in catalog["operations"]:
                paths.update(operation[key]["ref"] for key in G.SCHEMA_KEYS)
            for name in paths:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((G.ROOT / name).read_bytes())
            destination = root / G.DESTINATION
            destination.mkdir(parents=True)
            for name, raw in G.build(root).items():
                (destination / name).write_bytes(raw)
            G.verify(root)
            (destination / "action-dispatch.md").write_bytes(
                (destination / "action-dispatch.md").read_bytes() + b"changed")
            with self.assertRaisesRegex(ValueError, "generated operation page changed"):
                G.verify(root)

    def test_symlink_page_refuses_verify_and_write_without_touching_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = json.loads((G.ROOT / G.CATALOG).read_bytes())
            paths = {G.CATALOG}
            for operation in catalog["operations"]:
                paths.update(operation[key]["ref"] for key in G.SCHEMA_KEYS)
            for name in paths:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((G.ROOT / name).read_bytes())
            destination = root / G.DESTINATION
            destination.mkdir(parents=True)
            for name, raw in G.build(root).items():
                (destination / name).write_bytes(raw)
            target = destination / "action-dispatch.md"
            outside = root / "outside.md"
            outside.write_bytes(target.read_bytes())
            target.unlink()
            target.symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "unsafe generated operation page"):
                G.verify(root)
            with self.assertRaisesRegex(ValueError, "unsafe generated operation page"):
                G.write(root)
            self.assertEqual(outside.read_bytes(), G.build(root)[target.name])


if __name__ == "__main__":
    unittest.main()
