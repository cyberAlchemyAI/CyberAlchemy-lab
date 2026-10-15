//! Candidate bridge. Seal typed drafts, append only to explicitly owned stores,
//! and reconstruct through the real inherited EventStore reducer.
use cal_ontology_lifecycle::*;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::{env, fs, process::ExitCode};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Events { semantic: Vec<SemanticEvent>, governance: Vec<GovernanceEvent> }

#[derive(Serialize)]
struct Sealed { semantic: Vec<SemanticEvent>, governance: Vec<GovernanceEvent> }

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let args = env::args().collect::<Vec<_>>();
    if args.len()==3 && args[1]=="seal" {
        let mut events: Events = serde_json::from_slice(&fs::read(&args[2])?)?;
        for event in &mut events.semantic { seal_semantic_event(event)?; }
        for event in &mut events.governance { seal_governance_event(event)?; }
        print!("{}",canonical_json(&Sealed {semantic:events.semantic,governance:events.governance})?);
        return Ok(());
    }
    if args.len()==5 && args[1]=="append" {
        let events: Events = serde_json::from_slice(&fs::read(&args[4])?)?;
        let mut store = EventStore::load(&args[2],&args[3])?;
        let mut versions = std::collections::BTreeMap::<String,u64>::new();
        for event in store.semantic_events() { *versions.entry(event.event.stream_id.clone()).or_insert(0)+=1; }
        let mut semantic = Vec::new();
        for event in events.semantic {
            let version = versions.entry(event.stream_id.clone()).or_insert(0);
            semantic.push(AppendSemanticEventRequest {expected_stream_version:*version,event});*version+=1;
        }
        if !semantic.is_empty() {store.append_semantic_batch(&args[2],semantic)?;}
        let mut versions = std::collections::BTreeMap::<String,u64>::new();
        for event in store.governance_events() { *versions.entry(event.event.stream_id.clone()).or_insert(0)+=1; }
        let mut governance = Vec::new();
        for event in events.governance {
            let version = versions.entry(event.stream_id.clone()).or_insert(0);
            governance.push(AppendGovernanceEventRequest {expected_stream_version:*version,event});*version+=1;
        }
        if !governance.is_empty() {store.append_governance_batch(&args[3],governance)?;}
        println!("{{\"result\":\"PASS\",\"authority_effect\":\"none\"}}");
        return Ok(());
    }
    if args.len()==5 && args[1]=="read" {
        let cursor: u64=args[4].parse()?;
        let store=EventStore::load(&args[2],&args[3])?;
        let cut=store.ontology_at(cursor)?;
        let mut governed=Vec::new();
        for subject in &cut.subjects {
            if subject.identity.subject_kind==SubjectKind::Node {
                governed.push(store.governed_node_view(&subject.identity,cursor,None)?);
            }
        }
        let checkpoint=store.checkpoint_at(cursor)?;
        if store.ontology_from_checkpoint(&checkpoint,cursor)? != cut {return Err("CHECKPOINT_PARITY_FAILED".into());}
        print!("{}",machine_projection(&json!({"result":"PASS","authority_effect":"none","cut":cut,
            "governed_nodes":governed,"semantic_events":store.semantic_events().iter().map(|e| &e.event).collect::<Vec<_>>(),
            "governance_events":store.governance_events().iter().map(|e| &e.event).collect::<Vec<_>>(),
            "checkpoint_parity":"PASS"}))?);
        return Ok(());
    }
    Err("usage: lab-ontology-native seal drafts.json | append semantic-dir governance-dir events.json | read semantic-dir governance-dir cursor".into())
}

fn main() -> ExitCode {
    match run() {Ok(())=>ExitCode::SUCCESS,Err(error)=>{eprintln!("{error}");ExitCode::from(1)}}
}
