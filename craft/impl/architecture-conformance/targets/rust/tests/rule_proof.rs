use domainspec_architecture_conformance_rust::{
    build_proof, inspect_source, mutate_source, repository_root_from_manifest,
};

#[test]
fn full_native_proof_is_complete() {
    let proof = build_proof(&repository_root_from_manifest()).expect("proof must pass");
    assert_eq!(proof["summary"]["accounting"]["positive"]["passed"], 3);
    assert_eq!(proof["summary"]["accounting"]["mutations"]["killed"], 3);
    assert_eq!(proof["runtime"]["isolated_workspace"], true);
}

#[test]
fn macros_build_generation_and_use_forms_fail_closed() {
    for hostile in [
        "include!(\"generated.rs\");",
        "macro_rules! rule { () => { true } }",
        "#[path = \"generated.rs\"] mod generated;",
        "use crate::generated::can_settle_payout;",
    ] {
        let error = inspect_source(hostile).expect_err("hostile source must block");
        assert_eq!(error.0, "RUST_RULE_MACRO_OR_GENERATION_UNSUPPORTED");
    }
}

#[test]
fn mutator_rejects_unsupported_base() {
    let error = mutate_source("pub fn can_settle_payout() -> bool { true }", "wrong-result")
        .expect_err("unsupported base must block");
    assert_eq!(error.0, "RUST_RULE_ITEM_SUBSET_UNSUPPORTED");
}
