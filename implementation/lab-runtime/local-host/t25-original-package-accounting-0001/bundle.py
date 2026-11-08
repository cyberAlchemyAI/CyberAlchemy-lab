"""Deterministic disposable archive for the exact original T25 public inputs."""

import hashlib
import io
import json
from pathlib import Path
import tempfile
import zipfile

import account

ROOT = account.ROOT
CONTROL_INPUTS = "META/final-member-inputs.json"
CONTROL_INVENTORY = "META/original-inventory.json"
CONTROL_MANIFEST = "META/bundle-manifest.json"


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def parse(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("duplicate bundle JSON key")
            value[key] = item
        return value

    def nonfinite(_):
        raise ValueError("nonfinite bundle JSON")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)


def valid_path(value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("noncanonical bundle path")
    path = Path(value)
    if path.is_absolute() or any(part in {".", ".."} for part in value.split("/")) or path.as_posix() != value:
        raise ValueError("noncanonical bundle path")
    return path


def zip_entry(name, raw):
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info, raw


def build():
    account.run()
    input_raw = account.selected(ROOT, {"path": account.INPUTS.relative_to(ROOT).as_posix(), "sha256": account.INPUTS_SHA256})
    inventory_raw = account.selected(ROOT, {"path": account.INVENTORY.relative_to(ROOT).as_posix(), "sha256": account.INVENTORY_SHA256})
    inputs = parse(input_raw)
    rows = sorted(inputs["files"], key=lambda row: row["path"])
    if len(rows) != 681 or len({row["path"] for row in rows}) != 681:
        raise ValueError("selected original file set changed")
    payloads = []
    manifest_rows = []
    for row in rows:
        name = "files/" + valid_path(row["path"]).as_posix()
        raw = account.selected(ROOT, row)
        payloads.append((name, raw))
        manifest_rows.append({"path": row["path"], "sha256": account.sha(raw), "size": len(raw)})
    manifest = {"schema_version": "lab-t25-original-input-bundle/v1",
                "original_members": 363, "public_files": 681,
                "inputs_sha256": account.INPUTS_SHA256,
                "inventory_sha256": account.INVENTORY_SHA256,
                "new_additions_included": False, "final_package": False,
                "files": manifest_rows}
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", allowZip64=True) as archive:
        for name, raw in [(CONTROL_INPUTS, input_raw),
                          (CONTROL_INVENTORY, inventory_raw),
                          (CONTROL_MANIFEST, encoded(manifest)), *payloads]:
            archive.writestr(*zip_entry(name, raw))
    return output.getvalue()


def replay(blob):
    with zipfile.ZipFile(io.BytesIO(blob), "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != 684 or len(set(names)) != len(names):
            raise ValueError("bundle member count or uniqueness changed")
        if names[:3] != [CONTROL_INPUTS, CONTROL_INVENTORY, CONTROL_MANIFEST]:
            raise ValueError("bundle controls changed")
        for info in infos:
            valid_path(info.filename)
            if (info.is_dir() or info.compress_type != zipfile.ZIP_STORED
                    or info.create_system != 3 or info.external_attr >> 16 != 0o100644):
                raise ValueError("unsafe bundle member")
        canonical = io.BytesIO()
        with zipfile.ZipFile(canonical, "w", allowZip64=True) as rebuilt:
            for info in infos:
                rebuilt.writestr(*zip_entry(info.filename, archive.read(info)))
        if canonical.getvalue() != blob:
            raise ValueError("noncanonical bundle bytes")
        input_raw = archive.read(CONTROL_INPUTS)
        inventory_raw = archive.read(CONTROL_INVENTORY)
        if account.sha(input_raw) != account.INPUTS_SHA256 or account.sha(inventory_raw) != account.INVENTORY_SHA256:
            raise ValueError("original controls changed")
        inputs = parse(input_raw)
        inventory = parse(inventory_raw)
        member_rows = inventory["members"]
        ids = [row.get("member_id", row.get("member_ref")) for row in member_rows]
        if (inputs["original_members"] != 363 or inventory["member_count"] != 363
                or len(member_rows) != 363 or len(set(ids)) != 363
                or any(not isinstance(i, str) or not i for i in ids)):
            raise ValueError("original member identity changed")
        manifest = parse(archive.read(CONTROL_MANIFEST))
        if (set(manifest) != {"schema_version", "original_members", "public_files", "inputs_sha256",
                             "inventory_sha256", "new_additions_included", "final_package", "files"}
                or manifest["schema_version"] != "lab-t25-original-input-bundle/v1"
                or manifest["original_members"] != 363 or manifest["public_files"] != 681
                or manifest["inputs_sha256"] != account.INPUTS_SHA256
                or manifest["inventory_sha256"] != account.INVENTORY_SHA256
                or manifest["new_additions_included"] is not False
                or manifest["final_package"] is not False):
            raise ValueError("bundle manifest changed")
        rows = sorted(inputs["files"], key=lambda row: row["path"])
        if len(rows) != 681 or len(manifest["files"]) != 681:
            raise ValueError("original file count changed")
        expected_names = ["files/" + valid_path(row["path"]).as_posix() for row in rows]
        if names[3:] != expected_names:
            raise ValueError("original file paths changed")
        with tempfile.TemporaryDirectory(prefix="cal-t25-replay-") as name:
            root = Path(name)
            for row, manifest_row, member in zip(rows, manifest["files"], expected_names):
                raw = archive.read(member)
                if (manifest_row != {"path": row["path"], "sha256": row["sha256"], "size": len(raw)}
                        or account.sha(raw) != row["sha256"]):
                    raise ValueError("original file bytes changed")
                target = root / valid_path(row["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                if account.sha(target.read_bytes()) != row["sha256"]:
                    raise ValueError("clean replay bytes changed")
        return {"schema_version": "lab-t25-original-input-replay/v1",
                "archive_sha256": hashlib.sha256(blob).hexdigest(),
                "original_members": 363, "replayed_public_files": 681,
                "new_additions_included": False, "final_package": False,
                "authority_effect": "none"}


if __name__ == "__main__":
    print(json.dumps(replay(build()), sort_keys=True, indent=2))
