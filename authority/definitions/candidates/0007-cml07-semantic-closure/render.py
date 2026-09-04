#!/usr/bin/env python3
from pathlib import Path
import importlib.util

from candidate_support import composed_registry_postimage

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent / "_candidate_pack.py"
spec = importlib.util.spec_from_file_location("candidate_pack", SHARED)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
module.registry_postimage = lambda root, candidate: composed_registry_postimage(module, root, candidate)

if __name__ == "__main__":
    module.render(ROOT)
