#!/usr/bin/env python3
"""Collect-all validation for the CA2-ROUTE-DEFINE CML-07 Definition Pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import render

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE = Path("/home/vrondelli/projects/domainspec-core")
PACK_PATH = ROOT / "definition-pack.json"
HANDLED_PATH = ROOT / "handled-definitions.json"
RECEIPT = ROOT / "receipts/validation.json"
DEFINE_SCHEMA = SOURCE / "cyberAlchemy-v2/define/schemas/define-package.schema.json"
EXPECTED_DISPOSITIONS = {
    "cal.definition.product": "propose",
    "CAV2-D32": "reuse",
    "CAV2-D20": "reuse",
    "CAV2-D59": "reuse",
    "CAV2-D60": "reuse",
    "cal.definition.identity-relation": "propose",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packed(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def selected(path: Path, item: dict) -> bytes:
    if item["selector_kind"] == "whole-file":
        return path.read_bytes()
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    return "".join(lines[item["start_line"] - 1:item["end_line"]]).encode()


def main() -> int:
    pack = load(PACK_PATH)
    handled = load(HANDLED_PATH)
    schema = load(DEFINE_SCHEMA)
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    producer = pack.get("producer", {})
    check("define-route-selected", producer.get("route_id") == "CA2-ROUTE-DEFINE" and producer.get("package_id") == "cav2.define", producer)
    producer_results = []
    for field, digest_field in (("profile_path", "profile_sha256"), ("contract_path", "contract_sha256"), ("schema_path", "schema_sha256")):
        path = SOURCE / producer[field]
        producer_results.append({"path": producer[field], "expected": producer[digest_field], "actual": sha(path)})
    check("define-package-contract-current", all(x["expected"] == x["actual"] for x in producer_results), producer_results)
    contract_text = (SOURCE / producer["contract_path"]).read_text(encoding="utf-8")
    check("define-result-presentation-policy", "Every Define invocation that reaches a saved-candidate or later state must show" in contract_text and "A path, receipt," in contract_text, producer["contract_path"])

    handled_schema = {"$schema": schema["$schema"], "$ref": "#/$defs/handledDefinitionRegistry", "$defs": schema["$defs"]}
    schema_errors = [e.message for e in jsonschema.Draft202012Validator(handled_schema).iter_errors(handled)]
    check("handled-registry-conforms-to-define-schema", not schema_errors, schema_errors)

    source_results = []
    for item in pack["source_refs"]:
        base = LAB if item["repository"] == "CyberAlchemy-lab" else SOURCE
        path = base / item["path"]
        actual = hashlib.sha256(selected(path, item)).hexdigest()
        source_results.append({"source_id": item["source_id"], "expected": item["sha256"], "actual": actual})
    check("all-exact-sources-current", len(source_results) == 13 and all(x["expected"] == x["actual"] for x in source_results), source_results)

    records = handled["records"]
    record_by_id = {x["record_id"]: x for x in records}
    concept_dispositions = {x["concept_id"]: x["current_disposition"] for x in records}
    check("one-disposition-per-required-concept", len(records) == len(record_by_id) == 6 and concept_dispositions == EXPECTED_DISPOSITIONS and set(pack["required_concept_ids"]) == set(EXPECTED_DISPOSITIONS), concept_dispositions)
    check("pack-record-closure", all(x["handled_definition_ref"] in record_by_id and record_by_id[x["handled_definition_ref"]]["concept_id"] == x["concept_id"] and record_by_id[x["handled_definition_ref"]]["current_disposition"] == x["current_disposition"] for x in pack["concepts"]), [x["handled_definition_ref"] for x in pack["concepts"]])
    flattened = {concept: disposition for disposition, values in pack["disposition_summary"].items() for concept in values}
    check("disposition-summary-current", flattened == EXPECTED_DISPOSITIONS, flattened)

    reused = {x["concept_id"]: x["reuse"] for x in records if x["current_disposition"] == "reuse"}
    expected_reuse = {"CAV2-D20":"ce8dd8633ff5df8fc76b71cf544327209f34a875ed9f93e262469f7c98d8b640","CAV2-D32":"28608be42869eaf5183bd5b4154d9bded38f1a17ad35c11072b9a49f1e4dc348","CAV2-D59":"f9589997351dcd40f5c37f970568aab3a09345c1b8ab6331860d5533d2c7a674","CAV2-D60":"3dc9faeecf91410b8b6a00aa8fd847d474031bd207e91743e72507dee6c526db"}
    check("stable-cav2-definitions-reused-exactly", set(reused) == set(expected_reuse) and all(reused[k]["canonical_definition_id"] == k and reused[k]["source_digest"] == v for k, v in expected_reuse.items()), reused)
    proposals = {x["concept_id"]: x["propose"] for x in records if x["current_disposition"] == "propose"}
    check("missing-source-definitions-proposed", set(proposals) == {"cal.definition.product", "cal.definition.identity-relation"} and all(x["status"] == "candidate" and x["canonical_target"] == "unassigned" for x in proposals.values()), sorted(proposals))

    requirement = {"goal": pack["goal"], "limits": pack["goal_limits"], "required_concept_ids": pack["required_concept_ids"]}
    candidate = {"context_id": pack["context"]["context_id"], "chain_digest": next(x["sha256"] for x in pack["source_refs"] if x["source_id"] == "SRC-LAB-CML07-CHAIN"), "concept_record_ids": [x["handled_definition_ref"] for x in pack["concepts"]]}
    sufficiency = pack["context_sufficiency"]
    check("context-sufficiency-digests", sufficiency["requirement_digest"] == packed(requirement) and sufficiency["candidate_digest"] == packed(candidate), {"expected_requirement": packed(requirement), "actual_requirement": sufficiency["requirement_digest"], "expected_candidate": packed(candidate), "actual_candidate": sufficiency["candidate_digest"]})
    concept_ids = set(EXPECTED_DISPOSITIONS)
    relation_ids = [x["relation_id"] for x in pack["relationships"]]
    check("explicit-relation-closure", len(relation_ids) == len(set(relation_ids)) == 6 and all(x["source_concept_id"] in concept_ids and x["target_concept_id"] in concept_ids for x in pack["relationships"]), relation_ids)
    check("open-questions-preserved", len(pack["open_questions_and_conflicts"]) == 3 and all(x["stop_required_for_candidate_pack"] is False and x["stop_required_for_promotion_or_construction"] is True for x in pack["open_questions_and_conflicts"]), [x["question_id"] for x in pack["open_questions_and_conflicts"]])
    check("candidate-0006-preserved-as-evidence-only", sha(LAB / "authority/definitions/candidates/0006-craft-identity/candidate.json") == "36cdfaf7faf206fdcd387289b66838a46e3fa731b3667eb974c649cd1417cd72" and any("0006" in x for x in pack["blocked_actions"]), sha(LAB / "authority/definitions/candidates/0006-craft-identity/candidate.json"))
    check("live-definition-registry-unchanged", sha(LAB / "authority/definitions/registry.json") == "4210c3f0805a904480e7a0c92c366612e3c3ba563ba354245c6151e4a9d96d3d", sha(LAB / "authority/definitions/registry.json"))
    check("authority-ceiling", pack["authority_effect"] == pack["implementation_effect"] == pack["promotion_effect"] == handled["authority_effect"] == handled["implementation_effect"] == handled["promotion_effect"] == "none", "none")
    expected_projection = render.render(pack, handled)
    check("generated-projection-parity", render.OUTPUT.is_file() and render.OUTPUT.read_text(encoding="utf-8") == expected_projection and expected_projection == render.render(pack, handled), sha(render.OUTPUT) if render.OUTPUT.is_file() else "missing")
    presentation = pack.get("result_presentation", {})
    result_details = []
    for concept in pack["concepts"]:
        record = record_by_id[concept["handled_definition_ref"]]
        visible = f"### {record['term']} (`{record['concept_id']}`)" in expected_projection and f"- Disposition: `{record['current_disposition']}`" in expected_projection
        if record["current_disposition"] == "reuse":
            source_id = render.REUSE_SOURCE_IDS[record["reuse"]["canonical_definition_id"]]
            _, source_text = render.selected_text(pack, source_id)
            quoted_source = "\n".join("> " + line if line else ">" for line in source_text.splitlines())
            visible = visible and quoted_source in expected_projection and record["reuse"]["source_digest"] in expected_projection
        else:
            payload = record[record["current_disposition"]]
            visible = visible and all(payload[field] in expected_projection for field in ("normative_voice", "formal_voice", "plain_language_voice", "domain_context_voice", "boundary"))
        result_details.append({"concept_id": record["concept_id"], "disposition": record["current_disposition"], "full_result_visible": visible})
    check("result-presentation-complete", presentation.get("required") is True and presentation.get("same_interaction") is True and presentation.get("must_show_every_required_concept") is True and presentation.get("path_or_receipt_only_is_sufficient") is False and all(x["full_result_visible"] for x in result_details), result_details)

    failed = [x for x in checks if x["result"] == "FAIL"]
    receipt = {
        "schema_version":"cav2-define-run-validation/v1",
        "subject":pack["pack_id"],
        "result":"PASS" if not failed else "FAIL",
        "authority_effect":"none",
        "checks":checks,
        "summary":{"passed":len(checks)-len(failed),"failed":len(failed),"total":len(checks)},
        "materials":{"definition_pack_sha256":sha(PACK_PATH),"handled_definitions_sha256":sha(HANDLED_PATH),"projection_sha256":sha(render.OUTPUT) if render.OUTPUT.is_file() else None},
        "next_route":"CA2-ROUTE-DEFINITIONS",
        "next_effect_ceiling":"successor Definition candidate only",
        "claim_ceiling":"PASS proves this CML-07 semantic run conforms to the selected CyberAlchemy-v2 Define contract, has exact current inputs, one disposition per concept, displays every resolved definition result, and has no authority effect. It does not accept the pack, promote definitions, make S2 evaluable, or authorize construction."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CML07_DEFINE_RUN={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    if failed:
        for item in failed:
            print(f"{item['check_id']}={item['detail']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
