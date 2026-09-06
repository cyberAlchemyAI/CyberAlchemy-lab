from __future__ import annotations

from enum import Enum, unique
from typing import NoReturn


ENUM_ID = "candidate.logistics.shipment-priority"


class DomainSpecEnumWireError(ValueError):
    code = "DOMAINSPEC_ENUM_UNKNOWN_WIRE"

    def __init__(self, wire_value: object):
        self.enum_id = ENUM_ID
        self.wire_value = wire_value
        super().__init__(f"{self.code}:{self.enum_id}:{wire_value!r}")

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "enum_id": self.enum_id,
            "wire_value": self.wire_value,
        }


class DomainSpecEnumMemberError(TypeError):
    code = "DOMAINSPEC_ENUM_MEMBER_INVALID"

    def __init__(self, member: object):
        self.enum_id = ENUM_ID
        self.member = member
        super().__init__(f"{self.code}:{self.enum_id}:{member!r}")


@unique
class ShipmentPriority(Enum):
    Deferred = "deferred"
    Expedited = "expedited"
    Normal = "normal"


def _invalid_member(member: object) -> NoReturn:
    raise DomainSpecEnumMemberError(member)


def emit_shipment_priority(member: ShipmentPriority) -> str:
    if member is ShipmentPriority.Deferred:
        return "deferred"
    if member is ShipmentPriority.Expedited:
        return "expedited"
    if member is ShipmentPriority.Normal:
        return "normal"
    return _invalid_member(member)


def parse_shipment_priority(wire_value: str) -> ShipmentPriority:
    if wire_value == "deferred":
        return ShipmentPriority.Deferred
    if wire_value == "expedited":
        return ShipmentPriority.Expedited
    if wire_value == "normal":
        return ShipmentPriority.Normal
    raise DomainSpecEnumWireError(wire_value)


def shipment_priority_member_id(member: ShipmentPriority) -> str:
    if member is ShipmentPriority.Deferred:
        return "priority.deferred"
    if member is ShipmentPriority.Expedited:
        return "priority.expedited"
    if member is ShipmentPriority.Normal:
        return "priority.normal"
    return _invalid_member(member)
