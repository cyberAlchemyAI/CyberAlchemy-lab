#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent / "_candidate_pack.py"
spec = importlib.util.spec_from_file_location("candidate_pack", SHARED)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

if __name__ == "__main__":
    module.render(ROOT)
