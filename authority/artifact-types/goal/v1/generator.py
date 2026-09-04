#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parents[3] / "tooling/generators/cml07_identity_artifact.py"
spec = importlib.util.spec_from_file_location("cml07_identity_generator", SHARED)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

if __name__ == "__main__":
    artifact = json.loads((ROOT / "artifact.json").read_text(encoding="utf-8"))
    (ROOT / "ARTIFACT.md").write_text(module.render_artifact(artifact), encoding="utf-8")
    witness = ROOT / artifact["validation_contract"]["positive_witness"]
    data = json.loads(witness.read_text(encoding="utf-8"))
    projection = ROOT / artifact["validation_contract"]["positive_projection"]
    projection.write_text(module.render_instance(artifact, data), encoding="utf-8")
