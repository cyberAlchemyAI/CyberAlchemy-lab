use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

use domainspec_architecture_conformance_rust::remaining_types::value_object_v1::{
    ComponentInput, FormationResult, SettlementAccountInput, SettlementValue,
    SettlementValueFactory, SettlementValueInput, ACCOUNT_ACTIVE_VALIDATOR_ID,
    BASE_FACTORY_ID, CURRENCY_PROTOCOL_ID, CURRENCY_PROTOCOL_SHA256,
    EXTENSION_FACTORY_ID, MINOR_UNITS_PROTOCOL_ID, MINOR_UNITS_PROTOCOL_SHA256,
    SETTLEMENT_ACCOUNT_PROTOCOL_ID, SETTLEMENT_ACCOUNT_PROTOCOL_SHA256,
};

fn owner_input(currency: &str, minor: &str, account: &str) -> SettlementValueInput {
    SettlementValueInput {
        currency: ComponentInput {
            protocol_id: CURRENCY_PROTOCOL_ID.to_owned(),
            protocol_sha256: CURRENCY_PROTOCOL_SHA256.to_owned(),
            normalized_value_sha256: currency.to_owned(),
        },
        minor_units: ComponentInput {
            protocol_id: MINOR_UNITS_PROTOCOL_ID.to_owned(),
            protocol_sha256: MINOR_UNITS_PROTOCOL_SHA256.to_owned(),
            normalized_value_sha256: minor.to_owned(),
        },
        minor_units_negative: false,
        settlement_account: SettlementAccountInput {
            component: ComponentInput {
                protocol_id: SETTLEMENT_ACCOUNT_PROTOCOL_ID.to_owned(),
                protocol_sha256: SETTLEMENT_ACCOUNT_PROTOCOL_SHA256.to_owned(),
                normalized_value_sha256: account.to_owned(),
            },
            account_ref: "settlement-account-001".to_owned(),
            active: true,
        },
    }
}

fn formed(result: FormationResult) -> SettlementValue {
    match result {
        FormationResult::Formed { value, .. } => value,
        FormationResult::Invalid(failure) => panic!("unexpected failure: {failure:?}"),
    }
}

fn hash(value: &SettlementValue) -> u64 {
    let mut hasher = DefaultHasher::new();
    value.hash(&mut hasher);
    hasher.finish()
}

#[test]
fn value_object_uses_complete_tuple_equality_hash_and_owned_nested_value() {
    let base = SettlementValueFactory::base();
    let left = formed(base.create(&owner_input("7", "8", "9")));
    let right = formed(base.create(&owner_input("7", "8", "9")));
    assert_eq!(left, right);
    assert_eq!(hash(&left), hash(&right));
    assert_ne!(left, formed(base.create(&owner_input("c", "8", "9"))));
    assert_ne!(left, formed(base.create(&owner_input("7", "d", "9"))));
    assert_ne!(left, formed(base.create(&owner_input("7", "8", "e"))));
    assert_eq!(left.normalized_tuple(), ["7", "8", "9"]);
    assert_eq!(left.component_bindings().len(), 3);
    assert_eq!(left.settlement_account().account_ref(), "settlement-account-001");
}

#[test]
fn value_object_validates_before_formation_and_extension_is_additive_only() {
    let base = SettlementValueFactory::base();
    assert_eq!(base.factory_id(), BASE_FACTORY_ID);
    let extension = base.extend_with_account_active().expect("one extension");
    assert_eq!(extension.factory_id(), EXTENSION_FACTORY_ID);
    assert!(extension.extend_with_account_active().is_none());
    assert_eq!(extension.validators().len(), base.validators().len() + 1);
    assert_eq!(extension.validators()[2].validator_id, ACCOUNT_ACTIVE_VALIDATOR_ID);

    let valid = owner_input("7", "8", "9");
    let base_value = formed(base.create(&valid));
    let extended_value = formed(extension.create(&valid));
    assert_eq!(base_value, extended_value);
    assert_eq!(hash(&base_value), hash(&extended_value));

    let mut inactive = valid.clone();
    inactive.settlement_account.active = false;
    assert!(matches!(base.create(&inactive), FormationResult::Formed { .. }));
    match extension.create(&inactive) {
        FormationResult::Invalid(failure) => {
            assert_eq!(failure.failure_codes, vec!["INACTIVE_SETTLEMENT_ACCOUNT"]);
            assert_eq!(failure.validator_trace.len(), 3);
        }
        FormationResult::Formed { .. } => panic!("extension formed inactive account"),
    }

    let mut stale = valid.clone();
    stale.currency.protocol_sha256 = "0".repeat(64);
    match base.create(&stale) {
        FormationResult::Invalid(failure) => {
            assert_eq!(failure.failure_codes, vec!["CURRENCY_PROTOCOL_INVALID"]);
            assert!(failure.validator_trace.is_empty());
        }
        FormationResult::Formed { .. } => panic!("stale protocol formed value"),
    }
}

#[test]
fn value_object_invalid_owner_case_never_forms_a_value() {
    let extension = SettlementValueFactory::base()
        .extend_with_account_active()
        .expect("extension");
    let mut negative = owner_input("7", "f", "9");
    negative.minor_units_negative = true;
    match extension.create(&negative) {
        FormationResult::Invalid(failure) => {
            assert_eq!(failure.failure_codes, vec!["NEGATIVE_MINOR_UNITS"]);
            assert_eq!(failure.validator_trace.len(), 2);
        }
        FormationResult::Formed { .. } => panic!("invalid owner case formed value"),
    }
}
