#!/usr/bin/env python3
"""Validate and materialize the isolated W7 ontology-product rehearsal."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
FIXTURES = SCRIPT.parent
EPOCH = FIXTURES.parent
ONTOLOGY_LIFECYCLE = EPOCH.parents[1]
LAB = EPOCH.parents[2]
MANIFEST_PATH = EPOCH / "manifest.json"
RUNNER_MANIFEST = FIXTURES / "rehearsal-runner" / "Cargo.toml"
RUNNER_SOURCE = FIXTURES / "rehearsal-runner" / "src" / "main.rs"
OUTPUT = FIXTURES / "output"
RECEIPT = EPOCH / "receipt.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def find_cargo() -> str | None:
    direct = shutil.which("cargo")
    if direct:
        return direct
    candidates = sorted(Path("/home/vrondelli/.rustup/toolchains").glob("*/bin/cargo"))
    return str(candidates[-1]) if candidates else None


def find_rustfmt() -> str | None:
    candidates = sorted(Path("/home/vrondelli/.rustup/toolchains").glob("*/bin/rustfmt"))
    if candidates:
        return str(candidates[-1])
    direct = shutil.which("rustfmt")
    return direct


def command(arguments: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def tree_entries(root: Path) -> list[dict[str, str]]:
    return [
        {"path": path.relative_to(root).as_posix(), "sha256": digest(path)}
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    ]


def tree_digest(entries: list[dict[str, str]]) -> str:
    preimage = "".join(f"{item['path']}\0{item['sha256']}\n" for item in entries)
    return hashlib.sha256(preimage.encode("utf-8")).hexdigest()


def record(checks: list[dict[str, Any]], check_id: str, passed: bool, detail: Any) -> None:
    checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})


def resolve_lab_ref(ref: dict[str, Any]) -> Path:
    return LAB / ref["path"]


def validate_bound_refs(manifest: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    refs: list[tuple[str, Path, str]] = [
        (
            "source-selection-decision",
            resolve_lab_ref(manifest["source_selection_ref"]),
            manifest["source_selection_ref"]["sha256"],
        ),
        (
            "w6-acceptance-decision",
            resolve_lab_ref(manifest["w6_acceptance_ref"]),
            manifest["w6_acceptance_ref"]["sha256"],
        ),
    ]
    for key in ("construction_binding", "verification", "d65_status"):
        ref = manifest["accepted_w6_epoch"][key]
        refs.append((f"accepted-w6-{key}", resolve_lab_ref(ref), ref["sha256"]))
    for index, ref in enumerate(manifest["accepted_w6_epoch"]["runtime"], start=1):
        refs.append((f"accepted-runtime-{index}", resolve_lab_ref(ref), ref["sha256"]))
    for index, ref in enumerate(manifest["plan_refs"], start=1):
        refs.append((f"w7-plan-{index}", resolve_lab_ref(ref), ref["sha256"]))
    failures = []
    for ref_id, path, expected in refs:
        actual = digest(path) if path.is_file() else None
        if actual != expected:
            failures.append(
                {"ref_id": ref_id, "path": str(path), "expected": expected, "actual": actual}
            )
    record(checks, "accepted-predecessor-and-plan-currentness", not failures, failures or {"refs": len(refs)})


def source_paths(manifest: dict[str, Any]) -> list[tuple[dict[str, Any], Path]]:
    source_root = Path(manifest["source_repository"]).resolve()
    resolved = []
    for item in manifest["inputs"]:
        path = (source_root / item["path"]).resolve()
        if not path.is_relative_to(source_root):
            raise ValueError(f"source path escapes selected repository: {path}")
        resolved.append((item, path))
    return resolved


def validate_sources(
    manifest: dict[str, Any], checks: list[dict[str, Any]]
) -> tuple[dict[str, str], dict[str, Any], dict[str, Any], dict[str, Any]]:
    actual: dict[str, str] = {}
    failures = []
    documents: dict[str, Any] = {}
    for item, path in source_paths(manifest):
        current = digest(path) if path.is_file() else None
        actual[item["input_id"]] = current or "missing"
        if current != item["sha256"]:
            failures.append(
                {"input_id": item["input_id"], "expected": item["sha256"], "actual": current}
            )
        elif current:
            documents[item["input_id"]] = load(path)
    record(checks, "selected-source-currentness", not failures, failures or actual)
    return (
        actual,
        documents.get("ontology-product-profile", {}),
        documents.get("ontology-product-nodes", {}),
        documents.get("ontology-product-relations", {}),
    )


def validate_mapping_coverage(
    manifest: dict[str, Any],
    profile: dict[str, Any],
    nodes_document: dict[str, Any],
    relations_document: dict[str, Any],
    checks: list[dict[str, Any]],
) -> None:
    node_records = nodes_document.get("nodes", [])
    relation_records = relations_document.get("relations", [])
    vocabulary_records = relations_document.get("relation_vocabulary", [])
    actual = {
        "profile": set(profile),
        "node": set().union(*(set(item) for item in node_records)) if node_records else set(),
        "relation": set().union(*(set(item) for item in relation_records)) if relation_records else set(),
        "relation_vocabulary": set().union(*(set(item) for item in vocabulary_records))
        if vocabulary_records
        else set(),
    }
    synthetic = {
        "node": {"complete legacy record"},
        "relation": {"complete legacy relation and vocabulary records"},
    }
    declared = {
        shape: {entry["field"] for entry in manifest["field_mapping"][shape]}
        - synthetic.get(shape, set())
        for shape in actual
    }
    differences = {
        shape: {
            "unclassified": sorted(actual[shape] - declared[shape]),
            "declared_but_absent": sorted(declared[shape] - actual[shape]),
        }
        for shape in actual
        if actual[shape] != declared[shape]
    }
    counts_match = (
        len(node_records) == manifest["rehearsal_contract"]["node_count"] == 23
        and len(relation_records) == manifest["rehearsal_contract"]["relation_count"] == 24
        and len(vocabulary_records)
        == manifest["rehearsal_contract"]["relation_vocabulary_count"]
        == 13
    )
    residue_closed = (
        manifest["profile_metadata"]["unclassified_fields"] == []
        and manifest["residue_policy"]["unclassified_inputs"] == []
        and manifest["residue_policy"]["acceptance_critical_residue"] == []
    )
    record(
        checks,
        "legacy-shape-classification-closure",
        not differences and counts_match and residue_closed,
        differences
        or {
            "profile_fields": len(actual["profile"]),
            "node_fields": len(actual["node"]),
            "relation_fields": len(actual["relation"]),
            "vocabulary_fields": len(actual["relation_vocabulary"]),
            "nodes": len(node_records),
            "relations": len(relation_records),
            "vocabulary_terms": len(vocabulary_records),
            "acceptance_critical_residue": 0,
        },
    )


def run_runner(
    cargo: str, manifest_path: Path, output: Path, target: Path, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    run_env = dict(env)
    run_env["CARGO_TARGET_DIR"] = str(target)
    return command(
        [
            cargo,
            "run",
            "--manifest-path",
            str(RUNNER_MANIFEST),
            "--locked",
            "--offline",
            "--",
            str(manifest_path),
            str(output),
        ],
        LAB,
        run_env,
    )


def validate_emitted_output(
    output: Path,
    manifest: dict[str, Any],
    nodes_document: dict[str, Any],
    relations_document: dict[str, Any],
    checks: list[dict[str, Any]],
) -> None:
    semantic_paths = sorted((output / "semantic-events").glob("*.json"))
    governance_paths = sorted((output / "governance-events").glob("*.json"))
    semantic = [load(path) for path in semantic_paths]
    governance = [load(path) for path in governance_paths]
    semantic_by_id = {event["event_id"]: event for event in semantic}
    node_by_id = {item["id"]: item for item in nodes_document["nodes"]}
    relation_by_id = {item["id"]: item for item in relations_document["relations"]}
    vocabulary_by_id = {item["id"]: item for item in relations_document["relation_vocabulary"]}
    expected_subjects = set(node_by_id) | set(relation_by_id)
    actual_subjects = {event["subject_identity"]["subject_id"] for event in semantic}
    cursor_pass = [event["semantic_cursor"] for event in semantic] == list(range(1, 48))
    governance_cursor_pass = [event["governance_cursor"] for event in governance] == list(
        range(1, 48)
    )
    exact_join_failures = []
    roundtrip_failures = []
    for event in governance:
        reference = event["semantic_ref"]
        source = semantic_by_id.get(reference["semantic_event_id"])
        if not source or reference != {
            "semantic_event_id": source["event_id"],
            "semantic_event_digest": source["event_digest"],
            "semantic_cursor": source["semantic_cursor"],
        }:
            exact_join_failures.append(event["event_id"])
            continue
        if event["complete_resulting_governance_state"]["semantic_ref"] != reference:
            exact_join_failures.append(event["event_id"])
        subject_id = source["subject_identity"]["subject_id"]
        residue = event["complete_resulting_governance_state"]["residue"]
        if len(residue) != 1 or residue[0]["residue_type"] != "legacy-record-roundtrip-witness":
            roundtrip_failures.append(subject_id)
            continue
        preserved = json.loads(residue[0]["observed_remainder"])
        if subject_id in node_by_id:
            expected = {"legacy_record": node_by_id[subject_id]}
        else:
            relation = relation_by_id[subject_id]
            expected = {
                "legacy_record": relation,
                "legacy_relation_vocabulary": vocabulary_by_id[relation["type"]],
            }
        if preserved != expected:
            roundtrip_failures.append(subject_id)
    lineage = load(output / "projections" / "lineage.json")
    lineage_subjects = {entry["subject_id"] for entry in lineage}
    record(
        checks,
        "canonical-event-and-lineage-closure",
        len(semantic) == 47
        and len(governance) == 47
        and cursor_pass
        and governance_cursor_pass
        and actual_subjects == expected_subjects
        and lineage_subjects == expected_subjects
        and len(lineage) == 47,
        {
            "semantic_events": len(semantic),
            "governance_events": len(governance),
            "lineage_entries": len(lineage),
            "subjects": len(actual_subjects),
        },
    )
    record(
        checks,
        "exact-governance-reference-join",
        not exact_join_failures,
        exact_join_failures or {"exact_joins": len(governance)},
    )
    record(
        checks,
        "information-preserving-typed-residue",
        not roundtrip_failures,
        roundtrip_failures or {"roundtripped_records": len(governance)},
    )

    result = load(output / "run-result.json")
    snapshots = load(output / "projections" / "latest-subject-snapshots.json")
    direct = (output / "projections" / "ontology-at-cursor.json").read_bytes()
    checkpoint = (output / "projections" / "ontology-from-checkpoint.json").read_bytes()
    views = load(output / "projections" / "governed-node-views.json")
    context = load(output / "projections" / "context-projection.json")
    context_subjects = context["projection_body"]["subjects"]
    projection_pass = (
        result["result"] == "PASS"
        and result["direct_and_checkpoint_rebuild_equal"] is True
        and len(snapshots) == 47
        and direct == checkpoint
        and len(views) == 23
        and len(context["selected_node_ids"]) == 23
        and len(context["selected_relation_ids"]) == 24
        and len(context_subjects) == 47
        and context["source_cursor"] == 47
        and {entry["source_cursor"] for entry in context_subjects} <= set(range(1, 48))
    )
    record(
        checks,
        "replay-equality-and-one-consistent-cut",
        projection_pass,
        {
            "snapshots": len(snapshots),
            "governed_node_views": len(views),
            "context_subjects": len(context_subjects),
            "source_cursor": context["source_cursor"],
            "direct_checkpoint_bytes_equal": direct == checkpoint,
        },
    )


def validate_source_drift_rejection(
    cargo: str,
    manifest: dict[str, Any],
    temporary: Path,
    env: dict[str, str],
    checks: list[dict[str, Any]],
) -> None:
    source_copy = temporary / "mutated-source"
    for item, source in source_paths(manifest):
        destination = source_copy / item["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    nodes_input = next(item for item in manifest["inputs"] if item["input_id"] == "ontology-product-nodes")
    mutated_nodes_path = source_copy / nodes_input["path"]
    mutated_nodes = load(mutated_nodes_path)
    mutated_nodes["nodes"][0]["label"] += " mutated"
    stable_write(mutated_nodes_path, mutated_nodes)
    mutated_manifest = copy.deepcopy(manifest)
    mutated_manifest["source_repository"] = str(source_copy)
    mutated_manifest_path = temporary / "mutated-manifest.json"
    stable_write(mutated_manifest_path, mutated_manifest)
    result = run_runner(
        cargo,
        mutated_manifest_path,
        temporary / "mutated-output",
        Path("/tmp/cal-w7-validation-runner-target"),
        env,
    )
    passed = result.returncode != 0 and "source digest drift" in result.stderr
    record(
        checks,
        "source-drift-mutation-rejected",
        passed,
        {"exit_code": result.returncode, "expected_failure": "source digest drift"},
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-fixtures", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    checks: list[dict[str, Any]] = []
    manifest = load(MANIFEST_PATH)
    cargo = find_cargo()
    rustfmt = find_rustfmt()
    if not cargo:
        record(checks, "rust-toolchain-available", False, "cargo unavailable")
    else:
        record(checks, "rust-toolchain-available", True, {"cargo": cargo, "rustfmt": rustfmt})

    validate_bound_refs(manifest, checks)
    source_before, profile, nodes_document, relations_document = validate_sources(manifest, checks)
    validate_mapping_coverage(manifest, profile, nodes_document, relations_document, checks)

    env = dict(os.environ)
    if cargo:
        env["PATH"] = str(Path(cargo).parent) + os.pathsep + env.get("PATH", "")
    env["TMPDIR"] = "/tmp"
    runner_format = None
    runner_check = None
    if rustfmt:
        runner_format = command([rustfmt, "--edition", "2024", "--check", str(RUNNER_SOURCE)], LAB, env)
    if cargo:
        check_env = dict(env)
        check_env["CARGO_TARGET_DIR"] = "/tmp/cal-w7-validation-check-target"
        runner_check = command(
            [cargo, "check", "--manifest-path", str(RUNNER_MANIFEST), "--locked", "--offline"],
            LAB,
            check_env,
        )
    record(
        checks,
        "rehearsal-runner-build",
        runner_format is not None
        and runner_format.returncode == 0
        and runner_check is not None
        and runner_check.returncode == 0,
        {
            "format_exit": runner_format.returncode if runner_format else None,
            "check_exit": runner_check.returncode if runner_check else None,
        },
    )

    with tempfile.TemporaryDirectory(prefix="cal-w7-validation-", dir="/tmp") as temporary_name:
        temporary = Path(temporary_name)
        run_a = temporary / "run-a"
        run_b = temporary / "run-b"
        first = (
            run_runner(
                cargo,
                MANIFEST_PATH,
                run_a,
                Path("/tmp/cal-w7-validation-runner-target"),
                env,
            )
            if cargo
            else None
        )
        second = (
            run_runner(
                cargo,
                MANIFEST_PATH,
                run_b,
                Path("/tmp/cal-w7-validation-runner-target"),
                env,
            )
            if cargo and first and first.returncode == 0
            else None
        )
        execution_pass = (
            first is not None
            and first.returncode == 0
            and second is not None
            and second.returncode == 0
        )
        record(
            checks,
            "isolated-two-run-execution",
            execution_pass,
            {
                "first_exit": first.returncode if first else None,
                "second_exit": second.returncode if second else None,
            },
        )
        run_a_entries = tree_entries(run_a) if run_a.is_dir() else []
        run_b_entries = tree_entries(run_b) if run_b.is_dir() else []
        run_a_digest = tree_digest(run_a_entries) if run_a_entries else None
        run_b_digest = tree_digest(run_b_entries) if run_b_entries else None
        record(
            checks,
            "two-run-byte-determinism",
            bool(run_a_entries) and run_a_entries == run_b_entries,
            {
                "file_count": len(run_a_entries),
                "run_a_tree_digest": run_a_digest,
                "run_b_tree_digest": run_b_digest,
            },
        )
        if execution_pass:
            validate_emitted_output(run_a, manifest, nodes_document, relations_document, checks)
            runtime_manifest = ONTOLOGY_LIFECYCLE / "runtime" / "Cargo.toml"
            cli_env = dict(env)
            cli_env["CARGO_TARGET_DIR"] = "/tmp/cal-w7-validation-runtime-target"
            cli = command(
                [
                    cargo,
                    "run",
                    "--manifest-path",
                    str(runtime_manifest),
                    "--locked",
                    "--offline",
                    "--bin",
                    "ontology-at-cursor",
                    "--",
                    str(run_a / "semantic-events"),
                    str(run_a / "governance-events"),
                    "47",
                ],
                LAB,
                cli_env,
            )
            expected_cli = (run_a / "projections" / "ontology-at-cursor.json").read_text(
                encoding="utf-8"
            )
            record(
                checks,
                "accepted-runtime-cli-equality",
                cli.returncode == 0 and cli.stdout == expected_cli,
                {"exit_code": cli.returncode, "bytes_equal": cli.stdout == expected_cli},
            )
            validate_source_drift_rejection(cargo, manifest, temporary, env, checks)
        else:
            for check_id in (
                "canonical-event-and-lineage-closure",
                "exact-governance-reference-join",
                "information-preserving-typed-residue",
                "replay-equality-and-one-consistent-cut",
                "accepted-runtime-cli-equality",
                "source-drift-mutation-rejected",
            ):
                record(checks, check_id, False, "not_evaluable: isolated execution failed")

        source_after = {
            item["input_id"]: digest(path) if path.is_file() else "missing"
            for item, path in source_paths(manifest)
        }
        record(
            checks,
            "legacy-source-bytes-unchanged",
            source_before == source_after,
            {"before": source_before, "after": source_after},
        )

        failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
        if args.write_fixtures and not failed:
            if OUTPUT.exists():
                output_equal = tree_entries(OUTPUT) == run_a_entries
            else:
                shutil.copytree(run_a, OUTPUT)
                output_equal = tree_entries(OUTPUT) == run_a_entries
            record(
                checks,
                "materialized-fixture-currentness",
                output_equal,
                {
                    "file_count": len(run_a_entries),
                    "output_tree_digest": tree_digest(run_a_entries),
                },
            )
        elif args.write_fixtures:
            record(
                checks,
                "materialized-fixture-currentness",
                False,
                "not_evaluable: predecessor validation failed",
            )

        failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
        result = "PASS" if not failed else "BLOCK"
        receipt = {
            "schema_version": "cal-w7-migration-rehearsal-receipt/v1",
            "epoch_id": manifest["epoch_id"],
            "gate_id": "G-W7",
            "result": result,
            "checks": checks,
            "failed_checks": failed,
            "coverage": {
                "selected_source_files": 3,
                "classified_profile_fields": len(manifest["field_mapping"]["profile"]),
                "classified_node_fields": len(manifest["field_mapping"]["node"]),
                "classified_relation_fields": len(manifest["field_mapping"]["relation"]),
                "classified_vocabulary_fields": len(
                    manifest["field_mapping"]["relation_vocabulary"]
                ),
                "nodes": 23,
                "relations": 24,
                "relation_vocabulary_terms": 13,
                "semantic_events": 47,
                "governance_events": 47,
                "lineage_entries": 47,
                "governed_node_views": 23,
            },
            "immutable_refs": {
                "manifest": {"path": "manifest.json", "sha256": digest(MANIFEST_PATH)},
                "runner_manifest": {
                    "path": "fixtures/rehearsal-runner/Cargo.toml",
                    "sha256": digest(RUNNER_MANIFEST),
                },
                "runner_lock": {
                    "path": "fixtures/rehearsal-runner/Cargo.lock",
                    "sha256": digest(RUNNER_MANIFEST.parent / "Cargo.lock"),
                },
                "runner_source": {
                    "path": "fixtures/rehearsal-runner/src/main.rs",
                    "sha256": digest(RUNNER_SOURCE),
                },
                "validator": {
                    "path": "fixtures/validate.py",
                    "sha256": digest(SCRIPT),
                },
                "source_selection_decision": manifest["source_selection_ref"],
                "w6_acceptance_decision": manifest["w6_acceptance_ref"],
            },
            "determinism": {
                "repeat_count": 2,
                "run_a_tree_digest": run_a_digest,
                "run_b_tree_digest": run_b_digest,
                "byte_identical": run_a_entries == run_b_entries,
                "materialized_output_tree_digest": tree_digest(tree_entries(OUTPUT))
                if OUTPUT.is_dir()
                else None,
            },
            "source_bytes_unchanged": source_before == source_after,
            "unclassified_inputs": manifest["residue_policy"]["unclassified_inputs"],
            "acceptance_critical_residue": manifest["residue_policy"][
                "acceptance_critical_residue"
            ],
            "blockers": []
            if result == "PASS"
            else [{"code": "W7_REHEARSAL_FAILED", "failed_checks": failed}],
            "downstream": {"W8": "ready" if result == "PASS" else "not_evaluable"},
            "authority_effect": "none",
            "claim_ceiling": "G-W7 isolated migration rehearsal evidence only. PASS proves exact source classification, information-preserving event mapping, exact governance joins, deterministic projection rebuilds, and unchanged legacy bytes for this one selected slice. It does not admit or accept an ontology, mutate a source, authorize migration cutover, publish, release, deploy, use credentials, perform destructive action, or grant external effects.",
        }
        if args.write_receipt:
            stable_write(RECEIPT, receipt)
        print(
            json.dumps(
                {
                    "epoch_id": manifest["epoch_id"],
                    "gate_id": "G-W7",
                    "result": result,
                    "failed_checks": failed,
                    "output_tree_digest": receipt["determinism"][
                        "materialized_output_tree_digest"
                    ],
                    "downstream": receipt["downstream"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
