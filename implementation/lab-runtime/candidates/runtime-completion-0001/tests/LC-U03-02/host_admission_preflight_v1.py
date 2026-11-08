"""Read-only LC-U03-02 host admission preflight; never qualifies a runtime.

The disposable cgroup oracle demonstrates mechanics. This preflight prevents
that evidence from being mistaken for selected exclusive host custody. It does
not create cgroups, start processes, signal PIDs, or inspect protected data.
"""
import json
import os
from pathlib import Path
import pwd
import sys


REQUIRED_CONTROLLERS = frozenset({"cpu", "memory", "pids"})


def snapshot():
    root = Path("/sys/fs/cgroup")
    mounts = Path("/proc/self/mountinfo").read_text().splitlines()
    cgroup2_root = any(" - cgroup2 " in line and line.split()[4] == "/sys/fs/cgroup" for line in mounts)
    membership = Path("/proc/self/cgroup").read_text().strip().splitlines()
    accounts = sorted({entry.pw_uid for entry in pwd.getpwall() if 0 < entry.pw_uid < 65534})
    return {
        "broker_uid": os.getuid(),
        "self_cgroup": membership[0] if len(membership) == 1 else None,
        "cgroup2_root_mounted": cgroup2_root,
        "root_uid": root.stat().st_uid,
        "root_mode": root.stat().st_mode & 0o7777,
        "root_writable_by_current_uid": os.access(root, os.W_OK),
        "controllers": sorted((root / "cgroup.controllers").read_text().split()),
        "local_account_uids": accounts,
    }


def assess(observation, selection=None):
    reasons = []
    if not observation["cgroup2_root_mounted"]:
        reasons.append("CGROUP2_ROOT_NOT_OBSERVED")
    if not REQUIRED_CONTROLLERS.issubset(observation["controllers"]):
        reasons.append("REQUIRED_CONTROLLERS_NOT_OBSERVED")
    if not isinstance(observation["self_cgroup"], str) or not observation["self_cgroup"].startswith("0::/"):
        reasons.append("UNEXPECTED_CGROUP_MEMBERSHIP")
    if selection is None:
        reasons.append("NO_INDEPENDENT_HOST_SELECTION")
    else:
        if set(selection) != {"broker_uid", "worker_uid", "scope_cgroup", "administrator_binding"}:
            reasons.append("SELECTION_SHAPE")
        else:
            if type(selection["broker_uid"]) is not int or selection["broker_uid"] != observation["broker_uid"]:
                reasons.append("BROKER_UID_MISMATCH")
            if type(selection["worker_uid"]) is not int or selection["worker_uid"] <= 0 or selection["worker_uid"] == observation["broker_uid"]:
                reasons.append("NO_SEPARATE_WORKER_UID")
            elif selection["worker_uid"] not in observation["local_account_uids"]:
                reasons.append("WORKER_ACCOUNT_NOT_OBSERVED")
            scope = selection["scope_cgroup"]
            if (not isinstance(scope, str) or not scope.startswith("/user.slice/") or
                    not scope.endswith(".scope") or any(part in ("", ".", "..") for part in scope[1:].split("/"))):
                reasons.append("SCOPE_NOT_NOMINATED")
            if not isinstance(selection["administrator_binding"], str) or len(selection["administrator_binding"]) != 64 or any(c not in "0123456789abcdef" for c in selection["administrator_binding"]):
                reasons.append("ADMINISTRATOR_BINDING_MISSING")
    return {
        "schema_version": "lab-lcu0302-host-admission-preflight/v1",
        "result": "BLOCKED" if reasons else "SELECTION_SHAPE_ONLY",
        "reasons": reasons,
        "observation": observation,
        "host_qualified": False,
        "effect_state": "none",
        "claim_ceiling": "Read-only observed capability and selection shape only; no delegated-scope custody, worker isolation, clone3 launch, historical-family oracle, or LC-U03-02 acceptance.",
    }


def main():
    if len(sys.argv) not in (1, 3) or (len(sys.argv) == 3 and sys.argv[1] != "--selection"):
        raise SystemExit("usage: host_admission_preflight_v1.py [--selection JSON_FILE]")
    selection = None
    if len(sys.argv) == 3:
        raw = Path(sys.argv[2]).read_bytes()
        if len(raw) > 4096:
            raise SystemExit("selection too large")
        selection = json.loads(raw)
        if not isinstance(selection, dict):
            raise SystemExit("selection must be object")
    print(json.dumps(assess(snapshot(), selection), sort_keys=True))


if __name__ == "__main__":
    main()
