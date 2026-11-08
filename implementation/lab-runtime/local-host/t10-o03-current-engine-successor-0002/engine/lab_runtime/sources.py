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


def verify_successor_join(parent, bundle, receipt, decision, previous_state, previous_state_sha,
                          previous_histories, current_state, current_histories, selected_files,
                          current_state_sha, cursor, expected_decision_id, expected_decision_ref):
    """Check the T12 predecessor, decision and two-history join on selected bytes."""
    root = parent.as_posix()
    decision_path = root + "/decision.json"
    authorization_path = root + "/authorization.json"
    response_path = root + "/owner-response.json"
    target = bundle["target"]
    require(bundle["predecessor_state"]["sha256"] == previous_state_sha and
            previous_state["node_id"] != current_state["node_id"],
            "bootstrap predecessor State join differs")
    require(decision["decision_id"] == expected_decision_id and
            decision["decision_ref"] == expected_decision_ref and
            decision["status"] == "owner-admitted" and
            decision["selected_outcome"] == "admit-exact-reviewed-target" and
            decision["target"] == target and
            decision["authorization"] == {"path": authorization_path,
                                            "sha256": selected_files[authorization_path]} and
            decision["response"] == {"path": response_path,
                                       "sha256": selected_files[response_path]} and
            receipt["target_sha256"] == target["sha256"],
            "bootstrap Decision/response/authorization join differs")
    semantic = current_histories["project-semantic-event-history"]["payload"]["events"][-1]
    governance = current_histories["project-governance-event-history"]["payload"]["events"][-1]
    previous_semantic = previous_histories["project-semantic-event-history"]["payload"]["events"]
    previous_governance = previous_histories["project-governance-event-history"]["payload"]["events"]
    require(semantic["cursor"] == governance["governance_cursor"] == cursor and
            semantic["previous_event_digest"] == previous_semantic[-1]["event_digest"] and
            governance["previous_event_digest"] == previous_governance[-1]["event_digest"] and
            semantic["predecessor_state_ref"] == previous_state["node_id"] and
            semantic["predecessor_state_digest"] == previous_state["payload"]["state_digest"] and
            semantic["resulting_state_ref"] == current_state["node_id"] and
            semantic["resulting_state_digest"] == current_state["payload"]["state_digest"] and
            bundle["current_project_state_sha256"] == current_state_sha and
            semantic["record_ref"] == governance["record_ref"] == decision_path and
            governance["decision_ref"] == decision["decision_id"] and
            governance["authorization_ref"] == authorization_path and
            governance["authorization_sha256"] == selected_files[authorization_path] and
            governance["semantic_event_ref"] == {
                "semantic_cursor": cursor, "semantic_event_id": semantic["event_id"],
                "semantic_event_digest": semantic["event_digest"]},
            "bootstrap State/Decision/history join differs")
    materials = {row["path"]: row["sha256"] for row in semantic["material_refs"]}
    require(len(materials) == len(semantic["material_refs"]) and
            all(materials.get(path) == sha for path, sha in (
                (target["path"], target["sha256"]),
                (decision_path, selected_files[decision_path]),
                (authorization_path, selected_files[authorization_path]),
                (response_path, selected_files[response_path]))) and
            set(governance["upstream_governance_evidence_refs"]) == set(materials),
            "bootstrap history material/Decision evidence join differs")


def _capture_parent(repo: Path, profile: dict):
    cap = Capture(repo)
    subjects = {}
    roots = []
    for binding in profile["roots"]:
        bundle = cap.read(binding["path"], binding["sha256"])
        parent = Path(binding["path"]).parent
        for material in bundle["files"]:
            cap.read((parent / material["path"]).as_posix(), material["sha256"])
        roots.append((parent, bundle))
    operational_roots = []
    for binding in profile["operational_roots"]:
        bundle = cap.read(binding["path"], binding["sha256"])
        parent = Path(binding["path"]).parent
        for material in bundle["files"]:
            cap.read((parent / material["path"]).as_posix(), material["sha256"])
        operational_roots.append((parent, bundle))
    # D74's immutable registry postimages remain the vocabulary authority anchor.
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
    def apply_overlay(parent, bundle, *, require_current_carrier=False):
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
                require(carrier in contracts, f"overlay carrier outside admitted contracts: {path}")
                contract = contracts[carrier]
                if require_current_carrier:
                    require(contract["lifecycle_state"] == "admitted-current", f"successor overlay requires current carrier: {path}")
                require(ver not in subjects, f"duplicate overlay version: {ver}")
                require(item.get("identity_ref", identity(doc)) == identity(doc), f"overlay identity mismatch: {path}")
                require(identity(doc) == ver.split("@")[0], f"overlay version identity mismatch: {path}")
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
    for parent, bundle in roots[:-1]:
        apply_overlay(parent, bundle)
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
    for parent, bundle in operational_roots[:1]:
        apply_overlay(parent, bundle, require_current_carrier=True)
    previous_state_path = (operational_roots[0][0] / "instances/project-state.json").as_posix()
    previous_state = cap.documents[previous_state_path]
    previous_histories = {kind: cap.documents[(operational_roots[0][0] / "instances" / (kind + ".json")).as_posix()]
                          for kind in ("project-semantic-event-history", "project-governance-event-history")}
    receipts = profile.get("successor_application_receipts", [])
    require(len(operational_roots) == 3 and len(receipts) == 2,
            "exact two post-D75 bootstrap successor roots required")
    expected_successors = (
        ("lab-repository-owner-bootstrap-v1-0005", "lab-repository-owner-bootstrap-bundle/v1", "bootstrap-0005", 6,
         "CAL-DECISION-LAB-REPOSITORY-OWNER-BOOTSTRAP-0005", "decision:lab-repository-owner-bootstrap-0005"),
        ("lab-specialist-owner-bootstrap-v1-0003", "lab-specialist-owner-bootstrap-bundle/v3", "bootstrap-0003", 7,
         "CAL-DECISION-LAB-SPECIALIST-OWNER-BOOTSTRAP-0003", "decision:lab-specialist-owner-bootstrap-0003"),
    )
    for (parent, bundle), receipt_binding, (directory, schema_name, version_suffix, cursor, decision_id, decision_ref) in zip(
            operational_roots[1:], receipts, expected_successors):
        require(parent.name == directory and bundle["schema_version"] == schema_name and
                bundle["authority_effect"] != "none" and bundle["external_effect_refs"] == [],
                "wrong bounded bootstrap successor bundle")
        require(bundle["predecessor_state"] == {"path": previous_state_path,
                                                 "sha256": cap.materials[previous_state_path]},
                "bootstrap predecessor State bytes differ")
        receipt_path = (parent / "receipts/application.json").as_posix()
        require(receipt_binding["path"] == receipt_path, "wrong bootstrap application receipt")
        receipt = cap.read(receipt_path, receipt_binding["sha256"])
        selected_files = {(parent / item["path"]).as_posix(): item["sha256"] for item in bundle["files"]}
        require(len(selected_files) == len(bundle["files"]), "duplicate bootstrap file")
        instance_files = {name: value for name, value in selected_files.items()
                          if name.startswith((parent / "instances").as_posix() + "/")}
        outputs = {(parent / item["path"]).as_posix(): item["sha256"] for item in receipt["output_hashes"]}
        require(outputs == instance_files and receipt["result"] == "PASS-only-if-current-lookup-committed" and
                receipt["authority_effect"] == "none" and
                receipt["target_sha256"] == bundle["target"]["sha256"] and
                receipt["authorization_sha256"] == selected_files[(parent / "authorization.json").as_posix()] and
                receipt["response_sha256"] == selected_files[(parent / "owner-response.json").as_posix()],
                "bootstrap receipt/output/authorization differs")
        cap.read(bundle["target"]["path"], bundle["target"]["sha256"])
        decision = cap.documents[(parent / "decision.json").as_posix()]
        transaction = cap.documents[(parent / "instances/admission-transaction.json").as_posix()]
        payload = transaction["payload"]
        require(payload["application_state"] == "applied" and payload["atomicity"] == "all-or-nothing" and
                payload["runtime_activations"] == 0 and payload["external_effect_refs"] == [] and
                payload["input_state_ref"] == previous_state["node_id"] and
                payload["input_state_sha256"] == cap.materials[previous_state_path] and
                payload["application_receipt_ref"] == receipt_path and
                payload["authorization_evidence_sha256"] == receipt["authorization_sha256"],
                "bootstrap transaction predecessor or receipt differs")
        targets = {item["target_ref"]: item["target_sha256"] for item in payload["admission_targets"]}
        require(len(targets) == len(payload["admission_targets"]), "duplicate bootstrap admission target")
        current_state_path = (parent / "instances/project-state.json").as_posix()
        require(bundle["current_project_state_ref"] == cap.documents[current_state_path]["node_id"] and
                bundle["current_project_state_sha256"] == cap.materials[current_state_path],
                "bootstrap current State binding differs")
        current_histories = {kind: cap.documents[(parent / "instances" / (kind + ".json")).as_posix()]
                             for kind in previous_histories}
        verify_successor_join(parent, bundle, receipt, decision, previous_state,
                              cap.materials[previous_state_path], previous_histories,
                              cap.documents[current_state_path], current_histories, selected_files,
                              cap.materials[current_state_path], cursor, decision_id, decision_ref)
        for kind, history in current_histories.items():
            earlier = previous_histories[kind]["payload"]["events"]
            events = history["payload"]["events"]
            require(len(events) == cursor and events[:len(earlier)] == earlier,
                    "bootstrap history does not extend exact predecessor")
            require(events[-1]["resulting_state_ref"] == bundle["current_project_state_ref"]
                    if kind == "project-semantic-event-history" else True,
                    "bootstrap semantic history State differs")
        require(current_state_path in instance_files, "bootstrap State absent from selected outputs")
        for path, digest_value in instance_files.items():
            record = cap.documents[path]
            if not isinstance(record, dict) or "node_id" not in record or "kind" not in record:
                continue
            ref = record["node_id"]
            if ref in targets:
                require(targets[ref] == digest_value, "bootstrap target body differs")
                version = ref + "@" + version_suffix
            else:
                version = ref + "@sha256." + digest_value
            matches = [key for key, contract in contracts.items()
                       if record.get(contract["instance_discriminator"]["path"].lstrip("/")) ==
                       contract["instance_discriminator"]["value"]]
            require(len(matches) == 1, "bootstrap instance has no exact carrier: " + path)
            carrier = matches[0]
            schema_binding = contracts[carrier]
            cap.schema(schema_binding["schema_path"], schema_binding["schema_sha256"])
            validate_schema(record, schema_binding["schema_path"], None, cap.documents)
            require(version not in subjects, "duplicate bootstrap instance version")
            for prior in subjects.values():
                if prior["identity"] == ref and prior["effective_state"] == "admitted-current":
                    prior["effective_state"] = "admitted-historical"
            category = "typed-relation" if record["kind"] == "typed-relation" else "artifact-instance"
            subjects[version] = make_record(record, category=category, version=version,
                                            state="admitted-current", path=path, sha=digest_value,
                                            decision=decision["decision_id"], carrier=carrier)
        require({ref for ref in targets} <= {value["identity"] for value in subjects.values()},
                "bootstrap admitted targets missing from projection")
        previous_state_path, previous_state, previous_histories = current_state_path, cap.documents[current_state_path], current_histories
    selection = profile["current_selection"]
    current_path = selection["state_path"]
    require(current_path in cap.documents, "selected State outside frozen admission envelope")
    selected = subjects.get(selection["state_version_ref"])
    require(selected and selected["source"]["path"] == current_path and selected["effective_state"] == "admitted-current",
            "selected State does not match exact current admitted revision")
    selected_roots = [(p, b) for p, b in operational_roots if (p / "bundle.json").as_posix() == selection["bundle_path"]]
    require(len(selected_roots) == 1, "selected current admission root missing or ambiguous")
    parent, current_bundle = selected_roots[0]
    current_decisions = (current_bundle.get("decision_refs") or
                         [cap.documents[(parent / "decision.json").as_posix()]["decision_id"]])
    require(current_bundle["current_project_state_ref"] == selected["identity"] and
            current_bundle["current_project_state_sha256"] == selected["source"]["sha256"], "admission State binding mismatch")
    lookup_binding = selection["lookup"]
    lookup = cap.read(lookup_binding["path"], lookup_binding["sha256"])
    require(lookup["authority_effect"] == "none" and lookup["replay_source"] is False and
            lookup["projection_policy"] == "generated-from-immutable-admission-bundle", "current lookup claims authority")
    require(lookup["admission_bundle"] == {"path": selection["bundle_path"], "sha256": cap.materials[selection["bundle_path"]]} and
            lookup["current_project_state"] == selected["source"] and lookup["identity_ref"] == selected["identity"] and
            lookup["decision_ref"] in current_decisions, "current lookup differs from frozen admission selection")
    # Successor States have different identities; only the selected revision is current.
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
    histories = {k: cap.documents[selection["history_base"] + "/" + k + ".json"] for k in ("project-semantic-event-history", "project-governance-event-history")}
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
    require(state["payload"]["cursor"] == profile["admission_as_of"], "selected admission cursor mismatch")
    for kind, history in histories.items():
        require(len(history["payload"]["events"]) == selection["history_cursor"], "selected history cursor mismatch")
        current = resolve(subjects, history["node_id"])
        require(current["source"]["path"] == selection["history_base"] + "/" + kind + ".json",
                "selected history differs from effective current revision")
        last = history["payload"]["events"][-1]
        if kind == "project-semantic-event-history":
            require(last["resulting_state_ref"] == state["node_id"] and last["resulting_state_digest"] == state["payload"]["state_digest"],
                    "selected history does not end at selected State")
    result = {"schema_version": "lab-runtime-source-snapshot/v1", "profile": profile,
              "materials": cap.materials, "documents": cap.documents, "subjects": subjects, "epoch_inventory": epoch_inventory(repo),
              "contracts": contracts, "relation_contracts": relation_contracts,
              "state": state, "histories": histories, "admission_as_of": profile["admission_as_of"],
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


def capture(repo: Path, profile: dict):
    """Original D75 subjects plus separately qualified candidate mapping inputs."""
    from .endpoint_mapping import mapping_document, MAPPING_PATH, MAPPING_SHA, PROPOSAL_PATH, PROPOSAL_SHA
    result = _capture_parent(repo, profile)
    capture_mapping = Capture(repo)
    value = capture_mapping.read(MAPPING_PATH, MAPPING_SHA)
    require(value == mapping_document(), 'candidate source mapping differs from executable mapping')
    capture_mapping.read(PROPOSAL_PATH, PROPOSAL_SHA)
    for row in value['mappings']:
        for binding in (row['schema_binding'], row['descriptor_binding']):
            capture_mapping.read(binding['path'], binding['sha256'])
    for path, expected in capture_mapping.materials.items():
        require(path not in result['materials'] or result['materials'][path] == expected,
            'candidate mapping input conflicts with inherited admission source')
        result['materials'][path] = expected
    result['documents'].update(capture_mapping.documents)
    result.pop('snapshot_digest')
    result['snapshot_digest'] = digest(result)
    return result
