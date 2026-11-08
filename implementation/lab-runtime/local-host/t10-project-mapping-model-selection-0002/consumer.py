"""One candidate Project Identity/v1 to reference-slice Project join."""

from jsonschema import Draft202012Validator


def need(condition, message):
    if not condition:
        raise ValueError(message)


def consume(payload):
    proposal = payload["proposal"]
    schema = payload["schema"]
    pack = payload["pack"]
    project = payload["project"]
    receipt = payload["receipt"]
    project_binding = payload["project_binding"]
    schema_binding = payload["schema_binding"]
    pack_sha256 = payload["pack_sha256"]

    need(proposal["carrier_ref"] == "cal.artifact-type.project-identity/v1" and
         proposal["endpoint_kind"] == "project" and
         proposal["identity_selector"] == "/project_id" and
         proposal["schema_binding"] == schema_binding and
         proposal["status"] == "candidate-semantic-mapping-not-an-admitted-alias" and
         "exact semantic owner review at R08" in proposal["requires"],
         "selected Project mapping proposal differs")
    Draft202012Validator.check_schema(schema)
    need(not list(Draft202012Validator(schema).iter_errors(project)),
         "selected Project Identity/v1 record invalid")
    need(project["schema_version"] == "cyberalchemy-lab-project-identity/v1" and
         project["status"] == "candidate-unadmitted" and
         project["authority_effect"] == "none", "Project carrier posture differs")

    matches = [row for row in pack["artifacts"] if row["path"] == project_binding["path"]]
    need(len(matches) == 1, "selected Project producer row absent or duplicated")
    row = matches[0]
    need(row["sha256"] == project_binding["sha256"] and
         row["carrier_type_ref"] == proposal["carrier_ref"] and
         row["semantic_kind"] == "project" and
         row["identity_ref"] == project["project_id"] == "project:cyberalchemy-v2-to-lab-migration" and
         row["version_ref"] == "project:cyberalchemy-v2-to-lab-migration@candidate.1" and
         project["version"] == "1.0.0-candidate.1" and
         pack["status"] == "candidate-owner-review-open" and
         pack["authority_effect"] == "none", "Project producer/consumer identity differs")
    products = [other for other in pack["artifacts"] if other["semantic_kind"] == "product"]
    need(len(products) == 1 and products[0]["carrier_type_ref"] ==
         "cal.artifact-type.product-identity/v2" and
         products[0]["identity_ref"] != row["identity_ref"],
         "Project and Product source meanings collapsed")

    checks = {check["check_id"]: check for check in receipt["checks"]}
    validated = checks["all-artifacts-use-admitted-current-schemas"]
    selected = [item for item in validated["detail"] if item["identity_ref"] == row["identity_ref"]]
    need(receipt["result"] == "PASS" and receipt["authority_effect"] == "evidence-only" and
         receipt["materials"]["pack_sha256"] == pack_sha256 and
         validated["result"] == "PASS" and len(selected) == 1 and
         selected[0] == {"identity_ref": row["identity_ref"],
                         "carrier_type_ref": row["carrier_type_ref"], "errors": []},
         "retained producer validation differs")
    return {"selected_carrier_ref": row["carrier_type_ref"],
            "selected_carrier_binding": project_binding,
            "identity_selector": proposal["identity_selector"],
            "candidate_endpoint_kind": row["semantic_kind"],
            "candidate_endpoint_ref": row["identity_ref"],
            "candidate_endpoint_version_ref": row["version_ref"],
            "carrier_version": project["version"],
            "product_identity_distinct": True,
            "validation_receipt_result": receipt["result"],
            "general_alias_admitted": False, "instance_admitted": False,
            "authority_effect": "none"}
