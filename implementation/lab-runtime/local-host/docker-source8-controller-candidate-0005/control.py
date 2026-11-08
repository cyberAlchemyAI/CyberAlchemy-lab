"""Bounded Docker admission, volume-event, inventory and lock witness."""

import fcntl
import hashlib
import json
import os
import stat
import subprocess
import time


class Unknown(RuntimeError):
    pass


def docker(*args, checked=True, timeout=30):
    result = subprocess.run(["docker", *args], capture_output=True, text=True,
                            timeout=timeout, check=False)
    if checked and result.returncode:
        raise Unknown("DOCKER_QUERY_FAILED " + repr(args[:4]) + " " +
                      result.stderr[-500:])
    return result


def endpoint():
    if any(os.environ.get(name) for name in ("DOCKER_HOST", "DOCKER_CONTEXT")):
        raise Unknown("DOCKER_ENDPOINT_OVERRIDE_UNSELECTED")
    context = docker("context", "show").stdout.strip()
    values = json.loads(docker("context", "inspect", context).stdout)
    host = values[0]["Endpoints"]["docker"]["Host"]
    if context != "default" or host != "unix:///var/run/docker.sock":
        raise Unknown("DOCKER_ENDPOINT_CHANGED")
    sock = os.stat("/var/run/docker.sock", follow_symlinks=False)
    if (not stat.S_ISSOCK(sock.st_mode) or sock.st_uid != 0
            or stat.S_IMODE(sock.st_mode) != 0o660):
        raise Unknown("DOCKER_SOCKET_IDENTITY_CHANGED")
    daemon = docker("info", "--format", "{{.ID}}").stdout.strip()
    if not daemon:
        raise Unknown("DAEMON_ID_UNKNOWN")
    return {"context": context, "endpoint": host, "daemon_id": daemon,
            "socket": [sock.st_dev, sock.st_ino, sock.st_uid, sock.st_gid,
                       stat.S_IMODE(sock.st_mode)],
            "operator_uid": os.getuid(), "operator_gids": os.getgroups()}


class HeldLock:
    def __init__(self, path):
        self.path = path
        self.fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.identity = self._identity()
        self.digest = self._digest()

    def _digest(self):
        size = os.fstat(self.fd).st_size
        if size > 1_048_576:
            raise Unknown("CONTROLLER_MANIFEST_TOO_LARGE")
        content = os.pread(self.fd, size, 0)
        if len(content) != size:
            raise Unknown("CONTROLLER_MANIFEST_SHORT_READ")
        return hashlib.sha256(content).hexdigest()

    def _identity(self):
        held = os.fstat(self.fd)
        named = os.stat(self.path, follow_symlinks=False)
        if (not stat.S_ISREG(held.st_mode) or held.st_nlink != 1
                or (held.st_dev, held.st_ino) != (named.st_dev, named.st_ino)):
            raise Unknown("CONTROLLER_LOCK_LINK_CHANGED")
        return [held.st_dev, held.st_ino, held.st_uid,
                stat.S_IMODE(held.st_mode)]

    def check(self):
        if self._identity() != self.identity:
            raise Unknown("CONTROLLER_LOCK_IDENTITY_CHANGED")
        if self._digest() != self.digest:
            raise Unknown("CONTROLLER_MANIFEST_CONTENT_CHANGED")
        # Re-taking the same OFD flock is harmless; this is not proof against a
        # separate process that ignores the cooperative lock.
        fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def close(self):
        os.close(self.fd)


class EventStream:
    """Event-order witness through full selected-resource relinquishment.

    No wall-clock value selects interval membership. `--since 0` requests the
    daemon's retained history plus live tail. If history has evicted either
    barrier at replay, or live and replay differ, acceptance is UNKNOWN.
    """

    def __init__(self, kind, volume=None):
        self.kind = kind
        self.volume = volume
        command = ["docker", "events", "--since", "0"]
        if kind != "global":
            command += ["--filter", "type=" + kind]
        if volume is not None and kind == "volume":
            command += ["--filter", "volume=" + volume]
        command += ["--format", "{{json .}}"]
        self.command = command
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        os.set_blocking(self.process.stdout.fileno(), False)
        self.partial = b""
        self.events = []
        self.anchor_cid = None
        self.anchor_index = None
        self.terminal_cid = None
        self.terminal_index = None
        self.final_cid = None
        self.final_index = None
        self.volume_destroy_expected = False
        self.volume_destroy_seen = False
        self.volume_create_seen = False
        self.closed = False

    def _selected(self, item):
        if not isinstance(item.get("timeNano"), int):
            raise Unknown("EVENT_INCOMPLETE " + self.kind)
        if self.kind == "global":
            kind = item.get("Type")
            if kind == "container":
                return item.get("Action") in ("create", "destroy")
            if kind == "volume":
                return (item.get("Actor", {}).get("ID") == self.volume
                        and item.get("Action") in ("create", "mount", "unmount", "destroy"))
            return False
        if item.get("Type") != self.kind:
            raise Unknown("EVENT_INCOMPLETE " + self.kind)
        if self.kind == "volume":
            if item.get("Actor", {}).get("ID") != self.volume:
                raise Unknown("VOLUME_EVENT_SUBJECT_CHANGED")
            return True
        return item.get("Action") in ("create", "destroy")

    def _barrier(self, item, cid):
        if self.kind in ("container", "global"):
            return (item.get("Type") == "container" and item.get("Action") == "create"
                    and item.get("Actor", {}).get("ID") == cid)
        attrs = item.get("Actor", {}).get("Attributes", {})
        return (item.get("Action") == "mount" and attrs.get("container") == cid
                and attrs.get("read/write") == "false")

    def _final_barrier(self, item):
        if self.kind in ("container", "global"):
            return (item.get("Type") == "container" and item.get("Action") == "create"
                    and item.get("Actor", {}).get("ID") == self.final_cid)
        return (item.get("Action") == "destroy"
                and item.get("Actor", {}).get("ID") == self.volume)

    def _enforce(self, item, allowed):
        if self.kind == "global":
            allowed_ids, allowed_rw = allowed
            if item["Type"] == "container":
                if item.get("Action") == "create":
                    cid = item.get("Actor", {}).get("ID")
                    if not isinstance(cid, str) or cid not in allowed_ids:
                        raise Unknown("UNADMITTED_CONTAINER_CREATE " + str(cid))
                return
            action = item.get("Action")
            if action == "create":
                if self.volume_create_seen or self.volume_destroy_seen:
                    raise Unknown("VOLUME_RECREATE_EVENT")
                self.volume_create_seen = True
            elif action == "mount":
                attrs = item.get("Actor", {}).get("Attributes", {})
                rw, cid = attrs.get("read/write"), attrs.get("container")
                if rw not in ("true", "false") or not isinstance(cid, str):
                    raise Unknown("MOUNT_EVENT_INCOMPLETE")
                if rw == "true" and cid not in allowed_rw:
                    raise Unknown("COMPETING_RW_MOUNT_EVENT " + cid)
            elif action == "destroy":
                if not self.volume_destroy_expected or self.volume_destroy_seen:
                    raise Unknown("UNEXPECTED_VOLUME_DESTROY_EVENT")
                self.volume_destroy_seen = True
            return
        if self.kind == "container":
            cid = item.get("Actor", {}).get("ID")
            if not isinstance(cid, str) or not cid:
                raise Unknown("CONTAINER_EVENT_CID_UNKNOWN")
            if item.get("Action") == "create" and cid not in allowed:
                raise Unknown("UNADMITTED_CONTAINER_CREATE " + cid)
        elif item.get("Action") == "mount":
            attrs = item.get("Actor", {}).get("Attributes", {})
            rw, cid = attrs.get("read/write"), attrs.get("container")
            if rw not in ("true", "false") or not isinstance(cid, str):
                raise Unknown("MOUNT_EVENT_INCOMPLETE")
            if rw == "true" and cid != allowed:
                raise Unknown("COMPETING_RW_MOUNT_EVENT " + cid)
        elif item.get("Action") == "create":
            raise Unknown("VOLUME_RECREATE_EVENT")
        elif item.get("Action") in ("destroy", "remove"):
            if (item.get("Action") != "destroy" or not self.volume_destroy_expected
                    or self.volume_destroy_seen):
                raise Unknown("UNEXPECTED_VOLUME_DESTROY_EVENT")
            self.volume_destroy_seen = True

    def poll(self, allowed):
        if self.closed or self.process.poll() is not None:
            raise Unknown("EVENT_STREAM_LOST " + self.kind)
        while True:
            try:
                chunk = os.read(self.process.stdout.fileno(), 65536)
            except BlockingIOError:
                break
            if not chunk:
                raise Unknown("EVENT_STREAM_EOF " + self.kind)
            self.partial += chunk
            if len(self.partial) > 1_048_576:
                raise Unknown("EVENT_STREAM_OVERFLOW " + self.kind)
            while b"\n" in self.partial:
                line, self.partial = self.partial.split(b"\n", 1)
                try:
                    item = json.loads(line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise Unknown("EVENT_PARSE_LOST " + self.kind) from exc
                if not self._selected(item):
                    continue
                self.events.append(item)
                if len(self.events) > 100_000:
                    raise Unknown("EVENT_BUFFER_LIMIT " + self.kind)
                index = len(self.events) - 1
                if self.anchor_index is None:
                    if self.anchor_cid and self._barrier(item, self.anchor_cid):
                        self.anchor_index = index
                    continue
                self._enforce(item, allowed)
                if (self.terminal_index is None and self.terminal_cid
                        and self._barrier(item, self.terminal_cid)):
                    self.terminal_index = index
                if self.final_index is None and self.final_cid is not None and self._final_barrier(item):
                    if self.terminal_index is None:
                        raise Unknown("FINAL_BEFORE_TERMINAL " + self.kind)
                    self.final_index = index
        return len(self.events)

    def anchor(self, cid, allowed):
        self.anchor_cid = cid
        deadline = time.monotonic() + 8
        while self.anchor_index is None and time.monotonic() < deadline:
            self.poll(allowed)
            time.sleep(0.05)
        if self.anchor_index is None:
            raise Unknown("START_BARRIER_NOT_OBSERVED " + self.kind)
        return self.anchor_index

    def terminal(self, cid, allowed):
        self.terminal_cid = cid
        deadline = time.monotonic() + 8
        while self.terminal_index is None and time.monotonic() < deadline:
            self.poll(allowed)
            time.sleep(0.05)
        if self.terminal_index is None:
            raise Unknown("TERMINAL_BARRIER_NOT_OBSERVED " + self.kind)
        return self.terminal_index

    def expect_volume_destroy(self):
        if self.kind not in ("volume", "global") or self.terminal_index is None or self.volume_destroy_expected:
            raise Unknown("VOLUME_DESTROY_ORDER_REFUSED")
        self.volume_destroy_expected = True
        if self.kind == "volume":
            self.final_cid = self.volume

    def final_destroy(self, allowed):
        if self.kind != "volume" or not self.volume_destroy_expected:
            raise Unknown("VOLUME_FINAL_ORDER_REFUSED")
        # The selected volume name and event subject, not a local clock,
        # identifies the final destructive event in this stream.
        return self._await_final(allowed)

    def final_container(self, cid, allowed):
        if self.kind not in ("container", "global") or self.terminal_index is None:
            raise Unknown("CONTAINER_FINAL_ORDER_REFUSED")
        self.final_cid = cid
        return self._await_final(allowed)

    def _await_final(self, allowed):
        deadline = time.monotonic() + 8
        while self.final_index is None and time.monotonic() < deadline:
            self.poll(allowed)
            time.sleep(0.05)
        if self.final_index is None:
            raise Unknown("FINAL_BARRIER_NOT_OBSERVED " + self.kind)
        return self.final_index

    def _replay(self):
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        os.set_blocking(process.stdout.fileno(), False)
        partial = b""
        anchor_seen = False
        replay = []
        found_final = False
        deadline = time.monotonic() + 10
        try:
            while time.monotonic() < deadline and not found_final:
                if process.poll() is not None:
                    raise Unknown("REPLAY_STREAM_LOST " + self.kind)
                try:
                    chunk = os.read(process.stdout.fileno(), 65536)
                except BlockingIOError:
                    time.sleep(0.05)
                    continue
                if not chunk:
                    raise Unknown("REPLAY_STREAM_EOF " + self.kind)
                partial += chunk
                if len(partial) > 1_048_576:
                    raise Unknown("REPLAY_BUFFER_LIMIT " + self.kind)
                while b"\n" in partial:
                    line, partial = partial.split(b"\n", 1)
                    try:
                        item = json.loads(line)
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                        raise Unknown("REPLAY_PARSE_LOST " + self.kind) from exc
                    if not self._selected(item):
                        continue
                    if not anchor_seen:
                        if self._barrier(item, self.anchor_cid):
                            anchor_seen = True
                        continue
                    replay.append(item)
                    if self._final_barrier(item):
                        found_final = True
                        break
            if not anchor_seen or not found_final:
                raise Unknown("REPLAY_BARRIER_MISSING " + self.kind)
            return replay
        finally:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
            process.stdout.close()
            process.stderr.close()

    def reconcile(self, allowed, expected_writer):
        if (self.anchor_index is None or self.terminal_index is None
                or self.final_index is None):
            raise Unknown("EVENT_BARRIERS_INCOMPLETE " + self.kind)
        live = self.events[self.anchor_index + 1:self.final_index + 1]
        replay = self._replay()
        if live != replay:
            raise Unknown("EVENT_REPLAY_MISMATCH " + self.kind)
        if not any(self._barrier(e, self.terminal_cid) for e in replay):
            raise Unknown("TERMINAL_BARRIER_MISSING_FROM_REPLAY " + self.kind)
        if not self._final_barrier(replay[-1]):
            raise Unknown("FINAL_BARRIER_MISSING_FROM_REPLAY " + self.kind)
        if self.kind == "global":
            if not self.volume_create_seen or not self.volume_destroy_seen:
                raise Unknown("SELECTED_VOLUME_LIFECYCLE_INCOMPLETE")
            if not any(e.get("Type") == "container" and e.get("Action") == "create"
                       and e.get("Actor", {}).get("ID") == expected_writer for e in replay):
                raise Unknown("EXPECTED_WRITER_CREATE_EVENT_MISSING")
            if not any(e.get("Type") == "volume" and e.get("Action") == "mount"
                       and e.get("Actor", {}).get("Attributes", {}).get("container") == expected_writer
                       and e.get("Actor", {}).get("Attributes", {}).get("read/write") == "true"
                       for e in replay):
                raise Unknown("EXPECTED_WRITER_RW_MOUNT_EVENT_MISSING")
            if not any(e.get("Type") == "volume" and e.get("Action") == "destroy"
                       for e in replay):
                raise Unknown("SELECTED_VOLUME_DESTROY_NOT_IN_REPLAY")
            return {"live_event_count": len(live), "replay_event_count": len(replay),
                    "preselection_cid": self.anchor_cid,
                    "terminal_barrier_cid": self.terminal_cid,
                    "postcustody_barrier_cid": self.final_cid,
                    "selected_volume_destroyed": True}
        if self.kind == "container":
            if not any(e.get("Action") == "create" and e.get("Actor", {}).get("ID") == expected_writer
                       for e in replay):
                raise Unknown("EXPECTED_WRITER_CREATE_EVENT_MISSING")
            return {"live_event_count": len(live), "replay_event_count": len(replay),
                    "start_barrier_cid": self.anchor_cid,
                    "terminal_barrier_cid": self.terminal_cid,
                    "final_barrier_cid": self.final_cid,
                    "created_cids": [e["Actor"]["ID"] for e in replay
                                     if e.get("Action") == "create"]}
        if not any(e.get("Action") == "mount"
                   and e.get("Actor", {}).get("Attributes", {}).get("container") == expected_writer
                   and e["Actor"]["Attributes"].get("read/write") == "true"
                   for e in replay):
            raise Unknown("EXPECTED_WRITER_RW_MOUNT_EVENT_MISSING")
        if not self.volume_destroy_seen or not self.volume_destroy_expected:
            raise Unknown("SELECTED_VOLUME_DESTROY_NOT_OBSERVED")
        return {"live_event_count": len(live), "replay_event_count": len(replay),
                "start_barrier_cid": self.anchor_cid,
                "terminal_barrier_cid": self.terminal_cid,
                "final_destroy_volume": self.volume,
                "rw_mount_cids": [e["Actor"]["Attributes"]["container"]
                                   for e in replay if e.get("Action") == "mount"
                                   and e["Actor"]["Attributes"].get("read/write") == "true"]}

    def close(self):
        self.closed = True
        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=3)
        self.process.stdout.close()
        self.process.stderr.close()

    def drain_complete(self, allowed):
        """Do not silently drop a fragmented final event line."""
        deadline = time.monotonic() + 2
        while True:
            self.poll(allowed)
            if not self.partial:
                return
            if time.monotonic() >= deadline:
                raise Unknown("INCOMPLETE_FINAL_EVENT_LINE " + self.kind)
            time.sleep(0.05)


class VolumeEvents(EventStream):
    def __init__(self, volume):
        super().__init__("volume", volume)


class ContainerEvents(EventStream):
    def __init__(self):
        super().__init__("container")


class GlobalEvents(EventStream):
    def __init__(self, volume):
        super().__init__("global", volume)


def inventory(volume, allowed_writer, keeper_cid, *, require_writer):
    # Ask the daemon for every container referencing this exact volume,
    # including stopped containers. Unrelated auto-removing containers cannot
    # invalidate this snapshot; the volume event stream covers short-lived
    # mounts that disappear between snapshots.
    ids = docker("ps", "-aq", "--filter", "volume=" + volume).stdout.splitlines()
    attached = []
    for cid in ids:
        values = json.loads(docker("container", "inspect", cid).stdout)
        if len(values) != 1:
            raise Unknown("CONTAINER_INSPECT_AMBIGUOUS")
        item = values[0]
        for mount in item.get("Mounts", []):
            if mount.get("Name") != volume:
                continue
            if mount.get("Type") != "volume":
                raise Unknown("VOLUME_MOUNT_TYPE_CHANGED")
            rw = mount.get("RW")
            attached.append({"cid": item["Id"], "rw": rw,
                             "state": item["State"]["Status"]})
            if rw is True and item["Id"] != allowed_writer:
                raise Unknown("COMPETING_RW_MOUNT_INVENTORY " + item["Id"])
            if rw not in (True, False):
                raise Unknown("MOUNT_RW_UNKNOWN")
    if not any(row["cid"] == keeper_cid and row["rw"] is False for row in attached):
        raise Unknown("KEEPER_REFERENCE_LOST")
    if require_writer and not any(row["cid"] == allowed_writer and row["rw"] is True
                                  for row in attached):
        raise Unknown("WRITER_RW_REFERENCE_LOST")
    return attached


