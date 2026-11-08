#!/usr/bin/env python3
"""Build an isolated exact-230 native fixture runtime with <=64-target batches."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PREVIOUS = ROOT / "implementation/lab-runtime/local-host/t11-native-w06-six-0001"
PREVIOUS_MANIFEST_SHA = "e44501e5ba57158430744931fcb1549b9dc7156522eb941ca8a94ec96a280dd5"
OLD_PATH = "implementation/lab-runtime/local-host/t11-native-w06-six-0001/runtime"
NEW_PATH = "implementation/lab-runtime/local-host/t11-native-all-scopes-0002/runtime"
MATRIX = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T11/scope-routing-matrix-0002.json"
MATRIX_SHA = "f74f5c6a85e7eacb420785165fcb8257f2120337b31e482bf6bfb65125575628"
LEGACY = "lab.legacy-source-assertion.cav2-product-thesis"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(value, reason):
    if not value:
        raise ValueError(reason)


def build():
    matrix_raw = MATRIX.read_bytes()
    need(sha(matrix_raw) == MATRIX_SHA, "T11 matrix changed")
    routes = json.loads(matrix_raw)["routes"]
    need(len(routes) == 230, "T11 member set differs")
    by_scope = {}
    for route in routes:
        scope = route["body_scope_ref"]
        members = by_scope.setdefault(scope, {})
        version = route["version_ref"]
        need(version not in members and route["operation"] == "admit" and
             route["category"] == "artifact-instance", "T11 route differs")
        members[version] = {"carrier": route["carrier_ref"],
                            "sha256": route["body_binding"]["sha256"]}
    need(sorted(map(len, by_scope.values())) == [1, 1, 1, 1, 6, 220], "scope group sizes differ")
    batches = {scope: [dict(list(members.items())[start:start + 64])
                       for start in range(0, len(members), 64)]
               for scope, members in by_scope.items()}
    need(sorted(len(b) for b in batches[LEGACY]) == [28, 64, 64, 64] and
         all(len(b) <= 64 for groups in batches.values() for b in groups),
         "native batch partition differs")
    store_ids = {scope: "T11-exact-scope-" + str(index).zfill(2)
                 for index, scope in enumerate(sorted(by_scope), 1)}
    manifest_raw = (PREVIOUS / "RUNTIME-MANIFEST.json").read_bytes()
    need(sha(manifest_raw) == PREVIOUS_MANIFEST_SHA, "previous runtime manifest changed")
    previous = json.loads(manifest_raw)
    files = {}
    for row in previous["files"]:
        raw = (PREVIOUS / "runtime" / row["path"]).read_bytes()
        need(sha(raw) == row["sha256"], "previous runtime file changed: " + row["path"])
        files[row["path"]] = raw
    store = files["lab_runtime/store.py"].decode()
    old = """        t11_fixture_scope = (selected_scope_ref == 'scope:lab-runtime-local:w06-learning-0002-560605b8' and
            store_id == 'T11-W06-fixture' and
            owner_ref == 'principal:t11-local-fixture' and
            categories == ['artifact-instance'] and effects == ['admit'] and
            correction_profile_binding is None and authorized_domain_scope_refs is None)"""
    new = ("        t11_fixture_scope = (selected_scope_ref in " + repr(store_ids) + " and\n"
           "            store_id == " + repr(store_ids) + "[selected_scope_ref] and\n"
           "            owner_ref == 'principal:t11-local-fixture' and\n"
           "            categories == ['artifact-instance'] and effects == ['admit'] and\n"
           "            correction_profile_binding is None and authorized_domain_scope_refs is None)")
    need(store.count(old) == 1, "previous Store scope guard differs")
    files["lab_runtime/store.py"] = store.replace(old, new).encode()
    operations = files["lab_runtime/operations.py"].decode()
    start = operations.index("    if config['scope_ref'] == 'scope:lab-runtime-local:w06-learning-0002-560605b8':")
    end = operations.index("    if verify_base:", start)
    guard = """    if config['scope_ref'] in T11_BATCHES:
        # Closed <=64-member batches. Replay reaches this exact-member guard.
        batches = T11_BATCHES[config['scope_ref']]
        selected = next((batch for index, batch in enumerate(batches, 1)
                         if proposal['proposal_id'] ==
                         'T11-exact-scope-' + config['store_id'] + '-batch-' + str(index).zfill(2)), None)
        require(config['store_id'] == T11_STORE_IDS[config['scope_ref']] and
                config['owner_ref'] == 'principal:t11-local-fixture' and
                config['allowed_categories'] == ['artifact-instance'] and
                config['allowed_effects'] == ['admit'] and
                proposal['schema_version'] == ORIGINAL_PROPOSAL_VERSIONS[0] and
                proposal['schemas'] == {} and proposal['schema_contents'] == {} and
                selected is not None and
                len(proposal['targets']) == len(selected) and
                {t['version_ref'] for t in proposal['targets']} == set(selected),
                'T11 exact scope batch or fixture configuration differs')
        for t11 in proposal['targets']:
            exact = selected[t11['version_ref']]
            require(t11['category'] == 'artifact-instance' and t11['operation'] == 'admit' and
                    t11['carrier_ref'] == exact['carrier'] and
                    t11['decision_ref'] == 'decision:T11-fixture:' + byte_digest(t11['version_ref'].encode())[:16] and
                    t11['predecessor_ref'] is None and t11['contract'] is None and
                    t11['record']['node_id'] == t11['version_ref'].split('@', 1)[0] and
                    t11['record']['scope_ref'] == config['scope_ref'] and
                    t11['content']['byte_sha256'] == exact['sha256'],
                    'T11 exact member, scope or original bytes differ')
"""
    old_constant_start = operations.index("T11_W06_EXACT_MEMBERS = ")
    old_constant_end = operations.index("\n\ndef endpoint_kind(", old_constant_start)
    constants = ("T11_BATCHES = " + repr(batches) + "\n" +
                 "T11_STORE_IDS = " + repr(store_ids) + "\n")
    operations = operations[:old_constant_start] + constants + operations[old_constant_end:]
    operations = operations[:operations.index("    if config['scope_ref'] == 'scope:lab-runtime-local:w06-learning-0002-560605b8':")] + guard + operations[operations.index("    if verify_base:", operations.index("def prepare(")):]
    files["lab_runtime/operations.py"] = operations.encode()
    profile = json.loads(files["profile.json"])
    materials = profile["runtime_materials"]
    need(len(materials) == 45 and all(p.startswith(OLD_PATH + "/") for p in materials),
         "previous runtime material closure differs")
    profile["runtime_materials"] = [NEW_PATH + p[len(OLD_PATH):] for p in materials]
    files["profile.json"] = (json.dumps(profile, sort_keys=True, indent=2) + "\n").encode()
    runtime = HERE / "runtime"
    need(not runtime.exists(), "disjoint runtime already exists")
    runtime.mkdir()
    for path, raw in files.items():
        output = runtime / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(raw)
    manifest = {"schema_version": "lab-T11-exact-230-bounded-native-fixture-runtime/v1",
                "source_manifest_sha256": PREVIOUS_MANIFEST_SHA,
                "selected_matrix_sha256": MATRIX_SHA,
                "selected_scopes": {s: {"store_id": store_ids[s], "members": len(by_scope[s]),
                                        "batches": [len(b) for b in batches[s]]}
                                    for s in sorted(by_scope)},
                "copied_root": NEW_PATH,
                "files": [{"path": path, "sha256": sha(raw),
                           "previous_sha256": next(r["sha256"] for r in previous["files"] if r["path"] == path)}
                          for path, raw in sorted(files.items())]}
    (HERE / "RUNTIME-MANIFEST.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    return {"file_count": len(files), "changed": [r["path"] for r in manifest["files"]
                                                  if r["sha256"] != r["previous_sha256"]],
            "member_count": len(routes), "scope_count": len(by_scope),
            "manifest_sha256": sha((HERE / "RUNTIME-MANIFEST.json").read_bytes())}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
