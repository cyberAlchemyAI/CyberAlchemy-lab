from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Callable, Final


def _stable_hash(parts: tuple[str, ...]) -> int:
    digest = hashlib.sha256("\x00".join(parts).encode("utf8")).digest()
    value = int.from_bytes(digest[:8], byteorder="big", signed=True)
    return -2 if value == -1 else value


@dataclass(frozen=True, slots=True)
class IdentityComponent:
    component_name: str
    type_id: str
    type_sha256: str
    normalized_value_sha256: str


@dataclass(frozen=True, slots=True)
class SettlementIdentity:
    organization_id: IdentityComponent
    settlement_id: IdentityComponent

    @property
    def canonical_tuple(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.organization_id.type_id,
            self.organization_id.type_sha256,
            self.organization_id.normalized_value_sha256,
            self.settlement_id.type_id,
            self.settlement_id.type_sha256,
            self.settlement_id.normalized_value_sha256,
        )


def _define_snapshot_type() -> tuple[
    type[SettlementEntitySnapshot],
    Callable[..., SettlementEntitySnapshot],
    object,
]:
    construction_token = object()

    def require_construction_authority(observed: object) -> None:
        if observed is not construction_token:
            raise TypeError("SETTLEMENT_ENTITY_DIRECT_CONSTRUCTOR_INACCESSIBLE")

    @dataclass(frozen=True, slots=True, eq=False, init=False)
    class SettlementEntitySnapshot:
        snapshot_id: str
        entity_case_id: str
        sequence: int
        route_id: str
        predecessor_snapshot_id: str | None
        identity: SettlementIdentity
        state_sha256: str

        def __init__(
            self,
            _construction_token: object,
            snapshot_id: str,
            entity_case_id: str,
            sequence: int,
            route_id: str,
            predecessor_snapshot_id: str | None,
            identity: SettlementIdentity,
            state_sha256: str,
        ) -> None:
            require_construction_authority(_construction_token)
            object.__setattr__(self, "snapshot_id", snapshot_id)
            object.__setattr__(self, "entity_case_id", entity_case_id)
            object.__setattr__(self, "sequence", sequence)
            object.__setattr__(self, "route_id", route_id)
            object.__setattr__(self, "predecessor_snapshot_id", predecessor_snapshot_id)
            object.__setattr__(self, "identity", identity)
            object.__setattr__(self, "state_sha256", state_sha256)

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, SettlementEntitySnapshot):
                return NotImplemented
            return self.identity == other.identity

        def __hash__(self) -> int:
            return _stable_hash(self.identity.canonical_tuple)

    def construct(
        _construction_authority: object,
        **fields: object,
    ) -> SettlementEntitySnapshot:
        require_construction_authority(_construction_authority)
        return SettlementEntitySnapshot(construction_token, **fields)

    return SettlementEntitySnapshot, construct, construction_token


(
    SettlementEntitySnapshot,
    _construct_snapshot,
    _factory_construction_authority,
) = _define_snapshot_type()
del _define_snapshot_type


@dataclass(frozen=True, slots=True)
class ValidatorRef:
    validator_id: str
    validator_sha256: str
    origin: str


@dataclass(frozen=True, slots=True)
class ValidatorExecution:
    validator_id: str
    validator_sha256: str
    origin: str
    ordinal: int
    outcome: str


@dataclass(frozen=True, slots=True)
class FactoryRef:
    factory_id: str
    factory_sha256: str
    concept_id: str


@dataclass(frozen=True, slots=True)
class IdentityResolverRef:
    resolver_id: str
    resolver_sha256: str


@dataclass(frozen=True, slots=True)
class SettlementEntityInput:
    snapshot_id: str
    entity_case_id: str
    sequence: int
    predecessor_snapshot_id: str | None
    organization_id_sha256: str
    settlement_id_sha256: str
    owner_organization_id_sha256: str
    amount_minor: int
    duplicate_exists: bool
    state_sha256: str


@dataclass(frozen=True, slots=True)
class ConstructionTrace:
    route_id: str
    normalization_ordinal: int
    validator_trace: tuple[ValidatorExecution, ...]
    identity_resolution_ordinal: int
    construction_ordinal: int
    immutability_ordinal: int


@dataclass(frozen=True, slots=True)
class SettlementEntitySuccess:
    ok: bool
    value: SettlementEntitySnapshot
    failure_codes: tuple[()]
    trace: ConstructionTrace


@dataclass(frozen=True, slots=True)
class SettlementEntityFailure:
    ok: bool
    value: None
    failure_codes: tuple[str, ...]
    route_id: str
    validator_trace: tuple[ValidatorExecution, ...]
    identity_resolution_ordinal: None
    construction_ordinal: None


ORGANIZATION_ID_TYPE: Final = IdentityComponent(
    "organization_id",
    "identity.organization-id/v1",
    "1" * 64,
    "0" * 64,
)
SETTLEMENT_ID_TYPE: Final = IdentityComponent(
    "settlement_id",
    "identity.settlement-id/v1",
    "2" * 64,
    "0" * 64,
)
BASE_FACTORY_REF: Final = FactoryRef(
    "factory.settlement-entity.base/v1",
    "a" * 64,
    "settlement.Settlement",
)
EXTENSION_FACTORY_REF: Final = FactoryRef(
    "factory.settlement-entity.extended/v1",
    "b" * 64,
    "settlement.Settlement",
)
IDENTITY_RESOLVER_REF: Final = IdentityResolverRef(
    "resolver.settlement-entity.composite-identity/v1",
    "d" * 64,
)
BASE_VALIDATORS: Final = (
    ValidatorRef(
        "rule.settlement.owner-matches/v1",
        "3" * 64,
        "base",
    ),
    ValidatorRef(
        "rule.settlement.amount-valid/v1",
        "4" * 64,
        "base",
    ),
)
DUPLICATE_BLOCKED_VALIDATOR: Final = ValidatorRef(
    "rule.settlement.duplicate-blocked/v1",
    "5" * 64,
    "extension",
)


def _identity(input_data: SettlementEntityInput) -> SettlementIdentity:
    return SettlementIdentity(
        IdentityComponent(
            ORGANIZATION_ID_TYPE.component_name,
            ORGANIZATION_ID_TYPE.type_id,
            ORGANIZATION_ID_TYPE.type_sha256,
            input_data.organization_id_sha256,
        ),
        IdentityComponent(
            SETTLEMENT_ID_TYPE.component_name,
            SETTLEMENT_ID_TYPE.type_id,
            SETTLEMENT_ID_TYPE.type_sha256,
            input_data.settlement_id_sha256,
        ),
    )


def _bind_factory_execute(
    construct_snapshot: Callable[..., SettlementEntitySnapshot],
    construction_authority: object,
) -> Callable[..., SettlementEntitySuccess | SettlementEntityFailure]:
    def execute(
        self: SettlementEntityFactory,
        route_id: str,
        input_data: SettlementEntityInput,
    ) -> SettlementEntitySuccess | SettlementEntityFailure:
        if route_id not in (
            "factory",
            "deserialization-reconstruction",
            "lifecycle-transition",
        ):
            raise ValueError("SETTLEMENT_ENTITY_CONSTRUCTION_ROUTE_UNSUPPORTED")
        trace: list[ValidatorExecution] = []
        for ordinal, validator in enumerate(self.validators, start=1):
            failure_code: str | None = None
            if (
                validator.validator_id == "rule.settlement.owner-matches/v1"
                and input_data.organization_id_sha256
                != input_data.owner_organization_id_sha256
            ):
                failure_code = "OWNER_MISMATCH"
            if (
                validator.validator_id == "rule.settlement.amount-valid/v1"
                and input_data.amount_minor <= 0
            ):
                failure_code = "AMOUNT_INVALID"
            if (
                validator.validator_id == "rule.settlement.duplicate-blocked/v1"
                and input_data.duplicate_exists
            ):
                failure_code = "DUPLICATE_SETTLEMENT"
            trace.append(ValidatorExecution(
                validator.validator_id,
                validator.validator_sha256,
                validator.origin,
                ordinal,
                "fail" if failure_code is not None else "pass",
            ))
            if failure_code is not None:
                return SettlementEntityFailure(
                    False,
                    None,
                    (failure_code,),
                    route_id,
                    tuple(trace),
                    None,
                    None,
                )
        identity_ordinal = len(trace) + 1
        snapshot = construct_snapshot(
            construction_authority,
            snapshot_id=input_data.snapshot_id,
            entity_case_id=input_data.entity_case_id,
            sequence=input_data.sequence,
            route_id=route_id,
            predecessor_snapshot_id=input_data.predecessor_snapshot_id,
            identity=_identity(input_data),
            state_sha256=input_data.state_sha256,
        )
        return SettlementEntitySuccess(
            True,
            snapshot,
            (),
            ConstructionTrace(
                route_id,
                0,
                tuple(trace),
                identity_ordinal,
                identity_ordinal + 1,
                identity_ordinal + 2,
            ),
        )

    return execute


@dataclass(frozen=True, slots=True)
class SettlementEntityFactory:
    mode: str = "base"

    @property
    def factory_ref(self) -> FactoryRef:
        return BASE_FACTORY_REF if self.mode == "base" else EXTENSION_FACTORY_REF

    @property
    def validators(self) -> tuple[ValidatorRef, ...]:
        if self.mode == "base":
            return BASE_VALIDATORS
        return (*BASE_VALIDATORS, DUPLICATE_BLOCKED_VALIDATOR)

    @property
    def identity_resolver_ref(self) -> IdentityResolverRef:
        return IDENTITY_RESOLVER_REF

    @property
    def direct_constructor(self) -> None:
        return None

    def extend_with_duplicate_blocked(self) -> SettlementEntityFactory | None:
        if self.mode != "base":
            return None
        return SettlementEntityFactory("duplicate-blocked")

    _execute = _bind_factory_execute(
        _construct_snapshot,
        _factory_construction_authority,
    )

    def create(
        self,
        input_data: SettlementEntityInput,
    ) -> SettlementEntitySuccess | SettlementEntityFailure:
        return self._execute("factory", input_data)

    def reconstruct(
        self,
        input_data: SettlementEntityInput,
    ) -> SettlementEntitySuccess | SettlementEntityFailure:
        return self._execute("deserialization-reconstruction", input_data)

    def transition(
        self,
        predecessor: SettlementEntitySnapshot,
        *,
        snapshot_id: str,
        state_sha256: str,
        amount_minor: int,
        duplicate_exists: bool = False,
    ) -> SettlementEntitySuccess | SettlementEntityFailure:
        source = SettlementEntityInput(
            snapshot_id,
            predecessor.entity_case_id,
            predecessor.sequence + 1,
            predecessor.snapshot_id,
            predecessor.identity.organization_id.normalized_value_sha256,
            predecessor.identity.settlement_id.normalized_value_sha256,
            predecessor.identity.organization_id.normalized_value_sha256,
            amount_minor,
            duplicate_exists,
            state_sha256,
        )
        return self._execute("lifecycle-transition", source)


del _bind_factory_execute
del _construct_snapshot
del _factory_construction_authority


def create_settlement_entity_factory() -> SettlementEntityFactory:
    return SettlementEntityFactory("base")


@dataclass(frozen=True, slots=True)
class SettlementEntityProtocol:
    protocol_id: str
    concept_id: str
    identity_components: tuple[str, str]
    equality_mode: str
    hash_mode: str
    immutability_mode: str
    validator_order: str
    extension_policy: str
    extension_cycle_policy: str
    construction_routes: tuple[str, str, str, str]
    direct_constructor_policy: str


SETTLEMENT_ENTITY_PROTOCOL: Final = SettlementEntityProtocol(
    "python.validated-extensible-entity-factory/v1",
    "settlement.Settlement",
    ("organization_id", "settlement_id"),
    "canonical-identity-only",
    "canonical-identity-only",
    "immutable-lifecycle-snapshots",
    "base-then-extension-before-identity-and-construction",
    "additive-only",
    "acyclic",
    (
        "factory",
        "deserialization-reconstruction",
        "lifecycle-transition",
        "language-visible-direct-constructor",
    ),
    "private-inaccessible",
)
