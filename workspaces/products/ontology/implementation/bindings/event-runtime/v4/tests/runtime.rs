use cal_ontology_source_runtime::{self as rt, Command, Manifest, storage};
use serde_json::{Value, json};
use std::{fs, path::Path};
use tempfile::{TempDir, tempdir};
fn write(p: &Path, v: &Value) {
    fs::write(p, serde_json::to_vec_pretty(v).unwrap()).unwrap();
}
fn fixture() -> (TempDir, Manifest) {
    let t = tempdir().unwrap();
    let source = json!({"ontology_id":"same-name","nodes":[
 {"id":"a","type":"Entity","label":"A","challenge_contract":{"owner":"human","questions":["why"]},"props":{"bool":true,"null":null}},
 {"id":"b","type":"Entity","label":"B"}],"relations":[{"id":"a","type":"links","source":"a","target":"b"}]});
    write(&t.path().join("source.json"), &source);
    let sha = rt::sha(&fs::read(t.path().join("source.json")).unwrap());
    let sr = json!({"root":"test","path":"source.json","sha256":sha});
    let key = format!("pkg-{}", rt::sha(b"test:source.json"));
    let m = json!({"schema_version":"cal-source-runtime-manifest/v1","authority_effect":"none","roots":{"test":t.path()},
 "packages":[{"package_key":key,"ontology_id":"same-name","profile":sr,"owner":"source-owner","source_status":"candidate",
 "nodes":{"source":sr,"selector":"/nodes","id_field":"id","type_field":"type","source_field":null,"target_field":null,"direction_map":{}},
 "relations":{"source":sr,"selector":"/relations","id_field":"id","type_field":"type","source_field":"source","target_field":"target","direction_map":{"directed":"directed"}},
 "endpoint_aliases":{},"documents":[sr]}]});
    (t, serde_json::from_value(m).unwrap())
}
fn save(t: &TempDir, m: &Manifest) -> std::path::PathBuf {
    let p = t.path().join("manifest.json");
    fs::write(&p, serde_json::to_vec_pretty(m).unwrap()).unwrap();
    p
}
fn boot(t: &TempDir, m: &Manifest) -> std::path::PathBuf {
    let p = t.path().join("store");
    storage::import(&save(t, m), &p).unwrap();
    p
}
fn change(t: &TempDir, m: &mut Manifest, f: impl FnOnce(&mut Value)) {
    let p = t.path().join("source.json");
    let mut v: Value = serde_json::from_slice(&fs::read(&p).unwrap()).unwrap();
    f(&mut v);
    write(&p, &v);
    let s = rt::sha(&fs::read(&p).unwrap());
    let p = &mut m.packages[0];
    p.profile.sha256 = s.clone();
    p.nodes.source.sha256 = s.clone();
    p.relations.source.sha256 = s.clone();
    p.documents[0].sha256 = s;
}
fn cmd(m: &Manifest, operation: &str, kind: &str, record: Value, expected: u64) -> Command {
    Command {
        operation: operation.into(),
        kind: kind.into(),
        package_key: m.packages[0].package_key.clone(),
        record,
        expected_version: expected,
    }
}
fn tree(p: &Path) -> Vec<(String, Vec<u8>)> {
    let mut v: Vec<_> = fs::read_dir(p)
        .unwrap()
        .map(|e| {
            let e = e.unwrap();
            (
                e.file_name().to_str().unwrap().to_string(),
                fs::read(e.path()).unwrap(),
            )
        })
        .collect();
    v.sort();
    v
}
#[test]
fn source_roundtrip_and_document_preservation() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    let loaded = storage::load(&p).unwrap();
    let x = rt::project(&loaded.pairs, None, true).unwrap();
    let original: Value =
        serde_json::from_slice(&fs::read(t.path().join("source.json")).unwrap()).unwrap();
    assert_eq!(x["records"].as_array().unwrap().len(), 4);
    for row in x["records"].as_array().unwrap() {
        let sel = row["source_binding"]["selector"].as_str().unwrap();
        if sel == "/document" {
            assert_eq!(
                row["source_record"]["content"],
                fs::read_to_string(t.path().join("source.json")).unwrap()
            );
        } else {
            assert_eq!(&row["source_record"], original.pointer(sel).unwrap());
        }
    }
}
#[test]
fn independent_transactions_identical() {
    let (t, m) = fixture();
    let path = save(&t, &m);
    let a = t.path().join("a");
    let b = t.path().join("b");
    storage::import(&path, &a).unwrap();
    storage::import(&path, &b).unwrap();
    assert_eq!(tree(&a), tree(&b));
}
#[test]
fn update_changes_snapshot_after_restart() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    storage::apply(
        &p,
        &cmd(
            &m,
            "update",
            "node",
            json!({"id":"a","type":"Entity","label":"Changed","props":{"n":7}}),
            1,
        ),
    )
    .unwrap();
    let loaded = storage::load(&p).unwrap();
    assert_eq!(loaded.sequence, 2);
    let x = rt::project(&loaded.pairs, None, true).unwrap();
    assert!(
        x["records"]
            .as_array()
            .unwrap()
            .iter()
            .any(|r| r["source_record"]["label"] == "Changed")
    );
    let q = rt::project(&loaded.pairs, None, false).unwrap();
    assert_eq!(q["semantic_events"], 5);
    assert_eq!(q["latest_snapshots"], 4);
}
#[test]
fn stale_version_no_writes() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    let before = tree(&p);
    let e = storage::apply(
        &p,
        &cmd(&m, "update", "node", json!({"id":"a","type":"Entity"}), 0),
    )
    .unwrap_err();
    assert!(e.to_string().contains("expected version"));
    assert_eq!(before, tree(&p));
}
#[test]
fn create_and_duplicate_create() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    let c = cmd(&m, "create", "node", json!({"id":"new","type":"Entity"}), 0);
    storage::apply(&p, &c).unwrap();
    assert!(
        storage::apply(&p, &c)
            .unwrap_err()
            .to_string()
            .contains("expected version")
    );
}
#[test]
fn retire_relation_then_node() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    storage::apply(
        &p,
        &cmd(
            &m,
            "retire",
            "relation",
            json!({"id":"a","type":"links","source":"a","target":"b"}),
            1,
        ),
    )
    .unwrap();
    storage::apply(
        &p,
        &cmd(&m, "retire", "node", json!({"id":"a","type":"Entity"}), 1),
    )
    .unwrap();
    let s = storage::load(&p).unwrap();
    assert_eq!(s.sequence, 3);
}
#[test]
fn retire_connected_node_rejected() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    let before = tree(&p);
    assert!(
        storage::apply(
            &p,
            &cmd(&m, "retire", "node", json!({"id":"a","type":"Entity"}), 1)
        )
        .is_err()
    );
    assert_eq!(before, tree(&p));
}
#[test]
fn changed_type_rejected() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    assert!(
        storage::apply(
            &p,
            &cmd(&m, "update", "node", json!({"id":"a","type":"Rule"}), 1)
        )
        .unwrap_err()
        .to_string()
        .contains("identity/type")
    );
}
#[test]
fn missing_committed_tail_refused() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    storage::apply(
        &p,
        &cmd(&m, "create", "node", json!({"id":"c","type":"Entity"}), 0),
    )
    .unwrap();
    fs::remove_file(p.join("transaction-00000002.json")).unwrap();
    assert!(storage::load(&p).is_err());
}
#[test]
fn tampered_frame_refused() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    let f = p.join("transaction-00000001.json");
    let mut v: Value = serde_json::from_slice(&fs::read(&f).unwrap()).unwrap();
    v["pairs"][0][0]["event_digest"] = json!("bad");
    write(&f, &v);
    assert!(storage::load(&p).unwrap_err().to_string().contains("chain"));
}
#[test]
fn recovery_removes_only_uncommitted_tail() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    let s = storage::load(&p).unwrap();
    let before = tree(&p);
    fs::write(p.join("PENDING.json"), "partial").unwrap();
    fs::write(p.join("transaction-00000002.json"), "orphan").unwrap();
    assert!(storage::load(&p).is_ok());
    assert!(storage::recover(&p, "wrong").is_err());
    let r = storage::recover(&p, &s.digest).unwrap();
    assert_eq!(r["removed_uncommitted_files"].as_array().unwrap().len(), 2);
    assert_eq!(tree(&p), before);
}
#[test]
fn writer_lock_not_stolen() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    fs::write(p.join("WRITER-LOCK"), "other-writer").unwrap();
    assert!(
        storage::apply(
            &p,
            &cmd(&m, "create", "node", json!({"id":"c","type":"Entity"}), 0)
        )
        .unwrap_err()
        .to_string()
        .contains("lock held")
    );
    assert_eq!(
        fs::read_to_string(p.join("WRITER-LOCK")).unwrap(),
        "other-writer"
    );
}
#[test]
fn cross_package_context_includes_endpoints() {
    let (t, mut m) = fixture();
    let second =
        json!({"ontology_id":"same-name","nodes":[{"id":"c","type":"Entity"}],"relations":[]});
    write(&t.path().join("other.json"), &second);
    let mut p = m.packages[0].clone();
    p.package_key = format!("pkg-{}", rt::sha(b"test:other.json"));
    let sr = rt::Source {
        root: "test".into(),
        path: "other.json".into(),
        sha256: rt::sha(&fs::read(t.path().join("other.json")).unwrap()),
    };
    p.profile = sr.clone();
    p.nodes.source = sr.clone();
    p.relations.source = sr.clone();
    p.documents = vec![sr];
    m.packages[0]
        .endpoint_aliases
        .insert("other".into(), p.package_key.clone());
    m.packages.push(p);
    change(&t, &mut m, |v| {
        v["relations"][0]["target"] = json!("other::c")
    });
    let root = boot(&t, &m);
    let s = storage::load(&root).unwrap();
    let out = rt::project(&s.pairs, Some(&m.packages[0].package_key), false).unwrap();
    assert_eq!(out["context_nodes"], 4); // two own nodes, one own document, foreign endpoint
    assert_eq!(out["context_relations"], 1);
}
#[test]
fn duplicate_tuple_relation_refused() {
    let (t, mut m) = fixture();
    m.packages[0].relations.id_field = "$tuple".into();
    change(&t, &mut m, |v| {
        let r = v["relations"][0].clone();
        v["relations"].as_array_mut().unwrap().push(r)
    });
    assert!(
        rt::plan(&m)
            .unwrap_err()
            .to_string()
            .contains("duplicate subject")
    );
}
#[test]
fn unresolved_alias_refused() {
    let (t, mut m) = fixture();
    change(&t, &mut m, |v| {
        v["relations"][0]["target"] = json!("unknown::a")
    });
    assert!(rt::plan(&m).is_err());
}
#[test]
fn source_drift_no_target() {
    let (t, m) = fixture();
    fs::write(t.path().join("source.json"), "{}").unwrap();
    let p = t.path().join("store");
    assert!(storage::import(&save(&t, &m), &p).is_err());
    assert!(!p.exists());
}
#[test]
fn duplicate_identity_refused() {
    let (t, mut m) = fixture();
    change(&t, &mut m, |v| v["nodes"][1]["id"] = json!("a"));
    assert!(rt::plan(&m).is_err());
}
#[test]
fn unknown_package_query_refused() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    let s = storage::load(&p).unwrap();
    assert!(rt::project(&s.pairs, Some("missing"), false).is_err());
}
#[test]
fn existing_target_preserved() {
    let (t, m) = fixture();
    let p = boot(&t, &m);
    let before = tree(&p);
    assert!(storage::import(&save(&t, &m), &p).is_err());
    assert_eq!(before, tree(&p));
}
#[test]
fn authority_flag_refused() {
    let (_t, mut m) = fixture();
    m.authority_effect = "admit".into();
    assert!(rt::plan(&m).is_err());
}
#[test]
fn large_numbers_lossless() {
    let (t, mut m) = fixture();
    let n: Value = serde_json::from_str("1234567890123456789012345678901234567890").unwrap();
    change(&t, &mut m, |v| v["nodes"][0]["large"] = n.clone());
    let p = boot(&t, &m);
    let s = storage::load(&p).unwrap();
    let out = rt::project(&s.pairs, None, true).unwrap();
    assert!(
        out["records"]
            .as_array()
            .unwrap()
            .iter()
            .any(|r| r["source_record"]["large"] == n)
    );
}
#[test]
fn closed_envelope_validation() {
    let (_t, m) = fixture();
    let mut pairs = rt::plan(&m).unwrap();
    rt::props_mut(&mut pairs[0].0.complete_resulting_semantic_state)
        .values
        .insert("extra".into(), json!(1));
    rt::kernel::seal_semantic_event(&mut pairs[0].0).unwrap();
    assert!(rt::kernel::validate_import_history(&pairs).is_err());
}
#[cfg(unix)]
#[test]
fn symlink_target_refused() {
    let (t, m) = fixture();
    let p = t.path().join("linked");
    std::os::unix::fs::symlink(t.path().join("absent"), &p).unwrap();
    assert!(storage::import(&save(&t, &m), &p).is_err());
}
