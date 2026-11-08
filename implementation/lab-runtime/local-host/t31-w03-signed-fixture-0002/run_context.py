"""Run one native Context delivery on the exact W03 Reader-v2 cut."""
from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[4]
CONTEXT = (ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances/"
           "legacy-local-62f4c217e8b9a30d/context-w03-0005")
SCRATCH = Path("/home/vlad_/.local/cal-t31-workflow-source-legacy-local-62f4c217e8b9a30d")
CONTEXT_SHA = "5f40f7b23cb966d9e048c5fe270b417b2f14bb9e8580bb485997d466dc951ca0"
MAPPER_PACKAGE_SHA = "022644442f5cebd30ac5695ee393de11ee2b3ea916279a95c85f741082792427"


def main() -> None:
    if hashlib.sha256((CONTEXT / "source-manifest.json").read_bytes()).hexdigest() != CONTEXT_SHA:
        raise ValueError("selected Context source changed")
    if SCRATCH.is_symlink() or not SCRATCH.is_dir() or SCRATCH.stat().st_uid != os.getuid() or SCRATCH.stat().st_mode & 0o777 != 0o700:
        raise ValueError("task-owned scratch differs")
    os.environ["TMPDIR"] = str(SCRATCH)
    tempfile.tempdir = None
    name = "_cal_t31_w03_reader_v2_context"
    spec = importlib.util.spec_from_file_location(name, CONTEXT / "__init__.py",
                                                  submodule_search_locations=[str(CONTEXT)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    build = __import__(name + ".build", fromlist=["build"])
    build.build(CONTEXT_SHA, MAPPER_PACKAGE_SHA)


if __name__ == "__main__":
    main()
