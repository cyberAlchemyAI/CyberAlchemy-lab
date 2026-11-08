"""Exact dependency inventory for the selected API45 revision-2 WSL candidate.

This is a portability preflight, not a package builder. It reads and hashes
selected files but never copies them or opens protected source bodies.
"""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
API = "product/lab/release-candidates/v1/interface/api-integration-v45-r03-0005-coverage-0002"
SOURCE = {"path": f"{API}/source-manifest.json", "sha256": "3f21cda1927c7479efb77059255118d8a171a2f4ee8e1c8086b0ddbb1268faeb"}
PROFILE = {"path": f"{API}/contract-profile.json", "sha256": "05edcf558bd7bc3974ed5d7da76367b32e8ebc8f45636a65734700800b9c86aa"}
SELECTION = {"path": "product/lab/release-candidates/v1/interface/api-integration-v30/SCHEMA-EXECUTION-DEPENDENCIES.json", "sha256": "61d6d75ab210a2cff4cc48dbc35fe67101f9f1e428222ce784507f67edca3932"}
REBIND_RECEIPT = {"path": f"{API}/rebind-receipt.json", "sha256": "26bcefb0d678893b514913d9151ebfbc59ef141259bca253e03660a6fe7f10b4"}


def canonical(obj):
    return (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def read_binding(binding):
    path = Path(binding["path"])
    target = path if path.is_absolute() else ROOT / path
    raw = target.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
        raise ValueError(f"selected binding changed: {binding['path']}")
    return json.loads(raw)


def classify(path):
    p = Path(path)
    if p.is_absolute():
        return "absolute_host_dependency"
    parts = p.parts
    if not parts or ".." in parts:
        return "invalid_relative_path"
    if any(part in {"secrets", "protected", "private"} for part in parts):
        return "explicit_private_path"
    if parts[0] == "authority":
        return "live_authority_state"
    if parts[0] == ".local":
        return "local_runtime_artifact"
    if parts[0] in {"working", "receipts", "docs"}:
        return "repository_evidence_or_documentation"
    return "repository_code_or_contract"


def unique_rows(rows, label):
    paths = [row["path"] for row in rows]
    if paths != sorted(set(paths)):
        raise ValueError(f"{label} paths are not unique and sorted")
    if any(not {"path", "sha256"} <= set(row) or not set(row) <= {"path", "sha256", "size_bytes"} for row in rows):
        raise ValueError(f"{label} has an invalid row")
    return {row["path"]: row for row in rows}


def select(source, profile, selection):
    source_rows = unique_rows(source["files"], "source")
    profile_rows = unique_rows(profile["files"], "profile")
    execution_rows = unique_rows(selection["files"], "execution")
    if set(selection["selection_reasons"]) != set(execution_rows):
        raise ValueError("selection reasons do not cover the exact execution rows")
    for path, row in execution_rows.items():
        if profile_rows.get(path) != row:
            raise ValueError(f"execution row outside selected profile: {path}")
    if profile["schema_execution_dependency_binding"] != SELECTION:
        raise ValueError("profile selects a different execution closure")
    overlapping = set(source_rows) & set(execution_rows)
    for path in overlapping:
        if source_rows[path] != execution_rows[path]:
            raise ValueError(f"source/execution conflict: {path}")
    extra = [profile["schema_execution_dependency_binding"], profile["original_operation_catalog_binding"], profile["original_schema_inputs_binding"]]
    exact_guard = dict(execution_rows)
    for row in extra:
        old = exact_guard.get(row["path"])
        if old is not None and old != row:
            raise ValueError(f"guard binding conflict: {row['path']}")
        exact_guard[row["path"]] = row
    return source_rows, execution_rows, exact_guard, overlapping


def file_status(row):
    path = Path(row["path"])
    target = path if path.is_absolute() else ROOT / path
    if not target.is_file():
        return "missing"
    try:
        h = hashlib.sha256()
        with target.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(chunk)
        return "matching" if h.hexdigest() == row["sha256"] else "changed"
    except OSError:
        return "unreadable"


def check_guard_extras(rows):
    checked = []
    for row in rows:
        status = file_status(row)
        if status != "matching":
            raise ValueError(f"extra guard binding {status}: {row['path']}")
        checked.append({**row, "class": classify(row["path"]), "current_byte_status": status})
    return checked


def startup_reads(source, profile, selection):
    """Top-level guard/schema reads outside the 5,250 selected data rows.

    The rebind receipt has only a preflight snapshot pin: the selected API
    checks its semantic fields but does not bind its raw bytes in its source
    manifest. That distinction is retained in the inventory.
    """
    names = (
        "family_source_manifest_binding", "family_source_package_binding",
        "family_reader_manifest_binding", "family_mapped_package_binding",
        "family_mapping_binding", "family_context_manifest_binding",
        "family_context_package_binding", "engine_profile_binding",
        "predecessor_source_manifest_binding",
    )
    bindings = [(source[name], "source_manifest_binding") for name in names]
    bindings += [
        (selection["parent_source_binding"], "schema_selection_parent"),
        (selection["parent_profile_binding"], "schema_selection_parent"),
        (SELECTION, "selected_schema_selection"),
        (profile["original_schema_inputs_binding"], "profile_guard_binding"),
        (SOURCE, "selected_source_manifest"),
        (REBIND_RECEIPT, "preflight_snapshot_only"),
    ]
    if len(bindings) != 15 or len({row["path"] for row, _ in bindings}) != 15:
        raise ValueError("top-level startup read inventory differs")
    checked = []
    for row, origin in sorted(bindings, key=lambda item: item[0]["path"]):
        status = file_status(row)
        if status != "matching":
            raise ValueError(f"startup binding {status}: {row['path']}")
        checked.append({**row, "pin_origin": origin, "class": classify(row["path"]),
                        "current_byte_status": status})
    return checked


def build():
    source = read_binding(SOURCE)
    profile = read_binding(PROFILE)
    selection = read_binding(SELECTION)
    source_rows, execution_rows, exact_guard, overlapping = select(source, profile, selection)
    rows = []
    for path in sorted(set(source_rows) | set(execution_rows)):
        source_row = source_rows.get(path)
        execution_row = execution_rows.get(path)
        row = source_row or execution_row
        rows.append({
            "path": path,
            "sha256": row["sha256"],
            "class": classify(path),
            "source_manifest_selected": source_row is not None,
            "schema_execution_selected": execution_row is not None,
            "selection_reasons": selection["selection_reasons"].get(path, []),
            "current_byte_status": file_status(row),
        })
    counts = {}
    statuses = {}
    for row in rows:
        counts[row["class"]] = counts.get(row["class"], 0) + 1
        statuses[row["current_byte_status"]] = statuses.get(row["current_byte_status"], 0) + 1
    extra_guard = check_guard_extras([exact_guard[path] for path in sorted(set(exact_guard) - set(execution_rows))])
    startup = startup_reads(source, profile, selection)
    return {
        "schema_version": "lab-t25-api45r2-portability-preflight/v1",
        "selected_source_manifest": SOURCE,
        "selected_contract_profile": PROFILE,
        "selected_schema_execution_closure": SELECTION,
        "source_manifest_rows": len(source_rows),
        "schema_execution_rows": len(execution_rows),
        "overlap_rows": len(overlapping),
        "union_rows": len(rows),
        "guard_rows": len(exact_guard),
        "extra_guard_rows": extra_guard,
        "top_level_startup_read_count_outside_selected_rows": len(startup),
        "top_level_startup_read_rows": startup,
        "class_counts": dict(sorted(counts.items())),
        "byte_status_counts": dict(sorted(statuses.items())),
        "portability_blockers": [
            "Absolute WSL/Python host dependencies are selected by exact path and hash.",
            "Selected authority rows refer to mutable local authority state and are not copied.",
            "The complete 33434-row contract profile is much broader than the 5043-row execution selection; startup reads extend beyond this union.",
            "ABI, loader, credentials and protected private Source/issuer inputs are outside this metadata-only inventory.",
            "The 15 top-level guard/schema startup reads are recorded separately; this is not a transitive startup closure.",
        ],
        "rows": rows,
        "claim_ceiling": "Exact selected dependency preflight only; no portable API45 package, installed runtime or protected effect.",
    }


if __name__ == "__main__":
    print(canonical(build()).decode(), end="")
