from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

import remaining_types.entity_v1 as entity_module
from remaining_types.entity_v1 import (
    SETTLEMENT_ENTITY_PROTOCOL,
    SettlementEntityInput,
    SettlementEntitySnapshot,
    create_settlement_entity_factory,
)


def digest(character: str) -> str:
    return character * 64


def entity_input(
    *,
    snapshot_id: str = "snapshot.settlement-a.created",
    entity_case_id: str = "settlement-a",
    settlement_id: str = "7",
    amount_minor: int = 100,
    duplicate_exists: bool = False,
    state: str = "8",
) -> SettlementEntityInput:
    return SettlementEntityInput(
        snapshot_id,
        entity_case_id,
        0,
        None,
        digest("6"),
        digest(settlement_id),
        digest("6"),
        amount_minor,
        duplicate_exists,
        digest(state),
    )


class PythonEntityV1Test(unittest.TestCase):
    def test_identity_only_equality_hash_and_frozen_snapshots(self) -> None:
        factory = create_settlement_entity_factory().extend_with_duplicate_blocked()
        assert factory is not None
        created = factory.create(entity_input())
        self.assertTrue(created.ok)
        assert created.ok
        completed = factory.transition(
            created.value,
            snapshot_id="snapshot.settlement-a.completed",
            state_sha256=digest("9"),
            amount_minor=100,
        )
        self.assertTrue(completed.ok)
        assert completed.ok
        self.assertIsNot(created.value, completed.value)
        self.assertEqual(created.value, completed.value)
        self.assertEqual(hash(created.value), hash(completed.value))
        self.assertEqual(created.value.identity, completed.value.identity)
        self.assertNotEqual(created.value.state_sha256, completed.value.state_sha256)
        with self.assertRaises(FrozenInstanceError):
            completed.value.state_sha256 = digest("0")  # type: ignore[misc]
        distinct = factory.create(entity_input(
            snapshot_id="snapshot.settlement-b.created",
            entity_case_id="settlement-b",
            settlement_id="c",
        ))
        assert distinct.ok
        self.assertNotEqual(created.value, distinct.value)

    def test_all_routes_converge_and_direct_constructor_is_inaccessible(self) -> None:
        factory = create_settlement_entity_factory().extend_with_duplicate_blocked()
        assert factory is not None
        created = factory.create(entity_input())
        reconstructed = factory.reconstruct(entity_input(
            snapshot_id="snapshot.settlement-a.reconstructed",
        ))
        assert created.ok and reconstructed.ok
        self.assertEqual(created.trace.validator_trace, reconstructed.trace.validator_trace)
        self.assertEqual(created.value.identity, reconstructed.value.identity)
        self.assertEqual(factory.direct_constructor, None)
        with self.assertRaisesRegex(
            TypeError,
            "SETTLEMENT_ENTITY_DIRECT_CONSTRUCTOR_INACCESSIBLE",
        ):
            SettlementEntitySnapshot(
                object(),
                "bypass",
                "settlement-a",
                0,
                "language-visible-direct-constructor",
                None,
                created.value.identity,
                digest("8"),
            )
        self.assertFalse(hasattr(entity_module, "_construct_snapshot"))
        self.assertFalse(hasattr(entity_module, "_define_snapshot_type"))
        for route_id in ("language-visible-direct-constructor", "undeclared-route"):
            with self.assertRaisesRegex(
                ValueError,
                "SETTLEMENT_ENTITY_CONSTRUCTION_ROUTE_UNSUPPORTED",
            ):
                factory._execute(route_id, entity_input())

    def test_validator_order_structured_failure_and_additive_extension(self) -> None:
        base = create_settlement_entity_factory()
        extended = base.extend_with_duplicate_blocked()
        assert extended is not None
        self.assertEqual(extended.validators[:len(base.validators)], base.validators)
        self.assertEqual(extended.identity_resolver_ref, base.identity_resolver_ref)
        self.assertIsNone(extended.extend_with_duplicate_blocked())
        duplicate = entity_input(duplicate_exists=True)
        self.assertTrue(base.create(duplicate).ok)
        failure = extended.create(duplicate)
        self.assertFalse(failure.ok)
        self.assertIsNone(failure.value)
        self.assertEqual(failure.failure_codes, ("DUPLICATE_SETTLEMENT",))
        self.assertEqual(
            tuple(item.origin for item in failure.validator_trace),
            ("base", "base", "extension"),
        )
        invalid = extended.create(entity_input(amount_minor=0))
        self.assertFalse(invalid.ok)
        self.assertIsNone(invalid.value)
        self.assertEqual(invalid.failure_codes, ("AMOUNT_INVALID",))
        self.assertIsNone(invalid.identity_resolution_ordinal)
        self.assertIsNone(invalid.construction_ordinal)

    def test_protocol_is_exact_and_no_per_call_validator_surface_exists(self) -> None:
        factory = create_settlement_entity_factory()
        self.assertEqual(
            SETTLEMENT_ENTITY_PROTOCOL.protocol_id,
            "python.validated-extensible-entity-factory/v1",
        )
        self.assertEqual(
            SETTLEMENT_ENTITY_PROTOCOL.identity_components,
            ("organization_id", "settlement_id"),
        )
        self.assertEqual(
            SETTLEMENT_ENTITY_PROTOCOL.equality_mode,
            "canonical-identity-only",
        )
        self.assertEqual(
            SETTLEMENT_ENTITY_PROTOCOL.construction_routes,
            (
                "factory",
                "deserialization-reconstruction",
                "lifecycle-transition",
                "language-visible-direct-constructor",
            ),
        )
        with self.assertRaises(TypeError):
            factory.create(entity_input(), validator=lambda _: True)  # type: ignore[call-arg]


if __name__ == "__main__":
    unittest.main()
