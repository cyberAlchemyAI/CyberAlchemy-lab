pub mod kernel;
use kernel::*;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::{Component, Path};
pub type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;
pub const PROFILE: &str = "source-record-profile/v1";

pub fn sha(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
fn require(ok: bool, message: &str) -> Result<()> {
    if !ok {
        return Err(message.to_string().into());
    }
    Ok(())
}
fn text<'a>(v: &'a Value, key: &str) -> Result<&'a str> {
    v.get(key)
        .and_then(Value::as_str)
        .filter(|s| !s.is_empty())
        .ok_or_else(|| format!("missing string field {key}").into())
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Source {
    pub root: String,
    pub path: String,
    pub sha256: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Registry {
    pub source: Source,
    pub selector: String,
    pub id_field: String,
    pub type_field: String,
    pub source_field: Option<String>,
    pub target_field: Option<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Package {
    pub package_key: String,
    pub ontology_id: String,
    pub profile: Source,
    pub owner: String,
    pub source_status: String,
    pub nodes: Registry,
    pub relations: Registry,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Manifest {
    pub schema_version: String,
    pub authority_effect: String,
    pub roots: BTreeMap<String, String>,
    pub packages: Vec<Package>,
    pub unsupported: Vec<Value>,
}
fn read_source(manifest: &Manifest, source: &Source) -> Result<Value> {
    require(
        !Path::new(&source.path).is_absolute()
            && Path::new(&source.path)
                .components()
                .all(|c| matches!(c, Component::Normal(_))),
        "unsafe source path",
    )?;
    let root = Path::new(
        manifest
            .roots
            .get(&source.root)
            .ok_or("unknown source root")?,
    )
    .canonicalize()?;
    let path = root.join(&source.path);
    require(!path.is_symlink(), "source symlink refused")?;
    let resolved = path.canonicalize()?;
    require(resolved.starts_with(&root), "source escapes root")?;
    let bytes = fs::read(resolved)?;
    require(
        sha(&bytes) == source.sha256,
        &format!("source digest drift: {}", source.path),
    )?;
    Ok(serde_json::from_slice(&bytes)?)
}
fn records(manifest: &Manifest, registry: &Registry) -> Result<Vec<Value>> {
    let doc = read_source(manifest, &registry.source)?;
    let records = doc
        .pointer(&registry.selector)
        .and_then(Value::as_array)
        .ok_or("array selector missing")?;
    require(
        records.iter().all(Value::is_object),
        "records must be objects",
    )?;
    Ok(records.clone())
}
pub fn qualified(kind: &str, raw: &str) -> String {
    format!("{kind}-{}", sha(raw.as_bytes()))
}
fn properties(
    record: &Value,
    package: &Package,
    registry: &Registry,
    index: usize,
) -> Result<TypedPropertySet> {
    let binding = json!({"package_key":package.package_key,"path":registry.source.path,
        "sha256":registry.source.sha256,"selector":format!("{}/{}",registry.selector,index),
        "record_sha256":sha(canonical_json(record)?.as_bytes())});
    Ok(TypedPropertySet {
        profile_ref: PROFILE.into(),
        values: BTreeMap::from([
            ("source_record".into(), record.clone()),
            ("source_binding".into(), binding),
        ]),
    })
}
pub fn plan(manifest: &Manifest) -> Result<Vec<(SemanticEvent, GovernanceEvent)>> {
    require(
        manifest.schema_version == "cal-source-import-manifest/v1"
            && manifest.authority_effect == "none",
        "invalid manifest or authority inflation",
    )?;
    require(!manifest.packages.is_empty(), "empty manifest")?;
    let mut packages = manifest.packages.clone();
    packages.sort_by(|a, b| a.package_key.cmp(&b.package_key));
    require(
        packages
            .windows(2)
            .all(|w| w[0].package_key != w[1].package_key),
        "duplicate package key",
    )?;
    let mut output = Vec::new();
    for package in packages {
        require(
            package.package_key
                == format!(
                    "pkg-{}",
                    sha(format!("{}:{}", package.profile.root, package.profile.path).as_bytes())
                ),
            "package key does not match source-qualified profile identity",
        )?;
        require(
            !package.owner.is_empty() && !package.source_status.is_empty(),
            "missing source owner or status",
        )?;
        let profile = read_source(manifest, &package.profile)?;
        let profile_id = profile
            .get("ontology_id")
            .or_else(|| profile.get("package_id"))
            .and_then(Value::as_str);
        require(
            profile_id == Some(package.ontology_id.as_str()),
            "profile identity mismatch",
        )?;
        let mut nodes: Vec<_> = records(manifest, &package.nodes)?
            .into_iter()
            .enumerate()
            .collect();
        let mut relations: Vec<_> = records(manifest, &package.relations)?
            .into_iter()
            .enumerate()
            .collect();
        let mut node_ids = BTreeSet::new();
        for (_, n) in &nodes {
            require(
                node_ids.insert(text(n, &package.nodes.id_field)?.to_owned()),
                "duplicate node id",
            )?;
        }
        require(!nodes.is_empty(), "empty node registry")?;
        let mut relation_ids = BTreeSet::new();
        for (_, r) in &relations {
            require(
                relation_ids.insert(text(r, &package.relations.id_field)?.to_owned()),
                "duplicate relation id",
            )?;
            let from = text(
                r,
                package
                    .relations
                    .source_field
                    .as_deref()
                    .ok_or("source mapping missing")?,
            )?;
            let to = text(
                r,
                package
                    .relations
                    .target_field
                    .as_deref()
                    .ok_or("target mapping missing")?,
            )?;
            require(
                node_ids.contains(from) && node_ids.contains(to),
                "unresolved relation endpoint; explicit adapter required",
            )?;
        }
        nodes.sort_by_key(|(_, v)| v[&package.nodes.id_field].as_str().unwrap().to_owned());
        relations.sort_by_key(|(_, v)| v[&package.relations.id_field].as_str().unwrap().to_owned());
        for (kind, rows, registry) in [
            (SubjectKind::Node, nodes, &package.nodes),
            (SubjectKind::Relation, relations, &package.relations),
        ] {
            for (index, record) in rows {
                let id = text(&record, &registry.id_field)?;
                let source_type = text(&record, &registry.type_field)?;
                let identity = OntologySubjectIdentity {
                    subject_id: qualified(&kind.to_string(), id),
                    ontology_id: package.package_key.clone(),
                    subject_kind: kind,
                    type_ref: qualified("source-type", source_type),
                };
                let props = properties(&record, &package, registry, index)?;
                let state = if kind == SubjectKind::Node {
                    OntologySemanticState::Node(OntologyNodeSemanticState {
                        identity: identity.clone(),
                        lifecycle: Lifecycle::Active,
                        label: record
                            .get("label")
                            .and_then(Value::as_str)
                            .unwrap_or(id)
                            .into(),
                        definition_or_claim: record
                            .get("definition_or_claim")
                            .or_else(|| record.get("claim"))
                            .or_else(|| record.get("summary"))
                            .and_then(Value::as_str)
                            .filter(|s| !s.is_empty())
                            .unwrap_or("Source record; full meaning retained in source_record.")
                            .into(),
                        scope: format!(
                            "Lossless source record import; package={}; source_status={}",
                            package.package_key, package.source_status
                        ),
                        semantic_components: vec![],
                        semantic_definition_refs: vec![DefinitionReference {
                            definition_id: qualified("record", id),
                            selector_sha256: sha(canonical_json(&record)?.as_bytes()),
                        }],
                        typed_properties: props,
                        use_obligations: vec![],
                        forbidden_collapse: vec![],
                        profile_ref: PROFILE.into(),
                    })
                } else {
                    let direction = match record.get("direction").and_then(Value::as_str) {
                        None | Some("directed") => RelationDirection::Directed,
                        Some("symmetric") => RelationDirection::Symmetric,
                        _ => return Err("unsupported relation direction".into()),
                    };
                    OntologySemanticState::Relation(OntologyRelationSemanticState {
                        identity: identity.clone(),
                        lifecycle: Lifecycle::Active,
                        source_node_id: qualified(
                            "node",
                            text(&record, registry.source_field.as_deref().unwrap())?,
                        ),
                        target_node_id: qualified(
                            "node",
                            text(&record, registry.target_field.as_deref().unwrap())?,
                        ),
                        direction,
                        typed_properties: props,
                        forbidden_collapse: vec![],
                    })
                };
                let cursor = (output.len() + 1) as u64;
                let mut event = SemanticEvent {
                    source_kind: SourceKind::CanonicalEvent,
                    event_family: EventFamily::Semantic,
                    event_id: format!("import-semantic-{cursor:08}"),
                    event_digest: ZERO_DIGEST.into(),
                    stream_id: identity.semantic_stream_id(),
                    subject_identity: identity.clone(),
                    previous_event_digest: None,
                    semantic_cursor: cursor,
                    complete_resulting_semantic_state: state,
                };
                seal_semantic_event(&mut event)?;
                let reference = ExactSemanticEventReference {
                    semantic_event_id: event.event_id.clone(),
                    semantic_event_digest: event.event_digest.clone(),
                    semantic_cursor: cursor,
                };
                // The imported authority/challenge fields remain source data, not operative grants.
                let owner = record
                    .get("owner_route")
                    .and_then(Value::as_str)
                    .filter(|s| !s.is_empty())
                    .unwrap_or(&package.owner);
                let governance=OntologyGovernanceState{
                    semantic_ref:reference.clone(),
                    provenance:vec![ProvenanceEntry{source_ref:format!("{}#{};sha256={}",registry.source.path,registry.selector,registry.source.sha256),
                        relation:"lossless-record-import".into(),operation:"prototype-source-import".into(),
                        owner_route:owner.into(),posture:package.source_status.clone()}],
                    owner_route:owner.into(),candidate_or_maturity_status:"candidate-import".into(),
                    promotion_state_or_handle:"not-promoted".into(),
                    authority_kind_and_posture:AuthorityKindAndPosture{kind:"source-reference".into(),posture:package.source_status.clone()},
                    authority_effect:AuthorityEffect::None,
                    evidence_confidence:ConfidenceReference{scheme_ref:"source-import/v1".into(),level:"exact-source-record".into()},
                    commitment_confidence:ConfidenceReference{scheme_ref:"source-import/v1".into(),level:"prototype".into()},
                    challenge_contract:ChallengeContract{challenge_response:"Compare the original record and route any semantic dispute to its source owner.".into(),
                        valid_challenge_modes:vec![ChallengeMode::Evidence,ChallengeMode::Contradiction,ChallengeMode::OwnerReview],
                        contradiction_edges:vec![],validation_edges:vec![],owner_route:owner.into(),
                        resolution_gate:"source-owner-review".into(),blocking_questions:vec![],
                        challenge_residue_route:owner.into()},
                    residue:vec![],conflicts:vec![],drift_owner:owner.into(),invalidation_route:owner.into(),
                };
                let mut gov = GovernanceEvent {
                    source_kind: SourceKind::CanonicalEvent,
                    event_family: EventFamily::Governance,
                    event_id: format!("import-governance-{cursor:08}"),
                    event_digest: ZERO_DIGEST.into(),
                    stream_id: identity.governance_stream_id(),
                    semantic_ref: reference,
                    governance_cursor: cursor,
                    previous_event_digest: None,
                    complete_resulting_governance_state: governance,
                };
                seal_governance_event(&mut gov)?;
                output.push((event, gov));
            }
        }
    }
    kernel::validate_import_history(&output)?;
    Ok(output)
}
fn write_new(path: &Path, value: &impl Serialize) -> Result<()> {
    let mut f = OpenOptions::new().write(true).create_new(true).open(path)?;
    f.write_all(canonical_json(value)?.as_bytes())?;
    f.sync_all()?;
    Ok(())
}
pub fn import(manifest_path: &Path, target: &Path) -> Result<Value> {
    require(!target.exists() && !target.is_symlink(), "target exists")?;
    for ancestor in target.ancestors() {
        require(!ancestor.is_symlink(), "symlink target ancestor")?;
    }
    let bytes = fs::read(manifest_path)?;
    let manifest: Manifest = serde_json::from_slice(&bytes)?;
    let pairs = plan(&manifest)?; // All source and mapping checks precede any target writes.
    fs::create_dir(target)?; // Require an existing parent, reserve one new directory.
    write_new(
        &target.join("IMPORT-IN-PROGRESS"),
        &json!({"manifest_sha256":sha(&bytes)}),
    )?;
    fs::create_dir(target.join("semantic-events"))?;
    fs::create_dir(target.join("governance-events"))?;
    let mut store = EventStore::load(
        target.join("semantic-events"),
        target.join("governance-events"),
    )?;
    store.append_semantic_batch(
        target.join("semantic-events"),
        pairs
            .iter()
            .map(|(e, _)| AppendSemanticEventRequest {
                expected_stream_version: 0,
                event: e.clone(),
            })
            .collect(),
    )?;
    store.append_governance_batch(
        target.join("governance-events"),
        pairs
            .iter()
            .map(|(_, e)| AppendGovernanceEventRequest {
                expected_stream_version: 0,
                event: e.clone(),
            })
            .collect(),
    )?;
    store.ontology_at(pairs.len() as u64)?;
    write_new(
        &target.join("import.json"),
        &json!({"manifest":manifest,"manifest_sha256":sha(&bytes),
        "semantic_events":pairs.len(),"governance_events":pairs.len(),"authority_effect":"none"}),
    )?;
    fs::remove_file(target.join("IMPORT-IN-PROGRESS"))?;
    observe(target, None)
}
pub fn open(target: &Path) -> Result<EventStore> {
    require(
        !target.join("IMPORT-IN-PROGRESS").exists(),
        "incomplete import; preserve for inspection",
    )?;
    let receipt: Value = serde_json::from_slice(&fs::read(target.join("import.json"))?)?;
    require(
        receipt["authority_effect"] == "none",
        "import authority inflation",
    )?;
    let store = EventStore::load(
        target.join("semantic-events"),
        target.join("governance-events"),
    )?;
    require(
        store.semantic_events().len() as u64
            == receipt["semantic_events"]
                .as_u64()
                .ok_or("missing semantic count")?,
        "semantic history count differs",
    )?;
    require(
        store.governance_events().len() as u64
            == receipt["governance_events"]
                .as_u64()
                .ok_or("missing governance count")?,
        "governance history count differs",
    )?;
    Ok(store)
}
pub fn observe(target: &Path, package: Option<&str>) -> Result<Value> {
    let store = open(target)?;
    let cursor = store
        .semantic_events()
        .last()
        .ok_or("empty store")?
        .event
        .semantic_cursor;
    let cut = store.ontology_at(cursor)?;
    let selected: Vec<_> = cut
        .subjects
        .iter()
        .filter(|s| package.is_none_or(|p| s.identity.ontology_id == p))
        .collect();
    require(!selected.is_empty(), "unknown or empty package selector")?;
    let context = store.context_projection(
        "source-import-context",
        &ContextSelector {
            semantic_cursor: cursor,
            required_subject_set: selected.iter().map(|s| s.identity.clone()).collect(),
            governance_join_policy: GovernanceJoinPolicy::RequireExact,
            intended_use: "source-record-inspection".into(),
            projection_profile: ProjectionProfile::TestCompleteV1,
        },
    )?;
    let snapshots = store.latest_subject_snapshots(cursor)?;
    Ok(
        json!({"result":"PASS","authority_effect":"none","process_model":"on-demand-cli",
        "semantic_events":store.semantic_events().len(),"governance_events":store.governance_events().len(),
        "latest_snapshots":snapshots.len(),"selected_nodes":context.selected_node_ids.len(),
        "selected_relations":context.selected_relation_ids.len(),
        "package_keys":selected.iter().map(|s|s.identity.ontology_id.clone()).collect::<BTreeSet<_>>(),
        "source_event_set_digest":cut.source_event_set_digest,"context":context}),
    )
}
pub fn export(target: &Path, package: Option<&str>) -> Result<Value> {
    let store = open(target)?;
    let cursor = store
        .semantic_events()
        .last()
        .ok_or("empty store")?
        .event
        .semantic_cursor;
    let cut = store.ontology_at(cursor)?;
    let rows: Vec<_> = cut
        .subjects
        .iter()
        .filter(|s| package.is_none_or(|p| s.identity.ontology_id == p))
        .map(|s| {
            let props = match &s.semantic_state {
                OntologySemanticState::Node(n) => &n.typed_properties,
                OntologySemanticState::Relation(r) => &r.typed_properties,
            };
            json!({"identity":s.identity,"source_binding":props.values["source_binding"],
                "source_record":props.values["source_record"]})
        })
        .collect();
    require(!rows.is_empty(), "unknown or empty package selector")?;
    Ok(json!({"authority_effect":"none","records":rows}))
}
