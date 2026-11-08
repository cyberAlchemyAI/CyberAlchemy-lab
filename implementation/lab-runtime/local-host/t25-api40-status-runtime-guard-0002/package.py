"""Portable technical seven-file API40 status guard, excluding unsafe source rows."""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import secrets
import stat
import subprocess
import sys
import tempfile
import types
import zipfile

ROOT = Path(__file__).absolute().parents[4]
HERE = Path(__file__).absolute().parent
ARCHIVE = HERE / "STATUS-RUNTIME-GUARD.zip"
GUARD_SHA = "6912b0928e41b694a3deffa1e8816db84a95b0646f69efe7412d96f3a18422dc"
SOURCE_SHA = "45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219"
PROFILE_SHA = "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614"
SCANNER = "implementation/lab-runtime/local-host/t20-candidate-package-privacy-0001/scan.py"
SCANNER_SHA = "ee08aa3ae06938202281fbdcaeea06208349ea88caa79322f6756c1ac506333f"
PRIOR_SCANNER = "implementation/lab-runtime/local-host/t20-local-privacy-0001/scan.py"
PRIOR_SCANNER_SHA = "8d01bcb71ade520f9fc8a168e4708bf3509a1a4cbdba1424ade2eddd0296e76b"
SOURCE = "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/source-manifest.json"
PROFILE = "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/contract-profile.json"
UNSAFE_OMITTED = (
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/private-plan-v2.schema.json",
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/test_installation_release.py",
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/test_preparation.py",
)
BOOT = (
    "import hashlib,sys\n"
    "expected,filename,root,profile=sys.argv[1:]\n"
    "raw=sys.stdin.buffer.read()\n"
    "if hashlib.sha256(raw).hexdigest()!=expected: raise SystemExit('selected guard bytes differ')\n"
    "sys.argv=[filename,root,profile]\n"
    "scope={'__name__':'__main__','__file__':filename}\n"
    "exec(compile(raw,filename,'exec'),scope)\n"
)


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
        raise ValueError("selected bytes changed: " + name)
    return raw


def selected_guard():
    raw = read_regular(HERE / "status_guard.py")
    if sha(raw) != GUARD_SHA:
        raise ValueError("selected technical guard changed")
    module = types.ModuleType("t25_selected_status_guard")
    module.__file__ = str(HERE / "status_guard.py")
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return raw, module


def privacy_scanner():
    raw = selected(SCANNER, SCANNER_SHA)
    module = types.ModuleType("t25_selected_public_privacy_scanner")
    module.__file__ = str(ROOT / SCANNER)
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    prior = module.load_selected(ROOT / PRIOR_SCANNER, PRIOR_SCANNER_SHA,
                                 "t25_selected_prior_privacy_scanner")
    return module, prior


def technical_profile(guard):
    source = parse(selected(SOURCE, SOURCE_SHA))
    profile = parse(selected(PROFILE, PROFILE_SHA))
    source_rows = {row["path"]: row["sha256"] for row in source["files"]}
    profile_rows = {row["path"]: row["sha256"] for row in profile["files"]}
    rows = [{"path": name, "sha256": digest} for name, digest in guard.ROWS]
    if len(source_rows) != 207 or len(profile_rows) != 33424 or len(rows) != 7:
        raise ValueError("original profile/source selection changed")
    for row in rows:
        name, digest = row["path"], row["sha256"]
        if profile_rows[name] != digest or (name in source_rows and source_rows[name] != digest):
            raise ValueError("status prerequisite source/profile mismatch")
    if sum(row["path"] in source_rows for row in rows) != 6 or len(source_rows) - 6 != 201:
        raise ValueError("original source-guard omission count differs")
    if any(name in {row["path"] for row in rows} for name in UNSAFE_OMITTED):
        raise ValueError("unsafe full-source row entered status recut")
    return {"schema_version": "lab-api40-status-runtime-guard-profile/v2",
            "original_source_manifest_sha256": SOURCE_SHA,
            "original_contract_profile_sha256": PROFILE_SHA,
            "operation": "lab.status", "rows": rows,
            "full_source_guard_rows_omitted": 201,
            "original_service_executed": False, "authority_effect": "none"}


def entry(name, raw):
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info, raw


def build():
    guard_raw, guard = selected_guard()
    profile_raw = canonical(technical_profile(guard))
    scanner, prior = privacy_scanner()
    materials = []
    for name, digest in guard.ROWS:
        raw = selected(name, digest)
        scanner.scan_public("files/" + name, raw, prior)
        materials.append(("files/" + name, raw))
    scanner.scan_public("runtime/status_guard.py", guard_raw, prior)
    scanner.scan_public("META/technical-profile.json", profile_raw, prior)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", allowZip64=True) as archive:
        for name, raw in [("META/technical-profile.json", profile_raw),
                          ("runtime/status_guard.py", guard_raw), *materials]:
            archive.writestr(*entry(name, raw))
    return output.getvalue()


def extracted_run(blob, mutation=None):
    if mutation not in (None, "missing", "changed"):
        raise ValueError("unknown mutation")
    guard_raw, guard = selected_guard()
    profile_raw = canonical(technical_profile(guard))
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        infos = archive.infolist()
        names = [x.filename for x in infos]
        expected = ["META/technical-profile.json", "runtime/status_guard.py"] + [
            "files/" + name for name, _ in guard.ROWS]
        if names != expected or len(set(names)) != len(names):
            raise ValueError("runtime guard archive members differ")
        if any(x.is_dir() or x.compress_type != zipfile.ZIP_STORED or x.create_system != 3
               or x.external_attr >> 16 != 0o100644 for x in infos):
            raise ValueError("unsafe runtime guard archive member")
        if archive.read(names[0]) != profile_raw or archive.read(names[1]) != guard_raw:
            raise ValueError("runtime guard control differs")
        with tempfile.TemporaryDirectory(prefix="cal-api40-status-guard-") as directory:
            root = Path(directory)
            for name in names:
                raw = archive.read(name)
                target = root / name.removeprefix("files/")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            profile_path = root / "META/technical-profile.json"
            original_guard_path = root / "runtime/status_guard.py"
            if sha(read_regular(original_guard_path)) != GUARD_SHA or sha(read_regular(profile_path)) != sha(profile_raw):
                raise ValueError("extracted guard/profile changed")
            target = root / guard.ROWS[-1][0]
            if mutation == "missing":
                target.unlink()
            elif mutation == "changed":
                target.write_bytes(b"changed\n")
            process = subprocess.run([sys.executable, "-I", "-B", "-c", BOOT, GUARD_SHA,
                                      str(original_guard_path), str(root), sha(profile_raw)],
                                     input=guard_raw, cwd=root, capture_output=True, timeout=30)
            if process.stderr:
                raise ValueError("clean-root guard emitted stderr")
            response = parse(process.stdout.strip())
            if mutation is None:
                if (process.returncode != 0 or response !=
                        {"schema_version": "lab-api40-status-runtime-guard-result/v1",
                         "status": "PASS", "operation": "lab.status", "verified_file_count": 7,
                         "original_service_executed": False,
                         "portable_api40_closure_complete": False, "authority_effect": "none"}):
                    raise ValueError("clean-root technical guard refused")
                return {"status": "PASS", "verified_files": 7}
            if (process.returncode != 1 or response.get("status") != "REFUSED" or
                    response.get("error_class") != ("FileNotFoundError" if mutation == "missing" else "ValueError")):
                raise ValueError("clean-root negative did not refuse")
            if mutation == "changed" and response.get("error") != "source changed " + guard.ROWS[-1][0]:
                raise ValueError("wrong changed-source refusal")
            if mutation == "missing" and response.get("error") != (
                    "[Errno 2] No such file or directory: '" + target.name + "'"):
                raise ValueError("wrong missing-source refusal")
            return {"status": "REFUSED", "reason": mutation + " selected catalog"}


def verify(blob):
    if blob != build():
        raise ValueError("runtime guard archive bytes differ")
    return {"schema_version": "lab-api40-status-runtime-guard-replay/v2",
            "archive_sha256": sha(blob), "technical_guard_sha256": GUARD_SHA,
            "selected_file_count": 7, "privacy_selected_classes": "PASS",
            "full_source_guard_rows_omitted": 201,
            "flagged_full_source_rows_omitted": list(UNSAFE_OMITTED),
            "positive": extracted_run(blob),
            "missing": extracted_run(blob, "missing"),
            "changed": extracted_run(blob, "changed"),
            "original_service_executed": False,
            "portable_api40_closure_complete": False,
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
        write_new(ARCHIVE, build())
    print(json.dumps(verify(read_regular(ARCHIVE)), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
