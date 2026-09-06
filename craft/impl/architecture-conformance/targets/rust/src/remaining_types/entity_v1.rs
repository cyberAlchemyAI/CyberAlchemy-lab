use std::hash::{Hash, Hasher};

pub const CONCEPT_ID: &str = "settlement.Settlement";
pub const BASE_FACTORY_ID: &str = "factory.settlement-entity.base/v1";
pub const BASE_FACTORY_SHA256: &str =
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
pub const EXTENSION_FACTORY_ID: &str = "factory.settlement-entity.extended/v1";
pub const EXTENSION_FACTORY_SHA256: &str =
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";

pub const ORGANIZATION_ID_TYPE_ID: &str = "identity.organization-id/v1";
pub const ORGANIZATION_ID_TYPE_SHA256: &str =
    "1111111111111111111111111111111111111111111111111111111111111111";
pub const SETTLEMENT_ID_TYPE_ID: &str = "identity.settlement-id/v1";
pub const SETTLEMENT_ID_TYPE_SHA256: &str =
    "2222222222222222222222222222222222222222222222222222222222222222";

pub const OWNER_MATCHES_VALIDATOR_ID: &str = "rule.settlement.owner-matches/v1";
pub const OWNER_MATCHES_VALIDATOR_SHA256: &str =
    "3333333333333333333333333333333333333333333333333333333333333333";
pub const AMOUNT_VALIDATOR_ID: &str = "rule.settlement.amount-valid/v1";
pub const AMOUNT_VALIDATOR_SHA256: &str =
    "4444444444444444444444444444444444444444444444444444444444444444";
pub const DUPLICATE_BLOCKED_VALIDATOR_ID: &str =
    "rule.settlement.duplicate-blocked/v1";
pub const DUPLICATE_BLOCKED_VALIDATOR_SHA256: &str =
    "5555555555555555555555555555555555555555555555555555555555555555";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct ValidatorRef {
    pub validator_id: &'static str,
    pub validator_sha256: &'static str,
    pub origin: &'static str,
}

pub const BASE_VALIDATORS: [ValidatorRef; 2] = [
    ValidatorRef {
        validator_id: OWNER_MATCHES_VALIDATOR_ID,
        validator_sha256: OWNER_MATCHES_VALIDATOR_SHA256,
        origin: "base",
    },
    ValidatorRef {
        validator_id: AMOUNT_VALIDATOR_ID,
        validator_sha256: AMOUNT_VALIDATOR_SHA256,
        origin: "base",
    },
];

pub const EXTENSION_VALIDATORS: [ValidatorRef; 3] = [
    BASE_VALIDATORS[0],
    BASE_VALIDATORS[1],
    ValidatorRef {
        validator_id: DUPLICATE_BLOCKED_VALIDATOR_ID,
        validator_sha256: DUPLICATE_BLOCKED_VALIDATOR_SHA256,
        origin: "extension",
    },
];

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct OrganizationId(String);

impl OrganizationId {
    fn resolve(normalized_value_sha256: &str) -> Self {
        Self(normalized_value_sha256.to_owned())
    }

    pub fn normalized_value_sha256(&self) -> &str {
        &self.0
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct SettlementId(String);

impl SettlementId {
    fn resolve(normalized_value_sha256: &str) -> Self {
        Self(normalized_value_sha256.to_owned())
    }

    pub fn normalized_value_sha256(&self) -> &str {
        &self.0
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct SettlementIdentity {
    organization_id: OrganizationId,
    settlement_id: SettlementId,
}

impl SettlementIdentity {
    fn resolve(input: &SettlementEntityInput) -> Self {
        Self {
            organization_id: OrganizationId::resolve(&input.organization_id_sha256),
            settlement_id: SettlementId::resolve(&input.settlement_id_sha256),
        }
    }

    pub fn organization_id(&self) -> &OrganizationId {
        &self.organization_id
    }

    pub fn settlement_id(&self) -> &SettlementId {
        &self.settlement_id
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SettlementEntityInput {
    pub snapshot_id: String,
    pub entity_case_id: String,
    pub sequence: u64,
    pub predecessor_snapshot_id: Option<String>,
    pub organization_id_sha256: String,
    pub settlement_id_sha256: String,
    pub state_sha256: String,
    pub owner_matches: bool,
    pub amount_valid: bool,
    pub duplicate_exists: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ConstructionRoute {
    Factory,
    DeserializationReconstruction,
    LifecycleTransition,
}

impl ConstructionRoute {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Factory => "factory",
            Self::DeserializationReconstruction => "deserialization-reconstruction",
            Self::LifecycleTransition => "lifecycle-transition",
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ValidatorTraceEntry {
    pub validator: ValidatorRef,
    pub ordinal: usize,
    pub outcome: &'static str,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ConstructionTrace {
    pub route: ConstructionRoute,
    pub normalization_ordinal: usize,
    pub validator_trace: Vec<ValidatorTraceEntry>,
    pub identity_resolution_ordinal: usize,
    pub construction_ordinal: usize,
    pub immutability_ordinal: usize,
}

#[derive(Clone, Debug)]
pub struct SettlementEntitySnapshot {
    snapshot_id: String,
    entity_case_id: String,
    sequence: u64,
    predecessor_snapshot_id: Option<String>,
    identity: SettlementIdentity,
    state_sha256: String,
}

impl SettlementEntitySnapshot {
    fn new(input: &SettlementEntityInput, identity: SettlementIdentity) -> Self {
        Self {
            snapshot_id: input.snapshot_id.clone(),
            entity_case_id: input.entity_case_id.clone(),
            sequence: input.sequence,
            predecessor_snapshot_id: input.predecessor_snapshot_id.clone(),
            identity,
            state_sha256: input.state_sha256.clone(),
        }
    }

    pub fn snapshot_id(&self) -> &str {
        &self.snapshot_id
    }

    pub fn entity_case_id(&self) -> &str {
        &self.entity_case_id
    }

    pub fn sequence(&self) -> u64 {
        self.sequence
    }

    pub fn predecessor_snapshot_id(&self) -> Option<&str> {
        self.predecessor_snapshot_id.as_deref()
    }

    pub fn identity(&self) -> &SettlementIdentity {
        &self.identity
    }

    pub fn state_sha256(&self) -> &str {
        &self.state_sha256
    }
}

impl PartialEq for SettlementEntitySnapshot {
    fn eq(&self, other: &Self) -> bool {
        self.identity == other.identity
    }
}

impl Eq for SettlementEntitySnapshot {}

impl Hash for SettlementEntitySnapshot {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.identity.hash(state);
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct EntityValidationFailure {
    pub failure_codes: Vec<&'static str>,
    pub validator_trace: Vec<ValidatorTraceEntry>,
}

#[derive(Clone, Debug)]
pub enum EntityResult {
    Formed {
        snapshot: SettlementEntitySnapshot,
        trace: ConstructionTrace,
    },
    Invalid(EntityValidationFailure),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum FactoryMode {
    Base,
    WithDuplicateBlocked,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SettlementEntityFactory {
    mode: FactoryMode,
}

fn trace_entry(validator: ValidatorRef, ordinal: usize, outcome: &'static str) -> ValidatorTraceEntry {
    ValidatorTraceEntry {
        validator,
        ordinal,
        outcome,
    }
}

impl SettlementEntityFactory {
    pub fn base() -> Self {
        Self {
            mode: FactoryMode::Base,
        }
    }

    pub fn factory_id(&self) -> &'static str {
        match self.mode {
            FactoryMode::Base => BASE_FACTORY_ID,
            FactoryMode::WithDuplicateBlocked => EXTENSION_FACTORY_ID,
        }
    }

    pub fn factory_sha256(&self) -> &'static str {
        match self.mode {
            FactoryMode::Base => BASE_FACTORY_SHA256,
            FactoryMode::WithDuplicateBlocked => EXTENSION_FACTORY_SHA256,
        }
    }

    pub fn validators(&self) -> &'static [ValidatorRef] {
        match self.mode {
            FactoryMode::Base => &BASE_VALIDATORS,
            FactoryMode::WithDuplicateBlocked => &EXTENSION_VALIDATORS,
        }
    }

    pub fn extend_with_duplicate_blocked(&self) -> Option<Self> {
        match self.mode {
            FactoryMode::Base => Some(Self {
                mode: FactoryMode::WithDuplicateBlocked,
            }),
            FactoryMode::WithDuplicateBlocked => None,
        }
    }

    pub fn create(&self, input: &SettlementEntityInput) -> EntityResult {
        self.execute_route(ConstructionRoute::Factory, input)
    }

    pub fn reconstruct(&self, input: &SettlementEntityInput) -> EntityResult {
        self.execute_route(ConstructionRoute::DeserializationReconstruction, input)
    }

    pub fn transition(
        &self,
        predecessor: &SettlementEntitySnapshot,
        snapshot_id: &str,
        state_sha256: &str,
    ) -> EntityResult {
        let input = SettlementEntityInput {
            snapshot_id: snapshot_id.to_owned(),
            entity_case_id: predecessor.entity_case_id.clone(),
            sequence: predecessor.sequence + 1,
            predecessor_snapshot_id: Some(predecessor.snapshot_id.clone()),
            organization_id_sha256: predecessor
                .identity
                .organization_id
                .normalized_value_sha256()
                .to_owned(),
            settlement_id_sha256: predecessor
                .identity
                .settlement_id
                .normalized_value_sha256()
                .to_owned(),
            state_sha256: state_sha256.to_owned(),
            owner_matches: true,
            amount_valid: true,
            duplicate_exists: false,
        };
        self.execute_route(ConstructionRoute::LifecycleTransition, &input)
    }

    fn execute_route(
        &self,
        route: ConstructionRoute,
        input: &SettlementEntityInput,
    ) -> EntityResult {
        let mut validator_trace = Vec::new();
        validator_trace.push(trace_entry(BASE_VALIDATORS[0], 1, if input.owner_matches {
            "pass"
        } else {
            "fail"
        }));
        if !input.owner_matches {
            return EntityResult::Invalid(EntityValidationFailure {
                failure_codes: vec!["OWNER_MISMATCH"],
                validator_trace,
            });
        }
        validator_trace.push(trace_entry(BASE_VALIDATORS[1], 2, if input.amount_valid {
            "pass"
        } else {
            "fail"
        }));
        if !input.amount_valid {
            return EntityResult::Invalid(EntityValidationFailure {
                failure_codes: vec!["AMOUNT_INVALID"],
                validator_trace,
            });
        }
        if self.mode == FactoryMode::WithDuplicateBlocked {
            validator_trace.push(trace_entry(EXTENSION_VALIDATORS[2], 3,
                if input.duplicate_exists { "fail" } else { "pass" }));
            if input.duplicate_exists {
                return EntityResult::Invalid(EntityValidationFailure {
                    failure_codes: vec!["DUPLICATE_SETTLEMENT"],
                    validator_trace,
                });
            }
        }
        let identity_resolution_ordinal = validator_trace.len() + 1;
        let identity = SettlementIdentity::resolve(input);
        let construction_ordinal = identity_resolution_ordinal + 1;
        let snapshot = SettlementEntitySnapshot::new(input, identity);
        let immutability_ordinal = construction_ordinal + 1;
        EntityResult::Formed {
            snapshot,
            trace: ConstructionTrace {
                route,
                normalization_ordinal: 0,
                validator_trace,
                identity_resolution_ordinal,
                construction_ordinal,
                immutability_ordinal,
            },
        }
    }
}
