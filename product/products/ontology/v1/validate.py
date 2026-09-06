#!/usr/bin/env python3
"""Run the complete thin Ontology-as-a-Product product test."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SOURCE_REPO = Path("/home/vrondelli/projects/domainspec-core")
RUNTIME = ROOT / "runtime/Cargo.toml"
CANDIDATE = ROOT / "candidates/0001-thin-end-to-end/candidate.json"
RECEIPT = ROOT / "candidates/0001-thin-end-to-end/receipts/product-test.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=LAB, text=True, capture_output=True, check=False, env=env)


def render_receipt(receipt: dict[str, Any]) -> str:
    lines = ["<!-- Generated from product-test.json. Do not edit. -->", "", "# Ontology-as-a-Product product test", "", f"- Result: `{receipt['result']}`", f"- Candidate: `{receipt['candidate_id']}`", f"- Checks: `{receipt['summary']['checks_passed']}/{receipt['summary']['checks_total']}`", f"- Candidate digest: `{receipt['candidate_sha256']}`", f"- Material digest: `{receipt['material_digest']}`", "", "## Checks", ""]
    lines.extend(f"- `{row['result']}` — `{row['check_id']}`: {row['detail']}" for row in receipt["checks"])
    lines += ["", "## Try it", "", "```bash", "cargo run --manifest-path product/products/ontology/v1/runtime/Cargo.toml --quiet -- validate product/products/ontology/v1/fixtures/valid/ontology-package.json", "cargo run --manifest-path product/products/ontology/v1/runtime/Cargo.toml --quiet -- list product/products/ontology/v1/fixtures/valid/ontology-package.json", "cargo run --manifest-path product/products/ontology/v1/runtime/Cargo.toml --quiet -- get product/products/ontology/v1/fixtures/valid/ontology-package.json demo.output", "```", "", "## Residue", ""]
    lines.extend(f"- {item}" for item in receipt["residue"])
    lines += ["", "## Claim ceiling", "", receipt["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> int:
    checks: list[dict[str, str]] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    product = json.loads((ROOT / "product.json").read_text())
    product_ontology = json.loads((ROOT / "product-ontology/ontology.json").read_text())
    closure = json.loads((ROOT / "source-closure.json").read_text())
    source = json.loads((ROOT / "fixtures/valid/source.json").read_text())
    package = json.loads((ROOT / "fixtures/valid/ontology-package.json").read_text())
    candidate = json.loads(CANDIDATE.read_text())

    roots = {"lab": LAB, "domainspec-core": SOURCE_REPO}
    closure_current = all((roots[row["root"]] / row["path"]).is_file() and sha256(roots[row["root"]] / row["path"]) == row["sha256"] for row in closure["sources"])
    check("OAP-01-SOURCE-CLOSURE", closure_current and len(closure["sources"]) == 7, "all seven exact prototype dependencies match their bound digests")
    check("OAP-02-PRODUCT-IDENTITY", product["product_id"] == "CA2-PRODUCT-ONTOLOGY" and product["core_output_ref"] == "CA2-OUTPUT-ONTOLOGY-PACKAGE" and product["authority_effect"] == "none", "Product identity, core output, and no-authority posture are explicit")
    roles = {row["role"] for row in product_ontology["nodes"]}
    check("OAP-03-PRODUCT-ONTOLOGY-SEPARATION", product_ontology["represented_product_ref"] == product["product_id"] and roles == {"product-identity", "product-capability", "core-value-bearing-output"} and len(product_ontology["non_collapse_invariants"]) == 3, "Product Ontology represents three distinct Product graph roles")
    check("OAP-04-GENERATED-LABELS", all(not row["canonical_axis"] and row["projection_policy"] == "generated-only" for row in product_ontology["derived_labels"]), "Ontology-as-a-Product and Product Ontology remain generated labels")

    source_schema = json.loads((ROOT / "contracts/source.schema.json").read_text())
    package_schema = json.loads((ROOT / "contracts/ontology-package.schema.json").read_text())
    try:
        jsonschema.Draft202012Validator.check_schema(source_schema)
        jsonschema.Draft202012Validator.check_schema(package_schema)
        jsonschema.validate(source, source_schema)
        resolver = jsonschema.RefResolver.from_schema(package_schema, store={source_schema["$id"]: source_schema})
        jsonschema.validate(package, package_schema, resolver=resolver)
        schema_ok = True
    except Exception:
        schema_ok = False
    check("OAP-05-CLOSED-SCHEMAS", schema_ok, "source and package instances validate against closed Draft 2020-12 schemas")

    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="cal-ontology-product-target-") as target, tempfile.TemporaryDirectory(prefix="cal-ontology-product-test-") as temporary:
        environment["CARGO_TARGET_DIR"] = target
        cargo_test = run(["cargo", "test", "--manifest-path", str(RUNTIME), "--locked", "--quiet"], env=environment)
        check("OAP-06-RUST-TESTS", cargo_test.returncode == 0, "all Rust library and CLI tests pass" if cargo_test.returncode == 0 else cargo_test.stderr[-500:])

        first = Path(temporary) / "first.json"
        second = Path(temporary) / "second.json"
        source_path = ROOT / "fixtures/valid/source.json"
        build_one = run(["cargo", "run", "--manifest-path", str(RUNTIME), "--locked", "--quiet", "--", "build", str(source_path), str(first)], env=environment)
        build_two = run(["cargo", "run", "--manifest-path", str(RUNTIME), "--locked", "--quiet", "--", "build", str(source_path), str(second)], env=environment)
        deterministic = build_one.returncode == 0 and build_two.returncode == 0 and first.read_bytes() == second.read_bytes() == (ROOT / "fixtures/valid/ontology-package.json").read_bytes()
        check("OAP-07-DETERMINISTIC-BUILD", deterministic, "two independent builds equal the committed package byte-for-byte")

        validate_run = run(["cargo", "run", "--manifest-path", str(RUNTIME), "--locked", "--quiet", "--", "validate", str(first)], env=environment)
        validate_payload = json.loads(validate_run.stdout) if validate_run.returncode == 0 else {}
        check("OAP-08-PACKAGE-VALIDATE", validate_payload.get("status") == "PASS" and validate_payload.get("nodes") == 3 and validate_payload.get("relations") == 2 and validate_payload.get("authority_effect") == "none", "the built package validates with three nodes, two relations, and no authority effect")

        list_run = run(["cargo", "run", "--manifest-path", str(RUNTIME), "--locked", "--quiet", "--", "list", str(first)], env=environment)
        get_run = run(["cargo", "run", "--manifest-path", str(RUNTIME), "--locked", "--quiet", "--", "get", str(first), "demo.output"], env=environment)
        missing_run = run(["cargo", "run", "--manifest-path", str(RUNTIME), "--locked", "--quiet", "--", "get", str(first), "missing"], env=environment)
        list_payload = json.loads(list_run.stdout) if list_run.returncode == 0 else []
        get_payload = json.loads(get_run.stdout) if get_run.returncode == 0 else {}
        check("OAP-09-BOUNDED-RETRIEVAL", len(list_payload) == 3 and get_payload.get("node_id") == "demo.output" and missing_run.returncode != 0 and "NODE_NOT_FOUND" in missing_run.stderr, "list/get retrieve declared nodes and unknown identities fail closed")

        project_run = run(["cargo", "run", "--manifest-path", str(RUNTIME), "--locked", "--quiet", "--", "project", str(first)], env=environment)
        check("OAP-10-RUST-PROJECTION", project_run.returncode == 0 and project_run.stdout == (ROOT / "fixtures/valid/ONTOLOGY-PACKAGE.md").read_text(), "Rust projection equals the committed generated human view")

        expected_hostile = {"duplicate-node.json": "NODE_ID_DUPLICATE", "dangling-relation.json": "RELATION_TARGET_MISSING", "authority-effect.json": "AUTHORITY_EFFECT_FORBIDDEN"}
        hostile_ok = True
        for filename, code in expected_hostile.items():
            output = Path(temporary) / f"{filename}.out"
            result = run(["cargo", "run", "--manifest-path", str(RUNTIME), "--locked", "--quiet", "--", "build", str(ROOT / "fixtures/invalid" / filename), str(output)], env=environment)
            hostile_ok = hostile_ok and result.returncode != 0 and code in result.stderr and not output.exists()
        check("OAP-11-HOSTILE-FIXTURES", hostile_ok, "duplicate identity, dangling endpoint, and authority inflation fixtures all fail closed without output")

    generator_check = run(["python3", str(ROOT / "generate.py"), "--check"], env=environment)
    check("OAP-12-GENERATED-HUMAN-VIEWS", generator_check.returncode == 0, "all seven human projections equal their canonical machine records")
    material_paths = candidate["material_paths"]
    material_unique = len(material_paths) == len(set(material_paths)) and all((ROOT / path).is_file() for path in material_paths)
    check("OAP-13-MATERIAL-CLOSURE", material_unique and len(material_paths) == 17, "candidate declares exactly 17 existing unique material files")
    check("OAP-14-CANDIDATE-BOUNDARY", candidate["status"] == "ready-for-product-testing" and candidate["authority_effect"] == "none" and "Product testing precedes" in candidate["approval_boundary"], "candidate is ready for testing but not approved or authoritative")

    material_rows = [{"path": path, "sha256": sha256(ROOT / path), "size": (ROOT / path).stat().st_size} for path in material_paths]
    material_digest = hashlib.sha256(json.dumps(material_rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result = "PASS" if all(row["result"] == "PASS" for row in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-product-test/v1",
        "candidate_id": candidate["candidate_id"],
        "result": result,
        "authority_effect": "none",
        "candidate_ref": CANDIDATE.relative_to(ROOT).as_posix(),
        "candidate_sha256": sha256(CANDIDATE),
        "material_digest": material_digest,
        "material": material_rows,
        "summary": {"checks_passed": sum(row["result"] == "PASS" for row in checks), "checks_total": len(checks), "nodes": len(package["nodes"]), "relations": len(package["relations"]), "hostile_fixtures": 3},
        "checks": checks,
        "residue": ["Legacy cav2.ontology-product source-registry drift remains open for source-preserving migration.", "Governance v3, Ontology Lifecycle v3, and their Context Map remain candidate-unadmitted.", "No human Product approval decision is recorded."],
        "claim_ceiling": "PASS proves this exact private thin candidate deterministically builds, validates, retrieves, and projects one governed ontology package while rejecting the exercised identity, endpoint, and authority failures. It does not prove general user value, production durability, context admission, runtime adoption, Product approval, publication, release, deployment, or migration completion."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    (RECEIPT.parent / "PRODUCT-TEST.md").write_text(render_receipt(receipt))
    print(json.dumps(receipt, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
