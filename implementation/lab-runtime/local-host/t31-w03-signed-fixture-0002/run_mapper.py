"""Run the exact native W03 Reader-v2 Mapper once."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[4]
MAPPER = (ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances/"
          "legacy-local-62f4c217e8b9a30d/mapped-w03-0004")
SCRATCH = Path("/home/vlad_/.local/cal-t31-workflow-source-legacy-local-62f4c217e8b9a30d")
MAPPER_SHA = "09a0e50dc3ab776e9a8c8d412faf1bb73ca9a1cb13596e1930decfbc2f10ee07"


def main() -> None:
    if hashlib.sha256((MAPPER / "source-manifest.json").read_bytes()).hexdigest() != MAPPER_SHA:
        raise ValueError("selected Mapper source changed")
    if SCRATCH.is_symlink() or not SCRATCH.is_dir() or SCRATCH.stat().st_uid != os.getuid() or SCRATCH.stat().st_mode & 0o777 != 0o700:
        raise ValueError("task-owned scratch differs")
    os.environ["TMPDIR"] = str(SCRATCH)
    tempfile.tempdir = None
    name = "_cal_t31_w03_reader_v2_mapper"
    spec = importlib.util.spec_from_file_location(name, MAPPER / "__init__.py",
                                                  submodule_search_locations=[str(MAPPER)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    build = __import__(name + ".build", fromlist=["build"])
    build.build(MAPPER_SHA)


if __name__ == "__main__":
    main()
