"""Python W3-A realization witness.

These native forms corroborate descriptor-bound DomainSpec meaning. They do not
infer a Mapping, Interface, Event, or Operation from syntax alone.
"""

from dataclasses import dataclass
from typing import Awaitable, Callable, Literal, Protocol


@dataclass(frozen=True)
class SettlementRecord:
    id: str
    player_id: str
    amount: int


@dataclass(frozen=True)
class SettlementResponse:
    settlement_id: str
    player_id: str
    amount: int


@dataclass(frozen=True)
class SettlementCreated:
    type: Literal["SettlementCreated"]
    version: Literal["1"]
    occurrence_id: str
    settlement_id: str
    player_id: str
    amount: int


def map_settlement_response(record: SettlementRecord) -> SettlementResponse:
    return SettlementResponse(
        settlement_id=record.id,
        player_id=record.player_id,
        amount=record.amount,
    )


class SettlementPortV1(Protocol):
    async def complete_settlement(self, request_id: str, player_id: str, amount: int) -> SettlementResponse: ...

    async def find_settlement(self, request_id: str) -> SettlementResponse | None: ...


def make_settlement_created(record: SettlementRecord) -> SettlementCreated:
    return SettlementCreated(
        type="SettlementCreated",
        version="1",
        occurrence_id=f"settlement:{record.id}",
        settlement_id=record.id,
        player_id=record.player_id,
        amount=record.amount,
    )


async def complete_settlement(
    *,
    request_id: str,
    player_id: str,
    amount: int,
    existing_settlement_id: str | None,
    commit_atomically: Callable[[SettlementRecord, SettlementCreated], Awaitable[None]],
) -> tuple[SettlementResponse, SettlementCreated]:
    allowed = amount > 0 and existing_settlement_id is None
    if not allowed:
        raise ValueError("SETTLEMENT_REJECTED")
    record = SettlementRecord(id=request_id, player_id=player_id, amount=amount)
    event = make_settlement_created(record)
    await commit_atomically(record, event)
    return map_settlement_response(record), event


def evaluate_w3_contract(descriptor: dict, observation: dict | None) -> tuple[str, tuple[str, ...]]:
    if observation is None:
        return "unsupported", ("ARCH_W3_OBSERVER_UNSUPPORTED",)
    if descriptor["kind"] != observation.get("kind"):
        return "indeterminate", ("ARCH_W3_OBSERVATION_INCOMPLETE",)

    findings: list[str] = []
    kind = descriptor["kind"]
    if kind == "Mapping":
        if (descriptor["source_contract_id"], descriptor["target_contract_id"]) != (
            observation.get("source_contract_id"), observation.get("target_contract_id")
        ):
            findings.append("ARCH_MAPPING_ENDPOINT_DRIFT")
        if descriptor["correspondence"] != observation.get("observed_correspondence"):
            findings.append("ARCH_MAPPING_CORRESPONDENCE_DRIFT")
        if descriptor["effect_policy"] == "none" and observation.get("effects"):
            findings.append("ARCH_MAPPING_EFFECT_UNDECLARED")
    elif kind == "Interface":
        contract = (descriptor["boundary_kind"], descriptor["contract_id"], descriptor["exact_version"])
        observed = (observation.get("boundary_kind"), observation.get("contract_id"), observation.get("version"))
        if contract != observed:
            findings.append("ARCH_INTERFACE_CONTRACT_DRIFT")
        if descriptor["exposed_bindings"] != observation.get("exposed_bindings"):
            findings.append("ARCH_INTERFACE_EXPOSURE_DRIFT")
    elif kind == "Event":
        if observation.get("tense") != "past":
            findings.append("ARCH_EVENT_NOT_PAST_FACT")
        if observation.get("durable_checkpoints") != [descriptor["fact_checkpoint"]]:
            findings.append("ARCH_EVENT_CHECKPOINT_INVALID")
        if observation.get("distributed_exactly_once_claim"):
            findings.append("ARCH_EVENT_EXACTLY_ONCE_INFLATION")
    elif kind == "Operation":
        if observation.get("trace") != descriptor["ordered_checkpoints"]:
            findings.append("ARCH_OPERATION_ORDER_DRIFT")
        if any(write["state"] == "restored" for write in observation.get("writes", [])):
            findings.append("ARCH_OPERATION_WRITE_RESTORE")
        if not all(item["invoked"] and item["decision_used"] for item in observation.get("guard_results", [])):
            findings.append("ARCH_OPERATION_GUARD_INVALID")
        if not observation.get("continuation_closed"):
            findings.append("ARCH_OPERATION_CONTINUATION_OPEN")
    return ("pass" if not findings else "reject"), tuple(findings)
