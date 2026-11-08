#!/usr/bin/python3.14 -I
"""Disposable, no-host-bind Docker Source8 slot mechanics probe."""

import argparse
import hashlib
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
IMAGE = "sha256:543d0cf66f0f85411e42e35adfbfb4a7171de325a3047c34b0b23674189eacfe"
MANIFEST = HERE / "manifest.json"
LABEL_RUN = "cal.source8.probe.run"
LABEL_ROLE = "cal.source8.probe.role"


class Refused(RuntimeError):
    pass


def docker(*args, timeout=30, checked=True):
    result = subprocess.run(["docker", *args], text=True, capture_output=True,
                            timeout=timeout, check=False)
    if checked and result.returncode:
        raise Refused("DOCKER_COMMAND_FAILED " + repr(args[:5]) + " " +
                      result.stderr[-1000:])
    return result


def source_bytes():
    manifest = json.loads(MANIFEST.read_text())
    if (manifest.get("schema") != "cal-docker-source8-slot-candidate/v1"
            or manifest.get("image_id") != IMAGE
            or manifest.get("service_uid_gid") != [20001, 20001]):
        raise Refused("MANIFEST_CHANGED")
    contents = {}
    for name, expected in manifest["source_sha256"].items():
        if name not in ("init_volume.py", "writer.py", "attacker.py", "audit.py"):
            raise Refused("SOURCE_LIST_CHANGED")
        body = (HERE / name).read_bytes()
        if hashlib.sha256(body).hexdigest() != expected:
            raise Refused("SOURCE_HASH_CHANGED " + name)
        contents[name] = body.decode("utf-8")
    if set(contents) != {"init_volume.py", "writer.py", "attacker.py", "audit.py"}:
        raise Refused("SOURCE_SET_CHANGED")
    image = json.loads(docker("image", "inspect", IMAGE).stdout)[0]
    if image.get("Id") != IMAGE or image.get("Architecture") != "amd64":
        raise Refused("IMAGE_ID_CHANGED")
    return contents


def label_args(run_id, role):
    return ["--label", LABEL_RUN + "=" + run_id,
            "--label", LABEL_ROLE + "=" + role]


def base_args(run_id, role, name, uid, mount=None, add_chown=False):
    result = ["--name", name, *label_args(run_id, role), "--network", "none",
              "--read-only", "--pids-limit", "32", "--memory", "128m",
              "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
              "--user", uid]
    if add_chown:
        result += ["--cap-add", "CHOWN"]
    if mount is not None:
        result += ["--mount", mount]
    return result


def inspect_volume(name, run_id):
    value = json.loads(docker("volume", "inspect", name).stdout)[0]
    expected = {LABEL_RUN: run_id, LABEL_ROLE: "volume"}
    if (value.get("Name") != name or value.get("Driver") != "local"
            or value.get("Scope") != "local" or value.get("Labels") != expected
            or value.get("Options") not in (None, {})):
        raise Refused("VOLUME_IDENTITY_CHANGED")
    return value


def inspect_container(name, run_id, role, volume, read_only):
    value = json.loads(docker("container", "inspect", name).stdout)[0]
    mounts = value.get("Mounts", [])
    if (value.get("Name") != "/" + name
            or any(value["Config"].get("Labels", {}).get(key) != expected
                   for key, expected in ((LABEL_RUN, run_id), (LABEL_ROLE, role)))
            or value["Config"].get("User") != "20001:20001"
            or value["HostConfig"].get("NetworkMode") != "none"
            or not value["HostConfig"].get("ReadonlyRootfs")
            or value["HostConfig"].get("Privileged")
            or "ALL" not in value["HostConfig"].get("CapDrop", [])
            or len(mounts) != 1
            or mounts[0].get("Type") != "volume"
            or mounts[0].get("Name") != volume
            or mounts[0].get("Destination") != "/lab"
            or mounts[0].get("RW") is not (not read_only)):
        raise Refused("CONTAINER_TOPOLOGY_CHANGED " + name)
    return value


def event(output, kind):
    matches = []
    for line in output.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if value.get("event") == kind:
            matches.append(value)
    if len(matches) != 1:
        raise Refused("EVENT_MISSING_OR_DUPLICATE " + kind)
    return matches[0]


def run_container(run_id, role, name, mount, script, *args, add_chown=False):
    argv = ["run", "--rm", *base_args(run_id, role, name,
            "0:0" if add_chown else "20001:20001", mount, add_chown),
            "--entrypoint", "/usr/bin/python3.14", IMAGE,
            "-I", "-B", "-S", "-c", script, *args]
    return docker(*argv, timeout=40).stdout


def owned_container(name, run_id):
    result = docker("container", "inspect", name, checked=False)
    if result.returncode:
        return False
    value = json.loads(result.stdout)[0]
    if value["Config"].get("Labels", {}).get(LABEL_RUN) != run_id:
        raise Refused("UNOWNED_CONTAINER_REFUSED " + name)
    return True


def cleanup(run_id, volume, names):
    # Delete only this nonce's labeled containers and volume. Unknown references
    # preserve the synthetic attempt for inspection rather than risking others.
    refs = docker("ps", "-a", "--filter", "volume=" + volume,
                  "--format", "{{.Names}}").stdout.splitlines()
    if not set(refs).issubset(set(names)):
        raise Refused("FOREIGN_VOLUME_REFERENCE_RETAINED " + repr(refs))
    for name in reversed(names):
        if owned_container(name, run_id):
            docker("rm", "-f", name)
    inspect_volume(volume, run_id)
    docker("volume", "rm", volume)
    if docker("volume", "inspect", volume, checked=False).returncode == 0:
        raise Refused("VOLUME_CLEANUP_UNCONFIRMED")
    for name in names:
        if owned_container(name, run_id):
            raise Refused("CONTAINER_CLEANUP_UNCONFIRMED " + name)


def run_disposable(code):
    run_id = secrets.token_hex(8)
    token = secrets.token_hex(16)  # public identity marker, never a credential
    volume = "cal-source8-probe-" + run_id
    keeper = "cal-source8-keeper-" + run_id
    writer = "cal-source8-writer-" + run_id
    names = [keeper, writer]
    if docker("volume", "inspect", volume, checked=False).returncode == 0:
        raise Refused("PROBE_VOLUME_NAME_ALREADY_USED")
    for name in names:
        if owned_container(name, run_id):
            raise Refused("PROBE_CONTAINER_NAME_ALREADY_USED")
    docker("volume", "create", "--driver", "local",
           *label_args(run_id, "volume"), volume)
    selected = inspect_volume(volume, run_id)
    ro_mount = "type=volume,source=" + volume + ",target=/lab,readonly"
    rw_mount = "type=volume,source=" + volume + ",target=/lab"
    audit_passed = False
    cleanup_started = False
    try:
        docker("create", *base_args(run_id, "keeper", keeper,
               "20001:20001", ro_mount), "--entrypoint", "/bin/true", IMAGE)
        keeper_info = inspect_container(keeper, run_id, "keeper", volume, True)
        initialized = event(run_container(run_id, "initializer",
                            "cal-source8-init-" + run_id, rw_mount,
                            code["init_volume.py"], run_id, token,
                            add_chown=True), "INIT_DONE")
        inspect_volume(volume, run_id)
        started = docker("run", "-d", *base_args(run_id, "writer", writer,
                         "20001:20001", rw_mount), "--entrypoint",
                         "/usr/bin/python3.14", IMAGE, "-I", "-B", "-S",
                         "-c", code["writer.py"], run_id, token,
                         str(initialized["volume_dev"]),
                         str(initialized["volume_ino"])).stdout.strip()
        writer_info = inspect_container(writer, run_id, "writer", volume, False)
        if writer_info.get("Id") != started:
            raise Refused("WRITER_CID_CHANGED")
        deadline = time.monotonic() + 10
        while True:
            logs = docker("logs", writer).stdout
            if "GAP_READY" in logs:
                gap = event(logs, "GAP_READY")
                break
            if time.monotonic() >= deadline:
                raise Refused("WRITER_GAP_NOT_OBSERVED")
            time.sleep(0.1)
        read_only_attack = event(run_container(run_id, "ro-attacker",
                                 "cal-source8-ro-" + run_id, ro_mount,
                                 code["attacker.py"], run_id, "readonly"),
                                 "ATTACK_RESULT")
        no_mount_attack = event(run_container(run_id, "no-mount-attacker",
                               "cal-source8-no-mount-" + run_id, None,
                               code["attacker.py"], run_id, "no_mount"),
                               "ATTACK_RESULT")
        gap_logs = docker("logs", writer).stdout
        gap_state = inspect_container(writer, run_id, "writer", volume, False)
        if "WRITER_DONE" in gap_logs or not gap_state["State"].get("Running"):
            raise Refused("ATTACKS_NOT_OBSERVED_DURING_LIVE_GAP")
        if docker("wait", writer, timeout=25).stdout.strip() != "0":
            raise Refused("WRITER_NONZERO")
        finished = event(docker("logs", writer).stdout, "WRITER_DONE")
        if ((finished["instance_dev"], finished["instance_ino"]) !=
                (gap["instance_dev"], gap["instance_ino"])):
            raise Refused("WRITER_INODE_CHANGED")
        rw_counterexample = event(run_container(run_id, "rw-counterexample",
                                  "cal-source8-rw-" + run_id, rw_mount,
                                  code["attacker.py"], run_id,
                                  "rw_counterexample"), "ATTACK_RESULT")
        audited = event(run_container(run_id, "auditor",
                        "cal-source8-audit-" + run_id, ro_mount,
                        code["audit.py"], run_id, token), "AUDIT_DONE")
        if (audited["marker_sha256"] != initialized["marker_sha256"]
                or audited["payload_sha256"] != finished["payload_sha256"]
                or audited["family_ino"] != finished["instance_ino"]):
            raise Refused("INDEPENDENT_SYNTHETIC_AUDIT_MISMATCH")
        if inspect_volume(volume, run_id).get("CreatedAt") != selected.get("CreatedAt"):
            raise Refused("VOLUME_CREATED_AT_CHANGED")
        audit_passed = True
        cleanup_started = True
        cleanup(run_id, volume, names)
        return {"schema": "cal-docker-source8-slot-probe-result/v1",
                "status": "PASS_DISPOSABLE_DOCKER_ONLY_CLEANED",
                "run_id": run_id, "volume": volume,
                "volume_created_at": selected.get("CreatedAt"),
                "keeper_cid": keeper_info["Id"], "writer_cid": started,
                "init": initialized, "writer": finished,
                "attacks": [read_only_attack, no_mount_attack, rw_counterexample],
                "audit": audited,
                "attacks_during_live_gap": True,
                "claim_ceiling": "same-UID denial only without a daemon-authorized RW mount; RW mount counterexample succeeds; no protected Source8 or T02 authority"}
    except BaseException:
        if audit_passed and not cleanup_started:
            cleanup(run_id, volume, names)
        else:
            print("RETAINED_SYNTHETIC_ATTEMPT_FOR_INSPECTION " +
                  json.dumps({"run_id": run_id, "volume": volume,
                              "containers": names}), file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--plan", action="store_true")
    actions.add_argument("--run-disposable", action="store_true")
    args = parser.parse_args()
    try:
        code = source_bytes()
        if args.plan:
            result = {"status": "DISPOSABLE_PLAN_ONLY", "effect": "none",
                      "image": IMAGE, "scripts": sorted(code)}
        else:
            result = run_disposable(code)
            destination = HERE / ("test-result-" + result["run_id"] + ".json")
            if destination.exists():
                raise Refused("RESULT_FILE_ALREADY_PRESENT")
            destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (Refused, OSError, subprocess.TimeoutExpired, ValueError, KeyError) as exc:
        print("REFUSED:" + str(exc), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
