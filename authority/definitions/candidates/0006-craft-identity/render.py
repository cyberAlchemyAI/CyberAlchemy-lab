#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT.parent / "_candidate_pack.py"
spec = importlib.util.spec_from_file_location("candidate_pack", TOOLS)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
module.render(ROOT)
