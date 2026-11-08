"""Cold inventory of API40 operation test sources; this runs no Lab operation."""
from __future__ import annotations

import ast
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[4]
BASE = Path("product/lab/release-candidates/v1/interface")
API = BASE / "api-integration-v40-current-t06-0001"
ACTION = BASE / "api-action-integration-v7-current-t06-0001"
GOVERNANCE = BASE / "api-governance-integration-v5-current-t12-0001"
T17 = Path("docs/plans/0011-lab-runtime-completion/work-pack/tasks/T17.md")
OLD_CALLER = Path("docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/common-all34-0277/caller.py")
OLD_SELECTION = Path("docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/common-all34-selection-0278/selection-plan.json")
BRANCH_SELECTION = Path("docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api40-0001/revision-0001/driver-selection.json")
HERE = Path(__file__).resolve().parent


def regular_bytes(path: Path) -> bytes:
    """Read an exact physical file, refusing a linked leaf or ancestor."""
    path = path.absolute()
    for parent in (path, *path.parents):
        mode = parent.lstat().st_mode
        if stat.S_ISLNK(mode) or (parent == path and not stat.S_ISREG(mode)):
            raise ValueError(f"linked or nonregular T17 input: {path}")
    return path.read_bytes()

# These are the reviewed API40 cut and historical design inputs, not hashes
# discovered while generating a new inventory. A different cut needs a new
# versioned builder and output.
EXPECTED_BINDINGS = {
    API / "source-manifest.json": "45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219",
    API / "contract-profile.json": "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614",
    API / "protocol.py": "f3f24585ac712732c297ef04b4a7f31f6cd70745b60f6dd0bc5df92b40d7bcde",
    API / "integration-members.json": "625ccd27d3a18166dbdaa837c3ec9395491853cb28cef5ff4e05392c99365732",
    ACTION / "source-manifest.json": "9f8fdb8dea1545fd7767853ba867f6d10c83ea7c8c50df047c054632eed15900",
    ACTION / "contract-profile.json": "b3767b2b1ececc73ce24ea7d55924956feab8a5f3b563c3359391122a95b3576",
    GOVERNANCE / "source-manifest.json": "8a215ad66e94179385bcb4dcac79eab5267ee6ac50e12e7b1dac21645301d337",
    GOVERNANCE / "contract-profile.json": "7798fda1f9e7e4038425bc8aa6f227f2e22612affa4acb2c28c9a12d31531af3",
    T17: "4d5d71bb4542ad3f3b36ea0ee9065adce5615abfb899b7dc5532ca2481009d50",
    OLD_CALLER: "45ce0d17e61a49855f0dd2735f7ad8cbf0da58dbadc959631bb36095b53b384a",
    OLD_SELECTION: "1625d9229d855796a7b32661c4a11a084b37a5352138c193de1ec8069aa0891b",
    BRANCH_SELECTION: "2709c559fdfe0ffca7bd684b7454903446367731170df63dd8243ca7076f4480",
}


def verify_expected(expected: dict[Path, str] = EXPECTED_BINDINGS, root: Path = ROOT) -> None:
    for path, digest in expected.items():
        actual = hashlib.sha256(regular_bytes(root / path)).hexdigest()
        if actual != digest:
            raise ValueError(f"frozen T17 input differs: {path}")


def pin(path: Path) -> dict:
    raw = regular_bytes(ROOT / path)
    return {"path": path.as_posix(), "sha256": hashlib.sha256(raw).hexdigest()}


def method(directory: Path, filename: str, name: str, claim: str) -> dict:
    path = directory / filename
    source = regular_bytes(ROOT / path).decode()
    matches = []
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef):
            matches.extend((node.name, child.lineno) for child in node.body
                           if isinstance(child, ast.FunctionDef) and child.name == name)
    if len(matches) != 1:
        raise ValueError(f"method absent or ambiguous: {path}:{name}")
    cls, line = matches[0]
    return {**pin(path), "class": cls, "method": name, "line": line,
            "claim": claim}


# Source candidates are not T17 results. `limited` means the method exercises
# only an empty result, component boundary, or another grant's refusal.
A = lambda file, name, claim="actual API40 candidate": method(API, file, name, claim)
X = lambda file, name, claim="selected Action-v7 branch candidate": method(ACTION, file, name, claim)
E = lambda directory, file, name, claim: method(BASE / directory, file, name, claim)

CANDIDATES = {
    "lab.status": (A("test_custody_api.py", "test_13_actual_stdout_nonce_authenticated_status"),
                   A("test_current_controls.py", "test_09_actual_nested_dispatch_refused_without_effect", "nested-dispatch refusal; not a per-operation causal Actor negative")),
    "catalog.get": (A("test_preparation.py", "test_four_retained_read_handlers_actual"), None),
    "artifact.inspect": (A("test_custody_sessions.py", "test_00_all_eleven_actual_operations"), None),
    "artifact.query": (A("test_custody_sessions.py", "test_00_all_eleven_actual_operations"), None),
    "change.prepare": (A("test_preparation.py", "test_actual_prepare_stages_exact_diff"),
                       A("test_preparation.py", "test_wrong_scope_refused_before_claim")),
    "change.validate": (A("test_preparation.py", "test_actual_validation_uses_runtime_and_no_authority"),
                        A("test_preparation.py", "test_wrong_candidate_contract_fails", "domain result=fail for wrong candidate contract; not a causal Actor negative")),
    "operation.inspect": (A("test_preparation.py", "test_completed_operation_inspection_bound"),
                          A("test_preparation.py", "test_unknown_operation_scoped_not_found", "unknown-operation lookup result; not a causal Actor negative")),
    "context.get": (A("test_custody_sessions.py", "test_00_all_eleven_actual_operations"),
                    A("test_metadata_scope.py", "test_05_metadata_cannot_invoke_any_Session_operation", "other-grant refusal; same permitted lifetime negative missing")),
    "session.open": (A("test_custody_sessions.py", "test_01_actual_private_memory_erased"),
                     A("test_custody_sessions.py", "test_13_wrong_principal_denied")),
    "session.close": (A("test_custody_sessions.py", "test_08_close_exact_retry"),
                      A("test_custody_sessions.py", "test_10_wrong_close_preimage_denied")),
    "session.inspect": (A("test_custody_sessions.py", "test_09_closed_metadata_retained"),
                        A("test_metadata_scope.py", "test_05_metadata_cannot_invoke_any_Session_operation", "other-grant refusal; same permitted lifetime negative missing")),
    "projection.refresh": (A("test_custody_sessions.py", "test_00_all_eleven_actual_operations"), None),
    "challenge.submit": (A("test_challenge_api.py", "test_01_actual_challenge_proposal_preserves_exact_revision_and_original_bytes"),
                         A("test_challenge_api.py", "test_03_undeclared_ground_refused_before_claim_without_file_changes", "invalid challenge contract; not a causal Actor negative")),
    "files.materialize": (A("test_file_exports.py", "test_00_actual_public_byte_export"),
                          A("test_file_exports.py", "test_09_parent_path_refused", "path-contract refusal; not a causal Actor negative")),
    "proposal.review": (A("test_review_api.py", "test_00_actual_two_target_review_one_checkpoint"),
                        A("test_review_api.py", "test_03_reordered_cores_refused_before_claim", "ordering and contract refusal; not a causal Actor negative")),
    "classification.prepare": (A("test_classification_api.py", "test_01_exact_original_ChangeProposal_result"),
                               A("test_classification_api.py", "test_06_missing_operator_grant_refuses_before_claim", "other-grant refusal; same permitted-lifetime Actor negative missing")),
    "failure.assess": (A("test_failure_api.py", "test_01_exact_original_ChangeProposal_and_connections"),
                       A("test_failure_api.py", "test_10_missing_grant_refuses_before_claim", "other-grant refusal; same permitted-lifetime Actor negative missing")),
    "typed.extension.prepare": (None, None),
    "lesson.select": (E("api52-lesson-checks-v1", "test_host.py", "test_01_actual_empty_inventory_and_zero_action", "external component; empty-inventory result, not selected Lesson positive"),
                      E("api52-lesson-checks-v1", "test_host.py", "test_02_spoofed_Actor_and_foreign_Assignment_refused", "external component; not common API40 dispatcher")),
    "package.import": (E("api54-package-checks-v1", "test_host.py", "test_01_actual_import_returns_exact_validated_candidate", "external component; not common API40 dispatcher"),
                       E("api54-package-checks-v1", "test_host.py", "test_02_actual_actor_control_cut_deadline_and_conflict_refusals", "external component; not common API40 dispatcher")),
    "package.export": (A("test_package_export.py", "test_01_controlled_native_candidate_export_with_original_source_proofs"),
                       A("test_package_export.py", "test_05_caller_cannot_replace_selected_privacy_review")),
    "lesson.assess": (None, None),
    "lesson.apply": (None, None),
    "challenge.resolve": (None, None),
    "workflow.transition": (E("workflow-transition-v1", "test_kernel.py", "test_10_actual_apply_replay_and_exact_retry", "external kernel; not common API40 dispatcher"),
                            E("workflow-transition-v1", "test_kernel.py", "test_11_conflicting_retry_refused", "external kernel; not common API40 dispatcher")),
    "ontology.project": (None, None),
    "installation.execute": (A("test_installation_release.py", "test_01_actual_install_has_verified_original_byte_closure"),
                             A("test_installation_release.py", "test_05_actor_claim_does_not_replace_authenticated_transport")),
    "release.prepare": (A("test_installation_release.py", "test_11_release_review_preserves_actual_missing_human_and_full_qualification", "correctly blocked release is conformance, not release approval"),
                        A("test_installation_release.py", "test_16_missing_actual_qualified_API_evidence_stays_blocked", "valid blocked-readiness result; not a causal Actor negative")),
    "action.evaluate": (X("test_action_api.py", "test_01_actual_evaluation_dispatch_output_and_exact_semantic_retry"),
                        X("test_action_api.py", "test_03_real_clock_deadline_response_budget_and_call_reuse", "mixed deadline, response-budget, and call-reuse checks; causal Actor negative remains unproven")),
    "action.dispatch": (X("test_action_api.py", "test_01_actual_evaluation_dispatch_output_and_exact_semantic_retry"),
                        X("test_action_api.py", "test_02_wrong_actor_scope_profile_and_input_binding_refuse_without_effect")),
    "action.reconcile": (X("test_action_api.py", "test_06_real_process_death_after_effect_preserves_uncertainty_and_reconcile_no_redispatch"),
                         X("test_action_api.py", "test_08_recovery_exact_residue_contract_and_actor_refusals")),
    "checkpoint.resolve": (None, None),
    "admission.apply": (None, None),
    "capability.adoption.prepare": (None, None),
}


def build() -> dict:
    verify_expected()
    protocol = ast.parse(regular_bytes(ROOT / API / "protocol.py").decode())
    env = {}
    def tuple_expression(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Tuple):
            return tuple(tuple_expression(item) for item in node.elts)
        if isinstance(node, ast.Name) and node.id in env:
            return env[node.id]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return tuple_expression(node.left) + tuple_expression(node.right)
        raise ValueError("nonliteral protocol operation expression")
    for node in protocol.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                env[node.targets[0].id] = tuple_expression(node.value)
            except (TypeError, ValueError):
                continue
    operations = env["SUPPORTED"]
    if len(operations) != 34 or len(set(operations)) != 34 or set(operations) != set(CANDIDATES):
        raise ValueError("API40 exact 34-operation selection differs")
    profile = json.loads(regular_bytes(ROOT / API / "contract-profile.json"))
    if profile["implemented_operations"] != list(operations):
        raise ValueError("API40 profile and protocol operation order differs")
    members = json.loads(regular_bytes(ROOT / API / "integration-members.json"))
    if (members["whole_API_qualified"] is not False or
            members["members"]["actions"]["directory"] != ACTION.name or
            members["members"]["governance"]["directory"] != GOVERNANCE.name or
            members["members"]["actions"]["source_sha256"] != pin(ACTION / "source-manifest.json")["sha256"] or
            members["members"]["actions"]["profile_sha256"] != pin(ACTION / "contract-profile.json")["sha256"] or
            members["members"]["governance"]["source_sha256"] != pin(GOVERNANCE / "source-manifest.json")["sha256"] or
            members["members"]["governance"]["profile_sha256"] != pin(GOVERNANCE / "contract-profile.json")["sha256"]):
        raise ValueError("API40 selected branch origins differ")
    old = json.loads(regular_bytes(ROOT / OLD_SELECTION))
    unit_outline = [{"unit": name, "operations": value["operations"]} for name, value in old["units"].items()]
    dispatched = [operation for unit in unit_outline for operation in unit["operations"]]
    if (len(unit_outline) != 23 or len(dispatched) != 34 or len(set(dispatched)) != 34 or
            set(dispatched) != set(operations) or
            next(unit["operations"] for unit in unit_outline if unit["unit"] == "member:Source8-lifecycle") !=
            ["context.get", "session.open", "session.inspect", "session.close", "lesson.select", "lesson.apply", "lesson.assess"]):
        raise ValueError("historical unit outline does not cover exact selected operations")
    source_rows = {}
    for directory in (API, ACTION, GOVERNANCE):
        manifest = json.loads(regular_bytes(ROOT / directory / "source-manifest.json"))
        for row in manifest["files"]:
            path, digest = row["path"], row["sha256"]
            if path in source_rows and source_rows[path] != digest:
                raise ValueError("conflicting selected source row: " + path)
            if hashlib.sha256(regular_bytes(ROOT / path)).hexdigest() != digest:
                raise ValueError("selected source row differs: " + path)
            source_rows[path] = digest
    rows = []
    for op in operations:
        positive, negative = CANDIDATES[op]
        for candidate in (positive, negative):
            if candidate is None:
                continue
            selected = source_rows.get(candidate["path"]) == candidate["sha256"]
            candidate["selected_by_cut_source_manifest"] = selected
            if candidate["path"].startswith((API.as_posix(), ACTION.as_posix(), GOVERNANCE.as_posix())) and not selected:
                raise ValueError("claimed current test method is not selected by its source manifest")
        rows.append({"operation": op, "positive_source_candidate": positive,
                     "negative_source_candidate": negative,
                     "positive_on_selected_common_dispatcher_proven": False,
                     "causal_negative_on_selected_common_dispatcher_proven": False,
                     "same_family_lifetime_proven": False})
    value = {"schema_version": "lab-t17-static-coverage-inventory/v1-candidate",
             "authority_effect": "none", "qualification_status": "NOT_RUN",
             "claim_ceiling": "Source-method inventory only; methods were not executed by this builder and branch/component tests do not prove maintained common-dispatcher coverage.",
             "api_source_binding": pin(API / "source-manifest.json"),
             "api_profile_binding": pin(API / "contract-profile.json"),
             "protocol_binding": pin(API / "protocol.py"),
             "members_binding": pin(API / "integration-members.json"),
             "action_source_binding": pin(ACTION / "source-manifest.json"),
             "governance_source_binding": pin(GOVERNANCE / "source-manifest.json"),
             "t17_contract_binding": pin(T17), "historical_caller_binding": pin(OLD_CALLER),
             "historical_selection_plan_binding": pin(OLD_SELECTION),
             "branch_selection_binding": pin(BRANCH_SELECTION),
             "dispatch_unit_outline": unit_outline,
             "api40_status": "Static API40 source inventory only; live call evidence is tracked separately",
             "operation_count": len(rows), "operations": rows,
             "no_positive_method_operations": [row["operation"] for row in rows if row["positive_source_candidate"] is None],
             "no_negative_method_operations": [row["operation"] for row in rows if row["negative_source_candidate"] is None],
             "current_positive_source_candidate_count": sum(row["positive_source_candidate"] is not None and
                      row["positive_source_candidate"]["path"].startswith((API.as_posix(), ACTION.as_posix())) for row in rows),
             "current_negative_source_candidate_count": sum(row["negative_source_candidate"] is not None and
                      row["negative_source_candidate"]["path"].startswith((API.as_posix(), ACTION.as_posix())) for row in rows)}
    verify_expected()
    return value


def encoded(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def verify_inventory(path: Path, data: bytes) -> None:
    if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
        raise ValueError("retained T17 inventory differs from frozen inputs")


def write_new(path: Path, data: bytes) -> None:
    if path.parent.resolve() != HERE or not path.name.startswith("INVENTORY-") or path.suffix != ".json":
        raise ValueError("output must be a new versioned inventory in this package")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o644)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--verify", type=Path, help="read-only comparison with an existing inventory")
    choice.add_argument("--output", type=Path, help="write a new, versioned inventory with exclusive creation")
    args = parser.parse_args()
    data = encoded(build())
    if args.verify is not None:
        verify_inventory(args.verify, data)
        target = args.verify
        mode = "verified"
    else:
        write_new(args.output, data)
        target = args.output
        mode = "created"
    print(json.dumps({"mode": mode, "output": str(target), "operations": 34,
                      "sha256": hashlib.sha256(data).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
