#!/usr/bin/python3.14 -I
"""Disposable Docker volume writer-admission controller candidate."""

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
    if (manifest.get("schema") != "cal-docker-source8-controller-candidate/v5"
            or manifest.get("image_id") != IMAGE
            or manifest.get("service_uid_gid") != [20001, 20001]
            or manifest.get("protected_activation_enabled") is not False):
        raise Refused("MANIFEST_CHANGED")
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != manifest.get("entrypoint_sha256"):
        raise Refused("ENTRYPOINT_HASH_CHANGED")
    contents = {}
    for name, expected in manifest["source_sha256"].items():
        if name not in ("init_volume.py", "writer.py", "attacker.py", "audit.py",
                        "competitor.py", "control.py"):
            raise Refused("SOURCE_LIST_CHANGED")
        body = (HERE / name).read_bytes()
        if hashlib.sha256(body).hexdigest() != expected:
            raise Refused("SOURCE_HASH_CHANGED " + name)
        contents[name] = body.decode("utf-8")
    if set(contents) != {"init_volume.py", "writer.py", "attacker.py", "audit.py",
                         "competitor.py", "control.py"}:
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


def run_container(run_id, role, name, mount, script, *args, add_chown=False,
                  remove=True):
    argv = ["run", *(["--rm"] if remove else []), *base_args(run_id, role, name,
            "0:0" if add_chown else "20001:20001", mount, add_chown),
            "--entrypoint", "/usr/bin/python3.14", IMAGE,
            "-I", "-B", "-S", "-c", script, *args]
    return docker(*argv, timeout=40).stdout


def run_container_tracked(run_id, role, name, mount, script, args,
                          allowed_ids, allowed_rw, *, add_chown=False):
    """Create first so the witness knows the initializer CID before its RW mount."""
    argv = [*base_args(run_id, role, name,
            "0:0" if add_chown else "20001:20001", mount, add_chown),
            "--entrypoint", "/usr/bin/python3.14", IMAGE,
            "-I", "-B", "-S", "-c", script, *args]
    cid = docker("create", *argv).stdout.strip()
    if not cid:
        raise Refused("TRACKED_CONTAINER_CID_MISSING")
    allowed_ids.add(cid)
    allowed_rw.add(cid)
    docker("start", "-a", name, timeout=40)
    if docker("wait", name).stdout.strip() != "0":
        raise Refused("TRACKED_CONTAINER_NONZERO")
    return docker("logs", name).stdout, cid


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


def cleanup_witnessed(control, lock, baseline, run_id, volume, selected,
                      names, final_name, global_final_name, writer_cid,
                      allowed_ids, allowed_rw, events, container_events,
                      global_events):
    """Keep all witnesses live through grant removal and post-check barrier."""
    refs = docker("ps", "-a", "--filter", "volume=" + volume,
                  "--format", "{{.Names}}").stdout.splitlines()
    if not set(refs).issubset(set(names)):
        raise Refused("FOREIGN_VOLUME_REFERENCE_RETAINED " + repr(refs))
    removed = []
    for name in reversed(names):
        if name in (final_name, global_final_name):
            continue
        if owned_container(name, run_id):
            docker("rm", "-f", name)
            removed.append(name)
            lock.check()
            if control["endpoint"]() != baseline:
                raise control["Unknown"]("DAEMON_CHANGED_DURING_RELEASE")
            if inspect_volume(volume, run_id).get("CreatedAt") != selected.get("CreatedAt"):
                raise control["Unknown"]("VOLUME_CHANGED_DURING_RELEASE")
            events.poll(writer_cid)
            container_events.poll(allowed_ids)
            global_events.poll((allowed_ids, allowed_rw))
    if docker("ps", "-aq", "--filter", "volume=" + volume).stdout.strip():
        raise Refused("VOLUME_REFERENCES_REMAIN_AFTER_WRITER_RELEASE")
    events.expect_volume_destroy()
    global_events.expect_volume_destroy()
    docker("volume", "rm", volume)
    events.final_destroy(writer_cid)
    container_events.poll(allowed_ids)
    global_events.poll((allowed_ids, allowed_rw))
    if docker("volume", "inspect", volume, checked=False).returncode == 0:
        raise Refused("VOLUME_RELEASE_UNCONFIRMED")
    for name in names:
        if name != final_name and owned_container(name, run_id):
            raise Refused("PRE_FINAL_CONTAINER_REMAINS " + name)
    lock.check()
    if control["endpoint"]() != baseline:
        raise control["Unknown"]("DAEMON_CHANGED_BEFORE_FINAL_BARRIER")
    # The container stream continues across the volume-stream destroy barrier.
    # Any create-only stopped grant in this skew interval is still refused.
    final_cid = docker("create", *base_args(run_id, "final-barrier", final_name,
                       "20001:20001", None), "--entrypoint", "/bin/true",
                       IMAGE).stdout.strip()
    allowed_ids.add(final_cid)
    container_events.final_container(final_cid, allowed_ids)
    events.poll(writer_cid)
    global_events.poll((allowed_ids, allowed_rw))
    volume_replay = events.reconcile(writer_cid, writer_cid)
    container_replay = container_events.reconcile(allowed_ids, writer_cid)
    if docker("volume", "inspect", volume, checked=False).returncode == 0:
        raise Refused("FINAL_VOLUME_ABSENCE_UNCONFIRMED")
    if any(owned_container(name, run_id) for name in names
           if name not in (final_name, global_final_name)):
        raise Refused("FINAL_NAMED_CONTAINER_ABSENCE_UNCONFIRMED")
    docker("rm", final_name)
    container_events.poll(allowed_ids)
    events.poll(writer_cid)
    global_events.poll((allowed_ids, allowed_rw))
    if any(owned_container(name, run_id) for name in names if name != global_final_name):
        raise Refused("FINAL_CONTAINER_CLEANUP_UNCONFIRMED")
    if docker("volume", "inspect", volume, checked=False).returncode == 0:
        raise Refused("POST_FINAL_VOLUME_ABSENCE_UNCONFIRMED")
    lock.check()
    if control["endpoint"]() != baseline:
        raise control["Unknown"]("DAEMON_CHANGED_AT_FINAL_CUSTODY_CHECK")
    # This no-mount create occurs after all selected-resource custody checks.
    # The mixed stream carries both container and selected-volume events, so
    # its retained-history replay has a common post-check end boundary.
    global_final_cid = docker("create", *base_args(
        run_id, "postcustody-barrier", global_final_name, "20001:20001", None),
        "--entrypoint", "/bin/true", IMAGE).stdout.strip()
    allowed_ids.add(global_final_cid)
    global_events.final_container(global_final_cid, (allowed_ids, allowed_rw))
    container_events.drain_complete(allowed_ids)
    events.drain_complete(writer_cid)
    global_events.drain_complete((allowed_ids, allowed_rw))
    global_replay = global_events.reconcile((allowed_ids, allowed_rw), writer_cid)
    docker("rm", global_final_name)
    container_events.drain_complete(allowed_ids)
    events.drain_complete(writer_cid)
    global_events.drain_complete((allowed_ids, allowed_rw))
    if owned_container(global_final_name, run_id):
        raise Refused("POSTCUSTODY_BARRIER_CLEANUP_UNCONFIRMED")
    return {"volume_event_replay": volume_replay,
            "container_event_replay": container_replay,
            "global_event_replay": global_replay,
            "removed_container_names": removed,
            "final_barrier_cid": final_cid,
            "postcustody_barrier_cid": global_final_cid,
            "final_volume_absent": True,
            "final_named_containers_absent": True,
            "streams_live_at_final_custody_check": True}


def check_control(control, lock, baseline, volume, run_id, selected, writer_cid,
                  keeper_cid, events, container_events, allowed_ids, *, require_writer):
    lock.check()
    if control["endpoint"]() != baseline:
        raise control["Unknown"]("DAEMON_OR_OPERATOR_IDENTITY_CHANGED")
    if inspect_volume(volume, run_id).get("CreatedAt") != selected.get("CreatedAt"):
        raise control["Unknown"]("VOLUME_CREATED_AT_CHANGED")
    events.poll(writer_cid)
    container_events.poll(allowed_ids)
    if not hasattr(events, "global_peer") or not hasattr(events, "global_allowed_rw"):
        raise control["Unknown"]("PRESELECTION_WITNESS_MISSING")
    events.global_peer.poll((allowed_ids, events.global_allowed_rw))
    return control["inventory"](volume, writer_cid, keeper_cid,
                                require_writer=require_writer)


def run_case(code, control, lock, baseline, *, competing, post_terminal=False):
    run_id = secrets.token_hex(8)
    token = secrets.token_hex(16)  # public marker, never an issuer grant
    volume = "cal-source8-control-" + run_id
    keeper = "cal-source8-keeper-" + run_id
    writer = "cal-source8-writer-" + run_id
    foreign = "cal-source8-foreign-" + run_id
    barrier = "cal-source8-start-" + run_id
    terminal = "cal-source8-end-" + run_id
    final_barrier = "cal-source8-final-" + run_id
    preselect = "cal-source8-preselect-" + run_id
    initializer = "cal-source8-init-" + run_id
    global_final = "cal-source8-global-final-" + run_id
    names = [preselect, initializer, keeper, writer, foreign, barrier, terminal,
             "cal-source8-ro-" + run_id,
             "cal-source8-no-mount-" + run_id, "cal-source8-audit-" + run_id,
             final_barrier, global_final]
    if docker("volume", "inspect", volume, checked=False).returncode == 0:
        raise Refused("PROBE_VOLUME_NAME_ALREADY_USED")
    for name in names:
        if docker("container", "inspect", name, checked=False).returncode == 0:
            raise Refused("PROBE_CONTAINER_NAME_ALREADY_USED")
    lock.check()
    if control["endpoint"]() != baseline:
        raise control["Unknown"]("DAEMON_CHANGED_BEFORE_CREATE")
    ro_mount = "type=volume,source=" + volume + ",target=/lab,readonly"
    rw_mount = "type=volume,source=" + volume + ",target=/lab"
    # All three streams start before this run selects or initializes the
    # volume. The mixed stream anchors on a no-mount preselection container.
    events = control["VolumeEvents"](volume)
    container_events = control["ContainerEvents"]()
    global_events = control["GlobalEvents"](volume)
    allowed_ids = set()
    allowed_rw = set()
    events.global_peer = global_events
    events.global_allowed_rw = allowed_rw
    terminal_checked = False
    audited = None
    try:
        preselect_cid = docker("create", *base_args(run_id, "preselection-barrier",
                               preselect, "20001:20001", None),
                               "--entrypoint", "/bin/true", IMAGE).stdout.strip()
        allowed_ids.add(preselect_cid)
        global_events.anchor(preselect_cid, (allowed_ids, allowed_rw))
        docker("volume", "create", "--driver", "local",
               *label_args(run_id, "volume"), volume)
        selected = inspect_volume(volume, run_id)
        global_events.poll((allowed_ids, allowed_rw))
        docker("create", *base_args(run_id, "keeper", keeper,
               "20001:20001", ro_mount), "--entrypoint", "/bin/true", IMAGE)
        keeper_info = inspect_container(keeper, run_id, "keeper", volume, True)
        allowed_ids.add(keeper_info["Id"])
        init_output, init_cid = run_container_tracked(
            run_id, "initializer", initializer, rw_mount, code["init_volume.py"],
            (run_id, token), allowed_ids, allowed_rw, add_chown=True)
        initialized = event(init_output, "INIT_DONE")
        global_events.poll((allowed_ids, allowed_rw))
        docker("rm", initializer)
        if owned_container(initializer, run_id):
            raise Refused("INITIALIZER_RW_GRANT_REMAINS")
        global_events.poll((allowed_ids, allowed_rw))
        allowed_rw.remove(init_cid)
        inspect_volume(volume, run_id)
        # The two type-specific streams were already launched before selection.
        # A known RO mount brackets event-order observation without using a
        # wall-clock timestamp. No writer is admitted until both streams have
        # observed this exact barrier and current inventory has been checked.
        barrier_cid = docker("create", *base_args(run_id, "start-barrier",
                             barrier, "20001:20001", ro_mount),
                            "--entrypoint", "/bin/true", IMAGE).stdout.strip()
        docker("start", barrier)
        allowed_ids.add(barrier_cid)
        container_events.anchor(barrier_cid, allowed_ids)
        events.anchor(barrier_cid, None)
        check_control(control, lock, baseline, volume, run_id, selected, None,
                      keeper_info["Id"], events, container_events, allowed_ids,
                      require_writer=False)
        started = docker("run", "-d", *base_args(run_id, "writer", writer,
                         "20001:20001", rw_mount), "--entrypoint",
                         "/usr/bin/python3.14", IMAGE, "-I", "-B", "-S",
                         "-c", code["writer.py"], run_id, token,
                         str(initialized["volume_dev"]),
                         str(initialized["volume_ino"])).stdout.strip()
        writer_info = inspect_container(writer, run_id, "writer", volume, False)
        if writer_info.get("Id") != started:
            raise Refused("WRITER_CID_CHANGED")
        allowed_ids.add(started)
        allowed_rw.add(started)
        deadline = time.monotonic() + 10
        while True:
            check_control(control, lock, baseline, volume, run_id, selected,
                          started, keeper_info["Id"], events, container_events,
                          allowed_ids, require_writer=True)
            logs = docker("logs", writer).stdout
            if "GAP_READY" in logs:
                gap = event(logs, "GAP_READY")
                break
            if time.monotonic() >= deadline:
                raise Refused("WRITER_GAP_NOT_OBSERVED")
            time.sleep(0.1)
        read_only_attack = event(run_container(run_id, "ro-attacker",
                                 "cal-source8-ro-" + run_id, ro_mount,
                                 code["attacker.py"], run_id, "readonly",
                                 remove=False),
                                 "ATTACK_RESULT")
        allowed_ids.add(json.loads(docker("container", "inspect",
                             "cal-source8-ro-" + run_id).stdout)[0]["Id"])
        check_control(control, lock, baseline, volume, run_id, selected,
                      started, keeper_info["Id"], events, container_events,
                      allowed_ids, require_writer=True)
        no_mount_attack = event(run_container(run_id, "no-mount-attacker",
                               "cal-source8-no-mount-" + run_id, None,
                               code["attacker.py"], run_id, "no_mount",
                               remove=False),
                               "ATTACK_RESULT")
        allowed_ids.add(json.loads(docker("container", "inspect",
                             "cal-source8-no-mount-" + run_id).stdout)[0]["Id"])
        check_control(control, lock, baseline, volume, run_id, selected,
                      started, keeper_info["Id"], events, container_events,
                      allowed_ids, require_writer=True)
        if "WRITER_DONE" in docker("logs", writer).stdout:
            raise Refused("ATTACKS_NOT_OBSERVED_DURING_LIVE_GAP")
        detected = None
        foreign_cid = None
        if competing:
            foreign_cid = docker("run", "-d", *base_args(run_id, "foreign-rw",
                                 foreign, "20001:20001", rw_mount),
                                 "--entrypoint", "/usr/bin/python3.14", IMAGE,
                                 "-I", "-B", "-S", "-c", code["competitor.py"],
                                 run_id).stdout.strip()
            foreign_info = inspect_container(foreign, run_id, "foreign-rw",
                                             volume, False)
            if foreign_info["Id"] != foreign_cid:
                raise Refused("FOREIGN_CID_CHANGED")
            event(docker("logs", foreign).stdout, "FOREIGN_RW_READY")
            try:
                check_control(control, lock, baseline, volume, run_id, selected,
                              started, keeper_info["Id"], events,
                              container_events, allowed_ids,
                              require_writer=True)
            except control["Unknown"] as exc:
                detected = str(exc)
            if not detected or not (detected.startswith("COMPETING_RW_")
                                    or detected == "UNADMITTED_CONTAINER_CREATE " + foreign_cid):
                raise Refused("COMPETING_RW_NOT_DETECTED")
        if docker("wait", writer, timeout=60).stdout.strip() != "0":
            raise Refused("WRITER_NONZERO")
        finished = event(docker("logs", writer).stdout, "WRITER_DONE")
        if ((finished["instance_dev"], finished["instance_ino"]) !=
                (gap["instance_dev"], gap["instance_ino"])):
            raise Refused("WRITER_INODE_CHANGED")
        if competing:
            # The foreign grant has already made the verdict UNKNOWN. We still
            # audit and clean the public synthetic fixture, without accepting it.
            if not control["inventory"](volume, started, keeper_info["Id"],
                                        require_writer=True):
                raise Refused("TERMINAL_INVENTORY_UNEXPECTED")
            raise Refused("COMPETING_INVENTORY_NOT_REFUSED")
        audited = event(run_container(run_id, "auditor",
                        "cal-source8-audit-" + run_id, ro_mount,
                        code["audit.py"], run_id, token, remove=False), "AUDIT_DONE")
        allowed_ids.add(json.loads(docker("container", "inspect",
                             "cal-source8-audit-" + run_id).stdout)[0]["Id"])
        if (audited["marker_sha256"] != initialized["marker_sha256"]
                or audited["payload_sha256"] != finished["payload_sha256"]
                or audited["family_ino"] != finished["instance_ino"]):
            raise Refused("INDEPENDENT_SYNTHETIC_AUDIT_MISMATCH")
        terminal_inventory = check_control(control, lock, baseline, volume,
                                            run_id, selected, started,
                                            keeper_info["Id"], events,
                                            container_events, allowed_ids,
                                            require_writer=True)
        terminal_cid = docker("create", *base_args(run_id, "end-barrier",
                              terminal, "20001:20001", ro_mount),
                             "--entrypoint", "/bin/true", IMAGE).stdout.strip()
        allowed_ids.add(terminal_cid)
        docker("start", terminal)
        container_events.terminal(terminal_cid, allowed_ids)
        events.terminal(terminal_cid, started)
        global_events.terminal(terminal_cid, (allowed_ids, allowed_rw))
        # This is an intermediate checkpoint. Enforcement must continue while
        # the stopped writer still holds an RW grant and the volume exists.
        terminal_inventory = check_control(control, lock, baseline, volume,
                                            run_id, selected, started,
                                            keeper_info["Id"], events,
                                            container_events, allowed_ids,
                                            require_writer=True)
        source_bytes()
        terminal_checked = True
        if post_terminal:
            # This transient stopped/removed RW grant occurs after *both*
            # intermediate barriers while the selected writer grant remains.
            # The live event streams must reject it even if final inventory
            # no longer contains the foreign container.
            foreign_cid = docker("run", "-d", *base_args(run_id, "foreign-rw",
                                 foreign, "20001:20001", rw_mount),
                                 "--entrypoint", "/usr/bin/python3.14", IMAGE,
                                 "-I", "-B", "-S", "-c", code["competitor.py"],
                                 run_id).stdout.strip()
            foreign_info = inspect_container(foreign, run_id, "foreign-rw",
                                             volume, False)
            if foreign_info["Id"] != foreign_cid:
                raise Refused("POST_TERMINAL_FOREIGN_CID_CHANGED")
            event(docker("logs", foreign).stdout, "FOREIGN_RW_READY")
            docker("rm", "-f", foreign)
            if owned_container(foreign, run_id):
                raise Refused("POST_TERMINAL_FOREIGN_REMOVE_UNCONFIRMED")
            detected = None
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                try:
                    check_control(control, lock, baseline, volume, run_id,
                                  selected, started, keeper_info["Id"], events,
                                  container_events, allowed_ids,
                                  require_writer=True)
                except control["Unknown"] as exc:
                    detected = str(exc)
                    break
                time.sleep(0.05)
            if (not detected or not
                    (detected.startswith("COMPETING_RW_MOUNT_EVENT ") or
                     detected == "UNADMITTED_CONTAINER_CREATE " + foreign_cid)):
                raise Refused("POST_TERMINAL_TRANSIENT_GRANT_NOT_DETECTED " + str(detected))
            raise control["Unknown"](detected)
        release = cleanup_witnessed(control, lock, baseline, run_id, volume,
                                    selected, names, final_barrier, global_final,
                                    started, allowed_ids, allowed_rw, events,
                                    container_events, global_events)
        events.close()
        events = None
        container_events.close()
        container_events = None
        global_events.close()
        global_events = None
        return {"status": "PASS_SYNTHETIC_CONTROL_INTERVAL_CLEANED",
                "run_id": run_id, "volume": volume,
                "volume_created_at": selected.get("CreatedAt"),
                "keeper_cid": keeper_info["Id"], "writer_cid": started,
                "lock_identity": lock.identity, "endpoint": baseline,
                "init": initialized, "writer": finished,
                "attacks": [read_only_attack, no_mount_attack],
                "audit": audited, "event_replay": release["volume_event_replay"],
                "container_event_replay": release["container_event_replay"],
                "global_event_replay": release["global_event_replay"],
                "release": release,
                "start_barrier_cid": barrier_cid,
                "terminal_barrier_cid": terminal_cid,
                "terminal_inventory": terminal_inventory}
    except control["Unknown"] as exc:
        if not (competing or post_terminal) or not (str(exc).startswith("COMPETING_RW_")
                                  or str(exc) == "UNADMITTED_CONTAINER_CREATE " + foreign_cid):
            print("RETAINED_SYNTHETIC_ATTEMPT_FOR_INSPECTION " +
                  json.dumps({"run_id": run_id, "volume": volume,
                              "containers": names, "reason": str(exc)}),
                  file=sys.stderr)
            raise
        # A rejected synthetic attempt is safe to discard only after a
        # read-only fixture audit. No protected Source package is present.
        if audited is None:
            audited = event(run_container(run_id, "auditor",
                            "cal-source8-audit-" + run_id, ro_mount,
                            code["audit.py"], run_id, token, remove=False), "AUDIT_DONE")
        if audited["marker_sha256"] != initialized["marker_sha256"]:
            raise Refused("REJECTED_FIXTURE_AUDIT_MISMATCH")
        if events is not None:
            events.close()
        if container_events is not None:
            container_events.close()
        if global_events is not None:
            global_events.close()
        cleanup(run_id, volume, names)
        return {"status": ("UNKNOWN_POST_TERMINAL_RW_GRANT_CLEANED" if post_terminal
                           else "UNKNOWN_COMPETING_RW_GRANT_CLEANED"),
                "reason": str(exc), "run_id": run_id, "volume": volume,
                "writer_cid": started, "foreign_cid": foreign_cid,
                "lock_identity": lock.identity, "endpoint": baseline,
                "audited_synthetic_only": audited,
                "admitted": False}
    except Exception as exc:
        print("RETAINED_SYNTHETIC_ATTEMPT_FOR_INSPECTION " +
              json.dumps({"run_id": run_id, "volume": volume,
                          "containers": names, "reason": str(exc)}),
              file=sys.stderr)
        raise
    finally:
        if events is not None and not events.closed:
            events.close()
        if container_events is not None and not container_events.closed:
            container_events.close()
        if global_events is not None and not global_events.closed:
            global_events.close()


def run_stopped_grant_case(code, control, lock, baseline):
    """Create then remove a stopped RW grant between inventory observations."""
    run_id = secrets.token_hex(8)
    token = secrets.token_hex(16)
    volume = "cal-source8-control-" + run_id
    keeper = "cal-source8-keeper-" + run_id
    foreign = "cal-source8-stopped-" + run_id
    barrier = "cal-source8-start-" + run_id
    preselect = "cal-source8-preselect-" + run_id
    initializer = "cal-source8-init-" + run_id
    names = [preselect, initializer, keeper, foreign, barrier]
    if docker("volume", "inspect", volume, checked=False).returncode == 0:
        raise Refused("STOPPED_VOLUME_NAME_ALREADY_USED")
    for name in names:
        if docker("container", "inspect", name, checked=False).returncode == 0:
            raise Refused("STOPPED_CONTAINER_NAME_ALREADY_USED")
    ro_mount = "type=volume,source=" + volume + ",target=/lab,readonly"
    rw_mount = "type=volume,source=" + volume + ",target=/lab"
    volume_events = control["VolumeEvents"](volume)
    container_events = control["ContainerEvents"]()
    global_events = control["GlobalEvents"](volume)
    allowed_ids = set()
    allowed_rw = set()
    volume_events.global_peer = global_events
    volume_events.global_allowed_rw = allowed_rw
    try:
        preselect_cid = docker("create", *base_args(run_id, "preselection-barrier",
                               preselect, "20001:20001", None),
                               "--entrypoint", "/bin/true", IMAGE).stdout.strip()
        allowed_ids.add(preselect_cid)
        global_events.anchor(preselect_cid, (allowed_ids, allowed_rw))
        docker("volume", "create", "--driver", "local",
               *label_args(run_id, "volume"), volume)
        selected = inspect_volume(volume, run_id)
        global_events.poll((allowed_ids, allowed_rw))
        docker("create", *base_args(run_id, "keeper", keeper,
               "20001:20001", ro_mount), "--entrypoint", "/bin/true", IMAGE)
        keeper_info = inspect_container(keeper, run_id, "keeper", volume, True)
        allowed_ids.add(keeper_info["Id"])
        init_output, init_cid = run_container_tracked(
            run_id, "initializer", initializer, rw_mount, code["init_volume.py"],
            (run_id, token), allowed_ids, allowed_rw, add_chown=True)
        initialized = event(init_output, "INIT_DONE")
        global_events.poll((allowed_ids, allowed_rw))
        docker("rm", initializer)
        if owned_container(initializer, run_id):
            raise Refused("INITIALIZER_RW_GRANT_REMAINS")
        global_events.poll((allowed_ids, allowed_rw))
        allowed_rw.remove(init_cid)
        barrier_cid = docker("create", *base_args(run_id, "start-barrier",
                             barrier, "20001:20001", ro_mount),
                            "--entrypoint", "/bin/true", IMAGE).stdout.strip()
        docker("start", barrier)
        allowed_ids.add(barrier_cid)
        container_events.anchor(barrier_cid, allowed_ids)
        volume_events.anchor(barrier_cid, None)
        check_control(control, lock, baseline, volume, run_id, selected, None,
                      keeper_info["Id"], volume_events, container_events,
                      allowed_ids,
                      require_writer=False)
        stopped_cid = docker("create", *base_args(run_id, "foreign-stopped",
                              foreign, "20001:20001", rw_mount),
                             "--entrypoint", "/bin/true", IMAGE).stdout.strip()
        item = inspect_container(foreign, run_id, "foreign-stopped", volume, False)
        if item["Id"] != stopped_cid or item["State"]["Status"] != "created":
            raise Refused("STOPPED_RW_GRANT_IDENTITY_CHANGED")
        docker("rm", foreign)
        if docker("container", "inspect", foreign, checked=False).returncode == 0:
            raise Refused("STOPPED_FOREIGN_REMOVE_UNCONFIRMED")
        detected = None
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            try:
                check_control(control, lock, baseline, volume, run_id, selected,
                              None, keeper_info["Id"], volume_events,
                              container_events, allowed_ids,
                              require_writer=False)
            except control["Unknown"] as exc:
                detected = str(exc)
                break
            time.sleep(0.05)
        if detected != "UNADMITTED_CONTAINER_CREATE " + stopped_cid:
            raise Refused("STOPPED_RW_GRANT_NOT_DETECTED " + str(detected))
        volume_events.close()
        container_events.close()
        global_events.close()
        # The synthetic initializer marker is independently read on an RO
        # mount before deletion; this audit happens after UNKNOWN is fixed.
        marker = event(run_container(run_id, "init-auditor",
                       "cal-source8-init-audit-" + run_id, ro_mount,
                       'import json,os,sys; r,t=sys.argv[1:3]; m=json.load(open("/lab/.volume-token")); assert m=={"schema":"cal-docker-source8-probe/v1","run_id":r,"volume_token":t}; assert set(os.listdir("/lab/instances"))=={".slot-lock"}; print(json.dumps({"event":"INIT_AUDIT_DONE","run_id":r}))',
                       run_id, token), "INIT_AUDIT_DONE")
        if initialized["run_id"] != marker["run_id"]:
            raise Refused("STOPPED_INIT_AUDIT_MISMATCH")
        cleanup(run_id, volume, names)
        return {"status": "UNKNOWN_STOPPED_RW_GRANT_CLEANED", "admitted": False,
                "run_id": run_id, "volume": volume, "foreign_cid": stopped_cid,
                "reason": detected, "marker_sha256": initialized["marker_sha256"],
                "endpoint": baseline}
    except Exception as exc:
        print("RETAINED_SYNTHETIC_ATTEMPT_FOR_INSPECTION " +
              json.dumps({"run_id": run_id, "volume": volume,
                          "containers": names, "reason": str(exc)}), file=sys.stderr)
        raise
    finally:
        if volume_events is not None and not volume_events.closed:
            volume_events.close()
        if container_events is not None and not container_events.closed:
            container_events.close()
        if global_events is not None and not global_events.closed:
            global_events.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--plan", action="store_true")
    actions.add_argument("--run-disposable", action="store_true")
    args = parser.parse_args()
    try:
        code = source_bytes()
        # Execute the exact bytes already captured and hashed above. Reopening
        # a mutable path between hash and execution would be a code identity race.
        control = {"__name__": "captured_controller"}
        exec(compile(code["control.py"], "<captured-control.py>", "exec"), control)
        baseline = control["endpoint"]()
        if args.plan:
            result = {"status": "DISPOSABLE_PLAN_ONLY", "effect": "none",
                      "image": IMAGE, "scripts": sorted(code),
                      "endpoint": baseline}
        else:
            lock = control["HeldLock"](MANIFEST)
            try:
                clean = run_case(code, control, lock, baseline, competing=False)
                rejected = run_case(code, control, lock, baseline, competing=True)
                stopped = run_stopped_grant_case(code, control, lock, baseline)
                post_terminal = run_case(code, control, lock, baseline,
                                         competing=False, post_terminal=True)
                if rejected["status"] != "UNKNOWN_COMPETING_RW_GRANT_CLEANED":
                    raise Refused("COMPETING_CASE_ADMITTED")
                if stopped["status"] != "UNKNOWN_STOPPED_RW_GRANT_CLEANED":
                    raise Refused("STOPPED_CASE_ADMITTED")
                if post_terminal["status"] != "UNKNOWN_POST_TERMINAL_RW_GRANT_CLEANED":
                    raise Refused("POST_TERMINAL_CASE_ADMITTED")
                result = {"schema": "cal-docker-source8-control-test/v5",
                          "status": "PASS_SYNTHETIC_ALL_CASES_CLEANED",
                          "clean": clean, "competing": rejected, "stopped": stopped,
                          "post_terminal": post_terminal,
                          "claim_ceiling": "Bounded Docker-event observation with conservative rejection of every unadmitted container creation; Docker-group/daemon administrators remain trusted and unrelated creation can yield UNKNOWN; no protected Source8 family, issuer grant, T02 or production admission."}
                destination = HERE / ("test-result-" + clean["run_id"] + ".json")
                if destination.exists():
                    raise Refused("RESULT_FILE_ALREADY_PRESENT")
                destination.write_text(json.dumps(result, indent=2,
                                                  sort_keys=True) + "\n")
            finally:
                lock.close()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (Refused, OSError, subprocess.TimeoutExpired, ValueError, KeyError,
            RuntimeError) as exc:
        print("REFUSED:" + str(exc), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
