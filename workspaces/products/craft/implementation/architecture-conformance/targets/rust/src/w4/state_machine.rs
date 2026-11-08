#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SettlementState { Pending, Settled, Failed }
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SettlementTrigger { Confirm, Reject }
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TransitionDecision { pub accepted: bool, pub next_state: Option<SettlementState>, pub guard_ids: Vec<&'static str>, pub effect_intents: Vec<&'static str> }

pub fn transition_settlement_lifecycle(state: SettlementState, trigger: SettlementTrigger) -> TransitionDecision {
    match (state, trigger) {
        (SettlementState::Pending, SettlementTrigger::Confirm) => TransitionDecision {accepted: true, next_state: Some(SettlementState::Settled), guard_ids: vec!["can-settle"], effect_intents: vec!["persist-settlement", "append-settlement-created"]},
        (SettlementState::Pending, SettlementTrigger::Reject) => TransitionDecision {accepted: true, next_state: Some(SettlementState::Failed), guard_ids: vec!["can-settle"], effect_intents: vec!["record-rejection"]},
        _ => TransitionDecision {accepted: false, next_state: None, guard_ids: vec![], effect_intents: vec![]},
    }
}
