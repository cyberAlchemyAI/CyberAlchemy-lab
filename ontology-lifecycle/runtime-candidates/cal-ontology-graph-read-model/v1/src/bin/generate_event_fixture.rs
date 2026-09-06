use cal_ontology_graph_read_model::{
    GraphReadModel, ProjectedChallengeContract, RUNTIME_IDENTITY, RecoveryExpectation, SubjectKey,
};
use cal_ontology_lifecycle::{
    AuthorityEffect, AuthorityKindAndPosture, ChallengeContract, ChallengeMode,
    ConfidenceReference, ConsistentOntologyCut, DefinitionReference, EventFamily,
    ExactSemanticEventReference, GovernanceEvent, Lifecycle, OntologyGovernanceState,
    OntologyNodeSemanticState, OntologyRelationSemanticState, OntologySemanticState,
    OntologySubjectIdentity, ProjectedSubject, ProjectionSubjectReference, ProvenanceEntry,
    RelationDirection, SemanticEvent, SourceKind, SubjectKind, TypedPropertySet, ZERO_DIGEST,
    canonical_json, seal_governance_event, seal_semantic_event,
};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process::ExitCode;
use std::time::Instant;

const ONTOLOGY_ID: &str = "benchmark.synthetic.event-file-ontology";

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct EventFileProfile {
    node_count: usize,
    relations_per_node: usize,
    maximum_process_recovery_ns: u128,
    seed: u64,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Profiles {
    schema_version: String,
    profiles: BTreeMap<String, EventFileProfile>,
}

#[derive(Serialize)]
struct GenerationReceipt {
    schema_version: String,
    profile_id: String,
    config: EventFileProfile,
    generated_node_count: usize,
    generated_relation_count: usize,
    generated_subject_count: usize,
    semantic_event_file_count: usize,
    governance_event_file_count: usize,
    semantic_event_bytes: u64,
    governance_event_bytes: u64,
    semantic_event_directory_digest_sha256: String,
    governance_event_directory_digest_sha256: String,
    generation_ns: u128,
    expectation: RecoveryExpectation,
    fixture_kind: String,
    canonical_replay_source: bool,
    authority_effect: String,
}

struct TreeWriter {
    directory: PathBuf,
    hasher: Sha256,
    bytes: u64,
    count: usize,
}

impl TreeWriter {
    fn new(directory: PathBuf) -> Result<Self, String> {
        if directory.exists() {
            return Err(format!(
                "fixture directory already exists: {}",
                directory.display()
            ));
        }
        fs::create_dir_all(&directory).map_err(|error| error.to_string())?;
        Ok(Self {
            directory,
            hasher: Sha256::new(),
            bytes: 0,
            count: 0,
        })
    }

    fn write<T: Serialize>(
        &mut self,
        cursor: u64,
        event_id: &str,
        event: &T,
    ) -> Result<(), String> {
        let name = format!("{cursor:08}-{event_id}.json");
        let body = canonical_json(event).map_err(|failure| failure.to_string())?;
        fs::write(self.directory.join(&name), body.as_bytes())
            .map_err(|error| error.to_string())?;
        self.hasher.update(name.as_bytes());
        self.hasher.update([0]);
        self.hasher.update(body.as_bytes());
        self.hasher.update([0]);
        self.bytes += body.len() as u64;
        self.count += 1;
        Ok(())
    }

    fn finish(self) -> (String, u64, usize) {
        (
            format!("{:x}", self.hasher.finalize()),
            self.bytes,
            self.count,
        )
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(receipt) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&receipt).expect("serializable receipt")
            );
            ExitCode::SUCCESS
        }
        Err(error) => {
            eprintln!("GENERATION_BLOCK: {error}");
            ExitCode::from(2)
        }
    }
}

fn run() -> Result<GenerationReceipt, String> {
    let profile_id = argument("--profile").ok_or_else(|| "--profile is required".to_owned())?;
    let profiles_path =
        PathBuf::from(argument("--profiles").ok_or_else(|| "--profiles is required".to_owned())?);
    let output_root = PathBuf::from(
        argument("--output-root").ok_or_else(|| "--output-root is required".to_owned())?,
    );
    let profiles: Profiles =
        serde_json::from_slice(&fs::read(&profiles_path).map_err(|error| error.to_string())?)
            .map_err(|error| error.to_string())?;
    if profiles.schema_version != "cal-event-file-benchmark-profiles/v1-prototype" {
        return Err(format!(
            "unsupported profiles schema {}",
            profiles.schema_version
        ));
    }
    let config = profiles
        .profiles
        .get(&profile_id)
        .cloned()
        .ok_or_else(|| format!("unknown profile {profile_id}"))?;
    if config.node_count == 0 || config.relations_per_node == 0 {
        return Err("node_count and relations_per_node must be positive".to_owned());
    }

    let started = Instant::now();
    let mut semantic_writer = TreeWriter::new(output_root.join("semantic-events"))?;
    let mut governance_writer = TreeWriter::new(output_root.join("governance-events"))?;
    let subject_count = config.node_count * (config.relations_per_node + 1);
    let mut subjects = Vec::with_capacity(subject_count);
    let mut challenges = Vec::with_capacity(subject_count);

    for index in 0..config.node_count {
        let identity = OntologySubjectIdentity {
            subject_id: node_id(index),
            ontology_id: ONTOLOGY_ID.to_owned(),
            subject_kind: SubjectKind::Node,
            type_ref: format!("node-type-{}", index % 4),
        };
        let state = OntologySemanticState::Node(OntologyNodeSemanticState {
            identity: identity.clone(),
            lifecycle: Lifecycle::Active,
            label: format!("Synthetic event-file node {index}"),
            definition_or_claim:
                "Generated canonical-format benchmark fixture; no product meaning.".to_owned(),
            scope: "local event-file recovery experiment".to_owned(),
            semantic_components: Vec::new(),
            semantic_definition_refs: vec![DefinitionReference {
                definition_id: "BENCHMARK-SYNTHETIC-DEFINITION".to_owned(),
                selector_sha256: format!("{:064x}", config.seed),
            }],
            typed_properties: empty_properties(),
            use_obligations: Vec::new(),
            forbidden_collapse: Vec::new(),
            profile_ref: "test-empty-profile/v1".to_owned(),
        });
        append_subject(
            &mut semantic_writer,
            &mut governance_writer,
            &mut subjects,
            &mut challenges,
            identity,
            state,
        )?;
    }
    for source_index in 0..config.node_count {
        for edge_index in 0..config.relations_per_node {
            let target_index = (source_index
                .wrapping_mul(17)
                .wrapping_add(edge_index.wrapping_mul(31))
                .wrapping_add(config.seed as usize))
                % config.node_count;
            let identity = OntologySubjectIdentity {
                subject_id: format!("relation-{source_index:08}-{edge_index:02}"),
                ontology_id: ONTOLOGY_ID.to_owned(),
                subject_kind: SubjectKind::Relation,
                type_ref: format!("relation-type-{}", edge_index % 4),
            };
            let state = OntologySemanticState::Relation(OntologyRelationSemanticState {
                identity: identity.clone(),
                lifecycle: Lifecycle::Active,
                source_node_id: node_id(source_index),
                target_node_id: node_id(target_index),
                direction: RelationDirection::Directed,
                typed_properties: empty_properties(),
                forbidden_collapse: Vec::new(),
            });
            append_subject(
                &mut semantic_writer,
                &mut governance_writer,
                &mut subjects,
                &mut challenges,
                identity,
                state,
            )?;
        }
    }

    let references = subjects
        .iter()
        .map(|subject| ProjectionSubjectReference {
            identity: subject.identity.clone(),
            source_event_id: subject.source_event_id.clone(),
            source_event_digest: subject.source_event_digest.clone(),
            source_cursor: subject.source_cursor,
        })
        .collect::<Vec<_>>();
    let source_event_set_digest = sha256(
        canonical_json(&references)
            .map_err(|failure| failure.to_string())?
            .as_bytes(),
    );
    let cut = ConsistentOntologyCut {
        schema_version: "cal-consistent-ontology-cut/v2-candidate".to_owned(),
        authority_effect: AuthorityEffect::None,
        semantic_cursor: subject_count as u64,
        source_event_count: subject_count,
        source_event_set_digest: source_event_set_digest.clone(),
        subjects,
    };
    let model = GraphReadModel::from_calculated_cut(cut, challenges)
        .map_err(|failure| failure.to_string())?;
    let expectation = RecoveryExpectation {
        runtime_identity: RUNTIME_IDENTITY.to_owned(),
        semantic_cursor: subject_count as u64,
        source_event_count: subject_count,
        source_event_set_digest,
        expected_index_digest: model.metadata().index_digest.clone(),
    };
    let (semantic_digest, semantic_bytes, semantic_count) = semantic_writer.finish();
    let (governance_digest, governance_bytes, governance_count) = governance_writer.finish();
    Ok(GenerationReceipt {
        schema_version: "cal-event-file-generation-receipt/v1-prototype".to_owned(),
        profile_id,
        config,
        generated_node_count: model.metadata().node_count,
        generated_relation_count: model.metadata().relation_count,
        generated_subject_count: subject_count,
        semantic_event_file_count: semantic_count,
        governance_event_file_count: governance_count,
        semantic_event_bytes: semantic_bytes,
        governance_event_bytes: governance_bytes,
        semantic_event_directory_digest_sha256: semantic_digest,
        governance_event_directory_digest_sha256: governance_digest,
        generation_ns: started.elapsed().as_nanos(),
        expectation,
        fixture_kind: "synthetic-canonical-format-event-files".to_owned(),
        canonical_replay_source: false,
        authority_effect: "none".to_owned(),
    })
}

fn append_subject(
    semantic_writer: &mut TreeWriter,
    governance_writer: &mut TreeWriter,
    subjects: &mut Vec<ProjectedSubject>,
    challenges: &mut Vec<ProjectedChallengeContract>,
    identity: OntologySubjectIdentity,
    semantic_state: OntologySemanticState,
) -> Result<(), String> {
    let cursor = subjects.len() as u64 + 1;
    let semantic_event_id = format!("synthetic-semantic-{cursor:08}");
    let mut semantic = SemanticEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Semantic,
        event_id: semantic_event_id.clone(),
        event_digest: ZERO_DIGEST.to_owned(),
        stream_id: identity.semantic_stream_id(),
        subject_identity: identity.clone(),
        previous_event_digest: None,
        semantic_cursor: cursor,
        complete_resulting_semantic_state: semantic_state.clone(),
    };
    seal_semantic_event(&mut semantic).map_err(|failure| failure.to_string())?;
    semantic_writer.write(cursor, &semantic_event_id, &semantic)?;

    let semantic_ref = ExactSemanticEventReference {
        semantic_event_id: semantic_event_id.clone(),
        semantic_event_digest: semantic.event_digest.clone(),
        semantic_cursor: cursor,
    };
    let contract = challenge_contract();
    let governance_event_id = format!("synthetic-governance-{cursor:08}");
    let mut governance = GovernanceEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Governance,
        event_id: governance_event_id.clone(),
        event_digest: ZERO_DIGEST.to_owned(),
        stream_id: identity.governance_stream_id(),
        semantic_ref: semantic_ref.clone(),
        governance_cursor: cursor,
        previous_event_digest: None,
        complete_resulting_governance_state: OntologyGovernanceState {
            semantic_ref,
            provenance: vec![ProvenanceEntry {
                source_ref: "synthetic-event-file-generator/v1".to_owned(),
                relation: "generated-for-recovery-experiment".to_owned(),
                operation: "generate-canonical-format-fixture".to_owned(),
                owner_route: "benchmark-owner".to_owned(),
                posture: "non-authoritative-synthetic-evidence".to_owned(),
            }],
            owner_route: "benchmark-owner".to_owned(),
            candidate_or_maturity_status: "synthetic".to_owned(),
            promotion_state_or_handle: "not-promoted".to_owned(),
            authority_kind_and_posture: AuthorityKindAndPosture {
                kind: "benchmark-fixture".to_owned(),
                posture: "non-authoritative".to_owned(),
            },
            authority_effect: AuthorityEffect::None,
            evidence_confidence: ConfidenceReference {
                scheme_ref: "benchmark-confidence/v1".to_owned(),
                level: "generated".to_owned(),
            },
            commitment_confidence: ConfidenceReference {
                scheme_ref: "benchmark-confidence/v1".to_owned(),
                level: "none".to_owned(),
            },
            challenge_contract: contract.clone(),
            residue: Vec::new(),
            conflicts: Vec::new(),
            drift_owner: "benchmark-owner".to_owned(),
            invalidation_route: "benchmark-owner".to_owned(),
        },
    };
    seal_governance_event(&mut governance).map_err(|failure| failure.to_string())?;
    governance_writer.write(cursor, &governance_event_id, &governance)?;

    let subject = ProjectedSubject {
        identity: identity.clone(),
        source_event_id: semantic_event_id.clone(),
        source_event_digest: semantic.event_digest.clone(),
        source_cursor: cursor,
        semantic_state,
    };
    challenges.push(ProjectedChallengeContract {
        subject: SubjectKey::new(ONTOLOGY_ID, &identity.subject_id),
        semantic_event_id,
        semantic_event_digest: semantic.event_digest,
        semantic_cursor: cursor,
        contract,
    });
    subjects.push(subject);
    Ok(())
}

fn challenge_contract() -> ChallengeContract {
    ChallengeContract {
        challenge_response: "Inspect generated event-file evidence.".to_owned(),
        valid_challenge_modes: vec![
            ChallengeMode::Evidence,
            ChallengeMode::Contradiction,
            ChallengeMode::OwnerReview,
        ],
        contradiction_edges: Vec::new(),
        validation_edges: Vec::new(),
        owner_route: "benchmark-owner".to_owned(),
        resolution_gate: "none".to_owned(),
        blocking_questions: Vec::new(),
        challenge_residue_route: "benchmark-report".to_owned(),
    }
}

fn empty_properties() -> TypedPropertySet {
    TypedPropertySet {
        profile_ref: "test-empty-profile/v1".to_owned(),
        values: BTreeMap::new(),
    }
}

fn node_id(index: usize) -> String {
    format!("node-{index:08}")
}

fn sha256(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn argument(name: &str) -> Option<String> {
    let arguments = env::args().collect::<Vec<_>>();
    arguments
        .iter()
        .position(|argument| argument == name)
        .and_then(|index| arguments.get(index + 1).cloned())
}
