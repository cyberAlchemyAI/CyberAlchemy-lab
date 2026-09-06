use cal_ontology_product::{
    build_package, canonical_json, get_node, human_projection, list_nodes, load_package,
};
use serde_json::json;
use std::env;
use std::fs;
use std::process::ExitCode;

fn usage() {
    eprintln!("usage:");
    eprintln!("  cal-ontology-product build <source.json> <ontology-package.json>");
    eprintln!("  cal-ontology-product validate <ontology-package.json>");
    eprintln!("  cal-ontology-product list <ontology-package.json>");
    eprintln!("  cal-ontology-product get <ontology-package.json> <node-id>");
    eprintln!("  cal-ontology-product project <ontology-package.json>");
}

fn run(arguments: &[String]) -> Result<(), Box<dyn std::error::Error>> {
    match arguments {
        [command, source, output] if command == "build" => {
            let source_bytes = fs::read(source)?;
            let package = build_package(&source_bytes)?;
            fs::write(output, canonical_json(&package)?)?;
            println!("{}", package.package_id);
        }
        [command, package_path] if command == "validate" => {
            let package = load_package(package_path)?;
            println!(
                "{}",
                serde_json::to_string(&json!({
                    "status": "PASS",
                    "package_id": package.package_id,
                    "nodes": package.nodes.len(),
                    "relations": package.relations.len(),
                    "authority_effect": package.authority_effect
                }))?
            );
        }
        [command, package_path] if command == "list" => {
            let package = load_package(package_path)?;
            let rows = list_nodes(&package)
                .into_iter()
                .map(|node| {
                    json!({
                        "node_id": node.node_id,
                        "type_ref": node.type_ref,
                        "label": node.label
                    })
                })
                .collect::<Vec<_>>();
            println!("{}", serde_json::to_string_pretty(&rows)?);
        }
        [command, package_path, node_id] if command == "get" => {
            let package = load_package(package_path)?;
            println!(
                "{}",
                String::from_utf8(canonical_json(get_node(&package, node_id)?)?)?
            );
        }
        [command, package_path] if command == "project" => {
            let package = load_package(package_path)?;
            print!("{}", human_projection(&package));
        }
        _ => {
            usage();
            return Err("CLI_ARGUMENTS_INVALID".into());
        }
    }
    Ok(())
}

fn main() -> ExitCode {
    let arguments = env::args().skip(1).collect::<Vec<_>>();
    match run(&arguments) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("{error}");
            ExitCode::from(1)
        }
    }
}
