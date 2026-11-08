"""Cold-check that the candidate status still describes the selected local smoke."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[4]
STATUS = Path(__file__).with_name("RELEASE-STATUS-0001.json")
SELECTED_REFERENCES = {
    "candidate_inventory": ("implementation/lab-runtime/local-host/t25-local-candidate-0001/INVENTORY.json",
                            "268e54ebce2674006b327f1a1d5c45ff64ac7031465eaa3d9b35e4845306b8e9"),
    "candidate_result": ("implementation/lab-runtime/local-host/t25-local-candidate-0001/RESULT.json",
                         "649cf258cdbb22b3bbd4daea4cad4808dfa3a70ca7f2bbdd9b1b5be9fe4b6182"),
    "local_import": ("implementation/lab-runtime/local-host/t30-candidate-rehearsal-0001/RESULT.json",
                     "42bb3468826059bdc5636f69b6b024c2e70e1eddcf58d90c6347802448d6c451"),
    "docker_smoke": ("implementation/lab-runtime/local-host/t30-candidate-rehearsal-0001/RUN-DOCKER-0001.json",
                     "27b1652ecbf78ba48c81d3676ec8a77410db9989dcbb728537eba53fea68b66e"),
    "docker_review": ("implementation/lab-runtime/local-host/working/t30-candidate-rehearsal-independent-review-0001/REVIEW-0003.md",
                      "f96aa5c9b34fe1f55cba8b24c15d46d56d5dc77ac3d4786e0e6ec5d5aee4679e"),
}
ARCHIVE_SHA256 = "020f2755bd2687003f15d93a49a1e3bd6a49d838e3efe1398d6731881edce448"
LOCAL_GAPS = ["portable installed API40 closure", "all selected API checks",
              "full uninstall and restore from candidate", "final original-member dispositions"]
ORIGINAL_GAPS = ["AC12 human pilot usefulness", "protected Source8 qualification",
                 "repository-owner Decision and admission", "canonical publication/release"]


def read_regular(path: Path) -> bytes:
    cursor = path
    while cursor != cursor.parent:
        state = cursor.lstat()
        if cursor == path:
            if not stat.S_ISREG(state.st_mode):
                raise ValueError("release reference is not a regular file")
        elif not stat.S_ISDIR(state.st_mode):
            raise ValueError("release reference ancestor is not a directory")
        cursor = cursor.parent
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError("release reference is not a regular file")
        with os.fdopen(fd, "rb", closefd=False) as source:
            raw = source.read()
    finally:
        os.close(fd)
    return raw


def selected(ref: dict) -> bytes:
    raw = read_regular(ROOT / ref["path"])
    if hashlib.sha256(raw).hexdigest() != ref["sha256"]:
        raise ValueError("release reference bytes changed")
    return raw


def verify() -> dict:
    record = json.loads(read_regular(STATUS))
    selected_refs = {name: {"path": path, "sha256": digest}
                     for name, (path, digest) in SELECTED_REFERENCES.items()}
    if (record["schema_version"] != "lab-local-engineering-release-status/v1" or
            record["status"] != "candidate-not-released" or
            record["references"] != selected_refs or
            record["archive_sha256"] != ARCHIVE_SHA256 or
            record["local_fixture_smoke_passed"] is not True or
            record["selected_docker_cleanup_passed"] is not True or
            record["local_fixture_journeys"] != ["source-reader-mapper-context", "work"] or
            record["authority_effect"] != "none" or
            record["external_publication_effects"] != 0 or
            record["ephemeral_docker_resources_created_and_removed"] is not True or
            record["unfulfilled_local_checks"] != LOCAL_GAPS or
            record["unfulfilled_original_clauses"] != ORIGINAL_GAPS):
        raise ValueError("release-status claim differs")
    evidence = {name: selected(ref) for name, ref in record["references"].items()}
    smoke = json.loads(evidence["docker_smoke"])
    if (smoke["archive_sha256"] != record["archive_sha256"] or
            smoke["both_journeys_passed"] is not True or
            smoke["cleanup_passed"] is not True or
            smoke["installed_api40_replay"] is not False or
            smoke["full_t30_release"] is not False):
        raise ValueError("selected Docker smoke differs")
    return {"result": "PASS", "status": record["status"],
            "selected_archive_sha256": record["archive_sha256"],
            "reference_count": len(evidence)}


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
