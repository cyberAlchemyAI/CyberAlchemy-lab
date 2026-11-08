#!/usr/bin/env python3
"""Build a disjoint, exact-member W06 native fixture runtime."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PREVIOUS = ROOT / "implementation/lab-runtime/local-host/t11-native-one-member-0001"
OLD_PATH = "implementation/lab-runtime/local-host/t11-native-one-member-0001/runtime"
NEW_PATH = "implementation/lab-runtime/local-host/t11-native-w06-six-0001/runtime"
MATRIX = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T11/scope-routing-matrix-0002.json"
MATRIX_SHA = "f74f5c6a85e7eacb420785165fcb8257f2120337b31e482bf6bfb65125575628"
PREVIOUS_MANIFEST_SHA = "4be0c0976b4679cabcd0696590fe371c39919e7d681c759ee274755c76df0de9"
SCOPE = "scope:lab-runtime-local:w06-learning-0002-560605b8"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(value: bool, reason: str) -> None:
    if not value:
        raise ValueError(reason)


def build() -> dict:
    matrix_raw = MATRIX.read_bytes()
    need(sha(matrix_raw) == MATRIX_SHA, "selected matrix changed")
    routes = [r for r in json.loads(matrix_raw)["routes"] if r["body_scope_ref"] == SCOPE]
    need(len(routes) == 6 and len({r["version_ref"] for r in routes}) == 6, "W06 selection differs")
    need(all(r["operation"] == "admit" and r["category"] == "artifact-instance" for r in routes),
         "W06 effect differs")
    table = {r["version_ref"]: {"carrier": r["carrier_ref"], "sha256": r["body_binding"]["sha256"]}
             for r in routes}
    need(sha((PREVIOUS / "RUNTIME-MANIFEST.json").read_bytes()) == PREVIOUS_MANIFEST_SHA,
         "previous runtime manifest changed")
    previous = json.loads((PREVIOUS / "RUNTIME-MANIFEST.json").read_bytes())
    runtime = HERE / "runtime"
    need(not runtime.exists(), "disjoint runtime already exists")
    files = {}
    for row in previous["files"]:
        raw = (PREVIOUS / "runtime" / row["path"]).read_bytes()
        need(sha(raw) == row["sha256"], "previous runtime file changed: " + row["path"])
        files[row["path"]] = raw
    store = files["lab_runtime/store.py"].decode()
    old = """        t11_fixture_scope = (selected_scope_ref == 'scope:lab-integrated-model' and
            store_id == 'T11-catalog-generator-fixture' and
            owner_ref == 'principal:t11-local-fixture' and
            categories == ['artifact-instance'] and effects == ['admit'] and
            correction_profile_binding is None and authorized_domain_scope_refs is None)"""
    new = """        t11_fixture_scope = (selected_scope_ref == 'scope:lab-runtime-local:w06-learning-0002-560605b8' and
            store_id == 'T11-W06-fixture' and
            owner_ref == 'principal:t11-local-fixture' and
            categories == ['artifact-instance'] and effects == ['admit'] and
            correction_profile_binding is None and authorized_domain_scope_refs is None)"""
    need(store.count(old) == 1, "previous scope guard differs")
    files["lab_runtime/store.py"] = store.replace(old, new).encode()
    operations = files["lab_runtime/operations.py"].decode()
    start = operations.index("    if config['scope_ref'] == 'scope:lab-integrated-model':")
    end = operations.index("    if verify_base:", start)
    guard = """    if config['scope_ref'] == 'scope:lab-runtime-local:w06-learning-0002-560605b8':
        # Exact six selected fixture bodies. Replay reaches this same guard.
        require(config['store_id'] == 'T11-W06-fixture' and
                config['owner_ref'] == 'principal:t11-local-fixture' and
                config['allowed_categories'] == ['artifact-instance'] and
                config['allowed_effects'] == ['admit'] and
                len(proposal['targets']) == 1 and
                proposal['schema_version'] == ORIGINAL_PROPOSAL_VERSIONS[0] and
                proposal['schemas'] == {} and proposal['schema_contents'] == {},
                'T11 W06 fixture configuration or proposal differs')
        t11 = proposal['targets'][0]
        exact = T11_W06_EXACT_MEMBERS.get(t11['version_ref'])
        require(exact is not None and
                t11['category'] == 'artifact-instance' and t11['operation'] == 'admit' and
                t11['carrier_ref'] == exact['carrier'] and
                t11['decision_ref'] == 'decision:T11-W06-fixture:' + byte_digest(t11['version_ref'].encode())[:16] and
                t11['predecessor_ref'] is None and t11['contract'] is None and
                t11['record']['node_id'] == t11['version_ref'].split('@', 1)[0] and
                t11['record']['scope_ref'] == config['scope_ref'] and
                t11['content']['byte_sha256'] == exact['sha256'],
                'T11 W06 exact member, scope or original bytes differ')
"""
    constant = "T11_W06_EXACT_MEMBERS = " + repr(table) + "\n\n"
    operations = operations[:start] + guard + operations[end:]
    operations = operations.replace("\n\ndef endpoint_kind(", "\n\n" + constant + "def endpoint_kind(", 1)
    files["lab_runtime/operations.py"] = operations.encode()
    profile = json.loads(files["profile.json"])
    materials = profile["runtime_materials"]
    need(len(materials) == 45 and all(p.startswith(OLD_PATH + "/") for p in materials),
         "previous runtime material closure differs")
    profile["runtime_materials"] = [NEW_PATH + p[len(OLD_PATH):] for p in materials]
    files["profile.json"] = (json.dumps(profile, sort_keys=True, indent=2) + "\n").encode()
    runtime.mkdir()
    for path, raw in files.items():
        output = runtime / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(raw)
    manifest = {"schema_version": "lab-T11-W06-six-native-fixture-runtime/v1",
                "source_manifest_sha256": PREVIOUS_MANIFEST_SHA,
                "selected_matrix_sha256": MATRIX_SHA,
                "selected_scope_ref": SCOPE,
                "selected_members": table,
                "copied_root": NEW_PATH,
                "files": [{"path": path, "sha256": sha(raw),
                           "previous_sha256": next(r["sha256"] for r in previous["files"] if r["path"] == path)}
                          for path, raw in sorted(files.items())]}
    (HERE / "RUNTIME-MANIFEST.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    return {"file_count": len(files), "changed": [r["path"] for r in manifest["files"]
                                                  if r["sha256"] != r["previous_sha256"]],
            "member_count": len(table), "manifest_sha256": sha((HERE / "RUNTIME-MANIFEST.json").read_bytes())}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
