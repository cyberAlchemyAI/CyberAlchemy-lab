"""Candidate-local native Python witness for WP-RMT-002 Mapping."""
from __future__ import annotations
import json
import sys
from dataclasses import dataclass

@dataclass(frozen=True)
class MappingFailure:
    code: str
    details: tuple[str, ...]

def evaluate_mapping(descriptor: dict[str, object], observed: dict[str, object]) -> tuple[str, tuple[str, ...]]:
    findings: list[str] = []
    if (observed["source_contract_id"], observed["target_contract_id"]) != (descriptor["source_contract_id"], descriptor["target_contract_id"]): findings.append("RMT_MAP_SOURCE_TARGET_SWAP")
    if observed["direction"] != descriptor["direction"]: findings.append("RMT_MAP_DIRECTION_FLIP")
    if observed["missing_required_fields"]: findings.append("RMT_MAP_MISSING_REQUIRED_FIELD")
    if observed["undeclared_extra_fields"]: findings.append("RMT_MAP_UNDECLARED_EXTRA_FIELD")
    if sorted(observed["observed_correspondence"], key=lambda item: json.dumps(item, sort_keys=True)) != sorted(descriptor["correspondence"], key=lambda item: json.dumps(item, sort_keys=True)): findings.append("RMT_MAP_CORRESPONDENCE_DRIFT")
    if observed["totality"] != descriptor["totality"]: findings.append("RMT_MAP_TOTALITY_OVERCLAIM")
    if observed["coercions"]: findings.append("RMT_MAP_SILENT_COERCION")
    if observed["effect_policy"] != descriptor["effect_policy"] or observed["effects"]: findings.append("RMT_MAP_EFFECT_POLICY_VIOLATION")
    failure = observed["failure_outcome"]
    if failure["status"] != "failure": findings.append("RMT_MAP_FAILURE_AS_SUCCESS")
    elif not failure["code"] or not failure["details"]: findings.append("RMT_MAP_FAILURE_DETAIL_LOSS")
    return ("pass" if not findings else "reject"), tuple(findings)

def evaluate_case(case: dict[str, object]) -> dict[str, object]:
    descriptor=case["descriptor"];observation=case["observation"];verdict,findings=evaluate_mapping(descriptor,observation)
    w3d=case["w3_descriptor"];w3o=case["w3_observation"];w3_findings=[]
    if (w3d["source_contract_id"],w3d["target_contract_id"]) != (w3o["source_contract_id"],w3o["target_contract_id"]): w3_findings.append("ARCH_MAPPING_ENDPOINT_DRIFT")
    if w3d["direction"] != w3o["direction"]: w3_findings.append("ARCH_MAPPING_DIRECTION_DRIFT")
    if w3d["correspondence"] != w3o["observed_correspondence"]: w3_findings.append("ARCH_MAPPING_CORRESPONDENCE_DRIFT")
    if w3d["effect_policy"] == "none" and w3o["effects"]: w3_findings.append("ARCH_MAPPING_EFFECT_UNDECLARED")
    if verdict != "pass" or w3_findings: raise ValueError(f"RMT_MAP_PYTHON_REJECTED:{','.join((*findings,*w3_findings))}")
    portable={"schema_version":"domainspec.mapping-portable-result/v1","result":"pass","meta_type":"Mapping","source_contract_id":descriptor["source_contract_id"],"target_contract_id":descriptor["target_contract_id"],"direction":descriptor["direction"],"correspondence":sorted(f'{item["source"]}->{item["target"]}:{"required" if item["required"] else "optional"}' for item in descriptor["correspondence"]),"totality":descriptor["totality"],"failure_contract_id":descriptor["failure_contract_id"],"structured_failure_preserved":True,"silent_coercion_rejected":True,"effect_policy":descriptor["effect_policy"],"authority_effect":"none"}
    return {"portable":portable,"native_evidence":{"language":"python","mechanism":"frozen-failure-and-explicit-correspondence"}}

if __name__ == "__main__" and sys.argv[1:] == ["--evaluate"]:
    try: print(json.dumps(evaluate_case(json.load(sys.stdin)),sort_keys=True,separators=(",",":")))
    except Exception as error:
        print(str(error),file=sys.stderr);raise SystemExit(1) from error
