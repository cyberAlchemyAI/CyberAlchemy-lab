"""Validate local proposal identities, references and frozen request source bytes."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[4]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


definitions = load(BASE / "definitions.json")
ontology = load(BASE / "ontology.json")
request = load(BASE / "define-v2/request.json")
governance_request = load(BASE / "define-v2/project-goal-request.json")
product = load(ROOT / "product/products/engineer-assessment/v1/product.json")
project = load(BASE / "lab-records/project-identity.json")
ids = [d["id"] for d in definitions["definitions"]]
assert len(ids) == len(set(ids)) == 16
assert set(ids) == set(ontology["local_meanings"])
assert len(ontology["external_meanings"]) == 10
concepts = [r["concept_id"] for item in (request, governance_request) for r in item["required_concepts"]]
handling = [r["concept_id"] for item in (request, governance_request) for r in item["handling"]]
assert len(request["required_concepts"]) == 24 and len(governance_request["required_concepts"]) == 2
assert len(concepts) == len(set(concepts)) == 26
assert set(concepts) == set(handling) == set(ids) | set(ontology["external_meanings"])
nodes = {n["id"] for n in ontology["node_types"]}
assert len(nodes) == len(ontology["node_types"])
assert all(e["from"] in nodes and e["to"] in nodes for e in ontology["edge_types"])
assert product["product_id"] == ontology["product_id"] == "EA-PRODUCT-001"
assert project["project_id"] == ontology["project_id"] == "project:ea-research-001"
assert product["authority_effect"] == request["authority_effect"] == "none"
assert governance_request["authority_effect"] == "none"
goals = [load(p) for p in sorted((BASE / "lab-records").glob("goal-*.json"))]
assert len(goals) == 6 and len({g["goal_id"] for g in goals}) == 6
inquiry = load(BASE / "lab-records/research-inquiry.json")
design = load(BASE / "lab-records/experiment-design.json")
assert inquiry["project_ref"] == design["project_ref"] == project["project_id"]
assert design["research_refs"] == [inquiry["node_id"] + "@candidate.1"]
assert all(g["authority_effect"] == "none" and g["status"] == "candidate-unadmitted" for g in goals)
assert inquiry["evidence_aggregate_refs"] == design["run_refs"] == []
for item in (request, governance_request):
    for b in item["source_bindings"]:
        path = ROOT / b["path"]
        raw = path.read_bytes()
        assert len(raw) == b["bytes"] and hashlib.sha256(raw).hexdigest() == b["sha256"], b["path"]
for md in list(BASE.glob("*.md")) + list((BASE / "lab-records").glob("*.md")):
    body = md.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", body):
        if target.startswith(("https://", "http://", "#")):
            continue
        assert (md.parent / target).exists(), (md.name, target)
assert "at most ten minutes" in (BASE / "EXPERIMENTS.md").read_text(encoding="utf-8") or "ten-minute" in (BASE / "EXPERIMENTS.md").read_text(encoding="utf-8")
print("PASS: 16 local meanings, 10 reused meanings in two requests, 26 handled concepts, Lab records, ontology edges, exact sources, local links")
