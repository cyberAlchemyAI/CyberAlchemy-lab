"""Replay structural stress examples; this is not a semantic theorem checker."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / "authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json").is_file())
HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads((ROOT / path).read_text())


def binding(path):
    return {"path": path, "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}


def main():
    registry_path = "authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json"
    registry = read(registry_path)
    pairs = 0
    for entry in registry["entries"]:
        assert binding(entry["instance_path"])["sha256"] == entry["instance_sha256"]
        count = len(read(entry["instance_path"])["payload"]["allowed_endpoint_pairs"])
        assert count == entry["exact_endpoint_pair_count"]
        pairs += count
    sources = {registry_path}
    carrier_registry_path = "authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json"
    carrier_registry = read(carrier_registry_path)
    sources.add(carrier_registry_path)
    carrier_records = []
    for kind in ["delegation", "model-instance-binding", "contract"]:
        current = carrier_registry["current_by_identity"]["cal.artifact-type." + kind]
        records = [d for d in carrier_registry["descriptors"] if d["artifact_type_ref"] == current]
        assert len(records) == 1
        record = records[0]
        assert binding(record["schema_path"])["sha256"] == record["schema_sha256"]
        assert binding(record["descriptor_path"])["sha256"] == record["descriptor_sha256"]
        sources.update((record["schema_path"], record["descriptor_path"]))
        carrier_records.append(record)
    cases = []

    def case(name, schema_path, schema, fixture_path, mutate=None, expected=True):
        sources.update((schema_path, fixture_path))
        value = deepcopy(read(fixture_path))
        if mutate:
            mutate(value)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda e: str(list(e.path)))
        accepted = not errors
        assert accepted == expected, (name, [e.message for e in errors])
        cases.append({"name": name, "schema_source": schema_path,
                      "fixture_source": fixture_path, "input": value,
                      "expected_structural_acceptance": expected,
                      "actual_structural_acceptance": accepted,
                      "errors": [e.message for e in errors]})

    base = "authority/relation-kinds/candidates/0006-definition-complete-instances/instances"
    for name, mutations in {
        "acts-for": [
            ("unresolved-delegation", {"delegation_ref": "delegation:missing@v9"}),
            ("uninterpreted-period", {"effective_period": "not-a-period"}),
            ("uninterpreted-revocation", {"revocation_state": "not-a-revocation-state"}),
        ],
        "inherits-contract": [
            ("unresolved-binding", {"binding_ref": "binding:missing@v9"}),
            ("unmatched-contract-version", {"contract_version_ref": "contract:other@v9"}),
        ],
    }.items():
        source = f"{base}/relation-kinds/{name}.json"
        fixture = f"{base}/typed-relations/{name}.json"
        q = read(source)["payload"]["qualifier_contract"]
        schema = {"type": "object", "properties": {"payload": {
            "type": "object", "properties": {"qualifiers": {
                "type": "object", "properties": q["properties"],
                "required": q["required_axes"], "additionalProperties": not q["closed"]}},
            "required": ["qualifiers"]}}, "required": ["payload"]}
        case(f"{name}-qualifier-baseline", source, schema, fixture)
        for label, patch in mutations:
            case(f"{name}-{label}", source, schema, fixture,
                 lambda v, patch=patch: v["payload"]["qualifiers"].update(patch))
        first = q["required_axes"][0]
        case(f"{name}-empty-qualifier-negative-control", source, schema, fixture,
             lambda v, first=first: v["payload"]["qualifiers"].update({first: ""}), False)

    for name in ["delegation", "model-instance-binding", "contract"]:
        source = f"authority/artifact-types/{name}/v1/schema.json"
        fixture = f"authority/artifact-types/{name}/v1/fixtures/valid/record.json"
        schema = read(source)
        case(f"{name}-carrier-baseline", source, schema, fixture)
        if name == "delegation":
            case("delegation-expired-carrier", source, schema, fixture,
                 lambda v: v["payload"].update({"revocation_state": "expired"}))
            case("delegation-different-agent-carrier", source, schema, fixture,
                 lambda v: v["payload"].update({"eligible_agent_ref": "agent-instance:other"}))
        elif name == "model-instance-binding":
            case("binding-different-instance-carrier", source, schema, fixture,
                 lambda v: v.update({"instance_ref": "capability-instance:other"}))
        else:
            case("contract-uninterpreted-overlapping-norms", source, schema, fixture,
                 lambda v: v["payload"].update({"obligation_refs": ["action:publish"],
                                                "prohibition_refs": ["action:publish"]}))

    report = {
        "status": "candidate-structural-audit", "theorems_proved": 0,
        "claim_ceiling": "JSON Schema structural acceptance only; no reference resolution, logical consistency, temporal effectiveness, conformance or authority is established.",
        "qualifier_check_scope": "The two relation qualifier contracts are extracted exactly; these cases do not validate the entire typed-relation envelope.",
        "registry_verified": {"relation_kinds": len(registry["entries"]), "ordered_endpoint_pairs": pairs},
        "selected_current_carrier_records": carrier_records,
        "source_bindings": [binding(p) for p in sorted(sources)],
        "cases": cases,
        "case_count": len(cases),
        "passing_baselines": sum(c["name"].endswith("baseline") for c in cases),
        "accepted_stress_mutations": sum(c["actual_structural_acceptance"] and not c["name"].endswith("baseline") for c in cases),
        "rejected_negative_controls": sum(not c["actual_structural_acceptance"] for c in cases),
    }
    (HERE / "schema-stress-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ["registry_verified", "case_count", "passing_baselines", "accepted_stress_mutations", "rejected_negative_controls", "theorems_proved"]}))


if __name__ == "__main__":
    main()
