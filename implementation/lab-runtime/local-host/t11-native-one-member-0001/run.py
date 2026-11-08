#!/usr/bin/env python3
"""Disposable native Store.apply for one exact T11 candidate under fixture authority."""

from __future__ import annotations

import copy
import hashlib
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNTIME = HERE / "runtime"
MANIFEST_SHA = "4be0c0976b4679cabcd0696590fe371c39919e7d681c759ee274755c76df0de9"
MATRIX_PATH = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T11/scope-routing-matrix-0002.json"
MATRIX_SHA = "f74f5c6a85e7eacb420785165fcb8257f2120337b31e482bf6bfb65125575628"
MEMBER = "protocol:C10:catalog-generator"
SCOPE = "scope:lab-integrated-model"
VERSION = "implementation:lab-candidate-catalog-generator@S02-final-candidate.0276"
BODY_SHA = "f5d5b1e5fd82060105c6428c4ca8a545a32d638ad44052d9ce1111a6d06b3b77"
HISTORICAL_COMMIT = "19d860e719d6d65c05bff74b1c7547b3d48defcc"
SNAPSHOT_PATHS = (
    "authority",
    "tooling/schemas",
    "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline",
    "product/lab/release-candidates/v1/interface/custody-correction-v4/runtime",
    "product/lab/release-candidates/v1/interface/coupling/engine/endpoint-mapping.json",
    "implementation/lab-runtime/v1/lab.py",
    "implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json",
    "docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission",
    "docs/decisions/0072-project-state-bootstrap-admission",
    "docs/decisions/0073-first-governed-agent-work-episode-admission",
    "docs/decisions/0074-governance-transaction-surface-admission",
    "docs/decisions/0075-lab-operational-runtime-v1-admission",
    "ontology-lifecycle/runtime-candidates/cal-ontology-graph-read-model/v1/README.md",
)


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_pinned(path, digest):
    need(path.is_file() and not path.is_symlink() and
         all(not parent.is_symlink() for parent in path.parents if parent != Path('/')),
         "selected file missing or linked")
    raw = path.read_bytes()
    need(sha(raw) == digest, "selected bytes changed: " + str(path))
    return raw


def selected_runtime():
    manifest = json.loads(read_pinned(HERE / "RUNTIME-MANIFEST.json", MANIFEST_SHA))
    need(manifest["schema_version"] == "lab-T11-one-member-native-fixture-runtime/v1" and
         manifest["authority_effect"] == "none" and len(manifest["files"]) == 45 and
         sum(row["changed"] for row in manifest["files"]) == 3 and
         {row["path"] for row in manifest["files"] if row["changed"]} ==
         {"lab_runtime/store.py", "lab_runtime/operations.py", "profile.json"},
         "runtime recut closure differs")
    actual = {p.relative_to(RUNTIME).as_posix() for p in RUNTIME.rglob('*') if p.is_file()}
    need(actual == {row["path"] for row in manifest["files"]}, "runtime file set differs")
    for row in manifest["files"]:
        read_pinned(RUNTIME / row["path"], row["sha256"])
        original = read_pinned(ROOT / manifest["original_root"] / row["path"], row["original_sha256"])
        if not row["changed"]:
            need(sha(original) == row["sha256"], "unchanged runtime copy differs")
    return manifest


def selected_body():
    matrix = json.loads(read_pinned(ROOT / MATRIX_PATH, MATRIX_SHA))
    rows = [row for row in matrix["routes"] if row["member_ref"] == MEMBER]
    need(len(rows) == 1, "selected T11 member differs")
    route = rows[0]
    need(route["body_scope_ref"] == SCOPE and route["version_ref"] == VERSION and
         route["operation"] == "admit" and route["category"] == "artifact-instance" and
         route["carrier_ref"] == "cal.artifact-type.implementation/v1" and
         route["body_binding"]["sha256"] == BODY_SHA and
         route["correction_eligibility"]["eligible"] is False and
         route["historical_producer_execution_proven"] is False,
         "T11 candidate route differs")
    raw = read_pinned(ROOT / route["body_binding"]["path"], BODY_SHA)
    body = json.loads(raw)
    schema = json.loads(read_pinned(ROOT / route["schema_binding"]["path"],
                                    route["schema_binding"]["sha256"]))
    descriptor = json.loads(read_pinned(ROOT / route["descriptor_binding"]["path"],
                                        route["descriptor_binding"]["sha256"]))
    from jsonschema import Draft202012Validator
    Draft202012Validator(schema).validate(body)
    need(body["node_id"] == VERSION.split('@', 1)[0] and body["scope_ref"] == SCOPE and
         body["authority_effect"] == "none" and descriptor["artifact_type_ref"] == route["carrier_ref"],
         "selected body or carrier differs")
    return route, raw, body


def historical_snapshot(destination):
    """Extract only committed historical fixture inputs into a disposable root."""
    need(not destination.exists(), "historical fixture root already exists")
    command = ["git", "archive", "--format=tar", HISTORICAL_COMMIT, "--", *SNAPSHOT_PATHS]
    process = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=90)
    need(process.returncode == 0, "historical fixture archive unavailable: " +
         process.stderr.decode(errors="replace")[:400])
    need(len(process.stdout) < 128 * 1024 * 1024, "historical fixture archive too large")
    destination.mkdir(mode=0o700)
    seen = set()
    with tarfile.open(fileobj=io.BytesIO(process.stdout), mode="r:") as archive:
        for member in archive:
            relative = Path(member.name)
            need(not relative.is_absolute() and ".." not in relative.parts and
                 relative.as_posix() not in seen and (member.isfile() or member.isdir()),
                 "unsafe historical fixture archive entry")
            seen.add(relative.as_posix())
            target = destination / relative
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as output:
                    source = archive.extractfile(member)
                    need(source is not None, "historical fixture member missing")
                    output.write(source.read())
    need(sha((destination / "authority/project-state-transitions/current.json").read_bytes()) ==
         "8ba8ee25ccbf12721d800c693120a3452ddf1ec4427c6fdf1e0655beae31bc12",
         "historical D75 lookup differs")
    manifest = selected_runtime()
    for row in manifest["files"]:
        relative = Path(manifest["copied_root"]) / row["path"]
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output:
            output.write(read_pinned(RUNTIME / row["path"], row["sha256"]))
    profile = json.loads((destination / manifest["copied_root"] / "profile.json").read_bytes())
    need(set(profile["runtime_materials"]) ==
         {str(Path(manifest["copied_root"]) / row["path"]) for row in manifest["files"]},
         "source snapshot misses fixture executable closure")
    return len(seen)


def run():
    manifest = selected_runtime()
    route, raw, body = selected_body()
    sys.path.insert(0, str(RUNTIME))
    store_module = importlib.import_module("lab_runtime.store")
    custody = importlib.import_module("lab_runtime.custody")
    operations = importlib.import_module("lab_runtime.operations")
    common = importlib.import_module("lab_runtime.common")
    need(all(Path(m.__file__).resolve().is_relative_to(RUNTIME.resolve())
             for m in (store_module, custody, operations, common)), "runtime module origin differs")
    negatives = []
    with tempfile.TemporaryDirectory(prefix="cal-T11-native-one-member-") as temp:
        owned = Path(temp)
        source_root = owned / "historical-source"
        historical_files = historical_snapshot(source_root)
        store_module.keygen(owned / "fixture-owner.pem", owned / "fixture-owner.pub")
        store = store_module.Store(owned / "store", source_root)
        profile = common.load(RUNTIME / "profile.json")
        store.initialize(profile, "T11-catalog-generator-fixture", "principal:t11-local-fixture",
                         (owned / "fixture-owner.pub").read_text().strip(),
                         allowed_categories=["artifact-instance"], allowed_effects=["admit"],
                         selected_scope_ref=SCOPE)
        before = store.replay(require_current=True)
        config = before["config"]
        proposal = {"schema_version": "lab-runtime-proposal/v1",
                    "proposal_id": "T11-catalog-generator-exact-fixture",
                    "expected_head": before["head"]["transaction_digest"],
                    "source_snapshot_digest": config["source_snapshot_digest"],
                    "scope_ref": SCOPE, "policy_ref": config["policy_ref"],
                    "challenge_route": config["challenge_route"], "schemas": {},
                    "targets": [{"category": "artifact-instance", "operation": "admit",
                                 "version_ref": VERSION, "carrier_ref": route["carrier_ref"],
                                 "record": body, "predecessor_ref": None,
                                 "decision_ref": "decision:T11-catalog-generator-fixture",
                                 "contract": None}]}
        proposal = custody.with_originals(proposal, {VERSION: raw}, {})
        preimage = common.digest(before["projection"])

        def refusal(label, change, expected):
            candidate = copy.deepcopy(proposal)
            change(candidate)
            try:
                operations.prepare(before["projection"], candidate,
                                   before["head"]["transaction_digest"], config)
            except Exception as exc:
                reason = str(exc)
                need(expected in reason, "wrong refusal cause " + label + ": " + reason)
                need(common.digest(before["projection"]) == preimage,
                     "negative changed original projection")
                negatives.append({"case": label, "reason": reason})
            else:
                raise ValueError("unreviewed T11 candidate accepted: " + label)

        refusal("wrong-scope", lambda p: p.__setitem__("scope_ref", "scope:other"),
                "proposal outside provisioned scope")
        refusal("stale-head", lambda p: p.__setitem__("expected_head", "0" * 64),
                "stale expected HEAD")
        refusal("same-domain-other-version",
                lambda p: p["targets"][0].__setitem__("version_ref", VERSION + "-other"),
                "T11 exact member")
        refusal("changed-original-body",
                lambda p: p["targets"][0]["content"].__setitem__("byte_sha256", "0" * 64),
                "original content size or byte digest differs")
        post, cores = operations.prepare(before["projection"], proposal,
                                         before["head"]["transaction_digest"], config)
        need(len(cores) == 1 and post["subjects"][VERSION]["record"] == body and
             post["subjects"][VERSION]["effective_state"] == "local-admitted-current" and
             post["subjects"][VERSION]["source"]["sha256"] == BODY_SHA and
             common.digest(before["projection"]) == preimage,
             "native prepare effect or preimage differs")
        approval = store.authorize(proposal, owned / "fixture-owner.pem")
        application = store.apply(proposal, approval)
        after = store.replay(require_current=True)
        duplicate = copy.deepcopy(proposal)
        duplicate["proposal_id"] = "T11-catalog-generator-duplicate-fixture"
        duplicate["expected_head"] = after["head"]["transaction_digest"]
        duplicate_preimage = common.digest(after["projection"])
        try:
            operations.prepare(after["projection"], duplicate,
                               after["head"]["transaction_digest"], after["config"])
        except Exception as exc:
            reason = str(exc)
            need("a recorded Decision identity cannot authorize different new effects" in reason,
                 "wrong duplicate refusal cause: " + reason)
            need(common.digest(after["projection"]) == duplicate_preimage,
                 "duplicate changed applied projection")
            negatives.append({"case": "duplicate-after-apply", "reason": reason})
        else:
            raise ValueError("duplicate T11 member accepted after native apply")
        recovered = custody.original_bytes(store, VERSION, after["head"]["transaction_digest"])
        need(recovered == raw and after["projection"]["subjects"][VERSION]["record"] == body and
             after["projection"]["subjects"][VERSION]["effective_state"] == "local-admitted-current" and
             after["head"]["sequence"] == before["head"]["sequence"] + 1,
             "native apply/readback differs")
        cold_code = ("import json,sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);"
                     "from lab_runtime.store import Store;from lab_runtime.custody import original_bytes;"
                     "s=Store(sys.argv[2],sys.argv[3]);d=s.replay(require_current=True);"
                     "raw=original_bytes(s,sys.argv[4],d['head']['transaction_digest']);"
                     "print(json.dumps({'head':d['head']['transaction_digest'],'body_sha256':__import__('hashlib').sha256(raw).hexdigest(),"
                     "'state':d['projection']['subjects'][sys.argv[4]]['effective_state']}))")
        cold = subprocess.run([sys.executable, "-I", "-B", "-c", cold_code,
                               str(RUNTIME), str(store.path), str(source_root), VERSION],
                              capture_output=True, text=True, timeout=120)
        need(cold.returncode == 0, "cold native readback failed: " + cold.stderr[:500])
        cold_result = json.loads(cold.stdout)
        need(cold_result == {"head": after["head"]["transaction_digest"],
                             "body_sha256": BODY_SHA, "state": "local-admitted-current"},
             "cold native readback differs")
        need(all(not p.is_symlink() for p in store.path.rglob('*')), "owned store entry linked")
        receipt = {"schema_version": "lab-T11-one-member-native-fixture-result/v1",
                   "member_ref": MEMBER, "route_binding": route["body_binding"],
                   "historical_candidate_decision_ref": route["decision_ref"],
                   "fixture_decision_ref": proposal["targets"][0]["decision_ref"],
                   "runtime_manifest_sha256": MANIFEST_SHA,
                   "historical_source_commit": HISTORICAL_COMMIT,
                   "historical_snapshot_entries": historical_files,
                   "runner_sha256": sha(Path(__file__).read_bytes()),
                   "preimage_projection_digest": preimage,
                   "prepared_postimage_digest": common.digest(post),
                   "applied_projection_digest": common.digest(after["projection"]),
                   "before_head": before["head"]["transaction_digest"],
                   "after_head": after["head"]["transaction_digest"],
                   "application_idempotent": application.get("idempotent", False),
                   "exact_original_body_sha256": BODY_SHA,
                   "cold_readback": cold_result, "negative_cases": negatives,
                   "local_fixture_effects": 1, "original_operational_routes": 0,
                   "authority_effect": "none", "T11_complete": False,
                   "claim_ceiling": "One exact selected T11 candidate applied in a disposable native fixture store; no current domain grant, producer execution proof, original authority or other 229 routes."}
    need(not owned.exists(), "owned fixture store not removed")
    selected_runtime()
    selected_body()
    return receipt


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
