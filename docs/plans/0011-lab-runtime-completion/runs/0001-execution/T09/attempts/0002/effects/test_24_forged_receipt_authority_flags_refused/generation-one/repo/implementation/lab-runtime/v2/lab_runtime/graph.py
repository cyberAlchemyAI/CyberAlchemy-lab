"""Derived, bounded graph; global semantics and local trace edges stay separate."""
from __future__ import annotations

from collections import deque

from .common import RuntimeFault, byte_digest, digest, encoded, require
from .operations import validate_relation
from .sources import resolve


def posture(entry):
    r = entry["record"]
    return {"identity": entry["identity"], "version_ref": entry["version_ref"], "category": entry["category"],
            "kind": entry["kind"], "source": entry["source"], "decision_ref": entry["decision_ref"],
            "axes": {"kind": entry["kind"], "status": entry["effective_state"],
                     "evidence_confidence": r.get("evidence_confidence", "not-evaluated"),
                     "commitment": r.get("commitment", "not-evaluated"), "provenance": entry["source"],
                     "owner": r.get("owner_ref", r.get("semantic_owner_ref", r.get("accountable_owner_ref", r.get("owner_route", "unknown")))),
                     "residue": r.get("residue_refs", r.get("typed_residue", []))},
            "state_tracks": {"instance_admission": entry["effective_state"],
                             "domain": r.get("lifecycle_posture", {}).get("status", r.get("lifecycle_state", r.get("status", r.get("record_state", "unknown")))),
                             "contract": entry.get("carrier_ref"), "ontology_representation": "candidate-derived",
                             "runtime": "not-observed", "agent_session": entry.get("operational_disposition", r.get("payload", {}).get("termination_state", "not-applicable"))},
            "challenge_route": r.get("challenge_route", r.get("drift_route", "unknown"))}


def build(data):
    projection = data["projection"]
    nodes = {key: posture(entry) for key, entry in projection["subjects"].items()}
    edges, diagnostics = [], []
    def edge(source, target, predicate, mode, evidence, posture="source-backed"):
        require(source in nodes and target in nodes, "graph edge endpoint missing")
        if mode == "ontology-local":
            signatures = data["baseline"]["profile"]["local_edge_signatures"]
            require(predicate in signatures, "undeclared ontology-local edge predicate")
            def fits(key, expected):
                return key in projection["subjects"] if expected == "subject" else nodes[key]["kind"] == expected
            require(any(fits(source, a) and fits(target, b) for a, b in signatures[predicate]), "undeclared ontology-local endpoint signature")
        core = {"source": source, "target": target, "predicate": predicate, "mode": mode, "evidence": evidence, "posture": posture}
        edges.append({"edge_id": "ontology-edge:" + digest(core), **core})
    for version, entry in sorted(projection["subjects"].items()):
        path = entry["source"]["path"]
        file_id = "source-file:" + entry["source"].get("store_id", "repository") + ":" + path + "#" + entry["source"].get("selector", "whole-file")
        nodes.setdefault(file_id, {"identity": file_id, "kind": "source-file", "source": entry["source"], "posture": "observed-material"})
        edge(version, file_id, "cites-source", "ontology-local", [entry["source"]])
        carrier = entry.get("carrier_ref")
        if carrier in nodes:
            edge(version, carrier, "uses-contract", "ontology-local", [entry["source"], projection["subjects"][carrier]["source"]])
        decisions = entry["decision_ref"] if isinstance(entry["decision_ref"], list) else [entry["decision_ref"]]
        for decision in decisions:
            key = "recorded-decision:" + decision
            sources = []
            for record in projection["subjects"].values():
                if record["kind"] == "decision" and record["identity"] == decision:
                    sources.append(record["source"])
            for name, document in projection["documents"].items():
                if isinstance(document, dict) and document.get("decision_id") == decision:
                    sources.append({"path": name, "sha256": data["baseline"]["materials"].get(name, "unknown")})
            nodes.setdefault(key, {"identity": decision, "kind": "decision", "posture": "recorded-admission-effect",
                                   "sources": sources, "authorization_for_new_action": "not-evaluated"})
            edge(version, key, "admitted-by", "ontology-local", [entry["source"], *sources])
            for tx in data.get("transactions", [])[1:]:
                if any(core["decision_ref"] == decision for core in tx["decision_cores"]):
                    approval_ref = "runtime-approval:" + digest(tx["approval"])
                    binding = {"path": f"transactions/{tx['sequence']:010d}.json", "selector": "/approval",
                               "store_id": data["config"]["store_id"], "sha256": byte_digest(encoded(tx["approval"]))}
                    nodes.setdefault(approval_ref, {"identity": approval_ref, "kind": "source-file", "source": binding,
                                                  "posture": "verified-local-owner-signature", "scope": tx["approval"]["scope_ref"]})
                    edge(key, approval_ref, "authorizes-recorded-effect", "ontology-local", [binding])
            for source in sources:
                if source["path"] not in projection["documents"]:
                    continue
                doc = projection["documents"][source["path"]]
                auth = doc.get("authorization", {})
                if isinstance(auth, dict) and auth.get("path") in data["baseline"]["materials"]:
                    auth_id = "source-file:" + auth["path"]
                    binding = {"path": auth["path"], "sha256": data["baseline"]["materials"][auth["path"]]}
                    nodes.setdefault(auth_id, {"identity": auth_id, "kind": "source-file", "source": binding})
                    edge(key, auth_id, "authorizes-recorded-effect", "ontology-local", [source, binding])
        if entry["category"] == "artifact-type":
            for ref in entry["record"].get("semantic_definition_refs", []):
                if ref in nodes:
                    edge(version, ref, "defined-by", "ontology-local", [entry["source"], projection["subjects"][ref]["source"]])
                else:
                    diagnostics.append({"subject": version, "kind": "unresolved-definition-binding", "reference": ref})
        if entry["category"] == "typed-relation" and entry["effective_state"] in ("admitted-current", "local-admitted-current"):
            try:
                validate_relation(entry["record"], projection)
                payload = entry["record"]["payload"]
                edge(payload["source"]["version_ref"], payload["target"]["version_ref"], payload["relation_kind_ref"],
                     "global-typed-relation-projection", [entry["source"]])
                edges[-1].update(relation_subject=version, qualifiers=payload["qualifiers"], effective_admission=entry["effective_state"])
            except RuntimeFault as exc:
                diagnostics.append({"subject": version, "kind": "unresolved-global-connection", "reason": str(exc),
                                    "recorded_admission": entry["effective_state"], "excluded_from_confirmed_paths": True})
        for binding in data["baseline"]["profile"]["implementation_bindings"]:
            if binding["subject_kind"] == entry["kind"] and (not binding.get("subject_version_ref") or binding["subject_version_ref"] == version):
                key = "implementation-symbol:" + binding["path"] + "#" + binding["selector"]
                evidence = {"path": binding["path"], "selector": binding["selector"], "sha256": data["baseline"]["materials"][binding["path"]]}
                nodes.setdefault(key, {"identity": key, "kind": "implementation-symbol", "source": evidence,
                                       "posture": binding["posture"], "assertion": binding["assertion"], "runtime_conformance": "not-evaluated"})
                edge(version, key, "implemented-by", "ontology-local", [entry["source"], evidence], binding["posture"])
    states = {v["record"]["node_id"]: v for v in projection["subjects"].values() if v["kind"] == "project-state"}
    for event in projection["histories"]["project-semantic-event-history"]["payload"]["events"]:
        a, b = states.get(event["resulting_state_ref"]), states.get(event["predecessor_state_ref"])
        if a and b and a["record"]["payload"]["state_digest"] == event["resulting_state_digest"] and b["record"]["payload"]["state_digest"] == event["predecessor_state_digest"]:
            edge(a["version_ref"], b["version_ref"], "transition-from", "ontology-local",
                 [{"event_id": event["event_id"], "event_digest": event["event_digest"]}])
    edges = list({e["edge_id"]: e for e in edges}.values())
    for key, node in nodes.items():
        node["graph_id"] = key
    return {"nodes": nodes, "edges": sorted(edges, key=lambda e: e["edge_id"]), "diagnostics": diagnostics,
            "authority_effect": "none", "replay_source": False, "graph_digest": digest({"nodes": nodes, "edges": edges})}


def query(data, root="Lifecycle", direction="both", depth=4, max_nodes=100, max_edges=200, predicates=None):
    require(direction in ("incoming", "outgoing", "both"), "unknown traversal direction")
    require(0 <= depth <= 20 and 1 <= max_nodes <= 1000 and 1 <= max_edges <= 4000, "invalid traversal limits")
    graph = build(data)
    stale = data["freshness"]["status"] != "current"
    if stale:
        graph["diagnostics"].append({"subject": root, "kind": "stale-source-envelope", "changed": data["freshness"]["changed"],
                                    "excluded_from_confirmed_paths": True})
        graph["edges"] = []
    selectors = {"Lifecycle": {"project-state", "project-semantic-event-history", "project-governance-event-history", "admission-transaction", "agent-session"},
                 "Authority": {"decision", "authority-boundary", "decision-scope", "policy", "admission-transaction"},
                 "Provenance": {"product-capability", "product-thesis", "intent", "evidence"}}
    if root in selectors:
        initial = sorted(k for k, n in graph["nodes"].items() if n["kind"] in selectors[root] and n.get("axes", {}).get("status") in ("admitted-current", "local-admitted-current"))
    else:
        initial = [root if root in graph["nodes"] else resolve(data["projection"]["subjects"], root)["version_ref"]]
    selected = dict.fromkeys(initial[:max_nodes], 0)
    queue = deque(selected)
    selected_edges = {}
    paths = {k: [] for k in selected}
    omitted = set(initial[max_nodes:])
    adjacency = {}
    for e in graph["edges"]:
        if predicates and e["predicate"] not in predicates:
            continue
        if direction in ("outgoing", "both"):
            adjacency.setdefault(e["source"], []).append((e, e["target"]))
        if direction in ("incoming", "both"):
            adjacency.setdefault(e["target"], []).append((e, e["source"]))
    while queue:
        current = queue.popleft()
        for edge, other in adjacency.get(current, []):
            if edge["edge_id"] in selected_edges:
                continue
            if selected[current] >= depth or len(selected_edges) >= max_edges or (other not in selected and len(selected) >= max_nodes):
                omitted.add(edge["edge_id"])
                continue
            selected_edges[edge["edge_id"]] = edge
            if other not in selected:
                selected[other] = selected[current] + 1
                paths[other] = paths[current] + [edge["edge_id"]]
                queue.append(other)
    diagnostics = [d for d in graph["diagnostics"] if d["subject"] in selected or root in selectors or d["kind"] == "stale-source-envelope"]
    return {"schema_version": "lab-runtime-query-result/v1", "query": {"root": root, "direction": direction, "depth": depth,
            "max_nodes": max_nodes, "max_edges": max_edges, "predicates": predicates},
            "result_status": "partial" if omitted or diagnostics or data["freshness"]["status"] != "current" else "complete",
            "freshness": data["freshness"], "head": data["head"]["transaction_digest"],
            "admission_as_of": data["baseline"]["admission_as_of"], "nodes": [graph["nodes"][k] for k in selected],
            "connections": list(selected_edges.values()), "explanation_paths": paths,
            "gaps": diagnostics, "coverage": {"selected_nodes": len(selected), "selected_edges": len(selected_edges),
            "catalog_subjects": len(data["projection"]["subjects"]), "omitted": sorted(omitted), "truncated": bool(omitted),
            "scope": data["baseline"]["admission_as_of"] + " source envelope plus committed local operational transactions", "unmapped_repository_areas": "outside selected source envelope"},
            "authority_effect": "none", "replay_source": False,
            "claim_ceiling": "Derived evidence paths within selected scope; no new-action permission, domain fulfillment, or live runtime inference."}
