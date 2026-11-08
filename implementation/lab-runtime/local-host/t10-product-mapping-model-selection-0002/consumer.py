"""One candidate Product Identity/v2 to reference-slice Product join."""

from jsonschema import Draft202012Validator


def need(condition, message):
    if not condition:
        raise ValueError(message)


def consume(payload):
    proposal = payload["proposal"]
    schema = payload["schema"]
    pack = payload["pack"]
    product = payload["product"]
    receipt = payload["receipt"]
    product_binding = payload["product_binding"]
    schema_binding = payload["schema_binding"]
    pack_sha256 = payload["pack_sha256"]

    need(proposal["carrier_ref"] == "cal.artifact-type.product-identity/v2" and
         proposal["endpoint_kind"] == "product" and
         proposal["identity_selector"] == "/product_id" and
         proposal["schema_binding"] == schema_binding and
         proposal["status"] == "candidate-semantic-mapping-not-an-admitted-alias" and
         "exact semantic owner review at R08" in proposal["requires"],
         "selected Product mapping proposal differs")
    Draft202012Validator.check_schema(schema)
    need(not list(Draft202012Validator(schema).iter_errors(product)),
         "selected Product Identity/v2 record invalid")
    need(product["schema_version"] == "cyberalchemy-lab-product-identity/v2" and
         product["status"] == "candidate-unadmitted" and
         product["authority_effect"] == "none", "Product carrier posture differs")

    matches = [row for row in pack["artifacts"] if row["path"] == product_binding["path"]]
    need(len(matches) == 1, "selected Product producer row absent or duplicated")
    row = matches[0]
    need(row["sha256"] == product_binding["sha256"] and
         row["carrier_type_ref"] == proposal["carrier_ref"] and
         row["semantic_kind"] == "product" and
         row["identity_ref"] == product["product_id"] == "product:cyberalchemy-lab" and
         row["version_ref"] == "product:cyberalchemy-lab@candidate.1" and
         product["version"] == "2.0.0-candidate.1" and
         pack["status"] == "candidate-owner-review-open" and
         pack["authority_effect"] == "none", "Product producer/consumer identity differs")
    projects = [other for other in pack["artifacts"] if other["semantic_kind"] == "project"]
    need(len(projects) == 1 and projects[0]["carrier_type_ref"] ==
         "cal.artifact-type.project-identity/v1" and
         projects[0]["identity_ref"] != row["identity_ref"],
         "Product and Project source meanings collapsed")

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
            "selected_carrier_binding": product_binding,
            "identity_selector": proposal["identity_selector"],
            "candidate_endpoint_kind": row["semantic_kind"],
            "candidate_endpoint_ref": row["identity_ref"],
            "candidate_endpoint_version_ref": row["version_ref"],
            "carrier_version": product["version"],
            "project_identity_distinct": True,
            "validation_receipt_result": receipt["result"],
            "general_alias_admitted": False, "instance_admitted": False,
            "authority_effect": "none"}
