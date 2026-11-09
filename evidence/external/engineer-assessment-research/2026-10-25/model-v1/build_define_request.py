"""Build an exact, task-local Define v2 request from reviewed proposal files.

Run from the repository root with Python 3.11+. No admission or owner action.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[5]
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "implementation/define-cli/v2"))
from define_runtime.exact import binding, decode, encode, sha  # noqa: E402


def build(kind):
    registry = decode((ROOT / "authority/definitions/registry.json").read_bytes(), source=True)
    local_path = (BASE / "definitions.json").relative_to(ROOT).as_posix()
    local_raw = (ROOT / local_path).read_bytes()
    definitions = decode(local_raw)
    local_binding = binding(local_raw, local_path)
    assert kind in ("assessment", "project-goal")
    reused = (["CAV2-D60", "CAV2-D59"] if kind == "project-goal" else [
        "cal.definition.product", "cal.definition.product-thesis", "cal.definition.product-capability",
        "cal.definition.research-inquiry", "cal.definition.experiment-design",
        "cal.definition.measurement-method", "cal.definition.evidence", "cal.definition.authority"])
    concepts, handling, sources = [], [], [local_binding]
    for identity in reused:
        short = identity.split(".")[-1]
        current = registry["current_lookup"][identity]
        entry = next(e for e in registry["entries"] if e["definition_id"] + "@" + e["version"] == current)
        raw = (ROOT / entry["path"]).read_bytes()
        selected = decode(raw, source=True)
        sources.append(binding(raw, entry["path"]))
        concepts.append({"concept_id": identity, "question": "What is the current Lab meaning of " + short + "?", "scope": "Exact current admitted registry definition for this product/research model."})
        handling.append({"concept_id": identity, "disposition": "reuse", "payload": {
            "meaning_ref": {"kind": "external", "input_id": identity, "identity": identity,
                            "revision": entry["version"], "carrier_ref": registry["definition_artifact_type_ref"],
                            "selector": "", "sha256": sha(encode(selected))},
            "applicability": "The Lab meaning structures this candidate product and research model; it grants no effect authority."}})
    for definition in (definitions["definitions"] if kind == "assessment" else []):
        cid = definition["id"]
        concepts.append({"concept_id": cid, "question": "What does " + definition["term"] + " mean for this bounded assessment?", "scope": definition["scope"]})
        meaning = {"meaning_id": "working:" + cid, "revision": 1,
                   "statement": definition["statement"], "scope": definition["scope"],
                   "boundaries": definition["boundaries"], "parameters": definition["parameters"],
                   "ownership_posture": "Task-local proposed meaning; semantic owner principal unassigned.",
                   "lineage": [local_binding], "status": "local-proposed", "authority_effect": "none"}
        handling.append({"concept_id": cid, "disposition": "propose", "payload": {
            "working_meaning": meaning, "applicability": "Candidate assessment/research design only; owner review required before operational use."}})
    for filename in ["ontology.json", "PRODUCT-MODEL.md", "AUTHORITY.md", "RESEARCH.md", "EXPERIMENTS.md", "ARCHITECTURE.md", "ROADMAP.md", "IMPLEMENTATION-LAYERING.md", "WORK-PACK.md"]:
        path = (BASE / filename).relative_to(ROOT).as_posix()
        sources.append(binding((ROOT / path).read_bytes(), path))
    for file in sorted((BASE / "lab-records").glob("*.json")):
        path = file.relative_to(ROOT).as_posix()
        sources.append(binding(file.read_bytes(), path))
    lab_index = BASE / "lab-records/README.md"
    sources.append(binding(lab_index.read_bytes(), lab_index.relative_to(ROOT).as_posix()))
    for path in ["product/products/engineer-assessment/v1/product.json", "docs/proposals/engineer-assessment-research/2026-10-25/PRODUCT-RESEARCH-BRIEF.md"]:
        sources.append(binding((ROOT / path).read_bytes(), path))
    request = {"schema_version": "cal.define.prepare-request/v2", "request_id": "ea-assessment-complete-model-20261025" if kind == "assessment" else "ea-project-goal-20261025", "request_revision": 1,
               "goal": "Prepare exact meanings for the proposed three-session engineer-assessment product and research program." if kind == "assessment" else "Prepare exact Project and Goal meanings for candidate Lab records.",
               "originating_intent": "Test whether creativity, design and cooperation answers of at most ten minutes each can identify strong engineers against independent outcomes and comparators.",
               "context": "Candidate Lab product/research model, not an accepted employment assessment or live Define host use.",
               "consumer": "ea-product-research-design-review", "intended_use": "inspect-preparation", "adapter_selection_binding": None,
               "required_concepts": concepts, "handling": handling, "source_bindings": sources, "evidence_bindings": [],
               "applications": [], "assessments": [], "materialization_selection": [],
               "validation_scope": {"required_checks": ["exact current definition binding", "closed concept handling", "task-local proposal boundaries", "source reconstruction"],
                                    "evidence_scope": "Exact source and structure only; studies and owner decisions are unperformed.",
                                    "claim_ceiling": "Candidate design; no construct validity, selection performance, authority, admission or deployment."},
               "authority_effect": "none"}
    assert len(concepts) == len(handling) == (24 if kind == "assessment" else 2)
    assert len({c["concept_id"] for c in concepts}) == len(concepts)
    return request


if __name__ == "__main__":
    for kind, filename in [("assessment", "request.json"), ("project-goal", "project-goal-request.json")]:
        output = BASE / "define-v2" / filename
        output.parent.mkdir(exist_ok=True)
        output.write_bytes(encode(build(kind)))
        print(output)
