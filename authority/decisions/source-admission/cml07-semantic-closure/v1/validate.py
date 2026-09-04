#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

from render import render

HERE = Path(__file__).resolve().parent
LAB_ROOT = HERE.parents[4]
CORE_ROOT = LAB_ROOT.parent / "domainspec-core"
RECEIPT = HERE / "receipts" / "validation.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def selected_bytes(path: Path, start: int, end: int) -> bytes:
    lines = path.read_bytes().splitlines(keepends=True)
    return b"".join(lines[start - 1:end])


def main() -> int:
    checks = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "BLOCK", "detail": detail})

    try:
        data = json.loads((HERE / "admissions.json").read_text())
        check("canonical-json-parses", True, "admissions.json parsed")
    except Exception as exc:
        data = {}
        check("canonical-json-parses", False, str(exc))

    admissions = data.get("admissions", [])
    check("candidate-has-no-authority-effect", data.get("status") == "candidate-unadmitted" and data.get("authority_effect") == "none-until-bound-decision", "candidate posture remains non-effectful")
    check("exactly-three-selections", len(admissions) == 3, f"observed {len(admissions)} selections")
    check("selection-ids-unique", len({x.get('admission_id') for x in admissions}) == len(admissions), "admission IDs are unique")

    candidate_path = LAB_ROOT / "authority/definitions/candidates/0007-cml07-semantic-closure/candidate.json"
    candidate = json.loads(candidate_path.read_text())
    candidate_defs = {x["definition_id"] for x in candidate["definitions"]}
    bindings = {x["source_ref"]: x for x in candidate["source_bindings"]}
    expected = {
        "CAL-SOURCE-ADMISSION-CML07-CAV2-D38": "domainspec-core:CAV2-D38",
        "CAL-SOURCE-ADMISSION-CML07-CAV2-D56": "domainspec-core:CAV2-D56",
        "CAL-SOURCE-ADMISSION-CML07-CAV2-D65": "domainspec-core:CAV2-D65",
    }
    check("exact-selection-set", set(expected) == {x.get('admission_id') for x in admissions}, "D38, D56, and D65 are the complete selected set")

    for item in admissions:
        item_id = item.get("admission_id", "unknown")
        source = CORE_ROOT / item.get("source_path", "")
        full = source.read_bytes() if source.is_file() else b""
        check(f"{item_id}:source-exists", source.is_file(), str(source))
        check(f"{item_id}:source-file-current", sha(full) == item.get("source_file_sha256_at_authoring"), f"observed {sha(full)}")
        selected = selected_bytes(source, item["start_line"], item["end_line"]) if source.is_file() else b""
        check(f"{item_id}:selector-current", sha(selected) == item.get("selected_sha256"), f"observed {sha(selected)}")
        target_ids = set(item.get("target_definition_ids", []))
        check(f"{item_id}:targets-exist", bool(target_ids) and target_ids <= candidate_defs, f"targets {sorted(target_ids)}")
        binding = bindings.get(expected.get(item_id, ""), {})
        selector = binding.get("selector", {})
        aligned = (
            binding.get("path") == item.get("source_path")
            and binding.get("sha256") == item.get("selected_sha256")
            and binding.get("admission_posture") == "candidate-unadmitted"
            and selector.get("kind") == "line-range"
            and selector.get("start") == item.get("start_line")
            and selector.get("end") == item.get("end_line")
        )
        check(f"{item_id}:candidate-binding-aligned", aligned, expected.get(item_id, "missing expected binding"))

    projection = HERE / "SOURCE-ADMISSIONS.md"
    expected_projection = render(data)
    check("projection-generated-from-canonical", projection.is_file() and projection.read_text() == expected_projection, "SOURCE-ADMISSIONS.md matches deterministic render")

    status = "PASS" if all(x["result"] == "PASS" for x in checks) else "BLOCK"
    receipt = {
        "schema_version": "cyberalchemy-lab-validation-receipt/v1",
        "subject": data.get("record_id", "unparsed"),
        "status": status,
        "authority_effect": "none",
        "checks": checks,
        "summary": {"pass": sum(x["result"] == "PASS" for x in checks), "block": sum(x["result"] == "BLOCK" for x in checks)},
        "claim_ceiling": "PASS proves only that the exact source-admission candidate is internally coherent, current, and synchronized with candidate 0007. It does not admit any source or authorize S2."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"{status}: {receipt['summary']['pass']} PASS, {receipt['summary']['block']} BLOCK")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
