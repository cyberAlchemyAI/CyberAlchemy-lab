"""Build a conservative AC01-AC13 local engineering evidence matrix."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PRODUCT = "product/lab/release-candidates/v1/PRODUCT-ACCEPTANCE.md"
DAG = "docs/plans/0010-lab-one-shot-execution/dag.json"
UNITS = "docs/plans/0010-lab-one-shot-execution/swu-manifest.json"
STATE = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/engineering-state.json"
TASKS = "docs/plans/0011-lab-runtime-completion/work-pack/tasks"
SOURCE_PINS = {
    PRODUCT: "e3bc3ccd33d728a23ce70225abcc74f1328bbdca7e942ff041fd084a13267366",
    DAG: "541a8d188925cbe69b85b47976edd4fcfcded04384924351146cb039c36e7f20",
    UNITS: "bdc6628f0f479838d6d97006d542a31b623f5b7fa0f80088bcf443e8d6c6cec2",
}
TASK_SET_SHA256 = "6bc83a96e7032ace37fc0b294cb3ae381f442299ffeb3efd96f9874bf62caad4"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(root, relative):
    if not isinstance(relative, str):
        raise ValueError("noncanonical input path")
    part = Path(relative)
    if part.is_absolute() or not part.parts or any(p in {".", ".."} for p in part.parts) or part.as_posix() != relative:
        raise ValueError("noncanonical input path")
    path = root / part
    if path.resolve() != path or not path.is_file():
        raise ValueError(f"missing or redirected input: {relative}")
    return path.read_bytes()


def build(root=ROOT):
    product_raw = read(root, PRODUCT)
    if digest(product_raw) != SOURCE_PINS[PRODUCT]:
        raise ValueError("Product acceptance source changed")
    product = product_raw.decode("utf-8")
    sections = re.findall(r"^### (AC\d{2})\n\n(.*?)(?=^### AC\d{2}\n|^## Final decision|\Z)", product, re.M | re.S)
    expected = [f"AC{i:02d}" for i in range(1, 14)]
    if [name for name, _ in sections] != expected:
        raise ValueError("acceptance clauses changed")
    dag_raw = read(root, DAG)
    units_raw = read(root, UNITS)
    if digest(dag_raw) != SOURCE_PINS[DAG] or digest(units_raw) != SOURCE_PINS[UNITS]:
        raise ValueError("original task or unit source changed")
    dag = json.loads(dag_raw)
    units = json.loads(units_raw)
    if (len(dag["nodes"]) != 46 or len(units["units"]) != 63
            or len({r["id"] for r in dag["nodes"]}) != 46
            or len({r["id"] for r in units["units"]}) != 63):
        raise ValueError("original task or unit inventory changed")
    state_raw = read(root, STATE)
    state = json.loads(state_raw)
    tasks = state["tasks"]
    if len(tasks) != 36 or len({t["id"] for t in tasks}) != 36:
        raise ValueError("local task inventory changed")
    by_id = {t["id"]: t for t in tasks}
    evidence_bindings = {}
    for t in tasks:
        if t["status"] not in {"complete", "in_progress", "not_started"}:
            raise ValueError("invalid local task status")
        if t["status"] == "complete" and not t["evidence"]:
            raise ValueError("completed local task has no evidence")
        for path in t["evidence"]:
            evidence_bindings[path] = {"path": path, "sha256": digest(read(root, path))}
    mappings = {name: [] for name in expected}
    task_hashes = {}
    task_set_parts = []
    for name in by_id:
        relative = f"{TASKS}/{name}.md"
        raw = read(root, relative)
        task_hashes[name] = digest(raw)
        task_set_parts.append((f"{name}.md", digest(raw)))
        text = raw.decode("utf-8")
        match = re.search(r"^Tasks: .*? Acceptance: ([^.\n]+)\.", text, re.M)
        if match is None:
            raise ValueError(f"missing acceptance mapping: {name}")
        for ac in re.findall(r"AC\d{2}", match.group(1)):
            if ac not in mappings:
                raise ValueError(f"unknown acceptance mapping: {name}/{ac}")
            mappings[ac].append(name)
    task_set_raw = b"".join(name.encode() + b"\0" + sha.encode() + b"\0" for name, sha in sorted(task_set_parts))
    if digest(task_set_raw) != TASK_SET_SHA256:
        raise ValueError("local task contract set changed")
    if "T19" not in mappings["AC07"]:
        mappings["AC07"].append("T19")
    for linked in mappings.values():
        linked.sort()
    if any(not mapped for mapped in mappings.values()):
        raise ValueError("unmapped acceptance clause")
    rows = []
    for ac, body in sections:
        linked = mappings[ac]
        if body.count("\n\nEvidence:") != 1:
            raise ValueError(f"acceptance evidence form changed: {ac}")
        clause = body.split("\n\nEvidence:", 1)[0].strip()
        rows.append({
            "id": ac,
            "original_clause_sha256": digest(clause.encode("utf-8")),
            "original_clause": clause,
            "state_reported_local_task_status": {name: by_id[name]["status"] for name in linked},
            "state_reported_evidence_bindings": {name: [evidence_bindings[p] for p in by_id[name]["evidence"]] for name in linked if by_id[name]["evidence"]},
            "state_reported_local_activity": "partial" if any(by_id[name]["status"] != "not_started" for name in linked) else "unstarted",
            "local_task_completion_verified_by_this_matrix": False,
            "original_acceptance": "PENDING",
            "remaining_clause": clause,
        })
    return {
        "schema_version": "lab-local-acceptance-matrix/v1",
        "source_sha256": {PRODUCT: digest(product_raw), DAG: digest(dag_raw), UNITS: digest(units_raw), STATE: digest(state_raw)},
        "task_contract_sha256": task_hashes,
        "task_contract_set_sha256": TASK_SET_SHA256,
        "AC07_supplemental_mapping": "T19 managed-file producer/consumer proof per reviewed acceleration verification matrix",
        "original_tasks_accounted": 46,
        "original_units_accounted": 63,
        "acceptance_count": 13,
        "original_acceptance_pass_count": 0,
        "human_owner_pilot_observed": False,
        "protected_source_qualified": False,
        "canonical_admission_or_release_effect": False,
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
