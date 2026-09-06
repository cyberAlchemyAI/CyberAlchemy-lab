use cal_ontology_lifecycle::{
    AppendGovernanceEventRequest, AppendSemanticEventRequest, AuthorityEffect,
    AuthorityKindAndPosture, ChallengeContract, ChallengeMode, ConfidenceReference,
    ContextProjection, ContextSelector, DefinitionReference, EventFamily, EventStore,
    ExactSemanticEventReference, ForbiddenCollapse, GovernanceEvent, GovernanceJoinPolicy,
    LatestSubjectSnapshot, Lifecycle, OntologyGovernanceState, OntologyNodeSemanticState,
    OntologyRelationSemanticState, OntologySemanticState, OntologySubjectIdentity,
    ProjectionProfile, ProvenanceEntry, RelationDirection, ReplayFailure, SemanticEvent,
    SourceKind, SubjectKind, TypedPropertySet, TypedResidue, UseObligation, ZERO_DIGEST,
    canonical_json, seal_governance_event, seal_semantic_event,
};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::error::Error;
use std::fmt::{self, Display};
use std::fs;
use std::path::{Path, PathBuf};

pub const BINDING_ID: &str = "cal.binding.ontology-product-event-runtime/v2";
pub const PROJECTION_ID: &str = "cal.ontology-navigation.lab-cohesion";
pub const ONTOLOGY_ID: &str = "cal.ontology-system.lab-cohesion";
pub const ROOT_COMPONENT_ID: &str = "CAL-LAB-ONTOLOGY-SYSTEM";
pub const NAVIGATION_SHA256: &str =
    "e0738fd8083202fd96be9a6817ef0afe2f760ab0d40f6c5565f31e48c941d2e1";
pub const ROOT_DECISION_SHA256: &str =
    "b3d6b5b07ecb029b8ce39d0c084c107d004f1e019ac5801eceb95011558e35b8";
pub const RUNTIME_SOURCE_SHA256: &str =
    "f1b3f7cf463ebcc6e7b887b374d75adeac29ba38acfec3bafacfe4d3159f3a7b";
pub const EVENT_CONTRACT_SHA256: &str =
    "81d3436d0fc49f1c626ba17b00726f5a7bb007c0fe5b3f238aeb657b932b3167";
pub const INITIAL_CUT_SHA256: &str =
    "39911b9d29adeaca90bb777881c1c99fa2ea7e47cf22410b99c7562232d15db7";
pub const INITIAL_SEMANTIC_EVENT_SET_SHA256: &str =
    "1f6b187ed7c729b940b54f8e4418f94ad11585a4a425e7ef8abb9c5c29c1b991";
pub const INITIAL_GOVERNANCE_EVENT_SET_SHA256: &str =
    "5cf7d5686c1095cb5f590a381bf2dff24fd50884b51aced0518b4e512ef0af3b";

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RealizationError {
    pub code: String,
    pub detail: String,
}

impl RealizationError {
    fn new(code: impl Into<String>, detail: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            detail: detail.into(),
        }
    }
}

impl Display for RealizationError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}: {}", self.code, self.detail)
    }
}

impl Error for RealizationError {}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct AuthorityBinding {
    pub decision_id: String,
    pub decision_path: String,
    pub decision_sha256: String,
    pub validation_path: String,
    pub validation_sha256: String,
    pub validation_result: String,
    pub stage_state: String,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct NavigationRoot {
    pub component_id: String,
    pub system_id: String,
    pub admission_state: String,
    pub navigation_authority: bool,
    pub composition_overlay_authority: bool,
    pub source_model_path: String,
    pub source_model_sha256: String,
    pub replay_source: bool,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct NavigationComponent {
    pub component_id: String,
    pub kind: String,
    pub branch: String,
    pub source_authority_state: String,
    pub effective_authority_state: String,
    pub owner_route: String,
    pub source_refs: Vec<String>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct NavigationRelation {
    pub relation_id: String,
    pub r#type: String,
    pub source: String,
    pub target: String,
    pub source_status: String,
    pub effective_status: String,
    pub source_refs: Vec<String>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct ResidueRoute {
    pub residue_id: String,
    pub status: String,
    pub statement: String,
    pub owner_route: String,
    pub next_action: String,
    pub route_id: String,
    pub lane: String,
    pub affected_stage: String,
    pub route_status: String,
    pub authority_effect: String,
    #[serde(default)]
    pub review_route_count: Option<usize>,
    #[serde(default)]
    pub resolved_owner_route_count: Option<usize>,
    #[serde(default)]
    pub unresolved_owner_route_count: Option<usize>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct ReviewRoute {
    pub route_id: String,
    pub group_id: String,
    pub owner_route: String,
    pub owner_resolution_route: Option<String>,
    pub route_status: String,
    pub blocker_count: usize,
    pub source_profiles: Vec<String>,
    pub recommended_disposition: String,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct NavigationProjection {
    pub schema_version: String,
    pub projection_id: String,
    pub version: String,
    pub status: String,
    pub ontology_type: String,
    pub authority_effect: String,
    pub authority_binding: AuthorityBinding,
    pub root: NavigationRoot,
    pub components: Vec<NavigationComponent>,
    pub relations: Vec<NavigationRelation>,
    pub residue_routes: Vec<ResidueRoute>,
    pub review_routes: Vec<ReviewRoute>,
    pub canonical_truth_contract: serde_json::Value,
    pub query_contract: serde_json::Value,
    pub source_direction: serde_json::Value,
    pub work_lanes: serde_json::Value,
    pub claim_ceiling: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct IntegrationEpochEvent {
    pub schema_version: String,
    pub event_type: String,
    pub epoch_id: String,
    pub event_digest: String,
    pub navigation_sha256: String,
    pub root_decision_sha256: String,
    pub runtime_source_sha256: String,
    pub event_contract_sha256: String,
    pub initial_cut_sha256: String,
    pub initial_semantic_event_set_sha256: String,
    pub initial_governance_event_set_sha256: String,
    pub semantic_event_count: usize,
    pub governance_event_count: usize,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct RealizationObservation {
    pub schema_version: String,
    pub binding_id: String,
    pub projection_id: String,
    pub root_component_id: String,
    pub root_admission_preserved: bool,
    pub semantic_cursor: u64,
    pub semantic_event_count: usize,
    pub governance_event_count: usize,
    pub latest_snapshot_count: usize,
    pub node_count: usize,
    pub relation_count: usize,
    pub residue_route_count: usize,
    pub unresolved_review_owner_count: usize,
    pub source_event_set_digest: String,
    pub latest_snapshot_set_digest: String,
    pub context_projection_digest: String,
    pub integration_epoch_digest: String,
    pub child_ontologies_admitted_by_binding: usize,
    pub canonical_replay_source_is_event_history: bool,
    pub authority_effect: String,
}

pub struct MaterializedRuntime {
    pub store: EventStore,
    pub root: PathBuf,
    pub epoch: IntegrationEpochEvent,
}

pub fn sha256(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

pub fn parse_navigation(bytes: &[u8]) -> Result<NavigationProjection, RealizationError> {
    if sha256(bytes) != NAVIGATION_SHA256 {
        return Err(RealizationError::new(
            "NAVIGATION_DIGEST_MISMATCH",
            sha256(bytes),
        ));
    }
    let navigation: NavigationProjection = serde_json::from_slice(bytes)
        .map_err(|error| RealizationError::new("NAVIGATION_DECODE_FAILED", error.to_string()))?;
    validate_navigation(&navigation)?;
    Ok(navigation)
}

pub fn validate_navigation(navigation: &NavigationProjection) -> Result<(), RealizationError> {
    if navigation.schema_version != "cyberalchemy-lab-admitted-ontology-navigation/v1"
        || navigation.projection_id != PROJECTION_ID
        || navigation.status != "derived-from-admitted-root"
        || navigation.ontology_type != "business-system-bridge"
        || navigation.authority_effect != "none"
    {
        return Err(RealizationError::new(
            "NAVIGATION_IDENTITY_MISMATCH",
            &navigation.projection_id,
        ));
    }
    if navigation.authority_binding.decision_sha256 != ROOT_DECISION_SHA256
        || navigation.authority_binding.validation_result != "PASS"
        || navigation.authority_binding.stage_state != "ROOT_ADMITTED"
        || navigation.authority_binding.authority_effect != "root-admission-only"
    {
        return Err(RealizationError::new(
            "ROOT_ADMISSION_BINDING_MISMATCH",
            &navigation.authority_binding.decision_id,
        ));
    }
    if navigation.root.component_id != ROOT_COMPONENT_ID
        || navigation.root.system_id != ONTOLOGY_ID
        || navigation.root.admission_state != "admitted"
        || !navigation.root.navigation_authority
        || !navigation.root.composition_overlay_authority
        || navigation.root.replay_source
    {
        return Err(RealizationError::new(
            "ROOT_ADMISSION_STATE_MISMATCH",
            &navigation.root.component_id,
        ));
    }
    if navigation.components.len() != 14 || navigation.relations.len() != 15 {
        return Err(RealizationError::new(
            "GRAPH_COUNT_MISMATCH",
            format!(
                "{}/{}",
                navigation.components.len(),
                navigation.relations.len()
            ),
        ));
    }
    let component_ids = navigation
        .components
        .iter()
        .map(|item| item.component_id.as_str())
        .collect::<BTreeSet<_>>();
    if component_ids.len() != navigation.components.len() {
        return Err(RealizationError::new(
            "COMPONENT_ID_DUPLICATE",
            "navigation",
        ));
    }
    for component in &navigation.components {
        let expected = if component.component_id == ROOT_COMPONENT_ID {
            "admitted-root"
        } else {
            &component.source_authority_state
        };
        if component.effective_authority_state != expected {
            return Err(RealizationError::new(
                "CHILD_AUTHORITY_STATE_CHANGED",
                &component.component_id,
            ));
        }
        if component.owner_route.is_empty() || component.source_refs.is_empty() {
            return Err(RealizationError::new(
                "COMPONENT_ROUTE_OR_SOURCE_MISSING",
                &component.component_id,
            ));
        }
    }
    let relation_ids = navigation
        .relations
        .iter()
        .map(|item| item.relation_id.as_str())
        .collect::<BTreeSet<_>>();
    if relation_ids.len() != navigation.relations.len() {
        return Err(RealizationError::new("RELATION_ID_DUPLICATE", "navigation"));
    }
    for relation in &navigation.relations {
        if !component_ids.contains(relation.source.as_str())
            || !component_ids.contains(relation.target.as_str())
        {
            return Err(RealizationError::new(
                "RELATION_ENDPOINT_MISSING",
                &relation.relation_id,
            ));
        }
        if relation.effective_status != "admitted-composition-overlay"
            || relation.source_refs.is_empty()
        {
            return Err(RealizationError::new(
                "RELATION_ADMISSION_STATE_MISMATCH",
                &relation.relation_id,
            ));
        }
    }
    if navigation.residue_routes.len() != 5 || navigation.review_routes.len() != 10 {
        return Err(RealizationError::new(
            "RESIDUE_OR_REVIEW_ROUTE_COUNT_MISMATCH",
            "navigation",
        ));
    }
    if navigation.residue_routes.iter().any(|item| {
        item.owner_route.is_empty() || item.route_id.is_empty() || item.authority_effect != "none"
    }) {
        return Err(RealizationError::new("RESIDUE_ROUTE_INVALID", "navigation"));
    }
    let collision = navigation
        .residue_routes
        .iter()
        .find(|item| item.residue_id == "CAL-RES-DOMAINSPEC-SUCCESSOR-COLLISION")
        .ok_or_else(|| {
            RealizationError::new("DOMAINSPEC_COLLISION_RESIDUE_MISSING", "navigation")
        })?;
    if !collision
        .statement
        .contains("Eleven profile-qualified packages")
    {
        return Err(RealizationError::new(
            "DOMAINSPEC_COLLISION_COLLAPSED",
            &collision.statement,
        ));
    }
    let unresolved = navigation
        .review_routes
        .iter()
        .filter(|item| item.route_status == "blocked-owner-unresolved")
        .count();
    if unresolved != 2
        || navigation
            .review_routes
            .iter()
            .any(|item| item.authority_effect != "none" || item.blocker_count == 0)
    {
        return Err(RealizationError::new(
            "REVIEW_ROUTE_CLOSURE_MISMATCH",
            unresolved.to_string(),
        ));
    }
    Ok(())
}

pub fn realize_navigation(
    bytes: &[u8],
    runtime_root: impl Into<PathBuf>,
) -> Result<MaterializedRuntime, RealizationError> {
    let navigation = parse_navigation(bytes)?;
    let runtime_root = runtime_root.into();
    if runtime_root.exists()
        && fs::read_dir(&runtime_root)
            .map_err(io_error)?
            .next()
            .is_some()
    {
        return Err(RealizationError::new(
            "RUNTIME_ROOT_NOT_EMPTY",
            runtime_root.display().to_string(),
        ));
    }
    let semantic_directory = runtime_root.join("semantic-events");
    let governance_directory = runtime_root.join("governance-events");
    let integration_directory = runtime_root.join("integration-events");
    fs::create_dir_all(&semantic_directory).map_err(io_error)?;
    fs::create_dir_all(&governance_directory).map_err(io_error)?;
    fs::create_dir_all(&integration_directory).map_err(io_error)?;

    let mut cursor = 0_u64;
    for component in &navigation.components {
        cursor += 1;
        write_pair(
            &semantic_directory,
            &governance_directory,
            cursor,
            node_state(component),
            &component.owner_route,
            &component.effective_authority_state,
            if component.component_id == ROOT_COMPONENT_ID {
                navigation
                    .residue_routes
                    .iter()
                    .map(runtime_residue)
                    .collect()
            } else {
                vec![]
            },
        )?;
    }
    for relation in &navigation.relations {
        cursor += 1;
        write_pair(
            &semantic_directory,
            &governance_directory,
            cursor,
            relation_state(relation),
            "CyberAlchemy Lab ontology-system owner",
            &relation.effective_status,
            vec![],
        )?;
    }
    let store =
        EventStore::load(&semantic_directory, &governance_directory).map_err(runtime_error)?;
    validate_initial_cut(&store)?;
    let epoch = build_epoch(cursor as usize);
    let epoch_path =
        integration_directory.join("00000001-ontology-product-realization-epoch-0001.json");
    fs::write(&epoch_path, canonical_epoch(&epoch)?).map_err(io_error)?;
    validate_epoch(&epoch)?;
    let runtime = MaterializedRuntime {
        store,
        root: runtime_root,
        epoch,
    };
    runtime.observation()?;
    Ok(runtime)
}

pub fn load_realized_runtime(
    runtime_root: impl Into<PathBuf>,
) -> Result<MaterializedRuntime, RealizationError> {
    let root = runtime_root.into();
    let epoch_path =
        root.join("integration-events/00000001-ontology-product-realization-epoch-0001.json");
    let bytes = fs::read(&epoch_path)
        .map_err(|error| RealizationError::new("INTEGRATION_EPOCH_MISSING", error.to_string()))?;
    let epoch: IntegrationEpochEvent = serde_json::from_slice(&bytes).map_err(|error| {
        RealizationError::new("INTEGRATION_EPOCH_DECODE_FAILED", error.to_string())
    })?;
    if bytes != canonical_epoch(&epoch)?.as_bytes() {
        return Err(RealizationError::new(
            "INTEGRATION_EPOCH_NONCANONICAL",
            epoch_path.display().to_string(),
        ));
    }
    validate_epoch(&epoch)?;
    let store = EventStore::load(root.join("semantic-events"), root.join("governance-events"))
        .map_err(runtime_error)?;
    if store.semantic_events().len() < epoch.semantic_event_count
        || store.governance_events().len() < epoch.governance_event_count
    {
        return Err(RealizationError::new(
            "INTEGRATION_EPOCH_EVENT_COUNT_MISMATCH",
            "runtime",
        ));
    }
    validate_initial_cut(&store)?;
    Ok(MaterializedRuntime { store, root, epoch })
}

impl MaterializedRuntime {
    pub fn latest_snapshots(&self) -> Result<Vec<LatestSubjectSnapshot>, RealizationError> {
        let cursor = self.store.semantic_events().len() as u64;
        self.store
            .latest_subject_snapshots(cursor)
            .map_err(runtime_error)
    }

    pub fn context_projection(&self) -> Result<ContextProjection, RealizationError> {
        let cursor = self.store.semantic_events().len() as u64;
        let cut = self.store.ontology_at(cursor).map_err(runtime_error)?;
        let selector = ContextSelector {
            semantic_cursor: cursor,
            required_subject_set: cut
                .subjects
                .iter()
                .map(|item| item.identity.clone())
                .collect(),
            governance_join_policy: GovernanceJoinPolicy::RequireExact,
            intended_use: "cohesive-lab-ontology-navigation".to_owned(),
            projection_profile: ProjectionProfile::TestCompleteV1,
        };
        self.store
            .context_projection("cohesive-lab-root-selector", &selector)
            .map_err(runtime_error)
    }

    pub fn observation(&self) -> Result<RealizationObservation, RealizationError> {
        let cursor = self.store.semantic_events().len() as u64;
        let cut = self.store.ontology_at(cursor).map_err(runtime_error)?;
        let snapshots = self.latest_snapshots()?;
        let context = self.context_projection()?;
        let node_count = cut
            .subjects
            .iter()
            .filter(|item| item.identity.subject_kind == SubjectKind::Node)
            .count();
        let relation_count = cut
            .subjects
            .iter()
            .filter(|item| item.identity.subject_kind == SubjectKind::Relation)
            .count();
        Ok(RealizationObservation {
            schema_version: "cyberalchemy-lab-ontology-product-event-runtime-observation/v1"
                .to_owned(),
            binding_id: BINDING_ID.to_owned(),
            projection_id: PROJECTION_ID.to_owned(),
            root_component_id: ROOT_COMPONENT_ID.to_owned(),
            root_admission_preserved: true,
            semantic_cursor: cursor,
            semantic_event_count: self.store.semantic_events().len(),
            governance_event_count: self.store.governance_events().len(),
            latest_snapshot_count: snapshots.len(),
            node_count,
            relation_count,
            residue_route_count: 5,
            unresolved_review_owner_count: 2,
            source_event_set_digest: cut.source_event_set_digest,
            latest_snapshot_set_digest: digest_serialized(&snapshots)?,
            context_projection_digest: digest_serialized(&context)?,
            integration_epoch_digest: self.epoch.event_digest.clone(),
            child_ontologies_admitted_by_binding: 0,
            canonical_replay_source_is_event_history: true,
            authority_effect: "none".to_owned(),
        })
    }

    pub fn append_root_refresh(
        &mut self,
        component: &NavigationComponent,
        revision: &str,
    ) -> Result<(), RealizationError> {
        if component.component_id != ROOT_COMPONENT_ID {
            return Err(RealizationError::new(
                "ROOT_REFRESH_SUBJECT_MISMATCH",
                &component.component_id,
            ));
        }
        let cursor = self.store.semantic_events().len() as u64 + 1;
        let mut state = node_state(component);
        if let OntologySemanticState::Node(node) = &mut state {
            node.scope = format!("{}; revision={revision}", node.scope);
        }
        let identity = state.identity().clone();
        let stream_id = identity.semantic_stream_id();
        let semantic_version = self
            .store
            .semantic_events()
            .iter()
            .filter(|item| item.event.stream_id == stream_id)
            .count() as u64;
        let previous = self
            .store
            .semantic_events()
            .iter()
            .rev()
            .find(|item| item.event.stream_id == stream_id)
            .map(|item| item.event.event_digest.clone());
        let mut semantic = SemanticEvent {
            source_kind: SourceKind::CanonicalEvent,
            event_family: EventFamily::Semantic,
            event_id: format!("cohesive-semantic-refresh-{cursor:04}"),
            event_digest: ZERO_DIGEST.to_owned(),
            stream_id: stream_id.clone(),
            subject_identity: identity.clone(),
            previous_event_digest: previous,
            semantic_cursor: cursor,
            complete_resulting_semantic_state: state,
        };
        seal_semantic_event(&mut semantic).map_err(runtime_error)?;
        let semantic_ref = semantic_reference(&semantic);
        self.store
            .append_semantic_batch(
                self.root.join("semantic-events"),
                vec![AppendSemanticEventRequest {
                    expected_stream_version: semantic_version,
                    event: semantic,
                }],
            )
            .map_err(runtime_error)?;

        let governance_stream = identity.governance_stream_id();
        let governance_version = self
            .store
            .governance_events()
            .iter()
            .filter(|item| item.event.stream_id == governance_stream)
            .count() as u64;
        let previous_governance = self
            .store
            .governance_events()
            .iter()
            .rev()
            .find(|item| item.event.stream_id == governance_stream)
            .map(|item| item.event.event_digest.clone());
        let mut governance = GovernanceEvent {
            source_kind: SourceKind::CanonicalEvent,
            event_family: EventFamily::Governance,
            event_id: format!("cohesive-governance-refresh-{cursor:04}"),
            event_digest: ZERO_DIGEST.to_owned(),
            stream_id: governance_stream,
            semantic_ref: semantic_ref.clone(),
            governance_cursor: cursor,
            previous_event_digest: previous_governance,
            complete_resulting_governance_state: governance_state(
                semantic_ref,
                &component.owner_route,
                &component.effective_authority_state,
                vec![],
            ),
        };
        seal_governance_event(&mut governance).map_err(runtime_error)?;
        self.store
            .append_governance_batch(
                self.root.join("governance-events"),
                vec![AppendGovernanceEventRequest {
                    expected_stream_version: governance_version,
                    event: governance,
                }],
            )
            .map_err(runtime_error)?;
        Ok(())
    }
}

fn node_state(component: &NavigationComponent) -> OntologySemanticState {
    let identity = OntologySubjectIdentity {
        subject_id: component.component_id.clone(),
        ontology_id: ONTOLOGY_ID.to_owned(),
        subject_kind: SubjectKind::Node,
        type_ref: format!("cal.cohesive-component.{}", component.kind),
    };
    OntologySemanticState::Node(OntologyNodeSemanticState {
        identity,
        lifecycle: Lifecycle::Active,
        label: component.component_id.clone(),
        definition_or_claim: format!(
            "{} component in the admitted cohesive ontology navigation graph",
            component.kind
        ),
        scope: format!(
            "branch={}; source_state={}; effective_state={}; owner={}",
            component.branch,
            component.source_authority_state,
            component.effective_authority_state,
            component.owner_route
        ),
        semantic_components: vec![],
        semantic_definition_refs: component.source_refs.iter().map(definition_ref).collect(),
        typed_properties: empty_properties(),
        use_obligations: vec![UseObligation {
            obligation_id: format!(
                "preserve-owner-{}",
                sha256(component.component_id.as_bytes())
            ),
            requirement: format!(
                "Preserve owner route {} and authority state {}.",
                component.owner_route, component.effective_authority_state
            ),
            applies_to_use: "cohesive-navigation-realization".to_owned(),
        }],
        forbidden_collapse: vec![ForbiddenCollapse {
            left_ref: ROOT_COMPONENT_ID.to_owned(),
            right_ref: component.component_id.clone(),
            context: "Root admission must not admit or supersede a child ontology.".to_owned(),
            intended_use: "cohesive-navigation-realization".to_owned(),
        }],
        profile_ref: "test-empty-profile/v1".to_owned(),
    })
}

fn relation_state(relation: &NavigationRelation) -> OntologySemanticState {
    let identity = OntologySubjectIdentity {
        subject_id: relation.relation_id.clone(),
        ontology_id: ONTOLOGY_ID.to_owned(),
        subject_kind: SubjectKind::Relation,
        type_ref: format!("cal.cohesive-relation.{}", relation.r#type),
    };
    OntologySemanticState::Relation(OntologyRelationSemanticState {
        identity,
        lifecycle: Lifecycle::Active,
        source_node_id: relation.source.clone(),
        target_node_id: relation.target.clone(),
        direction: RelationDirection::Directed,
        typed_properties: empty_properties(),
        forbidden_collapse: vec![ForbiddenCollapse {
            left_ref: relation.source.clone(),
            right_ref: relation.target.clone(),
            context: format!(
                "The {} relation preserves direction and does not transfer authority.",
                relation.r#type
            ),
            intended_use: "cohesive-navigation-realization".to_owned(),
        }],
    })
}

fn definition_ref(source_ref: &String) -> DefinitionReference {
    DefinitionReference {
        definition_id: source_ref.clone(),
        selector_sha256: sha256(source_ref.as_bytes()),
    }
}

fn empty_properties() -> TypedPropertySet {
    TypedPropertySet {
        profile_ref: "test-empty-profile/v1".to_owned(),
        values: BTreeMap::new(),
    }
}

fn runtime_residue(route: &ResidueRoute) -> TypedResidue {
    TypedResidue {
        source_operation: BINDING_ID.to_owned(),
        expected_condition: route.next_action.clone(),
        observed_remainder: route.statement.clone(),
        residue_type: route.status.clone(),
        evidence_ref: route.route_id.clone(),
        owner_route: route.owner_route.clone(),
        treatment: format!("{}; lane={}", route.route_status, route.lane),
    }
}

fn write_pair(
    semantic_directory: &Path,
    governance_directory: &Path,
    cursor: u64,
    state: OntologySemanticState,
    owner_route: &str,
    posture: &str,
    residue: Vec<TypedResidue>,
) -> Result<(), RealizationError> {
    let identity = state.identity().clone();
    let mut semantic = SemanticEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Semantic,
        event_id: format!("cohesive-semantic-{cursor:04}"),
        event_digest: ZERO_DIGEST.to_owned(),
        stream_id: identity.semantic_stream_id(),
        subject_identity: identity.clone(),
        previous_event_digest: None,
        semantic_cursor: cursor,
        complete_resulting_semantic_state: state,
    };
    seal_semantic_event(&mut semantic).map_err(runtime_error)?;
    let reference = semantic_reference(&semantic);
    let mut governance = GovernanceEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Governance,
        event_id: format!("cohesive-governance-{cursor:04}"),
        event_digest: ZERO_DIGEST.to_owned(),
        stream_id: identity.governance_stream_id(),
        semantic_ref: reference.clone(),
        governance_cursor: cursor,
        previous_event_digest: None,
        complete_resulting_governance_state: governance_state(
            reference,
            owner_route,
            posture,
            residue,
        ),
    };
    seal_governance_event(&mut governance).map_err(runtime_error)?;
    write_canonical(semantic_directory, cursor, &semantic.event_id, &semantic)?;
    write_canonical(
        governance_directory,
        cursor,
        &governance.event_id,
        &governance,
    )
}

fn semantic_reference(event: &SemanticEvent) -> ExactSemanticEventReference {
    ExactSemanticEventReference {
        semantic_event_id: event.event_id.clone(),
        semantic_event_digest: event.event_digest.clone(),
        semantic_cursor: event.semantic_cursor,
    }
}

fn governance_state(
    reference: ExactSemanticEventReference,
    owner_route: &str,
    posture: &str,
    residue: Vec<TypedResidue>,
) -> OntologyGovernanceState {
    OntologyGovernanceState {
        semantic_ref: reference,
        provenance: vec![
            ProvenanceEntry {
                source_ref: PROJECTION_ID.to_owned(),
                relation: "translated-from".to_owned(),
                operation: "package-to-canonical-events".to_owned(),
                owner_route: owner_route.to_owned(),
                posture: posture.to_owned(),
            },
            ProvenanceEntry {
                source_ref: ROOT_DECISION_SHA256.to_owned(),
                relation: "authority-traced-to".to_owned(),
                operation: "preserve-root-only-admission".to_owned(),
                owner_route: "CyberAlchemy Lab ontology-system owner".to_owned(),
                posture: "root-admission-only".to_owned(),
            },
        ],
        owner_route: owner_route.to_owned(),
        candidate_or_maturity_status: posture.to_owned(),
        promotion_state_or_handle: "preserved-from-source".to_owned(),
        authority_kind_and_posture: AuthorityKindAndPosture {
            kind: "source-bound".to_owned(),
            posture: posture.to_owned(),
        },
        authority_effect: AuthorityEffect::None,
        evidence_confidence: ConfidenceReference {
            scheme_ref: "product-test/v1".to_owned(),
            level: "source-bound".to_owned(),
        },
        commitment_confidence: ConfidenceReference {
            scheme_ref: "product-test/v1".to_owned(),
            level: "candidate".to_owned(),
        },
        challenge_contract: ChallengeContract {
            challenge_response:
                "Route the challenge to the preserved source owner and root admission owner."
                    .to_owned(),
            valid_challenge_modes: vec![
                ChallengeMode::Evidence,
                ChallengeMode::Contradiction,
                ChallengeMode::OwnerReview,
            ],
            contradiction_edges: vec![],
            validation_edges: vec![],
            owner_route: owner_route.to_owned(),
            resolution_gate: "G-CAL-COHESIVE-ONTOLOGY-SYSTEM-ROOT-ADMISSION".to_owned(),
            blocking_questions: vec![],
            challenge_residue_route: owner_route.to_owned(),
        },
        residue,
        conflicts: vec![],
        drift_owner: owner_route.to_owned(),
        invalidation_route: owner_route.to_owned(),
    }
}

fn build_epoch(event_count: usize) -> IntegrationEpochEvent {
    let mut epoch = IntegrationEpochEvent {
        schema_version: "cyberalchemy-lab-ontology-product-realization-epoch/v1".to_owned(),
        event_type: "ontology-runtime-integration.IntegrationEpochWasRecorded".to_owned(),
        epoch_id: "CAL-ONTOLOGY-PRODUCT-EVENT-RUNTIME-EPOCH-001".to_owned(),
        event_digest: ZERO_DIGEST.to_owned(),
        navigation_sha256: NAVIGATION_SHA256.to_owned(),
        root_decision_sha256: ROOT_DECISION_SHA256.to_owned(),
        runtime_source_sha256: RUNTIME_SOURCE_SHA256.to_owned(),
        event_contract_sha256: EVENT_CONTRACT_SHA256.to_owned(),
        initial_cut_sha256: INITIAL_CUT_SHA256.to_owned(),
        initial_semantic_event_set_sha256: INITIAL_SEMANTIC_EVENT_SET_SHA256.to_owned(),
        initial_governance_event_set_sha256: INITIAL_GOVERNANCE_EVENT_SET_SHA256.to_owned(),
        semantic_event_count: event_count,
        governance_event_count: event_count,
        authority_effect: "none".to_owned(),
    };
    epoch.event_digest = sha256(
        serde_json::to_vec(&epoch)
            .expect("epoch serializes")
            .as_slice(),
    );
    epoch
}

fn validate_epoch(epoch: &IntegrationEpochEvent) -> Result<(), RealizationError> {
    let mut unsigned = epoch.clone();
    unsigned.event_digest = ZERO_DIGEST.to_owned();
    let expected = sha256(&serde_json::to_vec(&unsigned).map_err(serialization_error)?);
    if epoch.event_digest != expected
        || epoch.navigation_sha256 != NAVIGATION_SHA256
        || epoch.root_decision_sha256 != ROOT_DECISION_SHA256
        || epoch.runtime_source_sha256 != RUNTIME_SOURCE_SHA256
        || epoch.event_contract_sha256 != EVENT_CONTRACT_SHA256
        || epoch.initial_cut_sha256 != INITIAL_CUT_SHA256
        || epoch.initial_semantic_event_set_sha256 != INITIAL_SEMANTIC_EVENT_SET_SHA256
        || epoch.initial_governance_event_set_sha256 != INITIAL_GOVERNANCE_EVENT_SET_SHA256
        || epoch.semantic_event_count != 29
        || epoch.governance_event_count != 29
        || epoch.authority_effect != "none"
    {
        return Err(RealizationError::new(
            "INTEGRATION_EPOCH_INVALID",
            &epoch.epoch_id,
        ));
    }
    Ok(())
}

fn validate_initial_cut(store: &EventStore) -> Result<(), RealizationError> {
    if store.semantic_events().len() < 29 || store.governance_events().len() < 29 {
        return Err(RealizationError::new(
            "INITIAL_EVENT_SET_INCOMPLETE",
            "expected 29 semantic and 29 governance events",
        ));
    }
    let cut = store.ontology_at(29).map_err(runtime_error)?;
    let semantic = store.semantic_events()[..29]
        .iter()
        .map(|loaded| &loaded.event)
        .collect::<Vec<_>>();
    let governance = store.governance_events()[..29]
        .iter()
        .map(|loaded| &loaded.event)
        .collect::<Vec<_>>();
    if cut.source_event_set_digest != INITIAL_CUT_SHA256
        || digest_serialized(&semantic)? != INITIAL_SEMANTIC_EVENT_SET_SHA256
        || digest_serialized(&governance)? != INITIAL_GOVERNANCE_EVENT_SET_SHA256
    {
        return Err(RealizationError::new(
            "INITIAL_EVENT_SET_DIGEST_MISMATCH",
            cut.source_event_set_digest,
        ));
    }
    Ok(())
}

fn canonical_epoch(epoch: &IntegrationEpochEvent) -> Result<String, RealizationError> {
    serde_json::to_string(epoch)
        .map(|value| format!("{value}\n"))
        .map_err(serialization_error)
}

fn write_canonical<T: Serialize>(
    directory: &Path,
    cursor: u64,
    event_id: &str,
    event: &T,
) -> Result<(), RealizationError> {
    let path = directory.join(format!("{cursor:08}-{event_id}.json"));
    fs::write(path, canonical_json(event).map_err(runtime_error)?).map_err(io_error)
}

fn digest_serialized<T: Serialize>(value: &T) -> Result<String, RealizationError> {
    serde_json::to_vec(value)
        .map(|bytes| sha256(&bytes))
        .map_err(serialization_error)
}

fn runtime_error(error: ReplayFailure) -> RealizationError {
    RealizationError::new(error.code, error.detail)
}

fn io_error(error: std::io::Error) -> RealizationError {
    RealizationError::new("RUNTIME_IO_FAILED", error.to_string())
}

fn serialization_error(error: serde_json::Error) -> RealizationError {
    RealizationError::new("SERIALIZATION_FAILED", error.to_string())
}
