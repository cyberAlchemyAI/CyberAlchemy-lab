use cal_ontology_source_importer::{self as imp, kernel::*, *};
use serde_json::{Value, json};
use std::{collections::BTreeMap, fs, path::Path};
use tempfile::{TempDir, tempdir};
fn write(p: &Path, v: &Value) {
    fs::write(p, serde_json::to_vec_pretty(v).unwrap()).unwrap();
}
fn fixture() -> (TempDir, Manifest) {
    let t = tempdir().unwrap();
    let doc = json!({"ontology_id":"same-ontology","nodes":[
        {"id":"n1","type":"Entity","label":"One","properties":{"n":3,"b":true,"array":[1,null,"x"]},
         "challenge_contract":{"owner":"Human","modes":["evidence"]},"authority_effect":"source-only"},
        {"id":"n2","type":"Entity","label":"Two"}],
        "relations":[{"id":"n1","type":"depends_on","source":"n1","target":"n2"}]});
    write(&t.path().join("source.json"), &doc);
    let source = Source {
        root: "test".into(),
        path: "source.json".into(),
        sha256: sha(&fs::read(t.path().join("source.json")).unwrap()),
    };
    let registry = |selector: &str, id: &str, src: Option<&str>, dst: Option<&str>| Registry {
        source: source.clone(),
        selector: selector.into(),
        id_field: id.into(),
        type_field: "type".into(),
        source_field: src.map(str::to_owned),
        target_field: dst.map(str::to_owned),
    };
    let p = Package {
        package_key: format!("pkg-{}", sha(b"test:source.json")),
        ontology_id: "same-ontology".into(),
        profile: source.clone(),
        owner: "source owner".into(),
        source_status: "candidate".into(),
        nodes: registry("/nodes", "id", None, None),
        relations: registry("/relations", "id", Some("source"), Some("target")),
    };
    let m = Manifest {
        schema_version: "cal-source-import-manifest/v1".into(),
        authority_effect: "none".into(),
        roots: BTreeMap::from([("test".into(), t.path().to_str().unwrap().into())]),
        packages: vec![p],
        unsupported: vec![],
    };
    (t, m)
}
fn save(t: &TempDir, m: &Manifest) -> std::path::PathBuf {
    let p = t.path().join("manifest.json");
    fs::write(&p, serde_json::to_vec_pretty(m).unwrap()).unwrap();
    p
}
fn change(t: &TempDir, m: &mut Manifest, f: impl FnOnce(&mut Value)) {
    let p = t.path().join("source.json");
    let mut v: Value = serde_json::from_slice(&fs::read(&p).unwrap()).unwrap();
    f(&mut v);
    write(&p, &v);
    let digest = sha(&fs::read(&p).unwrap());
    m.packages[0].profile.sha256 = digest.clone();
    m.packages[0].nodes.source.sha256 = digest.clone();
    m.packages[0].relations.source.sha256 = digest;
}
#[test]
fn round_trip_preserves_every_json_value_and_challenge() {
    let (t, m) = fixture();
    let target = t.path().join("runtime");
    let initial = imp::import(&save(&t, &m), &target).unwrap();
    assert_eq!(initial, imp::observe(&target, None).unwrap());
    let exported = imp::export(&target, None).unwrap();
    let original: Value =
        serde_json::from_slice(&fs::read(t.path().join("source.json")).unwrap()).unwrap();
    for row in exported["records"].as_array().unwrap() {
        let selector = row["source_binding"]["selector"].as_str().unwrap();
        assert_eq!(&row["source_record"], original.pointer(selector).unwrap());
    }
    assert_eq!(exported["records"].as_array().unwrap().len(), 3);
    assert_eq!(initial["selected_nodes"], 2);
    assert_eq!(initial["selected_relations"], 1);
    assert_eq!(initial["authority_effect"], "none");
}
#[test]
fn independent_imports_are_byte_equal() {
    let (t, m) = fixture();
    let mp = save(&t, &m);
    let a = t.path().join("a");
    let b = t.path().join("b");
    imp::import(&mp, &a).unwrap();
    imp::import(&mp, &b).unwrap();
    for folder in ["semantic-events", "governance-events"] {
        for e in fs::read_dir(a.join(folder)).unwrap() {
            let e = e.unwrap();
            assert_eq!(
                fs::read(e.path()).unwrap(),
                fs::read(b.join(folder).join(e.file_name())).unwrap()
            );
        }
    }
}
#[test]
fn source_drift_refused_before_target_write() {
    let (t, m) = fixture();
    fs::write(t.path().join("source.json"), "{}").unwrap();
    let target = t.path().join("runtime");
    assert!(imp::import(&save(&t, &m), &target).is_err());
    assert!(!target.exists());
}
#[test]
fn duplicate_id_refused() {
    let (t, mut m) = fixture();
    change(&t, &mut m, |d| d["nodes"][1]["id"] = json!("n1"));
    assert!(plan(&m).is_err());
}
#[test]
fn endpoint_missing_refused() {
    let (t, mut m) = fixture();
    change(&t, &mut m, |d| {
        d["relations"][0]["target"] = json!("missing")
    });
    assert!(plan(&m).is_err());
}
#[test]
fn unsupported_direction_refused() {
    let (t, mut m) = fixture();
    change(&t, &mut m, |d| {
        d["relations"][0]["direction"] = json!("magic")
    });
    assert!(plan(&m).is_err());
}
#[test]
fn authority_inflation_refused() {
    let (_t, mut m) = fixture();
    m.authority_effect = "admit".into();
    assert!(
        plan(&m)
            .unwrap_err()
            .to_string()
            .contains("authority inflation")
    );
}
#[test]
fn unknown_mapping_refused() {
    let (_t, mut m) = fixture();
    m.packages[0].nodes.id_field = "invented".into();
    assert!(
        plan(&m)
            .unwrap_err()
            .to_string()
            .contains("missing string field")
    );
}
#[test]
fn invalid_runtime_identifier_refused_before_writes() {
    let (t, mut m) = fixture();
    m.packages[0].package_key = "invalid key".into();
    let target = t.path().join("runtime");
    assert!(imp::import(&save(&t, &m), &target).is_err());
    assert!(!target.exists());
}
#[test]
fn profile_qualified_identity_does_not_merge_equal_ontology_names() {
    let (t, mut m) = fixture();
    fs::copy(t.path().join("source.json"), t.path().join("other.json")).unwrap();
    let mut p = m.packages[0].clone();
    p.profile.path = "other.json".into();
    p.package_key = format!("pkg-{}", sha(b"test:other.json"));
    p.nodes.source.path = "other.json".into();
    p.relations.source.path = "other.json".into();
    m.packages.push(p);
    let target = t.path().join("runtime");
    let out = imp::import(&save(&t, &m), &target).unwrap();
    assert_eq!(out["package_keys"].as_array().unwrap().len(), 2);
    assert_eq!(out["selected_nodes"], 4);
    let scoped = imp::observe(&target, Some(&m.packages[0].package_key)).unwrap();
    assert_eq!(scoped["selected_nodes"], 2);
}
#[test]
fn existing_target_refused() {
    let (t, m) = fixture();
    let target = t.path().join("runtime");
    fs::create_dir(&target).unwrap();
    fs::write(target.join("keep"), "keep").unwrap();
    assert!(imp::import(&save(&t, &m), &target).is_err());
    assert_eq!(fs::read_to_string(target.join("keep")).unwrap(), "keep");
}
#[test]
fn missing_event_refused() {
    let (t, m) = fixture();
    let target = t.path().join("runtime");
    imp::import(&save(&t, &m), &target).unwrap();
    let p = fs::read_dir(target.join("semantic-events"))
        .unwrap()
        .next()
        .unwrap()
        .unwrap()
        .path();
    fs::remove_file(p).unwrap();
    assert!(imp::observe(&target, None).is_err());
}
#[test]
fn tampered_event_refused() {
    let (t, m) = fixture();
    let target = t.path().join("runtime");
    imp::import(&save(&t, &m), &target).unwrap();
    let p = fs::read_dir(target.join("semantic-events"))
        .unwrap()
        .next()
        .unwrap()
        .unwrap()
        .path();
    let mut e: Value = serde_json::from_slice(&fs::read(&p).unwrap()).unwrap();
    e["complete_resulting_semantic_state"]["typed_properties"]["values"]["source_record"]["injected"] =
        json!(true);
    write(&p, &e);
    assert!(imp::observe(&target, None).is_err());
}
#[test]
fn interrupted_import_refused() {
    let (t, m) = fixture();
    let target = t.path().join("runtime");
    imp::import(&save(&t, &m), &target).unwrap();
    fs::write(target.join("IMPORT-IN-PROGRESS"), "{}").unwrap();
    assert!(imp::observe(&target, None).is_err());
}
#[test]
fn closed_property_profile_refuses_unknown_fields() {
    let (t, m) = fixture();
    let mut pairs = plan(&m).unwrap();
    if let OntologySemanticState::Node(ref mut n) = pairs[0].0.complete_resulting_semantic_state {
        n.typed_properties
            .values
            .insert("extra".into(), json!(true));
    }
    seal_semantic_event(&mut pairs[0].0).unwrap();
    assert!(validate_import_history(&pairs).is_err());
    drop(t);
}
#[test]
fn latest_snapshot_uses_latest_subject_event() {
    let (t, m) = fixture();
    let target = t.path().join("runtime");
    imp::import(&save(&t, &m), &target).unwrap();
    let mut store = imp::open(&target).unwrap();
    let mut event = store.semantic_events()[0].event.clone();
    event.previous_event_digest = Some(event.event_digest.clone());
    event.semantic_cursor = 4;
    event.event_id = "update-4".into();
    if let OntologySemanticState::Node(ref mut n) = event.complete_resulting_semantic_state {
        n.label = "Updated".into();
    }
    seal_semantic_event(&mut event).unwrap();
    store
        .append_semantic_batch(
            target.join("semantic-events"),
            vec![AppendSemanticEventRequest {
                expected_stream_version: 1,
                event,
            }],
        )
        .unwrap();
    let reopened = EventStore::load(
        target.join("semantic-events"),
        target.join("governance-events"),
    )
    .unwrap();
    let snapshots = reopened.latest_subject_snapshots(4).unwrap();
    assert!(
        snapshots.iter().any(
            |s| matches!(&s.semantic_state,OntologySemanticState::Node(n) if n.label=="Updated")
        )
    );
    // Public importer commands are intentionally initial-import-only; receipt count now rejects this unreviewed update.
    assert!(imp::observe(&target, None).is_err());
}
