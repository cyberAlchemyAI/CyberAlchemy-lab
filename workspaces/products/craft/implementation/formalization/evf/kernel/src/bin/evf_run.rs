use std::env;
use std::path::PathBuf;

use evf_production_kernel::{EvfError, run_profile};
use serde_json::json;

fn value(args: &[String], flag: &str) -> Result<PathBuf, EvfError> {
    let index = args
        .iter()
        .position(|item| item == flag)
        .ok_or_else(|| EvfError::message("ARGUMENT_MISSING", flag))?;
    args.get(index + 1)
        .map(PathBuf::from)
        .ok_or_else(|| EvfError::message("ARGUMENT_VALUE_MISSING", flag))
}

fn text(args: &[String], flag: &str) -> Result<String, EvfError> {
    Ok(value(args, flag)?.to_string_lossy().into_owned())
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    let result = (|| {
        let root = value(&args, "--repo-root")?;
        let profile = value(&args, "--profile")?;
        let store = value(&args, "--store")?;
        let attempt_id = text(&args, "--attempt-id")?;
        run_profile(&root, &profile, &store, &attempt_id)
    })();
    match result {
        Ok(result) => {
            println!(
                "{}",
                serde_json::to_string(&json!({
                    "status": result.aggregate.aggregate_state,
                    "profile_id": result.aggregate.profile_id,
                    "evidence_payload_digest": result.aggregate.evidence_payload_digest,
                    "run_path": result.run_path,
                    "authority_effect": "none"
                }))
                .unwrap()
            );
        }
        Err(error) => {
            eprintln!(
                "{}",
                serde_json::to_string(&json!({
                    "status": "blocked",
                    "reason_code": error.code,
                    "message": error.message,
                    "authority_effect": "none"
                }))
                .unwrap()
            );
            std::process::exit(2);
        }
    }
}
