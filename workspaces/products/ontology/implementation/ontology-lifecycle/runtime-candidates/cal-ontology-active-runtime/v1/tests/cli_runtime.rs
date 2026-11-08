use serde_json::Value;
use std::io::Write;
use std::process::{Command, Stdio};

#[test]
fn cli_remains_active_for_commands_and_stops_cleanly() {
    let mut child = Command::new(env!("CARGO_BIN_EXE_cal-ontology-active-runtime"))
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .as_mut()
        .unwrap()
        .write_all(b"status\nprojection\nstop\n")
        .unwrap();
    let output = child.wait_with_output().unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    let lines = String::from_utf8(output.stdout).unwrap();
    let values = lines
        .lines()
        .map(|line| serde_json::from_str::<Value>(line).unwrap())
        .collect::<Vec<_>>();
    assert_eq!(values.len(), 4);
    assert_eq!(values[0]["kind"], "ready");
    assert_eq!(values[1]["kind"], "status");
    assert_eq!(values[2]["kind"], "projection");
    assert_eq!(values[3]["kind"], "stopped");
    assert_eq!(values[0]["body"], values[1]["body"]);
    assert_eq!(values[2]["body"]["semantic_cursor"], 47);
    assert_eq!(values[2]["body"]["source_event_count"], 47);
    assert_eq!(values[3]["body"]["cleanup_verified"], true);
}

#[test]
fn eof_stops_and_cleans_the_runtime() {
    let output = Command::new(env!("CARGO_BIN_EXE_cal-ontology-active-runtime"))
        .stdin(Stdio::null())
        .output()
        .unwrap();
    assert!(output.status.success());
    let lines = String::from_utf8(output.stdout).unwrap();
    let values = lines
        .lines()
        .map(|line| serde_json::from_str::<Value>(line).unwrap())
        .collect::<Vec<_>>();
    assert_eq!(values.len(), 2);
    assert_eq!(values[0]["kind"], "ready");
    assert_eq!(values[1]["kind"], "stopped");
    assert_eq!(values[1]["body"]["cleanup_verified"], true);
}

#[test]
fn arguments_are_rejected_before_runtime_start() {
    let output = Command::new(env!("CARGO_BIN_EXE_cal-ontology-active-runtime"))
        .arg("--live")
        .output()
        .unwrap();
    assert!(!output.status.success());
    let failure: Value = serde_json::from_slice(&output.stderr).unwrap();
    assert_eq!(failure["code"], "ACTIVE_RUNTIME_ARGUMENTS_FORBIDDEN");
    assert!(output.stdout.is_empty());
}
