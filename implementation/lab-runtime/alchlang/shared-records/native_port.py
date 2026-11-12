"""Delegate to the original selected native store and workspace owner."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "implementation/lab-runtime/v2"))
sys.path.insert(0, str(ROOT / "implementation/lab-workspaces/v2"))
from lab_runtime.store import Store
from lab_runtime.common import digest, byte_digest, encoded
import workspaces

from jsonschema import Draft202012Validator
from schema_metadata_cache import install
install(Draft202012Validator)

request = json.load(sys.stdin)
action = request["action"]
store = Store((request.get("store") or ROOT / ".local/lab-runtime/v2/store"), ROOT)
if action == "digest":
    result = {"digest": digest(request["value"])}
elif action == "context":
    profile = workspaces.load(request["workspace"])
    catalog = workspaces.load(request["catalog"])
    result = workspaces.resolve(profile, catalog, project_ref=request.get("project"),
                                goal_ref=request.get("goal"), work=request.get("work"),
                                expected_revision=request.get("workspace_revision"))
    if request.get("store"):
        data = store.replay(require_current=True)
        project = data["projection"]["state"]["payload"]["project_ref"]
        if result["project_ref"] != project:
            raise ValueError("native-project-context-mismatch")
        result.update(native_head=data["head"], native_config=data["config"],
                      native_source=data["baseline"]["snapshot_digest"])
elif action == "create":
    sys.path.insert(0, str(ROOT / "implementation/lab-runtime/alchlang/ports"))
    from creation import create_draft
    result = create_draft(
        store, request["file"], kind=request["kind"], project=request["project"],
        scope=request.get("scope", "project"), work=request.get("work"),
        carrier=request["carrier"], version=request.get("version"),
        decision=request["decision"], proposal_id=request["proposal_id"], output=request["output"],
        schema_source=request.get("schema"), contract_source=request.get("contract"), owner=request.get("owner")
    )
elif action == "apply":
    result = store.apply(request["proposal"], request["approval"])
elif action == "review":
    result = store.review(request["proposal"])
elif action == "recover":
    result = store.recover(request["expected_head"])
elif action == "committed":
    data = store.replay()
    transactions = [item for item in data["transactions"][1:] if item.get("proposal", {}).get("proposal_id") == request["operation"]]
    if len(transactions) != 1:
        raise ValueError("original-native-operation-not-committed")
    item = transactions[0]
    proposal = item["proposal"]
    original_transaction = (store.path / "transactions" / (str(item["sequence"]).zfill(10) + ".json")).read_bytes()
    result = {"proposal": proposal, "approval": item["approval"],
              "original_receipt": {"ref": "native-transaction:" + item["digest"],
                                   "sha256": byte_digest(original_transaction), "bytes": str(len(original_transaction))},
              "proposal_digest": digest(proposal), "targets_digest": digest(proposal["targets"]),
              "expected_head": proposal["expected_head"], "source_cut": proposal["source_snapshot_digest"],
              "transaction": item["digest"], "targets": proposal["targets"],
              "resolved_records": [target["record"] if target["record"] is not None else data["projection"]["subjects"][target["version_ref"]]["record"] for target in proposal["targets"]]}
elif action == "summary":
    data = store.replay(require_current=request.get("require_current", False))
    definitions = [e for e in data["projection"]["subjects"].values() if e["category"] == "definition"]
    current = [e for e in definitions if e["effective_state"] in ("admitted-current", "local-admitted-current")]
    result = {"baseline": {"snapshot_digest": data["baseline"]["snapshot_digest"]}, "head": data["head"], "freshness": data["freshness"], "definitions": {"versions": len(definitions), "current": len(current), "current_v2": sum(e["record"]["schema_version"] == "cyberalchemy-lab-definition/v2" for e in current)}}
elif action == "replay":
    result = store.replay(require_current=request.get("require_current", False))
else:
    raise ValueError("unknown-native-port-operation")
print(json.dumps(result))
