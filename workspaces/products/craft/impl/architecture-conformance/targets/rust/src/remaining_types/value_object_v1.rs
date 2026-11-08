use std::hash::{Hash, Hasher};

pub const CONCEPT_ID: &str = "settlement.SettlementValue";
pub const BASE_FACTORY_ID: &str = "factory.settlement-value.base/v1";
pub const BASE_FACTORY_SHA256: &str =
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
pub const EXTENSION_FACTORY_ID: &str =
    "factory.settlement-value.extended-validation/v1";
pub const EXTENSION_FACTORY_SHA256: &str =
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";

pub const CURRENCY_PROTOCOL_ID: &str =
    "rust.eq-hash-value-component.currency-code/v1";
pub const CURRENCY_PROTOCOL_SHA256: &str =
    "1111111111111111111111111111111111111111111111111111111111111111";
pub const MINOR_UNITS_PROTOCOL_ID: &str =
    "rust.eq-hash-value-component.minor-units/v1";
pub const MINOR_UNITS_PROTOCOL_SHA256: &str =
    "2222222222222222222222222222222222222222222222222222222222222222";
pub const SETTLEMENT_ACCOUNT_PROTOCOL_ID: &str =
    "rust.eq-hash-value-component.settlement-account/v1";
pub const SETTLEMENT_ACCOUNT_PROTOCOL_SHA256: &str =
    "3333333333333333333333333333333333333333333333333333333333333333";

pub const CURRENCY_VALIDATOR_ID: &str =
    "rule.settlement-value.currency-supported/v1";
pub const CURRENCY_VALIDATOR_SHA256: &str =
    "4444444444444444444444444444444444444444444444444444444444444444";
pub const MINOR_UNITS_VALIDATOR_ID: &str =
    "rule.settlement-value.nonnegative-minor-units/v1";
pub const MINOR_UNITS_VALIDATOR_SHA256: &str =
    "5555555555555555555555555555555555555555555555555555555555555555";
pub const ACCOUNT_ACTIVE_VALIDATOR_ID: &str =
    "rule.settlement-value.account-active/v1";
pub const ACCOUNT_ACTIVE_VALIDATOR_SHA256: &str =
    "6666666666666666666666666666666666666666666666666666666666666666";

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ComponentInput {
    pub protocol_id: String,
    pub protocol_sha256: String,
    pub normalized_value_sha256: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SettlementAccountInput {
    pub component: ComponentInput,
    pub account_ref: String,
    pub active: bool,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SettlementValueInput {
    pub currency: ComponentInput,
    pub minor_units: ComponentInput,
    pub minor_units_negative: bool,
    pub settlement_account: SettlementAccountInput,
}

#[derive(Clone, Debug)]
pub struct SettlementAccountValue {
    protocol_id: String,
    protocol_sha256: String,
    normalized_value_sha256: String,
    account_ref: String,
}

impl SettlementAccountValue {
    pub fn protocol_id(&self) -> &str {
        &self.protocol_id
    }

    pub fn protocol_sha256(&self) -> &str {
        &self.protocol_sha256
    }

    pub fn normalized_value_sha256(&self) -> &str {
        &self.normalized_value_sha256
    }

    pub fn account_ref(&self) -> &str {
        &self.account_ref
    }
}

impl PartialEq for SettlementAccountValue {
    fn eq(&self, other: &Self) -> bool {
        self.protocol_id == other.protocol_id
            && self.protocol_sha256 == other.protocol_sha256
            && self.normalized_value_sha256 == other.normalized_value_sha256
    }
}

impl Eq for SettlementAccountValue {}

impl Hash for SettlementAccountValue {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.protocol_id.hash(state);
        self.protocol_sha256.hash(state);
        self.normalized_value_sha256.hash(state);
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ComponentBinding {
    pub component_name: &'static str,
    pub protocol_id: String,
    pub protocol_sha256: String,
    pub normalized_value_sha256: String,
    pub nested_value_object: bool,
}

#[derive(Clone, Debug)]
pub struct SettlementValue {
    currency_sha256: String,
    minor_units_sha256: String,
    settlement_account: SettlementAccountValue,
    component_bindings: [ComponentBinding; 3],
}

impl SettlementValue {
    pub fn normalized_tuple(&self) -> [&str; 3] {
        [
            &self.currency_sha256,
            &self.minor_units_sha256,
            self.settlement_account.normalized_value_sha256(),
        ]
    }

    pub fn settlement_account(&self) -> &SettlementAccountValue {
        &self.settlement_account
    }

    pub fn component_bindings(&self) -> &[ComponentBinding; 3] {
        &self.component_bindings
    }
}

impl PartialEq for SettlementValue {
    fn eq(&self, other: &Self) -> bool {
        self.currency_sha256 == other.currency_sha256
            && self.minor_units_sha256 == other.minor_units_sha256
            && self.settlement_account == other.settlement_account
    }
}

impl Eq for SettlementValue {}

impl Hash for SettlementValue {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.currency_sha256.hash(state);
        self.minor_units_sha256.hash(state);
        self.settlement_account.hash(state);
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct ValidatorRef {
    pub validator_id: &'static str,
    pub validator_sha256: &'static str,
    pub origin: &'static str,
}

pub const BASE_VALIDATORS: [ValidatorRef; 2] = [
    ValidatorRef {
        validator_id: CURRENCY_VALIDATOR_ID,
        validator_sha256: CURRENCY_VALIDATOR_SHA256,
        origin: "base",
    },
    ValidatorRef {
        validator_id: MINOR_UNITS_VALIDATOR_ID,
        validator_sha256: MINOR_UNITS_VALIDATOR_SHA256,
        origin: "base",
    },
];

pub const EXTENSION_VALIDATORS: [ValidatorRef; 3] = [
    BASE_VALIDATORS[0],
    BASE_VALIDATORS[1],
    ValidatorRef {
        validator_id: ACCOUNT_ACTIVE_VALIDATOR_ID,
        validator_sha256: ACCOUNT_ACTIVE_VALIDATOR_SHA256,
        origin: "extension",
    },
];

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ValidationFailure {
    pub failure_codes: Vec<&'static str>,
    pub validator_trace: Vec<String>,
}

#[derive(Clone, Debug)]
pub enum FormationResult {
    Formed {
        value: SettlementValue,
        validator_trace: Vec<String>,
    },
    Invalid(ValidationFailure),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum FactoryMode {
    Base,
    WithAccountActive,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SettlementValueFactory {
    mode: FactoryMode,
}

fn trace_entry(validator: ValidatorRef) -> String {
    format!("{}@{}", validator.validator_id, validator.validator_sha256)
}

fn protocol_matches(input: &ComponentInput, id: &str, digest: &str) -> bool {
    input.protocol_id == id && input.protocol_sha256 == digest
}

impl SettlementValueFactory {
    pub fn base() -> Self {
        Self {
            mode: FactoryMode::Base,
        }
    }

    pub fn factory_id(&self) -> &'static str {
        match self.mode {
            FactoryMode::Base => BASE_FACTORY_ID,
            FactoryMode::WithAccountActive => EXTENSION_FACTORY_ID,
        }
    }

    pub fn factory_sha256(&self) -> &'static str {
        match self.mode {
            FactoryMode::Base => BASE_FACTORY_SHA256,
            FactoryMode::WithAccountActive => EXTENSION_FACTORY_SHA256,
        }
    }

    pub fn validators(&self) -> &'static [ValidatorRef] {
        match self.mode {
            FactoryMode::Base => &BASE_VALIDATORS,
            FactoryMode::WithAccountActive => &EXTENSION_VALIDATORS,
        }
    }

    pub fn extend_with_account_active(&self) -> Option<Self> {
        match self.mode {
            FactoryMode::Base => Some(Self {
                mode: FactoryMode::WithAccountActive,
            }),
            FactoryMode::WithAccountActive => None,
        }
    }

    pub fn create(&self, input: &SettlementValueInput) -> FormationResult {
        if !protocol_matches(
            &input.currency,
            CURRENCY_PROTOCOL_ID,
            CURRENCY_PROTOCOL_SHA256,
        ) {
            return FormationResult::Invalid(ValidationFailure {
                failure_codes: vec!["CURRENCY_PROTOCOL_INVALID"],
                validator_trace: vec![],
            });
        }
        if !protocol_matches(
            &input.minor_units,
            MINOR_UNITS_PROTOCOL_ID,
            MINOR_UNITS_PROTOCOL_SHA256,
        ) {
            return FormationResult::Invalid(ValidationFailure {
                failure_codes: vec!["MINOR_UNITS_PROTOCOL_INVALID"],
                validator_trace: vec![],
            });
        }
        if !protocol_matches(
            &input.settlement_account.component,
            SETTLEMENT_ACCOUNT_PROTOCOL_ID,
            SETTLEMENT_ACCOUNT_PROTOCOL_SHA256,
        ) {
            return FormationResult::Invalid(ValidationFailure {
                failure_codes: vec!["SETTLEMENT_ACCOUNT_PROTOCOL_INVALID"],
                validator_trace: vec![],
            });
        }

        let mut validator_trace = vec![trace_entry(BASE_VALIDATORS[0])];
        validator_trace.push(trace_entry(BASE_VALIDATORS[1]));
        if input.minor_units_negative {
            return FormationResult::Invalid(ValidationFailure {
                failure_codes: vec!["NEGATIVE_MINOR_UNITS"],
                validator_trace,
            });
        }
        if self.mode == FactoryMode::WithAccountActive {
            validator_trace.push(trace_entry(EXTENSION_VALIDATORS[2]));
            if !input.settlement_account.active {
                return FormationResult::Invalid(ValidationFailure {
                    failure_codes: vec!["INACTIVE_SETTLEMENT_ACCOUNT"],
                    validator_trace,
                });
            }
        }

        let account = SettlementAccountValue {
            protocol_id: input.settlement_account.component.protocol_id.clone(),
            protocol_sha256: input
                .settlement_account
                .component
                .protocol_sha256
                .clone(),
            normalized_value_sha256: input
                .settlement_account
                .component
                .normalized_value_sha256
                .clone(),
            account_ref: input.settlement_account.account_ref.clone(),
        };
        let component_bindings = [
            ComponentBinding {
                component_name: "currency",
                protocol_id: input.currency.protocol_id.clone(),
                protocol_sha256: input.currency.protocol_sha256.clone(),
                normalized_value_sha256: input.currency.normalized_value_sha256.clone(),
                nested_value_object: false,
            },
            ComponentBinding {
                component_name: "minor_units",
                protocol_id: input.minor_units.protocol_id.clone(),
                protocol_sha256: input.minor_units.protocol_sha256.clone(),
                normalized_value_sha256: input
                    .minor_units
                    .normalized_value_sha256
                    .clone(),
                nested_value_object: false,
            },
            ComponentBinding {
                component_name: "settlement_account",
                protocol_id: account.protocol_id.clone(),
                protocol_sha256: account.protocol_sha256.clone(),
                normalized_value_sha256: account.normalized_value_sha256.clone(),
                nested_value_object: true,
            },
        ];
        FormationResult::Formed {
            value: SettlementValue {
                currency_sha256: input.currency.normalized_value_sha256.clone(),
                minor_units_sha256: input.minor_units.normalized_value_sha256.clone(),
                settlement_account: account,
                component_bindings,
            },
            validator_trace,
        }
    }
}
