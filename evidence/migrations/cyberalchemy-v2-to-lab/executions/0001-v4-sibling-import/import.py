#!/usr/bin/env python3
"""Import the frozen ontology corpus from its relocated sibling source."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[4]
V4 = LAB / "implementation/bindings/ontology-product-event-runtime/v4"
BINARY = V4 / "target/release/cal-ontology-source-runtime"
TARGET = LAB / ".local/ontology-source-runtime-v4-sibling-import"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def need(condition, message):
    if not condition:
        raise ValueError(message)


def run(*args):
    return json.loads(subprocess.check_output([str(BINARY), *map(str, args)], cwd=LAB))


def tree(path):
    return {str(p.relative_to(path)): sha(p) for p in path.rglob("*") if p.is_file()}


def main():
    need(not TARGET.exists(), "Target already exists; observe it instead of reimporting")
    for ancestor in [TARGET, *TARGET.parents]:
        need(not ancestor.is_symlink(), "Symlink target ancestry")
    candidate = load(V4 / "candidate.json")
    approval = load(LAB / "docs/decisions/0050-source-runtime-v4-product-approval/decision.json")
    need(sha(V4 / "candidate.json") == approval["subject"]["candidate"]["sha256"], "Candidate drift")
    for ref in candidate["acceptance_material"] + candidate["preserved_material"]:
        need(sha(LAB / ref["path"]) == ref["sha256"], "Candidate material drift: " + ref["path"])
    manifest = load(HERE / "source-manifest.json")
    original = load(V4 / "source-manifest.json")
    original["roots"]["cav2"] = manifest["roots"]["cav2"]
    need(original == manifest, "Only the legacy source root may change")
    expected, documents, sources = {}, {}, {}
    counts = {"nodes": 0, "relations": 0}

    def source(ref):
        path = Path(manifest["roots"][ref["root"]]) / ref["path"]
        need(sha(path) == ref["sha256"], "Source drift: " + str(path))
        sources[path] = ref["sha256"]
        return path

    for package in manifest["packages"]:
        source(package["profile"])
        key = package["package_key"]
        for kind in counts:
            registry = package[kind]
            rows = load(source(registry["source"]))[registry["selector"].lstrip("/")]
            counts[kind] += len(rows)
            for i, row in enumerate(rows):
                expected[(key, registry["source"]["path"], registry["selector"] + "/" + str(i))] = row
        for ref in package["documents"]:
            documents[(key, ref["path"])] = source(ref).read_bytes()

    def verify_export(target):
        actual, docs = {}, {}
        before = tree(target)
        for row in run("export", target)["records"]:
            ref = row["source_binding"]
            if row["identity"]["type_ref"] == "source-document":
                key = (ref["package_key"], ref["path"])
                need(key not in docs, "Duplicate document")
                docs[key] = row["source_record"]["content"].encode("utf-8")
            else:
                key = (ref["package_key"], ref["path"], ref["selector"])
                need(key not in actual, "Duplicate record")
                actual[key] = row["source_record"]
        need(actual == expected and docs == documents, "Lossless roundtrip failed")
        summary = run("summary", target)
        need(before == tree(target), "Read commands mutated event history")
        return summary

    with tempfile.TemporaryDirectory(prefix="cal-sibling-import-") as temp:
        a, b = Path(temp) / "a", Path(temp) / "b"
        run("import", HERE / "source-manifest.json", a)
        run("import", HERE / "source-manifest.json", b)
        need(tree(a) == tree(b), "Import is not deterministic")
        baseline = verify_export(a)
        # Exercise writes only on the temporary store, keeping imported data pristine.
        for operation in ("create", "update", "retire"):
            run("apply", b, V4 / "commands" / (operation + ".json"))
        run("summary", b)
        for path, expected_sha in sources.items():
            need(sha(path) == expected_sha, "Source changed during preflight")
        TARGET.parent.mkdir(exist_ok=True)
        run("import", HERE / "source-manifest.json", TARGET)
        summary = verify_export(TARGET)
        need(summary == baseline and tree(TARGET) == tree(a), "Persistent import differs from rehearsal")
    for path, expected_sha in sources.items():
        need(sha(path) == expected_sha, "Source changed during import")
    receipt = {
        "result": "PASS", "executed_at": datetime.now(timezone.utc).isoformat(),
        "authorization": "so no we must continue importing ../cyberalchemy-v2",
        "candidate_sha256": sha(V4 / "candidate.json"),
        "execution_manifest_sha256": sha(HERE / "source-manifest.json"),
        "import_script_sha256": sha(Path(__file__)), "binary_sha256": sha(BINARY),
        "target": str(TARGET), "packages": len(manifest["packages"]),
        **counts, "documents": len(documents), "source_files_verified": len(sources),
        "lossless_export": True, "deterministic_import": True, "restart": True,
        "temporary_create_update_retire": True, "selected_sources_unchanged": True,
        "consumer_cutover": False, "summary": summary, "event_files": tree(TARGET),
    }
    with (HERE / "execution.json").open("x") as f:
        f.write(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "event_files"}, indent=2))


if __name__ == "__main__":
    main()
