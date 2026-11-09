use cal_ontology_product_event_runtime_binding::{load_realized_runtime, realize_navigation};
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process::ExitCode;

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("{error}");
            ExitCode::FAILURE
        }
    }
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let arguments = env::args().skip(1).collect::<Vec<_>>();
    match arguments.as_slice() {
        [command, navigation_path, runtime_path] if command == "materialize" => {
            let navigation = fs::read(navigation_path)?;
            let runtime = realize_navigation(&navigation, PathBuf::from(runtime_path))?;
            println!("{}", serde_json::to_string_pretty(&runtime.observation()?)?);
            Ok(())
        }
        [command, runtime_path] if command == "observe" => {
            let runtime = load_realized_runtime(PathBuf::from(runtime_path))?;
            println!("{}", serde_json::to_string_pretty(&runtime.observation()?)?);
            Ok(())
        }
        _ => Err(
            "usage: cal-ontology-product-event-runtime-binding materialize <navigation.json> <empty-runtime-dir> | observe <runtime-dir>"
                .into(),
        ),
    }
}
