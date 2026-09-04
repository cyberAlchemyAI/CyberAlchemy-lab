#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("ctx01_validator", ROOT.parents[3] / "tooling/validators/ctx01_artifact_type.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)
if __name__ == "__main__": raise SystemExit(MODULE.run(ROOT, "capability-instance"))
