use cal_ontology_active_runtime::{ActiveRuntime, ActiveRuntimeFailure};
use serde::Serialize;
use serde_json::json;
use std::io::{self, BufRead};
use std::process::ExitCode;

#[derive(Serialize)]
struct Output<T: Serialize> {
    kind: &'static str,
    body: T,
}

fn emit<T: Serialize>(kind: &'static str, body: T) -> Result<(), ActiveRuntimeFailure> {
    let line =
        serde_json::to_string(&Output { kind, body }).map_err(|error| ActiveRuntimeFailure {
            code: "ACTIVE_RUNTIME_OUTPUT_ENCODE_FAILED".to_owned(),
            detail: error.to_string(),
        })?;
    println!("{line}");
    Ok(())
}

fn run() -> Result<(), ActiveRuntimeFailure> {
    let arguments = std::env::args().skip(1).collect::<Vec<_>>();
    if !arguments.is_empty() {
        return Err(ActiveRuntimeFailure {
            code: "ACTIVE_RUNTIME_ARGUMENTS_FORBIDDEN".to_owned(),
            detail: "run without arguments; commands are status, projection, help, stop".to_owned(),
        });
    }

    let runtime = ActiveRuntime::start_canonical()?;
    emit("ready", runtime.status()?)?;
    let mut runtime = Some(runtime);
    for line in io::stdin().lock().lines() {
        let command = line.map_err(|error| ActiveRuntimeFailure {
            code: "ACTIVE_RUNTIME_INPUT_FAILED".to_owned(),
            detail: error.to_string(),
        })?;
        match command.trim() {
            "" => {}
            "status" => emit(
                "status",
                runtime.as_ref().expect("runtime present").status()?,
            )?,
            "projection" => emit(
                "projection",
                runtime.as_ref().expect("runtime present").projection(),
            )?,
            "help" => emit(
                "help",
                json!({"commands": ["status", "projection", "help", "stop"]}),
            )?,
            "stop" => {
                let receipt = runtime.take().expect("runtime present").stop()?;
                emit("stopped", receipt)?;
                return Ok(());
            }
            other => emit(
                "error",
                json!({"code": "ACTIVE_RUNTIME_COMMAND_UNKNOWN", "command": other}),
            )?,
        }
    }
    let receipt = runtime.take().expect("runtime present").stop()?;
    emit("stopped", receipt)?;
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(failure) => {
            eprintln!(
                "{}",
                serde_json::to_string(&failure).unwrap_or_else(|_| failure.to_string())
            );
            ExitCode::from(1)
        }
    }
}
