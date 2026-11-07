"""Materialize only explicitly selected, complete, source-bound Definition/v2 bodies."""
import importlib.util
from pathlib import Path
from jsonschema import Draft202012Validator
from .exact import binding, bound, decode, encode, pointer, read, require, sha, shape, write_package
from .package import inspect_local
from .prepare import resolve_reference

REPO = Path(__file__).resolve().parents[4]
TYPE = REPO / "authority/artifact-types/definition/v2"


def leaves(value, prefix=""):
    if isinstance(value, dict) and value:
        for key, child in value.items():
            yield from leaves(child, prefix + "/" + key.replace("~", "~0").replace("/", "~1"))
    elif isinstance(value, list) and value:
        for i, child in enumerate(value):yield from leaves(child, prefix + "/" + str(i))
    else:yield prefix


def materialize(directory, destination):
    _, _, _, buffers = inspect_local(directory)
    pack = decode(buffers["pack.json"])
    require(bool(pack["materialization_selection"]), "nothing-selected", "No shared meaning was selected for materialization", 3)
    schema_raw = read(TYPE / "schema.json");generator_raw = read(TYPE / "generator.py")
    schema = decode(schema_raw);validator = Draft202012Validator(schema)
    selected_inputs = {path.removeprefix("inputs/"): raw for path, raw in buffers.items() if path.startswith("inputs/")}
    def source(b):
        raw = selected_inputs.get(b["path"])
        require(raw is not None and sha(raw) == b["sha256"] and len(raw) == b["bytes"], "materialization-source-unavailable", exit_code=3)
        return raw
    output, rows = {}, []
    for index, selection in enumerate(pack["materialization_selection"]):
        require(selection["owner_route"] is not None, "materialization-owner-gap", exit_code=3)
        require(selection["meaning_ref"]["entry_kind"] == "working-meaning", "materialization-subject-kind")
        meaning, _ = resolve_reference(selection["meaning_ref"], {}, {}, pack)
        raw = source(selection["definition_binding"]);body = decode(raw)
        require(validator.is_valid(body), "definition-schema-invalid")
        require(body["voices"]["scientific_formal"]["normative_statement"] == meaning["statement"] and body["boundaries"] == meaning["boundaries"] and body["scope"]["applicability"] == meaning["scope"], "materialization-meaning-mismatch")
        require(body["voices"]["scientific_formal"]["notation"] == [{"symbol": p["name"], "meaning": p["interpretation"]} for p in meaning["parameters"]], "materialization-parameter-mismatch")
        require(body["schema_digest"] == sha(schema_raw) and body["source_direction"]["generator_sha256"] == sha(generator_raw), "materialization-provider-drift", exit_code=3)
        require(body["scope"]["authority_scope_ref"] == selection["authority_scope"], "materialization-scope-mismatch")
        parent = selection["parent_ref"]
        require((selection["identity_intention"] == "successor") == (parent is not None), "materialization-parent-mismatch")
        if parent:require(body["definition_id"] == parent["identity"] and body["version"] != parent["revision"], "successor-identity-mismatch")
        lineage = decode(source(selection["field_lineage_binding"]))
        shape(lineage, ("schema_version", "authored_by", "fields", "claim_ceiling", "authority_effect"))
        require(lineage["schema_version"] == "cal.define.field-lineage/v1" and lineage["authored_by"] and lineage["authority_effect"] == "none", "invalid-field-lineage")
        entries = lineage["fields"]
        require(isinstance(entries, list) and len(entries) <= 1024, "lineage-budget")
        targets = set()
        for entry in entries:
            shape(entry, ("target_selector", "source_binding", "source_selector"))
            require(entry["target_selector"] not in targets, "duplicate-field-lineage")
            targets.add(entry["target_selector"])
            require(pointer(body, entry["target_selector"]) == pointer(decode(source(entry["source_binding"])), entry["source_selector"]), "field-lineage-mismatch")
        require(set(leaves(body)) == targets, "incomplete-field-lineage")
        spec = importlib.util.spec_from_file_location("_define_selected_generator", TYPE / "generator.py")
        module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        prefix = "definitions/" + str(index).zfill(3) + "/"
        output[prefix + "definition.json"] = raw
        output[prefix + "DEFINITION.md"] = module.render(body).encode("utf-8")
        output[prefix + "field-lineage.json"] = source(selection["field_lineage_binding"])
        rows.append({"definition_id": body["definition_id"], "version": body["version"], "body_sha256": sha(raw), "posture": "candidate-only"})
    report = {"schema_version": "cal.define.materialization-report/v1", "definitions": rows,
              "schema_binding": binding(schema_raw, str((TYPE / "schema.json").relative_to(REPO))),
              "generator_binding": binding(generator_raw, str((TYPE / "generator.py").relative_to(REPO))),
              "semantic_fidelity_review": "required-separately", "actual_owner_outcome": None, "authority_effect": "none"}
    output["report.json"] = encode(report);write_package(destination, output)
    return report
