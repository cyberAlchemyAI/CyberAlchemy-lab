"""Stage Context v5 projection on the newly signed Reader-v2 Mapper cut."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INSTANCES = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances"
OLD = INSTANCES / "legacy-local-8d0312c813444f57"
NEW = INSTANCES / "legacy-local-62f4c217e8b9a30d"
OLD_MAPPER_SHA = "b19214cb65d40ed39adc6c413a0f6dbda2b9d77dd9025ef9f8301aec6859b04c"
OLD_MAPPER_PACKAGE_SHA = "06860ad635e2bce7c3e302f97e4d977330df4f72a2e0b5d363965a51cdcb0414"
OLD_SOURCE_SHA = "14639c94bd192ebbaf0f34524e588bf7b09ea75616e2b10bbe53df98695833d6"
NEW_SOURCE_SHA = "69967b19d3bb170885c28542f36b66a1a4ed8a3936abcd1850f64c44d19ac3b1"
NEW_MAPPER_SHA = "09a0e50dc3ab776e9a8c8d412faf1bb73ca9a1cb13596e1930decfbc2f10ee07"
OLD_CONTEXT_SHA = "1431ae034790ed477f533a9d00fd21924817f93ff313a50ae2b940685f202d87"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(path: Path) -> dict[str, str]:
    if path.is_symlink() or not path.is_file() or not path.is_relative_to(ROOT):
        raise ValueError("unselected Context input")
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def main() -> dict:
    old_context = OLD / "context-w03-0005"
    if sha(old_context / "source-manifest.json") != OLD_CONTEXT_SHA:
        raise ValueError("predecessor Context source changed")
    mapper = NEW / "mapped-w03-0004/source-manifest.json"
    mapper_package = NEW / "mapped-w03-0004/packages/0001/manifest.json"
    if sha(mapper) != NEW_MAPPER_SHA:
        raise ValueError("new Mapper source changed")
    package_value = json.loads(mapper_package.read_bytes())
    if package_value["source_manifest_binding"] != row(mapper):
        raise ValueError("Mapper package selects another source")
    expected = {item["path"] for item in package_value["files"]} | {row(mapper_package)["path"]}
    actual = {item.relative_to(ROOT).as_posix() for item in mapper_package.parent.rglob("*") if item.is_file()}
    if actual != expected:
        raise ValueError("Mapper package closure differs")
    dest = NEW / "context-w03-0005"
    if dest.exists():
        raise ValueError("new Context directory already exists")
    dest.mkdir()
    replacements = {
        b"legacy-local-8d0312c813444f57": b"legacy-local-62f4c217e8b9a30d",
        OLD_MAPPER_SHA.encode(): NEW_MAPPER_SHA.encode(),
        OLD_MAPPER_PACKAGE_SHA.encode(): sha(mapper_package).encode(),
        OLD_SOURCE_SHA.encode(): NEW_SOURCE_SHA.encode(),
    }
    local_files = []
    for prior in old_context.rglob("*"):
        if not prior.is_file() or "packages" in prior.relative_to(old_context).parts or prior.name == "source-manifest.json" or "__pycache__" in prior.parts:
            continue
        current = dest / prior.relative_to(old_context)
        current.parent.mkdir(parents=True, exist_ok=True)
        raw = prior.read_bytes()
        for before, after in replacements.items():
            raw = raw.replace(before, after)
        if prior.name == "implementation-binding.json":
            old_entry = str((NEW / "reader/reader.py").relative_to(ROOT)).encode()
            new_entry = str((NEW / "reader-w03-0002/reader.py").relative_to(ROOT)).encode()
            if raw.count(old_entry) != 2:
                raise ValueError("Context Implementation origin anchor differs")
            raw = raw.replace(old_entry, new_entry)
            binding = json.loads(raw)
            if binding["code_binding"] != {"ref": new_entry.decode(), "sha256": sha(NEW / "reader-w03-0002/reader.py")}:
                raise ValueError("Context Implementation code binding differs")
            if binding["entrypoint_ref"] != new_entry.decode() + "#SelectedReader.open_signed":
                raise ValueError("Context Implementation method differs")
        current.write_bytes(raw)
        local_files.append(current)
    if len(local_files) != 13:
        raise ValueError("Context local constructor/protocol inventory differs")
    prior_manifest = json.loads((old_context / "source-manifest.json").read_bytes())
    mapper_manifest = json.loads(mapper.read_bytes())
    rows: dict[str, dict[str, str]] = {}
    for item in prior_manifest["files"]:
        if "legacy-local-8d0312c813444f57" not in item["path"]:
            rows[item["path"]] = item
    for item in mapper_manifest["files"]:
        if row(ROOT / item["path"]) != item:
            raise ValueError("Mapper closure member changed")
        rows[item["path"]] = item
    rows[row(mapper)["path"]] = row(mapper)
    for item in package_value["files"]:
        if row(ROOT / item["path"]) != item:
            raise ValueError("Mapper package member changed")
        rows[item["path"]] = item
    rows[row(mapper_package)["path"]] = row(mapper_package)
    for path in local_files:
        selected = row(path)
        rows[selected["path"]] = selected
    result = dict(prior_manifest)
    result["files"] = [rows[key] for key in sorted(rows)]
    result["qualified_mapper_source_binding"] = row(mapper)
    result["qualified_mapper_package_binding"] = row(mapper_package)
    result["construction_status"] = "construction-bound-unqualified-w03-reader-v2-exact-entrypoint"
    output = dest / "source-manifest.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return {"context_source_sha256": sha(output), "source_rows": len(result["files"]),
            "mapper_package_sha256": sha(mapper_package),
            "implementation_binding_sha256": sha(dest / "implementation-binding.json")}


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True))
