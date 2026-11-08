use cal_ontology_lifecycle::{
    AppendGovernanceEventRequest, AppendSemanticEventRequest, AuthorityEffect,
    AuthorityKindAndPosture, ChallengeContract, ChallengeMode, ConfidenceReference,
    ContextSelector, DefinitionReference, EventFamily, EventStore, ExactSemanticEventReference,
    ForbiddenCollapse, GovernanceEvent, GovernanceJoinPolicy, Lifecycle, OntologyGovernanceState,
    OntologyNodeSemanticState, OntologyRelationSemanticState, OntologySemanticState,
    OntologySubjectIdentity, ProjectionProfile, ProvenanceEntry, SemanticComponent, SemanticEvent,
    SourceKind, SubjectKind, TypedPropertySet, TypedResidue, ZERO_DIGEST, machine_projection,
    seal_governance_event, seal_semantic_event,
};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::env;
use std::error::Error;
use std::fs;
use std::path::{Path, PathBuf};

type AnyResult<T> = Result<T, Box<dyn Error>>;

#[derive(Debug, Deserialize)]
struct Manifest {
    epoch_id: String,
    ontology_id: String,
    source_repository: String,
    inputs: Vec<ManifestInput>,
    rehearsal_contract: RehearsalContract,
}

#[derive(Debug, Deserialize)]
struct ManifestInput {
    input_id: String,
    path: String,
    sha256: String,
    expected_record_count: usize,
}

#[derive(Debug, Deserialize)]
struct RehearsalContract {
    semantic_event_count: usize,
    governance_event_count: usize,
    node_count: usize,
    relation_count: usize,
    relation_vocabulary_count: usize,
    final_semantic_cursor: u64,
    checkpoint_cursor: u64,
}

#[derive(Clone)]
struct GovernanceInput {
    original: Value,
    vocabulary: Option<Value>,
    owner_route: String,
    status: String,
    evidence_confidence: String,
    commitment_confidence: String,
    open_questions: Vec<String>,
    source_refs: Vec<Value>,
    evidence_ref: String,
}

#[derive(Debug, Serialize)]
struct LineageEntry {
    subject_id: String,
    subject_kind: String,
    source_file: String,
    source_record_pointer: String,
    semantic_event_id: String,
    semantic_event_digest: String,
    semantic_cursor: u64,
    governance_event_id: String,
    governance_event_digest: String,
    governance_cursor: u64,
}

#[derive(Debug, Serialize)]
struct ProjectionDigest {
    path: String,
    sha256: String,
}

#[derive(Debug, Serialize)]
struct RunResult {
    schema_version: String,
    epoch_id: String,
    ontology_id: String,
    result: String,
    semantic_event_count: usize,
    governance_event_count: usize,
    node_count: usize,
    relation_count: usize,
    relation_vocabulary_count: usize,
    lineage_count: usize,
    final_semantic_cursor: u64,
    checkpoint_cursor: u64,
    direct_and_checkpoint_rebuild_equal: bool,
    exact_governance_join_count: usize,
    projection_digests: Vec<ProjectionDigest>,
    authority_effect: String,
    claim_ceiling: String,
}

fn sha256(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn file_sha256(path: &Path) -> AnyResult<String> {
    Ok(sha256(&fs::read(path)?))
}

fn required_str(value: &Value, key: &str) -> AnyResult<String> {
    value
        .get(key)
        .and_then(Value::as_str)
        .map(str::to_owned)
        .ok_or_else(|| format!("required string {key} is missing").into())
}

fn string_array(value: &Value, key: &str) -> AnyResult<Vec<String>> {
    value
        .get(key)
        .and_then(Value::as_array)
        .ok_or_else(|| format!("required array {key} is missing"))?
        .iter()
        .map(|item| {
            item.as_str()
                .map(str::to_owned)
                .ok_or_else(|| format!("{key} contains a non-string").into())
        })
        .collect()
}

fn value_array(value: &Value, key: &str) -> AnyResult<Vec<Value>> {
    Ok(value
        .get(key)
        .and_then(Value::as_array)
        .ok_or_else(|| format!("required array {key} is missing"))?
        .clone())
}

fn source_definition_refs(source_refs: &[Value]) -> AnyResult<Vec<DefinitionReference>> {
    source_refs
        .iter()
        .map(|reference| {
            let definition_id = required_str(reference, "source_id")?;
            let selector = required_str(reference, "selector")?;
            Ok(DefinitionReference {
                definition_id,
                selector_sha256: sha256(selector.as_bytes()),
            })
        })
        .collect()
}

fn provenance(source_refs: &[Value], owner_route: &str) -> AnyResult<Vec<ProvenanceEntry>> {
    source_refs
        .iter()
        .map(|reference| {
            Ok(ProvenanceEntry {
                source_ref: format!(
                    "{}#{}",
                    required_str(reference, "source_id")?,
                    required_str(reference, "selector")?
                ),
                relation: "derived-from-selected-legacy-record".to_owned(),
                operation: "w7-isolated-migration-rehearsal".to_owned(),
                owner_route: owner_route.to_owned(),
                posture: "read-only-external-evidence".to_owned(),
            })
        })
        .collect()
}

fn forbidden_collapse(subject_id: &str, statement: String) -> Vec<ForbiddenCollapse> {
    vec![ForbiddenCollapse {
        left_ref: subject_id.to_owned(),
        right_ref: "legacy-collapse-boundary".to_owned(),
        context: statement,
        intended_use: "w7-migration-rehearsal".to_owned(),
    }]
}

fn exact_ref(event: &SemanticEvent) -> ExactSemanticEventReference {
    ExactSemanticEventReference {
        semantic_event_id: event.event_id.clone(),
        semantic_event_digest: event.event_digest.clone(),
        semantic_cursor: event.semantic_cursor,
    }
}

fn governance_state(
    semantic: &SemanticEvent,
    input: &GovernanceInput,
) -> AnyResult<OntologyGovernanceState> {
    let mut preserved = serde_json::Map::new();
    preserved.insert("legacy_record".to_owned(), input.original.clone());
    if let Some(vocabulary) = &input.vocabulary {
        preserved.insert("legacy_relation_vocabulary".to_owned(), vocabulary.clone());
    }
    let observed_remainder = serde_json::to_string(&Value::Object(preserved))?;
    let reference = exact_ref(semantic);
    Ok(OntologyGovernanceState {
        semantic_ref: reference,
        provenance: provenance(&input.source_refs, &input.owner_route)?,
        owner_route: input.owner_route.clone(),
        candidate_or_maturity_status: input.status.clone(),
        promotion_state_or_handle: "not-promoted".to_owned(),
        authority_kind_and_posture: AuthorityKindAndPosture {
            kind: "legacy-candidate".to_owned(),
            posture: "read-only-rehearsal".to_owned(),
        },
        authority_effect: AuthorityEffect::None,
        evidence_confidence: ConfidenceReference {
            scheme_ref: "legacy-cav2-confidence/v1".to_owned(),
            level: input.evidence_confidence.clone(),
        },
        commitment_confidence: ConfidenceReference {
            scheme_ref: "legacy-cav2-confidence/v1".to_owned(),
            level: input.commitment_confidence.clone(),
        },
        challenge_contract: ChallengeContract {
            challenge_response: "Preserve the selected legacy record and route challenges to its owner without changing source bytes.".to_owned(),
            valid_challenge_modes: vec![
                ChallengeMode::Evidence,
                ChallengeMode::Contradiction,
                ChallengeMode::OwnerReview,
            ],
            contradiction_edges: vec![],
            validation_edges: vec![],
            owner_route: input.owner_route.clone(),
            resolution_gate: "G-W7".to_owned(),
            blocking_questions: input.open_questions.clone(),
            challenge_residue_route: "CyberAlchemy-v2-ontology-migration-owner".to_owned(),
        },
        residue: vec![TypedResidue {
            source_operation: "map-selected-legacy-record".to_owned(),
            expected_condition: "Every source field is mapped first-class or preserved byte-exactly as typed residue.".to_owned(),
            observed_remainder,
            residue_type: "legacy-record-roundtrip-witness".to_owned(),
            evidence_ref: input.evidence_ref.clone(),
            owner_route: input.owner_route.clone(),
            treatment: "preserve-exact-for-owner-review".to_owned(),
        }],
        conflicts: vec![],
        drift_owner: input.owner_route.clone(),
        invalidation_route: input.owner_route.clone(),
    })
}

fn semantic_event(cursor: u64, state: OntologySemanticState) -> AnyResult<SemanticEvent> {
    let identity = state.identity().clone();
    let mut event = SemanticEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Semantic,
        event_id: format!("w7-semantic-{cursor:04}"),
        event_digest: ZERO_DIGEST.to_owned(),
        stream_id: identity.semantic_stream_id(),
        subject_identity: identity,
        previous_event_digest: None,
        semantic_cursor: cursor,
        complete_resulting_semantic_state: state,
    };
    seal_semantic_event(&mut event)?;
    Ok(event)
}

fn node_state(ontology_id: &str, node: &Value) -> AnyResult<OntologySemanticState> {
    if required_str(node, "authority_effect")? != "none" {
        return Err("legacy node authority_effect must be none".into());
    }
    let subject_id = required_str(node, "id")?;
    let source_refs = value_array(node, "source_refs")?;
    let definitions = source_definition_refs(&source_refs)?;
    let first_definition = definitions
        .first()
        .cloned()
        .ok_or("legacy node requires at least one source reference")?;
    let identity = OntologySubjectIdentity {
        subject_id: subject_id.clone(),
        ontology_id: ontology_id.to_owned(),
        subject_kind: SubjectKind::Node,
        type_ref: required_str(node, "role")?,
    };
    Ok(OntologySemanticState::Node(OntologyNodeSemanticState {
        identity,
        lifecycle: Lifecycle::Active,
        label: required_str(node, "label")?,
        definition_or_claim: required_str(node, "claim")?,
        scope: required_str(node, "scope")?,
        semantic_components: vec![SemanticComponent {
            component_id: format!("{subject_id}-plain-language"),
            type_ref: "legacy-plain-language".to_owned(),
            definition_ref: first_definition,
        }],
        semantic_definition_refs: definitions,
        typed_properties: TypedPropertySet {
            profile_ref: "test-empty-profile/v1".to_owned(),
            values: BTreeMap::new(),
        },
        use_obligations: vec![],
        forbidden_collapse: forbidden_collapse(
            &subject_id,
            required_str(node, "forbidden_collapse")?,
        ),
        profile_ref: "test-empty-profile/v1".to_owned(),
    }))
}

fn relation_state(ontology_id: &str, relation: &Value) -> AnyResult<OntologySemanticState> {
    if required_str(relation, "authority_effect")? != "none" {
        return Err("legacy relation authority_effect must be none".into());
    }
    let subject_id = required_str(relation, "id")?;
    let identity = OntologySubjectIdentity {
        subject_id: subject_id.clone(),
        ontology_id: ontology_id.to_owned(),
        subject_kind: SubjectKind::Relation,
        type_ref: required_str(relation, "type")?,
    };
    Ok(OntologySemanticState::Relation(
        OntologyRelationSemanticState {
            identity,
            lifecycle: Lifecycle::Active,
            source_node_id: required_str(relation, "source")?,
            target_node_id: required_str(relation, "target")?,
            direction: cal_ontology_lifecycle::RelationDirection::Directed,
            typed_properties: TypedPropertySet {
                profile_ref: "test-empty-profile/v1".to_owned(),
                values: BTreeMap::new(),
            },
            forbidden_collapse: forbidden_collapse(
                &subject_id,
                required_str(relation, "forbidden_collapse")?,
            ),
        },
    ))
}

fn governance_input_for_node(node: &Value) -> AnyResult<GovernanceInput> {
    Ok(GovernanceInput {
        original: node.clone(),
        vocabulary: None,
        owner_route: required_str(node, "owner_route")?,
        status: required_str(node, "candidate_status")?,
        evidence_confidence: required_str(node, "evidence_confidence")?,
        commitment_confidence: required_str(node, "commitment_confidence")?,
        open_questions: string_array(node, "open_questions")?,
        source_refs: value_array(node, "source_refs")?,
        evidence_ref: format!("nodes.json#/nodes/{}", required_str(node, "id")?),
    })
}

fn governance_input_for_relation(
    relation: &Value,
    vocabulary: &Value,
) -> AnyResult<GovernanceInput> {
    Ok(GovernanceInput {
        original: relation.clone(),
        vocabulary: Some(vocabulary.clone()),
        owner_route: required_str(relation, "owner_route")?,
        status: "candidate".to_owned(),
        evidence_confidence: "not-assessed".to_owned(),
        commitment_confidence: "not-assessed".to_owned(),
        open_questions: vec![],
        source_refs: value_array(relation, "source_refs")?,
        evidence_ref: format!(
            "relations.json#/relations/{}",
            required_str(relation, "id")?
        ),
    })
}

fn write_projection<T: Serialize>(directory: &Path, name: &str, value: &T) -> AnyResult<PathBuf> {
    let path = directory.join(name);
    fs::write(&path, machine_projection(value)?)?;
    Ok(path)
}

fn main() -> AnyResult<()> {
    let arguments = env::args().collect::<Vec<_>>();
    if arguments.len() != 3 {
        return Err(
            "usage: cal-w7-ontology-product-rehearsal <manifest.json> <new-output-directory>"
                .into(),
        );
    }
    let manifest_path = Path::new(&arguments[1]);
    let output = Path::new(&arguments[2]);
    if output.exists() {
        return Err(format!("output already exists: {}", output.display()).into());
    }
    let manifest: Manifest = serde_json::from_slice(&fs::read(manifest_path)?)?;
    let source_repository = Path::new(&manifest.source_repository).canonicalize()?;
    let inputs = manifest
        .inputs
        .iter()
        .map(|input| (input.input_id.as_str(), input))
        .collect::<BTreeMap<_, _>>();

    let resolve_input = |input_id: &str| -> AnyResult<PathBuf> {
        let input = inputs
            .get(input_id)
            .ok_or_else(|| format!("manifest input missing: {input_id}"))?;
        let path = source_repository.join(&input.path).canonicalize()?;
        if !path.starts_with(&source_repository) {
            return Err(format!("input escapes source repository: {}", path.display()).into());
        }
        let actual = file_sha256(&path)?;
        if actual != input.sha256 {
            return Err(format!(
                "source digest drift for {}: expected {}; actual {actual}",
                input.path, input.sha256
            )
            .into());
        }
        Ok(path)
    };

    let profile_path = resolve_input("ontology-product-profile")?;
    let nodes_path = resolve_input("ontology-product-nodes")?;
    let relations_path = resolve_input("ontology-product-relations")?;
    let profile: Value = serde_json::from_slice(&fs::read(&profile_path)?)?;
    let nodes_document: Value = serde_json::from_slice(&fs::read(&nodes_path)?)?;
    let relations_document: Value = serde_json::from_slice(&fs::read(&relations_path)?)?;
    if required_str(&profile, "ontology_id")? != manifest.ontology_id {
        return Err("profile ontology_id does not match manifest".into());
    }

    let mut nodes = value_array(&nodes_document, "nodes")?;
    let mut relations = value_array(&relations_document, "relations")?;
    let vocabulary = value_array(&relations_document, "relation_vocabulary")?;
    nodes.sort_by_key(|node| {
        node.get("id")
            .and_then(Value::as_str)
            .unwrap_or_default()
            .to_owned()
    });
    relations.sort_by_key(|relation| {
        relation
            .get("id")
            .and_then(Value::as_str)
            .unwrap_or_default()
            .to_owned()
    });
    let vocabulary_by_id = vocabulary
        .iter()
        .map(|entry| Ok((required_str(entry, "id")?, entry.clone())))
        .collect::<AnyResult<BTreeMap<_, _>>>()?;

    if nodes.len() != manifest.rehearsal_contract.node_count
        || relations.len() != manifest.rehearsal_contract.relation_count
        || vocabulary.len() != manifest.rehearsal_contract.relation_vocabulary_count
    {
        return Err("source record counts do not match manifest".into());
    }
    if inputs["ontology-product-profile"].expected_record_count != 1
        || inputs["ontology-product-nodes"].expected_record_count != nodes.len()
        || inputs["ontology-product-relations"].expected_record_count
            != relations.len() + vocabulary.len()
    {
        return Err("manifest expected_record_count mismatch".into());
    }
    let node_ids = nodes
        .iter()
        .map(|node| required_str(node, "id"))
        .collect::<AnyResult<BTreeSet<_>>>()?;
    for relation in &relations {
        let source = required_str(relation, "source")?;
        let target = required_str(relation, "target")?;
        if !node_ids.contains(&source) || !node_ids.contains(&target) {
            return Err(format!("relation endpoint missing: {source} -> {target}").into());
        }
    }

    let mut pending = Vec::<(SemanticEvent, GovernanceInput, String, String)>::new();
    let mut cursor = 1_u64;
    for node in &nodes {
        let state = node_state(&manifest.ontology_id, node)?;
        let subject_id = state.identity().subject_id.clone();
        pending.push((
            semantic_event(cursor, state)?,
            governance_input_for_node(node)?,
            "nodes.json".to_owned(),
            format!("/nodes/{subject_id}"),
        ));
        cursor += 1;
    }
    for relation in &relations {
        let relation_type = required_str(relation, "type")?;
        let vocabulary_entry = vocabulary_by_id
            .get(&relation_type)
            .ok_or_else(|| format!("relation vocabulary missing: {relation_type}"))?;
        let state = relation_state(&manifest.ontology_id, relation)?;
        let subject_id = state.identity().subject_id.clone();
        pending.push((
            semantic_event(cursor, state)?,
            governance_input_for_relation(relation, vocabulary_entry)?,
            "relations.json".to_owned(),
            format!("/relations/{subject_id}"),
        ));
        cursor += 1;
    }
    if pending.len() != manifest.rehearsal_contract.semantic_event_count
        || cursor - 1 != manifest.rehearsal_contract.final_semantic_cursor
    {
        return Err("semantic event count or cursor mismatch".into());
    }

    let mut governance = Vec::new();
    for (index, (semantic, input, _, _)) in pending.iter().enumerate() {
        let governance_cursor = index as u64 + 1;
        let reference = exact_ref(semantic);
        let mut event = GovernanceEvent {
            source_kind: SourceKind::CanonicalEvent,
            event_family: EventFamily::Governance,
            event_id: format!("w7-governance-{governance_cursor:04}"),
            event_digest: ZERO_DIGEST.to_owned(),
            stream_id: semantic.subject_identity.governance_stream_id(),
            semantic_ref: reference.clone(),
            governance_cursor,
            previous_event_digest: None,
            complete_resulting_governance_state: governance_state(semantic, input)?,
        };
        seal_governance_event(&mut event)?;
        governance.push(event);
    }
    if governance.len() != manifest.rehearsal_contract.governance_event_count {
        return Err("governance event count mismatch".into());
    }

    let semantic_directory = output.join("semantic-events");
    let governance_directory = output.join("governance-events");
    let projection_directory = output.join("projections");
    fs::create_dir_all(&semantic_directory)?;
    fs::create_dir_all(&governance_directory)?;
    fs::create_dir_all(&projection_directory)?;

    let mut store = EventStore::load(&semantic_directory, &governance_directory)?;
    let semantic_receipts = store.append_semantic_batch(
        &semantic_directory,
        pending
            .iter()
            .map(|(event, _, _, _)| AppendSemanticEventRequest {
                expected_stream_version: 0,
                event: event.clone(),
            })
            .collect(),
    )?;
    let governance_receipts = store.append_governance_batch(
        &governance_directory,
        governance
            .iter()
            .cloned()
            .map(|event| AppendGovernanceEventRequest {
                expected_stream_version: 0,
                event,
            })
            .collect(),
    )?;
    write_projection(
        &projection_directory,
        "semantic-append-receipts.json",
        &semantic_receipts,
    )?;
    write_projection(
        &projection_directory,
        "governance-append-receipts.json",
        &governance_receipts,
    )?;

    let rebuilt = EventStore::load(&semantic_directory, &governance_directory)?;
    let final_cursor = manifest.rehearsal_contract.final_semantic_cursor;
    let cut = rebuilt.ontology_at(final_cursor)?;
    let snapshots = rebuilt.latest_subject_snapshots(final_cursor)?;
    let checkpoint = rebuilt.checkpoint_at(manifest.rehearsal_contract.checkpoint_cursor)?;
    let checkpoint_cut = rebuilt.ontology_from_checkpoint(&checkpoint, final_cursor)?;
    if cut != checkpoint_cut {
        return Err("direct and checkpoint-tail ontology cuts differ".into());
    }
    let identities = cut
        .subjects
        .iter()
        .map(|subject| subject.identity.clone())
        .collect::<Vec<_>>();
    let selector = ContextSelector {
        semantic_cursor: final_cursor,
        required_subject_set: identities.clone(),
        governance_join_policy: GovernanceJoinPolicy::RequireExact,
        intended_use: "w7-migration-rehearsal".to_owned(),
        projection_profile: ProjectionProfile::TestCompleteV1,
    };
    let context = rebuilt.context_projection("w7-ontology-product-context", &selector)?;
    let node_identities = identities
        .iter()
        .filter(|identity| identity.subject_kind == SubjectKind::Node)
        .cloned()
        .collect::<Vec<OntologySubjectIdentity>>();
    let views = node_identities
        .iter()
        .map(|identity| {
            rebuilt.governed_node_view(
                identity,
                final_cursor,
                Some("w7-ontology-product-context".to_owned()),
            )
        })
        .collect::<Result<Vec<_>, _>>()?;

    let lineage = pending
        .iter()
        .zip(governance.iter())
        .map(
            |((semantic, _, source_file, pointer), governance)| LineageEntry {
                subject_id: semantic.subject_identity.subject_id.clone(),
                subject_kind: semantic.subject_identity.subject_kind.to_string(),
                source_file: source_file.clone(),
                source_record_pointer: pointer.clone(),
                semantic_event_id: semantic.event_id.clone(),
                semantic_event_digest: semantic.event_digest.clone(),
                semantic_cursor: semantic.semantic_cursor,
                governance_event_id: governance.event_id.clone(),
                governance_event_digest: governance.event_digest.clone(),
                governance_cursor: governance.governance_cursor,
            },
        )
        .collect::<Vec<_>>();

    let projection_paths = vec![
        write_projection(
            &projection_directory,
            "latest-subject-snapshots.json",
            &snapshots,
        )?,
        write_projection(&projection_directory, "ontology-at-cursor.json", &cut)?,
        write_projection(
            &projection_directory,
            "ontology-from-checkpoint.json",
            &checkpoint_cut,
        )?,
        write_projection(
            &projection_directory,
            "projection-checkpoint.json",
            &checkpoint,
        )?,
        write_projection(&projection_directory, "governed-node-views.json", &views)?,
        write_projection(&projection_directory, "context-projection.json", &context)?,
        write_projection(&projection_directory, "lineage.json", &lineage)?,
    ];
    fs::write(
        projection_directory.join("human-view.md"),
        cal_ontology_lifecycle::human_projection(&cut),
    )?;

    let mut projection_digests = projection_paths
        .iter()
        .map(|path| {
            Ok(ProjectionDigest {
                path: path
                    .strip_prefix(output)?
                    .to_string_lossy()
                    .replace('\\', "/"),
                sha256: file_sha256(path)?,
            })
        })
        .collect::<AnyResult<Vec<_>>>()?;
    let human_path = projection_directory.join("human-view.md");
    projection_digests.push(ProjectionDigest {
        path: "projections/human-view.md".to_owned(),
        sha256: file_sha256(&human_path)?,
    });
    projection_digests.sort_by(|left, right| left.path.cmp(&right.path));

    let result = RunResult {
        schema_version: "cal-w7-rehearsal-run-result/v1".to_owned(),
        epoch_id: manifest.epoch_id,
        ontology_id: manifest.ontology_id,
        result: "PASS".to_owned(),
        semantic_event_count: pending.len(),
        governance_event_count: governance.len(),
        node_count: nodes.len(),
        relation_count: relations.len(),
        relation_vocabulary_count: vocabulary.len(),
        lineage_count: lineage.len(),
        final_semantic_cursor: final_cursor,
        checkpoint_cursor: manifest.rehearsal_contract.checkpoint_cursor,
        direct_and_checkpoint_rebuild_equal: true,
        exact_governance_join_count: views.len(),
        projection_digests,
        authority_effect: "none".to_owned(),
        claim_ceiling: "Isolated deterministic W7 rehearsal result only; no source mutation, ontology admission or acceptance, publication, release, deployment, cutover, credentials, destructive action, or external effect.".to_owned(),
    };
    write_projection(output, "run-result.json", &result)?;
    Ok(())
}
