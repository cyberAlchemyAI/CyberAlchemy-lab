"""Exact d95 later-use diagnostic for API lesson.apply preclaim failure.

The application and assessment are unadmitted diagnostic candidates. Their
actual API replies, not this driver, determine the outcome.
"""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0001"
FAMILY = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-d95e3b741ca86f02"
API_SHA = "d9f4055c19b91939db4ba1029336fc2987b64ebcd2e92219a852df7b9ad6115c"
PROFILE_SHA = "b46151f27df0a42bc7e2ab206bc8bf43e812e2b75073a24c303e853693ea2fe0"
PROVIDER = ROOT / "product/lab/release-candidates/v1/interface/source8-session-runtime-v1-action-0148/provider.py"
LIFECYCLE = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T35/full-learning-driver-0005/positive_lifecycle.py"
LIFECYCLE_SHA = "0af8fece332548b4331225232d0b09ccdec845636ed747d883dbc8308ff41b82"
MARGIN = ROOT / "implementation/lab-runtime/local-host/t03-d95-margin-api-recut-0002/margin.py"
APPLICATION_METHOD = API.parent / "lesson-application-v4-completion-0001/preparation.py"
ASSESSMENT_METHOD = API.parent / "lesson-assessment-v2-action-0148/preparation.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def instant(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("unqualified expiry instant")
    return parsed.astimezone(timezone.utc)


def require_current(label, *expiries):
    now = datetime.now(timezone.utc)
    if not all(now < instant(value) for value in expiries):
        raise ValueError(label + " expired before the actual operation")
    return now.isoformat()


def journal_snapshot(root):
    if root is None:
        return None
    path = Path(root) / "journal"
    if not path.is_dir() or path.is_symlink():
        raise ValueError("owned regular-file journal unavailable")
    result = {}
    for member in sorted(path.rglob("*")):
        if member.is_symlink():
            raise ValueError("owned journal contains a symlink")
        if member.is_file():
            result[str(member.relative_to(path))] = sha(member)
    return result


def module(name, path, *, package=False):
    spec = importlib.util.spec_from_file_location(
        name, path, submodule_search_locations=[str(path.parent)] if package else None)
    selected = importlib.util.module_from_spec(spec)
    sys.modules[name] = selected
    spec.loader.exec_module(selected)
    return selected


def stage(name):
    row = {"phase": name, "started_utc": datetime.now(timezone.utc).isoformat(),
           "started_monotonic_ns": time.monotonic_ns()}
    print(json.dumps({"stage": name, "utc": row["started_utc"],
                      "monotonic_ns": row["started_monotonic_ns"]}, sort_keys=True),
          file=sys.stderr, flush=True)
    return row


def finish(row, phases):
    row["ended_utc"] = datetime.now(timezone.utc).isoformat()
    row["ended_monotonic_ns"] = time.monotonic_ns()
    row["elapsed_seconds"] = (row["ended_monotonic_ns"] - row["started_monotonic_ns"]) / 1e9
    phases.append(row)
    print(json.dumps({"stage_complete": row["phase"], "elapsed_seconds": row["elapsed_seconds"]},
                     sort_keys=True), file=sys.stderr, flush=True)


def main():
    if (sha(API / "source-manifest.json") != API_SHA or
            sha(API / "contract-profile.json") != PROFILE_SHA or
            sha(LIFECYCLE) != LIFECYCLE_SHA):
        raise ValueError("selected API/profile/lifecycle bytes changed")
    beginning = {"utc": datetime.now(timezone.utc).isoformat(), "monotonic_ns": time.monotonic_ns()}
    package = "_cal_t03_d95_preclaim_diagnostic_api"
    module(package, API / "__init__.py", package=True)
    provider = module("_cal_t03_d95_full_provider", PROVIDER)
    materials = module("_cal_t03_d95_full_materials", HERE / "lesson_materials.py")
    lifecycle = module("_cal_t03_d95_full_lifecycle", LIFECYCLE)
    margin_class = module("_cal_t03_d95_full_margin", MARGIN).DiagnosticMargin
    M = provider.modules(package)
    S = importlib.import_module(package + ".source_bridge")
    C = importlib.import_module(package + ".current_context_sessions")
    F, P = M["fixtures"], M["protocol"]
    events, roots, phases = [], [], []
    load_configuration = {"logical_cpus": os.cpu_count(), "load_average_at_start": os.getloadavg(),
                          "driver_native_processes": 1, "driver": "single-process"}
    phase = stage("signed-source-replay")
    with ExitStack() as stack:
        view = stack.enter_context(S.replay_source(S.CURRENT_SOURCE8_NAME))
        if not S.current_source8_view(view):
            raise ValueError("wrong current signed Source8 view")
        finish(phase, phases)
        selected = view.custody_signed_sources
        D = C.D
        material, plan = materials.prepare(M, D, selected)
        root = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="cal-t03-d95-full-", dir="/tmp")))
        root.chmod(0o700)
        roots.append(str(root))
        key, policy_path, policy_sha = provider.provision(M, root, D, selected,
            S.CURRENT_SOURCE8_NAME, material)
        channel = M["auth"].ReaderChannel(policy_path, policy_sha, P.Schemas(PROFILE_SHA))
        stack.callback(channel.close)
        channel.authenticate(F.proof(key, channel.challenge))
        key = None
        parent = M["service"].Service(view, channel, channel.schemas)
        stack.callback(parent.close)
        diagnostic = margin_class(package)
        stack.callback(diagnostic.close)
        phase = stage("context-and-session-open")
        context_reply, opened_reply, opening_raw = provider.opening(M, parent, D)
        finish(phase, phases)
        opened = opened_reply["message"]
        if opened["posture"] != "active":
            raise ValueError("later-use Session did not open")
        period = json.loads((FAMILY / "source/packages/0001/period.json").read_bytes())
        print(json.dumps({"stage":"actual-lease-bounds","utc":datetime.now(timezone.utc).isoformat(),
            "context_delivery_expires_at":context_reply["message"]["expires_at"],
            "session_expires_at":opened["expires_at"],
            "reader_expires_at":channel.policy["expires_at"],
            "source_expires_at":period["expires_at"]},sort_keys=True),file=sys.stderr,flush=True)
        require_current("new Session", period["expires_at"], channel.policy["expires_at"],
                        context_reply["message"]["expires_at"], opened["expires_at"])
        parent_resource = parent.sessions.live[opened["session_ref"]]
        peer = M["machine_transport"].select(parent, opened["session_ref"], {
            "path": str((API / "source-manifest.json").relative_to(ROOT)), "sha256": API_SHA})
        stack.callback(peer.close)
        machine_context = peer.authenticate(peer.proof())
        query = D.query(selected, peer.service.sessions.bridge)
        query["budget"].update(max_actions=0, max_input_bytes=65536, max_output_bytes=1048576)
        request = F.call(machine_context, "lab.status", M["handlers"].cut(view))
        request.update(operation="lesson.select", message=query)
        raw_selection = P.compact(request)
        selection_started_at = require_current("lesson.select", period["expires_at"],
            channel.policy["expires_at"], context_reply["message"]["expires_at"], opened["expires_at"])
        phase = stage("lesson-select")
        selection_reply = peer.call(raw_selection)
        finish(phase, phases)
        if selection_reply.get("kind") != "result":
            raise ValueError("actual Lesson selection failed: " + str(selection_reply.get("message", {}).get("code", selection_reply.get("code"))))
        selection = selection_reply["message"]
        if selection.get("schema_version") != "lab-lesson-selection/v1-candidate" or len(
                [row for row in selection["items"] if row["posture"] == "selected"]) != 1:
            raise ValueError("exact one-Lesson selection absent")

        def invoke(surface, req, label, expect, root=None):
            raw = P.compact(req)
            before = journal_snapshot(root)
            reply = surface.call(raw)
            after = journal_snapshot(root)
            if reply.get("kind") != expect:
                print(json.dumps({"stage": "native-api-error", "label": label,
                    "operation": req["operation"], "request_sha256": hashlib.sha256(raw).hexdigest(),
                    "reply_sha256": hashlib.sha256(P.compact(reply)).hexdigest(),
                    "reply_kind": reply.get("kind"), "public_error": reply.get("message"),
                    "owned_regular_file_journal_unchanged": before == after,
                    "journal_entries_before": 0 if before is None else len(before),
                    "journal_entries_after": 0 if after is None else len(after)},
                    sort_keys=True), file=sys.stderr, flush=True)
                raise ValueError(label + " returned " + str(reply.get("kind")) + ":" +
                                 str(reply.get("message", {}).get("code", reply.get("code"))))
            return reply
        def pair(host, req, root=None, surface=None):
            if surface is None:
                surface = importlib.import_module(package + ".integration_dispatch").IntegrationService(host)
            phase = stage("native-api:" + req["operation"])
            try:
                return invoke(surface, req, "lesson-positive:" + req["operation"], "result", root=root)
            finally:
                finish(phase, phases)
        lifecycle.API = API
        lifecycle.SOURCE_NAME = S.CURRENT_SOURCE8_NAME
        lifecycle.APPLICATION_METHOD = APPLICATION_METHOD
        lifecycle.ASSESSMENT_METHOD = ASSESSMENT_METHOD
        lifecycle.OWNED_TEMPORARY = lambda prefix: tempfile.TemporaryDirectory(prefix=prefix, dir="/tmp")
        lifecycle.MARGIN_COMPOSITION = diagnostic.compose_margin
        lifecycle.pair = pair
        lifecycle.invoke = invoke
        lifecycle.bind = lambda path: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
        application_started_at = require_current("Lesson application and assessment", period["expires_at"],
            channel.policy["expires_at"], context_reply["message"]["expires_at"], opened["expires_at"])
        phase = stage("lesson-application-and-assessment")
        cases = lifecycle.source8_lifecycle(stack, provider, M, D, selected, parent,
                                             selection, events, roots)
        finish(phase, phases)
        if parent_resource.closed or parent.sessions.live.get(opened["session_ref"]) is not parent_resource:
            raise ValueError("attached Lesson operator closed the parent Session")
        inspecting = F.call(channel.context, "lab.status", M["handlers"].cut(view))
        inspecting.update(operation="session.inspect", message={
            "schema_version": "lab-session-inspect-request/v1-candidate",
            "request_ref": "request:T03-full-inspect:" + uuid.uuid4().hex,
            "actor": parent.sessions.bridge.actor(),
            "session_ref": opened["session_ref"],
            "budget": inspecting["message"]["budget"], "authority_effect": "none"})
        phase = stage("session-inspect")
        inspected_reply = parent.call(P.compact(inspecting))
        finish(phase, phases)
        if inspected_reply.get("kind") != "result" or inspected_reply["message"]["posture"] != "active":
            raise ValueError("parent Session inspection failed")
        closing = F.call(channel.context, "lab.status", M["handlers"].cut(view))
        closing.update(operation="session.close", idempotency_key="close:" + uuid.uuid4().hex,
            message={"schema_version": "lab-agent-session-close/v1-candidate",
                     "request_ref": "request:T03-full-close:" + uuid.uuid4().hex,
                     "session_ref": opened["session_ref"],
                     "agent_instance_ref": opened["agent_instance_ref"],
                     "expected_session_binding": inspected_reply["message"]["last_receipt_binding"],
                     "requested_at": datetime.now(timezone.utc).isoformat(),
                     "reason": "completed", "eligible_audit_bindings": [],
                     "authority_effect": "none"})
        closing_started_at = require_current("Session close", period["expires_at"],
            channel.policy["expires_at"], context_reply["message"]["expires_at"], opened["expires_at"])
        phase = stage("session-close")
        closed_reply = parent.call(P.compact(closing))
        finish(phase, phases)
        if closed_reply.get("kind") != "result" or closed_reply["message"]["posture"] != "closed":
            raise ValueError("parent Session close failed")
        if not parent_resource.closed:
            raise ValueError("parent Session remained live")
        margin_receipt = diagnostic.public_receipt()
        ending = {"utc": datetime.now(timezone.utc).isoformat(), "monotonic_ns": time.monotonic_ns()}
        recorded = [{"operation": row["operation"], "case": row.get("case"),
                     "reply_sha256": hashlib.sha256(P.compact(row["reply"])).hexdigest(),
                     "reply_kind": row["reply"].get("kind")}
                    for row in events if "reply" in row]
        if not any(row["operation"] == "lesson.apply" and row["reply_kind"] == "result" for row in recorded):
            raise ValueError("actual Lesson Application reply absent")
        if not any(row["operation"] == "lesson.assess" and row["reply_kind"] == "result" for row in recorded):
            raise ValueError("actual Lesson Assessment reply absent")
        receipt = {"schema_version": "lab-T03-native-v4-later-use-full-lifecycle/v1-candidate",
            "api_manifest_sha256": API_SHA, "profile_sha256": PROFILE_SHA,
            "source_manifest_sha256": sha(FAMILY / "source/source-manifest.json"),
            "source_period": json.loads((FAMILY / "source/packages/0001/period.json").read_bytes()),
            "reader_policy_expires_at": channel.policy["expires_at"],
            "context_delivery_expires_at": context_reply["message"]["expires_at"],
            "session_expires_at": opened["expires_at"],
            "beginning": beginning, "ending": ending,
            "phase_timings": phases, "load_configuration": load_configuration,
            "selection_started_at": selection_started_at,
            "application_started_at": application_started_at,
            "closing_started_at": closing_started_at,
            "context_reply_sha256": hashlib.sha256(P.compact(context_reply)).hexdigest(),
            "session_open_reply_sha256": hashlib.sha256(P.compact(opened_reply)).hexdigest(),
            "lesson_request_sha256": hashlib.sha256(raw_selection).hexdigest(),
            "lesson_reply_sha256": hashlib.sha256(P.compact(selection_reply)).hexdigest(),
            "session_inspect_reply_sha256": hashlib.sha256(P.compact(inspected_reply)).hexdigest(),
            "session_close_reply_sha256": hashlib.sha256(P.compact(closed_reply)).hexdigest(),
            "lesson_result": selection, "lifecycle_cases": cases, "lifecycle_events": recorded,
            "margin": margin_receipt,
            "lesson_selected": True, "lesson_applied": True, "lesson_assessed": True,
            "effectiveness_claimed": False, "authority_effect": "none"}
    receipt["owned_private_fixture_roots_removed"] = all(not Path(path).exists() for path in roots)
    if not receipt["owned_private_fixture_roots_removed"]:
        raise ValueError("owned private fixture cleanup incomplete")
    receipt["private_margin_configuration_removed"] = not diagnostic.root.exists()
    if not receipt["private_margin_configuration_removed"]:
        raise ValueError("private diagnostic margin configuration survived cleanup")
    return receipt


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, indent=2), flush=True)
