use cal_ontology_lifecycle::{
    AuthorityEffect, AuthorityKindAndPosture, ChallengeContract, ChallengeMode,
    ConfidenceReference, ContextSelector, DefinitionReference, EventFamily, EventStore,
    ExactSemanticEventReference, ForbiddenCollapse as RuntimeForbiddenCollapse, GovernanceEvent,
    GovernanceJoinPolicy, Lifecycle, OntologyGovernanceState, OntologyNodeSemanticState,
    OntologyRelationSemanticState, OntologySemanticState, OntologySubjectIdentity,
    ProjectionProfile, ProvenanceEntry, RelationDirection, SemanticEvent, SourceKind, SubjectKind,
    TypedPropertySet, UseObligation, ZERO_DIGEST, canonical_json as runtime_json,
    seal_governance_event, seal_semantic_event,
};
use cal_ontology_product::{OntologyNode, OntologyRelation, OntologySource, validate_source};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::error::Error;
use std::fmt::{self, Display};
use std::fs;
use std::path::{Path, PathBuf};

pub const BINDING_ID: &str = "cal.binding.ontology-product-lifecycle";
pub const PRODUCT_REF: &str = "CA2-PRODUCT-ONTOLOGY/v1";
pub const COORDINATION_CONTEXT_REF: &str = "cal.coordination-context.ontology-product/v1";
pub const GOVERNANCE_CONTEXT_REF: &str = "cal.context.governance/v2";
pub const ONTOLOGY_LIFECYCLE_CONTEXT_REF: &str = "cal.context.ontology-lifecycle/v2";
pub const CONTEXT_MAP_REF: &str = "cal.context-map.governance-ontology-lifecycle/v2";
pub const ONTOLOGY_ID: &str = "cal.product-ontology.ontology-as-product";

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct BindingError {
    pub code: String,
    pub detail: String,
}

impl BindingError {
    fn new(code: impl Into<String>, detail: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            detail: detail.into(),
        }
    }
}

impl Display for BindingError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}: {}", self.code, self.detail)
    }
}

impl Error for BindingError {}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum ProductLifecycle {
    Active,
    Retired,
    Removed,
}

impl From<ProductLifecycle> for Lifecycle {
    fn from(value: ProductLifecycle) -> Self {
        match value {
            ProductLifecycle::Active => Lifecycle::Active,
            ProductLifecycle::Retired => Lifecycle::Retired,
            ProductLifecycle::Removed => Lifecycle::Removed,
        }
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum ProductChangeBody {
    Node {
        node: OntologyNode,
        lifecycle: ProductLifecycle,
    },
    Relation {
        relation: OntologyRelation,
        lifecycle: ProductLifecycle,
    },
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProductChange {
    pub sequence: u64,
    pub change_id: String,
    pub previous_change_digest: Option<String>,
    pub change_digest: String,
    pub body: ProductChangeBody,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProductNodeObservation {
    pub node_id: String,
    pub type_ref: String,
    pub label: String,
    pub definition_or_claim: String,
    pub scope: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProductRelationObservation {
    pub relation_id: String,
    pub type_ref: String,
    pub source_node_id: String,
    pub target_node_id: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProductObservation {
    pub schema_version: String,
    pub product_ref: String,
    pub cursor: u64,
    pub authority_effect: String,
    pub nodes: Vec<ProductNodeObservation>,
    pub relations: Vec<ProductRelationObservation>,
    pub observation_digest: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProductContextObservation {
    pub schema_version: String,
    pub product_ref: String,
    pub coordination_context_ref: String,
    pub governance_context_ref: String,
    pub ontology_lifecycle_context_ref: String,
    pub context_map_ref: String,
    pub source_cursor: u64,
    pub source_event_set_digest: String,
    pub selected_node_ids: Vec<String>,
    pub selected_relation_ids: Vec<String>,
    pub canonical_replay_source: bool,
    pub authority_effect: String,
}

pub trait ProductEvolutionRuntime {
    fn runtime_id(&self) -> &'static str;
    fn replay(
        &self,
        changes: &[ProductChange],
        target_cursor: u64,
    ) -> Result<ProductObservation, BindingError>;
    fn recover(
        &self,
        changes: &[ProductChange],
        checkpoint_cursor: u64,
        target_cursor: u64,
    ) -> Result<ProductObservation, BindingError>;
}

pub fn sha256(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn change_digest(change: &ProductChange) -> Result<String, BindingError> {
    let mut unsigned = change.clone();
    unsigned.change_digest = ZERO_DIGEST.to_owned();
    serde_json::to_vec(&unsigned)
        .map(|bytes| sha256(&bytes))
        .map_err(|error| BindingError::new("CHANGE_SERIALIZATION_FAILED", error.to_string()))
}

pub fn seal_change(change: &mut ProductChange) -> Result<(), BindingError> {
    change.change_digest = ZERO_DIGEST.to_owned();
    change.change_digest = change_digest(change)?;
    Ok(())
}

pub fn changes_from_source(source: &OntologySource) -> Result<Vec<ProductChange>, BindingError> {
    validate_source(source).map_err(|error| BindingError::new(error.code, error.message))?;
    let mut changes = Vec::new();
    for node in &source.nodes {
        push_change(
            &mut changes,
            ProductChangeBody::Node {
                node: node.clone(),
                lifecycle: ProductLifecycle::Active,
            },
        )?;
    }
    for relation in &source.relations {
        push_change(
            &mut changes,
            ProductChangeBody::Relation {
                relation: relation.clone(),
                lifecycle: ProductLifecycle::Active,
            },
        )?;
    }
    Ok(changes)
}

pub fn push_change(
    changes: &mut Vec<ProductChange>,
    body: ProductChangeBody,
) -> Result<(), BindingError> {
    let sequence = changes.len() as u64 + 1;
    let mut change = ProductChange {
        sequence,
        change_id: format!("product-change-{sequence:04}"),
        previous_change_digest: changes.last().map(|item| item.change_digest.clone()),
        change_digest: ZERO_DIGEST.to_owned(),
        body,
    };
    seal_change(&mut change)?;
    changes.push(change);
    Ok(())
}

fn validate_changes(changes: &[ProductChange], target_cursor: u64) -> Result<(), BindingError> {
    if target_cursor == 0 || target_cursor > changes.len() as u64 {
        return Err(BindingError::new(
            "TARGET_CURSOR_OUT_OF_RANGE",
            target_cursor.to_string(),
        ));
    }
    let mut previous = None;
    let mut ids = BTreeSet::new();
    for (index, change) in changes.iter().take(target_cursor as usize).enumerate() {
        let expected = index as u64 + 1;
        if change.sequence != expected {
            return Err(BindingError::new(
                "CHANGE_SEQUENCE_NOT_CONTIGUOUS",
                format!("expected {expected}; found {}", change.sequence),
            ));
        }
        if change.previous_change_digest != previous {
            return Err(BindingError::new(
                "CHANGE_CHAIN_BROKEN",
                change.change_id.clone(),
            ));
        }
        if !ids.insert(change.change_id.clone()) {
            return Err(BindingError::new(
                "CHANGE_ID_DUPLICATE",
                change.change_id.clone(),
            ));
        }
        if change.change_digest != change_digest(change)? {
            return Err(BindingError::new(
                "CHANGE_DIGEST_MISMATCH",
                change.change_id.clone(),
            ));
        }
        previous = Some(change.change_digest.clone());
    }
    Ok(())
}

#[derive(Default)]
struct ReferenceState {
    nodes: BTreeMap<String, (OntologyNode, ProductLifecycle)>,
    relations: BTreeMap<String, (OntologyRelation, ProductLifecycle)>,
}

fn apply_change(state: &mut ReferenceState, change: &ProductChange) -> Result<(), BindingError> {
    match &change.body {
        ProductChangeBody::Node { node, lifecycle } => {
            if !state.nodes.contains_key(&node.node_id) && *lifecycle != ProductLifecycle::Active {
                return Err(BindingError::new(
                    "LIFECYCLE_TRANSITION_INVALID",
                    node.node_id.clone(),
                ));
            }
            if state
                .nodes
                .get(&node.node_id)
                .is_some_and(|(_, current)| *current == ProductLifecycle::Removed)
            {
                return Err(BindingError::new(
                    "LIFECYCLE_TRANSITION_INVALID",
                    node.node_id.clone(),
                ));
            }
            state
                .nodes
                .insert(node.node_id.clone(), (node.clone(), *lifecycle));
        }
        ProductChangeBody::Relation {
            relation,
            lifecycle,
        } => {
            if !state.relations.contains_key(&relation.relation_id)
                && *lifecycle != ProductLifecycle::Active
            {
                return Err(BindingError::new(
                    "LIFECYCLE_TRANSITION_INVALID",
                    relation.relation_id.clone(),
                ));
            }
            if state
                .relations
                .get(&relation.relation_id)
                .is_some_and(|(_, current)| *current == ProductLifecycle::Removed)
            {
                return Err(BindingError::new(
                    "LIFECYCLE_TRANSITION_INVALID",
                    relation.relation_id.clone(),
                ));
            }
            state
                .relations
                .insert(relation.relation_id.clone(), (relation.clone(), *lifecycle));
        }
    }
    Ok(())
}

fn observation_from_reference(
    state: &ReferenceState,
    cursor: u64,
) -> Result<ProductObservation, BindingError> {
    let nodes = state
        .nodes
        .values()
        .filter(|(_, lifecycle)| *lifecycle == ProductLifecycle::Active)
        .map(|(node, _)| ProductNodeObservation {
            node_id: node.node_id.clone(),
            type_ref: node.type_ref.clone(),
            label: node.label.clone(),
            definition_or_claim: node.definition_or_claim.clone(),
            scope: node.scope.clone(),
        })
        .collect();
    let relations = state
        .relations
        .values()
        .filter(|(_, lifecycle)| *lifecycle == ProductLifecycle::Active)
        .map(|(relation, _)| ProductRelationObservation {
            relation_id: relation.relation_id.clone(),
            type_ref: relation.type_ref.clone(),
            source_node_id: relation.source_node_id.clone(),
            target_node_id: relation.target_node_id.clone(),
        })
        .collect();
    finalize_observation(cursor, nodes, relations)
}

fn finalize_observation(
    cursor: u64,
    mut nodes: Vec<ProductNodeObservation>,
    mut relations: Vec<ProductRelationObservation>,
) -> Result<ProductObservation, BindingError> {
    nodes.sort_by(|left, right| left.node_id.cmp(&right.node_id));
    relations.sort_by(|left, right| left.relation_id.cmp(&right.relation_id));
    let node_ids = nodes
        .iter()
        .map(|node| node.node_id.as_str())
        .collect::<BTreeSet<_>>();
    for relation in &relations {
        if !node_ids.contains(relation.source_node_id.as_str())
            || !node_ids.contains(relation.target_node_id.as_str())
        {
            return Err(BindingError::new(
                "RELATION_ENDPOINT_INTEGRITY",
                relation.relation_id.clone(),
            ));
        }
    }
    let mut observation = ProductObservation {
        schema_version: "cyberalchemy-lab-ontology-product-observation/v1".to_owned(),
        product_ref: PRODUCT_REF.to_owned(),
        cursor,
        authority_effect: "none".to_owned(),
        nodes,
        relations,
        observation_digest: ZERO_DIGEST.to_owned(),
    };
    observation.observation_digest =
        sha256(&serde_json::to_vec(&observation).map_err(|error| {
            BindingError::new("OBSERVATION_SERIALIZATION_FAILED", error.to_string())
        })?);
    Ok(observation)
}

#[derive(Clone, Copy, Debug, Default)]
pub struct ReferenceEvolutionRuntime;

impl ProductEvolutionRuntime for ReferenceEvolutionRuntime {
    fn runtime_id(&self) -> &'static str {
        "cal.runtime.reference-evolution/v1"
    }

    fn replay(
        &self,
        changes: &[ProductChange],
        target_cursor: u64,
    ) -> Result<ProductObservation, BindingError> {
        validate_changes(changes, target_cursor)?;
        let mut state = ReferenceState::default();
        for change in changes.iter().take(target_cursor as usize) {
            apply_change(&mut state, change)?;
        }
        observation_from_reference(&state, target_cursor)
    }

    fn recover(
        &self,
        changes: &[ProductChange],
        checkpoint_cursor: u64,
        target_cursor: u64,
    ) -> Result<ProductObservation, BindingError> {
        validate_changes(changes, target_cursor)?;
        if checkpoint_cursor == 0 || checkpoint_cursor > target_cursor {
            return Err(BindingError::new(
                "CHECKPOINT_CURSOR_INVALID",
                checkpoint_cursor.to_string(),
            ));
        }
        let mut checkpoint = ReferenceState::default();
        for change in changes.iter().take(checkpoint_cursor as usize) {
            apply_change(&mut checkpoint, change)?;
        }
        for change in changes
            .iter()
            .skip(checkpoint_cursor as usize)
            .take((target_cursor - checkpoint_cursor) as usize)
        {
            apply_change(&mut checkpoint, change)?;
        }
        observation_from_reference(&checkpoint, target_cursor)
    }
}

#[derive(Clone, Debug)]
pub struct LifecycleRuntimeBinding {
    runtime_root: PathBuf,
}

impl LifecycleRuntimeBinding {
    pub fn new(runtime_root: impl Into<PathBuf>) -> Self {
        Self {
            runtime_root: runtime_root.into(),
        }
    }

    fn materialize(
        &self,
        changes: &[ProductChange],
        target_cursor: u64,
    ) -> Result<EventStore, BindingError> {
        validate_changes(changes, target_cursor)?;
        if self.runtime_root.exists()
            && fs::read_dir(&self.runtime_root)
                .map_err(io_error)?
                .next()
                .is_some()
        {
            return Err(BindingError::new(
                "RUNTIME_ROOT_NOT_EMPTY",
                self.runtime_root.display().to_string(),
            ));
        }
        let semantic_dir = self.runtime_root.join("semantic-events");
        let governance_dir = self.runtime_root.join("governance-events");
        fs::create_dir_all(&semantic_dir).map_err(io_error)?;
        fs::create_dir_all(&governance_dir).map_err(io_error)?;
        let mut semantic_previous = BTreeMap::<String, String>::new();
        let mut governance_previous = BTreeMap::<String, String>::new();
        for change in changes.iter().take(target_cursor as usize) {
            let identity = runtime_identity(&change.body);
            let stream = identity.semantic_stream_id();
            let mut semantic = SemanticEvent {
                source_kind: SourceKind::CanonicalEvent,
                event_family: EventFamily::Semantic,
                event_id: format!("l3-semantic-{:04}", change.sequence),
                event_digest: ZERO_DIGEST.to_owned(),
                stream_id: stream.clone(),
                subject_identity: identity.clone(),
                previous_event_digest: semantic_previous.get(&stream).cloned(),
                semantic_cursor: change.sequence,
                complete_resulting_semantic_state: runtime_state(&change.body),
            };
            seal_semantic_event(&mut semantic).map_err(runtime_error)?;
            semantic_previous.insert(stream, semantic.event_digest.clone());
            write_runtime_event(
                &semantic_dir,
                change.sequence,
                &semantic.event_id,
                &semantic,
            )?;

            let reference = ExactSemanticEventReference {
                semantic_event_id: semantic.event_id.clone(),
                semantic_event_digest: semantic.event_digest.clone(),
                semantic_cursor: semantic.semantic_cursor,
            };
            let governance_stream = identity.governance_stream_id();
            let mut governance = GovernanceEvent {
                source_kind: SourceKind::CanonicalEvent,
                event_family: EventFamily::Governance,
                event_id: format!("l3-governance-{:04}", change.sequence),
                event_digest: ZERO_DIGEST.to_owned(),
                stream_id: governance_stream.clone(),
                semantic_ref: reference.clone(),
                governance_cursor: change.sequence,
                previous_event_digest: governance_previous.get(&governance_stream).cloned(),
                complete_resulting_governance_state: governance_state(reference),
            };
            seal_governance_event(&mut governance).map_err(runtime_error)?;
            governance_previous.insert(governance_stream, governance.event_digest.clone());
            write_runtime_event(
                &governance_dir,
                change.sequence,
                &governance.event_id,
                &governance,
            )?;
        }
        EventStore::load(&semantic_dir, &governance_dir).map_err(runtime_error)
    }

    pub fn context_observation(
        &self,
        changes: &[ProductChange],
        target_cursor: u64,
    ) -> Result<ProductContextObservation, BindingError> {
        let store = self.materialize(changes, target_cursor)?;
        let cut = store.ontology_at(target_cursor).map_err(runtime_error)?;
        let selector = ContextSelector {
            semantic_cursor: target_cursor,
            required_subject_set: cut
                .subjects
                .iter()
                .map(|subject| subject.identity.clone())
                .collect(),
            governance_join_policy: GovernanceJoinPolicy::RequireExact,
            intended_use: "ontology-product-l3-context-observation".to_owned(),
            projection_profile: ProjectionProfile::TestCompleteV1,
        };
        let projection = store
            .context_projection("ontology-product-l3-selector", &selector)
            .map_err(runtime_error)?;
        Ok(ProductContextObservation {
            schema_version: "cyberalchemy-lab-ontology-product-context-observation/v1".to_owned(),
            product_ref: PRODUCT_REF.to_owned(),
            coordination_context_ref: COORDINATION_CONTEXT_REF.to_owned(),
            governance_context_ref: GOVERNANCE_CONTEXT_REF.to_owned(),
            ontology_lifecycle_context_ref: ONTOLOGY_LIFECYCLE_CONTEXT_REF.to_owned(),
            context_map_ref: CONTEXT_MAP_REF.to_owned(),
            source_cursor: projection.source_cursor,
            source_event_set_digest: projection.source_event_set_digest,
            selected_node_ids: projection.selected_node_ids,
            selected_relation_ids: projection.selected_relation_ids,
            canonical_replay_source: false,
            authority_effect: "none".to_owned(),
        })
    }
}

impl ProductEvolutionRuntime for LifecycleRuntimeBinding {
    fn runtime_id(&self) -> &'static str {
        "cal.runtime.ontology-lifecycle-rust/v1"
    }

    fn replay(
        &self,
        changes: &[ProductChange],
        target_cursor: u64,
    ) -> Result<ProductObservation, BindingError> {
        let store = self.materialize(changes, target_cursor)?;
        observation_from_cut(
            &store.ontology_at(target_cursor).map_err(runtime_error)?,
            changes,
        )
    }

    fn recover(
        &self,
        changes: &[ProductChange],
        checkpoint_cursor: u64,
        target_cursor: u64,
    ) -> Result<ProductObservation, BindingError> {
        if checkpoint_cursor == 0 || checkpoint_cursor > target_cursor {
            return Err(BindingError::new(
                "CHECKPOINT_CURSOR_INVALID",
                checkpoint_cursor.to_string(),
            ));
        }
        let store = self.materialize(changes, target_cursor)?;
        let checkpoint = store
            .checkpoint_at(checkpoint_cursor)
            .map_err(runtime_error)?;
        observation_from_cut(
            &store
                .ontology_from_checkpoint(&checkpoint, target_cursor)
                .map_err(runtime_error)?,
            changes,
        )
    }
}

fn runtime_identity(body: &ProductChangeBody) -> OntologySubjectIdentity {
    match body {
        ProductChangeBody::Node { node, .. } => OntologySubjectIdentity {
            subject_id: node.node_id.clone(),
            ontology_id: ONTOLOGY_ID.to_owned(),
            subject_kind: SubjectKind::Node,
            type_ref: runtime_type_ref(&node.type_ref),
        },
        ProductChangeBody::Relation { relation, .. } => OntologySubjectIdentity {
            subject_id: relation.relation_id.clone(),
            ontology_id: ONTOLOGY_ID.to_owned(),
            subject_kind: SubjectKind::Relation,
            type_ref: runtime_type_ref(&relation.type_ref),
        },
    }
}

fn runtime_state(body: &ProductChangeBody) -> OntologySemanticState {
    let properties = || TypedPropertySet {
        profile_ref: "test-empty-profile/v1".to_owned(),
        values: BTreeMap::new(),
    };
    match body {
        ProductChangeBody::Node { node, lifecycle } => {
            let definitions = node
                .source_refs
                .iter()
                .map(|reference| DefinitionReference {
                    definition_id: reference.source_id.clone(),
                    selector_sha256: sha256(reference.selector.as_bytes()),
                })
                .collect();
            let obligations = node
                .use_obligations
                .iter()
                .enumerate()
                .map(|(index, requirement)| UseObligation {
                    obligation_id: format!("use-obligation-{:04}", index + 1),
                    requirement: requirement.clone(),
                    applies_to_use: "ontology-product".to_owned(),
                })
                .collect();
            let forbidden = node
                .forbidden_collapse
                .iter()
                .map(|item| RuntimeForbiddenCollapse {
                    left_ref: item.left_ref.clone(),
                    right_ref: item.right_ref.clone(),
                    context: item.reason.clone(),
                    intended_use: "ontology-product".to_owned(),
                })
                .collect();
            OntologySemanticState::Node(OntologyNodeSemanticState {
                identity: runtime_identity(body),
                lifecycle: (*lifecycle).into(),
                label: node.label.clone(),
                definition_or_claim: node.definition_or_claim.clone(),
                scope: node.scope.clone(),
                semantic_components: vec![],
                semantic_definition_refs: definitions,
                typed_properties: properties(),
                use_obligations: obligations,
                forbidden_collapse: forbidden,
                profile_ref: "test-empty-profile/v1".to_owned(),
            })
        }
        ProductChangeBody::Relation {
            relation,
            lifecycle,
        } => {
            let forbidden = relation
                .forbidden_collapse
                .iter()
                .map(|item| RuntimeForbiddenCollapse {
                    left_ref: item.left_ref.clone(),
                    right_ref: item.right_ref.clone(),
                    context: item.reason.clone(),
                    intended_use: "ontology-product".to_owned(),
                })
                .collect();
            OntologySemanticState::Relation(OntologyRelationSemanticState {
                identity: runtime_identity(body),
                lifecycle: (*lifecycle).into(),
                source_node_id: relation.source_node_id.clone(),
                target_node_id: relation.target_node_id.clone(),
                direction: RelationDirection::Directed,
                typed_properties: properties(),
                forbidden_collapse: forbidden,
            })
        }
    }
}

fn governance_state(reference: ExactSemanticEventReference) -> OntologyGovernanceState {
    OntologyGovernanceState {
        semantic_ref: reference,
        provenance: vec![ProvenanceEntry {
            source_ref: BINDING_ID.to_owned(),
            relation: "calculated-by".to_owned(),
            operation: "l3-product-test".to_owned(),
            owner_route: "CA2-ROUTE-IMPLEMENT".to_owned(),
            posture: "test-candidate".to_owned(),
        }],
        owner_route: "role:ontology-product-owner".to_owned(),
        candidate_or_maturity_status: "test-candidate".to_owned(),
        promotion_state_or_handle: "not-promoted".to_owned(),
        authority_kind_and_posture: AuthorityKindAndPosture {
            kind: "candidate".to_owned(),
            posture: "non-authoritative".to_owned(),
        },
        authority_effect: AuthorityEffect::None,
        evidence_confidence: ConfidenceReference {
            scheme_ref: "product-test/v1".to_owned(),
            level: "supported".to_owned(),
        },
        commitment_confidence: ConfidenceReference {
            scheme_ref: "product-test/v1".to_owned(),
            level: "experimental".to_owned(),
        },
        challenge_contract: ChallengeContract {
            challenge_response: "Route challenges to the Ontology Product owner.".to_owned(),
            valid_challenge_modes: vec![
                ChallengeMode::Evidence,
                ChallengeMode::Contradiction,
                ChallengeMode::OwnerReview,
            ],
            contradiction_edges: vec![],
            validation_edges: vec![],
            owner_route: "role:ontology-product-owner".to_owned(),
            resolution_gate: "L3-PRODUCT-TEST".to_owned(),
            blocking_questions: vec![],
            challenge_residue_route: "role:ontology-product-owner".to_owned(),
        },
        residue: vec![],
        conflicts: vec![],
        drift_owner: "role:ontology-product-owner".to_owned(),
        invalidation_route: "role:ontology-product-owner".to_owned(),
    }
}

fn observation_from_cut(
    cut: &cal_ontology_lifecycle::ConsistentOntologyCut,
    changes: &[ProductChange],
) -> Result<ProductObservation, BindingError> {
    let mut product_types = BTreeMap::<(SubjectKind, String), String>::new();
    for change in changes.iter().take(cut.semantic_cursor as usize) {
        match &change.body {
            ProductChangeBody::Node { node, .. } => {
                product_types.insert(
                    (SubjectKind::Node, node.node_id.clone()),
                    node.type_ref.clone(),
                );
            }
            ProductChangeBody::Relation { relation, .. } => {
                product_types.insert(
                    (SubjectKind::Relation, relation.relation_id.clone()),
                    relation.type_ref.clone(),
                );
            }
        }
    }
    let mut nodes = Vec::new();
    let mut relations = Vec::new();
    for subject in &cut.subjects {
        match &subject.semantic_state {
            OntologySemanticState::Node(node) => nodes.push(ProductNodeObservation {
                node_id: node.identity.subject_id.clone(),
                type_ref: product_types
                    .get(&(SubjectKind::Node, node.identity.subject_id.clone()))
                    .ok_or_else(|| {
                        BindingError::new(
                            "PRODUCT_TYPE_BINDING_MISSING",
                            node.identity.subject_id.clone(),
                        )
                    })?
                    .clone(),
                label: node.label.clone(),
                definition_or_claim: node.definition_or_claim.clone(),
                scope: node.scope.clone(),
            }),
            OntologySemanticState::Relation(relation) => {
                relations.push(ProductRelationObservation {
                    relation_id: relation.identity.subject_id.clone(),
                    type_ref: product_types
                        .get(&(SubjectKind::Relation, relation.identity.subject_id.clone()))
                        .ok_or_else(|| {
                            BindingError::new(
                                "PRODUCT_TYPE_BINDING_MISSING",
                                relation.identity.subject_id.clone(),
                            )
                        })?
                        .clone(),
                    source_node_id: relation.source_node_id.clone(),
                    target_node_id: relation.target_node_id.clone(),
                })
            }
        }
    }
    finalize_observation(cut.semantic_cursor, nodes, relations)
}

fn runtime_type_ref(product_type_ref: &str) -> String {
    format!("product-type:{}", sha256(product_type_ref.as_bytes()))
}

fn write_runtime_event<T: Serialize>(
    directory: &Path,
    cursor: u64,
    event_id: &str,
    event: &T,
) -> Result<(), BindingError> {
    let path = directory.join(format!("{cursor:08}-{event_id}.json"));
    fs::write(path, runtime_json(event).map_err(runtime_error)?).map_err(io_error)
}

fn runtime_error(error: cal_ontology_lifecycle::ReplayFailure) -> BindingError {
    BindingError::new(error.code, error.detail)
}
fn io_error(error: std::io::Error) -> BindingError {
    BindingError::new("RUNTIME_IO_FAILED", error.to_string())
}
