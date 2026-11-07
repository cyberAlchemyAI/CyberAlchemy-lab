"""Host-owned native target/core construction and immutable review input staging.

This module is embedded by a qualified host successor. It cannot replace the
host's authentication, routing verifier, independent review or owner ingress.
"""
import copy
from pathlib import Path

from jsonschema import Draft202012Validator
from .exact import binding, bound, decode, encode, read, require, sha, shape, write_package
from .package import privacy

COHORT_FIELDS = ("schema_version", "cohort_id", "revision", "source_cut", "source_profile_binding", "native_mechanics_bindings",
                 "scope_ref", "ordered_targets", "schema_bindings", "evidence_bindings", "owner_route_selections",
                 "examples_binding", "consequences_recipe_binding", "privacy_review_binding", "authority_effect")
TARGET_FIELDS = ("target_id", "category", "operation", "artifact_header", "predecessor_ref", "content_binding",
                 "candidate_contract_binding", "decision_ref", "native_contract", "requested_effect", "dependency_refs")
HEADER_FIELDS = ("scope_ref", "identity_ref", "version_ref", "carrier_ref", "byte_sha256")


def native_controls(view, cohort, input_root, current_cut):
    """Use the exact selected host helpers; independently simulate the full set."""
    shape(cohort, COHORT_FIELDS)
    require(cohort["authority_effect"] == "none" and cohort["schema_version"] == "cal.define.review-cohort/v1", "unsupported-cohort", exit_code=4)
    require(cohort["scope_ref"] == view.data["config"]["scope_ref"], "cohort-scope-mismatch")
    require(cohort["source_cut"] == current_cut, "stale-review-cut", exit_code=3)
    require(1 <= len(cohort["ordered_targets"]) <= 24, "cohort-budget")
    # The owning host must guard the selected mechanics and current source before and after this pure function.
    targets, cores, inputs, metadata, originals = [], [], {}, {}, {}
    versions, decisions, ids = set(), set(), set()
    native = view.handle
    require(cohort["source_profile_binding"]["sha256"] == current_cut["source_profile_sha256"], "review-profile-mismatch", exit_code=3)
    bound(input_root, cohort["source_profile_binding"])
    schemas, schema_bytes = {}, {}
    for b in cohort["schema_bindings"]:
        raw = bound(input_root, b);path = "runtime/schemas/" + Path(b["path"]).name
        require(path not in schemas, "duplicate-review-schema")
        schemas[path], schema_bytes[path] = decode(raw), raw
    for module in [native.common, native.operations, *([native.custody] if view.selected["name"] == "custody-participation" else [])]:
        actual = read(module.__file__)
        selected = [b for b in cohort["native_mechanics_bindings"] if b["sha256"] == sha(actual) and b["bytes"] == len(actual)]
        require(len(selected) == 1 and bound(input_root, selected[0]) == actual, "native-mechanics-unselected", exit_code=3)
    for row in cohort["ordered_targets"]:
        shape(row, TARGET_FIELDS);header = row["artifact_header"];shape(header, HEADER_FIELDS)
        require(row["target_id"] not in ids and header["version_ref"] not in versions and row["decision_ref"] not in decisions, "duplicate-review-target")
        ids.add(row["target_id"]);versions.add(header["version_ref"]);decisions.add(row["decision_ref"])
        require(header["scope_ref"] == cohort["scope_ref"], "target-scope-mismatch")
        require(all(d in {t["artifact_header"]["version_ref"] for t in cohort["ordered_targets"]} or d in view.data["projection"]["subjects"] for d in row["dependency_refs"]), "missing-target-dependency")
        withdrawal = row["operation"] == "withdraw"
        if withdrawal:
            require(row["content_binding"] is None and row["predecessor_ref"] == header, "invalid-withdrawal")
            raw, record = None, None
        else:
            raw = bound(input_root, row["content_binding"]);privacy(raw);record = decode(raw, source=True)
            require(sha(raw) == header["byte_sha256"], "target-body-mismatch")
            contract = view.data["projection"]["contracts"].get(header["carrier_ref"])
            require(contract is not None, "review-carrier-unavailable", exit_code=3)
            identity_field = contract["artifact"].get("instance_contract", {}).get("identity_field")
            identity = record["artifact_type_ref"].rsplit("/", 1)[0] if row["category"] == "artifact-type" else native.common.identity(record, identity_field)
            require(identity == header["identity_ref"], "candidate-identity-mismatch")
            originals[header["version_ref"]] = raw
        predecessor = row["predecessor_ref"]
        if predecessor is not None:
            shape(predecessor, HEADER_FIELDS)
            selected = view.data["projection"]["subjects"].get(predecessor["version_ref"])
            require(selected is not None and selected["identity"] == predecessor["identity_ref"] and selected["effective_state"] in ("admitted-current", "local-admitted-current"), "predecessor-not-current")
            require(selected["source"]["sha256"] == predecessor["byte_sha256"], "predecessor-byte-mismatch")
        target = {"category": row["category"], "operation": row["operation"], "version_ref": header["version_ref"],
                  "carrier_ref": header["carrier_ref"], "record": record, "predecessor_ref": predecessor["version_ref"] if predecessor else None,
                  "decision_ref": row["decision_ref"], "contract": row["native_contract"]}
        if view.selected["name"] == "custody-participation":
            target["content"] = None if withdrawal else native.custody.content_entry(raw)
        core = {"decision_ref": row["decision_ref"], "category": row["category"], "operation": row["operation"],
                "version_ref": header["version_ref"], "target_digest": native.common.digest(target)}
        targets.append(target);cores.append(core)
        number = str(len(targets)).zfill(3)
        if raw is not None:inputs[f"inputs/{number}-body.json"] = raw
        core_raw = native.common.encoded(core);inputs[f"inputs/{number}-core.json"] = core_raw
        meta = {"schema_version": "lab-candidate-target-metadata/v1-candidate", "category": row["category"], "decision_ref": row["decision_ref"], "contract": row["native_contract"]}
        inputs[f"inputs/{number}-metadata.json"] = encode(meta)
        metadata[header["version_ref"]] = {"ref": f"define-metadata:{sha(encode(cohort))}:{number}", "sha256": sha(encode(meta))}
    config = view.data["config"]
    proposal = {"schema_version": "lab-runtime-proposal/v1", "proposal_id": cohort["cohort_id"],
                "expected_head": view.data["head"]["transaction_digest"], "source_snapshot_digest": config["source_snapshot_digest"],
                "scope_ref": config["scope_ref"], "policy_ref": config["policy_ref"], "challenge_route": config["challenge_route"], "schemas": schemas, "targets": targets}
    if view.selected["name"] == "custody-participation":
        proposal = native.custody.with_originals(proposal, originals, schema_bytes, exact_schema_bytes=True)
        require(proposal["targets"] == targets, "custody-core-change")
    before = native.common.digest(view.data["projection"])
    _, computed = native.operations.prepare(view.data["projection"], proposal, proposal["expected_head"], config)
    require(before == native.common.digest(view.data["projection"]) and computed == cores, "native-preparation-mismatch")
    return {"proposal": proposal, "cores": cores, "inputs": inputs, "target_metadata": metadata}


def stage_review(view, gate, cohort_raw, input_root, destination, workspace_schema, source_guard, on_precommit=None):
    """Fresh immutable workspace only; host routing/policy issuance remains independent."""
    cohort = decode(cohort_raw);cohort_digest = sha(cohort_raw)
    current_cut = source_guard()
    observation = gate.permit("stage-review", cohort["scope_ref"], cohort_digest)
    controls = native_controls(view, cohort, input_root, current_cut)
    # Current owner/profile sources and routing must be selected and validated by the owning host.
    routed = gate.call("prepare-review-routing", {"cohort_sha256": cohort_digest, "cohort": cohort,
                                                "core_file_sha256s": [sha(view.handle.common.encoded(c)) for c in controls["cores"]]})
    shape(routed, ("routing", "policy_selection_binding", "verified_owner_route_selections", "authority_effect"))
    require(routed["verified_owner_route_selections"] == cohort["owner_route_selections"] and bool(cohort["owner_route_selections"]) and routed["authority_effect"] == "none", "owner-route-unqualified", exit_code=3)
    inputs = controls["inputs"]
    inputs["inputs/review-routing.json"] = encode(routed["routing"])
    for b in cohort["schema_bindings"]:
        path = "inputs/" + Path(b["path"]).name
        require(path not in inputs, "schema-input-path-conflict")
        inputs[path] = bound(input_root, b)
    for i, b in enumerate([*cohort["evidence_bindings"], cohort["examples_binding"], cohort["consequences_recipe_binding"], cohort["privacy_review_binding"]]):
        raw = bound(input_root, b);privacy(raw);inputs[f"inputs/support-{i:03d}.json"] = raw
    require(all(len(raw) <= 1048576 for raw in inputs.values()) and sum(map(len, inputs.values())) <= 16777216, "native-material-budget")
    materials = []
    for path, raw in inputs.items():
        ref = next((b["ref"] for b in controls["target_metadata"].values() if b["sha256"] == sha(raw)), "define-input:" + cohort_digest + ":" + Path(path).name)
        materials.append({"ref": ref, "path": path, "sha256": sha(raw)})
    workspace_ref = "define-review:" + cohort_digest[:48]
    manifest = {"schema_version": "lab-owned-candidate-workspace/v1-candidate", "workspace_ref": workspace_ref,
                "principal_ref": observation["principal_ref"], "scope_refs": [cohort["scope_ref"]], "materials": materials,
                "target_metadata": controls["target_metadata"], "authority_effect": "none", "actual_owner_outcome": None}
    require(Draft202012Validator(workspace_schema).is_valid(manifest), "workspace-schema-invalid")
    require(source_guard() == current_cut, "stale-review-cut", exit_code=3)
    gate.permit("stage-review", cohort["scope_ref"], cohort_digest)
    result = {"workspace_ref": workspace_ref, "workspace_binding": binding(encode(manifest), "workspace.json"),
            "policy_selection_binding": routed["policy_selection_binding"], "posture": "candidate-inputs-staged",
            "independent_host_review": "required", "current_owner_authority_verified": False,
            "actual_owner_outcome": None, "authority_effect": "none"}
    if on_precommit is not None:on_precommit(result)
    write_package(destination, {**inputs, "workspace.json": encode(manifest)}, empty_directories=("objects", "journal"))
    return result


class ReviewJournal:
    """Owned outer operation journal. It never answers native governing commit status."""
    def __init__(self, root, gate, scope):
        from .custody import Custody
        self.storage = Custody(root, "define-review-operations", scope, gate)
        self.gate, self.scope = gate, scope

    def close(self):self.storage.close()

    def verify_workspace(self, directory, expected):
        raw = read(directory / "workspace.json", private=True)
        require(sha(raw) == expected["workspace_binding"]["sha256"], "staged-workspace-changed", exit_code=3)
        m = decode(raw);paths = set()
        for row in m["materials"]:
            from .exact import logical
            logical(row["path"])
            require(row["path"].startswith("inputs/") and row["path"] not in paths, "invalid-workspace-members")
            paths.add(row["path"])
            require(sha(read(directory / row["path"], private=True)) == row["sha256"], "staged-input-changed", exit_code=3)
        require({"inputs/" + p.name for p in (directory / "inputs").iterdir()} == paths, "unselected-workspace-input", exit_code=3)
        return expected

    def stage(self, key, view, cohort_raw, input_root, schema, source_guard):
        from .exact import exclusive, fsync_dir
        cohort = decode(cohort_raw);digest = sha(cohort_raw)
        observation = self.gate.permit("stage-review", self.scope, digest)
        require(cohort["scope_ref"] == self.scope and source_guard() == cohort["source_cut"], "stale-review-cut", exit_code=3)
        operation = sha(encode({"principal": observation["principal_ref"], "scope": self.scope, "key": key}))
        fingerprint = sha(encode({"cohort_sha256": digest, "source_cut": cohort["source_cut"], "scope": self.scope, "directory_identity": list(self.storage.identity)}))
        with self.storage.lock():
            directory = self.storage.directory("operations/" + operation)
            request_path = directory / "request.json"
            if request_path.exists():
                old = decode(self.storage.selected_read(request_path))
                require(old["fingerprint"] == fingerprint, "idempotency-conflict", exit_code=3)
            else:self.storage.install(request_path, encode({"fingerprint": fingerprint, "cohort_sha256": digest, "authority_effect": "none"}))
            pending = directory / "pending-result.json"
            workspace = directory / "workspace"
            if workspace.exists():
                require(pending.exists(), "stage-outcome-unknown", "Inspect original owned operation; no restaging inferred", 3)
                result = self.verify_workspace(workspace, decode(self.storage.selected_read(pending)))
                self.gate.permit("stage-review", self.scope, digest)
                return result
            require(not pending.exists(), "stage-incomplete", "Inspect interrupted preparation and use an explicit new request", 3)
            result = stage_review(view, self.gate, cohort_raw, input_root, workspace, schema, source_guard,
                                  on_precommit=lambda value: self.storage.install(pending, encode(value)))
            self.storage.install(directory / "complete.json", encode({"operation_id": operation, "workspace_ref": result["workspace_ref"], "posture": "candidate-inputs-staged", "authority_effect": "none"}))
            return result

    def inspect(self, operation_id):
        from .exact import HEX
        require(HEX.fullmatch(operation_id), "invalid-operation-id")
        self.gate.permit("inspect-local-operation", self.scope, operation_id)
        directory = self.storage.root / "operations" / operation_id
        request = decode(self.storage.selected_read(directory / "request.json"))
        committed = (directory / "workspace").exists()
        result = None
        if committed:
            result = self.verify_workspace(directory / "workspace", decode(self.storage.selected_read(directory / "pending-result.json")))
        return {"operation_id": operation_id, "cohort_sha256": request["cohort_sha256"], "posture": "candidate-inputs-staged" if committed else "incomplete",
                "result": result, "native_governing_outcome": "not-established-by-local-journal", "authority_effect": "none"}
