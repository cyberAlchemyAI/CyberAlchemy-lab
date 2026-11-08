"""Exact API40 207-file source-guard subset archive and clean-root replay."""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import secrets
import stat
import tempfile
import types
import zipfile

ROOT = Path(__file__).absolute().parents[4]
HERE = Path(__file__).absolute().parent
SOURCE = "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/source-manifest.json"
SOURCE_SHA = "45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219"
PROFILE = "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/contract-profile.json"
PROFILE_SHA = "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614"
DISPOSITIONS = "implementation/lab-runtime/local-host/t25-api40-disposition-inventory-0002/DISPOSITIONS.json"
DISPOSITIONS_SHA = "fe0db17a3d8485a01dfceb0af45e8499f0a7325f6a165bc93a547cc96dc8cb98"
ARCHIVE = HERE / "SOURCE-GUARD.zip"
GUARD = "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/guard.py"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                       allow_nan=False) + "\n").encode()


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def parent_fd(path):
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("absolute selected path required")
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def read_regular(path):
    path = Path(path)
    parent = parent_fd(path)
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError("nonregular selected file")
            with os.fdopen(os.dup(fd), "rb") as stream:
                return stream.read()
        finally:
            os.close(fd)
    finally:
        os.close(parent)


def selected(name, digest):
    raw = read_regular(ROOT / name)
    if sha(raw) != digest:
        raise ValueError("selected source changed: " + name)
    return raw


def source_rows():
    manifest_raw = selected(SOURCE, SOURCE_SHA)
    manifest = parse(manifest_raw)
    profile = parse(selected(PROFILE, PROFILE_SHA))
    dispositions = parse(selected(DISPOSITIONS, DISPOSITIONS_SHA))
    rows = manifest["files"]
    if len(rows) != 207 or len({row["path"] for row in rows}) != 207:
        raise ValueError("API40 source row inventory differs")
    if rows != sorted(rows, key=lambda row: row["path"]):
        raise ValueError("API40 source row order differs")
    profile_index = {row["path"]: row["sha256"] for row in profile["files"]}
    disposition_index = {row["path"]: row for row in dispositions["rows"]}
    counts = {"archive-byte-selected": 0, "unresolved": 0, "not-in-profile": 0}
    for row in rows:
        name, digest = row["path"], row["sha256"]
        if not name.startswith("product/") or name.startswith("/") or ".." in Path(name).parts:
            raise ValueError("nonpublic source row")
        if name not in profile_index:
            counts["not-in-profile"] += 1
        else:
            if profile_index[name] != digest or disposition_index[name]["sha256"] != digest:
                raise ValueError("source/profile digest conflict")
            counts[disposition_index[name]["disposition"]] += 1
    if counts != {"archive-byte-selected": 1, "unresolved": 147, "not-in-profile": 59}:
        raise ValueError("source/profile archive coverage differs")
    if next(row["sha256"] for row in rows if row["path"] == PROFILE) != PROFILE_SHA:
        raise ValueError("source profile binding differs")
    return manifest_raw, rows, counts


def entry(name, raw):
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info, raw


def build():
    manifest_raw, rows, counts = source_rows()
    control = {"schema_version": "lab-api40-clean-source-guard-subset/v1",
               "source_manifest_binding": {"path": SOURCE, "sha256": SOURCE_SHA},
               "profile_binding": {"path": PROFILE, "sha256": PROFILE_SHA},
               "disposition_binding": {"path": DISPOSITIONS, "sha256": DISPOSITIONS_SHA},
               "source_file_count": 207, "coverage_counts": counts,
               "current_service_operation_executed": False,
               "portable_closure_complete": False, "authority_effect": "none"}
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", allowZip64=True) as archive:
        for name, raw in [("META/selection.json", canonical(control)),
                          ("META/source-manifest.json", manifest_raw)]:
            archive.writestr(*entry(name, raw))
        for row in rows:
            archive.writestr(*entry("files/" + row["path"],
                                   selected(row["path"], row["sha256"])))
    return output.getvalue()


def guard_module(raw, path):
    module = types.ModuleType("t25_selected_api40_source_guard")
    module.__file__ = str(path)
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


def extract_and_check(blob, *, mutation=None):
    if mutation not in (None, "missing", "changed"):
        raise ValueError("unknown clean-root mutation")
    manifest_raw, rows, counts = source_rows()
    expected_control = {"schema_version": "lab-api40-clean-source-guard-subset/v1",
                        "source_manifest_binding": {"path": SOURCE, "sha256": SOURCE_SHA},
                        "profile_binding": {"path": PROFILE, "sha256": PROFILE_SHA},
                        "disposition_binding": {"path": DISPOSITIONS, "sha256": DISPOSITIONS_SHA},
                        "source_file_count": 207, "coverage_counts": counts,
                        "current_service_operation_executed": False,
                        "portable_closure_complete": False, "authority_effect": "none"}
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        expected_names = ["META/selection.json", "META/source-manifest.json"] + [
            "files/" + row["path"] for row in rows]
        if names != expected_names or len(names) != len(set(names)):
            raise ValueError("source-guard archive members differ")
        for info in infos:
            if (info.is_dir() or info.compress_type != zipfile.ZIP_STORED or
                    info.create_system != 3 or info.external_attr >> 16 != 0o100644):
                raise ValueError("unsafe source-guard archive member")
        if (archive.read(names[0]) != canonical(expected_control) or
                archive.read(names[1]) != manifest_raw):
            raise ValueError("source-guard archive control differs")
        with tempfile.TemporaryDirectory(prefix="cal-api40-source-guard-") as directory:
            clean = Path(directory)
            for row in rows:
                name = "files/" + row["path"]
                raw = archive.read(name)
                if sha(raw) != row["sha256"]:
                    raise ValueError("source-guard archive byte differs")
                target = clean / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            guard = guard_module(read_regular(clean / GUARD), clean / GUARD)
            target = clean / PROFILE
            if mutation == "missing":
                target.unlink()
            elif mutation == "changed":
                target.write_bytes(b"changed\n")
            try:
                result = guard._verify_files(clean, rows)
            except FileNotFoundError:
                if mutation == "missing":
                    return {"status": "REFUSED", "reason": "missing selected profile"}
                raise
            except ValueError as error:
                if mutation == "changed" and str(error) == "source changed " + PROFILE:
                    return {"status": "REFUSED", "reason": "changed selected profile"}
                raise
            if mutation is not None:
                raise ValueError("missing/changed source accepted")
            if result["verified_files"] != 207:
                raise ValueError("clean-root full source subset incomplete")
            return {"status": "PASS", "verified_files": 207,
                    "anchored_directories": result["anchored_directories"]}


def verify(blob):
    if blob != build():
        raise ValueError("noncanonical or changed source-guard archive")
    positive = extract_and_check(blob)
    missing = extract_and_check(blob, mutation="missing")
    changed = extract_and_check(blob, mutation="changed")
    return {"schema_version": "lab-api40-clean-source-guard-replay/v1",
            "archive_sha256": sha(blob), "source_manifest_sha256": SOURCE_SHA,
            "source_file_count": 207, "positive": positive,
            "missing": missing, "changed": changed,
            "current_service_operation_executed": False,
            "portable_closure_complete": False,
            "authority_effect": "none", "task_complete": False}


def write_new(path, raw):
    path = Path(path)
    parent = parent_fd(path)
    temporary = "." + path.name + ".staging-" + secrets.token_hex(12)
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=parent)
        try:
            with os.fdopen(fd, "wb") as output:
                output.write(raw)
                output.flush()
                os.fsync(output.fileno())
        except BaseException:
            os.unlink(temporary, dir_fd=parent)
            raise
        try:
            os.link(temporary, path.name, src_dir_fd=parent, dst_dir_fd=parent,
                    follow_symlinks=False)
            os.fsync(parent)
        finally:
            os.unlink(temporary, dir_fd=parent)
    finally:
        os.close(parent)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.create == args.verify:
        parser.error("select exactly one mode")
    if args.create:
        raise ValueError("privacy HOLD: selected full source set must not be retained as a public archive")
    # The 207-file source guard is an in-memory diagnostic. The public-byte
    # privacy scan found selected classes in three original source files.
    blob = build()
    print(json.dumps(verify(blob), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
