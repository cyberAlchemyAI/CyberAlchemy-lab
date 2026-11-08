#!/usr/bin/env python3
"""Dependency-free, check-only validator for the Define system ontology."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent


def repository_root(start: Path) -> Path:
    cursor = start
    while cursor != cursor.parent:
        if (cursor / ".git").exists():
            return cursor
        cursor = cursor.parent
    raise RuntimeError("repository root not found")


PROJECT_ROOT = repository_root(PACKAGE)
REPO = PROJECT_ROOT.parent
DOMAINSPEC_V2 = REPO / "domainspec-core/projects/domainspec-v2"
if not DOMAINSPEC_V2.is_dir():
    DOMAINSPEC_V2 = PROJECT_ROOT / "projects/domainspec-v2"
checks: list[dict[str, str]] = []


def add(check_id: str, outcome: str, detail: str) -> None:
    checks.append({"check_id": check_id, "outcome": outcome, "detail": detail})


def read_json(relative: str):
    return json.loads((PACKAGE / relative).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_workspace_path(declared: str) -> Path:
    relative = Path(declared)
    if relative.parts[:2] == ("projects", "domainspec-v2"):
        return DOMAINSPEC_V2.joinpath(*relative.parts[2:]).resolve()
    if relative.parts[:1] == ("arcanum",):
        return (REPO / "domainspec-core" / relative).resolve()
    return (REPO / relative).resolve()


def unique(values) -> bool:
    return len(values) == len(set(values))


profile = read_json("PROFILE.json")
selection = read_json("TYPE-SELECTION.json")
decision = read_json("MATERIALIZATION-DECISION.json")
sources_doc = read_json("SOURCES.json")
nodes_doc = read_json("NODES.json")
relations_doc = read_json("RELATIONS.json")
views_doc = read_json("VIEWS.json")
bindings = read_json("SCHEMA-BINDINGS.json")
project = read_json("domainspec-project/project.json")
feature_path = project["features"][0]
feature_rel = f"domainspec-project/{feature_path}"
feature = read_json(feature_rel)
residue = [json.loads(line) for line in (PACKAGE / "RESIDUE.jsonl").read_text(encoding="utf-8").splitlines() if line]

node_paths = [f"domainspec-project/specs/define-session-runtime/{item}" for item in feature["node_sources"]]
expected_files = set(profile["inventory_contract"]["core_files"] + node_paths)
actual_files = {str(path.relative_to(PACKAGE)) for path in PACKAGE.rglob("*") if path.is_file() and not str(path.relative_to(PACKAGE)).startswith("receipts/")}
receipt_paths = sorted(PACKAGE.glob("receipts/validation-*.json"))
other_receipts = [path for path in (PACKAGE / "receipts").glob("*") if path.is_file() and path not in receipt_paths]
add("closed-package-inventory", "PASS" if actual_files == expected_files and not other_receipts else "BLOCK", f"{len(actual_files)} material files; receipt history excluded")

for relative in sorted(expected_files):
    try:
        if relative.endswith(".json"):
            json.loads((PACKAGE / relative).read_text(encoding="utf-8"))
    except Exception as exc:
        add(f"json:{relative}", "BLOCK", str(exc))
add("json-parse", "PASS" if not any(c["check_id"].startswith("json:") for c in checks) else "BLOCK", "all declared JSON material parses")

schema = read_json("schemas/ontology-package.schema.json")
add("owned-schema-shape", "PASS" if schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema" and set(schema.get("$defs", {})) >= {"profile", "sources", "nodes", "relations", "views", "residue"} else "BLOCK", "owned package schema has all required definitions")

source_ids = [row["source_id"] for row in sources_doc["sources"]]
add("source-id-uniqueness", "PASS" if unique(source_ids) else "BLOCK", f"{len(source_ids)} source identities")
for row in sources_doc["sources"]:
    candidate = resolve_workspace_path(row["path"])
    contained = REPO == candidate or REPO in candidate.parents
    present = contained and candidate.is_file()
    current = present and digest(candidate) == row["sha256"] and candidate.stat().st_size == row["size_bytes"]
    add(f"source-currency:{row['source_id']}", "PASS" if current else "BLOCK", row["path"] if contained else "path escapes repository")

for row in bindings["external_bindings"]:
    path = resolve_workspace_path(row["path"])
    add(f"schema-binding:{row['record']}", "PASS" if path.is_file() and digest(path) == row["sha256"] else "BLOCK", row["path"])

project_ok = (
    set(project) == {"schema_version", "project_id", "language", "features", "generated_root"}
    and project["schema_version"] == "minted-project/v1"
    and project["project_id"] == "define-session-runtime"
    and project["features"] == ["specs/define-session-runtime/feature.json"]
    and project["language"]["profile"] == {"id":"complete-backend-criteria","version":"2","digest":"2a339fb1eaf7a9913be42a2c6b07a68c33254cd56c770b0c32b1d189a83cfc85"}
    and project["language"]["registries"] == {"kinds_digest":"4394968327b785d50cd323ad58a799feb71b9debf7e06b650b4fd1e4008f9ede","relationships_digest":"82c55ea1ad031d3135c5b8a85162e44b4e85f296b54057fda0dc38131ab376a1"}
    and not project["generated_root"].startswith("/") and ".." not in Path(project["generated_root"]).parts
)
add("domainspec-project-shape", "PASS" if project_ok else "BLOCK", "minted-project/v1 with exact complete-backend-criteria@2 bindings")
feature_ok = set(feature) == {"schema_version", "feature_id", "source_layout", "node_sources"} and feature["schema_version"] == "minted-feature/v1" and feature["feature_id"] == "define-session-runtime" and feature["source_layout"] == "per-node-connections" and unique(feature["node_sources"])
add("domainspec-feature-shape", "PASS" if feature_ok else "BLOCK", f"{len(feature['node_sources'])} per-node sources")

current = json.loads((DOMAINSPEC_V2 / "definitions/meta-types/current-implementation.json").read_text())
allowed_kinds = {row["label"] for row in current["backend_meta_types"]}
formation = json.loads((DOMAINSPEC_V2 / "definitions/minted-project/formation-projection.v1.json").read_text())
formation_by_kind = {row["kind"]: row["body_schema"] for row in formation["kinds"]}


def body_matches(value, contract) -> bool:
    if contract.get("type") == "object":
        if not isinstance(value, dict): return False
        if any(key not in value for key in contract.get("required", [])): return False
        if contract.get("additionalProperties") is False and set(value) - set(contract.get("properties", {})): return False
        return all(body_matches(value[key], child) for key, child in contract.get("properties", {}).items() if key in value)
    if contract.get("type") == "array":
        if not isinstance(value, list): return False
        if len(value) < contract.get("minItems", 0): return False
        if contract.get("uniqueItems") and len({json.dumps(item, sort_keys=True) for item in value}) != len(value): return False
        return all(body_matches(item, contract.get("items", {})) for item in value)
    if contract.get("type") == "string" and not isinstance(value, str): return False
    if "minLength" in contract and len(value) < contract["minLength"]: return False
    if "const" in contract and value != contract["const"]: return False
    if "enum" in contract and value not in contract["enum"]: return False
    if "pattern" in contract and not re.search(contract["pattern"], value, re.I): return False
    return True


node_files = [read_json(path) for path in node_paths]
node_ids = [node["node_id"] for node in node_files]
node_map = {node["node_id"]: node for node in node_files}
node_pattern = re.compile(r"^[a-z][a-z0-9-]*\.[A-Za-z][A-Za-z0-9]*$")
nodes_shape = all(set(node) == {"schema_version","node_id","feature_id","kind","intent","body","connections"} and node["schema_version"] == "minted-node/v1" and node["feature_id"] == "define-session-runtime" and node_pattern.fullmatch(node["node_id"]) and node["intent"] for node in node_files)
add("domainspec-node-shapes", "PASS" if nodes_shape else "BLOCK", f"{len(node_files)} minted-node/v1 sources")
add("node-id-uniqueness", "PASS" if unique(node_ids) else "BLOCK", f"{len(node_ids)} stable node identities")
add("kind-membership-current-baseline", "PASS" if all(node["kind"] in allowed_kinds for node in node_files) else "BLOCK", f"all used kinds occur in {current['baseline']['id']}")
add("formation-body-contract", "PASS" if all(body_matches(node["body"], formation_by_kind[node["kind"]]) for node in node_files) else "BLOCK", "every node body matches the exact formation projection")

relationships = json.loads((DOMAINSPEC_V2 / "definitions/relationships/relationships.yml").read_text())
active = {row["id"]: row for row in relationships["signatures"] if row["status"] == "active"}
edge_rows = []
edge_shape_ok = True
signature_ok = True
for node in node_files:
    for edge in node["connections"]:
        edge_shape_ok &= set(edge) == {"edge_id","type","to"} and bool(re.fullmatch(r"^[a-z][a-z0-9-]*\.edge\.[a-z][a-z0-9-]*$", edge["edge_id"]))
        target = node_map.get(edge["to"])
        sig = active.get(edge["type"])
        source_types = set(sig.get("source_types", [sig.get("source_type")])) if sig else set()
        target_types = set(sig.get("target_types", [sig.get("target_type")])) if sig else set()
        signature_ok &= bool(target and sig and node["kind"] in source_types and target["kind"] in target_types and "same-feature" in sig["feature_scope"])
        edge_rows.append({"relation_id":edge["edge_id"],"type":edge["type"],"from_node_id":node["node_id"],"to_node_id":edge["to"],"source_node_path":next(row["source_path"] for row in nodes_doc["nodes"] if row["node_id"] == node["node_id"]),"status":"candidate","source_refs":["define.interaction","domainspec.relationships"],"authority_effect":"none"})
edge_ids = [row["relation_id"] for row in edge_rows]
add("connection-shapes", "PASS" if edge_shape_ok and unique(edge_ids) else "BLOCK", f"{len(edge_rows)} unique source-owned connections")
add("relationship-signatures", "PASS" if signature_ok else "BLOCK", "every edge matches an active exact kind signature and same-feature scope")
add("endpoint-closure", "PASS" if all(row["from_node_id"] in node_map and row["to_node_id"] in node_map for row in edge_rows) else "BLOCK", "every edge endpoint resolves")

creation_edges = [row for row in edge_rows if row["type"] == "creates"]
creation_ok = unique([row["from_node_id"] for row in creation_edges]) and unique([row["to_node_id"] for row in creation_edges])
add("creates-multiplicity", "PASS" if creation_ok else "BLOCK", "same-feature creates edges are one-to-one")

index_by_id = {row["node_id"]: row for row in nodes_doc["nodes"]}
index_ok = set(index_by_id) == set(node_ids) and len(index_by_id) == len(nodes_doc["nodes"])
for path, node in zip(node_paths, node_files):
    row = index_by_id.get(node["node_id"], {})
    index_ok &= row.get("source_path") == path and row.get("kind") == node["kind"] and row.get("intent") == node["intent"]
add("node-index-one-to-one", "PASS" if index_ok else "BLOCK", "NODES.json equals the per-node identity, path, kind, and intent projection")
relation_projection = {json.dumps(row, sort_keys=True) for row in relations_doc["relations"]}
source_projection = {json.dumps(row, sort_keys=True) for row in edge_rows}
add("relation-index-one-to-one", "PASS" if relation_projection == source_projection and len(relations_doc["relations"]) == len(edge_rows) else "BLOCK", "RELATIONS.json equals the source-owned edge projection independent of file traversal order")

source_id_set = set(source_ids)
add("node-source-ref-closure", "PASS" if all(set(row["source_refs"]) <= source_id_set for row in nodes_doc["nodes"]) else "BLOCK", "all indexed node evidence refs resolve")
add("relation-source-ref-closure", "PASS" if all(set(row["source_refs"]) <= source_id_set for row in relations_doc["relations"]) else "BLOCK", "all indexed relation evidence refs resolve")

view_ids = [view["view_id"] for view in views_doc["views"]]
required_views = {"view.context", "view.high-level-structure", "view.low-level-components", "view.workflow-process", "view.decision-flow", "view.dependency-interface"}
views_ok = set(view_ids) == required_views and len(view_ids) == 6 and all(set(view.get("node_ids", [])) <= set(node_ids) and set(view.get("relation_types", [])) <= set(profile["allowed_relation_types"]) for view in views_doc["views"])
add("six-view-reference-closure", "PASS" if views_ok else "BLOCK", "all six governed Design navigation views reference current ontology records")

design_validator = PACKAGE / "design/scripts/validate.py"
design_run_1 = subprocess.run([sys.executable, str(design_validator)], cwd=REPO, capture_output=True, text=True)
design_run_2 = subprocess.run([sys.executable, str(design_validator)], cwd=REPO, capture_output=True, text=True)
try:
    design_output = json.loads(design_run_1.stdout)
except Exception:
    design_output = {}
design_ok = design_run_1.returncode == design_run_2.returncode == 0 and design_run_1.stdout == design_run_2.stdout and design_output.get("overall") == "PASS" and design_output.get("authority_effect") == "none"
add("discovery-design-package", "PASS" if design_ok else "BLOCK", "bounded Design subpackage validates deterministically without claiming governed Design")

residue_ids = [row["residue_id"] for row in residue]
residue_ok = unique(residue_ids) and all(set(row["source_refs"]) <= source_id_set and row["authority_effect"] == "none" for row in residue)
add("residue-reference-closure", "PASS" if residue_ok else "BLOCK", f"{len(residue)} residue entries retain source and owner routes")

ceiling_ok = profile["status"] == "candidate" and profile["implementation_status"] == "not-implemented" and profile["authority_effect"] == "none" and profile["domainspec_binding"]["profile_status"] == "candidate" and profile["domainspec_binding"]["release_admission"] == "not-granted" and all(row["status"] == "candidate" and row["implementation_status"] == "not-implemented" and row["authority_effect"] == "none" for row in nodes_doc["nodes"]) and all(row["status"] == "candidate" and row["authority_effect"] == "none" for row in relations_doc["relations"])
add("candidate-release-authority-ceiling", "PASS" if ceiling_ok else "BLOCK", "candidate, not implemented, release not granted, authority effect none")
add("forbidden-implementation-admission-claims", "PASS" if selection["authority_effect"] == "none" and decision["authority_effect"] == "none" and decision["parent_package_inventory_effect"] == "admitted-nested-boundary" else "BLOCK", "nested-package admission grants no implementation, conformance, parent PASS, or other authority")

parent_profile = json.loads((REPO / "cyberAlchemy-v2/define/profile.json").read_text())
parent_children = {
    row.get("child_id"): row for row in parent_profile.get("child_packages", [])
}
parent_binding = parent_children.get("system", {})
parent_binding_ok = (
    "system-ontology" in parent_profile.get("nested_package_roots", [])
    and parent_binding.get("package_root") == "system-ontology"
    and parent_binding.get("ontology_id") == profile["ontology_id"]
    and parent_binding.get("ontology_type") == profile["ontology_type"]
    and parent_binding.get("branch") == profile["branch"]
    and parent_binding.get("profile_path") == "system-ontology/PROFILE.json"
    and parent_binding.get("validator_path") == "system-ontology/scripts/validate.py"
    and parent_binding.get("receipt_glob") == "system-ontology/receipts/validation-*.json"
    and parent_binding.get("owner_route") == profile["owner_route"]
    and parent_binding.get("visibility") == profile["visibility"]
    and parent_binding.get("authority_effect") == "none"
)
parent_inventory_residue = next(
    (row for row in residue if row.get("residue_id") == "RES-CAV2-DEFINE-SYS-001"),
    {},
)
parent_inventory_residue_ok = (
    parent_inventory_residue.get("kind") == "parent-closed-inventory"
    and parent_inventory_residue.get("source_refs") == ["define.profile"]
    and (
        (parent_binding_ok and parent_inventory_residue.get("status") == "resolved")
        or (
            not parent_binding_ok
            and parent_inventory_residue.get("status") in {"open", "blocked"}
        )
    )
)

material_hash = hashlib.sha256()
for relative in sorted(expected_files):
    material_hash.update(relative.encode())
    material_hash.update(b"\0")
    material_hash.update(hashlib.sha256((PACKAGE / relative).read_bytes()).digest())
material_digest = material_hash.hexdigest()

add("receipt-currency", "PASS", "all present append-only receipts bind the current material digest and exact check-only output; zero is allowed before first materialization")
add("parent-define-child-package-binding", "PASS" if parent_binding_ok else "BLOCK", "parent bridge admits and validates system-ontology as an independently owned nested child")
add("parent-inventory-residue-consistency", "PASS" if parent_inventory_residue_ok else "BLOCK", "RES-CAV2-DEFINE-SYS-001 status follows the exact parent nested-package declaration and child profile identity")
add("domainspec-v2-compilation", "NOT_EVALUABLE", profile["domainspec_binding"]["compiler_reason"])

def render() -> tuple[dict, str]:
    blocked = sum(row["outcome"] == "BLOCK" for row in checks)
    flagged = sum(row["outcome"] in {"FLAG", "NOT_EVALUABLE"} for row in checks)
    overall = "BLOCK" if blocked else "FLAG" if flagged else "PASS"
    result = {
        "schema_version":"cav2.define.system-ontology.validation-result/v1",
        "ontology_id":profile["ontology_id"],
        "overall":overall,
        "material_digest":material_digest,
        "summary":{"checks":len(checks),"passed":sum(row["outcome"] == "PASS" for row in checks),"flagged":flagged,"blocked":blocked,"nodes":len(node_files),"relations":len(edge_rows),"sources":len(sources_doc["sources"]),"views":len(views_doc["views"]),"residue_entries":len(residue)},
        "checks":checks,
        "claim_ceiling":"Private source-current candidate structure only; no implementation, compiler conformance, admission, parent package PASS, execution, publication, release, deployment, or external-effect authority.",
        "authority_effect":"none"
    }
    return result, json.dumps(result, indent=2, sort_keys=True) + "\n"


result, output = render()
expected_output_sha256 = hashlib.sha256(output.encode()).hexdigest()
receipt_current = sum(
    (row := json.loads(path.read_text())).get("ontology_id") == profile["ontology_id"]
    and row.get("material_digest") == material_digest
    and row.get("validation_output_sha256") == expected_output_sha256
    for path in receipt_paths
) == 1
if not receipt_current:
    next(row for row in checks if row["check_id"] == "receipt-currency")["outcome"] = "BLOCK"
    result, output = render()
sys.stdout.write(output)
overall = result["overall"]
sys.exit(1 if overall == "BLOCK" else 2 if overall == "FLAG" else 0)
