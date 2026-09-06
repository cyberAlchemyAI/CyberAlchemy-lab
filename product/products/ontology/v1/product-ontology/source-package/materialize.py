#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_REPO = Path("/home/vrondelli/projects/domainspec-core")
SOURCE_PACKAGE = SOURCE_REPO / "cyberAlchemy-v2/ontology/ontology-product"
IMPORTED = ROOT / "imported"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    migration = json.loads((ROOT / "migration.json").read_text(encoding="utf-8"))
    IMPORTED.mkdir(parents=True, exist_ok=True)
    for item in migration["imported_files"]:
        source = SOURCE_PACKAGE / item["path"]
        if sha(source) != item["sha256"]:
            raise SystemExit(f"SOURCE_PACKAGE_DRIFT:{item['path']}")
        shutil.copyfile(source, IMPORTED / item["path"])

    legacy = json.loads((IMPORTED / "sources.json").read_text(encoding="utf-8"))
    bindings = []
    for item in legacy["sources"]:
        source = SOURCE_REPO / item["path"]
        if not source.is_file():
            raise SystemExit(f"SOURCE_MISSING:{item['id']}:{item['path']}")
        current = sha(source)
        drifted = current != item["sha256"]
        bindings.append({
            "source_id": item["id"],
            "path": item["path"],
            "owner_route": item["owner_route"],
            "legacy_sha256": item["sha256"],
            "current_sha256": current,
            "binding_status": "drift-reconciled-by-successor-binding" if drifted else "current",
            "resolution": "Preserve the historical digest in imported sources.json and bind the Lab candidate to the exact current source bytes." if drifted else "The historical and current source digests agree."
        })
    ledger = {
        "schema_version": "cyberalchemy-lab-product-ontology-source-bindings/v1",
        "binding_id": "CAL-ONTOLOGY-PRODUCT-SOURCE-BINDINGS-0001",
        "status": "test-candidate",
        "authority_effect": "none",
        "source_registry_ref": "imported/sources.json",
        "source_registry_sha256": sha(IMPORTED / "sources.json"),
        "bindings": bindings,
        "drift_policy": "A changed source receives an explicit successor binding; no canonical field is inferred or silently overwritten.",
        "claim_ceiling": "These bindings select exact current source bytes for private testing only. They do not admit sources or repair the historical CyberAlchemy-v2 registry."
    }
    (ROOT / "source-bindings.json").write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
