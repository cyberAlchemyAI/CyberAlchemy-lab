//! Read-only bridge to the actual ontology lifecycle reducer. No store writes.
use cal_ontology_lifecycle::*;
use serde::{Deserialize, Serialize};
use std::{env, fs, process::ExitCode};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    selector_ref: String,
    selector: ContextSelector,
    governance_cursor: u64,
}

#[derive(Serialize)]
struct Output {
    schema_version: &'static str,
    authority_effect: AuthorityEffect,
    cut: ConsistentOntologyCut,
    context: ContextProjection,
    governance_cursor: u64,
    governance_event_refs: Vec<String>,
    governed_nodes: Vec<GovernedOntologyNodeView>,
}

// A pure serialization helper used by isolated tests: no directories are written.
#[derive(Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct FixtureEvents {
    semantic: Vec<SemanticEvent>,
    governance: Vec<GovernanceEvent>,
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let args = env::args().collect::<Vec<_>>();
    if args.len() == 3 && args[1] == "seal-fixture" {
        let mut events: FixtureEvents = serde_json::from_slice(&fs::read(&args[2])?)?;
        for event in &mut events.semantic { seal_semantic_event(event)?; }
        // Exact references are supplied by the fixture author after semantic sealing.
        for event in &mut events.governance { seal_governance_event(event)?; }
        print!("{}", canonical_json(&events)?);
        return Ok(());
    }
    if args.len() != 4 {
        return Err("usage: lab-context-native-reader semantic-dir governance-dir request.json".into());
    }
    let request: Request = serde_json::from_slice(&fs::read(&args[3])?)?;
    let store = EventStore::load(&args[1], &args[2])?;
    let actual_cursor = store.governance_events().last().map(|e| e.event.governance_cursor).unwrap_or(0);
    if actual_cursor != request.governance_cursor || actual_cursor == 0 {
        return Err("GOVERNANCE_PREFIX_PIN_MISMATCH".into());
    }
    let cut = store.ontology_at(request.selector.semantic_cursor)?;
    let context = store.context_projection(&request.selector_ref, &request.selector)?;
    let mut nodes = Vec::new();
    for identity in &request.selector.required_subject_set {
        if identity.subject_kind == SubjectKind::Node {
            nodes.push(store.governed_node_view(identity, request.selector.semantic_cursor, Some(request.selector_ref.clone()))?);
        }
    }
    let output = Output {
        schema_version: "lab-native-context-read/v1-candidate",
        authority_effect: AuthorityEffect::None,
        cut, context, governance_cursor: actual_cursor,
        governance_event_refs: store.governance_events().iter().map(|e| e.event.event_id.clone()).collect(),
        governed_nodes: nodes,
    };
    print!("{}", machine_projection(&output)?);
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => { eprintln!("{error}"); ExitCode::from(1) }
    }
}
