use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

use domainspec_architecture_conformance_rust::remaining_types::entity_v1::{
    EntityResult, SettlementEntityFactory, SettlementEntityInput,
    SettlementEntitySnapshot, AMOUNT_VALIDATOR_ID, BASE_FACTORY_ID,
    DUPLICATE_BLOCKED_VALIDATOR_ID, EXTENSION_FACTORY_ID,
    OWNER_MATCHES_VALIDATOR_ID,
};

const ORGANIZATION_A: &str =
    "6666666666666666666666666666666666666666666666666666666666666666";
const SETTLEMENT_A: &str =
    "7777777777777777777777777777777777777777777777777777777777777777";
const SETTLEMENT_B: &str =
    "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc";
const CREATED_STATE: &str =
    "8888888888888888888888888888888888888888888888888888888888888888";
const COMPLETED_STATE: &str =
    "9999999999999999999999999999999999999999999999999999999999999999";

fn owner_input(snapshot_id: &str, settlement_id: &str) -> SettlementEntityInput {
    SettlementEntityInput {
        snapshot_id: snapshot_id.to_owned(),
        entity_case_id: if settlement_id == SETTLEMENT_A {
            "settlement-a"
        } else {
            "settlement-b"
        }
        .to_owned(),
        sequence: 0,
        predecessor_snapshot_id: None,
        organization_id_sha256: ORGANIZATION_A.to_owned(),
        settlement_id_sha256: settlement_id.to_owned(),
        state_sha256: CREATED_STATE.to_owned(),
        owner_matches: true,
        amount_valid: true,
        duplicate_exists: false,
    }
}

fn formed(result: EntityResult) -> SettlementEntitySnapshot {
    match result {
        EntityResult::Formed {snapshot, ..} => snapshot,
        EntityResult::Invalid(failure) => panic!("unexpected failure: {failure:?}"),
    }
}

fn hash(value: &SettlementEntitySnapshot) -> u64 {
    let mut hasher = DefaultHasher::new();
    value.hash(&mut hasher);
    hasher.finish()
}

#[test]
fn entity_factory_routes_preserve_stable_typed_identity_and_identity_only_equality() {
    let extension = SettlementEntityFactory::base()
        .extend_with_duplicate_blocked()
        .expect("one additive extension");
    let created = formed(extension.create(&owner_input(
        "snapshot.settlement-a.created",
        SETTLEMENT_A,
    )));
    let reconstructed = formed(extension.reconstruct(&SettlementEntityInput {
        snapshot_id: "snapshot.settlement-a.reconstructed".to_owned(),
        ..owner_input("snapshot.settlement-a.created", SETTLEMENT_A)
    }));
    let completed = formed(extension.transition(
        &created,
        "snapshot.settlement-a.completed",
        COMPLETED_STATE,
    ));
    let distinct = formed(extension.create(&owner_input(
        "snapshot.settlement-b.created",
        SETTLEMENT_B,
    )));

    assert_eq!(created, reconstructed);
    assert_eq!(created, completed);
    assert_eq!(hash(&created), hash(&completed));
    assert_ne!(created, distinct);
    assert_eq!(completed.sequence(), 1);
    assert_eq!(completed.predecessor_snapshot_id(),
        Some("snapshot.settlement-a.created"));
    assert_eq!(completed.state_sha256(), COMPLETED_STATE);
    assert_eq!(completed.identity().organization_id().normalized_value_sha256(),
        ORGANIZATION_A);
    assert_eq!(completed.identity().settlement_id().normalized_value_sha256(),
        SETTLEMENT_A);
}

#[test]
fn entity_validators_are_factory_bound_base_before_extension_and_fail_without_snapshot() {
    let base = SettlementEntityFactory::base();
    assert_eq!(base.factory_id(), BASE_FACTORY_ID);
    assert_eq!(base.validators().iter().map(|item| item.validator_id)
        .collect::<Vec<_>>(), vec![OWNER_MATCHES_VALIDATOR_ID, AMOUNT_VALIDATOR_ID]);
    let extension = base.extend_with_duplicate_blocked().expect("extension");
    assert_eq!(extension.factory_id(), EXTENSION_FACTORY_ID);
    assert_eq!(extension.validators().iter().map(|item| item.validator_id)
        .collect::<Vec<_>>(), vec![OWNER_MATCHES_VALIDATOR_ID,
            AMOUNT_VALIDATOR_ID, DUPLICATE_BLOCKED_VALIDATOR_ID]);
    assert!(extension.extend_with_duplicate_blocked().is_none());

    let mut invalid = owner_input("snapshot.invalid", SETTLEMENT_A);
    invalid.amount_valid = false;
    match extension.create(&invalid) {
        EntityResult::Invalid(failure) => {
            assert_eq!(failure.failure_codes, vec!["AMOUNT_INVALID"]);
            assert_eq!(failure.validator_trace.len(), 2);
            assert_eq!(failure.validator_trace[0].outcome, "pass");
            assert_eq!(failure.validator_trace[1].outcome, "fail");
        }
        EntityResult::Formed {..} => panic!("invalid amount formed a snapshot"),
    }

    let mut duplicate = owner_input("snapshot.duplicate", SETTLEMENT_A);
    duplicate.duplicate_exists = true;
    match extension.create(&duplicate) {
        EntityResult::Invalid(failure) => {
            assert_eq!(failure.failure_codes, vec!["DUPLICATE_SETTLEMENT"]);
            assert_eq!(failure.validator_trace.len(), 3);
        }
        EntityResult::Formed {..} => panic!("duplicate formed a snapshot"),
    }
}

#[test]
fn entity_executing_routes_emit_one_ordered_pipeline_trace() {
    let extension = SettlementEntityFactory::base()
        .extend_with_duplicate_blocked()
        .expect("extension");
    let input = owner_input("snapshot.settlement-a.created", SETTLEMENT_A);
    for result in [extension.create(&input), extension.reconstruct(&input)] {
        match result {
            EntityResult::Formed {trace, ..} => {
                assert_eq!(trace.normalization_ordinal, 0);
                assert_eq!(trace.validator_trace.len(), 3);
                assert_eq!(trace.validator_trace.iter().map(|item| item.ordinal)
                    .collect::<Vec<_>>(), vec![1, 2, 3]);
                assert_eq!(trace.identity_resolution_ordinal, 4);
                assert_eq!(trace.construction_ordinal, 5);
                assert_eq!(trace.immutability_ordinal, 6);
            }
            EntityResult::Invalid(failure) => panic!("unexpected failure: {failure:?}"),
        }
    }
}
