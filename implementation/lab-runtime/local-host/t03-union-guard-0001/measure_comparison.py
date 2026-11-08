"""Compare selected Context preflight with union byte verification."""

import datetime as dt
import hashlib
import importlib.util
import json
import os
import stat
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "MEASUREMENT-0003.json"
_spec = importlib.util.spec_from_file_location("cal_t03_union_probe", HERE / "probe.py")
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected_context_preflight():
    folder = probe.FAMILY / "context"
    name = "_cal_t03_comparison_context"
    spec = importlib.util.spec_from_file_location(name, folder / "__init__.py",
                                                  submodule_search_locations=[str(folder)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    control = __import__(name + ".control", fromlist=["verify_source"])
    chain = json.loads(probe.CHAIN.read_bytes())
    pin = json.loads((probe.ROOT / chain["phase_results"]["context"]["path"]).read_bytes())[
        "context_binding"]["sha256"]
    started = time.monotonic()
    manifest = control.verify_source(pin)
    return round(time.monotonic() - started, 3), len(manifest["files"])


def measure():
    started = dt.datetime.now(dt.timezone.utc)
    original_seconds, context_rows = selected_context_preflight()
    candidate = probe.measure(samples=3)
    return {
        "schema": "cal-t03-selected-guard-comparison/v1", "authority_effect": "none",
        "observed_at_utc": started.isoformat(),
        "selected_context_preflight_seconds": original_seconds,
        "selected_context_source_rows": context_rows,
        "candidate_union_boundary_samples_seconds": candidate["samples_seconds"],
        "candidate_union_boundary_median_seconds": candidate["median_seconds"],
        "candidate_union_entry_exit_window_passed": candidate["entry_exit_window_passed"],
        "candidate_unique_selected_paths": candidate["unique_selected_paths"],
        "candidate_source_row_total": candidate["source_count"],
        "candidate_repeat_rows_avoided_per_boundary": candidate["repeat_rows_avoided_per_boundary"],
        "native_chain_receipt_sha256": sha(probe.CHAIN.read_bytes()),
        "context_source_manifest_sha256": sha((probe.FAMILY / "context/source-manifest.json").read_bytes()),
        "probe_code_sha256": sha((HERE / "probe.py").read_bytes()),
        "comparison_code_sha256": sha(Path(__file__).read_bytes()),
        "claim_ceiling": "Byte-closure candidate measured against real selected Context preflight; role semantic/native guard replacement and API Session outcome remain unproven.",
    }


def save(value):
    parent = RECEIPT.parent.stat()
    if parent.st_uid != os.getuid() or stat.S_IMODE(parent.st_mode) & 0o022:
        raise ValueError("MEASUREMENT_PARENT_REFUSED")
    raw = json.dumps(value, sort_keys=True, indent=2).encode() + b"\n"
    fd = os.open(RECEIPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        if stream.write(raw) != len(raw):
            raise OSError("MEASUREMENT_SHORT_WRITE")
        stream.flush()
        os.fsync(stream.fileno())
    return sha(raw)


if __name__ == "__main__":
    value = measure()
    print(json.dumps({"measurement_sha256": save(value),
                      "context_preflight_seconds": value["selected_context_preflight_seconds"],
                      "union_boundary_median_seconds": value["candidate_union_boundary_median_seconds"]},
                     sort_keys=True))
