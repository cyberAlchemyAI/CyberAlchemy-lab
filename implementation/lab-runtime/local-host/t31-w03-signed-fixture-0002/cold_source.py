"""Cold read the newly signed W03 source through its actual selected Reader v2."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[4]
INSTANCE = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-62f4c217e8b9a30d"
SOURCE_SHA = "69967b19d3bb170885c28542f36b66a1a4ed8a3936abcd1850f64c44d19ac3b1"
PACKAGE_SHA = "0dc6ad7f7769f96eeaa561d137d0bedd423bf33585f343f1283d36a003c94513"
READER_SHA = "63b89c72dca1c9ea2806b15ecf02d2b909328c4686a30e8a5380b52351f91baf"
SCRATCH = Path("/home/vlad_/.local/cal-t31-workflow-source-legacy-local-62f4c217e8b9a30d")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> dict:
    if [sha(INSTANCE / path) for path in (
        "source/source-manifest.json", "source/packages/0001/manifest.json", "reader-w03-0002/source-manifest.json"
    )] != [SOURCE_SHA, PACKAGE_SHA, READER_SHA]:
        raise ValueError("selected signed Source/Reader bytes changed")
    if SCRATCH.is_symlink() or not SCRATCH.is_dir() or SCRATCH.stat().st_uid != os.getuid() or SCRATCH.stat().st_mode & 0o777 != 0o700:
        raise ValueError("task-owned cold scratch differs")
    os.environ["TMPDIR"] = str(SCRATCH)
    tempfile.tempdir = None
    reader_dir = INSTANCE / "reader-w03-0002"
    name = "_cal_t31_w03_reader_v2_cold"
    spec = importlib.util.spec_from_file_location(name, reader_dir / "__init__.py",
                                                  submodule_search_locations=[str(reader_dir)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    selected = __import__(name + ".reader", fromlist=["SelectedReader"])
    reader = selected.SelectedReader(READER_SHA, SOURCE_SHA, PACKAGE_SHA)
    before = time.monotonic()
    with reader.open_signed(SOURCE_SHA, PACKAGE_SHA) as sources:
        records = reader.records
        desired = records.IMPLEMENTATION + "@" + records.VERSION
        subject = sources.view.subjects[desired]
        actual = subject["record"]["payload"]["execution_entrypoint_ref"]
        expected = str((reader_dir / "reader.py").relative_to(ROOT)) + "#SelectedReader.open_signed"
        if actual != expected or not any(r["artifact"]["version_ref"] == desired for r in sources.records):
            raise ValueError("signed Implementation does not bind eligible actual Reader v2")
        source_rows = json.loads((INSTANCE / "source/packages/0001/record-index.json").read_bytes())
        if len(source_rows) != 40 or len({row["version_ref"] for row in source_rows}) != 40:
            raise ValueError("signed 40-target source index differs")
        result = {"result": "PASS", "source_manifest_sha256": SOURCE_SHA,
                  "source_package_sha256": PACKAGE_SHA, "reader_manifest_sha256": READER_SHA,
                  "signed_source_targets": len(source_rows), "current_reader_eligible_records": len(sources.records),
                  "implementation_entrypoint_ref": expected,
                  "source_cut_head": sources.view.data["head"]["transaction_digest"],
                  "duration_seconds": time.monotonic() - before,
                  "authority_effect": "none", "actual_owner_outcome": None,
                  "session_created": False, "workflow_transition_created": False}
    reader.guard()
    return result


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, indent=2), flush=True)
