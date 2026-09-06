use cal_ontology_source_runtime::{self as rt, Result};
use std::path::Path;
fn run() -> Result<()> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    let v=match args.iter().map(String::as_str).collect::<Vec<_>>().as_slice(){
 ["plan",m]=>{let m:rt::Manifest=serde_json::from_slice(&std::fs::read(m)?)?;let p=rt::plan(&m)?;
 serde_json::json!({"result":"PASS","packages":m.packages.len(),"event_subjects":p.len(),"authority_effect":"none"})},
 ["import",m,t]=>rt::storage::import(Path::new(m),Path::new(t))?,
 ["apply",t,c]=>rt::storage::apply(Path::new(t),&serde_json::from_slice::<rt::Command>(&std::fs::read(c)?)?)?,
 ["recover",t,h]=>rt::storage::recover(Path::new(t),h)?,
 [op,t] if ["observe","summary","export"].contains(op)=>{
 let s=rt::storage::load(Path::new(t))?;let mut v=rt::project(&s.pairs,None,*op=="export")?;
 if *op=="summary"{v.as_object_mut().unwrap().remove("context");}
 v["head"]=serde_json::json!(s.digest);v},
 [op,t,p] if ["observe","summary","export"].contains(op)=>{
 let s=rt::storage::load(Path::new(t))?;let mut v=rt::project(&s.pairs,Some(p),*op=="export")?;
 if *op=="summary"{v.as_object_mut().unwrap().remove("context");}v["head"]=serde_json::json!(s.digest);v},
 _=>return Err("usage: plan <manifest> | import <manifest> <new-dir> | summary|observe|export <dir> [package] | apply <dir> <command.json> | recover <dir> <expected-head>".into())
 };
    println!("{}", serde_json::to_string_pretty(&v)?);
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
