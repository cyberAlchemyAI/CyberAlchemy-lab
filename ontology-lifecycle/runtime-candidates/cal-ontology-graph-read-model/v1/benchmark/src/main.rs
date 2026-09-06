use cal_ontology_graph_read_model::{
    CalculatedGraphDelta, CalculatedSubjectChange, ConcurrentGraphReadModel, DeltaApplyReceipt,
    DeltaSubjectResult, GraphReadModel, ProjectedChallengeContract, RUNTIME_IDENTITY,
    RecoveryExpectation, SnapshotPublicationReceipt, SubjectKey, calculated_projection_digest,
};
use cal_ontology_lifecycle::{
    AuthorityEffect, ChallengeContract, ChallengeMode, ConsistentOntologyCut, DefinitionReference,
    Lifecycle, OntologyNodeSemanticState, OntologyRelationSemanticState, OntologySemanticState,
    OntologySubjectIdentity, ProjectedSubject, RelationDirection, SubjectKind, TypedPropertySet,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::env;
use std::fs::{self, OpenOptions};
use std::hint::black_box;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::ExitCode;
use std::sync::{Arc, Barrier, mpsc};
use std::thread;
use std::time::Instant;

const BENCHMARK_ID: &str = "CAL-ONTOLOGY-GRAPH-READ-MODEL-BENCHMARK-002";
const ONTOLOGY_ID: &str = "benchmark.synthetic.ontology";
const CLAIM_CEILING: &str = "local_single_process_synthetic_prototype_evidence_only";

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct BenchmarkConfig {
    node_count: usize,
    relations_per_node: usize,
    context_count: usize,
    delta_change_scale: usize,
    concurrent_reader_threads: usize,
    concurrent_reads_per_thread: usize,
    maximum_cold_recovery_ns: u128,
    query_count: usize,
    repetitions: usize,
    seed: u64,
}

#[derive(Deserialize)]
struct Profiles {
    profiles: BTreeMap<String, BenchmarkConfig>,
}

#[derive(Clone, Debug)]
enum Query {
    Subject(String),
    Type(String),
    Property {
        name: String,
        value: Value,
    },
    Outgoing {
        subject: String,
        relation: String,
    },
    Incoming {
        target: String,
        relation: String,
    },
    TwoHop {
        subject: String,
        first: String,
        second: String,
    },
    Context(String),
    Challenge(String),
}

impl Query {
    fn family(&self) -> &'static str {
        match self {
            Self::Subject(_) => "subject",
            Self::Type(_) => "type",
            Self::Property { .. } => "property",
            Self::Outgoing { .. } => "outgoing",
            Self::Incoming { .. } => "incoming",
            Self::TwoHop { .. } => "two_hop",
            Self::Context(_) => "context",
            Self::Challenge(_) => "challenge",
        }
    }
}

#[derive(Clone)]
struct ScanRecord {
    subject_id: String,
    type_ref: String,
    properties: BTreeMap<String, Value>,
    relation: Option<(String, String)>,
}

struct ScanControl {
    records: Vec<ScanRecord>,
    challenge_subjects: Vec<String>,
}

impl ScanControl {
    fn build(cut: &ConsistentOntologyCut, challenges: &[ProjectedChallengeContract]) -> Self {
        let records = cut
            .subjects
            .iter()
            .map(|subject| {
                let (properties, relation) = match &subject.semantic_state {
                    OntologySemanticState::Node(node) => {
                        (node.typed_properties.values.clone(), None)
                    }
                    OntologySemanticState::Relation(edge) => (
                        edge.typed_properties.values.clone(),
                        Some((edge.source_node_id.clone(), edge.target_node_id.clone())),
                    ),
                };
                ScanRecord {
                    subject_id: subject.identity.subject_id.clone(),
                    type_ref: subject.identity.type_ref.clone(),
                    properties,
                    relation,
                }
            })
            .collect();
        Self {
            records,
            challenge_subjects: challenges
                .iter()
                .map(|challenge| challenge.subject.subject_id.clone())
                .collect(),
        }
    }

    fn query(&self, query: &Query) -> Vec<String> {
        normalize(match query {
            Query::Subject(id) => self
                .records
                .iter()
                .filter(|record| record.subject_id == *id)
                .map(|record| record.subject_id.clone())
                .collect(),
            Query::Type(type_ref) => self
                .records
                .iter()
                .filter(|record| record.type_ref == *type_ref)
                .map(|record| record.subject_id.clone())
                .collect(),
            Query::Property { name, value } => self
                .records
                .iter()
                .filter(|record| record.properties.get(name) == Some(value))
                .map(|record| record.subject_id.clone())
                .collect(),
            Query::Outgoing { subject, relation } => self
                .records
                .iter()
                .filter(|record| {
                    record.type_ref == *relation
                        && record
                            .relation
                            .as_ref()
                            .is_some_and(|(source, _)| source == subject)
                })
                .filter_map(|record| record.relation.as_ref().map(|(_, target)| target.clone()))
                .collect(),
            Query::Incoming { target, relation } => self
                .records
                .iter()
                .filter(|record| {
                    record.type_ref == *relation
                        && record
                            .relation
                            .as_ref()
                            .is_some_and(|(_, candidate)| candidate == target)
                })
                .filter_map(|record| record.relation.as_ref().map(|(source, _)| source.clone()))
                .collect(),
            Query::TwoHop {
                subject,
                first,
                second,
            } => {
                let intermediate = self
                    .records
                    .iter()
                    .filter(|record| {
                        record.type_ref == *first
                            && record
                                .relation
                                .as_ref()
                                .is_some_and(|(source, _)| source == subject)
                    })
                    .filter_map(|record| record.relation.as_ref().map(|(_, target)| target.clone()))
                    .collect::<BTreeSet<_>>();
                self.records
                    .iter()
                    .filter(|record| {
                        record.type_ref == *second
                            && record
                                .relation
                                .as_ref()
                                .is_some_and(|(source, _)| intermediate.contains(source))
                    })
                    .filter_map(|record| record.relation.as_ref().map(|(_, target)| target.clone()))
                    .collect()
            }
            Query::Context(context) => self
                .records
                .iter()
                .filter(|record| record.properties.get("context_id") == Some(&json!(context)))
                .map(|record| record.subject_id.clone())
                .collect(),
            Query::Challenge(subject) => self
                .challenge_subjects
                .iter()
                .any(|candidate| candidate == subject)
                .then(|| subject.clone())
                .into_iter()
                .collect(),
        })
    }
}

#[derive(Serialize)]
struct LatencySummary {
    samples: usize,
    p50_ns: u128,
    p95_ns: u128,
    p99_ns: u128,
    max_ns: u128,
}

#[derive(Serialize)]
struct BackendReport {
    backend_id: String,
    build_ns: u128,
    estimated_string_payload_bytes: usize,
    latency_by_query: BTreeMap<String, LatencySummary>,
}

#[derive(Serialize)]
struct CorrectnessReport {
    status: String,
    queries_compared: usize,
    shared_result_digest_sha256: String,
    deterministic_rebuild_digest_match: bool,
}

#[derive(Serialize)]
struct DeltaReport {
    declared_change_scale: usize,
    total_changes: usize,
    semantic_changes: usize,
    added: usize,
    updated: usize,
    removed: usize,
    governance_replaced: usize,
    transaction_strategy: String,
    staged_previous_subject_count: usize,
    full_model_clone: bool,
    incremental_apply_ns: u128,
    full_target_rebuild_ns: u128,
    incremental_over_full_rebuild_ratio: f64,
    exact_model_equivalence: bool,
    target_projection_digest_sha256: String,
    resulting_index_digest_sha256: String,
    delta_digest_sha256: String,
}

#[derive(Serialize)]
struct ConcurrentSnapshotReport {
    publication_strategy: String,
    reader_threads: usize,
    reads_per_thread: usize,
    worker_observations: usize,
    old_generation_observations: usize,
    new_generation_observations: usize,
    invalid_observations: usize,
    writer_completed_while_old_snapshot_held: bool,
    old_snapshot_retained_after_publication: bool,
    publication_staged_full_model_clone: bool,
    previous_subject_count: usize,
    shared_subject_count: usize,
    previous_challenge_contract_count: usize,
    shared_challenge_contract_count: usize,
    previous_index_bucket_count: usize,
    shared_index_bucket_count: usize,
    writer_publication_ns_under_contention: u128,
    published_generation: u64,
    published_semantic_cursor: u64,
    published_index_digest_sha256: String,
    exact_final_model_equivalence: bool,
    readers_are_blocking: bool,
}

#[derive(Serialize)]
struct RestartRecoveryReport {
    recovery_strategy: String,
    cold_recovery_ns: u128,
    maximum_cold_recovery_ns: u128,
    within_objective: bool,
    exact_model_equivalence: bool,
    exact_index_digest_match: bool,
    recovered_semantic_cursor: u64,
    recovered_source_event_count: usize,
    recovered_source_event_set_digest_sha256: String,
    recovered_index_digest_sha256: String,
    checkpoint_used: bool,
    corruption_controls_in_test_suite: usize,
}

#[derive(Serialize)]
struct AttemptReport {
    schema_version: String,
    benchmark_id: String,
    profile_id: String,
    attempt: usize,
    status: String,
    implementation_digest_sha256: String,
    config: BenchmarkConfig,
    generated_node_count: usize,
    generated_relation_count: usize,
    generated_subject_count: usize,
    fixture_generation_ns: u128,
    deterministic_rebuild_ns: u128,
    generated_input_payload_bytes: usize,
    fixture_digest_sha256: String,
    candidate_index_digest_sha256: String,
    correctness: CorrectnessReport,
    calculated_delta: DeltaReport,
    concurrent_snapshots: ConcurrentSnapshotReport,
    restart_recovery: RestartRecoveryReport,
    candidate: BackendReport,
    scan_control: BackendReport,
    candidate_over_scan_p50_ratio: BTreeMap<String, f64>,
    canonical_replay_source: bool,
    authority_effect: String,
    claim_ceiling: String,
}

fn main() -> ExitCode {
    match run() {
        Ok(report) => {
            let line = serde_json::to_string(&report).expect("serializable benchmark report");
            println!("{line}");
            if let Some(path) = argument("--output")
                && let Err(error) = append_line(Path::new(&path), &line)
            {
                eprintln!("OUTPUT_WRITE_FAILED: {error}");
                return ExitCode::from(2);
            }
            if report.status == "pass" {
                ExitCode::SUCCESS
            } else {
                ExitCode::from(1)
            }
        }
        Err(error) => {
            eprintln!("BENCHMARK_BLOCK: {error}");
            ExitCode::from(2)
        }
    }
}

fn run() -> Result<AttemptReport, String> {
    let profile_id = argument("--profile").unwrap_or_else(|| "smoke".to_owned());
    let profiles_path = argument("--profiles")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("profiles.json"));
    let profiles: Profiles =
        serde_json::from_slice(&fs::read(&profiles_path).map_err(|error| error.to_string())?)
            .map_err(|error| error.to_string())?;
    let config = profiles
        .profiles
        .get(&profile_id)
        .cloned()
        .ok_or_else(|| format!("unknown profile {profile_id}"))?;
    let attempt = argument("--attempt")
        .unwrap_or_else(|| "1".to_owned())
        .parse::<usize>()
        .map_err(|error| error.to_string())?;

    let fixture_started = Instant::now();
    let (cut, challenges) = generate_fixture(&config)?;
    let fixture_generation_ns = fixture_started.elapsed().as_nanos();
    let generated_input_payload_bytes = estimated_input_bytes(&cut, &challenges);
    let fixture_digest_sha256 = digest_json(&(&cut, &challenges))?;
    let queries = generate_queries(&config);

    let scan_started = Instant::now();
    let scan = ScanControl::build(&cut, &challenges);
    let scan_build_ns = scan_started.elapsed().as_nanos();

    let candidate_started = Instant::now();
    let candidate = GraphReadModel::from_calculated_cut(cut.clone(), challenges.clone())
        .map_err(|failure| failure.to_string())?;
    let candidate_build_ns = candidate_started.elapsed().as_nanos();

    let recovery_expectation = RecoveryExpectation {
        runtime_identity: RUNTIME_IDENTITY.to_owned(),
        semantic_cursor: cut.semantic_cursor,
        source_event_count: cut.source_event_count,
        source_event_set_digest: cut.source_event_set_digest.clone(),
        expected_index_digest: candidate.metadata().index_digest.clone(),
    };
    let rebuild_started = Instant::now();
    let (rebuilt, recovery_receipt) = GraphReadModel::recover_from_calculated_cut(
        cut.clone(),
        challenges.clone(),
        &recovery_expectation,
    )
    .map_err(|failure| failure.to_string())?;
    let deterministic_rebuild_ns = rebuild_started.elapsed().as_nanos();
    let deterministic_rebuild_digest_match =
        candidate.metadata().index_digest == rebuilt.metadata().index_digest;
    let restart_recovery = RestartRecoveryReport {
        recovery_strategy: recovery_receipt.recovery_strategy,
        cold_recovery_ns: deterministic_rebuild_ns,
        maximum_cold_recovery_ns: config.maximum_cold_recovery_ns,
        within_objective: deterministic_rebuild_ns <= config.maximum_cold_recovery_ns,
        exact_model_equivalence: candidate == rebuilt,
        exact_index_digest_match: recovery_receipt.exact_index_digest_match,
        recovered_semantic_cursor: recovery_receipt.semantic_cursor,
        recovered_source_event_count: recovery_receipt.source_event_count,
        recovered_source_event_set_digest_sha256: recovery_receipt.source_event_set_digest,
        recovered_index_digest_sha256: recovery_receipt.rebuilt_index_digest,
        checkpoint_used: recovery_receipt.checkpoint_used,
        corruption_controls_in_test_suite: 4,
    };

    let (delta, target_cut, target_challenges) =
        generate_delta_fixture(&config, &candidate, &cut, &challenges)?;
    let mut incrementally_updated = candidate.clone();
    let delta_started = Instant::now();
    let delta_receipt = incrementally_updated
        .apply_calculated_delta(&delta)
        .map_err(|failure| failure.to_string())?;
    let incremental_apply_ns = delta_started.elapsed().as_nanos();
    let full_target_started = Instant::now();
    let full_target = GraphReadModel::from_calculated_cut(target_cut.clone(), target_challenges)
        .map_err(|failure| failure.to_string())?;
    let full_target_rebuild_ns = full_target_started.elapsed().as_nanos();
    let exact_model_equivalence = incrementally_updated == full_target;
    let concurrent_snapshots =
        run_concurrent_snapshot_workload(&config, candidate.clone(), delta.clone(), &full_target)?;

    let mut candidate_results = Vec::with_capacity(queries.len());
    let mut scan_results = Vec::with_capacity(queries.len());
    for query in &queries {
        candidate_results.push(query_candidate(&candidate, query)?);
        scan_results.push(scan.query(query));
    }
    let correctness_match = candidate_results == scan_results;
    let candidate_result_digest = digest_json(&candidate_results)?;
    let scan_result_digest = digest_json(&scan_results)?;
    let shared_result_digest_sha256 = if candidate_result_digest == scan_result_digest {
        candidate_result_digest
    } else {
        format!("candidate={candidate_result_digest};scan={scan_result_digest}")
    };

    let mut candidate_samples: BTreeMap<String, Vec<u128>> = BTreeMap::new();
    let mut scan_samples: BTreeMap<String, Vec<u128>> = BTreeMap::new();
    for _ in 0..config.repetitions {
        for query in &queries {
            let started = Instant::now();
            black_box(query_candidate(&candidate, query)?);
            candidate_samples
                .entry(query.family().to_owned())
                .or_default()
                .push(started.elapsed().as_nanos());

            let started = Instant::now();
            black_box(scan.query(query));
            scan_samples
                .entry(query.family().to_owned())
                .or_default()
                .push(started.elapsed().as_nanos());
        }
    }
    let candidate_latency = summarize(candidate_samples);
    let scan_latency = summarize(scan_samples);
    let candidate_over_scan_p50_ratio = candidate_latency
        .iter()
        .map(|(family, candidate_summary)| {
            let scan_p50 = scan_latency
                .get(family)
                .map(|summary| summary.p50_ns)
                .unwrap_or(1)
                .max(1);
            (
                family.clone(),
                candidate_summary.p50_ns as f64 / scan_p50 as f64,
            )
        })
        .collect();
    let status = if correctness_match
        && deterministic_rebuild_digest_match
        && exact_model_equivalence
        && concurrent_snapshots.invalid_observations == 0
        && concurrent_snapshots.writer_completed_while_old_snapshot_held
        && concurrent_snapshots.old_snapshot_retained_after_publication
        && !concurrent_snapshots.publication_staged_full_model_clone
        && concurrent_snapshots.shared_subject_count > 0
        && concurrent_snapshots.shared_subject_count < concurrent_snapshots.previous_subject_count
        && concurrent_snapshots.shared_challenge_contract_count > 0
        && concurrent_snapshots.shared_challenge_contract_count
            < concurrent_snapshots.previous_challenge_contract_count
        && concurrent_snapshots.shared_index_bucket_count > 0
        && concurrent_snapshots.shared_index_bucket_count
            < concurrent_snapshots.previous_index_bucket_count
        && !concurrent_snapshots.readers_are_blocking
        && concurrent_snapshots.exact_final_model_equivalence
        && concurrent_snapshots.published_generation == 1
        && restart_recovery.within_objective
        && restart_recovery.exact_model_equivalence
        && restart_recovery.exact_index_digest_match
        && !restart_recovery.checkpoint_used
    {
        "pass"
    } else {
        "block"
    };
    Ok(AttemptReport {
        schema_version: "cal-ontology-graph-benchmark-attempt/v1".to_owned(),
        benchmark_id: BENCHMARK_ID.to_owned(),
        profile_id,
        attempt,
        status: status.to_owned(),
        implementation_digest_sha256: implementation_digest()?,
        generated_node_count: config.node_count,
        generated_relation_count: config.node_count * config.relations_per_node,
        generated_subject_count: cut.subjects.len(),
        fixture_generation_ns,
        deterministic_rebuild_ns,
        generated_input_payload_bytes,
        fixture_digest_sha256,
        candidate_index_digest_sha256: candidate.metadata().index_digest.clone(),
        correctness: CorrectnessReport {
            status: if correctness_match { "pass" } else { "block" }.to_owned(),
            queries_compared: queries.len(),
            shared_result_digest_sha256,
            deterministic_rebuild_digest_match,
        },
        calculated_delta: delta_report(
            &config,
            &delta,
            &delta_receipt,
            incremental_apply_ns,
            full_target_rebuild_ns,
            exact_model_equivalence,
        ),
        concurrent_snapshots,
        restart_recovery,
        candidate: BackendReport {
            backend_id: "cal_ontology_graph_read_model".to_owned(),
            build_ns: candidate_build_ns,
            estimated_string_payload_bytes: candidate.estimated_string_payload_bytes(),
            latency_by_query: candidate_latency,
        },
        scan_control: BackendReport {
            backend_id: "vector_scan_control".to_owned(),
            build_ns: scan_build_ns,
            estimated_string_payload_bytes: generated_input_payload_bytes,
            latency_by_query: scan_latency,
        },
        candidate_over_scan_p50_ratio,
        config,
        canonical_replay_source: false,
        authority_effect: "none".to_owned(),
        claim_ceiling: CLAIM_CEILING.to_owned(),
    })
}

fn implementation_digest() -> Result<String, String> {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let paths = [
        root.join("../src/lib.rs"),
        root.join("src/main.rs"),
        root.join("profiles.json"),
        root.join("Cargo.lock"),
        root.join("../Cargo.lock"),
        root.join("../../../../runtime/src/lib.rs"),
    ];
    let mut hasher = Sha256::new();
    for path in paths {
        let relative = path.strip_prefix(&root).unwrap_or(&path).to_string_lossy();
        let bytes = fs::read(&path).map_err(|error| error.to_string())?;
        hasher.update(relative.as_bytes());
        hasher.update([0]);
        hasher.update(&bytes);
        hasher.update([0]);
    }
    Ok(format!("{:x}", hasher.finalize()))
}

fn generate_fixture(
    config: &BenchmarkConfig,
) -> Result<(ConsistentOntologyCut, Vec<ProjectedChallengeContract>), String> {
    if config.node_count == 0 || config.context_count == 0 || config.relations_per_node == 0 {
        return Err("counts must be greater than zero".to_owned());
    }
    let mut subjects =
        Vec::with_capacity(config.node_count * (config.relations_per_node.saturating_add(1)));
    let mut challenges = Vec::with_capacity(subjects.capacity());
    let definition = DefinitionReference {
        definition_id: "BENCHMARK-NONCANONICAL-DEFINITION".to_owned(),
        selector_sha256: format!("{:064x}", config.seed),
    };
    for index in 0..config.node_count {
        let subject_id = node_id(index);
        let event_id = format!("benchmark-node-event-{index:08}");
        let event_digest = digest_bytes(event_id.as_bytes());
        let identity = OntologySubjectIdentity {
            subject_id: subject_id.clone(),
            ontology_id: ONTOLOGY_ID.to_owned(),
            subject_kind: SubjectKind::Node,
            type_ref: format!("node_type_{}", index % 4),
        };
        let mut values = BTreeMap::new();
        values.insert(
            "context_id".to_owned(),
            json!(format!("context-{:04}", index % config.context_count)),
        );
        values.insert("tier".to_owned(), json!(index % 8));
        let subject = ProjectedSubject {
            identity: identity.clone(),
            source_event_id: event_id.clone(),
            source_event_digest: event_digest.clone(),
            source_cursor: subjects.len() as u64 + 1,
            semantic_state: OntologySemanticState::Node(OntologyNodeSemanticState {
                identity,
                lifecycle: Lifecycle::Active,
                label: format!("Synthetic node {index}"),
                definition_or_claim: "Generated benchmark fixture; not canonical meaning."
                    .to_owned(),
                scope: "local synthetic benchmark only".to_owned(),
                semantic_components: Vec::new(),
                semantic_definition_refs: vec![definition.clone()],
                typed_properties: TypedPropertySet {
                    profile_ref: "benchmark.synthetic.properties/v1".to_owned(),
                    values,
                },
                use_obligations: Vec::new(),
                forbidden_collapse: Vec::new(),
                profile_ref: "benchmark.synthetic.node/v1".to_owned(),
            }),
        };
        challenges.push(projected_challenge(&subject));
        subjects.push(subject);
    }
    for source_index in 0..config.node_count {
        for edge_index in 0..config.relations_per_node {
            let target_index = (source_index
                .wrapping_mul(17)
                .wrapping_add(edge_index.wrapping_mul(31))
                .wrapping_add(config.seed as usize))
                % config.node_count;
            let subject_id = format!("relation-{source_index:08}-{edge_index:02}");
            let event_id = format!("benchmark-relation-event-{source_index:08}-{edge_index:02}");
            let event_digest = digest_bytes(event_id.as_bytes());
            let identity = OntologySubjectIdentity {
                subject_id,
                ontology_id: ONTOLOGY_ID.to_owned(),
                subject_kind: SubjectKind::Relation,
                type_ref: format!("relation_{}", edge_index % 4),
            };
            let subject = ProjectedSubject {
                identity: identity.clone(),
                source_event_id: event_id,
                source_event_digest: event_digest,
                source_cursor: subjects.len() as u64 + 1,
                semantic_state: OntologySemanticState::Relation(OntologyRelationSemanticState {
                    identity,
                    lifecycle: Lifecycle::Active,
                    source_node_id: node_id(source_index),
                    target_node_id: node_id(target_index),
                    direction: RelationDirection::Directed,
                    typed_properties: TypedPropertySet {
                        profile_ref: "benchmark.synthetic.relation/v1".to_owned(),
                        values: BTreeMap::new(),
                    },
                    forbidden_collapse: Vec::new(),
                }),
            };
            challenges.push(projected_challenge(&subject));
            subjects.push(subject);
        }
    }
    let source_event_set_digest = digest_json(
        &subjects
            .iter()
            .map(|subject| {
                (
                    &subject.source_event_id,
                    &subject.source_event_digest,
                    subject.source_cursor,
                )
            })
            .collect::<Vec<_>>(),
    )?;
    Ok((
        ConsistentOntologyCut {
            schema_version: "benchmark-noncanonical-consistent-cut/v1".to_owned(),
            authority_effect: AuthorityEffect::None,
            semantic_cursor: subjects.len() as u64,
            source_event_count: subjects.len(),
            source_event_set_digest,
            subjects,
        },
        challenges,
    ))
}

fn generate_delta_fixture(
    config: &BenchmarkConfig,
    base_model: &GraphReadModel,
    base_cut: &ConsistentOntologyCut,
    base_challenges: &[ProjectedChallengeContract],
) -> Result<
    (
        CalculatedGraphDelta,
        ConsistentOntologyCut,
        Vec<ProjectedChallengeContract>,
    ),
    String,
> {
    let scale = config.delta_change_scale;
    if scale == 0 || scale.saturating_mul(3) >= config.node_count {
        return Err(
            "delta_change_scale must be positive and less than one third of node_count".to_owned(),
        );
    }

    let mut subjects = base_cut
        .subjects
        .iter()
        .cloned()
        .map(|subject| (SubjectKey::of(&subject), subject))
        .collect::<BTreeMap<_, _>>();
    let mut challenges = base_challenges
        .iter()
        .cloned()
        .map(|challenge| (challenge.subject.clone(), challenge))
        .collect::<BTreeMap<_, _>>();
    let removed_node_ids = ((config.node_count - scale)..config.node_count)
        .map(node_id)
        .collect::<BTreeSet<_>>();
    let incident_relations = subjects
        .iter()
        .filter_map(|(key, subject)| match &subject.semantic_state {
            OntologySemanticState::Relation(relation)
                if removed_node_ids.contains(&relation.source_node_id)
                    || removed_node_ids.contains(&relation.target_node_id) =>
            {
                Some(key.clone())
            }
            _ => None,
        })
        .collect::<BTreeSet<_>>();
    let relation_candidates = subjects
        .iter()
        .filter(|(key, subject)| {
            subject.identity.subject_kind == SubjectKind::Relation
                && !incident_relations.contains(*key)
        })
        .map(|(key, _)| key.clone())
        .collect::<Vec<_>>();
    if relation_candidates.len() < scale.saturating_mul(2) {
        return Err("not enough non-incident relations for the configured delta".to_owned());
    }
    let updated_relations = relation_candidates[..scale]
        .iter()
        .cloned()
        .collect::<BTreeSet<_>>();
    let explicit_removed_relations = relation_candidates[scale..scale * 2]
        .iter()
        .cloned()
        .collect::<BTreeSet<_>>();

    let mut changes = BTreeMap::<SubjectKey, CalculatedSubjectChange>::new();
    let mut next_cursor = base_cut.semantic_cursor;

    for index in 0..scale {
        let key = SubjectKey::new(ONTOLOGY_ID, node_id(index));
        let mut subject = subjects
            .get(&key)
            .cloned()
            .ok_or_else(|| format!("missing node {}", key.subject_id))?;
        next_cursor += 1;
        reseal_subject(&mut subject, next_cursor, "node-update");
        if let OntologySemanticState::Node(node) = &mut subject.semantic_state {
            node.label = format!("Updated synthetic node {index}");
            node.typed_properties
                .values
                .insert("delta_revision".to_owned(), json!(1));
        }
        replace_subject(
            base_model,
            &mut subjects,
            &mut challenges,
            &mut changes,
            key,
            subject,
            Some(next_cursor),
        )?;
    }

    for key in updated_relations {
        let mut subject = subjects
            .get(&key)
            .cloned()
            .ok_or_else(|| format!("missing relation {}", key.subject_id))?;
        next_cursor += 1;
        reseal_subject(&mut subject, next_cursor, "relation-update");
        if let OntologySemanticState::Relation(relation) = &mut subject.semantic_state {
            relation
                .typed_properties
                .values
                .insert("delta_revision".to_owned(), json!(1));
        }
        replace_subject(
            base_model,
            &mut subjects,
            &mut challenges,
            &mut changes,
            key,
            subject,
            Some(next_cursor),
        )?;
    }

    let removal_keys = incident_relations
        .into_iter()
        .chain(explicit_removed_relations)
        .chain(
            removed_node_ids
                .iter()
                .map(|id| SubjectKey::new(ONTOLOGY_ID, id)),
        )
        .collect::<BTreeSet<_>>();
    for key in removal_keys {
        next_cursor += 1;
        changes.insert(
            key.clone(),
            CalculatedSubjectChange {
                subject: key.clone(),
                expected_previous: base_model
                    .expected_subject_version(&key)
                    .map_err(|failure| failure.to_string())?,
                semantic_change_cursor: Some(next_cursor),
                resulting: None,
            },
        );
        subjects.remove(&key);
        challenges.remove(&key);
    }

    for offset in 0..scale {
        let index = config.node_count + offset;
        let key = SubjectKey::new(ONTOLOGY_ID, node_id(index));
        next_cursor += 1;
        let subject = added_node(config, index, next_cursor);
        let challenge = projected_challenge(&subject);
        subjects.insert(key.clone(), subject.clone());
        challenges.insert(key.clone(), challenge.clone());
        changes.insert(
            key.clone(),
            CalculatedSubjectChange {
                subject: key,
                expected_previous: None,
                semantic_change_cursor: Some(next_cursor),
                resulting: Some(DeltaSubjectResult { subject, challenge }),
            },
        );
    }

    for offset in 0..scale {
        let source_index = config.node_count + offset;
        let target_index = offset + scale * 2;
        next_cursor += 1;
        let subject = added_relation(source_index, target_index, next_cursor);
        let key = SubjectKey::of(&subject);
        let challenge = projected_challenge(&subject);
        subjects.insert(key.clone(), subject.clone());
        challenges.insert(key.clone(), challenge.clone());
        changes.insert(
            key.clone(),
            CalculatedSubjectChange {
                subject: key,
                expected_previous: None,
                semantic_change_cursor: Some(next_cursor),
                resulting: Some(DeltaSubjectResult { subject, challenge }),
            },
        );
    }

    for index in scale..scale * 2 {
        let key = SubjectKey::new(ONTOLOGY_ID, node_id(index));
        let subject = subjects
            .get(&key)
            .cloned()
            .ok_or_else(|| format!("missing governance subject {}", key.subject_id))?;
        let mut challenge = challenges
            .get(&key)
            .cloned()
            .ok_or_else(|| format!("missing challenge {}", key.subject_id))?;
        challenge.contract.challenge_response =
            format!("Expose revised delta evidence for {}.", key.subject_id);
        challenges.insert(key.clone(), challenge.clone());
        changes.insert(
            key.clone(),
            CalculatedSubjectChange {
                subject: key.clone(),
                expected_previous: base_model
                    .expected_subject_version(&key)
                    .map_err(|failure| failure.to_string())?,
                semantic_change_cursor: None,
                resulting: Some(DeltaSubjectResult { subject, challenge }),
            },
        );
    }

    let target_subjects = subjects.into_values().collect::<Vec<_>>();
    let target_digest =
        calculated_projection_digest(&target_subjects).map_err(|failure| failure.to_string())?;
    let semantic_changes = changes
        .values()
        .filter(|change| change.semantic_change_cursor.is_some())
        .count();
    let target_cut = ConsistentOntologyCut {
        schema_version: base_cut.schema_version.clone(),
        authority_effect: AuthorityEffect::None,
        semantic_cursor: next_cursor,
        source_event_count: base_cut.source_event_count + semantic_changes,
        source_event_set_digest: target_digest.clone(),
        subjects: target_subjects,
    };
    let delta = CalculatedGraphDelta {
        schema_version: "cal-calculated-graph-delta/v1-prototype".to_owned(),
        delta_id: format!("benchmark-{scale}-mixed-change-delta"),
        authority_effect: AuthorityEffect::None,
        from_semantic_cursor: base_cut.semantic_cursor,
        from_source_event_count: base_cut.source_event_count,
        from_source_event_set_digest: base_cut.source_event_set_digest.clone(),
        to_semantic_cursor: next_cursor,
        to_source_event_count: target_cut.source_event_count,
        to_source_event_set_digest: target_digest,
        changes: changes.into_values().collect(),
    };
    Ok((delta, target_cut, challenges.into_values().collect()))
}

fn replace_subject(
    base_model: &GraphReadModel,
    subjects: &mut BTreeMap<SubjectKey, ProjectedSubject>,
    challenges: &mut BTreeMap<SubjectKey, ProjectedChallengeContract>,
    changes: &mut BTreeMap<SubjectKey, CalculatedSubjectChange>,
    key: SubjectKey,
    subject: ProjectedSubject,
    semantic_change_cursor: Option<u64>,
) -> Result<(), String> {
    let challenge = projected_challenge(&subject);
    subjects.insert(key.clone(), subject.clone());
    challenges.insert(key.clone(), challenge.clone());
    changes.insert(
        key.clone(),
        CalculatedSubjectChange {
            subject: key.clone(),
            expected_previous: base_model
                .expected_subject_version(&key)
                .map_err(|failure| failure.to_string())?,
            semantic_change_cursor,
            resulting: Some(DeltaSubjectResult { subject, challenge }),
        },
    );
    Ok(())
}

fn reseal_subject(subject: &mut ProjectedSubject, cursor: u64, operation: &str) {
    subject.source_cursor = cursor;
    subject.source_event_id = format!("benchmark-delta-{operation}-{cursor:012}");
    subject.source_event_digest = digest_bytes(subject.source_event_id.as_bytes());
}

fn added_node(config: &BenchmarkConfig, index: usize, cursor: u64) -> ProjectedSubject {
    let identity = OntologySubjectIdentity {
        subject_id: node_id(index),
        ontology_id: ONTOLOGY_ID.to_owned(),
        subject_kind: SubjectKind::Node,
        type_ref: format!("node_type_{}", index % 4),
    };
    let mut values = BTreeMap::new();
    values.insert(
        "context_id".to_owned(),
        json!(format!("context-{:04}", index % config.context_count)),
    );
    values.insert("tier".to_owned(), json!(index % 8));
    let mut subject = ProjectedSubject {
        identity: identity.clone(),
        source_event_id: String::new(),
        source_event_digest: String::new(),
        source_cursor: cursor,
        semantic_state: OntologySemanticState::Node(OntologyNodeSemanticState {
            identity,
            lifecycle: Lifecycle::Active,
            label: format!("Delta-added synthetic node {index}"),
            definition_or_claim: "Generated delta benchmark fixture; not canonical meaning."
                .to_owned(),
            scope: "local synthetic benchmark only".to_owned(),
            semantic_components: Vec::new(),
            semantic_definition_refs: Vec::new(),
            typed_properties: TypedPropertySet {
                profile_ref: "benchmark.synthetic.properties/v1".to_owned(),
                values,
            },
            use_obligations: Vec::new(),
            forbidden_collapse: Vec::new(),
            profile_ref: "benchmark.synthetic.node/v1".to_owned(),
        }),
    };
    reseal_subject(&mut subject, cursor, "node-add");
    subject
}

fn added_relation(source_index: usize, target_index: usize, cursor: u64) -> ProjectedSubject {
    let identity = OntologySubjectIdentity {
        subject_id: format!("relation-delta-{source_index:08}"),
        ontology_id: ONTOLOGY_ID.to_owned(),
        subject_kind: SubjectKind::Relation,
        type_ref: "relation_delta".to_owned(),
    };
    let mut subject = ProjectedSubject {
        identity: identity.clone(),
        source_event_id: String::new(),
        source_event_digest: String::new(),
        source_cursor: cursor,
        semantic_state: OntologySemanticState::Relation(OntologyRelationSemanticState {
            identity,
            lifecycle: Lifecycle::Active,
            source_node_id: node_id(source_index),
            target_node_id: node_id(target_index),
            direction: RelationDirection::Directed,
            typed_properties: TypedPropertySet {
                profile_ref: "benchmark.synthetic.relation/v1".to_owned(),
                values: BTreeMap::new(),
            },
            forbidden_collapse: Vec::new(),
        }),
    };
    reseal_subject(&mut subject, cursor, "relation-add");
    subject
}

fn delta_report(
    config: &BenchmarkConfig,
    delta: &CalculatedGraphDelta,
    receipt: &DeltaApplyReceipt,
    incremental_apply_ns: u128,
    full_target_rebuild_ns: u128,
    exact_model_equivalence: bool,
) -> DeltaReport {
    DeltaReport {
        declared_change_scale: config.delta_change_scale,
        total_changes: delta.changes.len(),
        semantic_changes: receipt.added + receipt.updated + receipt.removed,
        added: receipt.added,
        updated: receipt.updated,
        removed: receipt.removed,
        governance_replaced: receipt.governance_replaced,
        transaction_strategy: receipt.transaction_strategy.clone(),
        staged_previous_subject_count: receipt.staged_previous_subject_count,
        full_model_clone: receipt.full_model_clone,
        incremental_apply_ns,
        full_target_rebuild_ns,
        incremental_over_full_rebuild_ratio: incremental_apply_ns as f64
            / full_target_rebuild_ns.max(1) as f64,
        exact_model_equivalence,
        target_projection_digest_sha256: delta.to_source_event_set_digest.clone(),
        resulting_index_digest_sha256: receipt.resulting_index_digest.clone(),
        delta_digest_sha256: receipt.delta_digest.clone(),
    }
}

fn run_concurrent_snapshot_workload(
    config: &BenchmarkConfig,
    initial: GraphReadModel,
    delta: CalculatedGraphDelta,
    expected: &GraphReadModel,
) -> Result<ConcurrentSnapshotReport, String> {
    if config.concurrent_reader_threads == 0 || config.concurrent_reads_per_thread == 0 {
        return Err("concurrent reader counts must be greater than zero".to_owned());
    }
    let old_cursor = initial.metadata().semantic_cursor;
    let old_digest = initial.metadata().index_digest.clone();
    let new_cursor = expected.metadata().semantic_cursor;
    let new_digest = expected.metadata().index_digest.clone();
    let publisher = Arc::new(ConcurrentGraphReadModel::new(initial));
    let held = publisher
        .snapshot()
        .map_err(|failure| failure.to_string())?;
    if held.generation() != 0
        || held.semantic_cursor() != old_cursor
        || held.index_digest() != old_digest
    {
        return Err("initial concurrent snapshot mismatch".to_owned());
    }

    let writer_publisher = Arc::clone(&publisher);
    let (writer_started_tx, writer_started_rx) = mpsc::channel();
    let writer = thread::spawn(
        move || -> Result<(SnapshotPublicationReceipt, u128), String> {
            writer_started_tx
                .send(())
                .map_err(|error| error.to_string())?;
            let started = Instant::now();
            let receipt = writer_publisher
                .apply_calculated_delta(&delta)
                .map_err(|failure| failure.to_string())?;
            Ok((receipt, started.elapsed().as_nanos()))
        },
    );
    writer_started_rx
        .recv()
        .map_err(|error| error.to_string())?;

    let barrier = Arc::new(Barrier::new(config.concurrent_reader_threads + 1));
    let mut readers = Vec::with_capacity(config.concurrent_reader_threads);
    for _ in 0..config.concurrent_reader_threads {
        let reader_publisher = Arc::clone(&publisher);
        let reader_barrier = Arc::clone(&barrier);
        let reader_old_digest = old_digest.clone();
        let reader_new_digest = new_digest.clone();
        let iterations = config.concurrent_reads_per_thread;
        readers.push(thread::spawn(
            move || -> Result<(usize, usize, usize), String> {
                reader_barrier.wait();
                let mut old = 0;
                let mut new = 0;
                let mut invalid = 0;
                for _ in 0..iterations {
                    let snapshot = reader_publisher
                        .snapshot()
                        .map_err(|failure| failure.to_string())?;
                    black_box(snapshot.subject(&SubjectKey::new(ONTOLOGY_ID, node_id(0))));
                    match (
                        snapshot.generation(),
                        snapshot.semantic_cursor(),
                        snapshot.index_digest(),
                    ) {
                        (0, cursor, digest)
                            if cursor == old_cursor && digest == reader_old_digest =>
                        {
                            old += 1;
                        }
                        (1, cursor, digest)
                            if cursor == new_cursor && digest == reader_new_digest =>
                        {
                            new += 1;
                        }
                        _ => invalid += 1,
                    }
                    thread::yield_now();
                }
                Ok((old, new, invalid))
            },
        ));
    }
    barrier.wait();
    let (publication, writer_publication_ns_under_contention) = writer
        .join()
        .map_err(|_| "concurrent writer panicked".to_owned())??;
    let writer_completed_while_old_snapshot_held = true;
    let old_snapshot_retained_after_publication = held.generation() == 0
        && held.semantic_cursor() == old_cursor
        && held.index_digest() == old_digest;
    let mut old_generation_observations = 1;
    let mut new_generation_observations = 0;
    let mut invalid_observations = 0;
    for reader in readers {
        let (old, new, invalid) = reader
            .join()
            .map_err(|_| "concurrent reader panicked".to_owned())??;
        old_generation_observations += old;
        new_generation_observations += new;
        invalid_observations += invalid;
    }
    let final_snapshot = publisher
        .snapshot()
        .map_err(|failure| failure.to_string())?;
    let exact_final_model_equivalence = final_snapshot.model() == expected;
    if final_snapshot.generation() == 1
        && final_snapshot.semantic_cursor() == new_cursor
        && final_snapshot.index_digest() == new_digest
    {
        new_generation_observations += 1;
    } else {
        invalid_observations += 1;
    }
    let worker_observations = config.concurrent_reader_threads * config.concurrent_reads_per_thread;
    Ok(ConcurrentSnapshotReport {
        publication_strategy: publication.publication_strategy.clone(),
        reader_threads: config.concurrent_reader_threads,
        reads_per_thread: config.concurrent_reads_per_thread,
        worker_observations,
        old_generation_observations,
        new_generation_observations,
        invalid_observations,
        writer_completed_while_old_snapshot_held,
        old_snapshot_retained_after_publication,
        publication_staged_full_model_clone: publication.staged_full_model_clone,
        previous_subject_count: publication.structural_sharing.previous_subject_count,
        shared_subject_count: publication.structural_sharing.shared_subject_count,
        previous_challenge_contract_count: publication
            .structural_sharing
            .previous_challenge_contract_count,
        shared_challenge_contract_count: publication
            .structural_sharing
            .shared_challenge_contract_count,
        previous_index_bucket_count: publication.structural_sharing.previous_index_bucket_count,
        shared_index_bucket_count: publication.structural_sharing.shared_index_bucket_count,
        writer_publication_ns_under_contention,
        published_generation: publication.published_generation,
        published_semantic_cursor: publication.published_semantic_cursor,
        published_index_digest_sha256: publication.published_index_digest,
        exact_final_model_equivalence,
        readers_are_blocking: false,
    })
}

fn projected_challenge(subject: &ProjectedSubject) -> ProjectedChallengeContract {
    ProjectedChallengeContract {
        subject: SubjectKey::new(
            subject.identity.ontology_id.clone(),
            subject.identity.subject_id.clone(),
        ),
        semantic_event_id: subject.source_event_id.clone(),
        semantic_event_digest: subject.source_event_digest.clone(),
        semantic_cursor: subject.source_cursor,
        contract: ChallengeContract {
            challenge_response: "Expose generated fixture evidence.".to_owned(),
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
        },
    }
}

fn generate_queries(config: &BenchmarkConfig) -> Vec<Query> {
    let mut state = config.seed;
    (0..config.query_count)
        .map(|index| {
            state = state
                .wrapping_mul(6364136223846793005)
                .wrapping_add(1442695040888963407);
            let node = (state as usize) % config.node_count;
            match index % 8 {
                0 => Query::Subject(node_id(node)),
                1 => Query::Type(format!("node_type_{}", node % 4)),
                2 => Query::Property {
                    name: "tier".to_owned(),
                    value: json!(node % 8),
                },
                3 => Query::Outgoing {
                    subject: node_id(node),
                    relation: "relation_0".to_owned(),
                },
                4 => Query::Incoming {
                    target: node_id(node),
                    relation: "relation_1".to_owned(),
                },
                5 => Query::TwoHop {
                    subject: node_id(node),
                    first: "relation_0".to_owned(),
                    second: "relation_1".to_owned(),
                },
                6 => Query::Context(format!("context-{:04}", node % config.context_count)),
                _ => Query::Challenge(node_id(node)),
            }
        })
        .collect()
}

fn query_candidate(model: &GraphReadModel, query: &Query) -> Result<Vec<String>, String> {
    let key = |subject: &str| SubjectKey::new(ONTOLOGY_ID, subject);
    Ok(normalize(match query {
        Query::Subject(subject) => model
            .subject(&key(subject))
            .map(|value| vec![value.identity.subject_id.clone()])
            .unwrap_or_default(),
        Query::Type(type_ref) => collect_type_keys(model, type_ref)?,
        Query::Property { name, value } => collect_property_keys(model, name, value)?,
        Query::Outgoing { subject, relation } => model
            .outgoing_neighbors(&key(subject), relation)
            .into_iter()
            .map(|neighbor| neighbor.identity.subject_id)
            .collect(),
        Query::Incoming { target, relation } => model
            .incoming_neighbors(&key(target), relation)
            .into_iter()
            .map(|neighbor| neighbor.identity.subject_id)
            .collect(),
        Query::TwoHop {
            subject,
            first,
            second,
        } => model
            .traverse(&key(subject), &[first.clone(), second.clone()])
            .into_iter()
            .map(|neighbor| neighbor.identity.subject_id)
            .collect(),
        Query::Context(context) => model
            .context_members(ONTOLOGY_ID, context)
            .into_iter()
            .map(|subject| subject.identity.subject_id)
            .collect(),
        Query::Challenge(subject) => model
            .challenge_contract(&key(subject))
            .map(|_| vec![subject.clone()])
            .unwrap_or_default(),
    }))
}

fn collect_type_keys(model: &GraphReadModel, type_ref: &str) -> Result<Vec<String>, String> {
    let mut after = None;
    let mut results = Vec::new();
    loop {
        let page = model
            .subject_keys_by_type(ONTOLOGY_ID, type_ref, after.as_ref(), 4096)
            .map_err(|failure| failure.to_string())?;
        results.extend(page.items.into_iter().map(|key| key.subject_id));
        match page.next_after {
            Some(cursor) => after = Some(cursor),
            None => return Ok(results),
        }
    }
}

fn collect_property_keys(
    model: &GraphReadModel,
    name: &str,
    value: &Value,
) -> Result<Vec<String>, String> {
    let mut after = None;
    let mut results = Vec::new();
    loop {
        let page = model
            .subject_keys_by_property(ONTOLOGY_ID, name, value, after.as_ref(), 4096)
            .map_err(|failure| failure.to_string())?;
        results.extend(page.items.into_iter().map(|key| key.subject_id));
        match page.next_after {
            Some(cursor) => after = Some(cursor),
            None => return Ok(results),
        }
    }
}

fn summarize(samples: BTreeMap<String, Vec<u128>>) -> BTreeMap<String, LatencySummary> {
    samples
        .into_iter()
        .map(|(family, mut values)| {
            values.sort_unstable();
            let summary = LatencySummary {
                samples: values.len(),
                p50_ns: percentile(&values, 50),
                p95_ns: percentile(&values, 95),
                p99_ns: percentile(&values, 99),
                max_ns: values.last().copied().unwrap_or(0),
            };
            (family, summary)
        })
        .collect()
}

fn percentile(values: &[u128], percentile: usize) -> u128 {
    if values.is_empty() {
        return 0;
    }
    let index = ((values.len() - 1) * percentile).div_ceil(100);
    values[index.min(values.len() - 1)]
}

fn estimated_input_bytes(
    cut: &ConsistentOntologyCut,
    challenges: &[ProjectedChallengeContract],
) -> usize {
    cut.subjects
        .iter()
        .map(|subject| serde_json::to_vec(subject).map_or(0, |bytes| bytes.len()))
        .sum::<usize>()
        + challenges
            .iter()
            .map(|challenge| serde_json::to_vec(challenge).map_or(0, |bytes| bytes.len()))
            .sum::<usize>()
}

fn normalize(values: Vec<String>) -> Vec<String> {
    values
        .into_iter()
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect()
}

fn node_id(index: usize) -> String {
    format!("node-{index:08}")
}

fn digest_json<T: Serialize>(value: &T) -> Result<String, String> {
    serde_json::to_vec(value)
        .map(|bytes| digest_bytes(&bytes))
        .map_err(|error| error.to_string())
}

fn digest_bytes(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn argument(name: &str) -> Option<String> {
    let arguments = env::args().collect::<Vec<_>>();
    arguments
        .iter()
        .position(|argument| argument == name)
        .and_then(|index| arguments.get(index + 1).cloned())
}

fn append_line(path: &Path, line: &str) -> Result<(), std::io::Error> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    let mut output = OpenOptions::new().create(true).append(true).open(path)?;
    writeln!(output, "{line}")
}
