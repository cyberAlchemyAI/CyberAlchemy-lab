"""Supplemental exact-current relation closure for the API38 fixture mapping."""

import ast
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
INVENTORY = ROOT / "implementation/lab-runtime/local-host/t15-inherited-method-inventory-api38-0001"
MAPPING = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8/mapped/packages/0001/mapping.json"
MAPPING_SHA256 = "6c64958278d3841d6ffe66b4981997ce4b71dfb9dc481fed45d11936db8f2f8c"
SELECTION = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v38-current-t06-0001/legacy_fixture_selection.py"
SELECTION_SHA256 = "f1fb4f8d8b5d1f631586476ff521f0d1ea0946b478f5a3d7e345cbc6b681df7e"
PREFIX = "typed-relation:completion-legacy-local-947e6c2a5b3d10f8:"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected_versions(source_bytes):
    tree = ast.parse(source_bytes)
    found = []
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not any(
            isinstance(target, ast.Name) and target.id == "EXPECTED_RELATION_VERSIONS"
            for target in node.targets
        ):
            continue
        call = node.value
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and
                call.func.id == "frozenset" and len(call.args) == 1 and not call.keywords):
            raise ValueError("selected relation constant is not a closed literal")
        found.append(ast.literal_eval(call.args[0]))
    if len(found) != 1 or type(found[0]) is not list or len(found[0]) != 10 or len(set(found[0])) != 10:
        raise ValueError("selected relation version inventory differs")
    return set(found[0])


def check_rows(rows, expected):
    selected = [row["artifact"] for row in rows
                if row["artifact"]["version_ref"].startswith(PREFIX)]
    if any(item["carrier_ref"] != "cal.artifact-type.typed-relation/v3" for item in selected):
        raise ValueError("current relation carrier differs")
    versions = [item["version_ref"] for item in selected]
    if len(versions) != 10 or set(versions) != expected:
        raise ValueError("current relation closure differs")
    return sorted(versions)


def verify():
    spec = importlib.util.spec_from_file_location("t15_api38_inventory", INVENTORY / "inventory.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    actual = (json.dumps(module.build(), sort_keys=True, indent=2) + "\n").encode()
    if actual != (INVENTORY / "INVENTORY.json").read_bytes():
        raise ValueError("API38 inventory or selected source changed")
    for path, expected in ((MAPPING, MAPPING_SHA256), (SELECTION, SELECTION_SHA256)):
        if not module.regular_without_symlink_parents(ROOT, path) or sha(path.read_bytes()) != expected:
            raise ValueError("selected fixture bytes or origin changed")
    expected = selected_versions(SELECTION.read_bytes())
    value = json.loads(MAPPING.read_bytes())
    return {"api38_source_sha256": module.CURRENT_SOURCE_SHA256,
            "mapping_sha256": MAPPING_SHA256,
            "relation_versions": check_rows(value["rows"], expected),
            "count": 10,
            "claim_ceiling": "Exact selected API38 fixture mapping closure only; live model.connections and T16/T17 remain open."}


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True, indent=2))
