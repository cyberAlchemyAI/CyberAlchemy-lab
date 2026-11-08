"""Cold account of the 363-member original package and its 681 selected files."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
INPUTS = ROOT / "product/lab/release-candidates/v1/release-validation/0001/final-member-inputs-0276.json"
INPUTS_SHA256 = "a099221682af6d061cad24f4759ec225541f203882627fa74361285b54b25987"
INVENTORY = ROOT / "docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-review-0247/inventory.json"
INVENTORY_SHA256 = "2cd9850f8da1dfbf5c6a4a531f2ad0730956956c57d26003d0456196b5862f1d"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected(root, binding):
    if set(binding) != {"path", "sha256"}:
        raise ValueError("selected binding shape changed")
    relative = Path(binding["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("selected binding leaves checkout")
    path = root / relative
    if path.resolve() != path or not path.is_file():
        raise ValueError("selected bytes changed")
    raw = path.read_bytes()
    if sha(raw) != binding["sha256"]:
        raise ValueError("selected bytes changed")
    return raw


def account(inputs, inventory, root=ROOT):
    if inputs["original_members"] != 363 or inventory["member_count"] != 363:
        raise ValueError("original member count changed")
    binding = inputs["original_final_inventory_binding"]
    if binding != {"path": INVENTORY.relative_to(ROOT).as_posix(), "sha256": INVENTORY_SHA256}:
        raise ValueError("original inventory selector changed")
    rows = inventory["members"]
    ids = []
    for row in rows:
        keys = set(row) & {"member_id", "member_ref"}
        if len(keys) != 1:
            raise ValueError("original member identity changed")
        ids.append(row[keys.pop()])
    if len(rows) != 363 or len(set(ids)) != 363:
        raise ValueError("original member identity changed")
    files = inputs["files"]
    if len(files) != 681 or len({row["path"] for row in files}) != 681:
        raise ValueError("original input file inventory changed")
    for row in files:
        selected(root, row)
    return {"schema_version": "lab-t25-original-package-accounting/v1",
            "input_selection_sha256": INPUTS_SHA256, "original_inventory_sha256": INVENTORY_SHA256,
            "original_members": 363, "selected_public_files_rehashed": 681,
            "member_ids": ids, "original_package_materialized": False,
            "new_local_additions_accounted": False, "task_complete": False}


def run():
    inputs = json.loads(selected(ROOT, {"path": INPUTS.relative_to(ROOT).as_posix(), "sha256": INPUTS_SHA256}))
    inventory = json.loads(selected(ROOT, {"path": INVENTORY.relative_to(ROOT).as_posix(), "sha256": INVENTORY_SHA256}))
    return account(inputs, inventory)


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
