#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
CORE = Path("/home/vrondelli/projects/domainspec-core")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    data = json.loads((ROOT / "admissions.json").read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location("source_render", ROOT / "render.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    checks = []
    def check(check_id, ok, detail):
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})
    check("candidate-non-effectful", data["status"] == "candidate-unadmitted" and data["authority_effect"] == "none-until-bound-decision", data["status"])
    check("five-distinct-selections", len(data["admissions"]) == 5 and len({x["admission_id"] for x in data["admissions"]}) == 5, len(data["admissions"]))
    source_results = []
    for item in data["admissions"]:
        path = CORE / item["source_path"]
        content = path.read_bytes()
        selected = b"".join(content.splitlines(keepends=True)[item["start_line"] - 1:item["end_line"]])
        source_results.append({
            "id": item["admission_id"],
            "file_current": sha(content) == item["source_file_sha256_at_authoring"],
            "selection_current": sha(selected) == item["selected_sha256"],
            "actual_selected_sha256": sha(selected)
        })
    check("selected-source-bytes-current", all(x["file_current"] and x["selection_current"] for x in source_results), source_results)
    expected_projection = module.render(data)
    projection = ROOT / "SOURCE-ADMISSIONS.md"
    check("generated-projection-current", projection.is_file() and projection.read_text(encoding="utf-8") == expected_projection, str(projection))
    blocked = [x for x in checks if x["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-source-admission-validation/v1",
        "subject": data["record_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks)-len(blocked), "blocked": len(blocked), "total": len(checks)},
        "claim_ceiling": "PASS proves only exact current source bytes, closed selection count, and generated projection parity. It does not admit the selections or the derived Definition."
    }
    out = ROOT / "receipts/validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CANONICAL_PACKAGE_HOME_SOURCE_SELECTIONS={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
