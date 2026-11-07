"""Explicit v2 commands. Legacy commands remain on the frozen v1 launcher."""
import argparse
import json
from pathlib import Path
import sys

from . import VERSION
from .capture import snapshot
from .contracts import SCHEMAS, check
from .exact import Refusal, binding, decode, encode, read, require, sha, write_package
from .host import NativeHost
from .materialize import materialize
from .package import export, inspect_local
from .prepare import prepare

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parents[2]


def integrity():
    manifest = decode(read(PACKAGE / "runtime-manifest.json", maximum=1048576))
    require(manifest["schema_version"] == "cal.define.runtime-manifest/v2" and manifest["authority_effect"] == "none", "invalid-runtime-manifest")
    require(sha(encode(manifest["files"])) == manifest["inventory_sha256"], "runtime-inventory-mismatch", exit_code=3)
    for row in manifest["files"]:
        raw = read(REPO / row["path"])
        require(sha(raw) == row["sha256"] and len(raw) == row["bytes"], "runtime-source-drift", row["path"], 3)
    return len(manifest["files"])


def parser():
    p = argparse.ArgumentParser(description="Define v2: exact candidate preparation; no admission or domain execution.")
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    s = sub.add_parser("example");s.add_argument("--output", required=True)
    s = sub.add_parser("schema");s.add_argument("kind", choices=SCHEMAS)
    s = sub.add_parser("capture-snapshot")
    s.add_argument("--request", required=True);s.add_argument("--source-root", default=str(REPO));s.add_argument("--output", required=True)
    s.add_argument("--permit-retention", action="store_true", help="Explicitly attest local retention rights for all selected inputs; not host permission")
    s = sub.add_parser("prepare")
    s.add_argument("--request", required=True);s.add_argument("--capture", required=True);s.add_argument("--output", required=True)
    s = sub.add_parser("inspect-package");s.add_argument("directory")
    s = sub.add_parser("reconstruct-local");s.add_argument("directory");s.add_argument("--output", required=True)
    s = sub.add_parser("materialize");s.add_argument("directory");s.add_argument("--output", required=True)
    s = sub.add_parser("observe-use");s.add_argument("directory");s.add_argument("--requested-use", required=True);s.add_argument("--consumer", required=True);s.add_argument("--output", required=True)
    s = sub.add_parser("compile");s.add_argument("directory")
    for name in ["retain-package", "read-retained", "stage-review", "inspect-local-operation"]:
        s = sub.add_parser(name);s.add_argument("--host-selection", required=True);s.add_argument("--request", required=True)
    return p


def run(args):
    checked = integrity()
    if args.command == "doctor":
        return {"version": VERSION, "runtime_integrity": "verified", "checked_files": checked,
                "preparation": "available", "live_host": "requires-independent-selection-and-qualification", "release_adopted": False}
    if args.command == "schema":return SCHEMAS[args.kind]
    if args.command == "example":
        from .example import incident_request
        request = incident_request(REPO)
        write_package(args.output, {"request.json": encode(request)})
        return {"outcome": "prepared", "posture": "synthetic-authored-input", "output": str(Path(args.output).absolute())}
    if args.command == "capture-snapshot":
        request_raw = read(args.request, maximum=1048576);request = decode(request_raw)
        args.exact_request_binding = binding(request_raw, Path(args.request).name)
        capture, members = snapshot(request, Path(args.source_root), permit_retention=args.permit_retention)
        write_package(args.output, {"capture.json": encode(capture), **{"inputs/" + path: raw for path, raw in members.items()}})
        return {"outcome": "prepared-with-gaps", "capture_mode": "historical-snapshot", "output": str(Path(args.output).absolute()), "input_count": len(capture["input_rows"]), "live_host_capture": False}
    if args.command == "prepare":
        capture_dir = Path(args.capture)
        request_raw = read(args.request, maximum=1048576)
        args.exact_request_binding = binding(request_raw, Path(args.request).name)
        pack, report, members = prepare(request_raw, read(capture_dir / "capture.json", maximum=1048576), capture_dir / "inputs")
        result = export(args.output, pack, members)
        return {**result, "outcome": "prepared-with-gaps" if pack["gaps"] else "prepared", "readiness": report["readiness"], "output": str(Path(args.output).absolute())}
    if args.command in ("inspect-package", "reconstruct-local"):
        raw, m, required, buffers = inspect_local(args.directory)
        if args.command == "reconstruct-local":write_package(args.output, {**buffers, "manifest.json": raw})
        return {"outcome": "prepared", "root_sha256": sha(raw), "pack_sha256": m["pack_binding"]["sha256"], "required_members_verified": len(required), "current_use_readiness": "not-established", "posture": "complete-local-frozen-inspection"}
    if args.command == "materialize":return materialize(args.directory, args.output)
    if args.command == "observe-use":
        from .observe import observe
        return observe(args.directory, args.requested_use, args.consumer, REPO, args.output)
    if args.command == "compile":
        inspect_local(args.directory)
        raise Refusal("unsupported-pack-compile", "Pack/v2 is not the legacy semantic compiler protocol; choose a separately qualified consumer", 4)
    host = NativeHost(args.host_selection)
    request_raw = read(args.request, maximum=1048576)
    args.exact_request_binding = binding(request_raw, Path(args.request).name)
    request = decode(request_raw)
    # Host-owned operations validate their exact native contracts and permission.
    result = host.call(args.command, {"request_binding": binding(request_raw, Path(args.request).name), "request": request})
    require(isinstance(result, dict) and result.get("authority_effect") == "none", "invalid-host-result", exit_code=3)
    if args.command == "stage-review":
        from .exact import shape
        shape(result, ("schema_version", "request_binding", "cohort_binding", "source_cut", "workspace_ref", "workspace_binding", "policy_selection_binding", "target_bindings", "routing_binding", "stage_receipt_binding", "posture", "actual_owner_outcome", "current_owner_authority_verified", "authority_effect"))
        require(result["posture"] == "candidate-only" and result["actual_owner_outcome"] is None and result["current_owner_authority_verified"] is False, "host-stage-authority-promotion", exit_code=3)
    elif args.command == "retain-package":
        from .custody import LOCATOR, RECEIPT
        loc, pin = LOCATOR.fullmatch(result.get("locator", "")), RECEIPT.fullmatch(result.get("receipt_ref", ""))
        require(loc is not None and pin is not None and loc[1] == pin[1] and loc[2] == pin[2] and result.get("content_digest") == "sha256:" + loc[2], "invalid-retention-result", exit_code=3)
    elif args.command == "read-retained":
        require(result.get("schema_version") == "cal.define.reconstruction-observation/v1" and result.get("outcome") == "complete-frozen-reconstruction", "incomplete-reconstruction-result", exit_code=3)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = run(args)
        if args.command == "schema":sys.stdout.buffer.write(encode(result));return 0
        sys.stdout.buffer.write(encode({"schema_version": "cal.define.result/v2", "command": args.command,
                                      "request_binding": getattr(args, "exact_request_binding", None),
                                      "package_binding": {"root_sha256": result["root_sha256"], "pack_sha256": result["pack_sha256"]} if "root_sha256" in result and "pack_sha256" in result else None,
                                      "outcome": result.get("outcome") if result.get("outcome") in ("prepared", "prepared-with-gaps", "blocked", "invalid-input", "unsupported", "interrupted", "outcome-unknown") else "prepared", "readiness": result.get("readiness", {}),
                                      "diagnostics": [], "continuation": [],
                                      "observed_writes": [str(Path(args.output).absolute())] if getattr(args, "output", None) else [],
                                      "result": result, "authority_effect": "none"}))
        return 0
    except KeyboardInterrupt:
        sys.stdout.buffer.write(encode({"schema_version": "cal.define.result/v2", "outcome": "interrupted", "authority_effect": "none"}));return 130
    except (Refusal, OSError, KeyError, TypeError, ValueError) as exc:
        known = isinstance(exc, Refusal)
        # Do not echo raw inputs, provider stderr, private paths or credentials.
        code = exc.code if known else "invalid-input-or-unavailable-source"
        sys.stdout.buffer.write(encode({"schema_version": "cal.define.result/v2", "command": args.command,
                                      "outcome": "outcome-unknown" if code in ("host-outcome-unknown", "stage-outcome-unknown") else "unsupported" if known and exc.exit_code == 4 else "blocked" if known and exc.exit_code == 3 else "invalid-input",
                                      "diagnostics": [{"code": code, "message": str(exc) if known else "Input or required source unavailable; no success inferred."}], "authority_effect": "none"}))
        return exc.exit_code if known else 2


if __name__ == "__main__":raise SystemExit(main())
