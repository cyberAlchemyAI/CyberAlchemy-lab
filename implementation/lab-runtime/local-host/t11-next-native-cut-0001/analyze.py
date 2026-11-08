#!/usr/bin/env python3
"""Read-only exact-member closure analysis for the next T11 native fixture cut."""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[4]
MATRIX_PATH = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T11/scope-routing-matrix-0002.json"
MATRIX_SHA = "f74f5c6a85e7eacb420785165fcb8257f2120337b31e482bf6bfb65125575628"
COMMIT = "19d860e719d6d65c05bff74b1c7547b3d48defcc"
TYPE_REGISTRY = "authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json"
TYPE_SHA = "b2a34b5e27d49d94ee41c139ead7f66fcdc5cef163bced4d86d2c2bf03ab3390"
RELATION_REGISTRY = "authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json"
RELATION_SHA = "dab50815e3b8edd2ee0cccabcbd7b925318b86b3df2d92bd3a032c6f9a833b39"
LEGACY = "lab.legacy-source-assertion.cav2-product-thesis"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(value, reason):
    if not value:
        raise ValueError(reason)


def git_json(path, expected=None):
    raw = subprocess.check_output(["git", "show", COMMIT + ":" + path], cwd=ROOT)
    need(expected is None or sha(raw) == expected, "historical input changed: " + path)
    return json.loads(raw)


def main():
    raw = (ROOT / MATRIX_PATH).read_bytes()
    need(sha(raw) == MATRIX_SHA, "selected T11 matrix changed")
    routes = json.loads(raw)["routes"]
    need(len(routes) == 230, "T11 member set changed")
    type_registry = git_json(TYPE_REGISTRY, TYPE_SHA)
    contracts = {row["artifact_type_ref"]: row for row in type_registry["admitted_contracts"]}
    relation_registry = git_json(RELATION_REGISTRY, RELATION_SHA)
    relation_pairs = {}
    for row in relation_registry["entries"]:
        relation_pairs[row["relation_kind_ref"]] = git_json(row["instance_path"])["payload"]["allowed_endpoint_pairs"]
    bodies = {}
    by_scope = defaultdict(list)
    edges = []
    for route in routes:
        binding = route["body_binding"]
        path = Path(binding["path"])
        need(not path.is_absolute() and ".." not in path.parts, "body locator escapes repository")
        body_raw = (ROOT / path).read_bytes()
        need(sha(body_raw) == binding["sha256"], "exact body changed: " + binding["path"])
        body = json.loads(body_raw)
        need(body["node_id"] == route["version_ref"].split("@", 1)[0] and
             body["scope_ref"] == route["body_scope_ref"] and
             route["operation"] == "admit" and route["category"] == "artifact-instance",
             "member identity, scope, or operation changed")
        carrier = contracts.get(route["carrier_ref"])
        need(carrier is not None and carrier["lifecycle_state"] == "admitted-current" and
             carrier["schema_path"] == route["schema_binding"]["path"] and
             carrier["schema_sha256"] == route["schema_binding"]["sha256"] and
             carrier["artifact_path"] == route["descriptor_binding"]["path"] and
             carrier["artifact_sha256"] == route["descriptor_binding"]["sha256"],
             "D75 carrier/schema/descriptor differs")
        for relation in body.get("relation_refs", []):
            other = relation["counterpart_kind"]
            own = carrier["semantic_kind"]
            pair = {"source_kind": own, "target_kind": other} if relation["direction"] == "source" else {
                "source_kind": other, "target_kind": own}
            need(pair in relation_pairs.get(relation["relation_kind_ref"], []),
                 "D75 Relation Kind or endpoint pair absent")
            edges.append({"from": route["version_ref"], "to": relation["counterpart_ref"],
                          "kind": relation["relation_kind_ref"]})
        bodies[route["version_ref"]] = body
        by_scope[route["body_scope_ref"]].append({"version_ref": route["version_ref"],
                                                   "carrier_ref": route["carrier_ref"],
                                                   "size_bytes": len(body_raw)})
    need(len(bodies) == 230 and len(by_scope) == 6, "member identity/scope closure differs")
    legacy_routes = [r for r in routes if r["body_scope_ref"] == LEGACY]
    need(len(legacy_routes) == 220, "legacy group count changed")
    legacy_versions = {r["version_ref"] for r in legacy_routes}
    legacy_ids = {v.split("@", 1)[0] for v in legacy_versions}
    ontology_edges = [b for v, b in bodies.items() if v in legacy_versions and b["kind"] == "ontology-edge"]
    endpoints = [x for b in ontology_edges for x in
                 (b["payload"]["source_node_ref"], b["payload"]["target_node_ref"])]
    need(len(endpoints) == 100 and all(ref in legacy_ids for ref in endpoints),
         "ontology-edge endpoint closure changed")
    generated = [v for v in legacy_versions if bodies[v]["kind"] == "generated-output"]
    sources = [v for v in legacy_versions if bodies[v]["kind"] == "source"]
    need(len(generated) == 1 and len(sources) == 131, "legacy source/output count differs")
    generated_to_sources = {e["to"] for e in edges if e["from"] == generated[0] and e["to"] in sources}
    sources_to_generated = {e["from"] for e in edges if e["from"] in sources and e["to"] == generated[0]}
    need(len(generated_to_sources) == len(sources_to_generated) == 131,
         "source/generated-output mutual refs differ")
    scope_summary = {scope: {"members": len(rows), "body_bytes": sum(r["size_bytes"] for r in rows),
                             "largest_body_bytes": max(r["size_bytes"] for r in rows),
                             "carriers": dict(sorted(Counter(r["carrier_ref"] for r in rows).items()))}
                     for scope, rows in sorted(by_scope.items())}
    need(all(s["largest_body_bytes"] < 1024 * 1024 for s in scope_summary.values()) and
         scope_summary[LEGACY]["body_bytes"] < 16 * 1024 * 1024,
         "original content exceeds native custody byte limits")
    result = {"schema_version": "lab-T11-next-native-cut-analysis/v1",
              "matrix_binding": {"path": MATRIX_PATH, "sha256": MATRIX_SHA},
              "historical_source_commit": COMMIT,
              "type_registry_binding": {"path": TYPE_REGISTRY, "sha256": TYPE_SHA},
              "relation_registry_binding": {"path": RELATION_REGISTRY, "sha256": RELATION_SHA},
              "member_count": len(routes), "scope_summary": scope_summary,
              "embedded_relation_ref_count": len(edges),
              "embedded_relation_kinds": dict(sorted(Counter(e["kind"] for e in edges).items())),
              "declared_relation_pair_mismatches": 0,
              "legacy_ontology_edge_endpoints_internal": len(endpoints),
              "legacy_mutual_generated_output_source_pairs": len(sources),
              "native_custody_material_cap": 64,
              "legacy_members_over_material_cap": len(legacy_routes) - 64,
              "single_atomic_legacy_transaction_requires_explicit_exact_scope_material_cap": True,
              "native_prepare_calls": 0, "native_apply_calls": 0,
              "authority_effect": "none", "T11_complete": False,
              "claim_ceiling": "Static exact-body, D75 carrier, and D74 relation-declaration closure for all 230 candidates; no native effect or current/original admission."}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
