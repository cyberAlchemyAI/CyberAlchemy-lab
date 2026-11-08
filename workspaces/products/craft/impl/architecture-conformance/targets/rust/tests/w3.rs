use domainspec_architecture_conformance_rust::w3::*;
use std::cell::RefCell;

#[test]
fn realizes_mapping_event_and_operation() {
    let record = SettlementRecord {id: "req-1".into(), player_id: "player-1".into(), amount: 42};
    assert_eq!(map_settlement_response(&record).settlement_id, "req-1");
    assert_eq!(make_settlement_created(&record).occurrence_id, "settlement:req-1");

    let trace = RefCell::new(Vec::new());
    let (response, event) = complete_settlement(
        "req-1", "player-1", 42, None,
        |_, _| { trace.borrow_mut().extend(["write", "outbox"]); Ok(()) },
    ).expect("valid settlement");
    assert_eq!(response.settlement_id, "req-1");
    assert_eq!(event.event_type, "SettlementCreated");
    assert_eq!(*trace.borrow(), vec!["write", "outbox"]);
}

#[test]
fn operation_uses_one_atomic_commit_boundary() {
    let attempts = RefCell::new(Vec::new());
    let result = complete_settlement(
        "req-2", "player-1", 42, None,
        |_, _| { attempts.borrow_mut().push("atomic-commit"); Err("COMMIT_FAILED") },
    );
    assert_eq!(result, Err("COMMIT_FAILED"));
    assert_eq!(*attempts.borrow(), vec!["atomic-commit"]);
}

#[test]
fn rejects_mapping_and_effect_hostiles() {
    let fields = [("id", "settlement_id")];
    let contract = MappingContract {source: "Record/v1", target: "Response/v1", fields: &fields, effect_policy_none: true};
    let observed = MappingObservation {source: "Response/v1", target: "Record/v1", fields: &[], effects: &["log"]};
    assert_eq!(evaluate_mapping(&contract, Some(&observed)), (
        W3Verdict::Reject,
        vec!["ARCH_MAPPING_ENDPOINT_DRIFT", "ARCH_MAPPING_CORRESPONDENCE_DRIFT", "ARCH_MAPPING_EFFECT_UNDECLARED"],
    ));
    assert_eq!(evaluate_mapping(&contract, None).0, W3Verdict::Unsupported);

    assert_eq!(evaluate_event("present", "durable-outbox-append", &["domain-state-commit", "durable-outbox-append"], true), (
        W3Verdict::Reject,
        vec!["ARCH_EVENT_NOT_PAST_FACT", "ARCH_EVENT_CHECKPOINT_INVALID", "ARCH_EVENT_EXACTLY_ONCE_INFLATION"],
    ));
    assert_eq!(evaluate_operation(&["rule", "write", "event"], &["write", "rule", "event"], true, false, false), (
        W3Verdict::Reject,
        vec!["ARCH_OPERATION_ORDER_DRIFT", "ARCH_OPERATION_WRITE_RESTORE", "ARCH_OPERATION_GUARD_INVALID", "ARCH_OPERATION_CONTINUATION_OPEN"],
    ));
}

#[test]
fn interface_uses_exact_multi_member_exposure() {
    let expected = ["Operation:completeSettlement", "Query:findSettlement"];
    assert_eq!(evaluate_interface(("SettlementPort", "1", &expected), ("SettlementPort", "1", &expected)).0, W3Verdict::Pass);
    let extra = ["Operation:completeSettlement", "Query:findSettlement", "Operation:adminDelete"];
    assert_eq!(evaluate_interface(("SettlementPort", "1", &expected), ("SettlementPort", "1", &extra)).1, vec!["ARCH_INTERFACE_EXPOSURE_DRIFT"]);
}
