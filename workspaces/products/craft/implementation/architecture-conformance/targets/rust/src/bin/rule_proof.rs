use domainspec_architecture_conformance_rust::{build_proof, repository_root_from_manifest};
use std::fs;
use std::path::PathBuf;

fn main() {
    let mut arguments = std::env::args().skip(1);
    let mut output: Option<PathBuf> = None;
    let mut repository_root: Option<PathBuf> = None;
    while let Some(argument) = arguments.next() {
        match (argument.as_str(), arguments.next()) {
            ("--output", Some(path)) => output = Some(PathBuf::from(path)),
            ("--repository-root", Some(path)) => repository_root = Some(PathBuf::from(path)),
            _ => panic!("RUST_RULE_ARGUMENTS_INVALID"),
        }
    }
    let root = repository_root.unwrap_or_else(repository_root_from_manifest);
    let proof = build_proof(&root).expect("RUST_RULE_PROOF_FAILED");
    let rendered = format!("{}\n", serde_json::to_string_pretty(&proof).expect("RUST_RULE_JSON_INVALID"));
    if let Some(path) = output.as_ref() {
        fs::create_dir_all(path.parent().expect("RUST_RULE_OUTPUT_PARENT_INVALID")).expect("RUST_RULE_OUTPUT_FAILED");
        fs::write(path, rendered).expect("RUST_RULE_OUTPUT_FAILED");
    }
    println!("{}", serde_json::json!({
        "status": "pass",
        "summary_sha256": proof["summary_sha256"],
        "output": output,
        "authority_effect": "none",
    }));
}
