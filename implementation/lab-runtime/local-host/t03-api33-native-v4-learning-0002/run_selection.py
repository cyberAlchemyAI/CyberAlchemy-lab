"""Exercise one actual later-use Lesson selection in a fresh owned Session."""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v33-t03-one-lesson-native-v4-0004"
FAMILY = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-d95e3b741ca86f02"
API_SHA = "822bef0481a1ce2e050be1324a1059e9bd3f018b96fb290fb10776fbc648bc64"
PROFILE_SHA = "0d0fa9fd9f461a7e9c2f3775b397051d1518f23005a75483a8bf6143eaa7e02b"
PROVIDER = ROOT / "product/lab/release-candidates/v1/interface/source8-session-runtime-v1-action-0148/provider.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owned_snapshot(*roots):
    """Hash only owned regular files at the negative-call boundaries."""
    return {str(index) + ":" + str(path.relative_to(root)): sha(path)
            for index, root in enumerate(roots) for path in sorted(root.rglob("*"))
            if path.is_file() and not path.is_symlink()}


def selected(name, path, *, package=False):
    spec = importlib.util.spec_from_file_location(name, path,
        submodule_search_locations=[str(path.parent)] if package else None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    if sha(API / "source-manifest.json") != API_SHA or sha(API / "contract-profile.json") != PROFILE_SHA:
        raise ValueError("selected API source/profile changed")
    beginning = {"utc": datetime.now(timezone.utc).isoformat(), "monotonic_ns": time.monotonic_ns()}
    selected("_cal_t03_v4_lesson_api", API / "__init__.py", package=True)
    package = "_cal_t03_v4_lesson_api"
    provider = selected("_cal_t03_v4_lesson_provider", PROVIDER)
    materials = selected("_cal_t03_v4_lesson_materials", HERE / "lesson_materials.py")
    M = provider.modules(package)
    S = __import__(package + ".source_bridge", fromlist=["replay_source"])
    C = __import__(package + ".current_context_sessions", fromlist=["D"])
    F = M["fixtures"]
    P = M["protocol"]
    with ExitStack() as stack:
        view = stack.enter_context(S.replay_source(S.CURRENT_SOURCE8_NAME))
        if not S.current_source8_view(view):
            raise ValueError("wrong current signed Source8 view")
        selected_source = view.custody_signed_sources
        D = C.D
        material, plan = materials.prepare(M, D, selected_source)
        root = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="cal-t03-v4-lesson-", dir="/tmp")))
        root.chmod(0o700)
        key, policy_path, policy_sha = provider.provision(M, root, D, selected_source,
            S.CURRENT_SOURCE8_NAME, material)
        channel = M["auth"].ReaderChannel(policy_path, policy_sha, P.Schemas(PROFILE_SHA))
        reader_context = channel.authenticate(F.proof(key, channel.challenge))
        key = None
        service = M["service"].Service(view, channel, channel.schemas)
        stack.callback(service.close)
        context_reply, opened_reply, opening_raw = provider.opening(M, service, D)
        opened = opened_reply["message"]
        if opened["posture"] != "active":
            raise ValueError("later-use Session did not open")
        transport = M["machine_transport"]
        peer = transport.select(service, opened["session_ref"], {
            "path": str((API / "source-manifest.json").relative_to(ROOT)), "sha256": API_SHA})
        stack.callback(peer.close)
        machine_context = peer.authenticate(peer.proof())
        request = F.call(machine_context, "lab.status", M["handlers"].cut(view))
        bad_message = D.query(selected_source, service.sessions.bridge)
        bad_message["budget"].update(max_actions=0, max_input_bytes=65536, max_output_bytes=1048576)
        bad_request = F.call(machine_context, "lab.status", M["handlers"].cut(view))
        bad_request.update(operation="lesson.select", message=bad_message)
        bad_raw = P.compact(bad_request)
        before = owned_snapshot(service.vault.root, peer.service.vault.root)
        bad_reply = peer.call(bad_raw)
        after = owned_snapshot(service.vault.root, peer.service.vault.root)
        if (bad_reply.get("kind") != "error" or
                bad_reply.get("message", {}).get("code") != "unauthorized" or
                before != after):
            raise ValueError("wrong-bridge negative changed or caused an effect")
        message = D.query(selected_source, peer.service.sessions.bridge)
        message["budget"].update(max_actions=0, max_input_bytes=65536, max_output_bytes=1048576)
        request.update(operation="lesson.select", message=message)
        raw = P.compact(request)
        reply = peer.call(raw)
        if reply.get("kind") != "result":
            print(json.dumps({"phase":"lesson.select", "request_sha256":hashlib.sha256(raw).hexdigest(),
                "reply_sha256":hashlib.sha256(P.compact(reply)).hexdigest(),
                "reply_kind":reply.get("kind"), "reply_code":reply.get("message", {}).get("code", reply.get("code"))}),
                file=sys.stderr, flush=True)
            raise ValueError("lesson.select did not return result: " + str(reply.get("message", {}).get("code", reply.get("code"))))
        result = reply["message"]
        if result.get("schema_version") != "lab-lesson-selection/v1-candidate":
            raise ValueError("Lesson Selection contract differs")
        selected_items = [item for item in result["items"] if item["posture"] == "selected"]
        if len(selected_items) != 1:
            raise ValueError("actual later-use Lesson selection did not select exactly one")
        inspecting = F.call(reader_context, "lab.status", M["handlers"].cut(view))
        inspecting.update(operation="session.inspect", message={
            "schema_version": "lab-session-inspect-request/v1-candidate",
            "request_ref": "request:T03-later-inspect:" + uuid.uuid4().hex,
            "actor": service.sessions.bridge.actor(),
            "session_ref": opened["session_ref"],
            "budget": inspecting["message"]["budget"], "authority_effect": "none"})
        inspected_reply = service.call(P.compact(inspecting))
        if inspected_reply.get("kind") != "result" or inspected_reply["message"]["posture"] != "active":
            raise ValueError("later-use Session inspection failed")
        closing = F.call(reader_context, "lab.status", M["handlers"].cut(view))
        closing.update(operation="session.close", idempotency_key="close:" + uuid.uuid4().hex,
            message={"schema_version": "lab-agent-session-close/v1-candidate",
                     "request_ref": "request:T03-later-close:" + uuid.uuid4().hex,
                     "session_ref": opened["session_ref"],
                     "agent_instance_ref": opened["agent_instance_ref"],
                     "expected_session_binding": inspected_reply["message"]["last_receipt_binding"],
                     "requested_at": datetime.now(timezone.utc).isoformat(),
                     "reason": "completed", "eligible_audit_bindings": [],
                     "authority_effect": "none"})
        closed_reply = service.call(P.compact(closing))
        if closed_reply.get("kind") != "result" or closed_reply["message"]["posture"] != "closed":
            raise ValueError("later-use Session close failed")
        ending = {"utc": datetime.now(timezone.utc).isoformat(), "monotonic_ns": time.monotonic_ns()}
        receipt = {"schema_version": "lab-T03-native-v4-later-use-selection/v1-candidate",
            "api_manifest_sha256": API_SHA, "profile_sha256": PROFILE_SHA,
            "source_manifest_sha256": sha(FAMILY / "source/source-manifest.json"),
            "source_period": json.loads((FAMILY / "source/packages/0001/period.json").read_bytes()),
            "reader_policy_expires_at": channel.policy["expires_at"],
            "context_delivery_expires_at": context_reply["message"]["expires_at"],
            "session_expires_at": opened["expires_at"],
            "beginning": beginning, "ending": ending,
            "context_reply_sha256": hashlib.sha256(P.compact(context_reply)).hexdigest(),
            "session_open_reply_sha256": hashlib.sha256(P.compact(opened_reply)).hexdigest(),
            "lesson_request_sha256": hashlib.sha256(raw).hexdigest(),
            "lesson_reply_sha256": hashlib.sha256(P.compact(reply)).hexdigest(),
            "wrong_parent_bridge_negative": {"request_sha256": hashlib.sha256(bad_raw).hexdigest(),
                "reply_sha256": hashlib.sha256(P.compact(bad_reply)).hexdigest(),
                "code": bad_reply["message"]["code"],
                "owned_regular_file_state_unchanged": before == after},
            "session_inspect_reply_sha256": hashlib.sha256(P.compact(inspected_reply)).hexdigest(),
            "session_close_reply_sha256": hashlib.sha256(P.compact(closed_reply)).hexdigest(),
            "lesson_result": result,
            "lesson_selected": True,
            "lesson_applied": False,
            "lesson_assessed": False,
            "owned_private_fixture_removed": False,
            "authority_effect": "none"}
    receipt["owned_private_fixture_removed"] = not root.exists()
    return receipt


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, indent=2), flush=True)
