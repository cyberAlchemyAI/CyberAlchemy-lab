"""Closed proposals and deterministic transaction postimages."""
from __future__ import annotations

import copy

from .common import RuntimeFault, byte_digest, digest, encoded, identity, pointer, require
from .sources import make_record, resolve, validate_histories, validate_schema


def endpoint_kind(subject, projection, *, allow_historical=False):
    from .endpoint_mapping import subject_kind
    return subject_kind(subject, projection, allow_historical=allow_historical)


def endpoint_carrier_kind(carrier, projection):
    from .endpoint_mapping import carrier_kind
    return carrier_kind(carrier, projection)

CATEGORIES = ["artifact-instance", "typed-relation", "definition", "artifact-type", "relation-kind"]
OPERATIONS = ["admit", "revise", "withdraw"]
PROPOSAL_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["schema_version", "proposal_id", "expected_head", "source_snapshot_digest", "scope_ref", "policy_ref", "challenge_route", "targets", "schemas"],
    "properties": {
        "schema_version": {"const": "lab-runtime-proposal/v1"},
        **{k: {"type": "string", "minLength": 1} for k in ["proposal_id", "expected_head", "source_snapshot_digest", "scope_ref", "policy_ref", "challenge_route"]},
        "schemas": {"type": "object", "additionalProperties": {"type": "object"}},
        "targets": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False,
            "required": ["category", "operation", "version_ref", "carrier_ref", "record", "predecessor_ref", "decision_ref", "contract"],
            "properties": {
                "category": {"enum": CATEGORIES}, "operation": {"enum": OPERATIONS},
                **{k: {"type": "string", "minLength": 1} for k in ["version_ref", "carrier_ref", "decision_ref"]},
                "predecessor_ref": {"type": ["string", "null"]}, "record": {"type": ["object", "null"]},
                "contract": {"type": ["object", "null"]}
            }
        }}
    }
}


def protocol_check(value, schema):
    from jsonschema import Draft202012Validator
    errors = list(Draft202012Validator(schema).iter_errors(value))
    require(not errors, "protocol invalid: " + "; ".join(e.message for e in errors[:3]))


def current_contract(projection, ref):
    require(ref in projection["contracts"], f"unknown carrier: {ref}")
    contract = projection["contracts"][ref]
    require(contract["lifecycle_state"] in ("admitted-current", "local-admitted-current"), f"historical or withdrawn carrier: {ref}")
    return contract


def validate_relation(record, projection, *, allow_historical=False):
    payload = record["payload"]
    ref = payload["relation_kind_ref"]
    require(ref in projection["relation_contracts"], f"undeclared Relation Kind: {ref}")
    rc = projection["relation_contracts"][ref]["payload"]
    pair = {"source_kind": payload["source"]["kind"], "target_kind": payload["target"]["kind"]}
    require(pair in rc["allowed_endpoint_pairs"], f"undeclared exact endpoint pair: {pair}")
    for endpoint in (payload["source"], payload["target"]):
        subject = resolve(projection["subjects"], endpoint["version_ref"])
        require(subject["identity"] == endpoint["ref"] and endpoint_kind(subject, projection, allow_historical=allow_historical) == endpoint["kind"], "endpoint identity/kind mismatch")
        require(subject["effective_state"] not in ("withdrawn", "local-withdrawn"), "withdrawn endpoint")
    qc = rc["qualifier_contract"]
    protocol_check(payload["qualifiers"], {"type": "object", "additionalProperties": False,
                                           "required": qc["required_axes"], "properties": qc["properties"]})


def validate_record(record, carrier, projection):
    c = current_contract(projection, carrier)
    discriminator = c.get("instance_discriminator")
    if discriminator:
        require(pointer(record, discriminator["path"]) == discriminator["value"], "carrier discriminator mismatch")
    validate_schema(record, c["schema_path"], c.get("schema_selector"), projection["documents"])
    if record.get("kind") == "typed-relation":
        validate_relation(record, projection)
    # Source contract validation constrains any embedded global connection declarations.
    for relation in record.get("relation_refs", []):
        if not isinstance(relation, dict) or "relation_kind_ref" not in relation:
            continue
        require(relation["relation_kind_ref"] in projection["relation_contracts"], "unknown embedded Relation Kind")
        rc = projection["relation_contracts"][relation["relation_kind_ref"]]["payload"]
        own_kind = endpoint_carrier_kind(carrier, projection)
        other = relation["counterpart_kind"]
        pair = {"source_kind": own_kind, "target_kind": other} if relation["direction"] == "source" else {"source_kind": other, "target_kind": own_kind}
        require(pair in rc["allowed_endpoint_pairs"], "embedded connection has undeclared endpoint pair")


def prepare(projection, proposal, head, config, *, verify_base=True):
    protocol_check(proposal, PROPOSAL_SCHEMA)
    if verify_base:
        require(proposal["expected_head"] == head, "stale expected HEAD")
    require(proposal["source_snapshot_digest"] == config["source_snapshot_digest"], "proposal source snapshot mismatch")
    require(proposal["scope_ref"] == config["scope_ref"], "proposal outside provisioned scope")
    require(proposal["policy_ref"] == config["policy_ref"] and proposal["challenge_route"] == config["challenge_route"], "policy/challenge route mismatch")
    post = copy.deepcopy(projection)
    for path, schema in proposal["schemas"].items():
        require(path.startswith("runtime/schemas/") and ".." not in path and path.endswith(".json"), "schema path outside runtime/schemas")
        require(path not in post["documents"] or post["documents"][path] == schema, "immutable schema path conflict")
        post["documents"][path] = schema
    touched = set()
    identities = set()
    existing_decisions = set()
    for entry in projection["subjects"].values():
        refs = entry["decision_ref"] if isinstance(entry["decision_ref"], list) else [entry["decision_ref"]]
        existing_decisions.update(refs)
    # Stage contracts and records together, then validate against the whole proposed closure.
    for target in proposal["targets"]:
        require(target["decision_ref"] not in existing_decisions, "a recorded Decision identity cannot authorize different new effects")
        version = target["version_ref"]
        require(version not in touched, "duplicate transaction target")
        touched.add(version)
        require(target["operation"] in config["allowed_effects"] and target["category"] in config["allowed_categories"], "effect outside provisioned authority")
        prior = None
        if target["operation"] != "admit":
            require(target["predecessor_ref"] is not None, "revision/withdrawal requires exact predecessor")
            prior = resolve(post["subjects"], target["predecessor_ref"])
            require(prior["version_ref"] == target["predecessor_ref"], "predecessor must bind an exact version")
            require(prior["effective_state"] in ("admitted-current", "local-admitted-current"), "predecessor is not current")
            require(prior["category"] == target["category"], "category cannot change across revision")
        else:
            require(target["predecessor_ref"] is None, "admission cannot carry a predecessor")
        if target["operation"] == "withdraw":
            require(target["record"] is None and target["contract"] is None and version == prior["version_ref"], "withdrawal binds the existing exact revision")
            require(prior["kind"] not in ("project-state", "project-semantic-event-history", "project-governance-event-history"), "derived consequences cannot be withdrawn as user targets")
            prior["effective_state"] = "local-withdrawn"
            if target["category"] == "artifact-type":
                post["contracts"][prior["version_ref"]]["lifecycle_state"] = "local-withdrawn"
            if target["category"] == "relation-kind":
                del post["relation_contracts"][prior["identity"]]
            continue
        record = target["record"]
        require(isinstance(record, dict), "admission requires a record")
        if "scope_ref" in record:
            require(record["scope_ref"] == proposal["scope_ref"], "target outside authorized scope")
        carrier = current_contract(post, target["carrier_ref"])
        field = carrier["artifact"].get("instance_contract", {}).get("identity_field")
        category = target["category"]
        kind = carrier["semantic_kind"]
        ident = record["artifact_type_ref"].rsplit("/", 1)[0] if category == "artifact-type" else identity(record, field)
        require(category == {"definition": "definition", "artifact-type": "artifact-type", "relation-kind": "relation-kind", "typed-relation": "typed-relation"}.get(kind, "artifact-instance"), "category/carrier semantic kind mismatch")
        if category == "artifact-type":
            require(version == record["artifact_type_ref"], "artifact contract revision identity mismatch")
        else:
            require(version.startswith(ident + "@") and len(version) > len(ident) + 1, "version must qualify exact identity")
        require(ident not in identities, "multiple targets for one identity")
        identities.add(ident)
        require(version not in post["subjects"], "immutable revision already exists")
        if prior:
            require(prior["identity"] == ident, "revision changes identity")
            prior["effective_state"] = "local-admitted-historical"
        else:
            require(not any(x["identity"] == ident and x["effective_state"] in ("admitted-current", "local-admitted-current") for x in post["subjects"].values()), "identity already current; use revise")
        require(kind not in ("project-state", "project-semantic-event-history", "project-governance-event-history", "admission-transaction"), "runtime consequences are generated, not authored targets")
        entry = {"identity": ident, "version_ref": version, "category": category, "kind": kind,
                 "effective_state": "local-admitted-current", "source": {"path": f"transactions/{proposal['proposal_id']}/{version}", "sha256": byte_digest(encoded(record))},
                 "record": record, "decision_ref": target["decision_ref"], "carrier_ref": target["carrier_ref"]}
        entry.update(identity=ident, kind=kind)
        post["subjects"][version] = entry
        if category == "artifact-type":
            c = target["contract"]
            require(isinstance(c, dict), "new artifact type requires exact schema binding")
            required = {"semantic_kind", "schema_path", "schema_sha256", "schema_selector", "instance_discriminator", "identity_field", "allowed_relation_kinds", "relation_roles"}
            require(set(c) == required, "artifact contract binding must be closed")
            from .protocols import CONTRACT_BINDING_SCHEMA
            protocol_check(c, CONTRACT_BINDING_SCHEMA)
            require(c["schema_path"] in post["documents"], "artifact type schema not in proposed closure")
            require(c["schema_sha256"] == byte_digest(encoded(post["documents"][c["schema_path"]])), "artifact schema digest mismatch")
            require(all(record[k] == c[k] for k in ("semantic_kind", "schema_path", "schema_sha256", "schema_selector")), "descriptor differs from schema package binding")
            require(isinstance(c["identity_field"], str) and c["identity_field"], "explicit instance identity field required")
            require(isinstance(c["allowed_relation_kinds"], list) and isinstance(c["relation_roles"], list), "closed endpoint declaration lists required")
            artifact = {**record, "instance_contract": {"identity_field": c["identity_field"], "instance_discriminator": c["instance_discriminator"]},
                        "allowed_relation_kinds": c["allowed_relation_kinds"], "relation_roles": c["relation_roles"]}
            post["contracts"][version] = {**c, "artifact_type_ref": version, "artifact": artifact, "lifecycle_state": "local-admitted-current"}
            if prior:
                post["contracts"][prior["version_ref"]]["lifecycle_state"] = "local-admitted-historical"
        else:
            require(target["contract"] is None, "schema contract binding only belongs to artifact-type targets")
        if category == "relation-kind":
            require(record["payload"]["relation_kind_id"] == ident, "Relation Kind identity mismatch")
            post["relation_contracts"][ident] = record
    # Check touched records and extension closure after all staging.
    for target in proposal["targets"]:
        if target["operation"] == "withdraw":
            continue
        if target["category"] == "artifact-type":
            require(target["carrier_ref"] == "cal.artifact-type.artifact-type/v3", "type registration requires the declared v3 descriptor slot")
            meta = current_contract(post, target["carrier_ref"])
            validate_schema(target["record"], meta["schema_path"], "#/properties/registered_types/items", post["documents"])
            refs = target["record"]["semantic_definition_refs"]
            require(all(ref in post["subjects"] for ref in refs), "artifact type has an unresolved Definition binding")
        else:
            validate_record(target["record"], target["carrier_ref"], post)
        if target["category"] == "relation-kind":
            record = target["record"]
            for ref, other in projection["relation_contracts"].items():
                if ref != record["node_id"]:
                    require(other["payload"]["axis_id"] != record["payload"]["axis_id"], "new Relation Kind collapses an existing typed axis")
            current_kinds = {endpoint_carrier_kind(ref, post) for ref, c in post["contracts"].items() if c["lifecycle_state"] in ("admitted-current", "local-admitted-current")}
            prior_pairs = projection["relation_contracts"].get(record["node_id"], {}).get("payload", {}).get("allowed_endpoint_pairs", [])
            for pair in record["payload"]["allowed_endpoint_pairs"]:
                require(pair["source_kind"] in current_kinds and pair["target_kind"] in current_kinds, "Relation Kind endpoint has no current carrier")
                if pair in prior_pairs:
                    continue
                # Every affected carrier must permit this relation explicitly.
                for direction, kind, counterpart in (("source", pair["source_kind"], pair["target_kind"]), ("target", pair["target_kind"], pair["source_kind"])):
                    cs = [c for ref, c in post["contracts"].items() if c["lifecycle_state"] in ("admitted-current", "local-admitted-current") and endpoint_carrier_kind(ref, post) == kind]
                    require(any(record["node_id"] in c["artifact"].get("allowed_relation_kinds", []) for c in cs), "Relation Kind extension requires explicit endpoint carrier successor")
                    require(any(any(role.get("relation_kind_ref") == record["node_id"] and role.get("direction") == direction and counterpart in role.get("counterpart_kinds", []) for role in c["artifact"].get("relation_roles", [])) for c in cs), "Relation Kind extension requires exact directional endpoint role declarations")
    # New withdrawals/revisions must not invalidate existing active local relations.
    for entry in post["subjects"].values():
        if entry["category"] == "typed-relation" and entry["effective_state"] in ("admitted-current", "local-admitted-current"):
            old = projection["subjects"].get(entry["version_ref"])
            if old:
                try:
                    validate_relation(old["record"], projection, allow_historical=True)
                except RuntimeFault:
                    # Existing exact-version residue remains a diagnostic; it grants no new connection.
                    continue
            validate_relation(entry["record"], post, allow_historical=old is not None)
        if entry["category"] == "artifact-type" and entry["effective_state"] in ("admitted-current", "local-admitted-current"):
            for ref in entry["record"].get("semantic_definition_refs", []):
                if ref in post["subjects"]:
                    require(post["subjects"][ref]["effective_state"] != "local-withdrawn", "active carrier depends on withdrawn Definition")
    cores = [{"decision_ref": t["decision_ref"], "category": t["category"], "operation": t["operation"],
              "version_ref": t["version_ref"], "target_digest": digest(t)} for t in proposal["targets"]]
    require(len({c["decision_ref"] for c in cores}) == len(cores), "each independent target requires an independent stable Decision core")
    return post, cores


def consequences(projection, proposal, cores, approval, sequence, store_id):
    from .governance import records as governance_records
    old_state = projection["state"]
    state = copy.deepcopy(old_state)
    history = copy.deepcopy(projection["histories"])
    decision_refs = [c["decision_ref"] for c in cores]
    tx_path = f"transactions/{sequence:010d}.json"
    for i, target in enumerate(proposal["targets"]):
        if target["operation"] != "withdraw":
            projection["subjects"][target["version_ref"]]["source"].update(path=tx_path, selector=f"/proposal/targets/{i}/record", store_id=store_id)
    tx_ref = f"admission-transaction:{store_id}:{sequence}"
    state_ref = f"project-state:{store_id}:{sequence}"
    record_ref = f"runtime-transaction:{store_id}:{sequence}"
    state["node_id"] = state_ref
    state["scope_ref"] = proposal["scope_ref"]
    state["name"] = f"Local Project State {store_id} transaction {sequence}"
    state["evidence_refs"] = [record_ref]
    state["claim_ceiling"] = "Local operational successor over a frozen admitted baseline; no repository admission, deployment or external activation."
    state["relation_refs"] = [{"counterpart_kind": "project", "counterpart_ref": proposal.get("project_ref", old_state["payload"]["project_ref"]), "direction": "source", "relation_kind_ref": "relation.member-of"},
                              {"counterpart_kind": "project-state", "counterpart_ref": old_state["node_id"], "direction": "source", "relation_kind_ref": "relation.successor-of"},
                              {"counterpart_kind": "admission-transaction", "counterpart_ref": tx_ref, "direction": "target", "relation_kind_ref": "relation.materializes-consequence"}]
    p = state["payload"]
    p["cursor"] = record_ref
    p["decision_refs"] = old_state["payload"]["decision_refs"] + decision_refs
    p["artifact_refs"] = list(dict.fromkeys(old_state["payload"]["artifact_refs"] + [t["version_ref"] for t in proposal["targets"]] + [record_ref]))
    p["state_digest"] = "sha256:" + digest({"predecessor": old_state["payload"]["state_digest"], "proposal": digest(proposal), "decisions": cores})
    semantic_history = history["project-semantic-event-history"]["payload"]
    gov_history = history["project-governance-event-history"]["payload"]
    cursor = len(semantic_history["events"]) + 1
    semantic = {"event_id": f"project-semantic-event:{store_id}:{sequence}", "cursor": cursor,
                "previous_event_digest": semantic_history["events"][-1]["event_digest"], "change_kind": "local-admission-transaction",
                "predecessor_state_ref": old_state["node_id"], "predecessor_state_digest": old_state["payload"]["state_digest"],
                "resulting_state_ref": state_ref, "resulting_state_digest": p["state_digest"],
                "material_refs": [{"path": t["version_ref"], "sha256": digest(t)} for t in proposal["targets"]],
                "record_ref": record_ref, "semantic_summary": "Applied exact local targets and deterministic Project State consequences."}
    semantic["event_digest"] = digest(semantic)
    gov = {"event_id": f"project-governance-event:{store_id}:{sequence}", "governance_cursor": len(gov_history["events"]) + 1,
           "previous_event_digest": gov_history["events"][-1]["event_digest"],
           "semantic_event_ref": {"semantic_event_id": semantic["event_id"], "semantic_event_digest": semantic["event_digest"], "semantic_cursor": cursor},
           "decision_ref": "decision-bundle:" + digest(cores), "authorization_ref": "runtime-approval:" + digest(approval),
           "authorization_sha256": byte_digest(encoded(approval)), "policy_ref": proposal["policy_ref"],
           "challenge_contract_ref": proposal["challenge_route"], "upstream_governance_evidence_refs": decision_refs,
           "record_ref": record_ref, "governance_summary": "Verified provisioned local owner signature for exact scope, base HEAD and targets."}
    gov["event_digest"] = digest(gov)
    for key, event, watermark in [("project-semantic-event-history", semantic, "latest_cursor"), ("project-governance-event-history", gov, "latest_governance_cursor")]:
        h = history[key]
        h["payload"]["events"].append(event)
        h["payload"][watermark] += 1
        h["payload"]["chain_digest"] = digest([e["event_digest"] for e in h["payload"]["events"]])
        h["evidence_refs"] = [record_ref]
        h["scope_ref"] = proposal["scope_ref"]
        h["claim_ceiling"] = state["claim_ceiling"]
    receipt_ref = "runtime-receipt:" + record_ref
    governance = governance_records(projection, proposal, cores, approval, store_id, sequence)
    transaction = copy.deepcopy(projection["documents"]["authority/admissions/governance-transaction-surface/v1/instances/governance/admission-transaction.json"])
    transaction.update(node_id=tx_ref, name="Local authorized Admission Transaction", scope_ref=proposal["scope_ref"],
                       evidence_refs=[gov["authorization_ref"]], claim_ceiling=state["claim_ceiling"], relation_refs=[{
                           "counterpart_kind": "policy", "counterpart_ref": proposal["policy_ref"], "direction": "source", "relation_kind_ref": "relation.governed-by"}])
    registries = {"coverage": "authored-targets-and-pre-consequence-subjects", "subjects": {k: {x: v[x] for x in ("identity", "version_ref", "category", "kind", "effective_state", "source", "decision_ref")} for k, v in projection["subjects"].items()},
                  "contracts": projection["contracts"], "relation_contracts": projection["relation_contracts"]}
    generated = copy.deepcopy(projection["documents"]["authority/admissions/governance-transaction-surface/v1/instances/generated-output.json"])
    generated.update(node_id=f"generated-output:{store_id}:{sequence}", name="Local registry and index projection", scope_ref=proposal["scope_ref"],
                     evidence_refs=[record_ref], claim_ceiling=state["claim_ceiling"] + " This output indexes authored targets and pre-consequence subjects; the complete current catalog is replay-derived.")
    generated["relation_refs"][0]["counterpart_ref"] = tx_ref
    generated["payload"].update(generator_ref="implementation:lab-operational-runtime/v1", input_refs=[t["version_ref"] for t in proposal["targets"]],
                                output_digest="sha256:" + digest(registries), reproducibility_receipt_ref=receipt_ref)
    transaction["payload"].update(
        decision_bundle_ref=gov["decision_ref"], resolved_bundle_digest=digest(cores), review_bundle_digest=digest(proposal),
        decision_core_refs=[{"decision_ref": c["decision_ref"], "decision_core_sha256": digest(c), "selected_outcome": c["operation"]} for c in cores],
        authorization_evidence_ref=gov["authorization_ref"], authorization_evidence_sha256=gov["authorization_sha256"],
        admission_targets=[{"target_ref": t["version_ref"], "target_sha256": digest(t), "effect_kind": t["operation"]} for t in proposal["targets"]],
        input_state_ref=old_state["node_id"], input_state_sha256=byte_digest(encoded(old_state)), project_ref=p["project_ref"],
        deterministic_consequences=[{"consequence_kind": x["kind"], "consequence_ref": x["node_id"], "output_sha256": byte_digest(encoded(x)), "declared_input_ref": gov["decision_ref"]} for x in [state, *history.values(), generated]],
        application_receipt_ref=receipt_ref, rollback_ref="runtime-recovery:committed-head", runtime_activations=0, external_effect_refs=[])
    for record in [state, *history.values(), generated, transaction, *governance]:
        cs = [ref for ref, c in projection["contracts"].items() if c["semantic_kind"] == record["kind"] and c["lifecycle_state"] in ("admitted-current", "local-admitted-current")]
        require(len(cs) == 1, "ambiguous consequence carrier")
        validate_record(record, cs[0], projection)
        for prior in projection["subjects"].values():
            if prior["kind"] == record["kind"] and record["kind"] in ("project-state", "project-semantic-event-history", "project-governance-event-history") and prior["effective_state"] in ("admitted-current", "local-admitted-current"):
                prior["effective_state"] = "local-admitted-historical"
        ver = record["node_id"] + "@local." + str(sequence)
        projection["subjects"][ver] = make_record(record, category="artifact-instance", version=ver, state="local-admitted-current",
                                                  path=record_ref, sha=byte_digest(encoded(record)), decision=decision_refs, carrier=cs[0])
        if record is state:
            selector = "/consequences/project_state"
        elif record in history.values():
            selector = "/consequences/histories/" + record["kind"]
        elif record is generated:
            selector = "/consequences/generated_output"
        elif record is transaction:
            selector = "/consequences/admission_transaction"
        else:
            selector = "/consequences/governance_records/" + str(governance.index(record))
        projection["subjects"][ver]["source"].update(path=tx_path, selector=selector, store_id=store_id)
    projection["state"] = state
    projection["histories"] = history
    # These six fixed, declared deterministic connections are covered by the signed
    # protocol/source snapshot. They are instances of existing axes, not new meanings.
    typed_carriers = [ref for ref, c in projection["contracts"].items() if c["semantic_kind"] == "typed-relation" and c["lifecycle_state"] in ("admitted-current", "local-admitted-current")]
    require(len(typed_carriers) == 1, "ambiguous current Typed Relation consequence carrier")
    typed_carrier = typed_carriers[0]
    def endpoint(record):
        entry = resolve(projection["subjects"], record["node_id"])
        return {"kind": endpoint_kind(entry, projection), "ref": entry["identity"], "version_ref": entry["version_ref"]}
    project = resolve(projection["subjects"], state["payload"]["project_ref"])
    connections = [(state, old_state, "relation.successor-of", {"succession_effect": "continues-and-supersedes-current-state"}),
                   (state, project["record"], "relation.member-of", {"membership_role": "durable-project-state"})]
    for result in [state, *history.values(), generated]:
        connections.append((transaction, result, "relation.materializes-consequence", {"consequence_role": result["kind"],
                            "output_digest": "sha256:" + byte_digest(encoded(result)), "application_receipt_ref": receipt_ref}))
    relation_records = []
    for i, (source, target, predicate, qualifiers) in enumerate(connections):
        relation = copy.deepcopy(projection["documents"]["authority/admissions/governance-transaction-surface/v1/instances/typed-relations/materializes-project-state.json"])
        source_ep = endpoint(source)
        if target is old_state:
            old = next(v for v in projection["subjects"].values() if v["kind"] == "project-state" and v["record"]["node_id"] == old_state["node_id"])
            target_ep = {"kind": old["kind"], "ref": old["identity"], "version_ref": old["version_ref"]}
        elif target is project["record"]:
            target_ep = {"kind": endpoint_kind(project, projection), "ref": project["identity"], "version_ref": project["version_ref"]}
        else:
            target_ep = endpoint(target)
        relation.update(node_id=f"typed-relation:{store_id}:{sequence}:{i}", name="Deterministic local " + predicate,
                        schema_version=projection["contracts"][typed_carrier]["instance_discriminator"]["value"],
                        lifecycle_state="active", scope_ref=proposal["scope_ref"], evidence_refs=[record_ref], claim_ceiling=state["claim_ceiling"])
        relation["payload"].update(relation_kind_ref=predicate, source=source_ep, target=target_ep, qualifiers=qualifiers,
                                    relation_lifecycle_state="active", relation_evidence_refs=[record_ref])
        validate_record(relation, typed_carrier, projection)
        version = relation["node_id"] + "@local." + str(sequence)
        entry = make_record(relation, category="typed-relation", version=version, state="local-admitted-current", path=tx_path,
                            sha=byte_digest(encoded(relation)), decision=decision_refs, carrier=typed_carrier)
        entry["source"].update(selector="/consequences/typed_relations/" + str(i), store_id=store_id)
        projection["subjects"][version] = entry
        relation_records.append(relation)
    validate_histories(history)
    receipt = {"schema_version": "lab-runtime-application-receipt/v1", "transaction_ref": tx_ref, "proposal_digest": digest(proposal),
               "authorization_digest": digest(approval), "decision_core_digests": [digest(c) for c in cores],
               "outputs": [{"kind": x["kind"], "identity_ref": x["node_id"], "sha256": byte_digest(encoded(x))} for x in [state, *history.values(), generated, transaction, *governance, *relation_records]],
               "semantic_cursor": cursor, "governance_cursor": gov["governance_cursor"], "application_state": "applied",
               "authority_boundary": "provisioned-local-store", "repository_admission_effect": "none", "runtime_activations": 0, "external_effects": 0}
    return {"project_state": state, "histories": history, "admission_transaction": transaction, "generated_output": generated,
            "registry_projection": registries, "governance_records": governance, "typed_relations": relation_records, "receipt": receipt}
