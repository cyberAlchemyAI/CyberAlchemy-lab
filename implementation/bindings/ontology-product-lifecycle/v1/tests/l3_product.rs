use cal_ontology_product::OntologySource;
use cal_ontology_product_lifecycle_binding::{
    CONTEXT_MAP_REF, GOVERNANCE_CONTEXT_REF, LifecycleRuntimeBinding,
    ONTOLOGY_LIFECYCLE_CONTEXT_REF, ProductChangeBody, ProductEvolutionRuntime, ProductLifecycle,
    ReferenceEvolutionRuntime, changes_from_source, push_change,
};
use tempfile::tempdir;

const SOURCE: &[u8] =
    include_bytes!("../../../../../product/products/ontology/v1/fixtures/valid/source.json");

fn changes() -> Vec<cal_ontology_product_lifecycle_binding::ProductChange> {
    let source: OntologySource = serde_json::from_slice(SOURCE).expect("source");
    let mut changes = changes_from_source(&source).expect("seed changes");
    let mut evolved = source.nodes[0].clone();
    evolved.label = format!("{} evolved", evolved.label);
    push_change(
        &mut changes,
        ProductChangeBody::Node {
            node: evolved,
            lifecycle: ProductLifecycle::Active,
        },
    )
    .expect("evolution change");
    changes
}

#[test]
fn evolution_changes_the_observation_without_authority_effect() {
    let changes = changes();
    let initial_cursor = (changes.len() - 1) as u64;
    let reference = ReferenceEvolutionRuntime;
    let initial = reference.replay(&changes, initial_cursor).expect("initial");
    let evolved = reference
        .replay(&changes, changes.len() as u64)
        .expect("evolved");
    assert_ne!(initial.observation_digest, evolved.observation_digest);
    assert_eq!(evolved.authority_effect, "none");
    assert!(
        evolved
            .nodes
            .iter()
            .any(|node| node.label.ends_with(" evolved"))
    );
}

#[test]
fn replay_and_checkpoint_recovery_are_byte_equivalent() {
    let changes = changes();
    let target = changes.len() as u64;
    let checkpoint = target - 1;
    let replay_root = tempdir().expect("replay temp").path().join("runtime");
    let recovery_root = tempdir().expect("recovery temp").path().join("runtime");
    let replay = LifecycleRuntimeBinding::new(replay_root)
        .replay(&changes, target)
        .expect("full replay");
    let recovered = LifecycleRuntimeBinding::new(recovery_root)
        .recover(&changes, checkpoint, target)
        .expect("checkpoint recovery");
    assert_eq!(
        serde_json::to_vec(&replay).unwrap(),
        serde_json::to_vec(&recovered).unwrap()
    );
}

#[test]
fn existing_runtime_is_replaceable_behind_the_product_port() {
    let changes = changes();
    let target = changes.len() as u64;
    let native_root = tempdir().expect("native temp").path().join("runtime");
    let native = LifecycleRuntimeBinding::new(native_root)
        .replay(&changes, target)
        .expect("native runtime");
    let reference = ReferenceEvolutionRuntime
        .replay(&changes, target)
        .expect("reference runtime");
    assert_eq!(native, reference);
}

#[test]
fn context_observation_preserves_exact_endpoint_and_authority_boundaries() {
    let changes = changes();
    let target = changes.len() as u64;
    let root = tempdir().expect("context temp").path().join("runtime");
    let observation = LifecycleRuntimeBinding::new(root)
        .context_observation(&changes, target)
        .expect("context observation");
    assert_eq!(observation.governance_context_ref, GOVERNANCE_CONTEXT_REF);
    assert_eq!(
        observation.ontology_lifecycle_context_ref,
        ONTOLOGY_LIFECYCLE_CONTEXT_REF
    );
    assert_eq!(observation.context_map_ref, CONTEXT_MAP_REF);
    assert_eq!(observation.authority_effect, "none");
    assert!(!observation.canonical_replay_source);
    assert!(!observation.selected_node_ids.is_empty());
}

#[test]
fn malformed_change_chain_fails_closed_in_both_runtimes() {
    let mut changes = changes();
    changes[1].previous_change_digest = Some("0".repeat(64));
    let target = changes.len() as u64;
    let reference_error = ReferenceEvolutionRuntime
        .replay(&changes, target)
        .expect_err("reference must reject");
    let root = tempdir().expect("invalid temp").path().join("runtime");
    let native_error = LifecycleRuntimeBinding::new(root)
        .replay(&changes, target)
        .expect_err("native must reject");
    assert_eq!(reference_error.code, "CHANGE_CHAIN_BROKEN");
    assert_eq!(native_error.code, "CHANGE_CHAIN_BROKEN");
}
