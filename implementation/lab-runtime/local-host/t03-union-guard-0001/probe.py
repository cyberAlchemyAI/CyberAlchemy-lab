"""Measure one entry/exit byte-closure pass over the selected native family.

This is a candidate byte-verification primitive, not an API guard replacement.
The original role-specific semantic, signed-source, package and native checks
must still be preserved when a later versioned API integrates it.
"""

import datetime as dt
import hashlib
import importlib.util
import json
import statistics
import sys
import time
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FAMILY = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8"
CHAIN = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/NATIVE-CHAIN-RECEIPT-0001.json"
CHAIN_SHA = "75e0795f62a352926932e449f6007a674ad0964aa2c8a0cea17e5872fcf67d45"
CAPTURE_PIN = "eba3611c44fb76d89c7e741aac36ebcf52d3dc59786006af044d0ad98dc34962"
ROLES = ("source", "reader", "mapped", "context")


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected_capture():
    source = FAMILY / "source"
    name = "_cal_t03_union_selected_source"
    spec = importlib.util.spec_from_file_location(name, source / "__init__.py",
                                                  submodule_search_locations=[str(source)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    base = __import__(name + ".base", fromlist=["SOURCE_CAPTURE"])
    need(base._CAPTURE_PIN == CAPTURE_PIN and
         base.SOURCE_CAPTURE.kernel_digest() == CAPTURE_PIN,
         "SELECTED_CAPTURE_CHANGED")
    return base.SOURCE_CAPTURE


def union_rows(manifests, extra=()):
    selected = {}
    source_count = 0
    for manifest in manifests:
        need(type(manifest) is dict and type(manifest.get("files")) is list,
             "MANIFEST_FILE_SET_REFUSED")
        for row in manifest["files"]:
            source_count += 1
            _add(selected, row)
    for row in extra:
        _add(selected, row)
    return [selected[name] for name in sorted(selected)], source_count


def _add(selected, row):
    need(type(row) is dict and set(row) == {"path", "sha256"}, "UNION_ROW_SHAPE_REFUSED")
    old = selected.get(row["path"])
    need(old is None or old == row, "UNION_PIN_CONFLICT " + row["path"])
    selected[row["path"]] = row


def family_selection(capture):
    chain_raw = CHAIN.read_bytes()
    need(sha(chain_raw) == CHAIN_SHA, "CHAIN_RECEIPT_CHANGED")
    chain = json.loads(chain_raw)
    need(chain["schema"] == "cal-native-current-source8-local-chain-receipt/v1" and
         chain["protected_source8_qualification"] is False and
         chain["authority_effect"] == "none" and
         chain["instance"] == FAMILY.name and
         chain["family_path"] == FAMILY.relative_to(ROOT).as_posix(),
         "FAMILY_SELECTION_REFUSED")
    outputs = {name: json.loads(capture.capture_one(ROOT, chain["phase_results"][name],
                                                  code_sha256=CAPTURE_PIN))
               for name in ("source", "cold", "reader", "mapped", "context")}
    need(outputs["cold"]["result"] == "PASS-native-cold" and
         outputs["cold"]["independent_cold_replays"] == 2 and
         outputs["cold"]["original_byte_parity"] is True and
         outputs["reader"]["result"] == "PASS-current-reader" and
         outputs["mapped"]["result"] == "PASS-native-mapper" and
         outputs["context"]["result"] == "PASS-native-Context-construction",
         "NATIVE_PHASE_RESULT_REFUSED")
    pins = (outputs["source"]["source_binding"], outputs["reader"]["reader_binding"],
            outputs["mapped"]["mapper_binding"], outputs["context"]["context_binding"])
    manifests = []
    for role, row in zip(ROLES, pins):
        need(row["path"] == (FAMILY / role / "source-manifest.json").relative_to(ROOT).as_posix(),
             "ROLE_MANIFEST_ORIGIN_REFUSED")
        raw = capture.capture_one(ROOT, row, code_sha256=CAPTURE_PIN)
        manifests.append(json.loads(raw))
    source_manifest, reader_manifest, mapped_manifest, context_manifest = manifests
    need(outputs["source"]["source_binding"] == outputs["cold"]["source_binding"] and
         outputs["source"]["package_binding"] == outputs["cold"]["package_binding"] and
         chain["period_binding"] == outputs["cold"]["period_binding"] and
         reader_manifest["producer_source_binding"] == pins[0] and
         reader_manifest["producer_package_binding"] == outputs["source"]["package_binding"] and
         mapped_manifest["original_source_binding"] == pins[0] and
         mapped_manifest["original_package_binding"] == outputs["source"]["package_binding"] and
         mapped_manifest["adapter_source_binding"] == pins[1] and
         context_manifest["qualified_mapper_source_binding"] == pins[2] and
         context_manifest["qualified_mapper_package_binding"] == outputs["mapped"]["package_binding"],
         "NATIVE_PHASE_LINK_REFUSED")
    extra = list(pins) + [chain["period_binding"], outputs["source"]["package_binding"],
                          outputs["mapped"]["package_binding"],
                          outputs["context"]["package_binding"],
                          {"path": CHAIN.relative_to(ROOT).as_posix(), "sha256": CHAIN_SHA},
                          *chain["phase_results"].values()]
    rows, source_count = union_rows(manifests, extra)
    period_row = chain["period_binding"]
    period_raw = capture.capture_one(ROOT, period_row, code_sha256=CAPTURE_PIN)
    period = json.loads(period_raw)
    now = dt.datetime.now(dt.timezone.utc)
    need(dt.datetime.fromisoformat(period["not_before"]) <= now <
         dt.datetime.fromisoformat(period["expires_at"]), "SOURCE_PERIOD_EXPIRED")
    return rows, source_count, chain


def verify_boundary(root, rows, capture):
    return capture.verify_all(root, rows, code_sha256=CAPTURE_PIN)


@contextmanager
def guard_window(root, rows, capture, *, source_expires_at=None):
    """Hash every distinct selected input at entry and again at exit."""
    def current_source():
        if source_expires_at is None:
            return
        end = dt.datetime.fromisoformat(source_expires_at)
        need(end.tzinfo is not None and end.utcoffset() == dt.timedelta() and
             dt.datetime.now(dt.timezone.utc) < end, "SOURCE_PERIOD_EXPIRED")

    current_source()
    verify_boundary(root, rows, capture)
    primary = None
    try:
        yield
    except BaseException as error:
        primary = error
    try:
        verify_boundary(root, rows, capture)
        current_source()
    except BaseException as exit_error:
        if primary is not None:
            raise BaseExceptionGroup("body and exit integrity failed", [primary, exit_error])
        raise
    if primary is not None:
        raise primary


def measure(samples=3):
    need(type(samples) is int and 1 <= samples <= 5, "SAMPLE_COUNT_REFUSED")
    capture = selected_capture()
    rows, source_count, chain = family_selection(capture)
    seconds = []
    for _ in range(samples):
        started = time.monotonic()
        verify_boundary(ROOT, rows, capture)
        seconds.append(time.monotonic() - started)
    with guard_window(ROOT, rows, capture, source_expires_at=chain["expires_at"]):
        pass
    return {"schema": "cal-t03-union-byte-verification-probe/v1", "authority_effect": "none",
            "family_instance": chain["instance"], "source_count": source_count,
            "unique_selected_paths": len(rows), "repeat_rows_avoided_per_boundary": source_count - len(rows),
            "samples_seconds": [round(v, 3) for v in seconds],
            "median_seconds": round(statistics.median(seconds), 3),
            "entry_exit_window_passed": True,
            "claim_ceiling": "Selected local byte-closure union verification only; no replacement of role semantic/native guards or complete Session outcome."}


if __name__ == "__main__":
    print(json.dumps(measure(), sort_keys=True))
