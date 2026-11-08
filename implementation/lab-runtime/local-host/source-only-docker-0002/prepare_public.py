"""Construct a public-only Source development cut; never import or run Source.

The five historical private archives are filtered by exact path *before* any
input-byte read. All generated files remain inert until separate review.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
INTERFACE = "product/lab/release-candidates/v1/interface"
OLD_FAMILY = INTERFACE + "/legacy-session-fixture-source-v1-action-0148"
NEW_FAMILY = INTERFACE + "/docker-source-20261020-0001"
OLD_ID = "R03-legacy-session-fixture-0257"
NEW_ID = "R03-docker-source-20261020-0001"
OLD_AUTH = "docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json"
NEW_AUTH = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/source-only-dev-20261020/authorization.json"
OLD_MANIFEST_SHA = "f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2"
OLD_ROLE_SHA = {
    "__init__.py": "a3e7a2b9ec2c69a93c8ace06aa927816972435789274c10ffe8e0f32a542e6ed",
    "base.py": "b4b0e65b2d547ffc57a4345094fbdcf467a588cb2c9bda4bd1d01c6046037195",
    "build.py": "bedfe45b3d5f7c8dcc8a7c480f92d896afa9d665975acc459bd22e142455d96b",
    "cold.py": "5dbdad7f2511168d65fe73ba34a8d677ac64d4c98c171e5044f6f1e4685a3ee3",
    "records.py": "083134095603c6f070dbffcb28f6de9e8d4db73a8dbe27b692656c44f862e7ea",
}
EXPECTED_ID_COUNTS = {"__init__.py": 0, "base.py": 0, "build.py": 3, "cold.py": 0, "records.py": 7}
EXCLUDED = frozenset({
    INTERFACE + "/current-participation-v2/packages/0001/branch.snapshot",
    INTERFACE + "/current-participation-v3/packages/0001/branch.snapshot",
    INTERFACE + "/current-participation-v4/packages/0001/branch.snapshot",
    INTERFACE + "/custody-participation-v1/packages/0001/branch.snapshot",
    INTERFACE + "/session-participation-v2/packages/0001/branch.snapshot",
})
CAPTURE_CLOSURE_SHA = "b4c5ea62f32420501987ca13883d84a3bfb06503f85863a98eabc37b63229a87"
SOURCE_FIXED = {
    INTERFACE + "/custody-correction-v4/loader.py": "f1953bf08d36756810fbc7ec051df5d0e362f745e84644223b9dddd0df1b13ef",
    INTERFACE + "/custody-correction-v4/reader_adapter.py": "6f57bf712f09ce162754cd5515432b3f99cc2191b021b271987e37bb19cb3f41",
    INTERFACE + "/custody-correction-v4/pins.json": "d59fc534f60483fe9df93b2e6d45431d00ccec082332fbf4e76a91b0944e6b4d",
    INTERFACE + "/custody-correction-v4/engine-manifest.json": "329403eb89eb989a834cba02c7fb09f920d328e8ecdca9a0880660b1e97cbcaa",
    INTERFACE + "/current-participation-v5/episode-contract.json": "73c2afe2663bb80da0cf3a8f52a2951346a47dcefb34c8c04ac05ca1e37f4559",
    INTERFACE + "/current-participation-v5/packages/0001/period.json": "5d2184e3491509b6c8d15939d97c6f95609d5277c61bb8f3f0bbd911ff3f35e3",
}
FIXTURES = (
    ("principal", "v1", "record.json"), ("principal-reference", "v1", "record.json"),
    ("intent", "v1", "record.json"), ("goal", "v1", "goal.json"),
    ("work", "v1", "record.json"), ("agent-profile", "v1", "record.json"),
    ("agent-assignment", "v1", "record.json"),
    ("coordination-context", "v2", "product-project-goal.json"),
    ("context", "v1", "record.json"), ("implementation", "v1", "record.json"),
    ("agent-capability", "v1", "record.json"),
)
START = "2026-10-20T08:20:00+00:00"
END = "2026-10-21T08:20:00+00:00"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def binding(name: str, raw: bytes) -> dict:
    return {"path": name, "sha256": sha(raw)}


def valid_name(name: str) -> None:
    require(type(name) is str and name and not name.startswith("/") and "\\" not in name and
            "//" not in name and all(p not in ("", ".", "..") for p in name.split("/")),
            "unsafe public input path")


def public_bytes(name: str, digest: str | None) -> bytes:
    valid_name(name)
    require(name not in EXCLUDED and not name.endswith("/branch.snapshot") and
            not any(marker in name.lower() for marker in (".pem", ".key", "private", "secret", "credential")),
            "private or unknown archive input refused")
    path = REPO / name
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(REPO) and
            all(not p.is_symlink() for p in path.parents if p != REPO),
            "public input absent or symlinked: " + name)
    raw = path.read_bytes()
    require(digest is None or sha(raw) == digest, "public input changed: " + name)
    return raw


def project_role(name: str, raw: bytes) -> bytes:
    require(name in OLD_ROLE_SHA and sha(raw) == OLD_ROLE_SHA[name], "exact Source role preimage required")
    text = raw.decode("utf-8")
    require(text.count(OLD_ID) == EXPECTED_ID_COUNTS[name], "historical identity occurrence vector differs")
    text = text.replace(OLD_ID, NEW_ID)
    if name == "base.py":
        for old, new in (("_cal_legacy_session_fixture_engine_0257", "_cal_docker_source_engine_20261020_0001"),
                         ("_cal_legacy_session_fixture_bridge_0257", "_cal_docker_source_bridge_20261020_0001")):
            require(text.count(old) == 1, "original module alias occurrence differs")
            text = text.replace(old, new)
    if name in ("base.py", "records.py"):
        require(text.count(OLD_AUTH) == 1, "exact old authorization selector required once")
        text = text.replace(OLD_AUTH, NEW_AUTH)
    else:
        require(OLD_AUTH not in text, "unexpected authorization occurrence")
    result = text.encode("utf-8")
    compile(result, NEW_FAMILY + "/" + name, "exec", optimize=0)
    compile(result, NEW_FAMILY + "/" + name, "exec", optimize=2)
    require(OLD_ID.encode() not in result and OLD_AUTH.encode() not in result,
            "historical identity or authorization remains")
    return result


def construct() -> tuple[dict, dict[str, bytes]]:
    old_raw = public_bytes(OLD_FAMILY + "/source-manifest.json", OLD_MANIFEST_SHA)
    old = json.loads(old_raw)
    require(type(old.get("files")) is list and len(old["files"]) == 896,
            "historical Source input inventory differs")
    paths = [row["path"] for row in old["files"]]
    require(len(set(paths)) == 896 and set(paths) & EXCLUDED == EXCLUDED and
            {x for x in paths if x.endswith("/branch.snapshot")} == EXCLUDED,
            "exact five protected archive exclusions differ")
    require(len([row for row in old["files"] if row["path"] not in EXCLUDED]) == 891,
            "historical public metadata count differs")
    closure_raw = (HERE / "capture-closure.json").read_bytes()
    require(sha(closure_raw) == CAPTURE_CLOSURE_SHA, "frozen read-only capture proof differs")
    closure = json.loads(closure_raw)
    require(closure["result"] == "PASS" and closure["source_effect"] == "NOT_RUN" and
            closure["captured_materials"] == 788 and
            len(closure["epoch_inventory"]["admission_bundles"]) == 6 and
            len(closure["epoch_inventory"]["recorded_decisions"]) == 79,
            "read-only captured Source closure differs")
    selected: dict[str, dict] = {}
    reasons: dict[str, list[str]] = {}
    def add(row: dict, reason: str) -> None:
        require(type(row) is dict and set(row) == {"path", "sha256"}, "closed public binding")
        name, digest = row["path"], row["sha256"]
        public_bytes(name, digest)
        if name in selected:
            require(selected[name] == row, "conflicting public source binding: " + name)
        else:
            selected[name] = row
        reasons.setdefault(name, []).append(reason)
    def add_current(name: str, reason: str) -> None:
        add(binding(name, public_bytes(name, None)), reason)

    for row in closure["captured_material_bindings"]:
        add(row, "observed_read_only_source_capture")
    for name in closure["epoch_inventory"]["admission_bundles"] + closure["epoch_inventory"]["recorded_decisions"]:
        add_current(name, "exact_epoch_inventory_name")
    for name, digest in SOURCE_FIXED.items():
        add({"path": name, "sha256": digest}, "fixed_source_import_or_counterevidence")
    engine_path = INTERFACE + "/custody-correction-v4/engine-manifest.json"
    engine = json.loads(public_bytes(engine_path, SOURCE_FIXED[engine_path]))
    require(len(engine["files"]) == 45, "engine 45-file closure differs")
    for row in engine["files"]:
        add(row, "engine_manifest_file")
    add(engine["parent_binding"], "engine_parent_manifest")
    parent = json.loads(public_bytes(engine["parent_binding"]["path"],
                                     engine["parent_binding"]["sha256"]))
    require(len(parent["files"]) == 25, "parent engine 25-file closure differs")
    for row in parent["files"]:
        add(row, "parent_engine_manifest_file")
    for key in ("profile_binding", "mapping_binding", "correction_profile_binding"):
        add(engine[key], "engine_" + key)
    correction_binding = engine["correction_profile_binding"]
    correction = json.loads(public_bytes(correction_binding["path"], correction_binding["sha256"]))
    require(len(correction["member_bindings"]) == 10, "correction review member count differs")
    for key in ("review_manifest_binding", "source_proof_binding", "parent_engine_binding"):
        add(correction[key], "correction_" + key)
    for member_binding in correction["member_bindings"]:
        add(member_binding, "correction_review_member")
        member = json.loads(public_bytes(member_binding["path"], member_binding["sha256"]))
        for key in ("record_binding", "original_source_binding", "schema_binding"):
            add(member[key], "correction_member_" + key)
        signature = member["signature_binding"]
        add({"path": signature["ref"], "sha256": signature["sha256"]}, "correction_signature_witness")
        require(len(member["endpoint_witnesses"]) == 2, "correction endpoint witnesses differ")
        for witness in member["endpoint_witnesses"]:
            add(witness["source_binding"], "correction_endpoint_source")
            add(witness["admission_overlay"]["binding"], "correction_admission_overlay")
    for kind, version, filename in FIXTURES:
        add_current(f"authority/artifact-types/{kind}/{version}/fixtures/valid/{filename}",
                    "source_records_fixture")
    add_current("authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json",
                "source_records_typed_relation_fixture")
    public = [selected[name] for name in sorted(selected)]

    start, end = datetime.fromisoformat(START), datetime.fromisoformat(END)
    require(start.utcoffset() == timedelta(0) and end - start == timedelta(hours=24),
            "selected fresh UTC period differs")
    old_episode = json.loads(public_bytes(OLD_FAMILY + "/episode-contract.json", "bc6acaa6022791ea102ced5b1dfc8621403f8e5e557a937765e187a90d887055"))
    previous_period = selected[INTERFACE + "/current-participation-v5/packages/0001/period.json"]
    require(old_episode["expires_at"] < START and old_episode["old_episode_period_binding"] == previous_period,
            "expired historical episode/period counterevidence differs")
    auth = {
        "schema_version": "lab-source-only-development-authorization/v1",
        "authority_effect": "none", "actual_owner_outcome": None,
        "source": "User request for a locally runnable product on this WSL host",
        "scope": "One separately owned disposable Source-only Docker development cut and cold replay",
        "excluded_effects": ["historical protected archive reads", "canonical admission", "existing store or signer reuse",
                             "Reader/Mapper/Context execution", "protected host qualification", "external publication"],
        "claim_ceiling": "Development fixture authorization only; no owner disposition or historical Source8 grant.",
    }
    auth_raw = encoded(auth)
    episode = dict(old_episode)
    episode.update({"episode_ref": "protocol:" + NEW_ID,
                    "principal_ref": "principal:" + NEW_ID,
                    "assignment_version_ref": "agent-assignment:" + NEW_ID + "@1.0.0-candidate.1",
                    "period_ref": "protocol:" + NEW_ID + "-period/v1",
                    "not_before": START, "expires_at": END,
                    "authorization_binding": binding(NEW_AUTH, auth_raw),
                    "purpose": "Fresh disposable Docker Source-only development episode; no historical Assignment renewal.",
                    "scope": "One owned development source/store/signer and cold replay; no protected host or canonical effect.",
                    "actual_owner_outcome": None, "authority_effect": "none",
                    "original_Assignment_renewed": False, "original_signer_restored": False,
                    "Session_memory_rehydrated": False})
    episode_raw = encoded(episode)
    generated = {NEW_AUTH: auth_raw, NEW_FAMILY + "/episode-contract.json": episode_raw}
    for name, digest in OLD_ROLE_SHA.items():
        generated[NEW_FAMILY + "/" + name] = project_role(name, public_bytes(OLD_FAMILY + "/" + name, digest))
    additions = [binding(name, raw) for name, raw in generated.items()]
    rows = sorted(public + additions, key=lambda row: row["path"])
    require(len(rows) == len({x["path"] for x in rows}) and len(rows) == len(public) + len(additions),
            "closed public Source source row set differs")
    manifest = dict(old)
    manifest.update(files=rows,
                    fixed_new_episode_binding=binding(NEW_FAMILY + "/episode-contract.json", episode_raw),
                    implementation_code_binding=binding(NEW_FAMILY + "/cold.py", generated[NEW_FAMILY + "/cold.py"]),
                    implementation_entrypoint_ref=NEW_FAMILY + "/cold.py#open_source",
                    qualification=False, authority_effect="none", actual_owner_outcome=None)
    manifest_raw = encoded(manifest)
    generated[NEW_FAMILY + "/source-manifest.json"] = manifest_raw
    plan = {"schema_version": "lab-source-only-docker-public-cut/v1-inactive",
            "effect": "NOT_RUN", "private_archive_bodies_read": False,
            "old_manifest": binding(OLD_FAMILY + "/source-manifest.json", old_raw),
            "excluded_historical_archive_paths": sorted(EXCLUDED),
            "historical_inventory_rows": 896, "public_selected_rows": len(public),
            "public_provenance": [{"path": name, "reasons": sorted(set(reasons[name]))} for name in sorted(reasons)],
            "capture_closure_sha256": CAPTURE_CLOSURE_SHA,
            "new_generated_rows": len(generated),
            "source_manifest": binding(NEW_FAMILY + "/source-manifest.json", manifest_raw),
            "new_episode": binding(NEW_FAMILY + "/episode-contract.json", episode_raw),
            "new_authorization": binding(NEW_AUTH, auth_raw),
            "new_family": NEW_FAMILY, "identity_prefix": NEW_ID,
            "not_before": START, "expires_at": END,
            "public_inputs": public, "generated_bindings": [binding(n, r) for n, r in sorted(generated.items())],
            "claim_ceiling": "Exact public-only proposed Source input cut and role-byte adapter; no Source build or cold replay effect."}
    return plan, generated


if __name__ == "__main__":
    plan, generated = construct()
    target = HERE / "generated"
    require(not target.exists(), "generated candidate already exists")
    target.mkdir(mode=0o700)
    for name, raw in generated.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    (HERE / "public-cut.json").write_bytes(encoded(plan))
    print(json.dumps({"result": "PROPOSED_PUBLIC_CUT", "source_manifest_sha256": plan["source_manifest"]["sha256"],
                      "rows": len(plan["public_inputs"]), "effects": "NOT_RUN"}, sort_keys=True))
