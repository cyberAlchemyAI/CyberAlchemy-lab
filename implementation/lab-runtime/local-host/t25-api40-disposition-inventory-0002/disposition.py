"""Cold, bounded classification of the API40 profile against T25 selected bytes."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat

ROOT = Path(__file__).absolute().parents[4]
HERE = Path(__file__).absolute().parent
PROFILE = "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/contract-profile.json"
PROFILE_SHA = "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614"
ORIGINAL = "product/lab/release-candidates/v1/release-validation/0001/final-member-inputs-0276.json"
ORIGINAL_SHA = "a099221682af6d061cad24f4759ec225541f203882627fa74361285b54b25987"
CANDIDATE = "implementation/lab-runtime/local-host/t25-local-candidate-0001/INVENTORY.json"
CANDIDATE_SHA = "268e54ebce2674006b327f1a1d5c45ff64ac7031465eaa3d9b35e4845306b8e9"
OUTPUT = HERE / "DISPOSITIONS.json"


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
    if not path.is_absolute() or ".." in path.parts or len(path.parts) < 2:
        raise ValueError("absolute canonical selected path required")
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


def regular_unlinked(path):
    path = Path(path)
    parent = parent_fd(path)
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError("nonregular selected path")
            with os.fdopen(os.dup(fd), "rb") as stream:
                return stream.read()
        finally:
            os.close(fd)
    finally:
        os.close(parent)


def selected(name, expected):
    raw = regular_unlinked(ROOT / name)
    if sha(raw) != expected:
        raise ValueError("selected bytes changed: " + name)
    return parse(raw)


def profile_rows(profile):
    rows = profile["files"]
    if len(rows) != 33424 or any(type(row) is not dict or set(row) not in
                                  ({"path", "sha256"}, {"path", "sha256", "size_bytes"})
                                  for row in rows):
        raise ValueError("API40 profile row shape/count changed")
    paths = [row["path"] for row in rows]
    if len(set(paths)) != len(paths) or paths != sorted(paths):
        raise ValueError("API40 profile paths duplicate or reorder")
    for row in rows:
        if (type(row["path"]) is not str or not row["path"] or
                type(row["sha256"]) is not str or len(row["sha256"]) != 64 or
                any(ch not in "0123456789abcdef" for ch in row["sha256"])):
            raise ValueError("API40 profile path or digest invalid")
        if "size_bytes" in row and (type(row["size_bytes"]) is not int or row["size_bytes"] < 0):
            raise ValueError("API40 profile size invalid")
    return rows


def archive_selection(original, candidate):
    rows = original["files"]
    if (original["original_members"] != 363 or len(rows) != 681 or
            len({row["path"] for row in rows}) != 681 or
            len(candidate["additions"]) != 799 or len(candidate["original_member_ids"]) != 363 or
            candidate["archive_sha256"] != "020f2755bd2687003f15d93a49a1e3bd6a49d838e3efe1398d6731881edce448"):
        raise ValueError("T25 selected archive inventory changed")
    indexed = {}
    for row in rows:
        name = row["path"]
        if type(name) is not str or not name or type(row["sha256"]) is not str:
            raise ValueError("invalid original archive row")
        indexed[name] = (row["sha256"], "META/original-public-inputs.zip!files/" + name)
    for row in candidate["additions"]:
        member = row["path"]
        if not member.startswith("api40/"):
            continue
        name = member.removeprefix("api40/")
        if name in indexed:
            raise ValueError("ambiguous original/API40 archive path")
        indexed[name] = (row["sha256"], member)
    return indexed


def review_class(path):
    if path.startswith("/"):
        return "absolute-host-path"
    if path.startswith("authority/"):
        return "authority-path"
    if path.startswith("docs/"):
        return "document-or-evidence-path"
    if path.startswith(("product/", "implementation/")):
        return "product-or-implementation-path"
    return "other-relative-path"


def classify(profile, original, candidate):
    archived = archive_selection(original, candidate)
    result = []
    matches = set()
    for source in profile_rows(profile):
        name, digest = source["path"], source["sha256"]
        selected_pair = archived.get(name)
        exact = selected_pair is not None and selected_pair[0] == digest
        if exact:
            matches.add(name)
        result.append({"path": name, "sha256": digest,
                       "profile_size_bytes": source.get("size_bytes"),
                       "disposition": "archive-byte-selected" if exact else "unresolved",
                       "archive_member": selected_pair[1] if exact else None,
                       "review_class": review_class(name),
                       "archive_path_digest_conflict": selected_pair is not None and not exact,
                       "portable_install_verified": False,
                       "runtime_consumption_verified": False})
    if len(matches) != 684 or sum(row["archive_path_digest_conflict"] for row in result) != 0:
        raise ValueError("exact T25/API40 overlap changed")
    if sum(row["archive_member"].startswith("api40/") for row in result if row["archive_member"]) != 3:
        raise ValueError("API40 addition overlap changed")
    return result


def build():
    profile = selected(PROFILE, PROFILE_SHA)
    original = selected(ORIGINAL, ORIGINAL_SHA)
    candidate = selected(CANDIDATE, CANDIDATE_SHA)
    rows = classify(profile, original, candidate)
    document = {"schema_version": "lab-t25-api40-disposition-inventory/v2",
                "profile_binding": {"path": PROFILE, "sha256": PROFILE_SHA},
                "original_binding": {"path": ORIGINAL, "sha256": ORIGINAL_SHA},
                "candidate_binding": {"path": CANDIDATE, "sha256": CANDIDATE_SHA},
                "candidate_archive_sha256": candidate["archive_sha256"],
                "rows": rows}
    counts = {}
    for row in rows:
        key = row["review_class"]
        counts[key] = counts.get(key, 0) + 1
    summary = {"schema_version": "lab-t25-api40-disposition-result/v2",
               "profile_rows": len(rows),
               "archive_exact_rows": sum(row["disposition"] == "archive-byte-selected" for row in rows),
               "unresolved_rows": sum(row["disposition"] == "unresolved" for row in rows),
               "archive_conflict_rows": sum(row["archive_path_digest_conflict"] for row in rows),
               "review_class_counts": counts,
               "installed_api40_replay": False, "portable_closure_complete": False,
               "authority_effect": "none", "task_complete": False}
    # One immutable artifact means an interrupted create cannot publish a
    # mismatched table/result pair. The summary is bound inside the document.
    document["summary"] = summary
    return canonical(document)


def write_new(path, raw):
    path = Path(path)
    parent = parent_fd(path)
    temporary = "." + path.name + ".staging-" + secrets.token_hex(12)
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
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
        parser.error("select exactly one of --create or --verify")
    document = build()
    if args.create:
        write_new(OUTPUT, document)
    else:
        if regular_unlinked(OUTPUT) != document:
            raise ValueError("frozen disposition bytes differ")
    print(json.dumps(parse(document)["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
