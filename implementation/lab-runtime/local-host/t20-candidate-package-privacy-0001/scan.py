"""Scan the exact disposable T25 local candidate for public-byte privacy leaks."""

import hashlib
import io
import json
from pathlib import Path
import re
import stat
import types
import zipfile

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "implementation/lab-runtime/local-host/t25-local-candidate-0001/package.py"
PRIVACY = ROOT / "implementation/lab-runtime/local-host/t20-local-privacy-0001/scan.py"
PACKAGE_SHA = "891bc19939b719728039447519f0d127805dbca360df533f2459201b42efb4d7"
PRIVACY_SHA = "8d01bcb71ade520f9fc8a168e4708bf3509a1a4cbdba1424ade2eddd0296e76b"
ARCHIVE_SHA = "020f2755bd2687003f15d93a49a1e3bd6a49d838e3efe1398d6731881edce448"
PUBLIC_POLICY_PATH = "files/implementation/lab-ontology/candidates/v1/review/O06/packages/0001/proposals/private-source-use.json"
PUBLIC_POLICY_SHA = "2e8ad0b5f35d42ad071387a641078f820055bf61573a15c430a8c7568cdff0f6"
TEXT_CREDENTIAL = re.compile(
    rb"\b(?:password|secret|client[_-]?secret|api[_-]?key|access[_-]?token|refresh[_-]?token)"
    rb"[ \t]*(?::=|:|(?:\*\*|//|<<|>>|[+\-*/%&|^@])?=)[ \t]*([^\s,#;]+)", re.I)
TEXT_CREDENTIAL_KEY = re.compile(
    rb"\b(?:password|secret|client[_-]?secret|api[_-]?key|access[_-]?token|refresh[_-]?token)"
    rb"[ \t]*(?::=|:|(?:\*\*|//|<<|>>|[+\-*/%&|^@])?=)", re.I)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_selected(path, expected, name):
    for ancestor in (path, *path.parents):
        if ancestor == ROOT.parent:
            break
        if ancestor.is_symlink():
            raise ValueError("selected code linked")
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("selected code nonregular")
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError("selected code changed")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    if sha(path.read_bytes()) != expected:
        raise ValueError("selected code changed after load")
    return module


def scan_public(name, raw, privacy, *, placeholder=False):
    if placeholder:
        if raw:
            raise ValueError("name-only placeholder populated")
        privacy.scan_member(name, raw)
        return
    if name == PUBLIC_POLICY_PATH:
        # The selected public policy proposal has "private" in its title; its
        # exact reviewed bytes still get the same JSON/body checks.
        if sha(raw) != PUBLIC_POLICY_SHA:
            raise ValueError("public policy exception bytes changed")
        if privacy.PRIVATE_BLOCK.search(raw):
            raise ValueError("private key block in public policy")
        privacy.scan_json(privacy.strict_json(raw))
        return
    privacy.scan_member(name, raw, json_body=name.endswith(".json"))
    if not name.endswith(".json"):
        for line in raw.splitlines():
            for key in TEXT_CREDENTIAL_KEY.finditer(line):
                immediate = line[key.end():].lstrip(b" \t")
                if not immediate or immediate.startswith(b"#"):
                    raise ValueError("empty or multiline text credential assignment")
        for match in TEXT_CREDENTIAL.finditer(raw):
            end = raw.find(b"\n", match.end())
            rest = raw[match.end():end if end >= 0 else len(raw)]
            expression = re.sub(rb"\s+", b"", match.group(0)).lower()
            if expression == b"password=none)" and not rest.strip():
                continue  # The two selected PEM loader calls have no password.
            raise ValueError("populated text credential assignment")


def run():
    package = load_selected(PACKAGE, PACKAGE_SHA, "t20_selected_t25_package")
    privacy = load_selected(PRIVACY, PRIVACY_SHA, "t20_selected_prior_scanner")
    blob = package.build()
    if sha(blob) != ARCHIVE_SHA:
        raise ValueError("selected candidate archive changed")
    package.replay(blob)
    original_count = addition_count = placeholder_count = 0
    with zipfile.ZipFile(io.BytesIO(blob)) as outer:
        with zipfile.ZipFile(io.BytesIO(outer.read(package.ORIGINAL_ENTRY))) as inner:
            for name in inner.namelist():
                if name.startswith("files/"):
                    original_count += 1
                scan_public(name, inner.read(name), privacy)
        additions = package.parse(outer.read(package.CONTROL))["additions"]
        scan_public(package.CONTROL, outer.read(package.CONTROL), privacy)
        for row in additions:
            name = row["path"]
            placeholder = row["kind"] == "name-only-empty-placeholder"
            scan_public(name, outer.read(name), privacy, placeholder=placeholder)
            addition_count += 1
            placeholder_count += int(placeholder)
    if (original_count, addition_count, placeholder_count) != (681, 799, 78):
        raise ValueError("candidate scan membership changed")
    return {"schema_version": "lab-t20-local-candidate-privacy/v1",
            "archive_sha256": ARCHIVE_SHA, "original_public_files_scanned": original_count,
            "additions_scanned": addition_count, "name_only_placeholders": placeholder_count,
            "public_policy_path_exception_sha256": PUBLIC_POLICY_SHA,
            "selected_scanner_sha256": PRIVACY_SHA,
            "sensitive_class_matches": 0, "status": "PASS-LOCAL-SELECTED-CLASSES",
            "protected_source8_scanned": False, "full_privacy_qualified": False}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
