#!/usr/bin/env python3
"""One owned current Source8 API33 call through the reviewed T35 observer."""
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

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v33-t35-current-reader-0001"
OBSERVER = ("implementation/lab-runtime/local-host/t35-phase-observer-current-reader-0001/observe.py",
            "ca9462797c085885bf45f26b3c3790afd9292227e1e41bde47adbba6ecb7d448")
SELECTION = ("implementation/lab-runtime/local-host/t35-phase-observer-current-reader-0001/selected-boundaries.json",
             "903956f1cdd1bc4825a83d1ecdc63870c4966202fc14192a1c97c44708adff75")
API_MANIFEST = ("product/lab/release-candidates/v1/interface/api-integration-v33-t35-current-reader-0001/source-manifest.json",
                "b7fe1be6e05c48856791fe010b0ba007c38424d552b3007c33b59e8729eda827")
PROFILE = ("product/lab/release-candidates/v1/interface/api-integration-v33-t35-current-reader-0001/contract-profile.json",
           "1000942922f152ba03561086664eedc1004fb1dc1f292f322182d903723f90f8")
SOURCE_MANIFEST = ("implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8/source/source-manifest.json",
                   "501e59318f2e0f504c4bd9cbf2c364e9901712cef33d785d67dd0a7107fa6a27")
SOURCE_PERIOD = ("implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8/source/packages/0001/period.json",
                 "2b2a740a1263e068cb26197089534138b77db4babbd3b04b0c1c72faf5d4c745")


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pinned(binding: tuple[str, str]) -> bytes:
    path = ROOT / binding[0]
    need(path.is_file() and path.resolve() == path and
         all(not ancestor.is_symlink() for ancestor in (path, *path.parents) if ancestor == ROOT or ROOT in ancestor.parents),
         "selected file absent or linked")
    raw = path.read_bytes()
    need(sha(raw) == binding[1], "selected file changed: " + binding[0])
    return raw


def utc(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    need(result.tzinfo is not None and result.utcoffset().total_seconds() == 0,
         "selected deadline is not UTC")
    return result.astimezone(timezone.utc)


def preflight(*, require_current: bool = True) -> dict:
    for binding in (OBSERVER, SELECTION, API_MANIFEST, PROFILE, SOURCE_MANIFEST):
        pinned(binding)
    period = json.loads(pinned(SOURCE_PERIOD))
    need(period["period_ref"] == "protocol:completion-legacy-local-947e6c2a5b3d10f8-period/v1" and
         period["authority_effect"] == "none" and
         utc(period["not_before"]) < utc(period["expires_at"]),
         "selected Source8 period differs")
    if require_current:
        need(utc(period["not_before"]) <= datetime.now(timezone.utc) < utc(period["expires_at"]),
             "selected Source8 period is not current")
    return period


def verify_result(result: dict) -> None:
    period = preflight(require_current=False)
    expected = [{"path": path, "sha256": digest} for path, digest in
                (OBSERVER, SELECTION, API_MANIFEST, PROFILE, SOURCE_MANIFEST, SOURCE_PERIOD)]
    need(result["schema_version"] == "lab-T35-current-source8-one-call/v1" and
         result["selected_bindings"] == expected and
         result["source_period_expires_at"] == period["expires_at"] and
         result["source_name"] == "completion-current-participation:legacy-local-947e6c2a5b3d10f8" and
         result["operation"] == "lab.status" and result["reply_kind"] == "result" and
         result["authority_effect"] == "none" and
         result["owned_temporary_fixture_removed"] is True and
         result["runner_sha256"] == sha(Path(__file__).read_bytes()),
         "one-call result selection or claim differs")
    origin = result["reader_lease_origin"]
    need(set(origin) == {"policy_sha256", "period_sha256", "authenticated_context"} and
         type(origin["policy_sha256"]) is str and len(origin["policy_sha256"]) == 64 and
         origin["period_sha256"] == SOURCE_PERIOD[1] and
         origin["authenticated_context"] is True and
         all(type(result[key]) is str and len(result[key]) == 64 for key in
             ("request_sha256", "reply_sha256")), "lease or operation digest origin differs")
    observation = result["observation"]
    need(observation["boundary_selection_sha256"] == SELECTION[1] and
         observation["measurement_class"] == "selected-candidate" and
         observation["callback_count"] == 1 and
         observation["pure_scope_boundary_count"] == 0 and
         observation["authority_effect"] == "none" and
         len(observation["events"]) == 1, "explicit boundary count differs")
    event = observation["events"][0]
    start, end = utc(event["started_at_utc"]), utc(event["completed_at_utc"])
    source_end, reader_end = utc(period["expires_at"]), utc(result["reader_lease_expires_at"])
    run_start, run_end = utc(result["started_at_utc"]), utc(result["completed_at_utc"])
    need(event["name"] == "Service.call" and event["kind"] == "callback" and
         event["status"] == "PASS" and event["exception_class"] is None and
         event["expired_at_completion"] is False and
         utc(observation["source_expires_at"]) == source_end and
         utc(event["strictest_observed_expires_at"]) == min(source_end, reader_end) and
         start <= end < min(source_end, reader_end) and
         abs((end - start).total_seconds() - event["monotonic_elapsed_seconds"]) < 0.05 and
         run_start <= start <= end <= run_end < source_end and
         abs((run_end - run_start).total_seconds() - result["monotonic_elapsed_seconds"]) < 0.25,
         "measured call clock, deadline or outcome differs")


def loaded(name: str, file: Path, *, package: bool = False):
    spec = importlib.util.spec_from_file_location(
        name, file, submodule_search_locations=[str(file.parent)] if package else None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run() -> dict:
    run_started = datetime.now(timezone.utc)
    run_start_ns = time.monotonic_ns()
    period = preflight()
    observer = loaded("_cal_t35_selected_observer", ROOT / OBSERVER[0])
    selected = observer.verify_boundary_selection(ROOT / SELECTION[0], SELECTION[1], ROOT)
    name = "_cal_t35_current_source8_api33"
    loaded(name, API / "__init__.py", package=True)
    source = __import__(name + ".source_bridge", fromlist=["replay_source"])
    protocol = __import__(name + ".protocol", fromlist=["Schemas"])
    fixtures = __import__(name + ".fixtures", fromlist=["provision"])
    auth = __import__(name + ".auth", fromlist=["ReaderChannel"])
    service_module = __import__(name + ".service", fromlist=["Service"])
    handlers = __import__(name + ".handlers", fromlist=["cut"])
    source_expiry = utc(period["expires_at"])
    with ExitStack() as stack:
        view = stack.enter_context(source.replay_source(source.CURRENT_SOURCE8_NAME))
        need(source.current_source8_view(view) and
             view.source8_context_producer.reader.HERE == ROOT / source.CURRENT_SOURCE8_SOURCE,
             "actual current Source8 view or Reader origin differs")
        temp = tempfile.TemporaryDirectory(prefix="cal-t35-current-source8-", dir="/tmp")
        root = Path(stack.enter_context(temp))
        root.chmod(0o700)
        schemas = protocol.Schemas(PROFILE[1])
        key, policy_path, _ = fixtures.provision(root, source.CURRENT_SOURCE8_NAME,
                                               principal=period["principal_ref"])
        policy = protocol.frame_parse(policy_path.read_bytes())
        need(policy["source_name"] == source.CURRENT_SOURCE8_NAME and
             policy["principal_ref"] == period["principal_ref"] and
             policy["session_control"]["period_binding"]["sha256"] == SOURCE_PERIOD[1],
             "provisioned current Source8 policy origin differs")
        policy["source8_control"] = {**source.source8_bindings(source.CURRENT_SOURCE8_NAME),
                                     "application_journal_scope": None}
        policy_raw = protocol.compact(policy)
        policy_path.write_bytes(policy_raw)
        policy_pin = sha(policy_raw)
        channel = auth.ReaderChannel(policy_path, policy_pin, schemas)
        authentication = channel.authenticate(fixtures.proof(key, channel.challenge))
        authenticated = authentication["context"]
        key = None
        need(authenticated == channel.context and
             authentication["trusted_context_binding"]["sha256"] ==
             sha(protocol.compact(authenticated)) and
             authenticated["principal_ref"] == period["principal_ref"] and
             utc(authenticated["expires_at"]) <= utc(policy["expires_at"]) <= source_expiry,
             "authenticated Reader lease origin differs")
        service = service_module.Service(view, channel, schemas)
        stack.callback(service.close)
        request = fixtures.call(authenticated, "lab.status", handlers.cut(view))
        raw = protocol.compact(request)
        ledger = observer.BoundaryLedger("T35-current-Source8-lab.status-0001", source_expiry, selected)
        reader_deadline = utc(authenticated["expires_at"])
        reply = ledger.callback(selected["Service.call"], service.call, service.call,
                                reader_deadline, raw)
        need(reply["kind"] == "result" and schemas.valid("api-reply", reply) and
             reply["request_binding"]["sha256"] == sha(raw),
             "observed current API33 reply differs")
        observation = ledger.result()
        need(observation["measurement_class"] == "selected-candidate" and
             observation["callback_count"] == 1 and observation["pure_scope_boundary_count"] == 0 and
             len(observation["events"]) == 1 and
             observation["events"][0]["name"] == "Service.call" and
             observation["events"][0]["status"] == "PASS", "actual selected call was not observed")
        result = {"schema_version": "lab-T35-current-source8-one-call/v1",
                  "selected_bindings": [{"path": path, "sha256": expected} for path, expected in
                                        (OBSERVER, SELECTION, API_MANIFEST, PROFILE, SOURCE_MANIFEST, SOURCE_PERIOD)],
                  "source_name": source.CURRENT_SOURCE8_NAME,
                  "source_period_expires_at": period["expires_at"],
                  "reader_lease_expires_at": authenticated["expires_at"],
                  "reader_lease_origin": {"policy_sha256": policy_pin,
                                          "period_sha256": SOURCE_PERIOD[1],
                                          "authenticated_context": True},
                  "operation": "lab.status", "request_sha256": sha(raw),
                  "reply_sha256": sha(protocol.compact(reply)),
                  "reply_kind": reply["kind"], "observation": observation,
                  "claim_ceiling": "One actual current Source8 API33 reader-successor lab.status Service.call under an authenticated Reader lease. Only this explicit callback is counted; nested callbacks, pure scopes, Session open, Machine calls and whole T35 remain unmeasured.",
                  "runner_sha256": sha(Path(__file__).read_bytes()),
                  "authority_effect": "none"}
    need(not root.exists(), "private temporary fixture survived cleanup")
    result["owned_temporary_fixture_removed"] = True
    result["started_at_utc"] = run_started.isoformat()
    result["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    result["monotonic_elapsed_seconds"] = (time.monotonic_ns() - run_start_ns) / 1e9
    verify_result(result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
