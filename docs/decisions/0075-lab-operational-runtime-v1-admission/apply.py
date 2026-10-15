#!/usr/bin/env python3
"""Apply/check the exact owner-authorized runtime admission, preserving its code."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime
import fcntl
import os
from pathlib import Path
import shutil
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PACKAGE = REPO / "implementation/lab-runtime/v1"
sys.path.insert(0, str(PACKAGE))
from lab_runtime.common import atomic, byte_digest, digest, encoded, fsync_dir, load, require
from lab_runtime.operations import validate_record
from lab_runtime.sources import capture, make_record, resolve, validate_histories
from lab_runtime.store import Store

FINAL = REPO / "authority/admissions/lab-operational-runtime/v1"
OLD = REPO / "authority/admissions/governance-transaction-surface/v1"
POINTER = REPO / "authority/project-state-transitions/current.json"
DECISION = "CAL-DECISION-0075-LAB-OPERATIONAL-RUNTIME-V1-ADMISSION"
DREF = "decision:0075-lab-operational-runtime-v1-admission"
SCOPE = "scope:lab-operational-runtime-v1-admission-0075"
IMPL = "implementation:cyberalchemy-lab:operational-runtime:v1"
STATE = "project-state:cyberalchemy-v2-to-lab-migration:decision-0075"
TX = "admission-transaction:lab-operational-runtime-0075"
DB = "decision-bundle:lab-operational-runtime-0075"
CHECKPOINT = "decision-checkpoint:lab-operational-runtime-0075"
BOUNDARY = "authority-boundary:lab-operational-runtime-0075"
DSCOPE = "decision-scope:lab-operational-runtime-0075"
POLICY = "policy:cyberalchemy-lab-operational-foundation"
CHALLENGE = "challenge-contract:cyberalchemy-lab-operational-foundation"
CAPABILITY = "product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"
USER = "Admit Lab Operational Runtime/v1 as the implementation for local repository inspection, explicitly authorized local transactions, verified replay/recovery and ephemeral Agent context, bound to its exact reviewed package and validation evidence."
EXCLUDED = ["runtime-activation", "service-start", "deployment", "external-publication", "external-effects", "canonical-semantic-vocabulary-change", "capability-adoption", "source-profile-evolution"]
CEILING = "Admits only the exact reviewed Lab Operational Runtime/v1 implementation and its repository records. Execution remains within a provisioned local store and the frozen D74 source profile; no service activation, external authority, complete ontology coverage or product adoption is established."


def rel(p):
    return p.relative_to(REPO).as_posix()


def sha(p):
    return byte_digest(p.read_bytes())


def binding(p):
    return {"path": rel(p), "sha256": sha(p)}


def put(p, value):
    atomic(p, encoded(value))


def baseline():
    return capture(REPO, load(PACKAGE / "profile.json"))


def historical_source_check(source, validation):
    original = copy.deepcopy(source)
    for key in original["epoch_inventory"]:
        original["epoch_inventory"][key] = [p for p in original["epoch_inventory"][key] if p not in (rel(FINAL / "bundle.json"),rel(HERE / "decision.json"))]
    original.pop("snapshot_digest")
    require(digest(original) == validation["demonstration"]["source_snapshot_digest"], "reviewed D74 source material or unexpected authority epoch drift")


def package_checks():
    receipt = load(PACKAGE / "receipts/validation.json")
    require(receipt["result"] == "PASS" and receipt["tests_run"] == 33, "reviewed validation missing")
    require(len(receipt["checks"]) == 33 and all(x["result"] == "PASS" for x in receipt["checks"]), "reviewed checks incomplete")
    require(receipt["demonstration"]["result"] == "PASS" and receipt["sources_unchanged_during_validation"], "reviewed demo/source freeze failed")
    require(digest(receipt["source_manifest"]) == receipt["source_manifest_digest"], "manifest digest mismatch")
    require(len(receipt["source_manifest"]) == 24, "reviewed package changed")
    for x in receipt["source_manifest"]:
        p = REPO / x["path"]
        require(p.is_relative_to(PACKAGE) and sha(p) == x["sha256"], "reviewed file drift: " + x["path"])
    for name in ("authority_effect", "repository_admission_effect"):
        require(receipt[name] == "none", "candidate evidence scope changed")
    require(not (REPO / ".local/lab-runtime/store").exists(), "existing default operational store needs explicit reconciliation")
    return receipt


def template(name):
    return load(OLD / name)


def record(name, identity, title, ceiling=CEILING):
    r = template(name)
    r.update(node_id=identity, name=title, scope_ref=SCOPE, owner_ref="role:repository-owner",
             evidence_refs=[rel(HERE / "authorization.json")], challenge_route=CHALLENGE, claim_ceiling=ceiling)
    return r


def projection_with(projection, records):
    p = copy.deepcopy(projection)
    for path, r in records.items():
        carrier = next(c for c, v in p["contracts"].items() if v["lifecycle_state"] == "admitted-current" and v["semantic_kind"] == r["kind"])
        vref = r["node_id"] + ("@applied" if r["kind"] == "admission-transaction" else "@decision-0075")
        p["subjects"][vref] = make_record(r, category="typed-relation" if r["kind"] == "typed-relation" else "artifact-instance", version=vref,
            state="admitted-current", path=rel(FINAL / path), sha=byte_digest(encoded(r)), decision=DECISION, carrier=carrier)
    return p


def validate_records(projection, records):
    p = projection_with(projection, records)
    checks = []
    for path, r in records.items():
        entry = p["subjects"][r["node_id"] + ("@applied" if r["kind"] == "admission-transaction" else "@decision-0075")]
        validate_record(r, entry["carrier_ref"], p)
        checks.append({"path": path, "carrier_ref": entry["carrier_ref"], "result": "PASS"})
    validate_histories({k: records["instances/" + k + ".json"] for k in ("project-semantic-event-history", "project-governance-event-history")})
    return checks


def build(stage, source, validation):
    projection = Store.initial_projection(source)
    implementation = load(REPO / "authority/artifact-types/implementation/v1/fixtures/valid/record.json")
    implementation.update(node_id=IMPL, name="Lab Operational Runtime/v1", owner_ref="role:repository-owner", scope_ref=SCOPE,
        challenge_route=CHALLENGE, evidence_refs=[rel(PACKAGE / "receipts/validation.json"), rel(HERE / "target.json")], claim_ceiling=CEILING)
    implementation["payload"] = {"implementation_kind": "local-governed-operational-runtime",
        "conforms_to_schema_refs": [rel(p) for p in sorted((PACKAGE / "schemas").glob("*.json"))],
        "realizes_capability_refs": [CAPABILITY], "execution_entrypoint_ref": rel(PACKAGE / "lab.py"),
        "environment_contract_ref": rel(PACKAGE / "requirements.txt")}
    implementation["relation_refs"] = [{"relation_kind_ref": "relation.realizes", "direction": "source", "counterpart_kind": "product-capability", "counterpart_ref": CAPABILITY}]
    put(HERE / "implementation.json", implementation)
    target = {"schema_version": "lab-operational-runtime-admission-target/v1", "implementation_ref": IMPL,
        "package_root": rel(PACKAGE), "source_manifest": validation["source_manifest"], "source_manifest_digest": validation["source_manifest_digest"],
        "validation_receipt": binding(PACKAGE / "receipts/validation.json"), "implementation_record": binding(HERE / "implementation.json"),
        "scope": CEILING, "source_baseline": "decision:0074", "excluded_effects": EXCLUDED}
    put(HERE / "target.json", target)
    core = {"schema_version": "cyberalchemy-lab-independent-decision-core/v1", "decision_id": DECISION,
        "decision_ref": DREF, "owner_ref": "role:repository-owner", "scope_ref": DSCOPE, "effect_kind": "implementation-admission",
        "target_ref": IMPL, "target": binding(HERE / "target.json"), "selected_outcome": "admit-exact-reviewed-target",
        "hash_policy": "stable-core-excludes-generated-consequence-digests"}
    put(HERE / "decision-core.json", core)
    authorization = {"schema_version": "cyberalchemy-lab-owner-authorization/v2", "authorization_id": "CAL-AUTHORIZATION-0075-LAB-OPERATIONAL-RUNTIME",
        "authorized": True, "principal_ref": "principal:lab-owner", "recorded_on": "2026-10-07", "decision_refs": [DECISION],
        "decision_checkpoint_ref": CHECKPOINT, "selected_outcome": "admit-exact-reviewed-target", "verbatim_user_authorization": USER,
        "authorization_mechanism": "explicit-owner-message-in-current-conversation", "cryptographic_owner_signature": None,
        "interpreted_scope": CEILING + " Deterministic state, paired history and receipt consequences are part of this same admission.",
        "reviewed_bindings": {"target": binding(HERE / "target.json"), "decision_core": binding(HERE / "decision-core.json"),
            "validation_receipt": target["validation_receipt"], "source_manifest_digest": target["source_manifest_digest"]}, "excluded_effects": EXCLUDED}
    put(HERE / "authorization.json", authorization)
    for name in ("target.json", "implementation.json", "decision-core.json", "authorization.json"):
        shutil.copyfile(HERE / name, stage / name)
    for x in validation["source_manifest"]:
        p = stage / "reviewed-package" / Path(x["path"]).relative_to(rel(PACKAGE))
        p.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(REPO / x["path"], p)
    p = stage / "reviewed-package/receipts/validation.json"; p.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PACKAGE / "receipts/validation.json", p)
    stable = [binding(HERE / x) for x in ("target.json", "implementation.json", "decision-core.json", "authorization.json")]
    old_state = source["state"]
    r = {}
    r["instances/implementation.json"] = implementation
    state = record("instances/project-state.json", STATE, "Project State after runtime admission 0075")
    state["payload"].update(cursor="decision:0075", decision_refs=old_state["payload"]["decision_refs"] + [DECISION],
        artifact_refs=old_state["payload"]["artifact_refs"] + [x["path"] for x in stable],
        state_digest="sha256:" + digest({"predecessor": old_state["payload"]["state_digest"], "admitted_materials": stable}))
    state["relation_refs"] = [{"relation_kind_ref": "relation.member-of", "direction": "source", "counterpart_kind": "project", "counterpart_ref": state["payload"]["project_ref"]},
        {"relation_kind_ref": "relation.successor-of", "direction": "source", "counterpart_kind": "project-state", "counterpart_ref": old_state["node_id"]},
        {"relation_kind_ref": "relation.materializes-consequence", "direction": "target", "counterpart_kind": "admission-transaction", "counterpart_ref": TX}]
    r["instances/project-state.json"] = state
    semantic = copy.deepcopy(source["histories"]["project-semantic-event-history"])
    se = {"event_id": "project-semantic-event:cyberalchemy-v2-to-lab-migration:5", "cursor": 5,
        "previous_event_digest": semantic["payload"]["events"][-1]["event_digest"], "change_kind": "lab-operational-runtime-v1-admitted",
        "predecessor_state_ref": old_state["node_id"], "predecessor_state_digest": old_state["payload"]["state_digest"],
        "resulting_state_ref": STATE, "resulting_state_digest": state["payload"]["state_digest"], "material_refs": stable,
        "record_ref": rel(HERE / "target.json"), "semantic_summary": "Admitted exact runtime implementation; preserved frozen source profile, canonical vocabularies and activation boundaries."}
    se["event_digest"] = digest(se)
    governance = copy.deepcopy(source["histories"]["project-governance-event-history"])
    ge = {"event_id": "project-governance-event:cyberalchemy-v2-to-lab-migration:5", "governance_cursor": 5,
        "previous_event_digest": governance["payload"]["events"][-1]["event_digest"], "semantic_event_ref": {"semantic_event_id": se["event_id"], "semantic_event_digest": se["event_digest"], "semantic_cursor": 5},
        "decision_ref": DECISION, "authorization_ref": rel(HERE / "authorization.json"), "authorization_sha256": sha(HERE / "authorization.json"),
        "policy_ref": POLICY, "challenge_contract_ref": CHALLENGE, "upstream_governance_evidence_refs": [x["path"] for x in stable],
        "record_ref": rel(HERE / "decision-core.json"), "governance_summary": "One explicit owner admission, one stable Decision core, one atomic repository transaction; no activation or external effect."}
    ge["event_digest"] = digest(ge)
    for kind, history, event, cursor_key in (("project-semantic-event-history", semantic, se, "latest_cursor"), ("project-governance-event-history", governance, ge, "latest_governance_cursor")):
        history.update(scope_ref=SCOPE, evidence_refs=[x["path"] for x in stable], claim_ceiling="Append-only repository history through cursor 5; no runtime activation.")
        history["payload"]["events"].append(event); history["payload"][cursor_key] = 5
        history["payload"]["chain_digest"] = digest([e["event_digest"] for e in history["payload"]["events"]])
        history["relation_refs"] = [{"relation_kind_ref": "relation.materializes-consequence", "direction": "target", "counterpart_kind": "admission-transaction", "counterpart_ref": TX}]
        r["instances/" + kind + ".json"] = history
    ds = record("instances/governance/decision-scopes/decision-0074a.json", DSCOPE, "Exact runtime admission scope")
    ds["payload"].update(subject_refs=[IMPL], subject_kind_refs=["implementation"], permitted_effects=["implementation-admission"], excluded_effects=EXCLUDED)
    ds["relation_refs"][0]["counterpart_ref"] = BOUNDARY
    r["instances/governance/decision-scope.json"] = ds
    decision = record("instances/governance/decisions/decision-0074a.json", DREF, DECISION)
    decision["payload"].update(decision_maker_ref="principal:lab-owner", declared_effect_refs=["implementation-admission"], evidence_basis_refs=[rel(HERE / "authorization.json")], selected_outcome="admit-exact-reviewed-target", subject_refs=[IMPL])
    decision["relation_refs"][0]["counterpart_ref"] = DB
    r["instances/governance/decision.json"] = decision
    boundary = record("instances/governance/authority-boundary.json", BOUNDARY, "Owner exact implementation admission boundary")
    boundary["payload"].update(authority_scope_ref=DSCOPE, effective_period="decision-0075-admission-only", allowed_effect_kinds=["implementation-admission"], excluded_effect_kinds=EXCLUDED, challenge_route_ref=CHALLENGE)
    boundary["relation_refs"] = [{"relation_kind_ref": "relation.scopes-authority-over", "direction": "source", "counterpart_kind": "decision-scope", "counterpart_ref": DSCOPE}]
    r["instances/governance/authority-boundary.json"] = boundary
    db = record("instances/governance/decision-bundle.json", DB, "Resolved runtime admission bundle")
    resolved = digest([core])
    db["payload"].update(checkpoint_ref=CHECKPOINT, bundle_digest=resolved, ordered_decisions=[{"decision_ref": DREF, "decision_core_sha256": sha(HERE / "decision-core.json"), "owner_ref": "role:repository-owner", "scope_ref": DSCOPE, "effect_kind": "implementation-admission", "target_refs": [IMPL], "target_digests": [{"target_ref": IMPL, "sha256": sha(HERE / "target.json")}], "selected_outcome": "admit-exact-reviewed-target"}])
    db["relation_refs"] = [{"relation_kind_ref": "relation.member-of", "direction": "target", "counterpart_kind": "decision", "counterpart_ref": DREF}]
    r["instances/governance/decision-bundle.json"] = db
    checkpoint = record("instances/governance/decision-checkpoint.json", CHECKPOINT, "Resolved owner runtime admission checkpoint")
    recorded_at = datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()
    checkpoint["payload"].update(decision_bundle_ref=DB, presentation_state="resolved", opened_at=recorded_at, closed_at=recorded_at,
        workflow_instance_ref="workflow-instance:lab-runtime-admission-0075")
    r["instances/governance/decision-checkpoint.json"] = checkpoint
    generated = record("instances/generated-output.json", "generated-output:runtime-admission-0075", "Runtime admission index projection")
    index = {"scope": "Implementation, successor state, both histories and five governance records before Generated Output and transaction construction; not a complete catalog", "implementation_ref": IMPL, "records": {p: byte_digest(encoded(v)) for p,v in r.items()}}
    put(stage / "instance-index.json", index)
    generated["payload"].update(generator_ref="cal.generator.lab-runtime-admission/v1", input_refs=[rel(HERE / "target.json")], output_digest="sha256:" + sha(stage / "instance-index.json"), reproducibility_receipt_ref=rel(FINAL / "receipts/application.json"))
    generated["relation_refs"][0]["counterpart_ref"] = TX
    r["instances/generated-output.json"] = generated
    transaction = record("instances/governance/admission-transaction.json", TX, "Applied runtime admission transaction")
    outputs = {k:r["instances/" + k + ".json"] for k in ("project-state", "project-semantic-event-history", "project-governance-event-history", "generated-output")}
    transaction["payload"].update(project_ref=state["payload"]["project_ref"], decision_bundle_ref=DB,
        decision_core_refs=[{"decision_ref": DREF, "decision_core_sha256": sha(HERE / "decision-core.json"), "selected_outcome": "admit-exact-reviewed-target"}],
        review_bundle_digest=sha(HERE / "target.json"), resolved_bundle_digest=resolved,
        authorization_evidence_ref=rel(HERE / "authorization.json"), authorization_evidence_sha256=sha(HERE / "authorization.json"),
        input_state_ref=old_state["node_id"], input_state_sha256=sha(OLD / "instances/project-state.json"),
        admission_targets=[{"target_ref": IMPL, "target_sha256": sha(HERE / "target.json"), "effect_kind": "implementation-admission"}],
        deterministic_consequences=[{"consequence_ref":v["node_id"], "consequence_kind":k, "declared_input_ref":DB, "output_sha256":byte_digest(encoded(v))} for k,v in outputs.items()],
        application_state="applied", application_receipt_ref=rel(FINAL / "receipts/application.json"), rollback_ref=rel(OLD / "bundle.json"))
    transaction["relation_refs"] = [{"relation_kind_ref":"relation.governed-by", "direction":"source", "counterpart_kind":"policy", "counterpart_ref":POLICY}] + [{"relation_kind_ref":"relation.materializes-consequence", "direction":"source", "counterpart_kind":k, "counterpart_ref":v["node_id"]} for k,v in outputs.items()]
    r["instances/governance/admission-transaction.json"] = transaction
    for k,v in outputs.items():
        tr = record("instances/typed-relations/materializes-project-state.json", "typed-relation:decision-0075-materializes-"+k, "Runtime admission materializes " + k)
        tr["payload"].update(source={"kind":"admission-transaction", "ref":TX, "version_ref":TX+"@applied"}, target={"kind":k, "ref":v["node_id"], "version_ref":v["node_id"]+"@decision-0075"},
            qualifiers={"application_receipt_ref":rel(FINAL / "receipts/application.json"), "consequence_role":k, "output_digest":"sha256:"+byte_digest(encoded(v))}, relation_evidence_refs=[rel(HERE / "authorization.json")])
        r["instances/typed-relations/materializes-"+k+".json"] = tr
    project_version = resolve(projection["subjects"], state["payload"]["project_ref"])["version_ref"]
    for axis, other, kind, version, qualifiers in (("member-of", state["payload"]["project_ref"], "project", project_version, {"membership_role":"governed-current-project-state"}),
        ("successor-of", old_state["node_id"], "project-state", resolve(projection["subjects"], old_state["node_id"])["version_ref"], {"succession_effect":"runtime-implementation-admission"})):
        tr = record("instances/typed-relations/materializes-project-state.json", "typed-relation:decision-0075-"+axis, "Runtime admission state " + axis)
        tr["payload"].update(relation_kind_ref="relation."+axis, source={"kind":"project-state", "ref":STATE, "version_ref":STATE+"@decision-0075"}, target={"kind":kind, "ref":other, "version_ref":version}, qualifiers=qualifiers, relation_evidence_refs=[rel(HERE / "authorization.json")])
        r["instances/typed-relations/"+axis+".json"] = tr
    checks = validate_records(projection, r)
    for p,v in r.items(): put(stage / p, v)
    for name in ("project-state", "project-semantic-event-history", "project-governance-event-history"):
        p=stage / "history/decision-0074" / (name+".json"); p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(OLD / "instances" / (name+".json"), p)
    overlay = {"schema_version":"cyberalchemy-lab-implementation-admission/v1", "decision_id":DECISION, "status":"owner-admitted", "authority_effect":"implementation-admission",
        "implementation_ref":IMPL, "implementation_version_ref":IMPL+"@v1", "target":binding(HERE / "target.json"), "validation_evidence":target["validation_receipt"],
        "entry":{"identity_ref":IMPL, "carrier_type_ref":"cal.artifact-type.implementation/v1", "admitted_instance_path":rel(FINAL / "instances/implementation.json"), "sha256":sha(stage / "instances/implementation.json"), "lifecycle_state":"admitted-current"},
        "source_profile_as_of":"decision:0074", "repository_admission_as_of":"decision:0075", "runtime_activations":0, "external_effect_refs":[], "claim_ceiling":CEILING,
        "declaration_rule":"Implementation capability references declare this bounded scope; no separate Capability Realization Binding or global realizes connection is admitted."}
    put(stage / "implementation-admission.json", overlay)
    put(stage / "artifact-instance-admission.json", {"schema_version":"cyberalchemy-lab-artifact-instance-admission/v1", "decision_id":DECISION, "entries":[{"identity_ref":v["node_id"], "version_ref":v["node_id"]+("@applied" if v["kind"]=="admission-transaction" else "@decision-0075"), "semantic_kind":v["kind"], "carrier_type_ref":projection_with(projection,{p:v})["subjects"][v["node_id"]+("@applied" if v["kind"]=="admission-transaction" else "@decision-0075")]["carrier_ref"], "admitted_instance_path":rel(FINAL / p), "sha256":sha(stage / p), "lifecycle_state":"admitted-current"} for p,v in r.items() if v["kind"] != "typed-relation"],
        "predecessor_transitions":[{"identity_ref":old_state["node_id"], "to":"admitted-historical"}] + [{"identity_ref":h["node_id"], "version_ref":h["node_id"]+"@decision-0074", "to":"admitted-historical"} for h in source["histories"].values()], "claim_ceiling":CEILING})
    put(stage / "typed-relation-admission.json", {"schema_version":"cyberalchemy-lab-typed-relation-admission/v1", "decision_id":DECISION, "entries":[{"identity_ref":v["node_id"], "version_ref":v["node_id"]+"@decision-0075", "carrier_type_ref":"cal.artifact-type.typed-relation/v3", "admitted_instance_path":rel(FINAL / p), "sha256":sha(stage / p), "lifecycle_state":"admitted-current"} for p,v in r.items() if v["kind"] == "typed-relation"], "claim_ceiling":"Six declared deterministic connections only; no new Relation Kind or inferred realization connection."})
    decision_record = {"schema_version":"cyberalchemy-lab-runtime-implementation-admission-decision/v1", "decision_id":DECISION, "status":"owner-admitted", "decided_on":"2026-10-07", "owner_ref":"principal:lab-owner",
        "title":"Lab Operational Runtime/v1 implementation admission", "authority_effect":"implementation-admission", "authorization":binding(HERE / "authorization.json"), "decision_core":binding(HERE / "decision-core.json"),
        "target":binding(HERE / "target.json"), "admission_bundle_ref":rel(FINAL / "bundle.json"), "application_receipt_ref":rel(FINAL / "receipts/application.json"),
        "current_project_state_ref":STATE, "source_profile_as_of":"decision:0074", "effects":{"implementations_admitted":1,"definitions_admitted":0,"artifact_types_admitted":0,"relation_kinds_admitted":0,"project_states_materialized":1,"semantic_events_appended":1,"governance_events_appended":1,"typed_relations_admitted":6,"runtime_activations":0,"external_effects":0}, "claim_ceiling":CEILING}
    put(stage / "decision.json", decision_record)
    package_checks()
    require(source["snapshot_digest"] == baseline()["snapshot_digest"], "source epoch drift before publication")
    receipt = {"schema_version":"cyberalchemy-lab-runtime-implementation-admission-receipt/v1", "result":"PASS", "application_state":"applied", "decision_ref":DECISION,
        "transaction_ref":TX, "authorization":binding(HERE / "authorization.json"), "target":binding(HERE / "target.json"), "reviewed_validation":target["validation_receipt"],
        "source_manifest_digest":validation["source_manifest_digest"], "reviewed_package_files":24, "unchanged_reviewed_files":True, "schema_checks":checks,
        "source_snapshot_before_admission":source["snapshot_digest"], "history_cursors":{"semantic":5,"governance":5}, "outputs":[{"path":rel(FINAL/p),"sha256":sha(stage/p)} for p in sorted(r)],
        "current_project_state_ref":STATE, "runtime_activations":0, "external_effects":0, "power_loss_durability_claim":False, "commit_point":"one-atomic-rename-of-complete-immutable-bundle",
        "claim_ceiling":CEILING}
    put(stage / "receipts/application.json", receipt)
    files = [{"path":p.relative_to(stage).as_posix(),"sha256":sha(p)} for p in sorted(stage.rglob("*")) if p.is_file()]
    bundle = {"schema_version":"cyberalchemy-lab-runtime-implementation-admission-bundle/v1", "bundle_id":"CAL-LAB-OPERATIONAL-RUNTIME-ADMISSION-BUNDLE-0075", "status":"owner-admitted-postimage",
        "decision_refs":[DECISION], "decision_checkpoint_ref":CHECKPOINT, "authority_effect":"implementation-and-deterministic-project-state-admission",
        "authorization":binding(HERE / "authorization.json"), "files":files, "current_project_state_ref":STATE, "current_project_state_sha256":sha(stage / "instances/project-state.json"),
        "implementation_ref":IMPL, "runtime_activations":0, "external_effect_refs":[], "claim_ceiling":CEILING}
    put(stage / "bundle.json", bundle)


def synchronize():
    put(HERE / "decision.json", load(FINAL / "decision.json"))
    put(HERE / "receipts/application.json", load(FINAL / "receipts/application.json"))
    put(POINTER, {"schema_version":"cyberalchemy-lab-current-project-state-lookup/v1", "decision_ref":DECISION, "admission_bundle":binding(FINAL / "bundle.json"),
        "current_project_state":binding(FINAL / "instances/project-state.json"), "identity_ref":STATE, "replay_source":False, "projection_policy":"generated-from-immutable-admission-bundle", "authority_effect":"none"})


def check():
    validation = package_checks()
    b = load(FINAL / "bundle.json")
    require(b["decision_refs"] == [DECISION] and b["runtime_activations"] == 0, "wrong admission scope")
    for x in b["files"]:
        require(sha(FINAL / x["path"]) == x["sha256"], "admitted material drift: " + x["path"])
    for name in ("target.json", "implementation.json", "decision-core.json", "authorization.json", "decision.json"):
        require(sha(HERE / name) == sha(FINAL / name), "decision mirror drift: " + name)
    require(load(FINAL / "authorization.json")["verbatim_user_authorization"] == USER, "authorization changed")
    require(load(FINAL / "target.json")["source_manifest"] == validation["source_manifest"], "target differs from reviewed code")
    target = load(FINAL / "target.json")
    core = load(FINAL / "decision-core.json")
    auth = load(FINAL / "authorization.json")
    require(target["validation_receipt"] == binding(PACKAGE / "receipts/validation.json"), "target validation evidence mismatch")
    require(target["implementation_record"] == binding(HERE / "implementation.json"), "implementation target mismatch")
    require(core["target"] == binding(HERE / "target.json") and core["effect_kind"] == "implementation-admission", "Decision core binding mismatch")
    require(auth["reviewed_bindings"]["target"] == core["target"] and auth["reviewed_bindings"]["decision_core"] == binding(HERE / "decision-core.json"), "authorization binding mismatch")
    require(sha(FINAL / "instances/implementation.json") == sha(HERE / "implementation.json"), "admitted Implementation differs from exact target")
    for x in validation["source_manifest"]:
        p=FINAL / "reviewed-package" / Path(x["path"]).relative_to(rel(PACKAGE))
        require(sha(p) == x["sha256"], "frozen copy differs: " + x["path"])
    require(sha(FINAL / "reviewed-package/receipts/validation.json") == sha(PACKAGE / "receipts/validation.json"), "validation copy drift")
    source = baseline()
    # D75 changes the epoch listing, not the admitted runtime's frozen D74 source materials.
    historical_source_check(source, validation)
    records={x["path"]:load(FINAL / x["path"]) for x in b["files"] if x["path"].startswith("instances/") and x["path"].endswith(".json")}
    checks=validate_records(Store.initial_projection(source),records)
    receipt=load(FINAL / "receipts/application.json")
    for x in receipt["outputs"]: require(sha(REPO / x["path"]) == x["sha256"], "output receipt mismatch")
    transaction = records["instances/governance/admission-transaction.json"]["payload"]
    require(transaction["authorization_evidence_sha256"] == sha(HERE / "authorization.json"), "transaction authority mismatch")
    require(transaction["decision_core_refs"][0]["decision_core_sha256"] == sha(HERE / "decision-core.json"), "transaction Decision core mismatch")
    require(transaction["admission_targets"][0]["target_sha256"] == sha(HERE / "target.json"), "transaction target mismatch")
    for c in transaction["deterministic_consequences"]:
        require(c["output_sha256"] == sha(FINAL / "instances" / (c["consequence_kind"]+".json")), "transaction consequence mismatch")
    index=load(FINAL / "instance-index.json")
    for p, expected in index["records"].items(): require(sha(FINAL / p) == expected, "generated index mismatch")
    require(records["instances/generated-output.json"]["payload"]["output_digest"] == "sha256:"+sha(FINAL / "instance-index.json"), "Generated Output mismatch")
    for k in ("project-state","project-semantic-event-history","project-governance-event-history"):
        require(sha(FINAL / "history/decision-0074" / (k+".json")) == sha(OLD / "instances" / (k+".json")), "D74 preservation failed")
    pointer=load(POINTER)
    require(pointer["admission_bundle"] == binding(FINAL / "bundle.json") and pointer["current_project_state"] == binding(FINAL / "instances/project-state.json"), "current lookup drift")
    print(encoded({"result":"PASS", "decision_ref":DECISION, "schema_checks":len(checks), "reviewed_package_files":24, "unchanged_reviewed_files":True,
        "history_cursors":{"semantic":5,"governance":5}, "current_project_state_ref":STATE, "runtime_source_profile_as_of":"decision:0074", "runtime_activations":0, "external_effects":0}).decode(),end="")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply",action="store_true")
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    require(args.apply != args.check,"choose --apply or --check")
    if args.check:
        check(); return
    lock=REPO / ".local/admission-locks/runtime-0075.lock"
    lock.parent.mkdir(parents=True,exist_ok=True)
    with lock.open("a+") as h:
        fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if FINAL.exists():
            historical_source_check(baseline(), package_checks())
            synchronize(); check(); return
        require(not (HERE / "decision.json").exists(),"existing Decision 0075 requires reconciliation")
        validation=package_checks(); source=baseline()
        require(source["snapshot_digest"] == validation["demonstration"]["source_snapshot_digest"],"reviewed D74 epoch changed")
        stage_root=REPO / ".local/admission-staging"
        stage_root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="runtime-0075-",dir=stage_root) as temp:
            stage=Path(temp) / "bundle"; stage.mkdir()
            build(stage,source,validation)
            for p in stage.rglob("*"):
                if p.is_file():
                    with p.open("rb") as f: os.fsync(f.fileno())
            for p in sorted([p for p in stage.rglob("*") if p.is_dir()], key=lambda p:len(p.parts),reverse=True): fsync_dir(p)
            fsync_dir(stage)
            FINAL.parent.mkdir(parents=True,exist_ok=True)
            os.rename(stage,FINAL)
            fsync_dir(FINAL.parent)
        synchronize(); check()


if __name__ == "__main__":
    main()
