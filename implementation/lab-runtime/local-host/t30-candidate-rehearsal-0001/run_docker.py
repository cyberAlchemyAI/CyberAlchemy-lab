"""Run both local product journeys from a clean extraction of the T25 archive."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import uuid

import rehearse


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def command(args: list[str], *, env: dict[str, str] | None = None,
            timeout: int = 1800, expected_stdout: bytes | None = None) -> dict:
    start = time.monotonic()
    result = subprocess.run(args, cwd=rehearse.ROOT, env=env,
                            capture_output=True, timeout=timeout)
    return {"args": args[1:], "exit_code": result.returncode,
            "expected_stdout_seen": expected_stdout is None or expected_stdout in result.stdout,
            "stdout_sha256": sha(result.stdout), "stderr_sha256": sha(result.stderr),
            "elapsed_seconds": round(time.monotonic() - start, 3),
            "stdout_tail": result.stdout.decode("utf-8", errors="replace")[-2000:],
            "stderr_tail": result.stderr.decode("utf-8", errors="replace")[-2000:]}


def owned_resources(project: str, image: str) -> dict:
    containers = subprocess.run(["docker", "ps", "-aq", "--filter",
                                 f"label=com.docker.compose.project={project}"],
                                capture_output=True, check=True).stdout.decode().splitlines()
    volumes = subprocess.run(["docker", "volume", "ls", "-q", "--filter",
                              f"label=com.docker.compose.project={project}"],
                             capture_output=True, check=True).stdout.decode().splitlines()
    networks = subprocess.run(["docker", "network", "ls", "-q", "--filter",
                               f"label=com.docker.compose.project={project}"],
                              capture_output=True, check=True).stdout.decode().splitlines()
    inspect = subprocess.run(["docker", "image", "inspect", image],
                             capture_output=True)
    return {"containers": sorted(containers), "volumes": sorted(volumes),
            "networks": sorted(networks),
            "image_present": inspect.returncode == 0}


def run() -> dict:
    package, _, _ = rehearse.selected_modules()
    body = package.build()
    if sha(body) != rehearse.ARCHIVE_SHA:
        raise ValueError("candidate archive differs")
    token = uuid.uuid4().hex
    project = "cal-t30-" + token[:20]
    image = "cyberalchemy-lab-t30:local-" + token
    with tempfile.TemporaryDirectory(prefix="cal-t30-candidate-docker-") as name:
        root = Path(name) / "release"
        root.mkdir(mode=0o700)
        extraction = package.extract_verified(body, root)
        if extraction["extracted_fixture_context_verified"] is not True:
            raise ValueError("candidate fixture extraction refused")
        context = root / "fixture"
        compose = context / "compose.yaml"
        env = os.environ.copy()
        env["LAB_LOCAL_BUILD_CONTEXT"] = str(context)
        env["LAB_LOCAL_IMAGE"] = image
        prefix = ["docker", "compose", "-p", project, "-f", str(compose)]
        before = owned_resources(project, image)
        if before != {"containers": [], "volumes": [], "networks": [],
                      "image_present": False}:
            raise ValueError("unique Docker identity preoccupied")
        stages = []
        cleanup = []
        try:
            for args, timeout, marker in [
                (prefix + ["build", "--no-cache", "lab-fixture"], 1800, None),
                (prefix + ["run", "--rm", "--no-deps", "--pull", "never", "chain-fixture"],
                 1800, b"local Source \xe2\x86\x92 Reader \xe2\x86\x92 Mapper \xe2\x86\x92 Context fixture: PASS"),
                (prefix + ["run", "--rm", "--no-deps", "--pull", "never", "lab-fixture"],
                 1800, b"local Work journey: PASS"),
            ]:
                stage = command(args, env=env, timeout=timeout, expected_stdout=marker)
                stages.append(stage)
                if stage["exit_code"] != 0 or not stage["expected_stdout_seen"]:
                    break
        finally:
            cleanup.append(command(prefix + ["down", "-v", "--remove-orphans"], env=env,
                                   timeout=180))
            cleanup.append(command(["docker", "image", "rm", "--", image],
                                   timeout=180))
        after = owned_resources(project, image)
        return {"schema_version": "lab-t30-candidate-docker-smoke/v1",
                "archive_sha256": sha(body), "project": project, "image": image,
                "extracted_fixture_context_verified": True,
                "stages": stages, "cleanup": cleanup,
                "owned_resources_before": before, "owned_resources_after": after,
                "both_journeys_passed": len(stages) == 3 and all(
                    s["exit_code"] == 0 and s["expected_stdout_seen"] for s in stages),
                "cleanup_passed": all(s["exit_code"] == 0 for s in cleanup)
                                  and after == before,
                "installed_api40_replay": False,
                "full_t30_release": False,
                "authority_effect": "none"}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
