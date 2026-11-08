"""Live one-Lesson Source8 API read and Session check with owned fixture custody."""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v33-t03-one-lesson-0002"
API_MANIFEST_SHA = "7c2405d840737eafa9b734f988b2129c1caa5f71d4bf564ed4db8015cef40b8d"
API_PROFILE_SHA = "9d5a7b82edfe4ffb8692f144b6cd62730396e8c4df7a9b54bcd486a40c9ee869"
FAMILY = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-eeb637eb2c57b67f"
SOURCE_SHA = "b9c62e104a56580f90951a42e480405f3a6d7ce3cd38aaa33936f5e7005c281e"
PERIOD_SHA = "417df19027529d7dc12e5191f601cc05bdc3eb724871a8560aa374b47c50ab58"


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned(path, digest):
    need(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == digest,
         "selected byte origin differs: " + str(path))


def loaded(name, file, *, package=False):
    spec = importlib.util.spec_from_file_location(
        name, file, submodule_search_locations=[str(file.parent)] if package else None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run():
    for path, digest in ((API / "source-manifest.json", API_MANIFEST_SHA),
                         (API / "contract-profile.json", API_PROFILE_SHA),
                         (FAMILY / "source/source-manifest.json", SOURCE_SHA),
                         (FAMILY / "source/packages/0001/period.json", PERIOD_SHA)):
        pinned(path, digest)
    period = json.loads((FAMILY / "source/packages/0001/period.json").read_bytes())
    now = datetime.now(timezone.utc)
    need(datetime.fromisoformat(period["not_before"]) <= now < datetime.fromisoformat(period["expires_at"]),
         "one-Lesson period not current")
    name = "_cal_t03_one_lesson_api33"
    loaded(name, API / "__init__.py", package=True)
    source = __import__(name + ".source_bridge", fromlist=["replay_source"])
    protocol = __import__(name + ".protocol", fromlist=["Schemas"])
    fixture = __import__(name + ".fixtures", fromlist=["provision"])
    auth = __import__(name + ".auth", fromlist=["ReaderChannel"])
    service_mod = __import__(name + ".service", fromlist=["Service"])
    handlers = __import__(name + ".handlers", fromlist=["cut"])
    sessions = __import__(name + ".current_context_sessions", fromlist=["D"])
    need(source.CURRENT_SOURCE8_NAME == "completion-current-participation:legacy-local-eeb637eb2c57b67f",
         "wrong current Source8 family")
    evidence = []
    with ExitStack() as stack:
        view = stack.enter_context(source.replay_source(source.CURRENT_SOURCE8_NAME))
        need(source.current_source8_view(view) and
             view.source8_context_producer.reader.HERE == FAMILY / "source",
             "actual one-Lesson signed Reader origin differs")
        schemas = protocol.Schemas(API_PROFILE_SHA)
        temp = tempfile.TemporaryDirectory(prefix="cal-t03-one-lesson-", dir="/tmp")
        root = Path(stack.enter_context(temp)); root.chmod(0o700)
        key, policy_path, _ = fixture.provision(root, source.CURRENT_SOURCE8_NAME,
                                               principal=period["principal_ref"])
        policy = protocol.frame_parse(policy_path.read_bytes())
        need(policy["session_control"]["period_binding"]["sha256"] == PERIOD_SHA,
             "one-Lesson period grant differs")
        policy["source8_control"] = {**source.source8_bindings(source.CURRENT_SOURCE8_NAME),
                                     "application_journal_scope": None}
        policy_raw = protocol.compact(policy)
        policy_path.write_bytes(policy_raw)
        channel = auth.ReaderChannel(policy_path, sha(policy_raw), schemas)
        authentication = channel.authenticate(fixture.proof(key, channel.challenge))
        context = authentication["context"]
        need(context == channel.context and context["principal_ref"] == period["principal_ref"],
             "Reader authentication differs")
        key = None
        service = service_mod.Service(view, channel, schemas)
        stack.callback(service.close)

        def invoke(request, expected="result"):
            raw = protocol.compact(request)
            reply = service.call(raw)
            need(schemas.valid("api-reply", reply) and
                 reply["request_binding"]["sha256"] == sha(raw),
                 "API reply schema/request binding differs")
            evidence.append({"operation": request["operation"], "request_sha256": sha(raw),
                             "reply_sha256": sha(protocol.compact(reply)),
                             "reply_kind": reply["kind"],
                             "code": reply.get("message", {}).get("code")})
            need(reply["kind"] == expected,
                 "operation " + request["operation"] + " returned " + str(reply.get("message", {}).get("code")))
            print(json.dumps(evidence[-1], sort_keys=True), flush=True)
            return reply["message"]

        cut = handlers.cut(view)
        invoke(fixture.call(context, "lab.status", cut))
        D = sessions.D
        message = D.query(view.custody_signed_sources, service.sessions.bridge)
        message["budget"].update(max_input_bytes=65536, max_output_bytes=1048576)
        request = fixture.call(context, "lab.status", cut)
        request.update(operation="context.get", message=message)
        delivery = invoke(request)
        need(delivery["source_cut"] == cut and delivery["posture"] == "ready",
             "one-Lesson Context delivery differs")
        ref = lambda identity: view.custody_signed_sources.sources.resolve(identity + "@" + D.records.VERSION)[0].artifact
        opening = fixture.call(context, "lab.status", cut)
        budget = opening["message"]["budget"]
        budget["max_actions"] = 1
        opening.update(operation="session.open", idempotency_key="open:" + uuid.uuid4().hex,
            message={"schema_version": "lab-agent-session-open/v1-candidate",
                     "request_ref": "request:T03-open:" + uuid.uuid4().hex,
                     "actor": opening["message"]["actor"],
                     "assignment": ref(D.records.ASSIGNMENT),
                     "profile": ref(D.records.PROFILE),
                     "implementation": ref(D.records.IMPLEMENTATION),
                     "capabilities": [ref(D.records.CAPABILITY)],
                     "context_delivery_binding": protocol.binding(
                         "context-delivery:" + delivery["context_view"]["version_ref"],
                         protocol.compact(delivery)),
                     "authority_envelope_binding": sessions.stable_policy(channel),
                     "source_cut": cut, "budget": budget,
                     "memory_policy": {"persistence_allowed": False, "expires_with_session": True},
                     "authority_effect": "none"})
        opened = invoke(opening)
        need(opened["posture"] == "active", "Session did not open")
        inspecting = fixture.call(context, "lab.status", cut)
        inspecting.update(operation="session.inspect", message={
            "schema_version": "lab-session-inspect-request/v1-candidate",
            "request_ref": "request:T03-inspect:" + uuid.uuid4().hex,
            "actor": inspecting["message"]["actor"],
            "session_ref": opened["session_ref"],
            "budget": inspecting["message"]["budget"], "authority_effect": "none"})
        state = invoke(inspecting)
        need(state["posture"] == "active", "live Session inspection differs")
        closing = fixture.call(context, "lab.status", cut)
        closing.update(operation="session.close", idempotency_key="close:" + uuid.uuid4().hex,
            message={"schema_version": "lab-agent-session-close/v1-candidate",
                     "request_ref": "request:T03-close:" + uuid.uuid4().hex,
                     "session_ref": opened["session_ref"],
                     "agent_instance_ref": opened["agent_instance_ref"],
                     "expected_session_binding": state["last_receipt_binding"],
                     "requested_at": datetime.now(timezone.utc).isoformat(),
                     "reason": "completed", "eligible_audit_bindings": [],
                     "authority_effect": "none"})
        closed = invoke(closing)
        need(closed["posture"] == "closed" and closed["discarded_memory"] is True,
             "Session cleanup differs")
        stale = fixture.call(context, "lab.status", cut)
        stale["deadline"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        stale["message"]["budget"]["deadline"] = stale["deadline"]
        invoke(stale, expected="error")
        original_policy = policy_path.read_bytes()
        policy_path.write_bytes(original_policy + b" ")
        revoked = fixture.call(context, "lab.status", cut)
        revoked_reply = service.call(protocol.compact(revoked))
        need(revoked_reply.get("code") == "unauthenticated-channel", "policy revocation was not refused")
        evidence.append({"operation": "lab.status", "reply_kind": "transport-error",
                         "code": revoked_reply["code"], "policy_revoked": True})
        print(json.dumps(evidence[-1], sort_keys=True), flush=True)
        policy_path.write_bytes(original_policy)
    need(not root.exists(), "owned private fixture survived")
    return {"schema_version": "lab-T03-one-Lesson-live-Session/v1-candidate",
            "api_manifest_sha256": API_MANIFEST_SHA,
            "family_source_sha256": SOURCE_SHA, "period_sha256": PERIOD_SHA,
            "operations": evidence, "owned_private_fixture_removed": True,
            "lesson_selected": False, "lesson_applied": False,
            "authority_effect": "none", "runner_sha256": sha(Path(__file__).read_bytes())}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
