"""Prepare one explicitly scoped technical Lesson plan for a fresh live Session.

The plan is fixture-only evidence for `lesson.select`; it grants no application
or assessment and cannot turn the historical expired Lesson into a current one.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROVIDER = ROOT / "product/lab/release-candidates/v1/interface/source8-session-runtime-v1-action-0148/provider.py"


def prepare(modules, producer, selected):
    spec = importlib.util.spec_from_file_location("_cal_t03_lesson_materials_provider", PROVIDER)
    provider = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(provider)
    P = modules["protocol"]
    materials, plan = provider.lesson_materials(modules, producer, selected)
    lessons = [s for s in selected.view.subjects.values()
               if s["kind"] == "operational-lesson" and
                  s["effective_state"] in producer.reader.adapter.CURRENT]
    if len(lessons) != 1 or len(plan["lessons"]) != 1:
        raise ValueError("exact one-Lesson signed inventory required")
    subject = lessons[0]
    body = subject["record"]
    payload = body["payload"]
    artifact = plan["lessons"][0]["lesson"]
    if (artifact["version_ref"] != subject["version_ref"] or
            artifact["carrier_ref"] != "cal.artifact-type.operational-lesson/v1" or
            payload["applicability"] != "family:api33-native-disposition-review" or
            payload["status"] != "candidate" or
            payload["exclusions"] != ["outside the exact API33 current source and mapped disposition"]):
        raise ValueError("selected technical Lesson semantics differ")
    evidence = ROOT / payload["evidence_refs"][0]
    manifest = producer.reader.HERE / "source-manifest.json"
    listed = {r["path"]: r["sha256"] for r in P.source.parse(manifest.read_bytes())["files"]}
    if (str(evidence.relative_to(ROOT)) not in listed or
            P.source.sha(evidence.read_bytes()) != listed[str(evidence.relative_to(ROOT))]):
        raise ValueError("signed technical review evidence changed")
    mapping = producer.MAPPED.HERE / "packages/0001/mapping.json"
    mapped = P.source.parse(mapping.read_bytes())
    if (mapped["source_cut"] != selected.source_cut or
            not any(r["version_ref"] == artifact["version_ref"] and
                    r["disposition"] == "mapped" for r in mapped["projection_dispositions"])):
        raise ValueError("one Lesson lacks exact current mapping disposition")

    def put(label, value):
        raw = P.compact(value)
        materials[label] = raw
        return P.binding(label, raw)

    review = put("t03:one-lesson-technical-review", {
        "lesson": artifact, "source_cut": selected.source_cut,
        "domain_scope_ref": body["scope_ref"],
        "disposition": "reviewed-for-controlled-use",
        "effective_state": subject["effective_state"],
        "fixture_only": True, "authority_effect": "none"})
    retention = put("t03:one-lesson-retention", {
        "policy_ref": payload["retention_policy_ref"],
        "retain_project_evidence": True, "exclude_session_memory": True,
        "authority_effect": "none"})
    instruction = P.source.parse(materials["fixture:lesson-instructions"])
    rule = put("t03:one-lesson-applicability", {
        "schema_version": "lab-lesson-applicability/v1-candidate",
        "lesson": artifact, "source_cut": selected.source_cut,
        "project_ref": selected.sources.scope_ref,
        "family": payload["applicability"],
        "source_binding": plan["source_binding"],
        "required_instruction_refs": instruction["instruction_refs"],
        "excluded_tags": [],
        "influence_ref": "t03:exact-native-disposition-check-before-query-parity",
        "counterevidence": [], "authority_effect": "none"})
    exclusion = put("t03:one-lesson-exclusion-assessment", {
        "lesson": artifact, "source_cut": selected.source_cut,
        "exclusion_text": payload["exclusions"][0],
        "excluded": False, "authority_effect": "none"})
    plan["family"] = payload["applicability"]
    plan["lessons"][0] = {
        "lesson": artifact, "review_binding": review,
        "review_disposition": "reviewed-for-controlled-use",
        "fixture_only": True,
        "applicability_rule_binding": rule,
        "retention_binding": retention,
        "exclusions": [{"text": payload["exclusions"][0],
                         "excluded": False, "assessment_binding": exclusion}]}
    materials["fixture:lesson-plan"] = P.compact(plan)
    return materials, plan
