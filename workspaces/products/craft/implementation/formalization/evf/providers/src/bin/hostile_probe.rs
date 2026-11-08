use std::env;
use std::fs;
use std::net::{SocketAddr, TcpStream};
use std::path::PathBuf;
use std::thread;
use std::time::Duration;

use serde::Deserialize;
use serde_json::json;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    schema_version: String,
    mode: String,
}

fn input_path() -> Result<PathBuf, String> {
    let args: Vec<String> = env::args().skip(1).collect();
    let index = args
        .iter()
        .position(|value| value == "--input")
        .ok_or("missing --input")?;
    args.get(index + 1)
        .map(PathBuf::from)
        .ok_or("missing --input value".to_owned())
}

fn input() -> Result<Input, String> {
    let input: Input =
        serde_json::from_slice(&fs::read(input_path()?).map_err(|error| error.to_string())?)
            .map_err(|error| error.to_string())?;
    if input.schema_version != "evf.hostile-probe-input/v1" {
        return Err("invalid hostile probe input".to_owned());
    }
    Ok(input)
}

fn bounded_result(probe: &str) -> serde_json::Value {
    let address = SocketAddr::from(([1, 1, 1, 1], 53));
    let network_escape = TcpStream::connect_timeout(&address, Duration::from_millis(100)).is_ok();
    json!({
        "provider_id": "rust-hostile-probe",
        "native_outcome": "checked",
        "probe": probe,
        "ambient_secret_present": env::var_os("EVF_FORBIDDEN_SECRET").is_some(),
        "network_escape": network_escape
    })
}

fn main() {
    let input = match input() {
        Ok(input) => input,
        Err(error) => {
            eprintln!("{error}");
            std::process::exit(2);
        }
    };
    match input.mode.as_str() {
        "pass" => println!(
            "{}",
            serde_json::to_string(&bounded_result("pass")).unwrap()
        ),
        "mutation" => println!(
            "{}",
            serde_json::to_string(&bounded_result("mutation-killed")).unwrap()
        ),
        "timeout" => {
            thread::sleep(Duration::from_secs(5));
            println!(
                "{}",
                serde_json::to_string(&bounded_result("late")).unwrap()
            );
        }
        "oversized" => println!("{}", "x".repeat(4096)),
        "malformed" => println!("not-json"),
        "nonzero" => {
            eprintln!("declared hostile non-zero exit");
            std::process::exit(7);
        }
        other => {
            eprintln!("unsupported hostile mode: {other}");
            std::process::exit(2);
        }
    }
}
