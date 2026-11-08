"""Clean-root lower-bound dependency probe for the selected API40 status route."""

import hashlib
import json
from pathlib import Path
import tempfile
import types

ROOT = Path(__file__).absolute().parents[4]
API = "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/"
SOURCE = API + "source-manifest.json"
SOURCE_SHA = "45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219"
PROFILE = API + "contract-profile.json"
PROFILE_SHA = "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614"
DISPOSITIONS = "implementation/lab-runtime/local-host/t25-api40-disposition-inventory-0002/DISPOSITIONS.json"
DISPOSITIONS_SHA = "fe0db17a3d8485a01dfceb0af45e8499f0a7325f6a165bc93a547cc96dc8cb98"
NAMES = tuple(API + name for name in ("serve.py", "guard.py", "service.py", "handlers.py",
                                       "protocol.py", "auth.py")) + (
    "docs/proposals/0008-lab-api-contracts/api-contracts.json",)
REASONS = ("selected stdio entrypoint and pre-auth source guard",
           "selected source guard implementation", "operation dispatch to status handler",
           "status handler and direct catalog file read", "wire schema and request binding",
           "authenticated reader channel", "direct status response catalog binding")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected(name, expected):
    # The full-profile and source selectors are independently pinned by the
    # predecessor package. This probe remains read-only and does not claim an
    # adversarially immutable code origin for its own imports.
    path = ROOT / name
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError("selected path linked")
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError("selected bytes changed: " + name)
    return raw


def inputs():
    source = json.loads(selected(SOURCE, SOURCE_SHA))
    profile = json.loads(selected(PROFILE, PROFILE_SHA))
    dispositions = json.loads(selected(DISPOSITIONS, DISPOSITIONS_SHA))
    source_rows = {row["path"]: row["sha256"] for row in source["files"]}
    profile_rows = {row["path"]: row["sha256"] for row in profile["files"]}
    inventory_rows = {row["path"]: row for row in dispositions["rows"]}
    if (len(source_rows) != 207 or len(profile_rows) != 33424 or
            len(inventory_rows) != 33424 or len(NAMES) != len(set(NAMES))):
        raise ValueError("selected dependency context changed")
    rows = []
    payload = {}
    for name, reason in zip(NAMES, REASONS):
        digest = profile_rows[name]
        if name != NAMES[-1] and source_rows[name] != digest:
            raise ValueError("status source/profile binding differs")
        if inventory_rows[name]["sha256"] != digest or inventory_rows[name]["disposition"] != "unresolved":
            raise ValueError("status prerequisite disposition differs")
        payload[name] = selected(name, digest)
        rows.append({"path": name, "sha256": digest, "role": reason,
                     "source_manifest_selected": name in source_rows,
                     "archive_disposition": "unresolved"})
    return rows, payload


def guard_module(raw):
    module = types.ModuleType("t25_selected_api40_guard")
    module.__file__ = str(ROOT / API / "guard.py")
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


def source_guard_coverage():
    source = json.loads(selected(SOURCE, SOURCE_SHA))
    dispositions = json.loads(selected(DISPOSITIONS, DISPOSITIONS_SHA))
    index = {row["path"]: row for row in dispositions["rows"]}
    rows = []
    counts = {"archive-byte-selected": 0, "unresolved": 0, "not-in-profile": 0}
    for source_row in source["files"]:
        name, digest = source_row["path"], source_row["sha256"]
        selected_row = index.get(name)
        if selected_row is None:
            disposition = "not-in-profile"
        else:
            if selected_row["sha256"] != digest:
                raise ValueError("source guard/profile digest conflict")
            disposition = selected_row["disposition"]
        counts[disposition] += 1
        rows.append({"path": name, "sha256": digest, "profile_disposition": disposition})
    if len(rows) != 207 or counts != {"archive-byte-selected": 1,
                                       "unresolved": 147, "not-in-profile": 59}:
        raise ValueError("source guard coverage changed")
    return rows, counts


def exercise(rows, payload, mutation=None):
    guard = guard_module(payload[API + "guard.py"])
    with tempfile.TemporaryDirectory(prefix="cal-T25-status-dependency-") as directory:
        clean = Path(directory)
        for name, raw in payload.items():
            target = clean / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        if mutation == "missing":
            (clean / NAMES[-1]).unlink()
        elif mutation == "changed":
            (clean / NAMES[-1]).write_bytes(b"changed\n")
        elif mutation is not None:
            raise ValueError("unknown mutation")
        try:
            observed = guard._verify_files(clean, [{"path": row["path"], "sha256": row["sha256"]}
                                                    for row in rows])
        except FileNotFoundError:
            if mutation == "missing":
                return "REFUSED"
            raise
        except ValueError as error:
            if mutation == "changed" and str(error) == "source changed " + NAMES[-1]:
                return "REFUSED"
            raise
        if mutation is not None:
            raise ValueError("changed dependency accepted")
        if observed["verified_files"] != len(rows):
            raise ValueError("clean-root subset check incomplete")
        return "PASS"


def run():
    rows, payload = inputs()
    coverage, counts = source_guard_coverage()
    if exercise(rows, payload) != "PASS":
        raise ValueError("clean-root prerequisite check failed")
    negatives = {name: exercise(rows, payload, name) for name in ("missing", "changed")}
    if negatives != {"missing": "REFUSED", "changed": "REFUSED"}:
        raise ValueError("prerequisite negative differs")
    return {"schema_version": "lab-t25-api40-status-dependency-probe/v2",
            "source_manifest_sha256": SOURCE_SHA, "contract_profile_sha256": PROFILE_SHA,
            "dispositions_sha256": DISPOSITIONS_SHA, "operation": "lab.status",
            "statically_selected_lower_bound": rows,
            "full_source_guard_coverage_rows": coverage,
            "full_source_guard_coverage_counts": counts,
            "clean_root_guard_subset_verified": len(rows),
            "missing_dependency": negatives["missing"],
            "changed_dependency": negatives["changed"],
            "current_service_operation_executed": False,
            "full_source_guard_executed_in_clean_root": False,
            "portable_closure_complete": False,
            "authority_effect": "none", "task_complete": False}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
