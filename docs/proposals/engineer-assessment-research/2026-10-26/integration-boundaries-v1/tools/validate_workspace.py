"""Check migrated project links and the core model identities."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
model = ROOT / "model"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


product = load(ROOT / "product/product.json")
ontology = load(model / "ontology.json")
definitions = load(model / "definitions.json")
definition_record_index = load(model / "definition-records/index.json")
project = load(model / "lab-records/project-identity.json")
inquiry = load(model / "lab-records/research-inquiry.json")
design = load(model / "lab-records/experiment-design.json")
goals = [load(p) for p in sorted((model / "lab-records").glob("goal-*.json"))]
session_studies = load(ROOT / "research/session-studies.json")
product_research_trace = (model / "PRODUCT-RESEARCH-TRACE.md").read_text(encoding="utf-8")

assert product["product_id"] == ontology["product_id"] == "EA-PRODUCT-001"
assert product["version"] == "0.1.0-candidate.2"
assert project["project_id"] == ontology["project_id"] == inquiry["project_ref"] == design["project_ref"]
assert design["product_evaluation_context"]["product_ref"] == product["product_id"] + "@" + product["version"]
assert len(goals) == 6 and len({g["goal_id"] for g in goals}) == 6
assert len(definitions["definitions"]) == len({d["id"] for d in definitions["definitions"]}) == 86
assert definition_record_index["count"] == 86
assert {entry["definition_id"] for entry in definition_record_index["records"]} == {d["id"] for d in definitions["definitions"]}
assert {d["id"] for d in definitions["definitions"]} == set(ontology["local_meanings"])
assert all(d["statement"] and d["scope"] and d["boundaries"] for d in definitions["definitions"])
assert all(d.get("intuition") for d in definitions["definitions"] if d["id"] in {
    "ea.challenge", "ea.invitation", "ea.study-protocol", "ea.purpose-choice",
    "ea.assessment-attempt", "ea.assignment-manifest", "ea.session-assignment",
    "ea.administration-policy", "ea.session-event", "ea.media-object", "ea.asr-run",
    "ea.transcript-correction", "ea.evidence-span", "ea.adjudication",
    "ea.research-export", "ea.rights-request", "ea.retention-schedule",
    "ea.audit-event", "ea.participant", "ea.identity-vault", "ea.notice-version",
    "ea.outbox-job", "ea.generation-brief", "ea.generation-run",
    "ea.case-candidate", "ea.mechanism-fingerprint", "ea.similarity-assessment",
    "ea.case-trial", "ea.case-review", "ea.case-disposition", "ea.case-rule",
    "ea.case-use-case", "ea.case-operation", "ea.case-workflow",
    "ea.access-permission", "ea.access-policy", "ea.access-decision",
    "ea.exception-grant", "ea.feedback-metric", "ea.product-success-metric"
})
coverage = (ROOT / "software/DEFINITION-COVERAGE.md").read_text(encoding="utf-8")
for name in (
    "participant", "identity_vault", "notice_version", "purpose_choice",
    "study_protocol", "cohort_membership", "assignment_manifest",
    "assessment_attempt", "generation_brief", "generation_run", "case_candidate",
    "mechanism_fingerprint", "similarity_assessment", "case_trial", "case_review",
    "case_evaluation", "case_disposition", "case_exposure", "case_family",
    "case_version", "rubric_version",
    "session_assignment", "session_event", "recovery_decision", "upload_attempt", "media_object", "transcript_version",
    "scoring_run", "criterion_rating", "feedback_report", "criterion_observation",
    "research_export", "rights_request", "retention_schedule", "audit_event", "outbox_job",
    "principal", "role_assignment", "permission_policy_version", "access_decision",
    "exception_grant"
):
    assert "`" + name + "`" in coverage, name
for meaning in re.findall(r"`(ea\.[a-z-]+)`", coverage):
    assert meaning in {d["id"] for d in definitions["definitions"]}, meaning
question_lifecycle = (ROOT / "software/QUESTION-LIFECYCLE.md").read_text(encoding="utf-8")
for prefix, count in (("Q-R", 12), ("Q-U", 8), ("Q-O", 8)):
    assert {f"{prefix}{n:02d}" for n in range(1, count + 1)} == set(re.findall(rf"{prefix}\d{{2}}", question_lifecycle))
assert "Q-W01" in question_lifecycle
access_model = (ROOT / "software/ACCESS-MODEL.md").read_text(encoding="utf-8")
assert {f"P{n:02d}" for n in range(1, 37)} == set(re.findall(r"(?<![A-Z])P\d{2}(?!\d)", access_model))
for definition in definitions["definitions"]:
    if "formal_expression" in definition:
        assert definition["notation"] and definition["intuition"], definition["id"]
assert set(ontology["proposed_external_meanings"]) == {
    "cal.definition.experiment-run", "cal.definition.research-run", "cal.definition.evidence-set",
    "cal.definition.hypothesis", "cal.definition.finding",
    "cal.definition.measurement-result", "cal.definition.decision"
}
node_ids = {node["id"] for node in ontology["node_types"]}
assert len(node_ids) == len(ontology["node_types"])
assert set(ontology["local_meanings"]).issubset({node["meaning"] for node in ontology["node_types"]})
assert all(edge["from"] in node_ids and edge["to"] in node_ids for edge in ontology["edge_types"])
assert len({edge["id"] for edge in ontology["edge_types"]}) == len(ontology["edge_types"])
assert all(record["authority_effect"] == "none" for record in [product, project, inquiry, design, *goals])
for capability_id in re.findall(r"EA-CAP-\d{2}", (model / "PRODUCT-MODEL.md").read_text(encoding="utf-8")):
    assert capability_id in product_research_trace, capability_id
for experiment_id in ("E01", "E02", "E03", "E04", "E05A", "E05B", "E05C", "E06", "E07", "E08", "E09", "E10", "E11"):
    assert experiment_id in product_research_trace, experiment_id
assert session_studies["schema_version"] == "ea.session-study-register/v1"
assert session_studies["status"] == "candidate-designs"
assert session_studies["authority_effect"] == "none"
studies = session_studies["studies"]
assert len(studies) == 3
assert {study["session"] for study in studies} == {1, 2, 3}
assert {study["experiment_id"] for study in studies} == {"EA-E05A", "EA-E05B", "EA-E05C"}
assert all((ROOT / "research" / name).is_file() for name in ("evidence-review.md", "scoring-model.md", "full-protocol.md"))
for study in studies:
    assert (ROOT / study["protocol"]).is_file(), study["protocol"]
    assert all(study[key] for key in ("construct", "independent_criterion", "comparators", "critical_rivals", "falsifier", "preregistration_gaps"))
    assert study["run_refs"] == [], study["experiment_id"]
    protocol_text = (ROOT / study["protocol"]).read_text(encoding="utf-8")
    assert study["experiment_id"].replace("EA-", "") in protocol_text

for md in ROOT.rglob("*.md"):
    if ".git" in md.parts:
        continue
    body = md.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", body):
        if target.startswith(("https://", "http://", "#")):
            continue
        link = target.split("#", 1)[0]
        assert (md.parent / link).exists(), (md.relative_to(ROOT), target)

print("PASS: product/project/goal/experiment identities, 86 definitions, software/question/access coverage, ontology links, three session studies, authority posture and Markdown links")
