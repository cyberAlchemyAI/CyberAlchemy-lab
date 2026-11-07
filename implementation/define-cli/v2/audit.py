#!/usr/bin/env python3
"""Read-only runtime/schema/legacy-preservation audit. Does not authorize release."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from define_runtime.cli import integrity, REPO, PACKAGE
from define_runtime.contracts import SCHEMAS
from define_runtime.exact import decode, encode, read, require, sha


def main():
    checked = integrity()
    for name, schema in SCHEMAS.items():
        selected = decode(read(PACKAGE / "schemas" / (name + ".schema.json")))
        require(selected == {"$schema": "https://json-schema.org/draft/2020-12/schema", **schema}, "generated-schema-drift")
    legacy = decode(read(REPO / "implementation/define-cli/v1/runtime-manifest.json"))
    for row in legacy["files"]:
        require(sha(read(REPO / row["path"])) == row["sha256"], "legacy-source-drift", row["path"], 3)
    print(json.dumps({"runtime_integrity": "verified", "runtime_files": checked, "generated_schemas": len(SCHEMAS),
                      "legacy_members_unchanged": len(legacy["files"]), "live_host_qualification": "not-established",
                      "operational_release_ready": False, "actual_owner_outcome": None, "authority_effect": "none"}, indent=2))


if __name__ == "__main__":main()
