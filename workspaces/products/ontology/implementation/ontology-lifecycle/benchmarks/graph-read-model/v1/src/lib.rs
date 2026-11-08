use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::hint::black_box;
use std::time::Instant;

pub const BENCHMARK_ID: &str = "CAL-GRAPH-READ-MODEL-BENCHMARK-001";
pub const CLAIM_CEILING: &str = "local_single_process_experiment_only";

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Triple {
    pub subject: String,
    pub predicate: String,
    pub object: String,
}

#[derive(Clone, Debug)]
pub enum Query {
    NodeById(String),
    Outgoing {
        subject: String,
        predicate: String,
    },
    Incoming {
        object: String,
        predicate: String,
    },
    TwoHop {
        subject: String,
        first_predicate: String,
        second_predicate: String,
    },
    PredicateObject {
        predicate: String,
        object: String,
    },
    Context(String),
}

impl Query {
    pub fn family(&self) -> &'static str {
        match self {
            Self::NodeById(_) => "node_by_id",
            Self::Outgoing { .. } => "outgoing",
            Self::Incoming { .. } => "incoming",
            Self::TwoHop { .. } => "two_hop",
            Self::PredicateObject { .. } => "predicate_object",
            Self::Context(_) => "context_subgraph",
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct BenchmarkConfig {
    pub seed: u64,
    pub node_count: usize,
    pub relation_edges_per_node: usize,
    pub query_count: usize,
    pub repetitions: usize,
}

impl Default for BenchmarkConfig {
    fn default() -> Self {
        Self {
            seed: 65,
            node_count: 10_000,
            relation_edges_per_node: 4,
            query_count: 600,
            repetitions: 5,
        }
    }
}

#[derive(Clone, Debug, Serialize)]
pub struct LatencySummary {
    pub samples: usize,
    pub p50_ns: u128,
    pub p95_ns: u128,
    pub p99_ns: u128,
    pub max_ns: u128,
}

#[derive(Clone, Debug, Serialize)]
pub struct BackendReport {
    pub backend_id: String,
    pub status: String,
    pub build_ns: u128,
    pub incremental_insert_ns: u128,
    pub estimated_index_bytes: usize,
    pub result_digest_sha256: String,
    pub latency_by_query: BTreeMap<String, LatencySummary>,
}

#[derive(Clone, Debug, Serialize)]
pub struct CorrectnessReport {
    pub status: String,
    pub compared_backends: Vec<String>,
    pub shared_result_digest_sha256: String,
    pub interop_result_digest_sha256: String,
    pub query_results_compared: usize,
}

#[derive(Clone, Debug, Serialize)]
pub struct ExternalBackendStatus {
    pub backend_id: String,
    pub status: String,
    pub blocker: String,
    pub source_commit: String,
    pub license_posture: String,
}

#[derive(Clone, Debug, Serialize)]
pub struct BenchmarkReceipt {
    pub record_type: String,
    pub schema_version: String,
    pub benchmark_id: String,
    pub status: String,
    pub config: BenchmarkConfig,
    pub triple_count: usize,
    pub query_executions_per_backend: usize,
    pub fixture_digest_sha256: String,
    pub correctness: CorrectnessReport,
    pub backends: Vec<BackendReport>,
    pub external_backends: Vec<ExternalBackendStatus>,
    pub canonical_authority: String,
    pub claim_ceiling: String,
}

#[derive(Clone, Debug)]
pub struct ScanReadModel {
    triples: Vec<Triple>,
}

impl ScanReadModel {
    pub fn build(triples: &[Triple]) -> Self {
        Self {
            triples: triples.to_vec(),
        }
    }

    pub fn insert(&mut self, triple: Triple) {
        self.triples.push(triple);
    }

    pub fn estimated_bytes(&self) -> usize {
        self.triples.iter().map(triple_string_bytes).sum()
    }

    pub fn query(&self, query: &Query) -> Vec<String> {
        normalize(match query {
            Query::NodeById(id) => {
                if self.triples.iter().any(|triple| triple.subject == *id) {
                    vec![id.clone()]
                } else {
                    Vec::new()
                }
            }
            Query::Outgoing { subject, predicate } => self
                .triples
                .iter()
                .filter(|triple| triple.subject == *subject && triple.predicate == *predicate)
                .map(|triple| triple.object.clone())
                .collect(),
            Query::Incoming { object, predicate }
            | Query::PredicateObject { predicate, object } => self
                .triples
                .iter()
                .filter(|triple| triple.object == *object && triple.predicate == *predicate)
                .map(|triple| triple.subject.clone())
                .collect(),
            Query::Context(context) => self
                .triples
                .iter()
                .filter(|triple| triple.object == *context && triple.predicate == "in_context")
                .map(|triple| triple.subject.clone())
                .collect(),
            Query::TwoHop {
                subject,
                first_predicate,
                second_predicate,
            } => {
                let intermediate: BTreeSet<_> = self
                    .triples
                    .iter()
                    .filter(|triple| {
                        triple.subject == *subject && triple.predicate == *first_predicate
                    })
                    .map(|triple| triple.object.as_str())
                    .collect();
                self.triples
                    .iter()
                    .filter(|triple| {
                        intermediate.contains(triple.subject.as_str())
                            && triple.predicate == *second_predicate
                    })
                    .map(|triple| triple.object.clone())
                    .collect()
            }
        })
    }
}

#[derive(Clone, Debug)]
pub struct IndexedReadModel {
    subjects: BTreeSet<String>,
    spo: BTreeMap<(String, String), Vec<String>>,
    pos: BTreeMap<(String, String), Vec<String>>,
    string_bytes: usize,
}

impl IndexedReadModel {
    pub fn build(triples: &[Triple]) -> Self {
        let mut model = Self {
            subjects: BTreeSet::new(),
            spo: BTreeMap::new(),
            pos: BTreeMap::new(),
            string_bytes: 0,
        };
        for triple in triples {
            model.insert(triple.clone());
        }
        model
    }

    pub fn insert(&mut self, triple: Triple) {
        self.string_bytes += triple_string_bytes(&triple) * 2;
        self.subjects.insert(triple.subject.clone());
        self.spo
            .entry((triple.subject.clone(), triple.predicate.clone()))
            .or_default()
            .push(triple.object.clone());
        self.pos
            .entry((triple.predicate, triple.object))
            .or_default()
            .push(triple.subject);
    }

    pub fn estimated_bytes(&self) -> usize {
        self.string_bytes
    }

    pub fn query(&self, query: &Query) -> Vec<String> {
        normalize(match query {
            Query::NodeById(id) => {
                if self.subjects.contains(id) {
                    vec![id.clone()]
                } else {
                    Vec::new()
                }
            }
            Query::Outgoing { subject, predicate } => self
                .spo
                .get(&(subject.clone(), predicate.clone()))
                .cloned()
                .unwrap_or_default(),
            Query::Incoming { object, predicate }
            | Query::PredicateObject { predicate, object } => self
                .pos
                .get(&(predicate.clone(), object.clone()))
                .cloned()
                .unwrap_or_default(),
            Query::Context(context) => self
                .pos
                .get(&("in_context".to_string(), context.clone()))
                .cloned()
                .unwrap_or_default(),
            Query::TwoHop {
                subject,
                first_predicate,
                second_predicate,
            } => {
                let mut result = Vec::new();
                if let Some(intermediate) =
                    self.spo.get(&(subject.clone(), first_predicate.clone()))
                {
                    for node in intermediate {
                        if let Some(objects) =
                            self.spo.get(&(node.clone(), second_predicate.clone()))
                        {
                            result.extend(objects.iter().cloned());
                        }
                    }
                }
                result
            }
        })
    }
}

pub fn generate_fixture(config: &BenchmarkConfig) -> Vec<Triple> {
    assert!(config.node_count > 0, "node_count must be positive");
    let predicates = ["depends_on", "validates", "challenges", "binds", "enforces"];
    let mut triples =
        Vec::with_capacity(config.node_count * (config.relation_edges_per_node.saturating_add(2)));
    for node in 0..config.node_count {
        let subject = format!("node:{node:010}");
        triples.push(Triple {
            subject: subject.clone(),
            predicate: "node_type".to_string(),
            object: format!("type:{:02}", node % 16),
        });
        triples.push(Triple {
            subject: subject.clone(),
            predicate: "in_context".to_string(),
            object: format!("context:{:03}", node % 128),
        });
        for edge in 0..config.relation_edges_per_node {
            let mixed = node
                .wrapping_mul(1_103_515_245)
                .wrapping_add(edge.wrapping_mul(12_345))
                .wrapping_add(config.seed as usize);
            let target = mixed % config.node_count;
            triples.push(Triple {
                subject: subject.clone(),
                predicate: predicates[edge % predicates.len()].to_string(),
                object: format!("node:{target:010}"),
            });
        }
    }
    triples
}

pub fn generate_queries(config: &BenchmarkConfig) -> Vec<Query> {
    let predicates = ["depends_on", "validates", "challenges", "binds", "enforces"];
    (0..config.query_count)
        .map(|index| {
            let node =
                (index.wrapping_mul(7_919).wrapping_add(config.seed as usize)) % config.node_count;
            let subject = format!("node:{node:010}");
            match index % 6 {
                0 => Query::NodeById(subject),
                1 => Query::Outgoing {
                    subject,
                    predicate: predicates[index % predicates.len()].to_string(),
                },
                2 => Query::Incoming {
                    object: subject,
                    predicate: predicates[index % predicates.len()].to_string(),
                },
                3 => Query::TwoHop {
                    subject,
                    first_predicate: "depends_on".to_string(),
                    second_predicate: "validates".to_string(),
                },
                4 => Query::PredicateObject {
                    predicate: "node_type".to_string(),
                    object: format!("type:{:02}", node % 16),
                },
                _ => Query::Context(format!("context:{:03}", node % 128)),
            }
        })
        .collect()
}

pub fn execute(config: BenchmarkConfig, wavedb: ExternalBackendStatus) -> BenchmarkReceipt {
    let triples = generate_fixture(&config);
    let queries = generate_queries(&config);
    let fixture_digest = digest_serializable(&triples);

    let started = Instant::now();
    let mut scan = ScanReadModel::build(&triples);
    let scan_build_ns = started.elapsed().as_nanos();
    let started = Instant::now();
    let mut indexed = IndexedReadModel::build(&triples);
    let indexed_build_ns = started.elapsed().as_nanos();

    let scan_results: Vec<_> = queries.iter().map(|query| scan.query(query)).collect();
    let indexed_results: Vec<_> = queries.iter().map(|query| indexed.query(query)).collect();
    assert_eq!(
        scan_results, indexed_results,
        "backend correctness mismatch"
    );
    let shared_digest = digest_serializable(&scan_results);
    let interop_digest = interop_result_digest(&queries, &scan_results);

    let incremental = Triple {
        subject: "node:benchmark:incremental".to_string(),
        predicate: "binds".to_string(),
        object: "node:0000000000".to_string(),
    };
    let started = Instant::now();
    scan.insert(incremental.clone());
    let scan_insert_ns = started.elapsed().as_nanos();
    let started = Instant::now();
    indexed.insert(incremental);
    let indexed_insert_ns = started.elapsed().as_nanos();

    let scan_report = benchmark_backend(
        "rust_scan_control",
        scan_build_ns,
        scan_insert_ns,
        scan.estimated_bytes(),
        &queries,
        config.repetitions,
        |query| scan.query(query),
    );
    let indexed_report = benchmark_backend(
        "rust_spo_pos_index",
        indexed_build_ns,
        indexed_insert_ns,
        indexed.estimated_bytes(),
        &queries,
        config.repetitions,
        |query| indexed.query(query),
    );
    assert_eq!(
        scan_report.result_digest_sha256,
        indexed_report.result_digest_sha256
    );

    BenchmarkReceipt {
        record_type: "benchmark_run".to_string(),
        schema_version: "1.1.0".to_string(),
        benchmark_id: BENCHMARK_ID.to_string(),
        status: "pass".to_string(),
        triple_count: triples.len(),
        query_executions_per_backend: queries.len() * config.repetitions,
        fixture_digest_sha256: fixture_digest,
        correctness: CorrectnessReport {
            status: "pass".to_string(),
            compared_backends: vec![
                "rust_scan_control".to_string(),
                "rust_spo_pos_index".to_string(),
            ],
            shared_result_digest_sha256: shared_digest,
            interop_result_digest_sha256: interop_digest,
            query_results_compared: queries.len(),
        },
        backends: vec![scan_report, indexed_report],
        external_backends: vec![wavedb],
        canonical_authority:
            "canonical events only; every read model is disposable and rebuildable".to_string(),
        claim_ceiling: CLAIM_CEILING.to_string(),
        config,
    }
}

fn benchmark_backend<F>(
    backend_id: &str,
    build_ns: u128,
    incremental_insert_ns: u128,
    estimated_index_bytes: usize,
    queries: &[Query],
    repetitions: usize,
    mut query_fn: F,
) -> BackendReport
where
    F: FnMut(&Query) -> Vec<String>,
{
    let mut samples: BTreeMap<String, Vec<u128>> = BTreeMap::new();
    let mut digest = Sha256::new();
    for _ in 0..repetitions {
        for query in queries {
            let started = Instant::now();
            let result = query_fn(query);
            let elapsed = started.elapsed().as_nanos();
            samples
                .entry(query.family().to_string())
                .or_default()
                .push(elapsed);
            digest.update(query.family().as_bytes());
            digest.update(serde_json::to_vec(black_box(&result)).expect("serialize query result"));
        }
    }
    BackendReport {
        backend_id: backend_id.to_string(),
        status: "pass".to_string(),
        build_ns,
        incremental_insert_ns,
        estimated_index_bytes,
        result_digest_sha256: format!("{:x}", digest.finalize()),
        latency_by_query: samples
            .into_iter()
            .map(|(family, values)| (family, summarize(values)))
            .collect(),
    }
}

fn summarize(mut values: Vec<u128>) -> LatencySummary {
    values.sort_unstable();
    let count = values.len();
    LatencySummary {
        samples: count,
        p50_ns: percentile(&values, 50),
        p95_ns: percentile(&values, 95),
        p99_ns: percentile(&values, 99),
        max_ns: *values.last().unwrap_or(&0),
    }
}

fn percentile(values: &[u128], percentile: usize) -> u128 {
    if values.is_empty() {
        return 0;
    }
    let index = ((values.len() - 1) * percentile + 99) / 100;
    values[index]
}

fn normalize(mut values: Vec<String>) -> Vec<String> {
    values.sort();
    values.dedup();
    values
}

fn triple_string_bytes(triple: &Triple) -> usize {
    triple.subject.len() + triple.predicate.len() + triple.object.len()
}

fn digest_serializable(value: &impl Serialize) -> String {
    let bytes = serde_json::to_vec(value).expect("serialize digest input");
    format!("{:x}", Sha256::digest(bytes))
}

fn interop_result_digest(queries: &[Query], results: &[Vec<String>]) -> String {
    let mut digest = Sha256::new();
    for (query, values) in queries.iter().zip(results) {
        digest.update(query.family().as_bytes());
        digest.update([0]);
        for value in values {
            digest.update(value.as_bytes());
            digest.update([0]);
        }
        digest.update([0xff]);
    }
    format!("{:x}", digest.finalize())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fixture_is_deterministic() {
        let config = BenchmarkConfig {
            node_count: 100,
            query_count: 60,
            ..Default::default()
        };
        assert_eq!(generate_fixture(&config), generate_fixture(&config));
    }

    #[test]
    fn scan_and_indexed_models_return_identical_results() {
        let config = BenchmarkConfig {
            node_count: 1_000,
            query_count: 600,
            ..Default::default()
        };
        let triples = generate_fixture(&config);
        let scan = ScanReadModel::build(&triples);
        let indexed = IndexedReadModel::build(&triples);
        for query in generate_queries(&config) {
            assert_eq!(
                scan.query(&query),
                indexed.query(&query),
                "{} mismatch",
                query.family()
            );
        }
    }

    #[test]
    fn receipt_keeps_read_models_non_authoritative() {
        let config = BenchmarkConfig {
            node_count: 100,
            query_count: 60,
            repetitions: 1,
            ..Default::default()
        };
        let receipt = execute(
            config,
            ExternalBackendStatus {
                backend_id: "wavedb_graph".to_string(),
                status: "not_evaluable".to_string(),
                blocker: "fixture blocker".to_string(),
                source_commit: "fixture".to_string(),
                license_posture: "unresolved".to_string(),
            },
        );
        assert_eq!(receipt.status, "pass");
        assert!(
            receipt
                .canonical_authority
                .starts_with("canonical events only")
        );
        assert_eq!(receipt.external_backends[0].status, "not_evaluable");
    }
}
