"""Cold Method Identity/v1 join to the retained C09 candidate catalog."""

from jsonschema import Draft202012Validator


def need(condition, message):
    if not condition:
        raise ValueError(message)


def one_file(rows, binding):
    matches = [row for row in rows if row["path"] == binding["path"]]
    need(len(matches) == 1 and matches[0]["sha256"] == binding["sha256"],
         "Method producer or consumer file pin differs")


def consume(payload):
    proposal = payload["proposal"]
    schema = payload["schema"]
    method = payload["method"]
    manifest = payload["manifest"]
    receipt = payload["receipt"]
    inspection = payload["inspection"]
    method_binding = payload["method_binding"]
    schema_binding = payload["schema_binding"]
    schema_source_binding = payload["schema_source_binding"]
    inspection_binding = payload["inspection_binding"]
    manifest_sha256 = payload["manifest_sha256"]

    need(proposal["carrier_ref"] == "cal.artifact-type.method/v1" and
         proposal["endpoint_kind"] == "method" and
         proposal["identity_selector"] == "/method_id" and
         proposal["schema_binding"] == schema_binding and
         proposal["status"] == "candidate-carrier-required" and
         "exact relation binding and current eligibility" in proposal["requires"],
         "selected Method mapping proposal differs")
    need(schema_source_binding["sha256"] == schema_binding["sha256"] and
         schema_source_binding["path"] ==
         "implementation/lab-bootstrap/candidates/v1/packages/0004/method/schema.json",
         "Method schema source binding differs")
    Draft202012Validator.check_schema(schema)
    need(not list(Draft202012Validator(schema).iter_errors(method)),
         "selected Method Identity/v1 record invalid")
    need(method["schema_version"] == "cyberalchemy-lab-method/v1-candidate" and
         method["kind"] == "method" and method["status"] == "candidate-unadmitted" and
         method["authority_effect"] == "none" and
         method["method_id"] == "method:lab-governed-state-inspection" and
         method["version"] == "1.0.0-candidate.1", "Method carrier posture differs")

    need(manifest["authority_effect"] == "none" and
         manifest["actual_owner_outcome"] is None and
         receipt["result"] == "PASS" and receipt["authority_effect"] == "none" and
         receipt["actual_owner_outcome"] is None and receipt["external_effects"] == 0 and
         receipt["candidate_manifest_sha256"] == manifest_sha256,
         "retained C09 producer/consumer posture differs")
    one_file(manifest["files"], method_binding)
    one_file(manifest["files"], schema_source_binding)
    one_file(receipt["files"], method_binding)
    one_file(receipt["files"], schema_source_binding)
    one_file(receipt["files"], inspection_binding)
    need(inspection["successful"] is True and inspection["errors"] == 0 and
         inspection["failures"] == 0 and inspection["authority_effect"] == "none",
         "retained C09 inspection differs")
    joined = inspection["observations"]["joined"]
    catalog = joined["candidate_catalog"]
    key = "method:lab-governed-state-inspection@1.0.0-candidate.1"
    method_rows = [entry for entry in catalog.values() if entry["semantic_kind"] == "method"]
    need(len(method_rows) == 1 and catalog[key] is method_rows[0],
         "selected Method catalog row absent or ambiguous")
    row = catalog[key]
    need(row["record"] == method and row["sha256"] == method_binding["sha256"] and
         row["path"] == "method/example.json" and
         row["carrier_ref"] == proposal["carrier_ref"] and
         row["category"] == "artifact-instance" and row["semantic_kind"] == "method" and
         row["identity_selector"] == proposal["identity_selector"] and
         row["identity_transform"] == "none" and
         row["identity_ref"] == method["method_id"] and
         row["version_ref"] == method["method_id"] + "@" + method["version"] and
         row["effective_state"] == "candidate-unadmitted" and
         row["decision_ref"] is None and row["predecessor_ref"] is None and
         joined["actual_owner_outcome"] is None and
         joined["authority_effect"] == "none" and
         joined["real_work_satisfaction_claimed"] is False,
         "Method producer/consumer identity differs")
    return {"selected_carrier_ref": row["carrier_ref"],
            "selected_carrier_binding": method_binding,
            "identity_selector": row["identity_selector"],
            "candidate_endpoint_kind": row["semantic_kind"],
            "candidate_endpoint_ref": row["identity_ref"],
            "candidate_endpoint_version_ref": row["version_ref"],
            "carrier_version": method["version"],
            "inspection_binding": inspection_binding,
            "inspection_join_cold_checked": True,
            "general_alias_admitted": False, "instance_admitted": False,
            "authority_effect": "none"}
