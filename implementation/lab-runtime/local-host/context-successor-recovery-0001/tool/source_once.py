"""One-shot Source build and signed cold replay. DO NOT RUN before release review.

This is the proposed effectful entrypoint. It is intentionally not called by
the static test suite or the inert Docker preflight.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path

from preflight import FAMILY, ROOT, TOOL, main as inert_preflight


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def current(episode: dict, *, now: dt.datetime | None = None,
            plan: dict | None = None) -> None:
    now = now or dt.datetime.now(dt.timezone.utc)
    start = dt.datetime.fromisoformat(episode["not_before"])
    end = dt.datetime.fromisoformat(episode["expires_at"])
    require(start <= now < end and end - start == dt.timedelta(hours=24),
            "fresh development episode period not current")
    require(episode["max_session_seconds"] == 900 and
            episode["principal_ref"] == "principal:R03-docker-source-20261020-0002" and
            episode["assignment_version_ref"] == "agent-assignment:R03-docker-source-20261020-0002@1.0.0-candidate.1" and
            episode["period_ref"] == "protocol:R03-docker-source-20261020-0002-period/v1" and
            episode["authority_effect"] == "none" and
            episode["actual_owner_outcome"] is None,
            "development episode authority or duration differs")
    plan = plan if plan is not None else json.loads((TOOL / "public-cut.json").read_bytes())
    require(episode["authorization_binding"] == plan["new_authorization"],
            "development authorization binding differs")


def import_source_package():
    # The code paths were selected and verified by inert preflight against the
    # read-only input mount before this import. The output submount is distinct.
    package_name = "_cal_docker_source_20261020_0001"
    entry = FAMILY / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        package_name, entry, submodule_search_locations=[str(FAMILY)])
    require(spec is not None and spec.loader is not None, "Source package loader unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[package_name] = module
    spec.loader.exec_module(module)
    build_spec = importlib.util.spec_from_file_location(package_name + ".build", FAMILY / "build.py")
    require(build_spec is not None and build_spec.loader is not None, "Source build loader unavailable")
    build = importlib.util.module_from_spec(build_spec)
    sys.modules[build_spec.name] = build
    build_spec.loader.exec_module(build)
    cold_spec = importlib.util.spec_from_file_location(package_name + ".cold", FAMILY / "cold.py")
    require(cold_spec is not None and cold_spec.loader is not None, "Source cold loader unavailable")
    cold = importlib.util.module_from_spec(cold_spec)
    sys.modules[cold_spec.name] = cold
    cold_spec.loader.exec_module(cold)
    return build, cold


def selected_inputs_unchanged(plan: dict) -> None:
    for row in plan["public_inputs"] + plan["generated_bindings"]:
        path = ROOT / row["path"]
        require(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == row["sha256"],
                "selected Source input changed: " + row["path"])


def run() -> dict:
    preflight = inert_preflight(require_output_mounts=True)
    require(preflight["result"] == "PASS" and preflight["source_effect"] == "NOT_RUN",
            "independent inert preflight required")
    plan = json.loads((TOOL / "public-cut.json").read_bytes())
    episode = json.loads((FAMILY / "episode-contract.json").read_bytes())
    current(episode)
    source_pin = plan["source_manifest"]["sha256"]
    require(sha((FAMILY / "source-manifest.json").read_bytes()) == source_pin and
            not (FAMILY / "packages/0001").exists(),
            "fresh selected Source package required")
    build, cold = import_source_package()
    # The historical builder prints a provisional PASS before cold verification.
    # Never forward that line as the final verdict.
    provisional = io.StringIO()
    with contextlib.redirect_stdout(provisional):
        build.main(source_pin)
    lines = provisional.getvalue().splitlines()
    require(len(lines) == 1 and json.loads(lines[0])["result"] == "PASS",
            "Source builder terminal result differs")
    build_result = json.loads((FAMILY / "packages/0001/build-result.json").read_bytes())
    require(build_result["result"] == "PASS" and
            build_result["authored_current_artifacts"] == 11 and
            build_result["authored_current_typed_relations"] == 10 and
            build_result["signed_transactions"] == 2 and
            build_result["owned_store_and_key_removed"] is True and
            not Path(build_result["owned_root"]).exists(),
            "Source build counts or temporary signer/store cleanup differ")
    manifest = FAMILY / "packages/0001/manifest.json"
    require(manifest.is_file() and not manifest.is_symlink(), "Source package manifest absent")
    package_pin = sha(manifest.read_bytes())
    current(episode)
    with cold.open_source(source_pin, package_pin) as view:
        require(view.data["head"]["sequence"] == 2 and
                len(view.data["transactions"]) == 3 and
                view.expected["authority_effect"] == "none" and
                view.expected["actual_owner_outcome"] is None,
                "signed cold Source cut differs")
    current(episode)
    selected_inputs_unchanged(plan)
    require(sha(manifest.read_bytes()) == package_pin, "package changed after cold replay")
    return {"schema_version": "lab-source-only-docker-result/v1-development",
            "result": "PASS", "source_manifest_sha256": source_pin,
            "package_manifest_sha256": package_pin,
            "signed_transactions": 2, "authored_records": 11,
            "authored_typed_relations": 10,
            "cold_replay": "PASS", "authority_effect": "none",
            "actual_owner_outcome": None,
            "claim_ceiling": "New disposable local Source package and signed cold replay only; no Reader/Mapper/Context or protected Source8 qualification."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-reviewed-one-shot", action="store_true")
    ns = parser.parse_args()
    require(ns.execute_reviewed_one_shot, "reviewed one-shot release flag required")
    print(json.dumps(run(), sort_keys=True), flush=True)
