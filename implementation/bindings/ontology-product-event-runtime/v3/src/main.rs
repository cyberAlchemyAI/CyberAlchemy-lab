use cal_ontology_source_importer::{self as importer, Result};
use std::path::Path;
fn run() -> Result<()> {
    let a: Vec<_> = std::env::args().skip(1).collect();
    let value=match a.iter().map(String::as_str).collect::<Vec<_>>().as_slice() {
        ["import",manifest,target]=>importer::import(Path::new(manifest),Path::new(target))?,
        ["observe",target]=>importer::observe(Path::new(target),None)?,
        ["observe",target,package]=>importer::observe(Path::new(target),Some(package))?,
        ["export",target]=>importer::export(Path::new(target),None)?,
        ["export",target,package]=>importer::export(Path::new(target),Some(package))?,
        ["plan",manifest]=>{
            let m:importer::Manifest=serde_json::from_slice(&std::fs::read(manifest)?)?;
            let p=importer::plan(&m)?;
            serde_json::json!({"result":"PASS","subjects":p.len(),"packages":m.packages.len(),
                "unsupported":m.unsupported,"authority_effect":"none"})
        },
        _=>return Err("usage: plan <manifest> | import <manifest> <new-directory> | observe|export <directory> [package-key]".into())
    };
    println!("{}", serde_json::to_string_pretty(&value)?);
    Ok(())
}
fn main() -> std::process::ExitCode {
    match run() {
        Ok(()) => std::process::ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("{e}");
            std::process::ExitCode::FAILURE
        }
    }
}
