#!/usr/bin/env python3
"""Route six exact W06 bodies through a disposable native Store.apply fixture."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNTIME = HERE / "runtime"
MANIFEST_SHA = "e44501e5ba57158430744931fcb1549b9dc7156522eb941ca8a94ec96a280dd5"
PREVIOUS_RUN = ROOT / "implementation/lab-runtime/local-host/t11-native-one-member-0001/run.py"
PREVIOUS_RUN_SHA = "a496cb9c75666c35926d9238a2c5d787073bca4428c86d101928807924dee444"
MATRIX = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T11/scope-routing-matrix-0002.json",
          "sha256": "f74f5c6a85e7eacb420785165fcb8257f2120337b31e482bf6bfb65125575628"}
ROUTER = ROOT / "implementation/lab-runtime/local-host/t11-scoped-consumer-0001/router.py"
ROUTER_SHA = "171da60bce9b203c27c836029cb4b5e57b6d10f4cf99162e0a04d54578115052"
SCOPE = "scope:lab-runtime-local:w06-learning-0002-560605b8"


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def module_from_pinned(name, path, digest):
    raw = path.read_bytes()
    need(sha(raw) == digest, "selected executable changed: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(raw, str(path), "exec", dont_inherit=True), module.__dict__)
    return module


def preflight():
    raw = (HERE / "RUNTIME-MANIFEST.json").read_bytes()
    need(sha(raw) == MANIFEST_SHA, "runtime manifest changed")
    manifest = json.loads(raw)
    need(manifest["schema_version"] == "lab-T11-W06-six-native-fixture-runtime/v1" and
         manifest["selected_scope_ref"] == SCOPE and len(manifest["selected_members"]) == 6 and
         len(manifest["files"]) == 45 and
         {r["path"] for r in manifest["files"] if r["sha256"] != r["previous_sha256"]} ==
         {"lab_runtime/operations.py", "lab_runtime/store.py", "profile.json"},
         "runtime cut differs")
    actual = {p.relative_to(RUNTIME).as_posix() for p in RUNTIME.rglob("*") if p.is_file()}
    need(actual == {r["path"] for r in manifest["files"]}, "runtime file set differs")
    for row in manifest["files"]:
        path = RUNTIME / row["path"]
        need(not path.is_symlink() and sha(path.read_bytes()) == row["sha256"],
             "runtime file changed: " + row["path"])
    matrix = json.loads((ROOT / MATRIX["path"]).read_bytes())
    need(sha((ROOT / MATRIX["path"]).read_bytes()) == MATRIX["sha256"], "selected matrix changed")
    selected = [r for r in matrix["routes"] if r["body_scope_ref"] == SCOPE]
    need(len(matrix["routes"]) == 230 and len(selected) == 6 and
         {r["version_ref"] for r in selected} == set(manifest["selected_members"]),
         "selected W06 routes differ")
    need(all(manifest["selected_members"][r["version_ref"]] ==
             {"carrier": r["carrier_ref"], "sha256": r["body_binding"]["sha256"]}
             for r in selected), "selected W06 member contract differs")
    profile = json.loads((RUNTIME / "profile.json").read_bytes())
    expected = {"implementation/lab-runtime/local-host/t11-native-w06-six-0001/runtime/" + row["path"]
                for row in manifest["files"]}
    need(set(profile["runtime_materials"]) == expected, "runtime profile misses executable closure")
    previous = module_from_pinned("t11_previous_native", PREVIOUS_RUN, PREVIOUS_RUN_SHA)
    router = module_from_pinned("t11_scoped_router", ROUTER, ROUTER_SHA)
    return manifest, selected, previous, router


def grant(router, signer, route, now):
    core = {"schema": "lab-local-scoped-body-grant/v1", "actor": "fixture:t11-w06",
            "member_ref": route["member_ref"], "scope_ref": route["body_scope_ref"],
            "body_sha256": route["body_binding"]["sha256"], "operation": route["operation"],
            "not_before": (now - timedelta(minutes=1)).isoformat(),
            "expires_at": (now + timedelta(minutes=5)).isoformat()}
    return {"grant": core, "signature": signer.sign(router.canonical(core)).hex()}


class NativeRouteRefusal(ValueError):
    pass


def selected_body(manifest, consumer, router, signer, route, now):
    contract = manifest["selected_members"].get(route.get("version_ref"))
    if (route.get("body_scope_ref") != SCOPE or contract is None or
            route.get("carrier_ref") != contract["carrier"] or
            route.get("body_binding", {}).get("sha256") != contract["sha256"] or
            consumer.routes.get(route.get("member_ref")) != route):
        raise NativeRouteRefusal("no exact W06 native consumer for selected member and scope")

    def exact(raw, delivered):
        need(delivered == route and sha(raw) == route["body_binding"]["sha256"],
             "delivered route or bytes differ")
        return raw
    return consumer.consume(route["member_ref"], route["body_scope_ref"],
                            grant(router, signer, route, now), exact)


def run():
    manifest, selected, previous, router = preflight()
    signer = Ed25519PrivateKey.generate()
    consumer = router.ScopedConsumer(ROOT, MATRIX, signer.public_key())
    negatives = []
    first = selected[0]
    now = datetime.now(timezone.utc)
    packet = grant(router, signer, first, now)
    for label, member, scope, callback in (
        ("wrong-scope", first["member_ref"], "scope:other", lambda *_: None),
        ("missing-consumer", first["member_ref"], SCOPE, None),
        ("unsupported-member", "protocol:unknown", SCOPE, lambda *_: None),
    ):
        try:
            consumer.consume(member, scope, packet, callback)
        except router.RouteRefusal as exc:
            negatives.append({"case": label, "reason": str(exc)})
        else:
            raise ValueError("scope route accepted " + label)
    expired = grant(router, signer, first, now - timedelta(minutes=10))
    try:
        consumer.consume(first["member_ref"], SCOPE, expired, lambda *_: None)
    except router.RouteRefusal as exc:
        need("lease" in str(exc), "expired grant refused for wrong reason: " + str(exc))
        negatives.append({"case": "expired-grant", "reason": str(exc)})
    else:
        raise ValueError("expired scoped grant accepted")
    bodies = {route["version_ref"]: selected_body(manifest, consumer, router, signer, route,
                                                   datetime.now(timezone.utc))
              for route in selected}
    need(len(bodies) == 6, "full W06 body delivery absent")
    sys.path.insert(0, str(RUNTIME))
    store_module = importlib.import_module("lab_runtime.store")
    custody = importlib.import_module("lab_runtime.custody")
    operations = importlib.import_module("lab_runtime.operations")
    common = importlib.import_module("lab_runtime.common")
    need(all(Path(m.__file__).resolve().is_relative_to(RUNTIME.resolve())
             for m in (store_module, custody, operations, common)), "runtime module origin differs")
    receipts = []
    scratch = HERE / "working"
    scratch.mkdir(mode=0o700, exist_ok=True)
    need(not scratch.is_symlink() and scratch.resolve().is_relative_to(HERE.resolve()),
         "task scratch redirected")
    with tempfile.TemporaryDirectory(prefix="cal-T11-W06-six-", dir=scratch) as temp:
        owned = Path(temp)
        source_root = owned / "historical-source"
        entries = previous.historical_snapshot(source_root)
        for row in manifest["files"]:
            target = source_root / manifest["copied_root"] / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as output:
                output.write((RUNTIME / row["path"]).read_bytes())
        store_module.keygen(owned / "owner.pem", owned / "owner.pub")
        store = store_module.Store(owned / "store", source_root)
        profile = common.load(RUNTIME / "profile.json")
        store.initialize(profile, "T11-W06-fixture", "principal:t11-local-fixture",
                         (owned / "owner.pub").read_text().strip(),
                         allowed_categories=["artifact-instance"], allowed_effects=["admit"],
                         selected_scope_ref=SCOPE)
        for index, route in enumerate(selected, 1):
            before = store.replay(require_current=True)
            version = route["version_ref"]
            raw = bodies[version]
            body = json.loads(raw)
            config = before["config"]
            proposal = {"schema_version": "lab-runtime-proposal/v1",
                        "proposal_id": f"T11-W06-exact-fixture-{index:02d}",
                        "expected_head": before["head"]["transaction_digest"],
                        "source_snapshot_digest": config["source_snapshot_digest"],
                        "scope_ref": SCOPE, "policy_ref": config["policy_ref"],
                        "challenge_route": config["challenge_route"], "schemas": {},
                        "targets": [{"category": "artifact-instance", "operation": "admit",
                                     "version_ref": version, "carrier_ref": route["carrier_ref"],
                                     "record": body, "predecessor_ref": None,
                                     "decision_ref": "decision:T11-W06-fixture:" + sha(version.encode())[:16],
                                     "contract": None}]}
            proposal = custody.with_originals(proposal, {version: raw}, {})
            preimage = common.digest(before["projection"])
            if index == 1:
                import copy
                for label, mutate, expected in (
                    ("wrong-scope", lambda p: p.__setitem__("scope_ref", "scope:other"),
                     "proposal outside provisioned scope"),
                    ("wrong-member", lambda p: p["targets"][0].__setitem__("version_ref", version + "-other"),
                     "T11 W06 exact member"),
                    ("wrong-byte-digest", lambda p: p["targets"][0]["content"].__setitem__("byte_sha256", "0" * 64),
                     "original content size or byte digest differs"),
                    ("stale-head", lambda p: p.__setitem__("expected_head", "0" * 64),
                     "stale expected HEAD"),
                ):
                    changed = copy.deepcopy(proposal)
                    mutate(changed)
                    try:
                        operations.prepare(before["projection"], changed,
                                           before["head"]["transaction_digest"], config)
                    except Exception as exc:
                        need(expected in str(exc), "wrong refusal cause: " + label + ": " + str(exc))
                        need(common.digest(before["projection"]) == preimage,
                             "negative changed projection")
                        negatives.append({"case": label, "reason": str(exc)})
                    else:
                        raise ValueError("native route accepted " + label)
            post, cores = operations.prepare(before["projection"], proposal,
                                             before["head"]["transaction_digest"], config)
            need(len(cores) == 1 and post["subjects"][version]["record"] == body and
                 post["subjects"][version]["source"]["sha256"] == sha(raw) and
                 common.digest(before["projection"]) == preimage,
                 "native prepared postimage differs")
            approval = store.authorize(proposal, owned / "owner.pem")
            store.apply(proposal, approval)
            after = store.replay(require_current=True)
            recovered = custody.original_bytes(store, version, after["head"]["transaction_digest"])
            need(recovered == raw and after["projection"]["subjects"][version]["record"] == body and
                 after["head"]["sequence"] == index,
                 "native applied original or sequence differs")
            receipts.append({"member_ref": route["member_ref"], "version_ref": version,
                             "scope_ref": SCOPE, "body_sha256": sha(raw),
                             "prepared_postimage_digest": common.digest(post),
                             "applied_projection_digest": common.digest(after["projection"]),
                             "transaction_head": after["head"]["transaction_digest"],
                             "effective_state": after["projection"]["subjects"][version]["effective_state"]})
        import copy
        duplicate = copy.deepcopy(proposal)
        duplicate["proposal_id"] = "T11-W06-duplicate-fixture"
        duplicate["expected_head"] = after["head"]["transaction_digest"]
        final_digest = common.digest(after["projection"])
        try:
            operations.prepare(after["projection"], duplicate,
                               after["head"]["transaction_digest"], after["config"])
        except Exception as exc:
            need("a recorded Decision identity cannot authorize different new effects" in str(exc),
                 "wrong duplicate refusal cause: " + str(exc))
            need(common.digest(after["projection"]) == final_digest,
                 "duplicate changed applied projection")
            negatives.append({"case": "duplicate-after-apply", "reason": str(exc)})
        else:
            raise ValueError("duplicate W06 candidate accepted after native apply")
        cold_code = ("import json,sys,hashlib;from pathlib import Path;sys.path.insert(0,sys.argv[1]);"
                     "from lab_runtime.store import Store;from lab_runtime.custody import original_bytes;"
                     "s=Store(sys.argv[2],sys.argv[3]);d=s.replay(require_current=True);"
                     "print(json.dumps({v:hashlib.sha256(original_bytes(s,v,d['head']['transaction_digest'])).hexdigest() "
                     "for v in json.loads(sys.argv[4])}))")
        cold = subprocess.run([sys.executable, "-I", "-B", "-c", cold_code,
                               str(RUNTIME), str(store.path), str(source_root),
                               json.dumps([r["version_ref"] for r in selected])],
                              capture_output=True, text=True, timeout=180)
        need(cold.returncode == 0, "cold readback failed: " + cold.stderr[:500])
        cold_map = json.loads(cold.stdout)
        need(cold_map == {r["version_ref"]: r["body_binding"]["sha256"] for r in selected},
             "cold readback body digests differ")
        need(not any(p.is_symlink() for p in store.path.rglob("*")), "fixture store entry linked")
        final_head = receipts[-1]["transaction_head"]
    need(not owned.exists(), "disposable fixture root remains")
    return {"schema_version": "lab-T11-W06-six-native-fixture-result/v1",
            "matrix_binding": MATRIX, "runtime_manifest_sha256": MANIFEST_SHA,
            "runner_sha256": sha(Path(__file__).read_bytes()),
            "historical_source_commit": previous.HISTORICAL_COMMIT,
            "historical_snapshot_entries": entries,
            "selected_members": len(selected), "by_scope": dict(Counter(r["scope_ref"] for r in receipts)),
            "native_prepare_and_apply_effects": len(receipts), "final_head": final_head,
            "receipts": receipts, "cold_readback": cold_map, "negative_cases": negatives,
            "original_operational_routes": 0, "T11_complete": False, "authority_effect": "none",
            "claim_ceiling": "Six exact W06 candidates applied in a disposable historical-source native fixture store; original producer execution, current source/grants and 224 other native routes remain unproved."}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
