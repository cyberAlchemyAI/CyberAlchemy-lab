//! Rust W3-A realization witness. Native types corroborate an exact descriptor;
//! they do not mint DomainSpec meaning from a trait, struct, or function alone.

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SettlementRecord {
    pub id: String,
    pub player_id: String,
    pub amount: i64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SettlementResponse {
    pub settlement_id: String,
    pub player_id: String,
    pub amount: i64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SettlementCreated {
    pub event_type: &'static str,
    pub version: &'static str,
    pub occurrence_id: String,
    pub settlement_id: String,
    pub player_id: String,
    pub amount: i64,
}

pub fn map_settlement_response(record: &SettlementRecord) -> SettlementResponse {
    SettlementResponse {
        settlement_id: record.id.clone(),
        player_id: record.player_id.clone(),
        amount: record.amount,
    }
}

pub trait SettlementPortV1 {
    fn complete_settlement(&mut self, request_id: &str, player_id: &str, amount: i64) -> Result<SettlementResponse, &'static str>;
    fn find_settlement(&self, request_id: &str) -> Option<SettlementResponse>;
}

pub fn make_settlement_created(record: &SettlementRecord) -> SettlementCreated {
    SettlementCreated {
        event_type: "SettlementCreated",
        version: "1",
        occurrence_id: format!("settlement:{}", record.id),
        settlement_id: record.id.clone(),
        player_id: record.player_id.clone(),
        amount: record.amount,
    }
}

pub fn complete_settlement<C>(
    request_id: &str,
    player_id: &str,
    amount: i64,
    existing_settlement_id: Option<&str>,
    mut commit_atomically: C,
) -> Result<(SettlementResponse, SettlementCreated), &'static str>
where
    C: FnMut(&SettlementRecord, &SettlementCreated) -> Result<(), &'static str>,
{
    if amount <= 0 || existing_settlement_id.is_some() {
        return Err("SETTLEMENT_REJECTED");
    }
    let record = SettlementRecord {id: request_id.into(), player_id: player_id.into(), amount};
    let event = make_settlement_created(&record);
    commit_atomically(&record, &event)?;
    Ok((map_settlement_response(&record), event))
}

#[derive(Debug, PartialEq, Eq)]
pub enum W3Verdict { Pass, Reject, Unsupported, Indeterminate }

#[derive(Debug)]
pub struct MappingContract<'a> {
    pub source: &'a str,
    pub target: &'a str,
    pub fields: &'a [(&'a str, &'a str)],
    pub effect_policy_none: bool,
}

#[derive(Debug)]
pub struct MappingObservation<'a> {
    pub source: &'a str,
    pub target: &'a str,
    pub fields: &'a [(&'a str, &'a str)],
    pub effects: &'a [&'a str],
}

pub fn evaluate_mapping(contract: &MappingContract<'_>, observed: Option<&MappingObservation<'_>>) -> (W3Verdict, Vec<&'static str>) {
    let Some(observed) = observed else { return (W3Verdict::Unsupported, vec!["ARCH_W3_OBSERVER_UNSUPPORTED"]); };
    let mut findings = Vec::new();
    if (contract.source, contract.target) != (observed.source, observed.target) { findings.push("ARCH_MAPPING_ENDPOINT_DRIFT"); }
    if contract.fields != observed.fields { findings.push("ARCH_MAPPING_CORRESPONDENCE_DRIFT"); }
    if contract.effect_policy_none && !observed.effects.is_empty() { findings.push("ARCH_MAPPING_EFFECT_UNDECLARED"); }
    (if findings.is_empty() { W3Verdict::Pass } else { W3Verdict::Reject }, findings)
}

pub fn evaluate_interface(expected: (&str, &str, &[&str]), observed: (&str, &str, &[&str])) -> (W3Verdict, Vec<&'static str>) {
    let mut findings = Vec::new();
    if expected.0 != observed.0 || expected.1 != observed.1 { findings.push("ARCH_INTERFACE_CONTRACT_DRIFT"); }
    if expected.2 != observed.2 { findings.push("ARCH_INTERFACE_EXPOSURE_DRIFT"); }
    (if findings.is_empty() { W3Verdict::Pass } else { W3Verdict::Reject }, findings)
}

pub fn evaluate_event(tense: &str, expected_checkpoint: &str, checkpoints: &[&str], exactly_once_claim: bool) -> (W3Verdict, Vec<&'static str>) {
    let mut findings = Vec::new();
    if tense != "past" { findings.push("ARCH_EVENT_NOT_PAST_FACT"); }
    if checkpoints != [expected_checkpoint] { findings.push("ARCH_EVENT_CHECKPOINT_INVALID"); }
    if exactly_once_claim { findings.push("ARCH_EVENT_EXACTLY_ONCE_INFLATION"); }
    (if findings.is_empty() { W3Verdict::Pass } else { W3Verdict::Reject }, findings)
}

pub fn evaluate_operation(expected_trace: &[&str], trace: &[&str], restored: bool, guard_used: bool, continuation_closed: bool) -> (W3Verdict, Vec<&'static str>) {
    let mut findings = Vec::new();
    if expected_trace != trace { findings.push("ARCH_OPERATION_ORDER_DRIFT"); }
    if restored { findings.push("ARCH_OPERATION_WRITE_RESTORE"); }
    if !guard_used { findings.push("ARCH_OPERATION_GUARD_INVALID"); }
    if !continuation_closed { findings.push("ARCH_OPERATION_CONTINUATION_OPEN"); }
    (if findings.is_empty() { W3Verdict::Pass } else { W3Verdict::Reject }, findings)
}
