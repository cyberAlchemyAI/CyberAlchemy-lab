import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t11_w06_native_run", HERE / "run.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class W06SixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.routes, cls.previous, cls.router = module.preflight()

    def test_six_exact_scope_members_and_runtime_closure(self):
        self.assertEqual(len(self.routes), 6)
        self.assertEqual(len(self.manifest["files"]), 45)
        self.assertEqual(len({r["member_ref"] for r in self.routes}), 6)
        self.assertEqual({r["body_scope_ref"] for r in self.routes}, {module.SCOPE})

    def test_all_six_delivered_to_real_callback(self):
        now = datetime.now(timezone.utc)
        signer = Ed25519PrivateKey.generate()
        consumer = self.router.ScopedConsumer(module.ROOT, module.MATRIX,
                                              signer.public_key(), clock=lambda: now)
        for route in self.routes:
            with self.subTest(member=route["member_ref"]):
                raw = module.selected_body(self.manifest, consumer, self.router, signer, route, now)
                self.assertEqual(module.sha(raw), route["body_binding"]["sha256"])

    def test_valid_other_scope_member_has_no_native_consumer(self):
        now = datetime.now(timezone.utc)
        signer = Ed25519PrivateKey.generate()
        consumer = self.router.ScopedConsumer(module.ROOT, module.MATRIX,
                                              signer.public_key(), clock=lambda: now)
        route = next(r for r in consumer.matrix["routes"] if r["body_scope_ref"] != module.SCOPE)
        with self.assertRaisesRegex(module.NativeRouteRefusal, "no exact W06 native consumer"):
            module.selected_body(self.manifest, consumer, self.router, signer, route, now)

    def test_wrong_scope_and_missing_consumer_refuse(self):
        now = datetime.now(timezone.utc)
        signer = Ed25519PrivateKey.generate()
        consumer = self.router.ScopedConsumer(module.ROOT, module.MATRIX,
                                              signer.public_key(), clock=lambda: now)
        route = self.routes[0]
        packet = module.grant(self.router, signer, route, now)
        with self.assertRaisesRegex(self.router.RouteRefusal, "selected scope"):
            consumer.consume(route["member_ref"], "scope:other", packet, lambda *_: None)
        with self.assertRaisesRegex(self.router.RouteRefusal, "consumer missing"):
            consumer.consume(route["member_ref"], module.SCOPE, packet, None)

    def test_expired_signed_grant_refuses_at_real_clock(self):
        signer = Ed25519PrivateKey.generate()
        consumer = self.router.ScopedConsumer(module.ROOT, module.MATRIX,
                                              signer.public_key())
        route = self.routes[0]
        expired = module.grant(self.router, signer, route,
                               datetime.now(timezone.utc) - timedelta(minutes=10))
        with self.assertRaisesRegex(self.router.RouteRefusal, "lease"):
            consumer.consume(route["member_ref"], module.SCOPE, expired, lambda *_: None)

if __name__ == "__main__":
    unittest.main()
