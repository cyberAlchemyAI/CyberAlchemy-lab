"""Process-local Agent session state with schema-valid, source-bound views."""
from __future__ import annotations

import copy
import time
import uuid
from datetime import datetime, timezone

from .common import byte_digest, digest, encoded, require
from .graph import query
from .operations import validate_record
from .sources import resolve

TEMPLATES = "authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/"


class Session:
    def __init__(self, store, subject_ref, ttl=900, clock=time.time):
        require(1 <= ttl <= 86400, "session TTL must be 1..86400 seconds")
        self.store, self.clock = store, clock
        self.started, self.deadline = clock(), clock() + ttl
        self.session_id = "agent-session:lab-runtime:" + str(uuid.uuid4())
        self.instance_id = self.session_id.replace("agent-session:", "agent-instance:", 1)
        self.closed = False
        self.memory = []
        data = store.replay(require_current=True)
        self.head = data["head"]["transaction_digest"]
        resolve(data["projection"]["subjects"], subject_ref)
        self.pack = self._build(data, subject_ref)

    def _build(self, data, subject):
        p, config = data["projection"], data["config"]
        graph = query(data, subject, depth=2, max_nodes=60, max_edges=100)
        def template(name):
            record = copy.deepcopy(p["documents"][TEMPLATES + name + ".json"])
            record.update(owner_ref=config["owner_ref"], scope_ref=config["scope_ref"],
                          claim_ceiling="Candidate session projection; no source authority, durable Agent memory, or new-action authorization.")
            if "evidence_refs" in record:
                record["evidence_refs"] = ["runtime-head:" + self.head]
            return record
        event = p["histories"]["project-semantic-event-history"]["payload"]["events"][-1]
        gov = p["histories"]["project-governance-event-history"]["payload"]["events"][-1]
        tuple_ref = {"semantic_event_id": event["event_id"], "semantic_event_digest": event["event_digest"], "semantic_cursor": event["cursor"]}
        event_set_digest = digest(p["histories"])
        ontology = template("ontology")
        ontology.update(node_id="ontology:lab-runtime-session:" + digest(self.session_id),
                        purpose="Provide bounded source-backed context for one ephemeral local Agent session.",
                        boundaries=["Selected query scope only", "Separate source and projection authority", "No durable machine Agent memory"],
                        provenance_refs=[p["state"]["node_id"], "runtime-head:" + self.head], branch_refs=["branch:business", "branch:system", "branch:bridge"],
                        governance_rules=["Exact source bindings", "Closed local/global edge separation", "Expiry and HEAD checks"])
        node_records, by_graph_id = [], {}
        for view in graph["nodes"]:
            key = view["graph_id"]
            rec = template("ontology-node-project")
            rec["node_id"] = "ontology-node:lab-runtime:" + digest(key)
            rec["name"] = key
            payload = rec["payload"]
            source_digest = view.get("source", {}).get("sha256")
            source_digest = source_digest if source_digest and len(source_digest) == 64 else digest(view)
            payload.update(ontology_ref=ontology["node_id"], profile_ref="ontology-profile:lab-operational-runtime/v1",
                           ontology_manifest_ref="runtime-head:" + self.head,
                           node_type_ref="ontology-node-type:" + view["kind"],
                           branch="system" if view["kind"] in ("source-file", "implementation-symbol") else "business",
                           represented_subject={"ref": view["identity"], "kind": view["kind"], "version_ref": key, "digest": source_digest},
                           provenance_refs=["runtime-head:" + self.head])
            payload["semantic_state"].update(label=key, proposition="Source-backed derived representation within the selected session query.",
                                              semantic_components=[view["kind"]], semantic_definition_refs=[], typed_properties={"effective_posture": view})
            payload["governance_binding"].update(semantic_event_ref=tuple_ref, governance_event_refs=[gov["event_id"]],
                                                 evidence_confidence_ref="confidence:source-binding-only", commitment_confidence_ref="confidence:not-evaluated")
            node_records.append(rec)
            by_graph_id[key] = rec["node_id"]
        edge_records = []
        for connection in graph["connections"]:
            rec = template("ontology-edge")
            rec["node_id"] = connection["edge_id"]
            rec["name"] = connection["predicate"]
            payload = rec["payload"]
            payload.update(ontology_ref=ontology["node_id"], relation_type_ref=connection["predicate"],
                           source_node_ref=by_graph_id[connection["source"]], target_node_ref=by_graph_id[connection["target"]],
                           semantic_event_ref=tuple_ref, closed_qualifiers=connection.get("qualifiers", {}))
            if connection["mode"] == "global-typed-relation-projection":
                entry = p["subjects"][connection["relation_subject"]]
                payload.update(edge_mode="global-projection", local_interpretation=None,
                               global_typed_relation_binding={"typed_relation_ref": entry["identity"], "typed_relation_version_ref": entry["version_ref"], "typed_relation_digest": entry["source"]["sha256"]})
            else:
                payload.update(edge_mode="local-interpretation", global_typed_relation_binding=None,
                               local_interpretation={"interpretation": connection["predicate"], "local_scope": config["scope_ref"],
                                                     "owner_ref": config["owner_ref"], "evidence_refs": ["source-evidence:" + digest(connection["evidence"])]})
            edge_records.append(rec)
        ontology.update(node_refs=[r["node_id"] for r in node_records], relation_refs=[r["node_id"] for r in edge_records])
        cut = template("ontology-cut")
        cut["node_id"] = "ontology-cut:lab-runtime:" + digest({"head": self.head, "subject": subject})
        cut_digest = digest({"nodes": node_records, "edges": edge_records})
        cut["payload"].update(ontology_ref=ontology["node_id"], node_refs=ontology["node_refs"], edge_refs=ontology["relation_refs"],
                              semantic_cursor=event["cursor"], source_event_set_digest=event_set_digest, calculated_digest=cut_digest)
        started = datetime.fromtimestamp(self.started, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        expires = datetime.fromtimestamp(self.deadline, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        view = template("ontology-view")
        view["node_id"] = "ontology-view:lab-runtime:" + digest(self.session_id)
        view["payload"].update(ontology_ref=ontology["node_id"], cut_ref=cut["node_id"], cut_digest=cut_digest,
                               selector_ref="runtime-selector:" + subject, consumer_ref=self.session_id,
                               intended_use="Prepare scoped Agent context from exact committed Project State and source-backed ontology projection.",
                               selected_node_refs=ontology["node_refs"], selected_edge_refs=ontology["relation_refs"],
                               freshness_at=started, expires_at=expires, semantic_cursor=event["cursor"], source_event_set_digest=event_set_digest,
                               exclusions=["Unresolved global connections", "Sources outside the query envelope", "New action authority", "Durable Agent memory"])
        context = template("context-view")
        context.update(node_id="context-view:lab-runtime:" + digest(self.session_id), request_ref="context-request:lab-runtime:" + subject,
                       context_ref="context:lab-runtime:" + config["store_id"], context_version_ref="runtime-head:" + self.head,
                       source_epoch=self.head, generated_at=started, expires_at=expires,
                       lineage_refs=[p["state"]["node_id"], cut["node_id"]],
                       limitations=["Bounded selected query", "Source binding is not confidence or authorization", "Invalidated by source drift or changed runtime HEAD"],
                       included_material=[{"source_ref": p["state"]["node_id"], "selector": "whole-record", "sha256": byte_digest(encoded(p["state"]))},
                                          {"source_ref": cut["node_id"], "selector": "whole-cut", "sha256": byte_digest(encoded(cut))}])
        agent = template("agent-instance")
        agent.update(node_id=self.instance_id, name="Ephemeral local context consumer", lifecycle_state="active", relation_refs=[{
            "counterpart_kind": "agent-session", "counterpart_ref": self.session_id, "direction": "source", "relation_kind_ref": "relation.member-of"}])
        agent["payload"].update(session_ref=self.session_id, started_at=started, terminated_at="session-end-or-expiry",
                                accountable_principal_ref=config["owner_ref"], agent_classification_assignment_ref="classification:ephemeral-machine-agent",
                                implementation_ref="implementation:lab-operational-runtime/v1", profile_ref="agent-profile:local-context-consumer", capability_refs=[])
        session = template("agent-session")
        session.update(node_id=self.session_id, name="Local ephemeral Agent session", lifecycle_state="active", relation_refs=[{
            "counterpart_kind": "context-view", "counterpart_ref": context["node_id"], "direction": "source", "relation_kind_ref": "relation.consumes-view"}])
        session["payload"].update(agent_instance_ref=self.instance_id, assignment_ref="runtime-context-request:" + subject,
                                  context_view_ref=context["node_id"], ontology_view_ref=view["node_id"], policy_refs=[config["policy_ref"]],
                                  authority_envelope_ref="runtime-context-read-only:" + config["scope_ref"], input_refs=[subject, p["state"]["node_id"]],
                                  budget_refs=["runtime-session-ttl:" + str(int(self.deadline - self.started))], event_cursor=self.head,
                                  session_memory={"selected_input_refs": [context["node_id"], view["node_id"]], "working_record_refs": [], "unresolved_questions": [], "expires_with_session": True}, termination_state="running")
        all_records = [ontology, *node_records, *edge_records, cut, view, context, agent, session]
        for record in all_records:
            matches = [ref for ref, c in p["contracts"].items() if c["semantic_kind"] == record["kind"] and c["lifecycle_state"] in ("admitted-current", "local-admitted-current")]
            require(len(matches) == 1, "ambiguous session projection carrier")
            validate_record(record, matches[0], p)
        return {"session_id": self.session_id, "head": self.head, "project_state": p["state"], "context_view": context,
                "ontology": ontology, "ontology_nodes": node_records, "ontology_edges": edge_records,
                "ontology_cut": cut, "ontology_view": view, "agent_instance": agent, "agent_session": session,
                "query": graph, "authority_effect": "none", "durable_memory_owner": "Project State and source records",
                "session_memory_owner": self.session_id, "short_memory_persisted": False}

    def context(self):
        require(not self.closed, "session is closed")
        if self.clock() >= self.deadline:
            self.close()
            require(False, "session context expired")
        data = self.store.replay(require_current=True)
        require(data["head"]["transaction_digest"] == self.head, "session context invalidated by changed HEAD; prepare a new session")
        return copy.deepcopy(self.pack)

    def note(self, text):
        self.context()
        require(isinstance(text, str) and 0 < len(text) <= 10000, "session note length must be 1..10000")
        require(len(self.memory) < 100, "session memory limit reached")
        self.memory.append(text)
        return {"session_id": self.session_id, "memory_entries": len(self.memory), "persisted": False}

    def close(self):
        self.memory.clear()
        self.pack = None
        self.closed = True
        return {"session_id": self.session_id, "instance_id": self.instance_id, "termination_state": "closed", "short_memory_erased": True}
