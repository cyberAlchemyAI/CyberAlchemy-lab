"""One-shot Docker option probe. Never mounts private data or starts a container."""
from __future__ import annotations

import json
from pathlib import Path
import uuid

import controller as c

NAME = "cal-reader-create-diagnostic-20261020-0003"
RESULT = Path(__file__).with_name("create-only-diagnostic-0003.json")


def main() -> None:
    if RESULT.exists() or c.inspected(NAME) is not None:
        raise ValueError("diagnostic already consumed or name occupied")
    label = uuid.uuid4().hex
    argv = [c.DOCKER, "create", "--name", NAME,
            "--label", "cal.reader.diagnostic=" + label,
            "--network", "none", "--read-only", "--cap-drop", "ALL",
            "--ipc", "private", "--uts", "private",
            "--security-opt", "no-new-privileges:true", "--pids-limit", "1",
            "--memory", "1g", "--cpus", "1", "--user", "1000:1000",
            "--tmpfs", "/attempt/tmp:rw,nosuid,nodev,size=512m,mode=0700,uid=1000,gid=1000",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=256m,mode=1777",
            c.IMAGE, "python", "-B", "-c", "pass"]
    result = {"schema_version": "lab-reader-create-only-diagnostic/v1",
              "name": NAME, "label": label, "image_id": c.IMAGE,
              "argv_sha256": c.sha(c.json_bytes(argv)), "effect": "CREATE_ONLY_NO_START"}
    try:
        proc = c.cli(argv, seconds=20)
        result.update(returncode=proc.returncode,
                      stdout_sha256=c.sha(proc.stdout), stdout_size=len(proc.stdout),
                      stderr_sha256=c.sha(proc.stderr), stderr_size=len(proc.stderr),
                      stderr_diagnostic=c.create_diagnostic(proc.stderr),
                      stderr_text=proc.stderr.decode("utf-8", "replace"))
    except BaseException as error:
        result.update(create_error_class=type(error).__name__,
                      stdout_sha256=c.sha(getattr(error, "bounded_stdout", b"")),
                      stderr_sha256=c.sha(getattr(error, "bounded_stderr", b"")),
                      stderr_diagnostic=c.create_diagnostic(getattr(error, "bounded_stderr", b"")))
    info = c.inspected(NAME)
    if info is None:
        result["observation"] = "ABSENT"
    else:
        actual = info.get("Id")
        match = (type(actual) is str and len(actual) == 64 and
                 info.get("Name") == "/" + NAME and info.get("Image") == c.IMAGE and
                 info.get("Config", {}).get("Image") == c.IMAGE and
                 info.get("Config", {}).get("Labels", {}).get("cal.reader.diagnostic") == label and
                 info.get("State", {}).get("Status") == "created" and
                 info.get("State", {}).get("Running") is False)
        result.update(observation="PRESENT", identity_match=match,
                      container_id=actual if match else None)
        if match:
            removed = c.cli([c.DOCKER, "rm", actual], seconds=8)
            result["remove_returncode"] = removed.returncode
            result["post_remove_absent"] = (removed.returncode == 0 and
                                            c.inspected(NAME) is None and
                                            c.inspected(NAME) is None)
    c.exclusive(RESULT, c.json_bytes(result))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
