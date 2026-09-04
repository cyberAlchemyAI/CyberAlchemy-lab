#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parents[3] / "tooling/validators/cml07_identity_artifact_type.py"
spec = importlib.util.spec_from_file_location("cml07_identity_validator", SHARED)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

if __name__ == "__main__":
    raise SystemExit(module.run(ROOT, "identity-lineage"))
