"""Verify which compiled modules the pinned Lean runtime resolves for the K02 capture-to-entry and retained catalog staging."""
from pathlib import Path
import hashlib
import json
import os
import subprocess

HERE = Path(__file__).resolve().parent
SUCCESSOR = HERE.parents[3]
BASE = SUCCESSOR.parents[1]
ROOT = BASE.parents[3]


def binding(path):
    return {"path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    verification_path = HERE / "verification.json"
    verification = json.loads(verification_path.read_text())
    sources = [ROOT / item["path"] for item in verification["sources"]]
    for source, expected in zip(sources, verification["sources"]):
        assert binding(source) == expected
    runtime = BASE / "v1/formal/.toolcache/lean-4.33.1-linux"
    lean = runtime / "bin/lean"
    assert binding(lean) == verification["compiler"]
    stems = {source.stem for source in sources}
    output_bindings = {(item["phase"], Path(item["source"]["path"]).stem): item["olean"]
                       for item in verification["records"]}
    records = []
    for phase in ["compile", "replay"]:
        build = HERE / phase
        for source in sources:
            result = subprocess.run([str(lean), "--deps", str(source)], cwd=source.parent,
                                    env=dict(os.environ, LEAN_PATH=str(build)),
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            assert result.returncode == 0 and not result.stderr, (source, result.stderr)
            dependencies = []
            for line in result.stdout.splitlines():
                dependency = Path(line.strip()).resolve()
                assert dependency.is_file()
                if dependency.stem in stems:
                    assert dependency == build / (dependency.stem + ".olean"), dependency
                    assert binding(dependency) == output_bindings[phase, dependency.stem]
                    origin = "fresh-custom-module"
                else:
                    assert dependency.is_relative_to(runtime / "lib/lean"), dependency
                    origin = "pinned-runtime-library"
                dependencies.append(dict(binding(dependency), origin=origin))
            records.append({"phase": phase, "source": binding(source), "dependencies": dependencies})
    report = {"task": "N01", "unit": "K02-binding-capture", "result": "import-resolution-audit-pass",
              "driver": binding(Path(__file__)), "verification": binding(verification_path),
              "resolved_source_phase_pairs": len(records), "records": records,
              "claim_scope": "Custom imports resolve to exact outputs from the matching fresh compile/replay phase; this is not independent proof checking.",
              "inherited_discharges": 0, "authority_effect": "none"}
    (HERE / "import-resolution-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"result": report["result"], "resolved_source_phase_pairs": len(records)}))


if __name__ == "__main__":
    run()
