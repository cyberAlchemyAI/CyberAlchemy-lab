use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

use serde::Deserialize;
use serde_json::json;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    schema_version: String,
    source: String,
    target: String,
    nodes: Vec<String>,
    edges: Vec<[String; 2]>,
}

fn arg(flag: &str) -> Result<PathBuf, String> {
    let args: Vec<String> = env::args().skip(1).collect();
    let index = args
        .iter()
        .position(|value| value == flag)
        .ok_or_else(|| format!("missing {flag}"))?;
    args.get(index + 1)
        .map(PathBuf::from)
        .ok_or_else(|| format!("missing value for {flag}"))
}

fn run_souffle(souffle: &Path, program: &Path, input: &Input, root: &Path) -> Result<bool, String> {
    let facts = root.join("facts");
    let output = root.join("output");
    fs::create_dir_all(&facts).map_err(|error| error.to_string())?;
    fs::create_dir_all(&output).map_err(|error| error.to_string())?;
    let mut edge_bytes = String::new();
    for [source, target] in &input.edges {
        edge_bytes.push_str(source);
        edge_bytes.push('\t');
        edge_bytes.push_str(target);
        edge_bytes.push('\n');
    }
    fs::write(facts.join("Edge.facts"), edge_bytes).map_err(|error| error.to_string())?;
    let result = Command::new(souffle)
        .arg("--no-preprocessor")
        .arg("-j")
        .arg("1")
        .arg("-F")
        .arg(&facts)
        .arg("-D")
        .arg(&output)
        .arg(program)
        .output()
        .map_err(|error| error.to_string())?;
    if !result.status.success() {
        return Err(format!(
            "Souffle failed: {}",
            String::from_utf8_lossy(&result.stderr).trim()
        ));
    }
    let rows = fs::read_to_string(output.join("Reach.csv")).map_err(|error| error.to_string())?;
    Ok(rows.lines().any(|line| {
        let mut fields = line.split('\t');
        fields.next() == Some(input.source.as_str()) && fields.next() == Some(input.target.as_str())
    }))
}

fn run() -> Result<serde_json::Value, String> {
    let input: Input =
        serde_json::from_slice(&fs::read(arg("--input")?).map_err(|error| error.to_string())?)
            .map_err(|error| error.to_string())?;
    if input.schema_version != "evf.reachability-facts/v1" || input.nodes.is_empty() {
        return Err("invalid reachability facts".to_owned());
    }
    let souffle = arg("--souffle")?;
    let program = arg("--program")?;
    let temporary = tempfile::Builder::new()
        .prefix("evf-souffle-")
        .tempdir()
        .map_err(|error| error.to_string())?;
    let reachable = run_souffle(&souffle, &program, &input, temporary.path())?;
    Ok(json!({
        "provider_id": "souffle-2.5-reachability",
        "native_outcome": "checked",
        "reachable": reachable
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
