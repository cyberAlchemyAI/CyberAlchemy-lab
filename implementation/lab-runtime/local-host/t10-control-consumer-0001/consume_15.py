#!/usr/bin/env python3
"""Read-only W07 selection consumer with actual signed archive verification."""

import base64
import hashlib
import json
import math
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


ROOT = Path(__file__).resolve().parents[4]
CONTROL = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/protocol-review-alternatives-preparation-0001/bound-controls/15-signed-integration-selection.json"
CONTROL_SHA256 = "6c8686bd72621ee8d241148bfe96f7e3235df107ca3e05617c2c00fb56d777cf"
SELECTION = "implementation/lab-workflows/candidates/v1/tests/signed_integration/selection.json"
SELECTION_SHA256 = "6e5d8e24325e45c6801d64161b23539190c78befb2bf9d8f1a9d0f2819ffb1db"
RECEIPT = "implementation/lab-workflows/candidates/v1/receipts/integration/W07/0004.json"
RECEIPT_SHA256 = "3e40e0cb64a479b5546a30c069dc009c950b78a8a6357e0bd58b8e92ea840203"
DOMAINS = ("engineering", "failure", "learning", "research")
ARCHIVE_NAMES = {"HEAD.json", "baseline.json", "config.json",
                 "transactions/0000000000.json", "transactions/0000000001.json"}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def finite_float(value):
        parsed = float(value)
        need(math.isfinite(parsed), "nonfinite JSON")
        return parsed
    return json.loads(raw, object_pairs_hook=pairs, parse_float=finite_float,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def pinned(binding):
    need(type(binding) is dict and set(binding) in ({"path", "sha256"}, {"path", "sha256", "size_bytes"}),
         "invalid binding shape")
    name = binding["path"]
    need(type(name) is str and not Path(name).is_absolute() and ".." not in Path(name).parts,
         "unsafe bound path")
    path = ROOT / name
    need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT),
         "bound origin differs")
    raw = path.read_bytes()
    need(sha(raw) == binding["sha256"] and
         ("size_bytes" not in binding or len(raw) == binding["size_bytes"]),
         "bound bytes differ: " + name)
    return raw


def pointer(value, selector):
    need(type(selector) is str and selector.startswith("/"), "invalid source selector")
    for part in selector.split("/")[1:]:
        value = value[part.replace("~1", "/").replace("~0", "~")]
    return value


def validate_control(control, selection, receipt):
    need(control["member_ref"] == "review:W07:signed-integration-selection" and
         control["option_id"] == "T10:control-option:15" and
         control["control_kind"] == "verification-selection" and
         control["selected_choice"] is None and
         control["native_or_runtime_use_allowed"] is False and
         control["authority_effect"] == "none", "wrong W07 control")
    pinned(control["original_wrapper_binding"])
    pinned(control["original_disposition_binding"])
    need(control["control_bindings"] == [{"path": SELECTION, "sha256": SELECTION_SHA256}],
         "wrong W07 selection")
    for fact in control["source_facts"]:
        need(fact["selector_kind"] == "json-pointer" and
             pointer(strict_json(pinned(fact["binding"])), fact["selector"]) == fact["exact_value"],
             "W07 source clause changed")
    need(selection["schema_version"] == "lab-W07-signed-integration-selection/v1-candidate" and
         selection["authority_effect"] == "none" and selection["actual_owner_outcome"] is None,
         "W07 selected posture differs")
    need([Path(row["path"]).parent.name for row in selection["cases"]] == list(DOMAINS),
         "four W07 cases differ")
    for row in selection["cases"]:
        pinned(row)
    join = strict_json(pinned(selection["parent_join_binding"]))
    need(join["cases"] == selection["cases"] and join["original_cases_reexecuted"] == 0,
         "W07 parent case join differs")
    parent = strict_json(pinned(selection["parent_workflow_proof_binding"]))
    need(parent["result"] == "PASS" and parent["task"] == "W07" and
         parent["original_domain_cases_reexecuted"] == 0,
         "W07 parent proof differs")
    need(receipt["result"] == "PASS" and receipt["task"] == "W07" and
         receipt["source_drift"] == [] and receipt["original_domain_effects_reexecuted"] == 0 and
         receipt["canonical_effects_applied"] == 0 and
         selection["parent_join_binding"] in receipt["source_bindings"] and
         selection["parent_workflow_proof_binding"] in receipt["source_bindings"] and
         selection["parent_coupling_proof_binding"] == receipt["signed_coupling_proof_binding"],
         "W07 receipt/parent lineage differs")
    warm = strict_json(pinned(receipt["warm_join_binding"]))
    need(warm["result"] == "PASS" and warm["domain_case_count"] == 4 and
         warm["original_domain_cases_reexecuted"] == 0,
         "W07 four-case warm join differs")
    need([row["domain"] for row in selection["signed_coupling_witnesses"]] ==
         ["engineering", "research"], "signed witness domain set differs")
    return warm


def semantic_digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode())


def signature_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2,
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


def verify_witness(witness, *, approval=None, result=None):
    domain = witness["domain"]
    need(domain in ("engineering", "research"), "unselected signed domain")
    case = strict_json(pinned(witness["case_binding"]))
    original_approval = strict_json(pinned(witness["approval_binding"]))
    original_result = strict_json(pinned(witness["result_binding"]))
    proposal = strict_json(pinned(witness["proposal_binding"]))
    expected = strict_json(pinned(witness["expected_replay_binding"]))
    pinned(witness["original_source_witnesses_binding"])
    archive = strict_json(pinned(witness["archive_binding"]))
    need(archive["private_key_included"] is False and archive["Session_memory_included"] is False and
         set(archive["files"]) == ARCHIVE_NAMES, "signed archive shape or privacy differs")
    decoded = {}
    original_bytes = {}
    for name, row in archive["files"].items():
        raw = base64.b64decode(row["base64_original_bytes"], validate=True)
        need(sha(raw) == row["sha256"], "signed archive member bytes differ")
        original_bytes[name] = raw
        decoded[name] = strict_json(raw)
    config, baseline, head = decoded["config.json"], decoded["baseline.json"], decoded["HEAD.json"]
    genesis, transaction = decoded["transactions/0000000000.json"], decoded["transactions/0000000001.json"]
    for value in (config, head, genesis, transaction):
        need(value["digest"] == semantic_digest({k: v for k, v in value.items() if k != "digest"}),
             "signed archive envelope seal differs")
    need(baseline["snapshot_digest"] == semantic_digest({k: v for k, v in baseline.items()
                                                           if k != "snapshot_digest"}) and
         archive["config_sha256"] == sha(original_bytes["config.json"]) == expected["config_sha256"] and
         archive["baseline_snapshot_digest"] == baseline["snapshot_digest"] ==
         expected["baseline_snapshot_digest"] == config["source_snapshot_digest"] and
         all(row["config_digest"] == config["digest"] and
             row["baseline_digest"] == baseline["snapshot_digest"]
             for row in (head, genesis, transaction)),
         "signed archive config/baseline lineage differs")
    need(head["sequence"] == 1 and genesis["sequence"] == 0 and
         transaction["sequence"] == 1 and transaction["previous_digest"] == genesis["digest"] and
         head["transaction_digest"] == transaction["digest"] and
         archive["expected_head"] == transaction["digest"] and
         expected["expected_head"] == transaction["digest"] and
         expected["source_binding"] == witness["archive_binding"] and
         expected["engine_pins"] == archive["engine_pins"] and
         expected["projection_sha256"] == transaction["projection_digest"],
         "signed archive head lineage differs")
    targets = transaction["proposal"]["targets"]
    need(len(targets) == len(expected["actual_targets"]) and
         all(row["version_ref"] == target["version_ref"] and
             row["carrier_ref"] == target["carrier_ref"] and
             row["record_structural_sha256"] == semantic_digest(target["record"]) and
             row["source_binding"]["selector"] == f"/proposal/targets/{index}/record" and
             row["source_binding"]["path"] == "transactions/0000000001.json" and
             row["source_binding"]["store_id"] == config["store_id"]
             for index, (target, row) in enumerate(zip(targets, expected["actual_targets"]))),
         "signed archive expected targets differ")
    chosen_approval = original_approval if approval is None else approval
    chosen_result = original_result if result is None else result
    need(transaction["approval"] == chosen_approval and transaction["proposal"] == proposal,
         "signed approval/proposal does not match replayed transaction")
    core = {k: v for k, v in chosen_approval.items() if k != "signature"}
    need(core["store_id"] == config["store_id"] and
         core["owner_ref"] == config["owner_ref"] and
         core["proposal_digest"] == semantic_digest(proposal) and
         core["decision_core_digests"] == [semantic_digest(item) for item in transaction["decision_cores"]] and
         core["expected_head"] == genesis["digest"],
         "signed approval core differs")
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(config["public_key"])).verify(
            bytes.fromhex(chosen_approval["signature"]), signature_bytes(core))
    except (ValueError, TypeError) as error:
        raise ValueError("signed approval signature differs") from error
    except Exception as error:
        raise ValueError("signed approval signature differs") from error
    need(case["domain"] == domain and chosen_result["domain"] == domain and
         chosen_result["source_case_binding"] == witness["case_binding"] and
         chosen_result["result"] == "PASS" and chosen_result["fixture_signature_verified"] is True and
         chosen_result["signed_transactions"] == 1 and
         chosen_result["canonical_admission"] is False and
         chosen_result["actual_owner_outcome"] is None and
         chosen_result["authority_effect"] == "none" and
         chosen_result == original_result,
         "signed witness result or source join differs")
    return {"domain": domain, "transaction_digest": transaction["digest"],
            "approval_sha256": witness["approval_binding"]["sha256"],
            "result_sha256": witness["result_binding"]["sha256"]}


def consume():
    control = strict_json(pinned({"path": CONTROL, "sha256": CONTROL_SHA256}))
    selection = strict_json(pinned({"path": SELECTION, "sha256": SELECTION_SHA256}))
    receipt = strict_json(pinned({"path": RECEIPT, "sha256": RECEIPT_SHA256}))
    validate_control(control, selection, receipt)
    witnesses = [verify_witness(row) for row in selection["signed_coupling_witnesses"]]
    return {"schema_version": "lab-t10-control-consumer/v1", "member_ref": control["member_ref"],
            "control_sha256": CONTROL_SHA256, "selection_sha256": SELECTION_SHA256,
            "receipt_sha256": RECEIPT_SHA256, "case_count": 4,
            "signature_verified_witnesses": witnesses, "result": "PASS",
            "effect": "read-only verification of historical signed candidate selection"}


if __name__ == "__main__":
    print(json.dumps(consume(), sort_keys=True, indent=2))
