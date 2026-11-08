"""Prepare a new W03 signed Source whose Implementation selects Reader v2.

This stages only code and a source manifest. Signing is a separate native run.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INSTANCES = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances"
OLD_ID = "legacy-local-8d0312c813444f57"
NEW_ID = "legacy-local-62f4c217e8b9a30d"
OLD = INSTANCES / OLD_ID
NEW = INSTANCES / NEW_ID
OLD_SOURCE_SHA = "14639c94bd192ebbaf0f34524e588bf7b09ea75616e2b10bbe53df98695833d6"
SOURCE_FILES = ("__init__.py", "base.py", "build.py", "cold.py", "context-native-role.json", "episode-contract.json", "records.py")
READER_FILES = ("__init__.py", "adapter.py", "base.py", "eligibility.py", "inspection.py", "model.py", "reader.py")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def row(path: Path) -> dict[str, str]:
    if path.is_symlink() or not path.is_file() or not path.is_relative_to(ROOT):
        raise ValueError("unselected Source/Reader closure member")
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path.read_bytes())}


def stage() -> dict:
    prior_path = OLD / "source/source-manifest.json"
    if digest(prior_path.read_bytes()) != OLD_SOURCE_SHA:
        raise ValueError("predecessor Source manifest changed")
    if NEW.exists():
        raise ValueError("new Source instance already exists")
    (NEW / "source").mkdir(parents=True)
    (NEW / "reader-w03-0002").mkdir()
    old_text = OLD_ID.encode()
    new_text = NEW_ID.encode()
    for leaf in SOURCE_FILES:
        raw = (OLD / "source" / leaf).read_bytes().replace(old_text, new_text)
        if leaf == "records.py":
            old_entry = (f"instances/{NEW_ID}/reader/reader.py#SelectedReader.open_signed").encode()
            new_entry = (f"instances/{NEW_ID}/reader-w03-0002/reader.py#SelectedReader.open_signed").encode()
            if raw.count(old_entry) != 1:
                raise ValueError("Source Implementation entrypoint anchor differs")
            raw = raw.replace(old_entry, new_entry)
        if leaf == "episode-contract.json":
            episode = json.loads(raw)
            start = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(minutes=1)
            episode["not_before"] = start.isoformat()
            episode["expires_at"] = (start + timedelta(hours=24)).isoformat()
            raw = (json.dumps(episode, sort_keys=True, indent=2) + "\n").encode()
        (NEW / "source" / leaf).write_bytes(raw)
    for leaf in READER_FILES:
        raw = (OLD / "reader-w03-0002" / leaf).read_bytes().replace(old_text, new_text)
        (NEW / "reader-w03-0002" / leaf).write_bytes(raw)
    manifest = json.loads(prior_path.read_bytes())
    old_prefix = (OLD / "source").relative_to(ROOT).as_posix() + "/"
    kept = [item for item in manifest["files"] if not item["path"].startswith(old_prefix)]
    if len(manifest["files"]) - len(kept) != len(SOURCE_FILES):
        raise ValueError("predecessor Source self-closure differs")
    staged = [row(NEW / "source" / leaf) for leaf in SOURCE_FILES]
    reader = [row(NEW / "reader-w03-0002" / leaf) for leaf in READER_FILES]
    paths = {item["path"] for item in kept}
    if any(item["path"] in paths for item in staged + reader):
        raise ValueError("new Source/Reader path collides with inherited closure")
    manifest["files"] = sorted(kept + staged + reader, key=lambda item: item["path"])
    manifest["construction_status"] = "construction-bound-unqualified-w03-reader-v2-exact-entrypoint"
    source_path = NEW / "source/source-manifest.json"
    source_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    current = json.loads(source_path.read_bytes())
    if {r["path"]: r["sha256"] for r in current["files"]} != {
        r["path"]: digest((ROOT / r["path"]).read_bytes()) for r in current["files"]
    }:
        raise ValueError("new Source manifest closure did not cold rehash")
    return {"instance": NEW_ID, "source_manifest_sha256": digest(source_path.read_bytes()),
            "source_rows": len(current["files"]), "new_reader_code_rows": len(reader),
            "implementation_entrypoint": f"{(NEW / 'reader-w03-0002/reader.py').relative_to(ROOT)}#SelectedReader.open_signed"}


if __name__ == "__main__":
    print(json.dumps(stage(), sort_keys=True))
