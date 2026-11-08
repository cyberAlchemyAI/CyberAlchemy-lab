use std::collections::{BTreeSet, VecDeque};
use std::env;
use std::fs;
use std::path::PathBuf;

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
    if input.schema_version != "evf.reachability-facts/v1" {
        return Err("invalid reachability facts version".to_owned());
    }
    let nodes: BTreeSet<_> = input.nodes.iter().cloned().collect();
    if nodes.len() != input.nodes.len()
        || !nodes.contains(&input.source)
        || !nodes.contains(&input.target)
    {
        return Err("invalid reachability node universe".to_owned());
    }
    let mut frontier = VecDeque::from([input.source.clone()]);
    let mut visited = BTreeSet::from([input.source.clone()]);
    while let Some(node) = frontier.pop_front() {
        for [source, target] in &input.edges {
            if source == &node && visited.insert(target.clone()) {
                frontier.push_back(target.clone());
            }
        }
    }
    Ok(json!({
        "provider_id": "rust-bfs-reachability",
        "native_outcome": "checked",
        "reachable": visited.contains(&input.target)
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
