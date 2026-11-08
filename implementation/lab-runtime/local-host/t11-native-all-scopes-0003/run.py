#!/usr/bin/env python3
"""Execute six exact-scope T11 fixture batches in disposable native stores."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import copy
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
SELECTED = ROOT / "implementation/lab-runtime/local-host/t11-native-all-scopes-0002"
RUNTIME = SELECTED / "runtime"
MANIFEST_SHA = "bb00b243739ddb87c3427c7aced1adf3768c874a04e78c471db0e7d33f474c37"
MATRIX = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T11/scope-routing-matrix-0002.json",
          "sha256": "f74f5c6a85e7eacb420785165fcb8257f2120337b31e482bf6bfb65125575628"}
ROUTER = ROOT / "implementation/lab-runtime/local-host/t11-scoped-consumer-0001/router.py"
ROUTER_SHA = "171da60bce9b203c27c836029cb4b5e57b6d10f4cf99162e0a04d54578115052"
PREVIOUS_RUN = ROOT / "implementation/lab-runtime/local-host/t11-native-one-member-0001/run.py"
PREVIOUS_RUN_SHA = "a496cb9c75666c35926d9238a2c5d787073bca4428c86d101928807924dee444"
LEGACY = "lab.legacy-source-assertion.cav2-product-thesis"


class NativeRouteRefusal(ValueError):
    pass


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_module(name, path, digest):
    raw = path.read_bytes()
    need(sha(raw) == digest, "selected executable changed: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(raw, str(path), "exec", dont_inherit=True), module.__dict__)
    return module


def preflight():
    manifest_raw = (SELECTED / "RUNTIME-MANIFEST.json").read_bytes()
    need(sha(manifest_raw) == MANIFEST_SHA, "runtime manifest changed")
    manifest = json.loads(manifest_raw)
    need(manifest["schema_version"] == "lab-T11-exact-230-bounded-native-fixture-runtime/v1" and
         manifest["selected_matrix_sha256"] == MATRIX["sha256"] and
         len(manifest["files"]) == 45 and len(manifest["selected_scopes"]) == 6 and
         sorted(s["members"] for s in manifest["selected_scopes"].values()) == [1, 1, 1, 1, 6, 220] and
         sorted(manifest["selected_scopes"][LEGACY]["batches"]) == [28, 64, 64, 64] and
         all(sum(s["batches"]) == s["members"] and all(0 < n <= 64 for n in s["batches"])
             for s in manifest["selected_scopes"].values()) and
         {r["path"] for r in manifest["files"] if r["sha256"] != r["previous_sha256"]} ==
         {"lab_runtime/store.py", "lab_runtime/operations.py", "profile.json"},
         "runtime cut differs")
    files = {p.relative_to(RUNTIME).as_posix() for p in RUNTIME.rglob("*") if p.is_file()}
    need(files == {r["path"] for r in manifest["files"]}, "runtime file set differs")
    for row in manifest["files"]:
        path = RUNTIME / row["path"]
        need(not path.is_symlink() and sha(path.read_bytes()) == row["sha256"],
             "runtime file changed: " + row["path"])
    profile = json.loads((RUNTIME / "profile.json").read_bytes())
    expected = {manifest["copied_root"] + "/" + r["path"] for r in manifest["files"]}
    need(set(profile["runtime_materials"]) == expected, "profile misses runtime closure")
    matrix_raw = (ROOT / MATRIX["path"]).read_bytes()
    need(sha(matrix_raw) == MATRIX["sha256"], "selected matrix changed")
    routes = json.loads(matrix_raw)["routes"]
    need(len(routes) == 230 and len({r["member_ref"] for r in routes}) == 230 and
         len({r["version_ref"] for r in routes}) == 230 and
         {s: sum(r["body_scope_ref"] == s for r in routes) for s in manifest["selected_scopes"]} ==
         {s: v["members"] for s, v in manifest["selected_scopes"].items()},
         "matrix route closure differs")
    previous = pinned_module("t11_original_native_snapshot", PREVIOUS_RUN, PREVIOUS_RUN_SHA)
    router = pinned_module("t11_exact_scoped_reader", ROUTER, ROUTER_SHA)
    return manifest, routes, previous, router


def signed_grant(router, signer, route, now):
    core = {"schema": "lab-local-scoped-body-grant/v1", "actor": "fixture:t11-exact-230",
            "member_ref": route["member_ref"], "scope_ref": route["body_scope_ref"],
            "body_sha256": route["body_binding"]["sha256"], "operation": route["operation"],
            "not_before": (now - timedelta(minutes=1)).isoformat(),
            "expires_at": (now + timedelta(minutes=5)).isoformat()}
    return {"grant": core, "signature": signer.sign(router.canonical(core)).hex()}


def deliver(consumer, router, signer, route, now, expected_routes):
    if expected_routes.get(route.get("member_ref")) != route:
        raise NativeRouteRefusal("no exact native consumer for member and scope")

    def accept(raw, delivered):
        need(delivered == route and sha(raw) == route["body_binding"]["sha256"],
             "native adapter received changed route or bytes")
        return raw

    return consumer.consume(route["member_ref"], route["body_scope_ref"],
                            signed_grant(router, signer, route, now), accept)


def route_bodies(manifest, routes, router):
    signer = Ed25519PrivateKey.generate()
    consumer = router.ScopedConsumer(ROOT, MATRIX, signer.public_key())
    selected = {r["member_ref"]: r for r in routes}
    now = datetime.now(timezone.utc)
    packet = signed_grant(router, signer, routes[0], now)
    refused = []
    for name, member, scope, callback in (
        ("cross-scope", routes[0]["member_ref"], "scope:other", lambda *_: None),
        ("missing-consumer", routes[0]["member_ref"], routes[0]["body_scope_ref"], None),
    ):
        try:
            consumer.consume(member, scope, packet, callback)
        except router.RouteRefusal as exc:
            refused.append({"case": name, "reason": str(exc)})
        else:
            raise ValueError("router accepted " + name)
    wrong = copy.deepcopy(routes[0])
    wrong["member_ref"] = "protocol:unknown"
    try:
        deliver(consumer, router, signer, wrong, now, selected)
    except NativeRouteRefusal as exc:
        refused.append({"case": "missing-native-route", "reason": str(exc)})
    else:
        raise ValueError("native adapter accepted missing route")
    expired = signed_grant(router, signer, routes[0], now - timedelta(minutes=10))
    try:
        consumer.consume(routes[0]["member_ref"], routes[0]["body_scope_ref"], expired,
                         lambda *_: None)
    except router.RouteRefusal as exc:
        need("lease" in str(exc), "expired grant refused for wrong reason: " + str(exc))
        refused.append({"case": "expired-grant", "reason": str(exc)})
    else:
        raise ValueError("expired scoped grant accepted")
    bodies = {r["version_ref"]: deliver(consumer, router, signer, r,
                                        datetime.now(timezone.utc), selected)
              for r in routes}
    need(len(bodies) == 230, "native adapter did not deliver 230 original bodies")
    return bodies, refused


def proposal_for(routes, bodies, before, custody, batch_index):
    scope = routes[0]["body_scope_ref"]
    config = before["config"]
    need(all(r["body_scope_ref"] == scope for r in routes), "cross-scope batch")
    targets = []
    for r in routes:
        version = r["version_ref"]
        body = json.loads(bodies[version])
        targets.append({"category": "artifact-instance", "operation": "admit",
                        "version_ref": version, "carrier_ref": r["carrier_ref"],
                        "record": body, "predecessor_ref": None,
                        "decision_ref": "decision:T11-fixture:" + sha(version.encode())[:16],
                        "contract": None})
    proposal = {"schema_version": "lab-runtime-proposal/v1",
                "proposal_id": "T11-exact-scope-" + config["store_id"] + "-batch-" + str(batch_index).zfill(2),
                "expected_head": before["head"]["transaction_digest"],
                "source_snapshot_digest": config["source_snapshot_digest"],
                "scope_ref": scope, "policy_ref": config["policy_ref"],
                "challenge_route": config["challenge_route"], "schemas": {},
                "targets": targets}
    return custody.with_originals(proposal, {r["version_ref"]: bodies[r["version_ref"]] for r in routes}, {})


def native_negatives(operations, common, before, proposal):
    negatives = []
    original = common.digest(before["projection"])
    head = before["head"]["transaction_digest"]
    cases = [
        ("wrong-scope", lambda p: p.__setitem__("scope_ref", "scope:other"), "proposal outside provisioned scope"),
        ("stale-head", lambda p: p.__setitem__("expected_head", "0" * 64), "stale expected HEAD"),
        ("wrong-member", lambda p: p["targets"][0].__setitem__("version_ref", "artifact:unknown@1"),
         "T11 exact scope batch"),
        ("changed-original-digest", lambda p: p["targets"][0]["content"].__setitem__("byte_sha256", "0" * 64),
         "original content size or byte digest differs"),
    ]
    if len(proposal["targets"]) > 1:
        reason = ("original content material count exceeds bound" if len(proposal["targets"]) == 220
                  else "T11 exact scope batch")
        cases.append(("missing-member", lambda p: p["targets"].pop(), reason))
    for label, mutate, expected in cases:
        changed = copy.deepcopy(proposal)
        mutate(changed)
        try:
            operations.prepare(before["projection"], changed, head, before["config"])
        except Exception as exc:
            need(expected in str(exc), "wrong refusal cause: " + label + ": " + str(exc))
            need(common.digest(before["projection"]) == original,
                 "refusal mutated original projection")
            negatives.append({"case": label, "reason": str(exc)})
        else:
            raise ValueError("native route accepted " + label)
    return negatives


def unresolved_selected_refs(group, processed, bodies):
    """Count selected internal references not yet present at an intermediate HEAD."""
    group_versions = {r["version_ref"] for r in group}
    processed_versions = {r["version_ref"] for r in processed}
    identity_to_version = {r["version_ref"].split("@", 1)[0]: r["version_ref"] for r in group}
    unresolved = 0
    for route in processed:
        body = json.loads(bodies[route["version_ref"]])
        for relation in body.get("relation_refs", []):
            target = relation["counterpart_ref"]
            if target in group_versions and target not in processed_versions:
                unresolved += 1
        if body["kind"] == "ontology-edge":
            for key in ("source_node_ref", "target_node_ref"):
                target = identity_to_version.get(body["payload"][key])
                if target is not None and target not in processed_versions:
                    unresolved += 1
    return unresolved


def run():
    manifest, routes, previous, router = preflight()
    bodies, negatives = route_bodies(manifest, routes, router)
    by_scope = defaultdict(list)
    for r in routes:
        by_scope[r["body_scope_ref"]].append(r)
    sys.path.insert(0, str(RUNTIME))
    store_module = importlib.import_module("lab_runtime.store")
    custody = importlib.import_module("lab_runtime.custody")
    operations = importlib.import_module("lab_runtime.operations")
    common = importlib.import_module("lab_runtime.common")
    need(all(Path(m.__file__).resolve().is_relative_to(RUNTIME.resolve())
             for m in (store_module, custody, operations, common)), "native module origin differs")
    scratch = HERE / "working"
    scratch.mkdir(mode=0o700, exist_ok=True)
    need(not scratch.is_symlink() and scratch.resolve().is_relative_to(HERE.resolve()),
         "task scratch redirected")
    receipts = []
    with tempfile.TemporaryDirectory(prefix="cal-T11-exact-230-", dir=scratch) as temp:
        owned = Path(temp)
        source_root = owned / "historical-source"
        entries = previous.historical_snapshot(source_root)
        for row in manifest["files"]:
            target = source_root / manifest["copied_root"] / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as output:
                output.write((RUNTIME / row["path"]).read_bytes())
        profile = common.load(RUNTIME / "profile.json")
        for scope in sorted(by_scope):
            group = by_scope[scope]
            store_id = manifest["selected_scopes"][scope]["store_id"]
            batch_sizes = manifest["selected_scopes"][scope]["batches"]
            batches = []
            cursor = 0
            for size in batch_sizes:
                batches.append(group[cursor:cursor + size])
                cursor += size
            need(cursor == len(group) and all(0 < len(batch) <= 64 for batch in batches),
                 "bounded scope partition differs")
            stem = sha(scope.encode())[:12]
            private, public = owned / (stem + ".pem"), owned / (stem + ".pub")
            store_module.keygen(private, public)
            store = store_module.Store(owned / (stem + "-store"), source_root)
            store.initialize(profile, store_id, "principal:t11-local-fixture", public.read_text().strip(),
                             allowed_categories=["artifact-instance"], allowed_effects=["admit"],
                             selected_scope_ref=scope)
            processed = []
            for batch_index, batch in enumerate(batches, 1):
                before = store.replay(require_current=True)
                proposal = proposal_for(batch, bodies, before, custody, batch_index)
                if batch_index == 1:
                    negatives.extend({"scope_ref": scope, **n} for n in
                                     native_negatives(operations, common, before, proposal))
                preimage = common.digest(before["projection"])
                post, cores = operations.prepare(before["projection"], proposal,
                                                 before["head"]["transaction_digest"], before["config"])
                need(len(cores) == len(batch) and common.digest(before["projection"]) == preimage and
                     all(post["subjects"][r["version_ref"]]["record"] == json.loads(bodies[r["version_ref"]]) and
                         post["subjects"][r["version_ref"]]["source"]["sha256"] ==
                         r["body_binding"]["sha256"] for r in batch),
                     "native prepared postimage differs")
                approval = store.authorize(proposal, private)
                store.apply(proposal, approval)
                after = store.replay(require_current=True)
                processed.extend(batch)
                rows = {row["version_ref"]: row for row in custody.content_rows(after)
                        if row["role"] == "authored-target"}
                need(len(rows) == len(processed) and after["head"]["sequence"] == batch_index and
                     all(rows[r["version_ref"]]["raw"] == bodies[r["version_ref"]] and
                         after["projection"]["subjects"][r["version_ref"]]["effective_state"] ==
                         "local-admitted-current" for r in processed),
                     "native applied exact cumulative originals differ")
                unresolved = unresolved_selected_refs(group, processed, bodies)
                receipts.append({"scope_ref": scope, "store_id": store_id,
                                 "batch_index": batch_index, "member_count": len(batch),
                                 "cumulative_member_count": len(processed),
                                 "unresolved_selected_internal_refs": unresolved,
                                 "before_head": before["head"]["transaction_digest"],
                                 "after_head": after["head"]["transaction_digest"],
                                 "preimage_projection_digest": preimage,
                                 "prepared_postimage_digest": common.digest(post),
                                 "applied_projection_digest": common.digest(after["projection"])})
            need(len(processed) == len(group) and receipts[-1]["unresolved_selected_internal_refs"] == 0,
                 "final scope member/reference closure incomplete")
            duplicate = copy.deepcopy(proposal)
            # Keep the closed batch identity so the exact native guard permits
            # the probe to reach the already-used Decision identity check.
            duplicate["expected_head"] = after["head"]["transaction_digest"]
            applied_digest = common.digest(after["projection"])
            try:
                operations.prepare(after["projection"], duplicate,
                                   after["head"]["transaction_digest"], after["config"])
            except Exception as exc:
                need("a recorded Decision identity cannot authorize different new effects" in str(exc),
                     "wrong duplicate refusal cause: " + str(exc))
                need(common.digest(after["projection"]) == applied_digest,
                     "duplicate changed applied projection")
                negatives.append({"scope_ref": scope, "case": "duplicate-after-apply", "reason": str(exc)})
            else:
                raise ValueError("native duplicate accepted in " + scope)
            cold_code = ("import json,sys,hashlib;sys.path.insert(0,sys.argv[1]);"
                         "from lab_runtime.store import Store;from lab_runtime.custody import content_rows;"
                         "d=Store(sys.argv[2],sys.argv[3]).replay(require_current=True);"
                         "print(json.dumps({r['version_ref']:hashlib.sha256(r['raw']).hexdigest() "
                         "for r in content_rows(d) if r['role']=='authored-target'}))")
            cold = subprocess.run([sys.executable, "-I", "-B", "-c", cold_code,
                                   str(RUNTIME), str(store.path), str(source_root)],
                                  capture_output=True, text=True, timeout=300)
            need(cold.returncode == 0, "cold native readback failed: " + cold.stderr[:500])
            cold_map = json.loads(cold.stdout)
            need(cold_map == {r["version_ref"]: r["body_binding"]["sha256"] for r in group},
                 "cold native readback digests differ")
            receipts[-1]["cold_readback_count"] = len(cold_map)
            receipts[-1]["body_sha256s"] = dict(sorted(cold_map.items()))
            need(not any(p.is_symlink() for p in store.path.rglob("*")),
                 "task-owned store entry linked")
    need(not owned.exists(), "disposable fixture root remains")
    return {"schema_version": "lab-T11-exact-230-bounded-native-fixture-result/v1",
            "matrix_binding": MATRIX, "runtime_manifest_sha256": MANIFEST_SHA,
            "runner_sha256": sha(Path(__file__).read_bytes()),
            "historical_source_commit": previous.HISTORICAL_COMMIT,
            "historical_snapshot_entries": entries,
            "scope_batches": len(receipts), "native_prepare_and_apply_effects": sum(r["member_count"] for r in receipts),
            "receipts": receipts, "negative_cases": negatives,
            "original_operational_routes": 0, "authority_effect": "none", "T11_complete": False,
            "claim_ceiling": "All 230 exact candidates applied only if this terminal fixture receipt passes; historical source and ephemeral local signatures do not prove original producer execution, current grants or original admission."}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
