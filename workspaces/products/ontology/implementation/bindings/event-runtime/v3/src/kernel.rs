use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::error::Error;
use std::fmt::{self, Display};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::thread;

pub const ZERO_DIGEST: &str = "0000000000000000000000000000000000000000000000000000000000000000";

/// Pure preflight for the successor importer; performs no filesystem writes.
pub fn validate_import_history(
    pairs: &[(SemanticEvent, GovernanceEvent)],
) -> Result<(), ReplayFailure> {
    let semantic_events: Vec<_> = pairs
        .iter()
        .map(|(e, _)| LoadedSemanticEvent {
            event: e.clone(),
            path: PathBuf::new(),
        })
        .collect();
    let governance_events: Vec<_> = pairs
        .iter()
        .map(|(_, e)| LoadedGovernanceEvent {
            event: e.clone(),
            path: PathBuf::new(),
        })
        .collect();
    validate_semantic_history(&semantic_events)?;
    validate_governance_history(&semantic_events, &governance_events)?;
    validate_global_event_ids(&semantic_events, &governance_events)?;
    let store = EventStore {
        semantic_events,
        governance_events,
    };
    store.ontology_at(pairs.len() as u64)?;
    Ok(())
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SubjectKind {
    Node,
    Relation,
}

impl Display for SubjectKind {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(match self {
            Self::Node => "node",
            Self::Relation => "relation",
        })
    }
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Lifecycle {
    Active,
    Retired,
    Removed,
}

impl Display for Lifecycle {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(match self {
            Self::Active => "active",
            Self::Retired => "retired",
            Self::Removed => "removed",
        })
    }
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SourceKind {
    CanonicalEvent,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum EventFamily {
    Semantic,
    Governance,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum AuthorityEffect {
    None,
}

#[derive(Clone, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(deny_unknown_fields)]
pub struct OntologySubjectIdentity {
    pub subject_id: String,
    pub ontology_id: String,
    pub subject_kind: SubjectKind,
    pub type_ref: String,
}

impl OntologySubjectIdentity {
    pub fn semantic_stream_id(&self) -> String {
        format!(
            "semantic:{}:{}:{}",
            self.ontology_id, self.subject_kind, self.subject_id
        )
    }

    pub fn governance_stream_id(&self) -> String {
        format!(
            "governance:{}:{}:{}",
            self.ontology_id, self.subject_kind, self.subject_id
        )
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct DefinitionReference {
    pub definition_id: String,
    pub selector_sha256: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SemanticComponent {
    pub component_id: String,
    pub type_ref: String,
    pub definition_ref: DefinitionReference,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct TypedPropertySet {
    pub profile_ref: String,
    pub values: BTreeMap<String, serde_json::Value>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct UseObligation {
    pub obligation_id: String,
    pub requirement: String,
    pub applies_to_use: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ForbiddenCollapse {
    pub left_ref: String,
    pub right_ref: String,
    pub context: String,
    pub intended_use: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct OntologyNodeSemanticState {
    pub identity: OntologySubjectIdentity,
    pub lifecycle: Lifecycle,
    pub label: String,
    pub definition_or_claim: String,
    pub scope: String,
    pub semantic_components: Vec<SemanticComponent>,
    pub semantic_definition_refs: Vec<DefinitionReference>,
    pub typed_properties: TypedPropertySet,
    pub use_obligations: Vec<UseObligation>,
    pub forbidden_collapse: Vec<ForbiddenCollapse>,
    pub profile_ref: String,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum RelationDirection {
    Directed,
    Symmetric,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct OntologyRelationSemanticState {
    pub identity: OntologySubjectIdentity,
    pub lifecycle: Lifecycle,
    pub source_node_id: String,
    pub target_node_id: String,
    pub direction: RelationDirection,
    pub typed_properties: TypedPropertySet,
    pub forbidden_collapse: Vec<ForbiddenCollapse>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(untagged)]
pub enum OntologySemanticState {
    Node(OntologyNodeSemanticState),
    Relation(OntologyRelationSemanticState),
}

pub type ResultingSubjectState = OntologySemanticState;
pub type OntologyLifecycleState = Lifecycle;
pub type GraphCommitCursor = u64;
pub type OntologySubject = OntologySubjectIdentity;
pub type SubjectEventStream = Vec<SemanticEvent>;

impl OntologySemanticState {
    pub fn identity(&self) -> &OntologySubjectIdentity {
        match self {
            Self::Node(state) => &state.identity,
            Self::Relation(state) => &state.identity,
        }
    }

    pub fn lifecycle(&self) -> Lifecycle {
        match self {
            Self::Node(state) => state.lifecycle,
            Self::Relation(state) => state.lifecycle,
        }
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SemanticEvent {
    pub source_kind: SourceKind,
    pub event_family: EventFamily,
    pub event_id: String,
    pub event_digest: String,
    pub stream_id: String,
    pub subject_identity: OntologySubjectIdentity,
    pub previous_event_digest: Option<String>,
    pub semantic_cursor: u64,
    pub complete_resulting_semantic_state: OntologySemanticState,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ExactSemanticEventReference {
    pub semantic_event_id: String,
    pub semantic_event_digest: String,
    pub semantic_cursor: u64,
}

pub type GovernanceEventReference = ExactSemanticEventReference;

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProvenanceEntry {
    pub source_ref: String,
    pub relation: String,
    pub operation: String,
    pub owner_route: String,
    pub posture: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct AuthorityKindAndPosture {
    pub kind: String,
    pub posture: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ConfidenceReference {
    pub scheme_ref: String,
    pub level: String,
}

pub type EvidenceConfidence = ConfidenceReference;
pub type CommitmentConfidence = ConfidenceReference;

#[derive(Clone, Copy, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum ChallengeMode {
    Evidence,
    Contradiction,
    OwnerReview,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum EdgeReferenceKind {
    RelationId,
    Selector,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct EdgeReference {
    pub kind: EdgeReferenceKind,
    pub r#ref: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ChallengeContract {
    pub challenge_response: String,
    pub valid_challenge_modes: Vec<ChallengeMode>,
    pub contradiction_edges: Vec<EdgeReference>,
    pub validation_edges: Vec<EdgeReference>,
    pub owner_route: String,
    pub resolution_gate: String,
    pub blocking_questions: Vec<String>,
    pub challenge_residue_route: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct TypedResidue {
    pub source_operation: String,
    pub expected_condition: String,
    pub observed_remainder: String,
    pub residue_type: String,
    pub evidence_ref: String,
    pub owner_route: String,
    pub treatment: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct TypedConflict {
    pub conflict_id: String,
    pub conflict_type: String,
    pub statement: String,
    pub owner_route: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct OntologyGovernanceState {
    pub semantic_ref: ExactSemanticEventReference,
    pub provenance: Vec<ProvenanceEntry>,
    pub owner_route: String,
    pub candidate_or_maturity_status: String,
    pub promotion_state_or_handle: String,
    pub authority_kind_and_posture: AuthorityKindAndPosture,
    pub authority_effect: AuthorityEffect,
    pub evidence_confidence: ConfidenceReference,
    pub commitment_confidence: ConfidenceReference,
    pub challenge_contract: ChallengeContract,
    pub residue: Vec<TypedResidue>,
    pub conflicts: Vec<TypedConflict>,
    pub drift_owner: String,
    pub invalidation_route: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct GovernanceEvent {
    pub source_kind: SourceKind,
    pub event_family: EventFamily,
    pub event_id: String,
    pub event_digest: String,
    pub stream_id: String,
    pub semantic_ref: ExactSemanticEventReference,
    pub governance_cursor: u64,
    pub previous_event_digest: Option<String>,
    pub complete_resulting_governance_state: OntologyGovernanceState,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct LoadedSemanticEvent {
    pub event: SemanticEvent,
    pub path: PathBuf,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct LoadedGovernanceEvent {
    pub event: GovernanceEvent,
    pub path: PathBuf,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProjectionSubjectReference {
    pub identity: OntologySubjectIdentity,
    pub source_event_id: String,
    pub source_event_digest: String,
    pub source_cursor: u64,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProjectedSubject {
    pub identity: OntologySubjectIdentity,
    pub source_event_id: String,
    pub source_event_digest: String,
    pub source_cursor: u64,
    pub semantic_state: OntologySemanticState,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ConsistentOntologyCut {
    pub schema_version: String,
    pub authority_effect: AuthorityEffect,
    pub semantic_cursor: u64,
    pub source_event_count: usize,
    pub source_event_set_digest: String,
    pub subjects: Vec<ProjectedSubject>,
}

pub type CalculatedProjection = ConsistentOntologyCut;

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct LatestSubjectSnapshot {
    pub schema_version: String,
    pub authority: String,
    pub identity: OntologySubjectIdentity,
    pub source_event_id: String,
    pub source_event_digest: String,
    pub source_cursor: u64,
    pub semantic_state: OntologySemanticState,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProjectionCheckpoint {
    pub schema_version: String,
    pub authority: String,
    pub source_cursor: u64,
    pub source_event_set_digest: String,
    pub snapshots: Vec<LatestSubjectSnapshot>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SemanticStreamBoundary {
    pub event_digest: String,
    pub lifecycle: Lifecycle,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct BoundarySemanticEvent {
    pub reference: ExactSemanticEventReference,
    pub subject_identity: OntologySubjectIdentity,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct EventTailBoundary {
    pub schema_version: String,
    pub authority: String,
    pub semantic_cursor: u64,
    pub governance_cursor: u64,
    pub semantic_event_count: usize,
    pub governance_event_count: usize,
    pub projection_checkpoint_digest: String,
    pub semantic_stream_heads: BTreeMap<String, SemanticStreamBoundary>,
    pub governance_stream_heads: BTreeMap<String, String>,
    pub semantic_events_by_id: BTreeMap<String, BoundarySemanticEvent>,
    pub prior_event_ids: BTreeSet<String>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct EventTail {
    boundary: EventTailBoundary,
    target_semantic_cursor: u64,
    target_governance_cursor: u64,
    semantic_events: Vec<LoadedSemanticEvent>,
    governance_events: Vec<LoadedGovernanceEvent>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct GovernedOntologyNodeView {
    pub identity: OntologySubjectIdentity,
    pub semantic_state: OntologyNodeSemanticState,
    pub governance_state: OntologyGovernanceState,
    pub semantic_event_id: String,
    pub semantic_event_digest: String,
    pub semantic_cursor: u64,
    pub governance_event_refs: Vec<String>,
    pub calculated_view_digest: String,
    pub context_selector_ref: Option<String>,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub enum GovernanceJoinPolicy {
    #[serde(rename = "require-exact")]
    RequireExact,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub enum ProjectionProfile {
    #[serde(rename = "test-complete-profile/v1")]
    TestCompleteV1,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ContextSelector {
    pub semantic_cursor: u64,
    pub required_subject_set: Vec<OntologySubjectIdentity>,
    pub governance_join_policy: GovernanceJoinPolicy,
    pub intended_use: String,
    pub projection_profile: ProjectionProfile,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProjectionBody {
    pub subjects: Vec<ProjectionSubjectReference>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ContextProjection {
    pub context_selector_ref: String,
    pub source_cursor: u64,
    pub source_event_set_digest: String,
    pub selected_node_ids: Vec<String>,
    pub selected_relation_ids: Vec<String>,
    pub allowed_readings: Vec<String>,
    pub forbidden_authority_moves: Vec<String>,
    pub projection_body: ProjectionBody,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AppendSemanticEventRequest {
    pub expected_stream_version: u64,
    pub event: SemanticEvent,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AppendGovernanceEventRequest {
    pub expected_stream_version: u64,
    pub event: GovernanceEvent,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct AppendReceipt {
    pub schema_version: String,
    pub event_id: String,
    pub cursor: u64,
    pub event_digest: String,
    pub canonical_path: String,
    pub authority_effect: AuthorityEffect,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct ReplayFailure {
    pub code: String,
    pub detail: String,
}

impl ReplayFailure {
    fn new(code: &str, detail: impl Into<String>) -> Self {
        Self {
            code: code.to_owned(),
            detail: detail.into(),
        }
    }
}

impl Display for ReplayFailure {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}: {}", self.code, self.detail)
    }
}

impl Error for ReplayFailure {}

#[derive(Clone, Debug)]
pub struct EventStore {
    semantic_events: Vec<LoadedSemanticEvent>,
    governance_events: Vec<LoadedGovernanceEvent>,
}

impl EventStore {
    pub fn load(
        semantic_directory: impl AsRef<Path>,
        governance_directory: impl AsRef<Path>,
    ) -> Result<Self, ReplayFailure> {
        reject_in_progress_append(semantic_directory.as_ref())?;
        reject_in_progress_append(governance_directory.as_ref())?;
        let mut semantic_events = load_semantic_directory(semantic_directory.as_ref())?;
        semantic_events.sort_by_key(|loaded| loaded.event.semantic_cursor);
        validate_semantic_history(&semantic_events)?;

        let mut governance_events = load_governance_directory(governance_directory.as_ref())?;
        governance_events.sort_by_key(|loaded| loaded.event.governance_cursor);
        validate_governance_history(&semantic_events, &governance_events)?;
        validate_global_event_ids(&semantic_events, &governance_events)?;
        Ok(Self {
            semantic_events,
            governance_events,
        })
    }

    pub fn semantic_events(&self) -> &[LoadedSemanticEvent] {
        &self.semantic_events
    }

    pub fn governance_events(&self) -> &[LoadedGovernanceEvent] {
        &self.governance_events
    }

    fn latest_by_subject(
        &self,
        cursor: u64,
    ) -> Result<BTreeMap<OntologySubjectIdentity, &LoadedSemanticEvent>, ReplayFailure> {
        let latest = self.reduced_latest_by_subject(cursor)?;
        validate_relation_endpoints(&latest)?;
        Ok(latest)
    }

    fn reduced_latest_by_subject(
        &self,
        cursor: u64,
    ) -> Result<BTreeMap<OntologySubjectIdentity, &LoadedSemanticEvent>, ReplayFailure> {
        let maximum = self
            .semantic_events
            .last()
            .map(|loaded| loaded.event.semantic_cursor)
            .unwrap_or(0);
        if cursor == 0 || cursor > maximum {
            return Err(ReplayFailure::new(
                "CURSOR_OUT_OF_RANGE",
                format!("requested cursor {cursor}; available range is 1..={maximum}"),
            ));
        }
        let mut latest = BTreeMap::new();
        for loaded in self
            .semantic_events
            .iter()
            .filter(|loaded| loaded.event.semantic_cursor <= cursor)
        {
            latest.insert(loaded.event.subject_identity.clone(), loaded);
        }
        Ok(latest)
    }

    pub fn ontology_at(&self, cursor: u64) -> Result<ConsistentOntologyCut, ReplayFailure> {
        let latest = self.latest_by_subject(cursor)?;
        let subjects = latest
            .values()
            .filter(|loaded| {
                loaded.event.complete_resulting_semantic_state.lifecycle() == Lifecycle::Active
            })
            .map(|loaded| ProjectedSubject {
                identity: loaded.event.subject_identity.clone(),
                source_event_id: loaded.event.event_id.clone(),
                source_event_digest: loaded.event.event_digest.clone(),
                source_cursor: loaded.event.semantic_cursor,
                semantic_state: loaded.event.complete_resulting_semantic_state.clone(),
            })
            .collect::<Vec<_>>();
        let refs = subjects
            .iter()
            .map(projection_reference)
            .collect::<Vec<_>>();
        Ok(ConsistentOntologyCut {
            schema_version: "cal-consistent-ontology-cut/v2-candidate".to_owned(),
            authority_effect: AuthorityEffect::None,
            semantic_cursor: cursor,
            source_event_count: self
                .semantic_events
                .iter()
                .filter(|event| event.event.semantic_cursor <= cursor)
                .count(),
            source_event_set_digest: digest_value(&refs)?,
            subjects,
        })
    }

    pub fn latest_subject_snapshots(
        &self,
        cursor: u64,
    ) -> Result<Vec<LatestSubjectSnapshot>, ReplayFailure> {
        Ok(self
            .reduced_latest_by_subject(cursor)?
            .into_values()
            .map(|loaded| LatestSubjectSnapshot {
                schema_version: "cal-latest-subject-snapshot/v2-candidate".to_owned(),
                authority: "calculated-cache".to_owned(),
                identity: loaded.event.subject_identity.clone(),
                source_event_id: loaded.event.event_id.clone(),
                source_event_digest: loaded.event.event_digest.clone(),
                source_cursor: loaded.event.semantic_cursor,
                semantic_state: loaded.event.complete_resulting_semantic_state.clone(),
            })
            .collect())
    }

    pub fn checkpoint_at(&self, cursor: u64) -> Result<ProjectionCheckpoint, ReplayFailure> {
        let snapshots = self.latest_subject_snapshots(cursor)?;
        let references = snapshots
            .iter()
            .map(|snapshot| ProjectionSubjectReference {
                identity: snapshot.identity.clone(),
                source_event_id: snapshot.source_event_id.clone(),
                source_event_digest: snapshot.source_event_digest.clone(),
                source_cursor: snapshot.source_cursor,
            })
            .collect::<Vec<_>>();
        Ok(ProjectionCheckpoint {
            schema_version: "cal-projection-checkpoint/v2-candidate".to_owned(),
            authority: "calculated-cache".to_owned(),
            source_cursor: cursor,
            source_event_set_digest: digest_value(&references)?,
            snapshots,
        })
    }

    pub fn tail_boundary_at(
        &self,
        semantic_cursor: u64,
        governance_cursor: u64,
    ) -> Result<EventTailBoundary, ReplayFailure> {
        let checkpoint = self.checkpoint_at(semantic_cursor)?;
        if governance_cursor > self.governance_events.len() as u64 {
            return Err(ReplayFailure::new(
                "GOVERNANCE_CURSOR_OUT_OF_RANGE",
                governance_cursor.to_string(),
            ));
        }
        let semantic_prefix = self
            .semantic_events
            .iter()
            .filter(|loaded| loaded.event.semantic_cursor <= semantic_cursor)
            .collect::<Vec<_>>();
        let governance_prefix = self
            .governance_events
            .iter()
            .filter(|loaded| loaded.event.governance_cursor <= governance_cursor)
            .collect::<Vec<_>>();
        let semantic_stream_heads =
            semantic_prefix
                .iter()
                .fold(BTreeMap::new(), |mut heads, loaded| {
                    heads.insert(
                        loaded.event.stream_id.clone(),
                        SemanticStreamBoundary {
                            event_digest: loaded.event.event_digest.clone(),
                            lifecycle: loaded.event.complete_resulting_semantic_state.lifecycle(),
                        },
                    );
                    heads
                });
        let governance_stream_heads =
            governance_prefix
                .iter()
                .fold(BTreeMap::new(), |mut heads, loaded| {
                    heads.insert(
                        loaded.event.stream_id.clone(),
                        loaded.event.event_digest.clone(),
                    );
                    heads
                });
        let semantic_events_by_id = semantic_prefix
            .iter()
            .map(|loaded| {
                (
                    loaded.event.event_id.clone(),
                    BoundarySemanticEvent {
                        reference: ExactSemanticEventReference {
                            semantic_event_id: loaded.event.event_id.clone(),
                            semantic_event_digest: loaded.event.event_digest.clone(),
                            semantic_cursor: loaded.event.semantic_cursor,
                        },
                        subject_identity: loaded.event.subject_identity.clone(),
                    },
                )
            })
            .collect();
        let prior_event_ids = semantic_prefix
            .iter()
            .map(|loaded| loaded.event.event_id.clone())
            .chain(
                governance_prefix
                    .iter()
                    .map(|loaded| loaded.event.event_id.clone()),
            )
            .collect();
        Ok(EventTailBoundary {
            schema_version: "cal-event-tail-boundary/v1-prototype".to_owned(),
            authority: "calculated-cache".to_owned(),
            semantic_cursor,
            governance_cursor,
            semantic_event_count: semantic_prefix.len(),
            governance_event_count: governance_prefix.len(),
            projection_checkpoint_digest: checkpoint.source_event_set_digest,
            semantic_stream_heads,
            governance_stream_heads,
            semantic_events_by_id,
            prior_event_ids,
        })
    }

    pub fn ontology_from_checkpoint(
        &self,
        checkpoint: &ProjectionCheckpoint,
        cursor: u64,
    ) -> Result<ConsistentOntologyCut, ReplayFailure> {
        if cursor < checkpoint.source_cursor {
            return Err(ReplayFailure::new(
                "CHECKPOINT_CURSOR_AFTER_TARGET",
                format!("{} > {cursor}", checkpoint.source_cursor),
            ));
        }
        if &self.checkpoint_at(checkpoint.source_cursor)? != checkpoint {
            return Err(ReplayFailure::new(
                "CHECKPOINT_INVALID",
                checkpoint.source_cursor.to_string(),
            ));
        }
        let maximum = self
            .semantic_events
            .last()
            .map(|loaded| loaded.event.semantic_cursor)
            .unwrap_or(0);
        if cursor == 0 || cursor > maximum {
            return Err(ReplayFailure::new(
                "CURSOR_OUT_OF_RANGE",
                format!("requested cursor {cursor}; available range is 1..={maximum}"),
            ));
        }
        let mut latest = checkpoint
            .snapshots
            .iter()
            .map(|snapshot| {
                (
                    snapshot.identity.clone(),
                    ProjectedSubject {
                        identity: snapshot.identity.clone(),
                        source_event_id: snapshot.source_event_id.clone(),
                        source_event_digest: snapshot.source_event_digest.clone(),
                        source_cursor: snapshot.source_cursor,
                        semantic_state: snapshot.semantic_state.clone(),
                    },
                )
            })
            .collect::<BTreeMap<_, _>>();
        for loaded in self.semantic_events.iter().filter(|loaded| {
            loaded.event.semantic_cursor > checkpoint.source_cursor
                && loaded.event.semantic_cursor <= cursor
        }) {
            latest.insert(
                loaded.event.subject_identity.clone(),
                ProjectedSubject {
                    identity: loaded.event.subject_identity.clone(),
                    source_event_id: loaded.event.event_id.clone(),
                    source_event_digest: loaded.event.event_digest.clone(),
                    source_cursor: loaded.event.semantic_cursor,
                    semantic_state: loaded.event.complete_resulting_semantic_state.clone(),
                },
            );
        }
        validate_projected_relation_endpoints(&latest)?;
        let subjects = latest
            .into_values()
            .filter(|subject| subject.semantic_state.lifecycle() == Lifecycle::Active)
            .collect::<Vec<_>>();
        let references = subjects
            .iter()
            .map(projection_reference)
            .collect::<Vec<_>>();
        Ok(ConsistentOntologyCut {
            schema_version: "cal-consistent-ontology-cut/v2-candidate".to_owned(),
            authority_effect: AuthorityEffect::None,
            semantic_cursor: cursor,
            source_event_count: cursor as usize,
            source_event_set_digest: digest_value(&references)?,
            subjects,
        })
    }

    pub fn governed_node_view(
        &self,
        identity: &OntologySubjectIdentity,
        cursor: u64,
        context_selector_ref: Option<String>,
    ) -> Result<GovernedOntologyNodeView, ReplayFailure> {
        if identity.subject_kind != SubjectKind::Node {
            return Err(ReplayFailure::new(
                "GOVERNED_VIEW_REQUIRES_NODE",
                identity.subject_id.clone(),
            ));
        }
        let latest = self.latest_by_subject(cursor)?;
        let semantic = latest.get(identity).ok_or_else(|| {
            ReplayFailure::new("REQUIRED_SUBJECT_MISSING", identity.subject_id.clone())
        })?;
        let semantic_state = match &semantic.event.complete_resulting_semantic_state {
            OntologySemanticState::Node(state) if state.lifecycle == Lifecycle::Active => {
                state.clone()
            }
            OntologySemanticState::Node(_) => {
                return Err(ReplayFailure::new(
                    "REQUIRED_SUBJECT_NOT_ACTIVE",
                    identity.subject_id.clone(),
                ));
            }
            OntologySemanticState::Relation(_) => {
                return Err(ReplayFailure::new(
                    "GOVERNED_VIEW_REQUIRES_NODE",
                    identity.subject_id.clone(),
                ));
            }
        };
        let matching = self
            .governance_events
            .iter()
            .filter(|loaded| exact_reference_matches(&loaded.event.semantic_ref, &semantic.event))
            .collect::<Vec<_>>();
        let governance = matching.last().ok_or_else(|| {
            ReplayFailure::new(
                "EXACT_GOVERNANCE_STATE_MISSING",
                semantic.event.event_id.clone(),
            )
        })?;
        let mut view = GovernedOntologyNodeView {
            identity: identity.clone(),
            semantic_state,
            governance_state: governance.event.complete_resulting_governance_state.clone(),
            semantic_event_id: semantic.event.event_id.clone(),
            semantic_event_digest: semantic.event.event_digest.clone(),
            semantic_cursor: semantic.event.semantic_cursor,
            governance_event_refs: matching
                .iter()
                .map(|loaded| loaded.event.event_id.clone())
                .collect(),
            calculated_view_digest: ZERO_DIGEST.to_owned(),
            context_selector_ref,
        };
        view.calculated_view_digest = digest_value(&view)?;
        Ok(view)
    }

    pub fn context_projection(
        &self,
        context_selector_ref: &str,
        selector: &ContextSelector,
    ) -> Result<ContextProjection, ReplayFailure> {
        validate_identifier(context_selector_ref, "context_selector_ref")?;
        validate_identifier(&selector.intended_use, "intended_use")?;
        if selector.required_subject_set.is_empty() {
            return Err(ReplayFailure::new(
                "CONTEXT_REQUIRED_SET_EMPTY",
                context_selector_ref,
            ));
        }
        let required = selector
            .required_subject_set
            .iter()
            .cloned()
            .collect::<BTreeSet<_>>();
        if required.len() != selector.required_subject_set.len() {
            return Err(ReplayFailure::new(
                "CONTEXT_REQUIRED_SUBJECT_DUPLICATE",
                context_selector_ref,
            ));
        }
        let latest = self.latest_by_subject(selector.semantic_cursor)?;
        let mut references = Vec::new();
        let mut selected_node_ids = Vec::new();
        let mut selected_relation_ids = Vec::new();
        for identity in required {
            let loaded = latest.get(&identity).ok_or_else(|| {
                ReplayFailure::new("REQUIRED_SUBJECT_MISSING", identity.subject_id.clone())
            })?;
            if loaded.event.complete_resulting_semantic_state.lifecycle() != Lifecycle::Active {
                return Err(ReplayFailure::new(
                    "REQUIRED_SUBJECT_NOT_ACTIVE",
                    identity.subject_id,
                ));
            }
            if !self.governance_events.iter().any(|governance| {
                exact_reference_matches(&governance.event.semantic_ref, &loaded.event)
            }) {
                return Err(ReplayFailure::new(
                    "EXACT_GOVERNANCE_STATE_MISSING",
                    loaded.event.event_id.clone(),
                ));
            }
            match identity.subject_kind {
                SubjectKind::Node => selected_node_ids.push(identity.subject_id.clone()),
                SubjectKind::Relation => selected_relation_ids.push(identity.subject_id.clone()),
            }
            references.push(ProjectionSubjectReference {
                identity,
                source_event_id: loaded.event.event_id.clone(),
                source_event_digest: loaded.event.event_digest.clone(),
                source_cursor: loaded.event.semantic_cursor,
            });
        }
        selected_node_ids.sort();
        selected_relation_ids.sort();
        references.sort_by(|left, right| left.identity.cmp(&right.identity));
        Ok(ContextProjection {
            context_selector_ref: context_selector_ref.to_owned(),
            source_cursor: selector.semantic_cursor,
            source_event_set_digest: digest_value(&references)?,
            selected_node_ids,
            selected_relation_ids,
            allowed_readings: vec![format!("calculated-view-for-{}", selector.intended_use)],
            forbidden_authority_moves: vec![
                "admission-from-projection".to_owned(),
                "acceptance-from-projection".to_owned(),
                "publication-from-projection".to_owned(),
            ],
            projection_body: ProjectionBody {
                subjects: references,
            },
        })
    }

    pub fn append_semantic_batch(
        &mut self,
        semantic_directory: impl AsRef<Path>,
        requests: Vec<AppendSemanticEventRequest>,
    ) -> Result<Vec<AppendReceipt>, ReplayFailure> {
        if requests.is_empty() {
            return Err(ReplayFailure::new("APPEND_BATCH_EMPTY", "semantic"));
        }
        let mut versions = stream_versions_semantic(&self.semantic_events);
        let mut proposed = self.semantic_events.clone();
        let directory = semantic_directory.as_ref();
        let mut writes = Vec::new();
        for request in requests {
            let stream = request.event.stream_id.clone();
            let actual = versions.get(&stream).copied().unwrap_or(0);
            if request.expected_stream_version != actual {
                return Err(ReplayFailure::new(
                    "EXPECTED_STREAM_VERSION_MISMATCH",
                    format!(
                        "{stream}: expected {}; actual {actual}",
                        request.expected_stream_version
                    ),
                ));
            }
            versions.insert(stream, actual + 1);
            let file_name =
                canonical_file_name(request.event.semantic_cursor, &request.event.event_id)?;
            let canonical = canonical_json(&request.event)?;
            let path = directory.join(&file_name);
            proposed.push(LoadedSemanticEvent {
                event: request.event,
                path,
            });
            writes.push((file_name, canonical));
        }
        proposed.sort_by_key(|loaded| loaded.event.semantic_cursor);
        validate_semantic_history(&proposed)?;
        validate_global_event_ids(&proposed, &self.governance_events)?;
        persist_batch(directory, &writes)?;
        self.semantic_events = proposed;
        Ok(semantic_append_receipts(&self.semantic_events, writes))
    }

    pub fn append_governance_batch(
        &mut self,
        governance_directory: impl AsRef<Path>,
        requests: Vec<AppendGovernanceEventRequest>,
    ) -> Result<Vec<AppendReceipt>, ReplayFailure> {
        if requests.is_empty() {
            return Err(ReplayFailure::new("APPEND_BATCH_EMPTY", "governance"));
        }
        let mut versions = stream_versions_governance(&self.governance_events);
        let mut proposed = self.governance_events.clone();
        let directory = governance_directory.as_ref();
        let mut writes = Vec::new();
        for request in requests {
            let stream = request.event.stream_id.clone();
            let actual = versions.get(&stream).copied().unwrap_or(0);
            if request.expected_stream_version != actual {
                return Err(ReplayFailure::new(
                    "EXPECTED_STREAM_VERSION_MISMATCH",
                    format!(
                        "{stream}: expected {}; actual {actual}",
                        request.expected_stream_version
                    ),
                ));
            }
            versions.insert(stream, actual + 1);
            let file_name =
                canonical_file_name(request.event.governance_cursor, &request.event.event_id)?;
            let canonical = canonical_json(&request.event)?;
            let path = directory.join(&file_name);
            proposed.push(LoadedGovernanceEvent {
                event: request.event,
                path,
            });
            writes.push((file_name, canonical));
        }
        proposed.sort_by_key(|loaded| loaded.event.governance_cursor);
        validate_governance_history(&self.semantic_events, &proposed)?;
        validate_global_event_ids(&self.semantic_events, &proposed)?;
        persist_batch(directory, &writes)?;
        self.governance_events = proposed;
        Ok(governance_append_receipts(&self.governance_events, writes))
    }
}

impl EventTail {
    pub fn load(
        semantic_directory: impl AsRef<Path>,
        governance_directory: impl AsRef<Path>,
        boundary: EventTailBoundary,
        target_semantic_cursor: u64,
        target_governance_cursor: u64,
    ) -> Result<Self, ReplayFailure> {
        if target_semantic_cursor < boundary.semantic_cursor
            || target_governance_cursor < boundary.governance_cursor
        {
            return Err(ReplayFailure::new(
                "TAIL_CURSOR_BEFORE_BOUNDARY",
                format!(
                    "semantic {} -> {}; governance {} -> {}",
                    boundary.semantic_cursor,
                    target_semantic_cursor,
                    boundary.governance_cursor,
                    target_governance_cursor
                ),
            ));
        }
        reject_in_progress_append(semantic_directory.as_ref())?;
        reject_in_progress_append(governance_directory.as_ref())?;
        let semantic_events = load_semantic_directory_range(
            semantic_directory.as_ref(),
            boundary.semantic_cursor,
            target_semantic_cursor,
        )?;
        validate_semantic_tail(&boundary, &semantic_events, target_semantic_cursor)?;
        let governance_events = load_governance_directory_range(
            governance_directory.as_ref(),
            boundary.governance_cursor,
            target_governance_cursor,
        )?;
        validate_governance_tail(
            &boundary,
            &semantic_events,
            &governance_events,
            target_governance_cursor,
        )?;
        Ok(Self {
            boundary,
            target_semantic_cursor,
            target_governance_cursor,
            semantic_events,
            governance_events,
        })
    }

    pub fn boundary(&self) -> &EventTailBoundary {
        &self.boundary
    }

    pub fn semantic_events(&self) -> &[LoadedSemanticEvent] {
        &self.semantic_events
    }

    pub fn governance_events(&self) -> &[LoadedGovernanceEvent] {
        &self.governance_events
    }

    pub fn target_governance_cursor(&self) -> u64 {
        self.target_governance_cursor
    }

    pub fn ontology_from_checkpoint(
        &self,
        checkpoint: &ProjectionCheckpoint,
    ) -> Result<ConsistentOntologyCut, ReplayFailure> {
        if checkpoint.source_cursor != self.boundary.semantic_cursor
            || checkpoint.source_event_set_digest != self.boundary.projection_checkpoint_digest
        {
            return Err(ReplayFailure::new(
                "CHECKPOINT_BOUNDARY_MISMATCH",
                checkpoint.source_cursor.to_string(),
            ));
        }
        let mut latest = checkpoint
            .snapshots
            .iter()
            .map(|snapshot| {
                (
                    snapshot.identity.clone(),
                    ProjectedSubject {
                        identity: snapshot.identity.clone(),
                        source_event_id: snapshot.source_event_id.clone(),
                        source_event_digest: snapshot.source_event_digest.clone(),
                        source_cursor: snapshot.source_cursor,
                        semantic_state: snapshot.semantic_state.clone(),
                    },
                )
            })
            .collect::<BTreeMap<_, _>>();
        for loaded in &self.semantic_events {
            latest.insert(
                loaded.event.subject_identity.clone(),
                ProjectedSubject {
                    identity: loaded.event.subject_identity.clone(),
                    source_event_id: loaded.event.event_id.clone(),
                    source_event_digest: loaded.event.event_digest.clone(),
                    source_cursor: loaded.event.semantic_cursor,
                    semantic_state: loaded.event.complete_resulting_semantic_state.clone(),
                },
            );
        }
        validate_projected_relation_endpoints(&latest)?;
        let subjects = latest
            .into_values()
            .filter(|subject| subject.semantic_state.lifecycle() == Lifecycle::Active)
            .collect::<Vec<_>>();
        let references = subjects
            .iter()
            .map(projection_reference)
            .collect::<Vec<_>>();
        Ok(ConsistentOntologyCut {
            schema_version: "cal-consistent-ontology-cut/v2-candidate".to_owned(),
            authority_effect: AuthorityEffect::None,
            semantic_cursor: self.target_semantic_cursor,
            source_event_count: self.boundary.semantic_event_count + self.semantic_events.len(),
            source_event_set_digest: digest_value(&references)?,
            subjects,
        })
    }
}

pub fn seal_semantic_event(event: &mut SemanticEvent) -> Result<(), ReplayFailure> {
    event.event_digest = ZERO_DIGEST.to_owned();
    event.event_digest = digest_value(event)?;
    Ok(())
}

pub fn seal_governance_event(event: &mut GovernanceEvent) -> Result<(), ReplayFailure> {
    event.event_digest = ZERO_DIGEST.to_owned();
    event.event_digest = digest_value(event)?;
    Ok(())
}

pub fn canonical_json<T: Serialize>(value: &T) -> Result<String, ReplayFailure> {
    serde_json::to_string(value)
        .map(|json| format!("{json}\n"))
        .map_err(|error| ReplayFailure::new("CANONICAL_SERIALIZATION_FAILED", error.to_string()))
}

pub fn machine_projection<T: Serialize>(value: &T) -> Result<String, ReplayFailure> {
    serde_json::to_string_pretty(value)
        .map(|json| format!("{json}\n"))
        .map_err(|error| ReplayFailure::new("PROJECTION_SERIALIZATION_FAILED", error.to_string()))
}

pub fn human_projection(cut: &ConsistentOntologyCut) -> String {
    let mut output = format!(
        "# Ontology at cursor {}\n\nCalculated projection; canonical source remains the event history.\n\n| Subject | Kind | Lifecycle | Source cursor |\n| --- | --- | --- | ---: |\n",
        cut.semantic_cursor
    );
    for subject in &cut.subjects {
        output.push_str(&format!(
            "| `{}` | {} | {} | {} |\n",
            subject.identity.subject_id,
            subject.identity.subject_kind,
            subject.semantic_state.lifecycle(),
            subject.source_cursor
        ));
    }
    output
}

fn projection_reference(subject: &ProjectedSubject) -> ProjectionSubjectReference {
    ProjectionSubjectReference {
        identity: subject.identity.clone(),
        source_event_id: subject.source_event_id.clone(),
        source_event_digest: subject.source_event_digest.clone(),
        source_cursor: subject.source_cursor,
    }
}

fn digest_value<T: Serialize>(value: &T) -> Result<String, ReplayFailure> {
    Ok(sha256(canonical_json(value)?.as_bytes()))
}

fn validate_semantic_event_digest(event: &SemanticEvent) -> Result<(), ReplayFailure> {
    validate_sha256(&event.event_digest, "event_digest")?;
    let mut preimage = event.clone();
    preimage.event_digest = ZERO_DIGEST.to_owned();
    if event.event_digest != digest_value(&preimage)? {
        return Err(ReplayFailure::new(
            "EVENT_DIGEST_MISMATCH",
            event.event_id.clone(),
        ));
    }
    Ok(())
}

fn validate_governance_event_digest(event: &GovernanceEvent) -> Result<(), ReplayFailure> {
    validate_sha256(&event.event_digest, "event_digest")?;
    let mut preimage = event.clone();
    preimage.event_digest = ZERO_DIGEST.to_owned();
    if event.event_digest != digest_value(&preimage)? {
        return Err(ReplayFailure::new(
            "EVENT_DIGEST_MISMATCH",
            event.event_id.clone(),
        ));
    }
    Ok(())
}

fn load_semantic_directory(directory: &Path) -> Result<Vec<LoadedSemanticEvent>, ReplayFailure> {
    parallel_load_json_paths(directory, |path| {
        let bytes = fs::read(path).map_err(|error| io_failure("EVENT_READ_FAILED", path, error))?;
        reject_noncanonical_source(path, &bytes)?;
        let event: SemanticEvent = serde_json::from_slice(&bytes).map_err(|error| {
            ReplayFailure::new(
                "SEMANTIC_EVENT_DECODE_FAILED",
                format!("{}: {error}", path.display()),
            )
        })?;
        assert_canonical(path, &bytes, &event)?;
        Ok(LoadedSemanticEvent {
            event,
            path: path.to_path_buf(),
        })
    })
}

fn load_governance_directory(
    directory: &Path,
) -> Result<Vec<LoadedGovernanceEvent>, ReplayFailure> {
    parallel_load_json_paths(directory, |path| {
        let bytes = fs::read(path).map_err(|error| io_failure("EVENT_READ_FAILED", path, error))?;
        reject_noncanonical_source(path, &bytes)?;
        let event: GovernanceEvent = serde_json::from_slice(&bytes).map_err(|error| {
            ReplayFailure::new(
                "GOVERNANCE_EVENT_DECODE_FAILED",
                format!("{}: {error}", path.display()),
            )
        })?;
        assert_canonical(path, &bytes, &event)?;
        Ok(LoadedGovernanceEvent {
            event,
            path: path.to_path_buf(),
        })
    })
}

fn load_semantic_directory_range(
    directory: &Path,
    after_cursor: u64,
    through_cursor: u64,
) -> Result<Vec<LoadedSemanticEvent>, ReplayFailure> {
    let paths = json_paths_in_range(directory, after_cursor, through_cursor)?;
    parallel_load_paths(directory, paths, |path| {
        let bytes = fs::read(path).map_err(|error| io_failure("EVENT_READ_FAILED", path, error))?;
        reject_noncanonical_source(path, &bytes)?;
        let event: SemanticEvent = serde_json::from_slice(&bytes).map_err(|error| {
            ReplayFailure::new(
                "SEMANTIC_EVENT_DECODE_FAILED",
                format!("{}: {error}", path.display()),
            )
        })?;
        assert_canonical(path, &bytes, &event)?;
        Ok(LoadedSemanticEvent {
            event,
            path: path.to_path_buf(),
        })
    })
}

fn load_governance_directory_range(
    directory: &Path,
    after_cursor: u64,
    through_cursor: u64,
) -> Result<Vec<LoadedGovernanceEvent>, ReplayFailure> {
    let paths = json_paths_in_range(directory, after_cursor, through_cursor)?;
    parallel_load_paths(directory, paths, |path| {
        let bytes = fs::read(path).map_err(|error| io_failure("EVENT_READ_FAILED", path, error))?;
        reject_noncanonical_source(path, &bytes)?;
        let event: GovernanceEvent = serde_json::from_slice(&bytes).map_err(|error| {
            ReplayFailure::new(
                "GOVERNANCE_EVENT_DECODE_FAILED",
                format!("{}: {error}", path.display()),
            )
        })?;
        assert_canonical(path, &bytes, &event)?;
        Ok(LoadedGovernanceEvent {
            event,
            path: path.to_path_buf(),
        })
    })
}

fn parallel_load_json_paths<T, F>(directory: &Path, load: F) -> Result<Vec<T>, ReplayFailure>
where
    T: Send,
    F: Fn(&Path) -> Result<T, ReplayFailure> + Sync,
{
    let paths = json_paths(directory)?;
    parallel_load_paths(directory, paths, load)
}

fn parallel_load_paths<T, F>(
    directory: &Path,
    paths: Vec<PathBuf>,
    load: F,
) -> Result<Vec<T>, ReplayFailure>
where
    T: Send,
    F: Fn(&Path) -> Result<T, ReplayFailure> + Sync,
{
    if paths.is_empty() {
        return Ok(Vec::new());
    }
    let worker_count = thread::available_parallelism()
        .map(|value| value.get())
        .unwrap_or(1)
        .min(16)
        .min(paths.len());
    let chunk_size = paths.len().div_ceil(worker_count);
    thread::scope(|scope| {
        let handles = paths
            .chunks(chunk_size)
            .map(|chunk| {
                let load = &load;
                scope.spawn(move || {
                    chunk
                        .iter()
                        .map(|path| load(path))
                        .collect::<Result<Vec<_>, _>>()
                })
            })
            .collect::<Vec<_>>();
        let mut loaded = Vec::with_capacity(paths.len());
        for handle in handles {
            let chunk = handle.join().map_err(|_| {
                ReplayFailure::new(
                    "EVENT_LOAD_WORKER_PANICKED",
                    directory.display().to_string(),
                )
            })??;
            loaded.extend(chunk);
        }
        Ok(loaded)
    })
}

fn json_paths(directory: &Path) -> Result<Vec<PathBuf>, ReplayFailure> {
    let entries = fs::read_dir(directory)
        .map_err(|error| io_failure("EVENT_DIRECTORY_READ_FAILED", directory, error))?;
    let mut paths = entries
        .filter_map(|entry| entry.ok().map(|item| item.path()))
        .filter(|path| {
            path.extension()
                .is_some_and(|extension| extension == "json")
        })
        .collect::<Vec<_>>();
    paths.sort();
    Ok(paths)
}

fn json_paths_in_range(
    directory: &Path,
    after_cursor: u64,
    through_cursor: u64,
) -> Result<Vec<PathBuf>, ReplayFailure> {
    json_paths(directory)?
        .into_iter()
        .filter_map(|path| match event_file_cursor(&path) {
            Ok(cursor) if cursor > after_cursor && cursor <= through_cursor => Some(Ok(path)),
            Ok(_) => None,
            Err(failure) => Some(Err(failure)),
        })
        .collect()
}

fn event_file_cursor(path: &Path) -> Result<u64, ReplayFailure> {
    let name = path
        .file_name()
        .and_then(|value| value.to_str())
        .ok_or_else(|| ReplayFailure::new("EVENT_FILE_NAME_INVALID", path.display().to_string()))?;
    let cursor = name
        .split_once('-')
        .map(|(value, _)| value)
        .ok_or_else(|| ReplayFailure::new("EVENT_FILE_NAME_INVALID", path.display().to_string()))?;
    cursor
        .parse()
        .map_err(|_| ReplayFailure::new("EVENT_FILE_CURSOR_INVALID", path.display().to_string()))
}

fn reject_noncanonical_source(path: &Path, bytes: &[u8]) -> Result<(), ReplayFailure> {
    let value: serde_json::Value = serde_json::from_slice(bytes).map_err(|error| {
        ReplayFailure::new("EVENT_JSON_INVALID", format!("{}: {error}", path.display()))
    })?;
    if value.get("source_kind").and_then(serde_json::Value::as_str) != Some("canonical_event") {
        return Err(ReplayFailure::new(
            "NONCANONICAL_REPLAY_SOURCE",
            path.display().to_string(),
        ));
    }
    Ok(())
}

fn assert_canonical<T: Serialize>(
    path: &Path,
    actual: &[u8],
    value: &T,
) -> Result<(), ReplayFailure> {
    let expected = canonical_json(value)?;
    if actual != expected.as_bytes() {
        return Err(ReplayFailure::new(
            "NON_CANONICAL_JSON",
            path.display().to_string(),
        ));
    }
    Ok(())
}

fn validate_semantic_history(events: &[LoadedSemanticEvent]) -> Result<(), ReplayFailure> {
    let mut event_ids = BTreeSet::new();
    let mut last_by_stream = BTreeMap::<String, String>::new();
    let mut lifecycle_by_stream = BTreeMap::<String, Lifecycle>::new();
    for (index, loaded) in events.iter().enumerate() {
        let event = &loaded.event;
        let expected_cursor = index as u64 + 1;
        if event.semantic_cursor != expected_cursor {
            return Err(ReplayFailure::new(
                "GRAPH_CURSOR_NOT_CONTIGUOUS",
                format!(
                    "expected {expected_cursor}; found {}",
                    event.semantic_cursor
                ),
            ));
        }
        if event.event_family != EventFamily::Semantic {
            return Err(ReplayFailure::new("EVENT_FAMILY_MISMATCH", &event.event_id));
        }
        validate_identifier(&event.event_id, "event_id")?;
        validate_identity(&event.subject_identity)?;
        validate_semantic_state(&event.complete_resulting_semantic_state)?;
        validate_semantic_event_digest(event)?;
        if !event_ids.insert(event.event_id.clone()) {
            return Err(ReplayFailure::new(
                "SEMANTIC_EVENT_ID_DUPLICATE",
                event.event_id.clone(),
            ));
        }
        let expected_stream = event.subject_identity.semantic_stream_id();
        if event.stream_id != expected_stream {
            return Err(ReplayFailure::new(
                "SUBJECT_STREAM_ID_MISMATCH",
                format!("expected {expected_stream}; found {}", event.stream_id),
            ));
        }
        if event.complete_resulting_semantic_state.identity() != &event.subject_identity {
            return Err(ReplayFailure::new(
                "RESULTING_STATE_IDENTITY_MISMATCH",
                event.event_id.clone(),
            ));
        }
        let previous = last_by_stream.get(&event.stream_id);
        if event.previous_event_digest.as_ref() != previous {
            return Err(ReplayFailure::new(
                "SUBJECT_EVENT_CHAIN_BROKEN",
                format!("{} at cursor {}", event.stream_id, event.semantic_cursor),
            ));
        }
        validate_lifecycle_transition(
            lifecycle_by_stream.get(&event.stream_id).copied(),
            event.complete_resulting_semantic_state.lifecycle(),
            &event.event_id,
        )?;
        last_by_stream.insert(event.stream_id.clone(), event.event_digest.clone());
        lifecycle_by_stream.insert(
            event.stream_id.clone(),
            event.complete_resulting_semantic_state.lifecycle(),
        );
    }
    Ok(())
}

fn validate_semantic_tail(
    boundary: &EventTailBoundary,
    events: &[LoadedSemanticEvent],
    target_cursor: u64,
) -> Result<(), ReplayFailure> {
    if boundary.schema_version != "cal-event-tail-boundary/v1-prototype"
        || boundary.authority != "calculated-cache"
        || boundary.semantic_event_count != boundary.semantic_cursor as usize
        || boundary.governance_event_count != boundary.governance_cursor as usize
    {
        return Err(ReplayFailure::new(
            "EVENT_TAIL_BOUNDARY_INVALID",
            boundary.semantic_cursor.to_string(),
        ));
    }
    if events.len() as u64 != target_cursor - boundary.semantic_cursor {
        return Err(ReplayFailure::new(
            "SEMANTIC_TAIL_INCOMPLETE",
            format!(
                "expected {}; found {}",
                target_cursor - boundary.semantic_cursor,
                events.len()
            ),
        ));
    }
    let mut event_ids = boundary.prior_event_ids.clone();
    let mut heads = boundary.semantic_stream_heads.clone();
    for (index, loaded) in events.iter().enumerate() {
        let event = &loaded.event;
        let expected_cursor = boundary.semantic_cursor + index as u64 + 1;
        if event.semantic_cursor != expected_cursor {
            return Err(ReplayFailure::new(
                "GRAPH_CURSOR_NOT_CONTIGUOUS",
                format!(
                    "expected {expected_cursor}; found {}",
                    event.semantic_cursor
                ),
            ));
        }
        if event_file_cursor(&loaded.path)? != event.semantic_cursor {
            return Err(ReplayFailure::new(
                "EVENT_FILE_CURSOR_MISMATCH",
                loaded.path.display().to_string(),
            ));
        }
        if event.event_family != EventFamily::Semantic {
            return Err(ReplayFailure::new("EVENT_FAMILY_MISMATCH", &event.event_id));
        }
        validate_identifier(&event.event_id, "event_id")?;
        validate_identity(&event.subject_identity)?;
        validate_semantic_state(&event.complete_resulting_semantic_state)?;
        validate_semantic_event_digest(event)?;
        if !event_ids.insert(event.event_id.clone()) {
            return Err(ReplayFailure::new(
                "GLOBAL_EVENT_ID_DUPLICATE",
                event.event_id.clone(),
            ));
        }
        let expected_stream = event.subject_identity.semantic_stream_id();
        if event.stream_id != expected_stream {
            return Err(ReplayFailure::new(
                "SUBJECT_STREAM_ID_MISMATCH",
                format!("expected {expected_stream}; found {}", event.stream_id),
            ));
        }
        if event.complete_resulting_semantic_state.identity() != &event.subject_identity {
            return Err(ReplayFailure::new(
                "RESULTING_STATE_IDENTITY_MISMATCH",
                event.event_id.clone(),
            ));
        }
        let previous = heads.get(&event.stream_id);
        if event.previous_event_digest.as_ref() != previous.map(|head| &head.event_digest) {
            return Err(ReplayFailure::new(
                "SUBJECT_EVENT_CHAIN_BROKEN",
                format!("{} at cursor {}", event.stream_id, event.semantic_cursor),
            ));
        }
        validate_lifecycle_transition(
            previous.map(|head| head.lifecycle),
            event.complete_resulting_semantic_state.lifecycle(),
            &event.event_id,
        )?;
        heads.insert(
            event.stream_id.clone(),
            SemanticStreamBoundary {
                event_digest: event.event_digest.clone(),
                lifecycle: event.complete_resulting_semantic_state.lifecycle(),
            },
        );
    }
    Ok(())
}

fn validate_governance_history(
    semantic: &[LoadedSemanticEvent],
    governance: &[LoadedGovernanceEvent],
) -> Result<(), ReplayFailure> {
    let semantic_by_id = semantic
        .iter()
        .map(|loaded| (loaded.event.event_id.as_str(), loaded))
        .collect::<BTreeMap<_, _>>();
    let mut event_ids = BTreeSet::new();
    let mut last_by_stream = BTreeMap::<String, String>::new();
    for (index, loaded) in governance.iter().enumerate() {
        let event = &loaded.event;
        let expected_cursor = index as u64 + 1;
        if event.governance_cursor != expected_cursor {
            return Err(ReplayFailure::new(
                "GOVERNANCE_CURSOR_NOT_CONTIGUOUS",
                format!(
                    "expected {expected_cursor}; found {}",
                    event.governance_cursor
                ),
            ));
        }
        if event.event_family != EventFamily::Governance {
            return Err(ReplayFailure::new("EVENT_FAMILY_MISMATCH", &event.event_id));
        }
        validate_identifier(&event.event_id, "event_id")?;
        validate_governance_event_digest(event)?;
        validate_governance_state(&event.complete_resulting_governance_state)?;
        if event.semantic_ref != event.complete_resulting_governance_state.semantic_ref {
            return Err(ReplayFailure::new(
                "GOVERNANCE_STATE_REFERENCE_MISMATCH",
                event.event_id.clone(),
            ));
        }
        if !event_ids.insert(event.event_id.clone()) {
            return Err(ReplayFailure::new(
                "GOVERNANCE_EVENT_ID_DUPLICATE",
                event.event_id.clone(),
            ));
        }
        let semantic_event = semantic_by_id
            .get(event.semantic_ref.semantic_event_id.as_str())
            .ok_or_else(|| {
                ReplayFailure::new(
                    "GOVERNANCE_REFERENCE_MISSING",
                    event.semantic_ref.semantic_event_id.clone(),
                )
            })?;
        if !exact_reference_matches(&event.semantic_ref, &semantic_event.event) {
            return Err(ReplayFailure::new(
                "GOVERNANCE_REFERENCE_MISMATCH",
                event.semantic_ref.semantic_event_id.clone(),
            ));
        }
        let expected_stream = semantic_event.event.subject_identity.governance_stream_id();
        if event.stream_id != expected_stream {
            return Err(ReplayFailure::new(
                "GOVERNANCE_STREAM_ID_MISMATCH",
                format!("expected {expected_stream}; found {}", event.stream_id),
            ));
        }
        let previous = last_by_stream.get(&event.stream_id);
        if event.previous_event_digest.as_ref() != previous {
            return Err(ReplayFailure::new(
                "GOVERNANCE_EVENT_CHAIN_BROKEN",
                event.event_id.clone(),
            ));
        }
        last_by_stream.insert(event.stream_id.clone(), event.event_digest.clone());
    }
    Ok(())
}

fn validate_governance_tail(
    boundary: &EventTailBoundary,
    semantic_tail: &[LoadedSemanticEvent],
    governance_tail: &[LoadedGovernanceEvent],
    target_cursor: u64,
) -> Result<(), ReplayFailure> {
    if governance_tail.len() as u64 != target_cursor - boundary.governance_cursor {
        return Err(ReplayFailure::new(
            "GOVERNANCE_TAIL_INCOMPLETE",
            format!(
                "expected {}; found {}",
                target_cursor - boundary.governance_cursor,
                governance_tail.len()
            ),
        ));
    }
    let mut semantic_by_id = boundary.semantic_events_by_id.clone();
    for loaded in semantic_tail {
        semantic_by_id.insert(
            loaded.event.event_id.clone(),
            BoundarySemanticEvent {
                reference: ExactSemanticEventReference {
                    semantic_event_id: loaded.event.event_id.clone(),
                    semantic_event_digest: loaded.event.event_digest.clone(),
                    semantic_cursor: loaded.event.semantic_cursor,
                },
                subject_identity: loaded.event.subject_identity.clone(),
            },
        );
    }
    let mut event_ids = boundary.prior_event_ids.clone();
    event_ids.extend(
        semantic_tail
            .iter()
            .map(|loaded| loaded.event.event_id.clone()),
    );
    let mut heads = boundary.governance_stream_heads.clone();
    for (index, loaded) in governance_tail.iter().enumerate() {
        let event = &loaded.event;
        let expected_cursor = boundary.governance_cursor + index as u64 + 1;
        if event.governance_cursor != expected_cursor {
            return Err(ReplayFailure::new(
                "GOVERNANCE_CURSOR_NOT_CONTIGUOUS",
                format!(
                    "expected {expected_cursor}; found {}",
                    event.governance_cursor
                ),
            ));
        }
        if event_file_cursor(&loaded.path)? != event.governance_cursor {
            return Err(ReplayFailure::new(
                "EVENT_FILE_CURSOR_MISMATCH",
                loaded.path.display().to_string(),
            ));
        }
        if event.event_family != EventFamily::Governance {
            return Err(ReplayFailure::new("EVENT_FAMILY_MISMATCH", &event.event_id));
        }
        validate_identifier(&event.event_id, "event_id")?;
        validate_governance_event_digest(event)?;
        validate_governance_state(&event.complete_resulting_governance_state)?;
        if event.semantic_ref != event.complete_resulting_governance_state.semantic_ref {
            return Err(ReplayFailure::new(
                "GOVERNANCE_STATE_REFERENCE_MISMATCH",
                event.event_id.clone(),
            ));
        }
        if !event_ids.insert(event.event_id.clone()) {
            return Err(ReplayFailure::new(
                "GLOBAL_EVENT_ID_DUPLICATE",
                event.event_id.clone(),
            ));
        }
        let semantic = semantic_by_id
            .get(&event.semantic_ref.semantic_event_id)
            .ok_or_else(|| {
                ReplayFailure::new(
                    "GOVERNANCE_REFERENCE_MISSING",
                    event.semantic_ref.semantic_event_id.clone(),
                )
            })?;
        if semantic.reference != event.semantic_ref {
            return Err(ReplayFailure::new(
                "GOVERNANCE_REFERENCE_MISMATCH",
                event.semantic_ref.semantic_event_id.clone(),
            ));
        }
        let expected_stream = semantic.subject_identity.governance_stream_id();
        if event.stream_id != expected_stream {
            return Err(ReplayFailure::new(
                "GOVERNANCE_STREAM_ID_MISMATCH",
                format!("expected {expected_stream}; found {}", event.stream_id),
            ));
        }
        if event.previous_event_digest.as_ref() != heads.get(&event.stream_id) {
            return Err(ReplayFailure::new(
                "GOVERNANCE_EVENT_CHAIN_BROKEN",
                event.event_id.clone(),
            ));
        }
        heads.insert(event.stream_id.clone(), event.event_digest.clone());
    }
    Ok(())
}

fn exact_reference_matches(reference: &ExactSemanticEventReference, event: &SemanticEvent) -> bool {
    reference.semantic_event_id == event.event_id
        && reference.semantic_event_digest == event.event_digest
        && reference.semantic_cursor == event.semantic_cursor
}

fn validate_relation_endpoints(
    latest: &BTreeMap<OntologySubjectIdentity, &LoadedSemanticEvent>,
) -> Result<(), ReplayFailure> {
    let active_nodes = latest
        .iter()
        .filter_map(
            |(identity, loaded)| match &loaded.event.complete_resulting_semantic_state {
                OntologySemanticState::Node(state) if state.lifecycle == Lifecycle::Active => {
                    Some((identity.ontology_id.as_str(), identity.subject_id.as_str()))
                }
                _ => None,
            },
        )
        .collect::<BTreeSet<_>>();
    for (identity, loaded) in latest {
        if let OntologySemanticState::Relation(state) =
            &loaded.event.complete_resulting_semantic_state
            && state.lifecycle == Lifecycle::Active
            && (!active_nodes
                .contains(&(identity.ontology_id.as_str(), state.source_node_id.as_str()))
                || !active_nodes
                    .contains(&(identity.ontology_id.as_str(), state.target_node_id.as_str())))
        {
            return Err(ReplayFailure::new(
                "RELATION_ENDPOINT_INTEGRITY",
                format!(
                    "{} requires active endpoints {} and {}",
                    identity.subject_id, state.source_node_id, state.target_node_id
                ),
            ));
        }
    }
    Ok(())
}

fn validate_projected_relation_endpoints(
    latest: &BTreeMap<OntologySubjectIdentity, ProjectedSubject>,
) -> Result<(), ReplayFailure> {
    let active_nodes = latest
        .iter()
        .filter_map(|(identity, projected)| match &projected.semantic_state {
            OntologySemanticState::Node(state) if state.lifecycle == Lifecycle::Active => {
                Some((identity.ontology_id.as_str(), identity.subject_id.as_str()))
            }
            _ => None,
        })
        .collect::<BTreeSet<_>>();
    for (identity, projected) in latest {
        if let OntologySemanticState::Relation(state) = &projected.semantic_state
            && state.lifecycle == Lifecycle::Active
            && (!active_nodes
                .contains(&(identity.ontology_id.as_str(), state.source_node_id.as_str()))
                || !active_nodes
                    .contains(&(identity.ontology_id.as_str(), state.target_node_id.as_str())))
        {
            return Err(ReplayFailure::new(
                "RELATION_ENDPOINT_INTEGRITY",
                identity.subject_id.clone(),
            ));
        }
    }
    Ok(())
}

fn validate_global_event_ids(
    semantic: &[LoadedSemanticEvent],
    governance: &[LoadedGovernanceEvent],
) -> Result<(), ReplayFailure> {
    let mut identities = BTreeSet::new();
    for event_id in semantic
        .iter()
        .map(|loaded| loaded.event.event_id.as_str())
        .chain(
            governance
                .iter()
                .map(|loaded| loaded.event.event_id.as_str()),
        )
    {
        if !identities.insert(event_id) {
            return Err(ReplayFailure::new("GLOBAL_EVENT_ID_DUPLICATE", event_id));
        }
    }
    Ok(())
}

fn validate_identity(identity: &OntologySubjectIdentity) -> Result<(), ReplayFailure> {
    validate_identifier(&identity.subject_id, "subject_id")?;
    validate_identifier(&identity.ontology_id, "ontology_id")?;
    validate_identifier(&identity.type_ref, "type_ref")
}

fn validate_semantic_state(state: &OntologySemanticState) -> Result<(), ReplayFailure> {
    validate_identity(state.identity())?;
    match state {
        OntologySemanticState::Node(node) => {
            if node.identity.subject_kind != SubjectKind::Node {
                return Err(ReplayFailure::new(
                    "SUBJECT_KIND_MISMATCH",
                    node.identity.subject_id.clone(),
                ));
            }
            validate_nonempty(&node.label, "label")?;
            validate_nonempty(&node.definition_or_claim, "definition_or_claim")?;
            validate_nonempty(&node.scope, "scope")?;
            if node.semantic_definition_refs.is_empty() {
                return Err(ReplayFailure::new(
                    "SEMANTIC_DEFINITION_REFS_EMPTY",
                    node.identity.subject_id.clone(),
                ));
            }
            validate_typed_properties(&node.typed_properties)?;
            if node.profile_ref != node.typed_properties.profile_ref {
                return Err(ReplayFailure::new("PROFILE_REF_INVALID", &node.profile_ref));
            }
            for reference in &node.semantic_definition_refs {
                validate_identifier(&reference.definition_id, "definition_id")?;
                validate_sha256(&reference.selector_sha256, "selector_sha256")?;
            }
        }
        OntologySemanticState::Relation(relation) => {
            if relation.identity.subject_kind != SubjectKind::Relation {
                return Err(ReplayFailure::new(
                    "SUBJECT_KIND_MISMATCH",
                    relation.identity.subject_id.clone(),
                ));
            }
            validate_identifier(&relation.source_node_id, "source_node_id")?;
            validate_identifier(&relation.target_node_id, "target_node_id")?;
            validate_typed_properties(&relation.typed_properties)?;
        }
    }
    Ok(())
}

fn validate_typed_properties(properties: &TypedPropertySet) -> Result<(), ReplayFailure> {
    if properties.profile_ref == "source-record-profile/v1" {
        let v = &properties.values;
        if v.len() != 2
            || !v.get("source_record").is_some_and(|x| x.is_object())
            || !v.get("source_binding").is_some_and(|x| {
                x.as_object().is_some_and(|o| {
                    o.len() == 5
                        && ["package_key", "path", "sha256", "selector", "record_sha256"]
                            .iter()
                            .all(|k| {
                                o.get(*k)
                                    .is_some_and(|a| a.as_str().is_some_and(|s| !s.is_empty()))
                            })
                })
            })
        {
            return Err(ReplayFailure::new(
                "SOURCE_RECORD_PROFILE_INVALID",
                "closed source record envelope required",
            ));
        }
        let binding = &v["source_binding"];
        validate_sha256(binding["sha256"].as_str().unwrap(), "source sha256")?;
        validate_sha256(binding["record_sha256"].as_str().unwrap(), "record sha256")?;
        let record_digest = sha256(canonical_json(&v["source_record"])?.as_bytes());
        if binding["record_sha256"].as_str() != Some(record_digest.as_str()) {
            return Err(ReplayFailure::new(
                "SOURCE_RECORD_DIGEST_MISMATCH",
                "record differs",
            ));
        }
    } else if properties.profile_ref != "test-empty-profile/v1" || !properties.values.is_empty() {
        return Err(ReplayFailure::new(
            "UNTYPED_RESIDUE",
            "unsupported prototype property profile",
        ));
    }
    Ok(())
}

fn validate_governance_state(state: &OntologyGovernanceState) -> Result<(), ReplayFailure> {
    if state.provenance.is_empty() {
        return Err(ReplayFailure::new("PROVENANCE_EMPTY", "governance state"));
    }
    validate_nonempty(&state.owner_route, "owner_route")?;
    validate_identifier(
        &state.candidate_or_maturity_status,
        "candidate_or_maturity_status",
    )?;
    validate_identifier(
        &state.promotion_state_or_handle,
        "promotion_state_or_handle",
    )?;
    validate_nonempty(&state.drift_owner, "drift_owner")?;
    validate_nonempty(&state.invalidation_route, "invalidation_route")?;
    let modes = state
        .challenge_contract
        .valid_challenge_modes
        .iter()
        .copied()
        .collect::<BTreeSet<_>>();
    if modes.is_empty() || modes.len() != state.challenge_contract.valid_challenge_modes.len() {
        return Err(ReplayFailure::new(
            "CHALLENGE_MODES_INVALID",
            "modes must be non-empty and unique",
        ));
    }
    validate_nonempty(
        &state.challenge_contract.challenge_response,
        "challenge_response",
    )?;
    validate_nonempty(
        &state.challenge_contract.owner_route,
        "challenge_owner_route",
    )?;
    validate_identifier(&state.challenge_contract.resolution_gate, "resolution_gate")?;
    validate_nonempty(
        &state.challenge_contract.challenge_residue_route,
        "challenge_residue_route",
    )?;
    Ok(())
}

fn validate_lifecycle_transition(
    previous: Option<Lifecycle>,
    next: Lifecycle,
    event_id: &str,
) -> Result<(), ReplayFailure> {
    let valid = matches!(
        (previous, next),
        (None, Lifecycle::Active)
            | (Some(Lifecycle::Active), Lifecycle::Active)
            | (Some(Lifecycle::Active), Lifecycle::Retired)
            | (Some(Lifecycle::Active), Lifecycle::Removed)
            | (Some(Lifecycle::Retired), Lifecycle::Retired)
            | (Some(Lifecycle::Retired), Lifecycle::Active)
            | (Some(Lifecycle::Retired), Lifecycle::Removed)
    );
    if !valid {
        return Err(ReplayFailure::new(
            "LIFECYCLE_TRANSITION_INVALID",
            format!("{event_id}: {previous:?} -> {next:?}"),
        ));
    }
    Ok(())
}

fn stream_versions_semantic(events: &[LoadedSemanticEvent]) -> BTreeMap<String, u64> {
    let mut versions = BTreeMap::new();
    for event in events {
        *versions.entry(event.event.stream_id.clone()).or_insert(0) += 1;
    }
    versions
}

fn stream_versions_governance(events: &[LoadedGovernanceEvent]) -> BTreeMap<String, u64> {
    let mut versions = BTreeMap::new();
    for event in events {
        *versions.entry(event.event.stream_id.clone()).or_insert(0) += 1;
    }
    versions
}

fn semantic_append_receipts(
    events: &[LoadedSemanticEvent],
    writes: Vec<(String, String)>,
) -> Vec<AppendReceipt> {
    writes
        .into_iter()
        .map(|(file_name, _)| {
            let event = events
                .iter()
                .find(|loaded| {
                    loaded.path.file_name().and_then(|name| name.to_str())
                        == Some(file_name.as_str())
                })
                .expect("persisted semantic event");
            AppendReceipt {
                schema_version: "cal-semantic-event-append-receipt/v2-candidate".to_owned(),
                event_id: event.event.event_id.clone(),
                cursor: event.event.semantic_cursor,
                event_digest: event.event.event_digest.clone(),
                canonical_path: file_name,
                authority_effect: AuthorityEffect::None,
            }
        })
        .collect()
}

fn governance_append_receipts(
    events: &[LoadedGovernanceEvent],
    writes: Vec<(String, String)>,
) -> Vec<AppendReceipt> {
    writes
        .into_iter()
        .map(|(file_name, _)| {
            let event = events
                .iter()
                .find(|loaded| {
                    loaded.path.file_name().and_then(|name| name.to_str())
                        == Some(file_name.as_str())
                })
                .expect("persisted governance event");
            AppendReceipt {
                schema_version: "cal-governance-event-append-receipt/v2-candidate".to_owned(),
                event_id: event.event.event_id.clone(),
                cursor: event.event.governance_cursor,
                event_digest: event.event.event_digest.clone(),
                canonical_path: file_name,
                authority_effect: AuthorityEffect::None,
            }
        })
        .collect()
}

fn canonical_file_name(cursor: u64, event_id: &str) -> Result<String, ReplayFailure> {
    validate_identifier(event_id, "event_id")?;
    Ok(format!("{cursor:08}-{event_id}.json"))
}

fn persist_batch(directory: &Path, writes: &[(String, String)]) -> Result<(), ReplayFailure> {
    fs::create_dir_all(directory)
        .map_err(|error| io_failure("APPEND_DIRECTORY_CREATE_FAILED", directory, error))?;
    let lock_path = directory.join(".append.lock");
    let lock = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&lock_path)
        .map_err(|error| io_failure("APPEND_LOCK_FAILED", &lock_path, error))?;
    drop(lock);
    let mut temporary_paths = Vec::new();
    let mut committed_paths = Vec::new();
    let result = (|| -> Result<(), ReplayFailure> {
        for (name, bytes) in writes {
            let target = directory.join(name);
            if target.exists() {
                return Err(ReplayFailure::new(
                    "APPEND_TARGET_EXISTS",
                    target.display().to_string(),
                ));
            }
            let temporary = directory.join(format!(".{name}.tmp"));
            let mut file = OpenOptions::new()
                .write(true)
                .create_new(true)
                .open(&temporary)
                .map_err(|error| io_failure("APPEND_TEMPORARY_CREATE_FAILED", &temporary, error))?;
            file.write_all(bytes.as_bytes())
                .and_then(|_| file.sync_all())
                .map_err(|error| io_failure("APPEND_WRITE_FAILED", &temporary, error))?;
            temporary_paths.push(temporary);
        }
        for ((name, _), temporary) in writes.iter().zip(temporary_paths.iter()) {
            let target = directory.join(name);
            fs::hard_link(temporary, &target)
                .map_err(|error| io_failure("APPEND_TARGET_CREATE_FAILED", &target, error))?;
            committed_paths.push(target);
        }
        Ok(())
    })();
    if result.is_err() {
        for path in &committed_paths {
            let _ = fs::remove_file(path);
        }
    }
    for path in &temporary_paths {
        let _ = fs::remove_file(path);
    }
    let _ = fs::remove_file(&lock_path);
    result
}

fn reject_in_progress_append(directory: &Path) -> Result<(), ReplayFailure> {
    if directory.join(".append.lock").exists() {
        return Err(ReplayFailure::new(
            "APPEND_IN_PROGRESS",
            directory.display().to_string(),
        ));
    }
    Ok(())
}

fn validate_identifier(value: &str, field: &str) -> Result<(), ReplayFailure> {
    let valid = !value.is_empty()
        && value.bytes().enumerate().all(|(index, byte)| {
            byte.is_ascii_alphanumeric()
                || (index > 0 && matches!(byte, b'.' | b'_' | b':' | b'/' | b'-'))
        });
    if !valid {
        return Err(ReplayFailure::new(
            "IDENTIFIER_INVALID",
            format!("{field}: {value}"),
        ));
    }
    Ok(())
}

fn validate_nonempty(value: &str, field: &str) -> Result<(), ReplayFailure> {
    if value.is_empty() {
        return Err(ReplayFailure::new("NONEMPTY_STRING_REQUIRED", field));
    }
    Ok(())
}

fn validate_sha256(value: &str, field: &str) -> Result<(), ReplayFailure> {
    if value.len() != 64
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit() && !byte.is_ascii_uppercase())
    {
        return Err(ReplayFailure::new(
            "SHA256_INVALID",
            format!("{field}: {value}"),
        ));
    }
    Ok(())
}

fn sha256(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn io_failure(code: &str, path: &Path, error: std::io::Error) -> ReplayFailure {
    ReplayFailure::new(code, format!("{}: {error}", path.display()))
}
