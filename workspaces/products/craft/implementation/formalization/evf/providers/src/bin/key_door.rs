use std::env;
use std::fs;
use std::path::PathBuf;

use serde::Deserialize;
use serde_json::json;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Case {
    case_id: String,
    has_key: bool,
    door_locked: bool,
    expected_status: String,
    expected_door_locked: bool,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    schema_version: String,
    runtime_mode: String,
    cases: Vec<Case>,
}

fn input_path() -> Result<PathBuf, String> {
    let args: Vec<String> = env::args().skip(1).collect();
    let index = args
        .iter()
        .position(|value| value == "--input")
        .ok_or("missing --input")?;
    args.get(index + 1)
        .map(PathBuf::from)
        .ok_or("missing --input value".to_owned())
}

fn run() -> Result<serde_json::Value, String> {
    let input: Input =
        serde_json::from_slice(&fs::read(input_path()?).map_err(|error| error.to_string())?)
            .map_err(|error| error.to_string())?;
    if input.schema_version != "evf.key-door-provider-input/v1" || input.cases.is_empty() {
        return Err("invalid key-door provider input".to_owned());
    }
    let mut failed_case_ids = Vec::new();
    for case in input.cases {
        let (status, door_locked) = match input.runtime_mode.as_str() {
            "normal" if case.has_key && case.door_locked => ("unlocked", false),
            "normal" => ("denied", case.door_locked),
            "always_allow" => ("unlocked", false),
            "always_deny" => ("denied", true),
            other => return Err(format!("unsupported runtime mode: {other}")),
        };
        if status != case.expected_status || door_locked != case.expected_door_locked {
            failed_case_ids.push(case.case_id);
        }
    }
    Ok(json!({
        "provider_id": "rust-key-door-runtime",
        "native_outcome": "checked",
        "all_cases_match": failed_case_ids.is_empty(),
        "failed_case_ids": failed_case_ids
    }))
}

fn main() {
    match run() {
        Ok(value) => println!("{}", serde_json::to_string(&value).unwrap()),
        Err(error) => {
            eprintln!("{error}");
            std::process::exit(2);
        }
    }
}
