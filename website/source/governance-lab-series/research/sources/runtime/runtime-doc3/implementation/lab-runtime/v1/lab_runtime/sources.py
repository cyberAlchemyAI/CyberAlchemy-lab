"""Frozen source envelope and effective admission resolver; never rewrites sources."""
from __future__ import annotations

import copy
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from .common import RuntimeFault, byte_digest, digest, identity, load, pointer, require, under

BASE = "authority/admissions/governance-transaction-surface/v1"


def epoch_inventory(repo):
    return {"admission_bundles": sorted(p.relative_to(repo).as_posix() for p in repo.glob("authority/admissions/*/v*/bundle.json")),
            "recorded_decisions": sorted(p.relative_to(repo).as_posix() for p in repo.glob("docs/decisions/*/decision.json"))}


def validate_schema(record, path, selector, documents):
    """Resolve only frozen schemas. Remote access is deliberately unavailable."""
    resources = []
    needed = [path]
    seen = set()
    while needed:
        name = needed.pop()
        if name in seen:
            continue
        seen.add(name)
        require(name in documents, f"schema reference outside frozen source envelope: {name}")
        document = documents[name]
        value = copy.deepcopy(document)
        def remove_ids(node):
            if isinstance(node, dict):
                node.pop("$id", None)
                for x in node.values():
                    remove_ids(x)
            elif isinstance(node, list):
                for x in node:
                    remove_ids(x)
        remove_ids(value)
        uri = "https://lab.invalid/" + name
        def dependencies(node):
            if isinstance(node, dict):
                ref = node.get("$ref", "")
                if ref and not ref.startswith("#"):
                    absolute = urlparse(urljoin(uri, ref))
                    require(absolute.scheme == "https" and absolute.netloc == "lab.invalid", "external schema retrieval forbidden")
                    needed.append(unquote(absolute.path.lstrip("/")))
                for child in node.values():
                    dependencies(child)
            elif isinstance(node, list):
                for child in node:
                    dependencies(child)
        dependencies(value)
        value["$id"] = uri
        resources.append((uri, Resource.from_contents(value, default_specification=DRAFT202012)))
    def unknown(uri):
        raise RuntimeFault(f"schema reference outside frozen source envelope: {uri}")
    registry = Registry(retrieve=unknown).with_resources(resources)
    uri = "https://lab.invalid/" + path + (selector or "")
    require(path in documents, f"missing schema: {path}")
    try:
        Draft202012Validator.check_schema(pointer(documents[path], selector))
        errors = sorted(Draft202012Validator({"$ref": uri}, registry=registry).iter_errors(record), key=lambda e: str(e.path))
    except RuntimeFault:
        raise
    except Exception as exc:
        raise RuntimeFault(f"schema resolution failed for {path}: {exc}") from exc
    require(not errors, "schema invalid: " + "; ".join(f"{list(e.path)} {e.message}" for e in errors[:4]))


class Capture:
    def __init__(self, repo):
        self.repo = repo.resolve()
        self.materials = {}
        self.documents = {}

    def read(self, path, expected=None):
        f = under(self.repo, path)
        require(f.is_file(), f"missing source: {path}")
        raw = f.read_bytes()
        sha = byte_digest(raw)
        require(expected is None or expected == sha, f"source digest mismatch: {path}")
        require(path not in self.materials or self.materials[path] == sha, "source changed during capture")
        self.materials[path] = sha
        if path.endswith(".json"):
            self.documents[path] = load(f)
            return self.documents[path]
        return raw

    def schema(self, path, expected=None):
        if path in self.documents:
            self.read(path, expected)
            return
        doc = self.read(path, expected)
        def walk(value):
            if isinstance(value, dict):
                ref = value.get("$ref", "")
                if ref and not ref.startswith("#"):
                    require("://" not in ref, f"remote schema is not allowed: {ref}")
                    f = (self.repo / path).parent / ref.split("#")[0]
                    resolved = f.resolve()
                    require(resolved.is_relative_to(self.repo), "schema dependency outside repository")
                    self.schema(resolved.relative_to(self.repo).as_posix())
                for x in value.values():
                    walk(x)
            elif isinstance(value, list):
                for x in value:
                    walk(x)
        walk(doc)


def make_record(record, *, category, version, state, path, sha, decision, carrier=None):
    return {"identity": identity(record), "version_ref": version, "category": category,
            "kind": record.get("kind", category), "effective_state": state,
            "carrier_ref": carrier, "source": {"path": path, "sha256": sha},
            "decision_ref": decision, "record": record}


def capture(repo: Path, profile: dict):
    cap = Capture(repo)
    subjects = {}
    roots = []
    for binding in profile["roots"]:
        bundle = cap.read(binding["path"], binding["sha256"])
        parent = Path(binding["path"]).parent
        for material in bundle["files"]:
            cap.read((parent / material["path"]).as_posix(), material["sha256"])
        roots.append((parent, bundle))
    # D74's immutable registry postimages are the authority anchor.
    types = cap.documents[BASE + "/registries/artifact-type-registry.json"]
    definitions = cap.documents[BASE + "/registries/definition-registry.json"]
    # The mutable canonical lookup must still match the selected immutable epoch.
    cap.read("authority/definitions/registry.json", cap.materials[BASE + "/registries/definition-registry.json"])
    relations = cap.documents[BASE + "/registries/relation-kind-registry.json"]
    contracts = {}
    for item in types["admitted_contracts"]:
        doc = cap.read(item["artifact_path"], item["artifact_sha256"])
        cap.schema(item["schema_path"], item["schema_sha256"])
        contracts[item["artifact_type_ref"]] = {**item, "artifact": doc}
        ref = item["artifact_type_ref"]
        subjects[ref] = {"identity": doc.get("artifact_type_id", ref), "version_ref": ref,
                         "category": "artifact-type", "kind": "artifact-type", "effective_state": item["lifecycle_state"],
                         "carrier_ref": None, "source": {"path": item["artifact_path"], "sha256": item["artifact_sha256"]},
                         "decision_ref": item["admission_decision_ref"], "record": doc}
    for item in definitions["entries"]:
        doc = cap.read(item["path"], item["sha256"])
        version = item["definition_id"] + "@" + item["version"]
        current = definitions["current_lookup"].get(item["definition_id"])
        state = "admitted-current" if current == version else "admitted-historical"
        subjects[version] = make_record(doc, category="definition", version=version, state=state,
                                        path=item["path"], sha=item["sha256"], decision=item["admission_decision_ref"])
    relation_contracts = {}
    for item in relations["entries"]:
        doc = cap.read(item["instance_path"], item["instance_sha256"])
        relation_contracts[item["relation_kind_ref"]] = doc
        version = item["relation_kind_ref"] + "@" + item["instance_sha256"]
        subjects[version] = make_record(doc, category="relation-kind", version=version, state=item["lifecycle_state"],
                                        path=item["instance_path"], sha=item["instance_sha256"], decision=item["admission_decision_ref"])
    for parent, bundle in roots[:-1]:
        for file, category in [("artifact-instance-admission.json", "artifact-instance"), ("typed-relation-admission.json", "typed-relation")]:
            overlay = cap.documents[(parent / file).as_posix()]
            for item in overlay["entries"]:
                path = item["admitted_instance_path"]
                expected = item.get("admitted_instance_sha256", item.get("sha256"))
                doc = cap.read(path, expected)
                ver = item.get("version_ref", identity(doc) + "@sha256." + cap.materials[path])
                carrier = item.get("carrier_type_ref")
                if not carrier:
                    matches = [ref for ref, c in contracts.items() if doc.get("schema_version") == c.get("instance_discriminator", {}).get("value")]
                    require(len(matches) == 1, f"ambiguous relation carrier: {path}")
                    carrier = matches[0]
                subjects[ver] = make_record(doc, category=category, version=ver, state=item["lifecycle_state"],
                                            path=path, sha=cap.materials[path], decision=overlay["decision_id"], carrier=carrier)
                subjects[ver]["kind"] = item.get("semantic_kind", subjects[ver]["kind"])
                closure = overlay.get("operational_closure", {})
                for facet in ("agent_instance", "agent_session", "assignment", "work"):
                    if closure.get(facet + "_ref") == subjects[ver]["identity"]:
                        subjects[ver]["operational_disposition"] = closure.get(facet + "_disposition", "unknown")
                        subjects[ver]["session_memory_retained"] = closure.get("session_memory_retained", "unknown")
            transitions = overlay.get("predecessor_transitions", []) + ([overlay["predecessor_transition"]] if "predecessor_transition" in overlay else [])
            for transition in transitions:
                for value in subjects.values():
                    if value["identity"] == transition["identity_ref"] and (not transition.get("version_ref") or value["version_ref"] == transition["version_ref"]):
                        value["effective_state"] = transition["to"]
    # D74's exact admitted bundle is also the overlay for its consequences.
    for material in roots[-1][1]["files"]:
        path = BASE + "/" + material["path"]
        if not material["path"].startswith("instances/") or not path.endswith(".json"):
            continue
        doc = cap.documents[path]
        if not doc.get("node_id"):
            continue
        matches = [ref for ref, c in contracts.items() if doc.get("schema_version") == c.get("instance_discriminator", {}).get("value")]
        require(len(matches) == 1, f"no exact current carrier for {path}")
        carrier = matches[0]
        historical = "/project-history/" in path
        version = doc["node_id"] + ("@transaction.0073" if historical else "@transaction.0074")
        if not historical:
            version = profile["consequence_version_bindings"].get(doc["node_id"], version)
        for prior in subjects.values():
            if prior["identity"] == doc["node_id"]:
                prior["effective_state"] = "admitted-historical"
        subjects[version] = make_record(doc, category="typed-relation" if doc["kind"] == "typed-relation" else "artifact-instance",
                                        version=version, state="admitted-historical" if historical else "admitted-current",
                                        path=path, sha=material["sha256"], decision=roots[-1][1]["decision_refs"], carrier=carrier)
    # D74 supersedes the D72 Agent-episode state, even though IDs differ.
    current_path = BASE + "/instances/project-state.json"
    for value in subjects.values():
        if value["kind"] == "project-state" and value["source"]["path"] != current_path:
            value["effective_state"] = "admitted-historical"
    for path, doc in list(cap.documents.items()):
        # Decisions and authorizations referenced by the source envelopes.
        for key in ("authorization",):
            binding = doc.get(key) if isinstance(doc, dict) else None
            if isinstance(binding, dict) and "path" in binding and "sha256" in binding:
                name = binding["path"]
                f = repo / name
                if not f.exists():
                    name = (Path(path).parent / name).as_posix()
                cap.read(name, binding["sha256"])
    # Histories carry exact historical authorization and material references.
    state = cap.documents[current_path]
    histories = {k: cap.documents[BASE + "/instances/" + k + ".json"] for k in ("project-semantic-event-history", "project-governance-event-history")}
    for history in histories.values():
        for event in history["payload"]["events"]:
            for binding in event.get("material_refs", []):
                cap.read(binding["path"], binding["sha256"])
            if "authorization_ref" in event:
                cap.read(event["authorization_ref"], event["authorization_sha256"])
            name = event.get("record_ref")
            if name and (repo / name).is_file():
                cap.read(name)
    for binding in profile["implementation_bindings"]:
        cap.read(binding["path"])
    for name in profile.get("runtime_materials", []):
        cap.read(name)
    validate_histories(histories)
    result = {"schema_version": "lab-runtime-source-snapshot/v1", "profile": profile,
              "materials": cap.materials, "documents": cap.documents, "subjects": subjects, "epoch_inventory": epoch_inventory(repo),
              "contracts": contracts, "relation_contracts": relation_contracts,
              "state": state, "histories": histories, "admission_as_of": "decision:0074",
              "authority_effect": "none", "repository_runtime_activation": "not-observed"}
    result["snapshot_digest"] = digest(result)
    # Independent second read closes changes during collection.
    require(not freshness(repo, result)["changed"], "source drift during capture")
    return result


def freshness(repo, snapshot):
    changed = []
    for path, sha in snapshot["materials"].items():
        f = under(repo, path)
        if not f.is_file() or byte_digest(f.read_bytes()) != sha:
            changed.append(path)
    if snapshot.get("epoch_inventory") != epoch_inventory(repo):
        changed.append("repository-admission-epoch-inventory")
    return {"status": "stale" if changed else "current", "changed": sorted(changed),
            "checked_count": len(snapshot["materials"]), "snapshot_digest": snapshot["snapshot_digest"]}


def resolve(subjects, ref):
    if ref in subjects:
        return subjects[ref]
    matches = [v for v in subjects.values() if v["identity"] == ref and v["effective_state"] in ("admitted-current", "local-admitted-current")]
    require(len(matches) == 1, f"unknown or ambiguous subject/version: {ref}")
    return matches[0]


def validate_histories(histories):
    streams = []
    for kind, history in histories.items():
        events = history["payload"]["events"]
        previous = None
        for i, event in enumerate(events, 1):
            cursor = event.get("cursor", event.get("governance_cursor"))
            require(cursor == i and event["previous_event_digest"] == previous, "history cursor/chain mismatch")
            core = {k: v for k, v in event.items() if k != "event_digest"}
            require(event["event_digest"] == digest(core), "history event digest mismatch")
            previous = event["event_digest"]
        require(history["payload"]["chain_digest"] == digest([e["event_digest"] for e in events]), "history chain digest mismatch")
        require(history["payload"].get("latest_cursor", history["payload"].get("latest_governance_cursor")) == len(events), "history watermark mismatch")
        streams.append(events)
    semantic = histories["project-semantic-event-history"]["payload"]["events"]
    for gov in histories["project-governance-event-history"]["payload"]["events"]:
        link = gov["semantic_event_ref"]
        require(0 < link["semantic_cursor"] <= len(semantic), "governance references missing semantic event")
        event = semantic[link["semantic_cursor"] - 1]
        require(event["event_digest"] == link["semantic_event_digest"] and event["event_id"] == link["semantic_event_id"], "governance/semantic join mismatch")
