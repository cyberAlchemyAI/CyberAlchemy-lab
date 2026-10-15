"""Inspectable schema-backed consequences of one exact local approval."""
from __future__ import annotations

import copy

from .common import digest

BASE = "authority/admissions/governance-transaction-surface/v1/instances/governance/"


def records(projection, proposal, cores, approval, store_id, sequence):
    owner, scope = approval["owner_ref"], proposal["scope_ref"]
    evidence = "runtime-approval:" + digest(approval)
    bundle_id = "decision-bundle:" + digest(cores)
    boundary_id = f"authority-boundary:{store_id}:{sequence}"
    checkpoint_id = f"decision-checkpoint:{store_id}:{sequence}"
    def template(name):
        r = copy.deepcopy(projection["documents"][BASE + name + ".json"])
        r.update(owner_ref=owner, scope_ref=scope, evidence_refs=[evidence], challenge_route=proposal["challenge_route"],
                 claim_ceiling="Exact provisioned local operator approval and effect; no repository admission or external authority.")
        return r
    ordered, decisions, scopes = [], [], []
    for core in cores:
        scope_id = "decision-scope:local:" + digest(core)
        effect = core["category"] + "-" + core["operation"]
        decision = template("decisions/decision-0074a")
        decision.update(node_id=core["decision_ref"], name="Exact local " + effect)
        decision["payload"].update(decision_maker_ref=owner, declared_effect_refs=[effect], evidence_basis_refs=[evidence],
                                    selected_outcome=core["operation"], subject_refs=[core["version_ref"]])
        decision["relation_refs"] = [{"counterpart_kind": "decision-bundle", "counterpart_ref": bundle_id, "direction": "source", "relation_kind_ref": "relation.member-of"}]
        ds = template("decision-scopes/decision-0074a")
        ds.update(node_id=scope_id, name="Exact local Decision scope")
        ds["payload"].update(permitted_effects=[effect], subject_kind_refs=[core["category"]], subject_refs=[core["version_ref"]])
        ds["relation_refs"][0]["counterpart_ref"] = boundary_id
        if core.get('domain_scope_ref') is not None:
            decision['scope_ref']=core['domain_scope_ref'];ds['scope_ref']=core['domain_scope_ref']
            decision['evidence_refs'].extend([core['reference_correction_binding']['path'],core['correction_profile_binding']['path']])
            ds['evidence_refs'].extend([core['reference_correction_binding']['path'],core['correction_profile_binding']['path']])
        decisions.append(decision)
        scopes.append(ds)
        ordered.append({"decision_ref": core["decision_ref"], "decision_core_sha256": digest(core), "owner_ref": owner, "scope_ref": scope_id,
                        "effect_kind": effect, "selected_outcome": core["operation"], "target_refs": [core["version_ref"]],
                        "target_digests": [{"target_ref": core["version_ref"], "sha256": core["target_digest"]}]})
    boundary = template("authority-boundary")
    boundary.update(node_id=boundary_id, name="Provisioned local operator transaction boundary")
    boundary["payload"].update(owner_role_ref=owner, accountable_principal_ref=owner, authority_scope_ref=scope,
                               allowed_effect_kinds=list(dict.fromkeys(x["effect_kind"] for x in ordered)),
                               challenge_route_ref=proposal["challenge_route"], effective_period="exact-proposal:" + digest(proposal))
    boundary["relation_refs"] = [{"counterpart_kind": "decision-scope", "counterpart_ref": x["node_id"], "direction": "source", "relation_kind_ref": "relation.scopes-authority-over"} for x in scopes]
    bundle = template("decision-bundle")
    bundle.update(node_id=bundle_id, name="Resolved exact local Decision Bundle")
    bundle["payload"].update(bundle_digest=digest(cores), checkpoint_ref=checkpoint_id, ordered_decisions=ordered)
    bundle["relation_refs"] = [{"counterpart_kind": "decision", "counterpart_ref": x["node_id"], "direction": "target", "relation_kind_ref": "relation.member-of"} for x in decisions]
    checkpoint = template("decision-checkpoint")
    checkpoint.update(node_id=checkpoint_id, name="Resolved local explicit approval checkpoint")
    checkpoint["payload"].update(decision_bundle_ref=bundle_id, workflow_instance_ref="runtime-proposal:" + proposal["proposal_id"],
                                 workflow_profile_ref="runtime-workflow:single-exact-approval/v1", resolved_preference_ref=None,
                                 opened_at=approval["approved_at"], closed_at=approval["approved_at"])
    return [*decisions, *scopes, boundary, bundle, checkpoint]
