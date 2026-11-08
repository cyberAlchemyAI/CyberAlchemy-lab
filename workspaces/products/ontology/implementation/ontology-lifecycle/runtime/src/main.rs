use cal_ontology_lifecycle::{EventStore, machine_projection};
use std::env;
use std::process::ExitCode;

fn main() -> ExitCode {
    let arguments = env::args().collect::<Vec<_>>();
    if arguments.len() != 4 {
        eprintln!(
            "usage: ontology-at-cursor <semantic-event-directory> <governance-event-directory> <semantic-cursor>"
        );
        return ExitCode::from(2);
    }
    let cursor = match arguments[3].parse::<u64>() {
        Ok(cursor) => cursor,
        Err(error) => {
            eprintln!("CURSOR_INVALID: {error}");
            return ExitCode::from(2);
        }
    };
    let result = EventStore::load(&arguments[1], &arguments[2])
        .and_then(|store| store.ontology_at(cursor))
        .and_then(|cut| machine_projection(&cut));
    match result {
        Ok(projection) => {
            print!("{projection}");
            ExitCode::SUCCESS
        }
        Err(error) => {
            eprintln!("{error}");
            ExitCode::from(1)
        }
    }
}
