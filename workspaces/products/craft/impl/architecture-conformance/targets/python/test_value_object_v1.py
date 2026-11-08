from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from remaining_types.value_object_v1 import (
    CURRENCY_PROTOCOL,
    MINOR_UNITS_PROTOCOL,
    SETTLEMENT_ACCOUNT_PROTOCOL,
    ComponentInput,
    SettlementAccountInput,
    SettlementValueInput,
    create_settlement_value_factory,
)


def digest(character: str) -> str:
    return character * 64


def value_input() -> SettlementValueInput:
    return SettlementValueInput(
        ComponentInput(
            CURRENCY_PROTOCOL.protocol_id,
            CURRENCY_PROTOCOL.protocol_sha256,
            digest("7"),
        ),
        ComponentInput(
            MINOR_UNITS_PROTOCOL.protocol_id,
            MINOR_UNITS_PROTOCOL.protocol_sha256,
            digest("8"),
        ),
        SettlementAccountInput(
            SETTLEMENT_ACCOUNT_PROTOCOL.protocol_id,
            SETTLEMENT_ACCOUNT_PROTOCOL.protocol_sha256,
            digest("9"),
            "account-001",
            True,
        ),
    )


class PythonValueObjectV1Test(unittest.TestCase):
    def test_complete_tuple_equality_hash_and_recursive_immutability(self) -> None:
        factory = create_settlement_value_factory().extend_with_account_active()
        self.assertIsNotNone(factory)
        assert factory is not None
        left = factory.create(value_input())
        right = factory.create(value_input())
        self.assertTrue(left.ok and right.ok)
        assert left.ok and right.ok
        self.assertIsNot(left.value, right.value)
        self.assertEqual(left.value, right.value)
        self.assertEqual(hash(left.value), hash(right.value))
        with self.assertRaises(FrozenInstanceError):
            left.value.currency_sha256 = digest("0")  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            left.value.settlement_account.account_ref = "changed"  # type: ignore[misc]

    def test_every_component_participates_and_invalid_forms_no_value(self) -> None:
        factory = create_settlement_value_factory().extend_with_account_active()
        assert factory is not None
        baseline = factory.create(value_input())
        assert baseline.ok
        for component, marker in (
            ("currency", "c"),
            ("minor_units", "d"),
            ("settlement_account", "e"),
        ):
            source = value_input()
            changed = SettlementValueInput(
                ComponentInput(
                    source.currency.protocol_id,
                    source.currency.protocol_sha256,
                    digest(marker) if component == "currency"
                    else source.currency.normalized_value_sha256,
                ),
                ComponentInput(
                    source.minor_units.protocol_id,
                    source.minor_units.protocol_sha256,
                    digest(marker) if component == "minor_units"
                    else source.minor_units.normalized_value_sha256,
                ),
                SettlementAccountInput(
                    source.settlement_account.protocol_id,
                    source.settlement_account.protocol_sha256,
                    digest(marker) if component == "settlement_account"
                    else source.settlement_account.normalized_value_sha256,
                    source.settlement_account.account_ref,
                    True,
                ),
            )
            observed = factory.create(changed)
            assert observed.ok
            self.assertNotEqual(baseline.value, observed.value)
        invalid = value_input()
        negative = SettlementValueInput(
            invalid.currency,
            ComponentInput(
                invalid.minor_units.protocol_id,
                invalid.minor_units.protocol_sha256,
                digest("f"),
            ),
            invalid.settlement_account,
        )
        failure = factory.create(negative)
        self.assertFalse(failure.ok)
        self.assertIsNone(failure.value)
        self.assertEqual(failure.failure_codes, ("NEGATIVE_MINOR_UNITS",))

    def test_protocol_admission_and_owner_bound_extension(self) -> None:
        base = create_settlement_value_factory()
        extended = base.extend_with_account_active()
        assert extended is not None
        self.assertEqual(extended.validators[: len(base.validators)], base.validators)
        self.assertIsNone(extended.extend_with_account_active())
        inactive = value_input()
        inactive = SettlementValueInput(
            inactive.currency,
            inactive.minor_units,
            SettlementAccountInput(
                inactive.settlement_account.protocol_id,
                inactive.settlement_account.protocol_sha256,
                inactive.settlement_account.normalized_value_sha256,
                inactive.settlement_account.account_ref,
                False,
            ),
        )
        self.assertTrue(base.create(inactive).ok)
        self.assertEqual(
            extended.create(inactive).failure_codes,
            ("INACTIVE_SETTLEMENT_ACCOUNT",),
        )
        stale = value_input()
        stale = SettlementValueInput(
            stale.currency,
            stale.minor_units,
            SettlementAccountInput(
                stale.settlement_account.protocol_id,
                digest("0"),
                stale.settlement_account.normalized_value_sha256,
                stale.settlement_account.account_ref,
                True,
            ),
        )
        self.assertEqual(
            base.create(stale).failure_codes,
            ("COMPONENT_PROTOCOL_MISMATCH",),
        )


if __name__ == "__main__":
    unittest.main()
