from datetime import datetime, timezone
import importlib
import importlib.util
from pathlib import Path
import sys
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t11_all_scopes_run", HERE / "run.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AllScopesColdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.routes, cls.previous, cls.router = module.preflight()

    def test_exact_230_member_native_table_matches_selected_matrix(self):
        sys.path.insert(0, str(module.RUNTIME))
        operations = importlib.import_module("lab_runtime.operations")
        expected = {}
        for route in self.routes:
            expected.setdefault(route["body_scope_ref"], {})[route["version_ref"]] = {
                "carrier": route["carrier_ref"], "sha256": route["body_binding"]["sha256"]}
        self.assertEqual({scope: {version: row for batch in batches for version, row in batch.items()}
                          for scope, batches in operations.T11_BATCHES.items()}, expected)
        self.assertEqual({s: len(v) for s, v in expected.items()},
                         {s: v["members"] for s, v in self.manifest["selected_scopes"].items()})
        self.assertEqual(operations.T11_STORE_IDS,
                         {s: v["store_id"] for s, v in self.manifest["selected_scopes"].items()})
        self.assertEqual([len(batch) for batch in operations.T11_BATCHES[module.LEGACY]],
                         [64, 64, 64, 28])

    def test_230_signed_exact_original_body_deliveries(self):
        bodies, negatives = module.route_bodies(self.manifest, self.routes, self.router)
        self.assertEqual(len(bodies), 230)
        self.assertEqual({r["version_ref"]: r["body_binding"]["sha256"] for r in self.routes},
                         {v: module.sha(raw) for v, raw in bodies.items()})
        self.assertEqual([n["case"] for n in negatives],
                         ["cross-scope", "missing-consumer", "missing-native-route", "expired-grant"])

    def test_changed_route_refuses_before_callback(self):
        now = datetime.now(timezone.utc)
        signer = Ed25519PrivateKey.generate()
        consumer = self.router.ScopedConsumer(module.ROOT, module.MATRIX,
                                              signer.public_key(), clock=lambda: now)
        expected = {r["member_ref"]: r for r in self.routes}
        changed = {**self.routes[0], "body_scope_ref": "scope:other"}
        with self.assertRaisesRegex(module.NativeRouteRefusal, "no exact native consumer"):
            module.deliver(consumer, self.router, signer, changed, now, expected)

    def test_legacy_intermediate_references_are_partial_then_close(self):
        bodies, _ = module.route_bodies(self.manifest, self.routes, self.router)
        group = [r for r in self.routes if r["body_scope_ref"] == module.LEGACY]
        self.assertEqual(len(group), 220)
        first = module.unresolved_selected_refs(group, group[:64], bodies)
        self.assertGreater(first, 0)
        self.assertEqual(module.unresolved_selected_refs(group, group, bodies), 0)


if __name__ == "__main__":
    unittest.main()
