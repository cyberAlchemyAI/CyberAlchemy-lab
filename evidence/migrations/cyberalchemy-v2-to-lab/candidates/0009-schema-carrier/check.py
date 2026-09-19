#!/usr/bin/env python3
"""Inspect bounded graph structure without executing or interpreting its occupants."""
import argparse
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from support import ROOT, LAB, PACKAGE, load, sha, need


def read_input(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("Invalid JSON constant: " + value)
    return json.loads(path.read_text(), object_pairs_hook=unique, parse_constant=invalid)


def indexed(records, key):
    result = {x[key]: x for x in records}
    need(len(result) == len(records), "Duplicate " + key)
    return result


def shape(data, filename):
    errors = sorted(x.message for x in Draft202012Validator(load(PACKAGE / filename)).iter_errors(data))
    need(not errors, "; ".join(errors))


def validate_schema(record):
    artifact = load(PACKAGE / "artifact.json")
    need(sha(PACKAGE / "schema.json") == artifact["schema_digest"], "Schema carrier contract changed")
    for ref in artifact["semantic_definition_bindings"] + load(ROOT / "contracts.json")["schemas"]:
        need(sha(LAB / ref["path"]) == ref["sha256"], "Contract or Definition drift: " + ref["path"])
    shape(record, "schema.json")
    need(record["relative_level"]["schema_level_ref"] != record["relative_level"]["occupant_level_ref"], "Schema and occupant levels must be distinguished")
    kinds = set(record["kinds"])
    constraints = indexed(record["constraints"], "kind_ref")
    need(set(constraints) <= kinds, "Constraint references an unknown kind")
    for constraint in constraints.values():
        indexed(constraint["fields"], "name")
    rules = indexed(record["connection_rules"], "relation_ref")
    need(set(rules) == set(record["relations"]), "Every relation requires exactly one connection rule")
    for rule in rules.values():
        need(rule["source_kind"] in kinds and rule["target_kind"] in kinds, "Connection rule references an unknown kind")
        for side in ["source", "target"]:
            low, high = rule[f"min_per_{side}"], rule[f"max_per_{side}"]
            need(type(low) is int and (high is None or type(high) is int), "Multiplicity bounds require JSON integers")
            need(high is None or low <= high, "Reversed multiplicity bounds")
    return kinds, constraints, rules


def check_graph(record, graph):
    kinds, constraints, rules = validate_schema(record)
    shape(graph, "graph.schema.json")
    errors = []
    def issue(code, subject, detail):
        errors.append({"code": code, "subject": subject, "detail": detail})
    if graph["scope_ref"] != record["scope_ref"]:
        issue("scope-mismatch", "graph", "Graph scope differs from the selected schema scope")
    if graph["level_ref"] != record["relative_level"]["occupant_level_ref"]:
        issue("level-mismatch", "graph", "Graph is not at the declared occupant level")
    nodes = {}
    for node in graph["nodes"]:
        ident = node["id"]
        if ident in nodes:
            issue("duplicate-node", ident, "Node identities must be unique"); continue
        nodes[ident] = node
        if node["kind"] not in kinds:
            issue("unknown-kind", ident, node["kind"]); continue
        constraint = constraints.get(node["kind"])
        if constraint is None:
            continue
        fields = {x["name"]: x for x in constraint["fields"]}
        if constraint["closed_fields"]:
            for name in sorted(set(node["fields"]) - set(fields)):
                issue("unexpected-field", ident, name)
        for name, field in fields.items():
            if name not in node["fields"]:
                if field["required"]:
                    issue("missing-field", ident, name)
                continue
            expected = {"string": str, "integer": int, "boolean": bool}[field["value_type"]]
            if type(node["fields"][name]) is not expected:
                issue("wrong-field-type", ident, name + " requires " + field["value_type"])
    edges, valid_edges = set(), []
    for edge in graph["relations"]:
        ident = edge["id"]
        if ident in edges:
            issue("duplicate-relation", ident, "Relation identities must be unique"); continue
        edges.add(ident)
        if edge["kind"] not in rules:
            issue("unknown-relation", ident, edge["kind"]); continue
        if edge["source"] not in nodes or edge["target"] not in nodes:
            issue("missing-endpoint", ident, "Both endpoints must be present"); continue
        rule = rules[edge["kind"]]
        if nodes[edge["source"]]["kind"] != rule["source_kind"] or nodes[edge["target"]]["kind"] != rule["target_kind"]:
            issue("wrong-endpoint-kind", ident, "Endpoint kinds differ from the connection rule"); continue
        valid_edges.append(edge)
    counts = {}
    for edge in valid_edges:
        for side in ["source", "target"]:
            key = (edge["kind"], side, edge[side]); counts[key] = counts.get(key, 0) + 1
    for relation, rule in rules.items():
        for ident, node in nodes.items():
            for side in ["source", "target"]:
                if node["kind"] != rule[side + "_kind"]:
                    continue
                count = counts.get((relation, side, ident), 0)
                low, high = rule["min_per_" + side], rule["max_per_" + side]
                if count < low or (high is not None and count > high):
                    issue("multiplicity", ident, f"{relation} {side}: {count} connections; expected {low}..{high if high is not None else 'unbounded'}")
    return {"schema_version": "cal-schema-graph-conformance/v1", "schema_id": record["schema_id"],
        "conforms": not errors, "errors": errors, "nodes_checked": len(graph["nodes"]), "relations_checked": len(graph["relations"]),
        "assessment_scope": "declared graph structure only", "truth_assessed": False, "authority_effect": "none",
        "occupants_executed": False, "claim_ceiling": "Shape evidence only for this graph, schema scope and relative level; no truth, ownership, promotion or runtime-behavior proof."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", type=Path)
    parser.add_argument("graph", nargs="?", type=Path)
    args = parser.parse_args()
    try:
        record = read_input(args.schema)
        if args.graph:
            result = check_graph(record, read_input(args.graph)); code = 0 if result["conforms"] else 1
        else:
            validate_schema(record); result = {"schema_valid": True, "graph_assessed": False, "authority_effect": "none"}; code = 0
    except (ValueError, OSError) as exc:
        result = {"input_valid": False, "error": str(exc), "authority_effect": "none"}; code = 2
    print(json.dumps(result, indent=2, sort_keys=True)); return code


if __name__ == "__main__":
    raise SystemExit(main())
