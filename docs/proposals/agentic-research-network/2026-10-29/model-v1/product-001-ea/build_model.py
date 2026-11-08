"""Build an exact-source candidate EA crosswalk and miner-task catalog."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parent
EA = PACKAGE.parents[5] / "engineer-assessment"

SOURCE_DOCS = (
    "README.md", "product/product.json", "model/PRODUCT-MODEL.md",
    "model/PRODUCT-RESEARCH-TRACE.md", "model/PRODUCT-SUCCESS-METRICS.md",
    "model/ROADMAP.md", "model/WORK-PACK.md", "model/ARCHITECTURE.md",
    "model/EXPERIMENTS.md", "model/lab-records/README.md",
    "model/lab-records/project-identity.json",
    "model/lab-records/product-thesis.json",
    "model/lab-records/relation-proposals.json", "software/README.md",
    "software/DATA-MODEL.md", "software/BUILD-PLAN.md",
    "software/PRIVACY-ACCESS.md", "software/ACCESS-MODEL.md",
    "model/policies/README.md", "runtime/README.md",
    "research/PROGRAM-NOVELTY-METHOD.md",
    "research/PROGRAM-E12-FEASIBILITY-PACK.md",
    "research/PROGRAM-RESEARCH-READOUT-2026-10-27.md",
)

# One candidate work family for every EA Experiment Design. These are Network
# authoring proposals, never an executed EA run, accepted novelty review or offer.
TASK_SPECS = {
    "e01": ("role-construct-map", "permissioned-study", "Role/task map and rival construct hypotheses", "A frozen role, independent SME evidence and a falsifiable task-to-case link", "An independently checked map changes the case/construct decision", [3, 5]),
    "e02": ("case-family-generation", "public-synthetic-first", "Versioned case variant, prior/exposure check and solution paths", "Independent reviewers verify answerability, alternatives, access and mechanism difference", "A controlled contrast finds a useful case-family repair beyond a surface rewrite", [1, 3]),
    "e03": ("scorer-calibration", "public-synthetic-first", "Pinned answer/rubric/evidence-span comparison", "Blind ratings preserve valid alternatives, NA/UNK and transcript uncertainty", "A matched control reduces a predeclared scorer error without new false rejection, or decisively rejects the repair at a bounded scope", [2, 4]),
    "e04": ("one-case-stability", "permissioned-study", "Crossed case/rater/mode variance design and analysis", "A registered design estimates uncertainty for one case per session", "The result resolves whether an exact score/use scope is supportable", [4, 5]),
    "e05a": ("creative-transfer", "permissioned-study", "Session 1 to unseen creative work comparison", "Blind independent work criterion and exposure/fluency rivals", "A controlled transfer result changes the Session 1 claim or case policy", [5]),
    "e05b": ("design-transfer", "permissioned-study", "Session 2 to unseen design work comparison", "Blind design artifact and equal-time comparator", "A controlled transfer result changes the Session 2 claim or rubric", [5]),
    "e05c": ("cooperation-transfer", "permissioned-study", "Session 3 to observed coordination comparison", "Partner-dependent behavior rather than narrative alone", "A controlled result changes the Session 3 claim or case/rubric", [5]),
    "e06": ("prospective-selection", "permissioned-study", "Named-role prospective policy comparison", "Frozen capacity, independent outcomes, two comparators and missingness rule", "A bounded outcome finding changes the Product selection claim", [5, 7]),
    "e07": ("access-and-error", "public-synthetic-first", "Mode/access/error audit and failure reproduction", "Predeclared mode, source and correction checks; human conclusions held", "A reproducible repair reduces a defined access or scoring error", [1, 2, 4, 6, 7]),
    "e08": ("participant-and-customer-value", "public-synthetic-first", "Journey/feedback/cost comparison with explicit payer hypothesis", "A measured outcome uses exact cohort, burden and cost denominators", "A controlled result changes feedback, service scope or Product posture", [1, 2, 7]),
    "e09": ("ai-assistance-provenance", "public-synthetic-first", "Known-assistance and coached-answer stress corpus", "Human false positives and family/mode holdouts are explicit", "A tested rule changes interpretation without penalizing valid human answers", [4]),
    "e10": ("synthetic-answer-augmentation", "public-synthetic-first", "Synthetic answer/scorer challenger against human-only baseline", "No human-validity claim without untouched human answer holdout", "A controlled error reduction changes a scorer-development choice", [2, 4]),
    "e11": ("social-script-vulnerability", "public-synthetic-first", "Session 3 preparation and form contrast", "Observed coordination remains separate from social-script fluency", "A controlled contrast changes Session 3 case or rubric policy", [3, 5]),
    "e12": ("program-novelty-method", "public-synthetic-first", "Source-pinned hypothesis and nearest-prior comparison", "Reviewer arm leakage is controlled or interpretation is explicitly unblinded", "Executed decision value improves at matched source/review cost", [3]),
    "e13": ("human-response-simulator", "public-synthetic-first", "Path/revision simulator against cheap baselines", "Human alignment waits for permissioned untouched person/case/time holdout", "A simulator improves a named case/scorer decision beyond a simpler rival", [3, 4]),
}


def source_paths() -> list[str]:
    carriers = []
    for pattern in ("goal-*.json", "capability-*.json",
                    "research-inquiry*.json", "experiment-design*.json"):
        carriers.extend(f"model/lab-records/{path.name}"
                        for path in (EA / "model/lab-records").glob(pattern))
    carriers.extend(f"model/lab-records/roles/{path.name}"
                    for path in (EA / "model/lab-records/roles").glob("*.json"))
    return sorted(set(SOURCE_DOCS) | set(carriers))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stem_id(design_ref: str) -> str:
    tail = design_ref.split(":")[-1].split("@", 1)[0]
    return "e06" if tail == "e06-compact-selection" else tail.split("-", 1)[0]


def source_manifest() -> dict:
    entries = []
    for rel in source_paths():
        raw = (EA / rel).read_bytes()
        entries.append({"path": rel, "sha256": sha(raw), "bytes": len(raw)})
    cut = sha(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode())
    head = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=EA,
                          capture_output=True, text=True, check=False)
    return {"schema_version": "arn.ea-source-manifest/v1",
            "status": "candidate-source-cut", "authority_effect": "none",
            "source_root_from_package": "../../../../../../engineer-assessment",
            "git_head": head.stdout.strip() if head.returncode == 0 else None,
            "source_cut_sha256": cut, "files": entries,
            "claim_ceiling": "Exact selected file bytes only; no source-owner acceptance or Lab admission."}


def record_family(pattern: str, id_field: str) -> list[dict]:
    out = []
    for path in sorted((EA / "model/lab-records").glob(pattern)):
        record = json.loads(path.read_text())
        out.append({"ref": record[id_field], "source_path":
                    f"model/lab-records/{path.name}", "source_status": record["status"]})
    return out


def crosswalk(manifest: dict) -> dict:
    product = json.loads((EA / "product/product.json").read_text())
    project = json.loads((EA / "model/lab-records/project-identity.json").read_text())
    goals = record_family("goal-*.json", "goal_id")
    caps = record_family("capability-*.json", "node_id")
    inquiries = record_family("research-inquiry*.json", "node_id")
    designs = record_family("experiment-design*.json", "node_id")
    roles = []
    for path in sorted((EA / "model/lab-records/roles").glob("*.json")):
        role = json.loads(path.read_text())
        roles.append({"ref": role["node_id"],
                      "source_path": f"model/lab-records/roles/{path.name}",
                      "source_status": role["status"]})
    proposals = json.loads((EA / "model/lab-records/relation-proposals.json").read_text())
    rows = []
    for design in designs:
        ref = design["ref"]
        links = {"goal_refs": [], "inquiry_refs": [], "capability_refs": []}
        for edge in proposals["proposals"]:
            if edge["source_ref"].split("@", 1)[0] != ref:
                continue
            target = edge["target_ref"].split("@", 1)[0]
            relation = edge["relation_kind"]
            if relation == "relation.contributes-to" and target.startswith("goal:"):
                links["goal_refs"].append(target)
            elif relation == "relation.engages-inquiry":
                links["inquiry_refs"].append(target)
            elif relation == "relation.evaluates" and target.startswith("product-capability:"):
                links["capability_refs"].append(target)
        links = {key: sorted(set(value)) for key, value in links.items()}
        task_key = stem_id(ref)
        rows.append({"experiment_ref": ref, "source_path": design["source_path"],
                     "task_family_ref": f"ea-task:{task_key}",
                     "proposed_lab_links": links,
                     "lab_link_state": "candidate-unapplied",
                     "missing_proposed_links": [key for key, value in links.items()
                                                if not value],
                     "network_capability_hints": [
                         f"product-capability:ea:cap-{n:02d}"
                         for n in TASK_SPECS[task_key][5]],
                     "hint_basis": "author-synthesis-from-EA-EXPERIMENTS-and-PRODUCT-RESEARCH-TRACE"})
    return {"schema_version": "arn.ea-crosswalk/v1",
            "status": "candidate-unadmitted", "authority_effect": "none",
            "source_cut_sha256": manifest["source_cut_sha256"],
            "product_ref": f"{product['product_id']}@{product['version']}",
            "project_ref": project["project_id"],
            "goals": goals, "capabilities": caps, "inquiries": inquiries,
            "roles": roles,
            "experiment_designs": rows,
            "relation_proposal_count": proposals["proposal_count"],
            "claim_ceiling": "Source record identities and candidate links only; hints are synthesis, not Lab relations or observed findings."}


def task_catalog(manifest: dict, cross: dict) -> dict:
    by_task = {row["task_family_ref"].split(":")[-1]: row
               for row in cross["experiment_designs"]}
    tasks = []
    for key, spec in TASK_SPECS.items():
        name, entry, deliverable, execution_gate, advance_test, hints = spec
        source = by_task[key]
        tasks.append({"task_ref": f"ea-task:{key}", "family": name,
                      "experiment_ref": source["experiment_ref"],
                      "entry_class": entry,
                      "candidate_deliverable": deliverable,
                      "w_valid_execution_gate": execution_gate,
                      "u_durable_advance_test": advance_test,
                      "product_capability_hints": source["network_capability_hints"],
                      "offer_state": "no-task-offer",
                      "result_state": "no-ARN-run-or-finding"})
    return {"schema_version": "arn.ea-task-catalog/v1",
            "status": "candidate-unadmitted", "authority_effect": "none",
            "source_cut_sha256": manifest["source_cut_sha256"],
            "award_rule": "W requires valid accepted execution; U requires separate independent durable-advance adjudication; neither is automatic from this catalog.",
            "tasks": tasks,
            "claim_ceiling": "Candidate task families only; no assignment, completed run, W/U issue or Product adoption."}


def reports() -> dict[str, dict]:
    manifest = source_manifest()
    cross = crosswalk(manifest)
    return {"source-manifest.json": manifest, "crosswalk.json": cross,
            "task-catalog.json": task_catalog(manifest, cross)}


if __name__ == "__main__":
    for name, value in reports().items():
        (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
