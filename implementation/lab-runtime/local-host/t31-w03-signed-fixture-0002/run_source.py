"""Run the exact signed W03 Reader-v2 Source constructor once."""
from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[4]
SOURCE = (ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances/"
          "legacy-local-62f4c217e8b9a30d/source")
SCRATCH = Path("/home/vlad_/.local/cal-t31-workflow-source-legacy-local-62f4c217e8b9a30d")
SOURCE_SHA = "69967b19d3bb170885c28542f36b66a1a4ed8a3936abcd1850f64c44d19ac3b1"


def main() -> None:
    if SOURCE.is_symlink() or any(part.is_symlink() for part in SOURCE.parents if part != ROOT):
        raise ValueError("selected Source path is not a direct regular directory")
    if hashlib.sha256((SOURCE / "source-manifest.json").read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("selected W03 Source manifest changed")
    if not SCRATCH.exists():
        SCRATCH.mkdir(mode=0o700)
    if (SCRATCH.is_symlink() or not SCRATCH.is_dir() or SCRATCH.stat().st_uid != os.getuid()
            or SCRATCH.stat().st_mode & 0o777 != 0o700):
        raise ValueError("task-owned scratch identity or mode differs")
    os.environ["TMPDIR"] = str(SCRATCH)
    tempfile.tempdir = None
    name = "_cal_t31_w03_reader_v2_signed_source_constructor"
    spec = importlib.util.spec_from_file_location(name, SOURCE / "__init__.py",
                                                  submodule_search_locations=[str(SOURCE)])
    selected = importlib.util.module_from_spec(spec)
    sys.modules[name] = selected
    spec.loader.exec_module(selected)
    build = __import__(name + ".build", fromlist=["*"])
    build.main(SOURCE_SHA)


if __name__ == "__main__":
    main()
