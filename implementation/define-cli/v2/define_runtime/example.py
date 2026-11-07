"""An explicitly synthetic incident input, using the real selected Authority source."""
from pathlib import Path
from .exact import binding, decode, encode, read, sha
from .prepare import local_ref


def incident_request(repo):
    repo = Path(repo)
    registry_raw = read(repo / "authority/definitions/registry.json")
    registry = decode(registry_raw)
    entry = next(e for e in registry["entries"] if e["definition_id"] == "cal.definition.authority" and e["definition_id"] + "@" + e["version"] == registry["current_lookup"][e["definition_id"]])
    authority_raw = read(repo / entry["path"]);authority = decode(authority_raw)
    authority_binding = binding(authority_raw, entry["path"])
    value_path = "implementation/define-cli/v2/fixtures/incident-values.json"
    value_raw = read(repo / value_path);values = decode(value_raw);value_binding = binding(value_raw, value_path)
    parameters = [
        {"name": "S", "value_schema": {"type": "string", "minLength": 1}, "required": True, "interpretation": "Exact source snapshot identity."},
        {"name": "A", "value_schema": {"type": "string", "minLength": 1}, "required": True, "interpretation": "Account whose export is being examined."},
        {"name": "F", "value_schema": {"type": "object", "additionalProperties": False, "required": ["region", "status"], "properties": {"region": {"type": "string"}, "status": {"type": "string"}}}, "required": True, "interpretation": "Synthetic fixture filters: region and account status, interpreted within this fixture only."},
        {"name": "E", "value_schema": {"type": "array", "maxItems": 100, "items": {"type": "string"}}, "required": True, "interpretation": "Expected row identities for S, A and F."}]
    meaning = {"meaning_id": "working:incident-complete-export", "revision": 1,
               "statement": "For source snapshot S, account A and filters F, a complete export contains each expected row identity E exactly once and no unexpected row identity.",
               "scope": "Synthetic incident investigation; no claim about a real source system's filter semantics.",
               "boundaries": ["Saving an export is not proof of completeness.", "This criterion grants no data-write or incident-closure permission."],
               "parameters": parameters, "ownership_posture": "Attributable local example; actual semantic owner unselected.",
               "lineage": [value_binding], "status": "local-proposed", "authority_effect": "none"}
    ref = local_ref("incident-example", 1, "working-meaning", 0, meaning)
    mapping = {"S": "snapshot", "A": "account", "F": "filters", "E": "expected_ids"}
    application = {"application_id": "application:incident-1042", "revision": 1, "meaning_ref": ref,
                   "parameter_contract_ref": "parameters:" + meaning["meaning_id"] + "@1", "context_ref": "example:incident-1042", "consumer": "incident-investigator",
                   "intended_use": "inspect-preparation", "bindings": {name: values[key] for name, key in mapping.items()},
                   "value_provenance": [{"parameter": name, "input_id": value_path, "selector": "/" + key, "sha256": sha(encode(values[key]))} for name, key in mapping.items()],
                   "applicability": "established-for-candidate-examination", "binding_gaps": [], "lineage": [value_binding], "authority_effect": "none"}
    assessment = {"assessment_id": "assessment:synthetic-four-of-five", "revision": 1,
                  "application_ref": local_ref("incident-example", 1, "application", 0, application), "input_bindings": [value_binding], "evidence_bindings": [],
                  "method_profile_refs": [], "method_gaps": [{"gap_id": "qualified-method", "reason": "Synthetic authored report; no real Method execution receipt.", "affected_use": "consume-assessment", "continuation": "Obtain qualified producer/method evidence for a real incident."}],
                  "producer": {"identity": "example-author", "execution_posture": "synthetic", "execution_receipt": None},
                  "reported_result": "FAIL", "unevaluable_reason": None, "validation_posture": "unverified-reported",
                  "applicability_limits": ["Four observed rows against five expected rows is an authored fixture report; Define does not execute the comparison."], "lineage": [value_binding]}
    return {"schema_version": "cal.define.prepare-request/v2", "request_id": "incident-example", "request_revision": 1,
            "goal": "Clarify complete export for incident 1042.", "originating_intent": "Investigate missing rows without changing customer data.",
            "context": "Synthetic account acme, fixed snapshot and explicit filters.", "consumer": "incident-investigator", "intended_use": "inspect-preparation",
            "adapter_selection_binding": None, "required_concepts": [
                {"concept_id": "authority", "question": "What governs the investigation?", "scope": "Selected current repository meaning."},
                {"concept_id": "complete-export", "question": "What does complete mean?", "scope": "Local criterion."},
                {"concept_id": "incident-completeness", "question": "Which exact values apply?", "scope": "One synthetic incident."}],
            "handling": [
                {"concept_id": "authority", "disposition": "reuse", "payload": {"meaning_ref": {"kind": "external", "input_id": "authority", "identity": entry["definition_id"], "revision": entry["version"], "carrier_ref": registry["definition_artifact_type_ref"], "selector": "", "sha256": sha(encode(authority))}, "applicability": "Governing meaning and scoped authority remain separate from observations."}},
                {"concept_id": "complete-export", "disposition": "propose", "payload": {"working_meaning": meaning, "applicability": "Bounded synthetic proposal examination."}},
                {"concept_id": "incident-completeness", "disposition": "specialize", "payload": {"mode": "application", "parent_ref": ref, "application_id": application["application_id"], "applicability": "Exact fixture values; meaning unchanged."}}],
            "source_bindings": [authority_binding, value_binding], "evidence_bindings": [], "applications": [application], "assessments": [assessment],
            "materialization_selection": [], "validation_scope": {"required_checks": ["exact bytes", "closed handling", "parameter/value provenance", "preserved assessment limits"], "evidence_scope": "Synthetic preparation and binding checks only.", "claim_ceiling": "No domain execution, real incident conclusion, semantic acceptance or admission."}, "authority_effect": "none"}
