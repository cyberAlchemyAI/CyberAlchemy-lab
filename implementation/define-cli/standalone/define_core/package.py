"""Frozen package closure and exact local reconstruction; never follows member locators."""
from .exact import IDENT, HEX, binding, decode, encode, logical, member_paths, read, require, sha, shape, write_package
from .contracts import check


def manifest_for(pack, members):
    require("manifest.json" not in members and "pack.json" in members, "invalid-package-members")
    member_paths({*members, "manifest.json"})
    rows = {}
    for index, (path, raw) in enumerate(sorted(members.items())):
        logical(path)
        identity = "m" + str(index).zfill(4)
        rows[identity] = {"path": path, "role": "pack" if path == "pack.json" else "capture" if path == "capture.json" else "report" if path == "report.json" else "selected-input",
                          "media_type": "application/json" if path.endswith(".json") else "application/octet-stream", "encoding": "original-bytes",
                          "sha256": sha(raw), "bytes": len(raw), "required": True, "dependencies": []}
    identity = next(i for i, r in rows.items() if r["path"] == "pack.json")
    return {"schema_version": "cal.define.package-manifest/v1", "package_id": pack["pack_id"], "revision": pack["revision"],
            "pack_binding": {"member_id": identity, "sha256": rows[identity]["sha256"], "bytes": rows[identity]["bytes"], "media_type": "application/json"},
            "members": rows, "required_roots": list(rows), "closure_purpose": "frozen-pack-inspection",
            "limitations": [pack["claim_ceiling"], "Historical source standing is preserved; current permission and readiness require separate observations."], "authority_effect": "none"}


def privacy(raw):
    require(b"PRIVATE KEY-----" not in raw, "private-material", "Required member contains private key material", 3)
    try:
        value = decode(raw, source=True)
    except Exception as exc:
        from .exact import Refusal
        if isinstance(exc, Refusal) and exc.code == "invalid-json":
            # Text evidence is retained exactly; binary/unsupported encodings require an explicit successor.
            try:raw.decode("utf-8", errors="strict")
            except UnicodeError:require(False, "unsupported-member-encoding", exit_code=4)
            return
        raise
    def visit(v):
        if isinstance(v, dict):
            require(not ({"private_key", "access_token", "refresh_token", "password", "raw_session_memory", "session_memory"} & {k.lower() for k in v}), "private-material", "Required member contains excluded private/session material", 3)
            for child in v.values():visit(child)
        elif isinstance(v, list):
            for child in v:visit(child)
    visit(value)


def validate_manifest(raw):
    require(len(raw) <= 262144, "manifest-budget")
    m = decode(raw)
    shape(m, ("schema_version", "package_id", "revision", "pack_binding", "members", "required_roots", "closure_purpose", "limitations", "authority_effect"))
    require(m["schema_version"] == "cal.define.package-manifest/v1" and m["authority_effect"] == "none" and m["closure_purpose"] == "frozen-pack-inspection", "unsupported-package", exit_code=4)
    require(isinstance(m["members"], dict) and 1 <= len(m["members"]) <= 256, "member-budget")
    paths = set()
    for identity, row in m["members"].items():
        require(IDENT.fullmatch(identity) and "." not in identity, "invalid-member-id")
        shape(row, ("path", "role", "media_type", "encoding", "sha256", "bytes", "required", "dependencies"))
        logical(row["path"])
        require(row["path"] not in paths and row["path"] != "manifest.json", "duplicate-member-path")
        paths.add(row["path"])
        require(isinstance(row["sha256"], str) and HEX.fullmatch(row["sha256"]) and type(row["bytes"]) is int and 0 <= row["bytes"] <= 16777216 and type(row["required"]) is bool, "invalid-member-binding")
        require(row["encoding"] == "original-bytes" and row["media_type"] in ("application/json", "application/octet-stream", "text/plain"), "unsupported-member-encoding", exit_code=4)
        require(isinstance(row["dependencies"], list) and len(row["dependencies"]) <= 256 and len(set(row["dependencies"])) == len(row["dependencies"]) and all(d in m["members"] for d in row["dependencies"]), "invalid-dependency")
    member_paths({*paths, "manifest.json"})
    require(isinstance(m["required_roots"], list) and len(m["required_roots"]) <= 256 and len(set(m["required_roots"])) == len(m["required_roots"]), "invalid-required-roots")
    required, pending = set(), [(i, 0) for i in list(m["required_roots"]) + [i for i, r in m["members"].items() if r["required"]]]
    while pending:
        identity, depth = pending.pop()
        require(identity in m["members"], "missing-dependency")
        if identity not in required:
            require(depth <= 64, "dependency-depth")
            required.add(identity);pending.extend((i, depth + 1) for i in m["members"][identity]["dependencies"])
    shape(m["pack_binding"], ("member_id", "sha256", "bytes", "media_type"))
    b = m["pack_binding"];require(b["member_id"] in required, "pack-not-required")
    r = m["members"][b["member_id"]]
    require(r["path"] == "pack.json" and all(b[k] == r[k] for k in ("sha256", "bytes", "media_type")), "pack-binding-mismatch")
    require(sum(r["bytes"] for r in m["members"].values()) + len(raw) <= 16 * 1024 * 1024, "package-budget")
    return m, required


def verify_package(manifest_raw, loader, *, all_members=False):
    m, required = validate_manifest(manifest_raw)
    chosen = set(m["members"]) if all_members else required
    buffers = {}
    for identity in sorted(chosen):
        row = m["members"][identity]
        try:raw = loader(identity, row)
        except (KeyError, FileNotFoundError) as exc:
            from .exact import Refusal
            raise Refusal("reconstruction-incomplete", "Required member is absent: " + identity, 3) from exc
        require(len(raw) == row["bytes"] and sha(raw) == row["sha256"], "reconstruction-incomplete", "Missing or corrupt member " + identity, 3)
        privacy(raw);buffers[row["path"]] = raw
    pack = decode(buffers["pack.json"]);require(isinstance(pack, dict), "invalid-pack-document");require(pack.get("schema_version") == "cal.define.pack/v3", "unsupported-pack-version", exit_code=4);check(pack, "pack")
    require(pack["pack_id"] == m["package_id"] and pack["revision"] == m["revision"], "package-identity-mismatch")
    def exact_member(b, prefix=""):
        path = prefix + b["path"]
        require(path in buffers and sha(buffers[path]) == b["sha256"] and len(buffers[path]) == b["bytes"], "reconstruction-incomplete", "Required captured binding is absent or altered", 3)
    exact_member(pack["capture_binding"])
    exact_member(pack["lineage"]["request_binding"])
    capture = decode(buffers[pack["capture_binding"]["path"]]);check(capture, "capture")
    from .capture import bindings_in
    for b in bindings_in(capture):exact_member(b, "inputs/")
    for b in bindings_in(decode(buffers[pack["lineage"]["request_binding"]["path"]])):
        exact_member(b, "inputs/")
    # Recheck embedded refs against the frozen Pack, without turning this into domain execution.
    from .prepare import resolve_reference
    for app in pack["applications"]:
        if app["meaning_ref"]["kind"] == "embedded":resolve_reference(app["meaning_ref"], {}, {}, pack)
    for assessment in pack["assessments"]:resolve_reference(assessment["application_ref"], {}, {}, pack)
    return m, required, buffers


def inspect_local(directory):
    from pathlib import Path
    directory = Path(directory)
    raw = read(directory / "manifest.json", maximum=1024 * 1024)
    m, required, buffers = verify_package(raw, lambda _, row: read(directory / row["path"]))
    return raw, m, required, buffers


def export(destination, pack, members):
    m = manifest_for(pack, members);raw = encode(m)
    verify_package(raw, lambda _, row: members[row["path"]], all_members=True)
    write_package(destination, {**members, "manifest.json": raw})
    return {"root_sha256": sha(raw), "pack_sha256": sha(members["pack.json"]), "member_count": len(m["members"]), "authority_effect": "none"}
