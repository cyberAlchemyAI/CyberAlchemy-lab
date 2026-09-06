from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Final


@dataclass(frozen=True, slots=True)
class ComponentProtocol:
    protocol_id: str
    protocol_sha256: str


def _stable_hash(parts: tuple[str, ...]) -> int:
    digest = hashlib.sha256("\x00".join(parts).encode("utf8")).digest()
    value = int.from_bytes(digest[:8], byteorder="big", signed=True)
    return -2 if value == -1 else value


@dataclass(frozen=True, slots=True)
class ComponentInput:
    protocol_id: str
    protocol_sha256: str
    normalized_value_sha256: str


@dataclass(frozen=True, slots=True)
class SettlementAccountInput(ComponentInput):
    account_ref: str
    active: bool


@dataclass(frozen=True, slots=True)
class SettlementValueInput:
    currency: ComponentInput
    minor_units: ComponentInput
    settlement_account: SettlementAccountInput


@dataclass(frozen=True, slots=True)
class SettlementAccountValue:
    protocol_id: str
    protocol_sha256: str
    normalized_value_sha256: str
    account_ref: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SettlementAccountValue):
            return NotImplemented
        return (
            self.protocol_id,
            self.protocol_sha256,
            self.normalized_value_sha256,
        ) == (
            other.protocol_id,
            other.protocol_sha256,
            other.normalized_value_sha256,
        )

    def __hash__(self) -> int:
        return _stable_hash((
            self.protocol_id,
            self.protocol_sha256,
            self.normalized_value_sha256,
        ))


@dataclass(frozen=True, slots=True)
class ComponentBinding:
    component_name: str
    protocol_id: str
    protocol_sha256: str
    normalized_value_sha256: str
    nested_value_object: bool


@dataclass(frozen=True, slots=True)
class SettlementValue:
    currency_sha256: str
    minor_units_sha256: str
    settlement_account: SettlementAccountValue
    component_bindings: tuple[ComponentBinding, ComponentBinding, ComponentBinding]

    @property
    def normalized_tuple(self) -> tuple[str, str, str]:
        return (
            self.currency_sha256,
            self.minor_units_sha256,
            self.settlement_account.normalized_value_sha256,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SettlementValue):
            return NotImplemented
        return (
            self.currency_sha256 == other.currency_sha256
            and self.minor_units_sha256 == other.minor_units_sha256
            and self.settlement_account == other.settlement_account
        )

    def __hash__(self) -> int:
        return _stable_hash((
            self.currency_sha256,
            self.minor_units_sha256,
            self.settlement_account.protocol_id,
            self.settlement_account.protocol_sha256,
            self.settlement_account.normalized_value_sha256,
        ))


@dataclass(frozen=True, slots=True)
class ValidatorRef:
    validator_id: str
    validator_sha256: str
    origin: str


@dataclass(frozen=True, slots=True)
class FormationSuccess:
    ok: bool
    value: SettlementValue
    failure_codes: tuple[()]
    validator_trace: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ValidationFailure:
    ok: bool
    value: None
    failure_codes: tuple[str, ...]
    validator_trace: tuple[str, ...]


CURRENCY_PROTOCOL: Final = ComponentProtocol(
    "python.owned-value-component.currency-code/v1",
    "1" * 64,
)
MINOR_UNITS_PROTOCOL: Final = ComponentProtocol(
    "python.owned-value-component.minor-units/v1",
    "2" * 64,
)
SETTLEMENT_ACCOUNT_PROTOCOL: Final = ComponentProtocol(
    "python.owned-value-component.settlement-account/v1",
    "3" * 64,
)

BASE_VALIDATORS: Final = (
    ValidatorRef(
        "rule.settlement-value.currency-supported/v1",
        "4" * 64,
        "base",
    ),
    ValidatorRef(
        "rule.settlement-value.nonnegative-minor-units/v1",
        "5" * 64,
        "base",
    ),
)
ACCOUNT_ACTIVE_VALIDATOR: Final = ValidatorRef(
    "rule.settlement-value.account-active/v1",
    "6" * 64,
    "extension",
)


def _protocol_matches(observed: ComponentInput, expected: ComponentProtocol) -> bool:
    return (
        observed.protocol_id == expected.protocol_id
        and observed.protocol_sha256 == expected.protocol_sha256
    )


@dataclass(frozen=True, slots=True)
class SettlementValueFactory:
    mode: str = "base"

    @property
    def factory_ref(self) -> dict[str, str]:
        if self.mode == "base":
            return {
                "factory_id": "factory.settlement-value.base/v1",
                "factory_sha256": "a" * 64,
                "concept_id": "settlement.SettlementValue",
            }
        return {
            "factory_id": "factory.settlement-value.extended-validation/v1",
            "factory_sha256": "b" * 64,
            "concept_id": "settlement.SettlementValue",
        }

    @property
    def validators(self) -> tuple[ValidatorRef, ...]:
        if self.mode == "base":
            return BASE_VALIDATORS
        return (*BASE_VALIDATORS, ACCOUNT_ACTIVE_VALIDATOR)

    def extend_with_account_active(self) -> SettlementValueFactory | None:
        if self.mode != "base":
            return None
        return SettlementValueFactory("with-account-active")

    def create(
        self,
        input_data: SettlementValueInput,
    ) -> FormationSuccess | ValidationFailure:
        if not (
            _protocol_matches(input_data.currency, CURRENCY_PROTOCOL)
            and _protocol_matches(input_data.minor_units, MINOR_UNITS_PROTOCOL)
            and _protocol_matches(
                input_data.settlement_account,
                SETTLEMENT_ACCOUNT_PROTOCOL,
            )
        ):
            return ValidationFailure(
                False,
                None,
                ("COMPONENT_PROTOCOL_MISMATCH",),
                (),
            )
        trace: list[str] = []
        for validator in self.validators:
            trace.append(
                f"{validator.validator_id}@{validator.validator_sha256}",
            )
            if (
                validator.validator_id
                == "rule.settlement-value.nonnegative-minor-units/v1"
                and input_data.minor_units.normalized_value_sha256 == "f" * 64
            ):
                return ValidationFailure(
                    False,
                    None,
                    ("NEGATIVE_MINOR_UNITS",),
                    tuple(trace),
                )
            if (
                validator.validator_id
                == "rule.settlement-value.account-active/v1"
                and not input_data.settlement_account.active
            ):
                return ValidationFailure(
                    False,
                    None,
                    ("INACTIVE_SETTLEMENT_ACCOUNT",),
                    tuple(trace),
                )
        account = SettlementAccountValue(
            input_data.settlement_account.protocol_id,
            input_data.settlement_account.protocol_sha256,
            input_data.settlement_account.normalized_value_sha256,
            input_data.settlement_account.account_ref,
        )
        bindings = (
            ComponentBinding(
                "currency",
                input_data.currency.protocol_id,
                input_data.currency.protocol_sha256,
                input_data.currency.normalized_value_sha256,
                False,
            ),
            ComponentBinding(
                "minor_units",
                input_data.minor_units.protocol_id,
                input_data.minor_units.protocol_sha256,
                input_data.minor_units.normalized_value_sha256,
                False,
            ),
            ComponentBinding(
                "settlement_account",
                account.protocol_id,
                account.protocol_sha256,
                account.normalized_value_sha256,
                True,
            ),
        )
        return FormationSuccess(
            True,
            SettlementValue(
                input_data.currency.normalized_value_sha256,
                input_data.minor_units.normalized_value_sha256,
                account,
                bindings,
            ),
            (),
            tuple(trace),
        )


def create_settlement_value_factory() -> SettlementValueFactory:
    return SettlementValueFactory("base")


SETTLEMENT_VALUE_PROTOCOL: Final = {
    "protocol_id": "python.owned-value-object-factory/v1",
    "concept_id": "settlement.SettlementValue",
    "component_protocols": {
        "currency": CURRENCY_PROTOCOL,
        "minor_units": MINOR_UNITS_PROTOCOL,
        "settlement_account": SETTLEMENT_ACCOUNT_PROTOCOL,
    },
    "base_validator_count": 2,
    "extension_policy": "additive-validation-only",
    "equality_mode": "complete-normalized-tuple",
    "hash_mode": "same-normalized-complete-tuple",
    "immutability_mode": "formed-and-recursive-owned-components",
}
