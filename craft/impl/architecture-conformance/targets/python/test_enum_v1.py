from __future__ import annotations

import json
from pathlib import Path
from typing import cast
import unittest

from remaining_types.enum_v1 import (
    DomainSpecEnumMemberError,
    DomainSpecEnumWireError,
    ShipmentPriority,
    emit_shipment_priority,
    parse_shipment_priority,
    shipment_priority_member_id,
)


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[5]
OWNER_CATALOGUE = REPOSITORY_ROOT / (
    "projects/domainspec-v2/development/remaining-meta-types/admissions/enum/"
    "owner-member-wire-catalogue.json"
)


class PythonNominalEnumV1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.owner = json.loads(OWNER_CATALOGUE.read_text(encoding="utf8"))

    def test_owner_catalogue_is_the_expected_member_wire_source(self) -> None:
        expected = {
            member["member_key"]: (member["member_id"], member["wire_value"])
            for member in self.owner["members"]
        }
        self.assertEqual(set(ShipmentPriority.__members__), set(expected))
        self.assertEqual(len(ShipmentPriority.__members__), len(list(ShipmentPriority)))
        for member_key, member in ShipmentPriority.__members__.items():
            with self.subTest(member_key=member_key):
                member_id, wire_value = expected[member_key]
                self.assertEqual(shipment_priority_member_id(member), member_id)
                self.assertEqual(emit_shipment_priority(member), wire_value)
                self.assertIs(parse_shipment_priority(wire_value), member)

    def test_enum_is_nominal_without_string_mixin_aliases_or_raw_equality(self) -> None:
        self.assertFalse(issubclass(ShipmentPriority, str))
        self.assertEqual(len({id(member) for member in ShipmentPriority.__members__.values()}), 3)
        for member in ShipmentPriority:
            wire = emit_shipment_priority(member)
            self.assertNotEqual(member, wire)
            self.assertNotEqual(wire, member)

    def test_unknown_wire_has_domainspec_structure_and_never_constructs(self) -> None:
        unknown = "__unknown_shipment_priority__"
        with self.assertRaises(ValueError):
            ShipmentPriority(unknown)
        with self.assertRaises(DomainSpecEnumWireError) as caught:
            parse_shipment_priority(unknown)
        self.assertEqual(caught.exception.as_dict(), {
            "code": "DOMAINSPEC_ENUM_UNKNOWN_WIRE",
            "enum_id": "candidate.logistics.shipment-priority",
            "wire_value": unknown,
        })

    def test_member_emit_is_total_only_over_the_nominal_domain(self) -> None:
        with self.assertRaises(DomainSpecEnumMemberError) as caught:
            emit_shipment_priority(cast(ShipmentPriority, "normal"))
        self.assertEqual(caught.exception.code, "DOMAINSPEC_ENUM_MEMBER_INVALID")

    def test_populated_enum_rejects_subclass_extension(self) -> None:
        with self.assertRaises(TypeError):
            class ExtendedShipmentPriority(ShipmentPriority):
                Bulk = "bulk"


if __name__ == "__main__":
    unittest.main()
