"""Generate the declared 34-operation reference from one exact public catalog."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile


ROOT = Path(__file__).resolve().parents[4]
CATALOG = "docs/proposals/0008-lab-api-contracts/api-contracts.json"
CATALOG_SHA256 = "4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1"
DESTINATION = "docs/lab/runtime/reference/api"
OPERATION = re.compile(r"[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)+")
SCHEMA_KEYS = ("request_schema", "result_schema", "error_schema")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def safe_path(name: str) -> Path:
    value = PurePosixPath(name)
    if not isinstance(name, str) or not name or value.is_absolute() or value.as_posix() != name or any(
        part in ("", ".", "..") for part in value.parts
    ):
        raise ValueError("unsafe reference path")
    return Path(*value.parts)


def verified_file(root: Path, name: str, expected: str) -> bytes:
    relative = safe_path(name)
    parent = root
    for part in relative.parts[:-1]:
        parent = parent / part
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError("missing or unsafe reference parent: " + name)
    path = root / relative
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("missing or unsafe reference file: " + name)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError("missing or unsafe reference file: " + name)
        with os.fdopen(fd, "rb", closefd=False) as source:
            raw = source.read()
    finally:
        os.close(fd)
    if sha(raw) != expected:
        raise ValueError("changed reference file: " + name)
    return raw


def bullets(values: list[str]) -> str:
    return "\n".join("- " + value for value in values) if values else "- None declared."


def schema_line(root: Path, destination: Path, title: str, item: dict) -> str:
    if not isinstance(item, dict) or set(item) != {"ref", "resource_uri", "sha256"}:
        raise ValueError("invalid schema binding")
    schema = json.loads(verified_file(root, item["ref"], item["sha256"]))
    if not isinstance(schema, dict) or schema.get("$id") != item["resource_uri"]:
        raise ValueError("schema resource URI differs: " + item["ref"])
    target = os.path.relpath(root / safe_path(item["ref"]), root / destination)
    return f"- {title}: [{item['ref']}]({target}) (`{item['sha256']}`); resource `{item['resource_uri']}`."


def branch(operation: str) -> str:
    if operation.startswith("action."):
        return "Action"
    if operation in ("checkpoint.resolve", "admission.apply", "capability.adoption.prepare"):
        return "Governance"
    return "Base"


def page(root: Path, operation: dict) -> str:
    name = operation["operation"]
    folder = Path(DESTINATION)
    authority = operation["authority"]
    if not isinstance(authority, dict) or not isinstance(authority.get("required_obligation_refs"), list):
        raise ValueError("invalid authority contract")
    schemas = [schema_line(root, folder, title, operation[key]) for title, key in (
        ("Request", "request_schema"), ("Result", "result_schema"), ("Error", "error_schema")
    )]
    catalog_link = os.path.relpath(root / CATALOG, root / folder)
    lines = [
        f"# `{name}`", "", operation["description"], "",
        f"Declared contract: [API catalog]({catalog_link}), SHA-256 `{CATALOG_SHA256}`.",
        "Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.",
        "", "## Contract", "",
        f"- Branch: {branch(name)}.",
        f"- Declared effect: `{operation['effect_kind']}`.",
        f"- Catalog implementation label: `{operation['implementation_status']}`.",
        f"- Trusted channel required: `{str(authority['trusted_channel_required']).lower()}`; caller requirement: `{authority['caller_requirement']}`.",
        f"- Message claims grant authority: `{str(authority['message_claims_grant_authority']).lower()}`.",
        f"- Required obligation references: {', '.join('`' + x + '`' for x in authority['required_obligation_refs'])}.",
        f"- Repository admission possible: `{str(operation['repository_admission_possible']).lower()}`.",
        f"- Runtime activations recorded in catalog: `{operation['runtime_activations']}`.",
        "", "## Schemas", "", *schemas, "", "## Preconditions", "",
        bullets(operation["preconditions"]), "", "## Postconditions", "",
        bullets(operation["postconditions"]), "", "## Currentness, deadlines and retry", "",
        f"- Source-cut selectors: {', '.join('`' + x + '`' for x in operation['source_cut_selectors']) or 'none declared'}.",
        f"- Deadline: {operation['deadline_rule']}",
        f"- Idempotency required: `{str(operation['idempotency_required']).lower()}`; namespace: {', '.join('`' + x + '`' for x in operation['idempotency_namespace']) or 'none declared'}.",
        f"- Inner idempotency selector: `{operation['inner_idempotency_selector']}`.",
        f"- Retry: {operation['idempotency_rule']}",
        f"- Completion: {operation['completion_rule']}",
        "", "## Errors and external effects", "",
        f"- Allowed error codes: {', '.join('`' + x + '`' for x in operation['allowed_error_codes'])}.",
        f"- External effect references: {', '.join('`' + x + '`' for x in operation['external_effect_refs']) or 'none declared'}.",
        "", "[All operations](README.md).", "",
    ]
    return "\n".join(lines)


def build(root: Path = ROOT) -> dict[str, bytes]:
    raw = verified_file(root, CATALOG, CATALOG_SHA256)
    catalog = json.loads(raw)
    operations = catalog["operations"]
    if len(operations) != 34 or not isinstance(operations, list):
        raise ValueError("operation inventory changed")
    names = [item["operation"] for item in operations]
    if len(set(names)) != 34 or any(not OPERATION.fullmatch(name) for name in names):
        raise ValueError("invalid operation identities")
    if len([n for n in names if branch(n) == "Action"]) != 3 or len([n for n in names if branch(n) == "Governance"]) != 3:
        raise ValueError("branch inventory changed")
    files = {}
    rows = ["# Lab API operation contracts", "", "Exact public catalog SHA-256: `" + CATALOG_SHA256 + "`.", "",
            "These 34 pages document declared contracts. Current 34-operation runtime qualification is pending; catalog presence does not prove an operation succeeds.", "",
            "| Operation | Branch | Declared effect | Qualification |", "| --- | --- | --- | --- |"]
    for item in operations:
        name = item["operation"]
        filename = name.replace(".", "-") + ".md"
        files[filename] = page(root, item).encode("utf-8")
        rows.append(f"| [`{name}`]({filename}) | {branch(name)} | `{item['effect_kind']}` | Pending |")
    files["README.md"] = ("\n".join(rows) + "\n").encode("utf-8")
    return files


def output_directory(root: Path, *, create: bool) -> Path:
    current = root
    for part in safe_path(DESTINATION).parts:
        current = current / part
        if not current.exists() and create:
            current.mkdir()
        if not stat.S_ISDIR(current.lstat().st_mode):
            raise ValueError("unsafe generated reference directory")
    return current


def verify(root: Path = ROOT) -> None:
    expected = build(root)
    destination = output_directory(root, create=False)
    found = {p.name for p in destination.iterdir()}
    if found != set(expected):
        raise ValueError("generated operation file set changed")
    for name, raw in expected.items():
        path = destination / name
        if not stat.S_ISREG(path.lstat().st_mode):
            raise ValueError("unsafe generated operation page: " + name)
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            with os.fdopen(fd, "rb", closefd=False) as source:
                actual = source.read()
        finally:
            os.close(fd)
        if actual != raw:
            raise ValueError("generated operation page changed: " + name)


def write(root: Path = ROOT) -> None:
    expected = build(root)
    destination = output_directory(root, create=True)
    existing = {path.name for path in destination.iterdir()}
    if not existing.issubset(expected):
        raise ValueError("unexpected generated reference entry")
    for name in existing:
        if not stat.S_ISREG((destination / name).lstat().st_mode):
            raise ValueError("unsafe generated operation page: " + name)
    for name, raw in expected.items():
        target = destination / name
        fd, temporary = tempfile.mkstemp(prefix=".operation-", dir=destination)
        try:
            with os.fdopen(fd, "wb") as out:
                out.write(raw)
                out.flush()
                os.fsync(out.fileno())
            os.chmod(temporary, 0o644)
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    verify(root)


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--write"]:
        write()
        print("PASS: generated 34 operation pages and index")
    elif sys.argv[1:] == ["--verify"]:
        verify()
        print("PASS: 34 operation pages match exact catalog and schemas")
    else:
        raise SystemExit("usage: generate.py --write|--verify")
