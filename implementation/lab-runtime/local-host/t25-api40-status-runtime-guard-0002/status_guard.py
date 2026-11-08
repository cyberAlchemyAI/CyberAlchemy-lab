"""Relocatable seven-file API40 lab.status dependency preflight, not Service."""

import hashlib
import json
import os
from pathlib import Path
import stat
import sys

SOURCE_SHA = "45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219"
PROFILE_SHA = "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614"
API = "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/"
ROWS = (
    (API + "serve.py", "9c5d3cc01aa7cfb3da28f59b0d66562d7ded8e8e6f14e193897554983da8d9b0"),
    (API + "guard.py", "c447471b3a7ba342f5a47ce9720c70e6c5c43512c23c7dc955b0b129053ecb64"),
    (API + "service.py", "6c6cd97c1735e162758bb9c6d2df745db782ac4b3dd051d95192acfc569f0e60"),
    (API + "handlers.py", "5bfeadd53581306e14be7ab40ff4ac8451375b2ed52475e76f29fcfe73dd451f"),
    (API + "protocol.py", "f3f24585ac712732c297ef04b4a7f31f6cd70745b60f6dd0bc5df92b40d7bcde"),
    (API + "auth.py", "f667de38d845b59de41679d7cdad4f632ff4b60bc98d419557fb4091d0693bef"),
    ("docs/proposals/0008-lab-api-contracts/api-contracts.json",
     "4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1"),
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate profile key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite profile")))


def read_exact(root, name):
    root = Path(root)
    path = Path(name)
    if not root.is_absolute() or ".." in root.parts or path.is_absolute() or ".." in path.parts:
        raise ValueError("unsafe selected dependency path")
    full = root / path
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in full.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        leaf = os.open(full.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            if not stat.S_ISREG(os.fstat(leaf).st_mode):
                raise ValueError("nonregular selected dependency")
            with os.fdopen(os.dup(leaf), "rb") as stream:
                return stream.read()
        finally:
            os.close(leaf)
    finally:
        os.close(fd)


def run(root, profile_sha):
    raw = read_exact(root, "META/technical-profile.json")
    if sha(raw) != profile_sha:
        raise ValueError("technical profile changed")
    profile = parse(raw)
    if profile != {"schema_version": "lab-api40-status-runtime-guard-profile/v2",
                   "original_source_manifest_sha256": SOURCE_SHA,
                   "original_contract_profile_sha256": PROFILE_SHA,
                   "operation": "lab.status",
                   "rows": [{"path": name, "sha256": digest} for name, digest in ROWS],
                   "full_source_guard_rows_omitted": 201,
                   "original_service_executed": False,
                   "authority_effect": "none"}:
        raise ValueError("technical profile selection differs")
    for name, expected in ROWS:
        if sha(read_exact(root, name)) != expected:
            raise ValueError("source changed " + name)
    return {"schema_version": "lab-api40-status-runtime-guard-result/v1",
            "status": "PASS", "operation": "lab.status",
            "verified_file_count": len(ROWS),
            "original_service_executed": False,
            "portable_api40_closure_complete": False,
            "authority_effect": "none"}


def main():
    if len(sys.argv) != 3:
        raise SystemExit(2)
    try:
        result = run(sys.argv[1], sys.argv[2])
    except (FileNotFoundError, ValueError, OSError) as error:
        print(json.dumps({"schema_version": "lab-api40-status-runtime-guard-result/v1",
                          "status": "REFUSED", "error_class": type(error).__name__,
                          "error": str(error), "original_service_executed": False,
                          "authority_effect": "none"}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
