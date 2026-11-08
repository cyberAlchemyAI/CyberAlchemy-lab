import copy
import hashlib
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).parent))
from router import RouteRefusal, ScopedConsumer, canonical, sha


ROOT = Path(__file__).resolve().parents[4]
MATRIX = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T11/scope-routing-matrix-0002.json",
          "sha256": "f74f5c6a85e7eacb420785165fcb8257f2120337b31e482bf6bfb65125575628"}
NOW = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)


class ScopedConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = Ed25519PrivateKey.generate()
        cls.router = ScopedConsumer(ROOT, MATRIX, cls.key.public_key(), clock=lambda: NOW)

    def packet(self, route, **changes):
        grant = {"schema": "lab-local-scoped-body-grant/v1", "actor": "fixture:local-operator",
                 "member_ref": route["member_ref"], "scope_ref": route["body_scope_ref"],
                 "body_sha256": route["body_binding"]["sha256"], "operation": route["operation"],
                 "not_before": (NOW - timedelta(minutes=1)).isoformat(),
                 "expires_at": (NOW + timedelta(minutes=1)).isoformat()}
        grant.update(changes)
        return {"grant": grant, "signature": self.key.sign(canonical(grant)).hex()}

    def consume(self, route, packet=None, **kwargs):
        return self.router.consume(route["member_ref"], route["body_scope_ref"],
                                   packet or self.packet(route), lambda body, _: (sha(body), len(body)), **kwargs)

    def test_all_230_exact_full_body_routes(self):
        seen = set()
        for route in self.router.routes.values():
            digest, size = self.consume(route)
            self.assertEqual(digest, route["body_binding"]["sha256"])
            self.assertGreater(size, 0)
            seen.add(route["member_ref"])
        self.assertEqual(len(seen), 230)

    def test_cross_scope_refuses_before_consumer(self):
        route = next(iter(self.router.routes.values()))
        calls = []
        with self.assertRaises(RouteRefusal):
            self.router.consume(route["member_ref"], "scope:wrong", self.packet(route),
                                lambda body, row: calls.append(body))
        self.assertEqual(calls, [])

    def test_missing_consumer_refuses(self):
        route = next(iter(self.router.routes.values()))
        with self.assertRaises(RouteRefusal):
            self.router.consume(route["member_ref"], route["body_scope_ref"], self.packet(route), None)

    def test_wrong_member_refuses(self):
        route = next(iter(self.router.routes.values()))
        with self.assertRaises(RouteRefusal):
            self.router.consume("unknown", route["body_scope_ref"], self.packet(route), lambda *_: None)

    def test_changed_grant_refuses(self):
        route = next(iter(self.router.routes.values()))
        packet = self.packet(route)
        packet["grant"]["actor"] = "attacker"
        with self.assertRaises(RouteRefusal):
            self.consume(route, packet)

    def test_other_signer_refuses(self):
        route = next(iter(self.router.routes.values()))
        packet = self.packet(route)
        packet["signature"] = Ed25519PrivateKey.generate().sign(canonical(packet["grant"])).hex()
        with self.assertRaises(RouteRefusal):
            self.consume(route, packet)

    def test_expired_and_future_grants_refuse(self):
        route = next(iter(self.router.routes.values()))
        for changes in ({"expires_at": (NOW - timedelta(seconds=1)).isoformat()},
                        {"not_before": (NOW + timedelta(seconds=1)).isoformat()}):
            with self.subTest(changes=changes), self.assertRaises(RouteRefusal):
                self.consume(route, self.packet(route, **changes))

    def test_real_clock_does_not_accept_old_fixture_grant(self):
        route = next(iter(self.router.routes.values()))
        live = ScopedConsumer(ROOT, MATRIX, self.key.public_key())
        with self.assertRaises(RouteRefusal):
            live.consume(route["member_ref"], route["body_scope_ref"], self.packet(route), lambda *_: None)

    def test_changed_selected_body_refuses(self):
        route = next(iter(self.router.routes.values()))
        changed = copy.deepcopy(route)
        changed["body_binding"]["sha256"] = "0" * 64
        self.router._routes[route["member_ref"]] = changed
        try:
            with self.assertRaises(RouteRefusal):
                self.consume(changed)
        finally:
            self.router._routes[route["member_ref"]] = route

    def test_changed_selected_schema_refuses(self):
        route = next(iter(self.router.routes.values()))
        changed = copy.deepcopy(route)
        changed["schema_binding"]["sha256"] = "0" * 64
        self.router._routes[route["member_ref"]] = changed
        try:
            with self.assertRaises(RouteRefusal):
                self.consume(changed)
        finally:
            self.router._routes[route["member_ref"]] = route

    def test_callback_cannot_mutate_selected_route(self):
        route = next(iter(self.router.routes.values()))
        def consumer(body, row):
            row["operation"] = "revise"
            row["body_binding"]["sha256"] = "0" * 64
            return sha(body)
        first = self.router.consume(route["member_ref"], route["body_scope_ref"], self.packet(route), consumer)
        second, _ = self.consume(route)
        self.assertEqual(first, route["body_binding"]["sha256"])
        self.assertEqual(second, first)

    def test_inspection_snapshot_cannot_mutate_selected_route(self):
        route = next(iter(self.router.routes.values()))
        self.router.routes[route["member_ref"]]["operation"] = "revise"
        self.assertEqual(self.consume(route)[0], route["body_binding"]["sha256"])

    def test_changed_matrix_pin_refuses(self):
        changed = dict(MATRIX, sha256="0" * 64)
        with self.assertRaises(RouteRefusal):
            ScopedConsumer(ROOT, changed, self.key.public_key())


if __name__ == "__main__":
    unittest.main()
