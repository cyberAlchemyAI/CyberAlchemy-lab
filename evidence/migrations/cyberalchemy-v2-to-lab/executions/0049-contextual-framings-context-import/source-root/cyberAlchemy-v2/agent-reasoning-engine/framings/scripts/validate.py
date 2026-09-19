#!/usr/bin/env python3
"""Validate the contextual framings candidate ontology without writing by default."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
MATERIAL_FILES = (
    "README.md", "OWNER-INTENT.md", "profile.json", "product-capability.json",
    "sources.json", "nodes.json", "relations.json", "residue.jsonl",
    "schemas/framings.schema.json", "scripts/validate.py",
)
CLAIM_CEILING = (
    "Candidate contextual-framings Product Capability and business-domain ontology only; "
    "no model-weight modification, runtime implementation, DomainSpec admission, exact "
    "implementation binding, conformance, measured cognitive outcome, or effect authority."
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load(relative: str, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads((PACKAGE_ROOT / relative).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load {relative}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{relative} must contain one JSON object")
        return {}
    return value


def validate_instance(schema: dict[str, Any], name: str, value: dict[str, Any], errors: list[str]) -> None:
    validator = Draft202012Validator({"$defs": schema.get("$defs", {}), "$ref": f"#/$defs/{name}"})
    for failure in sorted(validator.iter_errors(value), key=lambda item: list(item.path)):
        locator = ".".join(str(part) for part in failure.path)
        errors.append(f"{name}{'.' + locator if locator else ''}: {failure.message}")


def selected_bytes(source: dict[str, Any], raw: bytes) -> bytes:
    if source["scope_kind"] == "whole-file":
        return raw
    heading = source["selector"]
    lines = raw.decode("utf-8").splitlines(keepends=True)
    starts = [index for index, line in enumerate(lines) if line.rstrip("\r\n") == heading]
    if len(starts) != 1:
        raise ValueError(f"heading must resolve exactly once; got {len(starts)}")
    start = starts[0]
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")), len(lines))
    return "".join(lines[start:end]).encode("utf-8")


def material_digest(errors: list[str]) -> str:
    state = hashlib.sha256()
    for relative in sorted(MATERIAL_FILES):
        path = PACKAGE_ROOT / relative
        if not path.is_file():
            errors.append(f"missing material file: {relative}")
            continue
        state.update(relative.encode() + b"\0" + path.read_bytes() + b"\0")
    return state.hexdigest()


def validate() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    profile = load("profile.json", errors)
    capability = load("product-capability.json", errors)
    sources_doc = load("sources.json", errors)
    nodes_doc = load("nodes.json", errors)
    relations_doc = load("relations.json", errors)
    schema = load("schemas/framings.schema.json", errors)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        errors.append(f"schema is invalid: {exc}")
    if schema:
        for definition, instance in (("profile", profile), ("productCapability", capability), ("sourceRegistry", sources_doc), ("nodeRegistry", nodes_doc), ("relationRegistry", relations_doc)):
            validate_instance(schema, definition, instance, errors)

    source_ids: set[str] = set()
    for index, source in enumerate(sources_doc.get("sources", [])):
        source_id = source.get("source_id")
        if source_id in source_ids:
            errors.append(f"duplicate source id: {source_id}")
        source_ids.add(source_id)
        relative = Path(str(source.get("path", "")))
        if relative.is_absolute() or ".." in relative.parts or not str(relative).startswith("cyberAlchemy-v2/"):
            errors.append(f"sources[{index}] path is unbounded")
            continue
        path = REPOSITORY_ROOT / relative
        if not path.is_file():
            errors.append(f"sources[{index}] is missing: {relative}")
            continue
        try:
            observed = digest(selected_bytes(source, path.read_bytes()))
        except (KeyError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"sources[{index}] selector failed: {exc}")
            continue
        if observed != source.get("sha256"):
            errors.append(f"sources[{index}] digest drift: {source_id}")

    node_by_id: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(nodes_doc.get("nodes", [])):
        node_id = node.get("id")
        if node_id in node_by_id:
            errors.append(f"duplicate node id: {node_id}")
        node_by_id[node_id] = node
        for ref in node.get("source_refs", []):
            if ref not in source_ids:
                errors.append(f"nodes[{index}] unknown source ref: {ref}")
    required_ids = {
        capability.get("capability_id"), capability.get("product_ref"),
        capability.get("parent_capability_ref"), capability.get("business_ontology_ref"),
        *capability.get("inputs", []), *capability.get("outputs", []),
    }
    missing = sorted(item for item in required_ids if item and item not in node_by_id)
    if missing:
        errors.append(f"capability references unknown ontology nodes: {', '.join(missing)}")

    relation_types = {item.get("type"): item for item in relations_doc.get("relation_types", [])}
    relation_ids: set[str] = set()
    for index, relation in enumerate(relations_doc.get("relations", [])):
        relation_id = relation.get("id")
        if relation_id in relation_ids:
            errors.append(f"duplicate relation id: {relation_id}")
        relation_ids.add(relation_id)
        source = node_by_id.get(relation.get("source"))
        target = node_by_id.get(relation.get("target"))
        if not source or not target:
            errors.append(f"relations[{index}] has a dangling endpoint")
            continue
        rule = relation_types.get(relation.get("type"))
        if not rule:
            errors.append(f"relations[{index}] has an unknown type")
        elif source.get("kind") not in rule.get("source_kinds", []) or target.get("kind") not in rule.get("target_kinds", []):
            errors.append(f"relations[{index}] violates its typed endpoint signature")
        for ref in relation.get("source_refs", []):
            if ref not in source_ids:
                errors.append(f"relations[{index}] unknown source ref: {ref}")

    residue_count = 0
    try:
        for line_number, line in enumerate((PACKAGE_ROOT / "residue.jsonl").read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            item = json.loads(line)
            residue_count += 1
            if item.get("authority_effect") != "none":
                errors.append(f"residue line {line_number} exceeds authority ceiling")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot validate residue.jsonl: {exc}")

    current_digest = material_digest(errors)
    current_receipt = False
    for path in sorted((PACKAGE_ROOT / "receipts").glob("validation-*.json")) if (PACKAGE_ROOT / "receipts").is_dir() else []:
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if receipt.get("status") == "PASS" and receipt.get("material_digest") == current_digest:
            current_receipt = True
    if not current_receipt:
        warnings.append("no current PASS receipt matches the live material digest")

    checks = [
        "closed Draft 2020-12 artifact shapes",
        "selector-level source currency",
        "stable node and relation identity",
        "typed relation endpoint closure",
        "Product Capability reference closure",
        "candidate and non-authorizing claim ceiling",
        "visible D65 successor-stage residue",
        "append-only receipt currency",
    ]
    return {
        "schema_ref": "schemas/framings.schema.json#/$defs/validationReceipt",
        "schema_version": "cav2-framings-validation/v1",
        "validated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "PASS" if not errors else "BLOCK",
        "package_root": "cyberAlchemy-v2/agent-reasoning-engine/framings",
        "ontology_type": "business-domain",
        "branch": "business",
        "authority_effect": "none",
        "counts": {"sources": len(source_ids), "nodes": len(node_by_id), "relation_types": len(relation_types), "relations": len(relation_ids), "residue": residue_count},
        "material_digest": current_digest,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "claim_ceiling": CLAIM_CEILING,
    }


def write_receipt(result: dict[str, Any]) -> Path:
    if result.get("status") != "PASS":
        raise ValueError("cannot write a receipt for a blocked package")
    path = PACKAGE_ROOT / "receipts" / f"validation-{result['material_digest'][:16]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return path
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.write_receipt and result["status"] == "PASS":
        result["receipt_path"] = str(write_receipt(result).relative_to(REPOSITORY_ROOT))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
