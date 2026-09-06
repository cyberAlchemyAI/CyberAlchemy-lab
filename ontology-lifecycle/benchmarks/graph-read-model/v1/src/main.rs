use cal_graph_read_model_benchmark::{BenchmarkConfig, ExternalBackendStatus, execute};
use std::env;
use std::fs::OpenOptions;
use std::io::Write;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut config = BenchmarkConfig::default();
    let mut output: Option<String> = None;
    let mut wavedb_status = "not_evaluable".to_string();
    let mut wavedb_blocker = "cmake is unavailable on the benchmark host; WaveDB correctness and timing were not measured".to_string();
    let mut wavedb_commit = "9c87530e948e414e077fae4f86262a9439905875".to_string();
    let args: Vec<String> = env::args().skip(1).collect();
    let mut index = 0;
    while index < args.len() {
        let value = args
            .get(index + 1)
            .ok_or_else(|| format!("missing value for {}", args[index]))?;
        match args[index].as_str() {
            "--nodes" => config.node_count = value.parse()?,
            "--edges-per-node" => config.relation_edges_per_node = value.parse()?,
            "--queries" => config.query_count = value.parse()?,
            "--repetitions" => config.repetitions = value.parse()?,
            "--seed" => config.seed = value.parse()?,
            "--output" => output = Some(value.clone()),
            "--wavedb-status" => wavedb_status = value.clone(),
            "--wavedb-blocker" => wavedb_blocker = value.clone(),
            "--wavedb-commit" => wavedb_commit = value.clone(),
            unknown => return Err(format!("unknown argument: {unknown}").into()),
        }
        index += 2;
    }
    if config.query_count == 0 || config.repetitions == 0 {
        return Err("query_count and repetitions must be positive".into());
    }

    let receipt = execute(
        config,
        ExternalBackendStatus {
            backend_id: "wavedb_graph".to_string(),
            status: wavedb_status,
            blocker: wavedb_blocker,
            source_commit: wavedb_commit,
            license_posture: "root_core_license_not_found; evaluation_only".to_string(),
        },
    );
    if let Some(path) = output {
        let mut file = OpenOptions::new().create(true).append(true).open(path)?;
        serde_json::to_writer(&mut file, &receipt)?;
        writeln!(file)?;
    } else {
        println!("{}", serde_json::to_string_pretty(&receipt)?);
    }
    Ok(())
}
