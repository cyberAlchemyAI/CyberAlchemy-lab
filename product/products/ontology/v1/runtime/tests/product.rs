use cal_ontology_product::{
    build_package, canonical_json, get_node, human_projection, list_nodes, validate_package,
};
use std::fs;
use std::process::Command;
use tempfile::tempdir;

const VALID_SOURCE: &[u8] = include_bytes!("../../fixtures/valid/source.json");

#[test]
fn equal_source_bytes_build_equal_package_bytes() {
    let first = canonical_json(&build_package(VALID_SOURCE).expect("first build")).expect("json");
    let second = canonical_json(&build_package(VALID_SOURCE).expect("second build")).expect("json");
    assert_eq!(first, second);
}

#[test]
fn valid_package_closes_product_output_and_query_contract() {
    let package = build_package(VALID_SOURCE).expect("package");
    validate_package(&package).expect("valid package");
    assert_eq!(package.product_ref, "CA2-PRODUCT-ONTOLOGY/v1");
    assert_eq!(package.product_output_ref, "CA2-OUTPUT-ONTOLOGY-PACKAGE");
    assert_eq!(package.authority_effect, "none");
    assert_eq!(package.query_contract.allowed_operations, ["list", "get"]);
}

#[test]
fn list_and_get_are_bounded_to_declared_nodes() {
    let package = build_package(VALID_SOURCE).expect("package");
    assert_eq!(list_nodes(&package).len(), 3);
    assert_eq!(
        get_node(&package, "demo.output").expect("known node").label,
        "Governed Ontology Package"
    );
    assert_eq!(
        get_node(&package, "unknown")
            .expect_err("unknown must fail")
            .code,
        "NODE_NOT_FOUND"
    );
}

#[test]
fn projection_is_deterministic_and_non_authoritative() {
    let package = build_package(VALID_SOURCE).expect("package");
    let first = human_projection(&package);
    let second = human_projection(&package);
    assert_eq!(first, second);
    assert!(first.contains("Authority effect: `none`"));
    assert!(first.contains("Unknown identity: `fail-closed`"));
}

#[test]
fn duplicate_node_is_rejected() {
    let bytes = include_bytes!("../../fixtures/invalid/duplicate-node.json");
    assert_eq!(
        build_package(bytes)
            .expect_err("duplicate node must fail")
            .code,
        "NODE_ID_DUPLICATE"
    );
}

#[test]
fn dangling_relation_is_rejected() {
    let bytes = include_bytes!("../../fixtures/invalid/dangling-relation.json");
    assert_eq!(
        build_package(bytes)
            .expect_err("dangling relation must fail")
            .code,
        "RELATION_TARGET_MISSING"
    );
}

#[test]
fn authority_inflation_is_rejected() {
    let bytes = include_bytes!("../../fixtures/invalid/authority-effect.json");
    assert_eq!(
        build_package(bytes)
            .expect_err("authority effect must fail")
            .code,
        "AUTHORITY_EFFECT_FORBIDDEN"
    );
}

#[test]
fn cli_build_validate_list_get_and_project() {
    let temporary = tempdir().expect("temporary directory");
    let source = temporary.path().join("source.json");
    let package = temporary.path().join("ontology-package.json");
    fs::write(&source, VALID_SOURCE).expect("write source");
    let binary = env!("CARGO_BIN_EXE_cal-ontology-product");
    for arguments in [
        vec!["build", source.to_str().unwrap(), package.to_str().unwrap()],
        vec!["validate", package.to_str().unwrap()],
        vec!["list", package.to_str().unwrap()],
        vec!["get", package.to_str().unwrap(), "demo.output"],
        vec!["project", package.to_str().unwrap()],
    ] {
        let output = Command::new(binary)
            .args(&arguments)
            .output()
            .expect("run CLI");
        assert!(
            output.status.success(),
            "{:?}: {}",
            arguments,
            String::from_utf8_lossy(&output.stderr)
        );
    }
}
