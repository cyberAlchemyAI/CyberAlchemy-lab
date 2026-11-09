pub mod kernel;
pub mod storage;
use kernel::*;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::{Component, Path},
};
pub type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;
pub const PROFILE: &str = "source-record-profile/v1";
pub const GRAPH: &str = "cal.source-runtime.v4";
pub type Pair = (SemanticEvent, GovernanceEvent);
pub fn sha(b: &[u8]) -> String {
    format!("{:x}", Sha256::digest(b))
}
pub fn need(ok: bool, s: &str) -> Result<()> {
    if !ok {
        return Err(s.into());
    }
    Ok(())
}
pub fn text<'a>(v: &'a Value, k: &str) -> Result<&'a str> {
    v.get(k)
        .and_then(Value::as_str)
        .filter(|s| !s.is_empty())
        .ok_or_else(|| format!("missing string {k}").into())
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
    pub direction_map: BTreeMap<String, String>,
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
    pub endpoint_aliases: BTreeMap<String, String>,
    pub documents: Vec<Source>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Manifest {
    pub schema_version: String,
    pub authority_effect: String,
    pub roots: BTreeMap<String, String>,
    pub packages: Vec<Package>,
}
pub fn bytes(m: &Manifest, s: &Source) -> Result<Vec<u8>> {
    need(
        !Path::new(&s.path).is_absolute()
            && Path::new(&s.path)
                .components()
                .all(|c| matches!(c, Component::Normal(_))),
        "unsafe source path",
    )?;
    let root = Path::new(m.roots.get(&s.root).ok_or("unknown source root")?).canonicalize()?;
    let path = root.join(&s.path);
    need(!path.is_symlink(), "source symlink")?;
    let resolved = path.canonicalize()?;
    need(resolved.starts_with(&root), "source escapes root")?;
    let b = fs::read(resolved)?;
    need(sha(&b) == s.sha256, &format!("source drift: {}", s.path))?;
    Ok(b)
}
fn rows(m: &Manifest, r: &Registry) -> Result<Vec<Value>> {
    let doc: Value = serde_json::from_slice(&bytes(m, &r.source)?)?;
    let a = doc
        .pointer(&r.selector)
        .and_then(Value::as_array)
        .ok_or("missing array selector")?;
    need(a.iter().all(Value::is_object), "nonobject record")?;
    Ok(a.clone())
}
pub fn record_id(v: &Value, r: &Registry) -> Result<String> {
    if r.id_field == "$tuple" {
        Ok(format!(
            "tuple-{}",
            sha(canonical_json(&json!([
                text(v, &r.type_field)?,
                text(
                    v,
                    r.source_field.as_deref().ok_or("missing source mapping")?
                )?,
                text(
                    v,
                    r.target_field.as_deref().ok_or("missing target mapping")?
                )?
            ]))?
            .as_bytes())
        ))
    } else {
        Ok(text(v, &r.id_field)?.into())
    }
}
pub fn q(package: &str, kind: &str, id: &str) -> String {
    format!("{package}:{kind}-{}", sha(id.as_bytes()))
}
fn endpoint(p: &Package, raw: &str) -> Result<String> {
    if let Some((alias, id)) = raw.split_once("::") {
        let key = p
            .endpoint_aliases
            .get(alias)
            .ok_or("undeclared endpoint alias")?;
        Ok(q(key, "node", id))
    } else {
        Ok(q(&p.package_key, "node", raw))
    }
}
pub fn props(s: &OntologySemanticState) -> &TypedPropertySet {
    match s {
        OntologySemanticState::Node(n) => &n.typed_properties,
        OntologySemanticState::Relation(r) => &r.typed_properties,
    }
}
pub fn props_mut(s: &mut OntologySemanticState) -> &mut TypedPropertySet {
    match s {
        OntologySemanticState::Node(n) => &mut n.typed_properties,
        OntologySemanticState::Relation(r) => &mut r.typed_properties,
    }
}
pub fn state(
    p: &Package,
    kind: &str,
    record: &Value,
    binding: Value,
) -> Result<OntologySemanticState> {
    let r = if kind == "node" {
        &p.nodes
    } else {
        &p.relations
    };
    let id = record_id(record, r)?;
    let typ = text(record, &r.type_field)?;
    let ident = OntologySubjectIdentity {
        subject_id: q(&p.package_key, kind, &id),
        ontology_id: GRAPH.into(),
        subject_kind: if kind == "node" {
            SubjectKind::Node
        } else {
            SubjectKind::Relation
        },
        type_ref: format!("source-type-{}", sha(typ.as_bytes())),
    };
    let properties = TypedPropertySet {
        profile_ref: PROFILE.into(),
        values: BTreeMap::from([
            ("source_record".into(), record.clone()),
            ("source_binding".into(), binding),
        ]),
    };
    if kind == "node" {
        Ok(OntologySemanticState::Node(OntologyNodeSemanticState {
            identity: ident,
            lifecycle: Lifecycle::Active,
            label: record
                .get("label")
                .and_then(Value::as_str)
                .filter(|s| !s.is_empty())
                .unwrap_or(&id)
                .into(),
            definition_or_claim: [
                "definition_or_claim",
                "claim",
                "summary",
                "meaning",
                "intent",
            ]
            .iter()
            .find_map(|k| {
                record
                    .get(k)
                    .and_then(Value::as_str)
                    .filter(|s| !s.is_empty())
            })
            .unwrap_or("Exact source record; no semantic authority inferred.")
            .into(),
            scope: format!(
                "Prototype representation of {}; source posture {}",
                p.package_key, p.source_status
            ),
            semantic_components: vec![],
            semantic_definition_refs: vec![DefinitionReference {
                definition_id: format!("record-{}", sha(id.as_bytes())),
                selector_sha256: sha(canonical_json(record)?.as_bytes()),
            }],
            typed_properties: properties,
            use_obligations: vec![],
            forbidden_collapse: vec![],
            profile_ref: PROFILE.into(),
        }))
    } else {
        let raw = record
            .get("direction")
            .and_then(Value::as_str)
            .unwrap_or("directed");
        let direction = r.direction_map.get(raw).ok_or("unmapped direction")?;
        Ok(OntologySemanticState::Relation(
            OntologyRelationSemanticState {
                identity: ident,
                lifecycle: Lifecycle::Active,
                source_node_id: endpoint(
                    p,
                    text(
                        record,
                        r.source_field.as_deref().ok_or("source mapping missing")?,
                    )?,
                )?,
                target_node_id: endpoint(
                    p,
                    text(
                        record,
                        r.target_field.as_deref().ok_or("target mapping missing")?,
                    )?,
                )?,
                direction: match direction.as_str() {
                    "directed" => RelationDirection::Directed,
                    "symmetric" => RelationDirection::Symmetric,
                    _ => return Err("invalid mapped direction".into()),
                },
                typed_properties: properties,
                forbidden_collapse: vec![],
            },
        ))
    }
}
fn binding(package: &str, s: &Source, selector: &str, record: &Value) -> Result<Value> {
    Ok(
        json!({"package_key":package,"path":s.path,"sha256":s.sha256,"selector":selector,
 "record_sha256":sha(canonical_json(record)?.as_bytes())}),
    )
}
pub fn pair(
    state: OntologySemanticState,
    p: &Package,
    cursor: u64,
    previous: Option<&Pair>,
) -> Result<Pair> {
    let ident = state.identity().clone();
    let mut sem = SemanticEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Semantic,
        event_id: format!("semantic-{cursor:08}"),
        event_digest: ZERO_DIGEST.into(),
        stream_id: ident.semantic_stream_id(),
        subject_identity: ident.clone(),
        previous_event_digest: previous.map(|p| p.0.event_digest.clone()),
        semantic_cursor: cursor,
        complete_resulting_semantic_state: state,
    };
    seal_semantic_event(&mut sem)?;
    let reference = ExactSemanticEventReference {
        semantic_event_id: sem.event_id.clone(),
        semantic_event_digest: sem.event_digest.clone(),
        semantic_cursor: cursor,
    };
    let source = &props(&sem.complete_resulting_semantic_state).values["source_binding"];
    let original = &props(&sem.complete_resulting_semantic_state).values["source_record"];
    let owner = original
        .get("owner_route")
        .and_then(Value::as_str)
        .filter(|x| !x.is_empty())
        .unwrap_or(&p.owner);
    let govstate=OntologyGovernanceState{semantic_ref:reference.clone(),
 provenance:vec![ProvenanceEntry{source_ref:format!("{}#{};sha256={}",source["path"],source["selector"],source["sha256"]),
 relation:"source-preserved".into(),operation:"prototype-event-construction".into(),owner_route:owner.into(),posture:p.source_status.clone()}],
 owner_route:owner.into(),candidate_or_maturity_status:"candidate-representation".into(),promotion_state_or_handle:"not-promoted".into(),
 authority_kind_and_posture:AuthorityKindAndPosture{kind:"source-reference".into(),posture:p.source_status.clone()},authority_effect:AuthorityEffect::None,
 evidence_confidence:ConfidenceReference{scheme_ref:"source-record/v1".into(),level:"exact-record".into()},
 commitment_confidence:ConfidenceReference{scheme_ref:"source-record/v1".into(),level:"prototype".into()},
 challenge_contract:ChallengeContract{challenge_response:"Preserve original challenge contract as source data; route interpretation to source owner.".into(),
 valid_challenge_modes:vec![ChallengeMode::Evidence,ChallengeMode::Contradiction,ChallengeMode::OwnerReview],
 contradiction_edges:vec![],validation_edges:vec![],owner_route:owner.into(),resolution_gate:"source-owner-review".into(),
 blocking_questions:vec![],challenge_residue_route:owner.into()},residue:vec![],conflicts:vec![],
 drift_owner:owner.into(),invalidation_route:owner.into()};
    let mut gov = GovernanceEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Governance,
        event_id: format!("governance-{cursor:08}"),
        event_digest: ZERO_DIGEST.into(),
        stream_id: ident.governance_stream_id(),
        semantic_ref: reference,
        governance_cursor: cursor,
        previous_event_digest: previous.map(|p| p.1.event_digest.clone()),
        complete_resulting_governance_state: govstate,
    };
    seal_governance_event(&mut gov)?;
    Ok((sem, gov))
}
pub fn plan(m: &Manifest) -> Result<Vec<Pair>> {
    need(
        m.schema_version == "cal-source-runtime-manifest/v1" && m.authority_effect == "none",
        "manifest authority/schema mismatch",
    )?;
    need(!m.packages.is_empty(), "empty manifest")?;
    let mut pkgs = m.packages.clone();
    pkgs.sort_by(|a, b| a.package_key.cmp(&b.package_key));
    need(
        pkgs.windows(2)
            .all(|p| p[0].package_key != p[1].package_key),
        "duplicate package key",
    )?;
    let allkeys: BTreeSet<_> = pkgs.iter().map(|p| p.package_key.clone()).collect();
    let mut states = Vec::new();
    let mut identities = BTreeSet::new();
    let mut nodes = BTreeSet::new();
    for p in &pkgs {
        need(
            !p.owner.is_empty() && !p.source_status.is_empty(),
            "missing source owner/status",
        )?;
        need(
            p.package_key
                == format!(
                    "pkg-{}",
                    sha(format!("{}:{}", p.profile.root, p.profile.path).as_bytes())
                ),
            "package key mismatch",
        )?;
        need(
            p.endpoint_aliases.values().all(|v| allkeys.contains(v)),
            "unknown endpoint package",
        )?;
        let profile: Value = serde_json::from_slice(&bytes(m, &p.profile)?)?;
        need(
            profile
                .get("ontology_id")
                .or_else(|| profile.get("package_id"))
                .and_then(Value::as_str)
                == Some(&p.ontology_id),
            "profile identity mismatch",
        )?;
        for (kind, r) in [("node", &p.nodes), ("relation", &p.relations)] {
            let rr = rows(m, r)?;
            if kind == "node" {
                need(!rr.is_empty(), "empty node array")?;
            }
            for (index, record) in rr.iter().enumerate() {
                let state = state(
                    p,
                    kind,
                    record,
                    binding(
                        &p.package_key,
                        &r.source,
                        &format!("{}/{}", r.selector, index),
                        record,
                    )?,
                )?;
                need(
                    identities.insert(state.identity().clone()),
                    "duplicate subject identity",
                )?;
                if kind == "node" {
                    nodes.insert(state.identity().subject_id.clone());
                }
                states.push((state, p));
            }
        }
        let mut docs = BTreeSet::new();
        for source in &p.documents {
            need(
                docs.insert((source.root.clone(), source.path.clone())),
                "duplicate document",
            )?;
            let content = String::from_utf8(bytes(m, source)?)?;
            let record = json!({"document_path":source.path,"content":content,"content_sha256":source.sha256});
            let properties = TypedPropertySet {
                profile_ref: PROFILE.into(),
                values: BTreeMap::from([
                    ("source_record".into(), record.clone()),
                    (
                        "source_binding".into(),
                        binding(&p.package_key, source, "/document", &record)?,
                    ),
                ]),
            };
            let state = OntologySemanticState::Node(OntologyNodeSemanticState {
                identity: OntologySubjectIdentity {
                    subject_id: q(&p.package_key, "document", &source.path),
                    ontology_id: GRAPH.into(),
                    subject_kind: SubjectKind::Node,
                    type_ref: "source-document".into(),
                },
                lifecycle: Lifecycle::Active,
                label: source.path.clone(),
                definition_or_claim: "Exact supporting source document; non-executable reference."
                    .into(),
                scope: p.package_key.clone(),
                semantic_components: vec![],
                semantic_definition_refs: vec![DefinitionReference {
                    definition_id: format!("document-{}", sha(source.path.as_bytes())),
                    selector_sha256: source.sha256.clone(),
                }],
                typed_properties: properties,
                use_obligations: vec![],
                forbidden_collapse: vec![],
                profile_ref: PROFILE.into(),
            });
            need(
                identities.insert(state.identity().clone()),
                "duplicate document identity",
            )?;
            states.push((state, p));
        }
    }
    for (s, _) in &states {
        if let OntologySemanticState::Relation(r) = s {
            need(
                nodes.contains(&r.source_node_id) && nodes.contains(&r.target_node_id),
                "unresolved relation endpoint",
            )?;
        }
    }
    states.sort_by_key(|(s, _)| (s.identity().subject_kind, s.identity().subject_id.clone()));
    let mut pairs = Vec::new();
    for (s, p) in states {
        pairs.push(pair(s, p, pairs.len() as u64 + 1, None)?);
    }
    kernel::validate_import_history(&pairs)?;
    Ok(pairs)
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Command {
    pub operation: String,
    pub package_key: String,
    pub kind: String,
    pub record: Value,
    pub expected_version: u64,
}
pub fn command_pairs(m: &Manifest, pairs: &[Pair], cmd: &Command) -> Result<Vec<Pair>> {
    need(cmd.kind == "node" || cmd.kind == "relation", "invalid kind")?;
    need(
        ["create", "update", "retire"].contains(&cmd.operation.as_str()),
        "invalid operation",
    )?;
    let p = m
        .packages
        .iter()
        .find(|p| p.package_key == cmd.package_key)
        .ok_or("unknown package")?;
    let encoded = canonical_json(cmd)?;
    let s = Source {
        root: "runtime".into(),
        path: "runtime-commands".into(),
        sha256: sha(encoded.as_bytes()),
    };
    let mut next = state(
        p,
        &cmd.kind,
        &cmd.record,
        binding(
            &p.package_key,
            &s,
            &format!("/{}", sha(encoded.as_bytes())),
            &cmd.record,
        )?,
    )?;
    let history: Vec<_> = pairs
        .iter()
        .filter(|p| p.0.subject_identity.subject_id == next.identity().subject_id)
        .collect();
    need(
        history.len() as u64 == cmd.expected_version,
        "expected version mismatch",
    )?;
    let old = history.last().copied();
    match cmd.operation.as_str() {
        "create" => need(old.is_none(), "subject exists")?,
        "update" | "retire" => {
            let previous = old.ok_or("subject missing")?;
            need(
                previous.0.subject_identity == *next.identity(),
                "identity/type mutation refused",
            )?;
            need(
                previous.0.complete_resulting_semantic_state.lifecycle() == Lifecycle::Active,
                "subject not active",
            )?;
        }
        _ => unreachable!(),
    }
    if cmd.operation == "retire" {
        match &mut next {
            OntologySemanticState::Node(n) => n.lifecycle = Lifecycle::Retired,
            OntologySemanticState::Relation(r) => r.lifecycle = Lifecycle::Retired,
        }
    }
    let pair = pair(next, p, pairs.len() as u64 + 1, old)?;
    let mut all = pairs.to_vec();
    all.push(pair.clone());
    kernel::validate_import_history(&all)?;
    Ok(vec![pair])
}
pub fn project(pairs: &[Pair], package: Option<&str>, export: bool) -> Result<Value> {
    let store = kernel::replay_pairs(pairs)?;
    let cursor = pairs.len() as u64;
    let cut = store.ontology_at(cursor)?;
    let mut selected: BTreeSet<_> = cut
        .subjects
        .iter()
        .filter(|s| {
            package.is_none_or(|p| {
                props(&s.semantic_state).values["source_binding"]["package_key"] == p
            })
        })
        .map(|s| s.identity.clone())
        .collect();
    need(!selected.is_empty(), "unknown package selector")?;
    if export {
        let records:Vec<_>=cut.subjects.iter().filter(|s|selected.contains(&s.identity)).map(|s|{
 let p=props(&s.semantic_state);json!({"identity":s.identity,"lifecycle":s.semantic_state.lifecycle(),"source_binding":p.values["source_binding"],"source_record":p.values["source_record"]})}).collect();
        return Ok(json!({"authority_effect":"none","records":records}));
    }
    // A Context including cross-package relations includes their endpoint nodes.
    let mut endpoints = BTreeSet::new();
    for s in &cut.subjects {
        if selected.contains(&s.identity) {
            if let OntologySemanticState::Relation(r) = &s.semantic_state {
                endpoints.insert(r.source_node_id.clone());
                endpoints.insert(r.target_node_id.clone());
            }
        }
    }
    for s in &cut.subjects {
        if endpoints.contains(&s.identity.subject_id) {
            selected.insert(s.identity.clone());
        }
    }
    let context = store.context_projection(
        "source-runtime-context",
        &ContextSelector {
            semantic_cursor: cursor,
            required_subject_set: selected.iter().cloned().collect(),
            governance_join_policy: GovernanceJoinPolicy::RequireExact,
            intended_use: "prototype-inspection".into(),
            projection_profile: ProjectionProfile::TestCompleteV1,
        },
    )?;
    let node_count = cut
        .subjects
        .iter()
        .filter(|s| {
            s.identity.subject_kind == SubjectKind::Node && s.identity.type_ref != "source-document"
        })
        .count();
    let documents = cut
        .subjects
        .iter()
        .filter(|s| s.identity.type_ref == "source-document")
        .count();
    Ok(
        json!({"result":"PASS","authority_effect":"none","semantic_events":pairs.len(),"governance_events":pairs.len(),
 "nodes":node_count,"relations":cut.subjects.iter().filter(|s|s.identity.subject_kind==SubjectKind::Relation).count(),"documents":documents,
 "latest_snapshots":store.latest_subject_snapshots(cursor)?.len(),"source_event_set_digest":cut.source_event_set_digest,
 "context_nodes":context.selected_node_ids.len(),"context_relations":context.selected_relation_ids.len(),"context":context}),
    )
}
