use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::json;

fn text(flag: &str) -> Result<String, String> {
    let args: Vec<String> = env::args().skip(1).collect();
    let index = args
        .iter()
        .position(|value| value == flag)
        .ok_or_else(|| format!("missing {flag}"))?;
    args.get(index + 1)
        .cloned()
        .ok_or_else(|| format!("missing value for {flag}"))
}

fn path(flag: &str) -> Result<PathBuf, String> {
    Ok(PathBuf::from(text(flag)?))
}

fn invoke_lean(lean: &Path, directory: &Path, file_name: &Path) -> Result<(bool, String), String> {
    let output = Command::new(lean)
        .arg("-o")
        .arg(file_name.with_extension("olean"))
        .arg(file_name)
        .current_dir(directory)
        .env_clear()
        .env("LEAN_PATH", directory)
        .output()
        .map_err(|error| error.to_string())?;
    let diagnostics = [output.stdout.as_slice(), output.stderr.as_slice()].concat();
    Ok((
        output.status.success(),
        String::from_utf8_lossy(&diagnostics).trim().to_owned(),
    ))
}

fn run_lean(lean: &Path, input: &Path, dependency: &Path) -> Result<(bool, String), String> {
    let temporary = tempfile::Builder::new()
        .prefix("evf-lean-")
        .tempdir()
        .map_err(|error| error.to_string())?;
    let dependency_name = dependency
        .file_name()
        .ok_or("Lean dependency has no file name")?;
    let input_name = input.file_name().ok_or("Lean input has no file name")?;
    fs::copy(dependency, temporary.path().join(dependency_name))
        .map_err(|error| error.to_string())?;
    fs::copy(input, temporary.path().join(input_name)).map_err(|error| error.to_string())?;
    let (dependency_checked, dependency_diagnostics) =
        invoke_lean(lean, temporary.path(), Path::new(dependency_name))?;
    if !dependency_checked {
        return Err(format!(
            "Lean dependency failed to compile: {dependency_diagnostics}"
        ));
    }
    invoke_lean(lean, temporary.path(), Path::new(input_name))
}

fn run() -> Result<serde_json::Value, String> {
    let input = path("--input")?;
    let lean = path("--lean")?;
    let dependency = path("--dependency")?;
    let expected = text("--expected")?;
    let source = fs::read_to_string(&input).map_err(|error| error.to_string())?;
    if source.contains("sorry") || source.contains("axiom ") || source.contains("unsafe ") {
        return Err("forbidden Lean construct present".to_owned());
    }
    let declaration = expected.rsplit('.').next().unwrap_or(&expected);
    let expected_declaration_present = source.lines().any(|line| {
        let line = line.trim_start();
        (line.starts_with("theorem ") || line.starts_with("lemma "))
            && line
                .split_whitespace()
                .nth(1)
                .is_some_and(|name| name.trim_end_matches(':') == declaration)
    });
    let (checked, diagnostics) = run_lean(&lean, &input, &dependency)?;
    if !checked && !diagnostics.is_empty() {
        eprintln!("{diagnostics}");
    }
    Ok(json!({
        "provider_id": "lean4-core-typechecker",
        "native_outcome": if checked { "checked" } else { "rejected" },
        "expected_declaration_present": expected_declaration_present
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
