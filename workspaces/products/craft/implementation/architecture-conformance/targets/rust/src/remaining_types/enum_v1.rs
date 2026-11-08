use std::error::Error;
use std::fmt::{Display, Formatter};

pub const SHIPMENT_PRIORITY_ENUM_ID: &str = "candidate.logistics.shipment-priority";
pub const UNKNOWN_WIRE_ERROR_CODE: &str = "DOMAINSPEC_ENUM_UNKNOWN_WIRE";

#[derive(Debug, Copy, Clone, PartialEq, Eq, Hash)]
pub enum ShipmentPriority {
    Deferred,
    Expedited,
    Normal,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DomainSpecEnumWireError {
    pub code: &'static str,
    pub enum_id: &'static str,
    pub wire_value: String,
}

impl Display for DomainSpecEnumWireError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> std::fmt::Result {
        write!(
            formatter,
            "{}:{}:{}",
            self.code, self.enum_id, self.wire_value
        )
    }
}

impl Error for DomainSpecEnumWireError {}

pub fn emit_shipment_priority(value: ShipmentPriority) -> &'static str {
    match value {
        ShipmentPriority::Deferred => "deferred",
        ShipmentPriority::Expedited => "expedited",
        ShipmentPriority::Normal => "normal",
    }
}

pub fn shipment_priority_member_id(value: ShipmentPriority) -> &'static str {
    match value {
        ShipmentPriority::Deferred => "priority.deferred",
        ShipmentPriority::Expedited => "priority.expedited",
        ShipmentPriority::Normal => "priority.normal",
    }
}

pub fn parse_shipment_priority(
    wire_value: &str,
) -> Result<ShipmentPriority, DomainSpecEnumWireError> {
    match wire_value {
        "deferred" => Ok(ShipmentPriority::Deferred),
        "expedited" => Ok(ShipmentPriority::Expedited),
        "normal" => Ok(ShipmentPriority::Normal),
        unknown => Err(DomainSpecEnumWireError {
            code: UNKNOWN_WIRE_ERROR_CODE,
            enum_id: SHIPMENT_PRIORITY_ENUM_ID,
            wire_value: unknown.to_owned(),
        }),
    }
}
