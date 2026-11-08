"""Stage the W03 Reader-v2 Mapper code with exact signed producer pins."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INSTANCES = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances"
OLD = INSTANCES / "legacy-local-8d0312c813444f57"
NEW = INSTANCES / "legacy-local-62f4c217e8b9a30d"
LEAVES = ("__init__.py", "base.py", "build.py", "policy.json")
REPLACEMENTS = {
    b"legacy-local-8d0312c813444f57": b"legacy-local-62f4c217e8b9a30d",
    b"14639c94bd192ebbaf0f34524e588bf7b09ea75616e2b10bbe53df98695833d6": b"69967b19d3bb170885c28542f36b66a1a4ed8a3936abcd1850f64c44d19ac3b1",
    b"b78fe83c69e40457b891550540873c62a53294d671d7622807d2129600766d27": b"0dc6ad7f7769f96eeaa561d137d0bedd423bf33585f343f1283d36a003c94513",
    b"0cd65a9e171dd5e41afe719b52ad61fef7c7365491df1b31f9d594c7b2824081": b"63b89c72dca1c9ea2806b15ecf02d2b909328c4686a30e8a5380b52351f91baf",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(path: Path) -> dict[str, str]:
    if path.is_symlink() or not path.is_file() or not path.is_relative_to(ROOT):
        raise ValueError("unselected Mapper input")
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def main() -> dict:
    old_source = OLD / "mapped-w03-0004/source-manifest.json"
    source = NEW / "source/source-manifest.json"
    package = NEW / "source/packages/0001/manifest.json"
    reader = NEW / "reader-w03-0002/source-manifest.json"
    if sha(old_source) != "b19214cb65d40ed39adc6c413a0f6dbda2b9d77dd9025ef9f8301aec6859b04c":
        raise ValueError("predecessor Mapper changed")
    if [sha(source), sha(package), sha(reader)] != [
        "69967b19d3bb170885c28542f36b66a1a4ed8a3936abcd1850f64c44d19ac3b1",
        "0dc6ad7f7769f96eeaa561d137d0bedd423bf33585f343f1283d36a003c94513",
        "63b89c72dca1c9ea2806b15ecf02d2b909328c4686a30e8a5380b52351f91baf",
    ]:
        raise ValueError("signed W03 Source/Reader pins differ")
    path = NEW / "mapped-w03-0004"
    if path.exists():
        raise ValueError("new Mapper directory already exists")
    path.mkdir()
    for leaf in LEAVES:
        raw = (OLD / "mapped-w03-0004" / leaf).read_bytes()
        for old, new in REPLACEMENTS.items():
            raw = raw.replace(old, new)
        (path / leaf).write_bytes(raw)
    old_manifest = json.loads(old_source.read_bytes())
    selected_reader = json.loads(reader.read_bytes())
    if selected_reader["producer_source_binding"] != row(source) or selected_reader["producer_package_binding"] != row(package):
        raise ValueError("Reader selects another signed Source")
    rows: dict[str, dict[str, str]] = {}
    for item in old_manifest["files"]:
        if "legacy-local-8d0312c813444f57" not in item["path"]:
            rows[item["path"]] = item
    for item in selected_reader["files"]:
        if row(ROOT / item["path"]) != item:
            raise ValueError("Reader closure row changed")
        rows[item["path"]] = item
    rows[row(reader)["path"]] = row(reader)
    for leaf in LEAVES:
        selected = row(path / leaf)
        rows[selected["path"]] = selected
    manifest = dict(old_manifest)
    manifest["files"] = [rows[name] for name in sorted(rows)]
    manifest["original_source_binding"] = row(source)
    manifest["original_package_binding"] = row(package)
    manifest["adapter_source_binding"] = row(reader)
    manifest["construction_status"] = "construction-bound-unqualified-w03-reader-v2-exact-entrypoint"
    output = path / "source-manifest.json"
    output.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    return {"mapper_source_sha256": sha(output), "source_rows": len(manifest["files"]),
            "source_sha256": sha(source), "source_package_sha256": sha(package), "reader_sha256": sha(reader)}


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True))
