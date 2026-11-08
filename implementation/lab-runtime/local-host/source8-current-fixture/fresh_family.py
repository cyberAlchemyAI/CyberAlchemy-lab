"""Create and verify a fresh, self-issued Source8-shaped local test family.

This is an engineering fixture. Its keys are never enrolled as Lab issuers.
Each invocation consumes a new directory; an expired family is never renewed.
"""

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import secrets
import stat
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BUILDER = HERE.parent / "working/source8-docker-fixture-0002/builder.py"
OLD_PERIOD = ROOT / "product/lab/release-candidates/v1/interface/current-participation-v5/packages/0001/period.json"
OLD_PERIOD_SHA256 = "5d2184e3491509b6c8d15939d97c6f95609d5277c61bb8f3f0bbd911ff3f35e3"
OLD_FAMILY_PERIOD = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/fresh-legacy-current-runtime-preparation-0009/instances/legacy-source8-20261018-b/source/packages/0001/period.json"
OLD_FAMILY_PERIOD_SHA256 = "4ce3a3c7a6a0a21c8ebb5720392faad0055f89b35de1e319d56a2e9cc40c8200"
SCHEMA = "cal-source8-current-local-selection/v1"


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def module():
    require(BUILDER.is_file() and not BUILDER.is_symlink(), "BUILDER_ORIGIN_REFUSED")
    spec = importlib.util.spec_from_file_location("cal_source8_current_fixture_builder", BUILDER)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def retained_period():
    rows = []
    for path, expected in ((OLD_PERIOD, OLD_PERIOD_SHA256),
                           (OLD_FAMILY_PERIOD, OLD_FAMILY_PERIOD_SHA256)):
        require(path.is_file() and not path.is_symlink(), "OLD_PERIOD_ORIGIN_REFUSED")
        raw = path.read_bytes()
        require(sha(raw) == expected, "OLD_PERIOD_CHANGED")
        rows.append({"path": path.relative_to(ROOT).as_posix(), "sha256": expected})
    return rows


def instance_path(home, run_id):
    require(len(run_id) == 16 and all(c in "0123456789abcdef" for c in run_id), "RUN_ID_REFUSED")
    require(home.is_dir() and not home.is_symlink(), "HOME_REFUSED")
    require(not home.resolve().is_relative_to(ROOT.resolve()), "HOME_INSIDE_REPOSITORY_REFUSED")
    metadata = home.stat()
    require(metadata.st_uid == os.getuid() and stat.S_IMODE(metadata.st_mode) == 0o700,
            "PRIVATE_HOME_REQUIRED")
    return home / run_id


def safe_family_paths(path):
    for leaf in ("inputs", "inputs/synthetic-input.json", "family", "family/public",
                 "family/protected"):
        selected = path / leaf
        require(selected.exists() and not selected.is_symlink(), "FAMILY_PATH_REFUSED")
    for folder in (path / "inputs", path / "family/public", path / "family/protected"):
        require(all(not child.is_symlink() for child in folder.iterdir()), "FAMILY_PATH_REFUSED")


def create(home, *, run_id=None, now=None):
    builder = module()
    run_id = run_id or secrets.token_hex(8)
    now = now or dt.datetime.now(dt.timezone.utc)
    require(now.tzinfo is not None and now.utcoffset() == dt.timedelta(0), "UTC_REQUIRED")
    require(abs((now - dt.datetime.now(dt.timezone.utc)).total_seconds()) <= 5,
            "ACTUAL_CLOCK_REQUIRED")
    old = retained_period()
    path = instance_path(home, run_id)
    require(not path.exists() and not path.is_symlink(), "CONSUMED_INSTANCE_REFUSED")
    path.mkdir(mode=0o700)
    inputs = path / "inputs"
    inputs.mkdir(mode=0o700)
    records = {kind: {"kind": kind, "identity": f"synthetic:{run_id}:{kind}"}
               for kind in builder.KINDS}
    value = {"schema": "cal-source8-synthetic-protected-input/v1", "run_id": run_id,
             "records": records, "profile": {"name": "synthetic-profile", "version": 1}}
    raw = builder.canonical(value)
    builder.write_new(inputs, "synthetic-input.json", raw)
    family = path / "family"
    built = builder.construct(inputs, family, run_id, now)
    audited = builder.audit(inputs, family, run_id, now)
    require(built["terminal_sha256"] == audited["terminal_sha256"] and
            audited["status"] == "PASS_SYNTHETIC_UNENROLLED", "COLD_AUDIT_REFUSED")
    selection = {"schema": SCHEMA, "run_id": run_id, "kind": "synthetic-local-fixture",
                 "input_sha256": sha(raw), "builder_sha256": sha(BUILDER.read_bytes()),
                 "source_sha256": audited["source_sha256"],
                 "terminal_sha256": audited["terminal_sha256"],
                 "old_period_bindings": old, "not_before": builder.stamp(now),
                 "expires_at": builder.stamp(now + dt.timedelta(hours=24)),
                 "authority_effect": "none"}
    builder.write_new(path, "selection.json", builder.canonical(selection))
    return selection


def select(home, run_id, *, now=None):
    """Accept only this constructor's current signed family and exact run ID."""
    builder = module()
    now = now or dt.datetime.now(dt.timezone.utc)
    path = instance_path(home, run_id)
    require(path.is_dir() and not path.is_symlink(), "INSTANCE_ORIGIN_REFUSED")
    safe_family_paths(path)
    selection_path = path / "selection.json"
    require(selection_path.is_file() and not selection_path.is_symlink(), "SELECTION_ORIGIN_REFUSED")
    selected = json.loads(selection_path.read_bytes())
    require(set(selected) == {"schema", "run_id", "kind", "input_sha256", "builder_sha256",
                              "source_sha256", "terminal_sha256", "old_period_bindings",
                              "not_before", "expires_at", "authority_effect"} and
            selected["schema"] == SCHEMA and selected["run_id"] == run_id and
            selected["kind"] == "synthetic-local-fixture" and
            selected["authority_effect"] == "none", "WRONG_CONSTRUCTOR_REFUSED")
    require(selected["builder_sha256"] == sha(BUILDER.read_bytes()), "BUILDER_CHANGED")
    require(selected["old_period_bindings"] == retained_period(), "OLD_PERIOD_CHANGED")
    require(builder.checked_time(selected["not_before"]) <= now <
            builder.checked_time(selected["expires_at"]) and
            builder.checked_time(selected["expires_at"]) -
            builder.checked_time(selected["not_before"]) == dt.timedelta(hours=24),
            "SOURCE_PERIOD_REFUSED")
    observed = builder.audit(path / "inputs", path / "family", run_id, now)
    require(observed["source_sha256"] == selected["source_sha256"] and
            observed["terminal_sha256"] == selected["terminal_sha256"] and
            selected["input_sha256"] == sha((path / "inputs/synthetic-input.json").read_bytes()),
            "SIGNED_FAMILY_BINDING_REFUSED")
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("home", type=Path)
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--select", metavar="RUN_ID")
    args = parser.parse_args()
    require(args.create != bool(args.select), "ONE_ACTION_REQUIRED")
    value = create(args.home) if args.create else select(args.home, args.select)
    print(json.dumps({"status": "PASS_LOCAL_SYNTHETIC", "run_id": value["run_id"],
                      "source_sha256": value["source_sha256"],
                      "authority_effect": "none"}, sort_keys=True))


if __name__ == "__main__":
    main()
